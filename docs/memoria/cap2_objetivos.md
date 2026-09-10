# Capítulo 2: Objetivos del TFM

Los objetivos traducen la pregunta del capítulo 1 en compromisos verificables al terminar:
cada uno nombra las fases que lo cumplen y, cuando procede, las métricas con que se comprueba.
Se ha procurado que ninguno prometa algo que el diseño experimental no pueda medir. Dos de
ellos, la revisión del conocimiento previo y la construcción del entorno, se verifican por sus
artefactos y no por una métrica.

## Objetivo general

Evaluar experimentalmente un agente de recuperación aumentada por evidencia, diseñado a tal
efecto, en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos
OBD-II manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la
sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no pertinente.

Tres decisiones sostienen este enunciado. El verbo es uno solo, *evaluar*, porque el
artefacto es aquí el medio y no el fin. Se añade «o no pertinente» porque la pregunta no solo
interroga si el agente reconoce la ausencia de evidencia, sino si distingue la evidencia
parecida de la que de verdad sostiene una afirmación. Y se escribe «datos OBD-II» sin
adjetivo, como la propia pregunta desde su enmienda del 3 de septiembre de 2026: la procedencia
de cada conjunto se declara en el capítulo 4 y su validez externa en el capítulo 6.

El enunciado difiere del aprobado en julio en dos puntos: aquel llevaba dos verbos y cerraba
con una cláusula sobre cómputo embarcado que ya no describe el trabajo ejecutado. Ambos ajustes están pendientes de consulta con la dirección
(`preguntas-abiertas-al-director.md`, P-01).

## Objetivos específicos

Son cinco. El primero revisa el conocimiento previo para delimitar el vacío que la pregunta
aborda; el segundo y el tercero construyen el entorno experimental y el modelo de diagnóstico;
el cuarto implementa el agente que recupera evidencia, construye afirmaciones, verifica su
soporte y decide; y el quinto evalúa ese agente bajo las cuatro condiciones de evidencia y
documenta el trabajo. La evaluación no está reservada al último: el tercero también evalúa lo
que construye.

**OE1. Revisar críticamente el estado del conocimiento** sobre diagnóstico vehicular a partir
de OBD-II, explicabilidad de modelos de diagnóstico, recuperación aumentada aplicada a
documentación técnica y abstención ante evidencia insuficiente, de modo que quede delimitado
el vacío que la pregunta de investigación aborda y las decisiones de diseño puedan
justificarse frente a trabajos previos. Se cumple en el capítulo 3, que describe también el
procedimiento de revisión inspirado en PRISMA con que se llevó a cabo.

**OE2. Construir un entorno experimental reproducible** que comprenda telemetría OBD-II
particionada sin fuga temporal y un corpus documental del vehículo con variantes congeladas
de disponibilidad de evidencia, de modo que cualquier tercero pueda repetir cada experimento
a partir de su registro. Lo cumplen las fases E1, E2, E4, E5 y E10; la fase E3, incorporación
de datos reales, queda como validación externa, pendiente de una fuente.

**OE3. Construir y evaluar un modelo de diagnóstico** sobre ventanas de telemetría,
contrastado frente a una referencia mínima y a un baseline tabular, con su confianza
calibrada y con atribución de descriptores, de modo que el sistema disponga de un contexto
diagnóstico verificable y caracterizado. Lo cumplen las fases E5 a E9 y se mide con el grupo
de métricas M1. La calibración se nombra expresamente porque la confianza alimenta el
criterio de suficiencia: sin calibrar, ese criterio decidiría sobre un número que no significa
lo que aparenta.

El enunciado aprobado hablaba de técnicas no supervisadas. El diseño ejecutado usa un modelo
supervisado con atribución, lo que condiciona lo que puede afirmarse sobre fallos no vistos
durante el entrenamiento.

**OE4. Implementar un agente** capaz de recuperar evidencia documental del vehículo, construir
afirmaciones sustentadas a la vez en la evidencia observacional y en la documental, verificar de
manera determinista que cada cita respalda aquello que se afirma, y decidir, mediante un
criterio de suficiencia independiente del modelo de lenguaje, cuándo existe fundamento para
explicar un diagnóstico y cuándo resulta más correcto abstenerse.

El objetivo se desarrolla entre las fases E11 y E16, de las que E14 y E16 siguen pendientes, y
sus fases recorren el mismo camino que hace un caso dentro del sistema. Primero se recupera la
evidencia documental pertinente, y la calidad de esa recuperación se observa con M2. Después se
construyen las afirmaciones a partir de la evidencia disponible; su adecuación estructural se
mide con M3, de carácter únicamente descriptivo. A continuación el verificador comprueba si las
citas recuperadas sostienen de verdad lo que se afirma, que es lo que M4 recoge bajo la
trazabilidad y la pertinencia de la evidencia. Y por último el criterio de suficiencia
determina si hay fundamento para explicar o si procede abstenerse, comportamiento que M5 evalúa
junto a su cobertura. El capítulo 4 detalla cada fase con su entrada, su proceso, su salida y su
artefacto.

Esa separación no es solo una decisión de arquitectura. Permite distinguir entre encontrar
información, usarla como evidencia y aceptar que esa evidencia basta para sostener una
explicación. Una recuperación aparentemente correcta no garantiza por sí sola que una afirmación
esté respaldada, igual que disponer de documentos semánticamente próximos no significa que sean
aplicables al caso analizado. Por esa razón la decisión final no se delega en el modelo de
lenguaje.

En el estado actual del trabajo, M2, M3 y M5 están definidas, implementadas y calculadas sobre
datos sintéticos, mientras M4 está implementada y sus magnitudes agregadas aún no se han
calculado. Los resultados obtenidos con todas ellas no se consideran todavía definitivos: la
recuperación que alimenta al agente está sometida a una reejecución canónica y la condición con
distractor continúa bajo diagnóstico. Mantener esa distinción importa, porque el objetivo y sus
mecanismos están implementados, y no correspondería presentar como establecido aquello cuya
evidencia experimental sigue en revisión.

**OE5. Evaluar el agente frente a las hipótesis declaradas bajo cuatro condiciones de
disponibilidad y pertinencia de la evidencia**, completa, parcial, ausente y con distractor,
midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las afirmaciones y
calidad de la abstención con su cobertura, aislando la contribución de cada componente
mediante ablaciones, y documentar el trabajo conforme a la normativa de la titulación,
incluidos de forma explícita los resultados negativos y las limitaciones de validez. Lo
cumplen las fases E17 a E20. «Con su cobertura» es deliberado, por la razón que el capítulo 4
desarrolla: un sistema que se abstuviera siempre tendría abstención perfecta y utilidad nula.

El enunciado de julio hablaba de dos escenarios y no cubría las ablaciones ni la demostración
final. La dirección validó el diseño de cuatro condiciones en septiembre de 2026.

## Correspondencia entre objetivos, fases y métricas

| Objetivo | Fases | Métricas | Estado a 10 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | avanzado; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cuatro cerradas; **E10 con la infraestructura cerrada y el corpus vacío**; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cuatro cerradas sobre datos sintéticos; **E8 pendiente** |
| OE4 | E11, E12, E13, E15; **E14 y E16 pendientes** | M2, M3, M4, M5 | M2, M3 y M5 calculadas **sobre datos sintéticos**; **M4 implementada, sin calcular sus magnitudes agregadas**; resultados no definitivos |
| OE5 | E17, E18, E19, E20 | M1–M6 | **E17 ejecutada sin informe de fase**: sus resultados constan en el registro de suficiencia y el índice de experimentos la da pendiente de cierre. E18 pendiente; E19 y E20 pendientes del conjunto de evaluación final |

Ninguna de las veinte fases queda sin objetivo, y ninguna subpregunta sin fase que la responda.

Los cinco se persiguen sobre un único vehículo de referencia, el Mazda 3 BK de 2007 con motor
Z6, y el alcance de lo que puede afirmarse queda acotado por esa elección, justificada en el
capítulo 4.

## Lo que los objetivos no incluyen

La propuesta temática de julio de 2026 contemplaba además el despliegue sobre una placa
embarcada, una aplicación móvil y una plataforma en la nube. Esos tres elementos no forman
parte de los objetivos de este trabajo: no aportan evidencia a la pregunta de investigación y
su coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6.
