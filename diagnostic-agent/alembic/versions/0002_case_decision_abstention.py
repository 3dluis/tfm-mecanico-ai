"""Decisión de suficiencia de la evidencia en el caso diagnóstico (ADR-0036).

Añade a ``diagnostics.diagnostic_cases`` las dos columnas que registran la salida del
nodo ``decide``: la decisión (explicación sostenida, contradicha, no concluyente o
**abstención por evidencia insuficiente**) y la fracción de afirmaciones sustentadas de
la explicación emitida. Ambas son la unidad de medida de las hipótesis H-MAIN, H-GRD y
H-ABS del pre-registro enmendado (ENM-001).

Cambio **aditivo** y con valores nulos permitidos (ADR-0007): los casos ya persistidos
siguen siendo válidos y se leen como «sin decisión registrada», que es lo que eran.

Revision ID: 0002_case_decision_abstention
Revises: 0001_pg_edge_baseline
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_case_decision_abstention"
down_revision = "0001_pg_edge_baseline"
branch_labels = None
depends_on = None

TABLE = "diagnostic_cases"
SCHEMA = "diagnostics"


def upgrade() -> None:
    op.add_column(TABLE, sa.Column("decision", sa.String(), nullable=True), schema=SCHEMA)
    op.add_column(
        TABLE, sa.Column("supported_claim_ratio", sa.Float(), nullable=True), schema=SCHEMA
    )
    op.create_index(
        f"ix_{TABLE}_decision", TABLE, ["decision"], schema=SCHEMA, postgresql_using="btree"
    )


def downgrade() -> None:
    op.drop_index(f"ix_{TABLE}_decision", table_name=TABLE, schema=SCHEMA)
    op.drop_column(TABLE, "supported_claim_ratio", schema=SCHEMA)
    op.drop_column(TABLE, "decision", schema=SCHEMA)
