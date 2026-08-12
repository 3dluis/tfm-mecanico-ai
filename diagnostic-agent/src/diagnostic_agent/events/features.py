"""Features por evento y firma de contexto (F6, docs/event-intelligence/06).

``event_features`` resume el tramo de telemetría de UN evento completo (clase DERIVED);
``build_context_signature`` produce la firma canónica que hace comparables eventos
equivalentes (mismo tipo, banda de velocidad, estado térmico y banda de duración).
"""

import itertools
import uuid

from mecanico_contracts import VehicleEvent
from mecanico_contracts.events_model import EventFeatureVector

EVENT_FEATURE_SCHEMA_VERSION = "efv:1"
PREPROCESSING_VERSION = "pp:1"

#: Nombres del esquema efv:1 (orden estable; los baselines dependen de él).
EVENT_FEATURE_NAMES: tuple[str, ...] = (
    "duration_s",
    "speed_start",
    "speed_end",
    "speed_delta",
    "speed_mean",
    "speed_max",
    "accel_mean_kmh_s",
    "accel_max_kmh_s",
    "rpm_mean",
    "rpm_max",
    "load_mean",
    "throttle_mean",
    "maf_mean",
    "maf_max",
    "maf_per_load",
    "stft_mean",
    "ltft_mean",
    "total_trim_mean",
    "map_mean",
    "coolant_mean",
)

_SPEED_BANDS = (0.0, 40.0, 80.0, 120.0)


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def event_features(window: dict[str, list[float]], sample_rate_hz: float = 1.0) -> dict[str, float]:
    """Features del esquema ``efv:1`` sobre el tramo de un evento (pid → serie)."""
    speed = window["SPEED"]
    n = len(speed)
    dur_s = n / sample_rate_hz
    accel = [(b - a) * sample_rate_hz for a, b in itertools.pairwise(speed)] or [0.0]
    maf, rpm, load = window["MAF"], window["RPM"], window["ENGINE_LOAD"]
    stft, ltft = window["SHORT_FUEL_TRIM_1"], window["LONG_FUEL_TRIM_1"]
    maf_per_load = _mean(
        [m / max(1.0, r * ld) * 1e4 for m, r, ld in zip(maf, rpm, load, strict=True)]
    )
    values = {
        "duration_s": dur_s,
        "speed_start": speed[0],
        "speed_end": speed[-1],
        "speed_delta": speed[-1] - speed[0],
        "speed_mean": _mean(speed),
        "speed_max": max(speed),
        "accel_mean_kmh_s": _mean(accel),
        "accel_max_kmh_s": max(accel),
        "rpm_mean": _mean(rpm),
        "rpm_max": max(rpm),
        "load_mean": _mean(load),
        "throttle_mean": _mean(window["THROTTLE_POS"]),
        "maf_mean": _mean(maf),
        "maf_max": max(maf),
        "maf_per_load": maf_per_load,
        "stft_mean": _mean(stft),
        "ltft_mean": _mean(ltft),
        "total_trim_mean": _mean([s + lt for s, lt in zip(stft, ltft, strict=True)]),
        "map_mean": _mean(window["INTAKE_PRESSURE"]),
        "coolant_mean": _mean(window["COOLANT_TEMP"]),
    }
    return {k: round(float(v), 4) for k, v in values.items()}


def _speed_band(v: float) -> str:
    for lo, hi in itertools.pairwise(_SPEED_BANDS):
        if v < hi:
            return f"{lo:.0f}-{hi:.0f}"
    return "120+"


def _thermal(coolant_mean: float) -> str:
    if coolant_mean < 60.0:
        return "cold"
    if coolant_mean < 80.0:
        return "warming"
    return "warm"


def _duration_band(dur_s: float) -> str:
    if dur_s < 8.0:
        return "d0-8s"
    if dur_s < 30.0:
        return "d8-30s"
    return "d30s+"


def build_context_signature(event_type: str, values: dict[str, float]) -> str:
    """Firma canónica, p. ej. ``ACCELERATION|0-40|warm|d8-30s`` (docs/ei/06 §firma)."""
    band = _speed_band(max(values["speed_start"], values["speed_end"]))
    return "|".join(
        [event_type, band, _thermal(values["coolant_mean"]), _duration_band(values["duration_s"])]
    )


def event_feature_vector(
    event: VehicleEvent,
    ticks: list[dict[str, float]],
    sample_rate_hz: float = 1.0,
) -> EventFeatureVector:
    """Construye el ``EventFeatureVector`` de un evento a partir de la sesión completa.

    El evento referencia la telemetría por ``seq_start/seq_end``; aquí se materializa el
    tramo sin duplicarlo en la persistencia (solo el resumen DERIVED se guarda).
    """
    s = event.seq_start or 0
    e = event.seq_end if event.seq_end is not None else len(ticks) - 1
    window = {pid: [t[pid] for t in ticks[s : e + 1]] for pid in ticks[0]}
    values = event_features(window, sample_rate_hz)
    return EventFeatureVector(
        efv_id=str(uuid.uuid4()),
        event_id=event.event_id,
        session_id=event.session_id,
        vehicle_id=event.vehicle_id,
        event_type=event.event_type,
        context_signature=build_context_signature(event.event_type, values),
        feature_schema_version=EVENT_FEATURE_SCHEMA_VERSION,
        preprocessing_version=PREPROCESSING_VERSION,
        detector_version=event.detector_version,
        values=values,
    )
