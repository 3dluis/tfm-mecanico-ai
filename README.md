# Mecánico IA

Sistema inteligente híbrido edge-cloud para diagnóstico y mantenimiento predictivo vehicular
mediante OBD-II. Trabajo Fin de Máster (UAX) — Luis Daniel Díaz, 2026.

> **Pregunta de investigación:** ¿puede un agente inteligente híbrido (LLM + aprendizaje no
> supervisado + memoria evolutiva + RAG) descubrir y explicar patrones de fallo vehicular
> previamente no documentados a partir de datos OBD-II?

## Estado

Fase 1 — fundamentos y entorno. Véase [`docs/`](docs/) para la planificación completa y
[`docs/adr/`](docs/adr/) para las decisiones de arquitectura.

## Estructura

```
docs/            Planificación, ADRs, estado del arte e informes de fase
docker/          Entorno reproducible (perfiles dev x86-limitado y arm64)
src/mecanico_ia/ Código fuente (paquete Python)
  vehicle_sim/   C1  Generador de escenarios + emulador ELM327
  acquisition/   C2  Cliente OBD-II, capa de transporte plugable
  storage/       C3  Persistencia SQLite (telemetría, casos, trazas)
  anomaly/       C4  Detección de anomalías no supervisada
  rag/           C5a RAG local (ChromaDB + sentence-transformers)
  memory/        C5b Memoria evolutiva de casos
  agent/         C6  Agente de diagnóstico (LangGraph)
  api/           C7  API REST (FastAPI) + UI mínima
experiments/     Scripts reproducibles por hipótesis (H1–H4)
tools/           Utilidades de desarrollo (evaluaciones, scripts puntuales)
tests/           Pruebas (pytest)
```

## Entorno de desarrollo

Requisitos: Python ≥ 3.11, Docker (opcional pero recomendado), sistema POSIX para el
emulador (usa pty).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip "setuptools<81" wheel
pip install -e ".[sim,anomaly,dev]"
# nota: ELM327-emulator requiere setuptools<81 (usa pkg_resources en su setup.py)
pip install --no-build-isolation ELM327-emulator
pre-commit install
```

Con Docker (perfil de desarrollo, recursos limitados a un equivalente de Raspberry Pi 5):

```bash
docker compose -f docker/compose.yml --profile dev up --build
```

Validación de compatibilidad ARM64 (build cruzado vía QEMU/binfmt):

```bash
docker buildx build --platform linux/arm64 -f docker/edge.Dockerfile .
```

## Reproducibilidad

Toda aleatoriedad usa semillas fijas; los datos emulados se regeneran por script; las
versiones están fijadas en `pyproject.toml`. El protocolo experimental se publica en
`docs/` **antes** de ejecutar los experimentos.

## Licencia y aviso

Prototipo de investigación académica. No sustituye el diagnóstico de un profesional.
