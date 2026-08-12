# 10 — Integración con el Agent Runtime

[← Índice](README.md)

## Event Detection Service (NO es un agente LLM)

Componente determinista/ML que corre en el pipeline de telemetría (tras la normalización) y
mantiene el estado vehicular + eventos al día. El runtime lo CONSUME vía Tool Registry.

## Nuevas herramientas (con esquemas estrictos; se añaden al catálogo ADR-0016)

`get_vehicle_state` · `query_vehicle_events` (filtros tipo/tiempo/trip) · `get_event_details`
· `get_event_telemetry` (segmento raw del evento) · `calculate_event_features` ·
`find_comparable_events` (mismo context_signature) · `compare_events` ·
`get_event_baseline` · `run_event_anomaly_detector` — todas READ_ONLY/SAFE_LOCAL.

## Efecto en los agentes

- **Telemetry Agent**: estado y eventos recientes como primera fuente de contexto.
- **Anomaly Agent**: además de ventanas, analiza event-aware (scope=EVENT).
- **Diagnostic Agent** recibe contexto YA DESTILADO (context engineering, agent-runtime/07):
  "Anomalía durante ACCELERATION (7,1 s, 41→81 km/h, motor caliente); 47 eventos comparables;
  desviaciones: maf_response −18 %, stft +6 %" — nunca miles de muestras; el raw se pide por
  tool si hace falta.
- **Verification Agent**: las reglas ganan condiciones de contexto ("en aceleraciones,
  MAF_response bajo con trims compensando → admisión") — más precisas que sobre ventanas.
