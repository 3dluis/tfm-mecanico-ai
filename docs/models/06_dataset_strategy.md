# 06 — Estrategia de datasets y linaje

## 1. Linaje obligatorio

Todo modelo apunta EXACTAMENTE a sus datos:

```
dataset_id · dataset_version · checksum · source · license
split_version · train_ids · validation_ids · test_ids
```

En la práctica: las sesiones sintéticas llevan `scenario_id + seed` (regenerables byte a
byte), las suites se versionan (`obd-lab-suite-v1`), y el split es un artefacto con
nombre (`suite-v1-split-1`: escenarios `normal` → train/val; `known_fault` + `held_out`
→ solo test). **Versión 1.1 (F9):** +16 sesiones normales SOLO de train
(`suite_v1_train_ext.yaml`, con justificación de diversidad); validation/test/held-out
idénticos a v1 — un cambio de train es un cambio de versión de dataset, nunca silencioso. `TrainingRun.dataset_*` y `ModelExperiment.dataset_*` registran el linaje;
los IDs por split viven junto a la suite (YAML) para no duplicarlos por modelo.

## 2. Conjuntos separados (sin fugas)

```
TRAINING DATA · VALIDATION DATA · TEST DATA · HELD-OUT DATA · REAL VEHICLE DATA
```

Reglas vigentes desde F3 (ADR-0010/0011), ahora formalizadas para TODOS los modelos:

- **held-out intocable:** jamás se usa para entrenar, ajustar hiperparámetros o decidir
  umbrales; solo evaluación final. Es la protección directa contra la circularidad (RI1).
- los datos usados para GENERAR escenarios (parámetros del simulador, catálogo de fallos)
  no se filtran al conjunto held-out: las anomalías held-out son relacionales/temporales
  y sus mecanismos no aparecen en el corpus de entrenamiento ni en las reglas de verify.
- los datos reales (HCRL, vehículo propio si llega) se reservan para validación
  cruzada de umbrales y calibración, con su propia ficha de dataset.
- el ground truth de eventos (F6) es estado privado del generador: el detector nunca lo
  ve en inferencia.

## 3. Qué dataset alimenta cada modelo

| Modelo | Entrena con | Se evalúa con |
|---|---|---|
| LOF / OC-SVM (ventana) | suite v1 `normal` (train) | val (normal) + test (known+held-out) |
| z-score / IForest | ídem (rechazados, mismos datos) | ídem |
| `ed:1` (eventos, reglas) | no entrena (umbral analítico) | ground truth de eventos obd-lab |
| `event-baseline-z` | aceleraciones normales comparables | held-out normal + trips con fallo |
| LLM (benchmark) | no entrena | benchmarks/agent-diagnostics (GT del catálogo) |
| Embeddings (futuro) | no entrena (pretrained) | corpus anotado + casos sintéticos |

## 4. Ficha de dataset

Cada dataset usado tiene ficha (docs/fase3/dataset_hcrl_verificacion.md es el patrón
para datasets externos): variables, muestreo, vehículos, condiciones, etiquetas,
licencia, limitaciones y mapeo de PIDs. El dataset debe ajustarse a la pregunta de
investigación, no al revés.
