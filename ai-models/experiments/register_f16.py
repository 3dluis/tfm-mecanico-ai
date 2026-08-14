"""Registro determinista del experimento F16 (EXP-ANOM-007, AE v2 + XAI).

Importa los resultados REALES de ``experiments/e6_results.json`` sin recalcularlos.
Sin entradas de modelo: D1=REJECT (ningún artefacto que gobernar/desplegar).
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelExperiment

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "e6_results.json"

F16_DATE = datetime(2026, 8, 13, tzinfo=UTC)


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    v11 = r["arms"]["ae_s_v11"]["test"]["point"]
    lof = r["arms"]["lof_frozen"]["test"]["point"]
    xai = r["xai"]
    fpr_m = r["arms"]["ae_m_v11"]["test"]["point"]["fp_rate_normal"]
    fpr_wd = r["arms"]["ae_s_v11_wd"]["test"]["point"]["fp_rate_normal"]
    ag = xai["agreement"]
    stab = xai["stability"]
    conclusion = (
        "D1 (detector) = REJECT: el train v1.1 NO corrige el FPR del AE "
        f"(0.112 a {v11['fp_rate_normal']}; AE-M {fpr_m}; weight decay {fpr_wd}) frente "
        f"a LOF congelado {lof['fp_rate_normal']} — el precedente de F9 no transfiere "
        "al AE. CAUSA RAIZ identificada por dos diagnósticos independientes "
        "convergentes (per-feature error + SHAP): los FP se concentran en normales de "
        "autovía (FPR por perfil 0.47-0.51 vs urbano 0.00-0.03) y están dominados por "
        "features ABSOLUTAS de fuel trim (LTFT mean/slope/std y total_trim son el "
        "top-5 global de atribución) — offsets de LTFT entre sesiones que son "
        "variación normal legítima; ni más datos, ni capacidad, ni regularización lo "
        "corrigen porque el problema es de REPRESENTACION de features. "
        "D2 (representación) = NEEDS MORE EVIDENCE: AE-M mejora silhouette entre "
        "fallos a 0.2022 (vs 0.1175 en E5, +72%) con PCA-2c 0.92, pero el espacio "
        "sigue contaminado por la misma patología; no se promueve a EXP-PAT todavía. "
        "D3 (SHAP/XAI) = ADOPT como mecanismo de evaluación y diagnóstico (no "
        "decisión automática): fidelidad muy por encima del azar en los fallos bien "
        "detectados (vacuum AR@1/3/5 = 1.0/1.0/1.0 vs azar 0.38; maf 1.0/1.0/0.85 vs "
        "0.29; corr_break 1.0/0.67/0.70 vs 0.24; los apenas detectados quedan cerca "
        f"del azar con n=1, coherente), agreement parcial (Jaccard@5 "
        f"{ag['mean_jaccard5']}; {ag['class_counts']}), estabilidad moderada (seeds "
        f"{stab['between_seeds_jaccard5']}, perturbación "
        f"{stab['under_perturbation_jaccard5']}), coste trivial "
        f"({xai['runtime_seconds']}s/{xai['samples_explained']} muestras) y VALOR "
        "DEMOSTRADO: las explicaciones de FP señalaron la causa del FPR de forma "
        "independiente al diagnóstico. Contrafactual validado (ventanas pre-fallo "
        "idénticas al gemelo; score 0.13 a 0.89 al inyectar). Sonda de fingerprint: "
        "el perfil de atribución en normales difiere entre escenarios (cos 0.05) — "
        "consistente con la patología de trims; se vigilará con datos reales. "
        "PROXIMO: EXP-ANOM-008 = ablation fs2-lite (LTFT_session_drift + multiescala "
        "+ lag-1 vs fs1), la corrección a nivel de features respaldada por ambos "
        "diagnósticos; secuenciales pospuestos (la patología no es de orden temporal)."
    )
    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-007",
            title="Autoencoder v2 (train v1.1, ablaciones) + primera evaluación XAI formal",
            objective=(
                "Resolver las tres decisiones abiertas de EXP-ANOM-006: D1 corregir el FPR "
                "del AE (train v1.1, capacidad, weight decay — un cambio por brazo), D2 "
                "re-evaluar el espacio latente, D3 ejecutar por primera vez la evaluación "
                "XAI completa de la Adenda (AR@K vs azar, agreement, estabilidad, FP)."
            ),
            dataset_id="obd-lab-suite-v1",
            dataset_version="1.1",
            split_version="suite-v1-split-1",
            feature_schema_version="fs1",
            evaluation_protocol="ADR-0011 + Adenda XAI v1 (config exp-anom-007.yaml)",
            study_type="exploratory",
            config_uri="ai-models/configs/exp-anom-007.yaml",
            training_run_ids=[],
            conclusion=conclusion,
            selected_model_id=None,
            report_uri="docs/models/comparisons/autoencoder_v2_xai_v1.md",
            created_at=F16_DATE,
        )
    )
    return reg


if __name__ == "__main__":
    build(ROOT / "registry")
    print("EXP-ANOM-007 registrado.")
