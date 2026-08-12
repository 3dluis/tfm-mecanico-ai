# ADR-0022 — Gobernanza de modelos: registry, cards, manifest y ciclo de vida

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 7

## Contexto

Los modelos (ML, embeddings, LLM) son artefactos experimentales de la investigación:
deben ser reproducibles, comparables y trazables. Hasta F6 existían piezas (ModelManifest,
tracking JSONL, protocolo ADR-0011) sin marco unificado ni ciclo de vida formal.

## Decisión

1. **Taxonomía formal** ML / EMBEDDING / LLM con responsabilidades y prohibiciones
   (docs/models/01); la separación ML/LLM de ADR-0009 se mantiene invariante.
2. **Baseline-first como política de modelos** (generaliza ADR-0011): ningún modelo
   complejo sin superar baselines bajo el mismo protocolo; resultados negativos se
   documentan con card (REJECTED), no se descartan en silencio.
3. **Model Registry** = catálogo lógico común, implementado como **filesystem + JSON**
   en `ai-models/registry/` con contratos (`ModelRegistryEntry/TrainingRun/
   ModelExperiment/ModelEvaluation/ModelDeployment`). Sin servicio independiente ni
   plataforma MLOps durante el TFM; diseño compatible con un registro cloud futuro.
4. **Ciclo de vida** EXPERIMENTAL→CANDIDATE→VALIDATED→EDGE_APPROVED→DEPLOYED
   (+REJECTED/SUPERSEDED/RETIRED) con transiciones validadas por código
   (`validate_status_transition`). **EDGE_APPROVED exige validación en hardware**
   (latencia, RAM, ARM64, estabilidad, formato) — nunca solo métricas offline.
5. **Model Cards obligatorias** (plantilla común v1 con sección de
   limitaciones/modos de fallo obligatoria) + **informes de comparación** por experimento.
6. **ModelManifest extendido aditivamente** (model_type, runtime_version,
   minimum_hardware, training_run_id + campos LLM opcionales) sin romper compatibilidad.
7. **ONNX como formato de distribución ML al edge** (formaliza la práctica F3);
   joblib/pickle solo justificado y nunca para distribución.
8. **Rollback diseñado** (`ModelDeployment` active/previous), instalación manual en el TFM.
9. **Entrenar ≠ inferir**: ai-models entrena, el edge infiere; sin online learning de
   modelos ML en esta fase (la memoria evolutiva no modifica pesos).

## Alternativas descartadas

- **MLflow/W&B**: valor real (UI, artefactos) pero infraestructura y dependencia
  innecesarias para ~10 modelos; los archivos versionados en git son suficientes y más
  auditables para un tribunal. Re-evaluable si el volumen crece.
- **Registro en la BD del edge**: mezclaría gobernanza (investigación) con runtime;
  el edge solo necesita el manifest del modelo activo.
- **Un registry por categoría**: duplicaría ciclo de vida y herramientas; las categorías
  difieren en campos de card, no en gobernanza.

## Consecuencias

Los resultados F3 quedan importados sin recalcular (EXP-ANOM-001); todo modelo futuro
nace con TrainingRun+card o no entra al sistema. CI ligero valida integridad del
registro (sin entrenamientos pesados).
