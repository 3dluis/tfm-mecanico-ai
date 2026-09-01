"""Idioma del fragmento y del documento.

El idioma no es cosmético. Determina tres cosas:

**Qué configuración usa la búsqueda de texto completo.** ``to_tsvector('english',
...)`` sobre texto español lematiza mal: no reconoce «ralentí» ni «combustible»
como raíces, y la búsqueda léxica pierde precisamente lo que aporta.

**Si un embedding es comparable con otro.** Un modelo monolingüe coloca una
consulta en español en una región del espacio que no corresponde a su traducción.
La recuperación seguiría devolviendo resultados, y serían casualidad.

**Qué se puede citar en qué idioma.** Una explicación en español que cita un
procedimiento en inglés debe poder mostrar el original: traducir la cita al
redactarla la haría incomprobable contra la fuente.

Revision ID: 0004
Revises: 0003
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

ESQUEMA = "rag"

#: Configuraciones de búsqueda de texto completo por idioma.
CONFIG_FTS = {"en": "english", "es": "spanish"}


def upgrade() -> None:
    op.add_column(
        "document_chunk",
        sa.Column("language", sa.Text, nullable=False, server_default="en"),
        schema=ESQUEMA,
    )
    op.create_index("ix_chunk_language", "document_chunk", ["language"], schema=ESQUEMA)

    # Índice de texto completo en español, junto al que ya existe en inglés. Se
    # mantienen los dos: cada fragmento se busca con la configuración de su
    # idioma, no con una común que degradaría ambos.
    op.execute(
        f"CREATE INDEX ix_chunk_fts_es ON {ESQUEMA}.document_chunk "
        "USING gin (to_tsvector('spanish', text))"
    )

    op.add_column(
        "retrieval_run",
        sa.Column("query_language", sa.Text),
        schema=ESQUEMA,
    )
    # El idioma de la consulta se registra porque una recuperación translingüe
    # --consulta en español, documento en inglés-- no es comparable con una
    # monolingüe, y confundirlas mezclaría dos condiciones distintas.


def downgrade() -> None:
    op.drop_column("retrieval_run", "query_language", schema=ESQUEMA)
    op.execute(f"DROP INDEX IF EXISTS {ESQUEMA}.ix_chunk_fts_es")
    op.drop_index("ix_chunk_language", "document_chunk", schema=ESQUEMA)
    op.drop_column("document_chunk", "language", schema=ESQUEMA)
