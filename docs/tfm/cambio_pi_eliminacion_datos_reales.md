# Cambio de la pregunta de investigación: eliminación del requisito «datos reales»

**Fecha:** 3 de septiembre de 2026 · **Decisión:** ADR-003
(`research/decisions/ADR-003-pi-sin-requisito-de-datos-reales.md`) · **Autor:** Luis Daniel
Díaz · **Skill aplicado:** `uax-tfm-ai-researcher` (flujo 01, enmienda documentada y no
retroactiva).

Actualización quirúrgica: cambia el requisito sobre la procedencia de los datos y nada del
problema científico. Cada aparición de «reales» se clasificó antes de tocarla; no hubo
sustitución ciega.

## 1. PI anterior

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II
> reales, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la
> evidencia disponible no es suficiente para sostener una explicación en lugar de generar
> una hipótesis sin fundamento?

## 2. PI nueva (única vigente)

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una
> hipótesis sin fundamento?

Diferencia intencional: «datos OBD-II reales» → «datos OBD-II». La palabra no vuelve a la PI.

## 3. Motivo del cambio

La fase que incorpora datos reales (E3) lleva bloqueada desde el inicio por falta de una
fuente con fallos etiquetados y documentación de taller aplicable. Toda la evidencia
experimental (E1–E17) se ha obtenido sobre `synthetic_v2`, calibrado contra el manual del
vehículo, y respondía a una «versión condicional» de la pregunta. Las cuatro subpreguntas
interrogan propiedades del agente, no del dato; solo PI.1 depende materialmente del realismo
de la telemetría. Exigir «reales» en el enunciado condicionaba las cuatro a una precondición
que afecta a una. Detalle y opciones descartadas en ADR-003.

## 4. Impacto conceptual

- **No cambia:** el problema científico (explicación plausible ≠ explicación sustentada), el
  experimento central (FULL / PARTIAL / ABSENT / DISTRACTOR sobre el mismo caso), la
  separación entre quien diagnostica, quien decide y quien redacta, la arquitectura RAG sobre
  PostgreSQL con pgvector, la doble trazabilidad, el alcance (sin descubrimiento autónomo,
  memoria evolutiva ni aprendizaje continuo).
- **Cambia:** la procedencia del dato pasa de precondición de la PI a variable declarada
  (`dataset_type`) y a limitación de validez externa (L-01). E3 pasa de bloqueo a validación
  externa. La matriz de validación deja de responder a una «versión condicional».
- **Se refuerza:** la distinción entre dato real, sintético y simulado se hace obligatoria y
  cerrada en el código; ningún resultado sintético se presenta como comportamiento real.

## 5. Documentos revisados

Inventario previo: 95 apariciones de «datos OBD-II reales», «OBD-II reales», «datos reales»
y variantes en el material vivo (`mecanico-ia-exp/` sin respaldos, más el espejo del
proyecto dentro del skill), más un barrido de formas próximas («OBD-II real», «caso real»,
«vehículo real») y uno semántico («versión condicional», «pregunta literal», «la PI habla
de»). Cada aparición se clasificó en uno de tres grupos:

| Grupo | Qué es | Tratamiento | Apariciones |
|---|---|---|---|
| A | La PI literal | sustituida por la PI nueva | 24 ficheros (README, matriz, plan, matriz de trazabilidad, `__init__.py`, generador de cuadernos, 17 cuadernos, informe de seguimiento, capítulo 1, espejo del skill) |
| B | Afirmaciones que condicionaban el alcance al enunciado anterior («la PI dice reales», «bloquea la PI literal», «versión condicional», «E3 bloqueada» como precondición) | reescritas una a una por su texto exacto; en informes de fase cerrados, nota fechada en lugar de reescritura | 73 sustituciones + 3 notas |
| C | Menciones correctas a datos reales: nombre de la fase E3, limitación L-01 y L-16, recomendaciones («cuando se disponga del vehículo real»), comparación real/sintético en código y análisis, característica de un estudio revisado, trabajo futuro | conservadas | ≈ 40 |

Los ADR-001 y ADR-002 y el análisis `research/e3-candidatos-datos.md` conservan su texto
como registro histórico; este último recibe una nota fechada.

## 6. Secciones modificadas

| Documento | Sección | Cambio |
|---|---|---|
| `README.md` | pregunta de investigación | PI nueva |
| `docs/matriz_validacion_pi.md` | cabecera; «Advertencia que condiciona toda la matriz» → «Procedencia de los datos, y lo que condiciona»; «Lo que esto NO significa»; «Lo que falta…» | la matriz responde a la PI sobre el dataset declarado; la condición pasa a procedencia y a L-01; E3 como validación externa |
| `docs/plan_experimental_macbook.md` | estado de fases; tres exigencias; E20; riesgos; decisiones abiertas | E3 de «bloquea la PI literal» a «validación externa»; riesgo rebajado a medio |
| `docs/EXPERIMENTO_PASO_A_PASO.md` | estado; tabla de pendientes | estado actualizado a pasos 0–13; datos reales como validación externa |
| `docs/methodology/experimental-design.md` | experimento central; **nueva sección «Procedencia de los datos»** | «caso real» → «caso»; taxonomía `real / synthetic / simulated / public_dataset`, campos mínimos de la ficha, regla de no agregación |
| `docs/methodology/calibracion-datos-sinteticos.md` | «Qué se hizo y qué no» | la PI no exige reales; la validez externa sí |
| `docs/experiments/E2_datos_sinteticos.md`, `E13_agente_slm.md` | limitaciones / siguiente | nota fechada (informes cerrados, no reescritos) |
| `docs/experiments/README.md` | tabla de fases | E3 pendiente como validación externa |
| `docs/entregas/informe_seguimiento_1_borrador.md` | PI; tabla de fases; dificultades; trabajo previsto | PI nueva; E3 reencuadrada |
| `docs/memoria/00_resumen.md` | última frase | procedencia declarada en lugar de «condicionales» |
| `docs/memoria/cap1_introduccion.md` | PI; advertencia final | PI nueva; la advertencia pasa a declarar procedencia y validez externa |
| `docs/memoria/cap2_objetivos.md` | justificación del OG; OE2; tabla de correspondencia | «datos OBD-II» definitivo; E3 y E19–E20 desbloqueadas de E3 |
| `docs/memoria/cap4_marco_metodologico.md` | estado; «Muestra: telemetría»; tabla de la muestra; limitación declarada | procedencia obligatoria; `dataset_type` en la tabla |
| `docs/memoria/cap5_resultados.md` | estado; «Lo que no sostienen» | sin «versión condicional»; acotado a procedencia |
| `docs/memoria/cap6_conclusiones.md` | conclusión; L-01; prospectiva; E20 | idem |
| `docs/memoria/LEEME.md` | regla 3; tabla de dependencias | idem |
| `research/traceability-matrix.md` | PI; fila PI.1; fila E3; procedencia bajo la matriz; **I-07 resuelta** (original conservado) | |
| `research/gates.md` | GATE-01 | `PASS_WITH_OBSERVATIONS` → `PASS` (3-09-2026); la validez externa sigue en L-01 |
| `research/objective-coverage.md` | OE-M2 | `BLOCKED` → `PASS_WITH_OBSERVATIONS`; E10 cerrada |
| `research/limitations-register.md` | L-01 «Consecuencia» | ya no «la PI dice reales»; validez externa acotada a procedencia |
| `research/propuestas-objetivos.md`, `research/e3-candidatos-datos.md` | notas de resolución | |
| `src/mecanico_ia_exp/__init__.py` | docstring | PI nueva |
| `src/mecanico_ia_exp/data/metadata.py` | `DatasetType` | `synthetic, real` → `synthetic, real, simulated, public_dataset`, documentados |
| `tests/test_dataset_provenance.py` | nuevo | taxonomía cerrada; ficha del dataset con procedencia |
| `scripts/gen_notebooks.py` y 17 cuadernos | celda de cabecera; cuaderno 02; cuadernos 10 y 15 | PI nueva; E3 como validación externa; E20 «mismo caso» |
| Espejo del skill (`TFM/.claude/skills/uax-tfm-ai-researcher/references/project/`) | `research-question`, `hypotheses`, `datasets`, `gaps`, `objectives`, `decisions`, `README` | PI nueva; GATE-01; hipótesis con «procedencia declarada»; GAP-01 revisado; E3 como validación externa. **Fuera del repositorio Git** |

## 7. Secciones que no requirieron modificación

Subpreguntas PI.1–PI.4 y sus criterios; hipótesis en su predicción y criterio; métricas
M1–M6; diseño de condiciones; casos anotados; código de los modelos, la recuperación, el
verificador y el agente; informes de fase E1, E4–E12, E15 (mencionan datos reales solo como
fase, comparación o recomendación); documentación RAG (`vehicle-corpus`,
`vehicle-applicability`, `rag-evaluation`: recomendaciones sobre el vehículo real);
`research/limitations-register.md` salvo L-01; ADR-001 y ADR-002 (históricos);
`docs/memoria/cap3_marco_teorico.md` y `bibliografia.md` (no dependían del requisito);
`research/references/`.

## 8. Objetivos afectados

| Objetivo | Antes | Ahora | Modificación |
|---|---|---|---|
| OG (opción A propuesta el 1-09) | escribía «datos OBD-II» *a la espera de E3* | «datos OBD-II» definitivo | ninguna en el enunciado; cambia la justificación (cap. 2) |
| OE2 entorno y corpus | `BLOCKED` por E3 | `PASS_WITH_OBSERVATIONS`; E3 validación externa | ninguna en el enunciado |
| OE3, OE4 | — | — | ninguna |
| OE5 evaluación | E19 y E20 «bloqueadas por E3» | pendientes de la decisión sobre el dataset de evaluación final | ninguna en el enunciado |

Ningún objetivo cambia de enunciado. Las reformulaciones de OG, OE3 y OE5 siguen pendientes
de consenso con el director por motivos ajenos a este cambio.

## 9. Hipótesis afectadas

Ninguna cambia de predicción ni de criterio. La columna «dataset» de la tabla de hipótesis
(espejo del skill) pasa de «real» a «procedencia declarada (hoy `synthetic_v2`)». La
hipótesis principal sigue evaluando explicación, trazabilidad, suficiencia y abstención;
ninguna depende del origen real del dato salvo en cuanto a generalización, que se declara.
No se modificó ninguna hipótesis para garantizar resultados.

## 10. Impacto metodológico

- Nueva sección «Procedencia de los datos» en `docs/methodology/experimental-design.md` y en
  el capítulo 4: taxonomía cerrada, campos mínimos de la ficha (`dataset_id`,
  `dataset_type`, `source`, `version`, vehículo o simulador, muestreo, `created_at`,
  `notes`), regla de no agregación entre procedencias.
- El apartado «Población y muestra» declara la procedencia en la tabla de la muestra.
- Los datos sintéticos quedan con sus usos legítimos declarados (desarrollo, inyección de
  fallos, equilibrio, ablaciones, cuatro condiciones) y con lo que no sostienen.
- Los datos reales, si se obtienen, se describen con vehículo, sesión, señales, frecuencia,
  condiciones, procedimiento y limitaciones.

## 11. Impacto experimental

E3 deja de ser precondición y pasa a validación externa. E19 y E20 dejan de estar bloqueadas
por E3 y pasan a depender de una decisión del autor: sobre qué dataset se ejecuta la
evaluación final. Ningún experimento se repite; ningún resultado se recalcula.

## 12. Impacto sobre datasets

| Dataset | `dataset_type` | Estado |
|---|---|---|
| `synthetic_v1` | `synthetic` | histórico (E2) |
| `synthetic_v2` | `synthetic` | conjunto de trabajo de E5–E17 |
| `synthetic_v3` | `synthetic` | variante registrada |
| datos reales (E3) | `real` | sin fuente; validación externa |

Las tres fichas existentes ya declaraban `dataset_type: synthetic`. Los registros de
`experiments/` llevan `dataset_id` pero no `dataset_type`; añadirlo forma parte de la
cabecera de tracking pendiente (§45 del prompt maestro), no de este cambio.

## 13. Impacto sobre resultados previos

Ninguno se invalida. Clasificación según su función respecto de la PI nueva:

| Resultado | Clasificación | Motivo |
|---|---|---|
| E15/E17: FULL → EXPLAIN, ABSENT/PARTIAL/DISTRACTOR → ABSTAIN sobre el mismo caso (7/9) | `DIRECT_EVIDENCE` para PI.3 y PI.4 | manipula la evidencia documental con dato, modelo y atribución fijos; depende poco del realismo del dato |
| E14/E15: cobertura de soporte 1,00; distractor degradado por el validador | `DIRECT_EVIDENCE` para PI.2 y PI.4 | idem |
| E12: recuperación semántica 0,00 frente a guiada 1,00; efecto del idioma | `DIRECT_EVIDENCE` para M2 | el corpus es real (manual); la consulta no depende del dato |
| E13: modelo de lenguaje 9/9 válidas, 0 citas inventadas | `DIRECT_EVIDENCE` para M3 y M4 | idem |
| E6/E7: bosque F1 0,879, GRU 0,823; calibración ECE 0,144 → 0,085 | `SUPPORTING_EVIDENCE` para PI.1 | el diagnóstico sí depende del realismo de la telemetría; sobre sintéticos caracteriza el mecanismo, no el rendimiento en vehículo |
| E9: atribución como evidencia observacional | `SUPPORTING_EVIDENCE` para PI.2 | idem |
| E2, E4, E5: generación, exploración, ventana y suelo de ruido | `DEVELOPMENT_ONLY` | instrumentales |
| Experimentos del repositorio heredado (`EXP-*`) | `HISTORICAL` / `OUT_OF_SCOPE` | ADR-001; no entran sin pasar el control de `legacy-map.md` |

Ningún resultado se reinterpreta más allá de lo que mostró. Todos conservan su etiqueta
`synthetic` y su partición (validación).

## 14. Pendientes

- Decisión del autor: dataset de la evaluación final (E19) y fuente de datos reales para E3.
- `dataset_type` en la cabecera de todos los registros de `experiments/` (con el tracking de
  §45 del prompt maestro).
- Reformulación de OG, OE3 y OE5 con el director (independiente de este cambio).
- Espejo del skill: los ficheros `experiments.md` y `results.md` conservan estados de fase
  del 1 de septiembre (E7–E17 cerradas después); no se han tocado porque no dependen del
  requisito de datos reales, pero están desactualizados.
- Matriz de trazabilidad: columnas RES/DISC/CONC en `PENDING` desde el 1 de septiembre
  aunque E7–E17 tienen resultados; actualización separada.
- Humanización: **no ejecutada**, ver §16.

## 15. Changelog

Cada fila: fichero · sección · concepto anterior · concepto actualizado · razón.

| Fichero | Sección | Antes | Después | Razón |
|---|---|---|---|---|
| `research/decisions/ADR-003-*.md` | nuevo | — | enmienda fechada de la PI, opciones, impacto, reversibilidad | el flujo 01 exige enmienda documentada, no cambio silencioso |
| `README.md`, `docs/plan_experimental_macbook.md`, `docs/matriz_validacion_pi.md`, `research/traceability-matrix.md`, `src/mecanico_ia_exp/__init__.py`, `scripts/gen_notebooks.py`, 17 cuadernos, `docs/entregas/informe_seguimiento_1_borrador.md`, `docs/memoria/cap1_introduccion.md`, espejo `research-question.md` | PI | «datos OBD-II reales» | «datos OBD-II» | PI nueva |
| `docs/matriz_validacion_pi.md` | advertencia inicial | «la pregunta no puede responderse todavía; versión condicional» | «responde a la PI sobre el dataset declarado; validez externa en L-01» | la condición deja de estar en el enunciado |
| `docs/matriz_validacion_pi.md` | «Lo que falta para responder…» | datos reales como requisito que «bloquea la pregunta literal» | datos reales como validación externa | E3 ya no es precondición |
| `docs/plan_experimental_macbook.md` | estado E3; riesgos; decisiones | «bloquea la PI literal»; riesgo alto | «validación externa»; riesgo medio | idem |
| `docs/methodology/experimental-design.md` | experimento central; nueva sección | «caso real», «OBD-II real →» | «caso», «OBD-II →»; taxonomía de procedencia | §10 y §15 del encargo |
| `docs/methodology/calibracion-datos-sinteticos.md` | qué no se hizo | «la PI habla de reales y exige registros reales» | «la PI no exige reales; la validez externa sí» | coherencia |
| `research/limitations-register.md` | L-01 consecuencia | «responde a una pregunta más estrecha que la enunciada» | «acotada a la procedencia declarada» | L-01 sigue crítica, cambia su naturaleza |
| `research/traceability-matrix.md` | I-07 | bloqueante | resuelta por ADR-003, original conservado | trazabilidad de la incidencia |
| `research/gates.md` | GATE-01 | `PASS_WITH_OBSERVATIONS` | `PASS` | observación resuelta |
| `research/objective-coverage.md` | OE-M2 | `BLOCKED` | `PASS_WITH_OBSERVATIONS` | E3 no bloquea; E10 cerrada |
| `src/mecanico_ia_exp/data/metadata.py` | `DatasetType` | dos valores | cuatro valores documentados | §10 |
| `tests/test_dataset_provenance.py` | nuevo | — | taxonomía cerrada y ficha con procedencia | §10 |
| `docs/memoria/cap1…cap6`, `00_resumen`, `LEEME` | advertencias y limitaciones | «condicional», «la pregunta enuncia reales» | «procedencia declarada», «validez externa» | coherencia con la PI |
| `docs/memoria/cap1`, `cap3`, `cap4`, `cap5`, `cap6` | vocabulario | «la literatura» ×6, «claramente» ×2, «no existe» ×1, «condicional» ×3 | vocabulario admitido por el skill | revisión académica (§20.1) |
| `docs/memoria/cap3`, `cap4`, `cap5` | títulos consecutivos | seis pares sin texto | párrafo de anuncio | plantilla UAX |
| `docs/experiments/E2`, `E13`; `research/e3-candidatos-datos.md`; `research/propuestas-objetivos.md` | notas | — | nota fechada de resolución | informes cerrados no se reescriben |
| Espejo del skill (7 ficheros) | PI, GATE-01, hipótesis, datasets, decisiones, vacío, objetivos | requisito de datos reales | procedencia declarada | coherencia del índice de lectura |

## 16. Quality gates

**Scripts del skill** (candidatos, verificados a mano):

| Script | Resultado | Lectura |
|---|---|---|
| `validate_structure.py` | 0 ERROR (eran 6: títulos consecutivos, corregidos); 24 avisos | los avisos son marcadores declarados (`[VERIFY_SOURCE]`, `[AMPLIAR]`, borradores) y tablas sin `TAB-NNN`, pendientes del volcado a Word |
| `validate_citations.py` | 0 ERROR; 1 aviso (cita larga sin página en cap. 5) | la «cita» es la salida literal del modelo, no una cita bibliográfica |
| `validate_references.py` | con las etiquetas `REF-`/`MET-` no reconoce citas; sin ellas, 8 ERROR y 26 avisos | los 8 son falsos positivos con citas compuestas («Béchard y Ayala», «Chow, 1970; Geifman…»): las ocho tienen entrada. Las etiquetas se retiran al volcar a Word |
| `validate_traceability.py` | cabecera no reconocida | la matriz usa `Sub-PI / Objetivo / Hipótesis / Experimento / Métricas / RES / DISC / CONC`; no se reestructura por el script |
| `word_count.py` | 12 336 palabras netas (≈ 30 páginas) | extensión pendiente de decisión con el director |
| `ruff`, `mypy --strict`, `pytest` | verde; 4 tests nuevos | — |

**Gates del skill afectados:** GATE-01 `PASS` (era `PASS_WITH_OBSERVATIONS`). GATE-03 sigue
`FAIL` por los objetivos pendientes de consenso, ajeno a este cambio. GATE-05, 08, 09
`BLOCKED`; GATE-11 `BLOCKED` por la extensión. GATE-13 `PASS`: ninguna cifra ni resultado
alterado; ninguna referencia añadida.

**Humanización (§20.3–20.5 del encargo): no ejecutada.** El skill impone como precondición
que los gates académicos estén en `PASS` o `PASS_WITH_OBSERVATIONS` y ordena parar y decirlo
si no lo están. GATE-03 está en `FAIL` y GATE-05, 08 y 09 en `BLOCKED`. Se aplicaron las
reglas académicas (vocabulario, estructura, fuerza de las afirmaciones) y la validación de
citas; la pasada de voz PHILIP-K-MODERATE y los antipatrones se harán cuando el gate
académico cierre. Comprobación previa hecha: la memoria no contiene aperturas vacías,
intensificadores sin evidencia ni marketing tecnológico del listado del skill.

**Revisión semántica:** tras los scripts se releyeron las secciones modificadas de los
capítulos 1, 2, 4, 5 y 6 y de la matriz. Ninguna cifra cambió (`validate_numbers.py --diff`
no era aplicable porque los cambios no tocan cifras; se comprobó por lectura).
