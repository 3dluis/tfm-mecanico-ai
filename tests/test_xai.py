"""Atribución: contrato de salida, fondo sin fuga y determinismo."""

from __future__ import annotations

import numpy as np
import pytest

from mecanico_ia_exp.xai.attribution import (
    FUNCION_EXPLICADA,
    CaseAttribution,
    SignalAttribution,
    select_background,
    split_feature_name,
)

NORMAL = "F00_normal"


# ------------------------------------------------------- nombres de descriptor


def test_un_descriptor_se_separa_en_senal_y_estadistico() -> None:
    """Ambos pueden llevar guiones bajos, así que no vale partir por el primero."""
    assert split_feature_name("coolant_temperature_delta_min") == (
        "coolant_temperature",
        "delta_min",
    )
    assert split_feature_name("rpm_mean") == ("rpm", "mean")
    assert split_feature_name("stft_bank1_autocorr1") == ("stft_bank1", "autocorr1")


def test_los_descriptores_de_correlacion_declaran_su_pareja() -> None:
    senal, estadistico = split_feature_name("corr_rpm_maf")
    assert senal == "rpm+maf"
    assert estadistico == "correlation"


def test_el_cociente_informado_por_la_fisica_se_reconoce() -> None:
    assert split_feature_name("maf_over_rpm_load") == ("maf", "ratio_rpm_load")


# ------------------------------------------------------------------- fondo


def test_el_fondo_sale_solo_de_muestras_normales() -> None:
    """Un fondo con fallos difuminaría el contraste que se quiere medir."""
    x = np.arange(60, dtype=np.float64).reshape(20, 3)
    y = np.array([NORMAL] * 10 + ["F01"] * 10)
    fondo, _ = select_background(x, y, normal_label=NORMAL, n=5)
    assert fondo.shape == (5, 3)
    # Todas las filas del fondo deben proceder de las diez primeras.
    assert all(fila[0] < 30 for fila in fondo)


def test_la_seleccion_del_fondo_es_determinista() -> None:
    """Sin esto, dos ejecuciones explican el mismo caso de forma distinta."""
    x = np.random.default_rng(0).normal(size=(40, 4))
    y = np.array([NORMAL] * 40)
    a, ha = select_background(x, y, normal_label=NORMAL, n=8, seed=7)
    b, hb = select_background(x, y, normal_label=NORMAL, n=8, seed=7)
    assert np.array_equal(a, b)
    assert ha == hb


def test_semillas_distintas_eligen_fondos_distintos() -> None:
    x = np.random.default_rng(0).normal(size=(40, 4))
    y = np.array([NORMAL] * 40)
    _, ha = select_background(x, y, normal_label=NORMAL, n=8, seed=1)
    _, hb = select_background(x, y, normal_label=NORMAL, n=8, seed=2)
    assert ha != hb


def test_la_huella_del_fondo_identifica_contra_que_se_comparo() -> None:
    x = np.random.default_rng(0).normal(size=(30, 3))
    y = np.array([NORMAL] * 30)
    _, huella = select_background(x, y, normal_label=NORMAL, n=5, seed=3)
    assert len(huella) == 16


def test_sin_muestras_normales_el_fondo_falla_con_mensaje_util() -> None:
    x = np.zeros((5, 2))
    y = np.array(["F01"] * 5)
    with pytest.raises(ValueError, match="No hay muestras"):
        select_background(x, y, normal_label=NORMAL)


# ------------------------------------------------------- contrato de salida


def _atribucion(**cambios: object) -> CaseAttribution:
    base: dict[str, object] = {
        "explanation_id": "m:c1",
        "case_id": "c1",
        "model_id": "m",
        "explained_function": FUNCION_EXPLICADA,
        "predicted_class": "F04_o2_lag",
        "confidence": 0.92,
        "attributions": (
            SignalAttribution(
                "oxygen_sensor_std", "oxygen_sensor", "std", -0.40, "decreases", 0.03
            ),
            SignalAttribution("stft_bank1_std", "stft_bank1", "std", 0.22, "increases", 2.9),
            SignalAttribution("rpm_mean", "rpm", "mean", 0.01, "neutral", 1800.0),
        ),
    }
    base.update(cambios)
    return CaseAttribution(**base)  # type: ignore[arg-type]


def test_xai_output_schema() -> None:
    """La salida identifica siempre qué función se explica."""
    datos = _atribucion().to_dict()
    assert datos["explained_function"] == FUNCION_EXPLICADA
    for clave in (
        "explanation_id",
        "case_id",
        "model_id",
        "predicted_class",
        "confidence",
        "attributions",
        "background_hash",
        "seed",
    ):
        assert clave in datos
    for atr in datos["attributions"]:
        assert set(atr) == {"feature", "signal", "statistic", "importance", "direction", "value"}


def test_cada_atribucion_declara_magnitud_y_direccion() -> None:
    """Sin dirección, «esta señal importa» no dice si subió o bajó."""
    for atr in _atribucion().attributions:
        assert atr.direction in {"increases", "decreases", "neutral"}


def test_las_señales_principales_se_ordenan_por_magnitud_absoluta() -> None:
    """Una contribución negativa grande importa tanto como una positiva grande."""
    a = _atribucion()
    principales = a.top(2)
    assert principales[0].feature == "oxygen_sensor_std"
    assert abs(principales[0].importance) >= abs(principales[1].importance)


def test_las_señales_se_devuelven_sin_repetir() -> None:
    a = _atribucion()
    señales = a.signals_involved(3)
    assert len(señales) == len(set(señales))
    assert señales[0] == "oxygen_sensor"


def test_la_ventana_temporal_viaja_con_la_atribucion() -> None:
    """Una observación sin ventana no se puede rastrear hasta el dato."""
    a = _atribucion(window_start_s=120.0, window_end_s=239.0, session_id="s1")
    datos = a.to_dict()
    assert datos["window_start_s"] == 120.0
    assert datos["window_end_s"] == 239.0
    assert datos["session_id"] == "s1"
