"""Motor de simulación de señales OBD-II.

Genera un instante por paso, manteniendo estado interno. El objetivo no es
fidelidad termodinámica --no la tiene, y afirmar lo contrario sería falso-- sino
tres propiedades que el experimento sí necesita:

1. **Rangos plausibles**: ningún valor cae fuera de lo físicamente posible.
2. **Relaciones entre señales**: acelerador↔régimen, régimen↔caudal, carga↔presión,
   temperatura↔tiempo, mezcla↔ajustes, velocidad↔régimen. Un generador de
   variables independientes al azar no serviría: el modelo no tendría estructura
   que aprender y la atribución no tendría nada que señalar.
3. **Reproducibilidad por semilla**: dos ejecuciones con la misma semilla producen
   exactamente la misma serie.

Procedencia: adaptado del motor de señales del proyecto de ingeniería hermano.

Limitación conocida y asumida: el modelo es paramétrico y no está calibrado
contra datos reales. Sirve para control experimental --conocer la verdad de
referencia y manipularla-- no para sustituir la validación con datos reales, que
es lo que la pregunta de investigación exige.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from random import Random

from mecanico_ia_exp.obd.regimes import COLD_START_REGIMES, REGIMES

_THERMOSTAT_C = 88.0
_IDLE_RPM = 820.0


@dataclass
class EngineState:
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
    """Produce los valores de las doce señales, paso a paso."""

    def __init__(
        self,
        regime: str = "urban",
        seed: int = 42,
        ambient_temp_c: float = 22.0,
        sample_rate_hz: float = 1.0,
    ) -> None:
        if regime not in REGIMES:
            msg = f"Régimen desconocido: {regime!r}; disponibles: {sorted(REGIMES)}"
            raise ValueError(msg)
        if sample_rate_hz <= 0:
            msg = f"La tasa de muestreo debe ser positiva, recibida {sample_rate_hz}"
            raise ValueError(msg)

        self.regime = regime
        self.rng = Random(seed)
        self.ambient = ambient_temp_c
        self.dt = 1.0 / sample_rate_hz
        self.t = 0.0
        arranque_frio = regime in COLD_START_REGIMES
        self.state = EngineState(coolant_c=ambient_temp_c if arranque_frio else 78.0)
        self._enter_phase(0)

    # ----------------------------------------------------------------- fases
    def _enter_phase(self, idx: int) -> None:
        fases = REGIMES[self.regime].phases
        fase = fases[idx % len(fases)]
        jitter = self.rng.uniform(0.7, 1.3)
        self.state.phase = fase.name
        self.state.phase_idx = idx
        self.state.phase_left_s = fase.mean_duration_s * jitter
        objetivo = fase.target_speed_kmh
        self.state.target_speed = (
            max(0.0, objetivo + self.rng.uniform(-8.0, 8.0)) if objetivo else 0.0
        )

    def _advance_phase(self) -> None:
        self.state.phase_left_s -= self.dt
        if self.state.phase_left_s <= 0:
            self._enter_phase(self.state.phase_idx + 1)
        if self.state.phase == "vary":
            self.state.target_speed += self.rng.uniform(-1.5, 1.5)
            self.state.target_speed = min(125.0, max(80.0, self.state.target_speed))

    # ------------------------------------------------------------------ paso
    def tick(self) -> dict[str, float]:
        """Avanza un paso y devuelve el valor de cada señal."""
        s, rng = self.state, self.rng
        self._advance_phase()

        # Dinámica longitudinal: aproximación de primer orden a la velocidad
        # objetivo. Frenar es más rápido que acelerar.
        ganancia = 0.06 if s.target_speed > s.speed_kmh else 0.12
        s.speed_kmh += (s.target_speed - s.speed_kmh) * ganancia * self.dt
        s.speed_kmh = max(0.0, s.speed_kmh + rng.gauss(0.0, 0.3))
        demanda = max(0.0, s.target_speed - s.speed_kmh) / 25.0

        # Régimen: relación con la velocidad según marcha aproximada, más ralentí.
        relacion = (
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
            else s.speed_kmh * relacion * (0.95 + 0.1 * demanda) + rng.gauss(0.0, 35.0)
        )
        rpm = min(5200.0, max(650.0, rpm))

        # Carga y mariposa: la carga cubre la resistencia al avance más la
        # demanda de aceleración; la mariposa sigue a la carga.
        resistencia = 6.0 + 0.16 * s.speed_kmh
        carga = min(95.0, max(3.0, resistencia + 60.0 * demanda + rng.gauss(0.0, 2.0)))
        mariposa = min(92.0, max(12.0, 13.0 + 0.75 * carga + rng.gauss(0.0, 1.5)))

        # Aire admitido: caudal proporcional a régimen por carga; presión de
        # colector creciente con la carga.
        maf = max(1.5, 0.00045 * rpm * carga + rng.gauss(0.0, 0.35))
        map_kpa = min(105.0, max(18.0, 22.0 + 0.8 * carga + rng.gauss(0.0, 1.2)))

        # Térmica: primer orden hacia el equilibrio, con el termostato regulando
        # el exceso por encima de su temperatura de apertura.
        aporte = 0.14 * (0.8 + carga / 80.0)
        s.coolant_c += (aporte - 0.0016 * (s.coolant_c - self.ambient)) * self.dt
        if s.coolant_c > _THERMOSTAT_C:
            s.coolant_c = _THERMOSTAT_C + (s.coolant_c - _THERMOSTAT_C) * 0.3 + rng.gauss(0.0, 0.15)
        admision = self.ambient + 9.0 + 0.05 * carga + rng.gauss(0.0, 0.4)

        # Mezcla: ajustes en torno a cero con ruido; el de largo plazo deriva muy
        # despacio, que es lo que lo hace informativo cuando se desplaza.
        stft = rng.gauss(0.0, 1.6)
        s.ltft_pct += rng.gauss(0.0, 0.01)
        s.ltft_pct = max(-4.0, min(4.0, s.ltft_pct))

        # Sonda lambda: oscilación rica/pobre en torno al punto estequiométrico.
        s.o2_phase += self.dt * (0.55 + 0.1 * demanda) * 2.0 * math.pi
        o2 = 0.45 + 0.35 * math.sin(s.o2_phase) + rng.gauss(0.0, 0.03)
        o2 = min(0.95, max(0.05, o2))

        # Avance de encendido: sube con el régimen, retrasa con la carga.
        avance = 12.0 + 24.0 * (rpm / 5200.0) - 14.0 * (carga / 95.0) + rng.gauss(0.0, 0.8)

        self.t += self.dt
        s.values = {
            "rpm": rpm,
            "vehicle_speed": s.speed_kmh,
            "engine_load": carga,
            "throttle_position": mariposa,
            "coolant_temperature": s.coolant_c,
            "intake_air_temperature": admision,
            "maf": maf,
            "map": map_kpa,
            "stft_bank1": stft,
            "ltft_bank1": s.ltft_pct,
            "oxygen_sensor": o2,
            "ignition_timing": avance,
        }
        return dict(s.values)
