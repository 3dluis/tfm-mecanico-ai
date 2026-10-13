# Índice de experimentos

Estado: **preliminar** (13-09-2026), construido solo a partir de lo que existe en `experiments/`,
`docs/experiments/`, `docs/methodology/`, `configs/`, `models/` y el historial Git. Donde un
dato no consta, se escribe `NOT RECORDED`. No se ha ejecutado ni regenerado nada para
elaborarlo.

## Identificadores

El identificador estable de cada experimento es el **`E<n>`** que ya usan la memoria, los
informes de `docs/experiments/`, los registros JSON (`experiment_id`) y los cuadernos.
Renombrarlos rompería esa correspondencia y obligaría a editar registros congelados, así
que **no se renombran**. La columna «Familia» agrupa por bloque técnico y sirve de alias de
lectura para un revisor externo; no sustituye al `E<n>`.

Estados (vocabulario cerrado): `PLANNED` (definido, sin ejecutar) · `RUN` (ejecutado, con
registro) · `VALIDATED` (ejecutado y su criterio declarado se cumplió) · `COMPLETED — WITH
DOCUMENTED LIMITATIONS` (ejecutado y medido, con sus limitaciones escritas, **sin que ello signifique
hipótesis demostrada**; se usa cuando no había criterio numérico preregistrado contra el que
contrastar) · `NEGATIVE` (ejecutado
y la hipótesis o el criterio no se sostuvo) · `INCONCLUSIVE` (ejecutado, sin resolución
declarada) · `SUPERSEDED` (sustituido por una versión posterior o invalidado por un hallazgo).

Etiqueta adicional `NON-CANONICAL`: registros reproducibles cuya procedencia el proyecto declaró
indeterminada (hallazgo `MIXED-EMBEDDING-SPACE`, 4-09-2026). Se conservan en
`experiments/pre_mixed_embedding_fix/` y no se borran: son la evidencia de la secuencia
resultado → detección del defecto → invalidación → pre-registro de RERUN-A → reejecución.

**RERUN-A se ejecutó el 13 y 14 de septiembre de 2026** sin alterar el pre-registro
(`docs/experiments/resultado-rerun-a.md`). Los registros canónicos de E12, E15 (oracular y no
oracular), E13b y E13 son ahora los de esa fecha en `experiments/`; las decisiones no cambiaron
(15/17) aunque los conjuntos recuperados sí (10 de 17 casos).

## Tabla principal

| ID | Familia | Pregunta | Hipótesis / criterio declarado | Método | Dataset | Estado | Resultado (fuente) |
|---|---|---|---|---|---|---|---|
| E1 | ENV | ¿El entorno cumple lo que el laboratorio exige? | `doctor` en verde (Python 3.11, arm64, MPS, PostgreSQL + pgvector) | `mecanico-exp doctor` | — | RUN | Entorno verificado: M4 Pro, macOS 26.6.2, Python 3.11.14, PyTorch 2.13.0, PostgreSQL 14.15, pgvector 0.8.0 (`research/reproducibility.md`, `docs/experiments/E1_entorno.md`) |
| E2 | DATA | ¿Se puede generar telemetría OBD-II sintética con verdad de referencia y de forma determinista? | Dos ejecuciones con la misma semilla producen ficheros idénticos | Generador paramétrico calibrado contra el manual (`obd/synthetic.py`, `configs/calibracion_mazda3_bk.yaml`) | `synthetic_v1` (36 sesiones), `synthetic_v2` (72 sesiones, 6 condiciones), `synthetic_v3` | VALIDATED | Determinismo verificado (`research/reproducibility.md`); v2: 43 200 muestras, 72 sesiones (`docs/experiments/E5_preprocesamiento.md:4`). Sin JSON propio |
| E3 | DATA | Validación externa con datos reales | — | — | — | PLANNED | Sin fuente decidida; desde ADR-003 es validación externa, no precondición (`docs/experiments/README.md:12`) |
| E4 | DATA | ¿Son separables las condiciones en las series? | Delta de Cliff sobre bloques de 60 s | `eda_runner.py` | `synthetic_v1` | RUN | Tablas `tables/E4_*.csv` y figuras `FIG-E4-01..06` (en disco, no versionadas). Sin JSON |
| E5 | FEAT | ¿Qué ventana y reparto evitan la fuga entre sesiones? | Geometría elegida por medición, no por costumbre (`preprocess_runner.py:3-6`) | Ventanado 120 s, 139 descriptores, reparto por sesión, test cerrado por excepción | `synthetic_v2` | RUN | 392 ventanas de entrenamiento, 98 de validación (`docs/memoria/cap5_resultados.md:17`); `tables/E5_*.csv` |
| E6 | ANOM | Línea base tabular frente a la clase mayoritaria | Referencia contra la que medir E7 | RandomForest 400 árboles, `class_weight=balanced`, semilla 20260901 | `synthetic_v2`; también `synthetic_v3` | VALIDATED | v2: accuracy 0,8776, macro-F1 0,8788, ECE 0,1439; mayoritaria macro-F1 0,0741 (`experiments/E6_baseline_synthetic_v2.json`). v3: macro-F1 0,9321, ECE 0,0801 |
| E7 | ANOM | ¿Supera el modelo temporal a la línea base? | «Si no la supera, su complejidad no está justificada» (`docs/experiments/E6_baseline.md:8`) | GRU bidireccional, 19 014 parámetros, MPS, semilla 20260901 | `synthetic_v2`; `synthetic_v3` | **NEGATIVE** (v2) / **INCONCLUSIVE** (v3) | v2: macro-F1 0,823 < 0,8788 del bosque (`experiments/E7_temporal_synthetic_v2.json`). v3: 0,9446 frente a 0,9321, margen «inferior al sesgo plausible: inconcluso» (`docs/experiments/E7_modelo_temporal.md:12-14`) |
| E8 | ANOM | Evaluación del modelo sobre test | — | — | — | SUPERSEDED por E19 | La evaluación sobre prueba se ejecutó como E19 bajo reglas congeladas; E8 no llegó a tener protocolo propio |
| **E19** | VALID | ¿Qué hace el sistema sobre el conjunto de prueba, con la política de suficiencia corregida? | Criterio **cualitativo**: la decisión cambia al retirar la evidencia, y comparación con las dos políticas triviales. **Sin umbral numérico preregistrado** para las dos tasas | Reglas congeladas y ancladas (`de6207f`), política v2.2, tres estratos, anotación sellada antes de medir | `synthetic_v2`, partición de prueba | **COMPLETED — WITH DOCUMENTED LIMITATIONS** | Estrato operativo: falsa confianza **0/14**, abstención innecesaria **2/8**, cobertura 6/10, sobre 10 sesiones. Diagnóstico F1 macro 0,8360 frente a 0,0741. Redactor 35/35 válidas y 35/35 respetan el veredicto. Tres intentos, dos interrumpidos; conjunto de prueba abierto tres veces (`docs/experiments/E19_evaluacion_final.md`, `docs/methodology/registro-aperturas-test.md`) |
| E9 | XAI | ¿Qué señales sostienen cada diagnóstico? | — | SHAP `Permutation` sobre `predict_proba[clase]`, fondo con semilla 20260901 | `synthetic_v2`, 18 casos de validación | RUN | 18 casos atribuidos (`experiments/E9_xai_synthetic_v2.json`); `tables/E9_*.csv` |
| E10 | RAG | Corpus documental condicionado por vehículo | — | `rag/vehicle.py`, `rag/manifest.py`; vehículo Mazda 3 BK 2007, motor Z6 | Manual de taller (no redistribuible) | RUN (infraestructura) | «infraestructura cerrada, corpus vacío» en el índice (`docs/experiments/README.md:19`); el corpus se cargó en E11 |
| E11 | RAG | Carga del corpus en pgvector | — | Ingesta + embeddings multilingües 384-d | 3 055 ficheros / 243 MB | RUN | 6 158 fragmentos, 981 con DTC (`docs/experiments/E11_carga_rag.md:9-14`). Registro en `results/rag_ingestion/` (no versionado) |
| E12 | RAG | ¿Cuánto aporta el filtrado por metadatos y autoridad sobre la similitud desnuda? | — | 5 estrategias, K = 10 | Goldset de 6 casos (5 puntuados) | VALIDATED (canónico 13-09); la ejecución del 1-09 queda **NON-CANONICAL** | `semantic` hit-rate 0,0 → `diagnosis-guided` hit-rate 1,0, MRR 0,4667, nDCG 0,653 (`experiments/E12_retrieval.json`, 13-09-2026, RERUN-A). Cifras iguales a las del 1-09 (`pre_mixed_embedding_fix/E12_retrieval.json`) salvo nDCG 0,642 → 0,653 |
| E13 | AGENT | ¿Redacta el SLM explicaciones válidas, respeta el veredicto del verificador y no inventa citas? | «después ≥ antes en válidas, cero citas inventadas, veredicto no peor» (`docs/experiments/E13_agente_slm.md:254-255`) | Qwen2.5-3B-Instruct, base y con LoRA; proveedores `echo`, `ollama`, `transformers`, `transformers-lora`; prompt `agent-2026-09-04` | 9 casos (4-09) y 17 casos (14-09) del goldset sobre `synthetic_v2` | VALIDATED (LoRA v2, canónico 14-09); RUN (base, LoRA v1); las ejecuciones del 4-09 quedan **NON-CANONICAL** | LoRA v2, 14-09 (RERUN-A, commit `487e98a`): **17/17 válidas, 17/17 veredicto respetado, 0 citas inventadas**; en los 9 casos comunes reproduce el 9/9 del 4-09. Base: 15/17 válidas (2 fallos de esquema). LoRA v1: 11/17 (6 fallos de esquema). Ollama (4-09): 2/9 válidas. Adaptador sigue `NON_CANONICAL_PENDING_REGENERATION`: entrenado sobre el conjunto anterior, no reentrenado |
| E13b | AGENT | Conjunto de ajuste del SLM sin fuga del manual | `leakage_check` sin texto del manual en las salidas | Pipeline real sobre ventanas de validación; reparto por `source_window` (antes `case_id`) | `synthetic_v2` | RUN (canónico 13-09); el conjunto del 1-09 (62 ejemplos) queda SUPERSEDED / NON-CANONICAL | 66 ejemplos, 43 casos, 0 fugas (`experiments/E13b_training_data.json`, 13-09). El adaptador LoRA v2 se entrenó sobre el conjunto anterior de 62 |
| E14 | VALID | Trazabilidad afirmación → evidencia | — | Integrada en E15 | — | PLANNED como fase propia | Sin registro propio (`docs/plan_experimental_macbook.md:39-45`) |
| E15 · v1 | VALID | ¿Decide bien el verificador determinista entre EXPLAIN y ABSTAIN? | Umbrales fijados solo con validación | Verificador v1 | 17 casos (goldset + condiciones) | **NEGATIVE → SUPERSEDED** | 9/17; hallazgo `LEXICAL-SUPPORT-CONFOUND` (`experiments/E15_suficiencia_verifier_v1.json`, commit `8c3ec98`) |
| E15 · v2 | VALID | ídem, soporte = fragmento de procedimiento | Política v2 escrita antes de implementar (`docs/methodology/politica-suficiencia-v2.md`) | Verificador v2 | 17 casos | **SUPERSEDED** | 14/17; corrige 5, regresiona `C05_vacuum_leak` (`E15_suficiencia_verifier_v2.json`, commit `100082d`) |
| E15 · v2.1 | VALID | ídem, sección como unidad de papel | Política v2.1 (`politica-suficiencia-v2-1.md`); revisión **no ciega**, declarada como tal | Verificador v2.1 | 17 casos | RUN (canónico, **cota superior asistida por oráculo**); registro del 4-09 NON-CANONICAL, registro del 13-09 canónico | 15/17; FULL 3/5, ABSENT 3/3, PARTIAL 3/3, DISTRACTOR 3/3; fallan C01 y C04. Registro canónico `experiments/E15_suficiencia.json` (13-09, RERUN-A, decisiones idénticas al del 4-09 `pre_mixed_embedding_fix/`); histórico `E15_suficiencia_verifier_v2_1.json` (commit `a34bab2`) |
| E15 · NX-01 | VALID | ¿Cambia el resultado al cerrar los canales de oráculo O-2 y O-3? | Predicción declarada antes: decisiones idénticas | Modo `non-oracle`, códigos derivados del diagnóstico | 17 casos | VALIDATED (la predicción se cumplió, también con recuperación canónica) | 15/17, idéntico al oracular (`E15_suficiencia_non_oracle.json`, 13-09; histórico 4-09 en `pre_mixed_embedding_fix/`, commit `43f56dc`) |
| E15 · NX-02 (1.ª) | VALID | Escenario adverso: ventanas mal clasificadas, selección por índice | — | Modo `adverse` | 6 ventanas | **SUPERSEDED** (regla de selección defectuosa) | Las 6 se abstuvieron por confianza baja existiendo errores con confianza 0,984 (`E15_suficiencia_adverse_seleccion_por_indice.json`) |
| E15 · NX-02 (ENM-A01) | VALID | Escenario adverso: el error más confiado | ENM-A01 | Modo `adverse` | 6 ventanas, confianza 0,929–0,984 | RUN, con hallazgo | Abstiene en las 6: D-2 (abstención) ×2, D-4 (rechazo por ausencia de soporte) ×4; todos los errores son `F00_normal` (error por omisión); hallazgo `EMPTY-DTC-GATE-BYPASS` (`E15_suficiencia_adverse.json`, commit `c502f9a`) |
| E15b | VALID | ¿Qué umbral de confianza es estable? | Criterio pre-escrito: menor umbral con precisión ≥ 0,93; ENM-U01 exige estabilidad en [t, t+0,05] | Barrido sobre validación (98 ventanas, 12 sesiones), `test_used = false` | `synthetic_v2` | VALIDATED | 0,72 cumplía por una sola ventana; el criterio enmendado da **0,79** (precisión 0,938, cobertura 0,827) (`experiments/E15b_barrido_umbral.json`, commit `35d2360`) |
| E16 | VALID | Abstención como fase propia | — | Integrada en E15 | — | PLANNED | Sin registro propio |
| E17 | VALID | Comportamiento bajo FULL / PARTIAL / ABSENT / DISTRACTOR | — | Condiciones puntuadas dentro de E15 | 17 casos | RUN parcial; condición DISTRACTOR diagnosticada en RERUN-A | Cifras por condición en `E15_suficiencia.json`. Diagnóstico canónico D-1/D-2 (`resultado-rerun-a.md` paso E): con filtro de motor, `VALID_CONDITION` en un fallo y `REDUNDANT_WITH_PARTIAL` en dos; sin filtro, válida en los tres. No hay inferencia confirmatoria posible (K no homogéneo) |
| E18 | ABL | ¿Qué aporta cada componente al comportamiento observado? | Definiciones operativas y criterio de interpretación fijados antes de medir (`preregistro-e18-ablaciones.md`) | Cuatro ablaciones sobre la configuración canónica, sin redactor | 17 casos anotados, `synthetic_v2`, política v2.1 | RUN (A1, A3, A4) · **INCONCLUSIVE** (A2) | A1 sin atribución: 0 de 17 decisiones distintas y evidencia idéntica. A2 sin recuperación semántica: cero fragmentos recuperados, inconclusa por la consulta conjuntiva (`ENM-E18-01`). A3 sin criterio de suficiencia: falsa confianza 6 de 9. A4 umbral único: 9 de 9, coincide con la política de referencia publicada (`E18_ablacion_A1..A4.json`, `docs/experiments/E18_ablaciones.md`) |
| E19, E20 | — | Evaluación final sobre el conjunto de prueba, demostración | — | — | — | PLANNED | Sin artefacto; exigen abrir el conjunto de prueba con declaración explícita |
| RERUN-A | RAG/VALID | ¿Era inocuo el defecto del espacio de embeddings? | `EXPECTED_DIRECTION: NONE`, pre-registrado y congelado antes de medir | Reejecutar E12/E15/E13b/E13 con espacio declarado | Estado congelado en `configs/manifest_rerun_a.json` (v1.3.0, `frozen_at_commit aed6fe2`) | RUN (13/14-09-2026) · INCONCLUSIVE respecto a la pregunta «¿era inocuo?» | Conjuntos recuperados cambian en 10/17 casos (solo se añaden fragmentos); decisiones idénticas 15/17; líneas base invariantes reproducidas; E12 igual salvo nDCG; E13 LoRA v2 17/17. Por el criterio pre-registrado: «sin efecto detectable con este instrumento». Pasos C (multilingüe) no ejecutable; adaptador no regenerado (`docs/experiments/resultado-rerun-a.md`, `artifacts/metrics/rerun_a_comparison.json`) |
| RERUN-B / v2.2 | VALID | ¿Cambia alguna decisión al exigir el requisito explícito de la puerta de códigos? | Predicción por modo, registrada antes de medir (`preregistro-e18-ablaciones.md` §5) | Política v2.2 en los tres modos | 17 casos y 6 ejecuciones adversas | RUN (1-10-2026) | Decisiones y motivos idénticos a v2.1 en los tres modos. En el adverso el requisito pasa a `DTC_NOT_APPLICABLE` y dos ejecuciones dejan de aceptar soporte para un diagnóstico incorrecto: cobertura 0,67 → 0,00. Cierra `EMPTY-DTC-GATE-BYPASS` (`E15_suficiencia*_v2_2.json`, `docs/experiments/resultado-rerun-b.md`) |
| E-EMBED-MULTILINGUAL | RAG | Comparación de embeddings multilingües | Pre-registrada; «no forma parte de la pregunta de investigación» | — | — | PLANNED | `docs/methodology/preregistro-embed-multilingual.md` |
| RX-00 … RX-05, NX-03, NX-04 | — | Plan de reejecución del ciclo de corrección | Tabla en `docs/tfm/revision/07b_reexecution_plan.md:25-34` | — | — | RX-00, RX-01, RX-02 y RX-04 ejecutados según los commits `f6396fe`, `24e94d1`, `ed27aad`, `f9c5c0c` (sus artefactos son los registros E15/E13/E15b de arriba); RX-03, RX-05, NX-03, NX-04: PLANNED | — |

## Resultados negativos e inconclusos

No se ocultan. Cada uno tiene fichero.

| Hallazgo | Qué pasó | Consecuencia declarada | Fichero |
|---|---|---|---|
| E7 frente a E6 | El GRU pierde en `synthetic_v2` y gana por 0,0125 en `synthetic_v3` | «inconcluso»; la complejidad del modelo temporal no queda justificada | `docs/experiments/E7_modelo_temporal.md:12-14` |
| Recuperación semántica pura | Hit-rate 0,00 y un distractor por encima del relevante | La similitud desnuda no basta; motivó las estrategias filtradas | `experiments/E12_retrieval.json` |
| `LEXICAL-SUPPORT-CONFOUND` | Al pasar de 1 fallo a 3 el verificador v1 cayó de 7/9 a 9/17 | Política v2 | `docs/experiments/hallazgo-lexical-support-confound.md` |
| Abstención falsa en v2 | v2 regresiona `C05_vacuum_leak` | Política v2.1 (sección como unidad) | `experiments/E15_suficiencia_verifier_v2.json` |
| `EMPTY-DTC-GATE-BYPASS` | Con `expected_dtc` vacío la condición de código no se ejecutaba | **corregido en v2.2 y medido el 1-10-2026**: en el escenario adverso desaparece el soporte falso de dos ejecuciones; ninguna decisión del conjunto principal cambia | `docs/experiments/hallazgo-puerta-dtc-ausente.md`, `docs/experiments/resultado-rerun-b.md` |
| `ENGINE-FILTER-PERMISSIVE` | Refuta una afirmación publicada: la defensa la hacía el vocabulario, no el filtro de motor | Afirmación retirada de la memoria | `docs/experiments/hallazgo-filtro-motor.md`, `docs/memoria/cap5_resultados.md:104` |
| Condición DISTRACTOR invalidada | Con filtro activo recupera lo mismo que PARTIAL | Rediseño adversarial pendiente | `docs/methodology/politica-condicion-distractor.md` |
| `MIXED-EMBEDDING-SPACE` (crítico, L-20) | 12 316 vectores de dos espacios incompatibles en el índice; ninguna búsqueda declaraba el espacio | Todos los resultados de recuperación pasaron a `SUPERSEDED`; memoria bloqueada hasta RERUN-A. RERUN-A (13/14-09): decisiones idénticas, conjuntos distintos en 10/17 casos | `docs/methodology/politica-espacio-de-embeddings.md`, `research/limitations-register.md:301-318`, `docs/experiments/resultado-rerun-a.md` |
| NX-02 por índice | La regla de selección no puso a prueba lo que pretendía | Reemplazado por ENM-A01 | `experiments/E15_suficiencia_adverse_seleccion_por_indice.json` |
| Umbral 0,72 frágil | Cumplía el objetivo «por una ventana» | ENM-U01 → 0,79 | `docs/methodology/criterio-umbral-enmienda-01.md` |
| Respeto al veredicto en E13 base | 2 de 9 runs sin veredicto evaluable; el «9/9» publicado era 7/7 evaluables | **Corregido el 13-09-2026** en `E13_agente_slm.md` y `cap5_resultados.md`, con nota | `experiments/pre_mixed_embedding_fix/E13_agente_transformers.json`, `docs/tfm/revision/07b_reexecution_plan.md:85` |
| NX-01 y NX-02 fuera del capítulo 5 | Dos ejecuciones negativas no llegaron a la memoria | L-18 | `research/limitations-register.md:231` |
| Afirmación de ausencia falsa | Cuatro informes decían que la fuga de vacío no tenía respaldo; había 30 fragmentos con P2187 | Corregido en E15 | `docs/experiments/E15_suficiencia.md:27-46` |

## Discrepancias entre documentos: detectadas el 13-09-2026 y cómo se resolvieron

Regla aplicada: no se armonizan números para que coincidan; se determina cuál corresponde a la
evidencia y el cambio queda visible en el propio documento, con fecha.

| # | Discrepancia | Qué dice la evidencia | Resolución |
|--:|---|---|---|
| D-1 | `results/RESULTADOS_TFM.md` declaraba «sin resultados» frente a 23 registros en `experiments/` | El fichero era una plantilla del 1-09 nunca actualizada | Conservado íntegro bajo un aviso OBSOLETO que remite a este índice (commit `aca345c`) |
| D-2 | `docs/experiments/E15_suficiencia.md` y `docs/matriz_validacion_pi.md` publican «7 de 9»; el registro vigente da 15/17 | 7/9 es el verificador v1 sobre 9 casos (1-09); 15/17 es v2.1 sobre 17 casos, confirmado por RERUN-A | Se conserva el 7/9 como histórico y se añade una nota fechada con la cifra vigente y la secuencia v1 → v2 → v2.1 |
| D-3 | «9/9» de respeto al veredicto para el modelo base y LoRA v1 en `E13_agente_slm.md` y `cap5_resultados.md` | Los registros tienen `respected_verdict: null` en los 2 runs con fallo de esquema de cada configuración: **7 de 7 evaluables**; el 9/9 contaba lo no evaluable | Corregido en ambos documentos con nota de corrección fechada; la cifra antigua se cita en la nota, no se borra |
| D-4 | E13 «bloqueada, sin proveedor» en `plan_experimental_macbook.md` frente a «cerrada, 9/9» en `docs/experiments/README.md` | E13 se ejecutó con `transformers` local el 4-09 (9/9) y el 14-09 (17/17) | Fila del plan actualizada, indicando qué decía antes |
| D-5 | E17 «pendiente» frente a «parcial» y condiciones ya puntuadas | Las condiciones están puntuadas dentro de E15; la de distractor quedó diagnosticada en RERUN-A | Ambos documentos actualizados al mismo estado («parcial», con el diagnóstico) |
| D-6 | Siete registros JSON anteriores al 4-09 sin `commit` ni `executed_at` | El defecto es real y no es corregible retroactivamente sin reejecutar; `registro.py` lo obliga desde el 4-09 | Se documenta como `NOT RECORDED` aquí y en `docs/reproducibility.md`; la fecha se reconstruye por el commit que añadió cada registro (tabla en `artifacts/README.md`) |
| D-7 | `vehicle.yaml` fija `engine_code: Z6` y sus notas decían que quedaba en `null` hasta comprobarlo sobre el vehículo real | El Z6 se fijó por decisión del autor al formalizar el vehículo de referencia (Tabla 4.1), no por un vehículo real | Nota del fichero corregida, indicando qué decía antes y por qué |

## Ficha por experimento (plantilla)

Para cada experimento con registro se propone una ficha `docs/experiments/fichas/E<n>.md` con
las secciones: Objetivo · Hipótesis · Motivación · Dataset · Descriptores · Montaje · Modelo o
método · Hiperparámetros · Semilla · Entorno · Métricas · Resultados · Interpretación ·
Limitaciones · Reproducción · Commits relacionados · Figuras relacionadas · Secciones del TFM.
Los campos sin dato llevan `NOT RECORDED`. Las fichas se redactarán tras la aprobación de este
índice; los informes existentes en `docs/experiments/E*_*.md` son su fuente principal y se
conservan.
