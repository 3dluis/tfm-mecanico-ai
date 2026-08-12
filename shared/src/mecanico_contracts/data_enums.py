"""Enumeraciones del modelo de datos v2 (arquitectura de datos, ADR-0012/0013)."""

from enum import StrEnum


class SessionSource(StrEnum):
    """Origen de una sesión de telemetría. Determina el peso epistemológico aguas abajo."""

    REAL_VEHICLE = "real_vehicle"
    OBD_SIMULATOR = "obd_simulator"  # emulador ELM327 en vivo
    DATASET_REPLAY = "dataset_replay"  # dataset público reproducido
    SYNTHETIC_GENERATOR = "synthetic_generator"  # generación offline de obd-lab
    BENCH_TEST = "bench_test"  # prueba controlada


class DataClass(StrEnum):
    """Clasificación epistemológica de un dato (ADR-0012).

    Un dato ``inferred`` nunca debe presentarse como una observación real.
    """

    RAW = "raw"  # observado directamente
    NORMALIZED = "normalized"  # transformado a esquema canónico
    DERIVED = "derived"  # calculado (features, ventanas)
    INFERRED = "inferred"  # producido por modelos o por el agente


class CaseStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class HypothesisStatus(StrEnum):
    PROPOSED = "proposed"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    CONFIRMED = "confirmed"  # requiere feedback externo, nunca lo fija el agente solo
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class EvidenceKind(StrEnum):
    TELEMETRY = "telemetry"  # features/ventanas contrastadas
    DTC = "dtc"
    DOCUMENT = "document"  # fragmento RAG
    CASE = "case"  # caso episódico recuperado
    PATTERN = "pattern"  # LearnedPattern
    FEEDBACK = "feedback"  # ground truth / validación externa
    MAINTENANCE = "maintenance"  # intervención y su efecto


class EvidenceRole(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"


class EpistemicLevel(StrEnum):
    """Nivel epistemológico de un caso de memoria: lo simulado JAMÁS pesa como lo real."""

    SIMULATED = "simulated"  # emulador en vivo
    SYNTHETIC = "synthetic"  # generador offline
    PUBLIC_DATASET = "public_dataset"
    REAL_UNVALIDATED = "real_unvalidated"
    HUMAN_VALIDATED = "human_validated"


class PatternStatus(StrEnum):
    CANDIDATE = "candidate"
    EMERGING = "emerging"
    VALIDATED = "validated"  # promoción NUNCA automática en esta fase (ADR-0013)
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


class PatternRelationKind(StrEnum):
    SIMILAR_TO = "similar_to"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    SPECIALIZATION_OF = "specialization_of"
    GENERALIZATION_OF = "generalization_of"
    CO_OCCURS_WITH = "co_occurs_with"
    PRECEDES = "precedes"


class FeedbackKind(StrEnum):
    SIMULATOR_GROUND_TRUTH = "simulator_ground_truth"
    DATASET_GROUND_TRUTH = "dataset_ground_truth"
    HUMAN_VALIDATION = "human_validation"
    MECHANIC_VALIDATION = "mechanic_validation"
    REPAIR_OUTCOME = "repair_outcome"


class FeedbackVerdict(StrEnum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    UNKNOWN = "unknown"


class MemoryMode(StrEnum):
    """Modo de memoria del agente (variable del experimento de memoria evolutiva)."""

    NONE = "none"
    EPISODIC = "episodic"
    EPISODIC_SEMANTIC = "episodic_semantic"


class StepStatus(StrEnum):
    OK = "ok"
    ERROR = "error"
    SKIPPED = "skipped"
