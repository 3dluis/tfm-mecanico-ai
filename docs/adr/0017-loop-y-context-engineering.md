# ADR-0017 — Loop engineering con límites duros y context engineering presupuestado

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 5 · **Docs:** agent-runtime/06 y 07

## Decisión

1. Ciclo iterativo OBSERVE→ANALYZE→PLAN→ACT→VERIFY→CRITIQUE con re-planificación dinámica
   persistida (current_plan en el estado; trazas en AgentRun/AgentStep).
2. **Stop conditions como límites duros**: max_iterations/execution_time/hypotheses/
   tool_calls/tool_retries/llm_calls + minimum_evidence/confidence. Agotar presupuesto
   fuerza Report con outcome honesto.
3. Outcomes válidos: CONFIRMED · PROBABLE · INCONCLUSIVE · INSUFFICIENT_DATA · ESCALATE ·
   FAILED. **INCONCLUSIVE/INSUFFICIENT_DATA son resultados correctos** — nunca se fuerza
   una respuesta (CONFIRMED requiere además feedback externo, ADR-0013).
4. Contexto del LLM ensamblado dinámicamente por secciones con presupuesto y prioridad
   (system+objective+vehicle+anomaly+hypotheses+cases+documents+tool outputs+questions);
   función pura del estado, reconstruible ex post vía RetrievalEvent.
5. Política de decisión v1 determinista; v2 permitirá que el LLM PROPONGA `next_action`
   validada contra transiciones legales — el control siempre es del código.

## Consecuencias

Convergencia y coste acotados por construcción; comparabilidad entre runs garantizada
(mismos presupuestos = misma configuración experimental).
