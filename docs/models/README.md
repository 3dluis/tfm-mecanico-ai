# Modelos de IA — estrategia, gobernanza y ciclo de vida

**Punto de entrada a la gestión de modelos del sistema (F7, ADR-0022/0023/0024).**
Los modelos NO son solo componentes técnicos: son **artefactos experimentales de la
investigación** y deben ser reproducibles, comparables y trazables. La regla fundamental:

```
¿Qué datos? → ¿Qué experimento? → ¿Qué modelo? → ¿Qué versión? → ¿Qué artefacto?
→ ¿Qué configuración? → ¿Qué inferencia? → ¿Qué decisión produjo?
```

debe poder reconstruirse **en ambos sentidos, siempre**.

## Las tres categorías (taxonomía formal, detalle en [01](01_model_strategy.md))

| Categoría | Responsabilidad | Prohibido |
|---|---|---|
| **ML** | Detección de anomalías (ventana Y contextual/evento), detección de eventos, clustering, change-point, modelado temporal, baselines | — |
| **Embeddings** | Representar corpus RAG, CaseMemory, LearnedPatterns, síntomas, eventos, perfiles | Evaluarse "de rebote" con el LLM: se evalúan POR SEPARADO |
| **LLM** | Funciones agénticas: planificación, triage, hipótesis, selección de herramientas, interpretación de evidencia, crítica, explicación, reporte | **Sustituir la detección matemática de anomalías** (ADR-0009, invariante desde F2) |

## Dónde ocurre cada cosa

- **Entrenamiento y evaluación offline:** `ai-models/` (único entorno de datasets,
  experimentos, entrenamiento, evaluación, exportación y empaquetado — [ai-models/README](../../ai-models/README.md)).
- **Inferencia:** `diagnostic-agent/` (Edge Agent Runtime). Regla arquitectónica:
  *ai-models entrena, el edge infiere*; el edge NO reentrena modelos pesados
  automáticamente y la memoria evolutiva es distinta del entrenamiento de pesos ([05](05_training_pipeline.md)).
- **Catálogo:** Model Registry en `ai-models/registry/` (filesystem + JSON,
  [08](08_model_registry.md)); cada artefacto viaja con su [ModelManifest](09_model_manifest.md) portable.
- **Paso a edge:** pipeline export→manifest→checksum→validación ARM64→EDGE_APPROVED→
  instalación (manual en el TFM) — [10](10_edge_deployment.md).
- **Fichas:** [model-cards/](model-cards/README.md) (plantilla común + cards reales).
- **Comparaciones:** [comparisons/](comparisons/) (una por experimento relevante).

## Mapa de documentos

| Doc | Qué responde |
|---|---|
| [01 Estrategia](01_model_strategy.md) | Taxonomía, escalera LLM (sin foundation training), relación con DSR |
| [02 Modelos ML](02_ml_models.md) | Familias, cards ML, detección de eventos, anomalía contextual vs ventana |
| [03 Modelos LLM](03_llm_models.md) | Candidatos, benchmark interno, ModelRouter, provenance de inferencia |
| [04 Embeddings](04_embedding_models.md) | Tres usos, evaluación separada (Recall@K/MRR/nDCG) |
| [05 Training pipeline](05_training_pipeline.md) | Dataset→…→Edge Validation; training vs inference; online learning fuera |
| [06 Datasets](06_dataset_strategy.md) | Linaje, splits versionados, held-out intocable, concept drift |
| [07 Evaluación](07_evaluation_protocol.md) | Protocolos por categoría; métricas por episodio; reportes |
| [08 Model Registry](08_model_registry.md) | Catálogo, ciclo de vida y condiciones de transición |
| [09 Model Manifest](09_model_manifest.md) | Contrato portable; revisión y extensión F7 |
| [10 Edge deployment](10_edge_deployment.md) | Pipeline a edge, matriz hardware, rollback |
| [11 Cuantización](11_quantization_optimization.md) | Optimización edge (después de baseline funcional, nunca antes) |
| [12 Tracking](12_experiment_tracking.md) | Configs declarativas, tracking simple, notebooks ≠ pipeline, CI |
| [13 Reproducibilidad](13_reproducibility.md) | Qué registra cada experimento y cómo re-ejecutarlo |
| [14 Selección](14_model_selection.md) | Criterios multicriterio, trade-offs, inventario de modelos |

Diagramas: [ciclo ML](diagrams/ml-lifecycle.mmd) · [ciclo LLM](diagrams/llm-lifecycle.mmd) ·
[provenance](diagrams/model-provenance.mmd) · [uso por agente](diagrams/agent-model-use.mmd)
· Validación ARM64/RPi paso a paso: [edge-validation-a2a3](edge-validation-a2a3.md)
· Índice de experimentos: [docs/experiments/](../experiments/README.md)

## Relación con el resto del sistema

- **[VehicleTelemetrySnapshot](../data-architecture/11_vehicle_telemetry_snapshot.md) (F11):**
  entrada canónica para ML — `snapshots[] → matriz/dataframe → windowing/event grouping →
  feature engineering → modelo`, sin que cada entrenamiento reconstruya su propio pivot
  long→wide. El snapshot **no contiene features** (siguen en `FeatureVector`/
  `EventFeatureVector`) y `NULL` significa ausencia, no cero: imputar es decisión de la fase
  de features y debe declararse en la card del modelo. **Desde F13 esta ruta está
  implementada y validada por paridad exacta** (`ai_models.data.snapshot_matrix`,
  [EXP-ANOM-005](comparisons/wide_path_parity_v1.md), ADR-0031); la línea de experimentos
  ML se rige por el [Protocolo ML v1](../experiments/protocolo_ml_v1.md).
- **[PostgreSQL + pgvector](../data-architecture/13_postgresql_pgvector_edge.md) (F12):** las
  inferencias viven en el schema `models`; los embeddings de conocimiento y memoria son
  columnas `vector(384)` en la misma base (sin segunda base vectorial: regla ADR-0030). Los
  modelos de embedding se siguen evaluando aparte (Recall@K/MRR/nDCG, [04](04_embedding_models.md)):
  la latencia medida del motor NO es calidad de recuperación.
- **[data-architecture](../data-architecture/README.md):** TrainingRun/ModelExperiment/
  ModelRegistryEntry/ModelEvaluation/ModelDeployment son contratos de
  `mecanico_contracts` (diccionario autogenerado); `ModelInference` (F4) enlaza cada
  inferencia con su modelo/versión — provenance completo en [diagrams/model-provenance.mmd](diagrams/model-provenance.mmd).
- **[agent-runtime](../agent-runtime/README.md):** qué agente consume qué categoría de
  modelo ([diagrams/agent-model-use.mmd](diagrams/agent-model-use.mmd)); el ModelRouter
  selecciona por `capabilities` del registro (routing sofisticado pospuesto).
- **[event-intelligence](../event-intelligence/README.md):** detectores de eventos y
  modelos contextuales son modelos ML de pleno derecho, con card y entrada de registro.
- **experimentos:** protocolo A0–A6 (agent-runtime/12) + ventana-vs-evento
  (event-intelligence/11) + preguntas experimentales de [07](07_evaluation_protocol.md).
