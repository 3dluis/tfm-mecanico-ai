# Protocolo Experimental de Machine Learning v1 (F13)

**Estado: VIGENTE para trabajo EXPLORATORIO · 2026-08-13 · clasificación según regla F10**

Este protocolo gobierna la línea experimental de **entrenamiento y evaluación de modelos
de IA sobre series temporales OBD-II** abierta en F13 por decisión del autor. Es el marco
común de los experimentos exploratorios de detección, representación y descubrimiento de
patrones; **no es un pre-registro**: la evidencia confirmatoria sigue gobernada por
`docs/experiments/preregistered/PROTO-CONF-001.md` y `docs/experiments/pre-registro-v1.md`
(rc1, pendiente de reconciliación y congelación por el autor — ver §14). Nada de lo que
este protocolo habilita toca semillas reservadas, brazos congelados ni splits held-out.

Relación con la investigación: la PI (Opción B) pregunta si un sistema inteligente híbrido
puede **descubrir y explicar** patrones de fallo vehicular previamente no documentados
mediante análisis contextual y **longitudinal** de datos OBD-II. Esta línea aporta la mitad
del *descubrir*: modelos que aprenden el comportamiento del vehículo y señalan desviaciones.
La contextualización, hipótesis y explicación (RAG, memoria, agentes, LLM) se estudian por
separado y consumen las salidas de esta línea (§12). La separación es vinculante (ADR-0009):
la detección es siempre matemática; el LLM razona sobre anomalías ya detectadas, jamás al
revés.

```text
Machine Learning / Deep Learning        ← esta línea (F13+)
        ↓  anomaly_score · embedding · candidate_pattern
memoria + contexto + RAG                ← líneas H-MEM / R3
        ↓
agentes / LLM                           ← líneas H-MAS / H-EXP
        ↓
explicación e hipótesis                 ← H-MAIN (confirmatorio, se ejecuta el último)
```

---

## 1. Hipótesis experimentales (exploratorias)

Cada hipótesis es verificable, tiene criterio de refutación y NO se confunde con las
familias confirmatorias H-* (pre-registro), a las que alimenta como evidencia de diseño.
Nomenclatura: **HX-ML-n** (hipótesis exploratoria de la línea ML).

| ID | Hipótesis | Verificación | Refutación honesta |
|---|---|---|---|
| HX-ML-1 | Las relaciones multivariables del estado wide permiten separar operación normal de estados anómalos mejor que umbrales univariantes | comparación contra `robust_zscore` (ya establecida en EXP-ANOM-001: LOF F1 0.64 vs 0.44) | los detectores multivariables no superan al z-score univariante |
| HX-ML-2 | Un autoencoder multivariable pequeño iguala o supera a LOF en held-out con FPR ≤ LOF (condición de adopción de ADR-0011) | EXP-ANOM-006: reconstruction error vs LOF con protocolo ADR-0011 idéntico | el AE no supera a LOF → LOF permanece; resultado negativo se publica con card |
| HX-ML-3 | Representaciones secuenciales (ventana [t-n..t] con orden temporal) detectan las derivas lentas que el techo actual no captura (`t-coolfreeze`, `t-jointdrift`: 0/brazos en E2/E3) | EXP-ANOM-007: LSTM/GRU-AE vs AE denso sobre las mismas ventanas | las derivas conjuntas siguen indetectadas → límite declarado del enfoque |
| HX-ML-4 | Los embeddings latentes de ventanas anómalas agrupan ocurrencias del mismo mecanismo de fallo (separabilidad por clase de inyección, que el modelo nunca ve) | EXP-PAT-001: clustering sobre embeddings; pureza respecto a provenance de inyección | los clusters no se corresponden con mecanismos → los embeddings no representan comportamiento |
| HX-ML-5 | Los patrones agrupados son estables: ocurrencias nuevas del mismo mecanismo caen en el mismo cluster con semillas y sesiones distintas | EXP-PAT-002: estabilidad inter-sesión e inter-semilla | asignación inestable → no hay patrón, solo ruido agrupado |
| HX-ML-6 | La inferencia completa del pipeline (ventana → features/AE → score) cabe en el presupuesto edge (detección ≤ 5 s por sesión de 30 min; RSS incremental ≤ 512 MB) | medición en sandbox-x86 y, cuando A2/A3 se ejecuten, en ARM64/RPi5 real | el modelo que gane en calidad pero viole el presupuesto se reporta como no viable |

**Distinción epistemológica vinculante** (ya canónica: `capitulo2_estado_del_arte.md` §def,
afirmación D10): *anomalía estadística* ≠ *patrón desconocido* ≠ *fallo mecánico
confirmado*. Ningún resultado de esta línea se enuncia como "fallo" — la gradación es:
outlier → anomalía contextual → patrón candidato → patrón no documentado validado (§11).

## 2. Unidad experimental

- **Unidad mínima de observación:** `estado_vehiculo(t)` = `VehicleTelemetrySnapshot`
  (representación NORMALIZED WIDE / TIME-ALIGNED, ADR-0025), alineado por `sync:v1`
  (ADR-0026) con NULL ≠ 0 (ADR-0027). **Validado como entrada canónica de ML por
  EXP-ANOM-005** (paridad exacta con el camino long de F3).
- **Unidad de aprendizaje:** `ventana(t-n..t)` sobre la matriz columnar
  (`ai_models.data.snapshot_matrix`). Para modelos tabulares la ventana colapsa a
  features fs1; para modelos secuenciales (nivel 3) la ventana conserva el orden temporal.
- **Unidad de agrupación para splits:** la **sesión** (secuencia de conducción completa).
  Ninguna ventana cruza sesiones (test `test_ventanas_no_cruzan_sesiones`).

**Ventanas temporales como hiperparámetro.** El tamaño 60 s / stride 30 s queda congelado
para todo lo comparable con fs1/arms-freeze-v1. Para experimentos nuevos, la rejilla
inicial de búsqueda es {10, 30, 60, 120} s con stride = size/2, a 1 Hz (única frecuencia
validada; 5 Hz sigue siendo candidato sin fijar, ADR-0026). Estos valores son puntos de
partida del barrido, no constantes del sistema; cada experimento registra los suyos.

**Calidad de datos por ventana** (política heredada de ADR-0026/0027, aplicada en
`snapshot_matrix.iter_windows`):

- señal ausente = NaN (nunca 0) + máscara de validez explícita;
- ventana con fracción válida < umbral (por defecto 1.0) se **descarta y se contabiliza**,
  no se imputa; la imputación, si un experimento la necesita, se decide y versiona en la
  fase de features (nunca en almacenamiento ni en la matriz);
- valores imposibles: rangos físicos de `diagnostic_agent.telemetry.windows` (`_RANGES`);
  la cuantización J1979 del emulador ya acota los valores del simulador;
- pérdida de conexión OBD / muestras desalineadas: `sync:v1` las convierte en
  `stale`/`missing` de forma determinista y auditable por `quality_flags`;
- rejillas mixtas prohibidas: `matrix_from_snapshots` rechaza mezclar
  `synchronization_version` o `interval_ms` distintos;
- timestamps: rejilla anclada al inicio de sesión (`timestamp_utc` + `sequence_number`);
  el emulador usa época simulada fija (2026-01-01) para reproducibilidad byte a byte.

## 3. Dataset y separación experimental

**Esquema de datos.** No se introduce un contrato nuevo: el esquema pedido por la fase se
cubre con los contratos vigentes (fuente de verdad: `shared/mecanico_contracts`):

| Concepto | Contrato/campo canónico |
|---|---|
| vehicle_id / session_id / trip_id | `VehicleTelemetrySnapshot.vehicle_id/session_id/trip_id` |
| timestamp | `timestamp_utc` + `sequence_number` (rejilla sync:v1) |
| operating_state / evento | `primary_event_type` + `SnapshotEventLink` (N:M, taxonomía v1) |
| variables OBD | 12 campos de señal del snapshot (mapeo `PID_TO_SNAPSHOT_FIELD`) |
| derived_features | `FeatureVector` (fs1) / futuro fs2 — nunca dentro del snapshot (ADR-0025) |
| labels si existen | `ScenarioSpec.category/fault/fault_start_s/fault_end_s` (ground truth del simulador) |
| anomaly_source (provenance) | `ScenarioSpec` + `RecordedSession.origin` (§8) |
| experiment_version | `ModelExperiment.dataset_version/split_version` + `runs.jsonl` |

**Separación train/validation/test.** Estrategia principal del TFM: **split por sesión con
composición fija por escenario** (la vigente desde suite-v1-split-1):

- train: solo sesiones normales (los detectores aprenden normalidad; ADR-0011);
- validation: normales de control de FP + fallos conocidos (selección de modelos/umbrales);
- test: normales + fallos conocidos con semillas nuevas + **held-out intocable** (RI1).

Justificación frente a alternativas: un split aleatorio por ventana filtra información
entre ventanas solapadas de la misma sesión (leakage directo, prohibido); el split por
viaje es equivalente al de sesión en el entorno emulado actual (1 sesión = 1 viaje); el
split temporal intra-sesión rompe la unidad de fallo (los fallos se inyectan a mitad de
sesión); el split por vehículo queda **condicionado a D2** (perfiles multi-vehículo de
obd-lab v2, pre-registro §D2) y pertenece a la línea H-PERS. Se adopta sesión como unidad
porque es el nivel más fino que garantiza independencia entre splits.

**Prevención de leakage (obligatoria, con tests automáticos):**

1. ninguna ventana cruza sesiones (`test_ventanas_no_cruzan_sesiones`);
2. ningún `scenario_id` ni `seed` aparece en dos splits (`test_splits_suite_v1_sin_leakage`);
3. clases held-out solo en test (`test_held_out_solo_en_test` + validación del loader RI1);
4. scalers/umbrales se ajustan SOLO con train (ADR-0011; el StandardScaler viaja embebido
   en el Pipeline/ONNX, lo que garantiza igualdad exacta entrenamiento↔inferencia edge);
5. ventanas solapadas de una misma sesión jamás se reparten entre train y test;
6. semillas de test siempre distintas de las de train/validation incluso para la misma
   clase de fallo (patrón v1: vacuum_leak 211 en val, 321 en test).

**Presupuesto de semillas.** Los bloques reservados por el pre-registro (901–925,
11000–20036, 30000–30079, 55000, 111000+/211000+/311000+) son **intocables** para esta
línea. El trabajo exploratorio F13+ usa el rango libre **401–599** (registrado aquí para
que ningún experimento futuro lo pise): 401–411 ya gastadas en tests de integración.

## 4. Feature engineering

**Nivel A — señales originales.** Las 12 señales canónicas del proyecto (docs/03 §3.1,
`CANONICAL_PIDS`): RPM, SPEED, ENGINE_LOAD, COOLANT_TEMP, INTAKE_TEMP, MAF, THROTTLE_POS,
STFT_1, LTFT_1, O2_B1S1, TIMING_ADVANCE, INTAKE_PRESSURE. No se asume ningún PID adicional
(battery_voltage, fuel_pressure… existen en el snapshot pero están fuera del ciclo de
sondeo actual → None+not_polled; un modelo solo puede consumirlos cuando la adquisición
los incorpore mediante cambio aditivo del mapeo).

**Nivel B — derivadas.** El esquema vigente es **fs1** (42 features: mean/std/slope × 12
PIDs + 5 correlaciones de Pearson + total_trim_mean), congelado en arms-freeze-v1. El
inventario formal versionado vive en `ai_models.features.schema` (nombre, PIDs origen,
unidad, tipo, raw/derivada, normalización), verificado por test contra el contrato.

**fs2 (borrador, sin implementación de extracción).** Solo entran candidatas con
justificación mecánica Y estadística previa — nada de cientos de features:

- `{RPM,MAF,COOLANT_TEMP,LTFT}_std_15` (multiescala): ADR-0011 detectó señal intermitente
  por ventana en held-out temporales;
- `corr_lag1_RPM_MAF`, `corr_lag1_THROTTLE_POS_MAF`: respuesta retardada entre demanda y
  flujo de aire (o2_lag, delayed response);
- `LTFT_session_drift` (deriva de LTFT relativa al inicio de la propia sesión): causa
  confirmada del FPR de eventos en autovía (EXP-ANOM-003, ratio entre/intra 1.56).

Los `delta_*`, `rolling_quantiles`, ratios adicionales, etc. del catálogo genérico quedan
explícitamente FUERA hasta que un análisis de errores los reclame. Promover fs2 = 
implementarlo en `shared` (cambio aditivo), fijar `feature_schema_version` nuevo y
regenerar schemas/diccionario; los modelos secuenciales (nivel 3) consumen señales
normalizadas directamente, no fs1/fs2.

**Normalización (análisis y decisión).**

| Familia | Scaler | Justificación |
|---|---|---|
| Baselines tabulares (IF/LOF/OC-SVM) | StandardScaler embebido | vigente y congelado; media/σ de train; viaja en el grafo ONNX (igualdad train↔edge por construcción) |
| robust_zscore | mediana/MAD propias | robusto a outliers por diseño |
| Autoencoders (niveles 2-3) | comparar StandardScaler vs RobustScaler en EXP-ANOM-006 | los AE son sensibles a colas pesadas (LTFT); RobustScaler (mediana/IQR) es el candidato a priori; MinMaxScaler se descarta salvo necesidad de activaciones acotadas — sensible a un único outlier |

Regla invariable: el scaler se ajusta SOLO con train y se persiste junto al artefacto con
orden de features, unidades y estadísticos de entrenamiento (`ModelManifest.expected_features`
+ preprocesado embebido o serializado; `verify_package` rechaza discrepancias en el edge).

## 5. Pipeline experimental por niveles

**Nivel 1 — Baseline tabular (COMPLETADO, no se repite).** Isolation Forest, LOF y
One-Class SVM ya fueron comparados extremo a extremo en **EXP-ANOM-001** (F3) con este
mismo protocolo: LOF k=10 SELECTED (test F1 0.6448, FPR 0.0345); OC-SVM candidate;
IForest y z-score REJECTED con card de resultado negativo. **EXP-ANOM-005** (F13) re-ejecutó
los cuatro extremo a extremo sobre el camino wide y verificó paridad exacta. HDBSCAN/DBSCAN
**no** se tratan en este nivel: no son detectores calibrables por umbral train-normal;
pertenecen a la etapa de descubrimiento (nivel 4).

**Nivel 2 — Autoencoder multivariable (EXP-ANOM-006, siguiente).** AE denso pequeño
(objetivo < 100k parámetros, tipo USAD simplificado; referencia B7 del estado del arte)
sobre ventanas fs1 o señales normalizadas. Produce reconstruction_error (score),
per-feature reconstruction error (explicabilidad §13) y latent_embedding. Comparación
obligatoria contra LOF congelado; condición de adopción = HX-ML-2. Export PyTorch→ONNX
(ruta ya prevista en ADR-0009), medición edge en sandbox + pendiente ARM64.

**Nivel 3 — Modelos longitudinales (EXP-ANOM-007, condicionado).** Solo si el nivel 2
deja evidencia de que la representación aprendida aporta (o de que el orden temporal es el
factor limitante — HX-ML-3): LSTM-AE y GRU-AE sobre [t-n..t]. TCN/Transformer temporal
pequeño NO se añaden por defecto: cada arquitectura extra exige una necesidad comparativa
declarada (la literatura de la línea A da ventaja a GRU en OBD-II embarcado). Salidas:
anomaly_score, latent_embedding, reconstruction_error.

**Nivel 4 — Descubrimiento de patrones (EXP-PAT-001/002).** Sobre embeddings del mejor
modelo de niveles 2-3: PCA (referencia lineal + varianza explicada), UMAP (solo
visualización/inspección, nunca métrica primaria — distorsiona densidades), HDBSCAN
(agrupación con ruido explícito; se estudian estabilidad/persistencia de clusters además
de Silhouette/Davies-Bouldin). Cadena objetivo:

```text
ventana OBD → encoder → embedding → clustering → candidate_pattern
```

Los clusters se denominan **candidate_pattern** (término ya canónico en el runtime y la
cadena de evidencia) — jamás "fallo" (§11).

## 6. Registro y reproducibilidad

Todo experimento registra (mecanismo vigente: `runs.jsonl` + config YAML declarativa +
Model Registry — ADR-0024 evaluó y descartó MLflow por complejidad no justificada en el
TFM; se re-evaluará solo si el volumen de experimentos lo exige):

`experiment_id · dataset_id/version/split_version · suite y semillas · features
(feature_schema_version) · window/stride · sampling_rate · normalización
(preprocessing_version) · algoritmo e hiperparámetros · random_seed · git_commit ·
hardware · python/machine · fit_seconds · métricas por split · infer_ms_per_window ·
peak_rss_mb · artefacto+sha256 (si hay) · conclusion`.

Los campos del contrato `TrainingRun`/`ModelExperiment`/`ModelEvaluation` cubren el
esquema completo pedido por la fase; `make registry` reconstruye el registro determinista
y `ModelRegistry.check()` verifica integridad referencial. Debe ser posible reconstruir
cualquier resultado de la memoria del TFM desde: suite YAML (semillas) + git_commit +
config YAML + seed de runner (42).

## 7. Serie de experimentos (nomenclatura canónica)

La serie EXP-ML-* propuesta en la instrucción de fase se integra en la nomenclatura
vigente `EXP-<FAMILIA>-<NNN>` (la consistencia documental tiene prioridad; IDs ejecutados
son inmutables y los reservados no se pisan):

| Propuesto | Canónico | Estado |
|---|---|---|
| EXP-ML-001 dataset | suites obd-lab versionadas (instrumental, sin ID de experimento) | v1/v1.1 hechas; v2 RESERVADA confirmatoria |
| EXP-ML-002 EDA/calidad | instrumental (informe de fase + tests de calidad) | parcial: cubierto por F3/F9 y tests F13 |
| EXP-ML-003 IForest | **EXP-ANOM-001** (ejecutado F3) | REJECTED con card; no se repite |
| EXP-ML-004 LOF/OC-SVM | **EXP-ANOM-001** (ejecutado F3) | LOF SELECTED; OC-SVM candidate |
| — (nuevo) camino wide | **EXP-ANOM-005** (ejecutado F13) | paridad exacta ✓ |
| EXP-ML-005 Autoencoder | **EXP-ANOM-006** | siguiente experimento |
| EXP-ML-006 ventanas | barrido de window/stride dentro de EXP-ANOM-006 | pendiente |
| EXP-ML-007 LSTM/GRU-AE | **EXP-ANOM-007** | condicionado a resultados de -006 |
| EXP-ML-008 embeddings | **EXP-PAT-001** (behavioral embeddings + clustering) | pendiente (EXP-EMB-* queda para embeddings de RAG, línea distinta) |
| EXP-ML-009 HDBSCAN | **EXP-PAT-001/002** | pendiente |
| EXP-ML-010 inyección controlada | catálogo obd-lab (8 clases) + extensiones exploratorias | vigente; nuevas clases nunca entran al held-out congelado |
| EXP-ML-011 evaluación comparativa | integrada en cada EXP (regla: siempre contra baseline congelado) | continua |
| EXP-ML-012 explicabilidad | preparación transversal (§13) + experimento propio si hay patrón candidato | pendiente |
| EXP-ML-013 inferencia RPi | **A2/A3** (instrumentales ARM64 ya definidos) + medición edge por EXP | pendiente del autor |
| EXP-ML-014 validación longitudinal e2e | **EXP-MAIN-001** (confirmatorio, PRE-REGISTRADO) | bloqueado hasta congelar pre-registro |

## 8. Anomalías controladas y procedencia

Riesgo principal del TFM: escasez de fallos reales. Estrategia vigente (ADR-0010 +
catálogo `obd_lab.injection.faults`): fallos físicamente plausibles, nunca ruido aleatorio.

Cobertura actual del catálogo frente a la taxonomía genérica: sensor drift → `maf_drift`;
stuck sensor → `thermostat_stuck`; delayed response → `o2_lag`; oscillation/spike →
`misfire`; correlation break → `corr_break_rpm_maf`; parameter divergence →
`load_coolant_decouple`; slow degradation conjunta → `joint_slow_drift`; combination →
`vacuum_leak` (MAP+trims+idle). Huecos declarados: `dropout` de señal (pérdida de PID) y
spike puro de sensor — candidatos a nuevas clases exploratorias (semillas 401–599, jamás
en el held-out congelado, cuyas clases son inmutables tras el primer confirmatorio).

**Provenance obligatoria por sesión/anomalía** (se registra en `RecordedSession.origin` +
`ScenarioSpec`): `REAL` (vehículo) · `CONTROLLED` (fallo provocado físicamente) ·
`SIMULATED` (inyección paramétrica del simulador — todo lo actual) · `SYNTHETIC`
(transformación post-hoc de datos). Los datos simulados jamás se presentan como reales;
las conclusiones se enuncian como válidas para el entorno emulado (pre-registro §12.2).

## 9. Métricas por familia

- **Detección (con etiquetas de inyección):** Precision, Recall, F1, FPR sobre normales
  (point-wise, sin point-adjustment), FNR; PR-AUC prioritaria sobre ROC-AUC bajo
  desbalance (añadir ambas a partir de EXP-ANOM-006; E1-E4 usaron métricas por umbral).
- **Temporal:** episodios detectados/total, detection_delay (medio y por episodio),
  persistencia de la anomalía (fracción de ventanas del episodio marcadas), duración de
  falsas alarmas (falsos eventos por sesión normal — ya en E2/E3).
- **Reconstrucción (niveles 2-3):** reconstruction_error global y por feature.
- **Clustering (nivel 4):** Silhouette, Davies-Bouldin, noise ratio (fracción sin cluster
  de HDBSCAN), estabilidad/persistencia de clusters HDBSCAN y estabilidad bajo re-muestreo
  (§10 criterios 1-2).
- **Edge:** inference_latency_ms por ventana, CPU, RSS pico, tamaño de artefacto,
  startup, throughput. El consumo energético NO se estima sin instrumento de medida (no
  se inventan datos); si A2/A3 incorporan medición física en RPi5, se añadirá entonces.

Presupuesto edge vinculante (pre-registro §3.4): un modelo que gana en calidad pero viola
el presupuesto se reporta como **no viable**.

## 10. Criterio para «candidate undocumented pattern»

Un cluster de comportamiento SOLO puede promoverse a *candidato a patrón no documentado*
si satisface las 8 condiciones (todas):

1. **recurrencia** — ≥ N ocurrencias (N≥3) en sesiones distintas;
2. **estabilidad** — las ocurrencias persisten bajo re-muestreo/semillas distintas;
3. **separación** — distancia a la operación normal superior a la dispersión intra-normal;
4. **coherencia temporal** — las ocurrencias tienen estructura temporal compatible;
5. **similitud entre ocurrencias** — distancia intra-cluster < inter-cluster (Silhouette>0);
6. **ausencia de regla previa** — ninguna regla/etiqueta proporcionada al sistema lo
   describe (verificable: el detector jamás vio la clase held-out);
7. **contraste documental** — la búsqueda en el corpus RAG/DTC no devuelve correspondencia
   suficiente (esta verificación pertenece a la capa de conocimiento, no a esta línea);
8. **explicaciones alternativas evaluadas** — descartadas causas triviales (deriva de
   sensor única, artefacto de simulación, contaminación de splits).

Solo tras 1-8 el candidato cuenta como evidencia hacia la PI, y su confirmación final
pertenece al protocolo held-out triple de EXP-MAIN-001 (retirada simultánea de datos,
corpus y memoria). La cadena epistemológica completa es vinculante:

```text
desviación estadística → persistencia temporal → similitud entre eventos →
patrón recurrente → contexto operacional → hipótesis → evidencia técnica → validación
```

Un anomaly_score alto JAMÁS se convierte directamente en diagnóstico mecánico.

## 11. Evidencia negativa

Resultado legítimo y publicable de cualquier experimento de esta línea:
«No existe evidencia suficiente para considerar este comportamiento un patrón estable.»
Los resultados negativos se conservan con card (regla F7 vigente: z-score/IForest
REJECTED, scoring robusto rechazado, LOF re-entrenado no adoptado — todos documentados).
La sobreinterpretación de clusters es el modo de fallo científico principal del nivel 4.

## 12. Contrato de salida hacia agentes (diseño, no implementado)

Las salidas del pipeline se diseñan para consumo posterior por el runtime agéntico, sobre
los contratos existentes (`DetectedAnomaly`, `ModelInference` — sin crear contratos nuevos
hasta que el consumidor exista):

```json
{
  "event_id": "…",            // DetectedAnomaly.anomaly_id
  "timestamp": "…",
  "anomaly_score": 0.92,       // score vs threshold del manifiesto
  "model_id": "anom-ae@0.1.0",
  "candidate_pattern": "PAT-…",// solo si supera §10; null en caso contrario
  "similar_events": [],        // búsqueda pgvector sobre eventos/patrones (§13 nota)
  "important_features": [],    // per-feature reconstruction error / contribuciones
  "context": {},               // primary_event_type, context_signature
  "confidence": {}             // separación relativa al umbral + estabilidad
}
```

Este objeto NUNCA contiene un diagnóstico mecánico definitivo.

**pgvector.** Los embeddings de comportamiento se persistirán únicamente asociados a
anomalías/casos/patrones candidatos (`case_memory`, `learned_patterns` — vector(384) ya
existente), para la consulta «eventos históricos similares al actual». **La telemetría no
se vectoriza** (REGLAS.md regla 8): no se almacena un embedding por ventana normal. Si un
experimento de nivel 4 demostrara necesidad de indexar ventanas normales, requerirá ADR
propio. pgvector no es dependencia del entrenamiento (los experimentos leen JSONL/matriz).

## 13. Explicabilidad (transversal desde el diseño)

Se conserva siempre información suficiente para responder: qué variables cambiaron,
cuándo, durante cuánto tiempo, contra qué baseline, qué features contribuyeron y qué
eventos históricos son similares. Instrumentos por familia: modelos clásicos → feature
contributions / permutation importance (SHAP solo si el coste se justifica); autoencoders
→ per-feature reconstruction error (ya previsto en docs/models/02 §4); ventanas
secuenciales → contribución por (feature, timestamp, ventana). El `DetectedAnomaly` actual
ya persiste top-PIDs y el dict completo de features; los niveles 2-4 deben mantener ese
estándar como mínimo.

## 14. Conflictos documentados en la apertura de esta línea (sin resolver aquí)

1. **Autoencoder y recorte de alcance:** `docs/07_cronograma_y_entregables.md` había
   recortado el autoencoder del cronograma («queda en baseline + IForest»). La instrucción
   del autor que abre F13 lo REACTIVA como línea exploratoria priorizada. Se mantiene la
   condición de adopción de ADR-0011 (superar a LOF en held-out con FPR ≤). El cronograma
   NO se reescribe en silencio: la reactivación queda registrada en ADR-0031 y este
   protocolo; la actualización del cronograma es decisión de redacción del autor (el
   riesgo «los autoencoders pueden consumir septiembre», F7, sigue declarado).
2. **Dos pre-registros coexistentes** (PROTO-CONF-001 vs pre-registro-v1 rc1): esta línea
   no depende de esa decisión (todo lo suyo es exploratorio), pero EXP-MAIN-001/EXP-ANOM-004
   sí. Sigue pendiente del autor congelar `prereg-v1.0`.
3. **PG-en-Edge:** resuelto por ADR-0030 (F12) — sin conflicto con esta línea; el
   entrenamiento no depende de la base de datos.
4. **EXP-ML-\* → nomenclatura canónica:** resuelto en §7 (consistencia documental primero).

## 15. Entornos

- **Entrenamiento/experimentación:** equipo de desarrollo (MacBook Apple Silicon) y
  sandbox x86; scikit-learn + PyTorch pequeño (extra `deep` ya declarado). Nada del
  diseño depende de GPU de datacenter; si un experimento la necesitara, esa necesidad se
  documenta como decisión experimental antes de ejecutar.
- **Inferencia objetivo:** Raspberry Pi 5 (ADR-0002). Todo modelo declara parameter
  count, tamaño de artefacto, RAM y latencia; cuantización INT8 como opción (ADR-0009).
  ARM64/RPi5 no se declara validado sin ejecución real (A2/A3 pendientes del autor).
- **LLM:** fuera de esta línea. Ningún fine-tuning (bloqueado por marco F7); los modelos
  fundacionales existentes se usan aguas abajo para explicación/hipótesis/RAG, y la
  contribución de ML debe poder estudiarse de forma independiente.
