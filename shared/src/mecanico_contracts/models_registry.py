"""Gobernanza de modelos de IA (F7, ADR-0022): registro, experimentos y ciclo de vida.

Los modelos no son solo componentes técnicos: son ARTEFACTOS EXPERIMENTALES de la
investigación. Estos contratos garantizan que siempre pueda reconstruirse la cadena
¿qué datos? → ¿qué experimento? → ¿qué modelo/versión? → ¿qué artefacto/configuración?
→ ¿qué inferencia? → ¿qué decisión produjo? (regla fundamental del plan F7).

Distinción Registry vs Manifest (docs/models/08 y 09): el registro es el CATÁLOGO de
modelos conocidos por el sistema; el ``ModelManifest`` (models.py) es el contrato
PORTABLE que acompaña a un artefacto concreto desplegado al edge.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from mecanico_contracts.models import ContractBase

MODEL_GOVERNANCE_VERSION = 1


class ModelType(StrEnum):
    """Las tres categorías de la taxonomía (docs/models/01)."""

    ML = "ml"  # detección de anomalías/eventos, clustering, CPD, temporal
    LLM = "llm"  # funciones agénticas; JAMÁS detección matemática de anomalías
    EMBEDDING = "embedding"  # representación para RAG/memoria/patrones


class ModelStatus(StrEnum):
    """Ciclo de vida (docs/models/08). EDGE_APPROVED exige validación en hardware,
    no solo métricas offline (latencia, memoria, ARM64, estabilidad, formato)."""

    EXPERIMENTAL = "experimental"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    EDGE_APPROVED = "edge_approved"
    DEPLOYED = "deployed"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


#: Transiciones permitidas del ciclo de vida (cualquier otra es un error de gobernanza).
#: Ajuste F9: EXPERIMENTAL/CANDIDATE también pueden pasar a SUPERSEDED — una versión
#: puede quedar sucedida por otra ANTES de validarse (caso real: event-baseline-z 0.1.0
#: → 0.2.0 tras EXP-ANOM-003). No afecta a ninguna transición previamente registrada.
ALLOWED_STATUS_TRANSITIONS: dict[ModelStatus, frozenset[ModelStatus]] = {
    ModelStatus.EXPERIMENTAL: frozenset(
        {ModelStatus.CANDIDATE, ModelStatus.REJECTED, ModelStatus.SUPERSEDED}
    ),
    ModelStatus.CANDIDATE: frozenset(
        {ModelStatus.VALIDATED, ModelStatus.REJECTED, ModelStatus.SUPERSEDED}
    ),
    ModelStatus.VALIDATED: frozenset(
        {ModelStatus.EDGE_APPROVED, ModelStatus.REJECTED, ModelStatus.SUPERSEDED}
    ),
    ModelStatus.EDGE_APPROVED: frozenset(
        {ModelStatus.DEPLOYED, ModelStatus.SUPERSEDED, ModelStatus.RETIRED}
    ),
    ModelStatus.DEPLOYED: frozenset({ModelStatus.SUPERSEDED, ModelStatus.RETIRED}),
    ModelStatus.REJECTED: frozenset(),
    ModelStatus.SUPERSEDED: frozenset({ModelStatus.RETIRED}),
    ModelStatus.RETIRED: frozenset(),
}


class ModelCapability(StrEnum):
    """Capacidades consultables por el ModelRouter del Agent Runtime (docs/models/03)."""

    TRIAGE = "triage"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    CRITIQUE = "critique"
    REPORTING = "reporting"
    TOOL_SELECTION = "tool_selection"
    EMBEDDINGS = "embeddings"
    ANOMALY_DETECTION = "anomaly_detection"
    EVENT_DETECTION = "event_detection"


class HardwareValidationStatus(StrEnum):
    """Estado de un modelo en un objetivo hardware de la matriz (docs/models/10)."""

    COMPATIBLE = "compatible"
    NOT_TESTED = "not_tested"
    FAILED = "failed"
    APPROVED = "approved"


class TrainingRun(ContractBase):
    """Un entrenamiento/ajuste concreto: reproducible por sí solo (docs/models/05)."""

    training_run_id: str
    experiment_id: str | None = Field(default=None, description="ModelExperiment al que aporta")
    model_id: str
    model_version: str
    model_type: ModelType = ModelType.ML
    dataset_id: str
    dataset_version: str
    dataset_checksum: str | None = None
    split_version: str | None = Field(
        default=None, description="Versión del split train/val/test (linaje, docs/models/06)"
    )
    feature_schema_version: str | None = None
    preprocessing_version: str | None = None
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None
    git_commit: str
    python_version: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    hardware: str = Field(description="Dónde se entrenó: 'sandbox-x86', 'mac-arm64', 'rpi5'…")
    metrics: dict[str, float] = Field(default_factory=dict)
    artifact_uri: str | None = None
    artifact_checksum: str | None = None
    status: str = Field(default="ok", description="'ok' | 'failed' | 'running'")


class ModelExperiment(ContractBase):
    """Comparación científicamente válida: varios TrainingRuns con dataset/split/features/
    protocolo IDÉNTICOS (docs/models/12)."""

    experiment_id: str = Field(description="p. ej. 'EXP-ANOM-001'")
    title: str
    objective: str = Field(description="Pregunta experimental que responde")
    dataset_id: str
    dataset_version: str
    split_version: str | None = None
    feature_schema_version: str | None = None
    evaluation_protocol: str = Field(
        description="Referencia al protocolo pre-registrado, p. ej. 'ADR-0011'"
    )
    config_uri: str | None = Field(
        default=None, description="Config declarativa del experimento (YAML)"
    )
    training_run_ids: list[str] = Field(default_factory=list)
    conclusion: str | None = Field(default=None, description="Interpretación y decisión")
    selected_model_id: str | None = None
    report_uri: str | None = Field(
        default=None, description="Informe de comparación (docs/models/comparisons/)"
    )
    created_at: datetime


class ModelEvaluation(ContractBase):
    """Evaluación de una versión concreta bajo un protocolo (offline o edge)."""

    evaluation_id: str
    model_id: str
    model_version: str
    dataset_id: str
    dataset_version: str
    protocol: str
    metrics: dict[str, float] = Field(default_factory=dict)
    per_scenario_metrics: dict[str, dict[str, float]] = Field(default_factory=dict)
    hardware: str = Field(description="Dónde se evaluó (interpreta latencias)")
    evaluated_at: datetime
    notes: str | None = None


class HardwareValidation(ContractBase):
    """Celda de la matriz de compatibilidad hardware (docs/models/10 §matriz)."""

    target: str = Field(description="'mac-dev' | 'arm64-container' | 'rpi5'")
    status: HardwareValidationStatus = HardwareValidationStatus.NOT_TESTED
    metrics: dict[str, float] = Field(
        default_factory=dict, description="RAM MB, latencia ms, tokens/s, temperatura…"
    )
    validated_at: datetime | None = None
    notes: str | None = None


class ModelRegistryEntry(ContractBase):
    """Entrada del catálogo lógico común ML/LLM/EMBEDDING (docs/models/08).

    Durante el TFM el registro se materializa como filesystem + JSON en
    ``ai-models/registry/`` — no requiere servicio independiente.
    """

    model_id: str
    name: str
    model_family: str = Field(description="p. ej. 'lof', 'qwen2.5', 'all-MiniLM'")
    model_type: ModelType
    version: str = Field(description="Versión del ARTEFACTO entrenado (≠ algoritmo/features)")
    algorithm_version: str | None = Field(
        default=None, description="Versión de la implementación del algoritmo"
    )
    capabilities: list[ModelCapability] = Field(default_factory=list)
    status: ModelStatus = ModelStatus.EXPERIMENTAL
    artifact_format: str | None = Field(default=None, description="'onnx' | 'gguf' | …")
    artifact_uri: str | None = None
    checksum: str | None = None
    manifest_uri: str | None = Field(default=None, description="ModelManifest portable asociado")
    model_card_uri: str | None = Field(default=None, description="docs/models/model-cards/…")
    training_run_id: str | None = None
    created_at: datetime
    validated_at: datetime | None = None
    edge_compatible: bool | None = Field(
        default=None, description="None = no probado aún (nunca se asume)"
    )
    hardware_validation: list[HardwareValidation] = Field(default_factory=list)
    notes: str | None = None


class ModelDeployment(ContractBase):
    """Estado de despliegue en UN dispositivo edge, con rollback (docs/models/10 §rollback)."""

    deployment_id: str
    device_id: str
    active_model_id: str
    active_model_version: str
    previous_model_id: str | None = Field(
        default=None, description="Versión a la que volver si la activa falla"
    )
    previous_model_version: str | None = None
    activated_at: datetime
    activated_by: str = Field(default="manual", description="'manual' en el TFM (ADR-0022)")
    rollback_of: str | None = Field(
        default=None, description="deployment_id que este despliegue revierte"
    )
    notes: str | None = None


def validate_status_transition(current: ModelStatus, new: ModelStatus) -> None:
    """Lanza ValueError si la transición del ciclo de vida no está permitida."""
    if new not in ALLOWED_STATUS_TRANSITIONS[current]:
        allowed = sorted(s.value for s in ALLOWED_STATUS_TRANSITIONS[current])
        msg = (
            f"transición de estado no permitida: {current.value} → {new.value} (válidas: {allowed})"
        )
        raise ValueError(msg)
