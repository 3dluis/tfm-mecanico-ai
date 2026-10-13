"""Reparto **dentro** de entrenamiento: ajuste, desarrollo y calibración.

``split_by_session`` reparte en entrenamiento, validación y prueba. Eso no basta
para comparar dos modelos de forma interpretable, por dos motivos que se
descubrieron auditando lo ya publicado:

1. **La época de la red se eligió mirando validación**, que es el conjunto sobre
   el que después se reporta. Un modelo que elige su punto de parada sobre el
   conjunto que lo mide tiene una ventaja que el bosque no tiene, porque el
   bosque no tiene paso de selección equivalente.
2. **El calibrador se ajustaba con validación cruzada por muestra**, de modo que
   ventanas solapadas de una misma sesión caían a la vez en el pliegue que
   ajusta el modelo y en el que ajusta el calibrador: justo la fuga que el
   reparto por sesión evita en todo lo demás.

Se corrigen con **tres** particiones internas de entrenamiento, repartidas por
sesión y disjuntas:

* **ajuste** --donde se entrena--;
* **desarrollo** --donde se elige la época y, si se tocaran, los
  hiperparámetros--;
* **calibración** --donde se ajusta el calibrador de los dos modelos--.

La tercera no es un lujo. Calibrar sobre desarrollo reutilizaría las
predicciones con que se eligió la época, que están sesgadas a favor de la red
precisamente por haberse elegido mirándolas; el bosque no pasa por ese filtro, y
la asimetría volvería por la puerta de atrás.

**Validación queda fuera de las tres** y no interviene en ninguna decisión de
ajuste. Prueba sigue cerrada.

## Los subconjuntos anidados de la curva de volumen

``subconjuntos_anidados`` construye T6 ⊂ T12 ⊂ T18 ⊂ T22 **por sesión**, con una
permutación declarada por semilla. El anidamiento es estructural y no un
resultado del sorteo: cada punto es un prefijo del siguiente sobre la misma
permutación, de modo que pasar de un punto al siguiente solo **añade** sesiones.
Sin eso, cambiar el volumen cambiaría además *qué* sesiones hay, y la curva
mezclaría las dos cosas.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from random import Random

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths

#: Semillas pre-registradas de las cinco réplicas, con su regla y la dependencia
#: entre ellas escrita al lado. Se leen del fichero y no se copian aquí para que
#: no haya dos versiones de la misma decisión.
RUTA_SEMILLAS = paths.CONFIGS / "semillas_pi1.json"


def semillas_preregistradas(ruta: Path | None = None) -> tuple[int, ...]:
    """Las cinco semillas, tal como quedaron fijadas antes de generar nada."""
    contenido = json.loads((ruta or RUTA_SEMILLAS).read_text("utf-8"))
    semillas = tuple(int(s) for s in contenido["semillas"])
    if len(set(semillas)) != len(semillas):
        msg = f"Hay semillas repetidas en {RUTA_SEMILLAS.name}: {semillas}"
        raise ValueError(msg)
    return semillas


#: Las tres particiones internas de entrenamiento, en el orden en que se usan.
PARTICIONES_INTERNAS: tuple[str, ...] = ("ajuste", "desarrollo", "calibracion")


class RepartoInternoInviableError(ValueError):
    """El reparto interno no puede construirse sin dejar algo vacío."""


@dataclass(frozen=True)
class ConfigInterna:
    """Proporciones del reparto interno, en sesiones.

    Las proporciones por omisión --4/6, 1/6, 1/6-- salen de que el punto más
    pequeño de la curva de volumen tiene seis sesiones de entrenamiento por
    condición: dan 4/1/1, que es el reparto más pequeño en que las tres
    particiones existen.
    """

    ajuste: float = 4.0 / 6.0
    desarrollo: float = 1.0 / 6.0
    calibracion: float = 1.0 / 6.0
    seed: int = 20260901

    def __post_init__(self) -> None:
        total = self.ajuste + self.desarrollo + self.calibracion
        if abs(total - 1.0) > 1e-9:
            msg = f"Las proporciones deben sumar 1, suman {total}"
            raise ValueError(msg)
        if min(self.ajuste, self.desarrollo, self.calibracion) <= 0:
            msg = "Ninguna partición interna puede quedar vacía por configuración"
            raise ValueError(msg)


@dataclass(frozen=True)
class RepartoInterno:
    """Asignación de cada sesión de entrenamiento a una partición interna."""

    assignment: dict[str, str]
    """session_id -> 'ajuste' | 'desarrollo' | 'calibracion'"""
    config: ConfigInterna

    def sessions(self, particion: str) -> set[str]:
        if particion not in PARTICIONES_INTERNAS:
            msg = f"Partición interna desconocida: {particion!r}"
            raise ValueError(msg)
        return {s for s, p in self.assignment.items() if p == particion}

    def mask(self, meta: pd.DataFrame, particion: str) -> np.ndarray:
        """Máscara de las ventanas de una partición interna."""
        return meta["session_id"].isin(self.sessions(particion)).to_numpy(dtype=bool)

    def resumen(self, meta: pd.DataFrame) -> pd.DataFrame:
        """Sesiones y ventanas por partición interna y condición."""
        marco = meta[meta["session_id"].isin(self.assignment)].copy()
        marco["particion_interna"] = marco["session_id"].map(self.assignment)
        agrupado = marco.groupby(["particion_interna", "session_fault_id"]).agg(
            sesiones=("session_id", "nunique"), ventanas=("session_id", "size")
        )
        return agrupado.reset_index()


def _por_condicion(meta: pd.DataFrame, sesiones: set[str]) -> dict[str, list[str]]:
    agrupado: dict[str, list[str]] = defaultdict(list)
    for session_id, grupo in meta.groupby("session_id", sort=True):
        if str(session_id) in sesiones:
            agrupado[str(grupo["session_fault_id"].iloc[0])].append(str(session_id))
    return agrupado


def repartir_interno(
    meta: pd.DataFrame,
    sesiones_entrenamiento: set[str],
    config: ConfigInterna | None = None,
) -> RepartoInterno:
    """Reparte las sesiones de entrenamiento en las tres particiones internas.

    Estratifica por condición y **falla si alguna condición no alcanza para las
    tres**, en lugar de dejar una vacía en silencio: un reparto en que una
    condición no aparece en calibración produce un calibrador que no ha visto
    esa clase, y eso no se detecta mirando la métrica agregada.
    """
    cfg = config or ConfigInterna()
    rng = Random(cfg.seed)
    agrupado = _por_condicion(meta, sesiones_entrenamiento)

    sin_datos = sesiones_entrenamiento - {s for v in agrupado.values() for s in v}
    if sin_datos:
        msg = (
            f"{len(sin_datos)} sesión(es) de entrenamiento sin ventanas en meta: "
            f"{sorted(sin_datos)[:3]}"
        )
        raise RepartoInternoInviableError(msg)
    if not agrupado:
        msg = "Ninguna sesión de entrenamiento encontrada en meta"
        raise RepartoInternoInviableError(msg)

    asignacion: dict[str, str] = {}
    for condicion in sorted(agrupado):
        lista = sorted(agrupado[condicion])
        if len(lista) < len(PARTICIONES_INTERNAS):
            msg = (
                f"La condición {condicion} tiene {len(lista)} sesión(es) de entrenamiento: "
                f"no alcanzan para {len(PARTICIONES_INTERNAS)} particiones internas"
            )
            raise RepartoInternoInviableError(msg)
        rng.shuffle(lista)

        n = len(lista)
        # Desarrollo y calibración redondean hacia arriba con mínimo uno: son
        # las que se quedan sin nada cuando el punto es pequeño, y una de ellas
        # vacía invalida el protocolo entero. Ajuste absorbe el resto.
        n_des = max(1, round(n * cfg.desarrollo))
        n_cal = max(1, round(n * cfg.calibracion))
        n_aj = n - n_des - n_cal
        if n_aj < 1:
            msg = f"La condición {condicion} se queda sin sesiones de ajuste"
            raise RepartoInternoInviableError(msg)

        for sesion in lista[:n_aj]:
            asignacion[sesion] = "ajuste"
        for sesion in lista[n_aj : n_aj + n_des]:
            asignacion[sesion] = "desarrollo"
        for sesion in lista[n_aj + n_des :]:
            asignacion[sesion] = "calibracion"

    return RepartoInterno(assignment=asignacion, config=cfg)


@dataclass(frozen=True)
class AuditoriaInterna:
    """Resultado de auditar un reparto interno."""

    compartidas: dict[tuple[str, str], set[str]]
    vacias: list[str]
    clases_ausentes: dict[str, set[str]]
    sesiones_por_particion: dict[str, int]

    @property
    def ok(self) -> bool:
        return not self.compartidas and not self.vacias and not self.clases_ausentes

    def __str__(self) -> str:
        if self.ok:
            cuenta = ", ".join(f"{p} {n}" for p, n in self.sesiones_por_particion.items())
            return f"Reparto interno viable y sin fuga: {cuenta} sesión(es)."
        lineas: list[str] = []
        for (a, b), sesiones in self.compartidas.items():
            lineas.append(f"FUGA: {len(sesiones)} sesión(es) compartidas entre {a} y {b}")
        for particion in self.vacias:
            lineas.append(f"VACÍA: la partición interna {particion} no tiene ventanas")
        for particion, clases in self.clases_ausentes.items():
            lineas.append(f"SIN CLASE: {particion} no contiene {sorted(clases)}")
        return "\n".join(lineas)


def auditar_interno(
    reparto: RepartoInterno,
    meta: pd.DataFrame,
    y: np.ndarray,
    *,
    validacion: set[str] | None = None,
    prueba: set[str] | None = None,
) -> AuditoriaInterna:
    """Comprueba que el reparto interno es viable y no toca lo que no debe.

    «No toca lo que no debe» incluye validación y prueba: si una sesión de
    validación aparece en una partición interna, la selección de época la estaría
    usando y la corrección no habría servido para nada.
    """
    conjuntos = {p: reparto.sessions(p) for p in PARTICIONES_INTERNAS}
    externos = {"validacion": validacion or set(), "prueba": prueba or set()}

    compartidas: dict[tuple[str, str], set[str]] = {}
    nombres = list(conjuntos) + [n for n, s in externos.items() if s]
    todos = {**conjuntos, **{n: s for n, s in externos.items() if s}}
    for i, a in enumerate(nombres):
        for b in nombres[i + 1 :]:
            comun = todos[a] & todos[b]
            if comun:
                compartidas[(a, b)] = comun

    clases = set(np.unique(y).tolist())
    vacias: list[str] = []
    ausentes: dict[str, set[str]] = {}
    for particion, sesiones in conjuntos.items():
        mascara = meta["session_id"].isin(sesiones).to_numpy(dtype=bool)
        if not mascara.any():
            vacias.append(particion)
            continue
        faltan = clases - set(np.unique(y[mascara]).tolist())
        if faltan:
            ausentes[particion] = faltan

    return AuditoriaInterna(
        compartidas=compartidas,
        vacias=vacias,
        clases_ausentes=ausentes,
        sesiones_por_particion={p: len(s) for p, s in conjuntos.items()},
    )


#: Los cuatro puntos de la curva de volumen, en sesiones de entrenamiento **por
#: condición**. El más alto, 22, es el que tiene `synthetic_v3`: la curva
#: reproduce el volumen ya explorado con el generador calibrado, no lo amplía.
PUNTOS_DE_VOLUMEN: tuple[int, ...] = (6, 12, 18, 22)


def subconjuntos_anidados(
    meta: pd.DataFrame,
    sesiones_entrenamiento: set[str],
    *,
    puntos: tuple[int, ...] = PUNTOS_DE_VOLUMEN,
    seed: int = 20260901,
) -> dict[int, set[str]]:
    """Construye los subconjuntos anidados de la curva de volumen.

    Devuelve, para cada punto, las sesiones de entrenamiento que lo componen:
    ``puntos[i]`` sesiones **por condición**, tomadas como prefijo de una única
    permutación por condición. El anidamiento es por tanto estructural.
    """
    if sorted(puntos) != list(puntos) or len(set(puntos)) != len(puntos):
        msg = f"Los puntos deben ser estrictamente crecientes, recibidos {puntos}"
        raise ValueError(msg)

    rng = Random(seed)
    agrupado = _por_condicion(meta, sesiones_entrenamiento)
    if not agrupado:
        msg = "Ninguna sesión de entrenamiento encontrada en meta"
        raise RepartoInternoInviableError(msg)

    permutado: dict[str, list[str]] = {}
    for condicion in sorted(agrupado):
        lista = sorted(agrupado[condicion])
        if len(lista) < max(puntos):
            msg = (
                f"La condición {condicion} tiene {len(lista)} sesión(es) de entrenamiento "
                f"y el punto más alto pide {max(puntos)}"
            )
            raise RepartoInternoInviableError(msg)
        rng.shuffle(lista)
        permutado[condicion] = lista

    return {n: {s for lista in permutado.values() for s in lista[:n]} for n in puntos}


def comprobar_anidamiento(subconjuntos: dict[int, set[str]]) -> None:
    """Falla si algún punto no contiene al anterior.

    Se comprueba en lugar de confiarse: el anidamiento es la propiedad de la que
    depende que la curva mida volumen y no realización.
    """
    puntos = sorted(subconjuntos)
    for menor, mayor in pairwise(puntos):
        if not subconjuntos[menor] <= subconjuntos[mayor]:
            fuera = subconjuntos[menor] - subconjuntos[mayor]
            msg = f"T{menor} no está contenido en T{mayor}: {len(fuera)} sesión(es) fuera"
            raise RepartoInternoInviableError(msg)


@dataclass(frozen=True)
class PlanDePunto:
    """El reparto completo de un punto de la curva, antes de entrenar nada.

    Se construye y se audita **por separado del entrenamiento** a propósito: un
    plan que no cuadra se descubre en segundos, y descubrirlo después de media
    hora de ajuste no aporta nada.
    """

    punto: int
    semilla: int
    sesiones: frozenset[str]
    reparto: RepartoInterno
    auditoria: AuditoriaInterna

    @property
    def viable(self) -> bool:
        return self.auditoria.ok

    def resumen(self) -> str:
        cuenta = ", ".join(f"{p} {n}" for p, n in self.auditoria.sesiones_por_particion.items())
        estado = "viable" if self.viable else "INVIABLE"
        return (
            f"T{self.punto} semilla {self.semilla}: {len(self.sesiones)} sesiones "
            f"({cuenta}) — {estado}"
        )


def planificar(
    meta: pd.DataFrame,
    sesiones_entrenamiento: set[str],
    y: np.ndarray,
    *,
    semilla: int,
    puntos: tuple[int, ...] = PUNTOS_DE_VOLUMEN,
    validacion: set[str] | None = None,
    prueba: set[str] | None = None,
) -> list[PlanDePunto]:
    """Construye y audita el plan de los cuatro puntos para una semilla.

    No entrena, no lee la partición de prueba y no escribe nada. Lo único que
    hace es dejar por escrito, antes de ejecutar, qué sesiones entran en cada
    punto y en cada partición interna, y comprobar que las tres existen con
    todas las clases en cada una.
    """
    subconjuntos = subconjuntos_anidados(meta, sesiones_entrenamiento, puntos=puntos, seed=semilla)
    comprobar_anidamiento(subconjuntos)

    planes: list[PlanDePunto] = []
    for punto in sorted(subconjuntos):
        sesiones = subconjuntos[punto]
        reparto = repartir_interno(meta, sesiones, ConfigInterna(seed=semilla))
        auditoria = auditar_interno(reparto, meta, y, validacion=validacion, prueba=prueba)
        planes.append(
            PlanDePunto(
                punto=punto,
                semilla=semilla,
                sesiones=frozenset(sesiones),
                reparto=reparto,
                auditoria=auditoria,
            )
        )
    return planes
