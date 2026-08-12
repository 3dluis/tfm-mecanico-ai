# Comparación — Detectores de anomalías v1 (EXP-ANOM-001, F3)

**Registro POST-HOC del experimento E1 de F3. Fuente interna: informe
docs/fase3/informe_iteracion_f3.md §4 + experiments/e1_results.csv + ADR-0011. Los
valores se importan sin recalcular.**

## Objetivo
¿Qué modelo no supervisado ofrece mejor equilibrio entre detección de anomalías
desconocidas (held-out relacional/temporal) y falsas alarmas?

## Protocolo (pre-registrado, ADR-0011)
Umbral por cuantil de train-normal (1 % FPR objetivo) · sin point-adjustment · métricas
point-wise Y por episodio · barrido de hiperparámetros SOLO sobre validación · held-out
exclusivamente en test.

## Modelos y datos
4 modelos (config final: z robusto mediana/MAD · IForest n=200 · LOF k=10 ·
OC-SVM ν=0.01 γ=0.005) · dataset `obd-lab-suite-v1@1` · split `suite-v1-split-1` ·
features `fs1` · seed 42 · git 69a1e4d · hardware sandbox-x86.

## Resultados (test)

| Modelo | F1 | FPR | R. conocidos | R. held-out | Episodios | Retardo | ms/ventana |
|---|---|---|---|---|---|---|---|
| z-score robusto | 0.4425 | 0.1034 | 0.9375 | 0.00 | 2/6 | 75 s | 0.0004 |
| Isolation Forest | 0.0 | 0.0172 | 0.0 | 0.0 | 0/6 | — | 0.095 |
| **LOF (k=10)** | 0.6448 | **0.0345** | 0.975 | 0.25 | 4/6 | **37.5 s** | 0.007 |
| OC-SVM | **0.6835** | 0.0862 | 0.9875 | **0.35** | **6/6** | 225 s | 0.003 |

## Interpretación
Los fallos conocidos son casi triviales (recall ≈0.98); el reto real son las anomalías
relacionales held-out — exactamente la pregunta de investigación. A nivel de EPISODIO sí
se detectan. El máx-|z| univariante y el IForest fracasan ante normalidad multimodal
(hallazgo citable, coherente con Schmidl et al. VLDB 2022; y con CADD/RAID 2024 —
motivación directa de la detección contextual F6).

## Limitaciones
Datos 100 % sintéticos cuantizados; 6 episodios held-out (muestra pequeña — leer
episodios como evidencia direccional); umbral sin recalibrar con datos reales.

## Decisión
**LOF k=10 seleccionado** como modelo por defecto (FPR 2.5× menor y retardo 6× menor que
OC-SVM con recall de conocidos equivalente); **OC-SVM segundo paquete** (CANDIDATE:
cobertura 6/6). z-score e IForest **REJECTED** con card de resultado negativo.
Autoencoders solo si superan a LOF en held-out con FPR ≤ acordado. Trade-offs en
[14 §1](../14_model_selection.md).
