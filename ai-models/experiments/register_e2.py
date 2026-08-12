"""Registro determinista de EXP-ANOM-002 (window vs event vs both) en el Model Registry.

Lee los resultados del artefacto commiteado ``experiments/e2_summary.json`` (producido
por ``e2_window_vs_event.py``) y crea: el ModelExperiment, los TrainingRuns de los
brazos de eventos (construir baselines ES un ajuste con linaje) y una ModelEvaluation
por brazo × split. No recalcula nada. Timestamps fijos ⇒ reconstrucción byte a byte.

Uso: ``python experiments/register_e2.py`` (o ``make registry``).
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_models.registry import ModelRegistry
from mecanico_contracts import (
    ModelCapability,
    ModelEvaluation,
    ModelExperiment,
    ModelRegistryEntry,
    ModelStatus,
    ModelType,
    TrainingRun,
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "experiments" / "e2_summary.json"
F8_DATE = datetime(2026, 8, 12, tzinfo=UTC)
HW = "sandbox-x86 (límites 4 CPU / 8 GB, perfil RPi emulado; ADR-0002)"
DATASET = {"dataset_id": "obd-lab-suite-v1", "dataset_version": "1"}
PROTOCOL = (
    "ADR-0011 extendido a marco por tick (config exp-anom-002.yaml; umbrales: LOF cuantil "
    "train 1% FPR, eventos cuantil LOSO train-normal 1% FPR; held-out intocable)"
)

#: brazo → (model_id, model_version) evaluado.
ARM_MODEL = {
    "AM-W": ("anom-lof", "0.1.0"),
    "AM-E": ("event-baseline-z", "0.1.0"),
    "AM-E-NOCTX": ("event-baseline-z", "0.1.0"),
    "AM-WE": ("anom-combined-we", "0.1.0"),
}


def _metrics(row: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k in ("precision", "recall", "f1", "fpr"):
        out[k] = float(row[k])
    out["episode_recall"] = row["episodes_detected"] / row["episodes_total"]
    if row["heldout_total"]:
        out["heldout_episode_recall"] = row["heldout_detected"] / row["heldout_total"]
    if row["mean_delay_s"] is not None:
        out["mean_delay_s"] = float(row["mean_delay_s"])
    return {k: round(v, 4) for k, v in out.items()}


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    # Entrada para la combinación (composición OR; sin pesos propios).
    reg.register(
        ModelRegistryEntry(
            model_id="anom-combined-we",
            name="combinación window+event (OR por tick)",
            model_family="ensemble_or",
            model_type=ModelType.ML,
            version="0.1.0",
            capabilities=[ModelCapability.ANOMALY_DETECTION],
            status=ModelStatus.EXPERIMENTAL,
            artifact_format="composition",
            model_card_uri="docs/models/comparisons/anomaly_window_vs_event_v1.md",
            created_at=F8_DATE,
            edge_compatible=None,
            notes=(
                "OR de anom-lof@0.1.0 y event-baseline-z@0.1.0 (EXP-ANOM-002). Mejora "
                "recall y retardo a costa de FPR; sin umbral propio."
            ),
        )
    )

    # TrainingRuns de los brazos de eventos (ajuste de baselines con linaje completo).
    for arm, run_id in (("AM-E", "TR-E2-EVENT-CTX"), ("AM-E-NOCTX", "TR-E2-EVENT-NOCTX")):
        cost = summary["costs"][arm]
        reg.save_training_run(
            TrainingRun(
                training_run_id=run_id,
                experiment_id="EXP-ANOM-002",
                model_id="event-baseline-z",
                model_version="0.1.0",
                model_type=ModelType.ML,
                split_version="suite-v1-split-1",
                feature_schema_version="efv:1",
                preprocessing_version="pp:1",
                hyperparameters={
                    "grouping": "event_type+context_signature"
                    if arm == "AM-E"
                    else "event_type (ablación sin contexto)",
                    "threshold": summary["thresholds"][arm],
                    "threshold_rule": "cuantil 1% FPR sobre scores LOSO de train normal",
                    "n_baselines": cost["n_baselines"],
                },
                seed=summary["seed"],
                git_commit=summary["git_sha"],
                started_at=F8_DATE,
                completed_at=F8_DATE,
                hardware=HW,
                metrics={
                    "model_size_bytes": cost["model_size_bytes"],
                    "scored_events": cost["scored_events"],
                    "unscored_events": cost["unscored_events"],
                    "fit_s": summary["fit_times_s"][arm],
                },
                **DATASET,
            )
        )

    # Una evaluación por brazo × split (marco común por tick).
    for row in summary["global"]:
        model_id, version = ARM_MODEL[row["arm"]]
        cost = summary["costs"].get(row["arm"], {})
        reg.save_evaluation(
            ModelEvaluation(
                evaluation_id=f"EV-E2-{row['arm']}-{row['split']}",
                model_id=model_id,
                model_version=version,
                protocol=PROTOCOL,
                metrics=_metrics(row)
                | {
                    k: float(v)
                    for k, v in cost.items()
                    if k
                    in (
                        "t_features_s",
                        "t_scoring_s",
                        "model_size_bytes",
                        "n_features",
                        "t_e2e_mean_s_per_session",
                    )
                },
                hardware=HW,
                evaluated_at=F8_DATE,
                notes=f"EXP-ANOM-002 brazo {row['arm']} · split {row['split']} · "
                f"episodios {row['episodes_detected']}/{row['episodes_total']} · "
                f"held-out {row['heldout_detected']}/{row['heldout_total']}",
                **DATASET,
            )
        )

    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-002",
            title="Window vs Event vs Both (R1+E1 fusionados, F8)",
            objective=(
                "¿La segmentación mediante eventos vehiculares mejora la detección de "
                "anomalías (especialmente multivariables/temporales) frente a ventanas "
                "temporales arbitrarias? (PI.5/H6)"
            ),
            evaluation_protocol=PROTOCOL,
            config_uri="ai-models/configs/exp-anom-002.yaml",
            training_run_ids=["TR-E2-EVENT-CTX", "TR-E2-EVENT-NOCTX"],
            conclusion=(
                "El brazo de eventos NO sustituye a LOF-ventana (F1 test 0.58 vs 0.67; "
                "FPR 0.15 vs 0.07): resultado direccional honesto con solo 6 sesiones "
                "normales de train (varianza entre sesiones domina los baselines, sobre "
                "todo en autovía). SÍ aporta señal complementaria: en el held-out "
                "relacional urbano localiza mucho mejor (R 0.73 vs 0.25; retardo 17 s "
                "vs 30 s) y la unión AM-WE sube recall (0.54→0.63) y baja el retardo "
                "medio (15→4.2 s) a costa de FPR (0.07→0.19). La ablación confirma que "
                "el context_signature aporta (F1 0.58 vs 0.52; held-out 2/4 vs 1/4). "
                "LOF k=10 SIGUE siendo el modelo por defecto (sin supersession)."
            ),
            selected_model_id="anom-lof",
            report_uri="docs/models/comparisons/anomaly_window_vs_event_v1.md",
            created_at=F8_DATE,
            split_version="suite-v1-split-1",
            **DATASET,
        )
    )
    return reg


if __name__ == "__main__":
    registry = build(ROOT / "registry")
    problems = registry.check()
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        f"EXP-ANOM-002 registrado: {len(registry.evaluations())} evaluaciones, "
        f"{len(registry.training_runs('EXP-ANOM-002'))} runs"
    )
