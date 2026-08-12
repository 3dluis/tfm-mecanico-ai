# Model Card — anom-zscore (baseline z robusto) — REJECTED

**Resultado NEGATIVO documentado (hallazgo citable, no fracaso a ocultar).**
Fuente: `TR-E1-ZSCORE.json` · `e1_results.csv` · informe F3 §4.

## Identificación
- **model_id:** `anom-zscore` · **version:** 0.1.0 · **status: REJECTED**
- **model_type:** ml · **family:** robust_zscore · **purpose:** baseline univariante
  (mediana/MAD por feature, agregación max-|z|)

## Datos y configuración
Idénticos al resto de EXP-ANOM-001 (`obd-lab-suite-v1@1`, `fs1`, seed 42).
**threshold:** 316.68 (cuantil 1 % FPR de train — valor ya sintomático: la cola de
train-normal es extrema).

## Métricas (test)
F1 **0.4425** · FPR **0.1034** · recall conocidos 0.9375 · **recall held-out 0.00** ·
episodios 2/6 · 0.0004 ms/ventana.

## Motivo del rechazo (✍)
La normalidad vehicular es MULTIMODAL (ralentí/urbano/autovía): la mediana/MAD global
mezcla regímenes y el umbral resultante (|z|>316) solo dispara en extremos absolutos.
Las anomalías held-out son RELACIONALES (cada PID en rango individual) → invisible por
construcción para un detector univariante. Hallazgo coherente con Schmidl et al. (VLDB
2022) y con CADD (RAID 2024: colapso del baseline global al mezclar regímenes) — refuerza
la motivación de la detección CONTEXTUAL de F6.

## Valor residual
Sigue siendo útil como (a) baseline de referencia en tablas comparativas y (b) candidato
a detector de extremos absolutos (capa 1 de las 3 capas de detección: global/ventana/evento).
