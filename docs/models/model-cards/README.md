# Model Cards

Cada modelo del sistema tiene una ficha versionada. Directorios: [`ml/`](ml/) ·
[`llm/`](llm/) · [`embeddings/`](embeddings/). Las cards se escriben CONTRA los datos
del registro (`ai-models/registry/`) — las métricas provienen de los TrainingRuns, nunca
se inventan ni se recalculan a mano. Secciones marcadas ⚙ son derivables automáticamente
de `TrainingRun + ModelManifest + evaluaciones` ([13 §4](../13_reproducibility.md)).

## Plantilla común (v1)

```yaml
# ⚙ Identificación
model_id | name | version | model_type (ml|llm|embedding) | model_family | purpose
owner/component            # quién lo consume (p. ej. diagnostic-agent:detection)
status                     # ciclo de vida del registro

# ⚙ Origen
base_model | algorithm | training_method | adaptation_method

# ⚙ Datos (linaje)
dataset_ids | dataset_versions | training_split | validation_split | test_split

# ⚙ Features
features | feature_schema_version | preprocessing_version

# ⚙ Configuración
hyperparameters

# ⚙ Artefacto
artifact_format | artifact_path | checksum | framework | framework_version

# ⚙ Fechas y hardware
created_at | trained_at | hardware_training | hardware_evaluation

# ⚙ Métricas
metrics                    # bajo el protocolo declarado

# ✍ Narrativa (obligatoria, humana)
limitations
known_failure_modes
out_of_distribution_risks
unsupported_use_cases

# ⚙ Edge
edge_compatible | edge_validation_status

# ⚙ Legal
license | source | references
```

No todos los campos aplican a todos los modelos (un LLM no tiene `training_split`; un
detector de reglas no tiene `checksum`), pero el esquema es común y los campos que no
aplican se marcan `n/a` — nunca se omiten en silencio. Campos extra por categoría:
ML en [02 §2](../02_ml_models.md) · LLM en [03 §4](../03_llm_models.md) · embeddings en
[04 §4](../04_embedding_models.md).

**La sección de limitaciones y modos de fallo conocidos es OBLIGATORIA** — es la parte
de mayor valor para la memoria del TFM.

## Cards existentes

| Card | Estado |
|---|---|
| [ml/anom-lof.md](ml/anom-lof.md) | VALIDATED (modelo por defecto) |
| [ml/anom-ocsvm.md](ml/anom-ocsvm.md) | CANDIDATE (2º paquete) |
| [ml/anom-zscore.md](ml/anom-zscore.md) | REJECTED (negativo documentado) |
| [ml/anom-iforest.md](ml/anom-iforest.md) | REJECTED (negativo documentado) |
| [ml/event-detector.md](ml/event-detector.md) | VALIDATED (baseline de eventos) |
| [ml/event-baseline-z.md](ml/event-baseline-z.md) | CANDIDATE |
| llm/ | sin modelos evaluados aún — candidatos en [03 §3](../03_llm_models.md) |
| embeddings/ | sin modelos evaluados aún — candidatos en [04 §5](../04_embedding_models.md) |
