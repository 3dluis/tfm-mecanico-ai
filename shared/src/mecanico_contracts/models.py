"""Contratos v1 del sistema Mecánico IA (ADR-0007).

Convenciones:
- Todos los mensajes heredan de ``ContractBase`` (inmutables, con ``schema_version``).
- Tiempos en UTC (``datetime`` timezone-aware); identificadores como ``str`` (UUID en producción).
- Solo cambios aditivos retro-compatibles dentro de una misma ``SCHEMA_VERSION``.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mecanico_contracts.data_enums import AnomalyScope
from mecanico_contracts.enums import (
    AgentNode,
    DetectorKind,
    Severity,
    SyncEntity,
    TransportKind,
)

SCHEMA_VERSION = 2


class ContractBase(BaseModel):
    """Base común: inmutable, validación estricta, versión de esquema."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Telemetría
# ---------------------------------------------------------------------------


class OBDReading(ContractBase):
    """Lectura puntual de un PID OBD-II."""

    timestamp: datetime
    pid: str = Field(description="Nombre python-OBD del comando, p. ej. 'RPM'")
    value: float
    unit: str = Field(description="Unidad canónica, p. ej. 'rpm', 'degC', '%'")
    vehicle_id: str
    device_id: str
    source: TransportKind = Field(description="Transporte por el que se capturó")


class VehicleTelemetry(ContractBase):
    """Ventana de telemetría normalizada (entrada de la detección)."""

    window_id: str
    vehicle_id: str
    device_id: str
    start: datetime
    end: datetime
    sample_rate_hz: float
    readings: list[OBDReading]


class DTCRecord(ContractBase):
    """Código de diagnóstico de fallo (modo 03) leído del vehículo."""

    timestamp: datetime
    vehicle_id: str
    code: str = Field(pattern=r"^[PCBU][0-9A-F]{4}$", description="p. ej. 'P0171'")
    description: str | None = None
    is_pending: bool = False


# ---------------------------------------------------------------------------
# Detección (ML — nunca producida por el LLM; ADR-0009 §5)
# ---------------------------------------------------------------------------


class DetectedAnomaly(ContractBase):
    """Anomalía emitida por un detector matemático sobre una ventana."""

    anomaly_id: str
    window_id: str | None = Field(
        default=None,
        description="Ventana origen; obligatoria si anomaly_scope=WINDOW (F3), opcional en F6",
    )
    event_id: str | None = Field(
        default=None, description="VehicleEvent origen si anomaly_scope=EVENT (F6, ADR-0021)"
    )
    baseline_id: str | None = Field(
        default=None, description="EventBaseline contra la que se evaluó (anomalías contextuales)"
    )
    anomaly_scope: AnomalyScope = Field(
        default=AnomalyScope.WINDOW,
        description="Ámbito: point|window|event|session|cross_event (default = F3)",
    )
    session_id: str | None = Field(default=None, description="Sesión de origen (trazabilidad)")
    inference_id: str | None = Field(
        default=None, description="ModelInference que la produjo (trazabilidad, ADR-0012)"
    )
    vehicle_id: str
    detected_at: datetime
    detector: DetectorKind
    model_name: str | None = Field(default=None, description="None para baselines sin modelo")
    model_version: str | None = None
    score: float = Field(description="Score del detector; mayor = más anómalo")
    threshold: float
    involved_pids: list[str] = Field(description="PIDs que más contribuyen a la desviación")
    features: dict[str, float] = Field(
        default_factory=dict, description="Valores de features en la ventana anómala"
    )

    @model_validator(mode="after")
    def _scope_requires_anchor(self) -> "DetectedAnomaly":
        """El ámbito exige su referencia: WINDOW→window_id, EVENT→event_id (ADR-0021)."""
        if self.anomaly_scope is AnomalyScope.WINDOW and self.window_id is None:
            msg = "anomaly_scope=window requiere window_id (compatibilidad F3)"
            raise ValueError(msg)
        if self.anomaly_scope is AnomalyScope.EVENT and self.event_id is None:
            msg = "anomaly_scope=event requiere event_id"
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Razonamiento (LLM/agente)
# ---------------------------------------------------------------------------


class DiagnosticHypothesis(ContractBase):
    """Causa candidata generada por el agente (v2: estructurada, con estado y ranking).

    Las evidencias NO viven aquí: son entidades ``DiagnosticEvidence`` (data_model) que
    referencian a la hipótesis, con rol supports/contradicts (ADR-0012).
    """

    hypothesis_id: str
    case_id: str | None = Field(default=None, description="Caso al que pertenece")
    rank: int = Field(ge=1, default=1, description="1 = hipótesis ganadora")
    suspected_component: str = Field(
        description="Componente sospechoso, p. ej. 'colector admisión'"
    )
    failure_mode: str = Field(description="Modo de fallo, p. ej. 'vacuum_leak'")
    cause: str = Field(description="Resumen legible, p. ej. 'fuga de vacío en admisión'")
    mechanism: str = Field(description="Cómo la causa produce los síntomas observados")
    status: str = Field(
        default="proposed",
        description=(
            "HypothesisStatus: proposed|supported|contradicted|confirmed|rejected|inconclusive"
        ),
    )
    verified_against_telemetry: bool = Field(
        default=False, description="True si el nodo 'verify' contrastó la hipótesis con los datos"
    )
    confidence: float = Field(ge=0.0, le=1.0)


class MaintenanceRecommendation(ContractBase):
    """Acción recomendada al usuario."""

    action: str
    urgency: Severity
    rationale: str
    estimated_risk_if_ignored: str | None = None


class DiagnosticResult(ContractBase):
    """Diagnóstico final explicable emitido por el agente."""

    diagnostic_id: str
    vehicle_id: str
    created_at: datetime
    trigger_anomaly_id: str | None = None
    trigger_dtcs: list[DTCRecord] = Field(default_factory=list)
    hypotheses: list[DiagnosticHypothesis] = Field(
        description="Ordenadas por confianza (ranking); la primera es la ganadora"
    )
    explanation: str = Field(description="Explicación en lenguaje natural para el usuario")
    severity: Severity
    recommendations: list[MaintenanceRecommendation] = Field(default_factory=list)
    llm_model: str = Field(description="Tag del LLM usado, p. ej. 'ollama:qwen2.5:3b'")
    retrieved_doc_ids: list[str] = Field(default_factory=list, description="Trazabilidad RAG")
    recalled_case_ids: list[str] = Field(default_factory=list, description="Trazabilidad memoria")
    disclaimer: str = "Prototipo de investigación: no sustituye el diagnóstico profesional."


class AgentEvent(ContractBase):
    """Traza de ejecución de un nodo del grafo (explicabilidad + evaluación)."""

    event_id: str
    diagnostic_id: str
    node: AgentNode
    started_at: datetime
    ended_at: datetime
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    tokens_in: int | None = None
    tokens_out: int | None = None


class CaseRecord(ContractBase):
    """Caso de la memoria evolutiva (episódica)."""

    case_id: str
    vehicle_id: str
    created_at: datetime
    updated_at: datetime
    symptom_signature: dict[str, float] = Field(
        description="Firma numérica de los síntomas (features de la anomalía)"
    )
    symptom_text: str = Field(description="Descripción textual (se embebe para similitud)")
    diagnosis: str
    outcome: str | None = Field(default=None, description="Desenlace confirmado, si se conoce")
    reinforcement_count: int = Field(default=1, ge=1, description="Nº de veces observado")
    source_diagnostic_ids: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Modelos ML (ciclo de vida, ADR-0009)
# ---------------------------------------------------------------------------


class ModelManifest(ContractBase):
    """Manifiesto que acompaña a todo artefacto de modelo distribuido al edge (ADR-0009)."""

    model_id: str = Field(description="Identificador único del paquete de modelo")
    name: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", description="semver")
    detector: DetectorKind
    algorithm: str = Field(description="Descripción del algoritmo, p. ej. 'IsolationForest(n=200)'")
    artifact_filename: str
    artifact_format: str = Field(default="onnx", description="'onnx' | 'json-params'")
    artifact_sha256: str
    runtime: str = Field(
        default="onnxruntime>=1.17", description="Compatibilidad de runtime requerida en el edge"
    )
    expected_features: list[str] = Field(description="Orden exacto de entrada del modelo")
    window_size: int = Field(gt=0, description="Muestras por ventana")
    window_stride: int = Field(gt=0, default=30, description="Paso entre ventanas (muestras)")
    preprocessing: str = Field(
        default="embedded",
        description="'embedded' (scaler dentro del artefacto) | 'none' | descripción",
    )
    decision_threshold: float
    score_direction: str = Field(
        default="higher_is_anomalous", description="Semántica del score frente al umbral"
    )
    validation_metrics: dict[str, float] = Field(default_factory=dict)
    training_seed: int | None = None
    trained_at: datetime | None = None


# ---------------------------------------------------------------------------
# obd-lab (escenarios y sesiones)
# ---------------------------------------------------------------------------


class ScenarioSpec(ContractBase):
    """Especificación declarativa de un escenario del laboratorio."""

    scenario_id: str
    description: str
    category: str = Field(
        default="normal",
        description="'normal' | 'known_fault' | 'held_out' (docs/adr/0010)",
    )
    driving_profile: str = Field(description="p. ej. 'idle', 'urban', 'highway', 'cold_start'")
    fault: str | None = Field(default=None, description="Modelo de fallo inyectado; None = normal")
    fault_params: dict[str, float] = Field(default_factory=dict)
    fault_start_s: float | None = Field(default=None, description="Inicio del fallo (ground truth)")
    fault_end_s: float | None = Field(default=None, description="Fin del fallo (ground truth)")
    ambient_temp_c: float = Field(default=22.0, description="Temperatura ambiente simulada")
    duration_s: float = Field(gt=0)
    sample_rate_hz: float = Field(gt=0, default=1.0)
    seed: int = Field(description="Semilla de reproducibilidad (obligatoria)")


class RecordedSession(ContractBase):
    """Cabecera de una sesión grabada (JSONL de OBDReading + esta cabecera).

    Formato común para sesiones sintéticas (obd-lab) y datasets reales
    reproducidos — los consumidores no distinguen la fuente (docs/09 §9.3.1).
    """

    session_id: str
    created_at: datetime
    origin: str = Field(description="'synthetic' | 'replay:<dataset>' | 'vehicle'")
    scenario: ScenarioSpec | None = Field(default=None, description="Solo si origin=synthetic")
    vehicle_id: str
    device_id: str
    n_readings: int = Field(ge=0)
    pids: list[str]


# ---------------------------------------------------------------------------
# Sincronización edge→cloud (patrón outbox)
# ---------------------------------------------------------------------------


class SyncEnvelope(ContractBase):
    """Sobre idempotente para el push por lotes del outbox del edge."""

    envelope_id: str = Field(description="Idempotency key")
    device_id: str
    created_at: datetime
    entity: SyncEntity
    payload: dict[str, Any] = Field(description="Mensaje serializado de la entidad")
