"""Particiones internas y subconjuntos anidados, sin tocar validación ni prueba."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mecanico_ia_exp.data.interno import (
    PARTICIONES_INTERNAS,
    PUNTOS_DE_VOLUMEN,
    ConfigInterna,
    RepartoInternoInviableError,
    auditar_interno,
    comprobar_anidamiento,
    planificar,
    repartir_interno,
    semillas_preregistradas,
    subconjuntos_anidados,
)

CONDICIONES = (
    "F00_normal",
    "F01_vacuum_leak",
    "F02_maf_drift",
    "F03_thermostat_stuck",
    "F04_o2_lag",
    "F05_misfire",
)


def _meta(sesiones_por_condicion: int, ventanas: int = 4) -> tuple[pd.DataFrame, np.ndarray]:
    """Metadatos sintéticos: ni se genera señal ni se lee ningún conjunto.

    Lo que se prueba es el reparto, que solo necesita identificadores y
    condiciones. Fabricarlos aquí mantiene el test rápido y lo deja
    independiente de cualquier partición real.
    """
    filas = []
    for condicion in CONDICIONES:
        for k in range(sesiones_por_condicion):
            for v in range(ventanas):
                filas.append(
                    {
                        "session_id": f"{condicion}__s{k:02d}",
                        "regime": "urban",
                        "session_fault_id": condicion,
                        "t_start": float(v * 60),
                        "t_end": float(v * 60 + 120),
                        "fault_active": condicion != "F00_normal",
                    }
                )
    meta = pd.DataFrame(filas)
    y = meta["session_fault_id"].to_numpy()
    return meta, y


def _sesiones(meta: pd.DataFrame) -> set[str]:
    return set(meta["session_id"].unique())


# ------------------------------------------------------------ reparto interno


def test_las_tres_particiones_existen_y_son_disjuntas() -> None:
    meta, _ = _meta(22)
    reparto = repartir_interno(meta, _sesiones(meta))
    conjuntos = [reparto.sessions(p) for p in PARTICIONES_INTERNAS]
    assert all(conjuntos)
    assert conjuntos[0] & conjuntos[1] == set()
    assert conjuntos[0] & conjuntos[2] == set()
    assert conjuntos[1] & conjuntos[2] == set()


def test_el_reparto_estratifica_por_condicion() -> None:
    meta, _ = _meta(22)
    reparto = repartir_interno(meta, _sesiones(meta))
    resumen = reparto.resumen(meta)
    for particion in PARTICIONES_INTERNAS:
        presentes = set(resumen.loc[resumen["particion_interna"] == particion, "session_fault_id"])
        assert presentes == set(CONDICIONES), f"{particion} no tiene las seis condiciones"


@pytest.mark.parametrize(
    ("punto", "esperado"),
    [(6, (4, 1, 1)), (12, (8, 2, 2)), (18, (12, 3, 3)), (22, (14, 4, 4))],
)
def test_el_reparto_de_cada_punto_es_el_declarado(punto: int, esperado: tuple[int, ...]) -> None:
    """4/1/1, 8/2/2, 12/3/3 y 14/4/4 por condición, como fija el protocolo."""
    meta, _ = _meta(punto)
    reparto = repartir_interno(meta, _sesiones(meta))
    cuenta = tuple(len(reparto.sessions(p)) // len(CONDICIONES) for p in PARTICIONES_INTERNAS)
    assert cuenta == esperado


def test_dos_sesiones_por_condicion_no_alcanzan() -> None:
    meta, _ = _meta(2)
    with pytest.raises(RepartoInternoInviableError, match="no alcanzan"):
        repartir_interno(meta, _sesiones(meta))


def test_una_sesion_sin_ventanas_es_un_error() -> None:
    meta, _ = _meta(6)
    with pytest.raises(RepartoInternoInviableError, match="sin ventanas"):
        repartir_interno(meta, {*_sesiones(meta), "fantasma"})


def test_la_misma_semilla_da_el_mismo_reparto() -> None:
    meta, _ = _meta(12)
    a = repartir_interno(meta, _sesiones(meta), ConfigInterna(seed=5))
    b = repartir_interno(meta, _sesiones(meta), ConfigInterna(seed=5))
    c = repartir_interno(meta, _sesiones(meta), ConfigInterna(seed=6))
    assert a.assignment == b.assignment
    assert a.assignment != c.assignment


def test_las_proporciones_tienen_que_sumar_uno() -> None:
    with pytest.raises(ValueError, match="suman"):
        ConfigInterna(ajuste=0.5, desarrollo=0.2, calibracion=0.2)


# ---------------------------------------------------------------- auditoría


def test_la_auditoria_aprueba_un_reparto_sano() -> None:
    meta, y = _meta(22)
    reparto = repartir_interno(meta, _sesiones(meta))
    informe = auditar_interno(reparto, meta, y)
    assert informe.ok, str(informe)
    assert sum(informe.sesiones_por_particion.values()) == len(_sesiones(meta))


def test_la_auditoria_detecta_una_sesion_de_validacion_dentro() -> None:
    """Si validación entra en el reparto interno, la corrección no sirve de nada."""
    meta, y = _meta(22)
    sesiones = _sesiones(meta)
    reparto = repartir_interno(meta, sesiones)
    intrusa = next(iter(reparto.sessions("desarrollo")))
    informe = auditar_interno(reparto, meta, y, validacion={intrusa})
    assert not informe.ok
    assert "desarrollo" in str(informe) and "validacion" in str(informe)


def test_la_auditoria_detecta_una_clase_ausente() -> None:
    meta, y = _meta(22)
    reparto = repartir_interno(meta, _sesiones(meta))
    # Una clase que el reparto no puede tener: ninguna sesión la lleva.
    y_con_fantasma = y.copy()
    y_con_fantasma[0] = "F99_inexistente"
    informe = auditar_interno(reparto, meta, y_con_fantasma)
    assert not informe.ok
    assert "F99_inexistente" in str(informe)


# ------------------------------------------------------ subconjuntos anidados


def test_los_subconjuntos_estan_anidados() -> None:
    meta, _ = _meta(22)
    subconjuntos = subconjuntos_anidados(meta, _sesiones(meta))
    comprobar_anidamiento(subconjuntos)
    for punto in PUNTOS_DE_VOLUMEN:
        assert len(subconjuntos[punto]) == punto * len(CONDICIONES)


def test_el_punto_mas_alto_son_132_sesiones() -> None:
    """Las mismas que tiene `synthetic_v3` de entrenamiento: la curva reproduce
    el volumen ya explorado, no lo amplía."""
    meta, _ = _meta(22)
    subconjuntos = subconjuntos_anidados(meta, _sesiones(meta))
    assert len(subconjuntos[22]) == 132


def test_el_anidamiento_falla_si_se_rompe() -> None:
    with pytest.raises(RepartoInternoInviableError, match="no está contenido"):
        comprobar_anidamiento({6: {"a", "b"}, 12: {"b", "c"}})


def test_no_alcanzan_las_sesiones_para_el_punto_mas_alto() -> None:
    meta, _ = _meta(10)
    with pytest.raises(RepartoInternoInviableError, match="pide 22"):
        subconjuntos_anidados(meta, _sesiones(meta))


def test_los_puntos_tienen_que_ser_crecientes() -> None:
    meta, _ = _meta(22)
    with pytest.raises(ValueError, match="crecientes"):
        subconjuntos_anidados(meta, _sesiones(meta), puntos=(12, 6))


# -------------------------------------------------------------- las semillas


def test_las_cinco_semillas_estan_preregistradas_y_son_distintas() -> None:
    semillas = semillas_preregistradas()
    assert len(semillas) == 5
    assert len(set(semillas)) == 5


# ------------------------------------------------------------------- el plan


def test_el_plan_cubre_los_cuatro_puntos_y_es_viable() -> None:
    meta, y = _meta(22)
    planes = planificar(meta, _sesiones(meta), y, semilla=semillas_preregistradas()[0])
    assert [p.punto for p in planes] == list(PUNTOS_DE_VOLUMEN)
    assert all(p.viable for p in planes), [p.resumen() for p in planes]


def test_el_plan_es_viable_con_las_cinco_semillas() -> None:
    """Una semilla que dejara una partición interna sin una clase invalidaría la
    réplica, y es mejor saberlo antes de entrenar que después."""
    meta, y = _meta(22)
    for semilla in semillas_preregistradas():
        for plan in planificar(meta, _sesiones(meta), y, semilla=semilla):
            assert plan.viable, plan.resumen()


def test_el_plan_no_mete_validacion_ni_prueba() -> None:
    meta, y = _meta(22)
    sesiones = _sesiones(meta)
    reservada = sorted(sesiones)[0]
    entrenamiento = sesiones - {reservada}
    with pytest.raises(RepartoInternoInviableError):
        # Con una sesión menos en una condición ya no alcanzan para T22.
        planificar(meta, entrenamiento, y, semilla=20260901)
