# Matriz de trazabilidad del TFM

Estado: **preliminar** (13-09-2026). Conecta pregunta de investigación → objetivo → experimento
→ evidencia (registro, tabla, figura) → sección de la memoria. No sustituye a las matrices
ya versionadas (`research/traceability-matrix.md`, `docs/matriz_validacion_pi.md`,
`docs/audits/full_memory_review/01_PI_TRACEABILITY_MATRIX.md`): las cita y las resume para
que un miembro del tribunal llegue a la evidencia en un paso.

## Pregunta de investigación (canónica, ADR-004)

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

Fuente: `docs/memoria/cap1_introduccion.md:25-28`; declarada canónica en
`research/decisions/ADR-004-pregunta-de-investigacion-canonica.md:20-25` (12-09-2026).
Subpreguntas PI.1–PI.4 e hipótesis por subpregunta: `research/traceability-matrix.md:29-32`;
criterios de sostenimiento y refutación: Tabla 4.6, `docs/memoria/cap4_marco_metodologico.md:140-151`.

## Matriz

| Objetivo | Subpregunta | Experimento | Evidencia (registro) | Figura / tabla | Sección del TFM | Estado que declara el proyecto |
|---|---|---|---|---|---|---|
| OE1 revisión crítica del estado del conocimiento | — | — (revisión bibliográfica) | `research/references/{references.md, bibliography.bib, evidence-matrix.md, search-log.md}` | — | cap. 3 (`cap3_marco_teorico.md`) | GATE-02 `PASS_WITH_OBSERVATIONS` (`research/gates.md`); L-08 (no es PRISMA formal), L-09 |
| OE2 entorno experimental reproducible | — | E1, E2, E5, E10, E11 | `research/reproducibility.md`; `data/raw/synthetic/*.meta.json` (no versionado); `corpus/vehicles/mazda-3-bk-2007/manifest.yaml`; `docs/experiments/E11_carga_rag.md` | Tablas 4.1–4.4 (`cap4:24-101`) | cap. 4 §Población y muestra; §Reproducibilidad (`cap4:334`) | E1, E2, E5, E11 cerradas; E3 pendiente |
| OE3 caracterizar patrones en ventanas de telemetría | PI.1 «un modelo temporal supera de forma clara al baseline y a la mayoritaria» | E4, E5, E6, E7, E9 | `experiments/E6_baseline_synthetic_v2.json` (macro-F1 0,8788, ECE 0,1439), `E7_temporal_synthetic_v2.json` (0,823), `E9_xai_synthetic_v2.json` (18 casos) | `tables/E6_*`, `tables/E7_*`, `FIG-E6-01`, `FIG-E7-01/02` (en disco, no versionadas); la memoria no incluye figuras (`14_TABLES_FIGURES_INVENTORY.md:51-53`) | cap. 5 §PI.1 (`cap5_resultados.md:27-48`) | PI.1 «sostenida sobre datos sintéticos» en `docs/matriz_validacion_pi.md:35`; **pero E7 no supera a E6 en v2** (negativo) y v3 es inconcluso: la hipótesis literal de PI.1 no se sostiene tal como está escrita. `[RECONCILIAR]` E6/E7 en `cap5:35` |
| OE4 agente que contrasta hipótesis con evidencia observacional y documental | PI.2 «toda afirmación se ancla en una observación o fragmento identificable» | E11, E12, E13, E15 (v2.1) | `experiments/E12_retrieval.json` (hit-rate 0,0 → 1,0); `E15_suficiencia_verifier_v2_1.json` (15/17, cobertura por condición); `E13_agente_transformers-lora@slm_lora_v2.json` (9/9, 0 citas inventadas) | `tables/E12_retrieval_por_{caso,estrategia}.csv`, `tables/E15_suficiencia.csv` (en disco) | cap. 5 §PI.2 (`cap5:50-72`) y §El modelo de lenguaje (`cap5:106-116`); cap. 4 fases 4.1–4.4 (`cap4:227-282`) | PI.2 «sostenida» en `matriz_validacion_pi.md:37`; estuvo congelada por `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` hasta RERUN-A, ejecutada el 13/14-09 con cifras iguales y procedencia determinada (`docs/experiments/resultado-rerun-a.md`); recuentos de trazabilidad empeorados 18/12/0,667 → 27/15/0,556 (`07c_claim_impact_matrix.md:27`) |
| OE4 / OE5 criterio explícito de suficiencia y abstención | PI.3 «al retirar la evidencia relevante, el agente pasa de explicar a abstenerse» | E15 (condiciones ABSENT/PARTIAL), E15b, NX-01, NX-02 | `E15_suficiencia_verifier_v2_1.json` (ABSENT 3/3, PARTIAL 3/3); `E15b_barrido_umbral.json` (umbral 0,79); `E15_suficiencia_non_oracle.json` (15/17 idéntico); `E15_suficiencia_adverse.json` (6/6 abstiene; D-2 ×2, D-4 ×4) | `tables/E15_suficiencia*.csv`, `tables/E15b_barrido_umbral.csv` (en disco) | cap. 5 §PI.3 y PI.4 (`cap5:76-104`); cap. 4 Tabla 4.7 (`cap4:159`) | PI.3 «sostenida» (`matriz_validacion_pi.md:38`, sobre 4 de 6 decisiones de una versión anterior); NX-01/NX-02 **no están en el capítulo 5** (L-18); `EMPTY-DTC-GATE-BYPASS` sin corregir |
| OE5 comportamiento con distractores y contribución de componentes | PI.4 «ante evidencia parecida pero incorrecta, el agente no la acepta como soporte» | E15 (DISTRACTOR), hallazgos `ENGINE-FILTER-PERMISSIVE` y condición distractor invalidada | `E15_suficiencia_verifier_v2_1.json` (DISTRACTOR 3/3, DISTRACTOR_NO_FILTER 3/3); `docs/experiments/hallazgo-filtro-motor.md`; `docs/methodology/politica-condicion-distractor.md` | — | cap. 5 §PI.3 y PI.4 (`cap5:76-104`), §Discusión (`cap5:120-140`) | PI.4 «queda bajo diagnóstico» (`cap5:134`); `CONFLICT` en `01_PI_TRACEABILITY_MATRIX.md:13-18`; L-10 (novedad más estrecha). Diagnóstico canónico en RERUN-A: distractor `REDUNDANT_WITH_PARTIAL` en dos de tres fallos con filtro; sin inferencia confirmatoria |
| Ablaciones y contribución de componentes | — | E18 | `experiments/E18_ablacion_A1.json` a `A4.json`; `artifacts/metrics/e18_ablaciones_resumen.json` | Tabla 5.8; `artifacts/tables/E18_ablacion_A*.csv` | cap. 4 §Ablaciones; cap. 5 §Contribución de cada componente | ejecutadas el 1-10-2026: A1 sin efecto, A3 y A4 cuantifican el criterio de suficiencia, A2 inconclusa |
| Datos reales como validación externa | — | E3 | — | — | cap. 4 §Pendiente (`cap4:347`); cap. 6 §Limitaciones (L-01, crítica) | PLANNED, sin fuente |

## Preguntas que un tribunal puede hacer y dónde está la respuesta

| Pregunta | Respuesta breve, con evidencia |
|---|---|
| ¿Dónde está la evidencia de que el sistema se abstiene cuando falta la evidencia? | Condiciones ABSENT 3/3 y PARTIAL 3/3 en `experiments/E15_suficiencia.json` (canónico, 13-09); idéntico sin oráculo; en el escenario adverso las 6 ventanas mal clasificadas terminan en abstención (`E15_suficiencia_adverse.json`, 4-09). Salvedad: cota superior asistida por oráculo; el adverso no se reejecutó por decisión del plan |
| ¿Qué experimento indica que las afirmaciones se rastrean hasta un fragmento? | E13 con LoRA v2: 0 citas inventadas en 17/17 (`E13_agente_transformers-lora@slm_lora_v2.json`, 14-09; 9/9 el 4-09); las citas se comprueban contra el índice, no contra el texto generado. Los recuentos de trazabilidad se recalcularon a la baja (27/15/0,556) en `07c_claim_impact_matrix.md` |
| ¿Cómo se obtuvo la métrica macro-F1 0,8788? | `uv run mecanico-exp train-baseline --dataset-id synthetic_v2` con semilla 20260901 sobre 98 ventanas de validación; registro `experiments/E6_baseline_synthetic_v2.json`. Test cerrado por excepción (`research/reproducibility.md` §Cierre del conjunto de test) |
| ¿Puede reproducirse? | E2–E9 sí, con los comandos de `docs/EXPERIMENTO_PASO_A_PASO.md:428-446` y el mismo entorno; E11–E15 exigen el manual de taller del Mazda 3 BK, **no redistribuible** (`corpus/.../manifest.yaml: redistributable: false`) y PostgreSQL con pgvector. Riesgos concretos en `docs/reproducibility.md` |
| ¿Qué ocurrió cuando el sistema falló? | Está escrito: E7 no supera a E6 (`E7_modelo_temporal.md`), verificador v1 9/17 (`LEXICAL-SUPPORT-CONFOUND`), regresión de v2, `EMPTY-DTC-GATE-BYPASS`, `ENGINE-FILTER-PERMISSIVE`, `MIXED-EMBEDDING-SPACE`. Índice completo en `docs/experiment-index.md` §Resultados negativos |
| ¿Por qué cambió la pregunta de investigación? | ADR-003 (3-09) retiró «datos reales» al no existir fuente; ADR-004 (12-09) fijó como canónica la acotada frente a la amplia del mandato (SD-01). Ambas decisiones con su motivación en `research/decisions/` |
| ¿Qué queda sin hacer? | E3, E8, E14, E16, E19, E20, la variante léxica `A2b`, el reentrenamiento del adaptador, el rediseño de la condición con distractor, el paso C de RERUN-A (translingüe); los gates `UNREPRESENTED_PATTERN_VALIDATION` fuera de alcance (`docs/methodology/diseno-gates-pi-pendientes.md`); L-13 «alcance ejecutado más estrecho que el aprobado» (P-03, `preguntas-abiertas-al-director.md:39`) |

## Limitaciones que el tribunal verá citadas

Registro completo con severidad: `research/limitations-register.md` (L-01 … L-21; L-22
retirada). Críticas: L-01 (datos sintéticos sin validez externa) y L-20 (`MIXED-EMBEDDING-SPACE`).
Todas las cifras son de validación, no de test (L-17); un solo vehículo (L-19); catálogo de
fallos cerrado (L-21).
