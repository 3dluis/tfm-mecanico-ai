# 13 — Política de reproducibilidad

## 1. Qué registra cada experimento (obligatorio)

```
git_commit · python_version · dependencies (lockfile/pyproject) · hardware

> **Fuente canónica de versiones (F20-aud):** el stack real —qué librerías se usan, en qué
> versión instalada y en qué capa— vive en [15 Stack ML/XAI](15_stack_ml_xai.md). No se
> repiten versiones en otros documentos para evitar divergencia. El inventario es
> reproducible (`uv run python tools/dep_inventory.py`) y está verificado por
> `tests-integration/test_dependency_inventory.py`.
dataset_version · feature_version (feature_schema_version + preprocessing_version)
seed · hyperparameters
model artifact checksum (cuando hay artefacto)
```

Implementación: `tracking.py` captura git sha, plataforma y recursos por run;
`TrainingRun` formaliza el resto; el manifest lleva el checksum. La aleatoriedad SIEMPRE
lleva semilla (invariante desde F1: los datos sintéticos son regenerables byte a byte).

## 2. Procedimiento de re-ejecución

Cada experimento tiene un comando documentado:

| Experimento | Comando |
|---|---|
| E1 baselines (F3) | `make experiments` (o `python experiments/e1_baselines.py`) |
| Registro de modelos (F7) | `python experiments/register_f3.py` — determinista byte a byte (test lo verifica) |
| Slice de eventos (F6) | `pytest tests-integration/test_event_slice.py` |
| Suite de escenarios | `make generate-suite` |

Criterio de éxito: otra persona, con el repo en el commit indicado y la misma semilla,
obtiene los mismos números (o, para tiempos/recursos, valores comparables en el mismo
hardware declarado).

## 3. Versionado (no mezclar identificadores)

Cuatro ejes INDEPENDIENTES, cada uno con su campo:

```
model algorithm version   → ModelRegistryEntry.algorithm_version  (implementación)
trained artifact version  → ModelRegistryEntry.version / ModelManifest.version (semver)
feature schema version    → feature_schema_version (fs1 = FEATURE_NAMES v1; efv:1 eventos)
dataset version           → dataset_id + dataset_version (+ split_version)
```

Ejemplo real que la distinción resuelve: `anom-lof` algoritmo `baselines-e1` tiene DOS
artefactos (0.1.0 del experimento E1, SUPERSEDED; 0.2.0 paquete ONNX, VALIDATED) sobre
las MISMAS features `fs1` y el MISMO dataset `obd-lab-suite-v1@1`.

## 4. Model Cards con parte autogenerada

Para evitar documentación manual inconsistente, la parte factual de una card
(identificación, linaje, hiperparámetros, métricas, hardware) puede derivarse de
`TrainingRun + ModelManifest + resultados de evaluación`; la parte narrativa
(interpretación, limitaciones, modos de fallo) es humana y obligatoria. La plantilla
([model-cards/README](model-cards/README.md)) marca qué secciones son derivables. La
generación automática se implementará cuando el nº de modelos lo justifique; hoy las
cards se escriben a mano CONTRA los JSON del registro (el test de integridad detecta
divergencias de métricas).
