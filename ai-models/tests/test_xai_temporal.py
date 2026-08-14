"""Tests de las métricas XAI temporales — definiciones congeladas ANTES de EXP-ANOM-009."""

import numpy as np
import pytest

from ai_models.xai.metrics import random_recall_baseline
from ai_models.xai.temporal import (
    TemporalGroundTruth,
    aggregate_by_feature,
    aggregate_by_time,
    cell_stability_jaccard,
    feature_attribution_recall_at_k,
    feature_time_hit_at_k,
    temporal_attribution_recall_at_k,
    temporal_gt_for,
    top_k_cells,
    top_k_steps,
)

PIDS = ["RPM", "MAF", "COOLANT_TEMP", "LONG_FUEL_TRIM_1"]
T, F = 6, 4


def _matrix(hot: list[tuple[int, int]], value: float = 10.0) -> np.ndarray:
    """Matriz de atribución con celdas 'calientes' declaradas y ruido determinista bajo."""
    rng = np.random.default_rng(0)
    a = rng.uniform(0.0, 0.1, size=(T, F))
    for t, f in hot:
        a[t, f] = value
    return a


def test_agregados_se_derivan_de_la_matriz() -> None:
    a = _matrix([(2, 1)])
    by_f = aggregate_by_feature(a, PIDS)
    by_t = aggregate_by_time(a)
    assert set(by_f) == set(PIDS)
    assert len(by_t) == T
    assert by_f["MAF"] == pytest.approx(np.abs(a[:, 1]).sum())
    assert by_t[2] == pytest.approx(np.abs(a[2, :]).sum())
    # la suma total coincide por ambas vías (son vistas de la MISMA matriz)
    assert sum(by_f.values()) == pytest.approx(sum(by_t.values()))


def test_agregados_usan_valor_absoluto() -> None:
    a = np.array([[-5.0, 0.0], [0.0, 1.0]])
    assert aggregate_by_feature(a, ["A", "B"])["A"] == pytest.approx(5.0)


def test_dimensiones_incompatibles_fallan() -> None:
    with pytest.raises(ValueError, match="n_steps, n_features"):
        aggregate_by_time(np.zeros((2, 2, 2)))
    with pytest.raises(ValueError, match="nombres"):
        aggregate_by_feature(np.zeros((3, 5)), PIDS)


def test_top_k_pasos_y_celdas_deterministas() -> None:
    a = _matrix([(4, 0), (1, 2)])
    assert top_k_steps(a, 2) == [4, 1] or top_k_steps(a, 2) == [1, 4]
    assert top_k_cells(a, PIDS, 2) == [(1, "COOLANT_TEMP"), (4, "RPM")] or top_k_cells(
        a, PIDS, 2
    ) == [(4, "RPM"), (1, "COOLANT_TEMP")]
    # empate exacto: desempata por paso ascendente y luego NOMBRE ascendente
    tie = np.zeros((2, 2))
    assert top_k_cells(tie, ["B", "A"], 3) == [(0, "A"), (0, "B"), (1, "A")]


# --------------------------------------------------------------- ground truth temporal


def test_gt_temporal_selecciona_los_pasos_del_intervalo() -> None:
    gt = temporal_gt_for(
        "vacuum_leak",
        sequence_start_s=100.0,
        n_steps=60,
        sample_rate_hz=1.0,
        fault_start_s=120.0,
        fault_end_s=140.0,
    )
    assert gt.time_steps == frozenset(range(20, 40))  # 120s..139s → pasos 20..39
    assert "LONG_FUEL_TRIM_1" in gt.features and "INTAKE_PRESSURE" in gt.features
    assert gt.n_cells == len(gt.features) * 20


def test_gt_temporal_vacio_si_la_secuencia_es_previa_al_fallo() -> None:
    gt = temporal_gt_for(
        "misfire",
        sequence_start_s=0.0,
        n_steps=60,
        sample_rate_hz=1.0,
        fault_start_s=600.0,
        fault_end_s=900.0,
    )
    assert gt.time_steps == frozenset()


def test_gt_temporal_cubre_el_catalogo_y_rechaza_fallo_desconocido() -> None:
    from obd_lab.injection.faults import CATALOG

    for fault in CATALOG:
        gt = temporal_gt_for(
            fault,
            sequence_start_s=0.0,
            n_steps=10,
            sample_rate_hz=1.0,
            fault_start_s=0.0,
            fault_end_s=10.0,
        )
        assert gt.features and gt.time_steps == frozenset(range(10))
    with pytest.raises(KeyError):
        temporal_gt_for(
            "no_existe",
            sequence_start_s=0.0,
            n_steps=1,
            sample_rate_hz=1.0,
            fault_start_s=0.0,
            fault_end_s=1.0,
        )


# ------------------------------------------------------------------------- métricas


def test_far_tar_fth_perfectos_cuando_la_atribucion_cae_en_la_region() -> None:
    gt = TemporalGroundTruth(
        fault="x",
        features=frozenset({"MAF"}),
        time_steps=frozenset({2, 3}),
        anomaly_start_s=0.0,
        anomaly_end_s=1.0,
    )
    a = _matrix([(2, 1), (3, 1)])
    assert feature_attribution_recall_at_k(a, PIDS, gt.features, 1) == 1.0
    assert temporal_attribution_recall_at_k(a, gt.time_steps, 2) == 1.0
    assert feature_time_hit_at_k(a, PIDS, gt.features, gt.time_steps, 2) == 1.0


def test_metricas_caen_cuando_la_atribucion_esta_fuera_de_la_region() -> None:
    gt_f, gt_t = frozenset({"MAF"}), frozenset({2, 3})
    a = _matrix([(0, 0), (5, 3)])  # señal y momento equivocados
    assert feature_attribution_recall_at_k(a, PIDS, gt_f, 1) == 0.0
    assert temporal_attribution_recall_at_k(a, gt_t, 2) == 0.0
    assert feature_time_hit_at_k(a, PIDS, gt_f, gt_t, 2) == 0.0


def test_normalizacion_por_min_gt_k_como_ar_at_k() -> None:
    """Con |GT| < K la métrica sigue pudiendo alcanzar 1.0 (misma convención que AR@K)."""
    a = _matrix([(2, 1)])
    assert feature_attribution_recall_at_k(a, PIDS, frozenset({"MAF"}), 3) == 1.0
    assert temporal_attribution_recall_at_k(a, frozenset({2}), 3) == 1.0


def test_gt_vacio_no_esta_definido() -> None:
    a = _matrix([(0, 0)])
    with pytest.raises(ValueError, match="GT vacío"):
        temporal_attribution_recall_at_k(a, frozenset(), 3)
    with pytest.raises(ValueError, match="GT vacío"):
        feature_attribution_recall_at_k(a, PIDS, frozenset(), 3)


def test_baseline_aleatorio_es_el_hipergeometrico_congelado() -> None:
    """Verificación por simulación: FTH@K aleatorio ≈ K·|GT_cells|/(T·F) / min(|GT|,K)."""
    gt_f, gt_t = frozenset({"MAF", "RPM"}), frozenset({2, 3})
    k, n_cells = 4, T * F
    gt_cells = len(gt_f) * len(gt_t)
    expected = random_recall_baseline(n_cells, gt_cells, k)
    rng = np.random.default_rng(7)
    vals = [
        feature_time_hit_at_k(rng.uniform(0, 1, size=(T, F)), PIDS, gt_f, gt_t, k)
        for _ in range(4000)
    ]
    assert float(np.mean(vals)) == pytest.approx(expected, abs=0.02)


def test_estabilidad_de_celdas() -> None:
    a = _matrix([(2, 1), (3, 1)])
    b = _matrix([(2, 1), (3, 1)], value=9.0)
    c = _matrix([(0, 0), (5, 3)])
    assert cell_stability_jaccard([a, b], PIDS, 2) == 1.0
    assert cell_stability_jaccard([a, c], PIDS, 2) == 0.0
    with pytest.raises(ValueError, match="≥2 matrices"):
        cell_stability_jaccard([a], PIDS, 2)
