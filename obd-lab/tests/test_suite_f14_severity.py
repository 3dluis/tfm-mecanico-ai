"""Validación de la suite exploratoria de severidad (F14) — reglas del Protocolo ML v1."""

from pathlib import Path

from obd_lab.injection.faults import CATALOG
from obd_lab.scenarios.loader import load_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
SEV = REPO_ROOT / "obd-lab" / "scenarios" / "suite_f14_severity.yaml"
V1 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1.yaml"


def test_semillas_en_rango_exploratorio_y_sin_colision() -> None:
    """Semillas dentro de 401-599 (rango F13+) y disjuntas de la suite v1 congelada."""
    sev = load_suite(SEV)["test"]
    seeds = {s.seed for s in sev}
    assert all(401 <= s <= 599 for s in seeds)
    v1 = load_suite(V1)
    v1_seeds = {s.seed for split in v1.values() for s in split}
    assert not seeds & v1_seeds
    assert len(seeds) == len(sev)  # sin semillas repetidas


def test_solo_split_de_evaluacion() -> None:
    """La suite es íntegramente conjunto de evaluación: un único split test (RI1)."""
    suite = load_suite(SEV)
    assert set(suite) == {"test"}


def test_severidades_validas_y_faults_del_catalogo() -> None:
    """Cada escenario con fallo usa un fault del catálogo y parámetros ≤ a los de referencia."""
    ref = {name: dict(f.default_params) for name, f in CATALOG.items()}
    for spec in load_suite(SEV)["test"]:
        if spec.fault is None:
            continue
        assert spec.fault in CATALOG
        for param, value in spec.fault_params.items():
            assert param in ref[spec.fault]
            assert value <= ref[spec.fault][param], "el sweep explora severidades ≤ referencia"


def test_controles_normales_presentes() -> None:
    """El sweep incluye controles normales para medir FPR (sin ellos el recall no se interpreta)."""
    specs = load_suite(SEV)["test"]
    assert sum(1 for s in specs if s.category == "normal") >= 2
