# 10 — Modelo vectorial y RAG

[← Índice](README.md) · ADR: [0014](../adr/0014-agente-v1.md)

## Entidades

**KnowledgeDocument** (título, fuente, LICENCIA obligatoria, versión, checksum) →
**KnowledgeChunk** (texto, metadata `failure_mode`/`component`, `embedding_ref`) →
**RetrievalEvent** (query, ids recuperados, scores, `used_in_hypothesis_ids`).

`embedding_ref` referencia el vector en el índice (Chroma en su iteración); el vector NO se
guarda en SQL — la BD relacional gobierna identidad y procedencia, el índice vectorial es
un derivado reconstruible del corpus.

## Grounding medible (por diseño)

Con RetrievalEvent + DiagnosticEvidence(kind=document) se calculan directamente:
- **grounding**: fracción de hipótesis con evidencia documental que las apoya;
- **calidad de recuperación**: ¿los chunks usados en la hipótesis ganadora estaban en el top-k?;
- **cobertura documental**: anomalías sin ningún chunk relevante (huecos del corpus);
- **respuestas sin respaldo**: hipótesis SUPPORTED sin documento ni telemetría — deben ser cero.

## Estado v1 y plan

v1 (esta iteración): retriever LÉXICO determinista (reproducible, sin dependencias pesadas)
sobre el corpus propio de fichas (`diagnostic-agent/knowledge/corpus_v1.yaml`, CC-BY-4.0,
7 documentos). Iteración RAG (pendiente de aprobación): embeddings sentence-transformers +
ChromaDB con el MISMO contrato (chunks/eventos idénticos, cambia el ranking), corpus ampliado
con manifiesto de licencias, y evaluación hit-rate/MRR contra un set de consultas etiquetado.
