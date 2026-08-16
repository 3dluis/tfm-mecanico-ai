"""Construcción y verificación de Synthetic Benchmark v3 (F22) — sin entrenar modelos.

Diferencia esencial con `e10_coverage_v2.py` (y razón de que este script exista): la
cobertura se **mide en el espacio de features que consume el modelo** y el criterio es
*a priori* y **bloqueante**. Si el banco generado no alcanza el criterio, este script NO
emite manifiesto y sale con código ≠ 0: no existe la opción de declarar cerrado un hueco
que no se ha cerrado, que es exactamente lo que ocurrió con v2 (informe F21).

Se reporta también la cobertura **declarada** (contador de sesión de F19/F20) junto a la
**efectiva**, para dejar por escrito la magnitud de la discrepancia entre ambos
instrumentos: esa comparación es el resultado metodológico de la fase.

Library-first (ADR-0035): la estadística la ponen NumPy/SciPy, el criterio lo pone
`ai_models.audit.coverage` (instrumento único, compartido con el runner de la réplica) y
el conteo de sesión reutiliza `e9_anomaly_audit.coverage_audit`. Aquí solo hay
orquestación y contrato.

Uso: python experiments/e12_coverage_v3.py --sessions data/sessions
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from e4_wide_parity import build_dataset_wide
from e6_ae_v2 import CANON_S, CANON_W, materialize_v11
from e9_anomaly_audit import coverage_audit

from ai_models.audit.coverage import (
    LTFT_FEATURE,
    check_coverage_criterion,
    ltft_level_coverage,
)
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import FEATURE_NAMES
from obd_lab.generate import write_session

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE_V3 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v3_coverage.yaml"
V11_ROOT = REPO_ROOT / "data" / "sessions_v11"
V2_TRAIN = REPO_ROOT / "data" / "sessions_v2" / "train"
V3_ROOT = REPO_ROOT / "data" / "sessions_v3" / "train"
RESULTS_JSON = Path(__file__).parent / "e12_benchmark_v3.json"

#: Versión del generador y del catálogo con las que se construye v3 (sin cambios: F22 no
#: toca ni el generador ni la inyección — solo la composición del train).
GENERATOR_VERSION = "obd-lab/generate.py @ ADR-0034 (RNG separado, modo heredado disponible)"
ANOMALY_CATALOG_VERSION = "catalog-v1 (8 fallos; sin cambios de inyección en F22)"


def _file_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for p in sorted(paths):
        digest.update(p.read_bytes())
    return digest.hexdigest()


def materialize_v3(out: Path) -> dict[str, Any]:
    """Genera las sesiones declaradas en la suite v3 (determinista por semilla)."""
    raw = yaml.safe_load(SUITE_V3.read_text(encoding="utf-8"))
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
        "criterion_declared_in": str(SUITE_V3.relative_to(REPO_ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    args = parser.parse_args()
    t0 = time.perf_counter()

    criterion = yaml.safe_load(SUITE_V3.read_text(encoding="utf-8"))["benchmark"][
        "coverage_criterion"
    ]
    min_pos = float(criterion["positive_level_share_min"])
    min_neg = float(criterion["negative_level_share_min"])
    print(
        f"criterio a priori: nivel+ ≥ {min_pos} y nivel− ≥ {min_neg} "
        f"sobre las ventanas de train ({LTFT_FEATURE})",
        flush=True,
    )

    materialize_v11(args.sessions, V11_ROOT)  # idempotente
    print("materializando la expansión v3…", flush=True)
    v3_meta = materialize_v3(V3_ROOT)
    print(
        f"  {v3_meta['n_sessions']} sesiones · {v3_meta['total_duration_s'] / 3600:.1f} h",
        flush=True,
    )

    # ---------------------------------------- cobertura EFECTIVA (espacio de features)
    print("midiendo cobertura EFECTIVA en el espacio de features…", flush=True)
    ltft_idx = FEATURE_NAMES.index(LTFT_FEATURE)
    train11, _, _ = build_dataset_wide(V11_ROOT / "train", CANON_W, CANON_S)
    exp_v3, _, _ = build_dataset_wide(V3_ROOT, CANON_W, CANON_S)
    x_v3 = np.vstack([train11.x, exp_v3.x])
    effective = {
        "train_v11": ltft_level_coverage(train11.x, ltft_idx),
        "expansion_v3": ltft_level_coverage(exp_v3.x, ltft_idx),
        "train_v3_total": ltft_level_coverage(x_v3, ltft_idx),
    }
    if V2_TRAIN.is_dir() and any(V2_TRAIN.glob("*.jsonl")):
        exp_v2, _, _ = build_dataset_wide(V2_TRAIN, CANON_W, CANON_S)
        effective["expansion_v2_para_comparar"] = ltft_level_coverage(exp_v2.x, ltft_idx)
    for name, cov in effective.items():
        print(
            f"  {name}: nivel+ {cov['positive_level_share']} · "
            f"nivel− {cov['negative_level_share']} · max {cov.get('max')}",
            flush=True,
        )

    verdict = check_coverage_criterion(effective["train_v3_total"], min_pos, min_neg)

    # -------------------- cobertura DECLARADA (contador de sesión de F19/F20), informativa
    print("midiendo cobertura DECLARADA (contador de sesión F19/F20, informativa)…", flush=True)
    declared = coverage_audit(
        {"train": V11_ROOT / "train", "train_v3": V3_ROOT, "test": args.sessions / "test"}
    )

    manifest = {
        "benchmark_version": "synthetic-benchmark-v3",
        "extends": "synthetic-benchmark-v1 (suite_v1.yaml + suite_v1_train_ext.yaml)",
        "supersedes": None,
        "replaces_expansion_of": "synthetic-benchmark-v2 (cobertura declarada pero no efectiva)",
        "v1_v2_untouched": True,
        "generator_version": GENERATOR_VERSION,
        "anomaly_catalog_version": ANOMALY_CATALOG_VERSION,
        "sampling": {"sample_rate_hz": 1.0, "window": CANON_W, "stride": CANON_S},
        "pid_schema": "CANONICAL_PIDS (12) · features fs1 (42) — sin cambios respecto a v1/v2",
        "config_hash": hashlib.sha256(SUITE_V3.read_bytes()).hexdigest(),
        "expansion": v3_meta,
        "effective_coverage": effective,
        "coverage_criterion": verdict,
        "declared_coverage_session_counter": {
            "gaps": declared["coverage_gaps"],
            "note": (
                "instrumento de F19/F20 (sesión, binario). Se reporta SOLO para dejar "
                "constancia de la discrepancia con la cobertura efectiva: es el instrumento "
                "que produjo el falso cierre de hueco en v2 (informe F21 §3)."
            ),
        },
        "validity_note": (
            "EXPLORATORIO; entorno emulado/sintético. El test histórico NO se modifica: el "
            "distribution shift documentado en AUDIT-DATA-001 se conserva como evidencia."
        ),
        "total_runtime_s": round(time.perf_counter() - t0, 1),
    }

    if not verdict["passes"]:
        print("\ncriterio de cobertura NO alcanzado:", flush=True)
        print(f"  nivel+ {verdict['measured']['positive_level_share']} (exigido ≥ {min_pos})")
        print(f"  nivel− {verdict['measured']['negative_level_share']} (exigido ≥ {min_neg})")
        failed = RESULTS_JSON.with_name("e12_benchmark_v3_FAILED.json")
        failed.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        print(f"NO se emite manifiesto de banco válido. Diagnóstico → {failed.name}")
        print("El banco v3 queda RECHAZADO; la réplica no debe ejecutarse sobre él.")
        return 1

    RESULTS_JSON.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print(
        f"\ncriterio ALCANZADO · nivel+ {verdict['measured']['positive_level_share']} "
        f"· nivel− {verdict['measured']['negative_level_share']}"
    )
    print(f"manifiesto → {RESULTS_JSON.name} ({manifest['total_runtime_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
