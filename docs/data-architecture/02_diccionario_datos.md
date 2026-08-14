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
| `window_id` | string \| null | opc. | Ventana origen; obligatoria si anomaly_scope=WINDOW (F3), opcional en F6 | — |
| `event_id` | string \| null | opc. | VehicleEvent origen si anomaly_scope=EVENT (F6, ADR-0021) | — |
| `baseline_id` | string \| null | opc. | EventBaseline contra la que se evaluó (anomalías contextuales) | — |
| `anomaly_scope` | AnomalyScope | opc. | Ámbito: point\|window\|event\|session\|cross_event (default = F3) | — |
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
| `model_type` | string | opc. | 'ml' \| 'llm' \| 'embedding' (taxonomía docs/models/01) | — |
| `preprocessing_version` | string \| null | opc. | Versión del preprocesado (complementa 'preprocessing') | — |
| `runtime_version` | string \| null | opc. | Versión concreta del runtime validada, p. ej. '1.17.3' | — |
| `minimum_hardware` | string \| null | opc. | Requisito mínimo, p. ej. 'arm64, 512MB RAM' | — |
| `training_run_id` | string \| null | opc. | TrainingRun que produjo el artefacto (provenance) | — |
| `quantization` | string \| null | opc. | p. ej. 'Q4_K_M' | — |
| `context_window` | integer \| null | opc. | — | — |
| `tokenizer` | string \| null | opc. | — | — |
| `prompt_compatibility` | string \| null | opc. | Versión de plantillas de prompt validadas con el modelo | — |
| `tool_schema_version` | string \| null | opc. | Versión del esquema de herramientas soportado | — |

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
| `seed` | integer | ✔ | Semilla del COMPORTAMIENTO NORMAL del vehículo (vehicle_behavior_seed). Obligatoria y reproducible. | — |
| `anomaly_seed` | integer \| null | opc. | Semilla INDEPENDIENTE de la inyección de anomalías (anomaly_injection_seed, ADR-0034). Si es None se mantiene el comportamiento heredado v1 —la anomalía comparte el generador aleatorio del motor— para que los datasets ya generados sigan reproduciéndose byte a byte. Si se indica, la anomalía usa su propio generador y NO altera la trayectoria normal fuera de la región intervenida. | — |

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
| `related_event_ids` | list[string] | opc. | VehicleEvents en los que se manifestó el problema (F6, ADR-0021) | — |
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
| `event_types` | list[string] | opc. | Tipos de evento donde el patrón se manifiesta (taxonomía F6, ADR-0021) | — |
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

### VehicleEvent

Evento vehicular segmentado (unidad formal de análisis; jerárquico).

**Clasificación:** INFERRED (event_class marca observed/inferred/estimated) · **Produce:** event detector (edge) / obd-lab (ground truth) · **Consume:** event features, baselines, agente, análisis · **Vive en:** edge → cloud (metadatos; la telemetría se referencia, no se duplica)
**Papel en la investigación:** Unidad formal de análisis contextual (F6): segmenta sin perder el RAW

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `event_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `event_type` | string | ✔ | Tipo de la taxonomía v1 (EVENT_TAXONOMY) | — |
| `event_subtype` | string \| null | opc. | — | — |
| `event_class` | EventClass | ✔ | observed \| inferred \| estimated | — |
| `taxonomy_version` | integer | opc. | — | — |
| `parent_event_id` | string \| null | opc. | Jerarquía (TRIP→evento→micro) | — |
| `start_time` | string | ✔ | — | — |
| `end_time` | string \| null | opc. | None = evento puntual/abierto | — |
| `duration_ms` | integer \| null | opc. | — | — |
| `seq_start` | integer \| null | opc. | Ref. a TelemetryPoint.seq inicial | — |
| `seq_end` | integer \| null | opc. | — | — |
| `confidence` | number | opc. | — | minimum=0.0; maximum=1.0 |
| `detection_method` | string | ✔ | 'rule:v1' \| 'state_machine:v1' \| 'hmm:…' | — |
| `detector_version` | string | ✔ | — | — |
| `source_sensors` | list[string] | opc. | obd\|imu\|gps | — |
| `evidence` | list[string] | opc. | Afirmaciones verificables que sustentan el evento | — |
| `metadata` | dict | opc. | — | — |
| `created_at` | string | ✔ | — | — |

### EventFeatureVector

Features DERIVED de un evento completo (comparable dentro de su contexto).

**Clasificación:** DERIVED · **Produce:** event features (edge) · **Consume:** baselines, detección contextual, comparación de eventos · **Vive en:** edge → cloud
**Papel en la investigación:** Hace comparables eventos equivalentes (misma context_signature)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `efv_id` | string | ✔ | — | — |
| `event_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `event_type` | string | ✔ | — | — |
| `context_signature` | string | ✔ | Firma canónica de comparabilidad, p. ej. 'ACCELERATION\|40-80\|warm\|d4-8s' | — |
| `feature_schema_version` | string | ✔ | — | — |
| `preprocessing_version` | string | ✔ | — | — |
| `detector_version` | string | ✔ | — | — |
| `values` | dict | ✔ | — | — |

### EventBaseline

Normalidad acumulada de UN vehículo para UN contexto de evento (INFERRED).

**Clasificación:** INFERRED (normalidad acumulada) · **Produce:** baseline builder (edge) · **Consume:** detección contextual, agente · **Vive en:** edge (por vehículo) → cloud (respaldo)
**Papel en la investigación:** 'Lo normal PARA ESTE vehículo en ESTE contexto' (H6/PI.5)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `baseline_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `event_type` | string | ✔ | — | — |
| `context_signature` | string | ✔ | — | — |
| `sample_count` | integer | ✔ | — | minimum=0 |
| `feature_distribution` | dict | ✔ | feature → {mean, std, p05, p50, p95} | — |
| `centroid` | dict | opc. | — | — |
| `feature_schema_version` | string | ✔ | — | — |
| `first_seen` | string | ✔ | — | — |
| `last_updated` | string | ✔ | — | — |
| `version` | integer | opc. | — | minimum=1 |
| `confidence` | number | opc. | — | minimum=0.0; maximum=1.0 |

### TrainingRun

Un entrenamiento/ajuste concreto: reproducible por sí solo (docs/models/05).

**Clasificación:** metadatos de experimentación · **Produce:** ai-models (entrenamiento) · **Consume:** registry, provenance, memoria del TFM · **Vive en:** ai-models (JSON) → cloud futuro
**Papel en la investigación:** Un entrenamiento reproducible: datos+config+seed+commit+métricas (F7)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `training_run_id` | string | ✔ | — | — |
| `experiment_id` | string \| null | opc. | ModelExperiment al que aporta | — |
| `model_id` | string | ✔ | — | — |
| `model_version` | string | ✔ | — | — |
| `model_type` | ModelType | opc. | — | — |
| `dataset_id` | string | ✔ | — | — |
| `dataset_version` | string | ✔ | — | — |
| `dataset_checksum` | string \| null | opc. | — | — |
| `split_version` | string \| null | opc. | Versión del split train/val/test (linaje, docs/models/06) | — |
| `feature_schema_version` | string \| null | opc. | — | — |
| `preprocessing_version` | string \| null | opc. | — | — |
| `hyperparameters` | dict | opc. | — | — |
| `seed` | integer \| null | opc. | — | — |
| `git_commit` | string | ✔ | — | — |
| `python_version` | string \| null | opc. | — | — |
| `started_at` | string | ✔ | — | — |
| `completed_at` | string \| null | opc. | — | — |
| `hardware` | string | ✔ | Dónde se entrenó: 'sandbox-x86', 'mac-arm64', 'rpi5'… | — |
| `metrics` | dict | opc. | — | — |
| `artifact_uri` | string \| null | opc. | — | — |
| `artifact_checksum` | string \| null | opc. | — | — |
| `status` | string | opc. | 'ok' \| 'failed' \| 'running' | — |

### ModelExperiment

Comparación científicamente válida: varios TrainingRuns con dataset/split/features/

**Clasificación:** metadatos de experimentación · **Produce:** ai-models (experimentos) · **Consume:** informes de comparación, selección de modelos · **Vive en:** ai-models (JSON+YAML) → cloud futuro
**Papel en la investigación:** Comparación válida: mismos datos/split/features/protocolo (F7)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `experiment_id` | string | ✔ | p. ej. 'EXP-ANOM-001' | — |
| `title` | string | ✔ | — | — |
| `objective` | string | ✔ | Pregunta experimental que responde | — |
| `dataset_id` | string | ✔ | — | — |
| `dataset_version` | string | ✔ | — | — |
| `split_version` | string \| null | opc. | — | — |
| `feature_schema_version` | string \| null | opc. | — | — |
| `evaluation_protocol` | string | ✔ | Referencia al protocolo pre-registrado, p. ej. 'ADR-0011' | — |
| `study_type` | string \| null | opc. | 'exploratory' \| 'confirmatory' (F10): los exploratorios informan el diseño; solo los confirmatorios con protocolo CONGELADO antes de ejecutar sirven como evidencia confirmatoria | — |
| `config_uri` | string \| null | opc. | Config declarativa del experimento (YAML) | — |
| `training_run_ids` | list[string] | opc. | — | — |
| `conclusion` | string \| null | opc. | Interpretación y decisión | — |
| `selected_model_id` | string \| null | opc. | — | — |
| `report_uri` | string \| null | opc. | Informe de comparación (docs/models/comparisons/) | — |
| `created_at` | string | ✔ | — | — |

### ModelEvaluation

Evaluación de una versión concreta bajo un protocolo (offline o edge).

**Clasificación:** metadatos de experimentación · **Produce:** ai-models / validación edge · **Consume:** registry, model cards, matriz hardware · **Vive en:** ai-models (JSON)
**Papel en la investigación:** Evaluación bajo protocolo con hardware explícito (interpreta latencias)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `evaluation_id` | string | ✔ | — | — |
| `model_id` | string | ✔ | — | — |
| `model_version` | string | ✔ | — | — |
| `dataset_id` | string | ✔ | — | — |
| `dataset_version` | string | ✔ | — | — |
| `protocol` | string | ✔ | — | — |
| `metrics` | dict | opc. | — | — |
| `per_scenario_metrics` | dict | opc. | — | — |
| `hardware` | string | ✔ | Dónde se evaluó (interpreta latencias) | — |
| `evaluated_at` | string | ✔ | — | — |
| `notes` | string \| null | opc. | — | — |

### ModelRegistryEntry

Entrada del catálogo lógico común ML/LLM/EMBEDDING (docs/models/08).

**Clasificación:** catálogo · **Produce:** ai-models:registry · **Consume:** diagnostic-agent (ModelRouter), despliegue · **Vive en:** ai-models/registry/ (filesystem+JSON) → cloud futuro
**Papel en la investigación:** Catálogo común ML/LLM/embedding con ciclo de vida y capacidades (F7)

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `model_id` | string | ✔ | — | — |
| `name` | string | ✔ | — | — |
| `model_family` | string | ✔ | p. ej. 'lof', 'qwen2.5', 'all-MiniLM' | — |
| `model_type` | ModelType | ✔ | — | — |
| `version` | string | ✔ | Versión del ARTEFACTO entrenado (≠ algoritmo/features) | — |
| `algorithm_version` | string \| null | opc. | Versión de la implementación del algoritmo | — |
| `capabilities` | list[ModelCapability] | opc. | — | — |
| `status` | ModelStatus | opc. | — | — |
| `artifact_format` | string \| null | opc. | 'onnx' \| 'gguf' \| … | — |
| `artifact_uri` | string \| null | opc. | — | — |
| `checksum` | string \| null | opc. | — | — |
| `manifest_uri` | string \| null | opc. | ModelManifest portable asociado | — |
| `model_card_uri` | string \| null | opc. | docs/models/model-cards/… | — |
| `training_run_id` | string \| null | opc. | — | — |
| `created_at` | string | ✔ | — | — |
| `validated_at` | string \| null | opc. | — | — |
| `edge_compatible` | boolean \| null | opc. | None = no probado aún (nunca se asume) | — |
| `hardware_validation` | list[HardwareValidation] | opc. | — | — |
| `notes` | string \| null | opc. | — | — |

### ModelDeployment

Estado de despliegue en UN dispositivo edge, con rollback (docs/models/10 §rollback).

**Clasificación:** estado de despliegue · **Produce:** despliegue manual (TFM) · **Consume:** edge runtime, rollback · **Vive en:** edge (activo) + registro
**Papel en la investigación:** active/previous por dispositivo: rollback posible aunque sea manual

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `deployment_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `active_model_id` | string | ✔ | — | — |
| `active_model_version` | string | ✔ | — | — |
| `previous_model_id` | string \| null | opc. | Versión a la que volver si la activa falla | — |
| `previous_model_version` | string \| null | opc. | — | — |
| `activated_at` | string | ✔ | — | — |
| `activated_by` | string | opc. | 'manual' en el TFM (ADR-0022) | — |
| `rollback_of` | string \| null | opc. | deployment_id que este despliegue revierte | — |
| `notes` | string \| null | opc. | — | — |

### HardwareValidation

Celda de la matriz de compatibilidad hardware (docs/models/10 §matriz).

**Clasificación:** metadatos de validación · **Produce:** validación por objetivo hardware · **Consume:** registry, decisión EDGE_APPROVED · **Vive en:** registry (embebido)
**Papel en la investigación:** Matriz mac/arm64/RPi: EDGE_APPROVED nunca solo por métricas offline

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `target` | string | ✔ | 'mac-dev' \| 'arm64-container' \| 'rpi5' | — |
| `status` | HardwareValidationStatus | opc. | — | — |
| `metrics` | dict | opc. | RAM MB, latencia ms, tokens/s, temperatura… | — |
| `validated_at` | string \| null | opc. | — | — |
| `notes` | string \| null | opc. | — | — |

### VehicleTelemetrySnapshot

Estado multivariable del vehículo alineado a un instante canónico (WIDE).

**Clasificación:** NORMALIZED WIDE / TIME-ALIGNED (ADR-0025; jamás INFERRED) · **Produce:** snapshot builder (edge) desde TelemetryPoint · **Consume:** ML, Event Intelligence, análisis longitudinal, visualización · **Vive en:** edge (retención media) → cloud (particionado por timestamp)
**Papel en la investigación:** Estado multivariable alineado por instante: elimina el pivot long→wide de cada consumidor; NULL≠0 con quality_flags

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `snapshot_id` | string | ✔ | — | — |
| `vehicle_id` | string | ✔ | — | — |
| `device_id` | string | ✔ | — | — |
| `session_id` | string | ✔ | — | — |
| `trip_id` | string \| null | opc. | VehicleEvent TRIP contenedor | — |
| `timestamp_utc` | string | ✔ | Instante canónico (rejilla, UTC) | — |
| `sequence_number` | integer | ✔ | Índice en la rejilla de la sesión | minimum=0 |
| `snapshot_interval_ms` | integer | ✔ | Paso de la rejilla (1000 = 1 Hz) | exclusiveMinimum=0 |
| `synchronization_version` | string | opc. | Política de alineación aplicada (ADR-0026) | — |
| `primary_event_id` | string \| null | opc. | Evento hoja más específico activo en el instante | — |
| `primary_event_type` | string \| null | opc. | — | — |
| `vehicle_state` | string \| null | opc. | Estado de la máquina de estados (OFF/IDLE/MOVING…) | — |
| `rpm` | number \| null | opc. | — | — |
| `vehicle_speed` | number \| null | opc. | km/h | — |
| `throttle_position` | number \| null | opc. | % | — |
| `engine_load` | number \| null | opc. | % | — |
| `coolant_temperature` | number \| null | opc. | °C | — |
| `intake_air_temperature` | number \| null | opc. | °C | — |
| `maf` | number \| null | opc. | g/s | — |
| `map_kpa` | number \| null | opc. | kPa (nombre 'map' es builtin) | — |
| `stft_bank1` | number \| null | opc. | % | — |
| `ltft_bank1` | number \| null | opc. | % | — |
| `stft_bank2` | number \| null | opc. | % (motores 2 bancos) | — |
| `ltft_bank2` | number \| null | opc. | — | — |
| `fuel_pressure` | number \| null | opc. | kPa | — |
| `fuel_level` | number \| null | opc. | % | — |
| `timing_advance` | number \| null | opc. | ° BTDC | — |
| `battery_voltage` | number \| null | opc. | V (PID 42) | — |
| `o2_sensor_1` | number \| null | opc. | V (B1S1) | — |
| `o2_sensor_2` | number \| null | opc. | V (B1S2) | — |
| `commanded_equivalence_ratio` | number \| null | opc. | λ (PID 44) | — |
| `active_dtc_count` | integer \| null | opc. | — | — |
| `acceleration_x` | number \| null | opc. | m/s² | — |
| `acceleration_y` | number \| null | opc. | — | — |
| `acceleration_z` | number \| null | opc. | — | — |
| `gyro_x` | number \| null | opc. | °/s | — |
| `gyro_y` | number \| null | opc. | — | — |
| `gyro_z` | number \| null | opc. | — | — |
| `gps_speed` | number \| null | opc. | km/h | — |
| `gps_heading` | number \| null | opc. | ° | — |
| `quality_score` | number | ✔ | señales medidas / señales esperadas en el ciclo | minimum=0.0; maximum=1.0 |
| `missing_metric_count` | integer | opc. | — | minimum=0 |
| `quality_flags` | dict | opc. | SOLO señales ≠ measured (compacto); vacío = todo medido | — |
| `created_at` | string | ✔ | — | — |

### SnapshotEventLink

Pertenencia N:M snapshot↔evento SIN duplicar snapshots (F11 §11).

**Clasificación:** relación N:M · **Produce:** snapshot builder / event linker · **Consume:** consultas por evento · **Vive en:** edge → cloud
**Papel en la investigación:** Pertenencia simultánea a varios eventos sin duplicar snapshots

| Campo | Tipo | Req. | Descripción | Restricciones |
|---|---|---|---|---|
| `schema_version` | integer | opc. | — | — |
| `snapshot_id` | string | ✔ | — | — |
| `event_id` | string | ✔ | — | — |
| `event_type` | string | ✔ | Denormalizado para filtrar sin join | — |

## Enumeraciones

- **SessionSource**: `real_vehicle`, `obd_simulator`, `dataset_replay`, `synthetic_generator`, `bench_test`
- **DataClass**: `raw`, `normalized`, `derived`, `inferred`
- **EventClass**: `observed`, `inferred`, `estimated`
- **AnomalyScope**: `point`, `window`, `event`, `session`, `cross_event`
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
- **ModelType**: `ml`, `llm`, `embedding`
- **ModelStatus**: `experimental`, `candidate`, `validated`, `edge_approved`, `deployed`, `rejected`, `superseded`, `retired`
- **ModelCapability**: `triage`, `hypothesis_generation`, `critique`, `reporting`, `tool_selection`, `embeddings`, `anomaly_detection`, `event_detection`
- **HardwareValidationStatus**: `compatible`, `not_tested`, `failed`, `approved`
- **SignalQuality**: `measured`, `stale`, `not_supported`, `not_polled`, `timeout`, `missing`, `invalid`
- **Severity**: `info`, `low`, `medium`, `high`, `critical`
- **DetectorKind**: `zscore`, `isolation_forest`, `lof`, `ocsvm`, `autoencoder`
- **TransportKind**: `serial`, `tcp`, `bluetooth-rfcomm`
- **AgentNode**: `triage`, `recall`, `retrieve`, `hypothesize`, `verify`, `report`, `memorize`
- **SyncEntity**: `telemetry_window`, `anomaly`, `diagnostic`, `case`
