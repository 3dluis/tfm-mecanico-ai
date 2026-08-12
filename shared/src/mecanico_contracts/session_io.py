"""E/S del formato común de sesión grabada (parte del contrato, ADR-0010).

Formato: archivo JSONL cuya primera línea es un ``RecordedSession`` y las siguientes
son ``OBDReading``. Es el formato único para sesiones sintéticas (obd-lab), datasets
reales reproducidos y capturas de vehículo — los consumidores no distinguen la fuente.
"""

import json
from collections.abc import Iterable
from pathlib import Path

from mecanico_contracts.models import OBDReading, RecordedSession


def write_session_file(header: RecordedSession, readings: Iterable[OBDReading], path: Path) -> Path:
    """Escribe una sesión completa (cabecera + lecturas) en JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(header.model_dump_json() + "\n")
        for reading in readings:
            fh.write(reading.model_dump_json() + "\n")
    return path


def read_session_header(path: Path) -> RecordedSession:
    """Lee solo la cabecera de una sesión."""
    with path.open(encoding="utf-8") as fh:
        return RecordedSession.model_validate_json(fh.readline())


def read_session_series(path: Path) -> tuple[RecordedSession, dict[str, list[float]]]:
    """Lee una sesión y devuelve (cabecera, series por PID alineadas por tick).

    Optimizado con ``json.loads`` directo (validar 20k lecturas con Pydantic en cada
    carga sería innecesario: el archivo lo escribió este mismo módulo o un adaptador
    que ya validó).
    """
    with path.open(encoding="utf-8") as fh:
        header = RecordedSession.model_validate_json(fh.readline())
        series: dict[str, list[float]] = {pid: [] for pid in header.pids}
        for line in fh:
            r = json.loads(line)
            series[r["pid"]].append(float(r["value"]))
    return header, series
