# Model Card — anom-ocsvm (One-Class SVM)

**Fuente:** `TR-E1-OCSVM.json` · `e1_results.csv` · informe F3 §4 · ADR-0011.

## Identificación
- **model_id:** `anom-ocsvm` · **version:** 0.1.0 · **status: CANDIDATE (segundo paquete)**
- **model_type:** ml · **family:** ocsvm · **purpose:** detección no supervisada de
  anomalías por ventana (mismo rol que anom-lof)
- **owner:** `ai-models` (candidato; no desplegado por defecto)

## Origen, datos y configuración
- **algorithm:** OneClassSVM(ν=0.01, γ=0.005) + scaler embebido · no supervisado
- **dataset/split/features/seed/git:** idénticos a anom-lof (`obd-lab-suite-v1@1`,
  `suite-v1-split-1`, `fs1`, seed 42, 69a1e4d) — comparación válida dentro de EXP-ANOM-001
- **threshold:** 0.000241 (cuantil train-normal 1 % FPR)

## Métricas (test)
| métrica | valor |
|---|---|
| F1 | **0.6835** · FPR **0.0862** |
| recall conocidos | 0.9875 · recall held-out | 0.35 |
| episodios held-out | **6/6** · retardo medio 225 s |
| inferencia | 0.003 ms/ventana · RSS 171.8 MB |

## Por qué NO es el modelo por defecto (trade-off documentado, [14 §1](../../14_model_selection.md))
Mejor F1 y cobertura total de episodios, pero FPR 2.5× mayor que LOF (0.086 vs 0.035) y
retardo de detección 6× mayor (225 s vs 37.5 s). En un asistente al conductor las falsas
alarmas erosionan la confianza; se mantiene como segundo paquete y como candidato si un
despliegue prioriza cobertura sobre FPR.

## Limitaciones (✍)
- Mismo riesgo OOD y de calibración sintética que anom-lof.
- ν/γ ajustados solo sobre validación sintética; γ es sensible al escalado — cualquier
  cambio de `preprocessing_version` obliga a re-barrer.
- Retardo de 225 s lo hace inadecuado para fallos de evolución rápida.
- **Unsupported:** tipo de fallo; seguridad en tiempo real.

## Legal
scikit-learn BSD-3 · informe F3 (interno); Schölkopf et al. 2001 — cita formal en EdA.
