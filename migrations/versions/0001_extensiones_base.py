"""Extensiones base del laboratorio.

Habilita ``vector`` (almacenamiento y búsqueda de embeddings del corpus RAG) y
``pg_trgm`` (apoyo léxico en la recuperación híbrida). Las tablas del corpus se
definen en una migración posterior, junto con el modelo de procedencia.

Revision ID: 0001
Revises:
"""

from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    # No se eliminan extensiones: podrían estar en uso por otros objetos.
    pass
