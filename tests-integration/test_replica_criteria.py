"""Los criterios de decisión de EXP-ANOM-010 se aplican tal como se pre-especificaron (F21).

El riesgo metodológico de este experimento no es de cálculo: es que los umbrales se
«ajusten» al ver los resultados. Estos tests fijan el contrato: los criterios del YAML
congelado son los que evalúa el runner, y la clasificación de un brazo depende solo de sus
métricas — no del brazo que sea ni del orden en que se evalúe.
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ai-models" / "experiments"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

pytest.importorskip("torch", reason="e11 importa el AE (grupo train, ADR-0032)")

from e11_replica import check_predictions, quantization_probe  # noqa: E402

CONFIG = REPO_ROOT / "ai-models" / "configs" / "exp-anom-010.yaml"
RESULTS = REPO_ROOT / "ai-models" / "experiments" / "e11_results.json"


def _results(fpr_median: float, fpr_max: float, f1_median: float) -> dict[str, Any]:
    """Estructura mínima de resultados con las métricas que deciden D1."""
    return {
        "arms": {
            "ae_v2": {
                "aggregate": {
                    "f1_median": f1_median,
                    "fp_rate_normal_median": fpr_median,
                    "fp_rate_normal_max": fpr_max,
                    "highway_fpr_median": 0.05,
                },
                # la mediana y el máximo bastan para D1; las semillas individuales solo
                # deciden si la categoría es ESTABLE (regla del estado de H1, F22)
                "seeds": {
                    "42": {"point": {"f1": f1_median, "fp_rate_normal": fpr_median}},
                    "43": {"point": {"f1": f1_median, "fp_rate_normal": fpr_median}},
                    "44": {"point": {"f1": f1_median, "fp_rate_normal": fpr_max}},
                },
                "per_fault_recall_median": {"joint_slow_drift": 0.0, "load_coolant_decouple": 0.0},
            },
            "ae_v11": {"aggregate": {"fp_rate_normal_median": 0.1379}},
            "lof_frozen": {"test": {"point": {"f1": 0.6448, "fp_rate_normal": 0.0345}}},
        }
    }


@pytest.mark.parametrize(
    ("fpr_median", "fpr_max", "f1_median", "expected"),
    [
        (0.02, 0.03, 0.73, "PROMOTE_CANDIDATE"),  # el escenario que buscaba la réplica
        (0.02, 0.06, 0.73, "PARTIAL"),  # una semilla se sale del límite
        (0.04, 0.05, 0.68, "PARTIAL"),
        (0.1336, 0.1422, 0.7095, "REJECT"),  # el resultado real de F21
        (0.01, 0.01, 0.60, "REJECT"),  # FPR perfecto pero peor que el LOF congelado
    ],
)
def test_d1_sigue_los_umbrales_preespecificados(
    fpr_median: float, fpr_max: float, f1_median: float, expected: str
) -> None:
    out = check_predictions(_results(fpr_median, fpr_max, f1_median), "ae_v2")
    assert out["D1_ae_v2"]["decision"] == expected


def test_p4_detecta_deriva_del_pipeline() -> None:
    """Si el LOF congelado no reproduce F18, P4 debe fallar (activa la regla de parada)."""
    res = _results(0.02, 0.03, 0.73)
    res["arms"]["lof_frozen"]["test"]["point"]["f1"] = 0.6500
    out = check_predictions(res, "ae_v2")
    assert out["predictions"]["P4_lof_congelado_reproduce_F18"]["holds"] is False


def test_p3_es_una_prediccion_negativa_falsable() -> None:
    """P3 se cumple con recalls bajos y FALLA si la cobertura sí arregla lo lento."""
    res = _results(0.02, 0.03, 0.73)
    assert (
        check_predictions(res, "ae_v2")["predictions"]["P3_lentas_siguen_bajo_0.10"]["holds"]
        is True
    )
    res["arms"]["ae_v2"]["per_fault_recall_median"]["joint_slow_drift"] = 0.42
    assert (
        check_predictions(res, "ae_v2")["predictions"]["P3_lentas_siguen_bajo_0.10"]["holds"]
        is False
    )


def test_sonda_del_mecanismo_usa_el_cuantizador_real() -> None:
    """Con truncamiento hacia cero hace falta un cuanto COMPLETO: P es mucho menor que con round.

    Si alguien sustituye el cuantizador por `round`, estas probabilidades se disparan
    (0.30 a 1800 s en lugar de ~0.05) y el dimensionado del banco vuelve a ser erróneo.
    """
    probe = quantization_probe(n_walks=600)
    assert probe["1800"]["p_any_positive_level_window"] < 0.15
    # el paseo es simétrico: niveles positivo y negativo deben ser comparables
    assert (
        abs(
            probe["5400"]["p_any_positive_level_window"]
            - probe["5400"]["p_any_negative_level_window"]
        )
        < 0.10
    )
    # duraciones más largas ⇒ más probabilidad (dependencia con √n del paseo)
    assert (
        probe["1800"]["p_any_positive_level_window"] < probe["5400"]["p_any_positive_level_window"]
    )


def test_config_congelada_declara_los_mismos_umbrales() -> None:
    """El YAML pre-especificado y el código no pueden divergir sin que salte un test."""
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    promote = config["decision_criteria"]["D1_ae_v2"]["PROMOTE_CANDIDATE"]
    assert "mediana(fp_rate_normal) <= 0.03" in promote
    assert "todas las semillas con fp_rate_normal <= 0.05" in promote
    assert "mediana(f1) >= 0.70" in promote
    assert config["experiment"]["study_type"] == "exploratory"


@pytest.mark.skipif(not RESULTS.exists(), reason="requiere haber ejecutado e11_replica.py")
def test_resultados_publicados_son_coherentes_con_el_informe() -> None:
    """Las cifras del informe F21 salen del artefacto, no de la memoria de nadie."""
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert res["hypothesis_test"]["D1_ae_v2"]["decision"] == "REJECT"
    assert res["arms"]["lof_frozen"]["threshold_matches_freeze"] is True
    cov = res["cause_report"]["ltft_mean_coverage"]
    assert cov["expansion_v2"]["positive_level_share"] == 0.0
    assert cov["false_positives"]["positive_level_share"] > 0.8
    assert res["benchmark"]["verified"] is True
