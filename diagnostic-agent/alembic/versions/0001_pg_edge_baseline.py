"""Baseline PostgreSQL + pgvector del edge (ADR-0030).

Crea: schemas lógicos · extensión ``vector`` · todas las tablas del modelo (espejo de los
contratos) · la tabla particionada de snapshots con sus particiones mensuales iniciales ·
los índices declarados (B-tree por query pattern + BRIN temporal).

Nota de método: el esquema se materializa desde ``Base.metadata`` porque **la fuente de
verdad son los contratos** y el esquema es su espejo verificado por tests. A partir de
aquí, cada cambio será una revisión Alembic con su delta explícito (no más create_all).

Revision ID: 0001_pg_edge_baseline
Revises:
"""

from datetime import UTC, datetime

from alembic import op

from diagnostic_agent.storage.partitions import plan_partitions
from diagnostic_agent.storage.schema import SCHEMAS, Base

revision = "0001_pg_edge_baseline"
down_revision = None
branch_labels = None
depends_on = None

SNAPSHOTS = "telemetry.vehicle_telemetry_snapshots"


def upgrade() -> None:
    bind = op.get_bind()
    for schema in SCHEMAS:
        op.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind)
    # Particiones: el mes en curso + 3 por delante (política simple, F12 §6) + DEFAULT
    # de seguridad para que una fila fuera de rango nunca rompa la ingesta.
    for p in plan_partitions(datetime.now(UTC), months_ahead=3):
        op.execute(
            f"CREATE TABLE IF NOT EXISTS {p.name} PARTITION OF {SNAPSHOTS} "
            f"FOR VALUES FROM ('{p.lower}') TO ('{p.upper}')"
        )
    op.execute(
        f"CREATE TABLE IF NOT EXISTS telemetry.snapshots_default PARTITION OF {SNAPSHOTS} DEFAULT"
    )


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
    for schema in reversed(SCHEMAS):
        op.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
