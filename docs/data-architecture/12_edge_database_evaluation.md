# 12 — Evaluación de persistencia Edge: SQLite vs PostgreSQL + pgvector (ADR-0029)

> **DOCUMENTO HISTÓRICO (F11).** Su recomendación (HYBRID / KEEP SQLITE) fue **superada** por
> la decisión de F12: **PostgreSQL + pgvector es la plataforma oficial del Edge**
> ([13](13_postgresql_pgvector_edge.md), ADR-0030). No cambiaron las mediciones sino el
> ALCANCE del edge (RAG + memoria episódica y evolutiva + runtime multiagente). Se conserva
> íntegro porque sus números son la base de los costes que la nueva decisión asume
> conscientemente.

**Estado: evaluación EJECUTADA con mediciones reales (F11).** Fuente:
`ai-models/experiments/edge_db_benchmark.json` (misma carga por el MISMO código —
EdgeStoreV2 + repositorios — solo cambia el motor; sandbox x86 4CPU/8GB, proxy
documentado del perfil RPi; el perfil `docker compose --profile edge-postgres up`
permite repetirlo en ARM64/Mac).

## 1. Opción A — SQLite (vigente)

**Ventajas:** simple · embebido (cero procesos extra) · sin administración · un fichero
(backup = copiar; recuperación = trivial) · consumo mínimo · comportamiento offline
excelente · arranque instantáneo. **Limitaciones:** sin pgvector nativo (los vectores
viven aparte: fichero/np, o extensión sqlite-vec) · escritores concurrentes limitados
(un solo escritor efectivo) · sin particionado nativo · almacén vectorial adicional si
el corpus crece.

## 2. Opción B — PostgreSQL + pgvector local

Un único motor para telemetría relacional + memoria del agente + RAG + embeddings +
LearnedPatterns + AgentRuns (arquitectura candidata del plan §30). Viabilidad ARM64:
confirmada (imagen oficial `pgvector/pgvector:pg16` multi-arch; paquete Debian
`postgresql-16-pgvector`). **Costes:** servicio residente, administración (vacuum,
roles, tuning), backup lógico, arranque del servidor, y la RAM/CPU medidas abajo.

## 3. Resultados medidos (carga idéntica: 8 h de snapshots = 28 800 filas + N:M)

| Métrica | SQLite | PostgreSQL 16 + pgvector | Δ |
|---|---|---|---|
| Startup (abrir+migrar / conectar+migrar) | **139 ms** | 234 ms + servicio residente | PG requiere el servidor ya arrancado |
| RAM idle adicional | **0 MB** (embebido) | **149.5 MB** (procesos postgres) | ~1.9 % de los 8 GB de una RPi 5 |
| Batch insert | **7 697 filas/s** | 5 091 filas/s | PG −34 % |
| Insert unitario | 655 filas/s | **707 filas/s** | PG +8 % |
| Query sesión (2 000 filas) | **134 ms** | 296 ms | PG +120 % |
| Query rango 2 h (7 401 filas) | 984 ms | **836 ms** | PG −15 % (dominada por ORM→Pydantic) |
| Query por tipo de evento (4 607) | 401 ms | **266 ms** | PG −34 % |
| Join diagnóstico N:M (1 800) | **35.4 ms** | 45.2 ms | PG +28 % |
| Disco (mismos datos) | **29.2 MB** | 39.7 MB | +36 % |
| Concurrencia de escritores | 1 efectivo | N reales | ventaja PG (irrelevante hoy: el edge tiene UN escritor) |

## 4. Benchmark vectorial (1 600 vectores × 384 dims: 1 000 chunks + 500 casos + 100 patrones; top-10, mediana de 50 consultas)

| Método | Latencia top-K | RAM |
|---|---|---|
| **numpy en proceso (mundo SQLite)** | **0.039 ms** | 2.5 MB |
| pgvector exacto | 1.28 ms | (en el servidor) |
| pgvector IVFFlat (lists=40) | 0.60 ms | (en el servidor) |

Vectores SINTÉTICOS: miden el MOTOR, no la calidad de recuperación. Lectura: al tamaño
del TFM (corpus ≈ 10²–10³ chunks; casos ≈ 10²–10³) la búsqueda exacta en proceso es
1–2 órdenes de magnitud más rápida que ir al servidor, con 2.5 MB de RAM. pgvector
empieza a compensar con ≥10⁵–10⁶ vectores, escrituras concurrentes o necesidad de
filtrado SQL+vectorial combinado — ninguno presente en el edge del TFM.

## 5. Análisis por criterios (plan §32)

Simplicidad/mantenimiento/arranque/recuperación/backup: SQLite. RAM/CPU: SQLite
(149 MB de PG compiten con el presupuesto del LLM en RPi). Almacenamiento: SQLite
(−27 %). Consultas: **reparto** — SQLite gana en sesión (134 vs 296 ms) y en el join
diagnóstico N:M (35 vs 45 ms); PG gana en rango largo (−15 %) y por tipo de evento (−34 %).
Ninguna diferencia es decisiva: en todos los casos la latencia está dominada por la
materialización ORM→Pydantic, no por el motor. Concurrencia: PG (sin caso
de uso en edge mono-escritor). Embeddings: numpy/proceso gana al tamaño actual; PG gana
a escala cloud. Raspberry: ambos viables; PG con coste fijo permanente.

## 6. Recomendación explícita (pendiente de la aprobación del autor)

**HYBRID — KEEP SQLITE en Edge + PostgreSQL+pgvector en Cloud.**

- **Edge: SQLite se mantiene.** Con las mediciones reales: mejor batch insert (+51 %),
  0 MB de RAM residente frente a 149 MB (RAM que en RPi compite con el LLM), −27 % de
  disco, backup/recuperación triviales y sin administración; el único punto fuerte de PG
  local (concurrencia de escritores) no tiene caso de uso en un edge mono-escritor; y la
  búsqueda vectorial del TFM se sirve mejor en proceso (0.04 ms, 2.5 MB).
- **Cloud: PostgreSQL + pgvector confirmado** como candidato natural (consolidación
  multi-vehículo, particionado mensual de snapshots — ADR-0028 —, corpus RAG maestro,
  concurrencia real). El MISMO modelo lógico mapea a ambos sin cambiar semántica —
  demostrado: `EdgeStoreV2(url=postgresql...)` crea y opera el esquema íntegro con el
  mismo código, tras los repositorios abstractos (F11 §36).
- **Sincronización sin cambios:** protocolo lógico Outbox→API→Cloud con idempotencia +
  schema_version + provenance ([09](09_retencion_sincronizacion.md)); jamás replicación
  física, ni siquiera si ambos extremos fueran PostgreSQL.
- **Umbrales de re-evaluación registrados (ADR-0029):** corpus vectorial ≥10⁵ vectores,
  aparición de multi-proceso escritor en edge, o requisitos de consulta híbrida
  SQL+vector — cualquiera reabre la decisión con este mismo benchmark (reproducible vía
  `edge-postgres` en ARM64).

Resultado del ADR-0029: **REJECT para sustituir SQLite en Edge ahora · ACCEPT como motor
Cloud · re-evaluable por umbrales.** Ninguna migración general se ejecuta sin tu
aprobación.
