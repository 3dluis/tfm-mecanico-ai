# Capítulo 3: Marco Teórico

## Propósito y procedimiento de la revisión

La construcción del marco teórico comenzó con una primera revisión realizada entre julio y
agosto de 2026, cuando la pregunta de investigación todavía contemplaba elementos que
posteriormente fueron reformulados. Aquel trabajo permitió obtener una primera caracterización
del estado del conocimiento, definir el procedimiento de búsqueda y reunir un conjunto inicial
de referencias verificadas. La evolución posterior de la pregunta hizo necesario revisar ese
material y reevaluar su pertinencia respecto del problema finalmente abordado en este TFM. Las
referencias procedentes de aquella revisión se conservaron cuando mantenían una relación
justificable con la formulación actual y su contenido podía comprobarse en la fuente primaria.

A partir de esta depuración, el marco teórico se organiza en cuatro frentes directamente
relacionados con la pregunta de investigación: el diagnóstico vehicular mediante telemetría
OBD-II, la explicabilidad de los modelos utilizados para analizarla, la recuperación de
información sobre documentación técnica mediante modelos de lenguaje y la abstención ante
evidencia insuficiente. Estos frentes se examinan atendiendo a la función que desempeñan dentro
del problema estudiado: identificar y caracterizar patrones observados en la telemetría,
determinar cuándo un patrón no está representado en el conocimiento disponible, aportar
información para la formulación de hipótesis diagnósticas, contrastarlas con documentación
aplicable y establecer cuándo la evidencia disponible resulta suficiente para validarlas.

La revisión se desarrolló mediante un procedimiento inspirado en PRISMA y organizado en cuatro
iteraciones realizadas entre julio y agosto de 2026. En conjunto se efectuaron aproximadamente
170 consultas, se examinaron unos 1 350 registros y se evaluaron alrededor de 250 trabajos
candidatos mediante sus fuentes primarias. El proceso dio lugar a 144 referencias consolidadas,
de las cuales 110 cuentan con un identificador persistente comprobado mediante Crossref o
DataCite; las 34 restantes carecen de identificador en su fuente de origen. Las referencias que
no pudieron verificarse con suficiente precisión se descartaron como soporte de las afirmaciones
formuladas en la memoria.

La búsqueda combinó buscadores académicos y web con la comprobación posterior en las páginas de
los editores y otras fuentes primarias. El acceso automatizado a dos de las principales bases
consultadas estuvo parcialmente restringido, lo que impidió completar los recuentos desagregados
necesarios para caracterizar el proceso como una revisión sistemática PRISMA completa. Por este
motivo se adopta la expresión *procedimiento inspirado en PRISMA*, conservando sus principios de
identificación, selección, trazabilidad y verificación. Las referencias metodológicas necesarias
para completar el diseño del TFM que no formaban parte del barrido inicial se incorporaron
después aplicando el mismo criterio de comprobación en fuente primaria.

Conviene precisar qué se aplicó de ese marco y qué no. Se aplicaron la formulación previa de las
consultas y su registro por iteración; el cribado en dos pasos, primero por título y resumen y
después en fuente primaria; unos criterios de inclusión y exclusión escritos antes de decidir
—alcance, acceso al texto completo, calidad metodológica, duplicidad y evaluabilidad—; el
registro de cada descarte con su motivo, sobre el principio de que un descarte sin motivo
escrito es un sesgo de selección invisible; y la verificación del identificador de cada
referencia incluida. No se aplicaron el protocolo registrado antes de comenzar, el cribado por
duplicado con resolución de discrepancias entre revisores y el diagrama de flujo con recuentos
desagregados por base de datos, que es precisamente lo que el acceso restringido impidió
construir.

## Diagnóstico vehicular a partir de OBD-II

Tres cuestiones ordenan este frente: qué señales expone el puerto de diagnóstico y qué
normas las fijan, qué datos existen para trabajar con ellas, y qué modelos se han usado
para diagnosticar a partir de esa telemetría.

### El puerto de diagnóstico y sus señales

El diagnóstico a bordo de segunda generación, OBD-II, es el estándar de diagnóstico
embarcado de adopción más extendida en turismos. Define un conector, un conjunto de protocolos de comunicación y, sobre todo, un catálogo de parámetros consultables
y de códigos de avería, especificado por SAE J1979 (MET-18) e ISO 15031-5 (MET-19). Los
parámetros incluyen régimen de giro, velocidad, carga calculada, posición de la mariposa,
temperaturas de refrigerante y de aire de admisión, caudal másico de aire, presión del
colector, correcciones de combustible a corto y largo plazo, tensión de las sondas de oxígeno
y avance del encendido. Los códigos de avería, con formato de una letra y cuatro dígitos,
tienen una parte normalizada, común a todos los fabricantes, y una parte específica de cada
uno. Ese detalle importa para este trabajo: el manual de un fabricante documenta sus propios
códigos, que pueden no coincidir con el código genérico que los repertorios habituales
asocian a un síntoma, y buscar el genérico en el manual puede dar la impresión falsa de que
el manual no documenta la avería.

Rimpas, Papadakis y Samarakou (2020, REF-098) caracterizan las señales accesibles por OBD-II
y su uso para monitorizar operación y consumo; Michailidis, Panagiotopoulou y Papadakis
(2025, REF-078) revisan las aplicaciones de aprendizaje automático sobre esa telemetría y
constatan que la mayoría se orienta a conducción, consumo y seguridad, y que el diagnóstico
de fallos ocupa una parte menor. Ramai et al. (2022, REF-097) describen cómo construir
registradores de bajo coste, lo que sitúa el acceso a los datos al alcance de un trabajo como
este.

### Datos: la limitación estructural del área

La revisión de Hossain et al. (2024, REF-049) dedica un apartado a la escasez de datos
etiquetados, y señala que la limitación principal de los datos reales es «la ausencia o el
carácter incompleto del etiquetado», porque anotar grandes volúmenes exige tiempo y
conocimiento especializado. Coincide en eso con lo que este trabajo encontró al buscar datos.

A esa dificultad, ya documentada, este trabajo añade una segunda que la revisión no trata: aun
cuando el conjunto exista y esté etiquetado, rara vez viene acompañado de la documentación de
taller del vehículo del que procede.

Conviene precisar la afirmación, porque decir que no hay datos sería falso. Los hay. Hojjati
et al. (2026, REF-048) publican un conjunto de detección de anomalías en motores de vehículos
reales, y Jun et al. (2025, REF-059) trabajan sobre predicción de códigos de avería en
vehículos comerciales. Lo que la revisión no encontró es un conjunto que reúna las **tres**
cosas que este trabajo necesita a la vez: telemetría del puerto de diagnóstico, una etiqueta
de fallo por sesión, y el manual de taller del mismo vehículo con los procedimientos que
documentan ese fallo. Dentro del corpus revisado, la documentación técnica asociada al mismo
vehículo fue el elemento menos frecuente, y sin ella la pregunta de investigación no puede
evaluarse, porque no habría evidencia documental que recuperar ni contra la que verificar.

La consecuencia para el diseño es directa y se declara en el capítulo 4: el trabajo genera
telemetría sintética cuyas constantes se parametrizan a partir de especificaciones documentadas
en páginas concretas del manual del vehículo, de modo que dato y documentación se refieran a la misma configuración
mecánica. Calibrar contra un manual real no convierte el dato en real, y el trabajo no lo
presenta así en ningún punto.

**Lo que la evidencia revisada no permite afirmar.** Que no existan conjuntos adecuados: solo
que en el corpus revisado no se identificó ninguno que cumpliera las tres condiciones. Ni que
los resultados obtenidos sobre datos sintéticos anticipen el comportamiento sobre telemetría
real, que es una cuestión abierta y la primera limitación del capítulo 6.

### Modelos de diagnóstico sobre telemetría

Los trabajos revisados usan tanto modelos tabulares sobre descriptores de ventana como
modelos secuenciales sobre las series crudas. Jun et al. (2025, REF-059) predicen códigos de
avería de vehículos comerciales con aprendizaje automático sobre telemetría; Prytz et al.
(2015, REF-095) anticipan reparaciones a partir de registros de mantenimiento y datos de
vehículo; Lu et al. (2025, REF-075) proponen un modelo híbrido explicable para diagnóstico
de fallos múltiples en electrónica de automoción. El bosque aleatorio (Breiman, 2001, MET-01)
constituye una línea base adecuada para datos tabulares con pocas muestras y clases
desbalanceadas, por la robustez que su autor documenta; las redes recurrentes con unidades GRU
(Cho et al., 2014, MET-02) son la alternativa secuencial sobre las series crudas. No se identificó, entre los trabajos revisados, evidencia concluyente sobre cuál de las
dos familias conviene con ventanas cortas y volúmenes reducidos, de modo que la comparación entre ambas forma
parte del diseño experimental.

Un aspecto que la mayoría de los trabajos revisados no trata, y que para este es central, es
la **calibración** de la confianza del modelo. Guo et al. (2017, MET-04) mostraron que los
modelos modernos tienden a estar mal calibrados, y el error esperado de calibración (Naeini,
Cooper y Hauskrecht, 2015, MET-07) permite medirlo; la regresión isotónica (Zadrozny y
Elkan, 2002, MET-05; Niculescu-Mizil y Caruana, 2005, MET-06) es una corrección estándar.
Cuando la confianza del modelo alimenta una decisión posterior, como aquí la de explicar o
abstenerse, una confianza sin calibrar hace que esa decisión opere sobre un número que no
significa lo que aparenta. El capítulo 4 lo trata como precondición y no como refinamiento.

## Explicabilidad de los modelos de diagnóstico

Los valores de Shapley aplicados a modelos de aprendizaje (Lundberg y Lee, 2017, MET-03) son
el método de atribución más frecuente en los trabajos de diagnóstico de fallos revisados, aunque
no el único. Brusa et al. (2023, REF-014) los usan para entender la contribución de cada
descriptor en monitorización de condición industrial. Haque, Zabin y Uddin (2025, REF-044)
recurren en cambio a explicaciones locales por aproximación con un modelo interpretable, y las
combinan con selección recursiva de descriptores y un ensamblado por voto para clasificar
fallos en motores de vehículo eléctrico: un recordatorio de que la atribución en este dominio
no se hace solo con valores de Shapley. Li y van Leeuwen (2023, REF-071) proponen detección
contextual de anomalías
explicable con bosques de regresión por cuantiles; Abboush et al. (2026, REF-002) buscan
detección robusta e interpretable en grabaciones de pruebas de automoción.

Lo que estos trabajos hacen con la atribución es explicar el modelo al analista. Este trabajo hace algo distinto: transforma la atribución en un **registro trazable de evidencia
observacional derivada**, asociado a señales, estadísticos, valores, dirección y ventanas
temporales concretas, para que una afirmación de la explicación final pueda referirse a ella igual que se refiere a una
página del manual. Esa conversión impone una restricción que los trabajos de explicabilidad
enuncian y que el trabajo asume como regla: la atribución indica de qué depende la predicción
del modelo, no qué le ocurre al vehículo. El diseño restringe las afirmaciones causales
derivadas exclusivamente de la atribución del modelo, y el esquema de salida rechaza las que
las formulan.

**Lo que la evidencia revisada no permite afirmar.** Que una atribución fiel al modelo sea una
explicación útil para quien repara el vehículo. Los estudios analizados evalúan la atribución
frente al comportamiento del modelo, no frente al juicio de un mecánico ni frente al resultado
de la reparación. Este trabajo hereda ese límite: mide que la afirmación esté anclada en la
observación y en el manual, no que la explicación conduzca a un diagnóstico acertado en el
taller.

## Modelos de lenguaje y recuperación aumentada sobre documentación técnica

El apartado parte del problema que motiva el trabajo, revisa las aplicaciones a
documentación de vehículos, describe cómo se ajusta un modelo pequeño sin que aprenda el
contenido del corpus, y termina en la recuperación semántica, léxica y filtrada.

### El problema

Ji et al. (2023, MET-15) revisan la producción de contenido no fundamentado por modelos de
lenguaje, las llamadas alucinaciones, y la clasifican en intrínseca, que contradice la fuente,
y extrínseca, que no puede verificarse con ella. La recuperación aumentada (Lewis et al.,
2020, MET-10; Gao et al., 2023, REF-035) reduce el problema al anclar la generación en
documentos recuperados: Shuster et al. (2021, REF-106) miden esa reducción en diálogo
abierto, y Béchard y Marquez Ayala (2024, REF-016) en salidas estructuradas. Ninguno de ellos afirma
que la elimine. La recuperación garantiza que haya documentos delante del modelo; no
garantiza que sean los pertinentes, ni que el modelo los use, ni que lo que escriba se
sostenga en ellos.

### Aplicaciones a documentación de vehículos

Los trabajos más próximos a este combinan modelos de lenguaje con documentación técnica de automoción.
Nam et al. (2025, REF-086) ajustan con adaptadores de rango bajo un sistema de recuperación
multimodal para responder preguntas sobre el manual de un vehículo concreto; Lin y Miao
(2025, REF-072) construyen un marco de diagnóstico sobre grafos de conocimiento y modelos de
lenguaje; Mahale, Kolhar y More (2025, REF-077) generan informes de diagnóstico con
aprendizaje automático híbrido y recuperación en varios pasos; Khan et al. (2024, REF-062)
usan modelos de lenguaje para interpretar detecciones de fallo. Y dos trabajos van más lejos:
Das, Griffith y Rathore (2025, REF-024) y Liu et al. (2025, REF-074) emplean el modelo de
lenguaje **como detector** sobre series temporales, los primeros con ganancias notables de F1
al congelar el modelo sobre representaciones de la serie, y los segundos con un rendimiento de
detección comparable al de los métodos profundos de referencia y con explicaciones asociadas.

Este trabajo no sigue esa vía, y la razón no está en esos resultados sino en lo que la pregunta
de investigación exige. La detección aquí debe producir una atribución de descriptores
verificable y una confianza calibrada que alimente el criterio de suficiencia, y ambas cosas se
obtienen de un modelo especializado sobre la ventana de telemetría. El modelo de lenguaje queda
así como redactor, no como detector: una decisión de diseño propia, que los trabajos revisados
no respaldan ni desmienten porque no evalúan esa separación.

En los trabajos revisados, la evaluación se concentra principalmente en la corrección de la
respuesta o en el rendimiento diagnóstico. No se identificó ninguno que mida si cada afirmación de la respuesta puede seguirse hasta el fragmento
documental que la sostiene, ni qué ocurre cuando el corpus **no** contiene la evidencia
necesaria. Esa diferencia de objeto de medida, más que de arquitectura, es la que sitúa a este
trabajo respecto de ellos.

**Lo que la evidencia revisada no permite afirmar.** Que la recuperación evite las
afirmaciones sin fundamento. Lo que Béchard y Marquez Ayala (2024, REF-016) miden es una **reducción**
en salidas estructuradas, y lo que este trabajo asume es que reducir no es eliminar: ninguno de
los dos artículos afirma haber eliminado el fenómeno, y el mecanismo que lo produce sigue
siendo el modelo de lenguaje. Recuperar el documento correcto no obliga al modelo a usarlo, y esa
distancia entre disponer de la evidencia y apoyarse en ella es justamente lo que este trabajo
convierte en objeto de medición.
Tres decisiones de diseño distinguen la propuesta desarrollada en este TFM dentro del corpus
analizado. Primero, el modelo de lenguaje no
diagnostica ni decide: recibe un diagnóstico, una atribución, una evidencia y una decisión ya
tomada, y redacta. Segundo, cada afirmación de la salida se ancla simultáneamente en la
telemetría y en el manual, y un componente determinista comprueba que la cita sostiene lo
afirmado antes de que el modelo la vea. Tercero, y es lo que no se encontró medido dentro del corpus
analizado, el sistema se evalúa retirando la evidencia y sustituyéndola por evidencia
parecida pero incorrecta, para comprobar que responde a su pertinencia y no a su presencia.

### El ajuste del modelo pequeño

Los adaptadores de rango bajo (Hu et al., 2022, MET-13) permiten ajustar un modelo de lenguaje
modificando una fracción muy pequeña de sus parámetros, lo que los hace viables para adaptar un
modelo pequeño al formato de una tarea sin reentrenarlo. Esa distinción entre adaptar el formato
y adaptar el contenido es la que importa aquí. Un modelo que hubiera memorizado la documentación
explicaría igual cuando la evidencia se retira del índice, y el experimento mediría entonces
memoria en lugar de evidencia. La aplicación de Nam et al. (2025, REF-086) no impone esa
restricción; el capítulo 4 describe el modelo empleado y los controles con que se comprueba.

### Recuperación: semántica, léxica y filtrada

Los embeddings de frases (Reimers y Gurevych, 2019, MET-11) son la base de la recuperación
semántica; la fusión por rango recíproco (Cormack, Clarke y Buettcher, 2009, MET-12) permite
combinarla con la búsqueda léxica sin ajustar pesos. Sobre documentación técnica, donde los
códigos de avería, los nombres de sensores y los identificadores de procedimiento son
términos exactos, la búsqueda léxica conserva relevancia cuando la documentación contiene identificadores y
términos técnicos cuya coincidencia exacta aporta información discriminativa. Esa asimetría entre proximidad
semántica y coincidencia exacta motiva dos decisiones que el capítulo 4 desarrolla y el 5
evalúa: guiar la consulta con los códigos de avería que el manual asocia al diagnóstico, y
emplear un modelo de embeddings multilingüe cuando la consulta y el manual no comparten idioma.

## Qué significa que un patrón no esté representado

La pregunta de investigación sitúa en su origen un patrón de fallo **no representado en el
conocimiento disponible**. La expresión reúne situaciones que la literatura trata por separado y
que conviene distinguir antes de llegar al diseño experimental, porque cada una se detecta de
forma distinta, se corrige por una vía distinta y compromete la explicación en un punto distinto.

Chandola, Banerjee y Kumar (2009, REF-019) organizan las técnicas de detección de anomalías
según el supuesto con que cada familia separa el comportamiento normal del anómalo, y advierten
que ese supuesto es el que determina si una técnica sirve en un dominio concreto. Trasladada a
un sistema con varios componentes, la advertencia obliga a preguntar **respecto de qué
conocimiento** se declara no representado un patrón. En la arquitectura que este trabajo estudia
hay al menos cinco respuestas posibles.

La primera es que el patrón **no esté en el conjunto de entrenamiento del modelo de
diagnóstico**: la clase existe en el dominio pero no entre las etiquetas aprendidas. Un
clasificador de conjunto cerrado no puede señalarla; a lo sumo repartirá su probabilidad entre
clases conocidas, y la confianza calibrada será baja sin que ese número diga por qué.

La segunda es que el patrón **esté en el conjunto de clases pero no en la ventana observada** de
forma reconocible, por ruido, por régimen de conducción o por una duración insuficiente. Es un
fallo de observación, no de conocimiento, y se manifiesta también como confianza baja, lo que
hace que ambas situaciones sean indistinguibles desde la salida del modelo.

La tercera es que el patrón sea **anómalo respecto del comportamiento normal** sin corresponder
a ninguna clase: la telemetría se aparta de lo esperado y no hay etiqueta que le convenga. Esta
es la situación que la detección de anomalías aborda, y es distinta de las dos anteriores porque
no exige un catálogo previo de fallos.

La cuarta es que el patrón esté reconocido pero **el corpus documental no contenga el
procedimiento** que lo trata. Aquí el conocimiento ausente no es el del modelo sino el de la
evidencia: el diagnóstico existe y no hay documentación aplicable con la que sostenerlo.

La quinta es que el conocimiento esté **en los parámetros del modelo de lenguaje** y no en la
evidencia entregada. Es el caso inverso y el más peligroso para la validez del experimento,
porque el sistema podría explicar correctamente sin evidencia y hacer indistinguible la
recuperación de la memorización.

Las cinco se comportan igual ante un lector de la salida final —el sistema no explica, o explica
con poca confianza— y exigen instrumentos distintos: detección fuera de distribución para la
primera, control del régimen de conducción para la segunda, detección de anomalías para la
tercera, medición de cobertura documental para la cuarta y control de contaminación del ajuste
para la quinta. El capítulo 4 declara cuáles de esos instrumentos incorpora el diseño ejecutado
y cuáles no, y el capítulo 6 recoge la consecuencia de las ausencias.

**Lo que la evidencia revisada no permite afirmar.** Que estas cinco situaciones agoten las
formas en que un patrón puede no estar representado, ni que la distinción entre ellas sea
resoluble a partir de la salida del sistema. Dentro del corpus analizado no se identificó un
trabajo que las separe experimentalmente en un sistema de diagnóstico con recuperación.

## Abstención ante evidencia insuficiente

La decisión de no responder tiene una teoría propia, anterior a los modelos de lenguaje.
Chow (1970, MET-08) formuló el compromiso entre error de reconocimiento y rechazo: un
clasificador con opción de rechazo puede reducir su error a costa de no decidir en parte de
los casos, y la calidad de esa política se mide por la curva que relaciona ambas magnitudes.
Geifman y El-Yaniv (2017, MET-09) trasladan la idea a las redes profundas como clasificación
selectiva, con cobertura y riesgo como ejes. Dos consecuencias de esa teoría estructuran la
evaluación de este trabajo: la abstención es una salida legítima cuya calidad se mide, no un
fallo; y no significa nada sin su cobertura, porque una política que se abstuviera en todos los
casos eliminaría el riesgo de respuestas incorrectas a costa de una cobertura nula.

En los sistemas con recuperación, la
abstención se ha tratado sobre todo como una propiedad del modelo de lenguaje: se le pide que
diga «no lo sé» cuando los documentos no bastan. Este trabajo adopta una estrategia distinta: la
suficiencia de la evidencia se evalúa mediante un componente determinista externo al modelo de
lenguaje, con un criterio conjuntivo sobre la confianza calibrada, el
número de fragmentos y fuentes que sostienen cada afirmación, la cobertura de las
afirmaciones y la ausencia de contradicciones. El modelo de lenguaje recibe la decisión
tomada y solo tiene que respetarla, y eso sí se mide. La razón es la misma que llevó a
separar la decisión de la redacción: si la disposición a abstenerse dependiera del modelo,
la respuesta a la pregunta de investigación dependería de una propiedad del modelo que no
puede darse por supuesta.

**Lo que la evidencia revisada no permite afirmar.** Que pedir a un modelo de lenguaje que
reconozca su ignorancia sea suficiente, ni tampoco que sea inútil: los estudios analizados
miden esa capacidad sobre preguntas de dominio general y no sobre documentación técnica de un
vehículo, donde la evidencia pertinente es un procedimiento concreto y no un pasaje
enciclopédico. La comparación entre una abstención decidida por el modelo y otra decidida
fuera de él no se encontró resuelta en el corpus revisado, y este trabajo tampoco la resuelve:
implementa la segunda y mide lo que consigue, sin contrastarla experimentalmente con la
primera.

## Vacío y posicionamiento

La revisión converge en un vacío central que se manifiesta en varias dimensiones relacionadas.
Los trabajos de diagnóstico mediante OBD-II permiten clasificar estados, detectar anomalías o
proporcionar atribuciones sobre las variables relevantes, pero no se identificó, dentro del
corpus revisado, una evaluación integrada en la que esas observaciones se utilicen para formular
una hipótesis diagnóstica que deba después contrastarse con evidencia documental antes de
considerarse válida. Del mismo modo, los trabajos que incorporan modelos de lenguaje y
recuperación sobre documentación técnica muestran mecanismos para generar respuestas
fundamentadas en documentos, pero no se encontró una evaluación sistemática de la
correspondencia entre cada afirmación y la evidencia concreta que la sostiene, especialmente
cuando la información disponible es incompleta, ausente o aparentemente pertinente pero
incorrecta.

En este contexto, la abstención constituye una parte del problema y no el vacío completo. La
cuestión central es determinar si un sistema puede recorrer de forma trazable el proceso que va
desde la identificación de un patrón no representado y su interpretación contextual y temporal
hasta la formulación de una hipótesis, su contraste con evidencia aplicable y la decisión de
validarla o mantenerla como no confirmada. Solo después de esa validación puede plantearse su
incorporación como conocimiento reutilizable.

Conviene acotar el alcance de esta afirmación. En particular, el rechazo de evidencia
engañosa presenta un alcance más acotado de lo que parecía al inicio: existen trabajos
sobre robustez de la recuperación a documentos irrelevantes en dominios generales. Lo que no se encontró, dentro del corpus
analizado, es su medición sobre documentación técnica de vehículo con evidencia incorrecta *del
mismo fabricante y de otro motor*, que es la forma que el distractor toma aquí. Esta limitación se recoge en el capítulo 6.

Los trabajos revisados permiten justificar los componentes necesarios para abordar cada parte
del problema, pero no muestran, dentro del alcance de la revisión realizada, una evaluación
integrada del ciclo completo planteado en este TFM: identificar un patrón de fallo no
representado en el conocimiento disponible, interpretarlo a partir del contexto y de la evolución temporal de
la telemetría, formular una hipótesis diagnóstica, contrastarla con evidencia aplicable,
rechazarla o abstenerse cuando esa evidencia resulte insuficiente y conservar como conocimiento
reutilizable únicamente aquello que haya superado el proceso de validación.

El vacío identificado no reside, por tanto, en la ausencia de modelos de diagnóstico, técnicas
de explicabilidad, sistemas de recuperación o mecanismos de abstención considerados por
separado. Todos ellos cuentan con antecedentes. La cuestión que permanece abierta, dentro de los
trabajos analizados, es cómo articularlos en un proceso diagnóstico en el que una hipótesis no
adquiera la condición de conocimiento por haber sido generada de forma plausible, sino por haber
sido contrastada con evidencia suficiente. Esta relación entre observación, hipótesis, evidencia,
validación y reutilización delimita el problema que el diseño experimental del capítulo siguiente
intenta estudiar.
