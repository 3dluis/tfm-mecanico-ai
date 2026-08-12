"""EXP-ANOM-003 — Refinamiento del FPR de Event Intelligence (config exp-anom-003.yaml).

Objetivo: comprobar si las falsas alarmas del brazo de eventos (EXP-ANOM-002) se deben a
insuficiencia de datos normales, baselines poco representativos, contabilidad de eventos
largos o context signatures inadecuadas — NO "hacer que Event Intelligence gane".

Brazos (atribución limpia: cada paso cambia UNA cosa):
  AM-W-v1   LOF sobre train v1 (referencia; idéntico a EXP-ANOM-002)
  AM-W-v2   LOF sobre train ampliado (equidad: la ventana también recibe los datos nuevos)
  AM-E-v1   eventos, media/σ, train v1 (referencia; idéntico a EXP-ANOM-002)
  AM-E-d    eventos, media/σ, train ampliado          → aísla el efecto DATOS
  AM-E-v2   eventos, scoring robusto (p50/percentiles), train ampliado → añade SCORING
  AM-WE-v1  AM-W-v1 OR AM-E-v1 · AM-WE-v2  AM-W-v2 OR AM-E-v2

Datos: dataset obd-lab-suite-v1 **versión 1.1** = v1 + 16 sesiones normales SOLO de
train (suite_v1_train_ext.yaml). Validation/test/held-out CONGELADOS e idénticos a
EXP-ANOM-001/002; umbrales solo con train (LOF cuantil; eventos LOSO); ningún ajuste
usa held-out. Métricas: tick-level (SIEMPRE, compatibilidad) + event-level nuevas
(evaluation.anomaly_events) + desglose urbano/autovía + descomposición de varianza
entre/intra sesión de las señales clave.

Uso: python experiments/e3_event_refinement.py [--fpr 0.01]
"""

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent))  # experiments/ = punto de composición

from e2_window_vs_event import (
    VEH,
    EventArm,
    Session,
    WindowArm,
    episode_row,
    load_suite,
    tick_metrics,
)

from ai_models.evaluation.anomaly_events import AnomalyEventReport, add_session
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from diagnostic_agent.events.baseline import MIN_SAMPLES
from mecanico_contracts import ScenarioSpec
from obd_lab.events_gt import generate_with_events

REPO_ROOT = Path(__file__).resolve().parents[2]
EXT_SUITE = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1_train_ext.yaml"
OUT_DIR = Path(__file__).parent
RUNS_FILE = OUT_DIR / "runs.jsonl"

STABILITY_FEATURES = ("ltft_mean", "maf_mean", "rpm_mean", "throttle_mean", "load_mean")


def load_train_extension() -> list[Session]:
    raw = yaml.safe_load(EXT_SUITE.read_text(encoding="utf-8"))
    out: list[Session] = []
    for entry in raw["train_extension"]:
        spec = ScenarioSpec(**entry)
        assert spec.category == "normal" and spec.fault is None, "extensión: SOLO normalidad"
        ticks, gt = generate_with_events(spec, vehicle_id=VEH)
        out.append(Session(spec, "train", ticks, gt, np.zeros(len(ticks), dtype=int)))
    return out


def window_false_runs(flags: np.ndarray) -> int:
    """Nº de rachas contiguas de ticks marcados (pseudo-eventos de la vía ventana)."""
    return int(np.sum(np.diff(np.concatenate(([0], flags.astype(int)))) == 1))


def stability_analysis(train: list[Session], arm: EventArm) -> list[dict[str, Any]]:
    """Varianza ENTRE sesiones vs INTRA sesión por perfil (CONSTANT_SPEED, features clave).

    ratio > 1 ⇒ la variación entre sesiones domina (deriva fisiológica tipo LTFT), que un
    baseline construido con pocas sesiones no puede representar.
    """
    rows: list[dict[str, Any]] = []
    for profile in ("urban", "highway"):
        sessions = [s for s in train if s.spec.driving_profile == profile]
        per_session: dict[str, dict[str, list[float]]] = {}
        for s in sessions:
            for ev, v in arm._session_pairs(s):
                if ev.event_type != "CONSTANT_SPEED":
                    continue
                for f in STABILITY_FEATURES:
                    per_session.setdefault(s.session_id, {}).setdefault(f, []).append(v.values[f])
        for f in STABILITY_FEATURES:
            means, stds = [], []
            for _sid, feats in per_session.items():
                xs = feats.get(f, [])
                if len(xs) >= 2:
                    means.append(statistics.fmean(xs))
                    stds.append(statistics.stdev(xs))
            if len(means) < 2:
                continue
            between = statistics.stdev(means)
            within = statistics.fmean(stds)
            rows.append(
                {
                    "profile": profile,
                    "feature": f,
                    "n_sessions": len(means),
                    "between_session_std": round(between, 4),
                    "within_session_std": round(within, 4),
                    "ratio_between_within": round(between / within, 2) if within else None,
                }
            )
    return rows


def main() -> int:  # noqa: PLR0912, PLR0915 — orquestación lineal del experimento
    parser = argparse.ArgumentParser()
    parser.add_argument("--fpr", type=float, default=0.01)
    args = parser.parse_args()

    sessions = load_suite()
    train_v1 = [s for s in sessions if s.split == "train"]
    train_ext = train_v1 + load_train_extension()
    splits = {sp: [s for s in sessions if s.split == sp] for sp in ("validation", "test")}
    print(f"train v1: {len(train_v1)} sesiones · train ampliado: {len(train_ext)}")

    arms: dict[str, Any] = {
        "AM-W-v1": WindowArm(),
        "AM-W-v2": WindowArm(),
        "AM-E-v1": EventArm(use_context=True, robust=False),
        "AM-E-d": EventArm(use_context=True, robust=False),
        "AM-E-v2": EventArm(use_context=True, robust=True),
    }
    train_for = {
        "AM-W-v1": train_v1,
        "AM-W-v2": train_ext,
        "AM-E-v1": train_v1,
        "AM-E-d": train_ext,
        "AM-E-v2": train_ext,
    }
    for name, arm in arms.items():
        t0 = time.perf_counter()
        arm.fit(train_for[name], args.fpr)
        print(f"{name}: umbral {arm.threshold:.4f} (fit {time.perf_counter() - t0:.1f}s)")

    combos = {
        "AM-WE-v1": ("AM-W-v1", "AM-E-v1"),  # original (idéntico a EXP-ANOM-002)
        "AM-WE-d": ("AM-W-v1", "AM-E-d"),  # solo mejora el brazo de eventos
        "AM-WE-v2": ("AM-W-v2", "AM-E-d"),  # ambos con train ampliado (combinado mejorado)
        "AM-WE-rob": ("AM-W-v2", "AM-E-v2"),  # variante con scoring robusto (evaluada)
    }
    all_arm_names = [*arms, *combos]

    # -------- flags por tick + resultados event-level por sesión (una sola pasada)
    flags: dict[str, dict[str, np.ndarray]] = {n: {} for n in all_arm_names}
    ev_reports: dict[tuple[str, str], AnomalyEventReport] = {}
    for sp, sp_sessions in splits.items():
        for s in sp_sessions:
            for name in ("AM-W-v1", "AM-W-v2"):
                flags[name][s.session_id] = arms[name].flag_ticks(s)
            for name in ("AM-E-v1", "AM-E-d", "AM-E-v2"):  # eventos con métricas event-level
                scored = arms[name].score_session(s)
                out = np.zeros(len(s.ticks), dtype=bool)
                items = []
                for ev, _score, flagged in scored:
                    assert ev.seq_start is not None and ev.seq_end is not None
                    if flagged:
                        out[ev.seq_start : ev.seq_end + 1] = True
                    items.append((ev.seq_start, ev.seq_end, flagged))
                flags[name][s.session_id] = out
                rep = ev_reports.setdefault((name, sp), AnomalyEventReport())
                add_session(rep, items, s.y_tick)
            for combo, (w, e) in combos.items():
                flags[combo][s.session_id] = flags[w][s.session_id] | flags[e][s.session_id]

    # ------------------------------------------------ métricas globales y desgloses
    global_rows: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    for name in all_arm_names:
        for sp, sp_sessions in splits.items():
            y_all = np.concatenate([s.y_tick for s in sp_sessions])
            f_all = np.concatenate([flags[name][s.session_id] for s in sp_sessions])
            row: dict[str, Any] = {"arm": name, "split": sp, **tick_metrics(y_all, f_all)}
            episodes = [e for s in sp_sessions if (e := episode_row(s, flags[name][s.session_id]))]
            row["episodes_detected"] = sum(e["detected"] for e in episodes)
            row["episodes_total"] = len(episodes)
            held = [e for e in episodes if e["category"] == "held_out"]
            row["heldout_detected"] = sum(e["detected"] for e in held)
            row["heldout_total"] = len(held)
            delays = [e["delay_s"] for e in episodes if e["delay_s"] is not None]
            row["mean_delay_s"] = round(float(np.mean(delays)), 1) if delays else None
            rep = ev_reports.get((name, sp))
            if rep is not None:
                row["event_precision"] = round(rep.precision, 4)
                row["event_recall"] = round(rep.recall, 4)
                row["event_f1"] = round(rep.f1, 4)
                row["false_events_per_normal_session"] = round(
                    rep.false_events_per_normal_session, 2
                )
            else:  # brazos de ventana: pseudo-eventos = rachas de ticks marcados
                normals = [s for s in sp_sessions if not s.y_tick.any()]
                runs = [window_false_runs(flags[name][s.session_id]) for s in normals]
                row["false_events_per_normal_session"] = (
                    round(float(np.mean(runs)), 2) if runs else 0.0
                )
            global_rows.append(row)
            for s in sp_sessions:
                fl = flags[name][s.session_id]
                ep = episode_row(s, fl)
                scenario_rows.append(
                    {
                        "arm": name,
                        "split": sp,
                        "scenario": s.spec.scenario_id,
                        "category": s.spec.category,
                        "fault": s.spec.fault or "none",
                        "profile": s.spec.driving_profile,
                        **tick_metrics(s.y_tick, fl),
                        "detected": None if ep is None else ep["detected"],
                        "delay_s": None if ep is None else ep["delay_s"],
                    }
                )

    # Desglose por perfil (urbano/autovía/…): agregando ticks de las sesiones del perfil.
    profile_rows: list[dict[str, Any]] = []
    for name in all_arm_names:
        for sp, sp_sessions in splits.items():
            for profile in sorted({s.spec.driving_profile for s in sp_sessions}):
                ss = [s for s in sp_sessions if s.spec.driving_profile == profile]
                y = np.concatenate([s.y_tick for s in ss])
                f = np.concatenate([flags[name][s.session_id] for s in ss])
                profile_rows.append(
                    {"arm": name, "split": sp, "profile": profile, **tick_metrics(y, f)}
                )

    # Fragmentación de contextos (v1 vs ampliado) + estabilidad de señales.
    ctx_stats = {}
    for label, arm_name in (("train_v1", "AM-E-v1"), ("train_ext", "AM-E-v2")):
        arm = arms[arm_name]
        sizes = [b.sample_count for b in arm.baselines.values()]
        ctx_stats[label] = {
            "n_baselines": len(sizes),
            "min_samples": min(sizes) if sizes else 0,
            "median_samples": int(statistics.median(sizes)) if sizes else 0,
            "max_samples": max(sizes) if sizes else 0,
            "min_required": MIN_SAMPLES,
            "unscored_val_test": arm.unscored_events,
            "scored_val_test": arm.scored_events,
        }
    stability = stability_analysis(train_ext, arms["AM-E-v2"])

    summary = {
        "experiment": "EXP-ANOM-003",
        "git_sha": git_sha(REPO_ROOT),
        "target_fpr": args.fpr,
        "dataset": {
            "id": "obd-lab-suite-v1",
            "version": "1.1",
            "train_sessions_v1": len(train_v1),
            "train_sessions_ext": len(train_ext),
            "frozen_splits": "validation/test/held-out idénticos a v1",
        },
        "thresholds": {n: round(a.threshold, 4) for n, a in arms.items()},
        "peak_rss_mb": peak_rss_mb(),
        "context_stats": ctx_stats,
        "stability": stability,
        "global": global_rows,
    }
    (OUT_DIR / "e3_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    for fname, rows in (
        ("e3_results.csv", global_rows),
        ("e3_per_scenario.csv", scenario_rows),
        ("e3_per_profile.csv", profile_rows),
    ):
        with (OUT_DIR / fname).open("w", newline="", encoding="utf-8") as fh:
            fieldnames = sorted({k for r in rows for k in r}, key=lambda k: k != "arm")
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    record_run(RUNS_FILE, {"experiment": "e3_event_refinement", **summary})
    print(json.dumps(global_rows, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
