# Matriz de trazabilidad — marco canónico

**Marco:** `mecanico-ia-exp` (ADR-001) · **Fecha:** 1 de septiembre de 2026, 15:00
(actualizada tras el cierre de E4, E5 y E6; **PI enmendada el 3 de septiembre de 2026, ADR-003**)

**Regla de lectura, vinculante:** si un elemento del proyecto no puede conectarse con una fila
de esta matriz, no pertenece al núcleo científico — es artefacto, instrumento o ingeniería, y
así debe presentarse.

**Toda hipótesis tiene al menos un experimento. Todo experimento responde a una subpregunta o
a un objetivo. Toda métrica declara qué propiedad mide. No hay experimentos huérfanos.**

Las columnas `RES`, `DISC` y `CONC` están en `PENDING` por diseño: no hay resultados. Lo que
esta matriz sirve para hacer **ahora** es detectar huecos, no documentar hallazgos.

---

## 1. Pregunta de investigación

> **PI.** ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos
> OBD-II, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo
> la evidencia disponible no es suficiente para sostener una explicación en lugar de generar
> una hipótesis sin fundamento?

## 2. Matriz principal

| Sub-PI | Objetivo | Hipótesis | Experimento | Métricas | RES | DISC | CONC | Evidencia |
|---|---|---|---|---|---|---|---|---|
| **PI.1** — diagnóstico a partir de OBD-II | OE-M3 ⚠ | ~~Un modelo temporal sobre ventanas OBD-II supera de forma clara al baseline y a la clase mayoritaria~~ **`SUPERSEDED 2026-10-12`**. Criterio vigente, único: **el diagnóstico supera a la clase mayoritaria con margen amplio y su confianza se puede calibrar** (`docs/matriz_validacion_pi.md`, cap. 4). El enunciado anterior exigía que *el modelo temporal* superase al baseline, que es una pregunta sobre arquitecturas y no sobre la capacidad de diagnosticar | **E6** ✅, **E19** ✅ (con E5 ✅, E7) | M1: F1 macro, PR-AUC, calibración | F1 macro del bosque **0,8788** frente a 0,0741 de la clase mayoritaria (E6, validación) y **sobre prueba** en E19 | PENDING | PENDING | `experiments/E6_baseline_synthetic_v2.json`, `experiments/E19_evaluacion_final_v3.json` |
| **PI.2** — explicación trazable | OE-M4 | Toda afirmación se ancla en una observación o en un fragmento identificable | **E14, E17** | M4: citation correctness, citation completeness, claim support rate, unsupported claim rate | PENDING | PENDING | PENDING | `[EXPERIMENT_REQUIRED]` |
| **PI.3** — reconocimiento de insuficiencia | OE-M4, OE-M5 ⚠ | Al retirar la evidencia relevante del corpus, el agente pasa de explicar a abstenerse sobre el mismo caso | **E16, E17** | M5: abstención correcta, abstención injustificada, cobertura | PENDING | PENDING | PENDING | `[EXPERIMENT_REQUIRED]` |
| **PI.4** — rechazo de evidencia engañosa | OE-M5 ⚠ | Ante evidencia parecida pero incorrecta, el agente no la acepta como soporte | **E17** | M5 sobre DISTRACTOR; M2 por condición | PENDING | PENDING | PENDING | `[EXPERIMENT_REQUIRED]` |

⚠ = incidencia detectada, ver §5.

**Procedencia de los datos** de todas las filas a fecha de hoy: `synthetic_v2`,
`dataset_type: synthetic`, calibrado contra el manual del vehículo. La PI no exige datos
reales (ADR-003); cada resultado se reporta con la procedencia del dato y la validez
externa se trata en L-01.

**Umbrales:** deliberadamente en blanco. Se fijan al cerrar **E15** sobre validación y quedan
registrados antes de tocar el conjunto de test. Escribir aquí un número después de ver
resultados anularía el propósito de la matriz.

## 3. Cobertura inversa — ningún experimento huérfano

| Fase | ¿A qué responde? | Estado | Objetivo |
|---|---|---|---|
| E1 entorno | precondición instrumental | **cerrada** | OE-M2 |
| E2 datos sintéticos | precondición instrumental | **cerrada** | OE-M2 |
| E3 datos reales | validación externa (ADR-003); ya no es precondición de la PI | pendiente — falta decidir la fuente | OE-M2 |
| E4 análisis exploratorio | instrumental: qué señales son utilizables | **cerrada** | OE-M2 |
| E5 preprocesamiento y particionado | instrumental crítico: sin partición limpia, nada posterior vale | **cerrada** — ventana 120 s, reparto por sesión, suelo de ruido medido | OE-M2 |
| E6 baseline | **control** de PI.1 | **cerrada** — F1 macro 0,876 en validación; umbral para E7 | OE-M3 |
| E7 modelo temporal | instrumental de PI.1 | pendiente | OE-M3 |
| E8 evaluación del modelo | **PI.1** | pendiente | OE-M3 |
| E9 atribución | instrumental: produce la evidencia observacional de PI.2 | pendiente | OE-M3 |
| E10 corpus documental | instrumental: produce la evidencia documental | pendiente | OE-M2 |
| E11 pgvector | instrumental | pendiente | OE-M4 |
| E12 evaluación de la recuperación | instrumental de PI.2/PI.3; **M2** | pendiente | OE-M4 |
| E13 integración del agente | instrumental | pendiente | OE-M4 |
| E14 trazabilidad de afirmaciones | **PI.2** | pendiente | OE-M4 |
| E15 suficiencia de evidencia | instrumental de PI.3; fija los umbrales | pendiente | OE-M4 |
| E16 abstención | **PI.3** | pendiente | OE-M4 |
| E17 condiciones de disponibilidad | **PI.2, PI.3, PI.4** — experimento central | pendiente | OE-M5 |
| E18 ablaciones | atribución de la contribución de cada pieza | pendiente | OE-M5 |
| E19 evaluación final | veredicto sobre la PI completa | pendiente | OE-M5 |
| E20 demostración | comunicación del contraste EXPLAIN/ABSTAIN | pendiente | OE-M5 |

**Ninguna fase queda sin objetivo.** Ninguna subpregunta queda sin experimento.

## 4. Métricas — ¿qué propiedad mide cada una?

| Grupo | Propiedad | Sub-PI que sirve | Estado |
|---|---|---|---|
| **M1** Diagnóstico | rendimiento y **calibración** del modelo especializado | PI.1 | justificada |
| **M2** Recuperación | calidad de la recuperación **por condición de corpus** | PI.4 (y soporte a PI.2/PI.3) | justificada |
| **M3** Explicación | adecuación al esquema, salidas válidas, legibilidad | **ninguna** ⚠ | descriptiva — ver §5 |
| **M4** Trazabilidad | existencia, resolución y **soporte** de la referencia | PI.2 | justificada |
| **M5** Abstención | corrección de la abstención **con cobertura** | PI.3, PI.4 | justificada |
| **M6** Rendimiento | latencia, tamaño de modelo, coste de recuperación | **ninguna** ⚠ | ver §5 |

**Métricas de atención prioritaria** (las que responden directamente a la PI):
`unsupported claim rate` · `citation correctness` · `citation completeness` ·
`claim support rate` · `correct abstention` · `false abstention` ·
`unsupported explanation rate`.

## 5. Incidencias detectadas

Esto es lo que la matriz sirve para encontrar hoy.

### I-01 — OE-M3 ya no describe lo que se va a hacer · **grave**

OE-M3, tal como está redactado en `docs/memoria/02_objetivos.md`, dice:

> «Implementar y comparar **técnicas no supervisadas de detección de anomalías** bajo un
> protocolo experimental publicado con anterioridad a su ejecución…»

El marco canónico **no usa detección no supervisada**: usa un modelo temporal supervisado con
confianza calibrada (E7-E8), sobre un baseline tabular (E6). El objetivo describe el marco
legacy.

`[AUTHOR_DECISION_REQUIRED]` — reformular OE-M3. La parte de explicabilidad (E9) sí sobrevive.

### I-02 — OE-M5 habla de «dos escenarios»; hay cuatro condiciones · **grave**

OE-M5 dice «bajo **dos escenarios** de disponibilidad de evidencia controlada». El marco
canónico tiene **cuatro**: FULL, PARTIAL, ABSENT, DISTRACTOR.

Además OE-M5 enumera «exactitud diagnóstica, soporte y fidelidad de la explicación, corrección
y completitud de la trazabilidad y calidad de la abstención» — vocabulario de las métricas
legacy. Hay que reexpresarlo sobre M1-M6.

`[AUTHOR_DECISION_REQUIRED]` — reformular OE-M5.

### I-03 — El vacío de investigación no cubre la pertinencia · **RESUELTA el 1-09-2026**

**Resultado: la hipótesis de vacío quedó refutada.** La búsqueda dirigida encontró que la
distinción presencia/pertinencia **sí está estudiada**, con banco público (RGB, Chen et al.,
AAAI 2024) y vocabulario establecido: «rechazo negativo» y «robustez contrafactual».

PI.4 gana motivación y pierde novedad amplia. El vacío se reformuló más estrecho —verificación
a nivel de afirmación, doble rama de evidencia, dominio vehicular— y queda pendiente de
confirmar con lectura a texto completo. Detalle en `references/project/gaps.md` GAP-02.

**GATE-02 pasa de `FAIL` a `PASS_WITH_OBSERVATIONS`.**

<details><summary>Formulación original de la incidencia, conservada</summary>

#### I-03 (original) — El vacío de investigación no cubre la pertinencia · grave

El vacío vigente (V4\*, legacy) enumera cuatro elementos: diagnóstico desde OBD-II real,
explicación por RAG, trazabilidad verificable, y comportamiento ante evidencia insuficiente.

**No menciona la distinción entre presencia y pertinencia de la evidencia**, que es
exactamente lo que aporta la condición DISTRACTOR y lo que ADR-001 declara como principal
razón de la canonicalización.

Consecuencia: **PI.4 es una subpregunta sin vacío que la justifique.** O se amplía el vacío
—con búsqueda que lo respalde, no por decreto— o PI.4 queda sin fundamento en el capítulo 3.

`[EVIDENCE_REQUIRED]` — ampliar la revisión para cubrir el rechazo de distractores en
sistemas RAG, y reformular el vacío en consecuencia.

</details>

### I-04 — M3 no responde a ninguna subpregunta · **observación**

El grupo M3 (calidad de la explicación) no aparece en la matriz de validación como métrica de
decisión de ninguna PI. Es legítimo que sea descriptiva —y así lo declara `metrics.md`, que
además la marca como el único sitio donde cabe un juez basado en modelo de lenguaje— pero
**debe declararse como descriptiva en el capítulo 4**, no presentarse junto a las demás como
si decidiera algo.

Refuerzo desde el legacy (LEG-E04): 20 de 20 salidas bien formadas con cero información
diagnóstica. La adecuación al esquema no es calidad.

### I-05 — M6 quedó sin subpregunta al cambiar de marco · **requiere decisión**

En el marco legacy, el presupuesto de cómputo era un criterio transversal (PI.f). En el
canónico, M6 mide latencia, tamaño y coste **sobre un MacBook M4 Pro**, y ninguna subpregunta
lo reclama.

`[AUTHOR_DECISION_REQUIRED]` — ¿M6 es criterio de aceptación o medición descriptiva? Si es
criterio, sobre qué hardware. Si es descriptiva, decirlo. Ver `prereg-classification.md` §3.4.

### I-06 — Ningún objetivo cubre explícitamente E18 y E20 · **observación**

Ablaciones y demostración están asignadas a OE-M5 por proximidad, no porque OE-M5 las nombre.
Al reformular OE-M5 (I-02), conviene que las incluya o que se declare que son instrumentales.

### I-08 — El umbral de suficiencia se apoyará en una confianza mal calibrada · **grave, nueva**

E6 midió un error de calibración esperado de **0,140**, con el modelo **infra**confiado
(confianza media 0,738 frente a 0,878 de acierto). El criterio de suficiencia de E15 toma la
confianza del modelo como una de sus cuatro señales conjuntivas.

Con estas probabilidades, un umbral sobre la confianza **se abstendría más de lo debido**, y
el sistema parecería prudente cuando en realidad está mal medido. La calibración deja de ser
una métrica de M1 y pasa a ser **una precondición de E15**.

Registrado como limitación L-14. No requiere decisión: requiere calibrar antes de fijar
umbral, sobre validación.

### I-09 — Existe una fuente natural de casos de abstención, y no estaba prevista · **oportunidad**

E6 encontró que el termostato bloqueado tiene un **límite físico de detección**: mientras el
motor no habría superado el techo de 71 °C por sí mismo, la señal de un motor averiado es
idéntica a la de uno sano (urbano **7/7**, calentamiento **2/7**; las dos medias que esta nota
citaba —70,7 y 54,3 °C— quedan **sin registro y no utilizables** desde el 12 de octubre de 2026,
ver `docs/experiments/E6_baseline.md`).

Son ventanas donde la evidencia es **genuinamente insuficiente por física, no por
construcción experimental**. El diseño de E17 preveía construir la insuficiencia retirando
documentos del corpus; esto aporta insuficiencia **observacional**, que es una condición
distinta y no está en la matriz de las cuatro condiciones.

`[AUTHOR_DECISION_REQUIRED]` — ¿entra como quinta condición, como estrato dentro de las
cuatro, o como análisis aparte? Aprovecharla es barato; no declararla sería perder el caso
más honesto que el experimento tiene a mano.

### I-07 — La PI dice «datos reales» y E3 está bloqueada · **RESUELTA el 3-09-2026 (ADR-003)**

**Resolución.** El autor enmendó la pregunta de investigación: «datos OBD-II» sin «reales».
La procedencia del dato pasa a ser una variable declarada (`dataset_type`) y la validez
externa, la limitación L-01. E3 deja de ser precondición y pasa a validación externa. El
texto original se conserva a continuación.

#### I-07 (original) — La PI dice «datos reales» y E3 está bloqueada · bloqueante

Es la incidencia de mayor impacto. La pregunta de investigación se formula sobre **datos
OBD-II reales**. E2 lo declara sin ambages: los datos sintéticos «no aportan validez externa
[…] ninguna conclusión sobre datos reales puede apoyarse en estos datos».

Si E3 no se resuelve, **PI.1 no puede responderse en sus términos actuales** y las demás se
responderían sobre datos sintéticos, lo que hay que declarar en el enunciado, no en las
limitaciones.

`[AUTHOR_DECISION_REQUIRED]` — fuente de datos reales, o reformulación del alcance de la PI.

## 6. Resumen de huérfanos

| Tipo | Encontrados |
|---|---|
| Objetivo sin experimento | 0 |
| Experimento sin objetivo | 0 |
| **Objetivo que describe otro marco** | **2** (OE-M3, OE-M5) |
| Subpregunta sin vacío que la justifique | **0** (era 1; resuelta) |
| **Métrica sin subpregunta** | **2** (M3 descriptiva declarada; M6 sin declarar) |
| **Condición experimental sin ubicar** | **1** (insuficiencia observacional de E6, I-09) |
| Resultado sin experimento | 0 |
| Hipótesis sin prueba | 0 |
| Evidencia huérfana | 0 |
| Conclusión sin resultado | 0 (no hay conclusiones) |

**GATE-03: FAIL** por I-01 e I-02 — hay objetivos que no describen el trabajo que se va a
hacer. **Es el único FAIL que queda.** Propuestas de reformulación en
`research/propuestas-objetivos.md`; la decisión es del autor.
**GATE-02: PASS_WITH_OBSERVATIONS** — I-03 resuelta; el vacío se reformuló tras buscar.
**GATE-04: PASS_WITH_OBSERVATIONS** — el diseño es coherente; falta cerrar I-05.

El FAIL restante no es de integridad: es de coherencia, y se corrige reformulando, no
experimentando. Pero se corrige **antes** de escribir el capítulo 2.
