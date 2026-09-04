# 00 · Línea base de la revisión integral

**Fecha:** 3 de septiembre de 2026 · **Repositorio:** `mecanico-ia-exp` · **Commit de partida:**
`8d55def` (auditorías de la suite) y `ac428e6` (estado del árbol al iniciar esta revisión;
solo difiere en el YAML del informe del tutor sobre ADR-003) · **Árbol limpio:** sí.
**Orquestador:** rol «Tfm-tutor» asumido por esta revisión, con `uax-tfm-ai-tutor` como
evaluador académico independiente (véase §2, hallazgo de descubrimiento).

**Pregunta de investigación vigente, bloqueada:**

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una
> hipótesis sin fundamento?

Fuente: `docs/matriz_validacion_pi.md`, enmendada por `research/decisions/ADR-003-…md`.
Ningún skill de esta revisión la modifica; los problemas que detecten se reportan.

## 1. Fase 0 · Descubrimiento del proyecto

| Elemento | Estado a la línea base | Fuente |
|---|---|---|
| Marco canónico | `mecanico-ia-exp` (ADR-001); `mecanico-ia` = fuente heredada | `research/decisions/ADR-001` |
| PI | enmendada el 3-09-2026 (ADR-003), única viva en todos los artefactos | `TUTOR-REPORT-20260903.md` §25 |
| Subpreguntas | PI.1 diagnóstico · PI.2 trazabilidad · PI.3 insuficiencia · PI.4 evidencia engañosa | `docs/matriz_validacion_pi.md` |
| Objetivos | OG + OE1–OE5 reformulados en `cap2` (opción A); aprobados en julio distintos; tres `[CONSENSUAR CON EL DIRECTOR]` abiertos | `docs/memoria/cap2_objetivos.md`, `research/propuestas-objetivos.md` |
| Fases | E1–E17 cerradas sobre `synthetic_v2` (`dataset_type: synthetic`); E3 validación externa sin fuente; E18 pendiente; E19–E20 dependen de la decisión sobre el dataset de evaluación final | `docs/experiments/README.md`, `docs/EXPERIMENTO_PASO_A_PASO.md` |
| Registros | `experiments/*.json` (15), `tables/*.csv`, `data/raw/synthetic/synthetic_v{1,2,3}.meta.json`; se sabe que E6, E7 y E12 tienen cifras distintas entre informe y registro (registros sobrescritos) | informes de la suite |
| Memoria | resumen, cap1–cap6, bibliografía, LEEME en `docs/memoria/`; 12 336 palabras netas; cap5 y cap6 borradores sobre sintéticos | `docs/memoria/LEEME.md`, `word_count.py` |
| Gates del proyecto | GATE-01 PASS; GATE-03 FAIL (objetivos); 05/08/09/11 BLOCKED; 13 PASS | `research/gates.md` |
| Limitaciones | L-01…L-17 (1 crítica, 9 altas) | `research/limitations-register.md` |
| Informes previos de la suite (mismo día, commit `8d55def`) | tutor (E12), RAG (E12), experimentos (E7), evidencia (cap5 §Discusión + cap6 §Conclusiones), estadística (E5), referencias (39 citadas), autenticidad (dos secciones), jurado (dry-run 1 y 2, banco, diez letales, pack) | `TFM/*-reports/` |
| Estado declarado por el jurado | documento `BLOCKED`; 16 MAJOR abiertos de la suite, 0 CRITICAL; preparación `NOT_READY (provisional)` | `jury-reports/JURY-DRY-RUN-01.md` §4 |

Los informes previos son **dry-runs acotados a una unidad cada uno**; ninguno cubre el TFM
completo. Esta revisión los toma como contexto y reevalúa sus hallazgos con los mismos
identificadores, como prescriben los propios skills.

## 2. Fase 1 · Inspección de skills

### 2.1 Inventario real en el sistema de ficheros

Las rutas `skills/…` corresponden al directorio de skills del entorno de trabajo, en la raíz
del escritorio del TFM. Son localizaciones del sistema de ficheros, no parte del trabajo
académico.

| Skill pedido | Encontrado | Ruta | Contenido |
|---|---|---|---|
| `Tfm-tutor` (orquestador) | **no existe** como skill | — | El rol de coordinación transversal lo asume esta revisión; la evaluación académica independiente, `uax-tfm-ai-tutor` |
| `uax-tfm-ai-tutor` | sí | `skills/uax-tfm-ai-tutor/` | SKILL, 18 workflows, 7 templates, 23 references (evaluation + rubrics), 2 scripts, 15 fixtures. Completado hoy: a las 13:30 carecía de workflows, templates, rúbricas y scripts (TUTOR-INF-003 queda resuelto) |
| `tfm-rag-evaluator` | sí | `skills/tfm-rag-evaluator/` | 11 workflows, 6 templates, 13 references, rúbrica, `validate_skill.py` |
| `tfm-experiment-auditor` | sí | `skills/tfm-experiment-auditor/` | 11 workflows, 7 templates, 13 references, rúbrica, `validate_skill.py` |
| `tfm-evidence-verifier` | sí | `skills/tfm-evidence-verifier/` | 10 workflows, 7 templates, 12 references, rúbrica, `validate_skill.py` |
| `tfm-statistical-reviewer` | sí | `skills/tfm-statistical-reviewer/` | 11 workflows, 7 templates, 14 references, rúbrica, `validate_skill.py` |
| `tfm-reference-auditor` | sí | `skills/tfm-reference-auditor/` | 10 workflows, 7 templates, 11 references, 8 scripts (inventario, citas, bib, duplicados, comparación, identificadores) |
| `tfm-writing-authenticity-auditor` | sí | `skills/tfm-writing-authenticity-auditor/` | 14 workflows, 9 templates, 11 references, 11 scripts (estadísticas de texto, n-gramas, similitud interna, snapshot de integridad, limpieza de marcas) |
| `uax-tfm-ai-jury` | sí | `skills/uax-tfm-ai-jury/` | 12 workflows, 9 templates, 12 references, `question_bank.py` |
| `tfm-defense-coach` | sí (instalado durante esta revisión, 3-09-2026) | `skills/tfm-defense-coach/` | SKILL, workflows, references, rubrics, templates, scripts, tests. Entrena la defensa oral (ANSWER → EVIDENCE → LIMITATION), consume los handoffs del jurado, del tutor y de los auditores, y emite NOT_READY / LEARNING / READY_WITH_GAPS / DEFENSE_READY |
| `uax-tfm-ai-researcher` | sí (productor) | `skills/uax-tfm-ai-researcher/` | 15 workflows, 12 templates, 35 references, 7 scripts. Es el único que **escribe**; los demás son read-only |

Todos los SKILL.md se leyeron íntegros; los workflows y referencias de cada skill los lee el
agente que lo ejecuta antes de empezar.

### 2.2 Entradas y salidas

| Skill | Entrada | Salida | Escribe en el repo |
|---|---|---|---|
| researcher | evidencia + reglas | capítulos, matrices, ADR | sí |
| tutor | documento + artefactos | `tutor-reports/TUTOR-REPORT-*.md` + `TUTOR_HANDOFF` | no |
| rag-evaluator | sistema RAG, registros, corpus | `rag-reports/RAG-EVALUATION-*.md` + handoff | no |
| experiment-auditor | experimentos, registros, datos, código | `experiment-reports/EXPERIMENT-AUDIT-*.md` + handoff | no |
| evidence-verifier | claims de la memoria | `evidence-reports/EVIDENCE-VERIFICATION-*.md`, `claims/` | no |
| statistical-reviewer | resultados cuantitativos | `statistical-reports/STATISTICAL-REVIEW-*.md` | no |
| reference-auditor | citas y bibliografía | `reference-reports/REFERENCE-AUDIT-*.md`, `verification-register.json` | no |
| authenticity-auditor | texto corregido | `authenticity-reports/AUTHENTICITY-AUDIT-*.md`; rewrite handoff solo con autorización | no (salvo `--apply` autorizado) |
| jury | documento final + findings | `jury-reports/JURY-REVIEW-*.md`, banco, letales, pack | no |

### 2.3 Solapamientos

- **Tutor ↔ todos los especialistas:** el tutor cubre RAG, abstención, referencias, estadística
  y reproducibilidad en sus propios workflows; los especialistas profundizan. Regla de la
  suite: el tutor consume los handoffs y **vuelve a verificar**; no copia.
- **Evidence-verifier ↔ reference-auditor:** frontera declarada: existencia y metadatos
  (auditor) frente a «¿la fuente dice esto?» (verificador).
- **Experiment-auditor ↔ statistical-reviewer:** el auditor detecta (unidad, efecto antes que
  p); el revisor profundiza. Handoff explícito `HANDOFF: tfm-statistical-reviewer`.
- **Experiment-auditor ↔ rag-evaluator:** el auditor delega la auditoría RAG profunda.
- **Authenticity-auditor ↔ researcher (humanización):** el researcher humaniza; el auditor
  audita antes y después y verifica integridad semántica.
- **Jury ↔ tutor:** ambos simulan tribunal (tutor workflow 17; jury completo). El jury es el
  que produce banco, letales y pack.

### 2.4 Contradicciones detectadas entre skills

| ID | Skill A | Skill B | Contradicción | Impacto | Decisión propuesta |
|---|---|---|---|---|---|
| CONFLICT-SK-01 | encargo (§3) | filesystem | Pide `Tfm-tutor`, que no existe como skill. `tfm-defense-coach` sí existe (instalado el 3-09-2026, después de la fase 1) | orquestación | la orquestación transversal la asume esta revisión; la fase 5 usará `tfm-defense-coach` tal como pide el encargo |
| CONFLICT-SK-02 | tutor `TUTOR-DRY-RUN-01` | tutor `TUTOR-REPORT-20260903` | Ambos usan `TUTOR-MAJ-001`, `TUTOR-MIN-00x` para hallazgos distintos (colisión de IDs) | conciliación con `finding_ledger.py` | el tutor en revisión completa declara la colisión y numera a partir del último ID global; no se renumera el pasado |
| CONFLICT-SK-03 | encargo (§28) | suite | Escalas de severidad: BLOCKER/MAJOR/MODERATE/MINOR/COSMETIC frente a CRITICAL/MAJOR/MINOR/INFO | consolidación | mapeo fijo CRITICAL→BLOCKER, MAJOR→MAJOR, MINOR→MODERATE, INFO→MINOR (COSMETIC si es puro formato); se conserva la severidad original en cada informe |
| CONFLICT-SK-04 | encargo (§24, voz Philip K. Dick) | researcher `voice-philip-k-moderate.md` | Coinciden en rasgos; el researcher además impone intensidad por sección (cap. 2, 4 y 5 en 0–1) y precondición de gate académico | humanización | se sigue el researcher: solo tras el gate académico y con intensidad por sección |
| CONFLICT-SK-05 | researcher `academic-writing.md` | encargo (§21) | Ambos prohíben «la literatura»; el researcher además prohíbe «no existe» y las siglas del máster | redacción | sin conflicto real; se aplican ambas |
| CONFLICT-SK-06 | jury SKILL.md | filesystem | *Resuelto*: el jury remite el entrenamiento a `tfm-defense-coach`, que ya está instalado | fase 5 (defensa) | sin conflicto |

Ninguna contradicción afecta a la PI, la metodología, las hipótesis, los resultados ni las
conclusiones; ninguna requiere decisión humana antes de la fase de auditoría.

## 3. Fase 2 · Auditoría de plantilla UAX

**Plantilla vigente:** `24-25 Plantilla TFM MUIA.docx` (raíz del TFM; la copia «2» es idéntica
byte a byte). Estructura real extraída en
`skills/uax-tfm-ai-researcher/references/uax/plantilla-oficial.md`: seis capítulos
fijos, resumen IMRyD de 300 palabras con cinco palabras clave, abstract, bibliografía APA 6.ª,
anexos ≤ 20 %. Conflictos oficiales registrados y no resueltos: extensión (tres cifras),
formato, APA 6.ª/IEEE, calendario, alcance aprobado (`conflictos-uax.md`).

| Sección UAX | Contenido actual | Estado | Skill responsable | Problemas conocidos | Corrección prevista | Gate |
|---|---|---|---|---|---|---|
| Resumen (300 palabras, IMRyD) + palabras clave | `00_resumen.md`, 331 palabras, cinco palabras clave | NEEDS_ALIGNMENT | evidence-verifier, tutor | se reescribe con E19; sobrepasa 300 | recortar a 300 al cerrar resultados | GATE-11 |
| Abstract + keywords | no existe | BLOCKED | researcher | traducción fiel pendiente del resumen final | tras E19 | GATE-11 |
| Cap. 1 · Justificación | `cap1_introduccion.md` §1 | NEEDS_REFERENCE_REVIEW | reference-auditor, evidence-verifier | falta la justificación **personal** que la plantilla pide; REF-049 y REF-106 con metadatos incompletos | añadir párrafo personal; completar referencias | GATE-11, GATE-10 |
| Cap. 1 · Presentación | `cap1` §2 | COMPLETE (borrador) | tutor | último párrafo se reescribe si E19 cambia el dataset | — | GATE-11 |
| Cap. 2 · Objetivo general | `cap2` §1, opción A | NEEDS_ALIGNMENT | tutor | reformulado frente al aprobado; `[CONSENSUAR CON EL DIRECTOR]`; conflicto canónico del jurado | decisión del director | GATE-03 |
| Cap. 2 · Objetivos específicos | `cap2` §2, cinco OE | NEEDS_ALIGNMENT | tutor | OE3 y OE5 reformulados; Anexo A de correspondencia no escrito | decisión del director; escribir Anexo A | GATE-03 |
| Cap. 3 · Marco teórico | `cap3`, 2 285 palabras, cuatro frentes | NEEDS_EVIDENCE, NEEDS_REFERENCE_REVIEW | tutor, reference-auditor | dos `[AMPLIAR]`; vacío GAP-02 revisado pendiente de lectura a texto completo; extensión por debajo de las 10–20 páginas recomendadas; reutilización del estado del arte v2.0 pendiente | importar secciones reutilizables del documento de agosto; lecturas pendientes | GATE-02, GATE-10 |
| Cap. 4 · Población y muestra | `cap4` §1 | COMPLETE (borrador) | experiment-auditor | versión final depende del dataset de E19; cifras E5 obsoletas (STAT-MAJ-001) | reconciliar E5 | GATE-04, GATE-06 |
| Cap. 4 · Objetivos de investigación | `cap4` §2 | COMPLETE | tutor | — | — | GATE-04 |
| Cap. 4 · Variables e instrumentos | `cap4` §3 | NEEDS_ALIGNMENT | rag-evaluator, statistical-reviewer | M6 sin decisión (criterio o descriptiva); M4 declarada y no calculada (EVID-MAJ-001) | decidir M6; calcular o reformular M4 | GATE-04 |
| Cap. 4 · Diseño experimental | `cap4` §4 | NEEDS_ALIGNMENT | experiment-auditor, rag-evaluator | oráculo del DTC no declarado (RAG-MAJ-003, TUTOR-MAJ-002); paradigma/tipo/alcance temporal no etiquetados con las palabras de la plantilla; DSR sin ADR propio | declarar el oráculo; etiquetar; ADR de método | GATE-04 |
| Cap. 4 · Modelo de análisis | `cap4` §5 | NEEDS_STATISTICAL_REVIEW | statistical-reviewer | «no atribuible al azar» (matriz) sin prueba; N independiente | revisar redacción | GATE-04 |
| Cap. 5 · Análisis descriptivo | `cap5` §1 | NEEDS_STATISTICAL_REVIEW | statistical-reviewer | cifras de E5 de un dataset que ya no existe bajo ese identificador | reconciliar | GATE-07 |
| Cap. 5 · Resultados | `cap5` §2 | NEEDS_EVIDENCE | evidence-verifier, experiment-auditor, rag-evaluator | E6/E7/E12 cifras ≠ registro vigente; ECE sin registro; tabla multilingüe sin registro; `[RECONCILIAR]` | fijar ejecuciones canónicas; registrar; citar JSON | GATE-07 |
| Cap. 5 · Discusión | `cap5` §3 | NEEDS_ALIGNMENT | evidence-verifier | «sostenidas» sobre un caso en PI.3/PI.4; distancia M4 «cero» no medida; cobertura 3/5 omitida en conclusión | acotar el alcance | GATE-08 |
| Cap. 6 · Conclusiones | `cap6` §0 | NEEDS_EVIDENCE | tutor, evidence-verifier | borrador; orden OE1→…→OG no seguido; cumplimiento por objetivo no declarado | reescribir tras E19 en el orden de la plantilla | GATE-09 |
| Cap. 6 · Limitaciones | `cap6` §1 | COMPLETE (borrador) | tutor | cinco limitaciones nuevas «pendientes de incorporar al registro» | incorporar L-18…L-22 al registro | GATE-09 |
| Cap. 6 · Prospectiva | `cap6` §2 | COMPLETE (borrador) | tutor | — | — | GATE-09 |
| Cap. 6 · Consideraciones finales | `cap6` §3 | BLOCKED | researcher | depende de E19; seis puntos de la plantilla | tras E19 | GATE-09 |
| Bibliografía (APA 6.ª, sangría francesa) | `bibliografia.md`, 39 entradas | NEEDS_REFERENCE_REVIEW | reference-auditor | 8 `[VERIFY_SOURCE]`; etiquetas REF-/MET- en citas; recuentos maestra 144/153 sin reconciliar | completar; retirar etiquetas al volcar | GATE-10 |
| Anexos | no existen | BLOCKED | researcher | Anexo A (objetivos aprobados ↔ reformulados) exigido por el propio proyecto | escribir | GATE-11 |
| Formato (Word, estilos, extensión) | no volcado a Word | BLOCKED | researcher | 12 336 palabras frente a 50 000–60 000 (plantilla) o ≥ 60 páginas (sesión informativa); decisión del director | decisión | GATE-11 |

Cribado ejecutado: `validate_structure.py` sin errores (24 avisos: marcadores declarados y
tablas sin `TAB-NNN`); `validate_citations.py` sin errores; `validate_references.py` con
falsos positivos por citas compuestas; `word_count.py` 12 336 palabras.

## 4. Productos de esta revisión

| Fichero | Contenido | Quién lo produce |
|---|---|---|
| `00_baseline.md` | este documento | orquestador |
| `01_tutor_findings.md` | evaluación académica completa | `uax-tfm-ai-tutor` |
| `02_rag_findings.md` | RAG, evidencia documental, abstención | `tfm-rag-evaluator` |
| `03_experiment_findings.md` | diseño, datos, fugas, reproducibilidad, clasificación de experimentos | `tfm-experiment-auditor` |
| `04_evidence_findings.md` | claims ↔ evidencia, cifras, conclusiones | `tfm-evidence-verifier` |
| `05_statistics_findings.md` | unidades, N, incertidumbre, umbrales | `tfm-statistical-reviewer` — **entregado**: `BLOCKED`, 5 MAJOR, 0 CRITICAL |
| `06_reference_findings.md` | existencia, metadatos, citas, APA | `tfm-reference-auditor` |
| `07_correction_plan.md` | plan consolidado por prioridad, conflictos entre skills | orquestador |
| `08_authenticity_findings.md`, `09_jury_report.md`, `10_defense_report.md`, `11_final_quality_report.md` | **no se producen en esta pasada** (STOP GATE 1) | — |

Informes completos de cada skill en `TFM/<skill>-reports/`, fuera del repositorio.


## 5. Nota de ejecución

La primera tanda de auditorías (6 en paralelo) se interrumpió por agotamiento de cuota del
servicio de inferencia antes de escribir sus informes. Sobrevivieron dos productos completos:
`statistical-reports/STATISTICAL-REVIEW-20260903.md` y la actualización de
`reference-reports/verification-register.json` (172 entradas). Las auditorías restantes se
relanzaron en tandas de tres. Este incidente no afecta a la evidencia: cada auditoría vuelve
a leer los artefactos del repositorio.
