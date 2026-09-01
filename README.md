# mecanico-ai-exp

Laboratorio experimental reproducible del Trabajo Fin de Máster en Inteligencia
Artificial (UAX). Aquí se construye, se ejecuta y se documenta el experimento
científico principal.

## Pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de
> datos OBD-II reales, rastreando cada explicación hasta su evidencia de origen,
> y reconocer cuándo la evidencia disponible no es suficiente para sostener una
> explicación en lugar de generar una hipótesis sin fundamento?

## Cadena experimental

```
datos OBD-II → series temporales → preprocesamiento → modelo especializado
  → diagnóstico + confianza → XAI → evidencia observacional
  → RAG → evidencia documental → evaluación de suficiencia
  → EXPLAIN / ABSTAIN → LLM → explicación trazable → evaluación científica
```

El LLM no diagnostica a partir de OBD-II crudo: redacta y organiza la evidencia
que otros componentes han producido. La decisión de explicar o abstenerse la
toma un componente determinista, fuera del LLM.

## Quick Start — entorno oficial (macOS Apple Silicon)

Requisitos: macOS sobre Apple Silicon, [uv](https://docs.astral.sh/uv/) y una
instalación local de PostgreSQL 14+ con la extensión `pgvector` disponible.

```bash
# 1. Entorno de Python (uv resuelve e instala Python 3.11)
uv sync --all-extras

# 2. Configuración
cp .env.example .env      # y rellenar DATABASE_USER y el proveedor LLM

# 3. Auditoría del entorno: intérprete, MPS, PostgreSQL, pgvector
uv run mecanico-exp doctor

# 4. Base de datos del laboratorio (crea solo lo suyo; no toca otras bases)
bash scripts/init_db.sh

# 5. Gates de calidad
uv run ruff check .
uv run mypy src
uv run pytest

# 6. Capa de análisis
uv run jupyter lab
```

Detalle paso a paso en [`docs/setup/macos-local.md`](docs/setup/macos-local.md)
y [`docs/setup/postgres-local.md`](docs/setup/postgres-local.md).

## Portable Setup — cualquier máquina

Para reproducir el experimento sin una instalación local de PostgreSQL:

```bash
docker compose up -d postgres        # PostgreSQL 16 + pgvector en el puerto 5433
cp .env.example .env                 # DATABASE_PORT=5433
uv sync --all-extras
uv run mecanico-exp doctor
```

El LLM puede ser un proveedor remoto por API o, opcionalmente, un modelo local
vía Ollama. El pipeline científico es idéntico en ambos modos; solo cambia de
dónde salen la base de datos y el modelo de lenguaje. Ver
[`docs/setup/docker-portable.md`](docs/setup/docker-portable.md),
[`docs/setup/llm-providers.md`](docs/setup/llm-providers.md) y
[`docs/setup/ollama-optional.md`](docs/setup/ollama-optional.md).

Los resultados obtenidos con Ollama no se mezclan con los resultados oficiales.

## Organización

| Ruta | Contenido |
|---|---|
| `src/mecanico_ai_exp/` | Todo el código científico. Los notebooks importan de aquí |
| `notebooks/` | Análisis, figuras y demostración. Sin lógica exclusiva |
| `data/` | Datasets sintéticos y reales, con metadata de procedencia |
| `corpus/` | Corpus documental para RAG y sus manifiestos |
| `migrations/` | Esquema de PostgreSQL, versionado y reproducible |
| `experiments/`, `results/`, `figures/`, `tables/` | Artefactos de cada ejecución |
| `docs/` | Instalación, metodología y registro de experimentos |

## Estado

Fase **E1 — entorno** cerrada. El plan por fases, con la clasificación de cada
componente (nuevo, reutilizado, adaptado, opcional o futuro), está en
[`docs/plan_experimental_macbook.md`](docs/plan_experimental_macbook.md).

## Relación con el proyecto de ingeniería

Existe un proyecto hermano, `mecanico-ia`, que construye el sistema de
diagnóstico como producto. Este laboratorio es independiente: no lo importa, no
depende de rutas hacia él y no lo modifica. Cuando se reutiliza un componente se
copia y se documenta su procedencia en `docs/`.
