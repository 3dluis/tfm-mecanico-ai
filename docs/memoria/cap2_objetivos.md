# Capítulo 2: Objetivos del TFM

> Estado: redactado sobre `research/propuestas-objetivos.md` (1 de septiembre de 2026),
> opción A en los tres casos. **Los enunciados reformulados están pendientes de consenso con
> el director**, junto con el título definitivo. La versión aprobada en la propuesta temática
> de julio de 2026 se conserva en el Anexo A con su correspondencia.

Los objetivos traducen la pregunta del capítulo 1 en compromisos verificables al terminar:
cada uno nombra las fases que lo cumplen y las métricas con que se comprueba. Ninguno promete
algo que el diseño no pueda medir.

## Objetivo general

Evaluar experimentalmente un agente de recuperación aumentada por evidencia, diseñado a tal
efecto, en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos
OBD-II manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la
sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no pertinente.

Tres decisiones de redacción conviene explicar. El verbo es uno solo, *evaluar*, porque el
artefacto es aquí el medio y no el fin. Se añade «o no pertinente» porque la pregunta no solo
interroga si el agente reconoce la ausencia de evidencia, sino si distingue la evidencia
parecida de la que de verdad sostiene una afirmación. Y se escribe «datos OBD-II» sin
adjetivo, como la propia pregunta desde su enmienda del 3 de septiembre de 2026: la procedencia
de cada conjunto se declara en el capítulo 4 y su validez externa en el capítulo 6.

El enunciado difiere del aprobado en julio en dos puntos: aquel llevaba dos verbos y cerraba
con una cláusula sobre cómputo embarcado que ya no describe el trabajo ejecutado. Ambos ajustes están pendientes de consulta con la dirección
(`preguntas-abiertas-al-director.md`, P-01).

## Objetivos específicos

Son cinco. El primero delimita el vacío que la
pregunta aborda; el segundo y el tercero construyen el entorno experimental y el modelo de
diagnóstico; el cuarto implementa el agente que recupera, verifica y decide; y el quinto lo
evalúa bajo las cuatro condiciones de evidencia y documenta el trabajo. La evaluación no está
reservada al último: el tercero también evalúa lo que construye.

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
de métricas M1. La calibración se nombra expresamente porque la confianza alimenta el
criterio de suficiencia: sin calibrar, ese criterio decidiría sobre un número que no significa
lo que aparenta.

El enunciado aprobado hablaba de técnicas no supervisadas de detección de anomalías. El diseño
ejecutado usa un modelo supervisado con atribución de descriptores, y conserva íntegra la parte
del enunciado original relativa a explicabilidad. El cambio condiciona lo que puede afirmarse
sobre fallos no vistos durante el entrenamiento, y por eso se declara aquí en lugar de quedar
implícito; su confirmación está pendiente de consulta con la dirección (P-01 y P-02 del registro
de preguntas abiertas).

**OE4. Implementar un agente** que recupere evidencia documental del vehículo, construya
afirmaciones ancladas simultáneamente en la evidencia observacional y en la documental,
verifique de forma determinista que cada cita sostiene lo afirmado y decida entre explicar y
abstenerse mediante un criterio de suficiencia independiente del modelo de lenguaje. Lo cumplen
las fases E11 a E16, de las que E14 y E16 siguen pendientes, y se mide con los grupos M2, M3,
M4 y M5.

Se desarrolla en cuatro fases que siguen el orden en que el sistema procesa un caso, y que el
capítulo 4 detalla con su entrada, su proceso, su salida y su artefacto: **recuperación** de la
evidencia documental, medida con M2 y ligada a PI.2; **construcción** de las afirmaciones
ancladas, con M3, que es descriptiva y no responde a ninguna subpregunta; **verificación**
determinista de que cada cita sostiene lo afirmado, con M4 y ligada a PI.2 y PI.4; y
**decisión** de explicar o abstenerse mediante el criterio de suficiencia, con M5 y ligada a
PI.3 y PI.4. Ninguna de las cuatro métricas está validada todavía, por dos razones que el
capítulo 4 desarrolla: la recuperación que las alimentó está bajo reejecución canónica y la
condición con distractor bajo diagnóstico.

**OE5. Evaluar el agente frente a las hipótesis declaradas bajo cuatro condiciones de
disponibilidad y pertinencia de la evidencia**, completa, parcial, ausente y con distractor,
midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las afirmaciones y
calidad de la abstención con su cobertura, aislando la contribución de cada componente
mediante ablaciones, y documentar el trabajo conforme a la normativa de la titulación,
incluidos de forma explícita los resultados negativos y las limitaciones de validez. Lo
cumplen las fases E17 a E20. «Con su cobertura» es deliberado, por la razón que el capítulo 4
desarrolla: un sistema que se abstuviera siempre tendría abstención perfecta y utilidad nula.

El enunciado de julio hablaba de dos escenarios y no cubría las ablaciones ni la demostración
final. La dirección validó expresamente el diseño de cuatro condiciones en septiembre de 2026.

## Correspondencia entre objetivos, fases y métricas

| Objetivo | Fases | Métricas | Estado a 10 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | avanzado; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cinco de seis cerradas; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cerradas sobre datos sintéticos |
| OE4 | E11, E12, E13, E15; **E14 y E16 pendientes** | M2, M3, M4, M5 | M2, M3 y M5 medidas; **M4 implementada y no medida**; ninguna validada |
| OE5 | E17, E18, E19, E20 | M1–M6 | E17 ejecutada; E18 pendiente; E19 y E20 pendientes del conjunto de evaluación final |

Ninguna de las veinte fases queda sin objetivo, y ninguna subpregunta sin fase que la responda.

Los cinco se persiguen sobre un único vehículo de referencia, el Mazda 3 BK de 2007 con motor
Z6, y el alcance de lo que puede afirmarse queda acotado por esa elección, justificada en el
capítulo 4.

## Lo que los objetivos no incluyen

La propuesta temática de julio de 2026 contemplaba además el despliegue sobre una placa
embarcada, una aplicación móvil y una plataforma en la nube. Esos tres elementos no forman
parte de los objetivos de este trabajo: no aportan evidencia a la pregunta de investigación y
su coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6. Esta acotación del alcance respecto de la propuesta inicial está pendiente de
constancia formal ante la dirección (P-03 del registro de preguntas abiertas).
