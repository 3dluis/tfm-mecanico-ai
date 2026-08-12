# ADR-0014 — Agente de diagnóstico v1: LangGraph con responsabilidades estrictas

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 4

## Decisión

1. **Grafo lineal v1** (LangGraph, `graph_version=g1`): triage → recall → retrieve →
   hypothesize → verify → report → memorize, con responsabilidades estrictas: solo
   `hypothesize` es generativo; `verify` es DETERMINISTA (reglas por failure_mode contra las
   features reales, produciendo evidencia a favor Y en contra); `report` compone desde
   evidencia; `memorize` registra el episodio y, como única transición de conocimiento,
   patrones CANDIDATE (ADR-0013).
2. **LLM plugable** tras la interfaz `Hypothesizer`: `OllamaHypothesizer` (JSON validado con
   reintento acotado; degradación honesta a "sin hipótesis válidas") y
   `HeuristicHypothesizer` determinista (CI/experimentos reproducibles y brazo "sin LLM" del
   estudio comparativo). La selección de modelo sigue abierta (smoke test del autor).
3. **RAG v1 léxico y determinista** sobre corpus propio (7 fichas CC-BY-4.0 germinadas de
   las firmas del catálogo de fallos); mismo contrato (KnowledgeChunk/RetrievalEvent) que la
   futura recuperación densa (Chroma+embeddings) — cambiará el ranking, no el modelo de datos.
4. **Todo persistido**: AgentRun (con memory_mode, latencia, tokens), AgentStep por nodo
   (E/S estructuradas, sin chain-of-thought), RetrievalEvent, caso/hipótesis/evidencias y
   ProvenanceRecord.

## Comportamiento verificado (tests-integration/test_agent_v1_behavior.py)

Fallo conocido (fuga de vacío) → hipótesis top `vacuum_leak` SUPPORTED con evidencia
telemétrica; anomalía held-out → INCONCLUSIVE/CONTRADICTED + LearnedPattern CANDIDATE (el
agente NO alucina una causa: declara patrón no cubierto — germen operativo de la PI y del
experimento H2b); memory_mode=none no consulta memoria; el 2º caso similar recupera al 1º.

## Alternativas consideradas

- *Grafo con bucles/reintentos (re-hypothesize si verify contradice):* valioso, pospuesto a
  v2 con datos de fallo reales del v1 — v1 prioriza evaluabilidad.
- *Verify con LLM-as-judge:* contradice el requisito de determinismo del autor y RI4;
  descartado para verify (podrá complementar la rúbrica de explicaciones, no la verificación).
