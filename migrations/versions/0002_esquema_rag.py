"""Esquema rag: documentos, versiones, fragmentos, embeddings y trazas.

Tres decisiones estructurales.

**El vehículo es una columna, no un comentario.** `vehicle_id` viaja en el
documento, en el fragmento y en el embedding. La recuperación filtra por él
*antes* de comparar vectores, de modo que documentación de otro coche no puede
aparecer como evidencia por mucho que su texto se parezca.

**Las versiones documentales no se sobrescriben.** Un documento tiene N
versiones, cada una con su huella. Un experimento registra qué versión usó, y
sigue siendo reconstruible cuando llegue una revisión posterior.

**Cada recuperación deja rastro.** `retrieval_run` y `retrieval_result` guardan
la consulta, sus parámetros y qué devolvió con qué puntuación. Sin eso, «el
sistema recuperó este fragmento» no es verificable después.

Revision ID: 0002
Revises: 0001
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

ESQUEMA = "rag"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {ESQUEMA}")

    op.create_table(
        "vehicle",
        sa.Column("vehicle_id", sa.Text, primary_key=True),
        sa.Column("manufacturer", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("model_year", sa.Integer, nullable=False),
        # Lo desconocido se queda en NULL. Nunca se infiere: un engine_code
        # inventado convertiría el validador de aplicabilidad en un generador de
        # coincidencias exactas falsas.
        sa.Column("generation", sa.Text),
        sa.Column("market", sa.Text),
        sa.Column("engine_code", sa.Text),
        sa.Column("engine_displacement", sa.Text),
        sa.Column("fuel_type", sa.Text),
        sa.Column("transmission", sa.Text),
        sa.Column("obd_protocol", sa.Text),
        sa.Column("notes", sa.Text, nullable=False, server_default=""),
        schema=ESQUEMA,
    )

    op.create_table(
        "document",
        sa.Column("document_id", sa.Text, primary_key=True),
        sa.Column(
            "vehicle_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.vehicle.vehicle_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("document_type", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        # Editor original y canal de adquisición son cosas distintas: confundirlos
        # convierte a un intermediario en autoridad.
        sa.Column("publisher", sa.Text, nullable=False),
        sa.Column("acquisition_source", sa.Text),
        sa.Column("acquisition_channel", sa.Text),
        sa.Column("source_url", sa.Text, nullable=False),
        sa.Column("authority_level", sa.Text, nullable=False),
        sa.Column("access_type", sa.Text, nullable=False),
        sa.Column("language", sa.Text, nullable=False, server_default="en"),
        sa.Column("model_year_start", sa.Integer),
        sa.Column("model_year_end", sa.Integer),
        sa.Column("engine_codes", sa.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("market", sa.Text),
        sa.Column("redistributable", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("verification_notes", sa.Text, nullable=False, server_default=""),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        schema=ESQUEMA,
    )
    op.create_index("ix_document_vehicle", "document", ["vehicle_id"], schema=ESQUEMA)

    op.create_table(
        "document_version",
        sa.Column("version_id", sa.Text, primary_key=True),
        sa.Column(
            "document_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.document.document_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sha256", sa.Text, nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revision", sa.Text),
        sa.Column("file_size", sa.BigInteger),
        sa.Column("local_file", sa.Text),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        # Una huella identifica una versión de un documento. Repetirla sería
        # registrar dos veces lo mismo.
        sa.UniqueConstraint("document_id", "sha256", name="uq_version_documento_huella"),
        schema=ESQUEMA,
    )

    op.create_table(
        "document_chunk",
        sa.Column("chunk_id", sa.Text, primary_key=True),
        sa.Column(
            "version_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.document_version.version_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("document_id", sa.Text, nullable=False),
        # Se desnormaliza el vehículo a propósito: la recuperación filtra por él
        # en cada consulta, y una unión más por consulta no aporta nada.
        sa.Column("vehicle_id", sa.Text, nullable=False),
        sa.Column("ordinal", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("content_hash", sa.Text, nullable=False),
        sa.Column("chapter", sa.Text),
        sa.Column("section", sa.Text),
        sa.Column("subsection", sa.Text),
        sa.Column("page_start", sa.Integer),
        sa.Column("page_end", sa.Integer),
        sa.Column("dtc_codes", sa.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("vehicle_system", sa.Text),
        sa.Column("system_classification", sa.Text),
        sa.Column("engine_codes", sa.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("source_file", sa.Text),
        sa.Column("n_tokens", sa.Integer),
        schema=ESQUEMA,
    )
    op.create_index("ix_chunk_vehicle", "document_chunk", ["vehicle_id"], schema=ESQUEMA)
    op.create_index("ix_chunk_version", "document_chunk", ["version_id"], schema=ESQUEMA)
    op.execute(f"CREATE INDEX ix_chunk_dtc ON {ESQUEMA}.document_chunk USING gin (dtc_codes)")
    # Búsqueda léxica junto a la semántica: un código como P0171 o el nombre de
    # una pieza se encuentran mejor por coincidencia exacta que por vecindad.
    op.execute(
        f"CREATE INDEX ix_chunk_fts ON {ESQUEMA}.document_chunk "
        "USING gin (to_tsvector('english', text))"
    )

    op.create_table(
        "ingestion_run",
        sa.Column("run_id", sa.Text, primary_key=True),
        sa.Column("vehicle_id", sa.Text, nullable=False),
        sa.Column("corpus_version", sa.Text, nullable=False),
        sa.Column("manifest_hash", sa.Text, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("embedding_provider", sa.Text),
        sa.Column("embedding_model", sa.Text),
        sa.Column("embedding_dimension", sa.Integer),
        sa.Column("chunking_version", sa.Text),
        sa.Column("documents_registered", sa.Integer, nullable=False, server_default="0"),
        sa.Column("chunks_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("embeddings_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=False, server_default=""),
        schema=ESQUEMA,
    )

    op.create_table(
        "retrieval_run",
        sa.Column("run_id", sa.Text, primary_key=True),
        sa.Column("vehicle_id", sa.Text, nullable=False),
        sa.Column("query_text", sa.Text, nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("embedding_provider", sa.Text),
        sa.Column("embedding_model", sa.Text),
        sa.Column("top_k", sa.Integer, nullable=False),
        sa.Column("filters", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("corpus_variant", sa.Text),
        sa.Column("experiment_id", sa.Text),
        schema=ESQUEMA,
    )

    op.create_table(
        "retrieval_result",
        sa.Column("result_id", sa.Text, primary_key=True),
        sa.Column(
            "run_id",
            sa.Text,
            sa.ForeignKey(f"{ESQUEMA}.retrieval_run.run_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_id", sa.Text, nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("applicability", sa.Text),
        sa.Column("authority_level", sa.Text),
        sa.Column("evidence_rank", sa.Integer),
        schema=ESQUEMA,
    )
    op.create_index("ix_result_run", "retrieval_result", ["run_id"], schema=ESQUEMA)

    op.create_table(
        "claim_evidence",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("experiment_id", sa.Text, nullable=False),
        sa.Column("case_id", sa.Text, nullable=False),
        sa.Column("claim_id", sa.Text, nullable=False),
        sa.Column("claim_text", sa.Text, nullable=False),
        sa.Column("evidence_kind", sa.Text, nullable=False),
        sa.Column("evidence_id", sa.Text, nullable=False),
        sa.Column("support_status", sa.Text, nullable=False),
        sa.Column("notes", sa.Text, nullable=False, server_default=""),
        schema=ESQUEMA,
    )
    op.create_index(
        "ix_claim_experimento", "claim_evidence", ["experiment_id", "case_id"], schema=ESQUEMA
    )


def downgrade() -> None:
    for tabla in (
        "claim_evidence",
        "retrieval_result",
        "retrieval_run",
        "ingestion_run",
        "document_chunk",
        "document_version",
        "document",
        "vehicle",
    ):
        op.drop_table(tabla, schema=ESQUEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {ESQUEMA}")
