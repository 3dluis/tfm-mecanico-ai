# Alineación científica v4 — Auditoría de impacto (Fase 1)

**2026-08-27 · Entregable 1 de la migración científica controlada.**
Este documento **no modifica nada**: localiza todo el material afectado por el cambio de
pregunta de investigación acordado con el tutor y lo clasifica en
`conservar / adaptar / mover a trabajo futuro / eliminar`. Las modificaciones se aplican en
las fases 2–6 y se justifican contra esta matriz.

Base de la auditoría: `main` = `a5910fd` (F25, bancos confirmatorios congelados), 635
ficheros versionados, 38 subdirectorios de `docs/`.

---

## 1. Qué cambia y qué no

**Cambia el núcleo científico.** La PI vigente hasta hoy (PI v3, 18-ago-2026) pedía al
sistema *identificar patrones no representados, generar hipótesis, validarlas e
incorporarlas como conocimiento reutilizable*: una cadena de ocho pasos cuyo tramo 4–8
—reconocimiento de insuficiencia, hipótesis, verificación, consolidación— **no tiene
todavía ninguna evidencia propia** (`alineacion_v3/02_trazabilidad.md` §2, lectura 4). La
nueva PI reduce el compromiso a un tramo más corto y enteramente ejecutable:

```text
datos OBD-II reales → diagnóstico → recuperación de evidencia (RAG)
    → explicación trazable → verificación del soporte
    → explicación sustentada  |  abstención por evidencia insuficiente
```

**No cambia el instrumental.** Los catorce experimentos ejecutados (F3–F22) pertenecen
todos a los pasos *observar / contextualizar / detectar*; siguen siendo válidos y siguen
produciendo el contexto diagnóstico que la nueva PI necesita como entrada. Los bancos
congelados (`suite_v2`, `cases_v2`), la auditoría anti-contaminación, la infraestructura
PostgreSQL+pgvector, el grafo del agente, el retriever y el verificador determinista se
conservan íntegros. Lo que cambia es **qué se afirma con ellos**.

**Ningún resultado se borra ni se renumera.** Los negativos mayores (F14, F17, F18, F21) y
el hallazgo de *cobertura declarada ≠ cobertura efectiva* (F19–F22) conservan su valor
metodológico y pasan a leerse como precondición instrumental de la nueva cadena.

---

## 2. Matriz de impacto por concepto

Leyenda de acciones:
**C** conservar sin cambio · **A** adaptar (se reescribe el encuadre, se conserva el
contenido) · **F** mover a trabajo futuro / fuera del alcance experimental ·
**E** eliminar (solo cuando el material no tiene utilidad y su permanencia genera
contradicción).

### 2.1 Pregunta de investigación, objetivos e hipótesis

| Elemento | Archivo(s) | Estado | Acción | Descripción |
|---|---|---|---|---|
| PI v3 (enunciado completo) | `docs/alineacion_v3/01_nucleo_cientifico.md` §1; `docs/01_comprension_del_problema.md` §1.3; `docs/experiments/pre-registro-v1.md` §1; `docs/memoria/01_introduccion.md`; `README.md` | vigente | **A** | Sustituida por PI v4. El enunciado anterior se conserva como registro histórico en el historial de la PI (v1→v4), nunca se oculta. |
| Cadena epistemológica de 8 pasos | `alineacion_v3/01` §0; `docs/01` §1.3; `memoria/01`, `memoria/03` | vigente | **A** | Se reduce a la cadena de 6 pasos de la nueva PI. Los pasos 5 (hipotetizar) y 8 (consolidar) salen del núcleo; el paso 4 se reformula como *verificación de suficiencia de la evidencia recuperada*. |
| Objetivo general científico | `alineacion_v3/01` §4; `docs/02_objetivos.md` §2.1; `memoria/02` §1 | vigente | **A** | Reescrito sobre explicación trazable + abstención. |
| OE-C1 (operacionalizar «patrón no representado») | `alineacion_v3/01` §4; `docs/02` §2.2 | vigente | **A** | Se conserva el **mecanismo** (exclusión controlada del corpus) y se cambia su finalidad: deja de definir «novedad» y pasa a definir **insuficiencia de evidencia recuperable**. Es el núcleo del Escenario B. |
| OE-C2 (detección contextual y longitudinal) | ídem | vigente | **A** | Degradado de objetivo científico a **objetivo instrumental**: produce el contexto diagnóstico. Conserva toda su evidencia (F3–F22). |
| OE-C3 (hipótesis verificadas por evidencia) | ídem | vigente | **A** | Reformulado: de *generar y verificar hipótesis* a *generar explicaciones trazables y verificar su soporte documental*. |
| OE-C4 (cadena completa con consolidación validada) | ídem | vigente | **A/F** | La parte *held-out/open-set + abstención* se conserva y pasa al nuevo OE de evaluación; la parte *consolidación validada* pasa a trabajo futuro. |
| H-MAIN v3 (P1–P5) | `alineacion_v3/01` §5; `pre-registro-v1.md` §4.6 | congelada (`prereg-v1.0`) | **A** por enmienda | No se reescribe el documento congelado: se añade **ENM-001** que retira H-MAIN v3 del contraste principal y registra las hipótesis nuevas. P2/P3 (reconocimiento de insuficiencia, identificación errónea confiada) se **reutilizan** casi literalmente; P1 pasa a precondición; P4 se reformula como corrección de la explicación; P5 sale del alcance. |
| H-EXP | `pre-registro-v1.md` §4.5 | congelada | **A** | Es la hipótesis que **más directamente sobrevive**: brazos X0/X1/X2 ≡ los tres brazos de la nueva PI. Se conserva casi íntegra y se amplía con trazabilidad y abstención. |
| H-EVT, H-PERS | `pre-registro-v1.md` §§4.1, 4.4 | congeladas | **F** | Salen del núcleo científico; se conservan como línea instrumental opcional sobre la calidad del contexto diagnóstico. H-PERS ya estaba condicionada a D2 (no materializado). |
| H-MEM (M0/M1/M2) | `pre-registro-v1.md` §4.2 | congelada | **F** | Trabajo futuro. El diseño (secuencias, inyección de conclusiones erróneas) se conserva íntegro y sin ejecutar. |
| H-MAS (A0–A6) | `pre-registro-v1.md` §4.3 | congelada, secundaria | **F** | Trabajo futuro. La escalera arquitectónica de ADR-0018 permanece documentada. |
| Criterio transversal edge | `pre-registro-v1.md` §3.4 | vigente | **C** | Se conserva sin cambio: la latencia y la RAM siguen siendo criterio de aceptación. |
| EXP-SEG-001 (precondición de segmentación) | `pre-registro-v1.md` §4.7 | pre-registrado, no ejecutado | **C** | Sigue siendo precondición instrumental; no depende del LLM y puede ejecutarse antes que nada. |

### 2.2 Vacío de investigación

| Elemento | Archivo(s) | Estado | Acción | Descripción |
|---|---|---|---|---|
| V\* (vacío central v3) | `alineacion_v3/01` §3.1; `estado_del_arte/00_sintesis.md`; `capitulo2_estado_del_arte.md` §14 | vigente | **A** | Reformulado. El nuevo vacío no afirma ausencia de sistemas RAG para diagnóstico vehicular; afirma que **en los trabajos revisados no fue identificada** la evaluación conjunta de: OBD-II real + explicación por RAG + trazabilidad explícita hasta la evidencia + comportamiento seguro ante evidencia insuficiente. |
| S1 (detección contextual) | `alineacion_v3/01` §3.2 y ~20 apariciones | vigente | **A** | Pasa a dimensión instrumental (produce el contexto). |
| S2 (generación de hipótesis) | ídem | vigente | **A** | Reformulada como **generación de explicaciones diagnósticas**. |
| S3 (verificación mediante evidencia) | ídem | vigente | **C/A** | Se conserva como dimensión central; se le añade explícitamente la **trazabilidad afirmación→evidencia**. |
| S4 (memoria longitudinal validada) | ídem | vigente | **F** | Trabajo futuro. |
| S5 (arquitectura híbrida/multiagente) | ídem | vigente | **A** | Pasa a condición de contorno (edge) y deja de aspirar a contribución. |
| S6 (patrones no representados como escenario) | ídem | vigente | **A** | Reformulada como **escenario de disponibilidad controlada de evidencia**: el mecanismo de exclusión se conserva, cambia lo que demuestra. |
| Matriz de cobertura de antecedentes (9 columnas por pasos de la cadena) | `alineacion_v3/02` §3 | vigente | **A** | Las 15 referencias se conservan; las columnas se reordenan hacia *Diagnóstico OBD-II · Explicación · RAG · Trazabilidad/citación · Fidelidad · Abstención/incertidumbre · Evaluación conjunta*. |

### 2.3 Diseño experimental

| Elemento | Archivo(s) | Estado | Acción | Descripción |
|---|---|---|---|---|
| Protocolo de 15 pasos de H-MAIN | `alineacion_v3/01` §8.1 | pre-registrado | **A** | Reducido al protocolo de la nueva cadena; los pasos de consolidación (14–15) se sustituyen por *decisión explicar/abstenerse*. |
| Estados epistemológicos OBSERVED…REFUTED (8 estados) | `alineacion_v3/01` §7; `shared/.../data_enums.py:EpistemicLevel`, `PatternStatus`, `HypothesisStatus` | implementado en contratos | **A/F** | Los estados de **decisión sobre una explicación** (`SUPPORTED`, `CONTRADICTED`/`REFUTED`, `INCONCLUSIVE`/`INSUFFICIENT_EVIDENCE`) se conservan y son ahora la salida central del sistema. Los estados de **promoción a conocimiento** (`EXPERIMENTALLY_VERIFIED`, `EXTERNALLY_CONFIRMED`) quedan fuera del alcance experimental; el código no se elimina (rompería contratos y migraciones) pero se documenta como no evaluado. |
| CN1–CN9 (controles negativos) | `alineacion_v3/01` §8.3; `pre-registro-v1.md` §4.6; `benchmarks/agent-diagnostics/cases_v2.yaml` | congelados y **materializados** | **C** (CN1, CN2, CN3, CN4, CN7, CN8, CN9) / **F** (CN5, CN6) | Los siete conservados son exactamente los controles que la nueva PI necesita: distractores documentales (CN3), evidencia contradictoria (CN4), causas múltiples (CN7), **evidencia insuficiente por construcción (CN8, 6 casos ya congelados)** y anomalía sin relevancia (CN9). CN5/CN6 dependen de memoria y salen del alcance. |
| `suite_v2` (10 réplicas, 370 sesiones, freeze por hash) | `obd-lab/scenarios/suite_v2/`, `ai-models/configs/suite-v2-freeze.json` | congelado y materializado | **C** | Íntegro. Sigue siendo la fuente del contexto diagnóstico y de los episodios held-out. |
| `cases_v2` (40 casos, 8 sin fallo, 6 insuficientes) | `benchmarks/agent-diagnostics/cases_v2.yaml` | congelado antes de ver salidas | **C** | Íntegro y **especialmente bien alineado**: los 6 casos «insuficientes» son el germen del Escenario B, y los 8 «sin fallo» ejercen la abstención. |
| Clases held-out (`corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift`) | `ai-models/configs/heldout-exclusions.yaml`; suites | congeladas | **C** con **reinterpretación** | Dejan de presentarse como *prueba de descubrimiento de fallos desconocidos* y pasan a ser el mecanismo de **control de la disponibilidad de evidencia**: el corpus no las describe, luego el comportamiento correcto es abstenerse. La exclusión E-RAG, que en F24 se registró como *hallazgo negativo* (corpus_v1 describe los mecanismos de las tres held-out), pasa a ser una **variable experimental manipulable**. |
| Auditoría de contaminación E-DET/E-RAG/E-MEM | `tools/contamination_audit.py`, `tests-integration/test_contamination_audit.py` | implementada, gate activo | **C/A** | Se conserva. E-RAG pasa de *restricción a cumplir* a *palanca experimental*: el mismo instrumento verifica ahora que el corpus del Escenario B **no** contiene la evidencia, y que el del Escenario A **sí**. |
| Brazos X0/X1/X2 de H-EXP | `pre-registro-v1.md` §4.5 | pre-registrados | **C/A** | Se conservan como los tres brazos de la nueva PI (sin RAG / RAG / RAG+verificación+abstención). |
| Ablación A0–A6 (arquitecturas) | ADR-0018; `agent-runtime/12` | diseñada, no ejecutada | **F** | Trabajo futuro. |
| Ablación M0/M1/M2 (memoria) | `alineacion_v3/01` §8.5 | diseñada, no ejecutada | **F** | Trabajo futuro. |
| Plan estadístico (Wilcoxon, McNemar, BCa, Holm, Clopper-Pearson) | `pre-registro-v1.md` §8 | congelado | **C** | Sigue siendo aplicable a las nuevas comparaciones sin cambio. |
| Bloqueante B0.1 (R2 · smoke del SLM) | `alineacion_v3/03` §0 | pendiente en el Mac | **C** | Sigue siendo el camino crítico: la nueva PI también necesita un SLM fijado. |

### 2.4 Estado del arte y revisión sistemática

| Elemento | Archivo(s) | Estado | Acción | Descripción |
|---|---|---|---|---|
| Protocolo PRISMA y búsquedas ejecutadas | `estado_del_arte/entrega1..3_revision_sistematica.md` (912 líneas) | ejecutado | **C** | No se descarta ninguna búsqueda. Se conserva como evidencia histórica del proceso. |
| Pregunta de revisión y criterios de relevancia | `entrega1`, `entrega3` | vigentes | **A** | Reorientados a la nueva PI; las búsquedas previas sobre memoria y descubrimiento se conservan etiquetadas como *contexto histórico*. |
| Línea A — OBD-II, ML y datasets | `linea_a_obd2_ml_datasets.md` | vigente | **C** | Sigue siendo línea principal. |
| Línea B — anomalías y SLM en edge | `linea_b_anomalias_slm_edge.md` | vigente | **A** | Se reduce a antecedente instrumental. |
| Línea C — agentes, RAG y memoria | `linea_c_agentes_rag_memoria.md` | vigente | **A** | Se divide: la parte RAG/agentes se amplía y se convierte en línea principal; la parte de memoria/aprendizaje continuo se reduce a antecedente y a trabajo futuro. |
| Líneas nuevas: fidelidad, atribución de evidencia, incertidumbre y abstención | — | **inexistentes** | **crear** | Hueco real de la revisión actual: `groundedness`, `faithfulness`, `provenance`, `citation attribution`, `selective prediction`, `abstention`, `hallucination mitigation`. Es el trabajo de la Fase 3. |
| Matriz de evidencias (15 antecedentes) | `alineacion_v3/02` §3 | vigente | **A** | Recodificada por las capacidades de la nueva PI. |
| `afirmaciones_novedad.md` | `estado_del_arte/afirmaciones_novedad.md` | vigente | **A** | Las afirmaciones de novedad ligadas a descubrimiento y memoria se retiran o se reformulan. |
| Uso de la palabra «literatura» | varios | ya corregido en v3 | **C** | Regla mantenida; se verifica de nuevo en la Fase 6. |

### 2.5 Arquitectura, ADRs y diagramas

| Elemento | Archivo(s) | Estado | Acción | Descripción |
|---|---|---|---|---|
| Diagrama principal de arquitectura | `docs/diagrams/arquitectura.mermaid` | vigente | **A** | El bloque de razonamiento debe mostrar el nuevo flujo con la bifurcación *evidencia suficiente / abstención*. Menciona además ChromaDB y SQLite, ya superados por ADR-0030 (pgvector) — corrección pendiente independiente de este cambio. |
| Flujo del agente | `agent-runtime/diagrams/diagnostic-flow.mmd` | vigente | **A** | Añadir el nodo de decisión de suficiencia. |
| `docs/05_arquitectura.md` | ídem | vigente | **A** | C5b se describe como «memoria evolutiva … consolidación simple»: se marca fuera de alcance. |
| ADR-0013 (memoria de tres niveles), ADR-0022 (gobernanza de modelos, memoria evolutiva) | `docs/adr/` | aceptados | **F** | No se eliminan (regla del repositorio: un ADR no se borra). Se anotan como *fuera del alcance de la validación del TFM*. |
| ADR-0014 (agente v1), ADR-0016, ADR-0017 | `docs/adr/` | aceptados | **C** | Vigentes y necesarios. |
| ADR-0015 (runtime multiagente), ADR-0018 (diseño experimental de arquitecturas) | `docs/adr/` | aceptados | **F** | Conservados; su ablación pasa a trabajo futuro. |
| ADR-0030 (PostgreSQL+pgvector), ADR-0032 (uv), ADR-0034 (RNG separado), ADR-0035 (library-first) | `docs/adr/` | aceptados | **C** | Sin cambio. |
| ADR nuevo — acotación del alcance científico | — | inexistente | **crear** | ADR-0036: registra la decisión, sus alternativas y sus consecuencias. |
| `docs/data-architecture/06_memoria_evolutiva.md` | ídem | vigente | **F** | Se conserva el diseño; se marca fuera de alcance. |
| `docs/data-architecture/07_provenance_versionado.md` | ídem | vigente | **C** | **Sube de importancia**: la procedencia es ahora parte del núcleo científico (trazabilidad). |
| `docs/data-architecture/10_modelo_vectorial_rag.md`, `05_diagnosticos_evidencias.md` | ídem | vigentes | **C** | Núcleo. |
| `docs/event-intelligence/09_memory_integration.md` | ídem | vigente | **F** | Fuera de alcance. |

### 2.6 Código

| Módulo | Ruta | Clasificación | Acción |
|---|---|---|---|
| Adquisición OBD-II, transporte, telemetría, ventanas, snapshots | `diagnostic-agent/src/diagnostic_agent/{acquisition,telemetry}/` | **necesario** | **C** |
| Detección (LOF/ONNX), features, eventos, baselines | `.../detection/`, `.../events/`, `ai-models/src/ai_models/` | **auxiliar reutilizable** (produce contexto) | **C** |
| Retriever léxico + ingesta de corpus | `.../reasoning/rag/retriever.py` | **necesario** | **A** — necesita devolver el `chunk_id` y el `document_id` como identificadores citables en la explicación, y una señal de suficiencia (score/umbral). |
| Verificador determinista de hipótesis | `.../reasoning/verify_rules.py` | **necesario** | **A** — se conserva íntegro (contrasta afirmaciones contra features reales) y se le añade la verificación del **soporte documental** de cada afirmación. |
| Generador LLM | `.../reasoning/llm/generator.py` | **necesario** | **A** — la salida debe llevar afirmaciones atomizadas con su referencia de evidencia. |
| Grafo del agente (`triage→recall→retrieve→hypothesize→verify→report→memorize`) | `.../reasoning/graph/agent_v1.py` | **necesario** | **A** — añadir el nodo de decisión de suficiencia entre `verify` y `report`; `memorize` pasa a opcional y fuera de la evaluación. |
| Memoria episódica | `.../reasoning/memory/episodic.py` | **fuera de alcance, conservable** | **F** — sin cambios; se documenta como no evaluado. |
| Runtime multiagente (supervisor, 748 líneas) | `.../runtime/supervisor.py` | **fuera de alcance, conservable** | **F** |
| Persistencia PostgreSQL, repositorios, migraciones, outbox | `.../storage/`, `alembic/` | **necesario** | **C** |
| Contratos compartidos (`DiagnosticEvidence`, `RetrievalEvent`, `KnowledgeChunk`, `ProvenanceRecord`…) | `shared/src/mecanico_contracts/` | **necesario** | **C/A** — ya soportan trazabilidad; posible campo aditivo para el soporte por afirmación. |
| `LearnedPattern`, `PatternRelation`, `PatternStatus` | `shared/.../data_model.py`, `data_enums.py` | **fuera de alcance, conservable** | **F** — no se eliminan (contratos aditivos, ADR-0007) |
| Herramientas de banco (`gen_suite_v2`, `freeze_benchmark`, `contamination_audit`) | `tools/` | **necesario** | **C/A** |
| `tools/llm_smoke.py`, `llm_smoke_deep.py`, `bench_agent_diagnostics.py` | `tools/` | **necesario** | **C** |
| Emulador y generador de escenarios | `obd-lab/` | **necesario** | **C** |
| `cloud-platform/`, `mobile-app/` | — | **fuera de alcance** (ya declarado OS1/OS2) | **C** |

**Candidatos a eliminación: ninguno.** No se ha identificado ningún módulo cuya
permanencia genere contradicción con la nueva PI. Todo lo que sale del alcance científico
sigue siendo código funcional, cubierto por tests y referenciado por contratos.

### 2.7 Pruebas

| Prueba | Ruta | Acción |
|---|---|---|
| `test_traceability_e2e.py` | `tests-integration/` | **C/A** — es la base directa de las nuevas pruebas de trazabilidad. |
| `test_agent_v1_behavior.py` | ídem | **A** — añadir los escenarios de suficiencia/insuficiencia. |
| `test_contamination_audit.py` | ídem | **C/A** — verificar también la **ausencia deliberada** de evidencia (Escenario B). |
| `test_suite_v2_cases_v2.py`, `test_benchmark_freeze.py`, `test_effective_coverage.py`, `test_replica_criteria.py` | ídem | **C** |
| `test_pg_edge_e2e.py`, `test_snapshot_e2e.py`, `test_event_slice.py`, `test_wide_parity.py`, `test_dependency_inventory.py` | ídem | **C** |
| `test_runtime_slice.py` | ídem | **C** — cubre el runtime multiagente, ahora fuera de alcance; se conserva como test de regresión. |
| Pruebas nuevas de los 6 escenarios científicos | — | **crear** (Fase 5) |

---

## 3. Recuento

| Acción | Elementos | Comentario |
|---|---|---|
| **Conservar (C)** | 38 | Todo el instrumental, los bancos congelados, la persistencia y la evidencia ejecutada. |
| **Adaptar (A)** | 31 | Reescritura de encuadre; el contenido se reutiliza. |
| **Mover a trabajo futuro (F)** | 14 | Memoria evolutiva, consolidación, H-MEM, H-MAS, H-EVT/H-PERS, ablaciones A0–A6 y M0/M1/M2, CN5/CN6. |
| **Eliminar (E)** | 0 | — |

---

## 4. Riesgos detectados durante la auditoría

1. **El pre-registro está congelado (`prereg-v1.0`, commit `9cee9e9`).** Su §2.1 prohíbe
   modificar hipótesis y umbrales tras la congelación salvo por **enmienda fechada y no
   retroactiva**. La migración debe hacerse por ENM-001, no reescribiendo el documento.
   Como no se ha ejecutado ningún experimento confirmatorio, la enmienda no es retroactiva
   sobre ningún resultado — igual que ocurrió con ENM-000.
2. **El corpus RAG v1 viola E-RAG** (hallazgo vigente de F24: `corpus_v1.yaml` describe los
   mecanismos de las tres clases held-out). Bajo la PI anterior era un defecto bloqueante;
   bajo la nueva PI es exactamente la palanca del Escenario A/B, pero **obliga a decidir el
   corpus v2** (pendiente R3 del autor) antes de ejecutar el experimento central.
3. **B0.1 (R2, smoke del SLM) sigue sin ejecutarse** y sigue siendo el camino crítico: sin
   un modelo de lenguaje fijado no hay generador de explicaciones ni juez.
4. **El historial de la PI que registra el repositorio** (`correspondencia_nomenclatura.md`
   §0) muestra que ya la PI v1 de Fase 0 contenía «descubrir … patrones no documentados».
   La nota metodológica de la Fase 2 debe redactarse sobre este registro, sin afirmar que
   la formulación inicial fuese exclusivamente de explicación trazable.
5. **`docs/08_roadmap_tecnico.md` está divergente** entre `main` y la copia local del autor
   (pendiente conocido). La migración toca este fichero.

---

## 5. Orden de aplicación

| Fase | Alcance | Documentos principales |
|---|---|---|
| 2 | PI, objetivos, hipótesis, vacío, contribución, DSR, trazabilidad | `alineacion_v4/01`, `02`, `04`, `05`; `docs/01`, `docs/02`; `memoria/01`, `02`, `04`; ENM-001; ADR-0036 |
| 3 | Estado del arte y revisión sistemática | `estado_del_arte/*`; `alineacion_v4/02` §matriz |
| 4 | Diseño experimental, escenarios, brazos, métricas | `alineacion_v4/03`; ENM-001 |
| 5 | Arquitectura, diagramas, código, pruebas | diagramas; `retriever.py`, `agent_v1.py`, `verify_rules.py`; tests nuevos |
| 6 | Consistencia global, gate de calidad, entrega | barrido textual; `make check`; bundle |
