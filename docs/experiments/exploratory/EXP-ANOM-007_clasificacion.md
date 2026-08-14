# EXP-ANOM-007 — Clasificación: EXPLORATORY (F16)

**Decisión del autor (aprobación de F15 + instrucción de fase):** exploratorio bajo el
Protocolo ML v1 + Adenda XAI v1. Sin seeds confirmatorias, sin tocar arms-freeze-v1;
LOF participa exclusivamente como brazo CONGELADO (umbral 0.163197, sin re-entrenar).

## Inventario de decisiones

**Existían ANTES de ejecutar:**
- Protocolo ADR-0011 (umbral solo-train) y condición de adopción D1; Adenda XAI v1
  completa (métricas, GT, background, sampling, estabilidad) — congelada en F15, ANTES
  de ver ningún resultado XAI.
- Dataset de evaluación congelado (suite-v1-split-1); train v1.1 como versión declarada
  (F9); brazos de ablation definidos con un cambio único cada uno; espacio de
  arquitectura acotado (AE-S/AE-M, <100k params; sin secuenciales).
- Hipótesis: el precedente F9 (ampliar normalidad) corregiría el FPR (documentada en
  EXP-ANOM-006 antes de esta iteración).

**Tomadas DURANTE el análisis:**
- Ninguna que afecte al ajuste: umbrales intactos tras ver test; ningún re-entreno tras
  ver resultados; el barrido de ventanas del candidato se ejecutó completo (10/30/120)
  pese a la evidencia previa, según la regla de no eliminar ventanas por métricas.

**Consecuencia de resultados OBSERVADOS:**
- D1 = REJECT (la hipótesis F9→AE queda REFUTADA: v1.1 empeora el FPR del AE; causa
  raíz identificada a nivel de features absolutas de fuel trim).
- D2 = NEEDS MORE EVIDENCE (mejora real con capacidad: 0.2022; insuficiente).
- D3 = ADOPT (fidelidad ≫ azar, agreement parcial, estabilidad moderada, diagnóstico
  de FP demostrado); alcance: evidencia y diagnóstico, no decisión automática.
- Propuesto EXP-ANOM-008 (ablation fs2-lite vs fs1) — pendiente de aprobación.

## Estado en el registro

- `ai-models/registry/experiments/EXP-ANOM-007.json` (`study_type: exploratory`)
- Artefactos: `e6_results.json`, `e6_diagnosis.json`, `e6_explanations.json` (12
  artefactos del contrato F15), `runs.jsonl`, figuras en `docs/fase16/figs/`
- Informe: `docs/models/comparisons/autoencoder_v2_xai_v1.md`
