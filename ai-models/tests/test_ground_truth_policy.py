"""El ground truth de atribución debe coincidir con lo que la inyección modifica (F20).

Cierra el hallazgo 3 de AUDIT-DATA-001: el GT declaraba señales que el fallo no toca
(corr_break, load_coolant) y omitía una que sí (misfire → STFT). La política v2 es
**verificable**: `FAULT_AFFECTED_PIDS` contiene exactamente los PIDs realmente alterados,
y la firma relacional vive en las features de correlación.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai-models" / "experiments"))

from e9_anomaly_audit import _series, _sham_def, _spec  # noqa: E402

from ai_models.xai.ground_truth import FAULT_AFFECTED_PIDS  # noqa: E402
from mecanico_contracts.features import CANONICAL_PIDS  # noqa: E402
from obd_lab.generate import generate_ticks  # noqa: E402
from obd_lab.injection.faults import CATALOG  # noqa: E402

SEED = 522  # exploratoria


def _actually_changed(fault: str) -> set[str]:
    """PIDs que la inyección modifica de verdad, aislando el efecto con el brazo SHAM."""
    sham_name = f"sham_{fault}"
    CATALOG[sham_name] = _sham_def(CATALOG[fault])
    try:
        sham = generate_ticks(_spec(sham_name, SEED))
        anom = generate_ticks(_spec(fault, SEED))
    finally:
        CATALOG.pop(sham_name, None)
    return {
        pid
        for pid in CANONICAL_PIDS
        if not np.array_equal(_series(sham)[pid][300:], _series(anom)[pid][300:])
    }


@pytest.mark.parametrize("fault", sorted(CATALOG))
def test_el_gt_declara_exactamente_los_pids_alterados(fault: str) -> None:
    declared, observed = FAULT_AFFECTED_PIDS[fault], _actually_changed(fault)
    assert declared == observed, (
        f"{fault}: GT declara {sorted(declared)} pero la inyección modifica "
        f"{sorted(observed)} — declarar señales inalteradas distorsiona AR@K"
    )


def test_correcciones_concretas_de_f19() -> None:
    """Las tres discrepancias que encontró la auditoría quedan cerradas."""
    assert "SHORT_FUEL_TRIM_1" in FAULT_AFFECTED_PIDS["misfire"]  # omitida antes
    assert "RPM" not in FAULT_AFFECTED_PIDS["corr_break_rpm_maf"]  # declarada de más
    assert "ENGINE_LOAD" not in FAULT_AFFECTED_PIDS["load_coolant_decouple"]


def test_la_firma_relacional_sigue_en_las_features_de_correlacion() -> None:
    """Retirar la señal compañera no pierde la relación: vive en las corr_*."""
    from ai_models.xai.ground_truth import gt_features_for

    gt = gt_features_for("corr_break_rpm_maf")
    assert "corr_RPM_MAF" in gt and "corr_ENGINE_LOAD_MAF" in gt
    assert not any(f.startswith("RPM_") for f in gt)  # RPM crudo ya no está
