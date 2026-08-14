"""Separación de generadores aleatorios: normal vs inyección (ADR-0034, F20).

Propiedad exigida por el autor: con el MISMO ``vehicle_behavior_seed`` y distinto
``anomaly_injection_seed``, la trayectoria normal debe ser idéntica fuera de la región
intervenida. Y los datasets v1 deben seguir reproduciéndose byte a byte.
"""

import numpy as np
import pytest

from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import CANONICAL_PIDS
from obd_lab.generate import generate_ticks

VEHICLE_SEED = 520  # exploratoria (bloque 426-599), fuera de todo bloque reservado
FAULT_START, FAULT_END, DURATION = 200.0, 500.0, 700.0


def _spec(fault: str | None, anomaly_seed: int | None, seed: int = VEHICLE_SEED) -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="t20-rng",
        description="test de separación de RNG",
        category="normal" if fault is None else "known_fault",
        driving_profile="urban",
        duration_s=DURATION,
        seed=seed,
        anomaly_seed=anomaly_seed,
        fault=fault,
        fault_start_s=FAULT_START if fault else None,
        fault_end_s=FAULT_END if fault else None,
    )


def _series(ticks: list[dict[str, float]], pid: str) -> np.ndarray:
    return np.array([t[pid] for t in ticks], dtype=float)


def test_distinta_semilla_de_anomalia_conserva_la_trayectoria_normal_fuera_de_la_region() -> None:
    """El requisito central: cambiar la anomalía no puede mover el comportamiento base."""
    a = generate_ticks(_spec("vacuum_leak", anomaly_seed=1))
    b = generate_ticks(_spec("vacuum_leak", anomaly_seed=999))
    for pid in CANONICAL_PIDS:
        sa, sb = _series(a, pid), _series(b, pid)
        assert np.array_equal(sa[: int(FAULT_START)], sb[: int(FAULT_START)]), (
            f"{pid} difiere ANTES del fallo"
        )
        assert np.array_equal(sa[int(FAULT_END) :], sb[int(FAULT_END) :]), (
            f"{pid} difiere DESPUÉS del fallo"
        )


def test_anomalias_distintas_comparten_la_misma_trayectoria_base() -> None:
    """`vehicle_behavior_seed` fijo + anomalías distintas = misma base, sólo cambia la firma."""
    drift = generate_ticks(_spec("joint_slow_drift", anomaly_seed=7))
    corr = generate_ticks(_spec("corr_break_rpm_maf", anomaly_seed=8))
    normal = generate_ticks(_spec(None, anomaly_seed=None))
    for pid in CANONICAL_PIDS:
        pre = slice(0, int(FAULT_START))
        assert np.array_equal(_series(drift, pid)[pre], _series(normal, pid)[pre])
        assert np.array_equal(_series(corr, pid)[pre], _series(normal, pid)[pre])
    # y una señal que ninguna de las dos toca permanece idéntica en TODA la sesión
    assert np.array_equal(_series(drift, "SPEED"), _series(normal, "SPEED"))
    assert np.array_equal(_series(corr, "SPEED"), _series(normal, "SPEED"))


def test_la_anomalia_no_consume_aleatoriedad_del_motor() -> None:
    """Con RNG separado, el normal y el anómalo comparten la trayectoria base completa
    salvo en las señales que la inyección modifica dentro de su ventana."""
    normal = generate_ticks(_spec(None, anomaly_seed=None))
    anom = generate_ticks(_spec("thermostat_stuck", anomaly_seed=42))
    # thermostat_stuck solo toca COOLANT_TEMP: el resto es idéntico de principio a fin
    for pid in CANONICAL_PIDS:
        if pid == "COOLANT_TEMP":
            continue
        assert np.array_equal(_series(normal, pid), _series(anom, pid)), f"{pid} contaminado"


def test_el_comportamiento_heredado_v1_se_conserva_sin_anomaly_seed() -> None:
    """Sin `anomaly_seed` la anomalía comparte el RNG del motor (v1 byte a byte)."""
    legacy_a = generate_ticks(_spec("vacuum_leak", anomaly_seed=None))
    legacy_b = generate_ticks(_spec("vacuum_leak", anomaly_seed=None))
    assert legacy_a == legacy_b  # determinista
    normal = generate_ticks(_spec(None, anomaly_seed=None))
    # en el modo heredado, una señal NO tocada por el fallo SÍ se desincroniza tras el
    # inicio: es exactamente la contaminación que documentó la auditoría F19
    assert not np.array_equal(_series(legacy_a, "SPEED"), _series(normal, "SPEED"))
    # y el modo separado corrige justamente eso
    separated = generate_ticks(_spec("vacuum_leak", anomaly_seed=5))
    assert np.array_equal(_series(separated, "SPEED"), _series(normal, "SPEED"))


def test_la_semilla_de_anomalia_si_cambia_la_firma_inyectada() -> None:
    """Separar RNG no elimina la aleatoriedad de la anomalía: solo la aísla."""
    a = generate_ticks(_spec("misfire", anomaly_seed=1))
    b = generate_ticks(_spec("misfire", anomaly_seed=2))
    win = slice(int(FAULT_START), int(FAULT_END))
    assert not np.array_equal(_series(a, "RPM")[win], _series(b, "RPM")[win])


def test_reproducibilidad_completa_con_ambas_semillas() -> None:
    assert generate_ticks(_spec("maf_drift", anomaly_seed=3)) == generate_ticks(
        _spec("maf_drift", anomaly_seed=3)
    )
    assert generate_ticks(_spec("maf_drift", anomaly_seed=3, seed=521)) != generate_ticks(
        _spec("maf_drift", anomaly_seed=3)
    )


@pytest.mark.parametrize("fault", ["vacuum_leak", "maf_drift", "o2_lag", "joint_slow_drift"])
def test_propiedad_valida_para_todo_el_catalogo(fault: str) -> None:
    a = generate_ticks(_spec(fault, anomaly_seed=11))
    b = generate_ticks(_spec(fault, anomaly_seed=12))
    for pid in CANONICAL_PIDS:
        assert np.array_equal(
            _series(a, pid)[: int(FAULT_START)], _series(b, pid)[: int(FAULT_START)]
        )
