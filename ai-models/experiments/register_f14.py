"""Registro determinista del experimento F14 (EXP-ANOM-006, autoencoder vs LOF).

Importa los resultados REALES de ``experiments/e5_results.json`` sin recalcularlos.
No registra entradas de modelo: ningún brazo AE cumple la condición de adopción de
ADR-0011, no hay artefacto exportado a ONNX y los pesos son regenerables por semilla.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelExperiment

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "e5_results.json"

#: Fecha y commit del experimento E5 (F14) — fijos para reconstrucción determinista.
F14_DATE = datetime(2026, 8, 13, tzinfo=UTC)
F14_GIT = "5035ae7"


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    w60 = r["windows"]["60"]
    ae_std = w60["autoencoder_standard"]["test"]
    ae_rob = w60["autoencoder_robust"]["test"]
    lof = w60["lof"]["test"]
    ho_std = ae_std["per_category"]["held_out_recall"]
    ho_lof = lof["per_category"]["held_out_recall"]
    cb_std = ae_std["per_fault_recall"]["corr_break_rpm_maf"]
    cb_lof = lof["per_fault_recall"]["corr_break_rpm_maf"]
    fpr_std, fpr_lof = ae_std["point"]["fp_rate_normal"], lof["point"]["fp_rate_normal"]
    f1_rob, f1_lof = ae_rob["point"]["f1"], lof["point"]["f1"]
    conclusion = (
        "NINGÚN brazo AE cumple la condición de adopción de ADR-0011 (superar a LOF en "
        "held-out con FPR ≤): a 60/30 autoencoder_standard mejora mucho el held-out "
        f"(recall {ho_std} vs {ho_lof} de LOF, "
        f"corr_break {cb_std} vs {cb_lof}, 6/6 episodios) "
        f"pero con FPR {fpr_std} ≈3× el de LOF ({fpr_lof}); "
        f"autoencoder_robust EMPATA con LOF (F1 {f1_rob} vs {f1_lof}, mismo FPR, "
        "held-out +0.006). LOF k=10 SIGUE SELECTED. Evidencia direccional que justifica "
        "continuar: (1) el AE-standard detecta el held-out relacional a TODAS las "
        "severidades del sweep exploratorio (episodio detectado incluso con decouple 0.3, "
        "donde LOF no detecta nada por debajo de 0.9) y multiplica el recall de misfire; "
        "(2) el FPR del AE-standard se concentra en normales — mismo diagnóstico de "
        "insuficiencia de normalidad que F9 → siguiente paso: re-entrenar con train v1.1 "
        "(22 normales) SIN tocar val/test; (3) derivas lentas conjuntas siguen "
        "esencialmente indetectadas por todos (joint_slow_drift ≤0.1, load_coolant_decouple "
        "≤0.175) → motivación de HX-ML-3 (secuenciales); (4) embeddings latentes con "
        "separación débil entre mecanismos (silhouette entre fallos 0.1175, global -0.0985): "
        "señal preliminar INSUFICIENTE para EXP-PAT-001 sin mejorar la representación. "
        "Resultados por ventana: 30 y 60 s dominan; 120 s colapsa el brazo robust "
        "(umbral 2.08, held-out 0). Sin modelo registrado: nada que gobernar/desplegar."
    )
    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-006",
            title="Autoencoder denso vs LOF sobre el camino wide",
            objective=(
                "HX-ML-2: evaluar si un autoencoder pequeño (4114 parámetros) iguala o "
                "supera a LOF k=10 bajo protocolo ADR-0011, con la ventana como "
                "hiperparámetro {10,30,60,120}s, resultados por anomalía y por severidad "
                "(sweep exploratorio solo-evaluación) y embeddings latentes preliminares."
            ),
            dataset_id="obd-lab-suite-v1",
            dataset_version="1",
            split_version="suite-v1-split-1",
            feature_schema_version="fs1",
            evaluation_protocol="ADR-0011 (config exp-anom-006.yaml)",
            study_type="exploratory",
            config_uri="ai-models/configs/exp-anom-006.yaml",
            training_run_ids=[],
            conclusion=conclusion,
            selected_model_id=None,
            report_uri="docs/models/comparisons/autoencoder_vs_lof_v1.md",
            created_at=F14_DATE,
        )
    )
    return reg


if __name__ == "__main__":
    build(ROOT / "registry")
    print("EXP-ANOM-006 registrado.")
