# 02 — Diccionario de datos (AUTOGENERADO)

> **No editar a mano.** Este documento se genera desde los contratos Pydantic con
> `make data-docs` (módulo `mecanico_contracts.gen_data_dictionary`). La cadena
> documentación ↔ contratos ↔ JSON Schema ↔ BD se mantiene sin divergencia porque los
> tres últimos derivan del mismo modelo y este documento se regenera en CI.

Clasificación de datos (ADR-0012): **RAW** = observado directamente · **NORMALIZED** =
transformado a esquema canónico · **DERIVED** = calculado (features/ventanas) ·
**INFERRED** = producido por modelos o por el agente. *Un dato inferido nunca se presenta
como observación real*: la clase de cada entidad consta en su ficha y la API/UI deben
etiquetarlo.

Convenciones globales: tiempos en UTC (ISO-8601); ids globalmente únicos (UUID/texto);
todo mensaje lleva `schema_version` (política de versionado en `07_provenance_versionado.md`);
unidades canónicas: rpm, km/h, %, °C, g/s, kPa, V, grados.

---
### OBDReading

Lectura puntual de un PID OBD-II.

**Clasificación:** RAW · **Produce:** acquisition (edge) / obd-lab · **Consume:** telemetry, storage · **Vive en:** edge (retención corta) → cloud opcional
**Papel en la investigación:** Observación directa del vehículo: base empírica de toda la cadena

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `timestamp` | string | ✔ | — | — |
| `pid` | string | ✔ | Nombre python-OBD del comando, p. ej. 'RPM' | — |
| `value` | number | ✔ | — | — |
| `unit` | string | ✔ | Unidad canónica, p. ej. 'rpm', 'degC', '%' | — |
| `vehicle_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `source` | TransportKind | ✔ | Transporte por el que se capturó | — |

### VehicleTelemetry

Ventana de telemetría normalizada (entrada de la detección).

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `window_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `start` | string | ✔ | — | — |
| `end` | string | ✔ | — | — |
| `sample_rate_hz` | number | ✔ | — | — |
| `readings` | list[OBDReading] | ✔ | — | — |

### DTCRecord

Código de diagnóstico de fallo (modo 03) leído del vehículo.

**Clasificación:** RAW · **Produce:** acquisition · **Consume:** agente · **Vive en:** edge → cloud
**Papel en la investigación:** Síntoma estándar; la detección NO depende de él

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `timestamp` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `code` | string | ✔ | p. ej. 'P0171' | pattern=^[PCBU][0-9A-F]{4}$ |
| `description` | string \| null | opc. | — | — |
| `is_pending` | boolean | opc. | — | — |

### DetectedAnomaly

Anomalía emitida por un detector matemático sobre una ventana.

**Clasificación:** INFERRED · **Produce:** detection (edge) · **Consume:** agente (disparador) · **Vive en:** edge → cloud (prioridad alta)
**Papel en la investigación:** El hecho a explicar; jamás la produce el LLM (separación ML/LLM)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `anomaly_id` | string | ✔ | — | — |
| `window_id` | string | ✔ | — | — |
| `session_id` | string \| null | opc. | Sesión de origen (trazabilidad) | — |
| `inference_id` | string \| null | opc. | ModelInference que la produjo (trazabilidad, ADR-0012) | — |
| `vehicle_id` | string | ✔ | — | — |
| `detected_at` | string | ✔ | — | — |
| `detector` | DetectorKind | ✔ | — | — |
| `model_name` | string \| null | opc. | None para baselines sin modelo | — |
| `model_version` | string \| null | opc. | — | — |
| `score` | number | ✔ | Score del detector; mayor = más anómalo | — |
| `threshold` | number | ✔ | — | — |
| `involved_pids` | list[string] | ✔ | PIDs que más contribuyen a la desviación | — |
| `features` | dict | opc. | Valores de features en la ventana anómala | — |

### DiagnosticHypothesis

Causa candidata generada por el agente (v2: estructurada, con estado y ranking).

**Clasificación:** INFERRED · **Produce:** agente:hypothesize · **Consume:** verify, report, feedback · **Vive en:** edge → cloud
**Papel en la investigación:** Causa candidata con estado y ranking auditables

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `hypothesis_id` | string | ✔ | — | — |
| `case_id` | string \| null | opc. | Caso al que pertenece | — |
| `rank` | integer | opc. | 1 = hipótesis ganadora | minimum=1 |
| `suspected_component` | string | ✔ | Componente sospechoso, p. ej. 'colector admisión' | — |
| `failure_mode` | string | ✔ | Modo de fallo, p. ej. 'vacuum_leak' | — |
| `cause` | string | ✔ | Resumen legible, p. ej. 'fuga de vacío en admisión' | — |
| `mechanism` | string | ✔ | Cómo la causa produce los síntomas observados | — |
| `status` | string | opc. | HypothesisStatus: proposed\|supported\|contradicted\|confirmed\|rejected\|inconclusive | — |
| `verified_against_telemetry` | boolean | opc. | True si el nodo 'verify' contrastó la hipótesis con los datos | — |
| `confidence` | number | ✔ | — | minimum=0.0; maximum=1.0 |

### DiagnosticResult

Diagnóstico final explicable emitido por el agente.

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `diagnostic_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `created_at` | string | ✔ | — | — |
| `trigger_anomaly_id` | string \| null | opc. | — | — |
| `trigger_dtcs` | list[DTCRecord] | opc. | — | — |
| `hypotheses` | list[DiagnosticHypothesis] | ✔ | Ordenadas por confianza (ranking); la primera es la ganadora | — |
| `explanation` | string | ✔ | Explicación en lenguaje natural para el usuario | — |
| `severity` | Severity | ✔ | — | — |
| `recommendations` | list[MaintenanceRecommendation] | opc. | — | — |
| `llm_model` | string | ✔ | Tag del LLM usado, p. ej. 'ollama:qwen2.5:3b' | — |
| `retrieved_doc_ids` | list[string] | opc. | Trazabilidad RAG | — |
| `recalled_case_ids` | list[string] | opc. | Trazabilidad memoria | — |
| `disclaimer` | string | opc. | — | — |

### MaintenanceRecommendation

Acción recomendada al usuario.

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `action` | string | ✔ | — | — |
| `urgency` | Severity | ✔ | — | — |
| `rationale` | string | ✔ | — | — |
| `estimated_risk_if_ignored` | string \| null | opc. | — | — |

### AgentEvent

Traza de ejecución de un nodo del grafo (explicabilidad + evaluación).

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `event_id` | string | ✔ | — | — |
| `diagnostic_id` | string | ✔ | — | — |
| `node` | AgentNode | ✔ | — | — |
| `started_at` | string | ✔ | — | — |
| `ended_at` | string | ✔ | — | — |
| `summary` | string | ✔ | — | — |
| `payload` | dict | opc. | — | — |
| `tokens_in` | integer \| null | opc. | — | — |
| `tokens_out` | integer \| null | opc. | — | — |

### CaseRecord

Caso de la memoria evolutiva (episódica).

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `case_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `created_at` | string | ✔ | — | — |
| `updated_at` | string | ✔ | — | — |
| `symptom_signature` | dict | ✔ | Firma numérica de los síntomas (features de la anomalía) | — |
| `symptom_text` | string | ✔ | Descripción textual (se embebe para similitud) | — |
| `diagnosis` | string | ✔ | — | — |
| `outcome` | string \| null | opc. | Desenlace confirmado, si se conoce | — |
| `reinforcement_count` | integer | opc. | Nº de veces observado | minimum=1 |
| `source_diagnostic_ids` | list[string] | opc. | — | — |

### ModelManifest

Manifiesto que acompaña a todo artefacto de modelo distribuido al edge (ADR-0009).

**Clasificación:** metadatos de modelo · **Produce:** ai-models:export · **Consume:** models_runtime · **Vive en:** cloud (registry) + edge (activo)
**Papel en la investigación:** Gobernanza del ciclo modelo→edge

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `model_id` | string | ✔ | Identificador único del paquete de modelo | — |
| `name` | string | ✔ | — | — |
| `version` | string | ✔ | semver | pattern=^\d+\.\d+\.\d+$ |
| `detector` | DetectorKind | ✔ | — | — |
| `algorithm` | string | ✔ | Descripción del algoritmo, p. ej. 'IsolationForest(n=200)' | — |
| `artifact_filename` | string | ✔ | — | — |
| `artifact_format` | string | opc. | 'onnx' \| 'json-params' | — |
| `artifact_sha256` | string | ✔ | — | — |
| `runtime` | string | opc. | Compatibilidad de runtime requerida en el edge | — |
| `expected_features` | list[string] | ✔ | Orden exacto de entrada del modelo | — |
| `window_size` | integer | ✔ | Muestras por ventana | exclusiveMinimum=0 |
| `window_stride` | integer | opc. | Paso entre ventanas (muestras) | exclusiveMinimum=0 |
| `preprocessing` | string | opc. | 'embedded' (scaler dentro del artefacto) \| 'none' \| descripción | — |
| `decision_threshold` | number | ✔ | — | — |
| `score_direction` | string | opc. | Semántica del score frente al umbral | — |
| `validation_metrics` | dict | opc. | — | — |
| `training_seed` | integer \| null | opc. | — | — |
| `trained_at` | string \| null | opc. | — | — |

### ScenarioSpec

Especificación declarativa de un escenario del laboratorio.

**Clasificación:** configuración experimental · **Produce:** suites obd-lab · **Consume:** generador, evaluación · **Vive en:** repo (YAML)
**Papel en la investigación:** Ground truth y reproducibilidad de escenarios

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `scenario_id` | string | ✔ | — | — |
| `description` | string | ✔ | — | — |
| `category` | string | opc. | 'normal' \| 'known_fault' \| 'held_out' (docs/adr/0010) | — |
| `driving_profile` | string | ✔ | p. ej. 'idle', 'urban', 'highway', 'cold_start' | — |
| `fault` | string \| null | opc. | Modelo de fallo inyectado; None = normal | — |
| `fault_params` | dict | opc. | — | — |
| `fault_start_s` | number \| null | opc. | Inicio del fallo (ground truth) | — |
| `fault_end_s` | number \| null | opc. | Fin del fallo (ground truth) | — |
| `ambient_temp_c` | number | opc. | Temperatura ambiente simulada | — |
| `duration_s` | number | ✔ | — | exclusiveMinimum=0 |
| `sample_rate_hz` | number | opc. | — | exclusiveMinimum=0 |
| `seed` | integer | ✔ | Semilla de reproducibilidad (obligatoria) | — |

### RecordedSession

Cabecera de una sesión grabada (JSONL de OBDReading + esta cabecera).

**Clasificación:** cabecera de archivo · **Produce:** obd-lab · **Consume:** ai-models, replay · **Vive en:** archivos JSONL
**Papel en la investigación:** Serialización de TelemetrySession + inventario del archivo

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `session_id` | string | ✔ | — | — |
| `created_at` | string | ✔ | — | — |
| `origin` | string | ✔ | 'synthetic' \| 'replay:<dataset>' \| 'vehicle' | — |
| `scenario` | ScenarioSpec \| null | opc. | Solo si origin=synthetic | — |
| `vehicle_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `n_readings` | integer | ✔ | — | minimum=0 |
| `pids` | list[string] | ✔ | — | — |

### SyncEnvelope

Sobre idempotente para el push por lotes del outbox del edge.

**Clasificación:** transporte · **Produce:** sync (edge) · **Consume:** cloud · **Vive en:** outbox edge
**Papel en la investigación:** Push idempotente priorizado edge→cloud

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `envelope_id` | string | ✔ | Idempotency key | — |
| `device_id` | string | ✔ | — | — |
| `created_at` | string | ✔ | — | — |
| `entity` | SyncEntity | ✔ | — | — |
| `payload` | dict | ✔ | Mensaje serializado de la entidad | — |

### TelemetrySession

Entidad central de captura: TODO dato de telemetría pertenece a una sesión.

**Clasificación:** contexto (agrupa RAW) · **Produce:** acquisition / obd-lab · **Consume:** todos · **Vive en:** edge + cloud (histórico)
**Papel en la investigación:** Reproducibilidad exacta de experimentos (fuente, semilla, versiones)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `session_id` | string | ✔ | — | — |
| `source` | SessionSource | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `started_at` | string | ✔ | — | — |
| `ended_at` | string \| null | opc. | — | — |
| `sample_rate_hz` | number | ✔ | — | exclusiveMinimum=0 |
| `scenario_id` | string \| null | opc. | Si proviene de obd-lab | — |
| `dataset_id` | string \| null | opc. | Si es replay de dataset público | — |
| `generator_version` | string \| null | opc. | Versión de obd-lab | — |
| `random_seed` | integer \| null | opc. | — | — |
| `software_version` | string | ✔ | Versión del software que capturó (git sha o semver) | — |
| `notes` | string \| null | opc. | — | — |

### TelemetryPoint

Tick NORMALIZED: valores validados en unidades canónicas, alineados por segundo.

**Clasificación:** NORMALIZED · **Produce:** telemetry (edge) · **Consume:** windows, features · **Vive en:** edge (retención media) → cloud resúmenes
**Papel en la investigación:** Esquema canónico: aísla al resto del sistema de la fuente concreta

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `session_id` | string | ✔ | — | — |
| `seq` | integer | ✔ | Índice de tick dentro de la sesión | minimum=0 |
| `timestamp` | string | ✔ | — | — |
| `values` | dict | ✔ | PID → valor en unidad canónica | — |
| `discarded_pids` | list[string] | opc. | Fuera de rango físico | — |

### TelemetryWindow

Ventana DERIVED sobre puntos normalizados (tamaño/stride del manifiesto activo).

**Clasificación:** DERIVED · **Produce:** telemetry (edge) · **Consume:** features, trazabilidad · **Vive en:** edge (retención larga en metadatos)
**Papel en la investigación:** Unidad de análisis temporal (multivariable, requisito de la PI)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `window_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `seq_start` | integer | ✔ | — | — |
| `seq_end` | integer | ✔ | — | — |
| `start` | string | ✔ | — | — |
| `end` | string | ✔ | — | — |
| `size` | integer | ✔ | — | exclusiveMinimum=0 |
| `stride` | integer | ✔ | — | exclusiveMinimum=0 |

### FeatureVector

Vector DERIVED de features canónicas de una ventana (contrato train↔inferencia).

**Clasificación:** DERIVED · **Produce:** detection (edge) / ai-models · **Consume:** modelos ML, verify · **Vive en:** edge → cloud (con anomalías)
**Papel en la investigación:** Contrato train↔inferencia; entrada exacta de los detectores

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `fv_id` | string | ✔ | — | — |
| `window_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `feature_set_version` | string | ✔ | Versión de la definición canónica de features | — |
| `values` | dict | ✔ | — | — |

### ModelInference

Ejecución INFERRED de un modelo ML sobre un FeatureVector (siempre persistida).

**Clasificación:** INFERRED · **Produce:** detection (edge) · **Consume:** anomalías, auditoría · **Vive en:** edge → cloud
**Papel en la investigación:** Toda ejecución de modelo queda auditada (qué modelo/versión/umbral)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `inference_id` | string | ✔ | — | — |
| `fv_id` | string | ✔ | — | — |
| `window_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `model_id` | string | ✔ | — | — |
| `model_name` | string | ✔ | — | — |
| `model_version` | string | ✔ | — | — |
| `score` | number | ✔ | — | — |
| `threshold` | number | ✔ | — | — |
| `flagged` | boolean | ✔ | — | — |
| `latency_ms` | number \| null | opc. | — | — |
| `executed_at` | string | ✔ | — | — |

### DiagnosticCase

Caso de diagnóstico (INFERRED): unidad de trabajo del agente sobre un disparador.

**Clasificación:** INFERRED · **Produce:** agente (edge) · **Consume:** API, móvil, cloud, memoria · **Vive en:** edge → cloud (prioridad alta)
**Papel en la investigación:** Unidad de razonamiento explicable; nunca solo texto

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `case_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `session_id` | string \| null | opc. | — | — |
| `status` | CaseStatus | opc. | — | — |
| `severity` | Severity | opc. | — | — |
| `opened_at` | string | ✔ | — | — |
| `closed_at` | string \| null | opc. | — | — |
| `trigger_anomaly_ids` | list[string] | opc. | — | — |
| `trigger_dtcs` | list[DTCRecord] | opc. | — | — |
| `explanation` | string \| null | opc. | Explicación final para el usuario (nodo report) | — |
| `provenance_id` | string \| null | opc. | — | — |

### DiagnosticEvidence

Pieza de evidencia (a favor/en contra) asociada a una hipótesis o al caso.

**Clasificación:** INFERRED (referencia datos RAW/DERIVED) · **Produce:** agente:verify · **Consume:** report, tribunal/memoria del TFM · **Vive en:** edge → cloud (permanente)
**Papel en la investigación:** Sustento verificable de cada hipótesis (a favor Y en contra)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `evidence_id` | string | ✔ | — | — |
| `case_id` | string | ✔ | — | — |
| `hypothesis_id` | string \| null | opc. | None = evidencia del caso | — |
| `kind` | EvidenceKind | ✔ | — | — |
| `role` | EvidenceRole | ✔ | — | — |
| `reference_id` | string \| null | opc. | Id del objeto referenciado (ventana, chunk, caso, DTC…) | — |
| `statement` | string | ✔ | Afirmación verificable, p. ej. 'total_trim_mean=+8.1%' | — |
| `strength` | number | opc. | — | minimum=0.0; maximum=1.0 |
| `produced_by` | string | ✔ | Nodo/proceso que la produjo, p. ej. 'verify' | — |
| `created_at` | string | ✔ | — | — |

### ProvenanceRecord

Procedencia completa de un artefacto INFERRED (obligatoria para diagnósticos).

**Clasificación:** metadatos · **Produce:** agente · **Consume:** auditoría, experimentos · **Vive en:** edge → cloud (permanente)
**Papel en la investigación:** Responde '¿de dónde salió este diagnóstico?' con un solo objeto navegable

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `provenance_id` | string | ✔ | — | — |
| `subject_kind` | string | ✔ | 'diagnostic_case' \| 'learned_pattern' \| … | — |
| `subject_id` | string | ✔ | — | — |
| `vehicle_id` | string \| null | opc. | — | — |
| `session_ids` | list[string] | opc. | — | — |
| `window_ids` | list[string] | opc. | — | — |
| `fv_ids` | list[string] | opc. | — | — |
| `inference_ids` | list[string] | opc. | — | — |
| `anomaly_ids` | list[string] | opc. | — | — |
| `model_refs` | list[string] | opc. | 'nombre@versión' | — |
| `document_chunk_ids` | list[string] | opc. | RAG utilizados | — |
| `case_memory_ids` | list[string] | opc. | Memoria recuperada | — |
| `agent_run_id` | string \| null | opc. | — | — |
| `prompt_version` | string \| null | opc. | — | — |
| `created_at` | string | ✔ | — | — |

### CaseMemory

Memoria EPISÓDICA: experiencia diagnóstica recuperable por similitud.

**Clasificación:** INFERRED (memoria episódica) · **Produce:** agente:memorize · **Consume:** recall · **Vive en:** edge (local) + cloud (consolidada)
**Papel en la investigación:** Experiencia recuperable; su nivel epistemológico pondera su peso

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `case_memory_id` | string | ✔ | — | — |
| `case_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `vehicle_profile` | dict | opc. | Rasgos del vehículo (combustible, cilindros…) | — |
| `symptom_text` | string | ✔ | Síntomas en texto (base del embedding) | — |
| `symptom_signature` | dict | ✔ | Firma numérica (features clave) | — |
| `temporal_signature` | string \| null | opc. | Descripción compacta de la dinámica (p. ej. 'deriva 5 min') | — |
| `related_dtcs` | list[string] | opc. | — | — |
| `anomaly_detector` | string \| null | opc. | — | — |
| `diagnosis` | string | ✔ | — | — |
| `outcome` | string \| null | opc. | — | — |
| `epistemic_level` | EpistemicLevel | ✔ | — | — |
| `embedding_ref` | string \| null | opc. | Referencia al vector en el índice (no el vector en sí) | — |
| `reinforcement_count` | integer | opc. | — | minimum=1 |
| `created_at` | string | ✔ | — | — |
| `updated_at` | string | ✔ | — | — |

### LearnedPattern

Memoria SEMÁNTICA/EVOLUTIVA: patrón consolidado emergente de múltiples casos.

**Clasificación:** INFERRED (memoria semántica) · **Produce:** consolidación (diseñada, no automática) · **Consume:** recall, investigación · **Vive en:** cloud (maestro) + subset edge
**Papel en la investigación:** LA memoria evolutiva: candidato a 'patrón no documentado' de la PI

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `pattern_id` | string | ✔ | — | — |
| `version` | integer | ✔ | — | minimum=1 |
| `title` | string | ✔ | — | — |
| `description` | string | ✔ | — | — |
| `telemetry_signature` | dict | ✔ | Rango/centroide de features que caracteriza el patrón | — |
| `temporal_signature` | string \| null | opc. | — | — |
| `affected_metrics` | list[string] | ✔ | PIDs/features implicados | — |
| `related_dtc` | list[string] | opc. | — | — |
| `suspected_failure_modes` | list[string] | opc. | — | — |
| `supporting_cases` | list[string] | opc. | case_memory_ids | — |
| `contradicting_cases` | list[string] | opc. | — | — |
| `n_independent_sessions` | integer | opc. | — | minimum=0 |
| `n_distinct_vehicles` | integer | opc. | — | minimum=0 |
| `confidence` | number | opc. | — | minimum=0.0; maximum=1.0 |
| `novelty_score` | number | opc. | Distancia a patrones/documentación existentes (clave para la PI) | minimum=0.0; maximum=1.0 |
| `validation_level` | EpistemicLevel | opc. | — | — |
| `status` | PatternStatus | opc. | — | — |
| `first_seen` | string | ✔ | — | — |
| `last_seen` | string | ✔ | — | — |
| `provenance_id` | string \| null | opc. | — | — |

### PatternRelation

Relación tipada entre patrones (grafo ligero sobre SQL; sin graph-DB por ahora).

**Clasificación:** metadatos · **Produce:** consolidación · **Consume:** análisis · **Vive en:** cloud + subset edge
**Papel en la investigación:** Grafo ligero de relaciones entre patrones

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `relation_id` | string | ✔ | — | — |
| `from_pattern_id` | string | ✔ | — | — |
| `to_pattern_id` | string | ✔ | — | — |
| `kind` | PatternRelationKind | ✔ | — | — |
| `note` | string \| null | opc. | — | — |
| `created_at` | string | ✔ | — | — |

### DiagnosticFeedback

Cierre del lazo: verdad externa sobre un diagnóstico (mide si la memoria mejora).

**Clasificación:** verdad externa · **Produce:** obd-lab (ground truth) / humano · **Consume:** evaluación · **Vive en:** edge → cloud (permanente)
**Papel en la investigación:** Cierra el lazo: mide si la memoria mejora el diagnóstico (H3)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `feedback_id` | string | ✔ | — | — |
| `case_id` | string | ✔ | — | — |
| `kind` | FeedbackKind | ✔ | — | — |
| `verdict` | FeedbackVerdict | ✔ | — | — |
| `true_cause` | string \| null | opc. | Causa real si se conoce | — |
| `detail` | string \| null | opc. | — | — |
| `provided_by` | string | ✔ | 'obd-lab' \| 'dataset' \| persona identificada | — |
| `created_at` | string | ✔ | — | — |

### MaintenanceEvent

Intervención de mantenimiento (permite estudiar anomalía→diagnóstico→reparación→efecto).

**Clasificación:** RAW (evento externo) · **Produce:** usuario/taller · **Consume:** agente, análisis · **Vive en:** edge → cloud
**Papel en la investigación:** Permite estudiar intervención→efecto en telemetría

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `event_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `performed_at` | string | ✔ | — | — |
| `action` | string | ✔ | — | — |
| `component` | string \| null | opc. | — | — |
| `related_case_id` | string \| null | opc. | — | — |
| `notes` | string \| null | opc. | — | — |

### AgentRun

Ejecución completa del grafo sobre un caso. SIN chain-of-thought: solo E/S estructuradas.

**Clasificación:** metadatos de ejecución · **Produce:** agente · **Consume:** auditoría, experimentos · **Vive en:** edge → cloud
**Papel en la investigación:** Working memory trazable; variable memory_mode del experimento H3

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `run_id` | string | ✔ | — | — |
| `case_id` | string | ✔ | — | — |
| `graph_version` | string | ✔ | — | — |
| `llm_model` | string | ✔ | Tag del LLM o 'heuristic' si generador determinista | — |
| `prompt_version` | string | ✔ | — | — |
| `memory_mode` | MemoryMode | ✔ | Variable del experimento de memoria | — |
| `config` | dict | opc. | — | — |
| `started_at` | string | ✔ | — | — |
| `ended_at` | string \| null | opc. | — | — |
| `latency_ms` | number \| null | opc. | — | — |
| `tokens_in` | integer \| null | opc. | — | — |
| `tokens_out` | integer \| null | opc. | — | — |
| `result_status` | string | opc. | 'ok' \| 'error' \| 'no_hypothesis' | — |

### AgentStep

Auditoría de un nodo del grafo: entradas/salidas estructuradas, nunca razonamiento libre.

**Clasificación:** metadatos de ejecución · **Produce:** agente · **Consume:** auditoría · **Vive en:** edge → cloud
**Papel en la investigación:** E/S estructuradas por nodo (sin chain-of-thought)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `step_id` | string | ✔ | — | — |
| `run_id` | string | ✔ | — | — |
| `node` | AgentNode | ✔ | — | — |
| `seq` | integer | ✔ | — | minimum=0 |
| `status` | StepStatus | opc. | — | — |
| `started_at` | string | ✔ | — | — |
| `ended_at` | string \| null | opc. | — | — |
| `inputs` | dict | opc. | — | — |
| `outputs` | dict | opc. | — | — |
| `tools_used` | list[string] | opc. | — | — |
| `error` | string \| null | opc. | — | — |
| `metrics` | dict | opc. | — | — |

### RetrievalEvent

Recuperación auditada (RAG o memoria): qué se pidió, qué volvió, qué se usó.

**Clasificación:** metadatos de ejecución · **Produce:** agente:recall/retrieve · **Consume:** métricas RAG · **Vive en:** edge → cloud
**Papel en la investigación:** Grounding medible: qué participó en cada diagnóstico

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `retrieval_id` | string | ✔ | — | — |
| `run_id` | string | ✔ | — | — |
| `step_id` | string | ✔ | — | — |
| `source` | string | ✔ | 'rag' \| 'episodic_memory' \| 'semantic_memory' | — |
| `query` | string | ✔ | — | — |
| `retrieved_ids` | list[string] | opc. | — | — |
| `scores` | list[number] | opc. | — | — |
| `used_in_hypothesis_ids` | list[string] | opc. | — | — |
| `created_at` | string | ✔ | — | — |

### KnowledgeDocument

Documento del corpus técnico (con licencia registrada en el manifiesto del corpus).

**Clasificación:** corpus · **Produce:** ingesta (con licencia) · **Consume:** retrieve · **Vive en:** cloud (maestro) + cache edge
**Papel en la investigación:** Conocimiento citable del RAG

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `document_id` | string | ✔ | — | — |
| `title` | string | ✔ | — | — |
| `source` | string | ✔ | — | — |
| `license` | string | ✔ | — | — |
| `version` | string | opc. | — | — |
| `checksum` | string \| null | opc. | — | — |
| `ingested_at` | string | ✔ | — | — |

### KnowledgeChunk

Fragmento indexable de un documento (unidad de recuperación y de cita).

**Clasificación:** corpus · **Produce:** ingesta · **Consume:** retrieve · **Vive en:** cloud + cache edge
**Papel en la investigación:** Unidad de recuperación y de cita

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `chunk_id` | string | ✔ | — | — |
| `document_id` | string | ✔ | — | — |
| `seq` | integer | ✔ | — | minimum=0 |
| `text` | string | ✔ | — | — |
| `metadata` | dict | opc. | — | — |
| `embedding_ref` | string \| null | opc. | — | — |

## Enumeraciones

- **SessionSource**: `real_vehicle`, `obd_simulator`, `dataset_replay`, `synthetic_generator`, `bench_test`
- **DataClass**: `raw`, `normalized`, `derived`, `inferred`
- **CaseStatus**: `open`, `closed`
- **HypothesisStatus**: `proposed`, `supported`, `contradicted`, `confirmed`, `rejected`, `inconclusive`
- **EvidenceKind**: `telemetry`, `dtc`, `document`, `case`, `pattern`, `feedback`, `maintenance`
- **EvidenceRole**: `supports`, `contradicts`, `neutral`
- **EpistemicLevel**: `simulated`, `synthetic`, `public_dataset`, `real_unvalidated`, `human_validated`
- **PatternStatus**: `candidate`, `emerging`, `validated`, `rejected`, `superseded`, `retired`
- **PatternRelationKind**: `similar_to`, `contradicts`, `supersedes`, `specialization_of`, `generalization_of`, `co_occurs_with`, `precedes`
- **FeedbackKind**: `simulator_ground_truth`, `dataset_ground_truth`, `human_validation`, `mechanic_validation`, `repair_outcome`
- **FeedbackVerdict**: `correct`, `partially_correct`, `incorrect`, `unknown`
- **MemoryMode**: `none`, `episodic`, `episodic_semantic`
- **StepStatus**: `ok`, `error`, `skipped`
- **Severity**: `info`, `low`, `medium`, `high`, `critical`
- **DetectorKind**: `zscore`, `isolation_forest`, `lof`, `ocsvm`, `autoencoder`
- **TransportKind**: `serial`, `tcp`, `bluetooth-rfcomm`
- **AgentNode**: `triage`, `recall`, `retrieve`, `hypothesize`, `verify`, `report`, `memorize`
- **SyncEntity**: `telemetry_window`, `anomaly`, `diagnostic`, `case`
