"""Particionado temporal de ``telemetry.vehicle_telemetry_snapshots`` (F12 §6/§35/§36).

Política SIMPLE y explícita (ADR-0030):

- Particiones mensuales por rango sobre ``timestamp_utc``.
- Se crean por ADELANTADO (``months_ahead``, por defecto 3): un TFM de pocos meses no
  necesita automatismos sofisticados, solo que nunca falte la partición del mes en curso.
- Partición ``_default`` de seguridad: una fila con timestamp fuera de rango NO se pierde
  ni rompe la ingesta; queda visible y se puede reubicar.
- ``drop_partition`` existe para la retención por partición, pero **nunca** se invoca de
  forma automática: borrar un mes exige comprobar antes que nada referenciado por
  provenance vive ahí (F12 §36).
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import Engine, text

SNAPSHOT_TABLE = "telemetry.vehicle_telemetry_snapshots"


def _month_bounds(year: int, month: int) -> tuple[str, str, str]:
    nxt_y, nxt_m = (year + 1, 1) if month == 12 else (year, month + 1)
    return (
        f"{year:04d}_{month:02d}",
        f"{year:04d}-{month:02d}-01",
        f"{nxt_y:04d}-{nxt_m:02d}-01",
    )


@dataclass(frozen=True)
class PartitionInfo:
    name: str
    lower: str
    upper: str


def plan_partitions(start: datetime, months_ahead: int = 3) -> list[PartitionInfo]:
    """Meses a garantizar: el del `start` y los `months_ahead` siguientes."""
    out: list[PartitionInfo] = []
    y, m = start.year, start.month
    for _ in range(months_ahead + 1):
        suffix, lo, hi = _month_bounds(y, m)
        out.append(PartitionInfo(f"telemetry.snapshots_{suffix}", lo, hi))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def ensure_partitions(
    engine: Engine, start: datetime | None = None, months_ahead: int = 3
) -> list[str]:
    """Crea (IF NOT EXISTS) las particiones mensuales necesarias. Devuelve las creadas."""
    if engine.dialect.name != "postgresql":
        return []
    start = start or datetime.now(UTC)
    created: list[str] = []
    with engine.begin() as conn:
        for p in plan_partitions(start, months_ahead):
            exists = conn.execute(
                text("SELECT to_regclass(:n) IS NOT NULL"), {"n": p.name}
            ).scalar_one()
            if exists:
                continue
            conn.execute(
                text(
                    f"CREATE TABLE {p.name} PARTITION OF {SNAPSHOT_TABLE} "
                    f"FOR VALUES FROM ('{p.lower}') TO ('{p.upper}')"
                )
            )
            created.append(p.name)
        default_name = "telemetry.snapshots_default"
        if not conn.execute(
            text("SELECT to_regclass(:n) IS NOT NULL"), {"n": default_name}
        ).scalar_one():
            conn.execute(text(f"CREATE TABLE {default_name} PARTITION OF {SNAPSHOT_TABLE} DEFAULT"))
            created.append(default_name)
    return created


def list_partitions(engine: Engine) -> list[tuple[str, int]]:
    """(nombre, bytes) de cada partición — para observabilidad y retención."""
    if engine.dialect.name != "postgresql":
        return []
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT c.relname, pg_total_relation_size(c.oid) "
                "FROM pg_class c JOIN pg_inherits i ON i.inhrelid = c.oid "
                "JOIN pg_class p ON p.oid = i.inhparent "
                "WHERE p.relname = 'vehicle_telemetry_snapshots' ORDER BY c.relname"
            )
        ).all()
    return [(r[0], int(r[1])) for r in rows]


def drop_partition(engine: Engine, name: str, *, i_verified_provenance: bool = False) -> None:
    """Retención por partición. Exige afirmación EXPLÍCITA de verificación de provenance."""
    if not i_verified_provenance:
        msg = (
            "drop_partition exige verificar antes que ninguna evidencia diagnóstica, "
            "CaseMemory o LearnedPattern referencie ese rango (F12 §36)"
        )
        raise RuntimeError(msg)
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {name}"))
