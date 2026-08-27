# Alineación científica v4 — Fuera del alcance experimental y trabajo futuro

**2026-08-27.** Este documento recoge lo que la alineación v4 retira del núcleo científico
del TFM. **Retirar del alcance no es eliminar.** El diseño, el código y la documentación de
todo lo que aparece aquí se conservan en el repositorio; lo que cambia es que **no forman
parte de la validación del TFM** y no pueden aparecer en la pregunta de investigación, los
objetivos principales, las hipótesis contrastadas ni la contribución central.

Regla de lectura: si un elemento de esta lista aparece en un documento vivo, debe llevar
una marca explícita de *fuera del alcance experimental* con enlace a este fichero.

---

## 1. Memoria evolutiva y consolidación de conocimiento

**Qué se retira.** La memoria como mecanismo epistemológico con derecho de admisión: la
promoción de hipótesis a conocimiento reutilizable, los estados de promoción
(`EXPERIMENTALLY_VERIFIED`, `EXTERNALLY_CONFIRMED`), el gate de consolidación, la ablación
M0/M1/M2 y la hipótesis H-MEM.

**Por qué.** Contrastar H-MEM exige secuencias longitudinales de casos con inyección
controlada de conclusiones erróneas, un experimento completo (EXP-MEM-001) que depende a su
vez de tener resuelto el generador de explicaciones. Es la parte más cara de la cadena
anterior y la que menos aporta a la pregunta acotada: la nueva PI se responde por completo
en el interior de un único caso diagnóstico, sin necesidad de historia entre casos.

**Qué se conserva y dónde.**

| Artefacto | Ruta | Estado |
|---|---|---|
| Diseño de la memoria de tres niveles | `docs/adr/0013-memoria-tres-niveles.md` | ADR aceptado, no se retira (regla del repositorio) |
| Modelo de datos de memoria evolutiva | `docs/data-architecture/06_memoria_evolutiva.md` | conservado |
| Integración con eventos | `docs/event-intelligence/09_memory_integration.md` | conservado |
| Contratos `LearnedPattern`, `PatternRelation`, `PatternStatus`, `EpistemicLevel` | `shared/src/mecanico_contracts/` | conservados (contratos aditivos, ADR-0007); no evaluados |
| Memoria episódica implementada | `diagnostic-agent/.../reasoning/memory/episodic.py` | funcional, cubierta por tests, no evaluada |
| Nodos `recall` y `memorize` del grafo | `.../reasoning/graph/agent_v1.py` | funcionales; **desactivados por configuración** en los experimentos de la PI v4 |
| Diseño de EXP-MEM-001 y secuencias | `docs/experiments/pre-registro-v1.md` §4.2, §6.3 | congelado, no ejecutado |
| Controles negativos CN5 (memoria contaminada) y CN6 (hipótesis falsa al verificador) | `pre-registro-v1.md` §4.6 | conservados, no instanciados |

**Trabajo futuro.** La pregunta *«¿cuándo una explicación verificada adquiere el derecho a
ser recordada como conocimiento?»* es una continuación natural y bien delimitada de este
TFM: el sistema que la v4 valida —explicación trazable con abstención— es exactamente el
productor de las entradas que una memoria con validación necesitaría admitir. El diseño
experimental ya existe y está congelado.

---

## 2. Descubrimiento de fallos no representados y generación de conocimiento

**Qué se retira.** El objetivo de que el sistema identifique patrones de fallo no
representados en su conocimiento disponible *como aportación de conocimiento nuevo*; la
generación de hipótesis diagnósticas como resultado científico; su validación para
convertirlas en conocimiento; y toda formulación del trabajo como ciclo de descubrimiento.

**Por qué.** El descubrimiento exige demostrar que lo producido es correcto y no estaba
disponible, lo que requiere validación externa (un mecánico, una reparación efectiva) que
este trabajo no puede aportar sobre datos emulados. La operacionalización por exclusión
triple resolvía la primera mitad del problema, no la segunda.

**Qué se conserva y con qué reinterpretación.**

- La **definición operativa por exclusión** y su auditor ejecutable
  (`tools/contamination_audit.py`) se conservan íntegros. La exclusión E-DET sigue
  protegiendo el contexto diagnóstico; la exclusión **E-RAG pasa de restricción a variable
  independiente**: es el mecanismo que produce la condición de evidencia insuficiente.
- Las **clases held-out congeladas** (`corr_break_rpm_maf`, `load_coolant_decouple`,
  `joint_slow_drift`) se conservan y se reinterpretan: dejan de ser *prueba de que el
  sistema descubre fallos desconocidos* y pasan a ser *casos en que se controla
  deliberadamente la disponibilidad del conocimiento para evaluar si el agente reconoce que
  no dispone de evidencia suficiente*. Los casos que sigan siendo útiles para detección de
  anomalías o para el diagnóstico se conservan también con ese uso.
- La **hipótesis del reconocimiento de insuficiencia** no se pierde: P2 y P3 de H-MAIN v3
  sobreviven casi literalmente como Q4 (abstención correcta) y Q5 (falsa aceptación) de
  H-MAIN v4.

**Trabajo futuro.** Evaluar si un sistema que ya sabe abstenerse puede, además, proponer
hipótesis útiles precisamente en los casos donde se abstiene, y bajo qué protocolo de
validación externa esas hipótesis podrían considerarse conocimiento.

---

## 3. Aprendizaje autónomo y aprendizaje continuo

**Qué se retira.** El aprendizaje de nuevos fallos por parte del sistema en ejecución, la
actualización automática del corpus o del detector, y cualquier formulación de mejora
autónoma con el uso. Ya estaba bloqueado sin aprobación explícita en `REGLAS.md`
(«online learning», «consolidación automática de patrones»); la v4 lo retira además del
discurso científico.

**Trabajo futuro.** Actualización supervisada del corpus documental a partir de casos
resueltos y verificados externamente.

---

## 4. Arquitectura multiagente como contribución

**Qué se retira.** H-MAS y la ablación A0–A6 como contraste del TFM.

**Por qué.** Era ya explícitamente secundaria en la alineación v3 y su refutación no
afectaba a la PI. Bajo la v4 no aporta nada al contraste: la unidad de análisis es la
explicación y su soporte, no la descomposición del razonador.

**Qué se conserva.** ADR-0015, ADR-0018, `docs/agent-runtime/` completo y
`diagnostic-agent/.../runtime/supervisor.py` (funcional, cubierto por
`tests-integration/test_runtime_slice.py`). El runtime se conserva como ingeniería y como
banco para el trabajo futuro; los experimentos de la PI v4 se ejecutan sobre el grafo
`agent_v1`.

---

## 5. Detección contextual como objetivo científico

**Qué se reclasifica.** H-EVT (eventos frente a ventanas) y H-PERS (normalidad
personalizada) dejan de ser hipótesis del núcleo y pasan a **línea instrumental** sobre
SD1: mejoran o no la calidad del contexto diagnóstico, pero su resultado no condiciona la
respuesta a la PI.

**Qué se conserva.** Todo: los catorce experimentos ejecutados, sus informes, los
detectores congelados, EXP-SEG-001 como precondición instrumental y el diseño completo de
EXP-ANOM-004. H-PERS seguía además condicionada al parámetro diferido D2, nunca
materializado.

**Nota importante.** Los detectores de anomalías **siguen existiendo y siguen siendo
necesarios**: producen el diagnóstico de entrada del paso 3. Lo que cambia es que dejan de
dominar la narrativa científica.

---

## 6. Resumen para la memoria del TFM

En el capítulo de limitaciones y trabajo futuro debe constar, en estos términos:

> El trabajo evalúa la explicación diagnóstica trazable y la abstención ante evidencia
> insuficiente. Quedan fuera de su validación experimental —con su diseño conservado y sin
> ejecutar— la consolidación de explicaciones verificadas como conocimiento reutilizable, el
> aprendizaje a partir de casos nuevos, la comparación de arquitecturas multiagente y la
> contribución de la detección contextual, que aquí se emplea únicamente como instrumento.
