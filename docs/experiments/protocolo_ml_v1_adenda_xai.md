# Adenda XAI v1 al Protocolo Experimental ML v1 (F15)

**Estado: VIGENTE para trabajo EXPLORATORIO · 2026-08-13 · extiende
[protocolo_ml_v1.md](protocolo_ml_v1.md) §13 sin sustituirlo · no modifica pre-registros
ni resultados ya obtenidos**

Esta adenda incorpora Explainable AI (XAI) como **dimensión transversal de evaluación**
del ciclo experimental: datos → entrenamiento → validación → evaluación → selección →
detección → descubrimiento → explicación → agente+RAG+memoria. La pregunta de
investigación NO cambia; XAI es uno de los mecanismos que **operacionaliza** la mitad
«explicar» de la PI, y añade una pregunta de evaluación a cada experimento: no solo
*¿el modelo detecta?*, sino *¿qué comportamiento aprendió para detectar?* y *¿esa
explicación es coherente, estable y compatible con la evidencia conocida?*

## 1. Principio canónico: dos capas y tres niveles que no se confunden

La distinción ya establecida por el Estado del Arte (capítulo 2: capa (a) = explicar la
decisión matemática del modelo; capa (b) = explicar la posible causa mecánica) se eleva
a regla operativa de toda la línea ML:

```text
Modelo ML
   ↓ prediction / anomaly_score / reconstruction_error
XAI                                  ← capa (a): SHAP, per-feature error…
   ↓ evidencia explicativa
contexto longitudinal + eventos similares + RAG + documentación técnica
   ↓
agente / LLM                         ← capa (b): hipótesis mecánica
   ↓
hipótesis explicada → validación
```

**Regla vinculante** (coherente con D10 de afirmaciones de novedad y con la cadena
epistemológica del protocolo §10):

```text
XAI attribution  ≠  mechanical causality  ≠  confirmed diagnosis
```

SHAP explica el comportamiento del modelo; no demuestra por sí solo la causa mecánica de
una avería. Ningún artefacto de esta adenda produce diagnósticos: produce **evidencia
estructurada e inspeccionable**.

## 2. Nomenclatura: XAI como dimensión, no como serie nueva

**Decisión:** XAI se evalúa DENTRO de los experimentos existentes (`EXP-ANOM-*`,
`EXP-PAT-*`) como subobjetivo formal con decisión propia (ver §12), y NO se crea la
serie `EXP-XAI-*`. Justificación: (1) una atribución solo tiene sentido respecto a un
modelo, un dataset y un split concretos — separarla duplicaría configs, registros y
clasificaciones sin añadir contenido; (2) la nomenclatura EXP-<FAMILIA> del pre-registro
mapea familias de hipótesis científicas (H-*), y XAI es una dimensión de evaluación
(como el presupuesto edge), no una familia de detección; (3) las hipótesis exploratorias
XAI (HX-XAI-*, §11) siguen el mismo mecanismo que HX-ML-* sin tocar nada congelado.
Puerta abierta declarada: si en el futuro un experimento tuviera por objeto los MÉTODOS
de explicación en sí (p. ej. comparar familias de explainers), ESE experimento sí
justificaría `EXP-XAI-001`; hoy generaría duplicidad documental.

## 3. SHAP dentro del ciclo de entrenamiento

SHAP actúa como **instrumento de diagnóstico del modelo** durante el proceso
experimental:

```text
dataset → train → validation → SHAP analysis → model/feature diagnosis
       → scientific decision → retrain only when justified
```

Prohibiciones explícitas: SHAP NO es función de pérdida, NO es criterio que el
optimizador maximice, NO se usa para ajustar umbrales ni hiperparámetros mirando test
(las explicaciones sobre test se calculan DESPUÉS de congelar el modelo del experimento,
como el resto de métricas de test). Un re-entrenamiento motivado por hallazgos SHAP es
una decisión experimental registrada (nueva versión/brazo), nunca un ajuste silencioso.

## 4. Dos niveles de explicación (comparables entre modelos)

| Nivel | Mecanismo | Modelos |
|---|---|---|
| **Específico del modelo** | per-feature reconstruction error (`AutoencoderDetector.per_feature_error`, ya implementado) · comportamiento de vecindario/distancias cuando aplique (LOF) · z por feature contra baseline contextual (event-baseline) · `involved_pids` (docs/models/02 §5) | propio de cada familia |
| **Común (XAI)** | **SHAP** sobre una función explícita del detector | todos los detectores tabulares |

Para detectores sin clasificación convencional (AE, LOF, OC-SVM) SHAP explica una
función declarada por experimento: `f(x) = reconstruction_error(x)` o
`f(x) = anomaly_score(x)`. La pregunta es siempre: *¿qué variables contribuyeron a que
el score aumentara?* SHAP es **complementario** del mecanismo específico, nunca su
sustituto; el desacuerdo entre ambos es objeto de estudio (§9), no error automático.

## 5. Explicación local y contrato de evidencia

Se generan explicaciones a nivel de `window`, `event`, `anomaly` y, en el futuro,
`pattern occurrence`. Contrato conceptual del artefacto (por ahora JSON experimental en
`ai-models/experiments/`, ver §15 para su futuro como contrato):

```text
event_id · window_id · model_id · model_version · anomaly_score · feature_values
shap_values · reconstruction_error (por feature, si AE) · top_features
reference_baseline (método + hash del background)
```

Este objeto extiende el contrato de salida hacia agentes del protocolo §12: el LLM no
recibe solo `anomaly_score`, recibe el paquete de evidencia completo. **Regla del
agente** (refuerza ADR-0009 y el nodo `verify` de la arquitectura C6): el agente no
puede transformar «SHAP señala MAF» en «fallo del sensor MAF confirmado»; debe
expresarlo como evidencia/hipótesis («la desviación fue atribuida principalmente a MAF,
STFT y MAP; en combinación con el historial y la documentación recuperada, este
comportamiento es compatible con…»).

## 6. Explicación global

Agregados `mean(|SHAP|)` y rankings de importancia desglosados por: modelo · tipo de
anomalía · severidad · escenario operacional (perfil de conducción) · tamaño de ventana.
Regla: una importancia global NO representa todos los escenarios — todo ranking global
se acompaña de al menos un desglose por tipo de anomalía antes de usarse en decisiones.

## 7. Ground truth sintético de explicabilidad

La inyección controlada ya conserva lo necesario (`ScenarioSpec`: fault, fault_params,
fault_start/end_s, category; catálogo con `expected_signature`). Se formaliza el mapeo
**fallo → conjunto de features esperadas** (ground truth de atribución, derivado de las
transformaciones reales del catálogo `obd_lab.injection.faults`):

| Fallo | Features fs1 esperadas (conjunto GT) |
|---|---|
| vacuum_leak | STFT_1, LTFT_1, INTAKE_PRESSURE, total_trim (+RPM en ralentí) |
| maf_drift | MAF, STFT_1, LTFT_1, total_trim |
| thermostat_stuck | COOLANT_TEMP |
| o2_lag | O2_B1S1, STFT_1 |
| misfire | RPM, ENGINE_LOAD, O2_B1S1 |
| corr_break_rpm_maf | {corr_RPM_MAF, corr_ENGINE_LOAD_MAF, MAF, RPM} — conjunto relacional |
| load_coolant_decouple | {COOLANT_TEMP_std, corr_ENGINE_LOAD_COOLANT_TEMP} |
| joint_slow_drift | {MAF, TIMING_ADVANCE} + derivadas |

Para anomalías multivariables (correlation break, divergencia, compuestas) NO se exige
una sola feature dominante: el GT es un conjunto y las métricas se evalúan contra el
conjunto (una atribución repartida entre las features relacionadas es la explicación
CORRECTA). El mapeo exacto por experimento se congela en su config antes de calcular
métricas.

## 8. Métricas XAI

Familia nueva `XAI Metrics` (se añade a las familias del protocolo §9):

- **Attribution Recall@K** (K ∈ {1,3,5}): sea `GT` el conjunto de features esperadas y
  `Top-K` las K features con mayor |atribución| para una ventana/evento anómalo:
  `AR@K = |GT ∩ Top-K| / min(|GT|, K)`. Ejemplo: GT={MAF, STFT}, Top-3={STFT, MAF, MAP}
  → AR@3 = 2/2 = 1.0. Se reporta agregada por tipo de anomalía y severidad, junto a un
  **baseline aleatorio** (esperanza de AR@K eligiendo K features al azar de las 42) —
  sin ese baseline el número no es interpretable (HX-XAI-1).
- **Attribution Precision@K** = `|GT ∩ Top-K| / K` — se adopta SOLO para GT con
  |GT| ≥ K (en GT pequeños penaliza artificialmente); decisión por experimento,
  registrada. No se adoptan más métricas por acumulación.
- **Agreement entre métodos** (§9): Jaccard@K y correlación de rango (Spearman) entre
  el ranking SHAP y el ranking del mecanismo específico del modelo; clasificación
  cualitativa `AGREE` (Jaccard@5 ≥ 0.6) · `PARTIAL_AGREEMENT` (0.2–0.6) ·
  `DISAGREE` (< 0.2) — cortes iniciales exploratorios, revisables con evidencia.
- **Explanation stability** (§10): Jaccard@K medio entre Top-K de `x` y de
  `x + ε` (perturbación pequeña que no cambia materialmente el score, p. ej. ruido
  gaussiano σ = 0.05·std por feature sobre entrada estandarizada, semilla fija) y
  entre Top-K de runs con seeds distintas.

## 9. Agreement per-feature-error ↔ SHAP

Se evalúa formalmente el acuerdo entre el mecanismo propio del AE y SHAP sobre las
mismas ventanas. La discrepancia NO se trata automáticamente como error: puede señalar
efectos de correlación (§13), interacciones que el error por feature no captura, o
problemas del explainer — se investiga y se documenta caso a caso (evidencia negativa
incluida).

## 10. Estabilidad

Dos dimensiones obligatorias en todo experimento que reporte XAI:

1. **Ante perturbaciones**: explicaciones de `x` vs `x+ε` (§8) — detecta explicaciones
   frágiles con comportamiento equivalente.
2. **Entre seeds**: SHAP Top-K de runs equivalentes (mismo protocolo, seed distinta) —
   detecta modelos con rendimiento similar pero explicaciones drásticamente distintas.
   Esta comparación es **dimensión de selección de modelos** (§14): un modelo con F1
   superior pero explicaciones inestables o incoherentes con el GT puede NO promoverse
   (evidencia negativa legítima del protocolo §11).

## 11. Hipótesis exploratorias XAI (mismo régimen que HX-ML-*; NO confirmatorias)

| ID | Hipótesis | Verificación | Refutación honesta |
|---|---|---|---|
| HX-XAI-1 | Las principales atribuciones coinciden con las variables alteradas en las anomalías sintéticas controladas por encima del baseline aleatorio | AR@K vs esperanza aleatoria, por tipo y severidad | AR@K ≈ azar → el modelo detecta sin aprender el mecanismo inyectado (hallazgo relevante) |
| HX-XAI-2 | Las explicaciones son razonablemente estables entre seeds para modelos de rendimiento equivalente | Jaccard@5 entre seeds | inestabilidad alta → la explicación no es propiedad del problema sino del run |
| HX-XAI-3 | Las anomalías multivariables muestran atribución distribuida entre las variables relacionadas (no una dominante espuria) | masa de atribución sobre el conjunto GT relacional | concentración en una variable ajena al GT → sospecha de proxy/fingerprint (§13) |

## 12. Decisiones independientes por experimento (retro-aplicado a EXP-ANOM-006)

Todo experimento de la línea con componente de representación/explicación separa tres
decisiones independientes (puede ser coherente rechazar una y promover otra):

```text
D1 — detector          → ADOPT | REJECT | INCONCLUSIVE
D2 — representación    → PROMOTE TO EXP-PAT | REJECT | NEEDS MORE EVIDENCE
D3 — mecanismo XAI     → ADOPT | REJECT | NEEDS MORE EVIDENCE
```

**Estado de EXP-ANOM-006 bajo este esquema** (sin alterar resultados obtenidos; los
JSON del registro quedan intactos): **D1 = REJECT** en su forma actual (FPR 3× LOF;
condición ADR-0011 no cumplida; vía de mejora EXP-ANOM-007) · **D2 = NEEDS MORE
EVIDENCE** (silhouette entre mecanismos 0.118: insuficiente para promover a EXP-PAT) ·
**D3 = NEEDS MORE EVIDENCE** (SHAP no se ejecutó en E5; el per-feature reconstruction
error está implementado pero su evaluación formal como explicación — AR@K, estabilidad,
agreement — queda especificada aquí y se ejecuta a partir de EXP-ANOM-007).

## 13. Auditorías y riesgos que SHAP debe vigilar

- **Leakage**: `session_id`, `trip_id`, `scenario_id`, `anomaly_type`, `generation_seed`,
  `split` y cualquier etiqueta NO pueden formar parte del vector de features (fs1 no los
  contiene; el test de igualdad con el contrato lo garantiza). Si una variable proxy o
  un metadato inesperado domina las explicaciones, se investiga leakage y se registra.
- **Synthetic-domain bias / huella del generador**: riesgo de que el modelo aprenda la
  firma del `SignalEngine` en vez de comportamiento vehicular. Vigilancia: comparar
  atribuciones entre seeds distintas, configuraciones/escenarios distintos y — cuando
  exista replay real (HCRL/X-CANIDS/AEGIS) — entre sintético puro e inyección sobre
  baseline real/emulado. Diferencias sistemáticas de atribución sin cambio de mecanismo
  = señal de fingerprint; se documenta como limitación del entorno emulado.
- **Correlación entre variables OBD-II** (limitación explícita): RPM, MAF, MAP, TPS,
  ENGINE_LOAD, STFT, LTFT están correlacionadas física y estadísticamente; SHAP puede
  repartir atribución entre correlacionadas. Por tanto: atribución baja ≠ feature
  irrelevante; atribución alta ≠ variable causal. Ninguna feature se elimina
  automáticamente por SHAP global bajo (§14).
- **Sobreinterpretación**: mitigada por la regla de capas (§1), el criterio de 8
  condiciones del protocolo §10 y la regla del agente (§5).

## 14. XAI en selección de features y de modelos

**Features (fs1 vs fs2-draft):** SHAP entra en la comparación, pero retirar una feature
exige considerar: importancia global · importancia por anomalía · importancia por
escenario · relevancia mecánica · relevancia longitudinal · estabilidad · correlación
con otras variables. Toda eliminación es una decisión experimental registrada.

**Modelos — la función multicriterio de docs/models/14 §1 se extiende:**

```text
Detection Performance + Explainability + Explanation Stability
+ Representation Quality + Edge Feasibility
```

**Decision gate** (docs/models/14; las preguntas 3–6 son las nuevas):

1. ¿Detecta adecuadamente? 2. ¿Mantiene el FPR permitido? 3. ¿Las variables atribuidas
son coherentes con el ground truth cuando existe? 4. ¿Las explicaciones son estables
(perturbación y seeds)? 5. ¿Hay señales de leakage? 6. ¿Hay señales de
synthetic-domain bias? 7. ¿Mantiene viabilidad edge?

La evidencia negativa aplica: «el modelo detecta bien pero sus atribuciones son
inestables y no coinciden con lo inyectado» es motivo legítimo de no-promoción aunque
su F1 sea superior.

## 15. Metodología SHAP (implementación)

- **Explainer**: no se fija KernelExplainer por defecto; se elige por tipo de modelo,
  versión de SHAP, coste computacional y framework soportado (p. ej. explainers
  agnósticos con background para AE/LOF; el explainer exacto es parte del registro).
- **Registro por experimento** (runs.jsonl/config): `shap_version · explainer_type ·
  background_method · background_size · background_hash · explained_output`
  (reconstruction_error | anomaly_score) `· samples_explained · runtime · hardware`.
- **Background**: EXCLUSIVAMENTE de particiones permitidas — preferencia: muestras
  normales de train; JAMÁS de test. Selección determinista (semilla) y hasheada.
- **Sampling**: SHAP no se calcula sobre todo; muestreo estratificado reproducible por
  {normal, TP, FP, FN} × tipo de anomalía × severidad × escenario, con tamaños
  declarados en la config del experimento.
- **Edge**: la inferencia edge sigue produciendo solo score / reconstruction error /
  embedding; el análisis XAI completo es offline (equipo de desarrollo / evaluación).
  Explicaciones ligeras en edge (p. ej. per-feature error, que es gratis) = trabajo
  futuro declarado; SHAP en RPi NO es requisito.
- **Dimensión temporal**: mientras los detectores sean tabulares (fs1), la atribución es
  por feature; cuando entren modelos secuenciales (EXP-ANOM-00x de nivel 3), la
  arquitectura debe conservar atribución `feature × tiempo` (qué variable y en qué
  momento) — contemplado en roadmap, no obligatorio implementarlo ya. El puente actual
  es la trazabilidad ventana→snapshots (`window_id → seq_start..seq_end`), que ya
  permite localizar el CUÁNDO a nivel de ventana.

## 16. Persistencia (diseño futuro, sin tablas prematuras)

Mientras el consumidor sea el proceso experimental, los artefactos XAI viven en
`ai-models/experiments/` (JSON versionados por git). Cuando el runtime agéntico consuma
explicaciones en vivo, se promoverán a contratos (cambio aditivo + ADR):

```text
ModelExplanation:  explanation_id · event_id · window_id · model_id · method
                   · explainer_version · background_hash · created_at
FeatureAttribution: explanation_id · feature · value · attribution · rank
```

El primer paso será el modelo conceptual (data-architecture), después el físico (regla
de contratos aditivos + Alembic). `DetectedAnomaly.features` + `involved_pids` ya cubren
la necesidad inmediata del runtime.

## 17. Estado del Arte y bibliografía

El EdA (capítulo 2, pendiente de commit por el autor) YA cubre XAI con la distinción
capa (a)/(b) y referencias verificadas: SHAP/LIME sobre clasificadores de fallos
(Brusa 2023; Haque 2025; Khemani & Qureshi 2026; Lu 2025), narrativa fiel de
atribuciones (Explingo, Zytek 2024), hipótesis causales LLM desde atribuciones
(FaultExplainer, Khan 2024; PI-Dual-STGCN, Zhao 2026), validación por consistencia
(Mohammadi 2025) y explicación contrafactual para AE de series temporales
(Srinivasan 2024). Esta adenda NO añade citas nuevas ni modifica el paquete EdA sin
commit; si la redacción de la memoria necesita ampliar la subsección XAI, se hará por
el mecanismo bibliográfico establecido (fichas + verificación), nunca inventando
referencias.

## 18. Validez de la explicación (marco metodológico)

El diseño experimental evalúa tres validez complementarias:

```text
Detection validity      ¿detecta lo que debe con el FPR permitido? (ADR-0011)
Representation validity ¿el espacio aprendido separa mecanismos? (silhouette, EXP-PAT)
Explanation validity    ¿la atribución es fiel al ground truth conocido, estable y
                        consistente entre métodos?  ← ESTA ADENDA
```

**Explanation validity NO es causalidad**: mide la relación entre la atribución del
modelo y el mecanismo de inyección conocido en el entorno controlado, más su
estabilidad. La validez causal mecánica pertenece a la capa (b) y al protocolo de
validación de hipótesis (H-EXP/H-MAIN), fuera del alcance de esta adenda.

## 19. Registro de riesgos (adición F15)

| Riesgo | Mitigación |
|---|---|
| XAI instability (explicaciones frágiles) | métricas de estabilidad obligatorias (§10); no promover sin ellas |
| SHAP computational cost | sampling estratificado reproducible + registro de runtime; XAI offline, nunca en el camino edge |
| correlated-feature attribution ambiguity | regla §13; interpretación por conjuntos GT; agreement entre métodos |
| synthetic-domain bias | vigilancia §13; contraste con replay real cuando exista; limitación declarada |
| explanation overinterpretation | regla de capas §1 + regla del agente §5 + criterio 8 condiciones |
| temporal attribution complexity | alcance acotado: feature-level ahora, feature×tiempo en roadmap (nivel 3) — **realizado en F18**: [adenda temporal](protocolo_ml_v1_adenda_xai_temporal.md), congelada antes de EXP-ANOM-009 |

(El fichero docs/04_riesgos.md está en el paquete evictado pendiente de verificación
del autor; esta tabla se integrará allí cuando ese paquete se commitee — nota en el
informe de fase.)
