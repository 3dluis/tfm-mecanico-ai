# 01 — Overview del Edge Agent Runtime

[← Índice](README.md)

## Qué es

Un runtime local (Raspberry Pi como objetivo) donde un **Supervisor** orquesta agentes
especializados para alcanzar un objetivo de diagnóstico usando: LLM locales, modelos
ML/estadísticos, herramientas OBD-II, RAG local, base de datos local y las tres memorias
(working/episódica/evolutiva), con ciclos iterativos de planificación-acción-observación-
evaluación (loop engineering) y límites estrictos.

## Principios (heredados y nuevos)

1. **Local-first**: todo el ciclo funciona sin conectividad (ADR-0006/0015).
2. **Separación ML/LLM** (ADR-0009): las anomalías son matemáticas; el LLM planifica,
   hipotetiza, recupera y explica — nunca produce una anomalía ni invalida silenciosamente
   un resultado determinista (modelo de inferencia híbrida de 3 niveles, doc 02 §niveles).
3. **Roles ≠ instancias de modelo** (ADR-0015): los agentes son roles lógicos que comparten
   los modelos físicos disponibles (un solo LLM local al inicio; ModelRouter preparado).
4. **Evidencia o silencio**: INCONCLUSIVE/INSUFFICIENT_DATA son resultados correctos; el
   runtime jamás fuerza una respuesta.
5. **Todo auditable**: cada iteración, tool call, recuperación y decisión persiste en el
   modelo de datos v2 existente (AgentRun/AgentStep/RetrievalEvent + provenance).
6. **Read-only sobre el vehículo por defecto** (ADR-0016).

## Qué reutiliza (no se reescribe nada funcional de F3/F4)

obd-lab (escenarios/ground truth) · pipeline de telemetría y detección ONNX+ModelManifest ·
LOF elegido (ADR-0011) · contratos v2 y esquema SQLite completos (ADR-0012) · memoria
episódica/semántica con pesos epistemológicos (ADR-0013) · retriever léxico y corpus v1 ·
verify_rules deterministas · hypothesizers plugables (ADR-0014). **El grafo lineal g1 de
F4 pasa a ser el caso degenerado del runtime (arquitectura A2 del diseño experimental) —
sigue existiendo como brazo de comparación.**

## Qué añade

Supervisor con política de decisión y re-planificación · DiagnosticState explícito ·
Tool Registry formal con categorías de riesgo · loop con stop conditions · working memory
explícita · context engineering con presupuestos · ModelRouter (concepto) · observabilidad
de runtime · feature flags experimentales A0–A6.
