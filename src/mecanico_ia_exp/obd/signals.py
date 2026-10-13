"""Catálogo de señales OBD-II del laboratorio.

Doce señales de motor de gasolina, cada una con unidad y rango físico admisible.
El rango no es decorativo: la validación lo usa para rechazar datos imposibles,
y el análisis exploratorio lo usa para distinguir un valor extremo de un error de
registro.

Procedencia: el conjunto de señales y sus rangos provienen del catálogo de PIDs
canónicos del proyecto de ingeniería hermano, reexpresado aquí en nomenclatura
descriptiva. La correspondencia se conserva en ``PID_EQUIVALENTE`` para poder
cruzar datos entre ambos proyectos sin ambigüedad.

Sobre la presión de combustible: se consideró incluirla, y se descartó. El modelo
de señales disponible no la produce, y añadirla exigiría inventar una dinámica
sin respaldo. Una señal sin fundamento contamina el análisis en lugar de
enriquecerlo.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalSpec:
    """Definición de una señal: qué mide, en qué unidad y entre qué límites."""

    name: str
    unit: str
    minimum: float
    maximum: float
    description: str


CANONICAL_SIGNALS: tuple[SignalSpec, ...] = (
    SignalSpec("rpm", "rpm", 0.0, 8000.0, "Régimen de giro del motor"),
    SignalSpec("vehicle_speed", "km/h", 0.0, 250.0, "Velocidad del vehículo"),
    SignalSpec("engine_load", "%", 0.0, 100.0, "Carga calculada del motor"),
    SignalSpec("throttle_position", "%", 0.0, 100.0, "Posición de la mariposa"),
    SignalSpec("coolant_temperature", "°C", -40.0, 150.0, "Temperatura del refrigerante"),
    SignalSpec("intake_air_temperature", "°C", -40.0, 120.0, "Temperatura del aire de admisión"),
    SignalSpec("maf", "g/s", 0.0, 300.0, "Caudal másico de aire"),
    SignalSpec("map", "kPa", 0.0, 255.0, "Presión absoluta en el colector de admisión"),
    SignalSpec("stft_bank1", "%", -100.0, 100.0, "Ajuste de combustible a corto plazo, banco 1"),
    SignalSpec("ltft_bank1", "%", -100.0, 100.0, "Ajuste de combustible a largo plazo, banco 1"),
    SignalSpec(
        "oxygen_sensor", "V", 0.0, 1.275, "Tensión de la sonda lambda anterior al catalizador"
    ),
    SignalSpec("ignition_timing", "° antes del PMS", -64.0, 64.0, "Avance del encendido"),
)

SIGNAL_NAMES: tuple[str, ...] = tuple(spec.name for spec in CANONICAL_SIGNALS)

SIGNALS_BY_NAME: dict[str, SignalSpec] = {spec.name: spec for spec in CANONICAL_SIGNALS}

#: Correspondencia con la nomenclatura de PIDs del proyecto de ingeniería.
PID_EQUIVALENTE: dict[str, str] = {
    "rpm": "RPM",
    "vehicle_speed": "SPEED",
    "engine_load": "ENGINE_LOAD",
    "throttle_position": "THROTTLE_POS",
    "coolant_temperature": "COOLANT_TEMP",
    "intake_air_temperature": "INTAKE_TEMP",
    "maf": "MAF",
    "map": "INTAKE_PRESSURE",
    "stft_bank1": "SHORT_FUEL_TRIM_1",
    "ltft_bank1": "LONG_FUEL_TRIM_1",
    "oxygen_sensor": "O2_B1S1",
    "ignition_timing": "TIMING_ADVANCE",
}

#: Columnas no-señal que acompañan a toda serie generada.
#:
#: ``fault_active`` dice que la función de fallo se aplicó; ``fault_expressed``,
#: que alteró la trayectoria. No son lo mismo y la diferencia importa: ver
#: ``obd/expresion.py``. ``fault_deviation_max`` guarda la magnitud de la mayor
#: alteración en umbrales de su propia señal, de modo que una lectura más
#: estricta no exige regenerar nada, y ``fault_deviation_signal`` dice qué señal
#: la lleva.
#:
#: Las tres últimas se incorporaron con `synthetic_v4`: **los conjuntos
#: anteriores no las tienen**, y el código que las lea debe tolerar su ausencia
#: en lugar de exigirlas.
METADATA_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "session_id",
    "regime",
    "fault_id",
    "fault_active",
    "fault_expressed",
    "fault_deviation_max",
    "fault_deviation_signal",
)

#: Las que solo existen desde `synthetic_v4`.
COLUMNAS_DE_EXPRESION: tuple[str, ...] = (
    "fault_expressed",
    "fault_deviation_max",
    "fault_deviation_signal",
)


def validate_ranges(values: dict[str, float]) -> list[str]:
    """Devuelve los nombres de las señales fuera de su rango físico.

    Lista vacía significa que todo está dentro de lo admisible. Se devuelve la
    lista y no un booleano porque saber *qué* señal se salió es lo que permite
    diagnosticar el problema.
    """
    fuera: list[str] = []
    for nombre, valor in values.items():
        spec = SIGNALS_BY_NAME.get(nombre)
        if spec is None:
            continue
        if not (spec.minimum <= valor <= spec.maximum):
            fuera.append(nombre)
    return fuera
