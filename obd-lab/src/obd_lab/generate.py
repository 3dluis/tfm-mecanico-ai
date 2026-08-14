"""Generación de sesiones reproducibles: ScenarioSpec → JSONL (cabecera + OBDReadings)."""

import random
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

from mecanico_contracts import OBDReading, RecordedSession, ScenarioSpec, TransportKind
from mecanico_contracts.features import CANONICAL_PIDS
from mecanico_contracts.session_io import read_session_series, write_session_file
from obd_lab.emulator.encoding import quantize_tick
from obd_lab.injection.faults import CATALOG, FaultRuntime
from obd_lab.signals import SignalEngine

_UNITS: dict[str, str] = {
    "RPM": "rpm",
    "SPEED": "kph",
    "ENGINE_LOAD": "percent",
    "COOLANT_TEMP": "degC",
    "INTAKE_TEMP": "degC",
    "MAF": "gps",
    "THROTTLE_POS": "percent",
    "SHORT_FUEL_TRIM_1": "percent",
    "LONG_FUEL_TRIM_1": "percent",
    "O2_B1S1": "volt",
    "TIMING_ADVANCE": "degree",
    "INTAKE_PRESSURE": "kilopascal",
}

#: Época simulada fija: las sesiones sintéticas son reproducibles byte a byte.
_SIM_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)


def iter_ticks_labeled(spec: ScenarioSpec) -> Iterator[tuple[dict[str, float], str]]:
    """Como :func:`iter_ticks`, pero acompaña cada tick con la fase interna del motor.

    La etiqueta de fase (``idle``/``accel``/``cruise``/``vary``/``decel``) es estado
    PRIVADO del generador: alimenta el ground truth de eventos (F6, ADR-0019) y NUNCA
    debe llegar al detector en inferencia.
    """
    engine = SignalEngine(
        profile=spec.driving_profile,
        seed=spec.seed,
        ambient_temp_c=spec.ambient_temp_c,
        sample_rate_hz=spec.sample_rate_hz,
    )
    fault = CATALOG[spec.fault] if spec.fault else None
    params = dict(fault.default_params) if fault else {}
    params.update(spec.fault_params)
    # Separación de generadores aleatorios (ADR-0034, F20). Con `anomaly_seed` la
    # inyección usa su PROPIO generador: no consume extracciones del motor de señales, de
    # modo que la trayectoria normal es idéntica fuera de la región intervenida y los
    # contrafactuales quedan limpios. Sin `anomaly_seed` se conserva el comportamiento
    # heredado (RNG compartido) para reproducir byte a byte los datasets v1.
    fault_rng = random.Random(spec.anomaly_seed) if spec.anomaly_seed is not None else engine.rng
    runtime = FaultRuntime(rng=fault_rng)

    n = int(spec.duration_s * spec.sample_rate_hz)
    start = spec.fault_start_s if spec.fault_start_s is not None else 0.0
    end = spec.fault_end_s if spec.fault_end_s is not None else spec.duration_s

    for i in range(n):
        t = i / spec.sample_rate_hz
        values = engine.tick()
        if fault and start <= t < end:
            runtime.elapsed_s = t - start
            values = fault.apply(values, t, params, runtime)
        # Cuantización J1979: misma resolución que el camino vivo (ver encoding.quantize).
        yield quantize_tick(values), engine.state.phase


def iter_ticks(spec: ScenarioSpec) -> Iterator[dict[str, float]]:
    """Genera tick a tick los valores de PIDs aplicando el fallo en su ventana.

    Iterador para poder alimentar tanto la generación offline como el emulador en vivo.
    """
    for values, _phase in iter_ticks_labeled(spec):
        yield values


def generate_ticks(spec: ScenarioSpec) -> list[dict[str, float]]:
    """Matriz completa de ticks (uso offline)."""
    return list(iter_ticks(spec))


def write_session(
    spec: ScenarioSpec,
    out_dir: Path,
    vehicle_id: str = "veh-sim",
    device_id: str = "obd-lab",
) -> Path:
    """Escribe la sesión en el formato común (shared.session_io)."""
    ticks = generate_ticks(spec)
    session_id = f"{spec.scenario_id}-seed{spec.seed}"
    header = RecordedSession(
        session_id=session_id,
        created_at=_SIM_EPOCH,
        origin="synthetic",
        scenario=spec,
        vehicle_id=vehicle_id,
        device_id=device_id,
        n_readings=len(ticks) * len(CANONICAL_PIDS),
        pids=list(CANONICAL_PIDS),
    )

    def _readings() -> Iterator[OBDReading]:
        for i, values in enumerate(ticks):
            ts = _SIM_EPOCH + timedelta(seconds=i / spec.sample_rate_hz)
            for pid in CANONICAL_PIDS:
                yield OBDReading(
                    timestamp=ts,
                    pid=pid,
                    value=round(values[pid], 4),
                    unit=_UNITS[pid],
                    vehicle_id=vehicle_id,
                    device_id=device_id,
                    source=TransportKind.TCP,
                )

    path = out_dir / f"{session_id}.jsonl"
    return write_session_file(header, _readings(), path)


# Reexport de conveniencia para consumidores del laboratorio.
read_session = read_session_series
