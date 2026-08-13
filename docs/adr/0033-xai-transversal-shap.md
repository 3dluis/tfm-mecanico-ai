# ADR-0033 — XAI transversal con SHAP en el ciclo experimental ML

**Estado:** Aceptada (decisión del autor, F15 · 2026-08-13)
**Relacionada con:** ADR-0009 (separación ML/LLM), ADR-0011 (protocolo y condición de
adopción), ADR-0031 (línea ML wide), Protocolo ML v1 §13 y
[Adenda XAI v1](../experiments/protocolo_ml_v1_adenda_xai.md)

## Contexto

La PI exige descubrir **y explicar** patrones de fallo. Hasta F14, la explicabilidad
estaba prevista de forma dispersa: protocolo §13 (transversal, «SHAP solo si el coste se
justifica»), models/02 §5 (evidencia por inferencia), per-feature reconstruction error
implementado en el AE, y el EdA con la distinción capa (a) decisión-del-modelo / capa
(b) causa-mecánica. Faltaba: un marco que haga la explicación **evaluable** (no solo
producible), métricas con ground truth, criterios de estabilidad, y su encaje en la
selección de modelos y en la evidencia del agente.

## Decisión

1. **XAI es dimensión transversal de evaluación** de la línea ML, gobernada por la
   **Adenda XAI v1** del Protocolo ML v1 (exploratoria; nada confirmatorio).
2. **Principio de capas vinculante:** `XAI attribution ≠ mechanical causality ≠
   confirmed diagnosis`. SHAP explica el comportamiento del modelo; la hipótesis
   mecánica pertenece al agente (capa b) y su confirmación al protocolo de validación.
3. **Dos niveles de explicación:** mecanismo específico del modelo (per-feature
   reconstruction error, distancias LOF, z contextual…) + **SHAP como capa común
   comparable entre modelos**, explicando una función declarada
   (`reconstruction_error(x)` o `anomaly_score(x)`). SHAP nunca es loss ni objetivo del
   optimizador; los hallazgos SHAP solo motivan re-entrenos como decisión registrada.
4. **Sin serie EXP-XAI-\*:** XAI se evalúa dentro de EXP-ANOM-*/EXP-PAT-* mediante el
   esquema de decisiones independientes **D1 (detector) / D2 (representación) /
   D3 (mecanismo explicativo)** — combinaciones mixtas son legítimas. Retro-aplicado a
   EXP-ANOM-006: D1=REJECT, D2=NEEDS MORE EVIDENCE, D3=NEEDS MORE EVIDENCE (SHAP aún
   no ejecutado); sus resultados registrados no se alteran.
5. **Métricas XAI** con ground truth sintético de atribución (mapeo fallo→conjunto de
   features derivado del catálogo de inyección): Attribution Recall@{1,3,5} contra
   baseline aleatorio, Precision@K condicionada, agreement per-feature-error↔SHAP
   (Jaccard@K, Spearman; AGREE/PARTIAL/DISAGREE) y estabilidad (perturbación y seeds).
   Para anomalías multivariables el GT es un conjunto: atribución distribuida = correcta.
6. **Selección de modelos ampliada** (docs/models/14): Detection Performance +
   Explainability + Explanation Stability + Representation Quality + Edge Feasibility,
   con decision gate de 7 preguntas. La evidencia negativa de explicación puede vetar la
   promoción de un modelo con mejor F1.
7. **Higiene experimental:** background SOLO de train-normal (hasheado, determinista);
   sampling estratificado reproducible; registro completo (shap_version, explainer,
   background, runtime, hardware); SHAP como auditoría de leakage y de
   synthetic-domain bias (huella del generador).
8. **Edge:** la inferencia edge produce score/reconstruction error/embedding; el
   análisis XAI completo es offline. Explicaciones ligeras en edge = trabajo futuro.
9. **Persistencia:** artefactos experimentales JSON por ahora; contratos
   `ModelExplanation`/`FeatureAttribution` documentados como diseño futuro (conceptual
   antes que físico; cambio aditivo + ADR cuando el runtime los consuma).
10. **Objetivos del TFM sin cambios:** los objetivos vigentes ya cubren «explicar»
    (OE con diagnósticos explicables; H-EXP; nodo `verify` de C6). XAI operacionaliza
    ese objetivo; no se reformula nada para adaptarlo a SHAP.

## Alternativas consideradas

- *Serie EXP-XAI-\* propia:* rechazada — duplicaría configs/registros por experimento y
  rompería el mapeo familias↔hipótesis del pre-registro; se reserva para experimentos
  cuyo OBJETO sean los métodos de explicación.
- *SHAP como criterio de entrenamiento (regularización/selección automática de
  features):* rechazada — mezcla evaluación con optimización, invalida la comparación
  con brazos congelados y contradice ADR-0011.
- *Fijar KernelExplainer:* rechazada — el explainer se elige por modelo/coste/versión y
  se registra; fijarlo a priori sesga el coste sin beneficio.
- *Crear ya tablas explanation/attribution:* rechazada — ningún consumidor en vivo las
  necesita; artefactos experimentales bastan y el esquema físico exige contrato aditivo.

## Consecuencias

- EXP-ANOM-007 (propuesto) incorpora de serie la evaluación XAI: SHAP sobre
  reconstruction_error, AR@K contra el GT del catálogo, estabilidad entre seeds y
  agreement con per-feature error — su spec hereda esta adenda sin cambios de protocolo.
- El paquete de evidencia hacia el agente se amplía (top_features, shap_values,
  reconstruction_error, reference_baseline) manteniendo la regla: el agente enuncia
  compatibilidad, jamás causalidad confirmada.
- Coste computacional de SHAP acotado por diseño (sampling + offline); riesgo declarado
  en el registro de la adenda §19.
- Los documentos evictados/untracked del autor (04_riesgos, EdA, metodología de Fase 0)
  NO se tocan: las integraciones pendientes quedan listadas en el informe F15.
