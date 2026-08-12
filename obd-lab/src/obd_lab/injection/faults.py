"""Modelos de fallo e inyección de anomalías (ADR-0010).

Cada fallo es una transformación parametrizada aplicada a los valores del tick DENTRO de su
ventana de actividad. Tres categorías (requisito del plan de investigación):

- ``known_fault``: degradaciones documentadas en literatura técnica con firma esperable en
  PIDs (fuga de vacío, deriva de MAF, termostato, sonda O2 lenta, fallo de encendido).
- ``held_out``: anomalías multivariables/temporales donde cada PID permanece en rango
  individualmente plausible pero la RELACIÓN entre señales o su evolución temporal es
  anómala. NUNCA se usan para ajustar modelos ni umbrales: solo en el conjunto de test
  final (protección frente a la circularidad RI1 y respuesta directa a la PI).
- ``normal``: sin fallo.

Fundamento de las firmas: fichas IN-8 en docs/estado_del_arte (a completar con citas
técnicas al redactar la memoria).
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, field

FaultFn = Callable[[dict[str, float], float, dict[str, float], "FaultRuntime"], dict[str, float]]


@dataclass
class FaultRuntime:
    """Estado interno persistente de un fallo durante la sesión."""

    rng: random.Random
    elapsed_s: float = 0.0
    memory: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class FaultDef:
    """Definición de un modelo de fallo del catálogo."""

    name: str
    category: str  # 'known_fault' | 'held_out'
    description: str
    expected_signature: str  # firma esperable en PIDs (para la memoria y el RAG)
    apply: FaultFn
    default_params: dict[str, float]


# ------------------------------------------------------------------ known faults


def _vacuum_leak(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """Fuga de vacío: aire no medido → mezcla pobre → trims positivos, peor en ralentí."""
    sev = p["severity"]  # 0..1
    idle_w = 1.0 if v["SPEED"] < 5.0 else 0.45
    v["SHORT_FUEL_TRIM_1"] += sev * 12.0 * idle_w + rt.rng.gauss(0.0, 0.5)
    ramp = min(1.0, rt.elapsed_s / 240.0)  # el LTFT aprende en minutos
    v["LONG_FUEL_TRIM_1"] += sev * 10.0 * idle_w * ramp
    v["INTAKE_PRESSURE"] += sev * 6.0 * idle_w  # MAP más alto en ralentí
    if v["SPEED"] < 5.0:
        v["RPM"] += rt.rng.gauss(0.0, sev * 45.0)  # ralentí inestable
    return v


def _maf_drift(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """MAF sucio/derivado: subestima flujo → ECU empobrece → trims compensan positivos."""
    drift = p["drift"] * min(1.0, rt.elapsed_s / p.get("ramp_s", 300.0))
    v["MAF"] *= 1.0 - drift
    v["SHORT_FUEL_TRIM_1"] += drift * 55.0 + rt.rng.gauss(0.0, 0.5)
    v["LONG_FUEL_TRIM_1"] += drift * 45.0 * min(1.0, rt.elapsed_s / 240.0)
    return v


def _thermostat_stuck(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """Termostato abierto: el motor no alcanza temperatura de régimen."""
    cap = p["temp_cap_c"]
    if v["COOLANT_TEMP"] > cap:
        v["COOLANT_TEMP"] = cap + rt.rng.gauss(0.0, 0.5)
    return v


def _o2_lag(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """Sonda O2 envejecida: respuesta lenta → oscilación amortiguada, trims más ruidosos."""
    alpha = p["smoothing"]  # 0..1 (mayor = más lag)
    prev = rt.memory.get("o2", v["O2_B1S1"])
    v["O2_B1S1"] = alpha * prev + (1.0 - alpha) * v["O2_B1S1"]
    rt.memory["o2"] = v["O2_B1S1"]
    v["SHORT_FUEL_TRIM_1"] += rt.rng.gauss(0.0, 1.8)
    return v


def _misfire(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """Fallo de encendido intermitente: caídas breves de RPM con sacudida de carga."""
    if rt.rng.random() < p["rate"]:
        rt.memory["active_until"] = rt.elapsed_s + rt.rng.uniform(1.0, 3.0)
    if rt.elapsed_s < rt.memory.get("active_until", -1.0):
        v["RPM"] = max(600.0, v["RPM"] - p["rpm_drop"] * rt.rng.uniform(0.7, 1.3))
        v["ENGINE_LOAD"] = min(98.0, v["ENGINE_LOAD"] + 7.0)
        v["SHORT_FUEL_TRIM_1"] += rt.rng.gauss(0.0, 2.5)
        v["O2_B1S1"] = min(0.95, v["O2_B1S1"] + 0.12)  # combustible sin quemar
    return v


# ------------------------------------------------------------------- held-out


def _corr_break_rpm_maf(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """[held-out] El MAF se desacopla de RPM/carga manteniéndose en rango plausible.

    Sustituye el MAF instantáneo por una media móvil lenta de sí mismo: cada valor es
    normal, la correlación RPM↔MAF de la ventana colapsa.
    """
    alpha = p["decouple"]  # 0..1 (1 = desacoplo total)
    prev = rt.memory.get("maf_ema", v["MAF"])
    ema = 0.995 * prev + 0.005 * v["MAF"]  # media móvil muy lenta: pierde el transitorio
    rt.memory["maf_ema"] = ema
    # Ruido propio no correlacionado: el valor se mantiene en banda plausible pero su
    # variación instantánea deja de seguir a RPM/carga.
    v["MAF"] = alpha * (ema + rt.rng.gauss(0.0, 0.8)) + (1.0 - alpha) * v["MAF"]
    v["MAF"] = max(1.5, v["MAF"])
    return v


def _load_coolant_decouple(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """[held-out] La temperatura deja de responder a la carga: microdinámica térmica muerta.

    El valor queda clavado en un punto de régimen perfectamente normal (~87 °C): ningún
    umbral univariante lo detecta; la anomalía es temporal (varianza y correlación nulas).
    """
    v["COOLANT_TEMP"] = p["freeze_at_c"] + rt.rng.gauss(0.0, 0.02)
    return v


def _joint_slow_drift(
    v: dict[str, float], t: float, p: dict[str, float], rt: FaultRuntime
) -> dict[str, float]:
    """[held-out] Deriva conjunta lenta: MAF↓ y avance de encendido↑, cada uno en rango.

    Individualmente ambos PIDs siguen dentro de banda normal; la combinación (menos aire
    con más avance a igual carga) es físicamente incoherente y solo emerge multivariable.
    """
    ramp = min(1.0, rt.elapsed_s / p.get("ramp_s", 400.0))
    v["MAF"] *= 1.0 - p["maf_drop"] * ramp
    v["TIMING_ADVANCE"] += p["timing_up"] * ramp + rt.rng.gauss(0.0, 0.2)
    return v


CATALOG: dict[str, FaultDef] = {
    f.name: f
    for f in [
        FaultDef(
            "vacuum_leak",
            "known_fault",
            "Fuga de vacío en el colector de admisión",
            "STFT/LTFT positivos (más en ralentí), MAP elevado, ralentí inestable",
            _vacuum_leak,
            {"severity": 0.6},
        ),
        FaultDef(
            "maf_drift",
            "known_fault",
            "Sensor MAF sucio/derivado (subestima flujo)",
            "MAF bajo para RPM×carga; trims positivos compensando",
            _maf_drift,
            {"drift": 0.15, "ramp_s": 300.0},
        ),
        FaultDef(
            "thermostat_stuck",
            "known_fault",
            "Termostato atascado abierto",
            "COOLANT_TEMP no alcanza régimen (~88 °C), meseta baja",
            _thermostat_stuck,
            {"temp_cap_c": 68.0},
        ),
        FaultDef(
            "o2_lag",
            "known_fault",
            "Sonda lambda pre-cat envejecida (respuesta lenta)",
            "Oscilación O2 amortiguada/lenta; STFT más ruidoso",
            _o2_lag,
            {"smoothing": 0.85},
        ),
        FaultDef(
            "misfire",
            "known_fault",
            "Fallo de encendido intermitente",
            "Caídas breves de RPM, carga a saltos, O2 rico intermitente",
            _misfire,
            {"rate": 0.06, "rpm_drop": 140.0},
        ),
        FaultDef(
            "corr_break_rpm_maf",
            "held_out",
            "Desacoplo MAF↔RPM con valores individualmente plausibles",
            "Colapso de corr(RPM,MAF) y corr(LOAD,MAF); univariantes normales",
            _corr_break_rpm_maf,
            {"decouple": 0.9},
        ),
        FaultDef(
            "load_coolant_decouple",
            "held_out",
            "Temperatura clavada en valor de régimen normal (dinámica muerta)",
            "std(COOLANT)≈0 y corr(LOAD,COOLANT)≈0 con media perfectamente normal",
            _load_coolant_decouple,
            {"freeze_at_c": 87.0},
        ),
        FaultDef(
            "joint_slow_drift",
            "held_out",
            "Deriva conjunta lenta MAF↓ + avance↑, cada PID en banda normal",
            "Incoherencia multivariable aire/encendido; univariantes en rango",
            _joint_slow_drift,
            {"maf_drop": 0.10, "timing_up": 4.0, "ramp_s": 400.0},
        ),
    ]
}


def known_fault_names() -> list[str]:
    """Fallos de la categoría known_fault (utilizables en ajuste/validación)."""
    return [n for n, f in CATALOG.items() if f.category == "known_fault"]


def held_out_names() -> list[str]:
    """Anomalías held-out: SOLO para el test final (nunca en ajuste)."""
    return [n for n, f in CATALOG.items() if f.category == "held_out"]
