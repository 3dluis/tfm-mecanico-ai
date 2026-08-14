# EXP-ANOM-009 — Autoencoders recurrentes (LSTM/GRU) sobre secuencias crudas (F18)

**Exploratorio** (Protocolo ML v1 + Adenda XAI v1 + [adenda temporal](../../experiments/protocolo_ml_v1_adenda_xai_temporal.md);
config [`exp-anom-009.yaml`](../../../ai-models/configs/exp-anom-009.yaml) CONGELADA antes
de ejecutar; runner `e8_temporal.py`; resultados `e8_results.json`; figuras
[`docs/fase18/figs/`](../../fase18/figs/)). **Validez: entorno emulado/sintético** — sin
HCRL ni ARM64/RPi5.

**Hipótesis HX-ML-3** (declarada y falsable antes de ejecutar): un AE recurrente que
observa la secuencia cruda `[T × PID]` detecta las anomalías lentas y relacionales mejor
que los detectores estáticos, manteniendo el FPR.

**Resultado: HX-ML-3 REFUTADA — y el brazo control identifica la causa real del techo.**

## 1. Comparación principal (test, seed 42)

| Brazo | F1 | Precisión | Recall | FPR normal | FPR autovía | held-out | PR-AUC |
|---|---|---|---|---|---|---|---|
| LSTM-AE (60×12) | 0.455 | 0.738 | 0.329 | 0.121 | 0.475 | **0.006** | 0.732 |
| GRU-AE (60×12) | 0.460 | 0.741 | 0.333 | 0.121 | 0.475 | **0.006** | 0.732 |
| AE estático fs1-S | 0.702 | 0.830 | 0.608 | 0.129 | 0.475 | 0.419 | 0.816 |
| AE estático fs1-M | 0.754 | 0.812 | 0.704 | 0.168 | 0.509 | 0.563 | 0.850 |
| **LOF congelado** | 0.645 | 0.936 | 0.492 | **0.035** | **0.085** | 0.250 | 0.838 |
| **Brazo control** (ver §3) | **0.727** | **0.966** | 0.583 | **0.022** | **0.085** | 0.381 | — |

Los recurrentes son **peores en todo lo que importa**: F1 por debajo de cualquier
estático, mismo FPR, y un recall held-out de 0.006 — es decir, prácticamente ciegos ante
anomalías no vistas, que es justamente la capacidad que justifica un detector no
supervisado. Estable con **3 seeds** (F1 0.451–0.467) y en las **3 longitudes**
evaluadas (30 s: F1 0.471/0.489 · 60 s: 0.455/0.460 · 120 s: 0.454/0.451): ninguna
longitud rescata la detección. La ablation secundaria **fs1-sequence** (GRU sobre 4
sub-ventanas de 15 s × 42 features) queda en F1 0.546 — mejor que la secuencia cruda
pero peor que el vector fs1 completo: el cuello de botella recurrente pierde información
que el AE denso sí explota.

### Fallos foco (recall, test)

| Brazo | joint_slow_drift | load_coolant_decouple | corr_break_rpm_maf |
|---|---|---|---|
| LSTM-AE / GRU-AE (3 seeds) | 0.000 | 0.000 | 0.013–0.038 |
| AE estático fs1-S / fs1-M | 0.025 / 0.175 | 0.025 / 0.075 | 0.813 / 1.000 |
| LOF congelado | 0.000 | 0.000 | 0.500 |
| Brazo control | 0.000 | 0.000 | 0.763 |

**Las anomalías lentas siguen sin detectarse por NINGÚN brazo**, incluido el control.
La memoria recurrente no las recupera; de hecho empeora incluso la ruptura de
correlación (0.013 vs 0.813 del estático).

### Métricas temporales (las que este nivel debía mejorar)

| Brazo | retardo medio | mediana | posición 1ª detección | persistencia | duración media de falsa alarma |
|---|---|---|---|---|---|
| LSTM-AE | 20.0 s | 30.0 s | 0.017 | 0.329 | 280 s |
| GRU-AE | 260.0 s | 30.0 s | 0.217 | 0.333 | 280 s |
| AE estático fs1-S | 115.0 s | 45.0 s | 0.096 | 0.608 | 290 s |
| LOF congelado | 37.5 s | 45.0 s | 0.031 | 0.492 | **37.5 s** |

Los recurrentes detectan 3/6 episodios (estáticos 6/6, LOF 4/6) y sus falsas alarmas
duran 280 s frente a los 37.5 s de LOF.

## 2. El FPR es, en su totalidad, el evento de cuantización del LTFT

Análisis explícito exigido por la instrucción (fase 7 del runner). En el normal de
autovía de test el LTFT cruza su frontera de cuantización en **t ≈ 920 s**; separando
las ventanas normales antes/después de ese instante:

| Brazo | marcado normal ANTES | marcado normal DESPUÉS | score medio slow-drift |
|---|---|---|---|
| AE estático fs1-S | 0.010 | **0.933** | 149.4 |
| LSTM-AE | 0.000 | **0.933** | 266.2 |
| GRU-AE | 0.000 | **0.933** | 244.4 |
| LOF congelado | 0.020 | 0.133 | 9.1 |
| **Brazo control** | 0.000 | **0.167** | 43.9 |

**Prácticamente el 100 % de los falsos positivos de la familia AE proviene de ventanas
posteriores al cruce**, en las tres arquitecturas. La transición es comportamiento
NORMAL del protocolo/sensor (cuantización J1979, paso 100/128 = 0.7812) y marcarla es
un falso positivo, no una detección. Todos los brazos separan la transición normal del
drift anómalo por score medio (columna derecha ≫ score post-cruce), pero solo LOF y el
control lo hacen **por debajo de su umbral**.

## 3. Brazo control: la causa refinada de F17 queda CONFIRMADA

Manipulación diagnóstica declarada: el MISMO AE denso fs1 (idéntica arquitectura,
semilla y protocolo que la referencia), entrenado con train v1.1 **más 10 sesiones
normales de autovía que sí cruzan fronteras de cuantización** (seeds exploratorias
437–509, seleccionadas por barrido según ese criterio, nunca por su efecto en métricas).

| | AE estático fs1-S (referencia) | Brazo control |
|---|---|---|
| FPR normal | 0.129 | **0.022** |
| FPR autovía | 0.475 | **0.085** (= LOF) |
| Marcado normal post-cruce | 0.933 | **0.167** |
| F1 | 0.702 | **0.727** |
| Precisión | 0.830 | **0.966** |
| Recall held-out | 0.419 | 0.381 |

El techo que la serie EXP-ANOM-006/007/008 atribuyó sucesivamente al volumen de datos,
a la capacidad, a la regularización y a la representación de features **no era ninguna
de esas cosas: era la cobertura de normalidad de un evento discreto legítimo y raro**
(2/22 sesiones de train lo contenían). Con ese evento representado, un AE denso
—el mismo que fue rechazado tres veces— alcanza a la vez mejor F1 que LOF (0.727 vs
0.645) y menor FPR (0.022 vs 0.035).

**Caveat epistémico que impide convertirlo en decisión (y por el que se declaró brazo
control, no candidato):** el criterio de cobertura se derivó de un diagnóstico realizado
sobre la sesión de **test** (F17). El brazo demuestra el mecanismo causal, pero una
promoción a detector exige una réplica independiente, con la cobertura definida sin mirar
test. No se toca el estado de LOF (sigue SELECTED) ni se abre adopción alguna aquí.

## 4. XAI temporal (primera ejecución de la adenda F18)

Explainer: **`shap.GradientExplainer`** (expected gradients). Elección documentada y
verificada, no por conveniencia: `DeepExplainer` es incompatible con celdas LSTM/GRU
(«unrecognized nn.Module» + fallo de aditividad) y `Permutation` sobre la entrada
aplanada cuesta ~21–27 s por secuencia a 60×12; Gradient produce la matriz `[T×F]`
nativamente en ~3 s para 17 secuencias.

| Métrica (GRU-AE / LSTM-AE) | Valor | Azar |
|---|---|---|
| FAR@5 maf_drift | 0.667 / 0.778 | 0.417 |
| FAR@5 vacuum_leak | 0.500 / 0.667 | 0.417 |
| FAR@5 corr_break | 0.000 / 0.500 | 0.417 |
| FTH@10 maf_drift / vacuum | 1.000 / 1.000 | 0.250 / 0.278 |
| TAR@10 | 1.000 | **1.000** |
| Agreement con `error[t][f]` (Jaccard@10 celdas) | 0.307 / 0.301 | — |
| Estabilidad entre seeds (celdas) | 0.682 / 0.611 | — |
| Estabilidad bajo perturbación (celdas) | 0.813 / 0.722 | — |
| **Acuerdo Gradient ↔ Permutation (celdas)** | **0.255 / 0.144** | — |

Tres lecturas, dos de ellas negativas y declaradas:

1. **TAR@K es no informativa en este diseño**: los fallos inyectados cubren la secuencia
   entera, de modo que `GT_t` = todos los pasos y el azar vale 1.0. La métrica solo
   discriminará con fallos que ocupen una fracción de la ventana — limitación del
   diseño experimental, no del explicador; queda anotada para el próximo experimento.
2. **La atribución a nivel de celda aún no es fiable**: dos variantes de SHAP sobre el
   mismo modelo y las mismas secuencias coinciden en apenas 0.14–0.26 de sus Top-10
   celdas. La dimensión «qué señal» (FAR/FTH, por encima del azar) es más robusta que la
   dimensión «cuándo».
3. La señal dominante vuelve a ser **`LONG_FUEL_TRIM_1`** (atribución global 1.94 en GRU
   y 4.92 en LSTM, un orden de magnitud sobre la siguiente), coherente con §2.

## 5. Embeddings temporales (D2)

| | LSTM-AE | GRU-AE | referencia estática (F17) |
|---|---|---|---|
| Silhouette entre fallos | 0.036 | 0.127 | **0.202** |
| Silhouette por seed | 0.020 / 0.099 | 0.153 / 0.121 | — |
| Vecino más cercano del mismo fallo | **0.800** | 0.721 | — |
| PCA 2c var. explicada | 0.941 | 0.903 | — |

Silhouette **peor** que el estático, pero la consistencia de vecindario es alta (72–80 %
de los vecinos más próximos comparten tipo de fallo): el espacio latente agrupa por
mecanismo aunque no separe los grupos. Señal real pero insuficiente.

## 6. Indicaciones edge (ARM64 real sigue PENDIENTE)

| Brazo | parámetros | tamaño | inferencia | entrenamiento |
|---|---|---|---|---|
| LSTM-AE (h32/l8) | 15 284 | ~60 KB | 0.110 ms/secuencia | 19.8 s |
| GRU-AE (h32/l8) | 11 700 | ~47 KB | 0.198 ms/secuencia | 78.2 s |
| AE estático fs1-S | 4 114 | ~16 KB | — | — |

Ambos dentro del presupuesto declarado (<150k). Nada se declara validado en edge hasta
ejecutar A2/A3.

## 7. Decisiones

- **D1 (detector temporal) = REJECT.** Peor en F1, mucho peor en held-out, sin mejora en
  anomalías lentas y con falsas alarmas más largas; estable en 3 seeds y 3 longitudes.
- **D2 (embeddings temporales) = NEEDS MORE EVIDENCE.** Silhouette inferior al estático;
  la consistencia de vecindario (0.72–0.80) es prometedora pero no basta. **EXP-PAT-001
  NO se abre.**
- **D3 (XAI temporal) = NEEDS MORE EVIDENCE.** La extensión feature×time funciona, es
  estable y supera el azar en la dimensión de features, pero el desacuerdo entre
  explainers (0.14–0.26) y la no informatividad de TAR@K en este diseño impiden
  adoptarla como evidencia de nivel celda. (D3 a nivel de FEATURE sigue ADOPT desde F16.)
- **LSTM-AE vs GRU-AE = NO WINNER.** F1 0.455 vs 0.460, FPR idéntico, diferencias dentro
  del ruido entre seeds; GRU es marginalmente mejor a 30 s y LSTM converge antes.

## 8. Regla de parada (activada) — informe de causa

Ni LSTM-AE ni GRU-AE mejoran las anomalías lentas manteniendo el FPR, así que **no se
añade profundidad ni se pasa a TCN/Transformer**. Diagnóstico de causa entre las cuatro
opciones declaradas:

- **Dataset insuficiente — CAUSA DOMINANTE, demostrada.** El brazo control la prueba
  directamente: con cobertura del evento raro, el FPR cae 6× y el AE denso supera a LOF.
- **Emulador / ground truth insuficientes — CAUSA SECUNDARIA ABIERTA.** Ningún brazo
  (tampoco el control, tampoco LOF) detecta `joint_slow_drift` ni
  `load_coolant_decouple`: recall 0.000 en toda la serie. Que seis modelos con
  representaciones muy distintas coincidan en cero sugiere que la inyección de esos
  fallos puede ser indistinguible de la variabilidad normal del emulador, más que un
  fallo de los modelos. Debe examinarse la magnitud de la inyección antes de volver a
  probar arquitecturas.
- **Representación temporal insuficiente — descartada como explicación del techo**: el
  problema no era la falta de contexto temporal (lo prueba §3).

**Próximo experimento recomendado:** (a) replicar la cobertura de normalidad de forma
independiente del diagnóstico de F17 —definiendo la ampliación sin mirar test— para
convertir el hallazgo del brazo control en una decisión legítima de detector; y (b)
auditar la inyección de anomalías lentas (magnitud efectiva frente a la variabilidad
normal) antes de evaluar más arquitecturas.
