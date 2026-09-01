"""El análisis exploratorio debe calcular lo que dice calcular."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mecanico_ia_exp.data.exploration import (
    BlockConfig,
    block_statistics,
    class_balance,
    cliffs_delta,
    correlation_matrix,
    cross_correlation,
    describe_signals,
    interpret_delta,
    missingness,
    separability,
    temporal_drift,
)
from mecanico_ia_exp.obd.faults import NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import (
    SessionSpec,
    build_balanced_specs,
    generate_dataset,
    generate_session,
)


@pytest.fixture(scope="module")
def datos() -> pd.DataFrame:
    specs = build_balanced_specs(seed=101, sessions_per_fault=2, duration_s=300.0)
    marco, _ = generate_dataset(specs, dataset_id="d_eda", seed=101)
    return marco


# ------------------------------------------------------------ tamaño de efecto


def _cliffs_delta_ingenuo(a: np.ndarray, b: np.ndarray) -> float:
    """Definición literal, cuadrática. Sirve de oráculo para la versión rápida."""
    mayores = sum(1 for x in a for y in b if x > y)
    menores = sum(1 for x in a for y in b if x < y)
    return (mayores - menores) / (len(a) * len(b))


def test_cliffs_delta_coincide_con_la_definicion() -> None:
    rng = np.random.default_rng(0)
    for _ in range(5):
        a = rng.normal(0.0, 1.0, 40)
        b = rng.normal(0.4, 1.5, 55)
        assert cliffs_delta(a, b) == pytest.approx(_cliffs_delta_ingenuo(a, b), abs=1e-12)


def test_cliffs_delta_de_una_muestra_consigo_misma_es_cero() -> None:
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert cliffs_delta(x, x) == pytest.approx(0.0)


def test_cliffs_delta_es_uno_cuando_no_hay_solape() -> None:
    assert cliffs_delta(np.array([10.0, 11.0]), np.array([1.0, 2.0])) == pytest.approx(1.0)
    assert cliffs_delta(np.array([1.0, 2.0]), np.array([10.0, 11.0])) == pytest.approx(-1.0)


def test_cliffs_delta_maneja_empates() -> None:
    # Con todos los valores iguales no hay dominancia en ninguna dirección.
    assert cliffs_delta(np.array([5.0, 5.0]), np.array([5.0, 5.0])) == pytest.approx(0.0)


def test_cliffs_delta_con_muestra_vacia_es_indefinido() -> None:
    assert np.isnan(cliffs_delta(np.array([]), np.array([1.0])))


def test_la_interpretacion_respeta_los_cortes_convencionales() -> None:
    assert interpret_delta(0.10) == "insignificante"
    assert interpret_delta(0.20) == "pequeño"
    assert interpret_delta(0.40) == "medio"
    assert interpret_delta(-0.80) == "grande"
    assert interpret_delta(float("nan")) == "indefinido"


# ----------------------------------------------------------------- descriptivos


def test_describe_cubre_todas_las_senales(datos: pd.DataFrame) -> None:
    resumen = describe_signals(datos)
    assert list(resumen["signal"]) == list(SIGNAL_NAMES)
    assert (resumen["missing"] == 0).all()


def test_los_datos_sinteticos_no_tienen_huecos(datos: pd.DataFrame) -> None:
    """Cero por construcción. Los reales no lo serán, y por eso se mide."""
    assert missingness(datos)["fraction"].max() == 0.0


def test_las_clases_estan_equilibradas(datos: pd.DataFrame) -> None:
    balance = class_balance(datos)
    assert balance["sessions"].nunique() == 1
    assert balance.loc[balance["fault_id"] == NORMAL_ID, "active_samples"].item() == 0


# --------------------------------------------------------------------- bloques


def test_los_bloques_no_cruzan_sesiones(datos: pd.DataFrame) -> None:
    bloques = block_statistics(datos, BlockConfig(length_s=60.0))
    esperados = len(datos["session_id"].unique()) * 5  # 300 s / 60 s
    assert len(bloques) == esperados


def test_cada_bloque_conserva_la_condicion_de_su_sesion(datos: pd.DataFrame) -> None:
    bloques = block_statistics(datos)
    por_sesion = bloques.groupby("session_id")["fault_id"].nunique()
    assert (por_sesion == 1).all()


# --------------------------------------------------------------- separabilidad


def test_la_separabilidad_no_evalua_la_condicion_normal(datos: pd.DataFrame) -> None:
    tabla = separability(datos)
    assert NORMAL_ID not in set(tabla["fault_id"])


def test_la_sonda_lenta_se_separa_por_dispersion_y_no_por_nivel(datos: pd.DataFrame) -> None:
    """El hallazgo de E2, convertido en test: si se midiera solo el nivel, esta
    condición se declararía indetectable siendo perfectamente separable."""
    tabla = separability(datos)
    fila = tabla[(tabla["fault_id"] == "F04_o2_lag") & (tabla["signal"] == "oxygen_sensor")]
    nivel = abs(float(fila["delta_level"].item()))
    dispersion = abs(float(fila["delta_dispersion"].item()))
    assert dispersion > 0.9, f"dispersión no separa: {dispersion:.3f}"
    assert dispersion > nivel, f"nivel {nivel:.3f} >= dispersión {dispersion:.3f}"


def test_el_termostato_bloqueado_se_separa_por_temperatura(datos: pd.DataFrame) -> None:
    tabla = separability(datos)
    fila = tabla[
        (tabla["fault_id"] == "F03_thermostat_stuck") & (tabla["signal"] == "coolant_temperature")
    ]
    assert abs(float(fila["delta_level"].item())) > 0.5


# ------------------------------------------------------------------ relaciones


def test_la_matriz_de_correlacion_es_cuadrada_y_simetrica(datos: pd.DataFrame) -> None:
    matriz = correlation_matrix(datos)
    assert matriz.shape == (len(SIGNAL_NAMES), len(SIGNAL_NAMES))
    assert np.allclose(matriz.to_numpy(), matriz.to_numpy().T, equal_nan=True)
    assert np.allclose(np.diag(matriz.to_numpy()), 1.0)


def test_la_correlacion_cruzada_localiza_un_desfase_conocido() -> None:
    t = np.arange(400, dtype=float)
    x = np.sin(t * 0.15)
    desfase = 7
    y = np.roll(x, desfase)
    tabla = cross_correlation(x[50:-50], y[50:-50], max_lag=20)
    mejor = int(tabla.loc[tabla["r"].idxmax(), "lag"])
    # y = roll(x, 7) va retrasada 7 respecto de x, y la convención del módulo
    # declara ese caso como desfase positivo.
    assert mejor == desfase, f"desfase detectado {mejor}, esperado {desfase}"


def test_la_correlacion_cruzada_exige_series_de_igual_longitud() -> None:
    with pytest.raises(ValueError, match="misma longitud"):
        cross_correlation(np.zeros(10), np.zeros(11))


def test_la_deriva_del_caudalimetro_solo_se_ve_en_comparacion_pareada() -> None:
    """La deriva del caudalímetro existe, pero la pendiente de una sesión la
    domina el perfil de conducción, no el fallo.

    Sin parear, la pendiente del caudal varía entre -0,00007 y -0,044 según el
    régimen y la realización concreta: dos órdenes de magnitud por encima del
    efecto del fallo. Comparar sesiones distintas mide sobre todo cómo se
    condujo. Pareando --misma semilla, mismo perfil, con y sin fallo-- el efecto
    aparece limpio y con el signo esperado.

    De aquí sale un requisito para E5: una pendiente calculada sobre la señal
    cruda es mayoritariamente régimen, no fallo.
    """
    efectos: list[float] = []
    for seed in (11, 22, 33):
        for regime in ("urban", "highway"):
            base = SessionSpec(session_id="a", regime=regime, duration_s=600.0, seed=seed)
            con_fallo = SessionSpec(
                session_id="a",
                regime=regime,
                duration_s=600.0,
                seed=seed,
                fault_id="F02_maf_drift",
                fault_onset_s=120.0,
            )
            n = generate_session(base)
            f = generate_session(con_fallo)
            pn = float(np.polyfit(n["timestamp"], n["maf"], 1)[0])
            pf = float(np.polyfit(f["timestamp"], f["maf"], 1)[0])
            efectos.append(pf - pn)

    assert all(e < 0 for e in efectos), f"la deriva no reduce el caudal: {efectos}"


def test_temporal_drift_devuelve_una_pendiente_por_sesion(datos: pd.DataFrame) -> None:
    tabla = temporal_drift(datos, "maf")
    assert len(tabla) == datos["session_id"].nunique()
    assert tabla["slope_per_s"].notna().all()
