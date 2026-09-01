"""Ingesta del corpus del Mazda 3 BK en pgvector."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.ingest import load_vehicle, manifest_hash
from mecanico_ia_exp.rag.manifest import DocumentManifest
from mecanico_ia_exp.rag.pipeline import ingest_collection
from mecanico_ia_exp.rag.store import PgVectorStore

VEHICULO = "mazda-3-bk-2007"
DOCUMENTO = "mazda3-bk-workshop-manual-local"


def main() -> int:
    base = paths.CORPUS / "vehicles" / VEHICULO
    manifiesto_ruta = base / "manifest.yaml"
    manifiesto = DocumentManifest.load(manifiesto_ruta)
    perfil = load_vehicle(VEHICULO)
    entrada = manifiesto.by_id(DOCUMENTO)

    if not entrada.local_file:
        print(f"{DOCUMENTO} no declara local_file en el manifiesto")
        return 1
    raiz = base / entrada.local_file
    if not raiz.exists():
        print(f"No existe {raiz}")
        return 1

    store = PgVectorStore()
    store.register_vehicle(perfil)
    print(f"vehículo registrado: {perfil.vehicle_id} · motor {perfil.engine_code}")

    run_id = str(uuid.uuid4())
    import sys

    modelo = sys.argv[1] if len(sys.argv) > 1 else "multilingual"
    provider = get_provider(modelo)

    resultado = ingest_collection(
        entrada=entrada,
        raiz=raiz,
        store=store,
        provider=provider,
        ingestion_run_id=None,
    )

    informe = {
        "run_id": run_id,
        "vehicle_id": VEHICULO,
        "corpus_version": manifiesto.corpus_version,
        "manifest_hash": manifest_hash(manifiesto_ruta),
        "started_at": datetime.now(UTC).isoformat(),
        "document_id": resultado.document_id,
        "version_id": resultado.version_id,
        "collection_sha256": resultado.collection_sha256,
        "documents_registered": len(manifiesto.documents),
        "files_processed": resultado.n_files,
        "files_without_text": resultado.n_files_sin_texto,
        "chunks_created": resultado.n_chunks,
        "embeddings_created": resultado.n_embeddings,
        "chunks_with_dtc": resultado.n_chunks_con_dtc,
        "distinct_dtc": resultado.dtc_distintos,
        "embedding": provider.identity.as_dict(),
        "seconds": round(resultado.seconds, 1),
        "skipped": resultado.skipped,
    }
    destino = paths.ensure(paths.RESULTS / "rag_ingestion") / f"{VEHICULO}_{run_id[:8]}.json"
    destino.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print()
    for clave in (
        "files_processed",
        "files_without_text",
        "chunks_created",
        "embeddings_created",
        "chunks_with_dtc",
        "distinct_dtc",
        "seconds",
    ):
        print(f"  {clave:<22} {informe[clave]}")
    print(f"\ninforme {destino.relative_to(paths.ROOT)}")
    store.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
