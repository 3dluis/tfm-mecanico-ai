# ADR-0015 — Edge Agent Runtime multiagente con agentes lógicos y LangGraph

> **⚠ Fuera del alcance experimental del TFM (ADR-0036, 27-ago-2026).** Tras la
> acotación de la pregunta de investigación a explicación diagnóstica trazable y
> abstención ante evidencia insuficiente, el runtime multiagente no forma parte de la validación
> experimental de este trabajo. **El diseño y el código se conservan** y siguen siendo
> correctos; simplemente no se evalúan. Catálogo completo y justificación:
> [`docs/alineacion_v4/05_fuera_de_alcance.md`](../alineacion_v4/05_fuera_de_alcance.md).

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 5 · **Docs:** docs/agent-runtime/

## Decisión

1. El núcleo del edge evoluciona de agente monolítico a **Mecánico IA Edge Agent Runtime**:
   9 agentes especializados (Supervisor, Telemetry, Anomaly, Diagnostic, Knowledge, Recall,
   Verification, Critic, Memory, Report) orquestados por un **Supervisor sobre LangGraph**
   con `DiagnosticState` explícito. El directorio físico sigue siendo `diagnostic-agent/`
   (renombrarlo hoy rompería historial/imports sin beneficio; se reevalúa post-TFM).
2. **Agentes = roles lógicos, no instancias de modelo** (`Agent Role ≠ LLM instance`): los
   roles comparten los modelos físicos que el hardware permita (RPi 5: un LLM local +
   embeddings + ONNX). El ModelRouter abstrae la asignación y la registra por AgentRun.
3. **Local-first**: el runtime completo (incluido RAG y memoria) opera offline; la nube
   sigue siendo complementaria (reafirma ADR-0006). SQLite local tras
   herramientas/repositorios — ni el Supervisor ni los agentes tocan SQL directo
   (reafirma ADR-0012).
4. Separación ML/LLM intacta (reafirma ADR-0009) formalizada como **inferencia híbrida de 3
   niveles** (determinista → ML → agéntico) donde ningún nivel superior invalida
   silenciosamente a uno inferior.
5. El grafo lineal g1 (ADR-0014) NO se elimina: es la arquitectura A2 del diseño
   experimental (brazo de comparación).

## Alternativas consideradas

- *Frameworks multiagente (CrewAI/AutoGen):* añaden abstracciones y dependencias pesadas
  para RPi; LangGraph ya está en el stack y su grafo explícito ES el artefacto de
  explicabilidad. Descartados.
- *Un LLM por agente:* inviable en 8 GB y experimentalmente confuso. Descartado.
- *Renombrar el directorio ahora:* impacto mecánico sin valor científico. Pospuesto.

## Consecuencias

Refactor acotado: agent_v1 se conserva; el runtime nuevo vive en
`diagnostic_agent/runtime/` reutilizando detección, memoria, retriever, verify_rules e
hipotetizadores. Riesgo principal: presupuesto de RPi con loops de LLM — mitigado por stop
conditions duras (ADR-0017) y por brazos experimentales con generador heurístico.
