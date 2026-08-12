# ADR-0001 — Estructura del repositorio y stack de calidad

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 1

## Contexto

El TFM combina investigación (experimentos reproducibles) e ingeniería (prototipo modular). El plazo (septiembre 2026) exige que la estructura no se rehaga a mitad de proyecto y que la calidad esté automatizada desde el primer commit (riesgos R5, R7).

## Decisión

1. **Monorepo con layout `src/`** (`src/mecanico_ia/`): evita importaciones accidentales del árbol de trabajo y es la práctica recomendada del ecosistema de empaquetado moderno. Un subpaquete por componente de la arquitectura (C1–C7, véase `docs/05_arquitectura.md`), lo que hace trazable requisito→código.
2. **`pyproject.toml` único con dependencias opcionales por grupo** (`sim`, `anomaly`, `agent`, `dev`): permite instalar en CI solo lo ligero, en la imagen edge solo lo necesario, y aísla el stack pesado del agente (LangGraph/Chroma/sentence-transformers) que no debe penalizar los tests rápidos.
3. **Stack de calidad:** ruff (lint+format), mypy estricto, pytest(+cov), pre-commit y GitHub Actions con un único job. Marcador `emulator` para separar pruebas lentas que requieren el emulador.
4. **Experimentos fuera del paquete** (`experiments/`), un script por hipótesis, resultados CSV versionados. **ADRs en `docs/adr/`** numerados.

## Alternativas consideradas

- *Layout plano (paquete en la raíz):* más simple, pero propenso a imports accidentales y menos profesional; descartado.
- *Poetry/PDM:* gestores completos, pero añaden herramienta y lockfile propietario; pip + pyproject estándar cubre la necesidad con menos superficie (criterio de simplicidad acordado en Fase 0).
- *Repos separados (código/memoria):* sobrecoste de sincronización injustificado para un equipo de una persona.

## Consecuencias

- CI verde desde el commit inicial; toda contribución pasa lint+tipos+tests.
- Restricción documentada: `ELM327-emulator` necesita `setuptools<81` y `--no-build-isolation` (su `setup.py` importa `pkg_resources`, retirado en setuptools ≥81). Anotado en README, CI y Dockerfile; riesgo de deuda si el paquete no se actualiza — vigilar en Fase 2.
