"""Congelación de un banco sintético — ancla de reproducibilidad (F21).

Emite un manifiesto **inmutable** con el hash SHA-256 de cada sesión y de cada partición,
más los metadatos declarados en la cabecera (perfil, semilla, duración, fallo). El
manifiesto se versiona en Git aunque los datos NO (``/data/`` está en .gitignore porque es
regenerable de forma determinista): el hash es la prueba de que una regeneración futura
produce EXACTAMENTE el mismo banco.

Congelar un banco significa: a partir de este punto, esa composición no cambia dentro de
la línea experimental que la use. Añadir sesiones = banco nuevo con versión nueva, nunca
una modificación silenciosa del anterior (misma regla que ``arms-freeze-v1``).

Library-first (ADR-0035): hashing y JSON de la biblioteca estándar; los contratos los pone
``mecanico_contracts``. Aquí solo hay orquestación.

Uso:
    python tools/freeze_benchmark.py --version synthetic-benchmark-v2 \
        --part train_v11=data/sessions_v11/train \
        --part expansion_v2=data/sessions_v2/train \
        --part test_historico=data/sessions/test \
        --out ai-models/configs/benchmark-v2-freeze.json
    python tools/freeze_benchmark.py --verify ai-models/configs/benchmark-v2-freeze.json
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from mecanico_contracts.session_io import read_session_header

REPO_ROOT = Path(__file__).resolve().parents[1]


#: Campos de la cabecera que definen el EXPERIMENTO (frente a los que definen el formato).
#: Un cambio aditivo de contrato (ADR: los contratos solo crecen) altera los bytes de la
#: cabecera sin alterar ninguno de estos campos ni una sola lectura.
SEMANTIC_SCENARIO_FIELDS = (
    "scenario_id",
    "category",
    "driving_profile",
    "fault",
    "fault_params",
    "fault_start_s",
    "fault_end_s",
    "ambient_temp_c",
    "duration_s",
    "sample_rate_hz",
    "seed",
    "anomaly_seed",
)


def file_sha256(path: Path) -> str:
    """SHA-256 del contenido íntegro del fichero (streaming, sin cargarlo en memoria)."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def semantic_sha256(path: Path) -> str:
    """SHA-256 **invariante a cambios aditivos de la cabecera** de sesión.

    Motivación (medida, no hipotética): al reconstruir el banco v2 desde cero en F22, las
    8 sesiones del test histórico dieron hash distinto con un delta CONSTANTE de +20 bytes
    — exactamente ``,"anomaly_seed":null``, el campo que ADR-0034 añadió al contrato. El
    cuerpo de lecturas era idéntico byte a byte. Es decir: el ancla de reproducibilidad se
    rompía por un cambio de contrato **legítimo y aditivo**, no por un cambio de datos.

    Este hash cubre (1) el flujo de lecturas íntegro y (2) la proyección canónica de los
    campos del escenario que definen el experimento. Garantía declarada con precisión:
    es invariante a campos nuevos en la CABECERA; **no** lo es a cambios en el esquema de
    las LECTURAS, que sí serían un cambio de datos y exigirían una versión nueva de banco.
    """
    raw = path.read_bytes()
    head, _, body = raw.partition(b"\n")
    header = json.loads(head)
    scenario = header.get("scenario") or {}
    canonical = {
        "scenario": {f: scenario.get(f) for f in SEMANTIC_SCENARIO_FIELDS},
        "n_readings": header.get("n_readings"),
        "pids": header.get("pids"),
    }
    digest = hashlib.sha256()
    digest.update(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    digest.update(body)
    return digest.hexdigest()


def _repo_path(directory: Path) -> str:
    """Ruta relativa al repositorio si está dentro; absoluta si no (bancos externos)."""
    try:
        return str(directory.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(directory.resolve())


def session_entry(path: Path) -> dict[str, Any]:
    """Metadatos declarados + hash de una sesión (lo que hace falta para auditarla)."""
    header = read_session_header(path)
    scenario = header.scenario
    return {
        "file": path.name,
        "session_id": header.session_id,
        "sha256": file_sha256(path),
        "semantic_sha256": semantic_sha256(path),
        "bytes": path.stat().st_size,
        "n_readings": header.n_readings,
        "scenario_id": scenario.scenario_id if scenario else None,
        "category": scenario.category if scenario else None,
        "driving_profile": scenario.driving_profile if scenario else None,
        "duration_s": scenario.duration_s if scenario else None,
        "seed": scenario.seed if scenario else None,
        "anomaly_seed": scenario.anomaly_seed if scenario else None,
        "fault": scenario.fault if scenario else None,
    }


def partition_manifest(name: str, directory: Path) -> dict[str, Any]:
    """Manifiesto de una partición: sesiones ordenadas + hash agregado determinista."""
    files = sorted(directory.glob("*.jsonl"))
    if not files:
        msg = f"partición vacía: {directory}"
        raise FileNotFoundError(msg)
    sessions = [session_entry(p) for p in files]
    aggregate = hashlib.sha256()
    aggregate_semantic = hashlib.sha256()
    for entry in sessions:
        aggregate.update(entry["file"].encode("utf-8"))
        aggregate.update(entry["sha256"].encode("utf-8"))
        aggregate_semantic.update(entry["file"].encode("utf-8"))
        aggregate_semantic.update(entry["semantic_sha256"].encode("utf-8"))
    return {
        "name": name,
        "path": _repo_path(directory),
        "n_sessions": len(sessions),
        "total_duration_s": sum(s["duration_s"] or 0.0 for s in sessions),
        "seeds": sorted(s["seed"] for s in sessions if s["seed"] is not None),
        "faults": sorted({s["fault"] for s in sessions if s["fault"]}),
        "aggregate_sha256": aggregate.hexdigest(),
        "aggregate_semantic_sha256": aggregate_semantic.hexdigest(),
        "sessions": sessions,
    }


def freeze(version: str, parts: dict[str, Path], note: str = "") -> dict[str, Any]:
    """Manifiesto congelado completo (particiones + hash global del banco)."""
    partitions = [partition_manifest(name, path) for name, path in parts.items()]
    glob_digest = hashlib.sha256()
    for part in partitions:
        glob_digest.update(part["name"].encode("utf-8"))
        glob_digest.update(part["aggregate_sha256"].encode("utf-8"))
    return {
        "benchmark_version": version,
        "frozen": True,
        "freeze_rule": (
            "esta composición no cambia dentro de la línea experimental que la usa; "
            "añadir o retirar sesiones exige una versión nueva del banco (nunca edición)"
        ),
        "provenance": "SIMULATED (obd-lab; regeneración determinista por semilla)",
        "note": note,
        "benchmark_sha256": glob_digest.hexdigest(),
        "partitions": partitions,
    }


def verify(manifest_path: Path) -> tuple[bool, list[str]]:
    """Recomprueba el manifiesto contra los datos en disco. Devuelve (ok, incidencias).

    Dos niveles de coincidencia, ambos explícitos en la salida:

    ``EXACT``
        el fichero es idéntico byte a byte al congelado;
    ``SEMANTIC``
        las lecturas y los campos de escenario coinciden, pero los bytes de la CABECERA
        han cambiado por un crecimiento aditivo del contrato. No es una incidencia: es el
        caso que rompía el ancla en F22 (ADR-0034 añadió ``anomaly_seed``, +20 bytes) sin
        que ninguna medición cambiara.

    Solo el desacuerdo semántico invalida el banco. Los manifiestos anteriores a F22 no
    llevan ``semantic_sha256``; para ellos la deriva de cabecera no puede clasificarse y
    se reporta como incidencia, indicando cómo re-emitir el manifiesto.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []
    drifted: list[str] = []
    for part in manifest["partitions"]:
        directory = REPO_ROOT / part["path"]
        if not directory.is_dir():
            problems.append(f"{part['name']}: falta el directorio {part['path']}")
            continue
        on_disk = {p.name: p for p in directory.glob("*.jsonl")}
        for entry in part["sessions"]:
            path = on_disk.pop(entry["file"], None)
            if path is None:
                problems.append(f"{part['name']}: falta {entry['file']}")
                continue
            if file_sha256(path) == entry["sha256"]:
                continue
            expected_semantic = entry.get("semantic_sha256")
            if expected_semantic is None:
                problems.append(
                    f"{part['name']}: hash distinto en {entry['file']} "
                    "(manifiesto sin semantic_sha256: re-emitir el freeze para clasificar)"
                )
            elif semantic_sha256(path) == expected_semantic:
                drifted.append(f"{part['name']}/{entry['file']}")
            else:
                problems.append(f"{part['name']}: DATOS distintos en {entry['file']}")
        for extra in sorted(on_disk):
            problems.append(f"{part['name']}: sesión NO declarada en el freeze: {extra}")
    if drifted:
        print(
            f"  · {len(drifted)} sesión(es) con deriva ADITIVA de cabecera "
            "(lecturas y escenario intactos): coincidencia SEMANTIC"
        )
    return (not problems), problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version")
    parser.add_argument("--part", action="append", default=[], metavar="nombre=ruta")
    parser.add_argument("--note", default="")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    if args.verify:
        ok, problems = verify(args.verify)
        for p in problems:
            print(f"  ✗ {p}")
        print("freeze VERIFICADO" if ok else f"freeze ROTO ({len(problems)} incidencias)")
        return 0 if ok else 1

    if not (args.version and args.part and args.out):
        parser.error("se requieren --version, --part y --out (o bien --verify)")
    parts = {}
    for item in args.part:
        name, _, raw = item.partition("=")
        parts[name] = (REPO_ROOT / raw) if not Path(raw).is_absolute() else Path(raw)
    manifest = freeze(args.version, parts, args.note)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(p["n_sessions"] for p in manifest["partitions"])
    print(f"{manifest['benchmark_version']}: {total} sesiones en {len(parts)} particiones")
    print(f"hash del banco: {manifest['benchmark_sha256'][:16]}…  →  {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
