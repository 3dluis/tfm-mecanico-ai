"""EXP-ANOM-002 — Window vs Event vs Both (R1+E1 fusionados; config exp-anom-002.yaml).

Pregunta: ¿la segmentación de telemetría mediante eventos vehiculares mejora la detección
de anomalías (especialmente multivariables/temporales) frente a ventanas arbitrarias?

Brazos (correspondencia con las etiquetas A2/A3/A6 del plan: ver config; A0–A6
registrados siguen siendo arquitecturas de agente, ADR-0018):
  AM-W       ventanas 60/30 + LOF k=10 (config E1 exacta)
  AM-E       eventos ed:1 + baseline-z por (event_type, context_signature)
  AM-E-NOCTX ablación: ídem SIN context_signature (solo event_type)
  AM-WE      OR por tick de AM-W y AM-E (sin umbral nuevo)

Marco común de evaluación POR TICK: cada brazo marca los ticks que cubren sus
detecciones; ground truth = intervalo real del fallo (spec). Mismos datos/splits/seeds
que EXP-ANOM-001; umbrales solo con train (LOF: cuantil train; eventos: cuantil
leave-one-session-out sobre train normal); held-out intocable (RI1).

Nota de composición: como tests-integration/, los scripts de experiments/ son puntos de
composición multi-proyecto (obd_lab + diagnostic_agent.events + ai_models); el paquete
``ai_models`` sigue sin importar ``diagnostic_agent``.

Uso: python experiments/e2_window_vs_event.py [--fpr 0.01] [--seed 42]
"""

import argparse
import csv
import json
import pickle
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ai_models.anomaly.baselines import make_baselines
from ai_models.evaluation.event_metrics import event_detection_report
from ai_models.evaluation.protocol import threshold_from_normal
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from diagnostic_agent.events import build_baseline, detect_events, event_feature_vector
from diagnostic_agent.events.baseline import (
    MIN_SAMPLES,
    score_against_baseline,
    score_against_baseline_robust,
)
from mecanico_contracts import ScenarioSpec, VehicleEvent
from mecanico_contracts.events_model import EventBaseline, EventFeatureVector
from mecanico_contracts.features import FEATURE_NAMES, extract_features
from obd_lab.events_gt import generate_with_events

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1.yaml"
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
OUT_DIR = Path(__file__).parent
WINDOW, STRIDE = 60, 30
VEH = "veh-suite"


# --------------------------------------------------------------------- datos
@dataclass
class Session:
    spec: ScenarioSpec
    split: str
    ticks: list[dict[str, float]]
    gt_events: list[VehicleEvent]
    y_tick: np.ndarray  # 1 = fallo activo en ese tick (ground truth del spec)

    @property
    def session_id(self) -> str:
        return f"{self.spec.scenario_id}-seed{self.spec.seed}"


def load_suite() -> list[Session]:
    raw = yaml.safe_load(SUITE.read_text(encoding="utf-8"))
    sessions: list[Session] = []
    for split, entries in raw["splits"].items():
        for entry in entries:
            spec = ScenarioSpec(**entry)
            ticks, gt = generate_with_events(spec, vehicle_id=VEH)
            y = np.zeros(len(ticks), dtype=int)
            if spec.fault:
                f0 = int(spec.fault_start_s or 0)
                f1 = int(spec.fault_end_s or spec.duration_s)
                y[f0:f1] = 1
            sessions.append(Session(spec, split, ticks, gt, y))
    return sessions


# ------------------------------------------------------------------ brazo AM-W
@dataclass
class WindowArm:
    threshold: float = 0.0
    model_size_bytes: int = 0
    t_features_s: float = 0.0
    t_scoring_s: float = 0.0

    def __post_init__(self) -> None:
        self.det = next(d for d in make_baselines(42) if d.name == "lof")

    def _features(self, s: Session) -> tuple[np.ndarray, list[int]]:
        rows, starts = [], []
        series = {pid: [t[pid] for t in s.ticks] for pid in s.ticks[0]}
        for start in range(0, len(s.ticks) - WINDOW + 1, STRIDE):
            win = {pid: vals[start : start + WINDOW] for pid, vals in series.items()}
            feats = extract_features(win)
            rows.append([feats.get(n, 0.0) for n in FEATURE_NAMES])
            starts.append(start)
        return np.asarray(rows), starts

    def fit(self, train: list[Session], target_fpr: float) -> None:
        t0 = time.perf_counter()
        xs = [self._features(s)[0] for s in train]
        self.t_features_s += time.perf_counter() - t0
        x = np.vstack(xs)
        t0 = time.perf_counter()
        self.det.fit(x)
        self.threshold = threshold_from_normal(self.det.scores(x), target_fpr)
        self.t_scoring_s += time.perf_counter() - t0
        self.model_size_bytes = len(pickle.dumps(self.det.pipeline))

    def flag_ticks(self, s: Session) -> np.ndarray:
        t0 = time.perf_counter()
        x, starts = self._features(s)
        self.t_features_s += time.perf_counter() - t0
        t0 = time.perf_counter()
        flagged_w = self.det.scores(x) >= self.threshold
        self.t_scoring_s += time.perf_counter() - t0
        out = np.zeros(len(s.ticks), dtype=bool)
        for start, fl in zip(starts, flagged_w, strict=True):
            if fl:
                out[start : start + WINDOW] = True
        return out


# ------------------------------------------------------------------ brazo AM-E
def _event_efv_pairs(
    s: Session, use_context: bool
) -> list[tuple[VehicleEvent, EventFeatureVector]]:
    events = [e for e in detect_events(s.ticks, s.session_id, VEH) if e.event_type != "TRIP"]
    out = []
    for e in events:
        if e.seq_start is None or e.seq_end is None or e.seq_end <= e.seq_start:
            continue
        v = event_feature_vector(e, s.ticks)
        if not use_context:
            v = v.model_copy(update={"context_signature": f"{e.event_type}|ALL"})
        out.append((e, v))
    return out


@dataclass
class EventArm:
    use_context: bool = True
    robust: bool = False  # scoring mediana/percentiles (F9) en lugar de media/σ
    threshold: float = 0.0
    baselines: dict[str, EventBaseline] = field(default_factory=dict)
    model_size_bytes: int = 0
    t_detect_s: float = 0.0
    t_features_s: float = 0.0
    t_scoring_s: float = 0.0
    scored_events: int = 0
    unscored_events: int = 0
    flagged_by_type: dict[str, int] = field(default_factory=dict)
    efv_cache: dict[str, list[tuple[VehicleEvent, EventFeatureVector]]] = field(
        default_factory=dict
    )

    def _session_pairs(self, s: Session) -> list[tuple[VehicleEvent, EventFeatureVector]]:
        if s.session_id not in self.efv_cache:
            t0 = time.perf_counter()
            pairs = _event_efv_pairs(s, self.use_context)
            self.t_features_s += time.perf_counter() - t0
            self.efv_cache[s.session_id] = pairs
        return self.efv_cache[s.session_id]

    @staticmethod
    def _build(efvs: list[EventFeatureVector]) -> dict[str, EventBaseline]:
        groups: dict[str, list[EventFeatureVector]] = {}
        for v in efvs:
            groups.setdefault(v.context_signature, []).append(v)
        return {ctx: build_baseline(vs) for ctx, vs in groups.items() if len(vs) >= MIN_SAMPLES}

    def _score(self, v: EventFeatureVector, baselines: dict[str, EventBaseline]) -> float | None:
        bl = baselines.get(v.context_signature)
        if bl is None:
            return None
        scorer = score_against_baseline_robust if self.robust else score_against_baseline
        zs = scorer(v, bl)
        return max(abs(z) for z in zs.values())

    def fit(self, train: list[Session], target_fpr: float) -> None:
        # Umbral: leave-one-session-out sobre train normal (scores fuera de muestra).
        loso_scores: list[float] = []
        for held in train:
            others = [s for s in train if s.session_id != held.session_id]
            bl = self._build([v for s in others for _, v in self._session_pairs(s)])
            for _, v in self._session_pairs(held):
                score = self._score(v, bl)
                if score is not None:
                    loso_scores.append(score)
        self.threshold = threshold_from_normal(np.asarray(loso_scores), target_fpr)
        # Baselines finales: TODO el train normal.
        t0 = time.perf_counter()
        self.baselines = self._build([v for s in train for _, v in self._session_pairs(s)])
        self.t_scoring_s += time.perf_counter() - t0
        self.model_size_bytes = sum(
            len(b.model_dump_json().encode()) for b in self.baselines.values()
        )

    def score_session(self, s: Session) -> list[tuple[VehicleEvent, float | None, bool]]:
        """(evento, score|None, flag) por evento — base de las métricas event-level (F9)."""
        out = []
        t0 = time.perf_counter()
        for ev, v in self._session_pairs(s):
            score = self._score(v, self.baselines)
            if score is None:
                self.unscored_events += 1
                out.append((ev, None, False))
                continue
            self.scored_events += 1
            flagged = score >= self.threshold
            if flagged:
                self.flagged_by_type[v.event_type] = self.flagged_by_type.get(v.event_type, 0) + 1
            out.append((ev, score, flagged))
        self.t_scoring_s += time.perf_counter() - t0
        return out

    def flag_ticks(self, s: Session) -> np.ndarray:
        out = np.zeros(len(s.ticks), dtype=bool)
        for ev, _score, flagged in self.score_session(s):
            if flagged and ev.seq_start is not None and ev.seq_end is not None:
                out[ev.seq_start : ev.seq_end + 1] = True
        return out


# ----------------------------------------------------------------- evaluación
def tick_metrics(y: np.ndarray, flags: np.ndarray) -> dict[str, float]:
    tp = int(((y == 1) & flags).sum())
    fp = int(((y == 0) & flags).sum())
    fn = int(((y == 1) & ~flags).sum())
    n_norm = int((y == 0).sum())
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(2 * p * r / (p + r), 4) if p + r else 0.0,
        "fpr": round(fp / n_norm, 4) if n_norm else 0.0,
    }


def episode_row(s: Session, flags: np.ndarray) -> dict[str, Any] | None:
    if not s.y_tick.any():
        return None
    idx = np.where(s.y_tick.astype(bool) & flags)[0]
    detected = bool(idx.size)
    delay = float(idx[0] - int(s.spec.fault_start_s or 0)) if detected else None
    return {"detected": detected, "delay_s": delay, "category": s.spec.category}


def main() -> int:  # noqa: PLR0915 — orquestación lineal del experimento (legible tal cual)
    parser = argparse.ArgumentParser()
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    t_pre0 = time.perf_counter()
    sessions = load_suite()
    t_preprocessing = time.perf_counter() - t_pre0
    train = [s for s in sessions if s.split == "train"]
    splits = {sp: [s for s in sessions if s.split == sp] for sp in ("validation", "test")}
    print(f"suite: {len(sessions)} sesiones (train {len(train)})")

    arms: dict[str, Any] = {
        "AM-W": WindowArm(),
        "AM-E": EventArm(use_context=True),
        "AM-E-NOCTX": EventArm(use_context=False),
    }
    fit_times: dict[str, float] = {}
    for name, arm in arms.items():
        t0 = time.perf_counter()
        arm.fit(train, args.fpr)
        fit_times[name] = round(time.perf_counter() - t0, 2)
        print(f"{name}: umbral {arm.threshold:.4f} (fit {fit_times[name]}s)")

    # Flags por tick para cada brazo/sesión; AM-WE = OR de AM-W y AM-E.
    flags: dict[str, dict[str, np.ndarray]] = {n: {} for n in (*arms, "AM-WE")}
    e2e: dict[str, list[float]] = {n: [] for n in (*arms, "AM-WE")}
    for sp_sessions in splits.values():
        for s in sp_sessions:
            for name, arm in arms.items():
                t0 = time.perf_counter()
                flags[name][s.session_id] = arm.flag_ticks(s)
                e2e[name].append(time.perf_counter() - t0)
            flags["AM-WE"][s.session_id] = flags["AM-W"][s.session_id] | flags["AM-E"][s.session_id]
            e2e["AM-WE"].append(e2e["AM-W"][-1] + e2e["AM-E"][-1])

    # ----------------------------------------------------- métricas y desgloses
    global_rows: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    for arm_name in flags:
        for sp, sp_sessions in splits.items():
            y_all = np.concatenate([s.y_tick for s in sp_sessions])
            f_all = np.concatenate([flags[arm_name][s.session_id] for s in sp_sessions])
            row: dict[str, Any] = {"arm": arm_name, "split": sp, **tick_metrics(y_all, f_all)}
            episodes = [
                e for s in sp_sessions if (e := episode_row(s, flags[arm_name][s.session_id]))
            ]
            row["episodes_detected"] = sum(e["detected"] for e in episodes)
            row["episodes_total"] = len(episodes)
            held = [e for e in episodes if e["category"] == "held_out"]
            row["heldout_detected"] = sum(e["detected"] for e in held)
            row["heldout_total"] = len(held)
            delays = [e["delay_s"] for e in episodes if e["delay_s"] is not None]
            row["mean_delay_s"] = round(float(np.mean(delays)), 1) if delays else None
            global_rows.append(row)
            for s in sp_sessions:
                fl = flags[arm_name][s.session_id]
                ep = episode_row(s, fl)
                scenario_rows.append(
                    {
                        "arm": arm_name,
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

    # Calidad del detector de eventos vs GT (independiente de anomalías; por split).
    quality_rows: list[dict[str, Any]] = []
    for sp, sp_sessions in splits.items():
        preds, gts = [], []
        for s in sp_sessions:
            preds.extend(e for e in detect_events(s.ticks, s.session_id, VEH))
            gts.extend(s.gt_events)
        for etype, rep in sorted(event_detection_report(preds, gts).items()):
            quality_rows.append(
                {
                    "split": sp,
                    "event_type": etype,
                    "event_precision": round(rep.precision, 3),
                    "event_recall": round(rep.recall, 3),
                    "event_f1": round(rep.f1, 3),
                    "mean_iou": round(rep.mean_iou, 3),
                    "onset_error": round(rep.mean_onset_error, 1),
                    "end_error": round(rep.mean_end_error, 1),
                    "duration_error": round(rep.mean_duration_error, 1),
                }
            )

    costs = {
        "AM-W": {
            "t_features_s": round(arms["AM-W"].t_features_s, 2),
            "t_scoring_s": round(arms["AM-W"].t_scoring_s, 3),
            "model_size_bytes": arms["AM-W"].model_size_bytes,
            "n_features": len(FEATURE_NAMES),
        },
        "AM-E": {
            "t_features_s": round(arms["AM-E"].t_features_s, 2),
            "t_scoring_s": round(arms["AM-E"].t_scoring_s, 3),
            "model_size_bytes": arms["AM-E"].model_size_bytes,
            "n_features": 20,
            "n_baselines": len(arms["AM-E"].baselines),
            "scored_events": arms["AM-E"].scored_events,
            "unscored_events": arms["AM-E"].unscored_events,
            "flagged_by_type": arms["AM-E"].flagged_by_type,
        },
        "AM-E-NOCTX": {
            "t_features_s": round(arms["AM-E-NOCTX"].t_features_s, 2),
            "t_scoring_s": round(arms["AM-E-NOCTX"].t_scoring_s, 3),
            "model_size_bytes": arms["AM-E-NOCTX"].model_size_bytes,
            "n_baselines": len(arms["AM-E-NOCTX"].baselines),
            "scored_events": arms["AM-E-NOCTX"].scored_events,
            "unscored_events": arms["AM-E-NOCTX"].unscored_events,
            "flagged_by_type": arms["AM-E-NOCTX"].flagged_by_type,
        },
    }
    for name, times in e2e.items():
        costs.setdefault(name, {})["t_e2e_mean_s_per_session"] = round(float(np.mean(times)), 3)

    summary = {
        "experiment": "EXP-ANOM-002",
        "git_sha": git_sha(REPO_ROOT),
        "seed": args.seed,
        "target_fpr": args.fpr,
        "t_preprocessing_s": round(t_preprocessing, 1),
        "peak_rss_mb": peak_rss_mb(),
        "thresholds": {n: round(a.threshold, 4) for n, a in arms.items()},
        "fit_times_s": fit_times,
        "costs": costs,
        "global": global_rows,
        "event_quality": quality_rows,
    }
    (OUT_DIR / "e2_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    for fname, rows in (("e2_results.csv", global_rows), ("e2_per_scenario.csv", scenario_rows)):
        with (OUT_DIR / fname).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    with (OUT_DIR / "e2_event_quality.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(quality_rows[0].keys()))
        writer.writeheader()
        writer.writerows(quality_rows)
    record_run(RUNS_FILE, {"experiment": "e2_window_vs_event", **summary})

    print(json.dumps(global_rows, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
