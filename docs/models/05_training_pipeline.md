# 05 — Training pipeline

## 1. Pipeline reproducible (diagrama: [ml-lifecycle](diagrams/ml-lifecycle.mmd))

```
Raw Dataset → Dataset Validation → Preprocessing → Feature Engineering → Split
→ Training → Validation → Test → Export → Model Manifest → Registry → Edge Validation
```

Cada etapa deja rastro: el dataset con `dataset_id/version/checksum` ([06](06_dataset_strategy.md)),
el split versionado, las features con `feature_schema_version`, el entrenamiento como
`TrainingRun` (config+seed+git_commit+hardware+métricas), la exportación con manifest y
checksum, el alta en el registro y la validación edge como `HardwareValidation`.
Implementación actual: `ai_models.data/anomaly/evaluation/export` + `tracking.py`
(runs.jsonl) + `registry.py`. El experimento E1 completo es re-ejecutable
(`make experiments`); su registro post-hoc está en `configs/exp-anom-001.yaml`.

## 2. Regla arquitectónica: entrenar ≠ inferir

```
ai-models            → TRAINING (y evaluación offline)
diagnostic-agent     → INFERENCE (Edge Agent Runtime)
```

El dispositivo edge NO reentrena modelos pesados automáticamente. La **memoria evolutiva
(CaseMemory/LearnedPattern) evoluciona sin modificar silenciosamente pesos de ningún
modelo**: son mecanismos distintos y así se evalúan (H3/H5 vs experimentos de modelos).

## 3. Online learning: fuera de esta fase

No se implementa online learning de modelos ML. Si se considerase en el futuro sería una
línea de investigación separada, por riesgos documentados: catastrophic forgetting,
contaminación del conjunto de entrenamiento, concept drift no controlado, ejemplos
adversarios y pérdida de reproducibilidad. Excepción acotada y ya diseñada: los
`EventBaseline` acumulan estadísticos por contexto (Welford) — no son pesos de modelo,
están versionados y su actualización es auditable (ADR-0021).

## 4. Concept drift (estudio futuro, sin implementar)

Cómo podríamos estudiarlo con lo ya diseñado: `comportamiento del vehículo en el tiempo
→ evolución de EventBaseline (version, sample_count, last_updated) → deriva del
concepto`. Comparar baselines del mismo contexto en ventanas temporales distintas da una
señal de drift por vehículo; su relación con la memoria evolutiva (¿un patrón aprendido
deja de aplicar?) queda como trabajo futuro explícito.

## 5. Hardware de entrenamiento documentado

Todo `TrainingRun`/`ModelEvaluation` registra su `hardware`, distinguiendo:

```
Development (Mac) · Training (sandbox-x86 / Mac) · Evaluation (ídem) · Edge Validation (arm64/RPi)
```

Sin esto, los tiempos de entrenamiento e inferencia no son interpretables (una latencia
medida en el sandbox x86 no es una latencia de RPi — matriz en [10 §3](10_edge_deployment.md)).
