# 01 · Hallazgos del tutor académico

**Evaluación académica independiente (tutor)** · modo `FULL_TFM_REVIEW` (workflows 00–16, con el 15 adversarial
obligatorio) · **Unidad:** el documento completo del TFM y los artefactos que lo sostienen ·
**Instantánea del veredicto:** commit `a6a5f40`, 3 de septiembre de 2026 ·
**Informe completo:** `TFM/tutor-reports/TUTOR-REPORT-20260903-FULL.md` (26 secciones,
scorecard y bloque `TUTOR_HANDOFF`).

> `HEAD` avanzó a `880a4eb` durante la evaluación con dos ficheros de otros auditores
> (`docs/tfm/revision/02_rag_findings.md`, `03_experiment_findings.md`). Ningún fichero de la
> unidad evaluada cambió. El veredicto se fija sobre `a6a5f40`.

> **Colisión de identificadores declarada.** Los dos informes anteriores del tutor usan
> series solapadas: `TUTOR-MAJ-001` y `TUTOR-MIN-003` designan problemas distintos en
> `TFM/tutor-reports/TUTOR-DRY-RUN-01.md` y en `tutor-reports/TUTOR-REPORT-20260903.md`.
> **No se renumera el pasado**; cada ID se cita con su informe de origen. Desde este informe
> la serie es global y única, y los IDs nuevos arrancan en `TUTOR-MAJ-003`,
> `TUTOR-MIN-006` y `TUTOR-INF-008`.

---

## 1. Veredicto y score

| | |
|---|---|
| **Estado** | **`FAIL`** |
| **Score** | **55 / 99** (proyección a 100: 56, orientativa) |
| **Regla aplicada** | Precedencia de findings: 0 `CRITICAL`, **13 `MAJOR` abiertos** de la clase «está mal». Regla de parada del workflow 16: **cuatro gates de integridad en `FAIL`** (05, 06, 07, 10) |
| **Recuento de findings** | 0 CRITICAL · 13 MAJOR · 17 MINOR · 12 INFO |
| **Reevaluación** | 7 de 7 findings del informe del 3-09 sobre el cambio de la PI: **`FIXED`** y confirmados uno a uno contra su criterio. 7 de 7 findings del dry-run sobre E12: **`NOT_FIXED`** |
| **¿Exige reejecutar experimentos?** | **No.** Ninguna de las trece acciones requeridas vuelve al laboratorio |

**Lo que este `FAIL` no significa.** No hay evidencia fabricada, ni referencia inexistente
sosteniendo el diseño, ni resultado incompatible con sus datos, ni cambio de diseño oculto.
El diseño experimental es correcto y en varios puntos superior a lo habitual. Lo que falla
es la capa que convierte el laboratorio en documento: cifras que se quedaron en una versión
anterior, correcciones que no viajaron del informe al capítulo, artefactos de trazabilidad
congelados y afirmaciones sin su n.

---

## 2. ¿El documento responde realmente a la pregunta principal?

**Parcialmente, y sobre una base más estrecha que la que el propio documento enuncia.**

**Sí, en lo más difícil.** El mecanismo que la pregunta interroga —que la decisión de
explicar responda a la evidencia disponible y no a la certeza del modelo ni a la disposición
del modelo de lenguaje— está demostrado con la variable aislada y registrado caso a caso.
En `tables/E15_suficiencia.csv`, las filas C05 a C09 comparten `case_id`
(`F01_vacuum_leak__idle__10@120s`), confianza calibrada 0,9078, cinco observaciones y tres
afirmaciones; lo único que cambia es `corpus_variant` y `n_excluded_chunks`. Con la
evidencia, el agente explica; retirada, se abstiene; incompleta, se abstiene; sustituida por
el procedimiento de otro motor, se abstiene. En PARTIAL y DISTRACTOR hay **cuatro documentos
aplicables delante** y la cobertura de afirmaciones es 0,00: el sistema responde a la
pertinencia, no a la presencia. Y el modelo de lenguaje respeta el veredicto en 9 de 9 en
las tres configuraciones, con 0 citas inexistentes en los siete registros.

**No, en el alcance con que se afirma.** Tres cosas lo impiden hoy:

1. **n = 1 por condición.** ABSENT, PARTIAL y las dos DISTRACTOR son el **mismo caso
   diagnóstico**. La matriz declara las cuatro subpreguntas «Sostenida» y el capítulo 6
   concluye «sí puede» sin decirlo (`TUTOR-MAJ-010`). El mecanismo está demostrado; la
   capacidad, no.
2. **La trazabilidad se apoya en cifras que no proceden del registro vigente.** La tabla de
   recuperación de `cap5:82-89` reproduce una ejecución de cinco casos cuyo registro fue
   sustituido por otra de seis con cifras distintas (`TUTOR-MAJ-001`, `NOT_FIXED`), y la
   estrategia que alcanza Hit@10 = 1,00 construye la consulta con la etiqueta anotada del
   conjunto de referencia, no con la predicción del modelo (`TUTOR-MAJ-002`, `NOT_FIXED`).
3. **El documento no cierra la respuesta.** El capítulo 6 no recorre los objetivos con grado
   de cumplimiento (`TUTOR-MAJ-008`), las ablaciones que aislarían la contribución de cada
   componente (E18) no se han ejecutado, y E19 depende de una decisión del autor.

**Respuesta por subpregunta.** PI.1: **sí**, sobre validación de `synthetic_v2`. PI.2:
**parcialmente** —la cadena se reconstruye y la cobertura de soporte es 1,00 en los cinco
casos con evidencia, pero las cifras de recuperación publicadas no coinciden con su
registro—. PI.3: **parcialmente** —mecanismo demostrado, n = 1—. PI.4: **parcialmente**
—dos líneas de defensa comprobadas, sobre un caso—.

**La pregunta no se toca.** Está bien planteada, es falsable, admite un «no», tiene cuatro
desenlaces de refutación escritos antes (`docs/methodology/experimental-design.md:115-121`,
respaldados por `ADR-002:87-93`) y dos de los cinco previstos se materializaron y se
reportan. Lo que hay que corregir no es la pregunta: es acotar la respuesta a lo medido.

---

## 3. Los trece gates, comparados con `research/gates.md`

Evaluados con la evidencia recogida en esta revisión, no con el registro del proyecto, y
después comparados con él.

| Gate | **Tutor** | `research/gates.md` | Discrepancia | Evidencia del tutor |
|---|---|---|---|---|
| **01** Pregunta | `PASS` | `PASS` | — | PI única y vigente; `grep` de la PI anterior → 0 fuera de `ADR-003`; desenlaces escritos antes |
| **02** Vacío | `PASS_WITH_OBSERVATIONS` | `PASS_WITH_OBSERVATIONS` | — | Barrido con recuentos en `cap3:20-29`; formulado como «ninguno de los revisados». Observación: la afirmación estrecha de `cap3:213-218` no lleva cita |
| **03** Objetivos | **`FAIL`** | `FAIL` | **mismo estado, motivo distinto** — `INFO` | El registro lo motiva en el enunciado legacy y el OG con dos verbos, ambos ya corregidos en `cap2`. El motivo vigente: **ningún OE aparece en ninguna conclusión** (`TUTOR-MAJ-008`) |
| **04** Metodología | **`FAIL`** | `PASS_WITH_OBSERVATIONS` | **discrepancia** — `MAJOR` | Dos condiciones de `PASS` incumplidas: paradigma/tipo/diseño no etiquetados (`grep` sobre `cap4` → 0) y bancos de selección y evaluación no disjuntos sin declararlo |
| **05** Evidencia | **`FAIL`** | `BLOCKED` | **integridad** — `MAJOR` | El registro dice «no hay claims redactados»; hay seis capítulos. `cap2:94-96` afirma el cierre de cuatro fases sin evidencia primaria |
| **06** Integridad experimental | **`FAIL`** | `PASS_WITH_OBSERVATIONS` | **integridad** — `MAJOR` | Tres bloques de cifras no reproducibles desde artefacto vigente; ningún registro con `commit`; índice vectorial no reconstruible desde el árbol |
| **07** Resultados | **`FAIL`** | `PASS_WITH_OBSERVATIONS` | **integridad** — `MAJOR` | Condición literal: «una cifra sin artefacto». `cap5:69-71`, `cap5:84-87`, `cap4:95-108` |
| **08** Discusión | **`FAIL`** | `BLOCKED` | **discrepancia** — `INFO` | El registro es anterior al capítulo 5. La discusión afirma más de lo que sostienen los resultados en el n de PI.3/PI.4 y omite la corrección registrada de E7 |
| **09** Conclusiones | `BLOCKED` | `BLOCKED` | — | Capítulo declarado condicionado a E19; sin recorrido por objetivo. No hay conclusión nueva sin resultado, que es la condición de `FAIL` |
| **10** Referencias | **`FAIL`** | `PASS_WITH_OBSERVATIONS` | **integridad** — `MAJOR` | Condición literal: «queda una referencia sin verificar». Siete `[VERIFY_SOURCE]` en `docs/memoria/bibliografia.md:36,40,44,50,54,76,84` |
| **11** UAX | `BLOCKED` | `BLOCKED` | — en el estado | Extensión sin decisión, con tres cifras oficiales incompatibles. Observación no recogida por el registro: falta el ABSTRACT, independiente del conflicto |
| **12** Humanización | `N/E` | «no procede» | — | No se ejecuta antes del gate académico |
| **13** Integridad global | `PASS_WITH_OBSERVATIONS` | `PASS` | **un nivel** — `INFO` | Sin evidencia inventada, sin marcador oculto, sin cita alterada. Observación: `cap5:84-87` publica cifras que su registro desmiente **sin marcador**, a diferencia de `cap5:47-50`, que sí lo lleva |

**Recuento:** `PASS` 1 · `PASS_WITH_OBSERVATIONS` 2 · `BLOCKED` 2 · `FAIL` 7 · `N/E` 1.
**Discrepancias con el registro: 7** (4 `MAJOR` sobre gates de integridad, 3 `INFO`).
La causa común: `research/gates.md` se evaluó el 1 de septiembre, antes de que existieran
los capítulos 5 y 6, y no se ha reevaluado. El propio registro lo advierte en su línea 3
(«Un gate no se reevalúa de memoria: se vuelve a comprobar»). Nota menor: `:28` habla de
«los dos `FAIL`» cuando la tabla contiene uno, y `:18` cita `experiments/E6_baseline.json`,
que no existe.

---

## 4. Matriz de secciones UAX

Estados: `COMPLETE` · `NEEDS_ALIGNMENT` · `NEEDS_EVIDENCE` · `NEEDS_EXPERIMENT` ·
`NEEDS_STATISTICAL_REVIEW` · `NEEDS_REFERENCE_REVIEW` · `NEEDS_REWRITE` · `BLOCKED`.

| Sección UAX | Contenido actual | Estado | Skill responsable | Problemas | Corrección | Gate |
|---|---|---|---|---|---|---|
| Portada | no existe como fichero; datos en `LEEME.md:3-5` | `NEEDS_ALIGNMENT` | productor | título definitivo y convocatoria sin consensuar | fijar en la reunión con el director y volcarla a la plantilla | 11 |
| RESUMEN (300 palabras, IMRyD) | `00_resumen.md:6-32`, 304 palabras, recorrido completo | `COMPLETE` con observación | productor | no traslada la cobertura 3 de 5 que `cap5:156` sí declara (`TUTOR-INF-017`) | añadir la cobertura al reescribirlo tras E19 | 11 |
| Palabras clave | `00_resumen.md:34-35`, **siete** | `NEEDS_REWRITE` | productor | la plantilla pide cinco (`TUTOR-MAJ-009`) | dejar cinco | 11 |
| ABSTRACT y Keywords (inglés) | **no existen** | `BLOCKED` | productor | apartado obligatorio ausente (`TUTOR-MAJ-009`) | redactar como traducción fiel, con la misma fuerza de afirmación | 11 |
| **Cap. 1 · Justificación del proyecto** | `cap1:7-77`, íntegramente científica | `NEEDS_REWRITE` | productor | falta la justificación **personal** que la plantilla pide expresamente; `grep` de primera persona → 0 | añadir el párrafo personal sin tocar el científico | 11 |
| **Cap. 1 · Presentación del proyecto y contenidos** | `cap1:79-117` | `COMPLETE` | productor | ninguno; la advertencia sobre la procedencia (`:101-111`) es **PRESERVE** | — | 11 |
| **Cap. 2 · Objetivo general** | `cap2:14-35` | `COMPLETE` con decisión abierta | productor | un verbo, infinitivo, verificable; enunciado pendiente de consenso (`:31-35`) | consensuar con el director | 3 |
| **Cap. 2 · Objetivos específicos** | `cap2:37-107` | `NEEDS_ALIGNMENT` | productor | `cap2:93-96` declara cerradas E8, E14, E16 y ejecutada E17, sin informe ni registro (`TUTOR-MAJ-007`); Anexo A inexistente (`TUTOR-MIN-011`); remisión a cap4 errónea (`TUTOR-MIN-010`) | declarar el estado real con la misma palabra en los cuatro artefactos; crear el anexo; corregir la remisión | 3, 5 |
| **Cap. 3 · Marco teórico** | `cap3:1-228`, cuatro áreas | `NEEDS_EVIDENCE` | productor + auditor de referencias | tres `[AMPLIAR]`; la afirmación de vacío de `:213-218` sin cita; `:82-84` contradicho por un registro (`TUTOR-MAJ-004`); «literatura» en `:191` | completar las lecturas; citar las fuentes que acotan el vacío; acotar `:82-84` al volumen de datos | 2, 5, 10 |
| **Cap. 4 · Población y muestra** | `cap4:26-155` | `NEEDS_ALIGNMENT` | productor | la tabla del suelo de ruido y la narrativa de `:95-108` no coinciden con `tables/E5_estudio_ventana.csv` (`TUTOR-MAJ-003`). **El resto es PRESERVE** | reconciliar solo esas cifras y esa frase | 6, 7 |
| **Cap. 4 · Objetivos de investigación** | `cap4:156-172` | `COMPLETE` | productor | cuatro subpreguntas con desenlace de sostén y de refutación, fijados antes | — | 1, 4 |
| **Cap. 4 · Variables e instrumentos** | `cap4:174-280` | `COMPLETE` con observación | productor | M6 con decisión abierta (`:232-233`); umbral sin procedencia fechada (`TUTOR-MAJ-005`) | decidir M6; registrar la procedencia del umbral | 4 |
| **Cap. 4 · Diseño experimental** | `cap4:282-329` | `NEEDS_ALIGNMENT` | productor | **no etiqueta paradigma, tipo ni alcance temporal** (`TUTOR-MAJ-012`); no menciona el pre-registro ni su evolución, que `ADR-002:115` exige narrar; «283 tests» frente a 290 reales (`TUTOR-MIN-015`) | añadir las etiquetas, narrar la evolución del pre-registro, fechar la cifra de tests | 4, 11 |
| **Cap. 4 · Modelo de análisis** | `cap4:331-356` | `COMPLETE` | productor | análisis comparativo y por caso, correctamente declarado como no inferencial con n = 9 | — | 4 |
| **Cap. 5 · Análisis descriptivo** | `cap5:10-31` | `COMPLETE` | productor | n, partición y procedencia visibles | — | 7 |
| **Cap. 5 · Resultados · PI.1** | `cap5:39-74` | `NEEDS_EVIDENCE` | productor + revisor estadístico | la fila calibrada no está en el registro citado (`TUTOR-MAJ-006`); falta la ejecución sobre `synthetic_v3` (`TUTOR-MAJ-004`) | escribir el bloque de calibración en el registro; incorporar la sensibilidad | 6, 7 |
| **Cap. 5 · Resultados · PI.2** | `cap5:76-119` | `NEEDS_ALIGNMENT` | productor + evaluador RAG | la tabla de `:82-87` no coincide con `experiments/E12_retrieval.json` y `:89` dice cinco casos frente a seis (`TUTOR-MAJ-001`); `:116-119` afirma «los cuatro informes» y son dos (`TUTOR-MIN-009`) | declarar la ejecución canónica y llevar sus cifras; corregir el recuento | 6, 7 |
| **Cap. 5 · Resultados · PI.3 y PI.4** | `cap5:121-162` | `COMPLETE` salvo el n | productor | coincide con el registro en las nueve filas; falta declarar el n por condición (`TUTOR-MAJ-010`). **PRESERVE la tabla** | añadir el n y la matriz de abstención por condición | 7 |
| **Cap. 5 · Resultados · modelo de lenguaje** | `cap5:164-194` | `COMPLETE` | productor | coincide con los siete registros. **PRESERVE** | — | 7 |
| **Cap. 5 · Discusión** | `cap5:196-239` | `NEEDS_EXPERIMENT` | productor | «las cuatro subpreguntas quedan sostenidas» sin el n (`TUTOR-MAJ-010`); sin alternativas descartadas para el contraste central; sin comparación con los trabajos del cap. 3; E18 pendiente | acotar; añadir alternativas; ejecutar E18 antes de atribuir por componente | 8 |
| **Cap. 6 · Conclusiones por objetivo** | **no existe** | `BLOCKED` | productor | ningún OE tiene conclusión ni grado (`TUTOR-MAJ-008`) | redactar OE1 → OE5 → OG con grado, aunque OE5 quede parcial | 3, 9 |
| **Cap. 6 · Limitaciones** | `cap6:32-101`, 17 entradas | `COMPLETE` con observaciones | productor | severidad de L-10 y L-15 divergente del registro (`TUTOR-MIN-016`); cinco limitaciones de E13 sin ID; L-04, L-05 y L-16 sin consecuencia. **PRESERVE el bloque** | unificar severidades, dar ID, completar tres enunciados | 9 |
| **Cap. 6 · Prospectiva** | `cap6:103-124` | `COMPLETE` | productor | deriva de las limitaciones y no introduce afirmaciones nuevas | — | 9 |
| **Cap. 6 · Consideraciones finales** | `cap6:126-137`, esbozo | `BLOCKED` | productor | de los seis puntos de la plantilla cubre uno; declarado pendiente de E19 | redactar los seis al cerrar E19 | 9, 11 |
| **Bibliografía** | `bibliografia.md`, 38 entradas | `NEEDS_REFERENCE_REVIEW` | auditor de referencias | siete `[VERIFY_SOURCE]`; «et al.» en dos entradas; identificadores internos dentro de la cita en texto (`TUTOR-MAJ-013`) | completar metadatos desde el original; retirar «et al.» y los identificadores en el volcado | 10 |
| **Anexos** | no existen | `NEEDS_ALIGNMENT` | productor | `cap2:6` cita un Anexo A con la correspondencia de objetivos (`TUTOR-MIN-011`) | crear el anexo o remitir a `research/propuestas-objetivos.md` | 11 |
| **Figuras y tablas** | 12 figuras en `figures/`, **0 en la memoria**; 21 tablas **sin ID** | `NEEDS_REWRITE` | productor | incumple pie, fuente e identificador (`TUTOR-MIN-013`) | numerar las tablas e incorporar las figuras con pie y fuente | 11 |
| **Formato del documento** | volcado a Word inexistente | `N/E` | productor | se evaluará sobre el documento volcado | — | 11 |
| **Extensión** | 12 550 palabras ≈ 31 páginas | `BLOCKED` | autor + director | tres cifras oficiales incompatibles; el mínimo del curso vigente es 60 páginas, con «No apto» aparejado | decisión del director | 11 |

---

## 5. Matriz maestra de trazabilidad, resumida

Reconstruida **desde el repositorio** y después contrastada con
`research/traceability-matrix.md`.

| Sub-PI | OE | EXP con informe **y** registro | MET | RES | DISC | CONC | Hueco |
|---|---|---|---|---|---|---|---|
| **PI.1** diagnóstico | OE3 | E6 ✓✓ · E7 ✓✓ · **E8 ✗✗** | M1 | `cap5:39-74` | `cap5:203-206` | **ninguna** | E8 declarada cerrada sin artefacto; la fila calibrada sin registro; la sensibilidad sobre v3 omitida; **ninguna conclusión por objetivo** |
| **PI.2** trazabilidad | OE4 | E11 ✓✓ · E12 ✓✓ · E15 ✓✓ · **E14 ✗✗** | M2, M4 | `cap5:76-119` | `cap5:206-208` | **ninguna** | cifras de recuperación ≠ registro; la estrategia ganadora usa la etiqueta anotada; `citation correctness` y `completeness` sin valor publicado; E14 declarada cerrada sin artefacto |
| **PI.3** insuficiencia | OE4, OE5 | E15 ✓✓ · **E16 ✗✗** · **E17 ✗✗** | M5 | `cap5:121-162` | `cap5:208` | `cap6:17-23`, sin ID ni grado | **n = 1 por condición**; umbral sin procedencia fechada; E16 y E17 declaradas cerradas o ejecutadas sin artefacto |
| **PI.4** evidencia engañosa | OE4, OE5 | E12 ✓✓ · E15 ✓✓ | M2, M5 | `cap5:158-162` | `cap5:209-210` | `cap6:20-22`, sin ID ni grado | **n = 2, mismo caso**; distractores medidos solo en la estrategia semántica |
| **Transversal** | OE5 | **E18 ✗✗ · E19 ✗✗ · E20 ✗✗** (pendientes, declaradas) | M1-M6 | — | — | — | sin ablaciones, la contribución de cada componente no está aislada; sin E19 el test sigue cerrado y todas las cifras son de validación |

**Huérfanos:** `ORPHAN_OBJECTIVE` **5 de 5** (ningún OE tiene conclusión) ·
`ORPHAN_EXPERIMENT` 0 · `ORPHAN_METRIC` 1 (M6, declarada como decisión abierta) ·
`ORPHAN_RESULT` 1 (los registros sobre `synthetic_v3`) · `DANGLING_ID` 4 rutas ·
`NOMENCLATURE_MIX` 1 (`OE-Mn` frente a `OEn`, sin correspondencia declarada; `ADR-001:119-128`
fija prohibiciones para otros identificadores y no para este).

**Diferencias con `research/traceability-matrix.md`:** doce fases declaradas «pendiente» que
tienen informe o registro; las columnas RES/DISC/CONC en `PENDING` «por diseño: no hay
resultados» mientras existe el capítulo 5; los umbrales «deliberadamente en blanco» mientras
`experiments/E15_suficiencia.json` los tiene fijados. `TUTOR-MAJ-011`.

**Claims auditados: 24.** `SUPPORTED` 13 · `PARTIALLY_SUPPORTED` 6 · `UNSUPPORTED` 3 ·
`CONTRADICTED` 2 · `UNVERIFIABLE` 0.

---

## 6. Findings

Severidad mapeada al esquema del orquestador: `CRITICAL` → **BLOCKER** · `MAJOR` →
**MAJOR** · `MINOR` → **MODERATE** · `INFO` → **MINOR** (**COSMETIC** si es puro formato).

### 6.1 Heredados y sin corregir (dry-run sobre E12)

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| TUTOR-MAJ-001 | MAJOR | `docs/memoria/cap5_resultados.md` · `docs/experiments/E12_evaluacion_recuperacion.md` | `cap5:82-89` · `E12:50-56, 145` | La tabla de recuperación reproduce una ejecución de cinco casos cuyo registro fue sustituido por otra de seis con cifras distintas; el capítulo cita un `.md` como registro | `E12_retrieval.json` y `tables/E12_retrieval_por_estrategia.csv`: nDCG 0,0 / 0,149 / 0,4679 / 0,6417 frente a 0,224 / 0,312 / 0,531 / 0,658; `n_cases = 6` | Declarar la ejecución canónica y llevar sus cifras al informe y al capítulo, citando el fichero de `experiments/` | Alto: es la evidencia de PI.2 y PI.4 en el capítulo | `NOT_FIXED` |
| TUTOR-MAJ-002 | MAJOR | `src/mecanico_ia_exp/experiments/retrieval_runner.py` · `docs/memoria/cap4_marco_metodologico.md` · `docs/matriz_validacion_pi.md` | `runner:161-191` · `cap4:255` · `matriz:164, 175-178` | La estrategia que alcanza Hit@10 = 1,00 construye la consulta con `caso["fault_id"]`, la etiqueta anotada, no con la predicción del modelo; el texto dice «condición predicha» y «el diagnóstico del modelo» | lectura del código; el modelo falla en C01 y C04, luego con la predicción la cifra sería otra | Declarar la procedencia del DTC; corregir `cap4:255` y la matriz; registrar el acoplamiento con M1 como limitación | Alto: convierte el resultado más llamativo en una cota oracular | `NOT_FIXED` |
| TUTOR-MIN-003 | MODERATE | `docs/experiments/E12_evaluacion_recuperacion.md` | `:22, :66, :119-125` | Tres pasajes siguen afirmando sin tachadura que C05 carece de documento relevante, corregido en E15 | `tables/E12_retrieval_por_caso.csv`: `C05_vacuum_leak, n_relevant=1` | Propagar la corrección al Hallazgo 4, a la tabla de casos y al recuento | Medio | `NOT_FIXED` |
| TUTOR-MIN-004 | MODERATE | `docs/experiments/E12_evaluacion_recuperacion.md` | `:50-56, :131-137` | P@10 y R@10 sin unidad declarada, y la explicación del techo es incoherente con un P@10 de 0,250 | lectura del informe y de `evaluation/retrieval.py` | Declarar la unidad y corregir la explicación | Bajo | `NOT_FIXED` |
| TUTOR-MIN-005 | MODERATE | `experiments/E12_retrieval.json` | claves de primer nivel | Sin `commit` ni `corpus_version`; `research/reproducibility.md` no los documenta para esa ejecución | claves: `experiment_id`, `executed_at`, `vehicle_id`, `engine_code`, `goldset`, `top_k`, `retrieval_depth`, `embedding`, `strategies` | Añadirlos al registro o documentarlos | Medio | `NOT_FIXED` |
| TUTOR-INF-006 | MINOR | `experiments/E12_retrieval.json` | `semantic` → `C03_o2_slow_response` | `distractor_ranks: []`, de modo que la afirmación de `E12:104-106` sobre el resultado #1 del motor `[LF]` no queda registrada | lectura del registro | Registrar el motor de cada fragmento recuperado o ampliar `distractor_files` | Bajo | `NOT_FIXED` |
| TUTOR-INF-007 | MINOR | `research/traceability-matrix.md` · `research/objective-coverage.md` | `:3` en ambos | Artefactos fechados el 1-09 a las 15:00, anteriores al cierre de las fases | comparación con `docs/experiments/README.md` | Actualizarlos al cierre de cada fase | Alto hoy: elevado a `TUTOR-MAJ-011` por cambio de alcance | `NOT_FIXED` |

### 6.2 Nuevos · MAJOR

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| TUTOR-MAJ-003 | MAJOR | `docs/memoria/cap4_marco_metodologico.md` · `docs/experiments/E5_preprocesamiento.md` | `cap4:95-108` · `E5:53-56, 68, 112` | La tabla del suelo de ruido y la narrativa que justifican la ventana de 120 s no coinciden con su registro en ninguna fila, y el descriptor que el texto usa como ejemplo es otro en el artefacto | `tables/E5_estudio_ventana.csv`: `noise_floor_p90` 0,3259 / 0,3653 / 0,4261 / 0,5133 frente a 0,369 / 0,399 / 0,438 / 0,512; para F05 a 30 s `best_feature` es `oxygen_sensor_mean` con `feature_declared_by_fault = True` | Reconciliar las cifras y la frase, o declarar cuál ejecución es canónica y regenerar la otra | Alto: es la justificación de la única decisión de preprocesamiento que condiciona todo | `OPEN` |
| TUTOR-MAJ-004 | MAJOR | `docs/memoria/cap5_resultados.md` · `cap3` · `cap6` | `cap5:52-62` · `cap3:82-84` · `cap6:47-49` | Una corrección registrada por el propio proyecto no llega a la memoria: con `synthetic_v3` el F1 del fallo de encendido pasa de 0,518 a 0,911 y la GRU deja de ser inferior al bosque | `E7_modelo_temporal.md:88-101`; `E6_baseline_synthetic_v3.json` macro F1 0,9321 frente a `E7_temporal_synthetic_v3.json` 0,9446 sobre 343 ventanas; `grep synthetic_v3 cap5` → 0 | Incorporar la ejecución con su n y su papel de sensibilidad; revisar L-15 y `cap3:82-84` | Alto: el tribunal encontrará una corrección del propio autor que el capítulo omite | `OPEN` |
| TUTOR-MAJ-005 | MAJOR | `docs/experiments/E15_suficiencia.md` · `docs/memoria/cap4_marco_metodologico.md` | `E15:213-226` · `cap4:143-145, 152-154` | El criterio del umbral 0,80 («precisión ≥ 0,93») no tiene fecha ni registro anterior al barrido, y el barrido corre sobre las 98 ventanas de validación de las que salen los nueve casos evaluados, solapamiento no declarado | `E15:215` frente a `E15:225` («ningún umbral alcanza 0,95»); la tabla del barrido no está en `experiments/` ni en `tables/` | Registrar la procedencia con fecha o declararla posterior; escribir la tabla del barrido; declarar el solapamiento en `cap4` | Medio: no cambia el contraste central, que abstiene por cobertura 0,00; sí la cifra «siete de nueve» | `OPEN` |
| TUTOR-MAJ-006 | MAJOR | `docs/memoria/cap5_resultados.md` | `:64-71` | La fila «Calibrado: ECE 0,085 · 0,886 · 0,878 · +0,009» no existe en `experiments/E15_suficiencia.json`, que el capítulo cita como registro | el JSON solo guarda `"calibration": "isotonic, cv=5 sobre entrenamiento"`; el único ECE registrado es el sin calibrar, en `E6_baseline_synthetic_v2.json` | Escribir el bloque de calibración en el registro o corregir la atribución | Alto: es la mitad del criterio de PI.1 | `OPEN` |
| TUTOR-MAJ-007 | MAJOR | `docs/memoria/cap2_objetivos.md` · `cap4` | `cap2:93-96` · `cap4:3` | Declara cerradas E8, E14 y E16 y ejecutada E17 —«experimento central» según la matriz—; ninguna tiene informe ni registro, y cuatro artefactos dan cuatro estados | `ls docs/experiments/` y `ls experiments/`; `README.md:17,23,25,26` las da pendientes; el plan da E8 ⬜, E14/E16 «integradas en E15» y E17 «parcial» | Declarar el estado real con la misma palabra en los cuatro artefactos; abrir informe de E17 o declarar que E15 lo absorbe | Alto: es la tabla de cobertura de objetivos | `OPEN` |
| TUTOR-MAJ-008 | MAJOR | `docs/memoria/cap6_conclusiones.md` | capítulo completo | No recorre OE1 → … → OE5 → OG con grado de cumplimiento; ningún objetivo tiene conclusión | `grep "OE1\|OE2\|OE3\|OE4\|OE5\|Objetivo general"` → 0 | Redactar el recorrido con grado y con el resultado que lo sostiene | Alto: condición literal de `FAIL` de GATE-03 y GATE-09 | `OPEN` |
| TUTOR-MAJ-009 | MAJOR | `docs/memoria/00_resumen.md` | fichero completo · `:34-35` | No existe ABSTRACT ni keywords en inglés; siete palabras clave donde la plantilla pide cinco | `grep -i "abstract\|keywords"` → 0 | Redactar el ABSTRACT como traducción fiel y dejar cinco palabras clave por idioma | Medio: incumplimiento visible en la primera página | `OPEN` |
| TUTOR-MAJ-010 | MAJOR | `docs/matriz_validacion_pi.md` · `cap5` · `cap6` | `matriz:39-40, 187-196` · `cap5:203-212` · `cap6:17-23` | ABSENT, PARTIAL y las dos DISTRACTOR se evalúan sobre **un único caso**, y las conclusiones afirman las subpreguntas «sostenidas» sin declararlo | `tables/E15_suficiencia.csv`: C05–C09 comparten `case_id F01_vacuum_leak__idle__10@120s` y confianza 0,9078; matriz de abstención reconstruida TP 3 · FP 0 · FN 2 · TN 4, cobertura en FULL 0,60 | Declarar el n por condición y publicar la matriz de abstención con cobertura | Alto: es la afirmación central del trabajo | `OPEN` |
| TUTOR-MAJ-011 | MAJOR | `research/traceability-matrix.md` · `research/objective-coverage.md` | `:3, 13-14, 41-43, 49-68` · `:3, 11-14, 31-32, 39` | Congelados el 1-09: doce fases «pendiente» que tienen informe o registro, RES/DISC/CONC «PENDING por diseño: no hay resultados» y umbrales «en blanco» | comparación con `docs/experiments/README.md` y `experiments/E15_suficiencia.json` | Regenerar ambos y reevaluar GATE-03 | Alto: la matriz es el instrumento de auditoría del tribunal | `OPEN` |
| TUTOR-MAJ-012 | MAJOR | `docs/memoria/cap4_marco_metodologico.md` · `research/decisions/` | capítulo completo | No etiqueta paradigma, tipo ni alcance temporal, que la plantilla pide expresamente; el marco que sí declara —ciclo de ciencias del diseño— no está fijado por ningún ADR, y el documento no distingue por escrito ese marco del protocolo de revisión documental | `grep` de «paradigma», «cuantitativ», «transversal», «tipo de investigación» sobre `cap4` → 0; `ls research/decisions/` → tres ADR, ninguno menciona el marco | Añadir las etiquetas; separar por escrito marco metodológico y protocolo de revisión; registrar el marco en un ADR | Medio-alto: criterio de mayor peso de la rúbrica de metodología | `OPEN` |
| TUTOR-MAJ-013 | MAJOR | `docs/memoria/bibliografia.md` | `:36, 40, 44, 50, 54, 76, 84` | Siete entradas con metadatos incompletos marcados `[VERIFY_SOURCE]`; dos usan «et al.» dentro de la entrada. Ninguna se ha comprobado inexistente | lectura de la bibliografía de depósito; dos de ellas sostienen el planteamiento del vacío en `cap1:16-17, 30` y `cap3:63-64, 127` | Completar los metadatos desde el documento original; retirar «et al.» | Alto: es el único incumplimiento que la normativa asocia expresamente a «No apto» | `OPEN` |

### 6.3 Nuevos · MODERATE y MINOR

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| TUTOR-MIN-006 | MODERATE | `docs/matriz_validacion_pi.md` | `:39` | «4 de 6 decisiones correctas» frente a «7 de 9» en `:120` y `cap5:139` | `tables/E15_suficiencia.csv`, columna `correct` | Actualizar la fila | Medio | `OPEN` |
| TUTOR-MIN-007 | MODERATE | `docs/matriz_validacion_pi.md` | `:216-217` | Lista como «Pendiente» los umbrales calibrados y la corrección del mapeo, que el mismo fichero y `cap5` dan por hechos | `:89, :127`; `E15_suficiencia.json` → `thresholds` | Retirar o reescribir las dos filas | Medio | `OPEN` |
| TUTOR-MIN-008 | MODERATE | `docs/matriz_validacion_pi.md` | `:69-73` | Conserva las cifras anteriores a la corrección (18 / 12 / 0,667) junto a la cobertura 1,00, sin decir cuál rige | lectura del bloque de PI.2 | Fechar cada cifra o retirar la anterior | Medio | `OPEN` |
| TUTOR-MIN-009 | MODERATE | `docs/memoria/cap5_resultados.md` | `:116-119` | «Los cuatro informes conservan la afirmación falsa tachada»: solo E11 y E12 la contenían y la conservan tachada | `grep -rn "P0171" docs/experiments/` → `E11:160`, `E12:33`, `E15:30`; `E2` y `E10` no contienen ni la afirmación ni ningún `~~` | Corregir el número y nombrar los informes | Bajo | `OPEN` |
| TUTOR-MIN-010 | MODERATE | `docs/memoria/cap2_objetivos.md` | `:47-48` | OE1 remite el procedimiento de revisión al capítulo 4; está en `cap3:20-29` | `grep PRISMA cap4` → 0 | Corregir la remisión | Bajo | `OPEN` |
| TUTOR-MIN-011 | MODERATE | `docs/memoria/cap2_objetivos.md` | `:6` | Cita un «Anexo A» con la correspondencia de objetivos que no existe | `ls docs/memoria/` | Crear el anexo o remitir a `research/propuestas-objetivos.md` | Medio: es un ítem de la checklist | `OPEN` |
| TUTOR-MIN-012 | COSMETIC | `cap5`, `cap6`, `cap3` | `cap5:211` · `cap6:63` · `cap3:191` | Vocabulario prohibido del proyecto: «la literatura» | `grep -n literatura docs/memoria/` | Sustituir por la expresión que corresponda en cada caso | Bajo | `OPEN` |
| TUTOR-MIN-013 | MODERATE | `docs/memoria/` · `figures/` | todas las tablas | Ninguna figura en la memoria pese a existir doce verificadas; ninguna tabla con identificador | `ls figures/`; `grep "FIG-" docs/memoria/` → 0; `validate_structure.py`, once avisos | Numerar las tablas; incorporar las figuras con pie y fuente | Medio | `OPEN` |
| TUTOR-MIN-014 | MODERATE | `docs/memoria/cap5_resultados.md` | `:55-57, 71-74, 148-149` | El apartado «Resultados obtenidos» interpreta, contra la separación que la plantilla impone | lectura de los tres pasajes | Mover a discusión | Bajo | `OPEN` |
| TUTOR-MIN-015 | MODERATE | `docs/memoria/cap4_marco_metodologico.md` | `:329` | «una batería de 283 tests»; la batería recolecta y pasa 290 y ningún informe declara 283 | `uv run pytest` ejecutado en esta revisión: «290 passed in 5.59s»; mayor cifra declarada: 242 en `E15:270` | Citar la cifra con su fecha o retirarla | Bajo | `OPEN` |
| TUTOR-MIN-016 | MODERATE | `docs/memoria/cap6_conclusiones.md` · `research/limitations-register.md` | `cap6:47, 62` · `:138, 199, 234` | L-10 y L-15 aparecen bajo «Altas» en el capítulo y como «media» en el registro, que además se contradice a sí mismo en L-10 | comparación de campos y del recuento | Unificar severidades y cuadrar el recuento | Bajo | `OPEN` |
| TUTOR-MIN-017 | MODERATE | `research/gates.md` · `reproducibility.md` · `traceability-matrix.md` · `objective-coverage.md` · `limitations-register.md` | `gates:13, 18` · `repro:38` · `trace:29, 94, 124` · `cov:5` · `lim:134` | Tres rutas citadas no existen: `experiments/E6_baseline.json`, `references/project/gaps.md` (define GAP-01 y GAP-02, evidencia de GATE-02) y `docs/memoria/02_objetivos.md` | `ls`, `find . -name gaps.md` → sin resultados | Corregir las rutas o crear el fichero que define GAP-01…GAP-04 | Medio: dos gates citan evidencia inexistente | `OPEN` |
| TUTOR-MIN-018 | MODERATE | `cap2` frente a `research/` y `ADR-001` | `cap2:43-96` · `cov:10-14` · `trace:29-32` · `ADR-001:142` · `ADR-003:90` | Dos series de identificadores para los mismos objetivos (`OE1…OE5` y `OE-M1…OE-M5`) sin correspondencia declarada; `ADR-001:119-128` prohíbe mezclar otras series y no esta | lectura de los cinco ficheros | Declarar la correspondencia en `ADR-001` o unificar | Medio: afecta al eslabón OE de la trazabilidad | `OPEN` |
| TUTOR-MIN-019 | MODERATE | `tables/` | `E6_baseline_confusion.csv`, `E6_baseline_importancias.csv`, `E7_temporal_por_clase.csv`, `E7_temporal_confusion.csv` | Las cuatro tablas sin sufijo de dataset son idénticas a las `_synthetic_v3`, mientras la memoria trabaja sobre v2 | `diff -q` sin diferencias frente a las `_synthetic_v3` | Renombrar o regenerar | Medio: quien abra el fichero «por defecto» lee otro dataset | `OPEN` |
| TUTOR-INF-008 | MINOR | `research/gates.md` | `:28` | «Los dos `FAIL` son de coherencia»; la tabla contiene uno | lectura de `:12-24` | Actualizar la regla de parada | Bajo | `OPEN` |
| TUTOR-INF-009 | MINOR | `docs/experiments/README.md` · `E10_corpus_vehiculo.md` | `README:19` · `E10:3, 26` | «corpus vacío» es cierto para el vehículo de E10 (Toyota), pero ningún índice remite a E11, que ingiere el corpus del vehículo de estudio | `results/rag_ingestion/toyota-corolla-2020_*.json`: `chunks_created 0`; `mazda-3-bk-2007_721d04b3.json`: 6 158 | Añadir la remisión | Bajo | `OPEN` |
| TUTOR-INF-010 | MINOR | `docs/experiments/E13_agente_slm.md` | fichero completo | Único informe sin sección de puertas de calidad; no cita por su nombre los registros de dos proveedores cuyas cifras sí reporta | `grep "Gates\|pytest"` → 0; `grep -rn "E13_agente_ollama\|E13_agente_echo" docs` → 0 | Añadir la sección y las rutas | Bajo | `OPEN` |
| TUTOR-INF-011 | MINOR | `docs/memoria/cap4_marco_metodologico.md` · `docs/experiments/E1_entorno.md` | `cap4:271-274` · `E1:34, 103` | No consta designado un proveedor oficial de modelo de lenguaje, aunque en la práctica todas las cifras publicadas proceden del mismo | lectura de ambos | Escribir la designación en `cap4` antes de E19 | Bajo | `OPEN` |
| TUTOR-INF-012 | MINOR | `research/available-skills.md` | `:8` | Registra herramientas de asistencia automatizada empleadas en el proceso, una de ellas aplicada en la enmienda de la pregunta | lectura del fichero | `[AUTHOR_DECISION_REQUIRED]`: decidir con el director su declaración conforme a la normativa y si el fichero acompaña al depósito | Medio si no se decide antes del depósito | `OPEN` |
| TUTOR-INF-013 | MINOR | `docs/experiments/E10_corpus_vehiculo.md` · `E11_carga_rag.md` | `E10:119` · `E11:128, 149` | La cadena acumulada de tests salta de 150 a 184 declarando 30 casos nuevos | aritmética de las cifras declaradas | Explicar el salto o corregir | Bajo | `OPEN` |
| TUTOR-INF-014 | MINOR | `docs/memoria/cap4_marco_metodologico.md` | `:143-145` | La regla de construcción del conjunto de nueve casos no está escrita; C04 es, entre los candidatos de F05 del registro de E9, el de menor confianza | `experiments/E9_xai_synthetic_v2.json`: 0,4652 frente a 0,7464 y 0,7365 | Escribir la regla de selección. No se ha encontrado indicio de selección posterior: se registra como observación | Bajo | `OPEN` |
| TUTOR-INF-015 | MINOR | `docs/experiments/E12_evaluacion_recuperacion.md` | `:173` | Declara «un solo modelo de embeddings» mientras el índice contiene dos | `cap4:129`; `docs/rag/multilingual.md:51`; `E12_retrieval.json` → `embedding_model` multilingüe | Ajustar la limitación a lo que el registro dice | Bajo | `OPEN` |
| TUTOR-INF-016 | MINOR | reglas compartidas | scripts de cribado | `validate_citations.py` no reconoce la forma `(Autor, año, REF-nnn)` y devuelve «0 citas»; `validate_references.py` marca las 38 entradas como no citadas. Falsos positivos verificados a mano | ejecución de ambos scripts | Registrar el límite en la documentación de reglas compartidas; no se corrige desde aquí | Bajo | `OPEN` |
| TUTOR-INF-017 | MINOR | `docs/memoria/00_resumen.md` | `:25-32` | El resumen no traslada la cobertura 3 de 5 que `cap5:156` sí declara | comparación de ambos | Incorporarla al reescribir el resumen tras E19 | Bajo | `OPEN` |

### 6.4 Coincidencias con otros auditores

Verificadas de forma independiente aquí. **Se corrigen una sola vez.**

| Finding del tutor | Equivalente | Nota |
|---|---|---|
| `TUTOR-MAJ-001` | `STAT-MAJ-006` | además es el finding heredado del dry-run |
| `TUTOR-MAJ-003` | `STAT-MAJ-001` | sobre E5 |
| `TUTOR-MAJ-004` | `STAT-MAJ-005` | corrección de E7 no propagada |
| `TUTOR-MAJ-005` | `STAT-MAJ-007` | procedencia del umbral |
| `TUTOR-MAJ-006` | `STAT-MAJ-008` | ECE calibrado sin registro |
| `TUTOR-MAJ-013` | `REF-MAJ-001`, `REF-MAJ-002` y siguientes | el tutor registra la consecuencia sobre GATE-10; el detalle por entrada lo mantiene la auditoría de referencias |

---

## 7. Decisiones que corresponden al autor

Ninguna se penaliza por estar abierta; se penalizaría no haberlas detectado, y todas están
detectadas salvo las tres últimas.

| # | Decisión | Dónde consta | Impacto |
|---|---|---|---|
| 1 | **Extensión del trabajo**: cuál de las tres cifras oficiales rige | `references/uax/conflictos-uax.md`, `UAX-RULE-CONFLICT-01`; `GATE-11` en `BLOCKED` | **El mayor.** El documento está en 12 550 palabras (≈ 31 páginas) frente al mínimo de 60 páginas del curso vigente, con «No apto» aparejado. Esa distancia no se cierra con correcciones |
| 2 | **Estilo de citación**: APA 6.ª o IEEE | `docs/memoria/bibliografia.md:6` | Formato de toda la bibliografía |
| 3 | **Objetivos reformulados, título definitivo y acotación de alcance**: consensuar y comunicar | `cap2:31-35, 64-66, 84-86, 107`; L-13 | `cap2:107` dice que la acotación «no consta comunicada formalmente» |
| 4 | **Cuál de las dos ejecuciones de E12 es canónica** | `TUTOR-MAJ-001` | Decide las cifras de PI.2 y PI.4 en el capítulo 5 |
| 5 | **Estrategia guiada**: redefinirla con la predicción del modelo o reportarla como cota superior con etiqueta oracular | `TUTOR-MAJ-002` | Decide cómo se presenta el resultado más llamativo del trabajo |
| 6 | **Papel de `synthetic_v3`**: sensibilidad u oficial | `TUTOR-MAJ-004`; `E7:119` lo declara sensibilidad | Cambia el signo de un resultado reportado |
| 7 | **M6: criterio o descriptiva** | `cap4:232-233`; incidencia I-05 | Decide si la latencia entra en la evaluación |
| 8 | **Cuándo se congela el pre-registro del marco canónico** | `ADR-002:44-45`; `research/prereg-classification.md:124-128`; L-07 | Decide si los experimentos pueden llamarse confirmatorios |
| 9 | **Convocatoria**: noviembre o diciembre de 2026 | `docs/memoria/LEEME.md:4-5` | Calendario |
| 10 | **Declaración del uso de herramientas de asistencia automatizada** conforme a la normativa, y si `research/available-skills.md` acompaña al depósito | `TUTOR-INF-012` | Integridad académica |

---

## 8. Secciones que deben conservarse tal cual (PRESERVE)

| Sección | Motivo |
|---|---|
| `docs/memoria/cap4_marco_metodologico.md:26-114` «Población y muestra» | El apartado mejor construido del documento: procedencia declarada, calibración constante a constante contra el manual con su página, taxonomía cerrada de `dataset_type` y limitación de validez externa con su consecuencia. Solo hay que corregir la tabla del suelo de ruido; el resto no se toca |
| `docs/memoria/cap4_marco_metodologico.md:174-201` «Variables intervinientes» | Declara una sola variable manipulada y enumera las controladas. Es lo que hace interpretable el experimento central, y el registro lo confirma |
| `docs/memoria/cap4_marco_metodologico.md:116-139` «Muestra: corpus documental» | Corpus operacional descrito en el capítulo que le corresponde, con huella SHA-256, aplicabilidad por motor y procedencia conservada hasta el fragmento. Cumple exactamente la separación que la norma exige |
| `docs/memoria/cap5_resultados.md:121-162` PI.3 y PI.4 | Coincide con `tables/E15_suficiencia.csv` en las nueve filas y las seis columnas. Solo hay que **añadir** el n por condición |
| `docs/memoria/cap5_resultados.md:164-194` el modelo de lenguaje | Coincide con los siete registros de `experiments/E13_agente_*.json`. La lectura de los tres resultados es proporcional y verificable |
| `docs/memoria/cap1_introduccion.md:101-111` la advertencia sobre la procedencia | Sostiene la honestidad de todo el documento y dice con precisión qué sostiene un resultado sobre sintéticos y qué no |
| `docs/memoria/cap5_resultados.md:47-50` el marcador `[RECONCILIAR]` | Declarar una discrepancia en lugar de elegir una cifra es la conducta correcta. Se conserva hasta que la discrepancia se explique |
| `docs/memoria/cap6_conclusiones.md:32-101` las limitaciones | Diecisiete limitaciones reales, ninguna ceremonial, todas con origen en un resultado o un documento de método. Solo hay que corregir dos severidades y completar tres enunciados |
| `docs/methodology/` (los cuatro ficheros) | Modelo de evidencia, diseño experimental, política de abstención y métricas. Es el andamiaje conceptual del trabajo y está mejor escrito que la mayoría de los capítulos |
| `configs/goldset_mazda3_bk.yaml` y `tests/test_retrieval_eval.py:195-207` | Verdad de referencia anclada al manual y no al criterio del autor, y test que impide que la consulta contenga la respuesta. Es el control que más protege el resultado de PI.2 |

---

## 9. Fortalezas con evidencia

Solo lo verificado en esta revisión, con el artefacto y el campo concreto. Sin adjetivos.

| ID | Fortaleza | Evidencia |
|---|---|---|
| S-01 | La cadena de procedencia se reconstruye por caso hasta el último eslabón, sin reconstrucción posterior | `experiments/E15_suficiencia.json`, C01: cada observación con señal, estadístico, valor, dirección y ventana; cada documento con `chunk_id`, sección, página, editor, `applicability`, `authority_level` y `dtc_codes`; cada afirmación con su evidencia observacional y documental |
| S-02 | El contraste central está aislado: solo cambia la variable manipulada | `tables/E15_suficiencia.csv`, C05–C09: mismo `case_id`, misma `confidence` 0,9078, mismo `n_observations` y `n_claims`; cambian `corpus_variant` y `n_excluded_chunks` (0/70/51/16/16) |
| S-03 | La abstención no es insensible ni trivial, y su cobertura se reporta | 3 de 5 EXPLAIN en FULL frente a 0 de 4 en las demás condiciones; `cap5:156` publica la cobertura en lugar de solo la corrección |
| S-04 | La decisión es determinista y externa al modelo de lenguaje, y esa separación se mide | `docs/methodology/abstention-policy.md:3-10`; recomputado sobre los siete registros: `respected_verdict` 9/9 en las tres configuraciones publicadas y `fake_citations` 0 en las siete |
| S-05 | Las tres filas del modelo de lenguaje del capítulo 5 coinciden exactamente con sus registros | 7/9 · 9/9 · 0 · 2 · 20,4 s; 7/9 · 9/9 · 0 · 2 · 14,7 s; 9/9 · 9/9 · 0 · 0 · 13,1 s |
| S-06 | El distractor es real y del propio corpus, no fabricado | `configs/goldset_mazda3_bk.yaml:10-14`; `E12_retrieval.json`, `semantic`: `cases_with_distractor_above_relevant = 1` con `distractor_ranks: [3]` |
| S-07 | Existe el test que impide que la evaluación mida la consulta en lugar de la recuperación | `tests/test_retrieval_eval.py:195-203`, en verde |
| S-08 | Una afirmación propia demostrada falsa se conserva tachada con su corrección | `E12:32-40` y `E11:160-167`, sobre P0171 → P2187 |
| S-09 | El baseline trivial existe y la distancia con el modelo es de otro orden | `E6_baseline_synthetic_v2.json`: `majority_baseline.macro_f1 = 0.0741` frente a `metrics.macro_f1 = 0.8788`, n = 98 |
| S-10 | Hay control del suelo de ruido antes de interpretar tamaños de efecto, y se reporta la estrategia que no aportó | `cap4:88-94`; `E12:139-146` reporta que la búsqueda híbrida no aportó nada en lugar de retirarla |
| S-11 | La procedencia del dato se declara en cada capítulo, con taxonomía cerrada | `docs/methodology/experimental-design.md:65-78`; `cap1:101-111`, `cap4:51-58`, `cap5:3-8`, `cap6:25-30`; la matriz indica por subpregunta cuánto depende del realismo del dato |
| S-12 | El cierre del test es técnico, no de palabra | `research/reproducibility.md:44-51`: excepción en `load_partition("test")`, con tres tests |
| S-13 | La batería de calidad pasa hoy, ejecutada por esta revisión | `uv run pytest` → **290 passed in 5,59 s** sobre `a6a5f40` |
| S-14 | La memoria declara por sí misma una discrepancia entre informes y registros en lugar de elegir una cifra | `cap5:47-50` |
| S-15 | La interpretación de la precisión con un solo relevante es correcta | `E12:131-137` |
| S-16 | Los desenlaces que refutarían el trabajo se escribieron antes y se reporta cuáles ocurrieron | `docs/methodology/experimental-design.md:115-121`; `matriz:225-236` declara que dos de los cinco se materializaron |

---

## 10. Qué desbloquea el estado

En orden de impacto. Las cuatro primeras cierran los cuatro gates de integridad y ninguna
vuelve al laboratorio.

1. Reconciliar las tres cifras publicadas sin artefacto vigente: `cap5:82-89`,
   `cap4:95-108` y `cap5:69-71`. Cierra GATE-06 y GATE-07.
2. Declarar el estado real de E8, E14, E16 y E17 con la misma palabra en los cuatro
   artefactos. Cierra GATE-05.
3. Acotar las afirmaciones de `matriz`, `cap5:203-212` y `cap6:17-23` al n por condición, y
   declarar la procedencia del DTC de la estrategia guiada.
4. Completar los metadatos de las siete entradas de la bibliografía. Cierra GATE-10.
5. Escribir el capítulo 6 por objetivo, con grado de cumplimiento. No depende de E19.
6. Añadir el ABSTRACT y las etiquetas metodológicas; regenerar los dos artefactos de
   trazabilidad.

Después de eso, y solo después, tiene sentido plantear E18, E19 y E20.
