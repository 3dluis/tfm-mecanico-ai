"""Registro determinista de EXP-ANOM-003 en el Model Registry (lee e3_summary.json).

Crea: dataset v1.1 en el linaje, entrada event-baseline-z@0.2.0 (baselines sobre train
ampliado; 0.1.0 → SUPERSEDED), anom-combined-we@0.2.0 (W-v1 OR E-d; 0.1.0 → SUPERSEDED),
TrainingRuns y una ModelEvaluation por brazo × split. NO reetiqueta resultados de
EXP-ANOM-002 (sus evaluaciones EV-E2-* permanecen intactas).
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
SUMMARY = ROOT / "experiments" / "e3_summary.json"
F9_DATE = datetime(2026, 8, 13, tzinfo=UTC)
HW = "sandbox-x86 (límites 4 CPU / 8 GB, perfil RPi emulado; ADR-0002)"
DATASET = {"dataset_id": "obd-lab-suite-v1", "dataset_version": "1.1"}
PROTOCOL = (
    "ADR-0011 por tick + métricas event-level (config exp-anom-003.yaml; umbrales solo "
    "train v1/v1.1 según brazo; validation/test/held-out congelados e idénticos a v1)"
)

ARM_MODEL: dict[str, tuple[str, str, str]] = {
    # brazo → (model_id, version, nota)
    "AM-W-v1": ("anom-lof", "0.1.0", "referencia (train v1; idéntico a EXP-ANOM-002)"),
    "AM-W-v2": (
        "anom-lof",
        "0.1.0",
        "VARIANTE reentrenada con train v1.1 — NO adoptada (FPR test 0.142 vs 0.067)",
    ),
    "AM-E-v1": ("event-baseline-z", "0.1.0", "referencia (train v1)"),
    "AM-E-d": ("event-baseline-z", "0.2.0", "configuración ADOPTADA (train v1.1, media/σ)"),
    "AM-E-v2": (
        "event-baseline-z",
        "0.2.0",
        "scoring robusto p50/percentiles — RECHAZADO (held-out 0/4; peor FPR que AM-E-d)",
    ),
    "AM-WE-v1": ("anom-combined-we", "0.1.0", "combinación original (EXP-ANOM-002)"),
    "AM-WE-d": (
        "anom-combined-we",
        "0.2.0",
        "combinación RECOMENDADA: W-v1 OR E-d (FPR 0.071 ≈ ventana sola)",
    ),
    "AM-WE-v2": ("anom-combined-we", "0.2.0", "variante W-v2 OR E-d — no adoptada (FPR 0.144)"),
    "AM-WE-rob": ("anom-combined-we", "0.2.0", "variante robusta — rechazada"),
}


def _metrics(row: dict[str, Any]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k in (
        "precision",
        "recall",
        "f1",
        "fpr",
        "event_precision",
        "event_recall",
        "event_f1",
        "false_events_per_normal_session",
    ):
        if k in row and row[k] is not None:
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

    # Nuevas versiones (0.1.0 → SUPERSEDED; transición F9 del ciclo de vida).
    for model_id, name, family, status, notes in (
        (
            "event-baseline-z",
            "contextual event baseline (robust z)",
            "zscore_contextual",
            ModelStatus.CANDIDATE,
            "Baselines sobre train v1.1 (22 sesiones normales), scoring media/σ (el "
            "robusto se evaluó y RECHAZÓ). FPR test 0.008 con umbral LOSO honesto; "
            "conserva la detección relacional urbana (R 0.41, retardo 38 s). "
            "Detalle: docs/models/comparisons/event_fpr_refinement_v1.md",
        ),
        (
            "anom-combined-we",
            "combinación window+event (OR por tick)",
            "ensemble_or",
            ModelStatus.EXPERIMENTAL,
            "W-v1 OR E-d (EXP-ANOM-003): F1 0.70, FPR 0.071 (≈ ventana sola 0.067), "
            "held-out 2/4, recall 0.58 > 0.54 de la ventana sola. Propuesta de "
            "promoción a CANDIDATE pendiente de aprobación del autor.",
        ),
    ):
        reg.register(
            ModelRegistryEntry(
                model_id=model_id,
                name=name,
                model_family=family,
                model_type=ModelType.ML,
                version="0.2.0",
                capabilities=[ModelCapability.ANOMALY_DETECTION],
                status=status,
                artifact_format="json-params" if family == "zscore_contextual" else "composition",
                model_card_uri="docs/models/model-cards/ml/event-baseline-z.md"
                if family == "zscore_contextual"
                else "docs/models/comparisons/event_fpr_refinement_v1.md",
                training_run_id="TR-E3-EVENT-EXT" if family == "zscore_contextual" else None,
                created_at=F9_DATE,
                edge_compatible=True if family == "zscore_contextual" else None,
                notes=notes,
            )
        )
        reg.update_status(model_id, "0.1.0", ModelStatus.SUPERSEDED)

    reg.save_training_run(
        TrainingRun(
            training_run_id="TR-E3-EVENT-EXT",
            experiment_id="EXP-ANOM-003",
            model_id="event-baseline-z",
            model_version="0.2.0",
            model_type=ModelType.ML,
            split_version="suite-v1.1-split-1 (train ampliado; val/test congelados)",
            feature_schema_version="efv:1",
            preprocessing_version="pp:1",
            hyperparameters={
                "grouping": "event_type+context_signature",
                "scoring": "media/σ (robusto evaluado y rechazado)",
                "threshold": summary["thresholds"]["AM-E-d"],
                "threshold_rule": "cuantil 1% FPR sobre scores LOSO de train normal (22 sesiones)",
                "n_baselines": summary["context_stats"]["train_ext"]["n_baselines"],
            },
            seed=42,
            git_commit=summary["git_sha"],
            started_at=F9_DATE,
            completed_at=F9_DATE,
            hardware=HW,
            metrics={
                "scored_events_valtest": summary["context_stats"]["train_ext"]["scored_val_test"],
                "unscored_events_valtest": summary["context_stats"]["train_ext"][
                    "unscored_val_test"
                ],
            },
            **DATASET,
        )
    )

    for row in summary["global"]:
        model_id, version, note = ARM_MODEL[row["arm"]]
        reg.save_evaluation(
            ModelEvaluation(
                evaluation_id=f"EV-E3-{row['arm']}-{row['split']}",
                model_id=model_id,
                model_version=version,
                protocol=PROTOCOL,
                metrics=_metrics(row),
                hardware=HW,
                evaluated_at=F9_DATE,
                notes=f"EXP-ANOM-003 brazo {row['arm']} · {note} · episodios "
                f"{row['episodes_detected']}/{row['episodes_total']} · held-out "
                f"{row['heldout_detected']}/{row['heldout_total']}",
                **DATASET,
            )
        )

    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-003",
            title="Refinamiento del FPR de Event Intelligence (F9)",
            objective=(
                "¿Las falsas alarmas del brazo de eventos se deben a datos normales "
                "insuficientes, baselines poco representativos, contabilidad de eventos "
                "largos o contextos inadecuados? Criterio de éxito CONJUNTO: FPR + "
                "held-out + retardo + event precision."
            ),
            evaluation_protocol=PROTOCOL,
            config_uri="ai-models/configs/exp-anom-003.yaml",
            training_run_ids=["TR-E3-EVENT-EXT"],
            conclusion=(
                "CAUSA CONFIRMADA: insuficiencia de normalidad, no defecto conceptual — "
                "la descomposición de varianza muestra que solo el LTFT de autovía tiene "
                "varianza entre-sesiones dominante (ratio 1.56) y con 22 sesiones el "
                "umbral LOSO se vuelve honesto: AM-E-d logra FPR test 0.008 (objetivo "
                "1%) y event precision 0.98 conservando la detección relacional urbana "
                "(R 0.41, 38 s; atenuada desde 0.73/17 s — trade-off documentado). El "
                "scoring robusto p50/percentiles se RECHAZA (held-out 0/4). El LOF "
                "reentrenado con train ampliado NO se adopta (FPR 0.142 vs 0.067 — "
                "hallazgo: más diversidad ayudó a los eventos y perjudicó al umbral de "
                "la ventana). Configuración recomendada: AM-WE-d = LOF-v1 (primario) OR "
                "eventos-v0.2.0 (complementario): F1 0.70, FPR 0.071 ≈ ventana sola, "
                "recall 0.58>0.54, held-out 2/4, retardo 15 s."
            ),
            selected_model_id="anom-lof",  # el primario NO cambia
            report_uri="docs/models/comparisons/event_fpr_refinement_v1.md",
            created_at=F9_DATE,
            split_version="suite-v1.1-split-1",
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
        f"EXP-ANOM-003 registrado: {len(registry.evaluations())} evaluaciones totales, "
        f"{len(registry.entries())} modelos"
    )
