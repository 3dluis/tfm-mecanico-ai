# 08 — Matriz de ownership Edge / Cloud

[← Índice](README.md) · Diagrama: [edge-cloud-data-flow.mmd](diagrams/edge-cloud-data-flow.mmd)

Principio: **el edge es dueño de la operación; la nube, del histórico y la consolidación.**
El sistema es 100 % funcional offline; la nube solo añade (ADR-0006).

| Dato | Edge (RPi) | Cloud | Autoridad |
|---|---|---|---|
| Sesiones recientes + raw reciente | ✅ retención corta | opcional (config) | edge |
| Telemetría normalizada | ✅ retención media | resúmenes | edge |
| Ventanas/features | ✅ retención larga (metadatos) | con anomalías | edge |
| Modelos ML activos (paquetes ONNX) | ✅ copia verificada | ✅ registry (maestro) | cloud |
| Anomalías + inferencias | ✅ | ✅ (sync prioridad alta) | edge crea, ambos conservan |
| Diagnostic cases + hipótesis + evidencias | ✅ permanente | ✅ (sync prioridad alta) | edge crea |
| Memoria episódica | ✅ local completa | ✅ consolidada multi-dispositivo | edge crea, cloud consolida |
| Memoria semántica (LearnedPattern) | subset relevante al vehículo | ✅ maestro | cloud |
| Corpus RAG | cache de chunks activos | ✅ documentos maestros | cloud |
| Feedback / mantenimiento | ✅ | ✅ | quien lo capture |
| Outbox | ✅ (solo edge) | — | edge |
| Métricas agregadas / experimentos / datasets (licencia mediante) | — | ✅ | cloud |
| Model Registry (entradas/experimentos/TrainingRuns, F7) | manifest del modelo ACTIVO + previous (rollback) | ✅ catálogo maestro (ai-models hoy; cloud futuro) | ai-models/cloud |
| ModelDeployment (activo/anterior por dispositivo) | ✅ | copia informativa | edge |

Reglas: (1) la nube nunca escribe en el edge salvo distribución de modelos y subset de
patrones — ambos pull verificado por el edge; (2) conflicto = last-write-wins por timestamp
UTC + registro del descartado (volumen esperado bajo: escritores disjuntos por diseño);
(3) sin conectividad, TODA la cadena captura→detección→diagnóstico→memoria opera igual y el
outbox acumula.
