"""Baseline del RAG local sobre pgvector (F12 §40).

Mide la recuperación top-K de los TRES usos aprobados, cada uno por separado y a través
de los repositorios reales (no SQL suelto):

- ``knowledge.knowledge_chunks``  → RAG técnico
- ``memory.case_memory``          → casos similares (con y sin filtro relacional)
- ``memory.learned_patterns``     → patrones relacionados

Honestidad: los vectores son SINTÉTICOS y deterministas — esto mide el MOTOR y la
latencia de la consulta, NO la calidad de recuperación (esa exige un corpus real y
métricas Recall@K/MRR/nDCG, docs/models/04). Estrategia: búsqueda EXACTA sin índice;
se mide también con IVFFlat para saber cuándo empezaría a compensar (F12 §14).

Uso: python tools/pg_vector_benchmark.py [--pg-url ...]
"""

import argparse
import json
import math
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.repositories import (
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
)
from diagnostic_agent.storage.store import EdgeStore
from mecanico_contracts import (
    CaseMemory,
    DiagnosticCase,
    KnowledgeChunk,
    KnowledgeDocument,
    LearnedPattern,
)
from mecanico_contracts.data_enums import EpistemicLevel

DIM = 384
N_CHUNKS, N_CASES, N_PATTERNS = 1000, 500, 100
TOPK, N_QUERIES = 10, 50
NOW = datetime(2026, 8, 13, tzinfo=UTC)


def _vec(seed: int) -> list[float]:
    raw = [
        math.sin(seed * 0.7 + i * 0.013) + 0.1 * math.cos(seed * 0.3 - i * 0.007)
        for i in range(DIM)
    ]
    norm = math.sqrt(sum(v * v for v in raw))
    return [v / norm for v in raw]


def _median_ms(fn, n: int = N_QUERIES) -> float:
    lat = []
    for i in range(n):
        t0 = time.perf_counter()
        fn(i)
        lat.append((time.perf_counter() - t0) * 1000)
    return round(statistics.median(lat), 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pg-url", default=os.environ.get("MECANICO_DB_URL"))
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parents[1]
        / "ai-models"
        / "experiments"
        / "pg_vector_benchmark.json",
    )
    args = ap.parse_args()
    store = EdgeStore(url=args.pg_url) if args.pg_url else EdgeStore()
    from diagnostic_agent.storage.schema import SCHEMAS

    with store.engine.begin() as conn:
        for s in SCHEMAS:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{s}" CASCADE'))
    store.migrate()

    know, mem = PostgresKnowledgeRepository(store), PostgresMemoryRepository(store)
    store.add(
        dbs.KnowledgeDocumentRow,
        KnowledgeDocument(
            document_id="doc-bench", title="corpus", source="bench", license="n/a", ingested_at=NOW
        ),
    )
    case = DiagnosticCase(case_id="case-bench", vehicle_id="veh-b", opened_at=NOW)
    store.add(dbs.CaseRow, case)

    t0 = time.perf_counter()
    for i in range(N_CHUNKS):
        know.add_chunk(
            KnowledgeChunk(chunk_id=f"c{i}", document_id="doc-bench", seq=i, text=f"chunk {i}"),
            embedding=_vec(i),
        )
    t_load_chunks = time.perf_counter() - t0
    for i in range(N_CASES):
        mem.add_case(
            CaseMemory(
                case_memory_id=f"cm{i}",
                case_id="case-bench",
                vehicle_id=f"veh-{i % 5}",
                symptom_text=f"sintoma {i}",
                symptom_signature={"maf_mean": float(i % 30)},
                diagnosis="d",
                epistemic_level=EpistemicLevel.SIMULATED,
                created_at=NOW,
                updated_at=NOW,
            ),
            embedding=_vec(10_000 + i),
        )
    for i in range(N_PATTERNS):
        mem.add_pattern(
            LearnedPattern(
                pattern_id=f"lp{i}",
                version=1,
                title=f"patron {i}",
                description="d",
                telemetry_signature={"maf_slope": float(i % 7)},
                affected_metrics=["MAF"],
                first_seen=NOW,
                last_seen=NOW,
            ),
            embedding=_vec(20_000 + i),
        )

    results = {
        "measured_at": datetime.now(UTC).isoformat(),
        "note": (
            "vectores SINTÉTICOS: miden motor y latencia, NO calidad de recuperación "
            "(Recall@K/MRR/nDCG exigen corpus real — docs/models/04)"
        ),
        "corpus": {"chunks": N_CHUNKS, "cases": N_CASES, "patterns": N_PATTERNS, "dims": DIM},
        "load_chunks_s": round(t_load_chunks, 2),
        "exact": {
            "knowledge_topk_median_ms": _median_ms(lambda i: know.search(_vec(i), k=TOPK)),
            "case_topk_median_ms": _median_ms(
                lambda i: mem.similar_cases(_vec(10_000 + i), k=TOPK)
            ),
            "case_topk_filtered_median_ms": _median_ms(
                lambda i: mem.similar_cases(_vec(10_000 + i), k=TOPK, vehicle_id="veh-3")
            ),
            "pattern_topk_median_ms": _median_ms(
                lambda i: mem.similar_patterns(_vec(20_000 + i), k=TOPK), n=N_PATTERNS
            ),
        },
        "recall_sanity": None,
    }
    # Sanidad: cada vector debe recuperarse a sí mismo como primer resultado.
    hits = sum(1 for i in range(50) if know.search(_vec(i), k=1)[0][0].chunk_id == f"c{i}")
    results["recall_sanity"] = {"self_retrieval_top1": f"{hits}/50"}

    # ¿Cuándo compensaría un índice? Se mide IVFFlat sobre el mismo corpus.
    with store.engine.begin() as conn:
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_chunk_emb_ivf ON knowledge.knowledge_chunks "
                "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 40)"
            )
        )
        conn.execute(text("ANALYZE knowledge.knowledge_chunks"))
    results["ivfflat"] = {
        "knowledge_topk_median_ms": _median_ms(lambda i: know.search(_vec(i), k=TOPK)),
        "nota": "índice creado solo para MEDIR; no se adopta hasta que el volumen lo exija",
    }
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
