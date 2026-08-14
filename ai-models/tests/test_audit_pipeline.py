"""Tests de la auditoría F19: la inyección sobrevive la cadena y el GT es verificable."""

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-models" / "experiments"))

from e9_anomaly_audit import (  # noqa: E402
    _series,
    _sham_def,
    _spec,
    ground_truth_integrity,
    pipeline_trace,
    quantization_steps,
)

from mecanico_contracts.features import CANONICAL_PIDS  # noqa: E402
from obd_lab.generate import generate_ticks  # noqa: E402
from obd_lab.injection.faults import CATALOG  # noqa: E402

SEED = 513  # exploratoria, fuera de todo bloque reservado


def test_pasos_de_cuantizacion_j1979_conocidos() -> None:
    """El paso del LTFT (100/128) es el que explica el hallazgo de F17/F18."""
    steps = quantization_steps()
    assert steps["LONG_FUEL_TRIM_1"]["effective_step"] == pytest.approx(0.78125)
    assert steps["SHORT_FUEL_TRIM_1"]["effective_step"] == pytest.approx(0.78125)
    assert steps["COOLANT_TEMP"]["effective_step"] == pytest.approx(1.0)
    assert steps["TIMING_ADVANCE"]["effective_step"] == pytest.approx(0.5)
    assert steps["RPM"]["effective_step"] == pytest.approx(0.25)


def test_el_gemelo_es_identico_antes_del_fallo() -> None:
    """La inyección no puede afectar a lo anterior a fault_start (validez del pareado)."""
    normal = generate_ticks(_spec(None, SEED))
    anom = generate_ticks(_spec("vacuum_leak", SEED))
    for pid in CANONICAL_PIDS:
        assert np.array_equal(_series(normal)[pid][:300], _series(anom)[pid][:300])


def test_el_brazo_sham_aisla_la_desincronizacion_del_rng() -> None:
    """El SHAM consume el mismo RNG sin alterar valores: idéntico antes, distinto después.

    Comprueba la limitación declarada del diseño pareado (el fallo comparte el generador
    aleatorio del motor), que es lo que justifica el brazo de control.
    """
    CATALOG["sham_maf_drift"] = _sham_def(CATALOG["maf_drift"])
    try:
        normal = generate_ticks(_spec(None, SEED))
        sham = generate_ticks(_spec("sham_maf_drift", SEED))
    finally:
        CATALOG.pop("sham_maf_drift", None)
    for pid in CANONICAL_PIDS:
        assert np.array_equal(_series(normal)[pid][:300], _series(sham)[pid][:300])
    # tras el inicio, el SHAM diverge del normal SIN haber modificado ningún valor:
    # esa diferencia es exclusivamente desincronización del flujo aleatorio
    diverge = any(
        not np.array_equal(_series(normal)[pid][300:], _series(sham)[pid][300:])
        for pid in CANONICAL_PIDS
    )
    assert diverge, "si el SHAM no divergiera, el fallo no compartiría el RNG del motor"


def test_la_inyeccion_sobrevive_generacion_codificacion_y_ventaneo() -> None:
    trace = pipeline_trace("vacuum_leak", SEED)
    assert trace["matrix_preserves_effect"], "la matriz wide debe conservar el efecto"
    changed = [p for p, v in trace["mean_abs_diff_post_quantization"].items() if v > 1e-9]
    assert "LONG_FUEL_TRIM_1" in changed and "SHORT_FUEL_TRIM_1" in changed
    assert trace["n_features_changed"] > 0


def test_integridad_del_ground_truth_detecta_discrepancias_reales() -> None:
    """El GT de misfire omite STFT, que la inyección sí modifica (hallazgo F19)."""
    trace = pipeline_trace("misfire", SEED)
    gt = ground_truth_integrity("misfire", trace)
    assert "SHORT_FUEL_TRIM_1" in gt["observed_not_declared"]
    assert not gt["ground_truth_consistent"]
    # y en un fallo bien declarado no hay discrepancia
    gt_ok = ground_truth_integrity("vacuum_leak", pipeline_trace("vacuum_leak", SEED))
    assert gt_ok["ground_truth_consistent"]


def test_el_catalogo_queda_limpio_tras_la_auditoria() -> None:
    """Ningún fallo SHAM puede quedar registrado en el catálogo del laboratorio."""
    pipeline_trace("o2_lag", SEED)
    assert not [k for k in CATALOG if k.startswith("sham_")]
