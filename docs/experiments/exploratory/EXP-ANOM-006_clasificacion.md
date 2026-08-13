# EXP-ANOM-006 — Clasificación: EXPLORATORY (F14)

**Decisión del autor (continuación de la línea ML):** experimento exploratorio bajo el
Protocolo ML v1. No toca semillas reservadas del pre-registro, brazos congelados ni
held-out confirmatorio; el sweep de severidad usa semillas nuevas del rango exploratorio
(412–425) y es íntegramente conjunto de evaluación.

## Inventario de decisiones

**Existían ANTES de ejecutar:**
- Protocolo ADR-0011 y condición de adopción (superar a LOF en held-out con FPR ≤).
- Dataset de ajuste: train congelado de suite v1 (único conjunto de ajuste).
- Rejilla de ventanas {10,30,60,120} s e hipótesis HX-ML-2 (Protocolo ML v1 §§1–2, F13).
- Arquitectura acotada a priori: AE denso <100k parámetros (quedó en 4 114).
- Comparación StandardScaler vs RobustScaler (protocolo §4).

**Tomadas DURANTE el análisis:**
- Ninguna que afecte al ajuste: no se recalibró ningún umbral tras ver validación/test;
  no se repitieron entrenamientos "para mejorar"; no se excluyó ninguna celda.

**Consecuencia de resultados OBSERVADOS:**
- Adopción DENEGADA (FPR del brazo sensible ≈3× LOF); LOF sigue SELECTED.
- Autoencoder → EXPERIMENTING en el inventario; embeddings declarados insuficientes
  para EXP-PAT-001 con esta representación.
- Propuesta de EXP-ANOM-007 (re-entrenar con train v1.1) como mejora candidata
  precedentada por F9 — pendiente de aprobación del autor.

## Adición F15 — decisiones D1/D2/D3 (Adenda XAI v1, retro-aplicada)

D1 detector = **REJECT** (forma actual; FPR) · D2 representación = **NEEDS MORE
EVIDENCE** (silhouette 0.118) · D3 mecanismo explicativo = **NEEDS MORE EVIDENCE**
(SHAP no ejecutado en E5; se evalúa desde EXP-ANOM-007 según la adenda). Los resultados
registrados no se modifican.

## Estado en el registro

- `ai-models/registry/experiments/EXP-ANOM-006.json` (`study_type: exploratory`)
- Artefactos: `ai-models/experiments/e5_results.json`, `runs.jsonl` (12 entradas),
  `experiments/tmp/e5_embeddings.npz` (no versionado, regenerable por semilla)
- Informe: `docs/models/comparisons/autoencoder_vs_lof_v1.md`
