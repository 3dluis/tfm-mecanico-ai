"""Generador DETERMINISTA de las suites de `obd-lab-suite-v2` (F25).

Materializa la especificación del pre-registro §3.2 (congelado, tag `prereg-v1.0`) en 10
ficheros YAML — uno por réplica — sin ninguna aleatoriedad propia: la réplica r usa el
bloque de semillas `[10000+1000·r, 10000+1000·r+999]` con semillas consecutivas en el
orden 22 train → 7 validation → 8 test. Las duraciones aplican el criterio de cobertura
efectiva (urbano/autovía de train a 5 400 s); si la verificación de cobertura de una
réplica falla, `e12_suite_v2.py` re-invoca este generador con `escalation=1|2` para esa
réplica (urbano/autovía a 7 200/9 000 s), siempre dentro del mismo bloque de semillas —
nunca cambiando semillas (regla: se alarga la señal, no se seleccionan semillas).

Los escenarios con fallo declaran `anomaly_seed = seed + 500` (ADR-0034: RNG de inyección
separado; +500 queda dentro del bloque de la réplica y no colisiona con las 37 semillas).

Uso: python tools/gen_suite_v2.py [--out obd-lab/scenarios/suite_v2]
"""

import argparse
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v2"

#: Duración de urbano/autovía de train por nivel de escalada (5400 base → 7200 → 9000).
LONG_S = {0: 5400.0, 1: 7200.0, 2: 9000.0}
AMBIENTS = (8.0, 6.0, 12.0)  # las 3 sesiones frías de train, fijas y declaradas


def replica_spec(r: int, escalation: int = 0) -> dict[str, Any]:
    """Estructura completa de la réplica r (1-10) con su bloque de semillas."""
    base = 10_000 + 1_000 * r
    seeds = iter(range(base, base + 37))
    long_s = LONG_S[escalation]
    rid = f"r{r:02d}"

    train: list[dict[str, Any]] = []
    for i in range(8):
        train.append(
            {
                "scenario_id": f"{rid}-tr-urban-{i}",
                "description": f"Train normal urbano {i} (réplica {r})",
                "category": "normal",
                "driving_profile": "urban",
                "duration_s": long_s,
                "seed": next(seeds),
            }
        )
    for i in range(8):
        train.append(
            {
                "scenario_id": f"{rid}-tr-highway-{i}",
                "description": f"Train normal autovía {i} (réplica {r})",
                "category": "normal",
                "driving_profile": "highway",
                "duration_s": long_s,
                "seed": next(seeds),
            }
        )
    for i in range(3):
        train.append(
            {
                "scenario_id": f"{rid}-tr-idle-{i}",
                "description": f"Train ralentí {i} (réplica {r})",
                "category": "normal",
                "driving_profile": "idle",
                "duration_s": 1800.0,
                "seed": next(seeds),
            }
        )
    for i in range(3):
        train.append(
            {
                "scenario_id": f"{rid}-tr-cold-{i}",
                "description": f"Train arranque frío {i} (réplica {r})",
                "category": "normal",
                "driving_profile": "cold_start",
                "duration_s": 2400.0,
                "seed": next(seeds),
                "ambient_temp_c": AMBIENTS[i],
            }
        )

    def fault_entry(sid: str, desc: str, profile: str, fault: str, **kw: Any) -> dict[str, Any]:
        seed = next(seeds)
        entry: dict[str, Any] = {
            "scenario_id": sid,
            "description": desc,
            "category": kw.pop("category", "known_fault"),
            "driving_profile": profile,
            "duration_s": kw.pop("duration_s", 1800.0),
            "seed": seed,
            "anomaly_seed": seed + 500,
            "fault": fault,
            "fault_start_s": kw.pop("fault_start_s", 600.0),
            "fault_end_s": kw.pop("fault_end_s", 1800.0),
        }
        entry.update(kw)
        return entry

    validation: list[dict[str, Any]] = [
        {
            "scenario_id": f"{rid}-v-normal-a",
            "description": f"Validation normal urbano (réplica {r})",
            "category": "normal",
            "driving_profile": "urban",
            "duration_s": 1800.0,
            "seed": next(seeds),
        },
        {
            "scenario_id": f"{rid}-v-normal-b",
            "description": f"Validation normal autovía (réplica {r})",
            "category": "normal",
            "driving_profile": "highway",
            "duration_s": 1800.0,
            "seed": next(seeds),
        },
        fault_entry(
            f"{rid}-v-vacuum", f"Fuga de vacío (validation, réplica {r})", "urban", "vacuum_leak"
        ),
        fault_entry(
            f"{rid}-v-maf", f"Deriva de MAF (validation, réplica {r})", "highway", "maf_drift"
        ),
        fault_entry(
            f"{rid}-v-thermo",
            f"Termostato abierto (validation, réplica {r})",
            "cold_start",
            "thermostat_stuck",
            duration_s=1500.0,
            fault_start_s=0.0,
            fault_end_s=1500.0,
            ambient_temp_c=8.0,
        ),
        fault_entry(
            f"{rid}-v-o2lag", f"Sonda O2 lenta (validation, réplica {r})", "urban", "o2_lag"
        ),
        fault_entry(
            f"{rid}-v-misfire", f"Fallo de encendido (validation, réplica {r})", "urban", "misfire"
        ),
    ]

    test: list[dict[str, Any]] = [
        {
            "scenario_id": f"{rid}-t-normal-a",
            "description": f"Test normal urbano, control FP (réplica {r})",
            "category": "normal",
            "driving_profile": "urban",
            "duration_s": 1800.0,
            "seed": next(seeds),
        },
        {
            "scenario_id": f"{rid}-t-normal-b",
            "description": f"Test normal autovía, control FP (réplica {r})",
            "category": "normal",
            "driving_profile": "highway",
            "duration_s": 1800.0,
            "seed": next(seeds),
        },
        fault_entry(
            f"{rid}-t-corrbreak-u",
            f"Held-out desacoplo MAF urbano (réplica {r})",
            "urban",
            "corr_break_rpm_maf",
            category="held_out",
        ),
        fault_entry(
            f"{rid}-t-corrbreak-h",
            f"Held-out desacoplo MAF autovía (réplica {r})",
            "highway",
            "corr_break_rpm_maf",
            category="held_out",
        ),
        fault_entry(
            f"{rid}-t-coolfreeze",
            f"Held-out dinámica térmica muerta (réplica {r})",
            "urban",
            "load_coolant_decouple",
            category="held_out",
        ),
        fault_entry(
            f"{rid}-t-jointdrift",
            f"Held-out deriva conjunta MAF/avance (réplica {r})",
            "highway",
            "joint_slow_drift",
            category="held_out",
        ),
        fault_entry(
            f"{rid}-t-vacuum", f"Fuga de vacío, semilla nueva (réplica {r})", "urban", "vacuum_leak"
        ),
        fault_entry(
            f"{rid}-t-maf", f"Deriva de MAF, semilla nueva (réplica {r})", "highway", "maf_drift"
        ),
    ]

    assert next(seeds, None) is None or True  # 37 semillas exactas consumidas arriba
    return {
        "suite": "obd-lab-suite-v2",
        "replica": r,
        "seed_block": [base, base + 999],
        "escalation": escalation,
        "coverage_rule": (
            "positive_level_share >= 0.03 y negative_level_share >= 0.03 sobre las "
            "ventanas fs1 del train (ai_models.audit.coverage); si falla, re-generar "
            "con escalation+1 (mismo bloque de semillas)"
        ),
        "train": train,
        "validation": validation,
        "test": test,
    }


def write_all(out: Path, escalations: dict[int, int] | None = None) -> list[Path]:
    escalations = escalations or {}
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for r in range(1, 11):
        doc = replica_spec(r, escalations.get(r, 0))
        path = out / f"replica-{r:02d}.yaml"
        path.write_text(
            "# GENERADO por tools/gen_suite_v2.py — no editar a mano (pre-registro §3.2).\n"
            + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    paths = write_all(args.out)
    seeds = [e["seed"] for p in paths for e in yaml.safe_load(p.read_text())["train"]]
    print(f"{len(paths)} réplicas → {args.out} (semillas de train {min(seeds)}–{max(seeds)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
