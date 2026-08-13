# 03 — Modelo relacional (PostgreSQL + pgvector en Edge y en Cloud)

> **Actualizado en F12 (ADR-0030).** La versión anterior de este documento describía
> *SQLite en el edge / PostgreSQL en la nube*; esa combinación **queda obsoleta**. Ahora:
> **PostgreSQL + pgvector en Edge** y **PostgreSQL + pgvector en Cloud**, como **instancias
> independientes con responsabilidades distintas** (el edge opera, la nube consolida) que se
> sincronizan por Outbox lógico, nunca por replicación física. SQLite permanece únicamente
> como camino `LEGACY / TEST COMPATIBILITY`.

[← Índice](README.md)

## Principios

El esquema físico (`diagnostic_agent/storage/schema.py`) es un **espejo por convención de
nombres** de los contratos: mismos campos, mismos ids; los dicts/listas van a columnas JSON
(JSONB en PostgreSQL). Cada tabla declara además su **schema lógico**
(`telemetry`/`events`/`diagnostics`/`models`/`memory`/`knowledge`/`agent`/`sync`; `core`
reservado) — ver [13](13_postgresql_pgvector_edge.md) §3.
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
| Identidad | `snapshot_id`, `schema_version`, `created_at` | UUID global; PK compuesta con `timestamp_utc` (ver Claves) |
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

**Claves (F12/ADR-0030).** PK **compuesta `(snapshot_id, timestamp_utc)`**: PostgreSQL exige
que toda restricción única de una tabla particionada incluya la clave de partición.
`snapshot_id` (UUID) sigue siendo el identificador global de trazabilidad y la columna
principal del índice; la unicidad de `snapshot_id` aislado pasa a ser **lógica**. FK
`session_id → telemetry.telemetry_sessions`. Unicidad lógica `(session_id, sequence_number)`
garantizada por el builder y verificada en tests.

**Índices** (derivados de los query patterns documentados, no al revés):
`ix_snap_vehicle_ts (vehicle_id, timestamp_utc)` · `ix_snap_session_ts (session_id,
timestamp_utc)` · `ix_snap_eventtype_ts (primary_event_type, timestamp_utc)` ·
`ix_snap_ts_brin` (**BRIN** sobre `timestamp_utc`, la tabla se escribe en orden temporal).
Ningún índice adicional sin un patrón de consulta que lo justifique.

**`snapshot_event_links`** (N:M): `(snapshot_id, event_id, event_type)` con FK a
`events.vehicle_events`. Resuelve la pertenencia simultánea (TRIP + ENGINE_WARM +
ACCELERATION + …) **sin duplicar snapshots**. `snapshot_id` **no lleva FK física** desde F12:
la tabla destino está particionada y su unique es compuesta; la integridad es lógica y está
verificada por los tests de provenance (ADR-0030).

**Relaciones.** `telemetry_sessions 1─N snapshots`; `snapshots N─M vehicle_events` (vía
links) + `N─1` al evento primario; los `telemetry_points` del mismo `(session_id,
sequence_number)` son el origen normalizado, y desde ellos se llega a `obd_observations`
(provenance bidireccional verificada en `tests-integration/test_snapshot_e2e.py`).

**Clasificación.** NORMALIZED WIDE / TIME-ALIGNED — **no INFERRED**.

**Retención.** Sigue la política de [09](09_retencion_sincronizacion.md): recientes en edge,
antiguos a cloud/downsample, intervalos anómalos con retención larga, evidencia de
diagnóstico como referencia permanente; nada referenciado por provenance se purga sin
estrategia explícita.

**Particionamiento (ACTIVO desde F12).** Particionado declarativo por rango sobre
`timestamp_utc`, mensual, **también en el edge**, con partición `DEFAULT` de seguridad y
creación anticipada (mes en curso + 3). Retención por `DROP/DETACH PARTITION` solo tras
verificar provenance. Volumen medido: 1 Hz ≈ 107 MB/24 h de base + 162 MB de WAL.

**Motor.** PostgreSQL + pgvector es el oficial: `EdgeStore()` (URL en `MECANICO_DB_URL`).
`EdgeStore(db_path=…)` sigue abriendo el camino SQLite LEGACY con el mismo código y el mismo
modelo, para tests y compatibilidad durante la transición ([13](13_postgresql_pgvector_edge.md)).

## Migraciones

**Alembic es el mecanismo oficial** desde F12 (`make db-upgrade`; revisión base
`0001_pg_edge_baseline`: schemas + extensión `vector` + tablas + particiones + índices). Se
revisó y revirtió la decisión previa de posponerlo: ya no se recrea la base.

`EdgeStore.migrate()` (create_all idempotente + `ensure_partitions`) se conserva para tests y
arranque en seco; `PRAGMA user_version` (**5** desde F12: schemas lógicos, particionado y
columnas de embedding) aplica solo al camino SQLite legacy.

## Edge y Cloud: mismo modelo, instancias independientes

| Aspecto | Edge (PostgreSQL + pgvector) | Cloud (PostgreSQL + pgvector) |
|---|---|---|
| Responsabilidad | operar: capturar, detectar, diagnosticar, recordar | consolidar: histórico multi-vehículo, corpus maestro, métricas |
| Volumen | retención corta/media, un vehículo | histórico largo, N vehículos |
| Particionado de snapshots | mensual + DEFAULT (ya activo) | mensual (mismo diseño) |
| Vectores | chunks, casos y patrones locales | corpus RAG maestro y memoria consolidada |
| Escritores | uno (el runtime) | varios (API de ingesta) |
| Relación | **independientes**: Outbox → API → Cloud, idempotente y versionado — NUNCA replicación física |

Tipos (idénticos en ambos extremos; el camino SQLite legacy los degrada donde no existen):

| Concepto | PostgreSQL | SQLite (LEGACY) |
|---|---|---|
| ids UUID | TEXT/UUID | TEXT |
| dicts/listas | JSONB | JSON |
| instantes | TIMESTAMPTZ | DateTime ISO tz-aware |
| reales | DOUBLE PRECISION | REAL |
| embeddings | `vector(384)` (pgvector) | JSON (coseno en proceso) |
| schemas lógicos | 9 schemas | aplanados con `schema_translate_map` |
| versionado | **Alembic** | PRAGMA user_version |
| particionado | RANGE por `timestamp_utc` | no aplica |

## Retención

La política por clase de dato está en [09](09_retencion_sincronizacion.md); las tablas de la
cadena RAW/NORMALIZED son las únicas con purga programada — todo lo referenciado por
evidencia de diagnóstico se conserva.
