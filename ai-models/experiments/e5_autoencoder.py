"""Experimento E5 (EXP-ANOM-006, EXPLORATORIO) — autoencoder vs LOF sobre el camino wide.

Protocolo ML v1 §5 (nivel 2) e hipótesis HX-ML-2: ¿un autoencoder denso pequeño iguala o
supera a LOF k=10 con el mismo protocolo (ADR-0011)? Dimensiones del experimento:

- brazos: autoencoder_standard, autoencoder_robust (comparación de scaler §4) y LOF k=10
  re-entrenado por configuración como comparador; a 60/30 los números de LOF son los del
  brazo congelado (paridad verificada en EXP-ANOM-005).
- ventana como hiperparámetro: {10, 30, 60, 120} s, stride = size/2 (§2).
- resultados por anomalía (fault del catálogo) y por severidad (suite exploratoria
  suite_f14_severity.yaml, SOLO evaluación, semillas 412-425).
- embeddings latentes del AE a 60/30 con estadísticas preliminares de separabilidad
  (entrada futura de EXP-PAT-*; aquí NO se afirma descubrimiento).

Reglas: umbral = cuantil (1-FPR) sobre train normal; el train congelado de suite v1 es el
ÚNICO conjunto de ajuste; las sesiones de severidad jamás ajustan nada; los held-out no
intervienen en el ajuste (RI1).

Uso:
    python experiments/e5_autoencoder.py --sessions data/sessions \
        [--severity-out data/sessions_f14sev] [--seed 42] [--fpr 0.01]
"""

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))  # patrón e3: reutilizar módulos de experimentos

from e4_wide_parity import build_dataset_wide
from sklearn.metrics import silhouette_score

from ai_models.anomaly.autoencoder import AutoencoderDetector
from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import WindowDataset
from ai_models.evaluation.protocol import (
    event_metrics,
    point_metrics,
    threshold_from_normal,
)
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.session_io import read_session_header
from obd_lab.generate import write_session
from obd_lab.scenarios.loader import load_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_JSON = Path(__file__).parent / "e5_results.json"
TMP_DIR = Path(__file__).parent / "tmp"
SEVERITY_SUITE = REPO_ROOT / "obd-lab" / "scenarios" / "suite_f14_severity.yaml"

WINDOWS = (10, 30, 60, 120)
CANON = 60  # configuración congelada (fs1) para severidad + embeddings


def _fault_of(session_dir: Path) -> dict[str, tuple[str | None, dict[str, float]]]:
    """session_id → (fault, fault_params) leyendo solo cabeceras."""
    out: dict[str, tuple[str | None, dict[str, float]]] = {}
    for path in sorted(session_dir.glob("*.jsonl")):
        header = read_session_header(path)
        sc = header.scenario
        out[header.session_id] = (sc.fault if sc else None, dict(sc.fault_params) if sc else {})
    return out


def _make_lof(seed: int):
    det = next(d for d in make_baselines(seed) if d.name == "lof")
    return det


def _eval_split(det, thr: float, ds: WindowDataset, faults: dict) -> dict[str, object]:
    t0 = time.perf_counter()
    scores = det.scores(ds.x)
    infer_s = time.perf_counter() - t0
    flagged = scores > thr
    res: dict[str, object] = {
        "point": asdict(point_metrics(ds.y, flagged)),
        "event": asdict(event_metrics(ds, flagged)),
        "infer_ms_per_window": round(infer_s / len(ds.x) * 1000, 3),
    }
    per_cat: dict[str, float] = {}
    for cat in sorted(set(ds.categories)):
        idx = np.array([c == cat for c in ds.categories])
        if cat == "normal":
            per_cat[f"{cat}_fp_rate"] = round(float(flagged[idx].mean()), 4)
        else:
            fault_idx = idx & (ds.y == 1)
            if fault_idx.any():
                per_cat[f"{cat}_recall"] = round(float(flagged[fault_idx].mean()), 4)
    res["per_category"] = per_cat
    # por anomalía concreta (fault del catálogo)
    per_fault: dict[str, float] = {}
    fault_names = [faults.get(s, (None, {}))[0] for s in ds.session_ids]
    for fname in sorted({f for f in fault_names if f}):
        idx = np.array([f == fname for f in fault_names]) & (ds.y == 1)
        if idx.any():
            per_fault[fname] = round(float(flagged[idx].mean()), 4)
    res["per_fault_recall"] = per_fault
    return res


def _severity_eval(det, thr: float, sev_dir: Path) -> dict[str, object]:
    """Recall por escenario de severidad + FPR en los controles normales (60/30)."""
    ds, _disc, _t = build_dataset_wide(sev_dir, size=CANON, stride=CANON // 2)
    scores = det.scores(ds.x)
    flagged = scores > thr
    headers = _fault_of(sev_dir)
    out: dict[str, object] = {}
    for sid in sorted(set(ds.session_ids)):
        idx = np.array([s == sid for s in ds.session_ids])
        fault, params = headers[sid]
        if fault is None:
            out[sid] = {"fault": None, "fp_rate": round(float(flagged[idx].mean()), 4)}
        else:
            fidx = idx & (ds.y == 1)
            out[sid] = {
                "fault": fault,
                "params": params,
                "recall": round(float(flagged[fidx].mean()), 4) if fidx.any() else None,
                "episode_detected": bool(flagged[fidx].any()) if fidx.any() else False,
            }
    return out


def _embeddings_summary(ae, args, test_faults: dict) -> dict[str, object]:
    """Separabilidad preliminar del espacio latente (60/30); el descubrimiento es EXP-PAT-*."""
    test60, _dd, _tt = build_dataset_wide(args.sessions / "test", CANON, CANON // 2)
    z = ae.embed(test60.x)
    fault_names = [test_faults.get(s, (None, {}))[0] or "normal" for s in test60.session_ids]
    pairs = zip(fault_names, test60.y, strict=True)
    labels = np.array([f if y == 1 else "normal" for f, y in pairs])
    sil = None
    if len(set(labels)) > 1:
        sil = float(silhouette_score(z, labels, random_state=args.seed))
    anom = labels != "normal"
    sil_anom = None
    if anom.sum() > 2 and len(set(labels[anom])) > 1:
        sil_anom = float(silhouette_score(z[anom], labels[anom], random_state=args.seed))
    TMP_DIR.mkdir(exist_ok=True)
    np.savez_compressed(TMP_DIR / "e5_embeddings.npz", z=z, labels=labels, y=test60.y)
    return {
        "arm": "autoencoder_standard@60/30",
        "n_windows": int(z.shape[0]),
        "latent_dim": int(z.shape[1]),
        "classes": sorted(set(labels)),
        "silhouette_all_vs_normal": round(sil, 4) if sil is not None else None,
        "silhouette_between_faults_only": round(sil_anom, 4) if sil_anom is not None else None,
        "artifact": "experiments/tmp/e5_embeddings.npz (no versionado; regenerable por semilla)",
        "nota": (
            "estadística preliminar de separabilidad; la evaluación de descubrimiento de "
            "patrones (clustering, estabilidad, criterio de 8 condiciones) es EXP-PAT-001"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--severity-out", type=Path, default=REPO_ROOT / "data" / "sessions_f14sev")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    args = parser.parse_args()

    # 1. sesiones de severidad (deterministas por semilla; solo evaluación)
    sev_dir = args.severity_out / "test"
    sev_dir.mkdir(parents=True, exist_ok=True)
    suite = load_suite(SEVERITY_SUITE)
    for spec in suite["test"]:
        target = sev_dir / f"{spec.scenario_id}-seed{spec.seed}.jsonl"
        if not target.exists():
            write_session(ScenarioSpec(**spec.model_dump()), sev_dir)
    print(f"severidad: {len(list(sev_dir.glob('*.jsonl')))} sesiones en {sev_dir}")

    faults_by_split = {s: _fault_of(args.sessions / s) for s in ("train", "validation", "test")}
    results: dict[str, object] = {"windows": {}, "severity": {}, "embeddings": {}}

    canon_dets: dict[str, tuple[object, float]] = {}
    for window in WINDOWS:
        stride = window // 2
        train, _d1, _t1 = build_dataset_wide(args.sessions / "train", window, stride)
        val, _d2, _t2 = build_dataset_wide(args.sessions / "validation", window, stride)
        test, _d3, _t3 = build_dataset_wide(args.sessions / "test", window, stride)
        assert not train.y.any(), "train debe ser 100% normal (ADR-0011)"
        shapes = {
            "train": list(train.x.shape),
            "val": list(val.x.shape),
            "test": list(test.x.shape),
        }
        wres: dict[str, object] = {"shapes": shapes}
        arms = [
            AutoencoderDetector(seed=args.seed, scaler_kind="standard"),
            AutoencoderDetector(seed=args.seed, scaler_kind="robust"),
            _make_lof(args.seed),
        ]
        for det in arms:
            t0 = time.perf_counter()
            det.fit(train.x)
            fit_s = time.perf_counter() - t0
            thr = threshold_from_normal(det.scores(train.x), target_fpr=args.fpr)
            arm_res: dict[str, object] = {
                "threshold": round(float(thr), 6),
                "fit_seconds": round(fit_s, 3),
                "n_parameters": getattr(det, "n_parameters", None),
                "validation": _eval_split(det, thr, val, faults_by_split["validation"]),
                "test": _eval_split(det, thr, test, faults_by_split["test"]),
            }
            wres[det.name] = arm_res
            if window == CANON:
                canon_dets[det.name] = (det, thr)
            record_run(
                RUNS_FILE,
                {
                    "experiment": "e5_autoencoder",
                    "git_sha": git_sha(REPO_ROOT),
                    "model": det.name,
                    "window": window,
                    "stride": stride,
                    "seed": args.seed,
                    "target_fpr": args.fpr,
                    **{k: v for k, v in arm_res.items() if k != "n_parameters"},
                    "n_parameters": arm_res["n_parameters"],
                    "peak_rss_mb": peak_rss_mb(),
                },
            )
            tp = arm_res["test"]["point"]  # type: ignore[index]
            print(
                f"w={window:3d} {det.name:22s} thr={thr:10.5f} "
                f"test F1={tp['f1']:.3f} FPR={tp['fp_rate_normal']:.3f} "
                f"held={arm_res['test']['per_category'].get('held_out_recall', 0.0)}"  # type: ignore[index]
            )
        results["windows"][str(window)] = wres  # type: ignore[index]

    # 3. severidad (detectores de la configuración canónica 60/30)
    for name, (det, thr) in canon_dets.items():
        results["severity"][name] = _severity_eval(det, thr, sev_dir)  # type: ignore[index]

    # 4. embeddings preliminares (AE standard, 60/30) — NO es EXP-PAT-*
    ae, _thr = canon_dets["autoencoder_standard"]
    results["embeddings"] = _embeddings_summary(ae, args, faults_by_split["test"])

    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nresultados → {RESULTS_JSON.name}; embeddings → tmp/e5_embeddings.npz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
