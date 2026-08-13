# 13 — PostgreSQL + pgvector en el Edge (plataforma oficial de persistencia)

[← Índice](README.md) · **ADR-0030** (supera a ADR-0029) · Informe:
[fase12](../fase12/informe_migracion_postgresql.md)

## 1. Objetivo

Un **único motor** para todo lo que el edge necesita recordar: telemetría y snapshots,
eventos y features, anomalías y casos diagnósticos, ejecuciones de agentes, memoria episódica
y evolutiva, corpus RAG, embeddings, metadatos de modelos y la cola de sincronización.

```
Raspberry Pi → PostgreSQL 16 + pgvector
   telemetry · events · diagnostics · models · memory · knowledge · agent · sync
```

La razón no es rendimiento: es **alcance**. El edge dejó de ser un colector OBD con
inferencia y pasó a ser plataforma de telemetría + runtime ML + runtime multiagente + RAG
local + memoria. Con SQLite eso exigía tres sistemas (fichero relacional + almacén vectorial
+ ficheros sueltos); con PostgreSQL+pgvector es uno. Los costes de esa unificación están
medidos y declarados en §10, no escondidos.

## 2. Configuración y despliegue

```bash
make db-up        # levanta edge-postgres (pgvector/pgvector:pg16, multi-arch)
make db-upgrade   # aplica migraciones Alembic  ← mecanismo OFICIAL de esquema
make dev          # PostgreSQL + OBD Lab + agente + ollama, sin Cloud
make test-pg      # tests de integración REALES contra PostgreSQL
```

Conexión: `MECANICO_DB_URL=postgresql+psycopg://mecanico:mecanico@localhost:15432/mecanico_edge`.
Stack: **SQLAlchemy 2.x + psycopg 3**; pool **conservador** (5 conexiones + 2 de overflow) —
esto es una Raspberry Pi, no un servidor. Credenciales por variables de entorno
(`MECANICO_PG_USER/PASSWORD/DB/PORT`), nunca en el repositorio.

Perfil de tuning: `deploy/postgres/edge-postgresql.conf` (§9).

## 3. Schemas lógicos

| Schema | Contenido |
|---|---|
| `telemetry` | sessions · obd_observations · telemetry_points · **vehicle_telemetry_snapshots** · snapshot_event_links · windows · feature_vectors |
| `events` | vehicle_events · event_feature_vectors · event_baselines |
| `diagnostics` | detected_anomalies · cases · hypotheses · evidence · provenance · feedback · maintenance |
| `models` | model_inferences (+ registro de modelos cuando deje de vivir en ficheros) |
| `memory` | case_memory · learned_patterns · pattern_relations |
| `knowledge` | knowledge_documents · knowledge_chunks |
| `agent` | agent_runs · agent_steps · retrieval_events |
| `sync` | sync_outbox |
| `core` | **reservado**: hoy no existen contratos `Vehicle`/`EdgeDevice` y no se inventan entidades para llenarlo |

Evaluación de la propuesta inicial (9 schemas): se adoptan porque coinciden con fronteras de
dominio que ya existían en el modelo y no complican las consultas (los joins entre schemas en
PostgreSQL no tienen coste adicional). Dos ajustes honestos: `core` queda vacío hasta que
existan sus entidades, y `retrieval_events` va a `agent` (es actividad del agente sobre el
conocimiento, no parte del corpus).

El camino **SQLite legacy** aplana todos los schemas con `schema_translate_map` → el mismo
código y el mismo modelo funcionan en ambos motores mientras dure la transición.

## 4. `telemetry.vehicle_telemetry_snapshot`: particionado y claves

Tabla **particionada por rango sobre `timestamp_utc`**, particiones mensuales
(`telemetry.snapshots_2026_08`, `_09`, …) + una partición **`DEFAULT`** de seguridad: una fila
con timestamp fuera de rango no se pierde ni rompe la ingesta.

Política de creación (simple a propósito): mes en curso + 3 por delante, creadas por
adelantado en la migración y por `ensure_partitions()` al arrancar. Un TFM de pocos meses no
necesita automatismos sofisticados; necesita que nunca falte la partición del mes.

**Clave primaria.** PostgreSQL exige que toda restricción única de una tabla particionada
incluya la clave de partición, así que la PK es **compuesta `(snapshot_id, timestamp_utc)`**:

- `snapshot_id` (UUID) sigue siendo el identificador **global** de trazabilidad y la columna
  principal del índice, de modo que buscar por id sigue usando la PK;
- lo que se pierde es la unicidad *física* de `snapshot_id` aislado — pasa a ser garantía
  lógica (UUIDv4, generado en el builder);
- por el mismo motivo, `snapshot_event_links.snapshot_id` **no lleva FK física**: la
  integridad es lógica y está verificada por los tests de provenance.

Esta es exactamente la clase de decisión que el enunciado pedía no dar por supuesta.

## 5. Índices

Derivados de los query patterns documentados ([11 §6](11_vehicle_telemetry_snapshot.md)):
`(vehicle_id, timestamp_utc)` · `(session_id, timestamp_utc)` ·
`(primary_event_type, timestamp_utc)` · **BRIN** sobre `timestamp_utc`
(`pages_per_range=32`): la tabla se escribe en orden temporal, así que el BRIN ocupa una
fracción de un B-tree. Nada más sin un patrón que lo justifique — y lo que se añada, se mide.

## 6. Ingesta por lotes y persistencia asíncrona

```
OBD/IMU → buffer en memoria → normalización → snapshot builder → cola acotada
        → PersistenceWorker (hilo) → lote → PostgreSQL
```

- **Nunca un COMMIT por PID.** Lote por tamaño (500) o por tiempo (2 s), lo que ocurra antes.
- **Cola acotada** con contrapresión explícita: `BLOCK` (no perder datos, por defecto) o
  `DROP_OLDEST` (no congelar la adquisición) — y lo descartado **se cuenta**, nunca se pierde
  en silencio.
- Un fallo temporal de la base **no detiene la adquisición**: reintentos con backoff acotado y
  contador de fallos visible en las métricas.
- Caminos de escritura medidos (§10): `executemany` ~5 100–5 600 filas/s y **COPY ~9 700
  filas/s**. A 1 Hz sobra con ambos; COPY queda disponible para volcados masivos.

## 7. pgvector: qué se vectoriza y qué no

Extensión activada en la migración (`CREATE EXTENSION vector`). Embeddings (384 dims) solo en:

- `knowledge.knowledge_chunks.embedding` — RAG técnico;
- `memory.case_memory.embedding` — casos similares;
- `memory.learned_patterns.embedding` — patrones relacionados;
- *más adelante*, `events.event_signature_embedding` **solo si demuestra utilidad**.

**La telemetría no se vectoriza.** Las series temporales se analizan con SQL, features,
estadística y ML; pgvector no sustituye a los modelos de series temporales. El vector es una
columna **física**: no viaja en el contrato de intercambio (evita inflar el outbox).

**Estrategia inicial: búsqueda EXACTA sin índice.** Medido con 1 600 vectores: 2.97 ms
(chunks), 3.49 ms (casos), 3.19 ms (patrones); con IVFFlat 2.30 ms — la ganancia todavía no
justifica el índice. HNSW/IVFFlat cuando el volumen lo pida, no antes.

**Filtrado relacional + vectorial en la MISMA consulta** (la ventaja que motivó la adopción):

```sql
SELECT case_memory_id, embedding <=> :q AS d
FROM memory.case_memory
WHERE vehicle_id = :v AND epistemic_level = 'human_validated'
ORDER BY embedding <=> :q LIMIT 5;
```

Expuesto por repositorio: `similar_cases(embedding, k=5, vehicle_id=...)`. Verificado por test.

**Hybrid retrieval** (semántico + metadatos + full-text) queda **preparado conceptualmente**:
PostgreSQL ya trae `tsvector`, así que combinarlo con pgvector no exigirá otro sistema. No se
implementa todavía.

## 8. Acceso desde el Agent Runtime

```
Agent → Tool (entradas/salidas tipadas) → Repository → PostgreSQL
```

**Nunca** `LLM → SQL arbitrario → base`. Los repositorios (`TelemetryRepository`,
`EventRepository`, `DiagnosticRepository`, `MemoryRepository`, `KnowledgeRepository`,
`AgentRunRepository`, `ModelRepository`) son la única frontera con el motor y no aceptan SQL
del exterior. LangGraph no toca el ORM ni el driver.

**Fronteras transaccionales.** Deben ser atómicas: (1) `DiagnosticCase` + evidencias +
provenance + sobre de outbox; (2) snapshot + sus enlaces N:M; (3) toda escritura de negocio
junto a su outbox — `store.add_with_outbox(...)` y `store.transaction()` lo garantizan: si
falla el commit no queda ni el hecho ni su sobre.

## 9. Tuning conservador para Raspberry Pi

`deploy/postgres/edge-postgresql.conf` — punto de partida razonado, **no** una optimización:
`shared_buffers 512MB` · `effective_cache_size 2GB` · `work_mem 8MB` ·
`maintenance_work_mem 128MB` · `max_connections 20` · `wal_compression zstd` ·
`max_wal_size 1GB` · autovacuum algo más agresivo · `random_page_cost 1.1` (SSD).

`synchronous_commit` se mantiene **ON**: no se sacrifica durabilidad sin decisión explícita.
Cada valor debe confirmarse con `make pg-bench` sobre hardware real antes de darlo por bueno.

## 10. Consumo medido (dimensionamiento, no decisión)

Sandbox x86 4 CPU/8 GB como **proxy** de RPi 5, 1 Hz, PostgreSQL 16.13 con
**configuración por defecto** (`shared_buffers 128MB`, `wal_compression off`) — es decir, sin
el perfil de §9 aplicado; repetir con él es tarea pendiente:

| Volumen | Filas | BD | **WAL generado** | Batch (executemany) | Q sesión | Q evento | RSS postgres |
|---|---|---|---|---|---|---|---|
| 1 h | 3 600 | 16.9 MB | 6.7 MB | 5 570 filas/s | 104 ms | 35 ms | 140 MB |
| 8 h | 28 800 | 43.8 MB | 53.4 MB | 5 224 filas/s | 108 ms | 229 ms | 170 MB |
| 24 h | 86 400 | 106.9 MB | 161.7 MB | 5 068 filas/s | 109 ms | 1 160 ms | 236 MB |
| 8 h (COPY) | 28 800 | 44.2 MB | 52.0 MB | **9 703 filas/s** | 103 ms | 411 ms | 236 MB |

Lecturas honestas:

- **Disco:** 106.9 MB/24 h frente a 86.7 MB de SQLite (**+23 %**).
- **WAL:** 161.7 MB por 24 h de datos ⇒ amplificación de escritura ≈2.5×. En tarjeta SD eso
  importa: **se recomienda SSD** (§11).
- **RAM:** 140–236 MB residentes. Con un LLM de ~2–4 GB en 8 GB totales, cabe, pero deja de
  ser gratis: es el coste principal de la decisión.
- La latencia de las consultas grandes sigue dominada por la materialización ORM→Pydantic
  (86 600 objetos ⇒ 1.2 GB de RSS **en el cliente**), no por el motor. Para ML habrá que leer
  por columnas/lotes: pendiente identificado, no resuelto.

Vectorial (1 000 chunks + 500 casos + 100 patrones, 384 dims, top-10, mediana de 50):
exacta 2.97/3.49/3.19 ms, con filtro relacional 3.13 ms, IVFFlat 2.30 ms; auto-recuperación
50/50. Vectores **sintéticos**: miden el motor, no la calidad del RAG.

## 11. WAL, almacenamiento y durabilidad

Cada escritura pasa primero por el WAL, así que el volumen escrito en disco es mayor que el
volumen de datos (medido: ≈2.5× en 24 h). Consecuencias para el edge: preferir **SSD/NVMe por
USB3 antes que microSD** (las SD se degradan con la escritura sostenida y son el punto de
fallo típico de una RPi); mantener `wal_compression` activo; controlar `max_wal_size` para no
disparar checkpoints continuos. **No se desactiva `synchronous_commit`**: si algún día se
hiciera, el riesgo (perder el último tramo de telemetría ante un corte) exige su propio ADR.

## 12. Backup y recuperación

`pg_dump` local periódico (comprimido) sobre el volumen de datos, más la sincronización de lo
crítico hacia Cloud vía Outbox. **No hay HA y no se pretende**: el edge es reemplazable; lo
que no puede perderse son diagnósticos, evidencias, memoria y patrones, y eso viaja a Cloud.
Restaurar = `createdb` + `pg_restore` + `make db-upgrade`. Frente a SQLite (copiar un fichero)
esto es un paso atrás en simplicidad, y así queda registrado.

## 13. Retención por partición

Ventaja directa del particionado: retirar un mes es `DROP/DETACH PARTITION` en lugar de un
`DELETE` masivo. Regla inviolable: **nunca se desprende una partición sin comprobar antes que
ningún caso, evidencia, `CaseMemory` o `LearnedPattern` referencia ese rango**; si lo hace, ese
intervalo pasa a retención larga. `drop_partition()` exige afirmarlo explícitamente en la
llamada. Alta frecuencia (telemetría) y bajo volumen de alto valor (memoria, diagnósticos,
patrones, evidencia) tienen políticas distintas: ver [09](09_retencion_sincronizacion.md).

## 14. Sincronización con Cloud

Edge y Cloud son bases **independientes**, ambas PostgreSQL + pgvector, y **jamás** se
sincronizan por replicación física:

```
Edge PostgreSQL → sync.outbox (misma transacción) → API/Sync → Cloud PostgreSQL
```

con idempotencia (`envelope_id`), `schema_version` y provenance. Niveles de sincronización
(F12 §34): **CRITICAL** (anomalías, diagnósticos, evidencia, memoria) siempre · **SUMMARY**
(eventos, features, agregados) por defecto · **OPTIONAL** (snapshots completos, telemetría
cruda) solo bajo configuración explícita. Detalle en [09](09_retencion_sincronizacion.md) y
[docs/synchronization](../synchronization/README.md).

## 15. Despliegue en Raspberry Pi: nativo vs Docker

Ambas opciones son viables y la imagen `pgvector/pgvector:pg16` es multi-arch. Recomendación
provisional: **Docker para desarrollo** (reproducible, ya integrado en los perfiles) y decidir
para la RPi **después de medir en hardware real** RAM en reposo y bajo carga, CPU, E/S de
disco, arranque, temperatura y estabilidad. PostgreSQL nativo evita la capa de contenedor y
suele arrancar antes; Docker simplifica versiones y limpieza. **No se declara nada validado en
ARM64 por el hecho de que la imagen exista o de que el build funcione**: la validación se hace
en A2/A3 sobre la Raspberry Pi, ejecutando estos mismos benchmarks.

## 16. Observabilidad

`diagnostic_agent.storage.metrics.collect()` devuelve: tamaño de BD, filas de snapshots,
conexiones, bytes de WAL, ratio de acierto de cache, latencia de consulta y latencia de
consulta vectorial; `list_partitions()` añade el tamaño por partición, y el
`PersistenceWorker` expone lotes, filas escritas, descartadas y fallidas. Lo justo para
dimensionar y detectar degradación — nada de plataforma DBA.

## 17. Regla de simplicidad (vinculante)

PostgreSQL + pgvector debe cubrir el máximo posible de necesidades. **No** se introducen
TimescaleDB, Citus, Redis, Kafka, Elasticsearch, Neo4j, Qdrant ni Milvus — ni una segunda base
vectorial — salvo ADR explícito respaldado por una limitación **demostrada**.
