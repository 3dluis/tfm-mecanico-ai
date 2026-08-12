"""Experimento E1 — Baselines de detección sobre la suite v1 (ADR-0011).

Protocolo:
  1. train  (solo normal)      -> fit de detectores + umbral (cuantil FPR objetivo)
  2. validation (fallos conocidos) -> selección/comparación de modelos
  3. test   (held-out + conocidos con semilla nueva) -> evaluación final

Uso:
    python experiments/e1_baselines.py --sessions <dir_sesiones> [--seed 42] [--fpr 0.01]

Registra cada run en experiments/runs.jsonl y vuelca la tabla a experiments/e1_results.csv.
"""

import argparse
import csv
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import build_dataset
from ai_models.evaluation.protocol import event_metrics, point_metrics, threshold_from_normal
from ai_models.tracking import git_sha, peak_rss_mb, record_run

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_CSV = Path(__file__).parent / "e1_results.csv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--suite", default="suite_v1")
    args = parser.parse_args()

    print("Cargando datasets…")
    train = build_dataset(args.sessions / "train")
    val = build_dataset(args.sessions / "validation")
    test = build_dataset(args.sessions / "test")
    assert not train.y.any(), "el split train debe ser 100% normal (ADR-0011)"
    print(f"  train {train.x.shape} | val {val.x.shape} | test {test.x.shape}")

    rows = []
    for det in make_baselines(args.seed):
        t0 = time.perf_counter()
        det.fit(train.x)
        fit_s = time.perf_counter() - t0

        thr = threshold_from_normal(det.scores(train.x), target_fpr=args.fpr)

        run_row: dict[str, object] = {
            "experiment": "e1_baselines",
            "suite": args.suite,
            "sessions_dir": str(args.sessions),
            "git_sha": git_sha(REPO_ROOT),
            "model": det.name,
            "model_version": "0.1.0",
            "params": (getattr(det, "pipeline", None) and repr(det.pipeline.named_steps["model"]))
            or "median/MAD",
            "seed": args.seed,
            "target_fpr": args.fpr,
            "threshold": round(thr, 6),
            "fit_seconds": round(fit_s, 3),
        }

        for split_name, ds in [("validation", val), ("test", test)]:
            t0 = time.perf_counter()
            scores = det.scores(ds.x)
            infer_s = time.perf_counter() - t0
            flagged = scores > thr
            pm = point_metrics(ds.y, flagged)
            em = event_metrics(ds, flagged)

            # métricas por categoría de escenario (clave para la PI: held-out vs conocido)
            per_cat: dict[str, float] = {}
            for cat in sorted(set(ds.categories)):
                idx = np.array([c == cat for c in ds.categories])
                if cat == "normal":
                    per_cat[f"{cat}_fp_rate"] = round(float(flagged[idx].mean()), 4)
                else:
                    fault_idx = idx & (ds.y == 1)
                    if fault_idx.any():
                        per_cat[f"{cat}_recall"] = round(float(flagged[fault_idx].mean()), 4)

            run_row[f"{split_name}_point"] = asdict(pm)
            run_row[f"{split_name}_event"] = asdict(em)
            run_row[f"{split_name}_per_category"] = per_cat
            run_row[f"{split_name}_infer_ms_per_window"] = round(infer_s / len(ds.x) * 1000, 3)

        run_row["peak_rss_mb"] = peak_rss_mb()
        record_run(RUNS_FILE, run_row)
        rows.append(run_row)

        vp = run_row["validation_point"]
        tp = run_row["test_point"]
        print(
            f"{det.name:18s} umbral={thr:8.3f} | val F1={vp['f1']:.3f}"
            f" FPR={vp['fp_rate_normal']:.3f}"
            f" | test F1={tp['f1']:.3f} FPR={tp['fp_rate_normal']:.3f}"
            f" | held-out recall={run_row['test_per_category'].get('held_out_recall', 0.0):.3f}"
            f" | {run_row['test_infer_ms_per_window']:.2f} ms/ventana"
        )

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "model",
                "threshold",
                "val_f1",
                "val_fpr",
                "test_f1",
                "test_fpr",
                "test_recall_known",
                "test_recall_heldout",
                "episodes_detected",
                "mean_delay_s",
                "infer_ms_per_window",
                "fit_s",
                "peak_rss_mb",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r["model"],
                    r["threshold"],
                    r["validation_point"]["f1"],
                    r["validation_point"]["fp_rate_normal"],
                    r["test_point"]["f1"],
                    r["test_point"]["fp_rate_normal"],
                    r["test_per_category"].get("known_fault_recall", ""),
                    r["test_per_category"].get("held_out_recall", ""),
                    f"{r['test_event']['episodes_detected']}/{r['test_event']['episodes_total']}",
                    r["test_event"]["mean_detection_delay_s"],
                    r["test_infer_ms_per_window"],
                    r["fit_seconds"],
                    r["peak_rss_mb"],
                ]
            )
    print(f"\nResultados en {RESULTS_CSV} y registro en {RUNS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
