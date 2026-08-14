"""Integración F13 — paridad wide↔long, anti-leakage y reproducibilidad (EXP-ANOM-005).

Punto de composición multi-proyecto permitido (docs/09 §9.4): combina obd-lab (generación
determinista), diagnostic-agent (snapshot builder sync:v1) y ai-models (matriz + features).
"""

from pathlib import Path

import numpy as np

from ai_models.data.dataset import build_dataset
from ai_models.data.snapshot_matrix import iter_windows, matrix_from_snapshots
from diagnostic_agent.telemetry.snapshots import PID_TO_FIELD, build_from_ticks
from mecanico_contracts import PID_TO_SNAPSHOT_FIELD, ScenarioSpec
from mecanico_contracts.features import feature_vector
from mecanico_contracts.session_io import read_session_series
from obd_lab.generate import generate_ticks, write_session
from obd_lab.scenarios.loader import load_suite

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_V1 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1.yaml"

#: Escenarios cortos SOLO para tests (semillas 401/411: fuera de todo bloque reservado por
#: el pre-registro — 101-322 gastadas, 901-925 y 11000-20036+ RESERVADAS confirmatorias).
_NORMAL = ScenarioSpec(
    scenario_id="t13-normal",
    description="normal corto para tests F13",
    category="normal",
    driving_profile="urban",
    duration_s=180,
    seed=401,
)
_FAULT = ScenarioSpec(
    scenario_id="t13-vacuum",
    description="fallo conocido corto para tests F13",
    category="known_fault",
    driving_profile="urban",
    duration_s=180,
    seed=411,
    fault="vacuum_leak",
    fault_start_s=60.0,
)


def test_mapeo_pid_snapshot_unico() -> None:
    """El mapeo del edge y el del contrato compartido deben ser EL MISMO (F13)."""
    assert PID_TO_FIELD == PID_TO_SNAPSHOT_FIELD


def test_paridad_features_wide_vs_long(tmp_path: Path) -> None:
    """Mismas sesiones → mismas features por el camino long (F3) y el wide (snapshots)."""
    split_dir = tmp_path / "test"
    split_dir.mkdir()
    for spec in (_NORMAL, _FAULT):
        write_session(spec, split_dir)
    long_ds = build_dataset(split_dir, size=60, stride=30)
    assert long_ds.x.shape[1] == 42

    xs = []
    for path in sorted(split_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        n = min(len(v) for v in series.values())
        ticks = [{pid: series[pid][i] for pid in series} for i in range(n)]
        snapshots, _ = build_from_ticks(
            ticks,
            session_id=header.session_id,
            vehicle_id=header.vehicle_id,
            device_id=header.device_id,
        )
        matrix = matrix_from_snapshots(snapshots)
        for _start, window in iter_windows(matrix, size=60, stride=30):
            xs.append(feature_vector(window))
    wide_x = np.asarray(xs, dtype=np.float64)

    assert wide_x.shape == long_ds.x.shape
    assert np.array_equal(wide_x, long_ds.x)  # paridad EXACTA, no aproximada


def test_splits_suite_v1_sin_leakage() -> None:
    """Anti-leakage estructural: sesiones y semillas no se comparten entre splits."""
    suite = load_suite(SUITE_V1)
    ids = {split: {s.scenario_id for s in specs} for split, specs in suite.items()}
    seeds = {split: {s.seed for s in specs} for split, specs in suite.items()}
    for a in suite:
        for b in suite:
            if a < b:
                assert not ids[a] & ids[b], f"scenario_id compartido entre {a} y {b}"
                assert not seeds[a] & seeds[b], f"seed compartida entre {a} y {b}"


def test_held_out_solo_en_test() -> None:
    """RI1: las clases held-out no pueden aparecer fuera del split test."""
    suite = load_suite(SUITE_V1)
    for split, specs in suite.items():
        if split == "test":
            continue
        assert all(s.category != "held_out" for s in specs)
    assert any(s.category == "held_out" for s in suite["test"])


def test_ventanas_no_cruzan_sesiones(tmp_path: Path) -> None:
    """Ninguna ventana mezcla muestras de dos sesiones (unidad = sesión, luego ventana)."""
    split_dir = tmp_path / "x"
    split_dir.mkdir()
    for spec in (_NORMAL, _FAULT):
        write_session(spec, split_dir)
    ds = build_dataset(split_dir, size=60, stride=30)
    per_session = {sid: ds.session_ids.count(sid) for sid in set(ds.session_ids)}
    # 180 s a 1 Hz con 60/30 → 5 ventanas por sesión; el total es la suma exacta
    assert all(n == 5 for n in per_session.values())
    assert len(ds.session_ids) == sum(per_session.values())


def test_reproducibilidad_por_semilla() -> None:
    """La misma semilla produce EXACTAMENTE los mismos ticks (byte a byte)."""
    a = generate_ticks(_NORMAL)
    b = generate_ticks(_NORMAL)
    assert a == b
    c = generate_ticks(_NORMAL.model_copy(update={"seed": 402}))
    assert a != c


def test_dataset_v11_sin_leakage_y_reproducible(tmp_path: Path) -> None:
    """train v1.1 (22 normales): seeds disjuntas de val/test congelados y hash estable."""
    import yaml

    raw = yaml.safe_load((REPO_ROOT / "obd-lab/scenarios/suite_v1_train_ext.yaml").read_text())
    ext_seeds = {e["seed"] for e in raw["train_extension"]}
    suite = load_suite(SUITE_V1)
    train_seeds = {s.seed for s in suite["train"]} | ext_seeds
    eval_seeds = {s.seed for s in suite["validation"]} | {s.seed for s in suite["test"]}
    assert not train_seeds & eval_seeds, "leakage: semilla de train v1.1 en val/test"
    assert all(e["category"] == "normal" for e in raw["train_extension"])
    # bloques confirmatorios RESERVADOS jamás en datasets exploratorios
    reserved = set(range(901, 926)) | set(range(11000, 20037)) | set(range(30000, 30080))
    assert not (train_seeds | eval_seeds) & reserved
    # reproducibilidad de una sesión de la extensión
    spec = ScenarioSpec(**raw["train_extension"][0])
    assert generate_ticks(spec) == generate_ticks(spec)
