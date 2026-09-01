"""Generación de sesiones OBD-II sintéticas con verdad de referencia.

Una **sesión** es la unidad de generación y, más adelante, la unidad de reparto
entre entrenamiento, validación y test. Que coincidan no es casualidad: repartir
ventanas sueltas de una misma sesión entre entrenamiento y test filtraría
información de un lado a otro, y la evaluación mediría memoria en lugar de
capacidad de generalizar.

Cada muestra lleva anotado si el fallo estaba activo en ese instante. Esa es la
verdad de referencia contra la que se contrasta después todo lo demás.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

import pandas as pd

from mecanico_ia_exp.data.metadata import DatasetMetadata
from mecanico_ia_exp.obd.engine import SignalEngine
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID, FaultRuntime
from mecanico_ia_exp.obd.regimes import REGIMES
from mecanico_ia_exp.obd.signals import METADATA_COLUMNS, SIGNAL_NAMES, SIGNALS_BY_NAME

GENERATOR_VERSION = "1.0.0"


@dataclass(frozen=True)
class SessionSpec:
    """Todo lo que define una sesión de forma reproducible."""

    session_id: str
    regime: str
    duration_s: float
    seed: int
    fault_id: str = NORMAL_ID
    fault_onset_s: float = 0.0
    """Instante en que el fallo empieza a actuar. Antes de él la sesión es normal,
    lo que permite observar la transición en lugar de solo el estado final."""
    ambient_temp_c: float = 22.0
    sample_rate_hz: float = 1.0
    fault_params: tuple[tuple[str, float], ...] = ()
    """Parámetros que sustituyen a los del catálogo. Tupla y no diccionario para
    que la especificación sea hashable y comparable."""

    def __post_init__(self) -> None:
        if self.regime not in REGIMES:
            msg = f"Régimen desconocido: {self.regime!r}"
            raise ValueError(msg)
        if self.fault_id != NORMAL_ID and self.fault_id not in FAULTS:
            msg = f"Fallo desconocido: {self.fault_id!r}"
            raise ValueError(msg)
        if self.duration_s <= 0:
            msg = f"La duración debe ser positiva, recibida {self.duration_s}"
            raise ValueError(msg)


def _clip_to_physical_range(values: dict[str, float]) -> dict[str, float]:
    """Recorta cada señal a su rango físico.

    La inyección de un fallo puede empujar una señal fuera de lo posible --un
    ajuste de combustible del 140 %, por ejemplo--. Recortar es lo que hace un
    sensor real, que satura; dejar pasar el valor imposible regalaría al modelo
    una pista que en datos reales nunca existiría.
    """
    recortado: dict[str, float] = {}
    for nombre, valor in values.items():
        spec = SIGNALS_BY_NAME[nombre]
        recortado[nombre] = min(spec.maximum, max(spec.minimum, valor))
    return recortado


def generate_session(spec: SessionSpec) -> pd.DataFrame:
    """Genera una sesión completa como serie temporal."""
    motor = SignalEngine(
        regime=spec.regime,
        seed=spec.seed,
        ambient_temp_c=spec.ambient_temp_c,
        sample_rate_hz=spec.sample_rate_hz,
    )
    fallo = FAULTS.get(spec.fault_id)
    runtime = FaultRuntime(rng=Random(spec.seed + 1))
    params: dict[str, float] = {}
    if fallo is not None:
        params = {**fallo.default_params, **dict(spec.fault_params)}

    dt = 1.0 / spec.sample_rate_hz
    n = int(spec.duration_s * spec.sample_rate_hz)
    filas: list[dict[str, float | str | bool]] = []

    for i in range(n):
        t = i * dt
        valores = motor.tick()
        activo = fallo is not None and t >= spec.fault_onset_s
        if activo and fallo is not None:
            runtime.elapsed_s = t - spec.fault_onset_s
            valores = fallo.apply(valores, params, runtime)
        valores = _clip_to_physical_range(valores)

        fila: dict[str, float | str | bool] = {
            "timestamp": t,
            "session_id": spec.session_id,
            "regime": spec.regime,
            "fault_id": spec.fault_id,
            "fault_active": activo,
        }
        fila.update(valores)
        filas.append(fila)

    marco = pd.DataFrame(filas, columns=[*METADATA_COLUMNS, *SIGNAL_NAMES])
    return marco


def generate_dataset(
    specs: list[SessionSpec],
    *,
    dataset_id: str,
    seed: int,
    notes: str = "",
) -> tuple[pd.DataFrame, DatasetMetadata]:
    """Genera varias sesiones y su ficha de procedencia."""
    if not specs:
        msg = "Un dataset necesita al menos una sesión"
        raise ValueError(msg)

    identificadores = [s.session_id for s in specs]
    if len(set(identificadores)) != len(identificadores):
        msg = "Los identificadores de sesión deben ser únicos dentro de un dataset"
        raise ValueError(msg)

    marcos = [generate_session(spec) for spec in specs]
    datos = pd.concat(marcos, ignore_index=True)

    tasas = {s.sample_rate_hz for s in specs}
    metadata = DatasetMetadata(
        dataset_id=dataset_id,
        dataset_type="synthetic",
        source=f"mecanico_ia_exp.obd.synthetic v{GENERATOR_VERSION}",
        version=GENERATOR_VERSION,
        sampling_rate_hz=tasas.pop() if len(tasas) == 1 else -1.0,
        vehicle_or_simulator="simulador paramétrico de motor de gasolina",
        notes=notes,
        seed=seed,
        n_sessions=len(specs),
        n_samples=len(datos),
        signals=SIGNAL_NAMES,
        fault_ids=tuple(sorted({s.fault_id for s in specs})),
        session_ids=tuple(identificadores),
    )
    return datos, metadata


def build_balanced_specs(
    *,
    seed: int,
    sessions_per_fault: int = 6,
    duration_s: float = 600.0,
    regimes: tuple[str, ...] = ("urban", "highway", "idle", "warmup"),
) -> list[SessionSpec]:
    """Construye un plan de sesiones equilibrado entre condiciones.

    Cada condición --normal y los cinco fallos-- recibe el mismo número de
    sesiones, repartidas entre regímenes. El equilibrio se busca a propósito: un
    desbalance en datos sintéticos sería un artefacto elegido por quien genera,
    no una propiedad del problema, y contaminaría la lectura de las métricas.
    """
    rng = Random(seed)
    condiciones = [NORMAL_ID, *FAULTS]
    specs: list[SessionSpec] = []

    for fault_id in condiciones:
        for k in range(sessions_per_fault):
            regime = regimes[k % len(regimes)]
            inicio = 0.0 if fault_id == NORMAL_ID else duration_s * 0.2
            specs.append(
                SessionSpec(
                    session_id=f"{fault_id}__{regime}__{k:02d}",
                    regime=regime,
                    duration_s=duration_s,
                    seed=rng.randrange(1, 2**31),
                    fault_id=fault_id,
                    fault_onset_s=inicio,
                    ambient_temp_c=rng.uniform(15.0, 28.0),
                )
            )
    return specs
