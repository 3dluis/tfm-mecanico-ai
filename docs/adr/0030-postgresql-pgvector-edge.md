# ADR-0030 — Adoptar PostgreSQL + pgvector como plataforma de persistencia del Edge

- **Fase:** 12
- **Estado:** **Aceptada** (decisión del autor, 2026-08-13)
- **Supersede a:** [ADR-0029](0029-evaluacion-postgresql-pgvector-edge.md) (evaluación F11, que
  recomendaba HYBRID/KEEP SQLITE) y a la parte "SQLite en el edge" de
  [ADR-0012](0012-arquitectura-de-datos.md). **Ninguno se borra**: el histórico se conserva
  íntegro, incluidas sus mediciones.
- **Documentación:** [data-architecture/13](../data-architecture/13_postgresql_pgvector_edge.md) ·
  [03 modelo relacional](../data-architecture/03_modelo_relacional.md) ·
  informe [fase12](../fase12/informe_migracion_postgresql.md)

## Contexto

La evaluación de F11 (ADR-0029) midió SQLite frente a PostgreSQL+pgvector **para el alcance
que el edge tenía entonces**: recoger OBD y ejecutar inferencia. Con ese alcance, SQLite salía
mejor en RAM, disco y escritura, y la recomendación técnica fue HYBRID.

El alcance del edge ha cambiado. Ya no es

```
OBD collector + simple inference
```

sino

```
Telemetry Platform + ML Runtime + Multi-Agent Runtime + Local RAG
+ Episodic Memory + Evolutionary Memory
```

Con ese alcance aparecen necesidades que antes no existían: memoria episódica y evolutiva
consultables por similitud, RAG local sobre corpus técnico, embeddings de casos y patrones,
trazas de agentes, outbox transaccional y consultas analíticas sobre telemetría. La
alternativa SQLite exige acompañarse de un almacén vectorial aparte y de estructuras de
apoyo en ficheros: **tres sistemas de persistencia mal acoplados** en lugar de uno.

## Decisión

**PostgreSQL + pgvector es la plataforma oficial de persistencia del Edge de Mecánico IA.**
SQLite deja de ser la base principal del runtime.

1. Un único motor para telemetría, snapshots, eventos, features, anomalías, casos
   diagnósticos, ejecuciones de agentes, memoria episódica, memoria evolutiva, RAG,
   embeddings, metadatos de modelos y outbox de sincronización.
2. **Se aprovechan las capacidades que aportan valor**, no como simple reemplazo de SQLite:
   transacciones reales (negocio + outbox atómicos), claves ajenas que se aplican de verdad,
   JSONB, particionado temporal, búsqueda vectorial con filtrado relacional en la misma
   consulta, y consultas analíticas/CTE para provenance. Se evita todo lo que no aporte al
   TFM (replicación, HA, extensiones adicionales).
3. **Schemas lógicos** (`telemetry`, `events`, `diagnostics`, `models`, `memory`, `knowledge`,
   `agent`, `sync`; `core` reservado): un motor compartido con separación semántica explícita.
4. **Alembic** pasa a ser el mecanismo oficial de migración (se revisa la decisión previa de
   posponerlo): ya no se recrea la base.
5. **Migración controlada, no borrado**: el código SQLite queda clasificado
   `LEGACY / TEST COMPATIBILITY` y solo se retirará cuando se cumplan las condiciones del
   informe de F12.
6. **La sincronización no cambia**: Outbox → API → Cloud, lógica e idempotente. Edge y Cloud
   son bases **independientes**; jamás replicación física, aunque ambos sean PostgreSQL.

## Decisiones de diseño que esta ADR fija

- **Clave primaria de la tabla particionada:** PostgreSQL exige que toda restricción única de
  una tabla particionada incluya la clave de partición. `vehicle_telemetry_snapshots` usa PK
  **compuesta `(snapshot_id, timestamp_utc)`**. `snapshot_id` (UUID) sigue siendo el
  identificador global de trazabilidad y la columna principal del índice; lo que se pierde es
  la unicidad *física* de `snapshot_id` aislado, que pasa a ser garantía lógica (UUIDv4).
- **FK del enlace N:M:** `snapshot_event_links.snapshot_id` deja de tener FK física (habría
  que referenciar la unique compuesta). La integridad es lógica y está cubierta por los tests
  de provenance.
- **Particiones:** rango mensual + partición `DEFAULT` de seguridad; se crean por adelantado
  (mes en curso + 3). Nada automático que borre.
- **Índices:** los tres B-tree derivados de los query patterns + **BRIN** temporal (la tabla
  se escribe en orden de tiempo). Nada más sin patrón que lo justifique.
- **Vectores:** solo en `knowledge.knowledge_chunks`, `memory.case_memory` y
  `memory.learned_patterns`. **La telemetría no se vectoriza.** Búsqueda EXACTA al principio;
  HNSW/IVFFlat solo cuando el volumen lo exija.
- **Escritura:** por lotes con worker asíncrono y cola acotada; nunca un COMMIT por PID.
- **Acceso:** el runtime solo habla con repositorios tipados. El LLM **nunca** genera SQL.

## Alternativas consideradas

- **Mantener SQLite + almacén vectorial aparte (recomendación de ADR-0029):** más liviana en
  RAM y disco, pero fragmenta la persistencia justo cuando el edge incorpora RAG y memoria, y
  deja fuera transaccionalidad real entre negocio y outbox.
- **SQLite + extensión sqlite-vec:** evita el segundo store pero mantiene un solo escritor,
  sin particionado ni filtrado vectorial+relacional maduro, y con menos garantías.
- **Base vectorial dedicada (Qdrant/Milvus/Chroma) junto a SQLite:** añade un servicio más al
  edge, precisamente lo que esta decisión evita.
- **TimescaleDB/Citus:** rechazadas por ahora — complejidad sin necesidad demostrada.

## Consecuencias y costes (medidos, no ocultos)

Medido en sandbox x86 4 CPU/8 GB (proxy de RPi 5; ARM64 real **pendiente**), 1 Hz:

| Coste | Medida | Comentario |
|---|---|---|
| RAM | **~140–236 MB** de procesos postgres (0 MB con SQLite) | compite con el presupuesto del LLM local |
| Disco | 106.9 MB / 24 h (SQLite: 86.7 MB) | **+23 %** |
| WAL | **161.7 MB / 24 h** | amplificación de escritura ~2.5×: relevante para SD; se recomienda SSD |
| Escritura | 5 068–5 570 filas/s con `executemany`; **9 703 filas/s con COPY** | sigue holgado para 1 Hz (≈1 fila/s) |
| Administración | vacuum, roles, backup lógico, arranque del servicio | antes: copiar un fichero |
| Docker | un servicio más con healthcheck y volumen | mayor complejidad de despliegue |

Beneficios que ya se observan: las claves ajenas **se aplican de verdad** (el primer test E2E
sobre PostgreSQL detectó una inserción que SQLite aceptaba en silencio), la búsqueda vectorial
con filtro relacional funciona en una sola consulta, y negocio+outbox son atómicos.

## Riesgos

Mayor consumo de RAM y almacenamiento; write amplification del WAL sobre tarjetas SD;
recuperación tras corte de corriente más compleja que copiar un fichero; mantenimiento
(vacuum/bloat) que antes no existía; impacto térmico indirecto en RPi por CPU/E-S sostenidas;
y complejidad añadida en Docker/despliegue. Mitigaciones y umbrales en
[data-architecture/13](../data-architecture/13_postgresql_pgvector_edge.md).

## Regla derivada (vinculante)

**No se introduce una segunda base vectorial ni ningún motor adicional** (TimescaleDB, Citus,
Redis, Kafka, Elasticsearch, Neo4j, Qdrant, Milvus) **sin un ADR explícito respaldado por una
limitación demostrada de PostgreSQL + pgvector.**
