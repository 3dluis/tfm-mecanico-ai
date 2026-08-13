"""Tests del camino wide (snapshot → matriz columnar → ventanas) — F13."""

from datetime import UTC, datetime

import numpy as np
import pytest

from ai_models.data.snapshot_matrix import (
    MATRIX_PIDS,
    count_discarded,
    count_windows,
    iter_windows,
    matrix_from_snapshots,
)
from mecanico_contracts import PID_TO_SNAPSHOT_FIELD, VehicleTelemetrySnapshot
from mecanico_contracts.features import CANONICAL_PIDS

_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)


def _snap(seq: int, session: str = "s1", **signals: float | None) -> VehicleTelemetrySnapshot:
    base: dict[str, float | None] = {
        PID_TO_SNAPSHOT_FIELD[pid]: 10.0 * seq + i for i, pid in enumerate(CANONICAL_PIDS)
    }
    base.update(signals)
    return VehicleTelemetrySnapshot(
        snapshot_id=f"snap-{session}-{seq}",
        vehicle_id="veh-1",
        device_id="test",
        session_id=session,
        timestamp_utc=_EPOCH,
        sequence_number=seq,
        snapshot_interval_ms=1000,
        quality_score=1.0,
        created_at=_EPOCH,
        **base,  # type: ignore[arg-type]
    )


def test_orden_de_columnas_es_el_contrato_fs1() -> None:
    assert list(MATRIX_PIDS) == list(CANONICAL_PIDS)


def test_matriz_null_es_nan_nunca_cero() -> None:
    """ADR-0027: una señal ausente debe ser NaN en la matriz, jamás 0."""
    snaps = [_snap(0), _snap(1, maf=None)]
    m = matrix_from_snapshots(snaps)
    j = list(MATRIX_PIDS).index("MAF")
    assert np.isnan(m.values[1, j])
    assert not m.valid[1, j]
    assert m.valid[0, j]
    assert m.values[1, j] != 0.0 or np.isnan(m.values[1, j])


def test_matriz_ordena_por_sequence_number() -> None:
    m = matrix_from_snapshots([_snap(2), _snap(0), _snap(1)])
    assert m.seq.tolist() == [0, 1, 2]


def test_matriz_rechaza_sesiones_o_rejillas_mixtas() -> None:
    with pytest.raises(ValueError, match="sesiones distintas"):
        matrix_from_snapshots([_snap(0, session="a"), _snap(1, session="b")])
    otro = _snap(1).model_copy(update={"snapshot_interval_ms": 200})
    with pytest.raises(ValueError, match="interval_ms"):
        matrix_from_snapshots([_snap(0), otro])
    with pytest.raises(ValueError, match="no hay snapshots"):
        matrix_from_snapshots([])


def test_ventanas_formato_y_conteo() -> None:
    snaps = [_snap(i) for i in range(10)]
    m = matrix_from_snapshots(snaps)
    ventanas = list(iter_windows(m, size=4, stride=2))
    assert len(ventanas) == count_windows(10, 4, 2) == 4
    start, window = ventanas[0]
    assert start == 0
    assert set(window) == set(MATRIX_PIDS)
    assert all(len(v) == 4 for v in window.values())
    # los valores de la ventana reproducen la señal original
    j = list(MATRIX_PIDS).index("RPM")
    assert window["RPM"] == m.values[0:4, j].tolist()


def test_ventana_invalida_se_descarta_no_se_imputa() -> None:
    """Una señal bajo la fracción mínima de validez descarta la ventana (sin imputar)."""
    snaps = [_snap(i, maf=None if i == 1 else 100.0) for i in range(6)]
    m = matrix_from_snapshots(snaps)
    total = count_windows(6, 4, 2)
    kept = list(iter_windows(m, size=4, stride=2, min_valid_fraction=1.0))
    assert total == 2
    assert len(kept) == 1  # la ventana [0..3] contiene el NaN y cae
    assert kept[0][0] == 2
    assert count_discarded(m, 4, 2, min_valid_fraction=1.0) == 1
    # con tolerancia explícita la ventana vuelve, con su NaN visible (nunca 0)
    relaxed = list(iter_windows(m, size=4, stride=2, min_valid_fraction=0.7))
    assert len(relaxed) == 2


def test_determinismo() -> None:
    snaps = [_snap(i) for i in range(8)]
    a = matrix_from_snapshots(snaps)
    b = matrix_from_snapshots(list(reversed(snaps)))
    assert np.array_equal(a.values, b.values)
    assert list(iter_windows(a, 4, 2)) == list(iter_windows(b, 4, 2))
