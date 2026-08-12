# ADR-0013 — Memoria del agente en tres niveles con pesos epistemológicos

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 4 · **Docs:** docs/data-architecture/06

## Contexto

Una única estructura genérica "memory" mezclaría estado efímero, experiencia e
inducción — imposible de evaluar (H3) y epistemológicamente peligroso (lo simulado pesando
como lo real).

## Decisión

1. **Working memory**: estado del grafo, efímero; persiste solo su traza (`AgentRun`,
   `AgentStep` con E/S estructuradas — sin chain-of-thought; `RetrievalEvent`).
2. **Memoria episódica** (`CaseMemory`): recuperación por similitud de firma sintomática
   PONDERADA por `EpistemicLevel` — SIMULATED/SYNTHETIC 0,5 · PUBLIC_DATASET 0,7 ·
   REAL_UNVALIDATED 0,8 · HUMAN_VALIDATED 1,0. Un escenario simulado jamás adquiere
   automáticamente el peso de un caso real confirmado.
3. **Memoria semántica/evolutiva** (`LearnedPattern` + `PatternRelation`): patrones con
   estados CANDIDATE→EMERGING→VALIDATED (→REJECTED/SUPERSEDED/RETIRED), evidencia a favor y
   en contra, novelty_score y versionado (nunca edición in situ: SUPERSEDES).
4. **La promoción NUNCA es automática en esta fase**: el agente solo registra CANDIDATE
   (episodios sin correspondencia documentada) y acumula evidencia; los umbrales de
   consolidación EMERGING/VALIDATED son objeto de investigación y requieren aprobación.
5. Grafo de patrones sobre SQL (PatternRelation); sin Neo4j mientras el volumen no lo exija.
6. `AgentRun.memory_mode` (none/episodic/episodic_semantic) deja preparado el experimento
   comparativo H3 sin tocar el esquema.

## Consecuencias

- La memoria evolutiva es medible desde el día 1 (métricas en docs/data-architecture/06 §exp).
- Riesgo aceptado: la ponderación epistemológica fija (0,5–1,0) es una decisión de diseño
  a justificar/sensibilizar en la evaluación.
