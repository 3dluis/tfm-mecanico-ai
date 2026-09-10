# Capítulo 2: Objetivos del TFM

Los objetivos del TFM transforman la pregunta de investigación en aspectos concretos que pueden
desarrollarse y evaluarse a lo largo del trabajo. Cada objetivo específico se relaciona con las
fases que permiten abordarlo y, cuando su naturaleza lo requiere, con las métricas utilizadas
para analizar los resultados obtenidos. De este modo, se conserva una relación explícita entre
la pregunta de investigación, las decisiones metodológicas y la evidencia experimental. No todos
los objetivos requieren una medida cuantitativa: la revisión del conocimiento previo y la
construcción del entorno experimental se justifican mediante los artefactos y evidencias que
producen, mientras que los objetivos asociados al comportamiento del sistema se someten a
evaluación experimental.

## Objetivo general

Evaluar experimentalmente un agente de recuperación aumentada por evidencia, diseñado a tal
efecto, en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos
OBD-II manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la
sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no pertinente.

Tres decisiones sostienen este enunciado. El verbo es uno solo, *evaluar*, porque el artefacto
es aquí el medio y no el fin. Se añade «o no pertinente» porque la pregunta no solo interroga si
el agente reconoce la ausencia de evidencia, sino si distingue la evidencia parecida de la que
de verdad sostiene una afirmación. Y se escribe «datos OBD-II» sin adjetivo, como la pregunta
desde su enmienda del 3 de septiembre de 2026: la procedencia de cada conjunto se declara en el
capítulo 4.

El enunciado difiere del aprobado en julio en dos puntos: aquel llevaba dos verbos y cerraba con
una cláusula sobre cómputo embarcado que ya no describe el trabajo ejecutado. Ambos ajustes están
pendientes de consulta con la dirección (`preguntas-abiertas-al-director.md`, P-01).

## Objetivos específicos

Son cinco. El primero delimita el vacío que la pregunta aborda; el segundo y el tercero
construyen el entorno experimental y el modelo de diagnóstico; el cuarto implementa el agente y
el quinto lo evalúa bajo las cuatro condiciones de evidencia y documenta el trabajo. La
evaluación no está reservada al último: el tercero también evalúa lo que construye.

**OE1. Revisar críticamente el estado del conocimiento** sobre diagnóstico vehicular a partir
de OBD-II, explicabilidad, recuperación aumentada aplicada a documentación técnica y abstención
ante evidencia insuficiente, de modo que quede delimitado el vacío que la pregunta aborda y las
decisiones de diseño puedan justificarse frente a trabajos previos. Se cumple en el capítulo 3,
que describe también el procedimiento de revisión inspirado en PRISMA con que se llevó a cabo.

**OE2. Construir un entorno experimental reproducible** que comprenda telemetría OBD-II
particionada sin fuga temporal y un corpus documental del vehículo con variantes congeladas
de disponibilidad de evidencia, de modo que cualquier tercero pueda repetir cada experimento
a partir de su registro. Lo cumplen las fases E1, E2, E4, E5 y E10; E3, la incorporación de
datos reales, queda como validación externa pendiente de fuente.

**OE3. Construir y evaluar un modelo de diagnóstico** sobre ventanas de telemetría,
contrastado frente a una referencia mínima y a un baseline tabular, con su confianza calibrada
y con atribución de descriptores, de modo que el sistema disponga de un contexto diagnóstico
verificable y caracterizado. Lo cumplen las fases E5 a E9 y se mide con M1. La calibración se
nombra expresamente porque la confianza alimenta el criterio de suficiencia: sin calibrar, ese
criterio decidiría sobre un número que no significa lo que aparenta.

El enunciado aprobado hablaba de técnicas no supervisadas; el diseño ejecutado usa un modelo
supervisado con atribución, lo que condiciona lo que puede afirmarse sobre fallos no vistos.
La divergencia está planteada a la dirección y sin resolver (P-02).

**OE4. Implementar un agente** capaz de recuperar evidencia documental del vehículo, construir
afirmaciones sustentadas a la vez en la evidencia observacional y en la documental, verificar de
manera determinista que cada cita respalda aquello que se afirma, y decidir, mediante un
criterio de suficiencia independiente del modelo de lenguaje, cuándo existe fundamento para
explicar un diagnóstico y cuándo resulta más correcto abstenerse.

El objetivo se desarrolla entre las fases E11 y E16, de las que E14 y E16 siguen pendientes, y
sus cuatro fases recorren el mismo camino que hace un caso dentro del sistema: recuperar la
evidencia documental, que observa M2; construir las afirmaciones, cuya adecuación estructural
describe M3; verificar que las citas sostienen lo que se afirma, que es lo que M4 recoge; y
decidir si hay fundamento para explicar o procede abstenerse, comportamiento que M5 evalúa junto
a su cobertura, y el capítulo 4 detalla cada una. Separarlas permite distinguir entre encontrar información, usarla como evidencia y
aceptar que esa evidencia basta; por esa razón la decisión final no se delega en el modelo de
lenguaje.

Ninguno de los resultados obtenidos con esas métricas es todavía definitivo: la recuperación que
alimenta al agente está sometida a una reejecución canónica y la condición con distractor
continúa bajo diagnóstico.

**OE5. Evaluar el agente frente a las hipótesis declaradas bajo cuatro condiciones de
disponibilidad y pertinencia de la evidencia**, completa, parcial, ausente y con distractor,
midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las afirmaciones y
calidad de la abstención con su cobertura, aislando la contribución de cada componente
mediante ablaciones, y documentar el trabajo conforme a la normativa de la titulación,
incluidos de forma explícita los resultados negativos y las limitaciones de validez. Lo
cumplen las fases E17 a E20. «Con su cobertura» es deliberado: un sistema que se abstuviera
siempre tendría abstención perfecta y utilidad nula, como desarrolla el capítulo 4.

La dirección validó el diseño de cuatro condiciones en septiembre de 2026; el enunciado de julio
hablaba de dos escenarios y no cubría las ablaciones ni la demostración final.

## Correspondencia entre objetivos, fases y métricas

| Objetivo | Fases | Métricas | Estado a 10 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | en curso; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cuatro cerradas; **E10 con la infraestructura cerrada y el corpus vacío**; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cuatro cerradas sobre datos sintéticos; **E8 pendiente** |
| OE4 | E11, E12, E13, E15; **E14 y E16 pendientes** | M2, M3, M4, M5 | M2, M3 y M5 calculadas **sobre datos sintéticos**; **M4 implementada, sin calcular sus magnitudes agregadas**; resultados no definitivos |
| OE5 | E17, E18, E19, E20 | M1–M6 | **E17 ejecutada sin informe de fase**; E18 pendiente; E19 y E20 pendientes del conjunto de evaluación final |

Ninguna de las veinte fases queda sin objetivo, y ninguna subpregunta sin fase que la responda.

Los cinco se persiguen sobre un único vehículo de referencia, el Mazda 3 BK de 2007 con motor
Z6, elección justificada en el capítulo 4 que acota cuanto pueda afirmarse. El alcance ejecutado
es más estrecho que el aprobado en julio, y esa distancia está planteada a la dirección (P-03).

Quedan fuera el despliegue sobre placa embarcada, la aplicación móvil y la plataforma en la
nube que contemplaba la propuesta de julio de 2026: no aportan evidencia a la pregunta y su
coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6.
