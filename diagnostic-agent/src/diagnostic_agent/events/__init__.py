"""Event Intelligence del edge (F6, ADR-0019/0020/0021).

Detección determinista de eventos (máquina de estados sobre telemetría), features por
evento, baselines contextuales por vehículo y anomalías contextuales. El LLM no participa
en la detección de eventos (docs/event-intelligence/04).
"""

from diagnostic_agent.events.baseline import build_baseline, score_against_baseline
from diagnostic_agent.events.detector import DETECTOR_VERSION, DetectorConfig, detect_events
from diagnostic_agent.events.features import (
    EVENT_FEATURE_SCHEMA_VERSION,
    build_context_signature,
    event_feature_vector,
    event_features,
)

__all__ = [
    "DETECTOR_VERSION",
    "EVENT_FEATURE_SCHEMA_VERSION",
    "DetectorConfig",
    "build_baseline",
    "build_context_signature",
    "detect_events",
    "event_feature_vector",
    "event_features",
    "score_against_baseline",
]
