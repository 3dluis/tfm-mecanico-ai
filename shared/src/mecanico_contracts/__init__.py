"""mecanico_contracts — contratos compartidos del sistema Mecánico IA.

Única fuente de verdad de los mensajes que cruzan dominios (ADR-0007).
Regla: los proyectos dependen de este paquete y NUNCA entre sí.
"""

from mecanico_contracts.enums import (
    AgentNode,
    DetectorKind,
    Severity,
    SyncEntity,
    TransportKind,
)
from mecanico_contracts.models import (
    SCHEMA_VERSION,
    AgentEvent,
    CaseRecord,
    DetectedAnomaly,
    DiagnosticHypothesis,
    DiagnosticResult,
    DTCRecord,
    MaintenanceRecommendation,
    ModelManifest,
    OBDReading,
    RecordedSession,
    ScenarioSpec,
    SyncEnvelope,
    VehicleTelemetry,
)

__version__ = "0.1.0"

__all__ = [
    "SCHEMA_VERSION",
    "AgentEvent",
    "AgentNode",
    "CaseRecord",
    "DTCRecord",
    "DetectedAnomaly",
    "DetectorKind",
    "DiagnosticHypothesis",
    "DiagnosticResult",
    "MaintenanceRecommendation",
    "ModelManifest",
    "OBDReading",
    "RecordedSession",
    "ScenarioSpec",
    "Severity",
    "SyncEntity",
    "SyncEnvelope",
    "TransportKind",
    "VehicleTelemetry",
]
