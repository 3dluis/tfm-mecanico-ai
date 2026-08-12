"""Enumeraciones compartidas."""

from enum import StrEnum


class Severity(StrEnum):
    """Severidad de una anomalía, diagnóstico o recomendación."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransportKind(StrEnum):
    """Transporte físico/virtual hacia el adaptador OBD-II (ADR-0004)."""

    SERIAL = "serial"
    TCP = "tcp"
    BLUETOOTH_RFCOMM = "bluetooth-rfcomm"


class DetectorKind(StrEnum):
    """Familia del detector matemático de anomalías (separación ML/LLM)."""

    ZSCORE = "zscore"
    ISOLATION_FOREST = "isolation_forest"
    LOF = "lof"
    OCSVM = "ocsvm"
    AUTOENCODER = "autoencoder"


class AgentNode(StrEnum):
    """Nodos del grafo del agente de diagnóstico (docs/05 §5.2 C6)."""

    TRIAGE = "triage"
    RECALL = "recall"
    RETRIEVE = "retrieve"
    HYPOTHESIZE = "hypothesize"
    VERIFY = "verify"
    REPORT = "report"
    MEMORIZE = "memorize"


class SyncEntity(StrEnum):
    """Entidades sincronizables edge→cloud (patrón outbox)."""

    TELEMETRY_WINDOW = "telemetry_window"
    ANOMALY = "anomaly"
    DIAGNOSTIC = "diagnostic"
    CASE = "case"
