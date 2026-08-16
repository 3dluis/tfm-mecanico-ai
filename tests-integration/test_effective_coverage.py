"""El criterio de cobertura EFECTIVA mide lo que el modelo consume (F22).

Estos tests fijan la lección de EXP-ANOM-010: un banco puede declarar cerrado un hueco de
cobertura y no aportar **ni una sola ventana** útil, porque el contador de cobertura era de
SESIÓN y binario mientras que el modelo consume VENTANAS de features. El instrumento de
`ai_models.audit.coverage` existe para que esa discrepancia no pueda repetirse en silencio.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "ai-models" / "experiments"))

from ai_models.audit.coverage import (  # noqa: E402
    LTFT_HALF_QUANTUM,
    LTFT_QUANTUM,
    check_coverage_criterion,
    ltft_level_coverage,
)

SUITE_V3 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v3_coverage.yaml"
RESULTS_V3 = REPO_ROOT / "ai-models" / "experiments" / "e12_results.json"
MANIFEST_V3 = REPO_ROOT / "ai-models" / "experiments" / "e12_benchmark_v3.json"


def _windows(levels: list[float]) -> np.ndarray:
    """Matriz ventanas × features con el nivel de LTFT en la columna 0."""
    x = np.zeros((len(levels), 3), dtype=float)
    x[:, 0] = levels
    return x


def test_medio_cuanto_es_el_corte_y_deriva_del_cuanto_real() -> None:
    """El corte no es un número mágico: es medio cuanto J1979 del LTFT."""
    # ambos son exactos en binario (25/32 y 25/64): la comparación estricta es legítima
    assert LTFT_QUANTUM == 0.78125
    assert LTFT_HALF_QUANTUM == 0.390625


def test_separa_signo_positivo_y_negativo() -> None:
    """La asimetría importa: los falsos positivos de F21 eran TODOS de signo positivo.

    Un banco que solo cubra el lado negativo no aporta nada al problema medido, y un
    contador que no distinga signo lo declararía cubierto igualmente.
    """
    cov = ltft_level_coverage(_windows([-LTFT_QUANTUM] * 8 + [0.0] * 2), ltft_index=0)
    assert cov["negative_level_share"] == pytest.approx(0.8)
    assert cov["positive_level_share"] == 0.0


def test_un_nivel_por_debajo_de_medio_cuanto_no_cuenta() -> None:
    """El caso exacto que engañó a F20: el paseo cruza medio cuanto pero no emite nivel."""
    casi = LTFT_HALF_QUANTUM - 1e-9
    cov = ltft_level_coverage(_windows([casi] * 10), ltft_index=0)
    assert cov["positive_level_share"] == 0.0


def test_conjunto_vacio_no_revienta_ni_finge_cobertura() -> None:
    cov = ltft_level_coverage(np.zeros((0, 3)), ltft_index=0)
    assert cov["n_windows"] == 0.0
    assert cov["positive_level_share"] == 0.0


def test_el_criterio_falla_si_falta_cualquiera_de_los_dos_lados() -> None:
    """Se exigen AMBOS lados: cumplir uno solo no cierra el hueco."""
    solo_negativo = ltft_level_coverage(_windows([-LTFT_QUANTUM] * 5 + [0.0] * 95), 0)
    verdict = check_coverage_criterion(solo_negativo, 0.03, 0.03)
    assert verdict["negative_ok"] is True
    assert verdict["positive_ok"] is False
    assert verdict["passes"] is False


def test_el_criterio_registra_lo_exigido_aunque_se_cumpla() -> None:
    """Un criterio que solo se guarda cuando falla no es auditable."""
    ambos = ltft_level_coverage(_windows([LTFT_QUANTUM] * 5 + [-LTFT_QUANTUM] * 5 + [0.0] * 90), 0)
    verdict = check_coverage_criterion(ambos, 0.03, 0.03)
    assert verdict["passes"] is True
    assert verdict["criterion"]["positive_level_share>="] == 0.03
    assert verdict["measured"]["positive_level_share"] == pytest.approx(0.05)


def test_la_suite_v3_declara_el_criterio_antes_de_generar_nada() -> None:
    """El criterio vive en el YAML del banco, no en el informe escrito después."""
    criterion = yaml.safe_load(SUITE_V3.read_text(encoding="utf-8"))["benchmark"][
        "coverage_criterion"
    ]
    assert criterion["positive_level_share_min"] == 0.03
    assert criterion["negative_level_share_min"] == 0.03
    assert criterion["feature"] == "LONG_FUEL_TRIM_1_mean"


@pytest.mark.skipif(not MANIFEST_V3.exists(), reason="requiere haber construido el banco v3")
def test_el_banco_v3_cumple_su_propio_criterio() -> None:
    manifest = json.loads(MANIFEST_V3.read_text(encoding="utf-8"))
    assert manifest["coverage_criterion"]["passes"] is True
    # y la comparación que justifica la fase: v2 no aportaba nada por el lado positivo
    assert manifest["effective_coverage"]["expansion_v2_para_comparar"]["positive_level_share"] == 0


@pytest.mark.skipif(not RESULTS_V3.exists(), reason="requiere haber ejecutado la réplica v3")
def test_resultados_f22_son_coherentes_con_el_informe() -> None:
    """Las cifras del informe F22 salen del artefacto, no de la memoria de nadie."""
    res = json.loads(RESULTS_V3.read_text(encoding="utf-8"))
    assert res["experiment"] == "EXP-ANOM-010-R2"
    assert res["hypothesis_test"]["D1_ae_v3"]["decision"] == "PROMOTE_CANDIDATE"
    assert res["h1_exploratory_status"]["status"] == "SUPPORTED"
    assert res["coverage_criterion"]["passes"] is True
    assert res["arms"]["lof_frozen"]["threshold_matches_freeze"] is True
    # P3 sigue siendo la predicción negativa que se cumple: la cobertura no arregla lo lento
    slow = res["arms"]["ae_v3"]["per_fault_recall_median"]
    assert slow["joint_slow_drift"] == 0.0
    assert slow["load_coolant_decouple"] == 0.0
