# 12 — Experiment tracking

## 1. Herramienta: la más simple que cumpla (ADR-0024)

Decisión evaluada: **archivos estructurados versionados en git** — `runs.jsonl`
(tracking por ejecución, F3) + registro JSON (`ai-models/registry/`, F7) + configs YAML
declarativas. SQLite/MLflow solo si el volumen de experimentos lo justifica más adelante;
hoy añadirían infraestructura sin valor. **La reproducibilidad importa más que la
plataforma.**

## 2. Configuración declarativa

Todo experimento comparativo tiene config YAML (patrón en
[`ai-models/configs/exp-anom-001.yaml`](../../ai-models/configs/exp-anom-001.yaml)):

```yaml
experiment: {id: EXP-ANOM-001, protocol: ADR-0011}
dataset: {id: obd-lab-suite-v1, version: "1", split: suite-v1-split-1}
features: {schema: fs1, preprocessing: embedded-standard-scaler}
random_seed: 42
models:
  - {type: lof, parameters: {n_neighbors: 10, novelty: true}}
```

Los parámetros críticos NUNCA viven solo en notebooks ni hardcodeados en scripts.

## 3. Notebooks ≠ pipeline

`ai-models/notebooks/` sirve para exploración. Regla: **ningún resultado que aparezca en
la memoria del TFM puede provenir únicamente de un notebook** — debe re-ejecutarse por
script/config (`make experiments`, `experiments/e1_baselines.py`…). Un notebook puede
descubrir; un script reproduce.

## 4. Entidades

`ModelExperiment` (comparación válida: mismos datos/split/features/protocolo) agrupa
`TrainingRun`s (una ejecución concreta con config+seed+commit+hardware+métricas) y
produce un informe en [comparisons/](comparisons/) + decisión en el registro. Ejemplo
real: `EXP-ANOM-001` (LOF vs IForest vs OC-SVM vs z-score, F3, importado sin recalcular).

## 5. Validaciones de CI (ligeras; sin entrenamientos pesados)

- schemas JSON y diccionario regenerados sin divergencia (ya en `make check`);
- registro íntegro: todo JSON parsea como contrato y las referencias
  experimento↔run↔modelo existen (`ModelRegistry.check`, testeado);
- transiciones de estado válidas (contrato) y checksums verificables cuando el artefacto
  está presente;
- smoke de inferencia ONNX y paridad sklearn↔onnxruntime (tests F3/F4 existentes);
- Model Cards mínimas presentes para modelos en estado ≥ CANDIDATE (test).

CI NUNCA ejecuta entrenamientos pesados; los experimentos se lanzan manualmente.
