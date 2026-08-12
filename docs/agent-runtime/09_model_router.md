# 09 — Model Router (concepto; implementación mínima)

[← Índice](README.md) · Diagrama: [model-router.mmd](diagrams/model-router.mmd)

Abstracción rol→modelo para que los agentes lógicos compartan modelos físicos y el hardware
dicte el despliegue. v1: tabla estática de configuración; NO se despliegan múltiples LLM.

| Tarea | v1 (RPi 5 realista) | Futuro |
|---|---|---|
| triage / tareas simples | política determinista (sin LLM) | SLM rápido (1B) |
| hipótesis / crítica / informe | LLM local único (a elegir con llm-smoke) o heurístico | modelo de más razonamiento |
| RAG / búsqueda de memoria | léxico v1 | modelo de embeddings compacto |
| detección de anomalías | LOF ONNX (ADR-0011) | + modelos temporales si superan a LOF |

Contratos: cada resolución del router queda en `AgentRun.llm_model` y `AgentRun.config`
(mapa tarea→modelo) — dos runs solo son comparables si su mapa coincide (política de
versionado, data-architecture/07). El router también centraliza presupuestos de contexto
por modelo (doc 07).
