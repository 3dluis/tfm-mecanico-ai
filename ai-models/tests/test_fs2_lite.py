"""Tests de fs2-lite (extracción + esquema + GT generalizado) — F17, EXP-ANOM-008."""

import math

import numpy as np
import pytest

from ai_models.features.fs2_lite import (
    FS2_LITE_NAMES,
    MULTISCALE_BLOCK,
    REF_S,
    REPLACED,
    SessionTrimReference,
    fs2lite_features,
    fs2lite_vector,
    session_reference,
)
from ai_models.features.schema import FS1, FS2_LITE, validate_fs2_lite_against_extraction
from ai_models.xai.ground_truth import gt_features_for
from ai_models.xai.shap_runner import attributions_as_dict
from mecanico_contracts.features import CANONICAL_PIDS, FEATURE_NAMES

W = 60  # ventana canónica (ADR-0011)


def _window(seed: int = 7, ltft_level: float = 3.0) -> dict[str, list[float]]:
    """Ventana sintética determinista con las 12 señales canónicas."""
    rng = np.random.default_rng(seed)
    win = {pid: list(rng.normal(50.0, 5.0, W)) for pid in CANONICAL_PIDS}
    win["LONG_FUEL_TRIM_1"] = list(rng.normal(ltft_level, 0.4, W))
    win["SHORT_FUEL_TRIM_1"] = list(rng.normal(0.5, 0.3, W))
    return win


def _ref() -> SessionTrimReference:
    return SessionTrimReference(ltft_ref=1.0, total_trim_ref=1.5)


# ---------------------------------------------------------------- esquema / nombres


def test_fs2_lite_tiene_48_features_y_orden_estable() -> None:
    assert len(FS2_LITE_NAMES) == 48
    assert len(set(FS2_LITE_NAMES)) == 48
    # los absolutos sustituidos NO están; el resto de fs1 se conserva
    assert not set(REPLACED) & set(FS2_LITE_NAMES)
    assert set(FEATURE_NAMES) - set(REPLACED) < set(FS2_LITE_NAMES)


def test_esquema_fs2_lite_coincide_con_extraccion() -> None:
    validate_fs2_lite_against_extraction()
    assert FS2_LITE.names == list(FS2_LITE_NAMES)
    assert FS2_LITE.schema_id == "fs2-lite"
    assert "experimental" in FS2_LITE.status  # NO canónico: prohibido fuera de ai-models


def test_vector_sigue_el_orden_de_nombres() -> None:
    win = _window()
    feats = fs2lite_features(win, _ref())
    vec = fs2lite_vector(win, _ref())
    assert vec == [feats[n] for n in FS2_LITE_NAMES]
    assert len(vec) == 48


def test_extraccion_determinista() -> None:
    win = _window()
    assert fs2lite_vector(win, _ref()) == fs2lite_vector(dict(win), _ref())


# ---------------------------------------------------------------- referencia de sesión


def test_referencia_usa_solo_los_primeros_ref_s_segundos() -> None:
    """Anti-leakage intra-sesión: nada posterior al arranque altera la referencia."""
    rng = np.random.default_rng(11)
    ltft = list(rng.normal(2.0, 0.5, 600))
    stft = list(rng.normal(0.0, 0.3, 600))
    ref_a = session_reference(ltft, stft)
    ltft_b = ltft[:REF_S] + [999.0] * (len(ltft) - REF_S)
    stft_b = stft[:REF_S] + [999.0] * (len(stft) - REF_S)
    assert session_reference(ltft_b, stft_b) == ref_a


def test_referencia_sesion_corta_usa_lo_disponible_y_vacia_falla() -> None:
    ref = session_reference([2.0] * 30, [1.0] * 30)
    assert ref.ltft_ref == pytest.approx(2.0)
    assert ref.total_trim_ref == pytest.approx(3.0)
    with pytest.raises(ValueError, match="vacía"):
        session_reference([], [])


def test_drift_cero_cuando_la_ventana_iguala_al_arranque() -> None:
    win = _window()
    ltft_mean = float(np.mean(win["LONG_FUEL_TRIM_1"]))
    total_mean = float(
        np.mean(
            [
                s + lt
                for s, lt in zip(win["SHORT_FUEL_TRIM_1"], win["LONG_FUEL_TRIM_1"], strict=True)
            ]
        )
    )
    ref = SessionTrimReference(ltft_ref=ltft_mean, total_trim_ref=total_mean)
    feats = fs2lite_features(win, ref)
    assert feats["LTFT_session_drift"] == pytest.approx(0.0, abs=1e-12)
    assert feats["total_trim_session_drift"] == pytest.approx(0.0, abs=1e-12)


def test_drift_detecta_offset_dentro_de_la_sesion() -> None:
    """La señal de fallo se conserva: LTFT que sube DESPUÉS del arranque → drift > 0."""
    feats = fs2lite_features(_window(ltft_level=6.0), _ref())
    assert feats["LTFT_session_drift"] == pytest.approx(5.0, abs=0.3)


def test_offset_legitimo_de_sesion_no_produce_drift() -> None:
    """La patología de EXP-ANOM-007 desaparece por construcción: dos sesiones con
    offsets absolutos distintos pero estables dan el MISMO drift (≈0)."""
    for level in (0.0, 4.0, 8.0):
        win = _window(seed=int(level) + 1, ltft_level=level)
        ltft = win["LONG_FUEL_TRIM_1"]
        stft = win["SHORT_FUEL_TRIM_1"]
        ref = session_reference(ltft, stft)  # arranque de la propia sesión, mismo nivel
        feats = fs2lite_features(win, ref)
        assert abs(feats["LTFT_session_drift"]) < 0.5


# ---------------------------------------------------------------- multiescala / lag-1


def test_multiscale_std_valor_conocido() -> None:
    win = _window()
    xs = win["RPM"]
    blocks = [
        float(np.std(xs[i * MULTISCALE_BLOCK : (i + 1) * MULTISCALE_BLOCK], ddof=1))
        for i in range(len(xs) // MULTISCALE_BLOCK)
    ]
    feats = fs2lite_features(win, _ref())
    assert feats["RPM_std_15"] == pytest.approx(float(np.mean(blocks)))


def test_multiscale_ventana_corta_falla() -> None:
    win = {pid: vals[: MULTISCALE_BLOCK - 1] for pid, vals in _window().items()}
    with pytest.raises(ValueError, match="multiescala"):
        fs2lite_features(win, _ref())


def test_lag1_corr_desplazamiento_exacto_y_constante() -> None:
    win = _window()
    ramp = [math.sin(i / 5.0) * 10.0 + i * 0.1 for i in range(W)]
    win["MAF"] = ramp
    win["RPM"] = [0.0, *ramp[:-1]]  # RPM(t) = MAF(t-1) exactamente
    win["THROTTLE_POS"] = [1.0] * W  # constante → convención 0.0
    feats = fs2lite_features(win, _ref())
    assert feats["corr_lag1_RPM_MAF"] == pytest.approx(1.0)
    assert feats["corr_lag1_THROTTLE_POS_MAF"] == 0.0


# ---------------------------------------------------------------- GT y SHAP generalizados


def test_gt_fs2_lite_cubre_catalogo_y_traduce_trims() -> None:
    from obd_lab.injection.faults import CATALOG

    for fault in CATALOG:
        gt = gt_features_for(fault, schema=FS2_LITE)
        assert gt and gt <= set(FS2_LITE_NAMES)
    gt_vac = gt_features_for("vacuum_leak", schema=FS2_LITE)
    assert {"LTFT_session_drift", "total_trim_session_drift"} <= gt_vac
    assert not set(REPLACED) & gt_vac  # los absolutos ya no existen en el esquema


def test_gt_fs2_lite_incluye_lag1_en_relacionales() -> None:
    gt = gt_features_for("corr_break_rpm_maf", schema=FS2_LITE)
    assert "corr_lag1_RPM_MAF" in gt


def test_gt_por_defecto_sigue_siendo_fs1() -> None:
    assert gt_features_for("vacuum_leak") == gt_features_for("vacuum_leak", schema=FS1)
    assert "total_trim_mean" in gt_features_for("vacuum_leak")


def test_attributions_as_dict_parametrizado_por_esquema() -> None:
    vals = np.arange(48, dtype=np.float64)
    d = attributions_as_dict(vals, feature_names=FS2_LITE_NAMES)
    assert list(d) == list(FS2_LITE_NAMES)
    with pytest.raises(ValueError, match="incompatible"):
        attributions_as_dict(vals)  # 48 valores no caben en fs1 (42)
