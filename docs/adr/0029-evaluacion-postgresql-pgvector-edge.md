# ADR-0029 — Evaluación de PostgreSQL + pgvector como persistencia Edge

- **Fase:** 11
- **Estado:** **Evaluación ejecutada · resultado REJECT (para sustituir SQLite en Edge ahora) ·
  ACCEPT (como motor Cloud) · re-evaluable por umbrales** — pendiente de aprobación del autor
- **Contexto documental:** [data-architecture/12](../data-architecture/12_edge_database_evaluation.md)
- **Evidencia:** `ai-models/experiments/edge_db_benchmark.json` (mediciones reales,
  reproducibles con `docker compose --profile edge-postgres up` + `python tools/edge_db_benchmark.py`)

> Este ADR es **de evaluación, no de sustitución**. No declara ganador *a priori*: el
> resultado se escribió después de ejecutar el benchmark.

## Contexto

El edge usa SQLite. La hipótesis a evaluar: un único motor (PostgreSQL + pgvector local en
RPi5/ARM64) para telemetría relacional + memoria del agente + RAG + embeddings +
LearnedPatterns + AgentRuns simplificaría la arquitectura y evitaría un almacén vectorial
aparte.

## Opciones

- **A — SQLite (vigente):** embebido, sin administración, un fichero, arranque instantáneo,
  offline excelente. Limitaciones: sin pgvector nativo, un escritor efectivo, sin particionado
  nativo, almacén vectorial aparte.
- **B — PostgreSQL 16 + pgvector local:** un solo motor para todo, concurrencia real,
  particionado declarativo, búsqueda vectorial en SQL. Costes: servicio residente, RAM/CPU
  permanentes, administración (vacuum, roles, tuning), backup lógico.

Viabilidad ARM64 de B: **confirmada** (imagen multi-arch `pgvector/pgvector:pg16`, paquete
Debian `postgresql-16-pgvector`) — la viabilidad no era el problema.

## Evidencia decisiva (misma carga, mismo código, solo cambia el motor)

- Batch insert: SQLite 7 697 vs PG 5 091 filas/s (**+51 % SQLite**).
- RAM residente adicional: **0 MB vs 149.5 MB** — en RPi 5 esa RAM compite directamente con el
  presupuesto del LLM local.
- Disco: 29.2 vs 39.7 MB (**−27 % SQLite**).
- Consultas: reparto sin diferencia decisiva (SQLite mejor en sesión y join N:M; PG mejor en
  rango largo y por tipo de evento); todas dominadas por la capa ORM, no por el motor.
- Vectorial al tamaño del TFM (1 600 × 384): numpy en proceso **0.039 ms / 2.5 MB** vs pgvector
  exacto 1.28 ms / IVFFlat 0.60 ms.
- Concurrencia multi-escritor: única ventaja clara de PG, **sin caso de uso** en un edge
  mono-escritor.

## Decisión

**HYBRID — KEEP SQLITE en Edge · PostgreSQL + pgvector en Cloud.**

1. **REJECT** sustituir SQLite en el edge *ahora*. No se ejecuta ninguna migración general.
2. **ACCEPT** PostgreSQL + pgvector como motor **Cloud** (consolidación multi-vehículo,
   particionado mensual ADR-0028, corpus RAG maestro, concurrencia real).
3. El desacoplamiento se mantiene por **repositorios/interfaces** (`TelemetryRepository`,
   `MemoryRepository`, `KnowledgeRepository`, `AgentRunRepository`): el Agent Runtime trabaja
   contra interfaces, nunca contra un motor. `EdgeStoreV2` es agnóstico y crea el esquema
   íntegro en ambos motores (demostrado).
4. **La sincronización no cambia**: protocolo lógico Outbox → API/Sync → Cloud con
   idempotencia + `schema_version` + provenance. Nunca replicación física, ni siquiera si
   ambos extremos fueran PostgreSQL.
5. El perfil `docker compose --profile edge-postgres` se **conserva** (sin eliminar el camino
   SQLite) para poder repetir la comparación, incluida la repetición en ARM64 real.

## Umbrales que reabren la decisión

- Corpus vectorial ≥ 10⁵ vectores en edge.
- Aparición de escritores concurrentes reales (multi-proceso) en edge.
- Necesidad de consulta híbrida SQL + vector en la misma query.
- Repetición del benchmark en RPi 5 real con resultado cualitativamente distinto al proxy x86.

Cualquiera de ellos ⇒ se repite este mismo benchmark y se emite un ADR sucesor.

## Consecuencias

- El edge conserva backup trivial (copiar un fichero) y recuperación ante fallo simple.
- Se asume mantener dos caminos vectoriales (numpy/fichero en edge, pgvector en cloud); el
  coste es bajo porque la frontera es el `KnowledgeRepository`.
- Limitación declarada: las mediciones son de sandbox x86 4CPU/8GB como **proxy** del perfil
  RPi; la validación en hardware ARM64 real sigue pendiente y no se declara hecha.
