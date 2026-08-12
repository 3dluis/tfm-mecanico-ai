# 03 — Modelo relacional (SQLite edge / PostgreSQL cloud)

[← Índice](README.md)

## Principios

El esquema físico (`diagnostic_agent/storage/schema.py`) es un **espejo por convención de
nombres** de los contratos: mismos campos, mismos ids; los dicts/listas van a columnas JSON.
No redefine semántica — esa vive en los contratos y en el [diccionario](02_diccionario_datos.md).
El mapeo contrato↔fila es genérico (`storage/store.py::_to_row/_to_contract`) y está cubierto
por los tests de integridad.

## Tablas (21)

telemetry_sessions · obd_observations · telemetry_points · telemetry_windows ·
feature_vectors · model_inferences · detected_anomalies · diagnostic_cases ·
diagnostic_hypotheses · diagnostic_evidence · provenance_records · case_memory ·
learned_patterns · pattern_relations · diagnostic_feedback · maintenance_events ·
agent_runs · agent_steps · retrieval_events · knowledge_documents/knowledge_chunks ·
sync_outbox

Índices: por session_id en toda la cadena de telemetría; por case_id en diagnóstico;
por status/epistemic_level/memory_mode donde se filtra.

## Migraciones

`EdgeStoreV2.migrate()`: crea tablas ausentes y sella `PRAGMA user_version = 2`; rechaza
abrir una BD con versión más nueva que el runtime. Decisión: alembic se pospone hasta que
exista un despliegue con datos que conservar (hoy la BD es regenerable); cuando llegue, la
numeración `user_version` se traslada a revisiones alembic sin cambio de modelo.

## Equivalencia PostgreSQL (cloud)

| SQLite (edge) | PostgreSQL (cloud) | Nota |
|---|---|---|
| TEXT (ids UUID) | UUID | mismos valores; cast directo |
| JSON | JSONB | consultas indexables (GIN) en cloud |
| DateTime (ISO, tz) | TIMESTAMPTZ | ya se escribe timezone-aware |
| REAL | DOUBLE PRECISION | — |
| PRAGMA user_version | tabla schema_migrations / alembic | — |
| BD única | esquemas por dominio (telemetry, diagnostics, knowledge, registry) | particionado de telemetría histórica por mes |

El cloud reutiliza los mismos contratos; su DDL se generará de este mismo módulo con
dialecto PostgreSQL cuando se implemente la ingesta (la nube sigue siendo secundaria).

## Retención

La política por clase de dato está en [09](09_retencion_sincronizacion.md); las tablas de la
cadena RAW/NORMALIZED son las únicas con purga programada — todo lo referenciado por
evidencia de diagnóstico se conserva.
