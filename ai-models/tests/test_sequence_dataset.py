"""Tests del dataset secuencial crudo [T × PID] — F18, EXP-ANOM-009."""

import numpy as np
import pytest

from ai_models.data.sequence_dataset import (
    OVERLAP_LABEL,
    audit_overlap,
    iter_sequences,
    label_for,
    sequence_manifest,
    sequences_from_matrices,
)
from ai_models.data.snapshot_matrix import MATRIX_PIDS, WideMatrix

N_PIDS = len(MATRIX_PIDS)


def _matrix(session_id: str, n_steps: int = 300, missing: list[tuple[int, int]] | None = None):
    rng = np.random.default_rng(abs(hash(session_id)) % 2**32)
    values = rng.normal(50.0, 5.0, size=(n_steps, N_PIDS))
    for t, f in missing or []:
        values[t, f] = np.nan
    return WideMatrix(
        session_id=session_id,
        values=values,
        valid=~np.isnan(values),
        seq=np.arange(n_steps, dtype=np.int64),
        interval_ms=1000,
        synchronization_version="sync:v1",
    )


_NORMAL_META = {"category": "normal", "fault": None, "duration_s": 300.0}
_FAULT_META = {
    "category": "known_fault",
    "fault": "vacuum_leak",
    "fault_start_s": 120.0,
    "fault_end_s": 300.0,
    "duration_s": 300.0,
}


def test_iter_sequences_formas_y_paso() -> None:
    m = _matrix("s1", n_steps=100)
    seqs = list(iter_sequences(m, steps=60, stride=30))
    assert [s for s, _v, _k in seqs] == [0, 30]
    for _s, vals, mask in seqs:
        assert vals.shape == (60, N_PIDS) and mask.shape == (60, N_PIDS)
    with pytest.raises(ValueError, match="positivos"):
        list(iter_sequences(m, steps=0, stride=1))


def test_secuencias_no_se_descartan_por_ausencias_y_la_mascara_viaja() -> None:
    """NULL ≠ 0: la ausencia se conserva como máscara, no descarta ni se imputa aquí."""
    m = _matrix("s1", n_steps=60, missing=[(5, 2)])
    seqs = list(iter_sequences(m, steps=60, stride=60))
    assert len(seqs) == 1
    _s, vals, mask = seqs[0]
    assert np.isnan(vals[5, 2]) and not mask[5, 2]
    assert mask.sum() == 60 * N_PIDS - 1


def test_etiquetado_identico_al_de_ventanas_estaticas() -> None:
    """Solape ≥ 0.5 con el intervalo inyectado (misma regla que fs1: comparabilidad)."""
    assert label_for(0.0, 60.0, 120.0, 300.0, 300.0) == 0
    assert label_for(80.0, 60.0, 120.0, 300.0, 300.0) == 0  # solape 20/60 < 0.5
    assert label_for(90.0, 60.0, 120.0, 300.0, 300.0) == 1  # solape 30/60 = 0.5 (límite)
    assert label_for(100.0, 60.0, 120.0, 300.0, 300.0) == 1  # solape 40/60 > 0.5
    assert label_for(200.0, 60.0, 120.0, 300.0, 300.0) == 1
    assert label_for(0.0, 60.0, None, None, 300.0) == 0
    assert OVERLAP_LABEL == 0.5


def test_dataset_desde_matrices_con_metadatos() -> None:
    ds = sequences_from_matrices(
        [(_matrix("norm"), _NORMAL_META), (_matrix("fault"), _FAULT_META)], steps=60, stride=30
    )
    assert ds.x.shape[1:] == (60, N_PIDS)
    assert ds.x.shape[0] == ds.mask.shape[0] == len(ds.session_ids) == len(ds.y)
    assert ds.steps == 60 and ds.sample_rate_hz == 1.0
    assert ds.duration_s == 60.0  # duración REAL, no solo pasos
    assert ds.missing_fraction == 0.0
    assert set(ds.session_ids) == {"norm", "fault"}
    assert ds.y.sum() > 0 and (ds.y == 0).sum() > 0
    # las secuencias normales nunca llevan intervalo de fallo
    for sid, fault, iv in zip(ds.session_ids, ds.faults, ds.fault_intervals, strict=True):
        if sid == "norm":
            assert fault is None and iv is None
        else:
            assert fault == "vacuum_leak" and iv == (120.0, 300.0)


def test_dataset_es_determinista() -> None:
    items = [(_matrix("a"), _NORMAL_META)]
    a = sequences_from_matrices(items, 60, 30)
    b = sequences_from_matrices(items, 60, 30)
    assert np.array_equal(a.x, b.x) and np.array_equal(a.y, b.y)


def test_sample_rate_mixto_se_rechaza() -> None:
    m2 = _matrix("b")
    m2.interval_ms = 500
    with pytest.raises(ValueError, match="sample_rate mixto"):
        sequences_from_matrices([(_matrix("a"), _NORMAL_META), (m2, _NORMAL_META)], 60, 30)


def test_filled_conserva_la_mascara() -> None:
    ds = sequences_from_matrices(
        [(_matrix("a", n_steps=60, missing=[(1, 0)]), _NORMAL_META)], 60, 60
    )
    filled = ds.filled(0.0)
    assert filled[0, 1, 0] == 0.0
    assert not ds.mask[0, 1, 0]  # la máscara sigue marcando la ausencia
    assert np.isnan(ds.x[0, 1, 0])  # el dataset original no se modifica
    assert ds.missing_fraction > 0


def test_manifiesto_registra_duracion_real_y_hash_estable() -> None:
    items = [(_matrix("a"), _NORMAL_META), (_matrix("b"), _FAULT_META)]
    ds = sequences_from_matrices(items, 60, 30)
    man = sequence_manifest(
        ds,
        dataset_id="sequence-dataset-v1",
        source="obd-lab-suite-v1",
        provenance="SIMULATED",
        seeds=[101, 102],
    )
    assert man["sequence_steps"] == 60
    assert man["sequence_duration_seconds"] == 60.0
    assert man["sampling_rate_hz"] == 1.0
    assert man["n_sessions"] == 2 and man["seeds"] == [101, 102]
    assert man["provenance"] == "SIMULATED"
    assert man["faults"] == ["vacuum_leak"]
    assert len(man["dataset_hash"]) == 64
    assert (
        sequence_manifest(
            sequences_from_matrices(items, 60, 30),
            dataset_id="x",
            source="y",
            provenance="z",
            seeds=[],
        )["dataset_hash"]
        == man["dataset_hash"]
    )


def test_auditoria_anti_leakage_detecta_sesion_compartida() -> None:
    train = sequences_from_matrices([(_matrix("a"), _NORMAL_META)], 60, 30)
    test_ok = sequences_from_matrices([(_matrix("b"), _NORMAL_META)], 60, 30)
    assert audit_overlap(train, test_ok).clean
    test_bad = sequences_from_matrices([(_matrix("a"), _NORMAL_META)], 60, 30)
    rep = audit_overlap(train, test_bad)
    assert not rep.clean and rep.shared_sessions == ["a"] and rep.shared_step_ranges > 0
