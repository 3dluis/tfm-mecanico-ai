"""Experimento E4 (EXP-ANOM-005, EXPLORATORIO) — paridad del camino wide (F13).

Pregunta: ¿el camino wide canónico (sesión → VehicleTelemetrySnapshot → matriz columnar →
ventanas → features fs1) produce EXACTAMENTE el mismo dataset y las mismas métricas que el
camino long vigente de F3 (sesión → series → ventanas → features fs1)?

Por qué importa: ADR-0025 exige que la migración de consumidores al snapshot sea gradual y
«solo cuando ambos estén validados». Este experimento ES esa validación para el consumidor
ML: si la paridad es exacta, todo experimento futuro (autoencoders, ventanas como
hiperparámetro, embeddings) puede construirse sobre snapshots sin perder comparabilidad
con EXP-ANOM-001/002/003. No cambia la selección de modelos vigente (LOF sigue SELECTED).

Protocolo (idéntico a E1/ADR-0011): umbral = cuantil (1-FPR) sobre train normal; métricas
point-wise sin point-adjustment + por episodio; held-out jamás interviene en el ajuste.

Punto de composición multi-proyecto permitido (docs/09 §9.4): este script importa obd-lab
(nada) y diagnostic-agent (builder de snapshots) además de ai_models; los paquetes de
dominio siguen sin depender entre sí.

Uso:
    python experiments/e4_wide_parity.py --sessions data/sessions [--seed 42] [--fpr 0.01]
"""

import argparse
import csv
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import WindowDataset, _label, build_dataset
from ai_models.data.snapshot_matrix import (
    count_discarded,
    iter_windows,
    matrix_from_snapshots,
)
from ai_models.evaluation.protocol import event_metrics, point_metrics, threshold_from_normal
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from diagnostic_agent.telemetry.snapshots import build_from_ticks
from mecanico_contracts.features import feature_vector
from mecanico_contracts.session_io import read_session_series

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_CSV = Path(__file__).parent / "e4_results.csv"
PARITY_JSON = Path(__file__).parent / "e4_parity.json"

WINDOW, STRIDE = 60, 30  # congelados para paridad con fs1/arms-freeze-v1


def build_dataset_wide(session_dir: Path, size: int = WINDOW, stride: int = STRIDE):
    """Camino wide: JSONL → ticks → snapshots (sync:v1 identidad) → matriz → ventanas."""
    xs, ys, sids, cats, starts = [], [], [], [], []
    discarded = 0
    build_seconds = 0.0
    for path in sorted(session_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        n = min(len(v) for v in series.values())
        ticks = [{pid: series[pid][i] for pid in series} for i in range(n)]
        t0 = time.perf_counter()
        snapshots, _links = build_from_ticks(
            ticks,
            session_id=header.session_id,
            vehicle_id=header.vehicle_id,
            device_id=header.device_id,
        )
        matrix = matrix_from_snapshots(snapshots)
        build_seconds += time.perf_counter() - t0
        rate = header.scenario.sample_rate_hz if header.scenario else 1.0
        discarded += count_discarded(matrix, size, stride)
        for start_idx, window in iter_windows(matrix, size, stride):
            start_s = start_idx / rate
            xs.append(feature_vector(window))
            ys.append(_label(header, start_s, size / rate))
            sids.append(header.session_id)
            cats.append(header.scenario.category if header.scenario else "unknown")
            starts.append(start_s)
    ds = WindowDataset(
        x=np.asarray(xs, dtype=np.float64),
        y=np.asarray(ys, dtype=np.int64),
        session_ids=sids,
        categories=cats,
        window_starts=starts,
    )
    return ds, discarded, build_seconds


def dataset_parity(long_ds: WindowDataset, wide_ds: WindowDataset) -> dict[str, object]:
    """Paridad estricta entre datasets: misma forma, mismas etiquetas, mismas features."""
    report: dict[str, object] = {
        "shape_long": list(long_ds.x.shape),
        "shape_wide": list(wide_ds.x.shape),
        "shapes_equal": long_ds.x.shape == wide_ds.x.shape,
        "labels_equal": bool(np.array_equal(long_ds.y, wide_ds.y)),
        "sessions_equal": long_ds.session_ids == wide_ds.session_ids,
        "starts_equal": long_ds.window_starts == wide_ds.window_starts,
    }
    if report["shapes_equal"]:
        diff = np.abs(long_ds.x - wide_ds.x)
        report["max_abs_feature_diff"] = float(diff.max()) if diff.size else 0.0
        report["features_identical"] = bool(np.array_equal(long_ds.x, wide_ds.x))
    else:
        report["max_abs_feature_diff"] = None
        report["features_identical"] = False
    return report


def _fit_and_evaluate(det, splits: dict, path_name: str, fpr: float) -> dict[str, object]:
    """Entrena en train, fija umbral (solo train) y evalúa validation/test de un camino."""
    train_ds = splits["train"][path_name]
    assert isinstance(train_ds, WindowDataset)
    t0 = time.perf_counter()
    det.fit(train_ds.x)
    fit_s = time.perf_counter() - t0
    thr = threshold_from_normal(det.scores(train_ds.x), target_fpr=fpr)
    res: dict[str, object] = {"threshold": round(thr, 6), "fit_seconds": round(fit_s, 3)}
    for split in ("validation", "test"):
        ds = splits[split][path_name]
        assert isinstance(ds, WindowDataset)
        t0 = time.perf_counter()
        scores = det.scores(ds.x)
        infer_s = time.perf_counter() - t0
        flagged = scores > thr
        per_cat: dict[str, float] = {}
        for cat in sorted(set(ds.categories)):
            idx = np.array([c == cat for c in ds.categories])
            if cat == "normal":
                per_cat[f"{cat}_fp_rate"] = round(float(flagged[idx].mean()), 4)
            else:
                fault_idx = idx & (ds.y == 1)
                if fault_idx.any():
                    per_cat[f"{cat}_recall"] = round(float(flagged[fault_idx].mean()), 4)
        res[f"{split}_point"] = asdict(point_metrics(ds.y, flagged))
        res[f"{split}_event"] = asdict(event_metrics(ds, flagged))
        res[f"{split}_per_category"] = per_cat
        res[f"{split}_infer_ms_per_window"] = round(infer_s / len(ds.x) * 1000, 3)
    return res


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--suite", default="suite_v1")
    args = parser.parse_args()

    print("Construyendo datasets por ambos caminos…")
    splits: dict[str, dict[str, object]] = {}
    for split in ("train", "validation", "test"):
        long_ds = build_dataset(args.sessions / split)
        wide_ds, discarded, build_s = build_dataset_wide(args.sessions / split)
        parity = dataset_parity(long_ds, wide_ds)
        parity["windows_discarded_by_validity"] = discarded
        parity["snapshot_build_seconds"] = round(build_s, 3)
        splits[split] = {"long": long_ds, "wide": wide_ds, "parity": parity}
        print(
            f"  {split:10s} long {long_ds.x.shape} wide {wide_ds.x.shape} "
            f"identicas={parity['features_identical']} descartadas={discarded}"
        )

    train = splits["train"]["wide"]
    assert isinstance(train, WindowDataset)
    assert not train.y.any(), "el split train debe ser 100% normal (ADR-0011)"

    rows = []
    metric_parity: dict[str, dict[str, object]] = {}
    for det_long, det_wide in zip(
        make_baselines(args.seed), make_baselines(args.seed), strict=True
    ):
        # Camino wide (candidato) y camino long (referencia) con protocolo idéntico.
        results: dict[str, dict[str, object]] = {
            path_name: _fit_and_evaluate(det, splits, path_name, args.fpr)
            for path_name, det in (("long", det_long), ("wide", det_wide))
        }

        comparable = {
            k: (results["long"].get(k), results["wide"].get(k))
            for k in results["long"]
            if not k.endswith(("seconds", "ms_per_window"))
        }
        metrics_equal = all(a == b for a, b in comparable.values())
        metric_parity[det_long.name] = {
            "metrics_equal": metrics_equal,
            "detail": {k: v for k, v in comparable.items() if v[0] != v[1]},
        }

        run_row: dict[str, object] = {
            "experiment": "e4_wide_parity",
            "suite": args.suite,
            "sessions_dir": str(args.sessions),
            "git_sha": git_sha(REPO_ROOT),
            "model": det_long.name,
            "path": "wide(snapshot)+long(referencia)",
            "seed": args.seed,
            "target_fpr": args.fpr,
            "window": WINDOW,
            "stride": STRIDE,
            "wide": results["wide"],
            "long": results["long"],
            "metrics_equal": metrics_equal,
        }
        run_row["peak_rss_mb"] = peak_rss_mb()
        record_run(RUNS_FILE, run_row)
        rows.append(run_row)
        wt = results["wide"]
        print(
            f"{det_long.name:18s} umbral wide={wt['threshold']:>10} "
            f"| metricas identicas long/wide: {metrics_equal}"
        )

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["model", "threshold_wide", "threshold_long", "metrics_equal"])
        for row in rows:
            writer.writerow(
                [
                    row["model"],
                    row["wide"]["threshold"],  # type: ignore[index]
                    row["long"]["threshold"],  # type: ignore[index]
                    row["metrics_equal"],
                ]
            )

    parity_doc = {
        "experiment": "EXP-ANOM-005 (e4_wide_parity)",
        "dataset_parity": {s: splits[s]["parity"] for s in splits},
        "metric_parity": metric_parity,
        "all_equal": all(
            splits[s]["parity"]["features_identical"]
            for s in splits  # type: ignore[index]
        )
        and all(v["metrics_equal"] for v in metric_parity.values()),
    }
    PARITY_JSON.write_text(
        json.dumps(parity_doc, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nParidad global: {parity_doc['all_equal']}  →  {PARITY_JSON.name}")
    return 0 if parity_doc["all_equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
