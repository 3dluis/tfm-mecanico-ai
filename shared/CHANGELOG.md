# CHANGELOG — mecanico_contracts

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
