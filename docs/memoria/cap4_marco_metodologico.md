# Capítulo 4: Marco Metodológico
El trabajo sigue el ciclo de la investigación en ciencias del diseño (Peffers et al., 2007, MET-16; Hevner et al., 2004, MET-17): identifica un problema, fija los objetivos de una solución, construye un artefacto, lo demuestra sobre casos, lo evalúa con criterios fijados de antemano y comunica el resultado. La elección no es de conveniencia. La pregunta de investigación no puede responderse observando sistemas existentes, porque ninguno de los revisados separa la decisión de explicar de la redacción de la explicación; hay que construir uno que lo haga y medir su comportamiento; atribuir ese comportamiento a la separación misma exige, además, las ablaciones que el diseño prevé. El artefacto es el instrumento, no la contribución: la contribución es la evidencia experimental sobre su comportamiento bajo condiciones controladas de evidencia.

Dos compromisos de método atraviesan todo el capítulo. El primero es que **el criterio de éxito de cada experimento se escribe antes de ejecutarlo**, y cuando se modifica después de ver un resultado la modificación se registra como enmienda, con su fecha y su motivo, junto al criterio original; los resultados negativos se publican con el mismo detalle que los positivos. Ese compromiso no se cumplió siempre, y los tres casos en que un criterio cambió tras ver resultados —las subpreguntas, el umbral de confianza y el criterio de suficiencia— se declaran donde aparecen. El segundo es que **toda cifra publicada procede de un registro de ejecución**, con su semilla, versiones de datos, corpus, modelo y prompt; los registros posteriores al 4 de septiembre de 2026 incluyen además la versión del código, y los anteriores no. Lo que no se ha ejecutado se declara como no ejecutado.

Todas las cifras de este capítulo proceden de registros de ejecución versionados o de la ficha de calibración del vehículo, y el diseño que describe se ejecutó sobre datos sintéticos. De las veinte fases planificadas se han ejecutado y registrado las de entorno y datos, las del modelo de diagnóstico salvo su evaluación sobre el conjunto de prueba, las de corpus y recuperación y las del agente y la suficiencia; la recuperación y la suficiencia se reejecutaron el 13 y el 14 de septiembre de 2026 tras corregir un defecto del índice documental, con un procedimiento fijado antes de medir. Quedan pendientes la validación externa con telemetría de vehículos reales, las ablaciones, la evaluación final sobre el conjunto de prueba y la demostración integrada.

## Población y muestra
Se describen, por este orden, la población a la que se pretende generalizar, la muestra de telemetría con su procedencia, la muestra documental que constituye el corpus y los casos de referencia sobre los que se evalúa el agente.

### Población
La población de referencia es el conjunto de ventanas de telemetría OBD-II de un vehículo de combustión con puerto normalizado, en condiciones de conducción ordinarias, con y sin fallo en los sistemas de admisión, combustible, encendido, refrigeración y emisiones.

La configuración mecánica de referencia del entorno experimental es un Mazda 3 de la generación BK, año 2007, con motor de gasolina de 1,6 litros código Z6 y transmisión manual. Se seleccionó entre tres candidatos —Mazda 3, Honda Civic y Toyota Corolla del rango 2000-2016— por dos razones metodológicas. La primera es la disponibilidad del manual de taller completo, sin la cual no habría corpus documental sobre el que recuperar ni contra el que verificar. La segunda es que sus procedimientos de diagnóstico son específicos del motor, lo que permite construir la condición con distractor con documentación auténtica del fabricante correspondiente a otro motor de la misma gama, en lugar de con un texto artificialmente irrelevante.

Esa configuración tiene un estatuto que conviene no confundir. El código de motor, la cilindrada y la transmisión son un **supuesto de trabajo del generador sintético**, no una lectura tomada de un vehículo físico: la telemetría de esta memoria no procede de un Mazda 3 real. El supuesto se justifica porque los códigos de avería que el experimento utiliza están documentados en el manual para los motores Z6 y ZJ, de modo que la telemetría generada y la documentación consultada se refieren a la misma configuración mecánica. Si se incorpora telemetría real como validación externa, esos tres valores deberán tomarse del vehículo del que proceda, y la correspondencia con el corpus dejará de estar garantizada por construcción para convertirse en una comprobación previa.

Conviene distinguir los niveles de agregación, porque el diseño los usa para cosas distintas y confundirlos produciría pseudorreplicación. La **unidad de análisis** del modelo de diagnóstico es la ventana de telemetría; las ventanas proceden de **sesiones** de conducción, y las de una misma sesión no son independientes entre sí, de modo que el reparto entre entrenamiento, validación y test se hace por sesión y no por ventana. La **unidad de análisis del agente** no es la ventana sino el **caso**: un diagnóstico concreto evaluado bajo una condición de evidencia concreta. El número de filas de una tabla de resultados no equivale, por tanto, al número de observaciones independientes que la sostienen; la Tabla 4.13 recoge, para cada métrica, la unidad de análisis, la de independencia y ambos recuentos.

Esta elección, recogida en la Tabla 4.1, encadena el resto del entorno experimental. De ella dependen la calibración del generador, cuyas constantes proceden de páginas concretas del manual y conservan su cita; el corpus sobre el que recupera el agente; los códigos de avería que documentan cada condición de fallo; los procedimientos que el verificador exige como soporte; y la construcción de la condición con distractor, que emplea el procedimiento del motor LF para el mismo código de avería.

No dependen de ella, en cambio, la arquitectura del agente, la política de suficiencia ni los criterios de verificación: ninguna de sus reglas nombra un motor, un código ni una señal concretos.

**Tabla 4.1. Caracterización del vehículo de referencia y del corpus documental asociado.**

|  |  |
| --- | --- |
| Vehículo | Mazda 3 |
| Generación | BK |
| Año de referencia | 2007 |
| Motor del experimento | Z6, gasolina de 1,6 litros |
| Transmisión | manual |
| Corpus documental | manual de taller del fabricante para la generación BK, 1 documento estructurado en 6 158 fragmentos indexados |
| Motores documentados en el corpus | LF de 2,0 litros con 507 ficheros, Z6 de 1,6 con 486 y ZJ de 1,4 con 486, más 90 comunes a los tres |

*Fuente: elaboración propia.*

El alcance de los resultados queda acotado por esta elección. Describen el comportamiento del sistema sobre un vehículo, una generación y un corpus documental. La coherencia entre telemetría, documentación y códigos de avería que aquí queda garantizada por construcción es precisamente lo que no puede darse por supuesto en otro vehículo, donde el fabricante puede emplear códigos genéricos distintos, estructurar los procedimientos de otra forma o no publicar un manual accesible. La generalización a otros modelos o a otras generaciones del mismo modelo no se sigue de estos resultados, y se recoge entre las amenazas a la validez del capítulo 6.

### Muestra: telemetría
La base experimental utilizada en este trabajo está constituida por telemetría OBD-II sintética, generada mediante un modelo paramétrico determinista con semilla fija. La procedencia de los datos se conserva explícitamente durante el proceso experimental y se mantiene diferenciada de cualquier fuente real, simulada o procedente de conjuntos públicos. La incorporación de telemetría obtenida de vehículos reales se plantea como una etapa posterior de validación externa.

El generador produce sesiones correspondientes a tres regímenes de funcionamiento —ralentí, conducción urbana y carretera— y seis condiciones experimentales: funcionamiento sin fallo y cinco condiciones de fallo asociadas a los sistemas considerados. Cada condición modifica una o varias señales siguiendo un mecanismo previamente definido. Por ejemplo, una fuga de vacío modifica las correcciones de combustible a corto y largo plazo, mientras que un termostato bloqueado en posición abierta altera la evolución de la temperatura del refrigerante.

Las constantes empleadas por el generador se parametrizan a partir de especificaciones documentadas en el manual de taller del vehículo de referencia. Entre ellas se encuentran el régimen de ralentí, la temperatura de apertura del termostato, los rangos de tensión de la sonda de oxígeno y los límites de corrección de combustible asociados a determinados códigos de avería. La procedencia documental de estos valores se conserva en la ficha de calibración utilizada para construir el conjunto experimental. Las principales características de la muestra resultante se presentan en la Tabla 4.2.

**Tabla 4.2. Características de la muestra sintética de telemetría OBD-II.**

| Característica | Descripción |
| --- | --- |
| Procedencia | telemetría sintética |
| Regímenes de funcionamiento | ralentí, conducción urbana y carretera |
| Condiciones experimentales | 6: funcionamiento sin fallo y cinco condiciones de fallo |
| Número de sesiones | 72; 12 por condición |
| Duración por sesión | 600 s |
| Frecuencia de muestreo | 1 Hz |
| Número total de muestras | 43 200 |
| Señales OBD-II | 12 |
| Longitud de ventana | 120 s, con desplazamiento de 60 s (solape del 50 %) |
| Descriptores por ventana | 139 |
| Partición de los datos | por sesión, separando entrenamiento, validación y prueba |
| Ventanas de entrenamiento | 392, sobre 48 sesiones |
| Ventanas de validación | 98, sobre 12 sesiones |
| Ventanas de prueba | 98, sobre 12 sesiones; reservadas para la evaluación final |
| Semilla de generación | 20260901 |

*Fuente: elaboración propia.*

Las ventanas que cruzan la entrada de un fallo se descartan, por lo que el reparto anterior no agota la totalidad de las ventanas construidas. El conjunto de prueba permanece cerrado por diseño hasta la fase de evaluación final: su tamaño forma parte del diseño experimental, pero ninguna cifra de esta memoria se ha obtenido sobre él.

La muestra contiene doce señales OBD-II relacionadas con el estado operativo del motor, la admisión, la combustión y el control de emisiones. La Tabla 4.3 recoge cada señal con su unidad y el rango físico dentro del cual el generador la mantiene; su función dentro del entorno experimental se desarrolla en el apartado de variables e instrumentos.

**Tabla 4.3. Señales OBD-II utilizadas en el entorno experimental.**

| Señal | Unidad | Rango físico admitido |
| --- | --- | --- |
| Régimen de giro del motor | rpm | 0 a 8 000 |
| Velocidad del vehículo | km/h | 0 a 250 |
| Carga calculada del motor | % | 0 a 100 |
| Posición de la mariposa | % | 0 a 100 |
| Temperatura del refrigerante | °C | −40 a 150 |
| Temperatura del aire de admisión | °C | −40 a 120 |
| Caudal másico de aire | g/s | 0 a 300 |
| Presión absoluta en el colector de admisión | kPa | 0 a 255 |
| Ajuste de combustible a corto plazo, banco 1 | % | −100 a 100 |
| Ajuste de combustible a largo plazo, banco 1 | % | −100 a 100 |
| Tensión de la sonda lambda anterior al catalizador | V | 0 a 1,275 |
| Avance del encendido | ° antes del PMS | −64 a 64 |

*Fuente: elaboración propia a partir de la especificación de señales del entorno experimental.*

Esta construcción permite controlar qué mecanismos de fallo están representados, en qué régimen aparecen y con qué intensidad, y repetir cualquier experimento sobre exactamente los mismos datos: la semilla, la versión del generador y la ficha de calibración quedan fijadas en el registro de cada ejecución. Lo que no permite es establecer, por sí sola, que el comportamiento observado se reproduzca sobre telemetría de un vehículo en operación.

La longitud de la ventana de análisis no se fijó por convención. Se evaluaron cuatro longitudes —10, 30, 60 y 120 segundos—, midiendo para cada fallo la separabilidad de sus descriptores respecto de la condición sin fallo, en nivel y en dispersión, mediante el delta de Cliff. Como seleccionar el mayor de 139 descriptores infla el máximo por el propio número de comparaciones, cada valor se contrastó contra una referencia nula construida con el mismo estadístico sobre la condición sin fallo partida en dos mitades por sesión, en treinta repeticiones, de la que se toma el percentil 90. El criterio de selección fue doble: que el tamaño de efecto del mejor descriptor superase esa referencia, y que el descriptor separable coincidiese con el mecanismo físico declarado del fallo. La configuración adoptada es de **120 segundos con solape**. Los valores obtenidos en esa comparación se presentan en el capítulo 5.

**Alcance de la muestra.** Los resultados obtenidos sobre esta muestra no permiten establecer por sí solos su generalización a telemetría real. El generador reproduce los mecanismos que la documentación permite parametrizar y no incorpora la variabilidad entre conductores, el desgaste de los componentes, las condiciones ambientales, el ruido propio de los sensores, la interacción entre fallos simultáneos ni los fenómenos que no forman parte de su modelo. Cada una de esas ausencias es una amenaza a la validez externa, y el capítulo 6 las desarrolla. Todo resultado obtenido sobre esta muestra se presenta con su procedencia declarada y acotado a ella.

### Muestra: corpus documental
El corpus es el manual de taller del vehículo, en su copia local del autor, procedente de un repositorio secundario en la web. No se redistribuye; se registra su huella SHA-256 para que un tercero que disponga del mismo documento pueda comprobar la identidad. Está compuesto por ficheros por procedimiento, cada uno con los códigos de motor a los que aplica; la Tabla 4.4 resume su composición.

**Tabla 4.4. Composición del corpus documental del vehículo de referencia.**

| Corpus | Valor |
| --- | --- |
| Ficheros del manual con aplicabilidad al motor LF | 507 |
| Ficheros con aplicabilidad a los motores ZJ y Z6 | 486 |
| Ficheros comunes a los tres motores | 90 |
| Fragmentos indexados | 6 158, todos en inglés |
| Modelos de embeddings indexados | dos: uno monolingüe en inglés y otro multilingüe, ambos sobre los 6 158 fragmentos, para medir el efecto del idioma de la consulta |
| Idioma de las consultas | cada caso anotado lleva la consulta en español y en inglés; las mediciones de recuperación y suficiencia vigentes usan la inglesa |

*Fuente: elaboración propia.*

El manual no se traduce. El trabajo se escribe en español y la documentación está en inglés, que es la situación normal de un taller en España con un vehículo de fabricante extranjero. Una medición descriptiva, recogida en el capítulo 5, indica que la recuperación translingüe no funciona sola con un modelo de embeddings monolingüe; las mediciones vigentes de recuperación y suficiencia se hicieron con la consulta en inglés.

Cada fragmento conserva su procedencia completa: documento, versión, sección, página, códigos de avería que contiene, sistema del vehículo y motores a los que aplica. Esa metadata es lo que permite construir las variantes del corpus del diseño experimental retirando o dejando fragmentos por código de avería o por fichero, sin tocar nada más.

### Casos de referencia
La evaluación del agente se hace sobre un conjunto anotado de diecisiete casos, construidos a partir de ventanas de validación correctamente clasificadas: cinco con evidencia completa, uno por condición de fallo, y doce que cruzan tres de esos fallos con las condiciones de evidencia ausente, parcial y con distractor, esta última con y sin filtro de motor. Una primera versión del conjunto tenía nueve casos, sobre un solo fallo para las condiciones distintas de la completa. La ampliación a tres fallos se hizo el 4 de septiembre de 2026, después de las mediciones sobre nueve casos y antes de la medición vigente; la deriva del caudalímetro y el fallo de encendido no se ampliaron porque sus casos con evidencia completa ya se abstenían por confianza del modelo, y retirarles la evidencia no habría medido nada. Las anotaciones y las consultas se redactaron conociendo el fallo de cada caso. Cada caso lleva anotado el diagnóstico esperado, la consulta en los dos idiomas, los ficheros del manual que constituyen evidencia relevante, los de apoyo, los distractores, qué se retira del índice y la acción esperada, explicar o abstenerse. La anotación prevista en el diseño incluye además las señales y ventanas relevantes, los fragmentos a nivel de unidad documental, las afirmaciones admisibles y la evidencia mínima exigible a cada una; esos cuatro campos no están anotados todavía, de modo que las magnitudes que dependen de ellos no pueden calcularse sobre el conjunto actual.

El conjunto de test de la telemetría **permanece cerrado** hasta la evaluación final. Los umbrales del criterio de suficiencia se fijaron únicamente sobre validación.

## Objetivos de investigación
La Tabla 4.5 lleva la correspondencia del capítulo 2 hasta las fases, las métricas y el estado de ejecución de cada objetivo. Declara también dónde el diseño todavía no alcanza al objetivo que dice desarrollar.

**Tabla 4.5. Correspondencia entre objetivos, fases experimentales, métricas y estado de ejecución.**

| Objetivo | Fases | Métricas | Estado a 14 de septiembre de 2026 |
| --- | --- | --- | --- |
| OE1 | revisión documental | — | realizada; el procedimiento se declara inspirado en PRISMA y no como flujo PRISMA formal |
| OE2 | E1, E2, E4, E5, E10, E11 | — | ejecutadas sobre telemetría sintética; la validación externa con datos reales (E3) queda fuera de esta versión |
| OE3 | E5, E6, E7, E9 | M1; para la atribución, concordancia descriptiva entre las señales atribuidas y las declaradas para cada fallo | ejecutadas sobre la partición de validación; la evaluación sobre el conjunto de prueba (E8) corresponde a la evaluación final |
| OE4 | E11, E12, E13, E15 (E14 y E16 quedan integradas en E15) | M2, M3, M4, M5 | calculadas sobre validación y reejecutadas con recuperación canónica el 13 y 14 de septiembre; resultados parciales |
| OE5 | E15 y E17 (condiciones de evidencia), E18, E19, E20 | M5 con sus dos tipos de error, M6 | condiciones completa, parcial y ausente evaluadas; la condición con distractor, diagnosticada; ablaciones (E18), evaluación final (E19) y demostración (E20) pendientes |

*Fuente: elaboración propia.*

Los objetivos del capítulo 2 se operacionalizan en cuatro subpreguntas, cada una con un desenlace que la sostendría y otro que la refutaría, recogidos en la Tabla 4.6.

**Tabla 4.6. Subpreguntas de investigación con sus desenlaces de sostenimiento y refutación.**

| Subpregunta | Qué pregunta | Sostenida si | Refutada si |
| --- | --- | --- | --- |
| PI.1 | ¿Diagnostica a partir de la telemetría? | supera a la clase mayoritaria con margen amplio y su confianza está calibrada | no supera a la referencia mínima, o la confianza no significa lo que aparenta |
| PI.2 | ¿La explicación es trazable? | toda afirmación admitida se ancla en una observación y un documento verificados | las referencias existen pero no sostienen lo afirmado |
| PI.3 | ¿Reconoce la insuficiencia? | la decisión cambia al retirar la evidencia, con todo lo demás idéntico | explica igual con y sin evidencia, o se abstiene siempre |
| PI.4 | ¿Rechaza evidencia engañosa? | el procedimiento de otro motor no se acepta como soporte | acepta distractores como evidencia |

*Fuente: elaboración propia.*

Esta tabla no es la formulación original. Los criterios se escribieron por primera vez el 1 de septiembre de 2026, antes de entrenar ningún modelo, y eran más exigentes en dos puntos: PI.1 pedía que un modelo temporal superase a la línea base con un margen no atribuible al azar, y PI.2 y PI.3 fijaban sus criterios sobre umbrales numéricos de las métricas de trazabilidad y abstención que debían fijarse al cerrar la fase de suficiencia y que nunca llegaron a fijarse. Esa misma tarde, con la línea base, el modelo temporal, la evaluación de la recuperación y una primera versión de la suficiencia ya ejecutados, las cuatro subpreguntas se reescribieron en su forma actual. La formulación original de PI.1 no se cumplió, y la de PI.2 y PI.3 no llegó a ser evaluable; el capítulo 5 lo recoge.

La respuesta global a la pregunta admite tres valores con una regla fijada en aquella primera versión: sostenida, si las cuatro subpreguntas cumplen su criterio; parcialmente sostenida, si PI.1 y PI.2 se cumplen y PI.3 o PI.4 no; y no sostenida, si PI.2 o PI.3 no se cumplen. Cinco desenlaces la refutarían, enumerados también entonces: que el agente explique con la misma soltura con y sin evidencia; que se abstenga también con evidencia completa y la abstención resulte trivial; que acepte distractores; que las referencias existan pero no sostengan lo que se afirma con ellas; y que el modelo de diagnóstico no supere a la línea base.

## Variables intervinientes e instrumentos de evaluación
El apartado declara la única variable manipulada, las que se mantienen controladas, las seis familias de variables medidas y los instrumentos con que se miden.

### Variable manipulada
**Qué evidencia documental está disponible en el corpus**. Toma los cuatro valores que define la Tabla 4.7. La condición con distractor se evalúa además con el filtro de motor desactivado, de modo que en esa variante cambia también un parámetro de la recuperación; se declara como segunda variable y sus casos se leen por separado.

**Tabla 4.7. Condiciones experimentales de disponibilidad y pertinencia de la evidencia documental.**

| Condición | Corpus | Comportamiento esperado |
| --- | --- | --- |
| FULL | contiene la evidencia correcta | EXPLAIN, con cada afirmación trazada |
| PARTIAL | evidencia incompleta | ABSTAIN, salvo explicación limitada declarada como tal |
| ABSENT | la evidencia relevante ha sido retirada del índice | ABSTAIN |
| DISTRACTOR | contiene evidencia parecida pero incorrecta | rechazo del distractor; ABSTAIN si no queda otra |

*Fuente: elaboración propia.*

Las variantes se construyen sobre el mismo índice, excluyendo fragmentos por código de avería o por fichero en el momento de la consulta. La condición PARTIAL retira los ficheros de procedimiento diagnóstico del fallo y deja las tablas de códigos y la lógica de detección: el corpus sigue diciendo que el código existe y qué lo dispara, pero no cómo se diagnostica. Que eso sea insuficiente depende de una regla del verificador, que no admite una tabla de códigos como soporte por sí sola, y esa regla se fijó en la tercera versión del criterio sobre los mismos casos; la condición parcial pone a prueba, por tanto, esa regla tanto como la presencia de documentación. La condición PARTIAL retira los ficheros de procedimiento diagnóstico del fallo y deja las tablas de códigos y la lógica de detección: el corpus sigue diciendo que el código existe y qué lo dispara, pero no cómo se diagnostica. Que eso sea insuficiente depende de una regla del verificador, que no admite una tabla de códigos como soporte por sí sola, y esa regla se fijó en la tercera versión del criterio sobre los mismos casos; la condición parcial pone a prueba, por tanto, esa regla tanto como la presencia de documentación. La condición ABSENT retira todos los fragmentos que portan los códigos de avería de la condición, no solo los del procedimiento principal; una primera versión que retiraba solo estos últimos dejaba evidencia en las tablas de códigos y produjo un falso positivo del experimento central, detectado y corregido.

### Variables controladas
Los datos de telemetría, el modelo de diagnóstico, la atribución, la confianza calibrada, la consulta, el proveedor de lenguaje y sus parámetros, la semilla y la versión del prompt se mantienen idénticos entre condiciones. Es esa constancia lo que permite atribuir un cambio de comportamiento del agente a la disponibilidad de evidencia y no a otra cosa.

### Variables medidas
Se agrupan en seis familias. No todas se calculan en cada experimento; se reporta la que corresponde y se dice cuál.

**M1, diagnóstico.** Exactitud, F1 macro y calibración del modelo especializado. La calibración se mide con el error esperado de calibración (Naeini, Cooper y Hauskrecht, 2015, MET-07) y se corrige con regresión isotónica (Zadrozny y Elkan, 2002, MET-05; Niculescu-Mizil y Caruana, 2005, MET-06) ajustada por validación cruzada sobre entrenamiento, para no gastar la validación en dos cosas.

**M2, recuperación.** Tasa de acierto entre los diez primeros resultados (Hit@10), rango recíproco medio (MRR) y ganancia acumulada descontada normalizada (nDCG) sobre el conjunto anotado, por estrategia de recuperación. Solo se puntúan los casos con fichero relevante, que en el conjunto actual son todos de evidencia completa; en las demás condiciones la recuperación se describe por el número de documentos aplicables que llegan al verificador.

**M3, explicación.** Adecuación al esquema de salida y tasa de salidas válidas. Es descriptiva y no responde a ninguna subpregunta; se declara como tal.

**M4, trazabilidad.** Corrección de las citas (existen y resuelven), completitud (proporción de afirmaciones con cita), tasa de soporte (proporción de afirmaciones cuya cita sostiene lo afirmado) y su complemento. La distancia entre completitud y soporte mediría cuántas afirmaciones llevan una referencia que no las respalda, el fallo más difícil de ver porque el texto parece bien citado. En esta implementación esa distancia es nula por construcción para las afirmaciones del verificador, que solo cita un fragmento cuando ya superó sus comprobaciones; medirla de forma independiente exige anotar las afirmaciones admisibles y la evidencia mínima de cada caso, y sobre la redacción del modelo de lenguaje se mide como la proporción de afirmaciones que citan algún fragmento no aceptado por el verificador.

**M5, abstención.** Abstención correcta, abstención innecesaria y explicación sin fundamento, siempre acompañadas de la cobertura, porque corrección y cobertura solo significan algo juntas. Los dos errores posibles se cuentan por separado y no se agregan en una sola tasa de acierto, porque no son intercambiables. La **falsa confianza** es explicar un caso en el que la evidencia no bastaba y el sistema debía abstenerse; se mide como la proporción de casos que debían terminar en abstención y terminaron en explicación:

T_FC = N(explica cuando debía abstenerse) / N(casos que debían abstenerse)

La **abstención innecesaria** es callar teniendo evidencia suficiente; se mide como la proporción de casos que debían terminar en explicación y terminaron en abstención:

T_AI = N(se abstiene cuando debía explicar) / N(casos que debían explicar)

La primera compromete a quien actúa sobre el vehículo; la segunda solo cuesta cobertura. Un sistema que se abstuviera siempre tendría falsa confianza nula y sería inútil; uno que explicara siempre tendría cobertura total y sería inseguro. Las dos tasas se publican juntas, con el número de ejecuciones y el de ventanas independientes, junto a las mismas tasas para dos políticas de referencia —abstenerse siempre y explicar siempre que el modelo confía—, y no se combinan en una sola cifra.

**M6, rendimiento.** Latencia por etapa y extremo a extremo, tamaño del modelo y coste de la recuperación, con el dispositivo real de cada etapa. Se reporta como **métrica descriptiva** y no como criterio de aceptación: el trabajo no fija un presupuesto de latencia, porque el despliegue embarcado que lo habría justificado queda fuera del alcance de este trabajo.

### Instrumentos
Todos los instrumentos son código versionado con tests, y ninguna métrica que responda a una subpregunta depende de un juicio humano ni de un modelo de lenguaje.

El **modelo de diagnóstico** es un bosque aleatorio (Breiman, 2001, MET-01) sobre los 139 descriptores de ventana, con pesos de clase, elegido como baseline por su robustez con pocos datos; se contrastó con una red recurrente bidireccional de unidades GRU (Cho et al., 2014, MET-02) sobre las secuencias crudas, que no lo superó en este volumen de datos. La **atribución** usa valores de Shapley (Lundberg y Lee, 2017, MET-03) en su variante por permutación, con un fondo de referencia de ventanas sin fallo y semilla fija, y produce para cada caso las señales, estadísticos, valores, dirección y ventana temporal que más contribuyen a la predicción. La memoria no afirma en ningún punto que esa atribución sea causal: indica de qué depende la predicción del modelo, no qué le ocurre al vehículo.

Este instrumento es un clasificador supervisado de conjunto cerrado: asigna cada ventana a una de las clases de fallo etiquetadas durante el entrenamiento, de modo que lo que el diseño puede examinar son patrones pertenecientes a esas clases. La detección de fallos ajenos al catálogo queda fuera del alcance de este trabajo.

El **sistema de recuperación** combina búsqueda semántica con un modelo multilingüe de embeddings de frases (Reimers y Gurevych, 2019, MET-11) sobre una base de datos PostgreSQL con extensión vectorial, búsqueda léxica sobre el texto completo y fusión por rango recíproco (Cormack, Clarke y Buettcher, 2009, MET-12) que conserva las puntuaciones originales; se filtra siempre por vehículo y, cuando procede, por motor. La recuperación guiada por el diagnóstico añade a la consulta los códigos de avería que el manual asocia a la condición predicha. Un **validador de aplicabilidad** asigna a cada fragmento uno de cinco grados respecto del vehículo, coincidencia exacta, compatible, parcial, desconocido o incompatible; en la configuración evaluada solo la coincidencia exacta cuenta como evidencia.

El **verificador de suficiencia** es determinista. Construye una afirmación por observación atribuida, con plantillas que enuncian lo observado sin atribuir causa; para cada una busca fragmentos aplicables que la sostengan, comprobando que el fragmento mencione la señal, tenga contenido diagnóstico y porte un código de avería de la condición; y decide con un criterio conjuntivo sobre la confianza calibrada, el número de fragmentos y fuentes de apoyo, la cobertura de las afirmaciones y la ausencia de contradicciones. La abstención es una salida válida del esquema, con su motivo y la evidencia que falta. El criterio sigue la lógica de la clasificación con opción de rechazo (Chow, 1970, MET-08; Geifman y El-Yaniv, 2017, MET-09): la decisión de no responder es una salida legítima cuya calidad se mide junto con su cobertura.

El **modelo de lenguaje** es Qwen2.5 de 3 000 millones de parámetros (Qwen Team, 2024, MET-14), ejecutado localmente sin clave ni red tras la descarga. Recibe el diagnóstico, la confianza, la decisión del verificador con sus motivos, las observaciones de la telemetría y los fragmentos con coincidencia exacta de aplicabilidad, y redacta la salida en un esquema fijo; una barrera externa rechaza cualquier cita que no corresponda a algo entregado. No recibe las afirmaciones que el verificador construyó, de modo que puede citar fragmentos aplicables que este no aceptó como soporte. Se ajustó con adaptadores de rango bajo (Hu et al., 2022, MET-13) sobre las proyecciones de atención, con ejemplos derivados de ejecuciones auténticas del propio pipeline sobre ventanas de validación, con la pérdida calculada solo sobre la respuesta y con una comprobación automática de que ningún fragmento del manual aparece en las salidas de entrenamiento. El ajuste enseña el formato de la tarea y no el contenido del vehículo: si el modelo memorizara el manual, en la condición ABSENT lo recordaría de sus pesos y el experimento mediría memoria en lugar de evidencia.

## Diseño experimental
El plan tiene veinte fases, cada una con su informe, su criterio de aceptación y las comprobaciones automatizadas de calidad del código que la acompañan. Se agrupan en los cinco bloques de la Tabla 4.8.

**Tabla 4.8. Agrupación en bloques de las veinte fases del plan experimental.**

| Bloque | Fases | Qué producen |
| --- | --- | --- |
| Entorno y datos | E1–E5 | auditoría del entorno, datos sintéticos calibrados, análisis exploratorio, ventana y reparto sin fuga |
| Modelo de diagnóstico | E6–E9 | baseline, modelo temporal, evaluación, atribución |
| Corpus y recuperación | E10–E12 | corpus del vehículo, ingesta, evaluación de la recuperación |
| Agente y suficiencia | E13–E16 | modelo de lenguaje, modelo de evidencia, verificador, abstención |
| Evaluación | E17–E20 | experimento integrado, ablaciones, evaluación final, demostración |

*Fuente: elaboración propia.*

### Experimento central
El experimento parte del mismo caso en dos condiciones. En la primera se conserva la evidencia documental relevante. La telemetría pasa por el modelo de diagnóstico, se obtiene la atribución y se recupera la documentación técnica. Si la evidencia resulta aplicable y suficiente, el sistema explica y mantiene cada afirmación trazada hasta aquello que la sostiene.

En la segunda condición se utilizan los mismos datos, el mismo modelo, la misma atribución y la misma confianza. Solo cambia la evidencia disponible: los fragmentos relevantes se retiran del índice. Si el sistema no encuentra soporte suficiente, debe abstenerse. Esta comparación permite observar el efecto de la evidencia sin modificar el diagnóstico de partida.

Las condiciones PARTIAL y DISTRACTOR amplían el experimento. PARTIAL conserva documentación relacionada con el caso, pero insuficiente para sostener las afirmaciones necesarias. DISTRACTOR introduce documentación parecida que no debería utilizarse como soporte. Con ello se busca distinguir entre encontrar documentos y disponer realmente de evidencia suficiente.

FULL y ABSENT permiten estudiar el efecto de disponer o no de la evidencia relevante. PARTIAL permite observar qué ocurre cuando existe documentación, pero el soporte es incompleto. DISTRACTOR examina un problema diferente: si el sistema puede evitar que documentación aparentemente relacionada termine sosteniendo una afirmación que no le corresponde. Esta última condición se mantiene sujeta a validación experimental antes de atribuir el resultado al mecanismo diseñado.

### Particiones y cierre del test
Entrenamiento, validación y test se separan por sesión, nunca por partición aleatoria de ventanas consecutivas, porque dos ventanas contiguas comparten casi toda su información y repartirlas entre entrenamiento y test convertiría la evaluación en un espejo. El test permanece cerrado hasta la evaluación final y su apertura exige una declaración explícita y una razón escrita. Los umbrales del criterio de suficiencia se fijan sobre validación.

### Fases del agente y su instrumentación
El agente se desarrolla en cuatro fases que recorren el camino de un caso por el sistema. Cada una recibe lo que la anterior produjo y deja escrito un artefacto que la siguiente consume, de modo que la cadena entre el dato observado y la decisión final queda reconstruible en cualquier punto.

#### Fase de recuperación de información documental (E11, E12)
Esta fase proporciona la información documental que posteriormente será evaluada como posible evidencia para contrastar la hipótesis diagnóstica. La recuperación se realiza sobre el corpus técnico asociado al vehículo de referencia y bajo la variante documental definida para cada condición experimental. La Tabla 4.9 resume sus principales elementos.

**Tabla 4.9. Diseño de la fase de recuperación de información documental.**

| Elemento | Descripción |
| --- | --- |
| Entrada | Ventana de telemetría OBD-II previamente analizada, configuración del vehículo y variante del corpus documental correspondiente a la condición experimental. |
| Procedimiento | Recuperación de fragmentos del corpus mediante búsqueda sobre el índice documental, restringiendo la aplicabilidad por vehículo y motor y utilizando la información diagnóstica disponible para orientar la consulta. Se conserva la procedencia de cada fragmento hasta su documento y sección de origen. |
| Salida | Conjunto ordenado de fragmentos documentales con su identificador, documento de procedencia, sección y puntuación de recuperación. |
| Evaluación | La recuperación se caracteriza mediante M2, considerando la tasa de acierto entre los diez primeros resultados, el rango recíproco medio y la ganancia acumulada descontada normalizada, por estrategia y sobre los casos con fichero relevante. En las demás condiciones se describe por el número de fragmentos aplicables que llegan al verificador. |
| Propósito experimental | Comprobar que las modificaciones introducidas en el corpus para cada condición experimental se reflejan efectivamente en la información que alcanza las etapas posteriores del sistema. |
| Trazabilidad | Se conserva la relación entre cada fragmento recuperado y su fuente documental para permitir su posterior evaluación de aplicabilidad y soporte. |

*Fuente: elaboración propia.*

La interpretación de esta fase requiere considerar una característica del diseño experimental. La consulta utiliza información diagnóstica para restringir la recuperación y, por tanto, la presencia o ausencia de determinados documentos está parcialmente controlada por la construcción de cada condición. En consecuencia, esta fase no pretende demostrar por sí sola la capacidad del recuperador para discriminar entre documentación correcta e incorrecta. Su función experimental es comprobar que la manipulación realizada sobre el corpus se propaga hasta la información disponible para las etapas posteriores de verificación. La pertinencia de los fragmentos recuperados, el soporte que proporcionan a las afirmaciones diagnósticas y su suficiencia se evalúan posteriormente mediante criterios independientes.

#### Fase de construcción de la explicación (E13, E14)
Esta fase transforma la información producida por los componentes anteriores en una explicación estructurada. Su propósito no es determinar si una hipótesis es válida, sino construir una representación trazable que conserve la relación entre las observaciones de la telemetría, la inferencia diagnóstica y la información documental recuperada.

**Tabla 4.10. Diseño de la fase de construcción de la explicación.**

| Elemento | Descripción |
| --- | --- |
| Entrada | Atribuciones obtenidas sobre la ventana de telemetría, estimación de confianza del modelo especializado y fragmentos documentales recuperados. |
| Procedimiento | Construcción de afirmaciones diagnósticas vinculadas con las observaciones que las originan y con los fragmentos documentales utilizados como soporte. La construcción es determinista y no interviene en ella el modelo de lenguaje. |
| Salida | Conjunto estructurado de afirmaciones con sus observaciones de origen y referencias documentales asociadas. |
| Evaluación | La métrica M3 comprueba la adecuación de la salida al esquema definido y la proporción de respuestas estructuralmente válidas. |
| Criterio metodológico | Toda afirmación debe conservar la referencia a la observación y a los fragmentos documentales utilizados en su construcción. |

*Fuente: elaboración propia.*

El diseño distingue cuatro elementos que cumplen funciones diferentes: la **observación** corresponde al valor derivado de la telemetría; la **inferencia** procede del modelo especializado; la **información documental** se obtiene del corpus técnico; y la **explicación** expresa la relación establecida entre estos elementos. Mantener esta separación permite evaluar posteriormente si una afirmación está realmente respaldada por la documentación citada.

#### Fase de verificación del soporte documental (E15)
La fase de verificación determina si los fragmentos documentales asociados a cada afirmación resultan aplicables al caso y proporcionan soporte para lo que se afirma. Esta comprobación se realiza mediante reglas independientes del modelo de lenguaje, con el propósito de evitar que la propia generación textual actúe como criterio de validación.

**Tabla 4.11. Diseño de la fase de verificación del soporte documental.**

| Elemento | Descripción |
| --- | --- |
| Entrada | Afirmaciones estructuradas producidas en la fase anterior y fragmentos documentales asociados a cada una. |
| Procedimiento | Comprobación determinista de la aplicabilidad y del soporte documental mediante atributos como la señal considerada, el contenido diagnóstico, el código de avería aplicable y la función desempeñada por el fragmento dentro del procedimiento técnico. |
| Salida | Resultado de verificación para cada relación entre afirmación y fragmento, acompañado del motivo correspondiente. |
| Evaluación | M4 caracteriza la trazabilidad mediante la corrección de las citas, la completitud de las referencias y la proporción de afirmaciones que disponen de soporte documental suficiente. |
| Criterio metodológico | Una afirmación no puede considerarse respaldada cuando el fragmento citado no resulta aplicable o no sostiene el contenido que se le atribuye. |

*Fuente: elaboración propia.*

La existencia de una cita no se considera equivalente a disponer de evidencia. Un fragmento puede haber sido recuperado y estar correctamente identificado y, aun así, no ser aplicable al vehículo, al motor o a la afirmación concreta. La verificación del soporte se mantiene separada, por tanto, de la recuperación documental y de la generación de la explicación.

#### Fase de decisión entre explicar y abstenerse (E15, E16)
La última etapa determina si la evidencia disponible resulta suficiente para presentar la hipótesis diagnóstica como respaldada o si el sistema debe abstenerse. La decisión se adopta mediante un criterio explícito e independiente del modelo de lenguaje.

**Tabla 4.12. Diseño de la fase de decisión entre explicar y abstenerse.**

| Elemento | Descripción |
| --- | --- |
| Entrada | Resultado de la verificación del soporte, estimación de confianza del modelo especializado y medidas asociadas a la cantidad y cobertura de la evidencia aplicable. |
| Procedimiento | Aplicación de un criterio de suficiencia compuesto por condiciones explícitas sobre confianza, aplicabilidad, soporte y cobertura de las afirmaciones. Los umbrales utilizados se determinan sobre el conjunto de validación y se mantienen separados de la evaluación final. |
| Salida | Decisión `EXPLICA` o `ABSTIENE`, acompañada de los motivos que justifican la abstención cuando corresponda. |
| Evaluación | M5 analiza la frecuencia y adecuación de las decisiones de explicación y abstención, considerando también la cobertura alcanzada por el sistema. |
| Criterio metodológico | El sistema solo puede presentar una hipótesis como suficientemente respaldada cuando se satisfacen simultáneamente los requisitos definidos para la evidencia; en caso contrario debe abstenerse. |

*Fuente: elaboración propia.*

La abstención se considera una decisión válida cuando la evidencia disponible no permite sostener la hipótesis con los criterios definidos. Su evaluación, sin embargo, no puede limitarse a contabilizar abstenciones correctas: un sistema que se abstuviera de forma sistemática reduciría las explicaciones sin fundamento a costa de perder utilidad diagnóstica. M5 se lee, por eso, junto a la cobertura del sistema.

#### Redacción de la explicación final
Adoptada la decisión, el modelo de lenguaje redacta la respuesta a partir de las observaciones, de los fragmentos aplicables y del veredicto ya emitido. Su intervención se limita a la expresión textual: no formula la hipótesis diagnóstica, que procede del modelo especializado, ni determina la suficiencia de la evidencia, que resuelve el criterio de la fase anterior. Una barrera externa rechaza cualquier identificador documental que no corresponda a un fragmento entregado, de modo que la respuesta no puede citar lo que no ha recibido. Lo que sí se mide sobre esta etapa es si respeta el veredicto y si sus citas existen entre los fragmentos entregados.

La secuencia completa queda, por tanto, así: telemetría, inferencia diagnóstica, recuperación de información documental, construcción de afirmaciones, verificación del soporte, evaluación de la suficiencia, decisión y redacción final.

### Unidades de análisis e independencia experimental
Las distintas variantes documentales aplicadas sobre una misma ventana de telemetría no constituyen observaciones independientes. Comparten los mismos datos OBD-II, la misma predicción y la misma atribución, y difieren únicamente en la información documental disponible. La unidad de independencia es la ventana de telemetría, no el número total de ejecuciones.

**Tabla 4.13. Unidades de análisis utilizadas en las métricas asociadas a OE4.**

| Métrica | Unidad de análisis | Unidad de independencia | Ejecuciones / ventanas independientes |
| --- | --- | --- | --- |
| M2. Recuperación | consulta de un caso anotado | ventana de telemetría | 6 evaluadas, 5 puntuadas / 5 |
| M3. Explicación | salida del modelo de lenguaje por caso | ventana de telemetría | 17 / 5 |
| M4. Trazabilidad | relación afirmación-fragmento | ventana de telemetría | 51 afirmaciones en 17 casos / 5 |
| M5. Abstención | decisión por caso | ventana de telemetría | 17 / 5; falsa confianza 9 / 3 (12 / 3 con la condición con distractor y filtro); abstención innecesaria 5 / 5 |

*Fuente: elaboración propia.*

Las ejecuciones correspondientes a distintas variantes del corpus sobre una misma ventana se consideran medidas relacionadas. No se interpretan como observaciones independientes ni se utilizan para incrementar artificialmente el tamaño efectivo de la muestra.

### Métricas asociadas a la generación y validación de hipótesis
**Tabla 4.14. Métricas utilizadas en la evaluación de la generación y validación de hipótesis.**

| Métrica | Dimensión evaluada | Interpretación |
| --- | --- | --- |
| M2 | Recuperación documental | Capacidad para recuperar y ordenar información documental relevante, por estrategia de recuperación |
| M3 | Validez estructural de la explicación | Grado en que la salida respeta el esquema y conserva los vínculos requeridos |
| M4 | Trazabilidad y soporte | Correspondencia entre las afirmaciones formuladas y los fragmentos documentales que las respaldan |
| M5 | Explicación y abstención | Adecuación de la decisión de explicar o abstenerse según la suficiencia de la evidencia |

*Fuente: elaboración propia.*

La definición formal de cada magnitud —tasa de acierto entre los diez primeros, rango recíproco medio, ganancia acumulada descontada normalizada, cobertura y tasas de decisión— se recoge en el apartado de variables medidas. «Cobertura» se usa en dos sentidos que conviene no mezclar: la cobertura de afirmaciones de un caso, proporción de sus afirmaciones con soporte, que es una condición del criterio; y la cobertura del sistema, proporción de casos con evidencia completa en los que explica.

### Reproducibilidad, versionado y trazabilidad experimental
Cada ejecución experimental registra un identificador único, la versión del conjunto de datos y del corpus documental, el modelo de embeddings utilizado, el proveedor y el modelo de lenguaje, la versión del prompt, la semilla de generación, los parámetros de configuración y las métricas obtenidas. Esta información se conserva en formatos estructurados, principalmente JSON y CSV, con el propósito de permitir la reconstrucción posterior de las condiciones bajo las que se obtuvo cada resultado.

El entorno de ejecución se mantiene mediante un gestor de dependencias con fichero de bloqueo, de forma que las versiones de las bibliotecas empleadas puedan reproducirse. Además, el código se somete a comprobaciones automatizadas de calidad, análisis estático, verificación de tipos y una batería automatizada de pruebas destinada a detectar cambios que puedan alterar el comportamiento esperado de los componentes experimentales.

Los resultados de recuperación y la procedencia de los fragmentos documentales se conservan junto con los registros experimentales. Esto permite reconstruir las consultas realizadas, identificar los documentos y secciones utilizados en cada ejecución y relacionar las salidas obtenidas con la configuración concreta del sistema.

Los artefactos de software, las configuraciones y los registros experimentales se mantienen bajo control de versiones, de modo que cada ejecución pueda vincularse con las versiones de los componentes, los datos, las semillas y los parámetros empleados.

La documentación técnica utilizada como corpus se identifica mediante metadatos y huellas criptográficas. La huella se calcula mediante SHA-256 sobre el fichero original completo, en su forma binaria, y no sobre el texto extraído ni sobre los fragmentos derivados de él; los fragmentos conservan además su propia huella, que identifica el resultado de la segmentación. Dado que las condiciones de distribución de algunos de estos documentos impiden incorporarlos directamente al repositorio del proyecto, sus huellas permiten comprobar que una ejecución reproducida utiliza exactamente el mismo documento sin necesidad de redistribuir el material original.

Los registros anteriores al 4 de septiembre de 2026 carecen de identificador de la versión del código y de fecha de ejecución; los posteriores los incluyen de forma obligatoria. Completar esa identificación para toda la evaluación es condición para dar por cerrada la evaluación final.

### Ablaciones
Cada ablación cambia exactamente un factor: sin atribución, sin recuperación semántica, sin criterio de suficiencia, con un único umbral en lugar del criterio compuesto. Sirven para saber qué parte del resultado aporta cada pieza. Su ejecución forma parte del trabajo experimental que queda por cerrar.

### Trabajo experimental pendiente para el cierre del TFM
Antes del cierre de la evaluación quedan previstas las ablaciones de los principales componentes, la apertura controlada del conjunto de prueba para la evaluación final y la demostración del experimento integrado sobre casos de la partición final.

Todas estas actividades forman parte del diseño experimental del presente trabajo y no se consideran líneas futuras.

## Modelo de análisis de datos
El análisis compara casos y condiciones, y no es un estudio inferencial en el sentido clásico: hay pocos casos anotados y varias ejecuciones recaen sobre la misma ventana de telemetría, de modo que contarlas como unidades independientes inflaría el tamaño efectivo de la muestra sin añadir información. Cada métrica conserva, por eso, su propia unidad de análisis.

Del modelo especializado se comparan exactitud y F1 macro contra una referencia mínima, la clase mayoritaria, y la confianza se examina aparte, con el error de calibración medido antes y después de calibrar. Estas cifras describen cómo se comporta el modelo dentro del conjunto experimental, y su alcance termina ahí: caracterizan el acierto sobre las clases del catálogo, no el comportamiento ante una avería ajena a él.

La validación de las hipótesis se mira afirmación por afirmación: de cada una se comprueba si existe la observación que la origina, si el fragmento citado está disponible, si aplica al vehículo y a la configuración mecánica evaluada, y en qué medida sostiene lo que se afirma. De esas comprobaciones salen las medidas de trazabilidad y completitud; la de soporte, sobre las afirmaciones del verificador, repite por construcción su propio criterio, y solo una anotación independiente la convertiría en medición.

La decisión entre explicar y abstenerse se estudia cambiando la evidencia documental y dejando lo demás quieto. Siempre que el diseño lo permite se mantienen la misma ventana, la misma predicción, la misma atribución y la misma confianza, de modo que lo que varíe pueda atribuirse al corpus. La frecuencia de abstención no se lee sola, sino junto a la cobertura: abstenerse siempre elimina las explicaciones sin fundamento, y también las que sí lo tienen. Los desaciertos se desglosan además en los dos tipos que M5 distingue, con sus denominadores y frente a las dos políticas de referencia.

Ante información distractora interesa dónde quedan los fragmentos recuperados y si el validador los considera aplicables, cuando en el índice hay documentos que se parecen al caso sin corresponder a su configuración. Se observan dos cosas distintas: qué recupera el sistema y si el proceso de validación impide que un fragmento no aplicable acabe sosteniendo una afirmación. Los resultados de esta condición solo se interpretan cuando la manipulación que la produce ha sido comprobada.

Al modelo de lenguaje se le hacen las mismas preguntas con el mismo motor de inferencia, comparando las configuraciones que el diseño define, y se cuentan las salidas válidas, si respetan la decisión que el verificador ya tomó, las referencias inexistentes y los incumplimientos del esquema. El criterio para quedarse con una configuración se fija sobre validación, y el conjunto de prueba no interviene.

Cada magnitud se publica con la partición de la que procede y con la unidad de análisis que la sostiene, entendiendo que las ejecuciones repetidas sobre una misma ventana bajo distintas variantes documentales son medidas relacionadas y no observaciones nuevas. Y cuando un resultado contradice lo que se esperaba se conservan ambos, el criterio tal como se escribió y el resultado tal como salió; si después se cambia el procedimiento, ese cambio se documenta aparte y no sirve para releer lo anterior.