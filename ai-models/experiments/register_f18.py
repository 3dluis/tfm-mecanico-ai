"""Registro determinista del experimento F18 (EXP-ANOM-009, autoencoders recurrentes).

Importa los resultados REALES de ``experiments/e8_results.json`` sin recalcularlos.
Sin entradas de modelo: D1=REJECT (ningún artefacto nuevo que gobernar/desplegar).
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_models.registry import ModelRegistry
from mecanico_contracts import ModelExperiment

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "e8_results.json"

F18_DATE = datetime(2026, 8, 14, tzinfo=UTC)


def build(registry_root: Path) -> ModelRegistry:
    reg = ModelRegistry(registry_root)
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    arms = r["arms"]
    lstm = arms["lstm_ae"]["test"]["point"]
    gru = arms["gru_ae"]["test"]["point"]
    stat = arms["static_ae_fs1_s"]["test"]["point"]
    lof = arms["lof_frozen"]["test"]["point"]
    ctl = r["control_arm"]["test"]["point"]
    ctl_prof = r["control_arm"]["fpr_by_profile_test"]
    q = r["quantization_analysis"]["static"]["by_arm"]["static_ae_fs1_s"]
    q_ctl = r["quantization_analysis"]["static"]["by_arm"]["control_arm"]
    q_pre, q_post = q["flag_rate_normal_pre_crossing"], q["flag_rate_normal_post_crossing"]
    ctl_post = q_ctl["flag_rate_normal_post_crossing"]
    ctl_fpr, ctl_f1, ctl_prec = ctl["fp_rate_normal"], ctl["f1"], ctl["precision"]
    held_seq = arms["gru_ae"]["test"]["per_category"].get("held_out_recall")
    emb = r["embeddings"]
    sil_gru = emb["gru_ae"]["silhouette_between_faults"]
    sil_lstm = emb["lstm_ae"]["silhouette_between_faults"]
    nn_lstm = emb["lstm_ae"]["neighbour_same_fault_rate"]
    xai_gru = r["xai"]["gru_ae"]
    far_maf = xai_gru["fidelity_by_fault"]["maf_drift"]["FAR@5"]
    cross_j = xai_gru["explainer_cross_check"]["jaccard_gradient_vs_permutation"]
    conclusion = (
        "HX-ML-3 REFUTADA en este espacio de modelos y datos. Los autoencoders "
        f"recurrentes son PEORES que los estáticos: LSTM-AE F1 {lstm['f1']} / FPR "
        f"{lstm['fp_rate_normal']} y GRU-AE F1 {gru['f1']} / FPR {gru['fp_rate_normal']} "
        f"frente al AE estático fs1 F1 {stat['f1']} / FPR {stat['fp_rate_normal']} y al LOF "
        f"congelado F1 {lof['f1']} / FPR {lof['fp_rate_normal']}; el recall held-out se "
        f"hunde a {held_seq} (LOF 0.25, AE estático 0.4188) y las anomalías lentas siguen "
        "en 0.0 (joint_slow_drift y load_coolant_decouple). Resultado estable con 3 seeds "
        "(42/43/44) y en las tres longitudes de secuencia evaluadas (30/60/120 pasos = "
        "30/60/120 s): ninguna rescata la detección. La ablation fs1-sequence (F1 0.5459) "
        "queda entre medias: el cuello de botella recurrente pierde información frente al "
        "vector fs1 completo. "
        "HALLAZGO PRINCIPAL (positivo): el BRAZO CONTROL confirma la causa refinada de "
        "EXP-ANOM-008 de forma cuantitativa. El análisis de cuantización muestra que el "
        "FPR de los AE se concentra ENTERAMENTE tras el cruce de cuantización del LTFT "
        f"(t≈920 s en el normal de autovía de test): tasa de marcado {q_pre} "
        f"antes del cruce y {q_post} después. Al añadir al train 10 "
        "sesiones normales de autovía que SÍ cruzan fronteras de cuantización (seeds "
        f"exploratorias 437-509), el MISMO AE denso estático baja el FPR a {ctl_fpr} "
        f"(autovía {ctl_prof['highway']}, igual que LOF) con F1 {ctl_f1} y precisión "
        f"{ctl_prec}, y su marcado post-cruce cae a {ctl_post}. "
        "Es decir: el techo de la serie EXP-ANOM-006/007/008 NO era ni el modelo ni la "
        "representación (estática o temporal), sino la COBERTURA DE NORMALIDAD de un evento "
        "discreto legítimo y raro. CAVEAT EPISTÉMICO que impide promoverlo: el criterio de "
        "cobertura se derivó de un diagnóstico hecho sobre la sesión de TEST (F17), por lo "
        "que el brazo control prueba el mecanismo causal pero NO puede convertirse en "
        "decisión de detector sin una réplica independiente sobre datos ajenos a ese "
        "diagnóstico. "
        f"D1 (detector temporal) = REJECT. D2 (embeddings temporales) = NEEDS MORE EVIDENCE: "
        f"silhouette entre fallos {sil_gru} (GRU) y "
        f"{sil_lstm} (LSTM) frente a 0.2022 del estático, "
        f"pero la consistencia de vecindario es alta ({nn_lstm} "
        "LSTM / 0.7208 GRU): el espacio agrupa por tipo de fallo aunque no lo separe; NO se "
        "abre EXP-PAT-001. D3 (XAI temporal) = NEEDS MORE EVIDENCE: la extensión feature×time "
        "se ejecuta y es estable (celdas: perturbación 0.81, seeds 0.68) y FTH@10 supera al "
        f"azar (1.0 vs 0.25 en maf_drift), pero FAR@5 apenas lo supera ({far_maf} "
        "vs 0.4167), TAR@K resulta NO INFORMATIVA cuando el fallo cubre toda la secuencia "
        "(azar = 1.0) y, sobre todo, la validación cruzada entre explainers SHAP discrepa "
        f"(Jaccard Gradient↔Permutation {cross_j} "
        "en GRU, 0.1438 en LSTM): la atribución a nivel de CELDA aún no es fiable. "
        "LSTM vs GRU = NO WINNER (diferencias dentro del ruido entre seeds). "
        "REGLA DE PARADA ACTIVADA (no se añade profundidad ni se pasa a TCN/Transformer): la "
        "causa dominante es DATASET INSUFICIENTE (cobertura de normalidad), demostrada por el "
        "brazo control; queda abierta como causa secundaria la suficiencia del EMULADOR/GT "
        "para los drifts lentos, que ningún brazo detecta (recall 0.0 incluso en el control). "
        "PROXIMO: replicar la cobertura de normalidad de forma independiente del diagnóstico "
        "y examinar la inyección de anomalías lentas antes de volver a modelos. Validez: "
        "entorno emulado/sintético; el fenómeno de cuantización debe re-examinarse con HCRL."
    )
    reg.save_experiment(
        ModelExperiment(
            experiment_id="EXP-ANOM-009",
            title="Autoencoders recurrentes (LSTM/GRU) sobre secuencias crudas OBD-II",
            objective=(
                "Comprobar HX-ML-3: ¿una arquitectura temporal entrenada solo con normalidad "
                "detecta las anomalías lentas y el contexto que los modelos estáticos no "
                "capturaron, manteniendo el FPR? Incluye brazo control diagnóstico para "
                "probar directamente la causa refinada de EXP-ANOM-008 (cobertura del evento "
                "de adaptación del LTFT cuantizado) y la primera evaluación XAI feature×time."
            ),
            dataset_id="sequence-dataset-v1",
            dataset_version="1.0 (derivado de obd-lab-suite-v1 train v1.1)",
            split_version="suite-v1-split-1",
            feature_schema_version="raw-sequence [T x 12 PIDs] (fs1 en los brazos estáticos)",
            evaluation_protocol=(
                "ADR-0011 + Adenda XAI v1 + adenda temporal F18 (config exp-anom-009.yaml)"
            ),
            study_type="exploratory",
            config_uri="ai-models/configs/exp-anom-009.yaml",
            training_run_ids=[],
            conclusion=conclusion,
            selected_model_id=None,
            report_uri="docs/models/comparisons/temporal_autoencoders_v1.md",
            created_at=F18_DATE,
        )
    )
    return reg


if __name__ == "__main__":
    build(ROOT / "registry")
    print("EXP-ANOM-009 registrado.")
