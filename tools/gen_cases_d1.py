"""Banco de SELECCIÓN de modelo (D1) — generación determinista.

**Por qué existe.** Fijar D1 evaluando modelos sobre `cases_v2` sería seleccionar sobre el
conjunto de evaluación: `cases_v2` es el banco confirmatorio de `EXP-EVID-001`. Este banco
es **disjunto** de él y su único uso es instrumental —comparar candidatos de modelo de
lenguaje— y nunca confirmatorio.

**Semillas.** Bloque `60000–60019`, con `anomaly_seed = seed + 10000` (bloque 70000–70019).
Ninguno interseca con los bloques reservados: suite v1 (101–322), benchmark v1 (31–9001),
suite-v2 (11000–20036), `cases_v2` y sus variantes (30000–30079, anomalías 40000–40039),
`sequences_v1` (55000) ni suite-v2-multi (111000+, 211000+, 311000+).

**Composición.** 15 casos con fallo (3 por cada uno de los 5 mecanismos conocidos) y 5
normales. Un generador que responda siempre el mismo mecanismo obtiene 3/20 = 0.15: es el
control trivial que un candidato debe superar con claridad para fijar D1.

**El contexto diagnóstico se DERIVA DE LA TELEMETRÍA MEDIDA**, no se redacta a mano: se
extraen las ventanas de features de la sesión emulada y se describe la ventana con mayor
desviación respecto de la referencia normal de la propia sesión. Redactar el contexto a mano
reintroduciría la circularidad que invalidó el corpus v1 —quien escribe el contexto conoce
la respuesta y tiende a insinuarla—.

Uso:
    python tools/gen_cases_d1.py            # escenarios + sesiones + casos
    python tools/gen_cases_d1.py --skip-sessions   # sólo re-derivar casos de sesiones ya generadas
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = REPO_ROOT / "obd-lab" / "scenarios" / "suite_d1.yaml"
SESSION_DIR = REPO_ROOT / "data" / "d1"
CASES_PATH = REPO_ROOT / "benchmarks" / "agent-diagnostics" / "cases_d1.yaml"

SEED_BASE = 60000
ANOMALY_OFFSET = 10000
DURATION_S = 1200.0
FAULT_START_S = 300.0

MECANISMOS = ["vacuum_leak", "maf_drift", "thermostat_stuck", "o2_lag", "misfire"]
PERFILES = ["urban", "highway", "idle", "cold_start"]

#: PID que se describen en el contexto, con su unidad. El contexto NO nombra mecanismos.
_DESCRITOS = [
    ("total_trim_mean", "%", "media de los ajustes de combustible"),
    ("SHORT_FUEL_TRIM_1_std", "%", "dispersión del ajuste a corto plazo"),
    ("LONG_FUEL_TRIM_1_mean", "%", "media del ajuste a largo plazo"),
    ("RPM_mean", "rpm", "régimen medio"),
    ("RPM_std", "rpm", "dispersión del régimen"),
    ("SPEED_mean", "km/h", "velocidad media"),
    ("MAF_mean", "g/s", "flujo de aire medio"),
    ("ENGINE_LOAD_mean", "%", "carga media"),
    ("COOLANT_TEMP_mean", "°C", "temperatura media del refrigerante"),
    ("INTAKE_PRESSURE_mean", "kPa", "presión media del colector"),
    ("O2_B1S1_mean", "V", "tensión media de la sonda de oxígeno"),
    ("O2_B1S1_std", "V", "dispersión de la sonda de oxígeno"),
]


def build_suite() -> dict[str, Any]:
    """15 casos con fallo (3 por mecanismo) y 5 normales, semillas consecutivas."""
    scenarios: list[dict[str, Any]] = []
    index = 0
    for mechanism in MECANISMOS:
        for repeat in range(3):
            seed = SEED_BASE + index
            scenarios.append(
                {
                    "scenario_id": f"d1-{mechanism}-{repeat}",
                    "description": f"Selección D1 · {mechanism} · repetición {repeat}",
                    "category": "known_fault",
                    "driving_profile": PERFILES[index % len(PERFILES)],
                    "duration_s": DURATION_S,
                    "seed": seed,
                    "anomaly_seed": seed + ANOMALY_OFFSET,
                    "fault": mechanism,
                    "fault_start_s": FAULT_START_S,
                    "fault_end_s": DURATION_S,
                }
            )
            index += 1
    for repeat in range(5):
        seed = SEED_BASE + index
        scenarios.append(
            {
                "scenario_id": f"d1-normal-{repeat}",
                "description": f"Selección D1 · normalidad {repeat}",
                "category": "normal",
                "driving_profile": PERFILES[index % len(PERFILES)],
                "duration_s": DURATION_S,
                "seed": seed,
            }
        )
        index += 1
    return {
        "suite": "obd-lab-suite-d1",
        "purpose": (
            "SELECCIÓN DE MODELO (D1) — instrumental, jamás confirmatorio. Disjunto de "
            "cases_v2 y de suite_v2."
        ),
        "seed_block": [SEED_BASE, SEED_BASE + index - 1],
        "anomaly_seed_rule": f"seed + {ANOMALY_OFFSET}",
        "splits": {"validation": scenarios},
    }


def _describe_window(names: list[str], vector: list[float]) -> str:
    """Descripción textual de una ventana a partir de sus features medidas."""
    values = dict(zip(names, vector, strict=False))
    parts = []
    for key, unit, label in _DESCRITOS:
        if key in values:
            parts.append(f"{label} {values[key]:.2f} {unit}")
    return "; ".join(parts)


def derive_cases(suite: dict[str, Any]) -> list[dict[str, Any]]:
    """Deriva el contexto diagnóstico de cada caso a partir de la telemetría generada."""
    sys.path.insert(0, str(REPO_ROOT / "ai-models" / "src"))
    import numpy as np

    from ai_models.data.dataset import build_dataset

    # El generador escribe bajo <out>/<split>/; el id de sesión lleva la semilla anexa.
    dataset = build_dataset(SESSION_DIR / "validation", size=60, stride=30)
    names = dataset.feature_names
    cases: list[dict[str, Any]] = []
    for scenario in suite["splits"]["validation"]:
        sid = scenario["scenario_id"]
        rows = [i for i, s in enumerate(dataset.session_ids) if s.startswith(f"{sid}-seed")]
        if not rows:
            continue
        fault = scenario.get("fault")
        # Ventana de referencia: con fallo activo si lo hay; si no, la de mayor desviación
        # respecto de la mediana de la sesión (control de sobre-diagnóstico honesto).
        candidates = [i for i in rows if dataset.y[i] == 1] or rows
        block = dataset.x[candidates]
        median = np.median(dataset.x[rows], axis=0)
        spread = np.median(np.abs(dataset.x[rows] - median), axis=0) + 1e-9
        deviation = np.abs(block - median) / spread
        chosen = candidates[int(np.argmax(deviation.sum(axis=1)))]
        cases.append(
            {
                "case_id": f"D1-{sid}",
                "description": scenario["description"],
                "scenario": {
                    "scenario_id": sid,
                    "seed": scenario["seed"],
                    "profile": scenario["driving_profile"],
                    "duration_s": scenario["duration_s"],
                },
                "input_context": _describe_window(names, list(dataset.x[chosen])),
                "window_start_s": dataset.window_starts[chosen],
                "ground_truth": {"failure_mode": fault, "component": None},
                "acceptable_hypotheses": [fault] if fault else ["none"],
                "expected_outcome": "probable" if fault else "no_fault",
            }
        )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-sessions", action="store_true")
    args = parser.parse_args()

    suite = build_suite()
    SUITE_PATH.write_text(
        "# GENERADO por tools/gen_cases_d1.py — no editar a mano.\n"
        + yaml.safe_dump(suite, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    n_esc = len(suite["splits"]["validation"])
    print(f"suite: {SUITE_PATH.relative_to(REPO_ROOT)} ({n_esc} escenarios)")

    if not args.skip_sessions:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "obd_lab.cli",
                "generate",
                "--suite",
                str(SUITE_PATH),
                "--out",
                str(SESSION_DIR),
            ],
            check=True,
            cwd=REPO_ROOT,
            env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT / "obd-lab" / "src")},
        )

    cases = derive_cases(suite)
    payload = {
        "version": "d1-selection-1",
        "purpose": (
            "Banco de SELECCIÓN de modelo (D1). Instrumental: no contrasta hipótesis y su "
            "resultado no se combina con evidencia confirmatoria. Disjunto de cases_v2."
        ),
        "seed_block": suite["seed_block"],
        "composition": {
            "total": len(cases),
            "con_fallo": sum(1 for c in cases if c["ground_truth"]["failure_mode"]),
            "normales": sum(1 for c in cases if not c["ground_truth"]["failure_mode"]),
            "control_trivial": (
                "un generador que responda siempre el mismo mecanismo acierta 3/20 = 0.15"
            ),
        },
        "context_note": (
            "input_context DERIVADO de las features medidas de la ventana, nunca redactado "
            "a mano: no nombra mecanismos ni insinúa la respuesta."
        ),
        "cases": cases,
    }
    CASES_PATH.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8"
    )
    print(f"casos:  {CASES_PATH.relative_to(REPO_ROOT)} ({len(cases)})")
    print(json.dumps(payload["composition"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
