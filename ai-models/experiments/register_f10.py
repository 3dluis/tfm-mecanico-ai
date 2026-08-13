"""Anotaciones F10 sobre el Model Registry (determinista; se ejecuta tras register_e3).

1. Clasifica EXP-ANOM-001/002/003 como ``study_type='exploratory'`` (decisión del autor,
   F10): sus resultados valen como evidencia exploratoria y para diseñar el protocolo
   definitivo, NO como evidencia confirmatoria pre-registrada.
2. Promueve ``anom-combined-we@0.2.0`` EXPERIMENTAL→CANDIDATE con nota explícita de que
   la promoción se basa en evidencia exploratoria de F8/F9; VALIDATED queda condicionado
   al confirmatorio pre-registrado PROTO-CONF-001.
3. Referencia el manifiesto de congelación de brazos (freeze v1).

Ningún resultado se recalcula ni se reetiqueta; solo se AÑADE metadata de clasificación.
"""

from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelStatus

ROOT = Path(__file__).resolve().parents[1]

EXPLORATORY = ("EXP-ANOM-001", "EXP-ANOM-002", "EXP-ANOM-003")
FREEZE_NOTE = (
    " · CONGELADO en freeze-v1 (ai-models/registry/frozen/arms-freeze-v1.json): "
    "cualquier mejora posterior será una versión nueva."
)


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)

    for exp_id in EXPLORATORY:
        exp = reg.get_experiment(exp_id)
        reg.save_experiment(exp.model_copy(update={"study_type": "exploratory"}))

    combined = reg.get("anom-combined-we", "0.2.0")
    if combined.status is ModelStatus.EXPERIMENTAL:
        reg.update_status("anom-combined-we", "0.2.0", ModelStatus.CANDIDATE)
    combined = reg.get("anom-combined-we", "0.2.0")
    reg.register(
        combined.model_copy(
            update={
                "notes": (
                    "PROMOCIÓN A CANDIDATE (F10) BASADA EN EVIDENCIA EXPLORATORIA de "
                    "F8/F9 (EXP-ANOM-002/003, study_type=exploratory). La promoción a "
                    "VALIDATED depende del confirmatorio pre-registrado PROTO-CONF-001 "
                    "(docs/experiments/preregistered/). Configuración: LOF-v1 primario ∨ "
                    "event-baseline-z@0.2.0 complementario; unión OR explícita y "
                    "auditable, CONFIGURABLE (anomaly_mode) — no regla fija de producción."
                    + FREEZE_NOTE
                )
            }
        )
    )
    # Nota de congelación también en los dos detectores congelados.
    for model_id, version in (("anom-lof", "0.1.0"), ("event-baseline-z", "0.2.0")):
        entry = reg.get(model_id, version)
        if FREEZE_NOTE.strip(" ·") not in (entry.notes or ""):
            reg.register(entry.model_copy(update={"notes": (entry.notes or "") + FREEZE_NOTE}))
    return reg


if __name__ == "__main__":
    registry = build(ROOT / "registry")
    problems = registry.check()
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        "F10 aplicado: EXP-ANOM-001/002/003 → exploratory; "
        f"anom-combined-we@0.2.0 → {registry.get('anom-combined-we', '0.2.0').status.value}"
    )
