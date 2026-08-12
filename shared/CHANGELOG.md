# CHANGELOG — mecanico_contracts

## v0.4.0 · SCHEMA_VERSION 2 (2026-08-12) — Gobernanza de modelos (F7)

Cambios ADITIVOS (retro-compatibles):

- Nuevo módulo `models_registry.py` (ADR-0022): `TrainingRun`, `ModelExperiment`,
  `ModelEvaluation`, `ModelRegistryEntry`, `ModelDeployment`, `HardwareValidation`,
  enums `ModelType`/`ModelStatus`/`ModelCapability`/`HardwareValidationStatus`,
  `ALLOWED_STATUS_TRANSITIONS` + `validate_status_transition` (ciclo de vida
  EXPERIMENTAL→CANDIDATE→VALIDATED→EDGE_APPROVED→DEPLOYED, + REJECTED/SUPERSEDED/RETIRED).
- `ModelManifest`: campos opcionales nuevos `model_type` (default "ml"),
  `preprocessing_version`, `runtime_version`, `minimum_hardware`, `training_run_id` y
  (solo LLM) `quantization`, `context_window`, `tokenizer`, `prompt_compatibility`,
  `tool_schema_version`. Ningún campo existente cambia.

## v0.3.0 · SCHEMA_VERSION 2 (2026-08-12) — Event Intelligence (F6)

Cambios ADITIVOS (retro-compatibles dentro de SCHEMA_VERSION 2, política de
docs/data-architecture/07):

- Nuevo módulo `events_model.py` (ADR-0019/0021): `VehicleEvent`, `EventFeatureVector`,
  `EventBaseline`, `EventClass` (observed/inferred/estimated), `EVENT_TAXONOMY` v1
  (`TAXONOMY_VERSION = 1`).
- Nuevo enum `AnomalyScope` (point/window/event/session/cross_event) en `data_enums`.
- `DetectedAnomaly`: `window_id` pasa a opcional (sigue siendo OBLIGATORIO cuando
  `anomaly_scope=window`, validado por modelo → el pipeline F3 no cambia); nuevos campos
  opcionales `event_id`, `baseline_id` y `anomaly_scope` (default `window`).
- `CaseMemory`: nuevo campo `related_event_ids` (default `[]`).
- `LearnedPattern`: nuevo campo `event_types` (default `[]`).

## v0.2.0 · SCHEMA_VERSION 2 (2026-08-12)

Cambio MAYOR (permitido: aún no existen datos persistidos en producción; a partir de
esta versión rige la política aditiva de docs/data-architecture/07_provenance_versionado.md).

- Nuevo modelo de datos completo (`data_model.py`, ADR-0012/0013): TelemetrySession
  (con SessionSource), TelemetryPoint, TelemetryWindow, FeatureVector, ModelInference,
  DiagnosticCase, DiagnosticEvidence, ProvenanceRecord, CaseMemory (EpistemicLevel),
  LearnedPattern, PatternRelation, DiagnosticFeedback, MaintenanceEvent, AgentRun,
  AgentStep, RetrievalEvent, KnowledgeDocument, KnowledgeChunk + 13 enums nuevos.
- **BREAKING** `DiagnosticHypothesis`: pasa a estructurada (case_id, rank,
  suspected_component, failure_mode, status); las listas `supporting_evidence` /
  `contradicting_evidence` se sustituyen por la entidad `DiagnosticEvidence` con rol.
- `CaseRecord` queda DEPRECADO en favor de `CaseMemory` (se retira en v3).
- Alias `OBDObservation = OBDReading` (nombre canónico de la observación cruda).

## v0.1.0 · SCHEMA_VERSION 1 (2026-08-12)

Contratos iniciales (ADR-0007).
