# 03 — Supervisor / Orchestrator

[← Índice](README.md)

## Responsabilidades (y NO responsabilidades)

Recibe el objetivo; administra el estado del caso; selecciona el próximo agente; decide qué
herramienta procede; detecta información faltante; controla iteraciones y límites; detiene
el proceso; escala cuando no hay evidencia suficiente. **No diagnostica él mismo**: si el
Supervisor necesitara "opinar" sobre causas, esa lógica pertenece a Diagnostic/Critic.

## DiagnosticState (estado explícito del grafo)

```python
DiagnosticState:
  # identidad y objetivo
  case_id · vehicle_id · session_id · objective
  # contexto observado
  telemetry_context        # resumen de ventanas/features disponibles
  detected_anomalies       # anomalías disparadoras + adquiridas en el loop
  dtcs
  # investigación
  active_hypotheses        # con rank/estado/confianza (contratos v2)
  evidence                 # DiagnosticEvidence acumulada (±)
  retrieved_documents      # chunks citados
  retrieved_cases          # casos/patrones con score y nivel epistemológico
  pending_questions        # qué falta por responder (alimenta la re-planificación)
  current_plan             # lista ordenada de acciones previstas (mutable)
  # control del loop
  iteration · tool_calls · llm_calls
  confidence               # de la mejor hipótesis verificada
  status                   # investigating | concluding | stopped
  next_action              # decisión del supervisor (enrutado LangGraph)
  outcome                  # CONFIRMED | PROBABLE | INCONCLUSIVE | INSUFFICIENT_DATA | ESCALATE | FAILED
```

Implementación: TypedDict de LangGraph; la working memory (doc 08) ES este estado — se
persiste solo su traza (AgentStep.inputs/outputs por nodo), nunca razonamiento libre.

## Política de decisión

v1 (vertical slice): política DETERMINISTA por prioridades — evaluable y depurable:
`sin anomalía→Anomaly · sin recuerdos→Recall · sin documentos→Knowledge · sin hipótesis→
Diagnostic · hipótesis sin verificar→Verification · verificadas→Critic · crítica pide más
evidencia y quedan presupuesto→Telemetry(plan) y reintentar · si no→Report`.
v2 (posterior): el LLM propone `next_action` y la política determinista VALIDA la
transición (lista blanca de transiciones legales + límites) — el LLM sugiere, el control es
del código. La re-planificación (doc 06) muta `current_plan` y queda persistida.
