# Git History Audit

Auditoría del historial Git de `mecanico-ia-exp`, realizada el 13-09-2026 antes de
cualquier modificación. **Ejecutada** el 13 y 14-09 según la opción A; resultado en
`docs/git-history-report.md`. Todo lo que sigue se obtuvo del propio repositorio; no se
infiere nada que no conste en Git o en los ficheros versionados.

## 1. Estado actual

| Elemento | Valor |
|---|---|
| Rama actual | `main` (única rama de trabajo) |
| HEAD | `3b001d4c210a696efb88fe73bfa54829d8065926` — «Introduccion: anunciar el vacio, que solo vivia en el capitulo 3» (13-09-2026 17:35 -0400) |
| Remote | `origin` → `https://github.com/3dluis/-mecanico-ai-exp.git`. `git ls-remote --exit-code origin` devuelve 2: **el remoto no tiene ninguna referencia**. La rama nunca se ha publicado; no hay ramas de seguimiento remoto |
| Working tree | Limpio (`git status`: «nothing to commit, working tree clean»). Sin ficheros untracked. Sin stash |
| Tags | Ninguno |
| Commits | 170, lineales, sin merges |
| Autoría | Un único autor y committer en los 170 commits: `Luis Diaz <danieldiaz288@gmail.com>` |
| Fechas | 2026-09-01 (28 commits), 09-02 (8), 09-03 (20), 09-04 (41), 09-10 (48), 09-11 (19), 09-13 (6). AuthorDate = CommitDate en 169 commits; en `a8e9f6c` difieren 78 s (enmienda inmediata) |
| Hooks / firmas | Sin hooks activos, sin commits firmados |
| Punto de recuperación | Rama `backup/pre-history-cleanup-20260913-1815` creada sobre `3b001d4` |

Ficheros ignorados presentes en disco (no versionados, regenerables): `.env`, `.venv/`,
`.idea/workspace.xml`, datasets `data/raw/synthetic/synthetic_v{1,2,3}.parquet`,
`data/processed/*`, figuras `figures/FIG-E4..E7-*.png`, `models/E7_*.npy` y los
adaptadores LoRA, `corpus/vehicles/mazda-3-bk-2007/raw/`. Ninguno se toca en esta auditoría.

Observación: `.gitignore` excluye `.idea/`, pero seis ficheros de `.idea/` están versionados
(añadidos antes de la regla o forzados). Se trata en la Fase 7 (calidad), no en el historial.

## 2. Historia técnica detectada

### 2.1 Resumen por jornada

| Jornada | Commits | Qué ocurrió realmente (según mensajes y ficheros) |
|---|---:|---|
| 2026-09-01 | 1–28 | Andamiaje del laboratorio (uv, pyproject, compose, Alembic, notebooks generados por script, plan experimental). En la misma tarde: E2 generador OBD-II sintético, E4 EDA, E5 ventanado y reparto, E6 baseline bosque aleatorio, E7 GRU sobre MPS, E10 corpus por vehículo, selección y calibración del Mazda 3 BK, E11 carga en pgvector, E12 evaluación de recuperación, E9 SHAP, E15 verificador de suficiencia, corpus multilingüe, guía de reproducción, matriz de validación de la PI, E17 condiciones de evidencia, E13 agente con SLM local, E13b conjunto de ajuste y entrenador LoRA |
| 2026-09-02 | 29–36 | E13: registro auditable del agente, medición antes/después, iteraciones 1 y 2 del ajuste (9/9), texto fuente de la memoria |
| 2026-09-03 | 37–56 | ADR-003 (la PI deja de exigir datos reales), taxonomía de procedencia, trazabilidad, cabeceras de cuadernos, informe de impacto; informe del tutor; revisión integral con siete auditorías consolidadas (línea base, estadística, referencias, RAG, experimentos, evidencia, tutor) y plan de corrección |
| 2026-09-04 | 57–97 | Ciclo de correcciones: criterio de umbral y barrido (RX-04), ENM-U01 (umbral 0,79), reejecuciones RX-00/01/02, P-03/P-05/P-06; verificador de suficiencia v1 → v2 (14/17) → v2.1 (15/17); modos no oracular y adverso, ENM-A01, NX-01/NX-02 y hallazgo EMPTY-DTC-GATE-BYPASS; puerta de DTC v2.2; invalidación de la condición distractor y refutación del filtro de motor; política de aislamiento de embeddings, reproducción y corrección de MIXED-EMBEDDING-SPACE; plan y pre-registro de RERUN-A; ENM-S01/S02/S03 |
| 2026-09-10 | 98–145 | Memoria: marcas editoriales, OE4 (dos iteraciones), vehículo de referencia formalizado, verificación de referencias en fuente primaria, matriz de alineación, capítulo de objetivos ajustado a plantilla, conclusiones acotadas, discrepancias declaradas en resultados, bibliografía, SD-01, política de expresión académica, inventario y matriz de trazabilidad, observaciones del tutor, registro de correcciones (iteración 3), resumen/introducción/objetivos/marco teórico reescritos según plantilla, normalización de tablas y figuras, diagnóstico de primera entrega |
| 2026-09-11 | 146–164 | Memoria: muestra, fase de recuperación, fases del agente, reproducibilidad, modelo de análisis, conclusiones provisionales, voz de referencia y criterio de escritura, registro del marco teórico |
| 2026-09-13 | 165–170 | Observaciones del tutor, ADR-004 (pregunta canónica acotada), cierre del feedback, marcas de trabajo de los capítulos 4 y 5, registro denso, vacío anunciado en la introducción |

Distribución por área (área dominante de cada commit): memoria 64, documentación 29,
revisión/auditoría 20, artefactos de experimentos 13, tests 8, código fuente 7, cuadernos 7,
research 7, suficiencia/evidencia 4, datos/corpus/config 3, agente/LLM 3, infraestructura 2,
RAG 2, generador de datos 1.

Lectura honesta de esta distribución: el código científico y los experimentos se
construyeron casi por completo el 1 y 2 de septiembre en commits grandes por experimento
(E2…E17); los 134 commits restantes son correcciones instrumentales, auditorías y redacción
de la memoria. El historial refleja eso y no se va a reescribir para que parezca otra cosa.

### 2.2 Tabla completa (170 commits, orden cronológico)

La columna «Trailer» indica si el mensaje contiene los dos trailers automáticos descritos en
la sección 3. «Archivos principales» son los tres ficheros con más líneas cambiadas.

| Orden | Commit | Fecha real | Área | Cambio | Ficheros | Archivos principales | Trailer |
|------:|--------|------------|------|--------|---------:|----------------------|---------|
| 1 | `3a2ce39` | 2026-09-01 13:21 | src, datos/corpus/config | Andamiaje del laboratorio experimental | 36 | `uv.lock`, `pyproject.toml`, `compose.yaml` | no |
| 2 | `9b84894` | 2026-09-01 13:21 | tests, src | Configuración tipada y auditoría del entorno | 9 | `src/mecanico_ai_exp/config/environment.py`, `src/mecanico_ai_exp/config/settings.py`, `src/mecanico_ai_exp/cli.py` | no |
| 3 | `41d06f0` | 2026-09-01 13:21 | infra, otro | Base de datos: Alembic y creación reproducible | 6 | `alembic.ini`, `migrations/env.py`, `scripts/init_db.sh` | no |
| 4 | `619940c` | 2026-09-01 13:21 | notebooks | Notebooks con estructura documental obligatoria | 18 | `scripts/gen_notebooks.py`, `notebooks/00_environment_check.ipynb`, `notebooks/TFM_EXPERIMENTO_COMPLETO.ipynb` | no |
| 5 | `eaee16c` | 2026-09-01 13:21 | docs, infra | Plan experimental, metodología y guías de instalación | 15 | `docs/plan_experimental_macbook.md`, `README.md`, `docs/methodology/experimental-design.md` | no |
| 6 | `f110fae` | 2026-09-01 13:22 | notebooks | Ajustar el generador de notebooks a los gates de estilo | 1 | `scripts/gen_notebooks.py` | no |
| 7 | `7b5fe34` | 2026-09-01 13:45 | src, notebooks | Renombrar el laboratorio a mecanico-ia-exp | 54 | `notebooks/00_environment_check.ipynb`, `docs/experiments/E1_entorno.md`, `scripts/gen_notebooks.py` | no |
| 8 | `e53dd31` | 2026-09-01 13:59 | datos/generador, docs | E2: generador OBD-II sintético con verdad de referencia | 10 | `tests/test_synthetic_obd.py`, `src/mecanico_ia_exp/obd/faults.py`, `src/mecanico_ia_exp/obd/synthetic.py` | no |
| 9 | `057bd3a` | 2026-09-01 14:12 | src, tests | E4: análisis exploratorio temporal | 9 | `src/mecanico_ia_exp/visualization/eda.py`, `src/mecanico_ia_exp/data/exploration.py`, `tests/test_exploration.py` | no |
| 10 | `a8e9f6c` | 2026-09-01 14:32 | notebooks, research | E5: ventanado, descriptores y reparto sin fuga | 38 | `research/references/bibliography.bib`, `tests/test_preprocessing.py`, `docs/experiments/E5_preprocesamiento.md` | no |
| 11 | `a031c29` | 2026-09-01 14:51 | research, docs | E6: baseline con bosque aleatorio | 16 | `research/limitations-register.md`, `research/traceability-matrix.md`, `docs/experiments/E6_baseline.md` | no |
| 12 | `27b9f8d` | 2026-09-01 15:06 | research, modelos | E7: modelo temporal GRU sobre MPS | 18 | `src/mecanico_ia_exp/models/training.py`, `docs/experiments/E7_modelo_temporal.md`, `src/mecanico_ia_exp/experiments/temporal_runner.py` | no |
| 13 | `dffe031` | 2026-09-01 15:16 | docs, rag | E10: corpus documental condicionado por vehículo | 18 | `tests/test_vehicle_corpus.py`, `src/mecanico_ia_exp/rag/document_downloader.py`, `src/mecanico_ia_exp/rag/ingest.py` | no |
| 14 | `35f8302` | 2026-09-01 15:28 | datos/corpus/config, research | Candidato Mazda 3 BK 2007 con manual de taller verificado en contenido | 5 | `research/references/references.md`, `docs/rag/vehicle-document-candidates.md`, `corpus/vehicles/mazda-3-bk-2007/manifest.yaml` | no |
| 15 | `770ce70` | 2026-09-01 15:46 | research, docs | Calibrar el generador OBD-II contra el manual de taller del Mazda 3 BK | 18 | `research/references/bibliography.bib`, `research/references/source-index.md`, `research/references/references.md` | no |
| 16 | `be5433b` | 2026-09-01 16:15 | rag, infra | E11: carga del corpus del Mazda 3 BK en pgvector | 13 | `src/mecanico_ia_exp/rag/store.py`, `tests/test_rag_pipeline.py`, `src/mecanico_ia_exp/rag/chunking.py` | no |
| 17 | `355d475` | 2026-09-01 16:23 | src, docs | E12: evaluacion de la recuperacion sobre conjunto anotado | 9 | `experiments/E12_retrieval.json`, `src/mecanico_ia_exp/experiments/retrieval_runner.py`, `tests/test_retrieval_eval.py` | no |
| 18 | `09ca1e5` | 2026-09-01 16:50 | docs, artefactos | E9: atribucion SHAP sobre el modelo especializado | 7 | `experiments/E9_xai_synthetic_v2.json`, `src/mecanico_ia_exp/xai/attribution.py`, `docs/experiments/E9_atribucion.md` | no |
| 19 | `4437d07` | 2026-09-01 17:07 | suficiencia/evidencia, src | E15: verificador de suficiencia, sin modelo de lenguaje | 13 | `experiments/E15_suficiencia.json`, `tests/test_sufficiency.py`, `src/mecanico_ia_exp/abstention/sufficiency.py` | no |
| 20 | `bd671b9` | 2026-09-01 17:21 | rag, src | Corpus multilingüe: español e inglés | 11 | `docs/rag/multilingual.md`, `tests/test_rag_pipeline.py`, `migrations/versions/0004_idioma.py` | no |
| 21 | `7a0d714` | 2026-09-01 17:30 | docs, datos/corpus/config | Guía de reproducción paso a paso y correccion propagada | 4 | `docs/EXPERIMENTO_PASO_A_PASO.md`, `configs/calibracion_mazda3_bk.yaml`, `docs/experiments/E12_evaluacion_recuperacion.md` | no |
| 22 | `be0516d` | 2026-09-01 17:33 | docs, artefactos | Matriz de validacion de la PI con resultados medidos | 2 | `docs/matriz_validacion_pi.md`, `experiments/E12_retrieval.json` | no |
| 23 | `c5f6c66` | 2026-09-01 17:50 | notebooks, docs | Plan actualizado y notebooks rellenados | 13 | `notebooks/04_preprocessing_features.ipynb`, `scripts/fill_notebooks.py`, `notebooks/03_timeseries_eda.ipynb` | no |
| 24 | `15a131e` | 2026-09-01 17:51 | infra | Relajar reglas de importacion en los notebooks | 1 | `pyproject.toml` | no |
| 25 | `7fb2255` | 2026-09-01 19:49 | docs, src | E17: las cuatro condiciones de evidencia y umbrales calibrados | 8 | `experiments/E15_suficiencia.json`, `docs/experiments/E15_suficiencia.md`, `configs/goldset_mazda3_bk.yaml` | no |
| 26 | `9bbbf81` | 2026-09-01 20:23 | agente/llm, artefactos | E13: agente con SLM local, herramientas y salida estructurada | 7 | `experiments/E13_agente_ollama.json`, `experiments/E13_agente_echo.json`, `src/mecanico_ia_exp/llm/provider.py` | no |
| 27 | `a6057fd` | 2026-09-01 21:38 | docs, infra | E13b: conjunto de ajuste del SLM y entrenador PyTorch+PEFT | 12 | `tests/test_llm_agent.py`, `uv.lock`, `src/mecanico_ia_exp/experiments/training_runner.py` | no |
| 28 | `6171407` | 2026-09-01 22:04 | agente/llm, tests | Proveedor transformers con adaptador LoRA y correccion del entrenador | 4 | `src/mecanico_ia_exp/llm/provider.py`, `src/mecanico_ia_exp/llm/finetune.py`, `tests/test_llm_agent.py` | no |
| 29 | `e2d7c59` | 2026-09-02 12:08 | datos/corpus/config, agente/llm | E13: un solo vocabulario de motivos de abstención y registro auditable del agente | 6 | `tests/test_llm_agent.py`, `models/slm_lora/adapter_config.json`, `models/slm_lora/finetune_config.json` | no |
| 30 | `76c5bfe` | 2026-09-02 12:10 | artefactos, docs | E13: documentar el ajuste ejecutado y la primera medición antes/después | 4 | `experiments/E13_agente_transformers-lora_esquema_v1.json`, `experiments/E13_agente_transformers_esquema_v1.json`, `docs/experiments/E13_agente_slm.md` | no |
| 31 | `0612026` | 2026-09-02 12:15 | notebooks, agente/llm | E13: resumen antes/después en el paquete y cuaderno 10 con hipótesis y criterio | 3 | `notebooks/10_llm_agent.ipynb`, `src/mecanico_ia_exp/llm/report.py`, `tests/test_llm_agent.py` | no |
| 32 | `1b4d299` | 2026-09-02 12:26 | agente/llm, docs | E13: cerrar la iteración 1 del ajuste y preparar la iteración 2 | 13 | `notebooks/10_llm_agent.ipynb`, `experiments/E13_agente_transformers-lora.json`, `experiments/E13_agente_transformers.json` | no |
| 33 | `144bef1` | 2026-09-02 12:26 | tests, agente/llm | E13: serializar el identificador del caso anotado en el registro del agente | 2 | `tests/test_llm_agent.py`, `src/mecanico_ia_exp/llm/agent.py` | no |
| 34 | `8ae57b4` | 2026-09-02 12:28 | notebooks | E13: el cuaderno 10 lee el registro de la iteración 2 cuando exista | 1 | `notebooks/10_llm_agent.ipynb` | no |
| 35 | `ffca7f9` | 2026-09-02 13:43 | docs, datos/corpus/config | E13: cerrar el ajuste del SLM con la iteración 2 (9/9 sobre el conjunto anotado) | 8 | `experiments/E13_agente_transformers-lora@slm_lora_v2.json`, `notebooks/10_llm_agent.ipynb`, `docs/experiments/E13_agente_slm.md` | no |
| 36 | `3f8eac3` | 2026-09-02 14:28 | memoria, research | Memoria: texto fuente de los capítulos que no dependen de los datos reales | 10 | `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap5_resultados.md`, `docs/memoria/cap3_marco_teorico.md` | no |
| 37 | `ce9be6d` | 2026-09-03 13:42 | research, src | ADR-003: la pregunta de investigación deja de exigir datos OBD-II reales | 3 | `research/decisions/ADR-003-pi-sin-requisito-de-datos-reales.md`, `src/mecanico_ia_exp/__init__.py`, `README.md` | no |
| 38 | `d8d8d32` | 2026-09-03 13:42 | tests, datos/generador | Procedencia de datos: taxonomía cerrada real / synthetic / simulated / public_dataset | 2 | `tests/test_dataset_provenance.py`, `src/mecanico_ia_exp/data/metadata.py` | no |
| 39 | `18a51be` | 2026-09-03 13:42 | docs | PI sin requisito de datos reales: matriz de validación, plan, diseño y notas de fase | 9 | `docs/matriz_validacion_pi.md`, `docs/methodology/experimental-design.md`, `docs/entregas/informe_seguimiento_1_borrador.md` | no |
| 40 | `fbebb91` | 2026-09-03 13:42 | research | Trazabilidad tras ADR-003: I-07 resuelta, GATE-01 en PASS, OE-M2 desbloqueado | 7 | `research/available-skills.md`, `research/traceability-matrix.md`, `research/gates.md` | no |
| 41 | `8b4f0d6` | 2026-09-03 13:42 | notebooks | Cuadernos: PI enmendada en la cabecera de los diecisiete y E3 como validación externa | 18 | `notebooks/10_llm_agent.ipynb`, `notebooks/TFM_EXPERIMENTO_COMPLETO.ipynb`, `notebooks/15_tfm_demo.ipynb` | no |
| 42 | `c94a3d6` | 2026-09-03 13:42 | memoria | Memoria: PI enmendada y procedencia declarada en lugar de resultados condicionales | 8 | `docs/memoria/cap1_introduccion.md`, `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap6_conclusiones.md` | no |
| 43 | `b7a68f9` | 2026-09-03 13:42 | revision/auditoria | Informe de impacto y changelog del cambio de la PI (ADR-003) | 1 | `docs/tfm/cambio_pi_eliminacion_datos_reales.md` | no |
| 44 | `ef61ee2` | 2026-09-03 13:47 | research, docs | Correcciones tras la auditoría independiente del cambio de la PI | 4 | `docs/matriz_validacion_pi.md`, `docs/memoria/cap5_resultados.md`, `research/traceability-matrix.md` | no |
| 45 | `8d55def` | 2026-09-03 13:47 | revision/auditoria, research | Informe del tutor sobre el cambio de la PI: FAIL por un MAJOR, corregido y reevaluado | 3 | `tutor-reports/TUTOR-REPORT-20260903.md`, `docs/tfm/cambio_pi_eliminacion_datos_reales.md`, `research/gates.md` | no |
| 46 | `ac428e6` | 2026-09-03 18:26 | revision/auditoria | Informe del tutor: estados FIXED también en el bloque de traspaso | 1 | `tutor-reports/TUTOR-REPORT-20260903.md` | no |
| 47 | `d45caad` | 2026-09-03 18:35 | revision/auditoria | Revisión integral: línea base, inventario de skills y auditoría de plantilla UAX | 1 | `docs/tfm/revision/00_baseline.md` | no |
| 48 | `2313c39` | 2026-09-03 22:15 | revision/auditoria | Revisión integral: informe estadístico consolidado y actualización del inventario de skills | 2 | `docs/tfm/revision/05_statistics_findings.md`, `docs/tfm/revision/00_baseline.md` | no |
| 49 | `a6a5f40` | 2026-09-03 22:39 | revision/auditoria | Revisión integral: auditoría de referencias consolidada (BLOCKED, 4 mayores) | 1 | `docs/tfm/revision/06_reference_findings.md` | no |
| 50 | `ee5cb0b` | 2026-09-03 22:40 | revision/auditoria | Revisión integral: auditoría RAG consolidada (FAIL, 11 mayores) | 1 | `docs/tfm/revision/02_rag_findings.md` | no |
| 51 | `880a4eb` | 2026-09-03 22:43 | revision/auditoria | Revisión integral: auditoría experimental consolidada (FAIL, 12 mayores) | 1 | `docs/tfm/revision/03_experiment_findings.md` | no |
| 52 | `8725ea1` | 2026-09-03 22:57 | revision/auditoria | Revisión integral: verificación de evidencia consolidada (FAIL, 11 mayores, 78 claims) | 1 | `docs/tfm/revision/04_evidence_findings.md` | no |
| 53 | `1162d1e` | 2026-09-03 23:30 | revision/auditoria | Revisión integral: evaluación académica del tutor consolidada (FAIL 55/99, 13 mayores) | 1 | `docs/tfm/revision/01_tutor_findings.md` | no |
| 54 | `cda9676` | 2026-09-03 23:32 | revision/auditoria | Revisión integral: plan de corrección consolidado (STOP GATE 1) | 1 | `docs/tfm/revision/07_correction_plan.md` | no |
| 55 | `af008f9` | 2026-09-03 23:33 | revision/auditoria | Revisión: rutas del entorno de trabajo escritas de forma neutra en los documentos de revisión | 2 | `docs/tfm/revision/00_baseline.md`, `docs/tfm/revision/02_rag_findings.md` | no |
| 56 | `42116d6` | 2026-09-03 23:55 | revision/auditoria | Plan de corrección detallado: reclasificación de severidad, reejecuciones y decisiones | 4 | `docs/tfm/revision/07_correction_plan.md`, `docs/tfm/revision/07b_reexecution_plan.md`, `docs/tfm/revision/07c_claim_impact_matrix.md` | no |
| 57 | `f6396fe` | 2026-09-04 00:07 | tests, src | Grupo 1 · P-06 y RX-00: corregir los tres defectos de instrumento y registrar la ejecución | 9 | `src/mecanico_ia_exp/experiments/sufficiency_runner.py`, `src/mecanico_ia_exp/experiments/registro.py`, `tests/test_evidence.py` | no |
| 58 | `081c309` | 2026-09-04 00:08 | docs | Criterio del umbral de suficiencia, fijado antes de ejecutar el barrido | 1 | `docs/methodology/criterio-umbral.md` | no |
| 59 | `f9c5c0c` | 2026-09-04 00:10 | artefactos, src | RX-04: barrido del umbral registrado como artefacto sobre validación | 4 | `experiments/E15b_barrido_umbral.json`, `src/mecanico_ia_exp/experiments/threshold_runner.py`, `tests/test_sufficiency.py` | no |
| 60 | `35d2360` | 2026-09-04 00:15 | docs | ENM-U01: enmienda al criterio del umbral, con regla de estabilidad cuantitativa | 1 | `docs/methodology/criterio-umbral-enmienda-01.md` | no |
| 61 | `f1d76d7` | 2026-09-04 00:18 | src, artefactos | ENM-U01 aplicada: el punto de operación pasa a 0,79 con su procedencia registrada | 4 | `src/mecanico_ia_exp/experiments/threshold_runner.py`, `experiments/E15b_barrido_umbral.json`, `src/mecanico_ia_exp/abstention/sufficiency.py` | no |
| 62 | `24e94d1` | 2026-09-04 00:19 | artefactos | RX-01: suficiencia reejecutada con instrumento corregido y umbral 0,79 | 1 | `experiments/E15_suficiencia.json` | no |
| 63 | `68cb5f5` | 2026-09-04 00:21 | docs, suficiencia/evidencia | P-05 y P-06C: separar lo medido de lo invariante y declarar la selección de época | 3 | `docs/methodology/metrics.md`, `docs/experiments/E7_modelo_temporal.md`, `src/mecanico_ia_exp/evidence/assembly.py` | no |
| 64 | `ed27aad` | 2026-09-04 00:47 | artefactos | RX-02: agente reejecutado en las tres configuraciones con el denominador corregido | 4 | `experiments/E13_agente_transformers.json`, `experiments/E13_agente_transformers-lora.json`, `experiments/E13_agente_transformers-lora@slm_lora_v2.json` | no |
| 65 | `14f800a` | 2026-09-04 00:51 | artefactos, datos/corpus/config | P-03: las cuatro condiciones se extienden de un fallo a tres, y aparece un fallo del verificador | 2 | `experiments/E15_suficiencia.json`, `configs/goldset_mazda3_bk.yaml` | no |
| 66 | `8c3ec98` | 2026-09-04 06:06 | suficiencia/evidencia, src | El registro de suficiencia estampa la versión de la política | 2 | `src/mecanico_ia_exp/abstention/sufficiency.py`, `src/mecanico_ia_exp/experiments/sufficiency_runner.py` | no |
| 67 | `be3d897` | 2026-09-04 06:07 | artefactos, docs | Congelar el resultado del verificador v1 y registrar el hallazgo que reveló | 3 | `experiments/E15_suficiencia_verifier_v1.json`, `docs/experiments/hallazgo-lexical-support-confound.md`, `experiments/E15_suficiencia.json` | no |
| 68 | `c474e81` | 2026-09-04 06:08 | docs | Política de suficiencia v2, documentada antes de implementarse | 1 | `docs/methodology/politica-suficiencia-v2.md` | no |
| 69 | `100082d` | 2026-09-04 06:11 | suficiencia/evidencia, tests | Verificador v2: el soporte exige que el fragmento sea un procedimiento | 5 | `tests/test_support_policy_v2.py`, `src/mecanico_ia_exp/evidence/support.py`, `tests/test_sufficiency.py` | no |
| 70 | `9d44037` | 2026-09-04 06:13 | artefactos | Verificador v2 medido sobre los mismos casos: 14/17, con una abstención falsa nueva | 2 | `experiments/E15_suficiencia_verifier_v2.json`, `experiments/E15_suficiencia.json` | no |
| 71 | `c1108b8` | 2026-09-04 06:31 | docs | Política de suficiencia v2.1, documentada antes de implementarse | 1 | `docs/methodology/politica-suficiencia-v2-1.md` | no |
| 72 | `a34bab2` | 2026-09-04 06:37 | tests, suficiencia/evidencia | Verificador v2.1: la seccion como unidad de papel | 4 | `tests/test_support_policy_v2_1.py`, `src/mecanico_ia_exp/evidence/support.py`, `tests/test_sufficiency.py` | sí |
| 73 | `10ed541` | 2026-09-04 06:41 | artefactos, docs | Resultado del verificador v2.1: 15/17, sin regresiones nuevas | 3 | `experiments/E15_suficiencia_verifier_v2_1.json`, `experiments/E15_suficiencia.json`, `docs/experiments/resultado-verificador-v2-1.md` | sí |
| 74 | `478ebe0` | 2026-09-04 06:41 | docs | Impacto del nuevo resultado canonico de E15 sobre lo ya escrito | 1 | `docs/experiments/resultado-verificador-v2-1.md` | sí |
| 75 | `1a58376` | 2026-09-04 07:08 | tests, artefactos | Ausencia de correspondencia de senal, declarada en vez de silenciada | 6 | `experiments/E15_suficiencia.json`, `tests/test_signal_mapping.py`, `docs/methodology/limitacion-vocabulario-senales.md` | sí |
| 76 | `f290263` | 2026-09-04 07:09 | docs | Politica de evaluacion no oracular y adversa, congelada antes de medir | 1 | `docs/methodology/politica-evaluacion-no-oracular.md` | sí |
| 77 | `43f56dc` | 2026-09-04 07:11 | src, infra/config | Modos no oracular y adverso del experimento de suficiencia | 2 | `src/mecanico_ia_exp/experiments/sufficiency_runner.py`, `src/mecanico_ia_exp/cli.py` | sí |
| 78 | `3b02cf8` | 2026-09-04 07:12 | artefactos, src | Corregir el nombre de artefacto en el mensaje final del runner | 3 | `experiments/E15_suficiencia_non_oracle.json`, `experiments/E15_suficiencia.json`, `src/mecanico_ia_exp/experiments/sufficiency_runner.py` | sí |
| 79 | `f34f625` | 2026-09-04 07:14 | artefactos, docs | Enmienda ENM-A01: el escenario adverso elige el error mas confiado | 2 | `experiments/E15_suficiencia_adverse.json`, `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md` | sí |
| 80 | `c502f9a` | 2026-09-04 07:14 | artefactos, src | Aplicar ENM-A01 y congelar la primera ejecucion adversa | 3 | `experiments/E15_suficiencia_adverse_seleccion_por_indice.json`, `src/mecanico_ia_exp/experiments/sufficiency_runner.py`, `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md` | sí |
| 81 | `465563a` | 2026-09-04 07:17 | artefactos, docs | Resultados NX-01 y NX-02, y hallazgo EMPTY-DTC-GATE-BYPASS | 4 | `experiments/E15_suficiencia_adverse.json`, `docs/experiments/resultado-no-oracular-y-adverso.md`, `docs/experiments/hallazgo-puerta-dtc-ausente.md` | sí |
| 82 | `9139dcd` | 2026-09-04 07:38 | docs | Politica de la puerta de DTC, documentada antes de implementarse | 1 | `docs/methodology/politica-puerta-dtc.md` | sí |
| 83 | `4c17732` | 2026-09-04 07:39 | suficiencia/evidencia, src | Puerta de DTC con requisito explicito (v2.2), IMPLEMENTED sin ejecutar | 5 | `src/mecanico_ia_exp/evidence/support.py`, `src/mecanico_ia_exp/experiments/sufficiency_runner.py`, `src/mecanico_ia_exp/evidence/assembly.py` | sí |
| 84 | `0292f72` | 2026-09-04 11:02 | docs, revision/auditoria | Decisiones del autor tras las cinco auditorias, y lineas base | 2 | `docs/methodology/lineas-base.md`, `docs/tfm/revision/08_decisiones_autor_20260904.md` | sí |
| 85 | `3964961` | 2026-09-04 11:04 | docs | Condicion distractor invalidada, rediseno adversarial y refutacion del filtro de motor | 3 | `docs/methodology/politica-condicion-distractor.md`, `docs/experiments/hallazgo-filtro-motor.md`, `docs/methodology/diseno-adversarial-v2.md` | sí |
| 86 | `7a3ef51` | 2026-09-04 11:05 | tests, suficiencia/evidencia | Pruebas de v2.2 en las ocho categorias exigidas, y una correccion que destaparon | 3 | `tests/test_support_policy_v2_2.py`, `src/mecanico_ia_exp/evidence/support.py`, `tests/test_support_policy_v2.py` | sí |
| 87 | `54071a2` | 2026-09-04 12:58 | docs | Politica de aislamiento del espacio de embeddings, antes de tocar codigo | 1 | `docs/methodology/politica-espacio-de-embeddings.md` | sí |
| 88 | `c6a95be` | 2026-09-04 12:59 | artefactos, tests | Pruebas que reproducen MIXED-EMBEDDING-SPACE, y artefactos congelados | 9 | `experiments/pre_mixed_embedding_fix/E15_suficiencia_verifier_v2.json`, `experiments/pre_mixed_embedding_fix/E15_suficiencia_non_oracle.json`, `experiments/pre_mixed_embedding_fix/E15_suficiencia.json` | sí |
| 89 | `43e2e87` | 2026-09-04 13:04 | tests, docs | Corregir MIXED-EMBEDDING-SPACE: el espacio se deriva del proveedor | 5 | `tests/test_embedding_space_isolation.py`, `docs/methodology/politica-espacio-de-embeddings.md`, `tests/test_rag_pipeline.py` | sí |
| 90 | `6b5b92d` | 2026-09-04 13:04 | docs | Plan de reejecucion canonica, pendiente del gate de diseno | 1 | `docs/methodology/plan-reejecucion-canonica.md` | sí |
| 91 | `3845c07` | 2026-09-04 13:59 | src, docs | Pre-registro de RERUN-A, congelado antes de cualquier medicion | 6 | `docs/methodology/preregistro-rerun-a.md`, `tests/test_embedding_space_isolation.py`, `src/mecanico_ia_exp/rag/store.py` | sí |
| 92 | `b79dfa7` | 2026-09-04 14:03 | docs | Plan corregido y estados provisionales del ciclo | 2 | `docs/methodology/estados-provisionales.md`, `docs/methodology/plan-reejecucion-canonica.md` | sí |
| 93 | `7ff9949` | 2026-09-04 16:28 | docs, tests | Correcciones de los tres gates: procedencia, conjunto acotado y ENM-S01 | 11 | `tests/test_contrato_rerun_a.py`, `src/mecanico_ia_exp/experiments/retrieval_runner.py`, `docs/methodology/preregistro-rerun-a.md` | sí |
| 94 | `df003f0` | 2026-09-04 16:56 | docs, datos/corpus/config | Mapa congelado, manifiesto de estado y ENM-S02 | 9 | `tests/test_contrato_rerun_a.py`, `docs/methodology/preregistro-rerun-a.md`, `configs/manifest_rerun_a.json` | sí |
| 95 | `57b6c93` | 2026-09-04 17:08 | datos/corpus/config, tests | Corregir el mapa congelado: omitia F04_o2_lag | 4 | `tests/test_contrato_rerun_a.py`, `docs/methodology/estados-provisionales.md`, `configs/e12_legacy_dtc_map.json` | sí |
| 96 | `aed6fe2` | 2026-09-04 17:12 | docs, datos/corpus/config | Cerrar residuos: la tabla legacy sale de la columna «antes» | 2 | `docs/methodology/plan-reejecucion-canonica.md`, `configs/manifest_rerun_a.json` | sí |
| 97 | `7d52627` | 2026-09-04 18:39 | docs, tests | ENM-S03 y el dispositivo como quinta variable | 3 | `docs/methodology/preregistro-rerun-a.md`, `tests/test_contrato_rerun_a.py`, `configs/manifest_rerun_a.json` | sí |
| 98 | `9c388d9` | 2026-09-10 00:46 | memoria, infra | Memoria: resolver las marcas editoriales y separar las preguntas al director | 15 | `docs/memoria/cap1_introduccion.md`, `docs/memoria/preguntas-abiertas-al-director.md`, `docs/audits/tutor_observations/01-template-audit.md` | no |
| 99 | `1d61772` | 2026-09-10 00:47 | memoria | Objetivos: desarrollar OE4 con sus cuatro fases y el estado real de sus metricas | 1 | `docs/memoria/cap2_objetivos.md` | no |
| 100 | `191bd84` | 2026-09-10 00:48 | memoria | Formalizar el Mazda 3 BK 2007 como vehiculo de referencia | 3 | `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap5_resultados.md`, `docs/memoria/cap2_objetivos.md` | no |
| 101 | `a80f14a` | 2026-09-10 00:49 | memoria | Conclusiones: L-17, los resultados describen un solo vehiculo | 1 | `docs/memoria/cap6_conclusiones.md` | no |
| 102 | `77281a9` | 2026-09-10 00:50 | memoria | Marco teorico: desarrollar los cuatro frentes y cerrar cada uno con su limite | 1 | `docs/memoria/cap3_marco_teorico.md` | no |
| 103 | `2550bc1` | 2026-09-10 00:57 | memoria, revision/auditoria | Verificar cuatro referencias en fuente primaria: una no sostiene lo citado | 4 | `docs/audits/tutor_observations/05-reference-sample-audit.md`, `docs/memoria/cap3_marco_teorico.md`, `docs/memoria/bibliografia.md` | no |
| 104 | `e2151ca` | 2026-09-10 00:58 | revision/auditoria, memoria | Matriz de alineacion, y corregir la asignacion de subpreguntas en OE4 | 2 | `docs/audits/tutor_observations/06-alignment-matrix.md`, `docs/memoria/cap2_objetivos.md` | no |
| 105 | `701f1c4` | 2026-09-10 01:07 | memoria | OE4: corregir los hallazgos de la auditoria experimental y estadistica | 1 | `docs/memoria/cap2_objetivos.md` | no |
| 106 | `d0866ce` | 2026-09-10 01:16 | memoria, revision/auditoria | OE4, iteracion 2: corregir lo que la reevaluacion encontro, incluido lo mio | 2 | `docs/memoria/cap2_objetivos.md`, `docs/audits/tutor_observations/06-alignment-matrix.md` | no |
| 107 | `6b65345` | 2026-09-10 06:45 | memoria | Objetivos: ajustar el capitulo a las 3 paginas que recomienda la plantilla | 2 | `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap4_marco_metodologico.md` | no |
| 108 | `dc12963` | 2026-09-10 06:47 | memoria | Objetivos: recuperar OE5, que el traslado se habia llevado, y corregir su presentacion | 2 | `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap4_marco_metodologico.md` | no |
| 109 | `f210021` | 2026-09-10 06:49 | memoria | Memoria: retirar las referencias a la plantilla del cuerpo del texto | 2 | `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap1_introduccion.md` | no |
| 110 | `94a08e4` | 2026-09-10 06:56 | memoria | Marco teorico: corregir una atribucion que contradecia a sus dos fuentes | 2 | `docs/memoria/cap3_marco_teorico.md`, `docs/memoria/bibliografia.md` | no |
| 111 | `4223508` | 2026-09-10 06:58 | memoria | Memoria: sacar los bloques de estado editorial del cuerpo de los capitulos | 9 | `docs/memoria/cap2_objetivos.md`, `docs/memoria/LEEME.md`, `docs/memoria/cap5_resultados.md` | no |
| 112 | `4a87700` | 2026-09-10 07:02 | memoria, revision/auditoria | OE4: voz academica en lugar de inventario de fases, y terminologia de validacion | 3 | `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap4_marco_metodologico.md`, `docs/audits/tutor_observations/06-alignment-matrix.md` | no |
| 113 | `ae9dfc3` | 2026-09-10 07:04 | memoria | Conclusiones: acotar el «si puede» a lo que la evidencia sostiene | 1 | `docs/memoria/cap6_conclusiones.md` | no |
| 114 | `a0cc296` | 2026-09-10 07:05 | memoria | Conclusiones: acotar la mitad de trazabilidad y declarar dos negativos no reportados | 1 | `docs/memoria/cap6_conclusiones.md` | no |
| 115 | `0c519fe` | 2026-09-10 07:10 | memoria, research | Declarar en la memoria el hallazgo que congela las cifras de recuperacion | 4 | `research/limitations-register.md`, `docs/memoria/cap6_conclusiones.md`, `docs/memoria/cap5_resultados.md` | no |
| 116 | `2903ecb` | 2026-09-10 07:11 | memoria | Resultados: declarar las cinco discrepancias y el oraculo de la comparacion | 1 | `docs/memoria/cap5_resultados.md` | no |
| 117 | `5e87ae8` | 2026-09-10 07:14 | memoria, research | Bibliografia: propagar las verificaciones a la lista maestra y corregir el apellido | 6 | `docs/memoria/LEEME.md`, `research/references/references.md`, `docs/memoria/cap3_marco_teorico.md` | no |
| 118 | `76e1046` | 2026-09-10 07:27 | memoria | Resultados: alinear las subpreguntas con el estado real y retirar la defensa doble | 1 | `docs/memoria/cap5_resultados.md` | no |
| 119 | `0f5e3b0` | 2026-09-10 12:33 | memoria | Memoria: sustituir el lenguaje metadocumental por lenguaje de metodo | 5 | `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap3_marco_teorico.md`, `docs/memoria/cap5_resultados.md` | no |
| 120 | `b5ca3b3` | 2026-09-10 12:39 | memoria | Memoria: corregir el capitulo 1 y alinear los estados de fase con el indice | 3 | `docs/memoria/cap1_introduccion.md`, `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap4_marco_metodologico.md` | no |
| 121 | `32c6a7d` | 2026-09-10 12:40 | memoria | Bibliografia: transcribir los datos que la lista maestra ya tenia | 1 | `docs/memoria/bibliografia.md` | no |
| 122 | `b0e13e2` | 2026-09-10 12:40 | research | Fichero de citas: desambiguar las claves repetidas | 1 | `research/references/bibliography.bib` | no |
| 123 | `0400ed2` | 2026-09-10 12:42 | docs | Politica de expresion academica del TFM, vinculante | 1 | `docs/methodology/politica-expresion-academica.md` | no |
| 124 | `835a317` | 2026-09-10 12:51 | revision/auditoria | Registrar SD-01: dos preguntas de investigacion en circulacion, con evidencia | 1 | `docs/audits/full_memory_review/11_BLOCKERS_AND_DECISIONS.md` | no |
| 125 | `5a61194` | 2026-09-10 12:53 | revision/auditoria | Inventario del trabajo para la revision integral | 1 | `docs/audits/full_memory_review/00_INVENTORY.md` | no |
| 126 | `615ebeb` | 2026-09-10 12:53 | revision/auditoria | Matriz de trazabilidad de la pregunta, con sus cinco huecos | 1 | `docs/audits/full_memory_review/01_PI_TRACEABILITY_MATRIX.md` | no |
| 127 | `4a0c6d8` | 2026-09-10 12:54 | memoria | Objetivos: ajustar al limite de la plantilla | 1 | `docs/memoria/cap2_objetivos.md` | no |
| 128 | `d0fa412` | 2026-09-10 13:04 | memoria, research | Cerrar cuatro observaciones del tutor y ajustar el capitulo 2 a la plantilla | 7 | `docs/memoria/cap2_objetivos.md`, `research/limitations-register.md`, `docs/memoria/cap6_conclusiones.md` | sí |
| 129 | `cc7eefd` | 2026-09-10 13:05 | revision/auditoria | Registro de correcciones: iteracion 3 | 1 | `docs/audits/full_memory_review/12_CORRECTION_LOG.md` | sí |
| 130 | `456e9a0` | 2026-09-10 13:23 | memoria | Objetivos: apertura con funcion metodologica en lugar de descripcion del documento | 1 | `docs/memoria/cap2_objetivos.md` | sí |
| 131 | `1d368e0` | 2026-09-10 13:26 | memoria | Introduccion: la presentacion presenta, y la trazabilidad se va a metodologia | 2 | `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap1_introduccion.md` | sí |
| 132 | `32e7c99` | 2026-09-10 13:31 | memoria | Resumen: reescrito segun la plantilla, con abstract en ingles | 2 | `docs/memoria/00_resumen.md`, `docs/memoria/cap4_marco_metodologico.md` | sí |
| 133 | `038c20c` | 2026-09-10 13:42 | memoria, revision/auditoria | Resumen del autor, y la comprobacion del ciclo de la pregunta | 2 | `docs/memoria/00_resumen.md`, `docs/audits/full_memory_review/02_PI_CYCLE_CLOSURE.md` | sí |
| 134 | `6f0e21d` | 2026-09-10 14:06 | memoria | Introduccion: 1.2 con el orden del argumento y la pregunta completa | 1 | `docs/memoria/cap1_introduccion.md` | sí |
| 135 | `12b665a` | 2026-09-10 14:12 | memoria | Objetivos: los objetivos concretan la pregunta, no la transforman | 1 | `docs/memoria/cap2_objetivos.md` | sí |
| 136 | `d7bdaef` | 2026-09-10 14:17 | memoria | Objetivos: objetivo general alineado con la pregunta, y fuera la historia editorial | 1 | `docs/memoria/cap2_objetivos.md` | sí |
| 137 | `6515210` | 2026-09-10 14:40 | memoria, research | Objetivos especificos reescritos, y las dos capacidades sin instrumentar declaradas | 4 | `docs/memoria/cap2_objetivos.md`, `research/limitations-register.md`, `docs/memoria/cap6_conclusiones.md` | sí |
| 138 | `d3ddde8` | 2026-09-10 15:06 | memoria | Marco teorico: agosto como metodologia, y fuera los resultados propios | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 139 | `c395368` | 2026-09-10 15:07 | memoria | Marco teorico: lo que la revision puede sostener, y no mas | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 140 | `43e1151` | 2026-09-10 15:15 | memoria | Marco teorico: precision en 3.1 y declaracion del alcance de PRISMA | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 141 | `521123c` | 2026-09-10 16:05 | memoria | Marco teorico: teoria en el capitulo 3, metodo en el 4, y que es un patron no representado | 2 | `docs/memoria/cap3_marco_teorico.md`, `docs/memoria/bibliografia.md` | sí |
| 142 | `6f7ec0f` | 2026-09-10 17:20 | memoria, revision/auditoria | Normalizar tablas y figuras, y dejar el criterio en un skill | 4 | `docs/audits/full_memory_review/14_TABLES_FIGURES_INVENTORY.md`, `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap2_objetivos.md` | sí |
| 143 | `c617d14` | 2026-09-10 18:47 | memoria, revision/auditoria | Poblacion y muestra: prosa academica, y el resultado de ventana fuera del metodo | 2 | `docs/memoria/cap4_marco_metodologico.md`, `docs/audits/full_memory_review/15_PENDING_CH5_INSERTIONS.md` | sí |
| 144 | `5e7f95d` | 2026-09-10 18:49 | revision/auditoria, memoria | Primera entrega: diagnostico, informe de preparacion y niveles de agregacion | 3 | `docs/audits/first_submission/FIRST_SUBMISSION_READINESS_REPORT.md`, `docs/audits/first_submission/FIRST_SUBMISSION_DIAGNOSTIC.md`, `docs/memoria/cap4_marco_metodologico.md` | sí |
| 145 | `66198d9` | 2026-09-10 22:35 | memoria, docs | Objetivos alcanzan la pregunta, y se disena lo que falta para ejecutarlos | 4 | `docs/methodology/diseno-gates-pi-pendientes.md`, `docs/memoria/cap2_objetivos.md`, `docs/memoria/cap4_marco_metodologico.md` | sí |
| 146 | `3d7ab90` | 2026-09-11 03:52 | memoria | Memoria: un parrafo, una linea | 8 | `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap3_marco_teorico.md`, `docs/memoria/cap5_resultados.md` | sí |
| 147 | `e7aeb14` | 2026-09-11 04:13 | memoria | Muestra: caracterizacion legible, y las doce senales con su propia tabla | 1 | `docs/memoria/cap4_marco_metodologico.md` | sí |
| 148 | `95d4e71` | 2026-09-11 05:08 | memoria | Fase de recuperacion: informacion documental, no evidencia todavia | 1 | `docs/memoria/cap4_marco_metodologico.md` | sí |
| 149 | `6d95a25` | 2026-09-11 05:17 | memoria, revision/auditoria | Fases del agente: diseno en el capitulo 4, incidentes en el 5 | 2 | `docs/memoria/cap4_marco_metodologico.md`, `docs/audits/full_memory_review/15_PENDING_CH5_INSERTIONS.md` | sí |
| 150 | `e4dfdf1` | 2026-09-11 05:44 | memoria | Reproducibilidad: separada del control de calidad, y la huella dice sobre que se calcula | 1 | `docs/memoria/cap4_marco_metodologico.md` | sí |
| 151 | `4cac4ae` | 2026-09-11 05:49 | memoria | Modelo de analisis: analisis, no resultados previstos | 1 | `docs/memoria/cap4_marco_metodologico.md` | sí |
| 152 | `cd52cdb` | 2026-09-11 05:51 | memoria | Marco teorico: romper la enumeracion formulaica de las cinco situaciones | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 153 | `37f1294` | 2026-09-11 05:54 | memoria | Conclusiones: alineadas con la pregunta, y sin el exceso de forma | 1 | `docs/memoria/cap6_conclusiones.md` | sí |
| 154 | `0b0864b` | 2026-09-11 05:57 | memoria | Introduccion: deshacer un eco entre parrafos contiguos | 1 | `docs/memoria/cap1_introduccion.md` | sí |
| 155 | `8be7fc2` | 2026-09-11 06:04 | memoria, revision/auditoria | Conclusiones provisionales para la primera entrega | 2 | `docs/memoria/cap6_conclusiones.md`, `docs/audits/full_memory_review/16_CH6_PROVISIONAL_CUSTODY.md` | sí |
| 156 | `4e9e4a6` | 2026-09-11 06:05 | memoria | Conclusiones: ritmo y ultimo conector de apertura | 1 | `docs/memoria/cap6_conclusiones.md` | sí |
| 157 | `daddffd` | 2026-09-11 06:11 | memoria | Separar prospectiva de trabajo pendiente dentro del TFM | 2 | `docs/memoria/cap6_conclusiones.md`, `docs/memoria/cap4_marco_metodologico.md` | sí |
| 158 | `4a6358b` | 2026-09-11 07:00 | memoria | Marco teorico: reescribir el proposito y procedimiento de la revision | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 159 | `9bb8c6c` | 2026-09-11 07:11 | memoria, docs | Fijar la voz de referencia del TFM y aplicarla donde mas se desviaba | 4 | `docs/methodology/politica-expresion-academica.md`, `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap6_conclusiones.md` | sí |
| 160 | `23208b0` | 2026-09-11 07:14 | memoria | Marco teorico: aplicar la voz de referencia a todo el capitulo | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 161 | `e5242d0` | 2026-09-11 07:17 | memoria | Marco teorico: moderar el vaiven del proposito y procedimiento | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 162 | `8220261` | 2026-09-11 07:34 | docs, memoria | Fijar el criterio de escritura del TFM | 3 | `docs/methodology/criterio-de-escritura.md`, `docs/memoria/cap3_marco_teorico.md`, `docs/methodology/politica-expresion-academica.md` | sí |
| 163 | `fad82f6` | 2026-09-11 07:40 | memoria | Marco teorico: devolver al proposito y procedimiento su registro denso | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 164 | `03ab04f` | 2026-09-11 07:43 | memoria | Marco teorico: registro denso en todo el capitulo | 1 | `docs/memoria/cap3_marco_teorico.md` | sí |
| 165 | `0505a2b` | 2026-09-13 11:17 | memoria | Observaciones del tutor: lo que no depende de la decision sobre la pregunta | 3 | `docs/memoria/00_resumen.md`, `docs/memoria/cap4_marco_metodologico.md`, `docs/memoria/cap1_introduccion.md` | sí |
| 166 | `4cb4de5` | 2026-09-13 11:24 | memoria, research | ADR-004: la pregunta canonica es la acotada, decidido por la direccion | 10 | `research/decisions/ADR-004-pregunta-de-investigacion-canonica.md`, `research/limitations-register.md`, `docs/memoria/cap3_marco_teorico.md` | sí |
| 167 | `089d48f` | 2026-09-13 11:36 | revision/auditoria, docs | Cerrar el feedback del tutor tambien fuera de la memoria | 9 | `docs/methodology/diseno-gates-pi-pendientes.md`, `docs/methodology/criterio-de-escritura.md`, `docs/audits/full_memory_review/14_TABLES_FIGURES_INVENTORY.md` | sí |
| 168 | `636cf15` | 2026-09-13 12:27 | memoria, revision/auditoria | Retirar las marcas de trabajo del capitulo 4 y documentar las del 5 | 3 | `docs/memoria/cap4_marco_metodologico.md`, `docs/audits/full_memory_review/15_PENDING_CH5_INSERTIONS.md`, `docs/memoria/00_resumen.md` | sí |
| 169 | `167e17e` | 2026-09-13 13:16 | memoria | Registro denso en los dos apartados que quedaban | 2 | `docs/memoria/cap6_conclusiones.md`, `docs/memoria/cap4_marco_metodologico.md` | sí |
| 170 | `3b001d4` | 2026-09-13 17:35 | docs, memoria | Introduccion: anunciar el vacio, que solo vivia en el capitulo 3 | 3 | `docs/experiments/E7_modelo_temporal.md`, `docs/experiments/E1_entorno.md`, `docs/memoria/cap1_introduccion.md` | sí |

## 3. Referencias a herramientas detectadas

Búsqueda en los 170 mensajes de commit y en los 312 ficheros versionados (excluidos
`.git`, `.venv`, cachés y `uv.lock`) de: `Co-Authored-By`, `Claude`, `Anthropic`, `Fable`,
`Generated`, `AI-generated`, `Generated by`, `Assisted by`, `Copilot`, `ChatGPT`, `OpenAI`,
`Gemini`, `created by AI`, `assistant`, `LLM-generated`, `Claude Code`, `skill`, `.claude/`,
`session_`.

Clasificación: **A** metadato automático prescindible · **B** comentario interno prescindible ·
**C** documentación técnicamente necesaria · **D** dependencia/integración real del sistema ·
**E** contenido histórico que no debería modificarse.

### 3.1 En los mensajes de commit

| Archivo/Commit | Referencia | Clasificación | Acción propuesta |
|---|---|---|---|
| 69 commits (posiciones 72–97, 128–170 salvo huecos; lista exacta en §5.1) | Trailer `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>` | **A** | Eliminar la línea del mensaje. No representa autoría humana: el único autor de los 170 commits es el autor del TFM |
| Los mismos 69 commits | Trailer `Claude-Session: https://claude.ai/code/session_01BxABErdF9ssaDxuxRUb1Dk` (26 commits, 04-09) y `…session_01J6War2vaULRmaHQZYtffHr` (43 commits, 10-09 a 13-09) | **A** | Eliminar la línea del mensaje. Es un enlace a una sesión privada de la herramienta, sin valor técnico para un lector del repositorio |
| Cuerpos de los 170 mensajes | Ninguna otra coincidencia (ni «Claude», ni «generado», ni «assisted», etc. fuera de los dos trailers) | — | Nada. Los cuerpos describen el cambio técnico y se conservan íntegros |

### 3.2 En los ficheros versionados

| Archivo | Referencia | Clasificación | Acción propuesta |
|---|---|---|---|
| `src/mecanico_ia_exp/config/settings.py:16` | `LLMProviderName = Literal["openai_compatible", "anthropic", "ollama", "echo"]` | **D** | Conservar: es el tipo de proveedor LLM del sistema |
| `.env.example:20` | `#   openai_compatible \| anthropic \| ollama \| echo` | **D** | Conservar: documenta los valores válidos de `LLM_PROVIDER` |
| `docs/setup/llm-providers.md:36-37,46` | Tabla de proveedores (`openai_compatible`, `anthropic`) | **C/D** | Conservar: documentación de configuración del sistema |
| `docs/plan_experimental_macbook.md:168` | «Abstracción de proveedores LLM … proveedores remotos por API» | **C** | Conservar |
| `src/mecanico_ia_exp/llm/agent.py:219`, `llm/training_data.py:190,207` | `"role": "assistant"` | **D** | Conservar: rol del protocolo de chat que consume el agente y el conjunto de ajuste |
| `research/references/bibliography.bib:1155`, `references.md:145` | «LLM-Based Automotive Assistant» (título de REF-107) | **C** | Conservar: título de una referencia bibliográfica |
| `research/available-skills.md` (todo el fichero, 6 coincidencias) | Inventario de los skills de auditoría del autor (`TFM/.claude/skills/`, `~/.claude/skills/`), con fechas de uso | **B/E** | Decisión del autor (ver §5.3). Documenta el proceso de revisión con asistentes; no es arquitectura del sistema ni resultado. Propuesta por defecto: conservar, porque los informes de revisión versionados (`docs/tfm/revision/`, `docs/audits/`) se remiten a él y retirarlo dejaría esas remisiones sin destino |
| `docs/tfm/revision/00_baseline.md:39-61,97,102,159` (26 coincidencias) | Inventario de once skills, conflictos CONFLICT-SK-01/06, ubicación de informes fuera del repositorio | **E** | Conservar: es el informe de línea base de una revisión ya consolidada y referenciada por commits posteriores |
| `docs/tfm/cambio_pi_eliminacion_datos_reales.md:5,97,215,223,240,245` | «Skill aplicado: `uax-tfm-ai-researcher`»; ruta `TFM/.claude/skills/uax-tfm-ai-researcher/references/project/` («fuera del repositorio Git») | **E** con un matiz **B** | Conservar el documento (informe de impacto de ADR-003). La ruta `TFM/.claude/skills/...` a un directorio externo al repositorio no aporta nada al lector: se propone sustituirla por «espejo del marco de investigación, fuera del repositorio» (mismo tratamiento que aplicó el commit `af008f9` al resto de rutas del entorno) |
| `docs/tfm/revision/01_tutor_findings.md`, `02_rag_findings.md:72`, `04_evidence_findings.md:3`, `05_statistics_findings.md:3`, `06_reference_findings.md:3` | Cabeceras «Skill: …» y ruta `skills/uax-tfm-ai-tutor/scripts/finding_ledger.py` (hallazgo RAG-INF-010) | **E** | Conservar: informes de auditoría consolidados, citados por el plan de corrección y por commits posteriores |
| `docs/audits/first_submission/FIRST_SUBMISSION_DIAGNOSTIC.md:15` | «definiciones de los once skills en `TFM/.claude/skills/`» | **E** con matiz **B** | Conservar el documento; misma sustitución de ruta externa que arriba |
| `docs/audits/full_memory_review/00_INVENTORY.md`, `research/prereg-classification.md`, `docs/methodology/politica-expresion-academica.md` | Mención genérica a «skill» (1–2 coincidencias cada uno) | **E** | Conservar |
| `tutor-reports/TUTOR-REPORT-20260903.md:8,287,298` | Rutas `TFM/.claude/skills/uax-tfm-ai-researcher/...` y `TFM/.claude/skills/uax-tfm-ai-tutor/` | **E** con matiz **B** | Conservar el informe; misma sustitución de ruta externa. Además, decisión del autor: `tutor-reports/` es el único directorio del repositorio con un solo fichero y su contenido pertenece conceptualmente a `docs/audits/` (ver `docs/commit-plan.md`) |
| Cuadernos `notebooks/*.ipynb` | Ninguna coincidencia | — | Nada |
| Código `src/`, `tests/`, `scripts/`, `migrations/`, `configs/` | Ninguna coincidencia fuera de las de tipo D anteriores. No hay comentarios del tipo «generated by», «AI suggested», etc. | — | Nada |

Conclusión de la Fase 2: **no existe ningún comentario de código ni marca de documentación
del tipo «generado por IA»**. Las únicas referencias prescindibles son (a) los dos trailers
automáticos de 69 commits y (b) cuatro rutas a un directorio `.claude/skills/` externo al
repositorio, dentro de informes de revisión que por lo demás deben conservarse.

## 4. Cambios locales pendientes

En el momento de la auditoría el working tree estaba limpio: **no hay cambios locales
previos sin confirmar** que dividir.

Los únicos cambios pendientes son los que produce esta misma auditoría (todos ficheros
nuevos, ninguno modifica código ni resultados):

| Fichero nuevo | Contenido | Commit independiente propuesto |
|---|---|---|
| `docs/git-history-audit.md` | Este informe | `docs(git): auditoría del historial previa a la limpieza` |
| `docs/commit-plan.md` | Plan de commits | mismo commit que el anterior |
| `docs/git-history-report.md` | Tabla commit → propósito → acción (se completa tras la ejecución) | mismo commit |
| `docs/experiment-index.md` | Índice de experimentos con identificadores estables | `docs(experiments): índice de experimentos con estado y evidencia` |
| `docs/tfm-traceability.md` | Matriz objetivo → experimento → evidencia → sección | `docs(tfm): matriz de trazabilidad pregunta → experimento → evidencia` |
| `docs/reproducibility.md` | Entorno, versiones, semillas y comandos | `docs(reproducibility): entorno, versiones y comandos de reproducción` |
| `README.md`, `JURY_GUIDE.md` | Redactados como borrador, aprobados por el autor el 13-09 y confirmados en su ubicación definitiva | `docs: README de investigación y guía de revisión para el tribunal` |

## 5. Reescrituras propuestas

### 5.1 Qué se modificaría

Los **69 commits** siguientes (posición en el historial, hash actual, fecha): 72 `a34bab2`, 73 `10ed541`,
74 `478ebe0`, 75 `1a58376`, 76 `f290263`, 77 `43f56dc`, 78 `3b02cf8`, 79 `f34f625`, 80 `c502f9a`,
81 `465563a`, 82 `9139dcd`, 83 `4c17732`, 84 `0292f72`, 85 `3964961`, 86 `7a3ef51`, 87 `54071a2`,
88 `c6a95be`, 89 `43e2e87`, 90 `6b5b92d`, 91 `3845c07`, 92 `b79dfa7`, 93 `7ff9949`, 94 `df003f0`,
95 `57b6c93`, 96 `aed6fe2`, 97 `7d52627` (todos del 04-09-2026); 128 `d0fa412`, 129 `cc7eefd`,
130 `456e9a0`, 131 `1d368e0`, 132 `32e7c99`, 133 `038c20c`, 134 `6f0e21d`, 135 `12b665a`,
136 `d7bdaef`, 137 `6515210`, 138 `d3ddde8`, 139 `c395368`, 140 `43e1151`, 141 `521123c`,
142 `6f7ec0f`, 143 `c617d14`, 144 `5e7f95d`, 145 `66198d9` (10-09); 146 `3d7ab90`, 147 `e7aeb14`,
148 `95d4e71`, 149 `6d95a25`, 150 `e4dfdf1`, 151 `4cac4ae`, 152 `cd52cdb`, 153 `37f1294`,
154 `0b0864b`, 155 `8be7fc2`, 156 `4e9e4a6`, 157 `daddffd`, 158 `4a6358b`, 159 `9bb8c6c`,
160 `23208b0`, 161 `e5242d0`, 162 `8220261`, 163 `fad82f6`, 164 `03ab04f` (11-09); 165 `0505a2b`,
166 `4cb4de5`, 167 `089d48f`, 168 `636cf15`, 169 `167e17e`, 170 `3b001d4` (13-09).

**Por qué:** los dos trailers son metadatos insertados automáticamente por la herramienta
de desarrollo. No identifican a una persona, no describen el cambio y no forman parte del
registro científico.

**Qué se eliminaría:** exactamente las dos líneas finales de cada uno de esos mensajes:

```
Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_…
```

y la línea en blanco que las precede.

**Qué permanece intacto:** el asunto y el cuerpo de cada mensaje; los árboles (contenido de
los ficheros); autor, committer, AuthorDate y CommitDate; el orden de los commits; las
ramas y el backup. Se usaría `git filter-repo --message-callback` (disponible vía
`uvx --from git-filter-repo git-filter-repo`, verificado), que reescribe mediante
fast-export/fast-import y **conserva ambas fechas**. Alternativa integrada en Git:
`git filter-branch --msg-filter`, con el mismo efecto sobre fechas.

### 5.2 Efecto colateral inevitable: cambian los SHA de 99 commits

El primer commit con trailer ocupa la posición 72. Al cambiar su mensaje cambia su SHA y,
en cadena, el de **todos los descendientes**: los 99 commits desde `a34bab2` hasta `3b001d4`
reciben un SHA nuevo, incluidos los 30 de ese tramo que no tienen trailer. Los 71 primeros
commits (`3a2ce39` … `d0866ce`) conservan su SHA.

**Riesgo de trazabilidad detectado (motivo de parada).** 37 SHA de commits distintos se citan
textualmente en ficheros versionados como prueba de procedencia: en documentos de método y
auditoría («documentado antes de implementarse», «congelado en el commit…»), en el campo
`commit` de los registros JSON de `experiments/` y en `configs/manifest_rerun_a.json`
(`frozen_at_commit`). **15 de ellos pertenecen al tramo que se reescribiría**:

| SHA citado | Posición | Dónde se cita | Tipo de fichero |
|---|---:|---|---|
| `a34bab2` | 72 | `docs/experiments/resultado-verificador-v2-1.md`; `experiments/E15_suficiencia_verifier_v2_1.json` (+ copia en `pre_mixed_embedding_fix/`) | prosa + **registro congelado** |
| `1a58376` | 75 | `docs/methodology/politica-evaluacion-no-oracular.md` | prosa |
| `f290263` | 76 | `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md` | prosa |
| `43f56dc` | 77 | `experiments/E15_suficiencia.json`, `experiments/E15_suficiencia_non_oracle.json` (+ copias) | **registros congelados** |
| `3b02cf8` | 78 | `docs/methodology/politica-evaluacion-no-oracular-enmienda-01.md`; `experiments/E15_suficiencia_adverse_seleccion_por_indice.json` (+ copia) | prosa + **registro** |
| `c502f9a` | 80 | `experiments/E15_suficiencia_adverse.json` (+ copia) | **registro congelado** |
| `54071a2`, `c6a95be`, `43e2e87` | 87–89 | `docs/methodology/plan-reejecucion-canonica.md` | prosa |
| `aed6fe2` | 96 | `configs/manifest_rerun_a.json` (`frozen_at_commit`) | **pre-registro congelado** |
| `9c388d9` | 98 | `docs/memoria/LEEME.md` | prosa |
| `b0e13e2` | 122 | `docs/audits/full_memory_review/11_BLOCKERS_AND_DECISIONS.md`, `12_CORRECTION_LOG.md` | prosa |
| `835a317` | 124 | `docs/audits/full_memory_review/00_INVENTORY.md` | prosa |
| `5a61194` | 125 | `docs/audits/full_memory_review/01_PI_TRACEABILITY_MATRIX.md` | prosa |
| `d0fa412` | 128 | `docs/audits/full_memory_review/12_CORRECTION_LOG.md` | prosa |

Los otros 22 SHA citados están en las posiciones 15–70 y **no cambian** (entre ellos los
`commit` de `E13_agente_transformers*.json` → `68cb5f5`, `E15_suficiencia_verifier_v1.json` →
`8c3ec98`, `E15_suficiencia_verifier_v2.json` → `100082d`, `E15b_barrido_umbral.json` →
`35d2360`, y los de `configs/e12_legacy_dtc_map.json`).

Ninguna de las citas apunta a los trailers ni a fechas: apuntan al commit como prueba de
«esto se congeló antes de aquello». Esa relación de orden se conserva íntegra tras la
reescritura; lo que se rompe es el puntero textual. Y **seis registros JSON congelados más un
pre-registro** llevan ese puntero dentro: editarlos para actualizarlo sería tocar un registro
experimental, cosa que esta auditoría no propone en ninguna opción.

### 5.3 Opciones que se someten a decisión del autor

| Opción | Qué implica | Recomendación |
|---|---|---|
| **A. Reescribir los 69 mensajes, no tocar ningún fichero existente, conservar el historial antiguo como rama de archivo** | La rama `backup/pre-history-cleanup-20260913-1815` se conserva (y se publica) de forma permanente como rama de archivo. Los 15 SHA antiguos siguen siendo objetos válidos del repositorio: `git show 43f56dc` sigue funcionando y muestra exactamente el mismo árbol que su equivalente nuevo. `git filter-repo` deja el mapa completo `SHA antiguo → SHA nuevo`; se publica en `docs/git-history-report.md`. Una nota en `docs/reproducibility.md` explica que los SHA citados en registros anteriores al 13-09-2026 se resuelven contra esa rama o con el mapa | **Recomendada.** Cumple el objetivo sin editar ni un solo registro, pre-registro o documento congelado. Coste: dos historiales paralelos en el repositorio (170 + 99 commits; los árboles son los mismos, así que el espacio extra es despreciable) |
| A+. Igual que A, y además actualizar los punteros en los **9 documentos de prosa** (12 SHA) con un commit dedicado | Los registros JSON y `configs/manifest_rerun_a.json` seguirían intactos. Los documentos de método cambiarían solo en el SHA citado | Aceptable, pero cuatro de esos documentos son políticas y planes «congelados antes de medir»: tocarlos, aunque sea en un puntero, exige que el autor lo autorice expresamente |
| B. No reescribir; dejar los trailers | Sin riesgo alguno. El historial conserva 69 mensajes con metadatos de herramienta | Aceptable si el autor prefiere que ningún SHA cambie |
| C. Reescribir y borrar el backup sin mapa | Deja 15 punteros rotos, seis de ellos en registros congelados | **Descartada**: altera la trazabilidad científica |

Decisiones adicionales que requieren al autor (no se ejecutan sin aprobación):

1. Conservar o no `research/available-skills.md` y `tutor-reports/` en el repositorio
   entregado al tribunal. Ambos documentan que la revisión del TFM se apoyó en asistentes;
   retirarlos no ocultaría cómo se hizo el trabajo (los informes de `docs/tfm/revision/` lo
   declaran igualmente) pero sí dejaría remisiones sin destino. Propuesta: conservar y, como
   mucho, mover `tutor-reports/` a `docs/audits/tutor_reports/`.
2. Sustituir las cuatro rutas `TFM/.claude/skills/...` por una descripción neutra, como ya
   hizo el commit `af008f9` con otras rutas del entorno de trabajo. Cambio de 4 líneas en 3
   ficheros, sin pérdida de información.

### 5.4 Precauciones antes de ejecutar

- `git filter-repo` exige trabajar sobre un clon fresco o usar `--force`; además **elimina el
  remote `origin`** por diseño. Habrá que volver a añadirlo con `git remote add origin
  https://github.com/3dluis/-mecanico-ai-exp.git` y anotarlo en el informe final.
- Se ejecutaría con `--refs main` para que la rama de archivo **no** se reescriba y conserve
  los objetos antiguos. Nota posterior a la ejecución: `git filter-repo` actualiza por defecto
  los SHA citados dentro de los mensajes de commit; afectó a dos mensajes (ver
  `docs/git-sha-mapping.md`). Se comprobará después que `git diff archive/... main` está vacío
  (mismos árboles) y que `git log --format=%B main | grep -c Co-Authored-By` devuelve 0.
- El remoto está vacío: no hay nadie más con este historial, por lo que la reescritura no
  invalida ningún clon ajeno. Aun así, no se hará `push` (ni normal ni forzado) sin orden
  explícita.
- Los experimentos, resultados, artefactos JSON, cuadernos, configuraciones y datos **no se
  modifican** en ninguna de las opciones.
