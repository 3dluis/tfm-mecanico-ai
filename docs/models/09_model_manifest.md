# 09 — Model Manifest (revisión F7)

## 1. Papel

Contrato portable (ADR-0009, implementado en F3) que acompaña a TODO artefacto
distribuido al edge. El runtime del edge se niega a cargar un artefacto cuyo checksum no
coincida con el manifest (ciclo de promoción validado en F4).

## 2. Revisión de cobertura (requisito F7 §24)

| Campo requerido | Estado en `ModelManifest` |
|---|---|
| model_id / version / type | ✅ `model_id`, `version`; `model_type` **añadido en F7** (default `ml`) |
| input_schema / output_schema | ✅ `expected_features` (orden exacto) + `score_direction`/`decision_threshold`; formal JSON-schema queda cubierto por los schemas exportados del contrato |
| features + feature_schema_version | ✅ `expected_features`; la versión viaja en FeatureVector; `preprocessing_version` **añadido** |
| preprocessing_version | ✅ añadido (complementa `preprocessing`) |
| artifact_format + checksum | ✅ ya existían (`artifact_format`, `artifact_sha256`) |
| runtime + runtime_version | ✅ `runtime` existía; `runtime_version` **añadido** |
| minimum_hardware | ✅ **añadido** (`minimum_hardware`) |
| metrics_summary | ✅ `validation_metrics` |
| created_at | ✅ `trained_at` (+`training_run_id` **añadido** para provenance) |

**Solo LLM (añadidos, opcionales):** `quantization · context_window · tokenizer ·
prompt_compatibility · tool_schema_version`.

Todos los cambios son ADITIVOS con default: ningún manifest existente deja de validar
(compatibilidad verificada por test). No se rompió compatibilidad.

## 3. Provenance desde la inferencia (obligatorio)

Navegación completa en ambos sentidos (diagrama [model-provenance](diagrams/model-provenance.mmd)):

```
ModelInference → Model version → Model Manifest → TrainingRun → ModelExperiment → Dataset
```

`ModelInference` (F4) ya registra `model_id/model_name/model_version/score/threshold/
latency/executed_at` e `input` por referencia (`fv_id→window→session`); el manifest
enlaza ahora `training_run_id`, y el TrainingRun enlaza experimento y dataset. Cada
`ModelInference` es por tanto auditable y el diagnóstico que produjo, reproducible.
