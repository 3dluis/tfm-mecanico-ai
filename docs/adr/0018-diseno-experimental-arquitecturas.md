# ADR-0018 — Diseño experimental por arquitecturas (A0–A6) con feature flags

> **⚠ Fuera del alcance experimental del TFM (ADR-0036, 27-ago-2026).** Tras la
> acotación de la pregunta de investigación a explicación diagnóstica trazable y
> abstención ante evidencia insuficiente, la ablación de arquitecturas A0–A6 no forma parte de la validación
> experimental de este trabajo. **El diseño y el código se conservan** y siguen siendo
> correctos; simplemente no se evalúan. Catálogo completo y justificación:
> [`docs/alineacion_v4/05_fuera_de_alcance.md`](../alineacion_v4/05_fuera_de_alcance.md).

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 5 · **Docs:** agent-runtime/12

## Decisión

1. Las 7 arquitecturas (A0 ML baseline → A6 full runtime con loop) se materializan como
   **configuraciones de una única base de código** (`RuntimeConfig`: flags de recall/
   semantic/critic/loop + memory_mode + límites), no como productos separados.
2. Métricas computables exclusivamente desde la BD (agent-runtime/11): precisión top-1/k,
   recall, false diagnosis rate, unsupported claims, evidence coverage, iteraciones, tool
   calls, tiempo, tokens, CPU/RAM (energía solo en RPi física).
3. Control por generador heurístico en todos los brazos con LLM (aísla arquitectura vs LLM).
4. **Hipótesis secundaria H5 adoptada** (sin cambiar la pregunta principal): memoria
   episódica + evolutiva + ciclos de verificación (A4–A6) mejoran la identificación y
   explicación de fallos no observados frente a agente sin memoria de ejecución única
   (A1–A2), medida sobre los escenarios held-out. H5 subsume H3 y se valida con el tutor
   junto a la redefinición operativa.

## Consecuencias

El plan experimental de docs/07 (Fase 4 del cronograma) se ejecutará con este diseño; el
piloto con HeuristicHypothesizer valida el harness antes de gastar cómputo LLM.
