# 08 — Memoria en el runtime

> **⚠ Fuera del alcance experimental del TFM (ADR-0036, 27-ago-2026).** Tras la
> acotación de la pregunta de investigación a explicación diagnóstica trazable y
> abstención ante evidencia insuficiente, la arquitectura de memoria del agente no forma parte de la validación
> experimental de este trabajo. **El diseño y el código se conservan** y siguen siendo
> correctos; simplemente no se evalúan. Catálogo completo y justificación:
> [`docs/alineacion_v4/05_fuera_de_alcance.md`](../../alineacion_v4/05_fuera_de_alcance.md).

[← Índice](README.md) · Diagrama: [memory.mmd](diagrams/memory.mmd) · Base: [ADR-0013](../adr/0013-memoria-tres-niveles.md) y [data-architecture/06](../data-architecture/06_memoria_evolutiva.md)

Sin cambios de modelo de datos: el runtime CONSUME la arquitectura de F4.

- **Working memory** = DiagnosticState (doc 03 §estado): objetivo, anomalías activas,
  hipótesis, evidencia, preguntas pendientes, plan, casos/documentos recuperados, resultados
  de tools. Efímera; su traza persiste como AgentRun/AgentStep. No confundir con episódica.
- **Episódica** (CaseMemory): la consulta el Recall Agent con similitud multifactor
  (vehículo/motor, síntomas, PIDs, DTC, feature vectors, firma temporal, diagnóstico) ×
  peso epistemológico. La escribe SOLO el Memory Agent al concluir.
- **Evolutiva** (LearnedPattern): comparación de patrón al memorizar → conocido: actualizar
  evidencia (supporting/contradicting, last_seen, preservando novelty/confidence/provenance/
  version) · desconocido: CANDIDATE. Consolidación CANDIDATE→EMERGING→VALIDATED: proceso
  aparte, semiautomático como máximo, fuera de la autonomía del runtime (SHOULD HAVE).

**Aprendizaje ≠ memoria** (requisito 12): el ML learning (telemetría→entrenamiento→modelo)
vive en `ai-models` y entra al edge como paquete ONNX+manifest (ADR-0009); la evolución de
memoria (experiencias→casos→patrones→conocimiento) vive en el runtime. Un LearnedPattern
JAMÁS modifica pesos de un modelo ML; si un patrón sugiere reentrenar, eso es una
recomendación al proceso de ai-models, con humanos en el lazo.
