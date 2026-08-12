"""Ground truth de eventos vehiculares del laboratorio (F6, ADR-0019).

El generador CONOCE el régimen que comanda en cada tick (fase del ``SignalEngine``) y las
condiciones iniciales (arranque en frío, motor en marcha). De ese conocimiento privado
deriva los ``VehicleEvent`` de referencia contra los que se evalúa el detector.

Reglas de aislamiento (RI1 aplicado a eventos):
- El detector NUNCA recibe estas etiquetas en inferencia; solo el evaluador las usa.
- El ground truth se define sobre lo que el simulador HIZO (fases + señal resultante),
  no sobre lo que el detector debería encontrar.
"""

import uuid
from datetime import UTC, datetime, timedelta

from mecanico_contracts import ScenarioSpec, VehicleEvent
from mecanico_contracts.events_model import EventClass
from obd_lab.generate import iter_ticks_labeled

__all__ = ["GT_DETECTOR_VERSION", "generate_with_events", "ground_truth_events"]

GT_DETECTOR_VERSION = "obd-lab-gt:1"

#: Época simulada fija (idéntica a generate._SIM_EPOCH; sesiones reproducibles).
_SIM_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)

#: Fase interna del motor → (event_type, event_class de la taxonomía v1).
_PHASE_EVENT: dict[str, tuple[str, EventClass]] = {
    "idle": ("IDLE", EventClass.OBSERVED),
    "accel": ("ACCELERATION", EventClass.OBSERVED),
    "cruise": ("CONSTANT_SPEED", EventClass.OBSERVED),
    "vary": ("CONSTANT_SPEED", EventClass.OBSERVED),  # crucero con variaciones suaves
    "decel": ("DECELERATION", EventClass.OBSERVED),
}

_COLD_START_MAX_C = 40.0  # coolant inicial por debajo ⇒ arranque en frío


def _mk_event(
    *,
    session_id: str,
    vehicle_id: str,
    event_type: str,
    event_class: EventClass,
    seq_start: int,
    seq_end: int,
    dt_s: float,
    evidence: list[str],
    parent_event_id: str | None = None,
    event_subtype: str | None = None,
) -> VehicleEvent:
    start = _SIM_EPOCH + timedelta(seconds=seq_start * dt_s)
    end = _SIM_EPOCH + timedelta(seconds=(seq_end + 1) * dt_s)
    return VehicleEvent(
        event_id=str(uuid.uuid4()),
        vehicle_id=vehicle_id,
        session_id=session_id,
        event_type=event_type,
        event_subtype=event_subtype,
        event_class=event_class,
        parent_event_id=parent_event_id,
        start_time=start,
        end_time=end,
        duration_ms=int((seq_end + 1 - seq_start) * dt_s * 1000),
        seq_start=seq_start,
        seq_end=seq_end,
        confidence=1.0,  # ground truth por construcción
        detection_method="ground_truth:phases",
        detector_version=GT_DETECTOR_VERSION,
        source_sensors=["simulator"],
        evidence=evidence,
        created_at=_SIM_EPOCH,
    )


def ground_truth_events(
    spec: ScenarioSpec,
    labeled: list[tuple[dict[str, float], str]],
    vehicle_id: str = "veh-sim",
    session_id: str | None = None,
) -> list[VehicleEvent]:
    """Deriva los eventos de referencia de una sesión etiquetada por fases.

    Jerarquía: un ``TRIP`` contenedor (toda la sesión con motor en marcha) es padre de
    los eventos de fase (IDLE/ACCELERATION/CONSTANT_SPEED/DECELERATION); ENGINE_START/
    ENGINE_STOP/COLD_START son eventos puntuales hijos del TRIP.
    """
    if not labeled:
        return []
    sid = session_id or f"{spec.scenario_id}-seed{spec.seed}"
    dt_s = 1.0 / spec.sample_rate_hz
    n = len(labeled)
    events: list[VehicleEvent] = []

    trip = _mk_event(
        session_id=sid,
        vehicle_id=vehicle_id,
        event_type="TRIP",
        event_class=EventClass.INFERRED,
        seq_start=0,
        seq_end=n - 1,
        dt_s=dt_s,
        evidence=[f"sesión sintética completa del perfil '{spec.driving_profile}'"],
    )
    events.append(trip)

    # Motor en marcha desde el tick 0 en el simulador actual: ENGINE_START puntual en t0.
    first_values = labeled[0][0]
    events.append(
        _mk_event(
            session_id=sid,
            vehicle_id=vehicle_id,
            event_type="ENGINE_START",
            event_class=EventClass.OBSERVED,
            seq_start=0,
            seq_end=0,
            dt_s=dt_s,
            parent_event_id=trip.event_id,
            evidence=[f"RPM={first_values['RPM']:.0f} > 0 en el primer tick de la sesión"],
        )
    )
    if first_values["COOLANT_TEMP"] < _COLD_START_MAX_C:
        events.append(
            _mk_event(
                session_id=sid,
                vehicle_id=vehicle_id,
                event_type="COLD_START",
                event_class=EventClass.INFERRED,
                seq_start=0,
                seq_end=0,
                dt_s=dt_s,
                parent_event_id=trip.event_id,
                evidence=[
                    f"COOLANT_TEMP inicial={first_values['COOLANT_TEMP']:.0f}°C "
                    f"< {_COLD_START_MAX_C:.0f}°C"
                ],
            )
        )

    # Segmentos contiguos de fase → eventos de régimen.
    run_start = 0
    run_phase = labeled[0][1]
    for i in range(1, n + 1):
        phase = labeled[i][1] if i < n else None
        if phase == run_phase:
            continue
        etype, eclass = _PHASE_EVENT[run_phase]
        events.append(
            _mk_event(
                session_id=sid,
                vehicle_id=vehicle_id,
                event_type=etype,
                event_subtype=run_phase if run_phase == "vary" else None,
                event_class=eclass,
                seq_start=run_start,
                seq_end=i - 1,
                dt_s=dt_s,
                parent_event_id=trip.event_id,
                evidence=[
                    f"fase '{run_phase}' comandada por el perfil (ticks {run_start}–{i - 1})"
                ],
            )
        )
        run_start, run_phase = i, phase  # type: ignore[assignment]

    events.append(
        _mk_event(
            session_id=sid,
            vehicle_id=vehicle_id,
            event_type="ENGINE_STOP",
            event_class=EventClass.OBSERVED,
            seq_start=n - 1,
            seq_end=n - 1,
            dt_s=dt_s,
            parent_event_id=trip.event_id,
            evidence=["fin de la sesión simulada (último tick con motor en marcha)"],
        )
    )
    return events


def generate_with_events(
    spec: ScenarioSpec,
    vehicle_id: str = "veh-sim",
    session_id: str | None = None,
) -> tuple[list[dict[str, float]], list[VehicleEvent]]:
    """Genera la sesión y su ground truth de eventos en una pasada.

    Devuelve ``(ticks, eventos)``. Los ticks son idénticos a :func:`generate_ticks`
    (misma semilla ⇒ misma serie); las etiquetas de fase no salen de esta función.
    """
    labeled = list(iter_ticks_labeled(spec))
    ticks = [values for values, _ in labeled]
    return ticks, ground_truth_events(spec, labeled, vehicle_id, session_id)
