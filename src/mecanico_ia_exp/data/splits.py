"""Reparto en entrenamiento, validación y test **sin fuga temporal**.

Este es el punto donde un error invalida todo lo posterior sin dar ninguna señal
de alarma: las métricas salen mejores, no peores.

La regla es una: **se reparten sesiones, nunca ventanas.** Dos ventanas
consecutivas de la misma sesión comparten casi toda su información --con solape,
literalmente comparten muestras; sin solape, comparten el mismo vehículo, el
mismo trayecto y el mismo instante de conducción--. Repartirlas entre
entrenamiento y test convierte la evaluación en un examen con las respuestas
delante.

El reparto se estratifica por condición para que las tres particiones contengan
las seis clases. Con clases equilibradas y pocas sesiones, no estratificar
dejaría particiones sin alguna condición.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from random import Random

import numpy as np
import pandas as pd

PARTICIONES = ("train", "validation", "test")


@dataclass(frozen=True)
class SplitConfig:
    """Proporciones del reparto, en sesiones."""

    train: float = 0.6
    validation: float = 0.2
    test: float = 0.2
    seed: int = 20260901

    def __post_init__(self) -> None:
        total = self.train + self.validation + self.test
        if abs(total - 1.0) > 1e-9:
            msg = f"Las proporciones deben sumar 1, suman {total}"
            raise ValueError(msg)
        if min(self.train, self.validation, self.test) <= 0:
            msg = "Ninguna partición puede quedar vacía"
            raise ValueError(msg)


@dataclass(frozen=True)
class Split:
    """Asignación de cada sesión a una partición."""

    assignment: dict[str, str]
    """session_id -> 'train' | 'validation' | 'test'"""
    config: SplitConfig

    def sessions(self, particion: str) -> set[str]:
        return {s for s, p in self.assignment.items() if p == particion}

    def mask(self, meta: pd.DataFrame, particion: str) -> np.ndarray:
        """Máscara booleana de las ventanas que caen en una partición."""
        return meta["session_id"].isin(self.sessions(particion)).to_numpy(dtype=bool)

    def summary(self, meta: pd.DataFrame) -> pd.DataFrame:
        """Sesiones y ventanas por partición y condición."""
        marco = meta.copy()
        marco["partition"] = marco["session_id"].map(self.assignment)
        agrupado = marco.groupby(["partition", "session_fault_id"]).agg(
            sessions=("session_id", "nunique"), windows=("session_id", "size")
        )
        return agrupado.reset_index()


def split_by_session(meta: pd.DataFrame, config: SplitConfig | None = None) -> Split:
    """Reparte las sesiones, estratificando por condición."""
    cfg = config or SplitConfig()
    rng = Random(cfg.seed)

    por_condicion: dict[str, list[str]] = defaultdict(list)
    for session_id, grupo in meta.groupby("session_id", sort=True):
        por_condicion[str(grupo["session_fault_id"].iloc[0])].append(str(session_id))

    asignacion: dict[str, str] = {}
    for condicion in sorted(por_condicion):
        sesiones = sorted(por_condicion[condicion])
        if len(sesiones) < len(PARTICIONES):
            msg = (
                f"La condición {condicion} tiene {len(sesiones)} sesión(es): "
                f"no alcanzan para {len(PARTICIONES)} particiones sin dejar alguna vacía"
            )
            raise ValueError(msg)
        rng.shuffle(sesiones)

        n = len(sesiones)
        # Se redondea hacia arriba en validación y test para que ninguna quede
        # vacía cuando el número de sesiones es pequeño; el resto va a
        # entrenamiento, que es el que mejor tolera perder una.
        n_val = max(1, round(n * cfg.validation))
        n_test = max(1, round(n * cfg.test))
        n_train = n - n_val - n_test
        if n_train < 1:
            msg = f"La condición {condicion} se queda sin sesiones de entrenamiento"
            raise ValueError(msg)

        for sesion in sesiones[:n_train]:
            asignacion[sesion] = "train"
        for sesion in sesiones[n_train : n_train + n_val]:
            asignacion[sesion] = "validation"
        for sesion in sesiones[n_train + n_val :]:
            asignacion[sesion] = "test"

    return Split(assignment=asignacion, config=cfg)


@dataclass(frozen=True)
class LeakageReport:
    """Resultado de auditar un reparto."""

    shared_sessions: dict[tuple[str, str], set[str]]
    empty_partitions: list[str]
    missing_classes: dict[str, set[str]]

    @property
    def ok(self) -> bool:
        return not self.shared_sessions and not self.empty_partitions

    def __str__(self) -> str:
        if self.ok and not self.missing_classes:
            return "Reparto sin fuga: ninguna sesión aparece en dos particiones."
        lineas: list[str] = []
        for (a, b), sesiones in self.shared_sessions.items():
            lineas.append(f"FUGA: {len(sesiones)} sesión(es) compartidas entre {a} y {b}")
        for particion in self.empty_partitions:
            lineas.append(f"VACÍA: la partición {particion} no tiene ventanas")
        for particion, clases in self.missing_classes.items():
            lineas.append(f"AVISO: {particion} no contiene {sorted(clases)}")
        return "\n".join(lineas)


def audit_split(split: Split, meta: pd.DataFrame, y: np.ndarray) -> LeakageReport:
    """Comprueba que el reparto no filtra información entre particiones.

    Se ejecuta siempre, no solo en los tests: un reparto correcto hoy puede
    dejar de serlo cuando cambie el generador o la geometría de las ventanas.
    """
    conjuntos = {p: split.sessions(p) for p in PARTICIONES}

    compartidas: dict[tuple[str, str], set[str]] = {}
    for i, a in enumerate(PARTICIONES):
        for b in PARTICIONES[i + 1 :]:
            comun = conjuntos[a] & conjuntos[b]
            if comun:
                compartidas[(a, b)] = comun

    vacias: list[str] = []
    faltantes: dict[str, set[str]] = {}
    todas_las_clases = set(np.unique(y).tolist())
    for particion in PARTICIONES:
        mascara = split.mask(meta, particion)
        if not mascara.any():
            vacias.append(particion)
            continue
        presentes = set(np.unique(y[mascara]).tolist())
        ausentes = todas_las_clases - presentes
        if ausentes:
            faltantes[particion] = ausentes

    return LeakageReport(
        shared_sessions=compartidas, empty_partitions=vacias, missing_classes=faltantes
    )


def audit_masks(meta: pd.DataFrame, masks: dict[str, np.ndarray]) -> LeakageReport:
    """Audita máscaras de ventanas arbitrarias, vengan de donde vengan.

    ``audit_split`` no puede detectar una fuga: su entrada es un diccionario
    ``sesión -> partición``, y ahí una sesión no puede estar en dos sitios. Esa
    es una garantía estructural, más fuerte que una comprobación, pero solo cubre
    los repartos construidos con ``split_by_session``.

    Esta función cubre el caso que sí ocurre: alguien reparte ventanas
    directamente --al azar, o con la herramienta de turno-- y las ventanas de una
    misma sesión acaban en particiones distintas. Es el error clásico, no da
    ningún síntoma y mejora las métricas.

    Se usa antes de entrenar, sobre las máscaras que realmente se van a emplear.
    """
    conjuntos = {
        nombre: set(meta.loc[mascara, "session_id"].unique().tolist())
        for nombre, mascara in masks.items()
    }
    nombres = list(masks)

    compartidas: dict[tuple[str, str], set[str]] = {}
    for i, a in enumerate(nombres):
        for b in nombres[i + 1 :]:
            comun = conjuntos[a] & conjuntos[b]
            if comun:
                compartidas[(a, b)] = comun

    vacias = [nombre for nombre, mascara in masks.items() if not mascara.any()]
    return LeakageReport(shared_sessions=compartidas, empty_partitions=vacias, missing_classes={})
