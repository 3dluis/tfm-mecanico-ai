# EXP-ANOM-008 — Ablation de esquema de features: fs2-lite vs fs1 (F17)

**Exploratorio** (Protocolo ML v1 + Adenda XAI v1; config
[`exp-anom-008.yaml`](../../../ai-models/configs/exp-anom-008.yaml); runner
`e7_fs2_ablation.py`; resultados `e7_results.json`; figuras
[`docs/fase17/figs/`](../../fase17/figs/)). **Validez: entorno emulado/sintético** —
sin HCRL ni ARM64/RPi5 (tareas dependientes registradas aparte; sin validez externa).

**Pregunta.** EXP-ANOM-007 identificó como causa raíz del FPR del AE las features
absolutas de fuel trim. ¿La corrección a nivel de representación (fs2-lite:
`LTFT_session_drift`/`total_trim_session_drift` EN SUSTITUCIÓN de los absolutos +
std multiescala + correlaciones lag-1; 48 features) corrige el FPR y mejora la
representación de anomalías lentas/relacionales sin degradar la explicabilidad?

**Respuesta: NO (con 3 seeds y causa refinada). Esquema = KEEP fs1.**

## 1. Diseño

Cambio único = esquema de features. Mismo train v1.1 (22 normales, hash en
`e7_results.json`), misma normalización (StandardScaler embebido), mismo protocolo de
umbral (cuantil 1-FPR sobre train del brazo, ADR-0011), mismas ventanas EXACTAS
(aserción en el runner: idénticos `session_ids`/`y`/`window_starts` entre esquemas; las
40 features fs1 conservadas son byte a byte idénticas — test de integración F17).
Referencia de sesión de fs2-lite = primeros 120 s de la PROPIA sesión (sin leakage
entre sesiones; streamable en el edge). LOF congelado (arms-freeze-v1: fs1, train v1.0,
umbral 0.163197) jamás re-entrenado ni reajustado. Seeds 42/43/44 en los 4 brazos AE.

## 2. Comparación principal (test, seed 42; rangos entre paréntesis = seeds 42/43/44)

| Brazo | n_feat | params | F1 | FPR normal | FPR autovía | held-out |
|---|---|---|---|---|---|---|
| fs1 + AE-S | 42 | 4 114 | 0.702 (0.691–0.702) | 0.129 (0.129–0.142) | 0.475 | 0.419 |
| fs1 + AE-M | 42 | 10 746 | 0.754 (0.751–0.763) | 0.168 (0.134–0.168) | 0.508 | 0.563 |
| fs2-lite + AE-S | 48 | 4 504 | 0.706 (0.688–0.706) | 0.134 (0.125–0.134) | 0.492 | 0.431 |
| fs2-lite + AE-M | 48 | 11 520 | 0.758 (0.708–0.758) | 0.138 (0.121–0.164) | 0.475 | 0.544 |
| **LOF congelado** | 42 | — | 0.645 | **0.035** | **0.085** | 0.250 |

Los rangos entre seeds de fs1 y fs2-lite SE SOLAPAN en F1 y FPR: no hay efecto del
esquema distinguible de la variabilidad de inicialización. El FPR de autovía queda en
0.47–0.51 en TODOS los brazos AE (LOF: 0.085). El FPR urbano sí baja a 0.00 con
fs2-lite (fs1: 0.017–0.034) — la sustitución elimina el offset inter-sesión, pero ese
no era el mecanismo dominante restante.

### Fallos foco (recall, test; instrucción F17)

| Brazo | joint_slow_drift | load_coolant_decouple | corr_break_rpm_maf |
|---|---|---|---|
| fs1 + AE-S/M (3 seeds) | 0.000–0.175 | 0.000–0.100 | 0.80–1.00 |
| fs2-lite + AE-S/M (3 seeds) | 0.000–0.075 | 0.000–0.150 | 0.76–1.00 |
| LOF congelado | 0.000 | 0.000 | 0.50 |

**fs2-lite NO mejora las anomalías lentas/relacionales**: joint_slow_drift y
load_coolant_decouple siguen prácticamente indetectados en todos los brazos. El barrido
de severidad (suite F14, solo evaluación) es casi idéntico entre esquemas
(corrbreak-high 0.83 fs2 vs 0.73 fs1; resto ±0.03) y muy superior a LOF en
corr_break/misfire, como en F14.

## 3. Causa refinada del FPR (diagnóstico sobre datos + SHAP convergentes, otra vez)

Las explicaciones SHAP de los FP del brazo fs2-lite señalan… **la propia
`LTFT_session_drift`** (dominante en 5/6 FP explicados; mean |SHAP| global 25.2, la
mayor del esquema). El diagnóstico sobre los datos lo confirma y lo precisa:

- El LTFT emulado está **cuantizado J1979** (`quantize_tick`, paso 100/128 = 0.7812 %).
- En el normal de autovía de test (1800 s), el LTFT subyacente cruza una frontera de
  cuantización en t≈920 s y **oscila entre dos cuantos adyacentes** (0.0 ↔ 0.7812)
  el resto de la sesión: las ventanas posteriores tienen deriva/std/slope de LTFT
  legítimas pero nunca vistas.
- En el train v1.1 solo **2/22 sesiones** cruzan alguna frontera (std de
  `LTFT_session_drift` en train = 0.076; p99 |drift| = 0.43): TODA feature derivada de
  LTFT — absoluta O relativa a la sesión — hereda varianza casi nula en train, y el
  error estandarizado se dispara ante el evento legítimo.

Conclusión: la patología de EXP-ANOM-007 no era (solo) el offset absoluto entre
sesiones, sino la **rareza en train del evento discreto de adaptación del trim** — un
fenómeno de contexto TEMPORAL que ninguna representación estática de ventana corrige:
la ventana no puede distinguir «paso de cuantización legítimo tras 15 min de autovía»
de «deriva inducida por fallo» sin contexto de la trayectoria. LOF sobre las MISMAS
features fs1 tolera el mismo evento (FPR autovía 0.085): la densidad local con k=10 es
menos sensible a una dirección rara que el error de reconstrucción del AE.

**Caveat de dominio sintético (declarado, no ocultado):** la oscilación entre cuantos
es un artefacto plausible del emulador (señal continua + ruido pequeño alrededor de una
frontera); en un vehículo real el ECU también publica LTFT cuantizado y adaptándose
lentamente, pero el patrón exacto de oscilación puede diferir. Se re-examinará con HCRL
(tarea dependiente). No se regeneraron sesiones para hacer desaparecer el hallazgo
(regla §29).

## 4. XAI comparado (parte de la decisión; finalistas fs2-lite+AE-S vs fs1+AE-S)

| Métrica | fs2-lite+AE-S | fs1+AE-S |
|---|---|---|
| AR@1/3/5 vacuum_leak (azar@5) | 1.0/1.0/1.0 (0.40) | 1.0/1.0/0.93 (0.38) |
| AR@1/3/5 maf_drift (azar@5) | 1.0/1.0/0.80 (0.33) | 1.0/1.0/0.87 (0.29) |
| AR@1/3/5 corr_break (azar@5) | 1.0/0.33/0.33 (0.29) | 0.67/0.56/0.60 (0.24) |
| Agreement J5 (clases A/P/D) | 0.527 (7/8/2) | 0.453 (6/9/2) |
| Estabilidad entre seeds (J5) | 0.635 | 0.556 |
| Estabilidad bajo perturbación (J5) | **0.627** | **0.833** |
| Sonda fingerprint (cos perfiles) | 0.050 | 0.037 |

Fidelidad ≫ azar donde hay detección en ambos esquemas; agreement y estabilidad entre
seeds ligeramente mejores en fs2-lite, pero la **estabilidad bajo perturbación cae de
0.83 a 0.63** (las nuevas features de deriva concentran atribución y son sensibles al
ruido) — por el criterio F17 («sin promoción automática si las explicaciones son
inestables»), esto por sí solo bloquearía la promoción aunque las métricas de detección
hubieran mejorado. Features dominantes inesperadas: ninguna fuera del mecanismo
diagnosticado (familia LTFT). Sonda fingerprint ≈ F16: el perfil de atribución en
normales sigue dependiendo del escenario — coherente con la patología de trims;
comparación intra-simulador, sin valor externo. (Runtimes SHAP: 7.9 s el primer brazo,
0.3 s el segundo — la diferencia es calentamiento de shap/numba, no del esquema.)

## 5. Embeddings (D2)

Silhouette entre fallos: AE-M 0.193 (fs2) vs 0.202 (fs1); AE-S 0.119 (fs2) vs 0.106
(fs1). PCA-2c 0.92–0.97. **Sin mejora de representación**: el espacio sigue
contaminado por el mismo mecanismo.

## 6. Decisiones

- **Esquema de features = KEEP fs1.** fs2-lite no corrige el FPR (rangos solapados, 3
  seeds), no mejora los fallos lentos/relacionales ni D2, y degrada la estabilidad de
  explicación bajo perturbación. El F1 marginalmente superior (0.758 vs 0.754) no
  justifica promoción (criterio F17). fs2-lite queda como esquema experimental
  documentado en `ai-models` (extracción + schema + GT), NO se promueve a contrato.
- **D1 (detector) = REJECT** (tercera vez): ningún brazo AE se acerca al FPR de LOF.
- **D2 (representación) = NEEDS MORE EVIDENCE**: sin cambios (AE-M ~0.20); EXP-PAT-001
  NO se abre.
- **D3 (XAI) = ADOPT confirmado**: SHAP volvió a localizar el mecanismo de los FP de
  forma independiente al diagnóstico (tercer caso de valor demostrado), con coste
  trivial.
- **Siguiente (directiva F17):** EXP-ANOM-009 — modelos temporales (LSTM-AE/GRU-AE,
  HX-ML-3): el evento de adaptación cuantizada y los drifts lentos no detectados son
  ambos problemas de contexto temporal. Alternativa documentada NO elegida (y por qué):
  cobertura dirigida de normalidad con cruces de cuantización en train — repetiría la
  estrategia F9 (ampliar normalidad) ya refutada para el AE en EXP-ANOM-007 y
  maquillaría el síntoma sin resolver la limitación representacional.
