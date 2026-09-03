# Capítulo 2: Objetivos del TFM

> Estado: redactado sobre `research/propuestas-objetivos.md` (1 de septiembre de 2026),
> opción A en los tres casos. **Los enunciados reformulados están pendientes de consenso con
> el director**, junto con el título definitivo. La versión aprobada en la propuesta temática
> de julio de 2026 se conserva en el Anexo A con su correspondencia.

El trabajo se organiza alrededor de la pregunta de investigación enunciada en el capítulo 1.
Los objetivos que siguen la traducen en compromisos verificables al terminar: cada uno nombra
las fases experimentales que lo cumplen y las métricas con las que se comprueba. Se ha
procurado que ningún objetivo prometa algo que el diseño experimental no pueda medir, y que
ninguna fase del plan quede sin objetivo al que servir.

## Objetivo general

Evaluar experimentalmente un agente de recuperación aumentada por evidencia, diseñado a tal
efecto, en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos
OBD-II manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la
sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no pertinente.

Tres decisiones de redacción merecen explicación. El verbo es uno solo, *evaluar*, porque el
artefacto es en esta investigación el medio y no el fin: su diseño queda recogido en el cuarto
objetivo específico. Se incorpora «o no pertinente» porque la pregunta de investigación no
solo interroga si el agente reconoce la ausencia de evidencia, sino también si distingue la
evidencia parecida de la evidencia que de verdad sostiene una afirmación, y esa distinción es
la que mide la condición con distractor del diseño experimental. Y se escribe «datos OBD-II»
sin adjetivo, igual que la propia pregunta desde su enmienda del 3 de septiembre de 2026: la
procedencia de cada dataset se declara en el capítulo 4 y su validez externa se trata en el
capítulo 6, sin condicionar el objetivo a que los datos sean reales.

`[CONSENSUAR CON EL DIRECTOR]` El enunciado aprobado en julio llevaba dos verbos, «diseñar y
evaluar», y una cláusula final sobre restricciones de cómputo de plataforma embarcada. La
primera contraviene la indicación de la plantilla de un único verbo; la segunda ya no describe
el trabajo, porque las mediciones de rendimiento se realizan sobre un ordenador de sobremesa y
el despliegue embarcado ha pasado a trabajo futuro.

## Objetivos específicos

Son cinco, dentro del rango que la plantilla recomienda. Los tres primeros construyen lo
necesario para responder a la pregunta; el cuarto integra el agente; el quinto lo evalúa y
documenta.

**OE1. Revisar críticamente el estado del conocimiento** sobre diagnóstico vehicular a partir
de OBD-II, explicabilidad de modelos de diagnóstico, recuperación aumentada aplicada a
documentación técnica y abstención ante evidencia insuficiente, de modo que quede delimitado
el vacío que la pregunta de investigación aborda y las decisiones de diseño puedan
justificarse frente a trabajos previos. Se cumple en el capítulo 3; su instrumento es la
revisión con procedimiento inspirado en PRISMA descrita en el capítulo 4.

**OE2. Construir un entorno experimental reproducible** que comprenda telemetría OBD-II
particionada sin fuga temporal y un corpus documental del vehículo con variantes congeladas
de disponibilidad de evidencia, de modo que cualquier tercero pueda repetir cada experimento
a partir de su registro. Lo cumplen las fases E1, E2, E4, E5 y E10; la fase E3, incorporación
de datos reales, queda como validación externa, pendiente de una fuente.

**OE3. Construir y evaluar un modelo de diagnóstico** sobre ventanas de telemetría,
contrastado frente a una referencia mínima y a un baseline tabular, con su confianza
calibrada y con atribución de descriptores, de modo que el sistema disponga de un contexto
diagnóstico verificable y caracterizado. Lo cumplen las fases E5 a E9 y se mide con el grupo
de métricas M1. La calibración se nombra expresamente porque la confianza del modelo alimenta
el criterio de suficiencia: una confianza sin calibrar haría que ese criterio decidiera sobre
un número que no significa lo que aparenta.

`[CONSENSUAR CON EL DIRECTOR]` El enunciado aprobado hablaba de técnicas no supervisadas de
detección de anomalías. El diseño ejecutado usa un modelo supervisado con atribución; la parte
sobre explicabilidad del enunciado original se conserva.

**OE4. Implementar un agente** que recupere evidencia documental del vehículo, construya
afirmaciones ancladas simultáneamente en la evidencia observacional y en la documental,
verifique de forma determinista que cada cita sostiene lo afirmado y decida entre explicar y
abstenerse mediante un criterio de suficiencia independiente del modelo de lenguaje. Lo
cumplen las fases E11 a E16 y se mide con los grupos M2, M4 y M5.

**OE5. Evaluar el agente frente a las hipótesis declaradas bajo cuatro condiciones de
disponibilidad y pertinencia de la evidencia**, completa, parcial, ausente y con distractor,
midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las afirmaciones y
calidad de la abstención con su cobertura, aislando la contribución de cada componente
mediante ablaciones, y documentar el trabajo conforme a la normativa de la titulación,
incluidos de forma explícita los resultados negativos y las limitaciones de validez. Lo
cumplen las fases E17 a E20. «Con su cobertura» es deliberado: la corrección de la abstención
y su cobertura solo significan algo juntas, porque un sistema que se abstuviera siempre
tendría abstención perfecta y utilidad nula.

`[CONSENSUAR CON EL DIRECTOR]` El enunciado aprobado hablaba de dos escenarios; el diseño
ejecutado tiene cuatro condiciones, y las ablaciones y la demostración final no estaban
cubiertas.

## Correspondencia entre objetivos, fases y métricas

| Objetivo | Fases | Métricas | Estado a 2 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | avanzado; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cinco de seis cerradas; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cerradas sobre datos sintéticos |
| OE4 | E11, E12, E13, E14, E15, E16 | M2, M4, M5 | cerradas sobre datos sintéticos |
| OE5 | E17, E18, E19, E20 | M1–M6 | E17 ejecutada sobre datos sintéticos; E18 pendiente; E19 y E20 pendientes de la decisión sobre el dataset de evaluación final |

Ninguna de las veinte fases queda sin objetivo. Ninguna subpregunta de investigación queda
sin fase que la responda.

## Lo que los objetivos no incluyen

La propuesta temática de julio de 2026 contemplaba además el despliegue sobre una placa
embarcada, una aplicación móvil y una plataforma en la nube. Esos tres elementos no forman
parte de los objetivos de este trabajo: no aportan evidencia a la pregunta de investigación y
su coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6. `[CONSENSUAR CON EL DIRECTOR]` La acotación no consta comunicada formalmente.
