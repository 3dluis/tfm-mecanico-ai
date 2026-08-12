"""Normalización y ventanas deslizantes sobre el flujo de lecturas."""

import uuid
from datetime import datetime

from mecanico_contracts import OBDReading, VehicleTelemetry
from mecanico_contracts.features import CANONICAL_PIDS

#: Rangos físicos plausibles por PID (validación de lecturas; fuera de rango = descarte).
_VALID_RANGES: dict[str, tuple[float, float]] = {
    "RPM": (0.0, 8000.0),
    "SPEED": (0.0, 250.0),
    "ENGINE_LOAD": (0.0, 100.0),
    "COOLANT_TEMP": (-40.0, 150.0),
    "INTAKE_TEMP": (-40.0, 90.0),
    "MAF": (0.0, 400.0),
    "THROTTLE_POS": (0.0, 100.0),
    "SHORT_FUEL_TRIM_1": (-100.0, 100.0),
    "LONG_FUEL_TRIM_1": (-100.0, 100.0),
    "O2_B1S1": (0.0, 1.3),
    "TIMING_ADVANCE": (-64.0, 64.0),
    "INTAKE_PRESSURE": (0.0, 255.0),
}


def is_valid(reading: OBDReading) -> bool:
    """Valida el rango físico de una lectura."""
    lo, hi = _VALID_RANGES.get(reading.pid, (float("-inf"), float("inf")))
    return lo <= reading.value <= hi


class WindowBuilder:
    """Acumula ticks (una pasada de PIDs por tick) y emite ventanas deslizantes.

    - ``size``: muestras por ventana (60 a 1 Hz = 60 s).
    - ``stride``: desplazamiento entre ventanas (30 = solape del 50 %).
    """

    def __init__(self, size: int = 60, stride: int = 30) -> None:
        self.size = size
        self.stride = stride
        self._ticks: list[dict[str, float]] = []
        self._timestamps: list[datetime] = []
        self._emitted = 0

    def push_tick(self, readings: list[OBDReading]) -> dict[str, list[float]] | None:
        """Añade un tick; devuelve la ventana (series por PID) cuando toca emitir una."""
        valid = {r.pid: r.value for r in readings if is_valid(r)}
        self._ticks.append(valid)
        self._timestamps.append(readings[0].timestamp if readings else datetime.now().astimezone())
        if len(self._ticks) < self.size:
            return None
        if (len(self._ticks) - self.size) % self.stride != 0:
            return None
        chunk = self._ticks[-self.size :]
        window = {pid: [t[pid] for t in chunk if pid in t] for pid in CANONICAL_PIDS}
        self._emitted += 1
        return window

    def window_telemetry(
        self, window: dict[str, list[float]], vehicle_id: str, device_id: str, sample_rate_hz: float
    ) -> VehicleTelemetry:
        """Empaqueta la última ventana como contrato ``VehicleTelemetry`` (sin lecturas crudas)."""
        return VehicleTelemetry(
            window_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            device_id=device_id,
            start=self._timestamps[-self.size],
            end=self._timestamps[-1],
            sample_rate_hz=sample_rate_hz,
            readings=[],  # las lecturas viven en storage; el contrato admite ventana vacía
        )
