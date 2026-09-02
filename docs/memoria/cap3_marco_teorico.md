# Capítulo 3: Marco Teórico

> Estado: **estructura realineada al marco canónico** y apartados redactados solo con
> referencias verificadas (`REF-nnn` de la lista maestra; `MET-nn` de método). El capítulo de
> estado del arte v2.0 del 18 de agosto de 2026 responde a la pregunta de investigación
> anterior (memoria evolutiva, multiagente, edge) y **no se reutiliza como texto**; sí se
> reutilizan su procedimiento de revisión y sus 144 referencias verificadas, previa
> comprobación de pertinencia. Los apartados marcados `[AMPLIAR]` necesitan lecturas
> adicionales de la lista maestra antes de cerrarse; se indica cuáles.

## Propósito y procedimiento de la revisión

Este capítulo delimita el conocimiento previo en los cuatro frentes que la pregunta de
investigación toca: el diagnóstico de vehículos a partir de la telemetría OBD-II, la
explicabilidad de los modelos que lo hacen, la recuperación aumentada de documentación
técnica con modelos de lenguaje, y la abstención ante evidencia insuficiente. Su finalidad
no es enumerar trabajos sino localizar el vacío que la pregunta aborda y justificar, frente
a lo que otros han hecho, las decisiones de diseño del capítulo 4.

La revisión siguió un procedimiento inspirado en PRISMA, en cuatro iteraciones entre julio y
agosto de 2026: unas 170 consultas, unos 1 350 registros visualizados, unos 250 candidatos
evaluados en fuente primaria y 144 referencias consolidadas, de las que 110 tienen su
identificador persistente comprobado programáticamente en Crossref o DataCite. Los
candidatos no verificables se descartaron en lugar de citarse. El barrido se hizo con
buscadores web y verificación en la página del editor; el acceso automatizado a dos de las
bases principales estuvo parcialmente bloqueado, de modo que el flujo PRISMA formal, con
recuentos por base, queda pendiente de acceso institucional. Las referencias de método que
este capítulo y el siguiente necesitan y que el barrido de dominio no incluía se verificaron
el 2 de septiembre de 2026 por la misma vía; su registro está en el repositorio.

## Diagnóstico vehicular a partir de OBD-II

### El puerto de diagnóstico y sus señales

El diagnóstico a bordo de segunda generación, OBD-II, es obligatorio en turismos de gasolina
en Estados Unidos desde 1996 y en la Unión Europea desde 2001. Define un conector, un
conjunto de protocolos de comunicación y, sobre todo, un catálogo de parámetros consultables
y de códigos de avería, especificado por SAE J1979 (MET-18) e ISO 15031-5 (MET-19). Los
parámetros incluyen régimen de giro, velocidad, carga calculada, posición de la mariposa,
temperaturas de refrigerante y de aire de admisión, caudal másico de aire, presión del
colector, correcciones de combustible a corto y largo plazo, tensión de las sondas de oxígeno
y avance del encendido. Los códigos de avería, con formato de una letra y cuatro dígitos,
tienen una parte normalizada, común a todos los fabricantes, y una parte específica de cada
uno. Ese detalle importa para este trabajo: el manual de un fabricante documenta sus propios
códigos, que pueden no coincidir con el código genérico que la literatura asocia a un
síntoma, y buscar el genérico en el manual puede dar la impresión falsa de que la
documentación no existe.

Rimpas, Papadakis y Samarakou (2020, REF-098) caracterizan las señales accesibles por OBD-II
y su uso para monitorizar operación y consumo; Michailidis, Panagiotopoulou y Papadakis
(2025, REF-078) revisan las aplicaciones de aprendizaje automático sobre esa telemetría y
constatan que la mayoría se orienta a conducción, consumo y seguridad, y que el diagnóstico
de fallos ocupa una parte menor. Ramai et al. (2022, REF-097) describen cómo construir
registradores de bajo coste, lo que sitúa el acceso a los datos al alcance de un trabajo como
este.

### Datos: la limitación estructural del área

`[AMPLIAR con REF-049 y las entradas de la línea de datasets OBD-II de la lista maestra]`
La revisión de Hossain et al. (2024, REF-049) sobre diagnóstico vehicular con inteligencia
artificial coincide con lo que este trabajo encontró al buscar datos: los conjuntos públicos
de telemetría OBD-II con fallos etiquetados son escasos, pequeños o de vehículos que no
documentan su avería con procedimientos de taller accesibles. La consecuencia para el diseño
experimental es directa y se declara en el capítulo 4: el trabajo ha tenido que generar
datos sintéticos calibrados contra la documentación del vehículo, y su incorporación de datos
reales es la primera limitación que enumera.

### Modelos de diagnóstico sobre telemetría

Los trabajos revisados usan tanto modelos tabulares sobre descriptores de ventana como
modelos secuenciales sobre las series crudas. Jun et al. (2025, REF-059) predicen códigos de
avería de vehículos comerciales con aprendizaje automático sobre telemetría; Prytz et al.
(2015, REF-095) anticipan reparaciones a partir de registros de mantenimiento y datos de
vehículo; Lu et al. (2025, REF-075) proponen un modelo híbrido explicable para diagnóstico
de fallos múltiples en electrónica de automoción. El bosque aleatorio (Breiman, 2001,
MET-01) es un baseline recurrente por su robustez con pocos datos y clases desbalanceadas;
las redes recurrentes con unidades GRU (Cho et al., 2014, MET-02) son la alternativa
secuencial habitual. Este trabajo compara ambas y, sobre su volumen de datos, el modelo
tabular no fue superado por el secuencial, un resultado que el capítulo 5 detalla y que la
literatura sobre series cortas hace esperable.

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
el método de atribución dominante en la literatura de diagnóstico de fallos revisada. Brusa
et al. (2023, REF-014) los usan para entender la contribución de cada descriptor en
monitorización de condición industrial; Haque, Zabin y Uddin (2025, REF-044) los combinan con
selección de descriptores y ensamblado para clasificar fallos en motores de vehículo
eléctrico; Li y van Leeuwen (2023, REF-071) proponen detección contextual de anomalías
explicable con bosques de regresión por cuantiles; Abboush et al. (2026, REF-002) buscan
detección robusta e interpretable en grabaciones de pruebas de automoción.

Lo que estos trabajos hacen con la atribución es explicar el modelo al analista. Lo que este
trabajo hace es distinto y conviene subrayarlo: convierte la atribución en **evidencia
observacional citable**, con señal, estadístico, valor, dirección y ventana temporal, para
que una afirmación de la explicación final pueda referirse a ella igual que se refiere a una
página del manual. Esa conversión impone una restricción que la literatura de explicabilidad
enuncia y que el trabajo asume como regla: la atribución indica de qué depende la predicción
del modelo, no qué le ocurre al vehículo. Ninguna afirmación del sistema atribuye causa a
partir de una atribución, y el esquema de salida rechaza las que lo hacen.

## Modelos de lenguaje y recuperación aumentada sobre documentación técnica

### El problema

Ji et al. (2023, MET-15) revisan la producción de contenido no fundamentado por modelos de
lenguaje, las llamadas alucinaciones, y la clasifican en intrínseca, que contradice la fuente,
y extrínseca, que no puede verificarse con ella. La recuperación aumentada (Lewis et al.,
2020, MET-10; Gao et al., 2023, REF-035) reduce el problema al anclar la generación en
documentos recuperados: Shuster et al. (2021, REF-106) miden esa reducción en diálogo
abierto, y Béchard y Ayala (2024, REF-016) en salidas estructuradas. Ninguno de ellos afirma
que la elimine. La recuperación garantiza que haya documentos delante del modelo; no
garantiza que sean los pertinentes, ni que el modelo los use, ni que lo que escriba se
sostenga en ellos.

### Aplicaciones a documentación de vehículos

`[AMPLIAR con las entradas de la línea de agentes y RAG de la lista maestra]` Los trabajos
más próximos a este combinan modelos de lenguaje con documentación técnica de automoción.
Nam et al. (2025, REF-086) ajustan con adaptadores de rango bajo un sistema de recuperación
multimodal para responder preguntas sobre el manual de un vehículo concreto; Lin y Miao
(2025, REF-072) construyen un marco de diagnóstico sobre grafos de conocimiento y modelos de
lenguaje; Mahale, Kolhar y More (2025, REF-077) generan informes de diagnóstico con
aprendizaje automático híbrido y recuperación en varios pasos; Khan et al. (2024, REF-062)
usan modelos de lenguaje para interpretar detecciones de fallo; Das, Griffith y Rathore
(2025, REF-024) y Liu et al. (2025, REF-074) exploran el modelo de lenguaje como detector
sobre series temporales, con resultados que aconsejan no confiarle la detección.

Tres rasgos separan este trabajo de los anteriores. Primero, el modelo de lenguaje no
diagnostica ni decide: recibe un diagnóstico, una atribución, una evidencia y una decisión ya
tomada, y redacta. Segundo, cada afirmación de la salida se ancla simultáneamente en la
telemetría y en el manual, y un componente determinista comprueba que la cita sostiene lo
afirmado antes de que el modelo la vea. Tercero, y es lo que ninguno de los trabajos
revisados mide, el sistema se evalúa retirando la evidencia y sustituyéndola por evidencia
parecida pero incorrecta, para comprobar que responde a su pertinencia y no a su presencia.

### El ajuste del modelo pequeño

Los adaptadores de rango bajo (Hu et al., 2022, MET-13) permiten ajustar un modelo de
lenguaje modificando una fracción muy pequeña de sus parámetros. Este trabajo los usa sobre
un modelo de tres mil millones de parámetros (Qwen Team, 2024, MET-14), ejecutado
localmente, y con una restricción que la aplicación de Nam et al. (2025, REF-086) no impone:
el ajuste enseña el formato de la tarea y no el contenido de la documentación, con
comprobación automática de que ningún pasaje del manual aparece en las salidas de
entrenamiento. La razón está en el diseño experimental: un modelo que hubiera memorizado el
manual explicaría igual cuando la evidencia se retira del índice, y el experimento central
mediría memoria en lugar de evidencia.

### Recuperación: semántica, léxica y filtrada

Los embeddings de frases (Reimers y Gurevych, 2019, MET-11) son la base de la recuperación
semántica; la fusión por rango recíproco (Cormack, Clarke y Buettcher, 2009, MET-12) permite
combinarla con la búsqueda léxica sin ajustar pesos. Sobre documentación técnica, donde los
códigos de avería, los nombres de sensores y los identificadores de procedimiento son
términos exactos, la búsqueda léxica no es un complemento menor. Este trabajo midió que, sobre
su corpus, la recuperación semántica pura no encuentra el procedimiento correcto entre los
diez primeros resultados en ningún caso, y que guiar la consulta con los códigos de avería
que el manual asocia al diagnóstico lo encuentra siempre; el capítulo 5 lo detalla. Midió
también que un modelo de embeddings monolingüe en inglés se hunde con consultas en español
sobre un manual en inglés, lo que justifica el modelo multilingüe.

## Abstención ante evidencia insuficiente

La decisión de no responder tiene una teoría propia, anterior a los modelos de lenguaje.
Chow (1970, MET-08) formuló el compromiso entre error de reconocimiento y rechazo: un
clasificador con opción de rechazo puede reducir su error a costa de no decidir en parte de
los casos, y la calidad de esa política se mide por la curva que relaciona ambas magnitudes.
Geifman y El-Yaniv (2017, MET-09) trasladan la idea a las redes profundas como clasificación
selectiva, con cobertura y riesgo como ejes. Dos consecuencias de esa teoría estructuran la
evaluación de este trabajo: la abstención es una salida legítima cuya calidad se mide, no un
fallo; y no significa nada sin su cobertura, porque un sistema que se abstiene siempre tiene
abstención perfecta y utilidad nula.

`[AMPLIAR: literatura sobre abstención en modelos de lenguaje y en RAG, si la lista maestra
la contiene; si no, verificar antes de citar]` En los sistemas con recuperación, la
abstención se ha tratado sobre todo como una propiedad del modelo de lenguaje: se le pide que
diga «no lo sé» cuando los documentos no bastan. Este trabajo toma otra vía, y es su decisión
de diseño más importante. La suficiencia de la evidencia la evalúa un componente
determinista, fuera del modelo, con un criterio conjuntivo sobre la confianza calibrada, el
número de fragmentos y fuentes que sostienen cada afirmación, la cobertura de las
afirmaciones y la ausencia de contradicciones. El modelo de lenguaje recibe la decisión
tomada y solo tiene que respetarla, y eso sí se mide. La razón es la misma que llevó a
separar la decisión de la redacción: si la disposición a abstenerse dependiera del modelo,
la respuesta a la pregunta de investigación dependería de una propiedad del modelo que no
puede darse por supuesta.

## Vacío y posicionamiento

De la revisión se desprende un vacío con tres caras. Los trabajos de diagnóstico sobre OBD-II
producen etiquetas y, a lo sumo, atribuciones para el analista; no producen evidencia que
una explicación pueda citar. Los trabajos de modelos de lenguaje con documentación de
vehículos anclan la generación en documentos, pero ninguno de los revisados verifica que cada
afirmación se sostenga en la evidencia citada ni mide qué ocurre cuando la evidencia
disponible es parecida pero incorrecta. Y la abstención, cuando aparece, es una propiedad
del modelo y no de la evidencia.

`[CONSENSUAR CON EL DIRECTOR]` La afirmación de novedad sobre la cuarta subpregunta, el
rechazo de evidencia engañosa, es más estrecha de lo que parecía al inicio: existen trabajos
sobre robustez de la recuperación a documentos irrelevantes en dominios generales. Lo que no
se ha encontrado es su medición sobre documentación técnica de vehículo con evidencia
incorrecta *del mismo fabricante y de otro motor*, que es la forma que el distractor toma
aquí. El registro de limitaciones lo recoge como L-10.

El trabajo se posiciona, por tanto, en la intersección de los cuatro frentes: un modelo de
diagnóstico calibrado cuya atribución se convierte en evidencia citable; una recuperación
sobre la documentación del vehículo con procedencia completa y aplicabilidad verificada; un
verificador determinista que construye las afirmaciones, comprueba su soporte y decide; y un
modelo de lenguaje pequeño y local que redacta lo decidido y cuya única obligación medible es
respetarlo y no inventar citas. La contribución no es ninguna de esas piezas por separado,
sino la evidencia experimental sobre cómo se comporta su composición cuando la evidencia se
retira o se sustituye.
