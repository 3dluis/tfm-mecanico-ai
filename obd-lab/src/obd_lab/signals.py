"""Motor de señales del laboratorio: simulación paramétrica de PIDs de motor de gasolina.

Modelo por tick (nominal 1 Hz) con estado interno, para servir tanto a la generación
offline de sesiones como a la alimentación en vivo del emulador ELM327 (ADR-0010).

El objetivo NO es fidelidad termodinámica, sino: (a) rangos y correlaciones plausibles
entre PIDs, (b) dinámica temporal razonable (calentamiento, transitorios de conducción),
(c) parametrización y reproducibilidad por semilla. La calibración fina contra datos
reales (HCRL) está prevista en `docs/fase3/dataset_hcrl_verificacion.md`.
"""

import math
import random
from dataclasses import dataclass, field

from mecanico_contracts.features import CANONICAL_PIDS

__all__ = ["CANONICAL_PIDS", "DrivingState", "SignalEngine"]

# Fases de un perfil de conducción: (nombre, velocidad_objetivo_kmh, duración_media_s)
_PROFILE_PHASES: dict[str, list[tuple[str, float, float]]] = {
    "idle": [("idle", 0.0, 120.0)],
    "urban": [
        ("idle", 0.0, 25.0),
        ("accel", 45.0, 15.0),
        ("cruise", 45.0, 40.0),
        ("decel", 0.0, 10.0),
    ],
    "highway": [
        ("accel", 110.0, 30.0),
        ("cruise", 110.0, 180.0),
        ("vary", 95.0, 60.0),
        ("cruise", 115.0, 120.0),
    ],
    "cold_start": [  # igual que urban; el arranque en frío lo determina ambient/coolant inicial
        ("idle", 0.0, 60.0),
        ("accel", 40.0, 20.0),
        ("cruise", 40.0, 60.0),
        ("decel", 0.0, 12.0),
    ],
}

_THERMOSTAT_C = 88.0  # temperatura de regulación
_IDLE_RPM = 820.0


@dataclass
class DrivingState:
    """Estado interno del vehículo simulado."""

    speed_kmh: float = 0.0
    target_speed: float = 0.0
    coolant_c: float = 22.0
    ltft_pct: float = 0.0
    phase: str = "idle"
    phase_left_s: float = 30.0
    phase_idx: int = 0
    o2_phase: float = 0.0
    values: dict[str, float] = field(default_factory=dict)


class SignalEngine:
    """Genera valores por tick de los 12 PIDs canónicos, con perfil y semilla."""

    def __init__(
        self,
        profile: str = "urban",
        seed: int = 42,
        ambient_temp_c: float = 22.0,
        sample_rate_hz: float = 1.0,
    ) -> None:
        if profile not in _PROFILE_PHASES:
            msg = f"Perfil desconocido: {profile!r}; disponibles: {sorted(_PROFILE_PHASES)}"
            raise ValueError(msg)
        self.profile = profile
        self.rng = random.Random(seed)
        self.ambient = ambient_temp_c
        self.dt = 1.0 / sample_rate_hz
        self.t = 0.0
        cold = profile == "cold_start"
        self.state = DrivingState(coolant_c=ambient_temp_c if cold else 78.0)
        self._enter_phase(0)

    # ------------------------------------------------------------------ fases
    def _enter_phase(self, idx: int) -> None:
        phases = _PROFILE_PHASES[self.profile]
        name, target, dur = phases[idx % len(phases)]
        jitter = self.rng.uniform(0.7, 1.3)
        self.state.phase = name
        self.state.phase_idx = idx
        self.state.phase_left_s = dur * jitter
        self.state.target_speed = max(0.0, target + self.rng.uniform(-8.0, 8.0)) if target else 0.0

    def _advance_phase(self) -> None:
        self.state.phase_left_s -= self.dt
        if self.state.phase_left_s <= 0:
            self._enter_phase(self.state.phase_idx + 1)
        if self.state.phase == "vary":  # variaciones suaves en autovía
            self.state.target_speed += self.rng.uniform(-1.5, 1.5)
            self.state.target_speed = min(125.0, max(80.0, self.state.target_speed))

    # ------------------------------------------------------------------- tick
    def tick(self) -> dict[str, float]:
        """Avanza un paso de simulación y devuelve los valores de todos los PIDs."""
        s, rng = self.state, self.rng
        self._advance_phase()

        # --- dinámica longitudinal
        accel_gain = 0.06 if s.target_speed > s.speed_kmh else 0.12
        s.speed_kmh += (s.target_speed - s.speed_kmh) * accel_gain * self.dt * 10.0 / 10.0
        s.speed_kmh = max(0.0, s.speed_kmh + rng.gauss(0.0, 0.3))
        accel_demand = max(0.0, (s.target_speed - s.speed_kmh)) / 25.0  # 0..~1

        # --- rpm: relación velocidad/marcha aproximada + ralentí
        gear_ratio = (
            105.0
            if s.speed_kmh < 20
            else 60.0
            if s.speed_kmh < 45
            else 38.0
            if s.speed_kmh < 75
            else 29.0
        )
        rpm = (
            _IDLE_RPM + rng.gauss(0.0, 12.0)
            if s.speed_kmh < 2.0
            else s.speed_kmh * gear_ratio * (0.95 + 0.1 * accel_demand) + rng.gauss(0.0, 35.0)
        )
        rpm = min(5200.0, max(650.0, rpm))

        # --- carga y mariposa
        drag = 6.0 + 0.16 * s.speed_kmh
        load = min(95.0, max(3.0, drag + 60.0 * accel_demand + rng.gauss(0.0, 2.0)))
        throttle = min(92.0, max(12.0, 13.0 + 0.75 * load + rng.gauss(0.0, 1.5)))

        # --- flujo de aire y presión de admisión (correlacionados con rpm×carga)
        maf = max(1.5, 0.00045 * rpm * load + rng.gauss(0.0, 0.35))  # g/s aprox
        map_kpa = min(105.0, max(18.0, 22.0 + 0.8 * load + rng.gauss(0.0, 1.2)))

        # --- térmica: primer orden hacia equilibrio > termostato (warmup ~8-10 min);
        #     el termostato regula el exceso. Equilibrio sin termostato ≈ amb + heat/k.
        heat_in = 0.14 * (0.8 + load / 80.0)  # °C/s aportados por la combustión
        s.coolant_c += (heat_in - 0.0016 * (s.coolant_c - self.ambient)) * self.dt
        if s.coolant_c > _THERMOSTAT_C:
            s.coolant_c = _THERMOSTAT_C + (s.coolant_c - _THERMOSTAT_C) * 0.3 + rng.gauss(0.0, 0.15)
        intake_temp = self.ambient + 9.0 + 0.05 * load + rng.gauss(0.0, 0.4)

        # --- mezcla: trims cerca de 0 con ruido; LTFT deriva lentísima
        stft = rng.gauss(0.0, 1.6)
        s.ltft_pct += rng.gauss(0.0, 0.01)
        s.ltft_pct = max(-4.0, min(4.0, s.ltft_pct))

        # --- sonda O2 pre-cat: oscilación rica/pobre (~0.6 Hz submuestreada a 1 Hz)
        s.o2_phase += self.dt * (0.55 + 0.1 * accel_demand) * 2.0 * math.pi
        o2 = 0.45 + 0.35 * math.sin(s.o2_phase) + rng.gauss(0.0, 0.03)
        o2 = min(0.95, max(0.05, o2))

        # --- avance de encendido
        timing = 12.0 + 24.0 * (rpm / 5200.0) - 14.0 * (load / 95.0) + rng.gauss(0.0, 0.8)

        self.t += self.dt
        s.values = {
            "RPM": rpm,
            "SPEED": s.speed_kmh,
            "ENGINE_LOAD": load,
            "COOLANT_TEMP": s.coolant_c,
            "INTAKE_TEMP": intake_temp,
            "MAF": maf,
            "THROTTLE_POS": throttle,
            "SHORT_FUEL_TRIM_1": stft,
            "LONG_FUEL_TRIM_1": s.ltft_pct,
            "O2_B1S1": o2,
            "TIMING_ADVANCE": timing,
            "INTAKE_PRESSURE": map_kpa,
        }
        return dict(s.values)
