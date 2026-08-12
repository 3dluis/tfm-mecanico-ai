"""Importación POST-HOC de los resultados reales de F3/F4/F6 al Model Registry (F7).

Regla del plan F7 (§47): importar los valores originales del experimento E1
(``e1_results.csv`` + informe docs/fase3/informe_iteracion_f3.md + ADR-0011) SIN
recalcularlos ni modificarlos. Este script es determinista (timestamps fijos de la
época del experimento) para que el registro sea reproducible byte a byte.

Uso: ``python experiments/register_f3.py`` desde ai-models/ (o make registry).
"""

import csv
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import (
    HardwareValidation,
    HardwareValidationStatus,
    ModelCapability,
    ModelExperiment,
    ModelRegistryEntry,
    ModelStatus,
    ModelType,
    TrainingRun,
)

ROOT = Path(__file__).resolve().parents[1]
E1_CSV = ROOT / "experiments" / "e1_results.csv"

#: Fecha del experimento E1 (F3) — fija: el registro debe ser determinista.
F3_DATE = datetime(2026, 8, 12, tzinfo=UTC)
F3_GIT = "69a1e4d"  # commit registrado en experiments/runs.jsonl
HW = "sandbox-x86 (límites 4 CPU / 8 GB, perfil RPi emulado; ADR-0002)"
DATASET = {"dataset_id": "obd-lab-suite-v1", "dataset_version": "1"}
COMMON = {
    "split_version": "suite-v1-split-1",  # normal→train/val; known_fault+held_out→test
    "feature_schema_version": "fs1",  # FEATURE_NAMES v1 (42 features, contratos v2)
    "preprocessing_version": "embedded-standard-scaler",
    "seed": 42,
    "git_commit": F3_GIT,
    "hardware": HW,
    "started_at": F3_DATE,
    "completed_at": F3_DATE,
}

#: Configuración final por modelo (fuente: informe F3 §4 y ADR-0011).
HYPERPARAMS: dict[str, dict[str, object]] = {
    "robust_zscore": {"method": "median/MAD", "aggregation": "max|z|"},
    "isolation_forest": {"n_estimators": 200, "random_state": 42},
    "lof": {"n_neighbors": 10, "novelty": True},
    "ocsvm": {"nu": 0.01, "gamma": 0.005},
}

MODEL_IDS = {
    "robust_zscore": "anom-zscore",
    "isolation_forest": "anom-iforest",
    "lof": "anom-lof",
    "ocsvm": "anom-ocsvm",
}

#: Estado inicial asignado según la decisión REAL del informe F3 (no recalculada).
F3_STATUS = {
    "anom-zscore": ModelStatus.REJECTED,  # colapsa ante normalidad multimodal (citable)
    "anom-iforest": ModelStatus.REJECTED,  # F1 test 0.0 (hallazgo coherente con VLDB'22)
    "anom-lof": ModelStatus.SUPERSEDED,  # 0.1.0 → sucedido por el paquete ONNX 0.2.0
    "anom-ocsvm": ModelStatus.CANDIDATE,  # segundo paquete (6/6 episodios; FPR mayor)
}


def _metrics_from_csv() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with E1_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.pop("model")
            episodes = row.pop("episodes_detected")  # "4/6" → 4.0 (el total consta aparte)
            metrics = {k: float(v) for k, v in row.items() if v not in ("", None)}
            metrics["episodes_detected"] = float(episodes.split("/")[0])
            metrics["episodes_total"] = float(episodes.split("/")[1])
            out[name] = metrics
    return out


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    metrics = _metrics_from_csv()

    run_ids: list[str] = []
    for name, model_id in MODEL_IDS.items():
        run_id = f"TR-E1-{model_id.split('-')[1].upper()}"
        run_ids.append(run_id)
        reg.save_training_run(
            TrainingRun(
                training_run_id=run_id,
                experiment_id="EXP-ANOM-001",
                model_id=model_id,
                model_version="0.1.0",
                model_type=ModelType.ML,
                hyperparameters=HYPERPARAMS[name],
                metrics=metrics[name],
                **DATASET,
                **COMMON,
            )
        )
        reg.register(
            ModelRegistryEntry(
                model_id=model_id,
                name=name,
                model_family=name,
                model_type=ModelType.ML,
                version="0.1.0",
                algorithm_version="baselines-e1",
                capabilities=[ModelCapability.ANOMALY_DETECTION],
                status=F3_STATUS[model_id],
                artifact_format="onnx" if name in ("lof", "ocsvm") else "json-params",
                artifact_uri=None,  # reproducible desde seed; sin artefacto commiteado
                model_card_uri=f"docs/models/model-cards/ml/{model_id}.md",
                training_run_id=run_id,
                created_at=F3_DATE,
                validated_at=F3_DATE,
                edge_compatible=None,
                notes="Métricas importadas de e1_results.csv (informe F3 §4, ADR-0011).",
            )
        )

    # LOF 0.2.0: paquete ONNX promovido en F4 (paridad exacta sklearn↔onnxruntime,
    # validado en el pipeline vivo emulador→detección; ARM64 pendiente en el Mac).
    reg.register(
        ModelRegistryEntry(
            model_id="anom-lof",
            name="lof",
            model_family="lof",
            model_type=ModelType.ML,
            version="0.2.0",
            algorithm_version="baselines-e1",
            capabilities=[ModelCapability.ANOMALY_DETECTION],
            status=ModelStatus.VALIDATED,
            artifact_format="onnx",
            artifact_uri="make export → models/model-lof-0.2.0/ (reproducible, seed 42)",
            model_card_uri="docs/models/model-cards/ml/anom-lof.md",
            training_run_id="TR-E1-LOF",
            created_at=F3_DATE,
            validated_at=F3_DATE,
            edge_compatible=None,  # EDGE_APPROVED exige validación ARM64 (pendiente A2/A3)
            hardware_validation=[
                HardwareValidation(
                    target="sandbox-x86",
                    status=HardwareValidationStatus.APPROVED,
                    metrics={"infer_ms_per_window": 0.007},
                    validated_at=F3_DATE,
                    notes="Pipeline vivo emulador→ONNX validado (F3/F4); paridad exacta.",
                ),
                HardwareValidation(target="arm64-container", notes="pendiente (acción A2/A3)"),
                HardwareValidation(target="rpi5", notes="sin hardware físico en el TFM (L2)"),
            ],
            notes="Modelo por defecto del edge (informe F3). Umbral 0.163197 (1% FPR train).",
        )
    )

    # Detectores de F6 (reglas/máquina de estados: modelos ML de la taxonomía, sin pesos).
    reg.register(
        ModelRegistryEntry(
            model_id="event-detector",
            name="event state machine",
            model_family="state_machine",
            model_type=ModelType.ML,
            version="ed:1",
            capabilities=[ModelCapability.EVENT_DETECTION],
            status=ModelStatus.VALIDATED,
            artifact_format="python-rules",
            model_card_uri="docs/models/model-cards/ml/event-detector.md",
            created_at=F3_DATE,
            validated_at=F3_DATE,
            edge_compatible=True,  # python puro, sin dependencias de inferencia
            notes="F1 0.77–1.00 por tipo vs ground truth (informe F6). Baseline a batir por ML.",
        )
    )
    reg.register(
        ModelRegistryEntry(
            model_id="event-baseline-z",
            name="contextual event baseline (robust z)",
            model_family="zscore_contextual",
            model_type=ModelType.ML,
            version="0.1.0",
            capabilities=[ModelCapability.ANOMALY_DETECTION],
            status=ModelStatus.CANDIDATE,
            artifact_format="json-params",
            model_card_uri="docs/models/model-cards/ml/event-baseline-z.md",
            created_at=F3_DATE,
            validated_at=F3_DATE,
            edge_compatible=True,
            notes=(
                "Slice F6: 0/5 FP held-out normal; 5/6 aceleraciones maf_drift señaladas. "
                "Pendiente experimento ventana-vs-evento (E1/R1)."
            ),
        )
    )

    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-001",
            title="Baselines no supervisados de detección de anomalías (E1, F3)",
            objective=(
                "¿Qué modelo no supervisado ofrece mejor equilibrio entre detección de "
                "anomalías desconocidas (held-out) y falsas alarmas?"
            ),
            evaluation_protocol="ADR-0011 (umbral 1% FPR solo-train; sin point-adjustment; "
            "métricas por episodio; held-out jamás usado para ajustar)",
            config_uri="ai-models/configs/exp-anom-001.yaml",
            training_run_ids=run_ids,
            conclusion=(
                "LOF k=10 seleccionado (F1 test 0.64, FPR 0.035, 0.975 recall conocidos, "
                "0.25 held-out, 4/6 episodios); OC-SVM segundo paquete (6/6 episodios, "
                "FPR 0.086). Máx-|z| univariante e IForest fracasan ante normalidad "
                "multimodal (hallazgo citable, coherente con Schmidl et al. VLDB 2022)."
            ),
            selected_model_id="anom-lof",
            report_uri="docs/models/comparisons/anomaly_detectors_v1.md",
            created_at=F3_DATE,
            **DATASET,
            split_version=str(COMMON["split_version"]),
            feature_schema_version=str(COMMON["feature_schema_version"]),
        )
    )
    return reg


if __name__ == "__main__":
    registry = build(ROOT / "registry")
    problems = registry.check()
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"Registro reconstruido en {ROOT / 'registry'}: {len(registry.entries())} modelos")
