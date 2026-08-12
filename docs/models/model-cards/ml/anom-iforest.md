# Model Card — anom-iforest (Isolation Forest) — REJECTED

**Resultado NEGATIVO documentado.** Fuente: `TR-E1-IFOREST.json` · `e1_results.csv` ·
informe F3 §4.

## Identificación
- **model_id:** `anom-iforest` · **version:** 0.1.0 · **status: REJECTED**
- **model_type:** ml · **family:** isolation_forest

## Datos y configuración
Idénticos al resto de EXP-ANOM-001. **hyperparameters:** n_estimators=200,
random_state=42 (barrido adicional max_features/max_samples en runs.jsonl sin mejora).
**threshold:** 0.0673 (1 % FPR train).

## Métricas (test)
**F1 0.0** · FPR 0.0172 · recall conocidos 0.0 · recall held-out 0.0 · episodios 0/6 ·
0.095 ms/ventana · fit 0.496 s.

## Motivo del rechazo (✍)
Con el umbral fijado al 1 % FPR sobre train-normal multimodal, los scores de las
anomalías de test quedan DENTRO del rango de scores normales: IForest aísla puntos
globalmente raros, y en una normalidad multimodal los regímenes minoritarios legítimos
(p. ej. arranque en frío) son tan "aislables" como las anomalías reales. Recall 0 con el
protocolo honesto (sin point-adjustment) — resultado consistente con la crítica
metodológica de Schmidl et al. (VLDB 2022) al uso de IForest con point-adjustment.

## Condición de reconsideración
Solo como detector POR CONTEXTO (un IForest por context_signature, tras F6) — nunca
global. Esa variante sería un modelo NUEVO con su propio experimento.
