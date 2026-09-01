"""Tabla de embeddings con dimensión fija.

``vector(n)`` obliga a declarar la dimensión en el esquema. Podría parecer una
rigidez incómoda; es lo contrario. Dos corpus indexados con modelos de embeddings
distintos **no son comparables**, y un esquema que aceptara cualquier dimensión
permitiría mezclarlos sin que nada fallara.

Al fijarla, cambiar de modelo exige una migración: la decisión queda escrita, con
fecha, en el historial del proyecto.

Dimensión 384: la de ``all-MiniLM-L6-v2`` y la del proveedor de hashing, que se
eligió igual a propósito para que ambos sean intercambiables sin reindexar el
esquema.

Revision ID: 0003
Revises: 0002
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

ESQUEMA = "rag"
DIMENSION = 384


def upgrade() -> None:
    op.create_table(
        "embedding",
        sa.Column("embedding_id", sa.Text, primary_key=True),
        sa.Column(
            "chunk_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.document_chunk.chunk_id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Se repiten aquí para poder filtrar por vehículo sin unir con el
        # fragmento: el filtro por vehículo se aplica en TODAS las consultas.
        sa.Column("vehicle_id", sa.Text, nullable=False),
        sa.Column("document_id", sa.Text, nullable=False),
        sa.Column("embedding_provider", sa.Text, nullable=False),
        sa.Column("embedding_model", sa.Text, nullable=False),
        sa.Column("embedding_dimension", sa.Integer, nullable=False),
        sa.Column("embedding_version", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "ingestion_run_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.ingestion_run.run_id", ondelete="SET NULL"),
        ),
        # Un fragmento tiene un vector por modelo, no uno por ejecución: repetir
        # la pareja significaría indexar dos veces lo mismo.
        sa.UniqueConstraint("chunk_id", "embedding_model", name="uq_embedding_chunk_modelo"),
        schema=ESQUEMA,
    )
    op.execute(f"ALTER TABLE {ESQUEMA}.embedding ADD COLUMN vector vector({DIMENSION}) NOT NULL")
    op.create_index("ix_embedding_vehicle", "embedding", ["vehicle_id"], schema=ESQUEMA)
    op.create_index("ix_embedding_model", "embedding", ["embedding_model"], schema=ESQUEMA)
    # Sin índice vectorial de momento. Con un corpus pequeño la búsqueda exacta
    # es suficiente y además es exacta: un índice aproximado introduciría
    # recuperaciones no reproducibles justo donde se mide la recuperación.
    # Si el volumen lo justifica se añadirá HNSW, y el cambio quedará registrado
    # en el experimento porque altera los resultados.


def downgrade() -> None:
    op.drop_table("embedding", schema=ESQUEMA)
