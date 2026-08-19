"""E12 (F25, instrumental) — materialización y congelación de `obd-lab-suite-v2`.

No es un experimento: es la generación del banco confirmatorio del pre-registro
(`prereg-v1.0`, §3.2), con su criterio bloqueante de cobertura efectiva y su congelación
por hash. Ninguna métrica de modelo interviene en ninguna decisión de este runner.

Por réplica (1-10): genera las 37 sesiones declaradas en
``obd-lab/scenarios/suite_v2/replica-XX.yaml`` (semillas del bloque reservado, ADR-0034
para los fallos), construye las ventanas fs1 del TRAIN por el camino wide canónico y
aplica el criterio de cobertura efectiva con el instrumento único
(``ai_models.audit.coverage``): si ``positive_level_share < 0.03`` o
``negative_level_share < 0.03``, re-genera la réplica con la escalada de duración
declarada (7 200 s, luego 9 000 s) **dentro del mismo bloque de semillas** — se alarga la
señal, jamás se seleccionan semillas. Tras 2 escaladas sin éxito la réplica queda
INVÁLIDA y el freeze falla (no se «repesca»).

Salida: sesiones en ``data/suite_v2/replica-XX/{train,validation,test}`` (no versionadas)
+ manifiesto congelado ``ai-models/configs/suite-v2-freeze.json`` (versionado) + resumen.

Uso: python experiments/e12_suite_v2.py [--replicas 1-10]
"""

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from e4_wide_parity import build_dataset_wide

from ai_models.audit.coverage import LTFT_FEATURE, ltft_level_coverage
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import FEATURE_NAMES
from obd_lab.generate import write_session

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from freeze_benchmark import partition_manifest  # noqa: E402
from gen_suite_v2 import replica_spec, write_all  # noqa: E402

SUITE_DIR = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v2"
DATA_ROOT = REPO_ROOT / "data" / "suite_v2"
FREEZE_OUT = REPO_ROOT / "ai-models" / "configs" / "suite-v2-freeze.json"
RESULTS_JSON = Path(__file__).parent / "e12_suite_v2.json"

CANON_W, CANON_S = 60, 30
COVERAGE_MIN = 0.03
MAX_ESCALATION = 2


def materialize_split(entries: list[dict[str, Any]], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        spec = ScenarioSpec(**entry)
        target = out / f"{spec.scenario_id}-seed{spec.seed}.jsonl"
        if not target.exists():
            write_session(spec, out)


def materialize_replica(r: int, escalation: int) -> Path:
    doc = replica_spec(r, escalation)
    root = DATA_ROOT / f"replica-{r:02d}"
    if root.exists():
        shutil.rmtree(root)  # la escalada regenera TODO el split de la réplica
    for split in ("train", "validation", "test"):
        materialize_split(doc[split], root / split)
    return root


def train_coverage(root: Path) -> dict[str, float]:
    ds, _, _ = build_dataset_wide(root / "train", CANON_W, CANON_S)
    return ltft_level_coverage(ds.x, FEATURE_NAMES.index(LTFT_FEATURE))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicas", default="1-10")
    args = parser.parse_args()
    first, last = (
        (int(x) for x in args.replicas.split("-"))
        if "-" in args.replicas
        else (
            int(args.replicas),
            int(args.replicas),
        )
    )
    t0 = time.perf_counter()

    escalations: dict[int, int] = {}
    replicas_report: dict[str, Any] = {}
    partitions = []
    invalid: list[int] = []

    for r in range(first, last + 1):
        esc = 0
        while True:
            print(f"réplica {r:02d} (escalada {esc}): materializando…", flush=True)
            root = materialize_replica(r, esc)
            cov = train_coverage(root)
            print(
                f"  cobertura train: +{cov['positive_level_share']:.4f} / "
                f"-{cov['negative_level_share']:.4f} ({int(cov['n_windows'])} ventanas)",
                flush=True,
            )
            ok = (
                cov["positive_level_share"] >= COVERAGE_MIN
                and cov["negative_level_share"] >= COVERAGE_MIN
            )
            if ok or esc >= MAX_ESCALATION:
                break
            esc += 1
        escalations[r] = esc
        replicas_report[f"replica-{r:02d}"] = {
            "escalation": esc,
            "coverage": cov,
            "coverage_ok": ok,
        }
        if not ok:
            invalid.append(r)
            continue
        for split in ("train", "validation", "test"):
            partitions.append(partition_manifest(f"replica-{r:02d}/{split}", root / split))

    # los YAML commiteados reflejan la escalada final REAL de cada réplica
    write_all(SUITE_DIR, escalations)

    import hashlib

    glob_digest = hashlib.sha256()
    for part in partitions:
        glob_digest.update(part["name"].encode())
        glob_digest.update(part["aggregate_semantic_sha256"].encode())
    manifest = {
        "benchmark_version": "obd-lab-suite-v2",
        "prereg": "prereg-v1.0 §3.2 (congelado antes de generar)",
        "frozen": len(invalid) == 0,
        "coverage_criterion": {
            "rule": (
                "positive_level_share >= 0.03 AND negative_level_share >= 0.03 (train, por réplica)"
            ),
            "instrument": "ai_models.audit.coverage.ltft_level_coverage (instrumento único)",
            "escalation_policy": (
                "5400 → 7200 → 9000 s en urbano/autovía de train; mismo bloque de semillas"
            ),
        },
        "replicas": replicas_report,
        "invalid_replicas": invalid,
        "benchmark_sha256": glob_digest.hexdigest(),
        "partitions": partitions,
    }
    FREEZE_OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    RESULTS_JSON.write_text(
        json.dumps(
            {
                "runner": "e12_suite_v2 (instrumental)",
                "replicas": replicas_report,
                "invalid_replicas": invalid,
                "total_runtime_s": round(time.perf_counter() - t0, 1),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    if invalid:
        print(f"FREEZE FALLIDO: réplicas inválidas {invalid}")
        return 1
    print(
        f"suite-v2 CONGELADA: {len(partitions)} particiones · "
        f"hash {manifest['benchmark_sha256'][:16]}… ({round(time.perf_counter() - t0, 1)}s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
