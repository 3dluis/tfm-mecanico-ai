# 07 — Context Engineering

[← Índice](README.md)

Nunca se envía al LLM "toda la base de datos". El contexto de cada llamada se ENSAMBLA
dinámicamente con presupuesto por sección (tokens aproximados por caracteres/4; el
presupuesto total se dimensiona al modelo activo vía ModelRouter):

| Sección | Presupuesto v1 | Prioridad | Fuente |
|---|---|---|---|
| system instructions (rol del agente) | 300 | fija | plantilla versionada (prompt_version) |
| objective | 100 | fija | estado |
| vehicle summary | 100 | alta | repositorio |
| current anomaly (features notables) | 400 | alta | estado (solo features |v|>ε, redondeadas) |
| active hypotheses (+estados) | 300 | alta | estado |
| retrieved cases (top-k, con nivel epistemológico) | 400 | media | Recall |
| retrieved documents (top-k truncados) | 900 | media | Knowledge |
| tool outputs recientes | 300 | media | working memory |
| pending questions | 100 | alta | estado |

Reglas: (1) prioridad ante desbordo — se truncan primero documentos, luego casos; nunca la
anomalía ni las hipótesis; (2) los datos numéricos entran RESUMIDOS (features de ventana,
no series crudas); (3) todo chunk/caso incluido en contexto queda registrado como
RetrievalEvent — el contexto es reconstruible ex post; (4) el ensamblado es una función
pura del estado → testeable y reproducible.


## Decisión F8/F9 — entrada del razonamiento (formal)

```
Window anomaly detector  →  señal PRIMARIA
Event Intelligence       →  contexto / evidencia complementaria
Agent Runtime            →  razona sobre AMBOS
```

El agente NUNCA recibe únicamente `anomaly_score = X`. El contexto diagnóstico
estructurado (context builder, versionado; v1 = `cb:1` en tools/llm_smoke_deep.py)
incluye como mínimo: `vehicle_context · current_event (tipo/contexto del evento
vigente) · anomaly_summary (detector, score, umbral, scope) · relevant_features (PIDs
implicados con dirección) · event_comparison (desviación frente a eventos comparables,
p. ej. 'la relación MAF/RPM se desvía del baseline de aceleraciones equivalentes') ·
historical_baseline (madurez/confianza del EventBaseline) · DTC · historical_context ·
retrieved_evidence`. Nunca telemetría cruda (cientos de muestras) — resúmenes
destilados (§presupuestos de este documento).
