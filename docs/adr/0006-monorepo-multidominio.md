# ADR-0006 — Monorepo multi-dominio con nube deliberadamente simple

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 2 · **Relacionada:** ADR-0001 (evoluciona)

## Contexto

El autor decidió paralelizar investigación y desarrollo y estructurar el sistema completo
(entrenamiento, edge, nube, móvil, laboratorio) desde el inicio, manteniendo la compatibilidad
con el plazo de septiembre de 2026.

## Decisión

1. **Monorepo único** con seis proyectos: `shared`, `obd-lab`, `ai-models`, `diagnostic-agent`,
   `cloud-platform`, `mobile-app`. Cada proyecto Python tiene su propio `pyproject.toml` y layout
   `src/`; el `pyproject.toml` raíz solo lleva tooling (ruff/mypy/pytest) para configuración única.
2. **Regla de dependencia:** todo proyecto depende únicamente de `shared`. Los artefactos
   (modelos, sesiones, corpus) cruzan dominios por sistema de archivos o API, jamás por import.
3. **Nube mínima:** FastAPI + PostgreSQL + docker compose. Sin Kubernetes, sin colas de mensajes,
   sin microservicios, sin S3 (artefactos en volumen). Cualquier ampliación exige nuevo ADR.
4. **Prioridad de implementación inalterada** pese a la estructura amplia: obd-lab →
   diagnostic-agent → ai-models → cloud-platform mínimo → mobile-app (OS1). La lista de recortes
   de docs/07 §7.3 sigue vigente.

## Alternativas consideradas

- *Multi-repo:* aislamiento máximo, pero para un equipo de una persona multiplica fricción
  (versionado de contratos entre repos, CI×6, sincronización). Descartado.
- *Paquete único (statu quo Fase 1):* simple, pero mezcla dependencias de entrenamiento con la
  imagen edge y no da entidad propia a obd-lab (contribución C4). Descartado tras el ajuste.
- *Nx/Bazel/uv-workspaces:* herramientas de monorepo formales; superficie innecesaria para 4
  paquetes Python. Convención + Makefile bastan. Reevaluable si el proyecto creciera.

## Consecuencias

- CI por rutas (job por proyecto, filtro de paths) — configurado en `.github/workflows/`.
- El historial de Fase 1 se preserva (`git mv`).
- Riesgo asumido R-arq1 (amplitud vs plazo) mitigado por prioridades explícitas (docs/09 §9.1).
