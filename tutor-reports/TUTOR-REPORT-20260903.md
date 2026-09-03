# Tutor Evaluation Report — 3 de septiembre de 2026

**Unidad evaluada:** actualización transversal de la pregunta de investigación (eliminación
del requisito «datos OBD-II reales»), ADR-003.
**Modo:** `TRACEABILITY_REVIEW` + `EVIDENCE_REVIEW`, acotados al cambio.
**Instantánea:** `mecanico-ia-exp` en el commit `b7a68f9` (los siete commits `ce9be6d` …
`b7a68f9` del 3 de septiembre de 2026), más el espejo del proyecto en
`TFM/.claude/skills/uax-tfm-ai-researcher/references/project/` (fuera de Git).
**Responsable del veredicto:** quien lo adopte; este informe no se firma por ninguna
herramienta.

## 1. Veredicto

**Primera evaluación (instantánea `b7a68f9`): `FAIL`**, por un `MAJOR` abierto
(TUTOR-MAJ-001): un artefacto canónico de trazabilidad conservaba la PI anterior como
vigente. Score de los bloques evaluables: **39 / 47**. Los findings preceden al score.

**Reevaluación del mismo día (§25), tras las correcciones del productor:
`PASS_WITH_OBSERVATIONS`.** Score de los bloques evaluables: **45 / 47**. Quedan abiertos
solo `INFO` (INF-003, decisión del autor) y una observación preexistente de trazabilidad.

## 2. Alcance revisado y limitaciones de esta evaluación

- Se evaluó **solo el cambio de la PI**: su registro (ADR-003), su propagación, la coherencia
  PI ↔ objetivos ↔ hipótesis ↔ vacío ↔ metodología ↔ experimentos ↔ métricas ↔ conclusiones
  previstas, la distinción de procedencias, el alcance, y la invariancia de cifras,
  referencias y resultados. No se evaluó el contenido científico de los capítulos ni los
  experimentos en sí.
- **El skill de tutor está incompleto en disco**: faltan `workflows/`, `templates/`
  (informe de 26 secciones, finding, scorecard, traceability-audit), `references/rubrics/`
  y `scripts/` (`validate_skill.py`, `finding_ledger.py`). Se evaluó con
  `references/evaluation/*` y `references/shared-rules.md`, que sí existen, y con las reglas
  compartidas del researcher. La estructura de este informe sigue las secciones que el
  SKILL.md nombra; donde la plantilla ausente exigía algo no reconstruible, se declara.
- Los IDs de finding empiezan en 001 porque no existe ningún `TUTOR-REPORT-*` anterior en
  `tutor-reports/`.

## 3. Evidencia inspeccionada

| Qué | Cómo |
|---|---|
| PI viva | `grep` de «OBD-II reales, rastreando» y de «¿Puede un agente con RAG…» en README, docs, research, src, scripts, 17 cuadernos y espejo del skill |
| Supervivientes de «reales» | listado con línea en material vivo; clasificación manual de cada uno |
| Invariancia de cifras | `validate_numbers.py --diff` entre `HEAD~7` y `HEAD` sobre cap. 1, 2, 4, 5, 6, resumen, matriz de validación, matriz de trazabilidad y registro de limitaciones |
| Resultados y referencias | `git diff --stat HEAD~7 HEAD` sobre `experiments/`, `results/`, `tables/`, `figures/`, `research/references/`, `bibliografia.md` |
| Coherencia | lectura de `cap2_objetivos.md` (OG y OE1–OE5), `matriz_validacion_pi.md` (filas PI.1–PI.4, veredicto), `cap4` §Muestra, `experimental-design.md` §Procedencia, `cap6` §Conclusiones y §Limitaciones, `traceability-matrix.md` §1, §2, §3, I-07 |
| Procedencias | `dataset_type` en las tres fichas `data/raw/synthetic/*.meta.json`; taxonomía en `metadata.py`; usos de «simulado» |
| Alcance | `grep` de descubrimiento autónomo, memoria evolutiva, aprendizaje continuo, promoción autónoma, multiagente en memoria y diseño |
| Registro de la decisión | `ADR-003` (contexto, opciones, decisión, impacto, reversibilidad); `ADR-002` §régimen de enmiendas |
| Tests | `pytest` (`tests/test_dataset_provenance.py`, 4 casos) ejecutado por el productor; el tutor comprobó que el fichero existe y qué afirma |

## 4. Claims auditados

| ID | Claim (literal abreviado) | Ubicación | Tipo | Fuente | Clase |
|---|---|---|---|---|---|
| C-01 | «La única PI vigente es la nueva» | `docs/tfm/cambio_pi…md` §2, §16 | E5 | grep en material vivo | **PARTIALLY_SUPPORTED** → `research/traceability-matrix.md:20-21` conserva la PI antigua (TUTOR-MAJ-001) |
| C-02 | «“reales” solo permanece como fase, limitación, recomendación, comparación o registro histórico» | idem §5 | E5 | listado de supervivientes | **PARTIALLY_SUPPORTED** → tres restos condicionantes (MIN-001, MIN-002, MIN-003) |
| C-03 | «Ningún objetivo cambia de enunciado» | idem §8 | E5 | `cap2_objetivos.md:16-80` vs `HEAD~7` | **SUPPORTED** |
| C-04 | «Ninguna hipótesis cambia de predicción ni de criterio» | idem §9 | E5 | `matriz_validacion_pi.md:37-40` sin cambios de criterio; espejo `hypotheses.md` solo cambia la columna dataset | **SUPPORTED** |
| C-05 | «Ninguna cifra, referencia ni resultado cambió» | idem §16 | E2 | `validate_numbers --diff`: solo aparecen «ADR-003», «2026», «1»; `git diff --stat` vacío sobre resultados y referencias | **SUPPORTED** |
| C-06 | «Ningún resultado sintético se presenta como comportamiento real» | cap. 1 :101-111, cap. 4 :106-110, cap. 5 :3-8, cap. 6 :24-29 y :38-43 | E5 | lectura | **SUPPORTED** |
| C-07 | «Las procedencias real/synthetic/simulated no se confunden» | `metadata.py`, `experimental-design.md:63-81`, fichas | E2/E5 | taxonomía cerrada con test; tres fichas `synthetic` | **SUPPORTED** |
| C-08 | «El alcance no se ha ampliado» | memoria y diseño | E5 | grep: única mención en cap. 3 :6, describiendo lo excluido | **SUPPORTED** |
| C-09 | «E3 pasa a validación externa» en todos los artefactos | plan, paso a paso, matriz, cobertura, informe | E5 | lectura | **PARTIALLY_SUPPORTED** → `research/reproducibility.md:35` y espejo `experiments.md`, `results.md` siguen en «bloqueada» (MIN-002, INF-001) |
| C-10 | «La decisión está registrada como enmienda fechada y no retroactiva» | ADR-003 | E4 | lectura; ADR-002 no exige más | **SUPPORTED** |

## 5. Findings

### TUTOR-MAJ-001 · `MAJOR` · trazabilidad · `OPEN` → `FIXED` en §25

- **Qué:** la matriz de trazabilidad canónica enuncia la PI anterior como vigente.
- **Dónde:** `research/traceability-matrix.md`, §1, líneas 20–21: «a partir de datos OBD-II
  reales, rastreando…». La cabecera del mismo fichero (línea 4) dice «PI enmendada el 3 de
  septiembre de 2026, ADR-003», y §2 ya escribe «PI.1 — diagnóstico a partir de OBD-II».
- **Por qué importa:** el encargo (§25) exige que la única PI vigente sea la nueva; el modelo
  de evaluación considera «dos versiones vigentes de la pregunta» condición de parada. La
  matriz es el artefacto que el capítulo 4 y el tribunal usan para seguir PI → OE → EXP.
- **Evidencia:** `grep -n "OBD-II reales, rastreando" research/traceability-matrix.md` → 21.
  El informe de impacto (§5) afirma haber sustituido la PI en esa matriz; el registro de
  aplicación del productor muestra «0 sustituciones» en ese fichero para el segundo patrón
  y no se comprobó después.
- **Acción:** sustituir el enunciado de §1 por la PI vigente.
- **Criterio de verificación:** `grep -rn "OBD-II reales, rastreando"` sobre README, docs,
  research, src, scripts y cuadernos devuelve solo ADR-003 y textos marcados como originales
  (I-07 original).

### TUTOR-MIN-001 · `MINOR` · coherencia interna · `OPEN` → `FIXED` en §25

- **Qué:** el veredicto de la matriz de validación sigue formulado sobre el enunciado
  anterior: «No respondida sobre datos reales».
- **Dónde:** `docs/matriz_validacion_pi.md:184-185`.
- **Por qué importa:** contradice la sección nueva del mismo fichero (líneas 12–29), que dice
  que la matriz responde a la PI sobre el dataset declarado. Un lector encuentra en un mismo
  documento que la pregunta está respondida y que no lo está.
- **Evidencia:** lectura de ambas secciones.
- **Acción:** reformular el veredicto como acotación de validez externa, sin decir que la
  pregunta no está respondida.
- **Criterio:** el veredicto nombra el dataset y la ausencia de validación externa, y no
  contiene «no respondida».

### TUTOR-MIN-002 · `MINOR` · coherencia entre artefactos · `OPEN` → `FIXED` en §25

- **Qué:** E3 sigue marcada «⛔ bloqueada» en el registro de reproducibilidad.
- **Dónde:** `research/reproducibility.md:35`.
- **Por qué importa:** el plan, la matriz de trazabilidad, la cobertura de objetivos y el
  informe de seguimiento ya dicen «pendiente — validación externa». Un artefacto de
  reproducibilidad con otro estado es una inconsistencia entre capítulos que el tribunal
  puede preguntar.
- **Acción:** actualizar la fila.
- **Criterio:** la fila de E3 dice «pendiente — validación externa (ADR-003)».

### TUTOR-MIN-003 · `MINOR` · coherencia interna · `OPEN` → `FIXED` en §25

- **Qué:** el marcador de pendientes del capítulo 5 dice «E19 sobre datos reales».
- **Dónde:** `docs/memoria/cap5_resultados.md:237-238`.
- **Por qué importa:** el estado del mismo capítulo (líneas 3–8) y el capítulo 6 hablan del
  «dataset de evaluación final»; el marcador reintroduce el requisito retirado.
- **Acción:** reescribir el marcador.
- **Criterio:** el marcador no contiene «datos reales» como condición de E19.

### TUTOR-INF-001 · `INFO` · índice de lectura · `OPEN` → `FIXED` en §25

- **Qué:** en el espejo del skill, `experiments.md:13,61` y `results.md:21` mantienen E3 como
  «BLOQUEADA» y «bloquea la fase».
- **Por qué importa:** es índice, no fuente; gana el repositorio. El productor lo declara en
  el informe de impacto §14. Se registra para que la reevaluación lo compruebe.
- **Criterio:** filas actualizadas o nota fechada.

### TUTOR-INF-002 · `INFO` · redacción · `OPEN` → `FIXED` en §25

- **Qué:** «Supera claramente a la clase mayoritaria» en `docs/matriz_validacion_pi.md:37`.
- **Por qué importa:** intensificador sin evidencia según las reglas compartidas; el
  productor lo retiró de la memoria pero no de este artefacto. No afecta a la validez.
- **Criterio:** «claramente» retirado.

### TUTOR-INF-003 · `INFO` · infraestructura de evaluación · `OPEN`

- **Qué:** el skill de tutor carece de flujos, plantillas, rúbricas y scripts.
- **Por qué importa:** esta evaluación no pudo seguir la plantilla de 26 secciones ni el
  scorecard por criterios; el score de §8 se calculó por bloques sin rúbrica detallada y se
  declara como aproximación auditable por los findings, no por criterios.
- **Acción:** completar el skill o aceptar la limitación. `[AUTHOR_DECISION_REQUIRED]`

## 6. Trazabilidad PI → … → conclusiones previstas

| Eslabón | Estado tras el cambio | Evidencia |
|---|---|---|
| PI | nueva en README, matriz de validación, cap. 1, 17 cuadernos, `__init__`, espejo; **antigua en `traceability-matrix.md` §1** | §3 |
| GAP | GAP-01 revisado sin «reales» (espejo `gaps.md`); el tipo de dataset no es el vacío | lectura |
| OG / OE | sin cambio de enunciado; OE2 y OE5 reencuadrados en su estado | `cap2_objetivos.md` |
| HYP | predicción y criterio intactos; columna dataset «procedencia declarada» | matriz :37-40; espejo `hypotheses.md` |
| EXP | E3 cambia de rol; E19–E20 dependen del dataset de evaluación final | plan, paso a paso |
| MET | sin cambio | `metrics.md` no tocado |
| RES | sin cambio (C-05) | `git diff --stat` vacío |
| CONC previstas | acotadas a procedencia; validez externa como L-01 | cap. 6 :24-43 |

**Reinterpretación (regla 5 de la revisión de trazabilidad):** los experimentos anteriores
no se renumeran ni se borran; su papel cambia y el cambio está documentado en el informe de
impacto §13, con clasificación por función. Se comprobó que la clasificación
`DIRECT_EVIDENCE` para PI.3 y PI.4 y `SUPPORTING_EVIDENCE` para PI.1 es coherente con la
propia matriz de validación (E2: PI.4 «puramente documental», PI.1 «la que más cambiaría»).

**Red team de la conclusión prevista** (cap. 6): «¿Qué evidencia demostraría que es falsa?»
Se puede nombrar: un caso FULL y su gemelo ABSENT con la misma decisión, o una cita que no
sostenga lo afirmado; ambos tienen medición en E15 (`tables/E15_suficiencia.csv`). Falsable
y evaluada, sobre el dataset declarado.

## 7. Gates afectados (reglas compartidas)

| Gate | Estado que el productor registró | Comprobación del tutor |
|---|---|---|
| GATE-01 Pregunta | `PASS` | **Con reserva:** correcto para la fuente canónica; incorrecto mientras TUTOR-MAJ-001 esté abierto, porque hay dos enunciados vigentes en artefactos canónicos |
| GATE-03 Objetivos | `FAIL` (previo, ajeno al cambio) | coincide |
| GATE-13 Integridad global | `PASS` | coincide: ninguna cifra, referencia ni resultado alterado; huecos marcados |

## 8. Score (bloques evaluables en este modo)

| Bloque | Máx. | Otorgado | Motivo del descuento |
|---|---|---|---|
| Problema, pregunta y objetivos | 10 | 7 | MAJ-001 (PI doble en artefacto canónico) |
| Metodología | 15 | 14 | MIN-002 (artefacto de reproducibilidad desactualizado) |
| Diseño experimental | 15 | 14 | `dataset_type` ausente de los registros de `experiments/`, declarado como pendiente |
| Trazabilidad | 5 | 2 | MAJ-001; columnas RES/DISC/CONC de la matriz en `PENDING` desde el 1-09 pese a E7–E17 (preexistente, declarado por el productor) |
| Redacción y citación | 2 | 2 | — |
| Resto de bloques | 53 | N/E | fuera del modo |
| **Total evaluable** | **47** | **39** | |

## 9. Strengths (con evidencia)

- STRENGTH: la decisión está registrada como enmienda fechada con opciones descartadas,
  impacto por elemento y reversibilidad (`ADR-003`), como exige el flujo 01 del researcher.
- STRENGTH: ninguna cifra ni referencia cambió con la actualización
  (`validate_numbers --diff` sobre nueve ficheros; `git diff --stat` vacío sobre
  resultados y referencias).
- STRENGTH: la procedencia del dato está cerrada en código y probada
  (`src/mecanico_ia_exp/data/metadata.py`, `tests/test_dataset_provenance.py`), y definida
  en el diseño con lo que cada tipo sostiene y no sostiene
  (`docs/methodology/experimental-design.md:63-81`).
- STRENGTH: la incidencia I-07 se resolvió conservando su texto original
  (`research/traceability-matrix.md:198-218`), y los informes de fase cerrados recibieron
  nota fechada en lugar de reescritura (E2, E13).
- STRENGTH: la clasificación de resultados previos por función no reinterpreta ninguno
  más allá de lo medido (`docs/tfm/cambio_pi…md` §13).

## 10. Racionalizaciones consideradas y rechazadas

- «La fuente canónica de la PI es `matriz_validacion_pi.md`, así que la matriz de
  trazabilidad es secundaria»: rechazada. El encargo exige una sola PI viva y la matriz es
  artefacto canónico del marco (ADR-001).
- «Los MINOR son cosméticos»: rechazada en parte. MIN-001 hace que un mismo documento diga
  que la pregunta está y no está respondida; es coherencia interna, no formato.

## 25. Reevaluación

Realizada el 3 de septiembre de 2026 sobre el árbol de trabajo posterior a `b7a68f9`, contra
el **criterio de verificación** de cada finding, no contra la impresión general. Sin IDs nuevos.

| ID | Criterio | Comprobación | Estado |
|---|---|---|---|
| TUTOR-MAJ-001 | ninguna PI con «reales» viva fuera de ADR e I-07 original | `grep -rn "OBD-II reales, rastreando"` sobre README, docs, research, src, scripts, cuadernos y espejo: 0 resultados vivos; `traceability-matrix.md` §1 enuncia la PI vigente | **FIXED** |
| TUTOR-MIN-001 | veredicto sin «no respondida», nombrando dataset y validación externa | `docs/matriz_validacion_pi.md:184-185`: «Sostenida sobre `synthetic_v2` (…). Sin validación externa en vehículo real (L-01).» | **FIXED** |
| TUTOR-MIN-002 | fila E3 = pendiente — validación externa | `research/reproducibility.md:35` | **FIXED** |
| TUTOR-MIN-003 | marcador sin «datos reales» como condición de E19 | `docs/memoria/cap5_resultados.md:237-239` | **FIXED** |
| TUTOR-INF-001 | filas de E3 actualizadas en el espejo | `experiments.md:13,61`, `results.md:21` | **FIXED** |
| TUTOR-INF-002 | «claramente» retirado | `grep -c claramente docs/matriz_validacion_pi.md` → 0 | **FIXED** |
| TUTOR-INF-003 | skill de tutor completo o limitación aceptada | sin cambio; decisión del autor | **OPEN** |

Precedencia tras la reevaluación: sin `CRITICAL`, sin `MAJOR`, sin `MINOR` abiertos; queda un
`INFO` abierto y la observación preexistente sobre las columnas RES/DISC/CONC de la matriz de
trazabilidad (declarada por el productor en el informe de impacto §14). Estado:
`PASS_WITH_OBSERVATIONS`.

Score reevaluado: Problema, pregunta y objetivos 10/10 · Metodología 15/15 · Diseño
experimental 14/15 (`dataset_type` ausente de los registros de `experiments/`, declarado) ·
Trazabilidad 4/5 (columnas RES/DISC/CONC desactualizadas, preexistente) · Redacción 2/2.
**45 / 47 evaluable.**

GATE-01: `PASS` sin reserva tras MAJ-001 `FIXED`.

## 26. Recomendación

Las acciones de MAJ-001, MIN-001 a MIN-003, INF-001 e INF-002 están aplicadas y verificadas
(§25). Queda INF-003 a decisión del autor. Actualizar las columnas RES/DISC/CONC de la
matriz de trazabilidad con los resultados de E7–E17 en una tarea separada. No continuar a
nuevas fases de redacción hasta que el autor revise el cambio, como él mismo pidió.

```yaml
TUTOR_HANDOFF:
  unit: "Actualización transversal de la PI (ADR-003)"
  snapshot: "b7a68f9"
  verdict: PASS_WITH_OBSERVATIONS
  verdict_first_evaluation: FAIL
  score: "45/47 evaluable (primera evaluación: 39/47)"
  blocked_items: []
  findings:
    - id: TUTOR-MAJ-001
      severity: MAJOR
      status: OPEN
      file: research/traceability-matrix.md
      lines: "20-21"
      action: "sustituir la PI de §1 por la vigente"
      verify: "grep 'OBD-II reales, rastreando' sin resultados vivos fuera de ADR e I-07 original"
    - id: TUTOR-MIN-001
      severity: MINOR
      status: OPEN
      file: docs/matriz_validacion_pi.md
      lines: "184-185"
      action: "reformular el veredicto como acotación de validez externa"
      verify: "sin 'no respondida'; nombra dataset y validación externa"
    - id: TUTOR-MIN-002
      severity: MINOR
      status: OPEN
      file: research/reproducibility.md
      lines: "35"
      action: "E3: pendiente — validación externa (ADR-003)"
      verify: "fila actualizada"
    - id: TUTOR-MIN-003
      severity: MINOR
      status: OPEN
      file: docs/memoria/cap5_resultados.md
      lines: "237-238"
      action: "marcador: E19 sobre el dataset de evaluación final"
      verify: "sin 'datos reales' como condición de E19"
    - id: TUTOR-INF-001
      severity: INFO
      status: OPEN
      file: "TFM/.claude/skills/uax-tfm-ai-researcher/references/project/{experiments,results}.md"
      action: "actualizar estado de E3 o nota fechada"
    - id: TUTOR-INF-002
      severity: INFO
      status: OPEN
      file: docs/matriz_validacion_pi.md
      lines: "37"
      action: "retirar 'claramente'"
    - id: TUTOR-INF-003
      severity: INFO
      status: OPEN
      file: "TFM/.claude/skills/uax-tfm-ai-tutor/"
      action: "completar workflows, templates, rubrics y scripts, o aceptar la limitación"
      author_decision_required: true
  author_decisions_required:
    - "dataset de la evaluación final (E19) y fuente de datos reales para E3"
    - "completar o no el skill de tutor"
```
