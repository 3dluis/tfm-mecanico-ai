"""Invariantes de los bancos confirmatorios materializados en F25 (prereg-v1.0).

La suite-v2 y cases_v2 son la base de TODOS los experimentos confirmatorios: estos tests
fijan su composición contra el pre-registro congelado, de modo que cualquier edición
posterior (que estaría prohibida sin enmienda) rompa la batería.
"""

import json
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v2"
FREEZE = REPO_ROOT / "ai-models" / "configs" / "suite-v2-freeze.json"
CASES = REPO_ROOT / "benchmarks" / "agent-diagnostics" / "cases_v2.yaml"

HELDOUT = {"corr_break_rpm_maf", "load_coolant_decouple", "joint_slow_drift"}
KNOWN = {"vacuum_leak", "maf_drift", "thermostat_stuck", "o2_lag", "misfire"}


def _replicas() -> list[dict]:
    return [
        yaml.safe_load(p.read_text(encoding="utf-8"))
        for p in sorted(SUITE_DIR.glob("replica-*.yaml"))
    ]


def test_diez_replicas_con_estructura_del_prereg() -> None:
    docs = _replicas()
    assert len(docs) == 10
    for doc in docs:
        assert len(doc["train"]) == 22
        assert len(doc["validation"]) == 7
        assert len(doc["test"]) == 8
        profiles = Counter(e["driving_profile"] for e in doc["train"])
        assert profiles == {"urban": 8, "highway": 8, "idle": 3, "cold_start": 3}


def test_bloques_de_semillas_sin_colisiones() -> None:
    seen: set[int] = set()
    for doc in _replicas():
        lo, hi = doc["seed_block"]
        seeds = [e["seed"] for k in ("train", "validation", "test") for e in doc[k]]
        anomaly = [
            e["anomaly_seed"] for k in ("validation", "test") for e in doc[k] if e.get("fault")
        ]
        assert len(seeds) == 37 and len(set(seeds)) == 37
        assert all(lo <= s <= hi for s in seeds + anomaly)
        assert not set(seeds) & seen and not set(anomaly) & set(seeds)
        seen |= set(seeds)
    assert min(seen) == 11000 and max(seen) == 20036 - 0  # réplica 10 → 20000-20036


def test_anticircularidad_y_heldout_solo_en_test() -> None:
    for doc in _replicas():
        assert all(e.get("fault") is None for e in doc["train"])  # train solo normal
        val_faults = {e.get("fault") for e in doc["validation"] if e.get("fault")}
        assert val_faults == KNOWN  # validation: los 5 conocidos, nunca held-out
        test_ho = [e for e in doc["test"] if e.get("category") == "held_out"]
        assert len(test_ho) == 4
        assert {e["fault"] for e in test_ho} == HELDOUT
        # ADR-0034: todo escenario con fallo declara su RNG de inyección separado
        for k in ("validation", "test"):
            assert all("anomaly_seed" in e for e in doc[k] if e.get("fault"))


def test_freeze_congelado_con_cobertura_por_replica() -> None:
    m = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert m["frozen"] is True and m["invalid_replicas"] == []
    assert len(m["partitions"]) == 30  # 10 réplicas × 3 splits
    for name, rep in m["replicas"].items():
        cov = rep["coverage"]
        assert cov["positive_level_share"] >= 0.03, name
        assert cov["negative_level_share"] >= 0.03, name
        assert rep["coverage_ok"] is True
    assert "ltft_level_coverage" in m["coverage_criterion"]["instrument"]


def test_escalada_declarada_coincide_con_los_yaml() -> None:
    """La escalada que decidió el freeze es exactamente la que declaran los YAML."""
    m = json.loads(FREEZE.read_text(encoding="utf-8"))
    for doc in _replicas():
        r = doc["replica"]
        esc = m["replicas"][f"replica-{r:02d}"]["escalation"]
        assert doc["escalation"] == esc
        long_s = {0: 5400.0, 1: 7200.0, 2: 9000.0}[esc]
        for e in doc["train"]:
            if e["driving_profile"] in {"urban", "highway"}:
                assert e["duration_s"] == long_s


def test_cases_v2_composicion_del_prereg() -> None:
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cases = doc["cases"]
    assert len(cases) == 40
    assert [c["scenario"]["seed"] for c in cases] == list(range(30000, 30040))
    assert Counter(c["complexity"] for c in cases) == {"simple": 20, "complex": 20}
    assert sum(1 for c in cases if c["ground_truth"]["failure_mode"] is None) == 8
    assert sum(1 for c in cases if c["expected_outcome"] == "insufficient_data") == 6
    faults = Counter(c["scenario"].get("fault") for c in cases if c["scenario"].get("fault"))
    assert set(faults) == KNOWN and all(v >= 3 for v in faults.values())
    assert not any(c["scenario"].get("fault") in HELDOUT for c in cases)  # sin held-out


def test_cases_v2_controles_negativos_presentes() -> None:
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    cn = Counter(c.get("negative_control") for c in doc["cases"] if c.get("negative_control"))
    # CN5 vive en EXP-MEM-001 y CN6 en el verificador; el resto se instancia aquí
    assert {"CN1", "CN2", "CN3", "CN4", "CN7", "CN8", "CN9"} <= set(cn)
    assert cn["CN8"] >= 6  # los 6 insuficientes + variantes


def test_cases_v2_outcomes_honestos_puntuables() -> None:
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    for c in doc["cases"]:
        assert c["expected_outcome"] in {
            "probable",
            "inconclusive",
            "insufficient_data",
            "no_fault",
        }
        if c["expected_outcome"] == "insufficient_data":
            assert c["complexity"] == "complex"  # definición §6.2 (iii)
