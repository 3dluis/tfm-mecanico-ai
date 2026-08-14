"""Tests de las métricas de auditoría — umbrales congelados ANTES de medir (F19)."""

import numpy as np
import pytest

from ai_models.audit.detectability import (
    AUC_DETECTABLE,
    AUC_WEAK,
    auc,
    classify_detectability,
    cohens_d,
    correlation_shift,
    coverage_bucket,
    coverage_gap,
    mahalanobis_scores,
    nearest_neighbour_ratio,
    overlap_coefficient,
    quantization_absorption,
    signal_to_normal_ratio,
    standardized_shift,
)

RNG = np.random.default_rng(0)


def test_auc_casos_conocidos() -> None:
    a = np.array([1.0, 2.0, 3.0])
    assert auc(a, np.array([4.0, 5.0])) == 1.0  # separación perfecta
    assert auc(a, np.array([-1.0, 0.0])) == 0.0  # invertida
    assert auc(a, a) == 0.5  # idénticas → azar (con corrección de empates)


def test_auc_coincide_con_sklearn() -> None:
    from sklearn.metrics import roc_auc_score

    a, b = RNG.normal(0, 1, 200), RNG.normal(0.7, 1, 180)
    y = np.r_[np.zeros(a.size), np.ones(b.size)]
    assert auc(a, b) == pytest.approx(roc_auc_score(y, np.r_[a, b]), abs=1e-9)


def test_cohens_d_y_desplazamiento_estandarizado() -> None:
    a = RNG.normal(0.0, 1.0, 5000)
    b = a + 2.0
    assert cohens_d(a, b) == pytest.approx(2.0, abs=0.1)
    assert standardized_shift(a, b) == pytest.approx(2.0, abs=0.1)
    # sin dispersión: efecto infinito si hay desplazamiento, 0 si no lo hay
    c = np.full(10, 5.0)
    assert cohens_d(c, c) == 0.0
    assert cohens_d(c, c + 1) == float("inf")
    with pytest.raises(ValueError, match="≥2 muestras"):
        cohens_d(np.array([1.0]), np.array([2.0]))


def test_overlap_coefficient() -> None:
    a = RNG.normal(0, 1, 4000)
    assert overlap_coefficient(a, a) == pytest.approx(1.0, abs=0.02)
    assert overlap_coefficient(a, a + 12.0) < 0.05


def test_signal_to_normal_ratio_y_absorcion_por_cuantizacion() -> None:
    assert signal_to_normal_ratio(0.5, 1.0) == 0.5  # efecto MENOR que el ruido normal
    assert signal_to_normal_ratio(3.0, 1.0) == 3.0
    assert signal_to_normal_ratio(1.0, 0.0) == float("inf")
    assert quantization_absorption(0.3, 0.7812) < 1.0  # se pierde al codificar
    assert quantization_absorption(4.0, 0.5) == 8.0
    with pytest.raises(ValueError, match="positivo"):
        quantization_absorption(1.0, 0.0)


def test_mahalanobis_y_vecino_mas_cercano() -> None:
    ref = RNG.normal(0, 1, size=(300, 3))
    near = RNG.normal(0, 1, size=(50, 3))
    far = RNG.normal(8, 1, size=(50, 3))
    assert mahalanobis_scores(ref, far).mean() > mahalanobis_scores(ref, near).mean()
    assert nearest_neighbour_ratio(ref, far) > nearest_neighbour_ratio(ref, near)


def test_correlation_shift_detecta_colapso_de_relacion() -> None:
    x = RNG.normal(0, 1, 500)
    y = x + RNG.normal(0, 0.05, 500)  # normal: muy correlacionadas
    y2 = RNG.normal(0, 1, 500)  # anómalo: relación rota
    s = correlation_shift(x, y, x, y2)
    assert s["corr_normal"] > 0.95 and abs(s["corr_anomalous"]) < 0.2
    assert s["corr_shift"] < -0.7


def test_clasificacion_usa_los_umbrales_congelados() -> None:
    assert classify_detectability(auc_best=0.99, d_best=2.0).label == "DETECTABLE"
    assert classify_detectability(auc_best=AUC_DETECTABLE, d_best=1.0).label == "DETECTABLE"
    assert classify_detectability(auc_best=AUC_WEAK, d_best=0.3).label == "WEAKLY_DETECTABLE"
    assert classify_detectability(auc_best=0.52, d_best=0.05).label == "INDISTINGUISHABLE"
    assert classify_detectability(auc_best=0.65, d_best=0.4).label == "NEEDS_MORE_EVIDENCE"
    # separación alta pero efecto pequeño: no se declara DETECTABLE a la ligera
    assert classify_detectability(auc_best=0.95, d_best=0.1).label == "WEAKLY_DETECTABLE"


def test_fallos_de_construccion_dominan_sobre_las_metricas() -> None:
    v = classify_detectability(auc_best=0.99, d_best=3.0, absorbed_by_quantization=True)
    assert v.label == "INVALID_BY_CONSTRUCTION" and "cuantización" in v.rationale
    v2 = classify_detectability(auc_best=0.99, d_best=3.0, ground_truth_broken=True)
    assert v2.label == "INVALID_BY_CONSTRUCTION" and "ground truth" in v2.rationale


def test_clase_desconocida_se_rechaza() -> None:
    from ai_models.audit.detectability import DetectabilityVerdict

    with pytest.raises(ValueError, match="clase desconocida"):
        DetectabilityVerdict("MUY_DETECTABLE", 0.9, 1.0, "x")


def test_buckets_de_cobertura_y_deteccion_de_hueco() -> None:
    assert coverage_bucket(0) == "ABSENT"
    assert coverage_bucket(1) == coverage_bucket(2) == "RARE"
    assert coverage_bucket(3) == coverage_bucket(9) == "FEW"
    assert coverage_bucket(10) == "REPRESENTED"
    with pytest.raises(ValueError, match="negativo"):
        coverage_bucket(-1)
    # el caso que motiva F19: comportamiento normal ausente en train pero presente en test
    assert coverage_gap(train_count=0, test_count=5)["coverage_gap"] is True
    assert coverage_gap(train_count=2, test_count=5)["coverage_gap"] is True
    assert coverage_gap(train_count=20, test_count=5)["coverage_gap"] is False
    assert coverage_gap(train_count=0, test_count=0)["coverage_gap"] is False
