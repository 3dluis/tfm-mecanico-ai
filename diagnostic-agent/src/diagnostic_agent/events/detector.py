"""Detector determinista de eventos vehiculares (máquina de estados; ADR-0019).

Entrada: series de PIDs de una sesión (el detector NUNCA ve etiquetas de ground truth).
Salida: ``VehicleEvent`` con confianza, método, versión y evidencias verificables.

Diseño (docs/event-intelligence/03 y 04): estados sobre velocidad suavizada y su derivada
con histéresis (umbral de entrada > umbral de salida), duración mínima y fusión de huecos.
Los umbrales iniciales provienen de la física del simulador y quedan marcados como
pendientes de validación con datos reales.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from mecanico_contracts import VehicleEvent
from mecanico_contracts.events_model import EventClass

DETECTOR_VERSION = "ed:1"
_METHOD = "state_machine:v1"

#: Época simulada de obd-lab (los timestamps de eventos se derivan de seq × dt).
_SIM_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)


@dataclass(frozen=True)
class DetectorConfig:
    """Umbrales del detector v1 (calibrados contra el simulador; a validar con HCRL)."""

    rpm_engine_on: float = 400.0
    speed_moving_kmh: float = 3.0  # por encima ⇒ en movimiento
    speed_idle_kmh: float = 2.0  # por debajo (y motor en marcha) ⇒ candidato a IDLE
    accel_enter_kmh_s: float = 0.9  # entrada en ACCELERATION (histéresis)
    accel_exit_kmh_s: float = 0.45  # salida de ACCELERATION
    smooth_n: int = 3  # ticks de suavizado de la derivada (SPEED cuantizada a 1 km/h)
    min_duration_ticks: int = 3  # eventos más cortos se fusionan con el vecino
    sample_rate_hz: float = 1.0


def _states(ticks: list[dict[str, float]], cfg: DetectorConfig) -> list[str]:
    """Asigna a cada tick un estado de régimen con histéresis en la aceleración."""
    speed = [t["SPEED"] for t in ticks]
    n = len(ticks)
    accel = [0.0] * n
    for i in range(n):
        j = max(0, i - cfg.smooth_n)
        if i > j:
            accel[i] = (speed[i] - speed[j]) / ((i - j) / cfg.sample_rate_hz)
    out: list[str] = []
    prev = "IDLE"
    for i in range(n):
        a, v = accel[i], speed[i]
        if ticks[i]["RPM"] < cfg.rpm_engine_on:
            state = "ENGINE_OFF"
        elif v <= cfg.speed_idle_kmh and abs(a) < cfg.accel_exit_kmh_s:
            state = "IDLE"
        elif a >= cfg.accel_enter_kmh_s or (prev == "ACCELERATION" and a >= cfg.accel_exit_kmh_s):
            state = "ACCELERATION"
        elif a <= -cfg.accel_enter_kmh_s or (prev == "DECELERATION" and a <= -cfg.accel_exit_kmh_s):
            state = "DECELERATION"
        elif v > cfg.speed_moving_kmh:
            state = "CONSTANT_SPEED"
        else:
            state = "IDLE"
        out.append(state)
        prev = state
    return out


def _segments(states: list[str], min_len: int) -> list[tuple[str, int, int]]:
    """Comprime estados en segmentos (estado, seq_ini, seq_fin) y absorbe los cortos."""
    segs: list[tuple[str, int, int]] = []
    start = 0
    for i in range(1, len(states) + 1):
        if i < len(states) and states[i] == states[start]:
            continue
        segs.append((states[start], start, i - 1))
        start = i
    # Fusión: un segmento más corto que min_len se absorbe en el vecino más largo.
    changed = True
    while changed and len(segs) > 1:
        changed = False
        for k, (_name, s, e) in enumerate(segs):
            if e - s + 1 >= min_len:
                continue
            left = segs[k - 1] if k > 0 else None
            right = segs[k + 1] if k + 1 < len(segs) else None
            host = max(
                (x for x in (left, right) if x is not None),
                key=lambda x: x[2] - x[1],
            )
            merged = (host[0], min(host[1], s), max(host[2], e))
            idx = segs.index(host)
            lo, hi = min(idx, k), max(idx, k)
            segs[lo : hi + 1] = [merged]
            changed = True
            break
    # Re-fusión de vecinos que quedaron con el mismo estado.
    out: list[tuple[str, int, int]] = []
    for seg in segs:
        if out and out[-1][0] == seg[0]:
            out[-1] = (seg[0], out[-1][1], seg[2])
        else:
            out.append(seg)
    return out


def _confidence(
    name: str, s: int, e: int, ticks: list[dict[str, float]], cfg: DetectorConfig
) -> tuple[float, list[str]]:
    """Confianza heurística basada en el margen sobre el umbral + evidencia textual."""
    speed = [t["SPEED"] for t in ticks[s : e + 1]]
    dur = e - s + 1
    if name in ("ACCELERATION", "DECELERATION"):
        delta = abs(speed[-1] - speed[0]) / max(1.0, dur / cfg.sample_rate_hz)
        margin = min(1.0, delta / cfg.accel_enter_kmh_s)
        ev = [
            f"|Δv| medio {delta:.2f} km/h/s (umbral {cfg.accel_enter_kmh_s}) "
            f"durante {dur} ticks (seq {s}–{e})"
        ]
        return round(0.6 + 0.35 * margin, 2), ev
    if name == "IDLE":
        vmax = max(speed)
        ev = [f"SPEED ≤ {vmax:.0f} km/h con motor en marcha durante {dur} ticks (seq {s}–{e})"]
        return 0.95, ev
    ev = [f"velocidad sostenida {min(speed):.0f}–{max(speed):.0f} km/h, seq {s}–{e}"]
    return 0.85, ev


def detect_events(
    ticks: list[dict[str, float]],
    session_id: str,
    vehicle_id: str,
    config: DetectorConfig | None = None,
    epoch: datetime = _SIM_EPOCH,
) -> list[VehicleEvent]:
    """Segmenta una sesión en eventos. Determinista: misma entrada ⇒ mismos eventos."""
    if not ticks:
        return []
    cfg = config or DetectorConfig()
    dt_s = 1.0 / cfg.sample_rate_hz
    now = epoch

    def mk(
        etype: str,
        eclass: EventClass,
        s: int,
        e: int,
        conf: float,
        evidence: list[str],
        parent: str | None,
        method: str = _METHOD,
    ) -> VehicleEvent:
        return VehicleEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            session_id=session_id,
            event_type=etype,
            event_class=eclass,
            parent_event_id=parent,
            start_time=epoch + timedelta(seconds=s * dt_s),
            end_time=epoch + timedelta(seconds=(e + 1) * dt_s),
            duration_ms=int((e + 1 - s) * dt_s * 1000),
            seq_start=s,
            seq_end=e,
            confidence=conf,
            detection_method=method,
            detector_version=DETECTOR_VERSION,
            source_sensors=["obd"],
            evidence=evidence,
            created_at=now,
        )

    n = len(ticks)
    events: list[VehicleEvent] = []
    trip = mk(
        "TRIP",
        EventClass.INFERRED,
        0,
        n - 1,
        0.9,
        ["contenedor: sesión con motor en marcha de principio a fin"],
        None,
    )
    events.append(trip)

    if ticks[0]["RPM"] >= cfg.rpm_engine_on:
        events.append(
            mk(
                "ENGINE_START",
                EventClass.OBSERVED,
                0,
                0,
                0.95,
                [f"RPM={ticks[0]['RPM']:.0f} ≥ {cfg.rpm_engine_on:.0f} en el primer tick"],
                trip.event_id,
                method="rule:v1",
            )
        )

    for name, s, e in _segments(_states(ticks, cfg), cfg.min_duration_ticks):
        if name == "ENGINE_OFF":
            continue
        conf, evidence = _confidence(name, s, e, ticks, cfg)
        events.append(mk(name, EventClass.OBSERVED, s, e, conf, evidence, trip.event_id))

    # Fin de stream con motor en marcha: ENGINE_STOP solo ESTIMATED (no observado).
    events.append(
        mk(
            "ENGINE_STOP",
            EventClass.ESTIMATED,
            n - 1,
            n - 1,
            0.5,
            ["fin del stream de telemetría; parada de motor no observada directamente"],
            trip.event_id,
            method="rule:v1",
        )
    )
    return events
