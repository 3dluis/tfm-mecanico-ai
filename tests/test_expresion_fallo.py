"""La expresión efectiva de un fallo no es lo mismo que su etiqueta.

Los tests de este fichero usan **sesiones generadas en el momento**, nunca la
partición final ni ningún conjunto reservado para evaluación.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mecanico_ia_exp.obd.expresion import (
    RATIO_DECLARADO,
    SIGMA_GENERADOR,
    SIN_ALTERACION,
    desviacion,
    tolerancias,
)
from mecanico_ia_exp.obd.signals import COLUMNAS_DE_EXPRESION, SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import SessionSpec, generate_session


def _sesion(fault_id: str, regime: str = "urban", seed: int = 7) -> SessionSpec:
    return SessionSpec(
        session_id=f"s_{fault_id}",
        regime=regime,
        duration_s=600.0,
        seed=seed,
        fault_id=fault_id,
        fault_onset_s=0.0 if fault_id == "F00_normal" else 120.0,
    )


# ----------------------------------------------------- el umbral y su origen


def test_hay_ruido_declarado_para_las_doce_senales() -> None:
    assert set(SIGMA_GENERADOR) == set(SIGNAL_NAMES)


def test_cada_sigma_declarada_aparece_en_el_motor() -> None:
    """Si el motor cambia su ruido, el umbral deja de medir lo que dice medir.

    No es una comprobación elegante, pero detecta la deriva silenciosa entre el
    módulo que genera y el que declara cuánto ruido genera.
    """
    from mecanico_ia_exp.config import paths

    fuente = (paths.ROOT / "src/mecanico_ia_exp/obd/engine.py").read_text("utf-8")
    ausentes = [
        f"{nombre}={sigma}" for nombre, sigma in SIGMA_GENERADOR.items() if f"{sigma}" not in fuente
    ]
    assert not ausentes, f"sigmas que ya no aparecen en engine.py: {ausentes}"


def test_el_umbral_es_proporcional_a_la_razon() -> None:
    uno = tolerancias(0.1)
    doble = tolerancias(0.2)
    for nombre in SIGNAL_NAMES:
        assert doble[nombre] == pytest.approx(2 * uno[nombre])


def test_una_razon_no_positiva_se_rechaza() -> None:
    with pytest.raises(ValueError, match="positiva"):
        tolerancias(0.0)


def test_la_desviacion_senala_que_senal_se_altero() -> None:
    umbrales = tolerancias()
    base = dict.fromkeys(SIGNAL_NAMES, 0.0)
    alterado = {**base, "maf": umbrales["maf"] * 3.0}
    magnitud, cual = desviacion(alterado, base, umbrales)
    assert cual == "maf"
    assert magnitud == pytest.approx(3.0)


def test_sin_alteracion_no_se_nombra_ninguna_senal() -> None:
    umbrales = tolerancias()
    base = dict.fromkeys(SIGNAL_NAMES, 1.0)
    magnitud, cual = desviacion(dict(base), base, umbrales)
    assert magnitud == 0.0
    assert cual == SIN_ALTERACION


# ------------------------------------------------- lo que el generador escribe


def test_la_columna_de_expresion_no_altera_la_serie() -> None:
    """La comprobación que el protocolo exige: añadir la columna no cambia los datos.

    Se hace variando la razón del umbral en dos órdenes de magnitud: si los
    valores de señal dependieran del cálculo de expresión --por consumir número
    aleatorio, por ejemplo-- esto lo delataría.
    """
    spec = _sesion("F02_maf_drift")
    floja = generate_session(spec, ratio_expresion=10.0)
    fina = generate_session(spec, ratio_expresion=0.001)
    assert np.array_equal(floja[list(SIGNAL_NAMES)].to_numpy(), fina[list(SIGNAL_NAMES)].to_numpy())
    assert floja["fault_expressed"].sum() < fina["fault_expressed"].sum()


def test_una_sesion_sana_no_expresa_nada() -> None:
    datos = generate_session(_sesion("F00_normal"))
    assert not datos["fault_expressed"].any()
    assert (datos["fault_deviation_max"] == 0.0).all()
    assert (datos["fault_deviation_signal"] == SIN_ALTERACION).all()


def test_antes_de_la_entrada_del_fallo_no_hay_expresion() -> None:
    datos = generate_session(_sesion("F01_vacuum_leak"))
    previas = datos[datos["timestamp"] < 120.0]
    assert not previas["fault_expressed"].any()


def test_el_termostato_se_aplica_sin_expresarse_en_calentamiento() -> None:
    """El caso que motivó todo esto.

    En una sesión de calentamiento el refrigerante arranca a temperatura
    ambiente y tarda minutos en superar el tope del termostato. Mientras no lo
    supera, la función se aplica y **no cambia ni un valor**: la desviación es
    exactamente cero, no pequeña, de modo que la clasificación no depende del
    umbral.
    """
    datos = generate_session(_sesion("F03_thermostat_stuck", regime="warmup"))
    activas = datos[datos["fault_active"]]
    assert activas["fault_expressed"].any(), "al final de la sesión sí debe expresarse"
    sin_expresar = activas[~activas["fault_expressed"]]
    assert len(sin_expresar) > 0, "en calentamiento tiene que haber muestras sin expresión"
    assert (sin_expresar["fault_deviation_max"] == 0.0).all()


def test_el_fallo_de_encendido_solo_se_expresa_en_sus_episodios() -> None:
    datos = generate_session(_sesion("F05_misfire"))
    activas = datos[datos["fault_active"]]
    expresadas = int(activas["fault_expressed"].sum())
    assert 0 < expresadas < len(activas), "es episódico: ni ninguna ni todas"
    assert (activas.loc[~activas["fault_expressed"], "fault_deviation_max"] == 0.0).all()


def test_la_senal_alterada_esta_entre_las_que_la_ficha_declara() -> None:
    """Si el fallo altera una señal que su ficha no menciona, la ficha miente."""
    from mecanico_ia_exp.obd.faults import FAULTS

    for fault_id, definicion in FAULTS.items():
        datos = generate_session(_sesion(fault_id, regime="urban"))
        alteradas = {
            s
            for s in datos.loc[datos["fault_expressed"], "fault_deviation_signal"].unique()
            if s != SIN_ALTERACION
        }
        fuera = alteradas - set(definicion.affected_signals)
        assert not fuera, f"{fault_id} altera {fuera}, que no están en affected_signals"


def test_la_magnitud_permite_releer_con_otro_umbral() -> None:
    """Una lectura más estricta no obliga a regenerar: basta reescalar.

    Es la propiedad que hace que el dato no lleve la decisión horneada.
    """
    spec = _sesion("F03_thermostat_stuck", regime="warmup")
    guardado = generate_session(spec)
    estricto = generate_session(spec, ratio_expresion=RATIO_DECLARADO * 4.0)
    relectura = guardado["fault_deviation_max"] >= 4.0
    assert np.array_equal(relectura.to_numpy(), estricto["fault_expressed"].to_numpy())


# ---------------------------------------------------- agregación por ventana


def test_la_ventana_conserva_la_fraccion_expresada_y_no_se_descarta() -> None:
    from mecanico_ia_exp.obd.synthetic import generate_dataset
    from mecanico_ia_exp.timeseries.windowing import make_windows

    specs = [
        SessionSpec(
            session_id=f"F03_thermostat_stuck__warmup__{k:02d}",
            regime="warmup",
            duration_s=600.0,
            seed=10 + k,
            fault_id="F03_thermostat_stuck",
            fault_onset_s=120.0,
        )
        for k in range(2)
    ]
    datos, _ = generate_dataset(specs, dataset_id="prueba_expresion", seed=1)
    ventanas = make_windows(datos)

    for columna in ("n_expressed", "fraction_expressed", "deviation_max", "fault_expressed"):
        assert columna in ventanas.meta.columns

    con_fallo = ventanas.meta[ventanas.meta["fault_active"]]
    sin_senal = con_fallo[con_fallo["n_expressed"] == 0]
    assert len(sin_senal) > 0, "en calentamiento hay ventanas etiquetadas y sin señal"
    # Y siguen estando: ninguna se eliminó por no expresar el fallo.
    assert len(con_fallo) == int(ventanas.meta["fault_active"].sum())


def test_sin_las_columnas_el_ventanado_sigue_funcionando() -> None:
    """Los conjuntos anteriores no las tienen y tienen que seguir leyéndose."""
    from mecanico_ia_exp.obd.synthetic import generate_dataset
    from mecanico_ia_exp.timeseries.windowing import make_windows

    specs = [_sesion("F01_vacuum_leak")]
    datos, _ = generate_dataset(specs, dataset_id="sin_expresion", seed=1)
    antiguo = datos.drop(columns=list(COLUMNAS_DE_EXPRESION))
    ventanas = make_windows(antiguo)
    assert len(ventanas) > 0
    assert "n_expressed" not in ventanas.meta.columns


def test_la_fraccion_expresada_esta_entre_cero_y_uno() -> None:
    from mecanico_ia_exp.obd.synthetic import generate_dataset
    from mecanico_ia_exp.timeseries.windowing import make_windows

    specs = [
        _sesion(f, regime="urban", seed=20 + i) for i, f in enumerate(("F05_misfire", "F04_o2_lag"))
    ]
    datos, _ = generate_dataset(specs, dataset_id="rango_fraccion", seed=1)
    meta: pd.DataFrame = make_windows(datos).meta
    assert meta["fraction_expressed"].between(0.0, 1.0).all()
