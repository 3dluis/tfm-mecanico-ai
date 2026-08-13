# EXP-ANOM-006 — Autoencoder denso vs LOF sobre el camino wide

**Fase 14 · 2026-08-13 · exploratorio · runner `ai-models/experiments/e5_autoencoder.py`
· config `ai-models/configs/exp-anom-006.yaml` · seed 42 · sandbox-x86 (4 CPU / 8 GB, CPU)**

## Objetivo e hipótesis

HX-ML-2 (Protocolo ML v1): ¿un autoencoder multivariable pequeño iguala o supera a LOF
k=10 bajo el protocolo ADR-0011? Condición de adopción intacta: el AE solo sustituye a
LOF si lo supera en held-out **con FPR ≤ LOF**. Dimensiones: dos scalers (Standard vs
Robust, §4 del protocolo), ventana como hiperparámetro {10, 30, 60, 120} s (stride =
size/2), resultados por anomalía, por severidad (sweep exploratorio solo-evaluación) y
embeddings latentes preliminares.

## Modelos y datos

AE denso 42→32→16→8→16→32→42 (**4 114 parámetros**, tipo USAD simplificado, referencia
B7), 200 épocas, Adam 1e-3, batch 32, CPU, determinista por semilla. Comparador: LOF
k=10 re-entrenado por configuración (a 60/30 reproduce exactamente el brazo congelado:
umbral 0.163197). Ajuste: EXCLUSIVAMENTE train de suite v1 (6 sesiones normales).
Severidad: `suite_f14_severity.yaml` — 14 sesiones solo-evaluación (semillas 412–425,
rango exploratorio; 2 controles normales + 4 fallos × 3 severidades).

## Resultados por ventana (split test)

| Ventana | Brazo | F1 | FPR | Held-out R | Episodios | Retardo |
|---|---|---|---|---|---|---|
| 10/5 | AE-standard | 0.608 | 0.022 | 0.200 | — | — |
| 10/5 | AE-robust | **0.653** | **0.015** | 0.250 | — | — |
| 10/5 | LOF | 0.636 | 0.033 | 0.233 | — | — |
| 30/15 | AE-standard | **0.730** | 0.114 | **0.469** | — | — |
| 30/15 | AE-robust | 0.688 | 0.038 | 0.325 | — | — |
| 30/15 | LOF | 0.652 | **0.030** | 0.256 | — | — |
| 60/30 | AE-standard | 0.724 | 0.112 | 0.456 | **6/6** | 185.0 s |
| 60/30 | AE-robust | 0.652 | 0.035 | 0.256 | 5/6 | 42.0 s |
| 60/30 | LOF (≡ congelado) | 0.645 | 0.035 | 0.250 | 4/6 | **37.5 s** |
| 120/60 | AE-standard | 0.724 | 0.250 | 0.550 | — | — |
| 120/60 | AE-robust | 0.491 | 0.000 | 0.000 | — | — |
| 120/60 | LOF | 0.688 | 0.018 | 0.313 | — | — |

## Resultados por anomalía (test, 60/30)

| Fallo | LOF | AE-standard | AE-robust |
|---|---|---|---|
| vacuum_leak | 1.000 | 1.000 | 1.000 |
| maf_drift | 0.950 | 0.950 | 0.975 |
| corr_break_rpm_maf (held-out) | 0.500 | **0.838** | 0.425 |
| load_coolant_decouple (held-out) | 0.000 | 0.050 | 0.175 |
| joint_slow_drift (held-out) | 0.000 | 0.100 | 0.000 |

## Resultados por severidad (sweep exploratorio, detectores de 60/30)

Recall de ventanas de fallo (episodio detectado entre paréntesis); FPR de controles
normales: LOF 0.0/0.026 · AE-standard 0.077/0.0 · AE-robust 0.026/0.0.

| Fallo · parámetro | Severidad | LOF | AE-standard | AE-robust |
|---|---|---|---|---|
| vacuum_leak · severity | 0.2 | 0.867 (✓) | 0.967 (✓) | 0.933 (✓) |
| | 0.4 | 1.000 (✓) | 1.000 (✓) | 1.000 (✓) |
| | 0.6 | 1.000 (✓) | 1.000 (✓) | 1.000 (✓) |
| maf_drift · drift | 0.05 | 0.833 (✓) | 0.867 (✓) | 0.833 (✓) |
| | 0.10 | 0.933 (✓) | 0.967 (✓) | 0.933 (✓) |
| | 0.15 | 0.933 (✓) | 0.967 (✓) | 0.933 (✓) |
| misfire · rate | 0.02 | 0.000 (✗) | 0.167 (✓) | 0.033 (✓) |
| | 0.04 | 0.033 (✓) | 0.367 (✓) | 0.067 (✓) |
| | 0.06 | 0.067 (✓) | **0.800** (✓) | 0.333 (✓) |
| corr_break_rpm_maf · decouple | 0.3 | 0.000 (✗) | 0.067 (✓) | 0.000 (✗) |
| | 0.6 | 0.000 (✗) | 0.167 (✓) | 0.000 (✗) |
| | 0.9 | 0.133 (✓) | **0.800** (✓) | 0.233 (✓) |

## Embeddings (preliminar; NO es EXP-PAT-001)

AE-standard @60/30 sobre test: 472 ventanas, latente dim 8. Silhouette global
(fallos+normal): **−0.099** (sin separación global); silhouette solo entre mecanismos de
fallo: **0.118** (separación débil). Artefacto `experiments/tmp/e5_embeddings.npz`
(no versionado; regenerable por semilla).

## Interpretación

1. **La condición de adopción NO se cumple** — LOF sigue SELECTED. AE-standard es el
   detector más sensible del banco (held-out 0.456 vs 0.250; corr_break 0.838 vs 0.500;
   6/6 episodios; misfire ×12 en el sweep) pero paga un FPR ≈3× (0.112 vs 0.035) que lo
   descalifica según ADR-0011. AE-robust logra el perfil de FPR de LOF pero pierde casi
   toda la ventaja de sensibilidad: **el scaler es hoy el dial sensibilidad↔falsas
   alarmas**, no la arquitectura.
2. **El FPR del AE-standard se concentra en normales** — el mismo diagnóstico de
   insuficiencia de normalidad que EXP-ANOM-003 (F9) resolvió para eventos ampliando el
   train a v1.1 (22 normales). La mejora candidata más barata y ya precedentada es
   re-entrenar el AE con train v1.1 SIN tocar val/test, antes de tocar arquitectura.
3. **Severidad**: la detección de fallos de mezcla (vacuum, maf) satura incluso a
   severidad baja — el margen discriminativo del banco no está ahí sino en los fallos
   relacionales e intermitentes, exactamente donde el AE-standard marca la diferencia
   (episodio de corr_break detectado a TODAS las severidades; LOF solo a 0.9).
4. **Ventana**: 30 y 60 s dominan; 10 s pierde contexto multivariable y 120 s deja al
   brazo robust sin datos efectivos (umbral 2.08, held-out 0: con ~9 ventanas/sesión el
   cuantil de train queda inestable). La rejilla {30, 60} queda como espacio útil.
5. **Derivas lentas conjuntas siguen sin techo resuelto** (joint_slow_drift ≤0.1,
   load_coolant_decouple ≤0.175 en el mejor brazo): refuerza HX-ML-3 — es un problema de
   representación temporal, no de umbral.
6. **Embeddings**: separación entre mecanismos débil (0.118). Señal preliminar
   INSUFICIENTE para lanzar EXP-PAT-001 con esta representación; el espacio latente debe
   mejorar (train ampliado, y/o representación secuencial) antes del clustering.

## Limitaciones

Una sola semilla y una sesión por celda de severidad (lecturas direccionales, sin
réplicas ni intervalos); entorno emulado; retardo del AE-standard inflado por episodios
que solo él detecta (185 s promedia detecciones tardías de fallos lentos); sin export
ONNX ni medición edge del AE (pendiente declarado); sweep de severidad ≤ referencia
(no explora severidades mayores).

## Decisión (estructura D1/D2/D3 según Adenda XAI v1, aplicada retrospectivamente)

> Adición F15 (ADR-0033) — no altera ningún resultado; formaliza la decisión en las
> tres dimensiones independientes del experimento:
>
> - **D1 — Autoencoder como detector: REJECT** (en su forma actual): FPR 0.112 ≈3× LOF
>   viola la condición de adopción de ADR-0011; vía de mejora identificada (EXP-ANOM-007,
>   train v1.1).
> - **D2 — Encoder como representación: NEEDS MORE EVIDENCE**: silhouette entre
>   mecanismos 0.118 (débil) — no se promueve a EXP-PAT ni se rechaza; la decisión se
>   re-evalúa con la representación mejorada.
> - **D3 — SHAP/XAI como mecanismo explicativo: NEEDS MORE EVIDENCE**: SHAP no se
>   ejecutó en E5 (la adenda es posterior); el per-feature reconstruction error está
>   implementado pero su evaluación formal (AR@K, estabilidad, agreement) se ejecuta a
>   partir de EXP-ANOM-007.
>
> Nota: D1=REJECT con D2/D3 abiertas NO es inconsistente — son dimensiones separadas.

- LOF k=10 **sigue SELECTED**; ningún modelo nuevo entra al registro (sin artefacto que
  gobernar). EXP-ANOM-006 registrado como exploratorio con conclusión completa.
- Autoencoder pasa a **EXPERIMENTING** en el inventario (evidencia real, adopción
  denegada por ahora).
- Próximo experimento recomendado: **EXP-ANOM-007 = AE re-entrenado con train v1.1**
  (mejora candidata precedentada por F9) manteniendo val/test congelados; los
  secuenciales (LSTM/GRU-AE) quedan condicionados a que ni siquiera eso resuelva el
  techo de las derivas lentas.
