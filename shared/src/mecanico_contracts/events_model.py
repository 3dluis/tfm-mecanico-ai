"""Modelo de datos de Vehicle Event Intelligence (F6; ADR-0019/0021).

Los eventos referencian telemetría (session_id + seq/timestamps), no la duplican.
Regla: un evento inferido nunca se presenta como hecho observado (``event_class``).
"""

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from mecanico_contracts.data_enums import AnomalyScope
from mecanico_contracts.models import ContractBase

__all__ = [
    "ALL_EVENT_TYPES",
    "EVENT_TAXONOMY",
    "TAXONOMY_VERSION",
    "AnomalyScope",
    "EventBaseline",
    "EventClass",
    "EventFeatureVector",
    "VehicleEvent",
]

TAXONOMY_VERSION = 1

#: Taxonomía v1 (docs/event-intelligence/02). Categoría → tipos.
EVENT_TAXONOMY: dict[str, list[str]] = {
    "POWER": ["IGNITION_ON", "IGNITION_OFF"],
    "ENGINE": ["ENGINE_START", "ENGINE_STOP", "COLD_START", "WARM_START", "IDLE"],
    "MOTION": [
        "VEHICLE_START_MOVING",
        "VEHICLE_STOPPED",
        "ACCELERATION",
        "DECELERATION",
        "CONSTANT_SPEED",
    ],
    "MANEUVER": ["TURN_LEFT", "TURN_RIGHT", "HARD_TURN", "HARD_BRAKING", "RAPID_ACCELERATION"],
    "TRANSMISSION": ["GEAR_SHIFT_INFERRED", "UPSHIFT_INFERRED", "DOWNSHIFT_INFERRED"],
    "ENVIRONMENT": ["VIBRATION", "IMPACT"],
    "ANOMALY": ["CONTEXTUAL_ANOMALY", "DATA_LOSS"],
    "TRIP": ["TRIP", "TRIP_START", "TRIP_END", "PARKED"],
}

ALL_EVENT_TYPES: set[str] = {t for types in EVENT_TAXONOMY.values() for t in types}


class EventClass(StrEnum):
    """Clase de conocimiento del evento (nunca se confunde inferencia con observación)."""

    OBSERVED = "observed"
    INFERRED = "inferred"
    ESTIMATED = "estimated"


class VehicleEvent(ContractBase):
    """Evento vehicular segmentado (unidad formal de análisis; jerárquico)."""

    event_id: str
    vehicle_id: str
    session_id: str
    event_type: str = Field(description="Tipo de la taxonomía v1 (EVENT_TAXONOMY)")
    event_subtype: str | None = None
    event_class: EventClass = Field(description="observed | inferred | estimated")
    taxonomy_version: int = TAXONOMY_VERSION
    parent_event_id: str | None = Field(default=None, description="Jerarquía (TRIP→evento→micro)")
    start_time: datetime
    end_time: datetime | None = Field(default=None, description="None = evento puntual/abierto")
    duration_ms: int | None = Field(default=None, ge=0)
    seq_start: int | None = Field(default=None, description="Ref. a TelemetryPoint.seq inicial")
    seq_end: int | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    detection_method: str = Field(description="'rule:v1' | 'state_machine:v1' | 'hmm:…'")
    detector_version: str
    source_sensors: list[str] = Field(default_factory=lambda: ["obd"], description="obd|imu|gps")
    evidence: list[str] = Field(
        default_factory=list, description="Afirmaciones verificables que sustentan el evento"
    )
    metadata: dict[str, float | str] = Field(default_factory=dict)
    created_at: datetime


class EventFeatureVector(ContractBase):
    """Features DERIVED de un evento completo (comparable dentro de su contexto)."""

    efv_id: str
    event_id: str
    session_id: str
    vehicle_id: str
    event_type: str
    context_signature: str = Field(
        description="Firma canónica de comparabilidad, p. ej. 'ACCELERATION|40-80|warm|d4-8s'"
    )
    feature_schema_version: str
    preprocessing_version: str
    detector_version: str
    values: dict[str, float]


class EventBaseline(ContractBase):
    """Normalidad acumulada de UN vehículo para UN contexto de evento (INFERRED)."""

    baseline_id: str
    vehicle_id: str
    event_type: str
    context_signature: str
    sample_count: int = Field(ge=0)
    feature_distribution: dict[str, dict[str, float]] = Field(
        description="feature → {mean, std, p05, p50, p95}"
    )
    centroid: dict[str, float] = Field(default_factory=dict)
    feature_schema_version: str
    first_seen: datetime
    last_updated: datetime
    version: int = Field(ge=1, default=1)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
