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
registro) · `VALIDATED` (ejecutado y su criterio declarado se cumplió) · `NEGATIVE` (ejecutado
y la hipótesis o el criterio no se sostuvo) · `INCONCLUSIVE` (ejecutado, sin resolución
declarada) · `SUPERSEDED` (sustituido por una versión posterior o invalidado por un hallazgo).

Advertencia transversal (`docs/methodology/estados-provisionales.md`, 4-09-2026): tras el
hallazgo `MIXED-EMBEDDING-SPACE`, **todos los resultados que dependen de recuperación
(E12, E15 y sus modos, E13 en cuanto usa evidencia recuperada) están marcados por el propio
proyecto como `SUPERSEDED_BY_EMBEDDING_SPACE_FIX`**: son reproducibles pero no canónicos hasta
que se ejecute la reejecución pre-registrada `RERUN-A`. Esa reejecución **no consta
ejecutada**: los registros de `experiments/` y sus copias en
`experiments/pre_mixed_embedding_fix/` tienen el mismo `commit` y `executed_at`.

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
| E8 | ANOM | Evaluación del modelo sobre test | — | — | — | PLANNED | Test cerrado; sin registro (`docs/experiments/README.md`) |
| E9 | XAI | ¿Qué señales sostienen cada diagnóstico? | — | SHAP `Permutation` sobre `predict_proba[clase]`, fondo con semilla 20260901 | `synthetic_v2`, 18 casos de validación | RUN | 18 casos atribuidos (`experiments/E9_xai_synthetic_v2.json`); `tables/E9_*.csv` |
| E10 | RAG | Corpus documental condicionado por vehículo | — | `rag/vehicle.py`, `rag/manifest.py`; vehículo Mazda 3 BK 2007, motor Z6 | Manual de taller (no redistribuible) | RUN (infraestructura) | «infraestructura cerrada, corpus vacío» en el índice (`docs/experiments/README.md:19`); el corpus se cargó en E11 |
| E11 | RAG | Carga del corpus en pgvector | — | Ingesta + embeddings multilingües 384-d | 3 055 ficheros / 243 MB | RUN | 6 158 fragmentos, 981 con DTC (`docs/experiments/E11_carga_rag.md:9-14`). Registro en `results/rag_ingestion/` (no versionado) |
| E12 | RAG | ¿Cuánto aporta el filtrado por metadatos y autoridad sobre la similitud desnuda? | — | 5 estrategias, K = 10 | Goldset de 6 casos (5 puntuados) | **SUPERSEDED** (procedencia indeterminada) | `semantic` hit-rate 0,0 → `diagnosis-guided` hit-rate 1,0, MRR 0,4667 (`experiments/E12_retrieval.json`, 1-09-2026). Marcado `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` hasta RERUN-A |
| E13 | AGENT | ¿Redacta el SLM explicaciones válidas, respeta el veredicto del verificador y no inventa citas? | «después ≥ antes en válidas, cero citas inventadas, veredicto no peor» (`docs/experiments/E13_agente_slm.md:254-255`) | Qwen2.5-3B-Instruct, base y con LoRA; proveedores `echo`, `ollama`, `transformers`, `transformers-lora`; prompt `agent-2026-09-04` | 9 casos del goldset sobre `synthetic_v2` | VALIDATED (LoRA v2); RUN (resto) | LoRA v2: 9/9 válidas, 9/9 veredicto respetado, 0 citas inventadas (`experiments/E13_agente_transformers-lora@slm_lora_v2.json`, 4-09-2026, commit `68cb5f5`). Base: 7/9 válidas, 2 con veredicto no evaluable. Ollama: 2/9 válidas (`E13_agente_ollama.json`). Adaptador marcado `NON_CANONICAL_PENDING_REGENERATION` (`estados-provisionales.md`) |
| E13b | AGENT | Conjunto de ajuste del SLM sin fuga del manual | `leakage_check` sin texto del manual en las salidas | Pipeline real sobre ventanas de validación; reparto por `case_id` | `synthetic_v2` | RUN | 62 ejemplos, 44 casos (`experiments/E13b_training_data.json`); `TRAINING_DATASET_V1` marcado `SUPERSEDED_PENDING_CONFIRMATION` |
| E14 | VALID | Trazabilidad afirmación → evidencia | — | Integrada en E15 | — | PLANNED como fase propia | Sin registro propio (`docs/plan_experimental_macbook.md:39-45`) |
| E15 · v1 | VALID | ¿Decide bien el verificador determinista entre EXPLAIN y ABSTAIN? | Umbrales fijados solo con validación | Verificador v1 | 17 casos (goldset + condiciones) | **NEGATIVE → SUPERSEDED** | 9/17; hallazgo `LEXICAL-SUPPORT-CONFOUND` (`experiments/E15_suficiencia_verifier_v1.json`, commit `8c3ec98`) |
| E15 · v2 | VALID | ídem, soporte = fragmento de procedimiento | Política v2 escrita antes de implementar (`docs/methodology/politica-suficiencia-v2.md`) | Verificador v2 | 17 casos | **SUPERSEDED** | 14/17; corrige 5, regresiona `C05_vacuum_leak` (`E15_suficiencia_verifier_v2.json`, commit `100082d`) |
| E15 · v2.1 | VALID | ídem, sección como unidad de papel | Política v2.1 (`politica-suficiencia-v2-1.md`); revisión **no ciega**, declarada como tal | Verificador v2.1 | 17 casos | RUN (canónico del proyecto, **cota superior asistida por oráculo**) | 15/17; FULL 3/5, ABSENT 3/3, PARTIAL 3/3, DISTRACTOR 3/3; fallan C01 y C04 (`E15_suficiencia_verifier_v2_1.json`, 4-09 10:38, commit `a34bab2`). Afectado por `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` |
| E15 · NX-01 | VALID | ¿Cambia el resultado al cerrar los canales de oráculo O-2 y O-3? | Predicción declarada antes: decisiones idénticas | Modo `non-oracle`, códigos derivados del diagnóstico | 17 casos | VALIDATED (la predicción se cumplió) | 15/17, `identical_to_oracle_run: true` (`E15_suficiencia_non_oracle.json`, commit `43f56dc`) |
| E15 · NX-02 (1.ª) | VALID | Escenario adverso: ventanas mal clasificadas, selección por índice | — | Modo `adverse` | 6 ventanas | **SUPERSEDED** (regla de selección defectuosa) | Las 6 se abstuvieron por confianza baja existiendo errores con confianza 0,984 (`E15_suficiencia_adverse_seleccion_por_indice.json`) |
| E15 · NX-02 (ENM-A01) | VALID | Escenario adverso: el error más confiado | ENM-A01 | Modo `adverse` | 6 ventanas, confianza 0,929–0,984 | RUN, con hallazgo | Abstiene en las 6: D-2 (abstención) ×2, D-4 (rechazo por ausencia de soporte) ×4; todos los errores son `F00_normal` (error por omisión); hallazgo `EMPTY-DTC-GATE-BYPASS` (`E15_suficiencia_adverse.json`, commit `c502f9a`) |
| E15b | VALID | ¿Qué umbral de confianza es estable? | Criterio pre-escrito: menor umbral con precisión ≥ 0,93; ENM-U01 exige estabilidad en [t, t+0,05] | Barrido sobre validación (98 ventanas, 12 sesiones), `test_used = false` | `synthetic_v2` | VALIDATED | 0,72 cumplía por una sola ventana; el criterio enmendado da **0,79** (precisión 0,938, cobertura 0,827) (`experiments/E15b_barrido_umbral.json`, commit `35d2360`) |
| E16 | VALID | Abstención como fase propia | — | Integrada en E15 | — | PLANNED | Sin registro propio |
| E17 | VALID | Comportamiento bajo FULL / PARTIAL / ABSENT / DISTRACTOR | — | Condiciones puntuadas dentro de E15 | 17 casos | RUN parcial; condición DISTRACTOR **SUPERSEDED** | Cifras por condición en `E15_suficiencia_verifier_v2_1.json`; «distractor 3/3 no es una quinta condición: es la parcial contada dos veces» (`docs/methodology/politica-condicion-distractor.md:19`). El índice lo declara «pendiente» (`docs/experiments/README.md:25`) |
| E18, E19, E20 | — | Ablaciones, evaluación final, demostración | — | — | — | PLANNED | Sin artefacto; E19/E20 «bloqueadas» (`docs/plan_experimental_macbook.md`) |
| RERUN-A | RAG/VALID | ¿Era inocuo el defecto del espacio de embeddings? | `EXPECTED_DIRECTION: NONE`, pre-registrado y congelado antes de medir | Reejecutar E12/E15 con espacio declarado | Estado congelado en `configs/manifest_rerun_a.json` (v1.3.0, `frozen_at_commit aed6fe2`) | PLANNED | Sin artefacto de salida |
| RERUN-B / v2.2 | VALID | Puerta de DTC con requisito explícito | Política v2.2 (`politica-puerta-dtc.md`) | Implementada y probada (`tests/test_support_policy_v2_2.py`) | — | PLANNED (implementada, **sin medir**) | `docs/methodology/preregistro-rerun-a.md:31-32` |
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
| `EMPTY-DTC-GATE-BYPASS` | Con `expected_dtc` vacío la condición de código no se ejecuta | «registrado, no corregido»; v2.2 implementada sin medir | `docs/experiments/hallazgo-puerta-dtc-ausente.md` |
| `ENGINE-FILTER-PERMISSIVE` | Refuta una afirmación publicada: la defensa la hacía el vocabulario, no el filtro de motor | Afirmación retirada de la memoria | `docs/experiments/hallazgo-filtro-motor.md`, `docs/memoria/cap5_resultados.md:104` |
| Condición DISTRACTOR invalidada | Con filtro activo recupera lo mismo que PARTIAL | Rediseño adversarial pendiente | `docs/methodology/politica-condicion-distractor.md` |
| `MIXED-EMBEDDING-SPACE` (crítico, L-20) | 12 316 vectores de dos espacios incompatibles en el índice; ninguna búsqueda declaraba el espacio | Todos los resultados de recuperación pasan a `SUPERSEDED`; memoria bloqueada hasta RERUN-A | `docs/methodology/politica-espacio-de-embeddings.md`, `research/limitations-register.md:301-318` |
| NX-02 por índice | La regla de selección no puso a prueba lo que pretendía | Reemplazado por ENM-A01 | `experiments/E15_suficiencia_adverse_seleccion_por_indice.json` |
| Umbral 0,72 frágil | Cumplía el objetivo «por una ventana» | ENM-U01 → 0,79 | `docs/methodology/criterio-umbral-enmienda-01.md` |
| Respeto al veredicto en E13 base | 2 de 9 runs sin veredicto evaluable; el «9/9» publicado es 7/7 | Corrección pendiente en la memoria | `experiments/E13_agente_transformers.json`, `docs/tfm/revision/07b_reexecution_plan.md:85` |
| NX-01 y NX-02 fuera del capítulo 5 | Dos ejecuciones negativas no llegaron a la memoria | L-18 | `research/limitations-register.md:231` |
| Afirmación de ausencia falsa | Cuatro informes decían que la fuga de vacío no tenía respaldo; había 30 fragmentos con P2187 | Corregido en E15 | `docs/experiments/E15_suficiencia.md:27-46` |

## Discrepancias entre documentos (detectadas, no corregidas)

1. `results/RESULTADOS_TFM.md:5-6` declara «sin resultados» frente a 23 registros en `experiments/`.
2. `docs/experiments/E15_suficiencia.md:68` y `docs/matriz_validacion_pi.md:120` publican «7 de 9»; el registro vigente da 15/17 (`resultado-verificador-v2-1.md:113-116` los marca como desfasados).
3. E13 «9/9» de respeto al veredicto para base y LoRA v1 frente a 7/7 efectivo (punto anterior).
4. E13 «bloqueada — sin proveedor» en `docs/plan_experimental_macbook.md:38` frente a «cerrada — 9/9» en `docs/experiments/README.md:22`.
5. E17 «pendiente» (`docs/experiments/README.md:25`) frente a «parcial» (`plan_experimental_macbook.md:42`) y condiciones ya puntuadas en el JSON.
6. Siete registros JSON (`E6_*`, `E7_*`, `E9_*`, `E13b_*`, `E13_agente_{echo,ollama,*_esquema_v1}`) carecen de `commit` y `executed_at`, contra la regla de `docs/experiments/README.md:33-35` (defecto reconocido en `src/mecanico_ia_exp/experiments/registro.py:6-12` y corregido para los registros posteriores).
7. `corpus/vehicles/mazda-3-bk-2007/vehicle.yaml` fija `engine_code: Z6` mientras sus `notes` dicen que queda en `null` hasta comprobarlo sobre el vehículo real.

## Ficha por experimento (plantilla)

Para cada experimento con registro se propone una ficha `docs/experiments/fichas/E<n>.md` con
las secciones: Objetivo · Hipótesis · Motivación · Dataset · Descriptores · Montaje · Modelo o
método · Hiperparámetros · Semilla · Entorno · Métricas · Resultados · Interpretación ·
Limitaciones · Reproducción · Commits relacionados · Figuras relacionadas · Secciones del TFM.
Los campos sin dato llevan `NOT RECORDED`. Las fichas se redactarán tras la aprobación de este
índice; los informes existentes en `docs/experiments/E*_*.md` son su fuente principal y se
conservan.
