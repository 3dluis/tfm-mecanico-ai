"""Snapshot builder — TelemetryPoint/OBDObservation → VehicleTelemetrySnapshot (F11).

Implementa la política de alineación temporal **sync:v1** (ADR-0026): rejilla canónica
de ``interval_ms`` anclada al inicio de sesión; para cada señal se toma la muestra más
cercana dentro de ±``alignment_window_ms``; si no hay muestra → ``None`` + flag
``missing`` (NULL ≠ 0, ADR-0027); si se reutiliza la última muestra conocida (dentro de
``stale_tolerance_ms``) → flag ``stale``. PIDs del ciclo de sondeo ausentes de la fuente
→ ``not_polled``. La frecuencia es configurable: 1 Hz es la validada por la adquisición
actual; 5 Hz sigue siendo candidato sin validar (ADR-0026 §frecuencia).

El snapshot NUNCA contiene features (medias, correlaciones…): solo estado alineado.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from mecanico_contracts import (
    OBDReading,
    SignalQuality,
    SnapshotEventLink,
    VehicleEvent,
    VehicleTelemetrySnapshot,
)
from mecanico_contracts.snapshot_model import SYNC_VERSION

#: PID canónico (python-OBD) → campo del snapshot. Los campos sin PID en el ciclo de
#: sondeo actual (fuel_pressure, battery_voltage, IMU, GPS…) quedan None+not_polled.
PID_TO_FIELD: dict[str, str] = {
    "RPM": "rpm",
    "SPEED": "vehicle_speed",
    "THROTTLE_POS": "throttle_position",
    "ENGINE_LOAD": "engine_load",
    "COOLANT_TEMP": "coolant_temperature",
    "INTAKE_TEMP": "intake_air_temperature",
    "MAF": "maf",
    "INTAKE_PRESSURE": "map_kpa",
    "SHORT_FUEL_TRIM_1": "stft_bank1",
    "LONG_FUEL_TRIM_1": "ltft_bank1",
    "O2_B1S1": "o2_sensor_1",
    "TIMING_ADVANCE": "timing_advance",
}


@dataclass(frozen=True)
class AlignmentConfig:
    """Parámetros de sync:v1 (se registran vía synchronization_version + interval)."""

    interval_ms: int = 1000  # 1 Hz validado; 5 Hz = candidato sin validar
    alignment_window_ms: int = 500  # ± ventana de búsqueda de la muestra más cercana
    stale_tolerance_ms: int = 2000  # máximo para reutilizar la última muestra (flag stale)


@dataclass
class _EventIndex:
    """Índice de eventos por seq para primary/trip/links (sin duplicar snapshots)."""

    events: list[VehicleEvent] = field(default_factory=list)

    def covering(self, seq: int) -> list[VehicleEvent]:
        return [
            e
            for e in self.events
            if e.seq_start is not None and e.seq_end is not None and e.seq_start <= seq <= e.seq_end
        ]

    def context_for(
        self, seq: int
    ) -> tuple[str | None, str | None, str | None, list[VehicleEvent]]:
        cov = self.covering(seq)
        trip = next((e for e in cov if e.event_type == "TRIP"), None)
        leaves = [e for e in cov if e.event_type != "TRIP"]
        primary = min(
            leaves,
            key=lambda e: (e.seq_end or 0) - (e.seq_start or 0),
            default=None,
        )
        return (
            trip.event_id if trip else None,
            primary.event_id if primary else None,
            primary.event_type if primary else None,
            cov,
        )


def _mk_snapshot(
    *,
    session_id: str,
    vehicle_id: str,
    device_id: str,
    seq: int,
    ts: datetime,
    values: dict[str, float],
    flags: dict[str, SignalQuality],
    cfg: AlignmentConfig,
    idx: _EventIndex,
    now: datetime,
) -> tuple[VehicleTelemetrySnapshot, list[SnapshotEventLink]]:
    trip_id, primary_id, primary_type, covering = idx.context_for(seq)
    polled = set(PID_TO_FIELD)
    n_expected = len(polled)
    n_bad = sum(1 for p in polled if PID_TO_FIELD[p] in flags)
    signals: dict[str, Any] = {PID_TO_FIELD[p]: values.get(PID_TO_FIELD[p]) for p in polled}
    snapshot = VehicleTelemetrySnapshot(
        snapshot_id=str(uuid.uuid4()),
        vehicle_id=vehicle_id,
        device_id=device_id,
        session_id=session_id,
        trip_id=trip_id,
        timestamp_utc=ts,
        sequence_number=seq,
        snapshot_interval_ms=cfg.interval_ms,
        synchronization_version=SYNC_VERSION,
        primary_event_id=primary_id,
        primary_event_type=primary_type,
        quality_score=round((n_expected - n_bad) / n_expected, 4) if n_expected else 1.0,
        missing_metric_count=n_bad,
        quality_flags=flags,
        created_at=now,
        **signals,
    )
    links = [
        SnapshotEventLink(
            snapshot_id=snapshot.snapshot_id, event_id=e.event_id, event_type=e.event_type
        )
        for e in covering
    ]
    return snapshot, links


def build_from_ticks(
    ticks: list[dict[str, float]],
    session_id: str,
    vehicle_id: str,
    device_id: str = "obd-lab",
    events: list[VehicleEvent] | None = None,
    cfg: AlignmentConfig | None = None,
    epoch: datetime | None = None,
) -> tuple[list[VehicleTelemetrySnapshot], list[SnapshotEventLink]]:
    """Camino rápido: los ticks del laboratorio YA están en rejilla (1 tick = 1 paso).

    La alineación es identidad (todas las señales presentes → measured); los PIDs del
    esquema no sondeados quedan None+not_polled.
    """
    cfg = cfg or AlignmentConfig()
    epoch = epoch or datetime(2026, 1, 1, tzinfo=UTC)
    idx = _EventIndex(events or [])
    now = epoch
    snapshots: list[VehicleTelemetrySnapshot] = []
    links: list[SnapshotEventLink] = []
    for seq, tick in enumerate(ticks):
        values: dict[str, float] = {}
        flags: dict[str, SignalQuality] = {}
        for pid, fname in PID_TO_FIELD.items():
            if pid in tick:
                values[fname] = float(tick[pid])
            else:
                flags[fname] = SignalQuality.NOT_POLLED
        snap, snap_links = _mk_snapshot(
            session_id=session_id,
            vehicle_id=vehicle_id,
            device_id=device_id,
            seq=seq,
            ts=epoch + timedelta(milliseconds=seq * cfg.interval_ms),
            values=values,
            flags=flags,
            cfg=cfg,
            idx=idx,
            now=now,
        )
        snapshots.append(snap)
        links.extend(snap_links)
    return snapshots, links


def build_from_observations(
    observations: list[OBDReading],
    session_id: str,
    events: list[VehicleEvent] | None = None,
    cfg: AlignmentConfig | None = None,
) -> tuple[list[VehicleTelemetrySnapshot], list[SnapshotEventLink]]:
    """Camino general sync:v1: observaciones RAW con timestamps dispares → rejilla.

    Para cada instante canónico y cada PID sondeado: muestra más cercana dentro de
    ±alignment_window_ms (measured) → si no, última muestra dentro de
    stale_tolerance_ms (stale) → si no, None (missing).
    """
    cfg = cfg or AlignmentConfig()
    if not observations:
        return [], []
    obs_sorted = sorted(observations, key=lambda o: o.timestamp)
    t0 = obs_sorted[0].timestamp
    t_end = obs_sorted[-1].timestamp
    by_pid: dict[str, list[OBDReading]] = {}
    for o in obs_sorted:
        if o.pid in PID_TO_FIELD:
            by_pid.setdefault(o.pid, []).append(o)
    idx = _EventIndex(events or [])
    vehicle_id = obs_sorted[0].vehicle_id
    device_id = obs_sorted[0].device_id
    n_steps = int((t_end - t0).total_seconds() * 1000 // cfg.interval_ms) + 1
    cursors = dict.fromkeys(by_pid, 0)
    snapshots: list[VehicleTelemetrySnapshot] = []
    links: list[SnapshotEventLink] = []
    for seq in range(n_steps):
        ts = t0 + timedelta(milliseconds=seq * cfg.interval_ms)
        values: dict[str, float] = {}
        flags: dict[str, SignalQuality] = {}
        for pid, fname in PID_TO_FIELD.items():
            series = by_pid.get(pid)
            if not series:
                flags[fname] = SignalQuality.NOT_POLLED
                continue
            i = cursors[pid]
            while i + 1 < len(series) and series[i + 1].timestamp <= ts:
                i += 1
            cursors[pid] = i
            best = series[i]
            if i + 1 < len(series):
                nxt = series[i + 1]
                if abs((nxt.timestamp - ts).total_seconds()) < abs(
                    (best.timestamp - ts).total_seconds()
                ):
                    best = nxt
            delta_ms = abs((best.timestamp - ts).total_seconds()) * 1000
            if delta_ms <= cfg.alignment_window_ms:
                values[fname] = best.value
            elif (
                best.timestamp <= ts
                and (ts - best.timestamp).total_seconds() * 1000 <= cfg.stale_tolerance_ms
            ):
                values[fname] = best.value
                flags[fname] = SignalQuality.STALE
            else:
                flags[fname] = SignalQuality.MISSING
        snap, snap_links = _mk_snapshot(
            session_id=session_id,
            vehicle_id=vehicle_id,
            device_id=device_id,
            seq=seq,
            ts=ts,
            values=values,
            flags=flags,
            cfg=cfg,
            idx=idx,
            now=t0,
        )
        snapshots.append(snap)
        links.extend(snap_links)
    return snapshots, links
