# 03 — Modelo relacional (SQLite edge / PostgreSQL cloud)

[← Índice](README.md)

## Principios

El esquema físico (`diagnostic_agent/storage/schema.py`) es un **espejo por convención de
nombres** de los contratos: mismos campos, mismos ids; los dicts/listas van a columnas JSON.
No redefine semántica — esa vive en los contratos y en el [diccionario](02_diccionario_datos.md).
El mapeo contrato↔fila es genérico (`storage/store.py::_to_row/_to_contract`) y está cubierto
por los tests de integridad.

## Tablas

telemetry_sessions · obd_observations · telemetry_points · **vehicle_telemetry_snapshots** ·
**snapshot_event_links** · vehicle_events · event_feature_vectors · event_baselines ·
telemetry_windows · feature_vectors · model_inferences · detected_anomalies ·
diagnostic_cases · diagnostic_hypotheses · diagnostic_evidence · provenance_records ·
case_memory · learned_patterns · pattern_relations · diagnostic_feedback ·
maintenance_events · agent_runs · agent_steps · retrieval_events ·
knowledge_documents/knowledge_chunks · sync_outbox

Índices: por session_id en toda la cadena de telemetría; por case_id en diagnóstico;
por status/epistemic_level/memory_mode donde se filtra.

## `vehicle_telemetry_snapshots` (entidad física, F11 / ADR-0025)

**Propósito.** Materializar la representación canónica **horizontal** y alineada en el tiempo
(una fila = estado multivariable del vehículo en un instante de la rejilla) para que ML,
Event Intelligence, análisis longitudinal, estadística y visualización consulten
directamente sin pivotar `telemetry_points` en cada consumidor. Semántica completa en
[11](11_vehicle_telemetry_snapshot.md).

**Columnas** (espejo del contrato `VehicleTelemetrySnapshot`, 45 campos; tipos y unidades en
el [diccionario](02_diccionario_datos.md)):

| Grupo | Columnas | Nota |
|---|---|---|
| Identidad | `snapshot_id` (PK), `schema_version`, `created_at` | id UUID global (sincronización idempotente) |
| Contexto | `vehicle_id`, `device_id`, `session_id` (FK), `trip_id` | `trip_id` = evento TRIP contenedor |
| Tiempo | `timestamp_utc`, `sequence_number`, `snapshot_interval_ms`, `synchronization_version` | `timestamp_utc` canónico; la sincronización fina local usa reloj monotónico del adquisidor |
| Evento | `primary_event_id` (FK), `primary_event_type`, `vehicle_state` | evento HOJA más específico; el resto vía N:M |
| OBD estándar | `rpm`, `vehicle_speed`, `throttle_position`, `engine_load`, `coolant_temperature`, `intake_air_temperature`, `maf`, `map_kpa`, `stft_bank1`, `ltft_bank1`, `stft_bank2`, `ltft_bank2`, `fuel_pressure`, `fuel_level`, `timing_advance`, `o2_sensor_1`, `o2_sensor_2`, `commanded_equivalence_ratio`, `active_dtc_count` | todas `REAL NULL`; NULL ≠ 0 (ADR-0027) |
| Eléctrico | `battery_voltage` | OBD estándar (PID 42) o sensor de plataforma |
| IMU | `acceleration_x/y/z`, `gyro_x/y/z` | fuera del ciclo OBD; simulado primero (ADR-0020) |
| GPS | `gps_speed`, `gps_heading` | opcional; hoy no sondeado |
| Calidad | `quality_score`, `missing_metric_count`, `quality_flags` (JSON) | flags COMPACTOS: solo señales ≠ `measured` |

No hay columnas de fabricante específico todavía (cuando las haya: prefijo `mfg_` y registro
explícito en el diccionario, nunca mezcladas con las estándar). **Prohibido** añadir columnas
derivadas (`rpm_mean_10s`, `maf_std`, correlaciones): pertenecen a `feature_vectors` /
`event_feature_vectors`.

**Claves.** PK `snapshot_id`. FK `session_id → telemetry_sessions`,
`primary_event_id → vehicle_events`. Unicidad lógica `(session_id, sequence_number)`
(no declarada como constraint física para no penalizar el batch insert; garantizada por el
builder y verificada en tests).

**Índices** (derivados de los query patterns documentados, no al revés):
`ix_snap_vehicle_ts (vehicle_id, timestamp_utc)` · `ix_snap_session_ts (session_id,
timestamp_utc)` · `ix_snap_eventtype_ts (primary_event_type, timestamp_utc)`. Ningún índice
adicional sin un patrón de consulta que lo justifique.

**`snapshot_event_links`** (N:M): `(snapshot_id, event_id, event_type)`, FKs a
`vehicle_telemetry_snapshots` y `vehicle_events`. Resuelve la pertenencia simultánea
(TRIP + ENGINE_WARM + ACCELERATION + …) **sin duplicar snapshots**.

**Relaciones.** `telemetry_sessions 1─N snapshots`; `snapshots N─M vehicle_events` (vía
links) + `N─1` al evento primario; los `telemetry_points` del mismo `(session_id,
sequence_number)` son el origen normalizado, y desde ellos se llega a `obd_observations`
(provenance bidireccional verificada en `tests-integration/test_snapshot_e2e.py`).

**Clasificación.** NORMALIZED WIDE / TIME-ALIGNED — **no INFERRED**.

**Retención.** Sigue la política de [09](09_retencion_sincronizacion.md): recientes en edge,
antiguos a cloud/downsample, intervalos anómalos con retención larga, evidencia de
diagnóstico como referencia permanente; nada referenciado por provenance se purga sin
estrategia explícita.

**Particionamiento.** En PostgreSQL, particionado declarativo por rango sobre
`timestamp_utc`, granularidad mensual como **candidato** (ADR-0028); no se crean particiones
sin evaluar volumen real (1 Hz ≈ 2.6 M filas/mes/vehículo). En SQLite no aplica: el edge se
apoya en retención corta.

**Mapeo SQLite/PostgreSQL.**

| SQLite (edge) | PostgreSQL (cloud/edge experimental) |
|---|---|
| `TEXT` (ids, enums, `vehicle_state`) | `TEXT`/`UUID` |
| `REAL NULL` (señales) | `DOUBLE PRECISION NULL` |
| `DateTime` tz-aware | `TIMESTAMPTZ` |
| `JSON` (`quality_flags`) | `JSONB` (indexable GIN si algún día se filtra por flag) |
| tabla única | tabla particionada por mes (candidato) |

El MISMO código crea ambos esquemas: `EdgeStoreV2(db_path=…)` o
`EdgeStoreV2(url="postgresql+psycopg://…")` — verificado en el benchmark de
[12](12_edge_database_evaluation.md).

## Migraciones

`EdgeStoreV2.migrate()`: crea tablas ausentes y sella `PRAGMA user_version = SCHEMA_DB_VERSION`
(**4** desde F11: +`vehicle_telemetry_snapshots`, +`snapshot_event_links`); rechaza abrir una
BD con versión más nueva que el runtime. En PostgreSQL el `PRAGMA` no aplica (el sellado de
versión se hará con tabla `schema_migrations`/alembic). Decisión: alembic se pospone hasta que
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
