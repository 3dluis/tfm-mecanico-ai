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


def file_sha256(path: Path) -> str:
    """SHA-256 del contenido íntegro del fichero (streaming, sin cargarlo en memoria)."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
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
    for entry in sessions:
        aggregate.update(entry["file"].encode("utf-8"))
        aggregate.update(entry["sha256"].encode("utf-8"))
    return {
        "name": name,
        "path": _repo_path(directory),
        "n_sessions": len(sessions),
        "total_duration_s": sum(s["duration_s"] or 0.0 for s in sessions),
        "seeds": sorted(s["seed"] for s in sessions if s["seed"] is not None),
        "faults": sorted({s["fault"] for s in sessions if s["fault"]}),
        "aggregate_sha256": aggregate.hexdigest(),
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
    """Recomprueba el manifiesto contra los datos en disco. Devuelve (ok, incidencias)."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []
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
            actual = file_sha256(path)
            if actual != entry["sha256"]:
                problems.append(f"{part['name']}: hash distinto en {entry['file']}")
        for extra in sorted(on_disk):
            problems.append(f"{part['name']}: sesión NO declarada en el freeze: {extra}")
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
