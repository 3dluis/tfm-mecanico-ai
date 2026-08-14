"""Tests del módulo XAI (métricas, GT, background, artefactos) — F16, Adenda XAI v1."""

import numpy as np
import pytest

from ai_models.xai.ground_truth import FAULT_AFFECTED_PIDS, gt_features_for
from ai_models.xai.metrics import (
    agreement_class,
    attribution_precision_at_k,
    attribution_recall_at_k,
    jaccard_at_k,
    random_recall_baseline,
    random_recall_pvalue,
    rank_correlation,
    stability_jaccard,
    top_k,
)
from mecanico_contracts.features import FEATURE_NAMES


def _attr(**vals: float) -> dict[str, float]:
    base = {f: 0.0 for f in FEATURE_NAMES}
    base.update(vals)
    return base


def test_gt_cubre_todo_el_catalogo_y_es_subconjunto_fs1() -> None:
    from obd_lab.injection.faults import CATALOG

    assert set(FAULT_AFFECTED_PIDS) == set(CATALOG), "el GT debe cubrir el catálogo completo"
    for fault in CATALOG:
        gt = gt_features_for(fault)
        assert gt and gt <= set(FEATURE_NAMES)


def test_gt_relacional_es_conjunto_no_una_feature() -> None:
    """Anomalías relacionales: GT distribuido (adenda §7), nunca una sola feature."""
    gt = gt_features_for("corr_break_rpm_maf")
    assert "corr_RPM_MAF" in gt and len(gt) > 3


def test_attribution_recall_ejemplo_de_la_adenda() -> None:
    """GT={MAF_mean, STFT_mean}, Top-3 contiene ambas → AR@3 = 1.0 (adenda §8)."""
    gt = frozenset({"MAF_mean", "SHORT_FUEL_TRIM_1_mean"})
    attr = _attr(SHORT_FUEL_TRIM_1_mean=0.9, MAF_mean=0.8, INTAKE_PRESSURE_mean=0.5)
    assert attribution_recall_at_k(attr, gt, 3) == 1.0
    assert attribution_recall_at_k(attr, gt, 1) == 1.0  # min(|GT|,1)=1 y top-1 ∈ GT


def test_precision_at_k_solo_si_gt_suficiente() -> None:
    gt3 = frozenset({"RPM_mean", "RPM_std", "RPM_slope"})
    attr = _attr(RPM_mean=1.0, RPM_std=0.9, MAF_mean=0.8)
    assert attribution_precision_at_k(attr, gt3, 3) == pytest.approx(2 / 3)
    with pytest.raises(ValueError, match="no aplica"):
        attribution_precision_at_k(attr, gt3, 5)


def test_baseline_aleatorio_hipergeometrico() -> None:
    """E[AR@K] con selección aleatoria = K·|GT|/n / min(|GT|,K); verificado por simulación."""
    n, g, k = 42, 12, 3
    esperado = random_recall_baseline(n, g, k)
    rng = np.random.default_rng(0)
    sims = [
        len(set(rng.choice(n, k, replace=False)) & set(range(g))) / min(g, k) for _ in range(20000)
    ]
    assert esperado == pytest.approx(float(np.mean(sims)), abs=0.01)
    # p-valor: obtener todos los aciertos posibles es menos probable que el azar medio
    assert random_recall_pvalue(n, g, k, hits=3) < random_recall_pvalue(n, g, k, hits=1)


def test_jaccard_spearman_y_clases() -> None:
    a = _attr(RPM_mean=1.0, MAF_mean=0.9, RPM_std=0.8, MAF_std=0.7, RPM_slope=0.6)
    assert jaccard_at_k(a, a, 5) == 1.0
    assert agreement_class(1.0) == "AGREE"
    assert agreement_class(0.4) == "PARTIAL_AGREEMENT"
    assert agreement_class(0.1) == "DISAGREE"
    assert rank_correlation(a, a) == pytest.approx(1.0)


def test_estabilidad_media_por_pares() -> None:
    a = _attr(RPM_mean=1.0, MAF_mean=0.9, RPM_std=0.8, MAF_std=0.7, RPM_slope=0.6)
    b = _attr(SPEED_mean=1.0, MAF_mean=0.9, RPM_std=0.8, MAF_std=0.7, RPM_slope=0.6)
    val = stability_jaccard([a, b], 5)
    assert 0.0 < val < 1.0
    with pytest.raises(ValueError, match="≥2"):
        stability_jaccard([a], 5)


def test_top_k_determinista_con_empates() -> None:
    attr = _attr(RPM_mean=0.5, MAF_mean=0.5, SPEED_mean=0.5)
    assert top_k(attr, 2) == ["MAF_mean", "RPM_mean"]  # desempate alfabético estable
