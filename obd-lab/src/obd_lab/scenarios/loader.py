"""Carga de suites de escenarios declarativas (YAML → ScenarioSpec)."""

from pathlib import Path
from typing import Any

import yaml

from mecanico_contracts import ScenarioSpec
from obd_lab.injection.faults import CATALOG


def load_suite(path: Path) -> dict[str, list[ScenarioSpec]]:
    """Carga una suite YAML: {split: [ScenarioSpec, ...]}.

    Valida la coherencia categoría↔fallo: un escenario con fallo held-out solo puede
    vivir en el split 'test' (protección anti-circularidad, ADR-0011).
    """
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    suite: dict[str, list[ScenarioSpec]] = {}
    for split, items in raw["splits"].items():
        specs: list[ScenarioSpec] = []
        for item in items:
            spec = ScenarioSpec(**item)
            if spec.fault:
                fault = CATALOG[spec.fault]  # KeyError si no existe: fallo temprano
                if fault.category != spec.category:
                    msg = (
                        f"{spec.scenario_id}: categoría {spec.category!r} no coincide "
                        f"con la del fallo {spec.fault!r} ({fault.category!r})"
                    )
                    raise ValueError(msg)
                if fault.category == "held_out" and split != "test":
                    msg = (
                        f"{spec.scenario_id}: los fallos held-out solo pueden usarse en el "
                        f"split 'test' (está en {split!r}); ver ADR-0011 / RI1"
                    )
                    raise ValueError(msg)
            specs.append(spec)
        suite[split] = specs
    return suite
