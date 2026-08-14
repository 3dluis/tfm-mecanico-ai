"""Construcción y verificación de Synthetic Benchmark v2 (F20) — sin entrenar modelos.

Materializa la expansión de cobertura dirigida por los huecos medidos en AUDIT-DATA-001,
**verifica** que los huecos se cierran (con la misma instrumentación de F19, no con una
nueva) y emite el manifiesto versionado del benchmark v2 con referencia explícita a v1.

Regla F20: la expansión está dirigida por cobertura, no por «más datos parece mejor».
Library-first (ADR-0035): la estadística la ponen NumPy/SciPy y el conteo de cobertura
reutiliza `ai_models.audit.detectability`; aquí solo hay orquestación y contrato.

Uso: python experiments/e10_coverage_v2.py --sessions data/sessions
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from e9_anomaly_audit import coverage_audit

from mecanico_contracts import ScenarioSpec
from obd_lab.generate import write_session

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE_V2 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v2_coverage.yaml"
SUITE_V1 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1.yaml"
TRAIN_EXT = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1_train_ext.yaml"
V2_ROOT = REPO_ROOT / "data" / "sessions_v2" / "train"
RESULTS_JSON = Path(__file__).parent / "e10_benchmark_v2.json"

#: Versión del generador y del catálogo con las que se construye v2.
GENERATOR_VERSION = "obd-lab/generate.py @ ADR-0034 (RNG separado, modo heredado disponible)"
ANOMALY_CATALOG_VERSION = "catalog-v1 (8 fallos; sin cambios de inyección en F20)"


def _file_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for p in sorted(paths):
        digest.update(p.read_bytes())
    return digest.hexdigest()


def materialize_v2(out: Path) -> dict[str, Any]:
    """Genera las sesiones de cobertura declaradas en la suite v2 (determinista)."""
    raw = yaml.safe_load(SUITE_V2.read_text(encoding="utf-8"))
    entries = raw["coverage_extension"]
    out.mkdir(parents=True, exist_ok=True)
    targets: dict[str, list[str]] = {}
    for entry in entries:
        spec_fields = {k: v for k, v in entry.items() if k != "coverage_target"}
        spec = ScenarioSpec(**spec_fields)
        targets[spec.scenario_id] = entry["coverage_target"].split(",")
        target_file = out / f"{spec.scenario_id}-seed{spec.seed}.jsonl"
        if not target_file.exists():
            write_session(spec, out)
    files = sorted(out.glob("*.jsonl"))
    return {
        "n_sessions": len(files),
        "seeds": sorted(e["seed"] for e in entries),
        "total_duration_s": sum(e["duration_s"] for e in entries),
        "coverage_targets": targets,
        "dataset_hash": _file_hash(files),
        "provenance": "SIMULATED (obd-lab; determinista por semilla)",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    args = parser.parse_args()
    t0 = time.perf_counter()

    print("cobertura ANTES (v1)…", flush=True)
    before = coverage_audit(
        {
            "train": args.sessions / "train",
            "train_v11": REPO_ROOT / "data" / "sessions_v11" / "train",
            "test": args.sessions / "test",
        }
    )
    print("materializando la expansión v2…", flush=True)
    v2_meta = materialize_v2(V2_ROOT)
    print(
        f"  {v2_meta['n_sessions']} sesiones · {v2_meta['total_duration_s'] / 3600:.1f} h",
        flush=True,
    )

    print("cobertura DESPUÉS (v1.1 + expansión v2)…", flush=True)
    after = coverage_audit(
        {
            "train": REPO_ROOT / "data" / "sessions_v11" / "train",
            "train_v2": V2_ROOT,
            "test": args.sessions / "test",
        }
    )
    # cobertura combinada real del train de v2 = v1.1 + expansión
    combined: dict[str, Any] = {}
    for behaviour, row in after["matrix"].items():
        total = row["train"]["count"] + row["train_v2"]["count"]
        combined[behaviour] = {
            "train_v11": row["train"]["count"],
            "expansion_v2": row["train_v2"]["count"],
            "train_v2_total": total,
            "test": row["test"]["count"],
            "was_gap_in_v1": behaviour in before["coverage_gaps"],
            "still_gap": bool(total <= 2 and row["test"]["count"] > 0),
        }
    closed = [b for b, r in combined.items() if r["was_gap_in_v1"] and not r["still_gap"]]
    remaining = [b for b, r in combined.items() if r["still_gap"]]

    manifest = {
        "benchmark_version": "synthetic-benchmark-v2",
        "extends": "synthetic-benchmark-v1 (suite_v1.yaml + suite_v1_train_ext.yaml)",
        "supersedes": None,
        "v1_untouched": True,
        "generator_version": GENERATOR_VERSION,
        "anomaly_catalog_version": ANOMALY_CATALOG_VERSION,
        "rng_policy": {
            "vehicle_behavior_seed": "ScenarioSpec.seed",
            "anomaly_injection_seed": "ScenarioSpec.anomaly_seed (ADR-0034)",
            "note": (
                "los escenarios normales de la expansión no inyectan anomalía; los "
                "escenarios con fallo del benchmark v2 declararán ambas semillas"
            ),
        },
        "sampling": {"sample_rate_hz": 1.0, "window": 60, "stride": 30},
        "pid_schema": "CANONICAL_PIDS (12) · features fs1 (42) — sin cambios respecto a v1",
        "config_hash": hashlib.sha256(SUITE_V2.read_bytes()).hexdigest(),
        "expansion": v2_meta,
        "normal_coverage_profile": combined,
        "gaps_closed": sorted(closed),
        "gaps_remaining": sorted(remaining),
        "coverage_before_v1": before["coverage_gaps"],
        "validity_note": (
            "EXPLORATORIO; entorno emulado/sintético. El test histórico NO se modifica: "
            "el distribution shift documentado en AUDIT-DATA-001 se conserva como evidencia."
        ),
    }
    manifest["total_runtime_s"] = round(time.perf_counter() - t0, 1)
    RESULTS_JSON.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print("\nhuecos cerrados:", closed)
    print("huecos que persisten:", remaining)
    print(f"manifiesto → {RESULTS_JSON.name} ({manifest['total_runtime_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
