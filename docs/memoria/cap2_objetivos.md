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

Este enunciado difiere del aprobado en julio en dos puntos, ambos documentados. Aquel llevaba
dos verbos, «diseñar y evaluar», mientras la plantilla de la titulación indica uno solo; y
cerraba con una cláusula sobre restricciones de cómputo en plataforma embarcada que ya no
describe el trabajo ejecutado, porque las mediciones de rendimiento se realizan sobre un
ordenador de sobremesa y el despliegue embarcado figura en la prospectiva del capítulo 6. La
confirmación de ambos ajustes está pendiente de consulta con la dirección
(`preguntas-abiertas-al-director.md`, P-01).

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

El enunciado aprobado hablaba de técnicas no supervisadas de detección de anomalías. El diseño
ejecutado usa un modelo supervisado con atribución de descriptores, y conserva íntegra la parte
del enunciado original relativa a explicabilidad. El cambio condiciona lo que puede afirmarse
sobre fallos no vistos durante el entrenamiento, y por eso se declara aquí en lugar de quedar
implícito; su confirmación está pendiente de consulta con la dirección (P-01 y P-02 del registro
de preguntas abiertas).

**OE4. Implementar un agente** que recupere evidencia documental del vehículo, construya
afirmaciones ancladas simultáneamente en la evidencia observacional y en la documental,
verifique de forma determinista que cada cita sostiene lo afirmado y decida entre explicar y
abstenerse mediante un criterio de suficiencia independiente del modelo de lenguaje. Lo
cumplen las fases E11 a E16 y se mide con los grupos M2, M4 y M5.

Es el objetivo que sostiene el núcleo de la pregunta, de modo que conviene desglosarlo en las
cuatro fases que lo componen, con lo que entra, lo que hace y lo que deja escrito cada una.
El desglose sigue el orden en que el sistema procesa un caso, y cada fase produce un artefacto
que la siguiente consume.

#### Fase 4.1 · Recuperación de evidencia (E11, E12)

| | |
|---|---|
| **Entrada** | ventana de telemetría OBD-II ya clasificada, ficha del vehículo y corpus documental de taller en la variante de corpus que la condición experimental determine |
| **Proceso** | consulta al índice vectorial acotada por vehículo, por motor aplicable y por los códigos de avería que documentan la condición diagnosticada; ordenación por autoridad documental; conservación de la procedencia de cada fragmento hasta su fichero de origen |
| **Salida** | conjunto de fragmentos recuperados, cada uno con su identificador, su documento, su sección y su puntuación |
| **Artefactos** | `experiments/E12_retrieval.json`, índice `rag.document_chunk` con procedencia por fragmento |
| **Métrica** | M2, recuperación: acierto en los diez primeros, rango recíproco medio y ganancia acumulada descontada, **reportados por condición** y no en agregado |
| **Criterio de aceptación** | que la evidencia relevante desaparezca de los fragmentos recuperados cuando la variante de corpus la retire. **La mitad afirmativa no es un criterio**: la búsqueda se acota por los códigos que documentan la condición diagnosticada, de modo que encontrar el documento correcto está garantizado por construcción y no puede fallar |
| **Responde a** | PI.2 |

#### Fase 4.2 · Construcción de la explicación (E13; E14 pendiente)

| | |
|---|---|
| **Entrada** | atribución de descriptores del modelo especializado, su confianza calibrada y los fragmentos de la fase anterior |
| **Proceso** | construcción de una afirmación por descriptor observado, anclada a la vez en la observación y en el fragmento documental que la sostiene; el modelo de lenguaje **redacta**, no decide: recibe el paquete de evidencia ya montado y el veredicto ya emitido |
| **Salida** | conjunto de afirmaciones, cada una con su observación de origen y sus citas documentales |
| **Artefactos** | `experiments/E13_agente_*.json` para cada configuración de redactor |
| **Métrica** | M3, explicación: adecuación al esquema de salida y tasa de salidas válidas. **Es descriptiva y no responde a ninguna subpregunta**, y así se declara |
| **Criterio de aceptación** | que la salida se ajuste al esquema y que ninguna afirmación cite un fragmento ausente del paquete recibido |
| **Responde a** | **ninguna subpregunta**, en coherencia con M3, que se declara descriptiva. La fase es condición necesaria de PI.2 —sin afirmaciones ancladas no hay nada que rastrear— pero no la mide |

La separación entre observación, evidencia, inferencia y explicación es deliberada y está en la
forma del dato, no solo en la redacción: la observación es el valor medido del descriptor, la
evidencia es el fragmento del manual, la inferencia es la salida del modelo especializado, y la
explicación es el texto que las une. Ninguna de las cuatro puede ocupar el lugar de otra sin que
el registro lo delate.

#### Fase 4.3 · Verificación del soporte (E15)

| | |
|---|---|
| **Entrada** | las afirmaciones de la fase anterior y los fragmentos citados |
| **Proceso** | comprobación determinista, **fuera del modelo de lenguaje**, de que cada fragmento citado menciona la señal observada, constituye contenido diagnóstico, porta el código de avería que documenta la condición y desempeña el papel documental de procedimiento |
| **Salida** | una comprobación por pareja de afirmación y fragmento, con su resultado y el motivo |
| **Artefactos** | `experiments/E15_suficiencia.json`, campo `support_checks`. **Es la corrida en modo oracular**, con los tres canales de información abiertos, que la metodología etiqueta como **cota superior asistida por oráculo** y no como estimación del comportamiento. Existen además las variantes no oracular y adversa |
| **Métrica** | M4, trazabilidad: corrección de las citas, completitud y tasa de soporte. La distancia entre completitud y soporte mide cuántas afirmaciones llevan una referencia que no las respalda |
| **Criterio de aceptación** | que ninguna afirmación quede marcada como sostenida por un fragmento que no la sostiene |
| **Responde a** | PI.2 y PI.4 |

Que la verificación sea determinista y externa al modelo de lenguaje es lo que impide que una
inferencia del propio modelo se presente como evidencia documental: el verificador no lee lo que
el modelo escribió, sino lo que el manual dice.

#### Fase 4.4 · Decisión de explicar o abstenerse (dentro de E15; E16 pendiente)

| | |
|---|---|
| **Entrada** | el veredicto de soporte, la confianza calibrada del modelo especializado y el recuento de evidencia aplicable |
| **Proceso** | aplicación de un criterio de suficiencia independiente del modelo de lenguaje, con umbrales declarados y calibrados sobre validación. El registro del barrido declara que **no fue un pre-registro ciego**: el criterio se fijó tras ver una tabla previa, y el punto de operación pasó de 0,72 a 0,79 mediante una enmienda posterior al primer barrido, fechada y publicada junto al resultado original |
| **Salida** | decisión **EXPLICA** o **ABSTIENE**, con los motivos concretos de la abstención cuando la haya |
| **Artefactos** | `experiments/E15_suficiencia.json`, campo `verdict`, **corrida oracular**; barrido del umbral en `E15b_barrido_umbral.json` |
| **Métrica** | M5, abstención: abstención correcta, abstención injustificada y explicación sin fundamento, **siempre con su cobertura** |
| **Criterio de aceptación** | que la decisión cambie al manipular la evidencia disponible manteniendo constantes los datos, el modelo, la atribución y la confianza |
| **Responde a** | PI.3 y PI.4 |

La abstención **no se cuenta como fallo** cuando la evidencia es insuficiente: es la respuesta
correcta a esa situación y una capacidad evaluable por derecho propio. Por eso M5 exige
reportarla junto a su cobertura. Un sistema que se abstuviera siempre obtendría abstención
perfecta y utilidad nula, y ese desenlace figura desde el diseño entre los que refutarían el
trabajo.

#### Tamaño de la evidencia que sostiene OE4

Ninguna de las magnitudes anteriores significa nada sin su denominador, y el denominador no es
el número de filas de la tabla.

| Métrica | Filas ejecutadas | Observaciones independientes |
|---|---|---|
| M2, recuperación | 6 casos | 6 consultas |
| M3, explicación | 9 ejecuciones | 9 |
| M4 y M5, trazabilidad y abstención | 17 filas | **5 ventanas de origen** |

Las diecisiete filas del experimento de suficiencia proceden de cinco ventanas de telemetría
evaluadas bajo varias variantes de corpus. Tratarlas como diecisiete observaciones
independientes sería pseudorreplicación: la unidad de independencia es la ventana, y las
variantes de una misma ventana comparten datos, atribución y confianza.

#### Estado de las métricas de OE4

La distinción entre definir, implementar, medir y validar evita que una métrica se dé por
obtenida porque esté descrita.

| Métrica | Definida | Implementada | Medida | Validada |
|---|---|---|---|---|
| M2, recuperación | sí | sí | sí, sobre datos sintéticos | **no**: la ejecución vigente está bajo reejecución canónica |
| M3, explicación | sí | sí | sí, sobre datos sintéticos | descriptiva; no valida ninguna subpregunta |
| M4, trazabilidad | sí | sí | **no**: el registro guarda las comprobaciones de soporte en crudo, pero las magnitudes agregadas —corrección de citas, completitud, tasa de soporte— no se han calculado ni escrito en ningún artefacto | no |
| M5, abstención | sí | sí | sí, sobre datos sintéticos | **no**: misma dependencia |

M6, rendimiento, pertenece a OE5 y no a este objetivo; se menciona aquí solo para evitar la
confusión que provocaba incluirla.

Ninguna cifra de estas métricas debe leerse como validada, y son **dos** las razones, no una:
la recuperación que las alimentó está bajo reejecución canónica, y la condición con distractor
está bajo diagnóstico porque su manipulación no se ha comprobado. Las magnitudes ya medidas son reproducibles desde sus registros y
se conservan; lo que está en revisión es si la recuperación que las alimentó aislaba
correctamente el espacio vectorial en que buscaba.

**OE5. Evaluar el agente frente a las hipótesis declaradas bajo cuatro condiciones de
disponibilidad y pertinencia de la evidencia**, completa, parcial, ausente y con distractor,
midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las afirmaciones y
calidad de la abstención con su cobertura, aislando la contribución de cada componente
mediante ablaciones, y documentar el trabajo conforme a la normativa de la titulación,
incluidos de forma explícita los resultados negativos y las limitaciones de validez. Lo
cumplen las fases E17 a E20. «Con su cobertura» es deliberado: la corrección de la abstención
y su cobertura solo significan algo juntas, porque un sistema que se abstuviera siempre
tendría abstención perfecta y utilidad nula.

El enunciado aprobado en julio hablaba de dos escenarios de evaluación. El diseño ejecutado
tiene **cuatro condiciones** de disponibilidad y pertinencia de la evidencia, y añade las
ablaciones y la demostración final, que aquel enunciado no cubría. La dirección validó
expresamente este diseño de cuatro condiciones en su revisión de septiembre de 2026.

## Correspondencia entre objetivos, fases y métricas

| Objetivo | Fases | Métricas | Estado a 2 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | avanzado; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cinco de seis cerradas; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cerradas sobre datos sintéticos |
| OE4 | E11, E12, E13, E14, E15, E16 | M2, M4, M5 | ejecutadas sobre datos sintéticos; medidas pero **no validadas**: la recuperación está bajo reejecución canónica |
| OE5 | E17, E18, E19, E20 | M1–M6 | E17 ejecutada sobre datos sintéticos; E18 pendiente; E19 y E20 pendientes de la decisión sobre el dataset de evaluación final |

Ninguna de las veinte fases queda sin objetivo. Ninguna subpregunta de investigación queda
sin fase que la responda.

Los cinco objetivos se persiguen sobre un único vehículo de referencia, el Mazda 3 BK de 2007
con motor Z6, cuya elección y consecuencias se justifican en el capítulo 4. El alcance de lo que
puede afirmarse queda acotado por esa decisión.

## Lo que los objetivos no incluyen

La propuesta temática de julio de 2026 contemplaba además el despliegue sobre una placa
embarcada, una aplicación móvil y una plataforma en la nube. Esos tres elementos no forman
parte de los objetivos de este trabajo: no aportan evidencia a la pregunta de investigación y
su coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6. Esta acotación del alcance respecto de la propuesta inicial está pendiente de
constancia formal ante la dirección (P-03 del registro de preguntas abiertas).
