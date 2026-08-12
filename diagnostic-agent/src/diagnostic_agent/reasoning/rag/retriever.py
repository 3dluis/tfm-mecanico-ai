"""RAG v1: ingesta del corpus y recuperación léxica auditada.

Decisión ADR-0014: el retriever v1 es LÉXICO y determinista (solape de términos con
ponderación tf) para que la iteración sea evaluable sin depender de modelos de
embeddings; la recuperación densa (ChromaDB + sentence-transformers) se incorpora en la
iteración RAG siguiendo el mismo contrato (``KnowledgeChunk`` + ``RetrievalEvent``).
"""

import hashlib
import re
import unicodedata
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import yaml

from diagnostic_agent.storage.schema import KnowledgeChunkRow, KnowledgeDocumentRow
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import KnowledgeChunk, KnowledgeDocument

_STOP = {
    "de",
    "la",
    "el",
    "en",
    "y",
    "a",
    "los",
    "las",
    "del",
    "que",
    "con",
    "por",
    "un",
    "una",
    "se",
    "su",
    "al",
    "es",
    "o",
    "para",
    "más",
    "entre",
    "sin",
    "sobre",
    "como",
    "muy",
}


def _tokens(text: str) -> list[str]:
    norm = unicodedata.normalize("NFKD", text.lower())
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9_]+", norm) if t not in _STOP and len(t) > 2]


def ingest_corpus(store: EdgeStoreV2, corpus_path: Path) -> int:
    """Carga el corpus YAML como documentos+chunks (idempotente por checksum)."""
    raw = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))
    n = 0
    for doc in raw["documents"]:
        checksum = hashlib.sha256(doc["text"].encode()).hexdigest()[:16]
        if store.count(KnowledgeDocumentRow, document_id=doc["id"]) == 0:
            store.add(
                KnowledgeDocumentRow,
                KnowledgeDocument(
                    document_id=doc["id"],
                    title=doc["title"],
                    source="Mecánico IA (obra propia)",
                    license="CC-BY-4.0",
                    checksum=checksum,
                    ingested_at=datetime.now(tz=UTC),
                ),
            )
            store.add(
                KnowledgeChunkRow,
                KnowledgeChunk(
                    chunk_id=f"{doc['id']}#0",
                    document_id=doc["id"],
                    seq=0,
                    text=doc["text"].strip(),
                    metadata={k: str(v) for k, v in doc.get("metadata", {}).items()},
                ),
            )
            n += 1
    return n


class LexicalRetriever:
    """Recuperación por solape de términos ponderado (determinista, reproducible)."""

    def __init__(self, store: EdgeStoreV2) -> None:
        self._chunks = store.raw_rows(KnowledgeChunkRow)

    def search(self, query: str, k: int = 3) -> list[tuple[str, float, dict[str, str]]]:
        """Devuelve [(chunk_id, score, metadata)] ordenado por score descendente."""
        q = Counter(_tokens(query))
        scored: list[tuple[str, float, dict[str, str]]] = []
        for chunk in self._chunks:
            c = Counter(_tokens(chunk.text))
            overlap = sum(min(q[t], c[t]) for t in q)
            denom = (sum(q.values()) * max(1, len(c))) ** 0.5
            score = overlap / denom if denom else 0.0
            if score > 0:
                scored.append((chunk.chunk_id, round(score, 5), dict(chunk.meta)))
        scored.sort(key=lambda x: -x[1])
        return scored[:k]

    def chunk_text(self, chunk_id: str) -> str:
        for chunk in self._chunks:
            if chunk.chunk_id == chunk_id:
                return str(chunk.text)
        return ""
