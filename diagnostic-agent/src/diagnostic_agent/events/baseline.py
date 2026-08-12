"""Baselines por vehículo y contexto + anomalía contextual (F6, ADR-0021).

Un ``EventBaseline`` acumula la distribución de features de los eventos NORMALES de un
vehículo en un contexto (``context_signature``). Un evento nuevo se compara contra su
baseline con z-scores robustos; la desviación produce una ``DetectedAnomaly`` con
``anomaly_scope=EVENT`` — matemática pura, sin LLM (separación ML/LLM intacta).
"""

import statistics
import uuid
from datetime import UTC, datetime

from mecanico_contracts import DetectedAnomaly, DetectorKind
from mecanico_contracts.data_enums import AnomalyScope
from mecanico_contracts.events_model import EventBaseline, EventFeatureVector

#: Mínimo de muestras para que un baseline sea utilizable en detección (docs/ei/07).
MIN_SAMPLES = 5
#: Umbral por defecto de |z| máximo para señalar anomalía contextual (a calibrar).
DEFAULT_Z_THRESHOLD = 4.0

_BASELINE_DETECTOR_NAME = "event-baseline-z"
_BASELINE_VERSION = "0.1.0"


def _percentile(sorted_xs: list[float], q: float) -> float:
    if not sorted_xs:
        return 0.0
    idx = min(len(sorted_xs) - 1, max(0, round(q * (len(sorted_xs) - 1))))
    return sorted_xs[idx]


def build_baseline(
    efvs: list[EventFeatureVector],
    now: datetime | None = None,
    version: int = 1,
) -> EventBaseline:
    """Construye el baseline de UN contexto a partir de EFVs normales homogéneos."""
    if not efvs:
        msg = "se requiere al menos un EventFeatureVector"
        raise ValueError(msg)
    ctx = {
        (e.vehicle_id, e.event_type, e.context_signature, e.feature_schema_version) for e in efvs
    }
    if len(ctx) != 1:
        msg = f"los EFVs mezclan contextos/vehículos/esquemas: {sorted(ctx)}"
        raise ValueError(msg)
    vehicle_id, event_type, signature, schema_v = next(iter(ctx))
    ts = now or datetime.now(UTC)
    features = sorted(efvs[0].values)
    dist: dict[str, dict[str, float]] = {}
    centroid: dict[str, float] = {}
    for name in features:
        xs = sorted(e.values[name] for e in efvs)
        mean = statistics.fmean(xs)
        std = statistics.stdev(xs) if len(xs) > 1 else 0.0
        dist[name] = {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "p05": round(_percentile(xs, 0.05), 4),
            "p50": round(_percentile(xs, 0.50), 4),
            "p95": round(_percentile(xs, 0.95), 4),
        }
        centroid[name] = round(mean, 4)
    return EventBaseline(
        baseline_id=str(uuid.uuid4()),
        vehicle_id=vehicle_id,
        event_type=event_type,
        context_signature=signature,
        sample_count=len(efvs),
        feature_distribution=dist,
        centroid=centroid,
        feature_schema_version=schema_v,
        first_seen=ts,
        last_updated=ts,
        version=version,
        confidence=round(min(1.0, len(efvs) / 20.0), 2),
    )


def score_against_baseline(efv: EventFeatureVector, baseline: EventBaseline) -> dict[str, float]:
    """Z-score por feature vía media/σ (v1; suelo de σ para evitar explosiones con σ≈0)."""
    scores: dict[str, float] = {}
    for name, d in baseline.feature_distribution.items():
        if name not in efv.values:
            continue
        floor = max(d["std"], 0.05 * abs(d["mean"]), 1e-3)
        scores[name] = round((efv.values[name] - d["mean"]) / floor, 3)
    return scores


def score_against_baseline_robust(
    efv: EventFeatureVector, baseline: EventBaseline
) -> dict[str, float]:
    """Z-score ROBUSTO por feature: mediana (p50) + σ robusta de percentiles (F9).

    σ_robusta = (p95 − p05) / 3.29 (rango que cubriría ±1.645σ en una normal). Mismos
    suelos que la versión media/σ. Usa SOLO campos ya presentes en ``EventBaseline``
    (p05/p50/p95): sin cambio de contrato ni de baselines persistidos — las dos
    puntuaciones son comparables sobre los mismos artefactos (ADR de EXP-ANOM-003).
    """
    scores: dict[str, float] = {}
    for name, d in baseline.feature_distribution.items():
        if name not in efv.values:
            continue
        sigma_r = (d["p95"] - d["p05"]) / 3.29
        floor = max(sigma_r, 0.05 * abs(d["p50"]), 1e-3)
        scores[name] = round((efv.values[name] - d["p50"]) / floor, 3)
    return scores


def contextual_anomaly(
    efv: EventFeatureVector,
    baseline: EventBaseline,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
    now: datetime | None = None,
) -> DetectedAnomaly | None:
    """Evalúa un evento contra su baseline; None si es normal o el baseline es inmaduro.

    La anomalía resultante lleva ``anomaly_scope=EVENT`` + ``event_id`` + ``baseline_id``
    (trazable hasta el RAW vía VehicleEvent.seq_start/seq_end → TelemetryPoint).
    """
    if baseline.sample_count < MIN_SAMPLES:
        return None
    if efv.context_signature != baseline.context_signature:
        msg = (
            f"contexto del EFV ({efv.context_signature}) ≠ baseline "
            f"({baseline.context_signature}): eventos no comparables"
        )
        raise ValueError(msg)
    scores = score_against_baseline(efv, baseline)
    max_z = max(scores.values(), key=abs)
    if abs(max_z) < z_threshold:
        return None
    involved = sorted(
        (k for k, v in scores.items() if abs(v) >= z_threshold),
        key=lambda k: -abs(scores[k]),
    )
    return DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        window_id=None,
        event_id=efv.event_id,
        baseline_id=baseline.baseline_id,
        anomaly_scope=AnomalyScope.EVENT,
        session_id=efv.session_id,
        vehicle_id=efv.vehicle_id,
        detected_at=now or datetime.now(UTC),
        detector=DetectorKind.ZSCORE,
        model_name=_BASELINE_DETECTOR_NAME,
        model_version=_BASELINE_VERSION,
        score=round(abs(max_z), 3),
        threshold=z_threshold,
        involved_pids=involved,
        features={k: efv.values[k] for k in involved if k in efv.values}
        | {f"z:{k}": scores[k] for k in involved},
    )
