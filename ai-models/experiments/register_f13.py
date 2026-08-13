"""Registro determinista del experimento F13 (EXP-ANOM-005, paridad del camino wide).

Importa los resultados REALES de ``experiments/e4_parity.json`` (generado por
``e4_wide_parity.py``) sin recalcularlos. Timestamps fijos de la época del experimento
para que ``make registry`` siga siendo reproducible byte a byte.

No crea entradas de modelo: la paridad demuestra que los artefactos re-entrenados son
equivalentes a los de E1 (mismos umbrales y métricas), así que la gobernanza de modelos
vigente (anom-lof@0.2.0 VALIDATED, etc.) no cambia.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelExperiment

ROOT = Path(__file__).resolve().parents[1]
PARITY_JSON = ROOT / "experiments" / "e4_parity.json"

#: Fecha y commit del experimento E4 (F13) — fijos: el registro debe ser determinista.
F13_DATE = datetime(2026, 8, 13, tzinfo=UTC)
F13_GIT = "d083f66"  # commit bajo el que se ejecutó (ver experiments/runs.jsonl)


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    parity = json.loads(PARITY_JSON.read_text(encoding="utf-8"))
    all_equal = bool(parity["all_equal"])
    shapes = {
        split: parity["dataset_parity"][split]["shape_wide"]
        for split in ("train", "validation", "test")
    }
    conclusion = (
        "PARIDAD EXACTA confirmada: el camino wide (VehicleTelemetrySnapshot sync:v1 → "
        "matriz columnar → ventanas 60/30 → fs1) produce features byte a byte idénticas al "
        f"camino long de F3 en train/validation/test {shapes} y métricas idénticas para "
        "robust_zscore, isolation_forest, lof y ocsvm (umbral LOF 0.163197 = ancla de "
        "arms-freeze-v1). El snapshot queda VALIDADO como entrada canónica para ML "
        "(ADR-0025 exigía validar ambos caminos antes de migrar consumidores); los "
        "experimentos futuros de F13+ (ventanas como hiperparámetro, autoencoders, "
        "embeddings) pueden construirse sobre snapshots sin perder comparabilidad con "
        "EXP-ANOM-001/002/003. No cambia la selección de modelos (LOF sigue SELECTED)."
        if all_equal
        else "PARIDAD NO ALCANZADA: revisar e4_parity.json antes de usar el camino wide."
    )
    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-005",
            title="Paridad del camino wide (snapshot → matriz → ventanas → fs1)",
            objective=(
                "Verificar que la representación horizontal canónica (ADR-0025/0026) puede "
                "sustituir al pivot long→window de F3 como base de los experimentos ML sin "
                "alterar dataset, umbrales ni métricas (precondición de la línea F13)."
            ),
            dataset_id="obd-lab-suite-v1",
            dataset_version="1",
            split_version="suite-v1-split-1",
            feature_schema_version="fs1",
            evaluation_protocol="ADR-0011 + paridad estricta (config exp-anom-005.yaml)",
            study_type="exploratory",
            config_uri="ai-models/configs/exp-anom-005.yaml",
            training_run_ids=[],
            conclusion=conclusion,
            selected_model_id=None,
            report_uri="docs/models/comparisons/wide_path_parity_v1.md",
            created_at=F13_DATE,
        )
    )
    return reg


if __name__ == "__main__":
    build(ROOT / "registry")
    print("EXP-ANOM-005 registrado.")
