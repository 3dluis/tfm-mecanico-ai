# 08 — Model Registry

## 1. Qué es

Catálogo lógico ÚNICO para las tres categorías (`ML | LLM | EMBEDDING`). Implementación
del TFM: **filesystem + JSON** en `ai-models/registry/` (sin servicio independiente),
con contratos `ModelRegistryEntry / ModelExperiment / TrainingRun` de
`mecanico_contracts.models_registry` y acceso por `ai_models.registry.ModelRegistry`
(transiciones validadas, verificación de checksum, chequeo de integridad referencial).

Campos de una entrada: `model_id · model_family · model_type · version ·
algorithm_version · capabilities · status · artifact_format/uri · checksum ·
manifest_uri · model_card_uri · training_run_id · created_at · validated_at ·
edge_compatible · hardware_validation[] · notes`.

## 2. Ciclo de vida y condiciones de transición

```
EXPERIMENTAL → CANDIDATE → VALIDATED → EDGE_APPROVED → DEPLOYED
        (+ REJECTED · SUPERSEDED · RETIRED)
```

| Transición | Condición verificable |
|---|---|
| EXPERIMENTAL→CANDIDATE | TrainingRun completo con linaje + métricas bajo protocolo pre-registrado |
| CANDIDATE→VALIDATED | supera a los baselines en su ModelExperiment; informe de comparación publicado; decisión registrada |
| VALIDATED→EDGE_APPROVED | **validación en hardware**: latencia, RAM, compatibilidad ARM64, estabilidad sostenida, formato/runtime verificados (matriz [10 §3](10_edge_deployment.md)). *Nunca solo métricas offline.* |
| EDGE_APPROVED→DEPLOYED | instalado en un dispositivo con `ModelDeployment` (active/previous para rollback) |
| →REJECTED | resultado negativo documentado (¡con card!: los negativos son hallazgos) |
| →SUPERSEDED | existe versión posterior que lo sustituye (desde F9 también aplicable a EXPERIMENTAL/CANDIDATE: una versión puede quedar sucedida antes de validarse) |
| →RETIRED | fuera de uso; se conserva el registro para reproducibilidad histórica |

Las transiciones ilegales las rechaza `validate_status_transition` (testeado).

## 3. Capacidades (para el ModelRouter)

Cada entrada declara `capabilities` (`TRIAGE, HYPOTHESIS_GENERATION, CRITIQUE,
REPORTING, TOOL_SELECTION, EMBEDDINGS, ANOMALY_DETECTION, EVENT_DETECTION`). El Agent
Runtime podrá pedir "un modelo con capability X en estado ≥ VALIDATED" — el routing
sofisticado queda pospuesto hasta que haya más de un modelo por capacidad.

## 4. Registry vs Manifest

**Registry** = catálogo de modelos conocidos por el sistema (esta página).
**Manifest** = contrato PORTABLE que acompaña a un artefacto concreto ([09](09_model_manifest.md)):

```
Registry → model version 2.1 → artifact.onnx + model-manifest.json
```

La entrada del registro APUNTA al manifest (`manifest_uri`); el manifest viaja con el
artefacto al edge y basta por sí solo para ejecutar la inferencia correctamente.

## 5. Cloud futuro

El diseño es compatible con un registro central en cloud (catálogo maestro, artefactos,
versionado, distribución y rollback) — pero durante el TFM todo funciona localmente y la
instalación es manual (ADR-0022). No se construye una plataforma MLOps completa.
