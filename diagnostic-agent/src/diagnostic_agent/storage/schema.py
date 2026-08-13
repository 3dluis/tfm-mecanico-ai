"""Esquema relacional v2 del edge (SQLite; equivalencia PostgreSQL en docs/data-architecture/03).

Espejo relacional de los contratos de ``mecanico_contracts`` (la fuente de verdad son los
contratos; este módulo NO redefine semántica, solo persistencia). Convenciones:
- Ids globalmente únicos (UUID en texto) → sincronización idempotente (docs/da/09).
- Dicts/listas de contratos → columnas JSON (portables a JSONB en PostgreSQL).
- ``schema_version`` de fila = versión del contrato con la que se escribió.
- Versionado del esquema físico: ``PRAGMA user_version`` gestionado por ``migrations.py``.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA_DB_VERSION = 4  # v4: vehicle_telemetry_snapshots + snapshot_event_links (F11)


class Base(DeclarativeBase):
    pass


class _Row:
    """Columnas comunes."""

    schema_version: Mapped[int] = mapped_column(Integer, default=2)


# ------------------------------------------------------------- telemetría (cadena)


class SessionRow(Base, _Row):
    __tablename__ = "telemetry_sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    device_id: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sample_rate_hz: Mapped[float] = mapped_column(Float)
    scenario_id: Mapped[str | None] = mapped_column(String, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    generator_version: Mapped[str | None] = mapped_column(String, nullable=True)
    random_seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    software_version: Mapped[str] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ObservationRow(Base, _Row):
    """RAW: observación OBD tal como llegó (una fila por PID y tick)."""

    __tablename__ = "obd_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("telemetry_sessions.session_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    pid: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)


class PointRow(Base, _Row):
    """NORMALIZED: tick validado en unidades canónicas."""

    __tablename__ = "telemetry_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("telemetry_sessions.session_id"), index=True)
    seq: Mapped[int] = mapped_column(Integer, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    values: Mapped[dict[str, object]] = mapped_column(JSON)
    discarded_pids: Mapped[list[object]] = mapped_column(JSON, default=list)


class WindowRow(Base, _Row):
    """DERIVED: ventana sobre puntos normalizados."""

    __tablename__ = "telemetry_windows"

    window_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("telemetry_sessions.session_id"), index=True)
    seq_start: Mapped[int] = mapped_column(Integer)
    seq_end: Mapped[int] = mapped_column(Integer)
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    size: Mapped[int] = mapped_column(Integer)
    stride: Mapped[int] = mapped_column(Integer)


class FeatureVectorRow(Base, _Row):
    """DERIVED: vector de features canónicas de una ventana."""

    __tablename__ = "feature_vectors"

    fv_id: Mapped[str] = mapped_column(String, primary_key=True)
    window_id: Mapped[str] = mapped_column(ForeignKey("telemetry_windows.window_id"), index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    feature_set_version: Mapped[str] = mapped_column(String)
    values: Mapped[dict[str, object]] = mapped_column(JSON)


class InferenceRow(Base, _Row):
    """INFERRED: ejecución de modelo ML (toda inferencia se persiste)."""

    __tablename__ = "model_inferences"

    inference_id: Mapped[str] = mapped_column(String, primary_key=True)
    fv_id: Mapped[str] = mapped_column(ForeignKey("feature_vectors.fv_id"), index=True)
    window_id: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    model_id: Mapped[str] = mapped_column(String)
    model_name: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    flagged: Mapped[bool] = mapped_column(Boolean, index=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AnomalyRow(Base, _Row):
    """INFERRED: anomalía emitida (enlaza a la inferencia que la produjo)."""

    __tablename__ = "detected_anomalies"

    anomaly_id: Mapped[str] = mapped_column(String, primary_key=True)
    inference_id: Mapped[str | None] = mapped_column(
        ForeignKey("model_inferences.inference_id"), nullable=True, index=True
    )
    window_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    event_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    baseline_id: Mapped[str | None] = mapped_column(String, nullable=True)
    anomaly_scope: Mapped[str] = mapped_column(String, default="window", index=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detector: Mapped[str] = mapped_column(String)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[float] = mapped_column(Float)
    threshold: Mapped[float] = mapped_column(Float)
    involved_pids: Mapped[list[object]] = mapped_column(JSON, default=list)
    features: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


# ----------------------------------------- snapshots (F11, ADR-0025/0026/0027)


class SnapshotRow(Base, _Row):
    """NORMALIZED WIDE / TIME-ALIGNED: estado multivariable por instante canónico.

    Índices según los query patterns documentados (docs/data-architecture/11 §queries):
    (vehicle_id, timestamp_utc) · (session_id, timestamp_utc) ·
    (primary_event_type, timestamp_utc). En PostgreSQL la tabla es candidata a
    particionado mensual por timestamp_utc (ADR-0028; evaluar volumen antes).
    """

    __tablename__ = "vehicle_telemetry_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String)
    device_id: Mapped[str] = mapped_column(String)
    session_id: Mapped[str] = mapped_column(ForeignKey("telemetry_sessions.session_id"))
    trip_id: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sequence_number: Mapped[int] = mapped_column(Integer)
    snapshot_interval_ms: Mapped[int] = mapped_column(Integer, default=1000)
    synchronization_version: Mapped[str] = mapped_column(String, default="sync:v1")
    primary_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    primary_event_type: Mapped[str | None] = mapped_column(String, nullable=True)
    vehicle_state: Mapped[str | None] = mapped_column(String, nullable=True)
    # OBD estándar — NULL = no disponible (quality_flags), jamás 0 (ADR-0027)
    rpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    vehicle_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    throttle_position: Mapped[float | None] = mapped_column(Float, nullable=True)
    engine_load: Mapped[float | None] = mapped_column(Float, nullable=True)
    coolant_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    intake_air_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    maf: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_kpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    stft_bank1: Mapped[float | None] = mapped_column(Float, nullable=True)
    ltft_bank1: Mapped[float | None] = mapped_column(Float, nullable=True)
    stft_bank2: Mapped[float | None] = mapped_column(Float, nullable=True)
    ltft_bank2: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    timing_advance: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery_voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
    o2_sensor_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    o2_sensor_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    commanded_equivalence_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    active_dtc_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acceleration_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    acceleration_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    acceleration_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    gyro_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    gyro_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    gyro_z: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0)
    missing_metric_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_flags: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_snap_vehicle_ts", "vehicle_id", "timestamp_utc"),
        Index("ix_snap_session_ts", "session_id", "timestamp_utc"),
        Index("ix_snap_eventtype_ts", "primary_event_type", "timestamp_utc"),
    )


class SnapshotEventLinkRow(Base, _Row):
    """Relación N:M snapshot↔evento (un instante pertenece a TRIP+ACCELERATION+…)."""

    __tablename__ = "snapshot_event_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("vehicle_telemetry_snapshots.snapshot_id"), index=True
    )
    event_id: Mapped[str] = mapped_column(ForeignKey("vehicle_events.event_id"), index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)


# --------------------------------------------------------- eventos (F6, ADR-0019/0021)


class EventRow(Base, _Row):
    """INFERRED: evento vehicular segmentado. Referencia telemetría (seq), no la duplica."""

    __tablename__ = "vehicle_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("telemetry_sessions.session_id"), index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    event_subtype: Mapped[str | None] = mapped_column(String, nullable=True)
    event_class: Mapped[str] = mapped_column(String)  # observed|inferred|estimated
    taxonomy_version: Mapped[int] = mapped_column(Integer, default=1)
    parent_event_id: Mapped[str | None] = mapped_column(
        ForeignKey("vehicle_events.event_id"), nullable=True, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seq_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seq_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    detection_method: Mapped[str] = mapped_column(String)
    detector_version: Mapped[str] = mapped_column(String)
    source_sensors: Mapped[list[object]] = mapped_column(JSON, default=list)
    evidence: Mapped[list[object]] = mapped_column(JSON, default=list)
    meta: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)  # 'metadata' contrato
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EventFeatureRow(Base, _Row):
    """DERIVED: features de evento completo (comparables por context_signature)."""

    __tablename__ = "event_feature_vectors"

    efv_id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(ForeignKey("vehicle_events.event_id"), index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    context_signature: Mapped[str] = mapped_column(String, index=True)
    feature_schema_version: Mapped[str] = mapped_column(String)
    preprocessing_version: Mapped[str] = mapped_column(String)
    detector_version: Mapped[str] = mapped_column(String)
    values: Mapped[dict[str, object]] = mapped_column(JSON)


class EventBaselineRow(Base, _Row):
    """INFERRED: normalidad acumulada por (vehículo, tipo de evento, contexto)."""

    __tablename__ = "event_baselines"

    baseline_id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    context_signature: Mapped[str] = mapped_column(String, index=True)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    feature_distribution: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    centroid: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    feature_schema_version: Mapped[str] = mapped_column(String)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


# --------------------------------------------------------------- diagnóstico


class CaseRow(Base, _Row):
    __tablename__ = "diagnostic_cases"

    case_id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, default="open", index=True)
    severity: Mapped[str] = mapped_column(String, default="info")
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger_anomaly_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    trigger_dtcs: Mapped[list[object]] = mapped_column(JSON, default=list)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_id: Mapped[str | None] = mapped_column(String, nullable=True)


class HypothesisRow(Base, _Row):
    __tablename__ = "diagnostic_hypotheses"

    hypothesis_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_cases.case_id"), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    suspected_component: Mapped[str] = mapped_column(String)
    failure_mode: Mapped[str] = mapped_column(String, index=True)
    cause: Mapped[str] = mapped_column(Text)
    mechanism: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="proposed", index=True)
    verified_against_telemetry: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float)


class EvidenceRow(Base, _Row):
    __tablename__ = "diagnostic_evidence"

    evidence_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_cases.case_id"), index=True)
    hypothesis_id: Mapped[str | None] = mapped_column(
        ForeignKey("diagnostic_hypotheses.hypothesis_id"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    reference_id: Mapped[str | None] = mapped_column(String, nullable=True)
    statement: Mapped[str] = mapped_column(Text)
    strength: Mapped[float] = mapped_column(Float, default=0.5)
    produced_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProvenanceRow(Base, _Row):
    __tablename__ = "provenance_records"

    provenance_id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_kind: Mapped[str] = mapped_column(String, index=True)
    subject_id: Mapped[str] = mapped_column(String, index=True)
    vehicle_id: Mapped[str | None] = mapped_column(String, nullable=True)
    session_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    window_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    fv_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    inference_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    anomaly_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    model_refs: Mapped[list[object]] = mapped_column(JSON, default=list)
    document_chunk_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    case_memory_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    agent_run_id: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ------------------------------------------------------------------- memoria


class CaseMemoryRow(Base, _Row):
    __tablename__ = "case_memory"

    case_memory_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_cases.case_id"), index=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    vehicle_profile: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    symptom_text: Mapped[str] = mapped_column(Text)
    symptom_signature: Mapped[dict[str, object]] = mapped_column(JSON)
    temporal_signature: Mapped[str | None] = mapped_column(String, nullable=True)
    related_dtcs: Mapped[list[object]] = mapped_column(JSON, default=list)
    related_event_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    anomaly_detector: Mapped[str | None] = mapped_column(String, nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    epistemic_level: Mapped[str] = mapped_column(String, index=True)
    embedding_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    reinforcement_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LearnedPatternRow(Base, _Row):
    __tablename__ = "learned_patterns"

    pattern_id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    telemetry_signature: Mapped[dict[str, object]] = mapped_column(JSON)
    temporal_signature: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_metrics: Mapped[list[object]] = mapped_column(JSON, default=list)
    event_types: Mapped[list[object]] = mapped_column(JSON, default=list)
    related_dtc: Mapped[list[object]] = mapped_column(JSON, default=list)
    suspected_failure_modes: Mapped[list[object]] = mapped_column(JSON, default=list)
    supporting_cases: Mapped[list[object]] = mapped_column(JSON, default=list)
    contradicting_cases: Mapped[list[object]] = mapped_column(JSON, default=list)
    n_independent_sessions: Mapped[int] = mapped_column(Integer, default=0)
    n_distinct_vehicles: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    novelty_score: Mapped[float] = mapped_column(Float, default=0.0)
    validation_level: Mapped[str] = mapped_column(String, default="synthetic")
    status: Mapped[str] = mapped_column(String, default="candidate", index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    provenance_id: Mapped[str | None] = mapped_column(String, nullable=True)


class PatternRelationRow(Base, _Row):
    __tablename__ = "pattern_relations"

    relation_id: Mapped[str] = mapped_column(String, primary_key=True)
    from_pattern_id: Mapped[str] = mapped_column(
        ForeignKey("learned_patterns.pattern_id"), index=True
    )
    to_pattern_id: Mapped[str] = mapped_column(
        ForeignKey("learned_patterns.pattern_id"), index=True
    )
    kind: Mapped[str] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# ------------------------------------------------------- feedback e intervención


class FeedbackRow(Base, _Row):
    __tablename__ = "diagnostic_feedback"

    feedback_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_cases.case_id"), index=True)
    kind: Mapped[str] = mapped_column(String)
    verdict: Mapped[str] = mapped_column(String)
    true_cause: Mapped[str | None] = mapped_column(String, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    provided_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MaintenanceRow(Base, _Row):
    __tablename__ = "maintenance_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String, index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    action: Mapped[str] = mapped_column(Text)
    component: Mapped[str | None] = mapped_column(String, nullable=True)
    related_case_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


# ------------------------------------------------------------ ejecución del agente


class AgentRunRow(Base, _Row):
    __tablename__ = "agent_runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_cases.case_id"), index=True)
    graph_version: Mapped[str] = mapped_column(String)
    llm_model: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String)
    memory_mode: Mapped[str] = mapped_column(String, index=True)
    config: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_status: Mapped[str] = mapped_column(String, default="ok")


class AgentStepRow(Base, _Row):
    __tablename__ = "agent_steps"

    step_id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.run_id"), index=True)
    node: Mapped[str] = mapped_column(String)
    seq: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="ok")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inputs: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    tools_used: Mapped[list[object]] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class RetrievalRow(Base, _Row):
    __tablename__ = "retrieval_events"

    retrieval_id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.run_id"), index=True)
    step_id: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    query: Mapped[str] = mapped_column(Text)
    retrieved_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    scores: Mapped[list[object]] = mapped_column(JSON, default=list)
    used_in_hypothesis_ids: Mapped[list[object]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# --------------------------------------------------------------- conocimiento


class KnowledgeDocumentRow(Base, _Row):
    __tablename__ = "knowledge_documents"

    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    license: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String, default="1")
    checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class KnowledgeChunkRow(Base, _Row):
    __tablename__ = "knowledge_chunks"

    chunk_id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("knowledge_documents.document_id"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    embedding_ref: Mapped[str | None] = mapped_column(String, nullable=True)


# ------------------------------------------------------------------ sincronización


class OutboxRow(Base, _Row):
    """Cola outbox edge→cloud (docs/data-architecture/09): push idempotente priorizado."""

    __tablename__ = "sync_outbox"

    envelope_id: Mapped[str] = mapped_column(String, primary_key=True)
    entity: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[str] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer, default=5, index=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)
    checksum: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
