# 05 — Tool Registry

[← Índice](README.md) · ADR: [0016](../adr/0016-tool-registry-y-seguridad.md)

Registro formal y único de las capacidades del runtime. Ningún agente ejecuta nada que no
esté registrado; el Supervisor tampoco toca SQL: **todo acceso a datos pasa por
herramientas/repositorios controlados**.

## Especificación de cada herramienta

`name · description · input_schema · output_schema · timeout_s · permissions (roles que
pueden invocarla) · side_effects (none|local_write|vehicle_write|network) · idempotent ·
risk_level (READ_ONLY | SAFE_LOCAL | VEHICLE_WRITE | EXTERNAL)`

## Catálogo v1 (implementado en el slice ⭐; el resto especificado)

| Herramienta | Riesgo | Side effects | Idem. | Notas |
|---|---|---|---|---|
| read_pid / read_multiple_pids ⭐ | READ_ONLY | none | ✔ | vía TransportLayer |
| read_dtc · get_freeze_frame | READ_ONLY | none | ✔ | |
| query_telemetry ⭐ / query_session ⭐ / query_vehicle_history | READ_ONLY | none | ✔ | repositorios sobre SQLite |
| calculate_feature ⭐ / calculate_statistics / compare_signals | SAFE_LOCAL | none | ✔ | features canónicas |
| run_anomaly_model ⭐ / run_model | SAFE_LOCAL | local_write (inferencia persistida) | ✔ | ONNX + manifest |
| retrieve_document / retrieve_chunks ⭐ | SAFE_LOCAL | local_write (RetrievalEvent) | ✔ | |
| search_case_memory ⭐ / search_learned_patterns ⭐ | SAFE_LOCAL | local_write (RetrievalEvent) | ✔ | etiqueta epistemológica |
| request_measurement ⭐ / run_diagnostic_test | READ_ONLY | none | ✖ (consume tiempo) | adquisición dirigida |
| store_case ⭐ / store_evidence ⭐ / store_feedback | SAFE_LOCAL | local_write | ✖ | Memory Agent |
| clear_dtc · reset_ecu · active_test | **VEHICLE_WRITE** | vehicle_write | ✖ | **NO registradas en v1**: exigirán confirmación humana explícita + doble validación; fuera de la autonomía inicial (doc 10) |

Toda ejecución se registra (tool, agente, inputs/outputs resumidos, duración, error) en el
historial de ejecución (AgentStep.tools_used + métricas; doc 11), y cuenta contra los
presupuestos del loop (max_tool_calls).
