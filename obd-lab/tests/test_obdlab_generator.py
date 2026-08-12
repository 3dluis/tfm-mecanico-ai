"""Tests del laboratorio: reproducibilidad, categorías, cuantización y protección RI1."""

import hashlib
from pathlib import Path

import pytest

from mecanico_contracts import ScenarioSpec
from obd_lab.emulator.encoding import encode_pid, quantize
from obd_lab.generate import generate_ticks, write_session
from obd_lab.injection.faults import CATALOG, held_out_names, known_fault_names
from obd_lab.scenarios.loader import load_suite

SUITE = Path(__file__).parents[1] / "scenarios" / "suite_v1.yaml"


def _spec(**kw: object) -> ScenarioSpec:
    base: dict[str, object] = {
        "scenario_id": "t",
        "description": "test",
        "driving_profile": "urban",
        "duration_s": 120,
        "seed": 5,
    }
    base.update(kw)
    return ScenarioSpec(**base)  # type: ignore[arg-type]


def test_reproducibilidad_byte_a_byte(tmp_path: Path) -> None:
    p1 = write_session(_spec(), tmp_path / "a")
    p2 = write_session(_spec(), tmp_path / "b")
    assert hashlib.sha256(p1.read_bytes()).digest() == hashlib.sha256(p2.read_bytes()).digest()


def test_semillas_distintas_difieren(tmp_path: Path) -> None:
    p1 = write_session(_spec(seed=1), tmp_path / "a")
    p2 = write_session(_spec(seed=2), tmp_path / "b")
    assert p1.read_bytes() != p2.read_bytes()


def test_catalogo_categorias() -> None:
    assert len(known_fault_names()) >= 5
    assert len(held_out_names()) >= 3
    assert set(known_fault_names()) | set(held_out_names()) == set(CATALOG)


def test_suite_v1_carga_y_protege_held_out() -> None:
    suite = load_suite(SUITE)
    assert set(suite) == {"train", "validation", "test"}
    assert all(s.fault is None for s in suite["train"])
    held_out_en_val = [s for s in suite["validation"] if s.category == "held_out"]
    assert not held_out_en_val


def test_loader_rechaza_held_out_fuera_de_test(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
splits:
  validation:
    - {scenario_id: x, description: d, category: held_out, driving_profile: urban,
       duration_s: 100, seed: 1, fault: corr_break_rpm_maf}
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="held-out"):
        load_suite(bad)


def test_fallo_modifica_senal() -> None:
    normal = generate_ticks(_spec(duration_s=400))
    fault = generate_ticks(
        _spec(duration_s=400, category="known_fault", fault="vacuum_leak", fault_start_s=0)
    )
    trim_n = sum(t["SHORT_FUEL_TRIM_1"] for t in normal[100:]) / 300
    trim_f = sum(t["SHORT_FUEL_TRIM_1"] for t in fault[100:]) / 300
    assert trim_f > trim_n + 3.0  # la fuga de vacío eleva trims claramente


def test_cuantizacion_idempotente_y_encoding() -> None:
    for pid, value in [
        ("RPM", 1234.56),
        ("COOLANT_TEMP", 87.7),
        ("MAF", 22.333),
        ("SHORT_FUEL_TRIM_1", -7.3),
        ("O2_B1S1", 0.437),
    ]:
        q = quantize(pid, value)
        assert quantize(pid, q) == q  # idempotente
        request, response = encode_pid(pid, value)
        assert request.startswith("^01") and "<data>41 " in response
