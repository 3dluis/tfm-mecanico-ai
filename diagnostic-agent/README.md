# diagnostic-agent — Mecánico IA Edge Agent Runtime

> Desde F5 este dominio implementa el **Edge Agent Runtime multiagente**
> ([docs/agent-runtime/](../docs/agent-runtime/README.md), ADR-0015): Supervisor LangGraph +
> agentes lógicos con Tool Registry, loop engineering y feature flags A0–A6. El nombre
> físico del directorio se conserva deliberadamente.

Núcleo inteligente EDGE (objetivo: Raspberry Pi 5, 8 GB).

## Estado

- **Pipeline validado en vivo** (F3): adquisición (TransportLayer serial|tcp) → normalización
  → SQLite → features canónicas → detección ONNX (LOF elegido, ADR-0011).
- **Esquema de datos v2** (F4, ADR-0012): 21 tablas espejo de los contratos con trazabilidad
  anomalía→raw por FK y provenance obligatoria. Ver
  [docs/data-architecture/](../docs/data-architecture/README.md).
- **Agente LangGraph v1** (ADR-0014): `triage→recall→retrieve→hypothesize→verify→report→
  memorize`; solo hypothesize es generativo (LLM plugable: Ollama o heurístico determinista);
  verify es determinista contra telemetría; memorize registra episodios y patrones CANDIDATE
  (nunca promociona automáticamente, ADR-0013).

Separación estricta ML/LLM (ADR-0009): `detection/` y `reasoning/` no se importan entre sí;
el LLM jamás decide anomalías.

## Corpus RAG v1

`knowledge/corpus_v1.yaml` — 7 fichas técnicas propias (CC-BY-4.0); retriever léxico
determinista en v1 (ADR-0014 §3), recuperación densa en la iteración RAG.

Configuración: variables `MECANICO_*` (ver `.env.example` raíz). API: `/health`, `/ready`.
