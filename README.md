# Mecánico IA

Sistema inteligente híbrido edge-cloud para diagnóstico y mantenimiento predictivo vehicular
mediante OBD-II. Trabajo Fin de Máster (Máster en IA, UAX) — Luis Daniel Díaz, 2026.

> **Pregunta de investigación (v4, 27-ago-2026):** ¿puede un agente con RAG explicar el
> diagnóstico de un vehículo a partir de datos OBD-II reales, rastreando cada explicación
> hasta su evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente
> para sostener una explicación en lugar de generar una hipótesis sin fundamento?

Núcleo científico canónico: [`docs/alineacion_v4/`](docs/alineacion_v4/01_nucleo_cientifico.md) ·
historia de la PI: [`04_historial_pi.md`](docs/alineacion_v4/04_historial_pi.md) ·
fuera del alcance experimental: [`05_fuera_de_alcance.md`](docs/alineacion_v4/05_fuera_de_alcance.md).

## Monorepo

| Proyecto | Rol | Estado |
|---|---|---|
| [`shared/`](shared/) | Contratos compartidos + modelo de datos v2 (Pydantic → JSON Schema → diccionario autogenerado) | ✅ v2 |
| [`obd-lab/`](obd-lab/) | Laboratorio OBD-II: generador 3 categorías, emulación en vivo, suites | ✅ funcional |
| [`ai-models/`](ai-models/) | Baselines evaluados (LOF elegido), export ONNX+manifest, tracking | ✅ funcional |
| [`diagnostic-agent/`](diagnostic-agent/) | **Edge Agent Runtime** (multiagente, ADR-0015) + pipeline validado + datos v2 | ✅ runtime v1 (slice) |
| [`cloud-platform/`](cloud-platform/) | Nube complementaria: auth, registro, sync, model registry (simple) | scaffolding |
| [`mobile-app/`](mobile-app/) | App Flutter offline-first (edge directo + cloud complementaria) | pospuesta (OS1) |

Arquitectura completa: [`docs/09_arquitectura_monorepo.md`](docs/09_arquitectura_monorepo.md) ·
**Arquitectura de datos: [`docs/data-architecture/`](docs/data-architecture/README.md)** ·
**Agent Runtime: [`docs/agent-runtime/`](docs/agent-runtime/README.md)** ·
**Event Intelligence: [`docs/event-intelligence/`](docs/event-intelligence/README.md)** ·
**Modelos de IA: [`docs/models/`](docs/models/README.md)** ·
Diagrama: [`docs/diagrams/arquitectura.mermaid`](docs/diagrams/arquitectura.mermaid) ·
Decisiones: [`docs/adr/`](docs/adr/README.md)

**Persistencia oficial (ADR-0030):** PostgreSQL + pgvector, tanto en el Edge como en el
Cloud, como instancias independientes sincronizadas por Outbox lógico — telemetría, memoria,
RAG y embeddings en un único motor ([`docs/data-architecture/13`](docs/data-architecture/13_postgresql_pgvector_edge.md)).
SQLite queda como camino legacy/tests. Reglas del repositorio: [`REGLAS.md`](REGLAS.md).

**Separación estricta ML/LLM:** la detección de anomalías es siempre matemática
(IForest/autoencoder vía ONNX); el LLM razona, explica y recomienda sobre anomalías ya
detectadas — nunca las decide (ADR-0009).

**Flujo científico principal (PI v4):** vehículo → OBD-II → procesamiento y contexto →
diagnóstico → recuperación de evidencia (RAG) → verificación del soporte → *¿evidencia
suficiente?* → explicación diagnóstica trazable **o** abstención declarada. Los detectores
de anomalías y el runtime multiagente son subsistemas auxiliares que producen el contexto;
no son la contribución científica (ADR-0036).

## Arranque rápido

Requisitos: Docker (Desktop en macOS). Para desarrollo local sin Docker: Python ≥ 3.11 y POSIX.

```bash
# entorno de desarrollo del núcleo (emulador OBD + agente + Ollama)
make dev            # equivale a: docker compose --profile dev up --build

# otros perfiles
make research       # JupyterLab para ai-models
make cloud          # API cloud + PostgreSQL
make edge           # agente con límites de recursos de Raspberry Pi 5
make full           # todo
```

Comprobación: `curl localhost:8000/health` y `curl localhost:8000/ready` (agente),
`curl localhost:8080/health` (cloud).

Desarrollo local sin Docker (requiere [uv](https://docs.astral.sh/uv/); ADR-0032):

```bash
make install            # uv sync --locked: crea .venv con los 5 paquetes + tooling
make check              # lint + tipos + tests + esquemas al día (todo vía uv run)
make install-emulator   # opcional: emulador ELM327 (fuera del lock, ADR-0003)
```

## Camino a la Raspberry Pi

macOS (desarrollo) → `make arm64-build` (validación de compatibilidad ARM64 vía QEMU) →
despliegue en RPi 5 con los mismos Dockerfiles (ADR-0002). Los modelos ML viajan como
paquetes ONNX + `manifest.json` a través del model registry (ADR-0009).

## Reproducibilidad

Semillas fijas en todos los escenarios y entrenamientos; sesiones regenerables por script;
protocolo experimental publicado en `docs/` antes de ejecutar experimentos; contratos
versionados (`schema_version`).

## Aviso

Prototipo de investigación académica. No sustituye el diagnóstico de un profesional.
