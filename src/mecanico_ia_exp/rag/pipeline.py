"""Pipeline de ingesta: de los ficheros del manual a vectores con procedencia.

    localizar → huella → cargar → trocear → metadata → embeber → pgvector → informe

Un manual de taller no es un fichero: es una colección de miles. Se trata como
**un documento con muchos ficheros de origen**, no como miles de documentos: es
un solo manual, con una sola revisión y una sola cadena de procedencia.

Su huella es la de la colección completa, calculada sobre la lista ordenada de
(ruta relativa, huella del fichero). Añadir, quitar o cambiar un solo fichero la
cambia, lo que hace que la idempotencia funcione a nivel de manual.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from mecanico_ia_exp.rag.chunking import Chunk, ChunkingConfig, chunk_document
from mecanico_ia_exp.rag.document_downloader import sha256_of
from mecanico_ia_exp.rag.embeddings import EmbeddingProvider
from mecanico_ia_exp.rag.loaders import LOADERS, load_document
from mecanico_ia_exp.rag.manifest import DocumentEntry
from mecanico_ia_exp.rag.store import PgVectorStore

EXTENSIONES = tuple(sorted({e for c in LOADERS for e in c.extensions}))


@dataclass
class CollectionFingerprint:
    """Huella de una colección de ficheros."""

    sha256: str
    n_files: int
    total_bytes: int
    files: list[tuple[str, str]] = field(default_factory=list)
    """(ruta relativa, huella) ordenado. Permite ver qué cambió entre versiones."""


def fingerprint_collection(
    raiz: Path, extensiones: tuple[str, ...] = EXTENSIONES
) -> CollectionFingerprint:
    """Huella determinista de todos los ficheros admitidos bajo una raíz.

    El orden se fija por ruta relativa para que la huella no dependa del sistema
    de ficheros. Dos máquinas con el mismo contenido obtienen la misma huella.
    """
    ficheros: list[tuple[str, str]] = []
    total = 0
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in extensiones:
            continue
        relativa = str(ruta.relative_to(raiz))
        ficheros.append((relativa, sha256_of(ruta)))
        total += ruta.stat().st_size

    digestor = hashlib.sha256()
    for relativa, huella in ficheros:
        digestor.update(relativa.encode("utf-8"))
        digestor.update(huella.encode("ascii"))
    return CollectionFingerprint(
        sha256=digestor.hexdigest(), n_files=len(ficheros), total_bytes=total, files=ficheros
    )


def iter_documents(raiz: Path, extensiones: tuple[str, ...] = EXTENSIONES) -> Iterator[Path]:
    for ruta in sorted(raiz.rglob("*")):
        if ruta.is_file() and ruta.suffix.lower() in extensiones:
            yield ruta


def _capitulo_de(ruta: Path, raiz: Path) -> str:
    """Capítulo = primer directorio bajo la raíz. En este manual es la sección
    funcional: srvc, engine, mission, introduction, esi_common."""
    relativa = ruta.relative_to(raiz)
    return relativa.parts[0] if len(relativa.parts) > 1 else "raiz"


@dataclass
class IngestionOutcome:
    """Lo que produjo una ingesta de corpus."""

    document_id: str
    version_id: str
    collection_sha256: str
    n_files: int
    n_files_sin_texto: int
    n_chunks: int
    n_embeddings: int
    n_chunks_con_dtc: int
    dtc_distintos: int
    seconds: float
    skipped: bool = False
    """``True`` si la huella no cambió y no se reingirió."""


def ingest_collection(
    *,
    entrada: DocumentEntry,
    raiz: Path,
    store: PgVectorStore,
    provider: EmbeddingProvider,
    chunking: ChunkingConfig | None = None,
    ingestion_run_id: str | None = None,
    batch_size: int = 256,
    force: bool = False,
    progress_every: int = 250,
) -> IngestionOutcome:
    """Ingiere una colección local como un único documento versionado."""
    inicio = datetime.now(UTC)
    cfg = chunking or ChunkingConfig()

    huella = fingerprint_collection(raiz)
    version_id = f"{entrada.document_id}@{huella.sha256[:12]}"
    print(
        f"colección: {huella.n_files} ficheros · {huella.total_bytes / 1e6:.0f} MB · "
        f"sha256 {huella.sha256[:16]}…"
    )

    store.register_document(entrada)
    registrada = store.register_version(
        version_id=version_id,
        document_id=entrada.document_id,
        sha256=huella.sha256,
        revision=entrada.revision,
        file_size=huella.total_bytes,
        local_file=str(raiz),
    )
    if registrada != version_id and not force:
        # La huella ya estaba: reingerir produciría los mismos fragmentos.
        print(f"versión {registrada} ya registrada con esta huella; no se reingiere")
        return IngestionOutcome(
            document_id=entrada.document_id,
            version_id=registrada,
            collection_sha256=huella.sha256,
            n_files=huella.n_files,
            n_files_sin_texto=0,
            n_chunks=0,
            n_embeddings=0,
            n_chunks_con_dtc=0,
            dtc_distintos=0,
            seconds=(datetime.now(UTC) - inicio).total_seconds(),
            skipped=True,
        )

    identidad = provider.identity
    print(f"embeddings: {identidad.model} · {identidad.dimension} dim · {identidad.provider}")

    lote: list[Chunk] = []
    n_chunks = n_emb = sin_texto = con_dtc = 0
    dtcs: set[str] = set()
    ordinal_global = 0

    def volcar(lote: list[Chunk]) -> int:
        if not lote:
            return 0
        store.store_chunks(lote)
        vectores = provider.embed([c.text for c in lote])
        return store.store_embeddings(lote, vectores, identidad, ingestion_run_id=ingestion_run_id)

    for i, ruta in enumerate(iter_documents(raiz), start=1):
        documento = load_document(ruta)
        if not documento:
            sin_texto += 1
            continue
        fragmentos = chunk_document(
            documento,
            document_id=entrada.document_id,
            version_id=version_id,
            vehicle_id=entrada.vehicle_id,
            chapter=_capitulo_de(ruta, raiz),
            config=cfg,
            relative_to=raiz,
        )
        # Los identificadores deben ser únicos en toda la colección, no dentro de
        # cada fichero: el troceado numera desde cero en cada documento.
        renumerados = [
            Chunk(
                **{
                    **c.__dict__,
                    "ordinal": ordinal_global + j,
                    "chunk_id": f"{version_id}:{ordinal_global + j:06d}",
                }
            )
            for j, c in enumerate(fragmentos)
        ]
        ordinal_global += len(renumerados)
        for c in renumerados:
            if c.dtc_codes:
                con_dtc += 1
                dtcs.update(c.dtc_codes)
        lote.extend(renumerados)
        n_chunks += len(renumerados)

        if len(lote) >= batch_size:
            n_emb += volcar(lote)
            lote = []
        if progress_every and i % progress_every == 0:
            print(f"  {i}/{huella.n_files} ficheros · {n_chunks} fragmentos")

    n_emb += volcar(lote)

    return IngestionOutcome(
        document_id=entrada.document_id,
        version_id=version_id,
        collection_sha256=huella.sha256,
        n_files=huella.n_files,
        n_files_sin_texto=sin_texto,
        n_chunks=n_chunks,
        n_embeddings=n_emb,
        n_chunks_con_dtc=con_dtc,
        dtc_distintos=len(dtcs),
        seconds=(datetime.now(UTC) - inicio).total_seconds(),
    )
