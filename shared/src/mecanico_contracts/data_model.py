"""Modelo de datos v2 del sistema (arquitectura de datos; ADR-0012 y ADR-0013).

Cadena de telemetría trazable (cada eslabón referencia al anterior por id):

    TelemetrySession → OBDObservation(=OBDReading) → TelemetryPoint → TelemetryWindow
        → FeatureVector → ModelInference → DetectedAnomaly

Diagnóstico estructurado: DiagnosticCase → DiagnosticHypothesis → DiagnosticEvidence.
Memoria en tres niveles (working=AgentRun/AgentStep; episódica=CaseMemory;
semántica/evolutiva=LearnedPattern+PatternRelation). Procedencia: ProvenanceRecord.

Documentación navegable: ``docs/data-architecture/`` (el diccionario se AUTOGENERA de
estos modelos: ``python -m mecanico_contracts.gen_data_dictionary``).
"""

from datetime import datetime
from typing import Any

from pydantic import Field

from mecanico_contracts.data_enums import (
    CaseStatus,
    EpistemicLevel,
    EvidenceKind,
    EvidenceRole,
    ExplanationDecision,
    FeedbackKind,
    FeedbackVerdict,
    MemoryMode,
    PatternRelationKind,
    PatternStatus,
    SessionSource,
    StepStatus,
)
from mecanico_contracts.enums import AgentNode, Severity
from mecanico_contracts.models import ContractBase, DTCRecord

# ---------------------------------------------------------------------------
# Telemetría (cadena trazable)
# ---------------------------------------------------------------------------


class TelemetrySession(ContractBase):
    """Entidad central de captura: TODO dato de telemetría pertenece a una sesión.

    Registra el origen y las condiciones exactas para reproducir el experimento.
    Clasificación: contexto (agrupa datos RAW).
    """

    session_id: str
    source: SessionSource
    vehicle_id: str
    device_id: str
    started_at: datetime
    ended_at: datetime | None = None
    sample_rate_hz: float = Field(gt=0)
    scenario_id: str | None = Field(default=None, description="Si proviene de obd-lab")
    dataset_id: str | None = Field(default=None, description="Si es replay de dataset público")
    generator_version: str | None = Field(default=None, description="Versión de obd-lab")
    random_seed: int | None = None
    software_version: str = Field(description="Versión del software que capturó (git sha o semver)")
    notes: str | None = None


class TelemetryPoint(ContractBase):
    """Tick NORMALIZED: valores validados en unidades canónicas, alineados por segundo.

    Se construye desde las observaciones RAW (OBDReading) tras validación de rangos;
    conserva qué PIDs se descartaron para no confundir pérdida con normalidad.
    """

    session_id: str
    seq: int = Field(ge=0, description="Índice de tick dentro de la sesión")
    timestamp: datetime
    values: dict[str, float] = Field(description="PID → valor en unidad canónica")
    discarded_pids: list[str] = Field(default_factory=list, description="Fuera de rango físico")


class TelemetryWindow(ContractBase):
    """Ventana DERIVED sobre puntos normalizados (tamaño/stride del manifiesto activo)."""

    window_id: str
    session_id: str
    seq_start: int
    seq_end: int
    start: datetime
    end: datetime
    size: int = Field(gt=0)
    stride: int = Field(gt=0)


class FeatureVector(ContractBase):
    """Vector DERIVED de features canónicas de una ventana (contrato train↔inferencia)."""

    fv_id: str
    window_id: str
    session_id: str
    feature_set_version: str = Field(description="Versión de la definición canónica de features")
    values: dict[str, float]


class ModelInference(ContractBase):
    """Ejecución INFERRED de un modelo ML sobre un FeatureVector (siempre persistida)."""

    inference_id: str
    fv_id: str
    window_id: str
    session_id: str
    model_id: str
    model_name: str
    model_version: str
    score: float
    threshold: float
    flagged: bool
    latency_ms: float | None = None
    executed_at: datetime


# ---------------------------------------------------------------------------
# Diagnóstico estructurado
# ---------------------------------------------------------------------------


class DiagnosticCase(ContractBase):
    """Caso de diagnóstico (INFERRED): unidad de trabajo del agente sobre un disparador."""

    case_id: str
    vehicle_id: str
    session_id: str | None = None
    status: CaseStatus = CaseStatus.OPEN
    severity: Severity = Severity.INFO
    opened_at: datetime
    closed_at: datetime | None = None
    trigger_anomaly_ids: list[str] = Field(default_factory=list)
    trigger_dtcs: list[DTCRecord] = Field(default_factory=list)
    explanation: str | None = Field(
        default=None, description="Explicación final para el usuario (nodo report)"
    )
    decision: ExplanationDecision | None = Field(
        default=None,
        description=(
            "Decisión del nodo decide sobre la suficiencia de la evidencia (ADR-0036): "
            "explicación sostenida, contradicha, no concluyente o abstención"
        ),
    )
    supported_claim_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fracción de afirmaciones que requieren evidencia y que la tienen",
    )
    provenance_id: str | None = None


class DiagnosticEvidence(ContractBase):
    """Pieza de evidencia (a favor/en contra) asociada a una hipótesis o al caso."""

    evidence_id: str
    case_id: str
    hypothesis_id: str | None = Field(default=None, description="None = evidencia del caso")
    kind: EvidenceKind
    role: EvidenceRole
    reference_id: str | None = Field(
        default=None, description="Id del objeto referenciado (ventana, chunk, caso, DTC…)"
    )
    statement: str = Field(description="Afirmación verificable, p. ej. 'total_trim_mean=+8.1%'")
    strength: float = Field(ge=0.0, le=1.0, default=0.5)
    produced_by: str = Field(description="Nodo/proceso que la produjo, p. ej. 'verify'")
    created_at: datetime


# ---------------------------------------------------------------------------
# Procedencia
# ---------------------------------------------------------------------------


class ProvenanceRecord(ContractBase):
    """Procedencia completa de un artefacto INFERRED (obligatoria para diagnósticos).

    Modelo explícito (decisión ADR-0012): concentra los enlaces en un objeto en lugar
    de dispersarlos, de modo que la pregunta «¿de dónde salió esto?» tenga una sola
    respuesta navegable.
    """

    provenance_id: str
    subject_kind: str = Field(description="'diagnostic_case' | 'learned_pattern' | …")
    subject_id: str
    vehicle_id: str | None = None
    session_ids: list[str] = Field(default_factory=list)
    window_ids: list[str] = Field(default_factory=list)
    fv_ids: list[str] = Field(default_factory=list)
    inference_ids: list[str] = Field(default_factory=list)
    anomaly_ids: list[str] = Field(default_factory=list)
    model_refs: list[str] = Field(default_factory=list, description="'nombre@versión'")
    document_chunk_ids: list[str] = Field(default_factory=list, description="RAG utilizados")
    case_memory_ids: list[str] = Field(default_factory=list, description="Memoria recuperada")
    agent_run_id: str | None = None
    prompt_version: str | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Memoria episódica y semántica/evolutiva
# ---------------------------------------------------------------------------


class CaseMemory(ContractBase):
    """Memoria EPISÓDICA: experiencia diagnóstica recuperable por similitud."""

    case_memory_id: str
    case_id: str
    vehicle_id: str
    vehicle_profile: dict[str, str] = Field(
        default_factory=dict, description="Rasgos del vehículo (combustible, cilindros…)"
    )
    symptom_text: str = Field(description="Síntomas en texto (base del embedding)")
    symptom_signature: dict[str, float] = Field(description="Firma numérica (features clave)")
    temporal_signature: str | None = Field(
        default=None, description="Descripción compacta de la dinámica (p. ej. 'deriva 5 min')"
    )
    related_dtcs: list[str] = Field(default_factory=list)
    related_event_ids: list[str] = Field(
        default_factory=list,
        description="VehicleEvents en los que se manifestó el problema (F6, ADR-0021)",
    )
    anomaly_detector: str | None = None
    diagnosis: str
    outcome: str | None = None
    epistemic_level: EpistemicLevel
    embedding_ref: str | None = Field(
        default=None, description="Referencia al vector en el índice (no el vector en sí)"
    )
    reinforcement_count: int = Field(default=1, ge=1)
    created_at: datetime
    updated_at: datetime


class LearnedPattern(ContractBase):
    """Memoria SEMÁNTICA/EVOLUTIVA: patrón consolidado emergente de múltiples casos.

    La promoción a VALIDATED nunca es automática en esta fase (ADR-0013).
    """

    pattern_id: str
    version: int = Field(ge=1)
    title: str
    description: str
    telemetry_signature: dict[str, float] = Field(
        description="Rango/centroide de features que caracteriza el patrón"
    )
    temporal_signature: str | None = None
    affected_metrics: list[str] = Field(description="PIDs/features implicados")
    event_types: list[str] = Field(
        default_factory=list,
        description="Tipos de evento donde el patrón se manifiesta (taxonomía F6, ADR-0021)",
    )
    related_dtc: list[str] = Field(default_factory=list)
    suspected_failure_modes: list[str] = Field(default_factory=list)
    supporting_cases: list[str] = Field(default_factory=list, description="case_memory_ids")
    contradicting_cases: list[str] = Field(default_factory=list)
    n_independent_sessions: int = Field(default=0, ge=0)
    n_distinct_vehicles: int = Field(default=0, ge=0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    novelty_score: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="Distancia a patrones/documentación existentes (clave para la PI)",
    )
    validation_level: EpistemicLevel = EpistemicLevel.SYNTHETIC
    status: PatternStatus = PatternStatus.CANDIDATE
    first_seen: datetime
    last_seen: datetime
    provenance_id: str | None = None


class PatternRelation(ContractBase):
    """Relación tipada entre patrones (grafo ligero sobre SQL; sin graph-DB por ahora)."""

    relation_id: str
    from_pattern_id: str
    to_pattern_id: str
    kind: PatternRelationKind
    note: str | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Feedback e intervenciones
# ---------------------------------------------------------------------------


class DiagnosticFeedback(ContractBase):
    """Cierre del lazo: verdad externa sobre un diagnóstico (mide si la memoria mejora)."""

    feedback_id: str
    case_id: str
    kind: FeedbackKind
    verdict: FeedbackVerdict
    true_cause: str | None = Field(default=None, description="Causa real si se conoce")
    detail: str | None = None
    provided_by: str = Field(description="'obd-lab' | 'dataset' | persona identificada")
    created_at: datetime


class MaintenanceEvent(ContractBase):
    """Intervención de mantenimiento (permite estudiar anomalía→diagnóstico→reparación→efecto)."""

    event_id: str
    vehicle_id: str
    performed_at: datetime
    action: str
    component: str | None = None
    related_case_id: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Ejecución del agente (working memory persistida para trazabilidad)
# ---------------------------------------------------------------------------


class AgentRun(ContractBase):
    """Ejecución completa del grafo sobre un caso. SIN chain-of-thought: solo E/S estructuradas."""

    run_id: str
    case_id: str
    graph_version: str
    llm_model: str = Field(description="Tag del LLM o 'heuristic' si generador determinista")
    prompt_version: str
    memory_mode: MemoryMode = Field(description="Variable del experimento de memoria")
    config: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    ended_at: datetime | None = None
    latency_ms: float | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    result_status: str = Field(default="ok", description="'ok' | 'error' | 'no_hypothesis'")


class AgentStep(ContractBase):
    """Auditoría de un nodo del grafo: entradas/salidas estructuradas, nunca razonamiento libre."""

    step_id: str
    run_id: str
    node: AgentNode
    seq: int = Field(ge=0)
    status: StepStatus = StepStatus.OK
    started_at: datetime
    ended_at: datetime | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    tools_used: list[str] = Field(default_factory=list)
    error: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class RetrievalEvent(ContractBase):
    """Recuperación auditada (RAG o memoria): qué se pidió, qué volvió, qué se usó."""

    retrieval_id: str
    run_id: str
    step_id: str
    source: str = Field(description="'rag' | 'episodic_memory' | 'semantic_memory'")
    query: str
    retrieved_ids: list[str] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    used_in_hypothesis_ids: list[str] = Field(default_factory=list)
    created_at: datetime


# ---------------------------------------------------------------------------
# Conocimiento documental (RAG)
# ---------------------------------------------------------------------------


class KnowledgeDocument(ContractBase):
    """Documento del corpus técnico (con licencia registrada en el manifiesto del corpus)."""

    document_id: str
    title: str
    source: str
    license: str
    version: str = "1"
    checksum: str | None = None
    ingested_at: datetime


class KnowledgeChunk(ContractBase):
    """Fragmento indexable de un documento (unidad de recuperación y de cita)."""

    chunk_id: str
    document_id: str
    seq: int = Field(ge=0)
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    embedding_ref: str | None = None
