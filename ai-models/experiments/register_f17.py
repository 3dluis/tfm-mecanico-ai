"""Registro determinista del experimento F17 (EXP-ANOM-008, ablation fs2-lite vs fs1).

Importa los resultados REALES de ``experiments/e7_results.json`` sin recalcularlos.
Sin entradas de modelo: la decisión de esquema es KEEP fs1 y D1=REJECT (ningún
artefacto nuevo que gobernar/desplegar).
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelExperiment

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "e7_results.json"

F17_DATE = datetime(2026, 8, 14, tzinfo=UTC)


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    fs1_s = r["arms"]["fs1+AE-S"]["test"]["point"]
    fs2_s = r["arms"]["fs2-lite+AE-S"]["test"]["point"]
    fs2_m = r["arms"]["fs2-lite+AE-M"]["test"]["point"]
    lof = r["arms"]["lof_frozen"]["test"]["point"]
    hw_fs2 = r["arms"]["fs2-lite+AE-S"]["fpr_by_profile_test"]["highway"]
    foco = r["arms"]["fs2-lite+AE-M"]["focus_fault_recalls"]
    emb_m_fs1 = r["embeddings"]["fs1+AE-M"]["silhouette_between_faults"]
    emb_m_fs2 = r["embeddings"]["fs2-lite+AE-M"]["silhouette_between_faults"]
    xai_fs2 = r["xai"][r["xai"]["finalists"]["fs2"]]
    stab = xai_fs2["stability"]
    conclusion = (
        "Esquema de features = KEEP fs1 (fs2-lite NO se promueve): con 3 seeds "
        "(42/43/44) fs2-lite NO corrige el FPR del AE (AE-S "
        f"{fs2_s['fp_rate_normal']} vs fs1 {fs1_s['fp_rate_normal']}; autovía "
        f"{hw_fs2} en todos los brazos; LOF congelado {lof['fp_rate_normal']}) ni "
        f"mejora los fallos lentos/relacionales foco (joint_slow_drift {foco['joint_slow_drift']}, "
        f"load_coolant_decouple {foco['load_coolant_decouple']}). CAUSA REFINADA "
        "(diagnóstico sobre datos + SHAP convergentes otra vez): el LTFT emulado está "
        "cuantizado J1979 (paso 100/128 = 0.7812) y en el normal de autovía de test "
        "(1800 s) oscila entre dos cuantos adyacentes desde t≈920 s, mientras solo "
        "2/22 sesiones del train v1.1 cruzan alguna frontera de cuantización — TODA "
        "feature derivada de LTFT (absoluta O relativa a la sesión) hereda varianza "
        "casi nula en train y dispara el error estandarizado; la patología no era el "
        "offset absoluto sino la RAREZA en train del evento discreto de adaptación, "
        "que es un fenómeno de contexto TEMPORAL, no de representación estática de "
        "ventana. D1 (detector) = REJECT (tercera vez: ningún brazo AE se acerca al "
        f"FPR de LOF). D2 (representación) = NEEDS MORE EVIDENCE (silhouette entre "
        f"fallos AE-M {emb_m_fs2} fs2 vs {emb_m_fs1} fs1 — sin mejora). D3 (XAI) = "
        "ADOPT confirmado: SHAP volvió a localizar el mecanismo de los FP "
        "(LTFT_session_drift y familia LTFT dominan las explicaciones de FP), "
        f"fidelidad ≫ azar donde hay detección (vacuum AR@5 1.0 vs 0.40), agreement "
        f"J5 {xai_fs2['agreement']['mean_jaccard5']}, estabilidad seeds "
        f"{stab['between_seeds_jaccard5']} / perturbación "
        f"{stab['under_perturbation_jaccard5']} (peor que fs1 en perturbación: 0.83 — "
        "otra razón para no promover). F1 marginalmente mejor de fs2-lite "
        f"({fs2_m['f1']} vs {fs1_s['f1']}) NO justifica promoción (criterio F17: no "
        "hay promoción automática por F1). PROXIMO (directiva F17): EXP-ANOM-009 = "
        "modelos temporales (LSTM-AE/GRU-AE, HX-ML-3) — el evento de adaptación "
        "cuantizada y los drifts lentos no detectados son ambos problemas de contexto "
        "temporal; alternativa documentada no elegida: cobertura dirigida de "
        "normalidad con cruces de cuantización en train. Validez: entorno "
        "emulado/sintético (la sonda de cuantización se re-examinará con HCRL)."
    )
    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-008",
            title="Ablation de esquema de features: fs2-lite (deriva de sesión) vs fs1",
            objective=(
                "Comprobar si fs2-lite (LTFT_session_drift en sustitución de los "
                "absolutos + std multiescala + correlaciones lag-1) corrige el FPR del "
                "AE identificado en EXP-ANOM-007 y mejora la representación de "
                "anomalías lentas/relacionales, sin degradar la explicabilidad "
                "(decisión de esquema + D1/D2/D3)."
            ),
            dataset_id="obd-lab-suite-v1",
            dataset_version="1.1",
            split_version="suite-v1-split-1",
            feature_schema_version="fs1 vs fs2-lite (experimental, no promovido)",
            evaluation_protocol="ADR-0011 + Adenda XAI v1 (config exp-anom-008.yaml)",
            study_type="exploratory",
            config_uri="ai-models/configs/exp-anom-008.yaml",
            training_run_ids=[],
            conclusion=conclusion,
            selected_model_id=None,
            report_uri="docs/models/comparisons/fs2_lite_ablation_v1.md",
            created_at=F17_DATE,
        )
    )
    return reg


if __name__ == "__main__":
    build(ROOT / "registry")
    print("EXP-ANOM-008 registrado.")
