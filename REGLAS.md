# REGLAS.md — reglas del repositorio Mecánico IA

Contexto para cualquier sesión de trabajo sobre este monorepo. **Estas reglas son
vinculantes**: si algo del código o de la documentación las contradice, gana este fichero y se
corrige lo demás.

## Proyecto

TFM del Máster en Inteligencia Artificial de la **UAX** (Universidad Alfonso X el Sabio) —
Luis Daniel Díaz, entrega **septiembre de 2026**. Sistema híbrido edge-cloud de diagnóstico
vehicular por OBD-II.

## Reglas arquitectónicas

1. **PostgreSQL + pgvector es la plataforma oficial de persistencia de Mecánico IA Edge**
   (ADR-0030). Telemetría, snapshots, eventos, features, anomalías, casos, ejecuciones de
   agentes, memoria episódica, memoria evolutiva, RAG, embeddings, metadatos de modelos y
   outbox viven en la MISMA base, separados por schemas lógicos.
2. **No introducir una segunda base vectorial** (Chroma, FAISS, Qdrant, Milvus…) **ni otro
   motor** (TimescaleDB, Citus, Redis, Kafka, Elasticsearch, Neo4j) **salvo ADR explícito
   respaldado por una limitación demostrada** de PostgreSQL + pgvector.
3. **SQLite es LEGACY / TEST COMPATIBILITY.** No se amplía; se retirará cuando se cumplan las
   condiciones del informe de F12. No borrar código SQLite que aún sostenga tests.
4. **Alembic es el mecanismo oficial de migración** (`make db-upgrade`). No se recrea la base.
5. **Los contratos de `shared/mecanico_contracts` son la única fuente de verdad.** El esquema
   físico es su espejo; los JSON Schema y el diccionario se autogeneran (`make data-docs`).
   Cambios de contrato: **aditivos**.
6. **El runtime trabaja contra repositorios tipados**, nunca contra el ORM o el driver.
   `Agent → Tool (entradas/salidas tipadas) → Repository → PostgreSQL`.
   **El LLM NUNCA genera SQL** ni accede a la base directamente.
7. **Separación ML/LLM (ADR-0009):** la detección de anomalías es siempre matemática; el LLM
   razona sobre anomalías ya detectadas. Jamás al revés.
8. **La telemetría no se vectoriza.** pgvector solo para conocimiento, casos y patrones.
9. **Sincronización siempre lógica**: Outbox → API → Cloud, idempotente y versionada. Nunca
   replicación física, aunque ambos extremos sean PostgreSQL.
10. **NULL ≠ 0** (ADR-0027) y **el snapshot no contiene features** (ADR-0025).
11. **Nada referenciado por provenance se borra** sin estrategia explícita, y ninguna partición
    se desprende sin verificar antes que no contiene evidencia referenciada.

## Reglas de método (no negociables)

- **Trabajo por fases aprobadas.** No avanzar a la siguiente fase sin aprobación explícita del
  autor. Cada fase termina con informe en `docs/faseN/`.
- **Nunca inventar referencias ni resultados.** Si un experimento no se ha ejecutado, se dice.
  Si el hardware no se ha probado, no se declara validado (ARM64/Raspberry Pi incluido).
- **Los resultados negativos se conservan y se publican** en la documentación.
- **Compatible con Raspberry Pi 5**, edge-first: cada decisión se juzga por su coste en RAM,
  CPU, disco y escritura sostenida.
- **Toda decisión relevante lleva ADR.** Un ADR antiguo no se borra: se marca como superado.
- **Regla de sincronización de ficheros:** nunca sobrescribir archivos modificados localmente
  que no estén en el historial de Git o respaldados explícitamente; toda sincronización va
  precedida de copia de seguridad y comprobación de `git status`.

## Estado bloqueado sin aprobación explícita

LoRA/QLoRA y cualquier fine-tuning · online learning · base de datos de grafos · varios LLM
concurrentes · MLOps en la nube · escritura sobre la ECU · consolidación automática de
patrones · ejecución de experimentos confirmatorios antes de congelar el pre-registro ·
ampliación masiva del Agent Runtime antes de validar la capa de persistencia.

## Comandos

El entorno lo gestiona **uv** (ADR-0032): `uv.lock` committeado es la única fuente de
versiones; los targets del Makefile corren vía `uv run`. No instalar con pip suelto.

```bash
make install        # entorno de desarrollo (uv sync --all-packages --locked)
make check          # ruff + mypy + pytest + regeneración de docs de datos
make db-up          # PostgreSQL + pgvector del edge
make db-upgrade     # migraciones Alembic (oficial)
make dev            # PostgreSQL + emulador OBD + agente + ollama
make test-pg        # tests de integración reales contra PostgreSQL
make pg-bench       # dimensionamiento (1h/8h/24h de snapshots)
make pg-vector-bench# baseline del RAG local
make registry       # reconstruye el Model Registry de forma determinista
```

Gate de calidad obligatorio antes de cerrar cualquier fase: `ruff format` + `ruff check` +
`mypy --strict` + `pytest` + regeneración de esquemas y diccionario.
