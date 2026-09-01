"""Catálogo de condiciones de fallo y su inyección.

Cada fallo es una transformación parametrizada que se aplica a los valores de un
instante, dentro de su ventana de actividad. La definición no se agota en el
código: lleva adjunta la firma que se espera observar, qué señales toca y qué
patrón temporal sigue. Esa ficha es lo que después permite comprobar si una
explicación se corresponde con lo que realmente ocurrió.

**Sobre el campo ``source``.** Ninguna de estas firmas tiene todavía respaldo
documental verificado en este laboratorio. El campo queda marcado como pendiente
a propósito: el corpus documental se construye en E10, y hasta entonces afirmar
que una firma está documentada sería exactamente el tipo de afirmación sin
evidencia que este trabajo se propone detectar. Un fallo cuya firma no llegue a
tener respaldo documental no podrá sostener una explicación, y eso es un
resultado, no un defecto.

Procedencia: los modelos de degradación derivan del catálogo de inyección del
proyecto de ingeniería hermano.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from random import Random

#: Marcador de respaldo documental no verificado todavía (se resuelve en E10).
PENDIENTE_RESPALDO = "[EVIDENCE_REQUIRED] respaldo documental pendiente de E10"


@dataclass
class FaultRuntime:
    """Estado que un fallo arrastra a lo largo de una sesión.

    Existe porque varias degradaciones no son instantáneas: el ajuste a largo
    plazo aprende durante minutos, y un fallo de encendido tiene episodios que
    duran más de un instante.
    """

    rng: Random
    elapsed_s: float = 0.0
    memory: dict[str, float] = field(default_factory=dict)


FaultFn = Callable[[dict[str, float], dict[str, float], FaultRuntime], dict[str, float]]


@dataclass(frozen=True)
class FaultDef:
    """Ficha completa de una condición de fallo."""

    fault_id: str
    fault_name: str
    affected_signals: tuple[str, ...]
    temporal_pattern: str
    expected_observation: str
    diagnostic_support: str
    source: str
    apply: FaultFn
    default_params: dict[str, float]


# --------------------------------------------------------------------- fallos


def _vacuum_leak(v: dict[str, float], p: dict[str, float], rt: FaultRuntime) -> dict[str, float]:
    """Aire que entra sin pasar por el caudalímetro: la mezcla se empobrece y la
    centralita compensa inyectando más. El efecto es mayor en ralentí, donde la
    depresión del colector es alta y la fuga proporcionalmente más importante."""
    sev = p["severity"]
    peso_ralenti = 1.0 if v["vehicle_speed"] < 5.0 else 0.45
    v["stft_bank1"] += sev * 12.0 * peso_ralenti + rt.rng.gauss(0.0, 0.5)
    rampa = min(1.0, rt.elapsed_s / 240.0)  # el ajuste a largo plazo aprende en minutos
    v["ltft_bank1"] += sev * 10.0 * peso_ralenti * rampa
    v["map"] += sev * 6.0 * peso_ralenti
    if v["vehicle_speed"] < 5.0:
        v["rpm"] += rt.rng.gauss(0.0, sev * 45.0)  # ralentí inestable
    return v


def _maf_drift(v: dict[str, float], p: dict[str, float], rt: FaultRuntime) -> dict[str, float]:
    """Caudalímetro contaminado: subestima el aire que entra, la centralita
    inyecta de menos y los ajustes suben para compensar. La deriva se instala
    progresivamente, no de golpe."""
    deriva = p["drift"] * min(1.0, rt.elapsed_s / p["ramp_s"])
    v["maf"] *= 1.0 - deriva
    v["stft_bank1"] += deriva * 55.0 + rt.rng.gauss(0.0, 0.5)
    v["ltft_bank1"] += deriva * 45.0 * min(1.0, rt.elapsed_s / 240.0)
    return v


def _thermostat_stuck(
    v: dict[str, float], p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """Termostato bloqueado en abierto: el refrigerante circula siempre y el
    motor no alcanza su temperatura de régimen. La firma es una ausencia --algo
    que debería subir y no sube-- y por eso es fácil de pasar por alto."""
    tope = p["temp_cap_c"]
    if v["coolant_temperature"] > tope:
        v["coolant_temperature"] = tope + rt.rng.gauss(0.0, 0.5)
    return v


def _o2_lag(v: dict[str, float], p: dict[str, float], rt: FaultRuntime) -> dict[str, float]:
    """Sonda lambda envejecida: sigue respondiendo, pero tarde. La oscilación
    rica/pobre se amortigua y la regulación se vuelve más errática."""
    alpha = p["smoothing"]
    previo = rt.memory.get("oxygen_sensor", v["oxygen_sensor"])
    v["oxygen_sensor"] = alpha * previo + (1.0 - alpha) * v["oxygen_sensor"]
    rt.memory["oxygen_sensor"] = v["oxygen_sensor"]
    v["stft_bank1"] += rt.rng.gauss(0.0, 1.8)
    return v


def _misfire(v: dict[str, float], p: dict[str, float], rt: FaultRuntime) -> dict[str, float]:
    """Fallo de encendido intermitente: episodios breves en los que un cilindro
    no aporta par. Caída de régimen, salto de carga y combustible sin quemar que
    llega a la sonda."""
    if rt.rng.random() < p["rate"]:
        rt.memory["active_until"] = rt.elapsed_s + rt.rng.uniform(1.0, 3.0)
    if rt.elapsed_s < rt.memory.get("active_until", -1.0):
        v["rpm"] = max(600.0, v["rpm"] - p["rpm_drop"] * rt.rng.uniform(0.7, 1.3))
        v["engine_load"] = min(98.0, v["engine_load"] + 7.0)
        v["stft_bank1"] += rt.rng.gauss(0.0, 2.5)
        v["oxygen_sensor"] = min(0.95, v["oxygen_sensor"] + 0.12)
    return v


FAULTS: dict[str, FaultDef] = {
    "F01_vacuum_leak": FaultDef(
        fault_id="F01_vacuum_leak",
        fault_name="Fuga de vacío en el colector de admisión",
        affected_signals=("stft_bank1", "ltft_bank1", "map", "rpm"),
        temporal_pattern=(
            "persistente, acentuado en ralentí; el ajuste a largo plazo sube en rampa de ~4 min"
        ),
        expected_observation=(
            "ajustes de combustible positivos, mayores a baja velocidad; presión de colector\n"
            "elevada en ralentí; régimen inestable en ralentí"
        ),
        diagnostic_support="mezcla pobre por aire no medido",
        source=PENDIENTE_RESPALDO,
        apply=_vacuum_leak,
        default_params={"severity": 0.6},
    ),
    "F02_maf_drift": FaultDef(
        fault_id="F02_maf_drift",
        fault_name="Deriva del caudalímetro de aire",
        affected_signals=("maf", "stft_bank1", "ltft_bank1"),
        temporal_pattern="deriva progresiva con rampa de instalación de ~5 min",
        expected_observation=(
            "caudal de aire por debajo de lo esperable para el régimen y la carga; ajustes\n"
            "de combustible positivos y crecientes"
        ),
        diagnostic_support="subestimación del aire admitido por el sensor",
        source=PENDIENTE_RESPALDO,
        apply=_maf_drift,
        default_params={"drift": 0.18, "ramp_s": 300.0},
    ),
    "F03_thermostat_stuck": FaultDef(
        fault_id="F03_thermostat_stuck",
        fault_name="Termostato bloqueado en posición abierta",
        affected_signals=("coolant_temperature",),
        temporal_pattern=(
            "techo constante de temperatura; la firma es la ausencia de calentamiento"
        ),
        expected_observation=(
            "temperatura de refrigerante estancada por debajo de la de régimen pese a carga\n"
            "y tiempo suficientes"
        ),
        diagnostic_support="circulación permanente de refrigerante",
        source=PENDIENTE_RESPALDO,
        apply=_thermostat_stuck,
        default_params={"temp_cap_c": 71.0},
    ),
    "F04_o2_lag": FaultDef(
        fault_id="F04_o2_lag",
        fault_name="Sonda lambda de respuesta lenta",
        affected_signals=("oxygen_sensor", "stft_bank1"),
        temporal_pattern="persistente; amortiguación de la oscilación característica",
        expected_observation=(
            "menor amplitud y menor frecuencia de conmutación de la sonda; ajuste a corto\n"
            "plazo más ruidoso"
        ),
        diagnostic_support="envejecimiento del elemento sensor",
        source=PENDIENTE_RESPALDO,
        apply=_o2_lag,
        default_params={"smoothing": 0.82},
    ),
    "F05_misfire": FaultDef(
        fault_id="F05_misfire",
        fault_name="Fallo de encendido intermitente",
        affected_signals=("rpm", "engine_load", "stft_bank1", "oxygen_sensor"),
        temporal_pattern="episódico: eventos de 1 a 3 s con tasa de aparición baja",
        expected_observation=(
            "caídas breves de régimen con salto simultáneo de carga y desplazamiento de la\n"
            "sonda hacia mezcla rica"
        ),
        diagnostic_support="combustión ausente o incompleta en un cilindro",
        source=PENDIENTE_RESPALDO,
        apply=_misfire,
        default_params={"rate": 0.02, "rpm_drop": 260.0},
    ),
}

FAULT_IDS: tuple[str, ...] = tuple(FAULTS)

#: Etiqueta de la condición sin fallo. No es un fallo más: es la clase de
#: referencia contra la que se contrasta todo lo demás.
NORMAL_ID = "F00_normal"
