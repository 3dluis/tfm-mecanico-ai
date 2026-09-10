# Capítulo 4: Marco Metodológico

El trabajo sigue el ciclo de la investigación en ciencias del diseño (Peffers et al., 2007,
MET-16; Hevner et al., 2004, MET-17): identifica un problema, fija los objetivos de una
solución, construye un artefacto, lo demuestra sobre casos, lo evalúa con criterios fijados
de antemano y comunica el resultado. La elección no es de conveniencia. La pregunta de
investigación no puede responderse observando sistemas existentes, porque ninguno de los
revisados separa la decisión de explicar de la redacción de la explicación; hay que
construir uno que lo haga y medir si esa separación produce el comportamiento que la
pregunta interroga. El artefacto es el instrumento, no la contribución: la contribución es
la evidencia experimental sobre su comportamiento bajo condiciones controladas de evidencia.

Dos compromisos de método atraviesan todo el capítulo. El primero es que **el criterio de
éxito de cada experimento se fija antes de ejecutarlo**, se escribe en el informe de fase y
no se modifica después de ver el resultado; los resultados negativos se publican con el mismo
detalle que los positivos. El segundo es que **toda cifra publicada procede de un registro
de ejecución reproducible**, con su commit, semilla, versiones de datos, corpus, modelo y
prompt. Lo que no se ha ejecutado se declara como no ejecutado.

Todas las cifras de este capítulo proceden de registros versionados del repositorio o de la
ficha de calibración del vehículo, y el diseño que describe se ejecutó sobre datos sintéticos.
De las veinte fases planificadas, once están cerradas y tres quedan sin cerrar dentro del tramo
ejecutado —la evaluación del modelo, el corpus documental, que tiene la infraestructura cerrada
y el contenido vacío, y las condiciones de evidencia, cuyos resultados constan en el registro sin
informe de fase—. Las seis restantes pertenecen al tramo pendiente: los datos reales, la
trazabilidad, la abstención, las ablaciones, la evaluación final y la demostración.

## Población y muestra

Se describen, por este orden, la población a la que se pretende generalizar, la muestra de
telemetría con su procedencia, la muestra documental que constituye el corpus y los casos
de referencia sobre los que se evalúa el agente.

### Población

La población de referencia es el conjunto de ventanas de telemetría OBD-II de un vehículo de
combustión con puerto normalizado, en condiciones de conducción ordinarias, con y sin fallo
en los sistemas de admisión, combustible, encendido, refrigeración y emisiones. El vehículo
de estudio es un Mazda 3 de la generación BK, año 2007, motor de gasolina de 1,6 litros con
código Z6 y transmisión manual. Se eligió entre tres candidatos, Mazda 3, Honda Civic y
Toyota Corolla del rango 2000–2016, por la disponibilidad de su manual de taller completo y
porque sus procedimientos de diagnóstico son específicos del motor, lo que permite construir
la condición con distractor con evidencia real de otro motor de la misma gama. La comparación
está documentada en el repositorio.

Esta elección fija el contexto experimental sobre el que se construyen la telemetría sintética,
el corpus documental y los casos utilizados para evaluar el agente.

| | |
|---|---|
| Vehículo | Mazda 3 |
| Generación | BK |
| Año de referencia | 2007 |
| Motor del experimento | Z6, gasolina de 1,6 litros |
| Transmisión | manual |
| Corpus documental | manual de taller del fabricante para la generación BK, 1 documento estructurado en 6 158 fragmentos indexados |
| Motores documentados en el corpus | LF de 2,0 litros con 507 ficheros, Z6 de 1,6 con 486 y ZJ de 1,4 con 486, más 90 comunes a los tres |

**Qué depende de esta elección.** La calibración del generador sintético, cuyas constantes
salen una a una de páginas concretas del manual y llevan su cita literal; el corpus sobre el que
recupera el agente; los códigos de avería que documentan cada condición de fallo; los
procedimientos de diagnóstico que el verificador exige como soporte; y la construcción de la
condición con distractor, que usa el procedimiento del motor LF para el mismo código de avería.

**Qué no depende.** La arquitectura del agente, la política de suficiencia y los criterios de
verificación son independientes del vehículo: ninguna de sus reglas nombra un motor, un código
ni una señal concretos.

**Qué limita.** Los resultados describen el comportamiento del sistema sobre **un vehículo, una
generación y un corpus documental**. La coherencia entre telemetría, documentación y códigos que
esta elección garantiza por construcción es precisamente lo que no puede darse por supuesto en
otro vehículo, donde el fabricante puede usar códigos genéricos distintos, documentar los
procedimientos con otra estructura o no publicar manual accesible. La generalización a otros
vehículos o a otras generaciones del mismo modelo no se sigue de estos resultados y figura entre
las amenazas a la validez del capítulo 6.

El código de motor, la cilindrada y la transmisión son un **supuesto de trabajo** del generador
sintético, no una lectura tomada de un vehículo. El supuesto se justifica porque los códigos de
avería que el experimento utiliza están documentados en el manual para los motores ZJ y Z6, de
modo que la telemetría generada y la documentación consultada se refieren a la misma
configuración mecánica. Si se incorpora telemetría real como validación externa, esos tres
valores deben tomarse del vehículo del que proceda, y la coincidencia con el corpus documental
deja de estar garantizada por construcción y pasa a ser una comprobación previa.

### Muestra: telemetría

La pregunta de investigación no exige que los datos sean reales; exige que cada resultado
declare sobre qué datos se obtuvo. La fase de incorporación de datos reales (E3) queda como
validación externa, pendiente de una fuente. La muestra con la que se han ejecutado los
experimentos es **sintética** (`dataset_type: synthetic`), generada por un modelo
paramétrico determinista con semilla fija. La taxonomía de procedencia que rige todo el
trabajo tiene cuatro valores, real, sintético, simulado y conjunto público, y ningún
resultado se agrega entre procedencias distintas sin decirlo. Se describe con precisión
porque su validez depende de cómo se construyó.

El generador produce sesiones de conducción en tres regímenes, ralentí, urbano y carretera,
para seis condiciones: sin fallo y cinco fallos representativos de los sistemas nombrados
arriba. Cada fallo tiene una firma que afecta a una o varias señales con un mecanismo físico
declarado; por ejemplo, una fuga de vacío eleva las correcciones de combustible a corto y
largo plazo sin tocar el caudal de aire medido, y un termostato bloqueado abierto impide que
la temperatura del refrigerante alcance su valor de régimen. Las constantes del generador,
régimen de ralentí, temperatura de apertura del termostato, rangos de tensión de la sonda de
oxígeno, límites de corrección de combustible que disparan cada código de avería, están
ancladas una por una a valores del manual de taller, con la cita de la página de la que
proceden, en un fichero de calibración versionado. La calibración se hizo después de una
primera versión de los datos y corrigió varias constantes que no procedían de ninguna fuente;
el proceso está documentado con cada hallazgo y su corrección.

| Parámetro de la muestra sintética | Valor |
|---|---|
| Procedencia (`dataset_type`) | `synthetic`; identificador `synthetic_v2` |
| Condiciones | 6 (sin fallo y cinco fallos) |
| Sesiones por condición | 12; 72 en total |
| Duración de cada sesión | 600 s |
| Frecuencia de muestreo | 1 Hz; 43 200 muestras |
| Señales | 12: régimen, velocidad, carga, mariposa, temperatura de refrigerante, temperatura de admisión, caudal másico, presión del colector, correcciones de combustible a corto y largo plazo, sonda de oxígeno, avance del encendido |
| Semilla | 20260901 |
| Ventana de análisis | 120 s, con solape |
| Descriptores por ventana | 139 |
| Reparto | entrenamiento, validación y test, por sesión; 392 ventanas de entrenamiento y 98 de validación |

Registro: `data/raw/synthetic/synthetic_v2.meta.json`.

La elección de la ventana no fue arbitraria. Se estudiaron cuatro longitudes, 10, 30, 60 y
120 segundos, midiendo para cada fallo la separabilidad de sus descriptores respecto de la
condición sin fallo, en nivel y en dispersión, y comparándola con el suelo de ruido que se
obtiene al tomar el máximo entre todos los descriptores de una condición sin fallo,
partida en dos mitades por sesión, en treinta repeticiones. Ese suelo no es despreciable, y
crece con la ventana:

| Ventana | Suelo de ruido (percentil 90 del máximo entre 139 descriptores) |
|---|---|
| 10 s | 0,369 |
| 30 s | 0,399 |
| 60 s | 0,438 |
| 120 s | 0,512 |

Con ventanas cortas, el mejor descriptor de un fallo de encendido resultaba ser una variante
de la temperatura del refrigerante, señal que ese fallo no toca, y su tamaño de efecto
quedaba por debajo del suelo de ruido. Es el fenómeno que el trabajo estudia, en miniatura:
evidencia aparente que no sobrevive al escrutinio. Con 60 y 120 segundos el mejor descriptor
de ese fallo pasa a ser la sonda de oxígeno, que sí está en su mecanismo declarado, y con
120 segundos los mecanismos físicos declarados y los descriptores separables coinciden en
todas las condiciones detectables. Registro: `docs/experiments/E5_preprocesamiento.md`.

**Limitación declarada.** Los datos sintéticos no tienen validez externa. Se parecen a los
reales en lo que el manual permite comprobar y en nada más; en particular, no reproducen la
variabilidad entre conductores, el desgaste, ni los fallos que no están en el generador.
Todos los resultados sobre ellos se presentan con su procedencia declarada y acotados a
ella.

### Muestra: corpus documental

El corpus es el manual de taller del vehículo, en su copia local del autor, procedente de un
repositorio secundario en la web. No se redistribuye; se registra su huella SHA-256 para que
un tercero que disponga del mismo documento pueda comprobar la identidad. Está compuesto por
ficheros por procedimiento, cada uno con los códigos de motor a los que aplica.

| Corpus | Valor |
|---|---|
| Ficheros del manual con aplicabilidad al motor LF | 507 |
| Ficheros con aplicabilidad a los motores ZJ y Z6 | 486 |
| Ficheros comunes a los tres motores | 90 |
| Fragmentos indexados | 6 158, todos en inglés |
| Modelos de embeddings indexados | dos: uno monolingüe en inglés y otro multilingüe, ambos sobre los 6 158 fragmentos, para medir el efecto del idioma de la consulta |
| Idioma de las consultas | español e inglés; cada caso anotado lleva la consulta en ambos |

El manual no se traduce. El trabajo se escribe en español y la documentación está en
inglés, que es la situación normal de un taller en España con un vehículo de fabricante
extranjero; la recuperación es translingüe, y el capítulo 5 muestra que no funciona sola.

Cada fragmento conserva su procedencia completa: documento, versión, sección, página, códigos
de avería que contiene, sistema del vehículo y motores a los que aplica. Esa metadata es lo
que permite construir las variantes del corpus del diseño experimental retirando o dejando
fragmentos por código de avería o por fichero, sin tocar nada más.

### Casos de referencia

La evaluación del agente se hace sobre un conjunto anotado de nueve casos, construidos a
partir de ventanas de validación correctamente clasificadas, uno o dos por condición de
fallo, cruzados con las condiciones de corpus. Cada caso lleva anotado, antes de ejecutar
nada, el diagnóstico esperado, la consulta en los dos idiomas, los ficheros del manual que
constituyen evidencia relevante, los de apoyo, los distractores, qué se retira del índice y la
acción esperada, explicar o abstenerse. `[Pendiente: señales y ventanas relevantes,
fragmentos a nivel de chunk, afirmaciones admisibles y evidencia mínima, previstos en el
diseño y no anotados todavía.]`

El conjunto de test de la telemetría **permanece cerrado** hasta la evaluación final. Los
umbrales del criterio de suficiencia se calibraron únicamente sobre validación, y todas las
cifras de esta memoria anteriores a E19 son de validación.

## Objetivos de investigación

Los objetivos del capítulo 2 se operacionalizan en cuatro subpreguntas, cada una con un
desenlace que la sostendría y otro que la refutaría, fijados antes de la evaluación.

| Subpregunta | Qué pregunta | Sostenida si | Refutada si |
|---|---|---|---|
| PI.1 | ¿Diagnostica a partir de la telemetría? | supera a la clase mayoritaria con margen amplio y su confianza está calibrada | no supera a la referencia mínima, o la confianza no significa lo que aparenta |
| PI.2 | ¿La explicación es trazable? | toda afirmación admitida se ancla en una observación y un documento verificados | las referencias existen pero no sostienen lo afirmado |
| PI.3 | ¿Reconoce la insuficiencia? | la decisión cambia al retirar la evidencia, con todo lo demás idéntico | explica igual con y sin evidencia, o se abstiene siempre |
| PI.4 | ¿Rechaza evidencia engañosa? | el procedimiento de otro motor no se acepta como soporte | acepta distractores como evidencia |

La respuesta global a la pregunta admite tres valores, sostenida, parcialmente sostenida y
no sostenida, y cuatro desenlaces la refutarían, enumerados de antemano: que el agente
explique con la misma soltura con y sin evidencia; que se abstenga casi siempre y la
abstención resulte trivial; que acepte distractores; y que las referencias existan pero no
sostengan lo que se afirma con ellas.

## Variables intervinientes e instrumentos de evaluación

El apartado declara la única variable manipulada, las que se mantienen controladas, las
seis familias de variables medidas y los instrumentos con que se miden.

### Variable manipulada

Una sola: **qué evidencia documental está disponible en el corpus**. Toma cuatro valores.

| Condición | Corpus | Comportamiento esperado |
|---|---|---|
| FULL | contiene la evidencia correcta | EXPLAIN, con cada afirmación trazada |
| PARTIAL | evidencia incompleta | ABSTAIN, salvo explicación limitada declarada como tal |
| ABSENT | la evidencia relevante ha sido retirada del índice | ABSTAIN |
| DISTRACTOR | contiene evidencia parecida pero incorrecta | rechazo del distractor; ABSTAIN si no queda otra |

Las variantes se construyen sobre el mismo índice, excluyendo fragmentos por código de
avería o por fichero en el momento de la consulta. La condición ABSENT retira todos los
fragmentos que portan los códigos de avería de la condición, no solo los del procedimiento
principal; una primera versión que retiraba solo estos últimos dejaba evidencia en las tablas
de códigos y produjo un falso positivo del experimento central, detectado y corregido.

### Variables controladas

Los datos de telemetría, el modelo de diagnóstico, la atribución, la confianza calibrada, la
consulta, el proveedor de lenguaje y sus parámetros, la semilla y la versión del prompt se
mantienen idénticos entre condiciones. Es esa constancia lo que permite atribuir un cambio de
comportamiento del agente a la disponibilidad de evidencia y no a otra cosa.

### Variables medidas

Se agrupan en seis familias. No todas se calculan en cada experimento; se reporta la que
corresponde y se dice cuál.

**M1, diagnóstico.** Exactitud, F1 macro y calibración del modelo especializado. La
calibración se mide con el error esperado de calibración (Naeini, Cooper y Hauskrecht, 2015,
MET-07) y se corrige con regresión isotónica (Zadrozny y Elkan, 2002, MET-05; Niculescu-Mizil
y Caruana, 2005, MET-06) ajustada por validación cruzada sobre entrenamiento, para no gastar
la validación en dos cosas.

**M2, recuperación.** Tasa de acierto en los diez primeros, rango recíproco medio y nDCG
sobre el conjunto anotado, reportados por condición de corpus y no solo en agregado, porque
el agregado promedia condiciones diseñadas para diferir.

**M3, explicación.** Adecuación al esquema de salida y tasa de salidas válidas. Es
descriptiva y no responde a ninguna subpregunta; se declara como tal.

**M4, trazabilidad.** Corrección de las citas (existen y resuelven), completitud (proporción
de afirmaciones con cita), tasa de soporte (proporción de afirmaciones cuya cita sostiene lo
afirmado) y su complemento. La distancia entre completitud y soporte es informativa por sí
misma: mide cuántas afirmaciones llevan una referencia que no las respalda, el fallo más
difícil de ver porque el texto parece impecable. Todas se calculan de forma determinista.

**M5, abstención.** Abstención correcta, abstención injustificada y explicación sin
fundamento, siempre acompañadas de la cobertura. Corrección y cobertura solo significan algo
juntas.

**M6, rendimiento.** Latencia por etapa y extremo a extremo, tamaño del modelo y coste de la
recuperación, con el dispositivo real de cada etapa. Se reporta como **métrica descriptiva** y
no como criterio de aceptación: el trabajo no fija un presupuesto de latencia, porque el
despliegue embarcado que lo habría justificado quedó fuera del alcance ejecutado.

### Instrumentos

Todos los instrumentos son código versionado con tests, y ninguna métrica que responda a una
subpregunta depende de un juicio humano ni de un modelo de lenguaje.

El **modelo de diagnóstico** es un bosque aleatorio (Breiman, 2001, MET-01) sobre los 139
descriptores de ventana, con pesos de clase, elegido como baseline por su robustez con pocos
datos; se contrastó con una red recurrente bidireccional de unidades GRU (Cho et al., 2014,
MET-02) sobre las secuencias crudas, que no lo superó en este volumen de datos. La
**atribución** usa valores de Shapley (Lundberg y Lee, 2017, MET-03) en su variante por
permutación, con un fondo de referencia de ventanas sin fallo y semilla fija, y produce para
cada caso las señales, estadísticos, valores, dirección y ventana temporal que más
contribuyen a la predicción. La memoria no afirma en ningún punto que esa atribución sea
causal: indica de qué depende la predicción del modelo, no qué le ocurre al vehículo.

El **sistema de recuperación** combina búsqueda semántica con un modelo multilingüe de
embeddings de frases (Reimers y Gurevych, 2019, MET-11) sobre una base de datos PostgreSQL
con extensión vectorial, búsqueda léxica sobre el texto completo y fusión por rango
recíproco (Cormack, Clarke y Buettcher, 2009, MET-12) que conserva las puntuaciones
originales; se filtra siempre por vehículo y, cuando procede, por motor. La recuperación
guiada por el diagnóstico añade a la consulta los códigos de avería que el manual asocia a la
condición predicha. Un **validador de aplicabilidad** asigna a cada fragmento uno de cinco
grados respecto del vehículo, coincidencia exacta, compatible, parcial, desconocido o
incompatible, y solo los dos primeros pueden contar como evidencia.

El **verificador de suficiencia** es determinista. Construye una afirmación por observación
atribuida, con plantillas que enuncian lo observado sin atribuir causa; para cada una busca
fragmentos aplicables que la sostengan, comprobando que el fragmento mencione la señal, tenga
contenido diagnóstico y porte un código de avería de la condición; y decide con un criterio
conjuntivo sobre la confianza calibrada, el número de fragmentos y fuentes de apoyo, la
cobertura de las afirmaciones y la ausencia de contradicciones. La abstención es una salida
válida del esquema, con su motivo y la evidencia que falta. El criterio sigue la lógica de la
clasificación con opción de rechazo (Chow, 1970, MET-08; Geifman y El-Yaniv, 2017, MET-09):
la decisión de no responder es una salida legítima cuya calidad se mide junto con su
cobertura.

El **modelo de lenguaje** es Qwen2.5 de 3 000 millones de parámetros (Qwen Team, 2024,
MET-14), ejecutado localmente sin clave ni red tras la descarga. Recibe la decisión, las
afirmaciones y la evidencia ya verificadas y redacta la salida en un esquema fijo; una
barrera externa rechaza cualquier cita que no corresponda a algo entregado. Se ajustó con
adaptadores de rango bajo (Hu et al., 2022, MET-13) sobre las proyecciones de atención, con
ejemplos derivados de ejecuciones auténticas del propio pipeline, con la pérdida calculada
solo sobre la respuesta y con una comprobación automática de que ningún fragmento del manual
aparece en las salidas de entrenamiento. El ajuste enseña el formato de la tarea y no el
contenido del vehículo: si el modelo memorizara el manual, en la condición ABSENT lo
recordaría de sus pesos y el experimento mediría memoria en lugar de evidencia.

## Diseño experimental

El plan tiene veinte fases, cada una con informe, criterio de aceptación y puertas de calidad
de código. Se agrupan en cinco bloques.

| Bloque | Fases | Qué producen |
|---|---|---|
| Entorno y datos | E1–E5 | auditoría del entorno, datos sintéticos calibrados, análisis exploratorio, ventana y reparto sin fuga |
| Modelo de diagnóstico | E6–E9 | baseline, modelo temporal, evaluación, atribución |
| Corpus y recuperación | E10–E12 | corpus del vehículo, ingesta, evaluación de la recuperación |
| Agente y suficiencia | E13–E16 | modelo de lenguaje, modelo de evidencia, verificador, abstención |
| Evaluación | E17–E20 | experimento integrado, ablaciones, evaluación final, demostración |

### Experimento central

El mismo caso, dos veces. En la primera, la telemetría pasa por el modelo, la atribución y
la recuperación, la evidencia resulta suficiente y el agente explica con cada afirmación
trazada. En la segunda, los mismos datos, el mismo modelo, la misma atribución y la misma
confianza, pero la evidencia relevante se ha retirado del índice: la recuperación no la
encuentra, la evidencia resulta insuficiente y el agente se abstiene. El contraste debe
verse sin necesidad de explicarlo. Las condiciones PARTIAL y DISTRACTOR extienden ese
contraste: la primera prueba que la evidencia incompleta no basta; la segunda, que la
evidencia parecida no cuenta. FULL y ABSENT prueban que el sistema responde a la *presencia*
de evidencia; DISTRACTOR prueba que responde a su *pertinencia*, y un sistema que confunda
similitud con soporte pasará las tres primeras y fallará esta.

### Particiones y cierre del test

Entrenamiento, validación y test se separan por sesión, nunca por partición aleatoria de
ventanas consecutivas, porque dos ventanas contiguas comparten casi toda su información y
repartirlas entre entrenamiento y test convertiría la evaluación en un espejo. El test
permanece cerrado hasta la evaluación final y su apertura exige una declaración explícita y
una razón escrita. Los umbrales del criterio de suficiencia se fijan sobre validación.

### Fases del agente y su instrumentación

El agente se desarrolla en cuatro fases que recorren el camino de un caso por el sistema. Cada
una recibe lo que la anterior produjo y deja escrito un artefacto que la siguiente consume, de
modo que la cadena entre el dato observado y la decisión final queda reconstruible en cualquier
punto.

#### Fase 4.1 · Recuperación de evidencia (E11, E12)

| | |
|---|---|
| **Entrada** | ventana de telemetría OBD-II ya clasificada, ficha del vehículo y corpus documental de taller en la variante de corpus que la condición experimental determine |
| **Proceso** | consulta al índice vectorial acotada por vehículo, por motor aplicable y por los códigos de avería que documentan la condición diagnosticada; ordenación por autoridad documental; conservación de la procedencia de cada fragmento hasta su fichero de origen |
| **Salida** | conjunto de fragmentos recuperados, cada uno con su identificador, su documento, su sección y su puntuación |
| **Artefactos** | `experiments/E12_retrieval.json`, índice `rag.document_chunk` con procedencia por fragmento |
| **Métrica** | M2, recuperación: acierto en los diez primeros, rango recíproco medio y ganancia acumulada descontada, **reportados por condición** y no en agregado |
| **Criterio de aceptación** | **Ninguno de los dos sentidos es refutable.** Encontrar el documento correcto está garantizado por construcción, porque la búsqueda se acota por los códigos que documentan la condición diagnosticada. Y que desaparezca al retirarlo también: la consulta se acota por el mismo código que la variante excluye, así que el conjunto recuperado sale vacío por definición. Lo que la fase comprueba es que **la manipulación del corpus llega al sistema**, no que el sistema discrimine |
| **Responde a** | PI.2 |

#### Fase 4.2 · Construcción de la explicación (E13; E14 pendiente)

| | |
|---|---|
| **Entrada** | atribución de descriptores del modelo especializado, su confianza calibrada y los fragmentos de la fase anterior |
| **Proceso** | construcción de una afirmación por descriptor observado, anclada a la vez en la observación y en el fragmento documental que la sostiene; el modelo de lenguaje **redacta**, no decide: recibe el paquete de evidencia ya montado y el veredicto ya emitido |
| **Salida** | conjunto de afirmaciones, cada una con su observación de origen y sus citas documentales |
| **Artefactos** | `experiments/E13_agente_*.json` para cada configuración de redactor |
| **Métrica** | M3, explicación: adecuación al esquema de salida y tasa de salidas válidas. **descriptiva, sin responder a ninguna subpregunta** |
| **Criterio de aceptación** | que la salida se ajuste al esquema y que ninguna afirmación cite un fragmento ausente del paquete recibido |
| **Responde a** | **ninguna subpregunta**. La fase es condición necesaria de PI.2 —sin afirmaciones ancladas no hay nada que rastrear— pero no la mide |

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
| **Proceso** | aplicación de un criterio de suficiencia independiente del modelo de lenguaje, con umbrales declarados sobre validación. La palabra «calibrado» solo puede aplicarse a **uno** de los seis: el de confianza. El que de hecho decide la mayoría de las abstenciones es el de cobertura de afirmaciones, fijado en 0,8 **sin barrido**, y dispara trece de las catorce abstenciones registradas, ocho de ellas como motivo único. El registro del barrido declara además que **no fue un pre-registro ciego**: el criterio se fijó tras ver una tabla previa, y el punto de operación pasó de 0,72 a 0,79 mediante una enmienda posterior al primer barrido, fechada y publicada junto al resultado original |
| **Salida** | decisión **EXPLICA** o **ABSTIENE**, con los motivos concretos de la abstención cuando la haya |
| **Artefactos** | `experiments/E15_suficiencia.json`, campo `verdict`, **corrida oracular**; barrido del umbral en `E15b_barrido_umbral.json` |
| **Métrica** | M5, abstención: abstención correcta, abstención injustificada y explicación sin fundamento, **siempre con su cobertura** |
| **Criterio de aceptación** | que la decisión cambie al manipular la evidencia disponible manteniendo constantes los datos, el modelo, la atribución y la confianza |
| **Responde a** | PI.3 y PI.4 |

Un matiz que la métrica sola no revela: de las catorce abstenciones registradas, **trece se
disparan por cobertura de afirmaciones insuficiente** y ocho tienen ese motivo como único. La
decisión de abstenerse, en la práctica, la toma casi siempre ese umbral y no el conjunto de las
cuatro condiciones del criterio. Atribuir la abstención al criterio completo sería atribuirle
más de lo que hace.

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
| M2, recuperación | 6 casos anotados | **5 ventanas**: dos de esos casos son la misma ventana con y sin evidencia |
| M3, explicación | 9 ejecuciones | **5 ventanas**: una de ellas se repite cinco veces bajo distintas variantes de corpus |
| M4 y M5, trazabilidad y abstención | 17 filas | **5 ventanas** |

Las diecisiete filas del experimento de suficiencia proceden de cinco ventanas de telemetría
evaluadas bajo varias variantes de corpus. Tratarlas como diecisiete observaciones
independientes sería pseudorreplicación: la unidad de independencia es la ventana, y las
variantes de una misma ventana comparten datos, atribución y confianza.

#### Estado de las métricas de OE4

La distinción entre definir, implementar, medir y validar evita que una métrica se dé por
obtenida porque esté descrita.

| Métrica | Definida | Implementada | Calculada | Resultado definitivo |
|---|---|---|---|---|
| M2, recuperación | sí | sí | sí, sobre datos sintéticos | **no**: la ejecución vigente está bajo reejecución canónica |
| M3, explicación | sí | sí | sí, sobre datos sintéticos | descriptiva; no valida ninguna subpregunta |
| M4, trazabilidad | sí | sí | **no**: el registro guarda las comprobaciones de soporte en crudo, pero las magnitudes agregadas —corrección de citas, completitud, tasa de soporte— no se han calculado ni escrito en ningún artefacto | no |
| M5, abstención | sí | sí | sí, sobre datos sintéticos | **no**: misma dependencia |

M6, rendimiento, pertenece al quinto objetivo específico y no a este.

Los resultados obtenidos con estas métricas no se consideran todavía definitivos, y son **dos**
las razones, no una:
la recuperación que las alimentó está bajo reejecución canónica, y la condición con distractor
está bajo diagnóstico porque su manipulación no se ha comprobado. Las magnitudes ya medidas son reproducibles desde sus registros y
se conservan; lo que está en revisión es si la recuperación que las alimentó aislaba
correctamente el espacio vectorial en que buscaba.


### Ablaciones

Cada ablación cambia exactamente un factor: sin atribución, sin recuperación semántica, sin
criterio de suficiencia, con un único umbral en lugar del criterio compuesto. Sirven para
saber qué parte del resultado aporta cada pieza. `[Pendiente: E18.]`

### Reproducibilidad y trazabilidad experimental

Toda ejecución registra identificador de experimento, versión del dataset, versión del
corpus, modelo de embeddings, proveedor y modelo de lenguaje, versión del prompt, semilla,
parámetros y métricas, en JSON y CSV. El entorno se fija con un gestor de dependencias con
fichero de bloqueo; las puertas de calidad, análisis estático, tipado estricto y una batería
de 400 tests, se ejecutan tras cada cambio.

Los artefactos de software, las configuraciones y los registros experimentales se mantienen
bajo control de versiones, de modo que cada ejecución pueda relacionarse con la configuración,
las semillas, las versiones de los componentes y los datos utilizados. La documentación técnica
empleada como corpus se identifica mediante metadatos y huellas criptográficas, dado que sus
condiciones de distribución impiden incorporarla directamente al repositorio. Este mecanismo
permite comprobar que las ejecuciones reproducidas utilizan la misma versión documental sin
redistribuir material sujeto a restricciones de uso.

La identificación del commit y de las versiones documentales en la cabecera de los registros
está implantada solo en parte, y completarla es condición para dar por cerrada la fase de
evaluación final.

## Modelo de análisis de datos

El análisis es comparativo y por caso, no inferencial en el sentido clásico: con nueve casos
anotados, una diferencia de una unidad no separa nada, y lo que se compara es la estructura
del comportamiento bajo condiciones diseñadas para diferir.

Para PI.1 se comparan exactitud y F1 macro del modelo frente a la referencia mínima de la
clase mayoritaria, y el error de calibración antes y después de corregir. Para PI.2 se
calcula, para cada afirmación admitida, si su observación existe, si su fragmento existe, si
el fragmento aplica al vehículo y si sostiene lo afirmado; el resultado es la tasa de
soporte y su distancia a la completitud. Para PI.3 se tabula la decisión del agente por
condición de corpus, manteniendo fija la confianza, y se comprueba que cambia entre FULL y
ABSENT; la abstención se acompaña siempre de su cobertura. Para PI.4 se cuentan los
distractores que superan al fragmento correcto en la recuperación semántica pura, con el
filtro de motor y sin él, y qué grado de aplicabilidad les asigna el validador.

Para el modelo de lenguaje se comparan, con el mismo motor de inferencia y las mismas nueve
preguntas, tres configuraciones: el modelo base, el modelo con el primer adaptador y el
modelo con el segundo. Las variables son salidas válidas, respeto del veredicto, citas
inexistentes y fallos de esquema; el criterio de éxito del ajuste se fijó antes de la
segunda medición y exige que el ajustado no sea peor que el base en ninguna de las dos
últimas.

Toda cifra se acompaña de la partición de la que procede y del registro que la produjo.
Cuando un resultado contradice una expectativa escrita, se publica la expectativa, el
resultado y la explicación, y no se ajusta la expectativa.
