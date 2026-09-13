# Informe de preparación de la primera entrega

10 de septiembre de 2026 · alcance: preliminares, capítulos 1 a 4 y bibliografía.

## A · Estado general

**`FIRST_SUBMISSION_READY_WITH_OBSERVATIONS`**

La memoria presenta una investigación trazable y honesta sobre lo definido y sobre lo que
permanece abierto. Dos términos de la pregunta de investigación no están instrumentados y eso
**está declarado en el propio texto**, no escondido. Ningún resultado abierto se presenta como
validado. Un capítulo queda por debajo de la extensión recomendada.

## B · Estado por capítulo

| Capítulo | Extensión | Recomendación | Estado |
|---|---|---|---|
| Resumen y abstract | 309 palabras | 300 | READY |
| 1 · Introducción | 4,1 pág | 5-10 | MINOR_REVISION — corto |
| 2 · Objetivos | 2,2 pág | 1-3 | MINOR_REVISION |
| 3 · Marco teórico | 10,6 pág | 10-20 | READY |
| 4 · Marco metodológico | 14,7 pág | 5-15 | READY |
| 5 · Resultados | — | — | FROZEN · no se entrega como cerrado |
| 6 · Conclusiones | — | — | provisional |

## C · Cambios realizados

Resumen reescrito en formato IMRyD con abstract en inglés y cinco palabras clave, que no
existían. Sección 1.2 reordenada según el argumento y liberada del estado de ejecución del
repositorio. Objetivo general alineado con la pregunta y objetivos específicos reescritos para
separar el objetivo científico de su implementación. Marco teórico depurado de resultados
propios, con la base conceptual del patrón no representado incorporada y las afirmaciones
universales acotadas al corpus revisado. Población y muestra reescritas en prosa académica, con
el vehículo declarado como configuración de referencia y no como fuente física de la telemetría.
Trece tablas numeradas, tituladas, atribuidas y referenciadas. Trazabilidad de repositorio
desplazada a la subsección de reproducibilidad.

Detalle completo en `docs/audits/full_memory_review/12_CORRECTION_LOG.md`.

## D · Problemas pendientes

`H-01` patrón no representado sin aislamiento demostrable · `H-02` conocimiento reutilizable sin
mecanismo · `H-03` dos términos del objetivo general sin objetivo específico · `H-04` capítulo 1
corto · `H-05` reconciliación 144 frente a 153 · `H-06` memoria sin figuras · `H-07` cifras de
recuperación pendientes de reejecución canónica.

## E · Resultados experimentales deliberadamente excluidos

Los cuatro valores de la selección de ventana —0,369, 0,399, 0,438 y 0,512— y su interpretación
salieron del capítulo 4 por ser resultado y no diseño. **No se han insertado en el capítulo 5
porque está congelado**, de modo que hoy no aparecen en el cuerpo de la memoria. Quedan
custodiados literalmente en `15_PENDING_CH5_INSERTIONS.md` y siguen registrados en
`docs/experiments/E5_preprocesamiento.md`.

Todas las cifras de recuperación permanecen fuera de los capítulos que se entregan.

## F · Referencias verificadas

144 referencias consolidadas; 110 con identificador persistente resuelto en Crossref o DataCite,
cero identificadores rotos; 34 sin identificador en su fuente de origen. Verificadas en fuente
primaria durante esta revisión: **REF-019** (Chandola et al., 2009), consultada en Crossref
antes de citarla y añadida a la bibliografía; **MET-18** y **MET-19**, cuya consulta reveló que
no sostenían la afirmación regulatoria que la memoria les atribuía —retirada—.

`SUPPORTED` en las citas comprobadas · la comprobación exhaustiva claim → pasaje sobre las 144
no se ha ejecutado y se declara pendiente.

## G · Tablas incluidas

Trece: Tabla 2.1 y Tablas 4.1 a 4.12. Sin saltos, sin duplicados, todas mencionadas por su
número, todas con procedencia. Seis más quedan propuestas para el capítulo 5.

## H · Figuras incluidas

**Ninguna.** `FIGURE_NUMBERING = N/A`. La plantilla no exige índice de figuras.

## I · Riesgos para la defensa

El principal es `H-01` combinado con `H-03`: la pregunta abre con la identificación de patrones
no representados y el diseño no puede examinarla. La defensa es sostenible si se presenta como
lo que es —una capacidad no instrumentada, no un resultado negativo— y se acompaña de la
corrección experimental propuesta. Presentarla de otro modo es refutable en minutos.

Riesgo secundario: la extensión del capítulo 1 y la ausencia de figuras dan una impresión de
trabajo incompleto que el contenido no merece.

## J · Preguntas que requieren decisión del tutor

**P-01** objetivo general · **P-02** OE3 de no supervisado a supervisado · **P-03** alcance ·
**P-04** edición de APA · **P-05** la nota al pie de la plantilla exige un mínimo de 50 000
palabras mientras sus recomendaciones por capítulo suman unas 50 páginas; la memoria está en
17 900 · **SD-01** qué versión de la pregunta es canónica · **H-03** instrumentar los dos
términos ausentes o acotar el objetivo general.

## Matriz de preparación

| Elemento | Estado | Observación |
|---|---|---|
| PI | LOCKED | no modificada en ningún punto |
| Capítulo 1 | MINOR_REVISION | 4,1 pág; margen en 1.1 |
| Objetivo general | PASS con observación | cubre el ciclo; dos términos sin OE |
| OE1 | PASS | |
| OE2 | PASS | |
| OE3 | PASS | divergencia supervisado/no supervisado declarada (P-02) |
| OE4 | PASS | separa generar hipótesis de validarla |
| OE5 | PASS | sin objetivos administrativos |
| Capítulo 3 | READY | cuatro frentes más la base del patrón no representado |
| Referencias | PASS con observación | `H-05` abierto |
| Población | PASS | niveles de agregación distinguidos; sin pseudorreplicación |
| Vehículo | PASS | configuración de referencia, no fuente física |
| Muestra | PASS | |
| Datos sintéticos | PASS | `EXPERIMENTAL_BASE` |
| Diseño experimental | PASS | cuatro condiciones como diseño |
| DISTRACTOR | BAJO_DIAGNÓSTICO | no presentado como validado |
| Patrón no representado | **BLOCKED** | `H-01` |
| Conocimiento reutilizable | **PENDING** | `H-02` |
| Capítulo 5 | FROZEN | no requerido en esta entrega |

## Gate final

| Control | Resultado |
|---|---|
| `PI_ALIGNMENT` | PASS con bloqueo declarado |
| `OBJECTIVES_ALIGNMENT` | PASS con observación |
| `THEORETICAL_FRAMEWORK` | PASS |
| `METHODOLOGY` | PASS |
| `POPULATION_SAMPLE` | PASS |
| `DATA_PROVENANCE` | PASS |
| `EXPERIMENTAL_DESIGN` | PASS |
| `METRICS` | PASS |
| `REFERENCE_INTEGRITY` | PASS con observación |
| `TABLE_FIGURE_FORMAT` | PASS · figuras N/A |
| `UAX_TEMPLATE_COMPLIANCE` | PASS con observación — capítulo 1 corto, `P-05` abierto |
| `WRITING_AUTHENTICITY` | PASS — `NO_MARKS_FOUND` en los cinco documentos entregables |

---

> **Superado por `ADR-004`, 12 de septiembre de 2026.** La dirección resolvió `SD-01` a favor de
> la pregunta acotada y descartó la formulación amplia. Lo que este documento registra sobre los
> componentes de esa formulación era cierto cuando se escribió y se conserva como tal; ya no
> describe el alcance vigente del trabajo.
