"""Ventanado, descriptores y reparto sin fuga.

El reparto es el punto donde un error no da la cara: las métricas salen mejores,
no peores. Por eso se audita explícitamente y no solo se confía en el código.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mecanico_ia_exp.data.exploration import noise_floor_max_delta
from mecanico_ia_exp.data.splits import (
    PARTICIONES,
    SplitConfig,
    audit_masks,
    audit_split,
    split_by_session,
)
from mecanico_ia_exp.features.temporal import (
    FEATURE_NAMES,
    extract_features,
)
from mecanico_ia_exp.obd.faults import NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import build_balanced_specs, generate_dataset
from mecanico_ia_exp.timeseries.windowing import WindowConfig, make_windows


@pytest.fixture(scope="module")
def datos() -> pd.DataFrame:
    specs = build_balanced_specs(seed=909, sessions_per_fault=4, duration_s=600.0)
    marco, _ = generate_dataset(specs, dataset_id="d_pre", seed=909)
    return marco


# ------------------------------------------------------------------ ventanado


def test_la_geometria_de_la_ventana_se_deriva_de_la_tasa() -> None:
    cfg = WindowConfig(length_s=120.0, stride_s=60.0, sample_rate_hz=1.0)
    assert cfg.n_steps == 120
    assert cfg.stride_steps == 60
    assert cfg.overlap_fraction == pytest.approx(0.5)


def test_un_paso_mayor_que_la_ventana_deja_huecos_y_se_rechaza() -> None:
    with pytest.raises(ValueError, match="huecos"):
        WindowConfig(length_s=30.0, stride_s=60.0)


def test_timeseries_windowing(datos: pd.DataFrame) -> None:
    """Las ventanas tienen la forma declarada y conservan su procedencia."""
    cfg = WindowConfig(length_s=120.0, stride_s=60.0)
    w = make_windows(datos, cfg)

    assert w.x.ndim == 3
    assert w.x.shape[1] == cfg.n_steps
    assert w.x.shape[2] == len(SIGNAL_NAMES)
    assert w.x.shape[0] == len(w.y) == len(w.meta)
    assert w.signals == SIGNAL_NAMES
    assert set(w.meta.columns) >= {"session_id", "regime", "session_fault_id", "t_start", "t_end"}


def test_ninguna_ventana_cruza_una_sesion(datos: pd.DataFrame) -> None:
    """Una ventana a caballo entre dos sesiones describiría algo que no ocurrió."""
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    duracion_esperada = w.config.length_s - 1.0 / w.config.sample_rate_hz
    duraciones = w.meta["t_end"] - w.meta["t_start"]
    assert np.allclose(duraciones.to_numpy(), duracion_esperada)


def test_ninguna_ventana_mezcla_normal_y_fallo(datos: pd.DataFrame) -> None:
    """Un tramo mitad normal y mitad averiado no pertenece a ninguna clase."""
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    assert w.n_discarded > 0, "con el fallo entrando a mitad de sesión debe descartarse alguna"

    for _, fila in w.meta.iterrows():
        etiqueta = w.y[int(fila.name)]
        if fila["fault_active"]:
            assert etiqueta == fila["session_fault_id"]
        else:
            assert etiqueta == NORMAL_ID


def test_las_ventanas_normales_de_una_sesion_averiada_se_etiquetan_como_normales(
    datos: pd.DataFrame,
) -> None:
    """Antes de que entre el fallo, la sesión es normal aunque acabe averiada."""
    w = make_windows(datos, WindowConfig(length_s=60.0, stride_s=60.0))
    previas = w.meta[(w.meta["session_fault_id"] != NORMAL_ID) & ~w.meta["fault_active"]]
    assert len(previas) > 0
    assert all(w.y[i] == NORMAL_ID for i in previas.index)


def test_una_ventana_mas_larga_que_la_sesion_se_rechaza_con_mensaje_util(
    datos: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="Ninguna ventana"):
        make_windows(datos, WindowConfig(length_s=9000.0, stride_s=9000.0))


# --------------------------------------------------------------- descriptores


def test_los_descriptores_tienen_el_orden_declarado(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    f = extract_features(w.x)
    assert f.shape == (len(w), len(FEATURE_NAMES))
    assert np.isfinite(f).all(), "ningún descriptor puede salir infinito o indefinido"


def test_los_descriptores_son_deterministas(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    assert np.array_equal(extract_features(w.x), extract_features(w.x))


def test_los_cruces_por_la_mediana_detectan_una_oscilacion_amortiguada() -> None:
    """Es el descriptor que separa una sonda sana de una lenta."""
    t = np.arange(120, dtype=np.float64)
    viva = np.sin(t * 0.6)
    apagada = np.sin(t * 0.6) * 0.02
    x = np.zeros((2, 120, len(SIGNAL_NAMES)), dtype=np.float64)
    x[0, :, 0] = viva
    x[1, :, 0] = apagada
    x[:, :, 1:] = 1.0
    f = extract_features(x)
    columna = FEATURE_NAMES.index("rpm_std")
    assert f[0, columna] > f[1, columna]


def test_se_rechaza_una_ventana_demasiado_corta() -> None:
    with pytest.raises(ValueError, match="no admite pendiente"):
        extract_features(np.zeros((2, 2, len(SIGNAL_NAMES))))


def test_se_rechaza_un_numero_de_senales_incoherente() -> None:
    with pytest.raises(ValueError, match="declaradas"):
        extract_features(np.zeros((2, 30, 3)))


# --------------------------------------------------------------------- fuga


def test_no_temporal_leakage(datos: pd.DataFrame) -> None:
    """Ninguna sesión aparece en dos particiones.

    Es *la* comprobación de esta fase. Si falla, toda métrica posterior mide
    memoria en lugar de capacidad de generalizar, y lo hace sin dar ningún aviso.
    """
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    reparto = split_by_session(w.meta)
    informe = audit_split(reparto, w.meta, w.y)

    assert informe.ok, str(informe)
    assert not informe.shared_sessions

    conjuntos = [reparto.sessions(p) for p in PARTICIONES]
    for i, a in enumerate(conjuntos):
        for b in conjuntos[i + 1 :]:
            assert not (a & b)


def test_ninguna_ventana_de_test_comparte_sesion_con_entrenamiento(
    datos: pd.DataFrame,
) -> None:
    """La misma comprobación, pero mirando las ventanas y no las etiquetas: es
    donde se manifestaría un fallo de la máscara."""
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    reparto = split_by_session(w.meta)
    sesiones_train = set(w.meta.loc[reparto.mask(w.meta, "train"), "session_id"])
    sesiones_test = set(w.meta.loc[reparto.mask(w.meta, "test"), "session_id"])
    assert not (sesiones_train & sesiones_test)


def test_las_tres_particiones_contienen_todas_las_condiciones(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    reparto = split_by_session(w.meta)
    informe = audit_split(reparto, w.meta, w.y)
    assert not informe.missing_classes, str(informe)


def test_el_reparto_es_reproducible(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    a = split_by_session(w.meta, SplitConfig(seed=123))
    b = split_by_session(w.meta, SplitConfig(seed=123))
    assert a.assignment == b.assignment


def test_semillas_distintas_reparten_distinto(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    a = split_by_session(w.meta, SplitConfig(seed=1))
    b = split_by_session(w.meta, SplitConfig(seed=2))
    assert a.assignment != b.assignment


def test_las_proporciones_deben_sumar_uno() -> None:
    with pytest.raises(ValueError, match="suman"):
        SplitConfig(train=0.5, validation=0.2, test=0.2)


def test_una_condicion_con_pocas_sesiones_se_rechaza_en_vez_de_degradarse() -> None:
    """Es preferible fallar ruidosamente a devolver una partición vacía."""
    meta = pd.DataFrame(
        {
            "session_id": ["s1", "s2"],
            "session_fault_id": [NORMAL_ID, NORMAL_ID],
            "regime": ["urban", "urban"],
        }
    )
    with pytest.raises(ValueError, match="no alcanzan"):
        split_by_session(meta)


def test_el_auditor_detecta_un_reparto_aleatorio_por_ventana(datos: pd.DataFrame) -> None:
    """El error clásico, provocado a propósito, debe detectarse.

    Un test que solo comprueba el caso correcto no demuestra que el auditor
    funcione. Aquí se reparten las ventanas al azar --que es lo que hace
    cualquier utilidad genérica de reparto-- y se exige que el auditor lo
    señale: las ventanas de una misma sesión acaban a ambos lados.
    """
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    rng = np.random.default_rng(0)
    sorteo = rng.random(len(w))
    mascaras = {
        "train": sorteo < 0.6,
        "validation": (sorteo >= 0.6) & (sorteo < 0.8),
        "test": sorteo >= 0.8,
    }

    informe = audit_masks(w.meta, mascaras)
    assert not informe.ok, "el auditor no detectó un reparto por ventana"
    assert informe.shared_sessions
    assert "FUGA" in str(informe)


def test_el_auditor_aprueba_el_reparto_por_sesion(datos: pd.DataFrame) -> None:
    """El mismo auditor, sobre el reparto correcto, no debe señalar nada."""
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    reparto = split_by_session(w.meta)
    mascaras = {p: reparto.mask(w.meta, p) for p in PARTICIONES}

    informe = audit_masks(w.meta, mascaras)
    assert informe.ok, str(informe)
    assert "sin fuga" in str(informe)


def test_el_auditor_detecta_una_particion_vacia(datos: pd.DataFrame) -> None:
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    vacia = np.zeros(len(w), dtype=bool)
    informe = audit_masks(w.meta, {"train": ~vacia, "test": vacia})
    assert not informe.ok
    assert "VACÍA" in str(informe)


# ------------------------------------------------------------ suelo de ruido


def test_el_suelo_de_ruido_es_positivo_y_menor_que_uno(datos: pd.DataFrame) -> None:
    """Con cientos de descriptores, el máximo tamaño de efecto está inflado
    aunque no haya ningún fallo. El control lo cuantifica."""
    w = make_windows(datos, WindowConfig(length_s=120.0, stride_s=60.0))
    f = extract_features(w.x)
    normal = w.y == NORMAL_ID
    suelo = noise_floor_max_delta(f[normal], w.meta.loc[normal, "session_id"], n_repeats=8)
    assert 0.0 < suelo < 1.0


def test_el_control_exige_al_menos_dos_sesiones() -> None:
    with pytest.raises(ValueError, match="dos sesiones"):
        noise_floor_max_delta(np.zeros((4, 3)), pd.Series(["s1"] * 4))
