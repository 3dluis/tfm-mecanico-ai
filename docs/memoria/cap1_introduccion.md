# Capítulo 1: Introducción al Trabajo Fin de Máster

> Estado: redactado. Actualizado el 3 de septiembre de 2026 a la PI sin requisito de datos
> reales (ADR-003). Referencias: lista maestra (`REF-nnn`) y de método
> (`MET-nn`), todas verificadas.

## Justificación del proyecto realizado

Un vehículo moderno informa de su estado a través del puerto de diagnóstico a bordo, OBD-II,
normalizado por SAE J1979 e ISO 15031-5 (MET-18; MET-19). Por él circulan decenas de señales
en tiempo real, régimen de giro, carga, temperaturas, caudal de aire, correcciones de
combustible, tensión de las sondas de oxígeno, y los códigos de avería que la centralita
registra cuando una de esas señales sale de lo que espera. Los trabajos revisados sobre aprendizaje
automático aplicado a esa telemetría son abundantes y recientes: se ha usado para clasificar
estilos de conducción, estimar consumo, predecir averías y detectar anomalías (Michailidis,
Panagiotopoulou y Papadakis, 2025, REF-078; Rimpas, Papadakis y Samarakou, 2020, REF-098;
Hossain et al., 2024, REF-049). Los modelos alcanzan buenos resultados de clasificación. Lo
que producen, sin embargo, es una etiqueta.

Una etiqueta no es un diagnóstico. El mecánico que la recibe necesita saber qué señales la
motivan, en qué tramo del trayecto, y qué dice la documentación del fabricante sobre esa
situación en ese motor concreto. Los modelos de lenguaje parecen la pieza que falta: leen
documentación técnica, redactan con soltura y responden preguntas. Los trabajos que los
combinan con recuperación de información sobre manuales de taller, con grafos de
conocimiento o con modelos de diagnóstico son ya varios (Lin y Miao, 2025, REF-072; Mahale,
Kolhar y More, 2025, REF-077; Nam et al., 2025, REF-086; Khan et al., 2024, REF-062). Y
comparten un problema que los estudios generales sobre modelos de lenguaje tienen bien
caracterizado: producen texto plausible cuando no tienen base para producirlo (Ji et al.,
2023, MET-15). La recuperación de documentos reduce ese comportamiento, pero no lo elimina
(Shuster et al., 2021, REF-106; Béchard y Ayala, 2024, REF-016). En un dominio donde la
explicación termina en una intervención sobre el vehículo, una explicación fluida y sin
fundamento es peor que ninguna explicación, porque no se distingue a simple vista de una
explicación correcta.

Ese es el vacío que este trabajo aborda. No pregunta si un modelo de lenguaje puede redactar
un diagnóstico, que puede. Pregunta si un agente puede hacerlo de manera que **cada afirmación
sea rastreable hasta la evidencia que la sostiene**, tanto la observación en la telemetría
como el pasaje del manual, y si puede **reconocer cuándo esa evidencia no basta** y
abstenerse. La segunda parte es la más exigente. Un sistema que explica siempre no está
usando la evidencia, la está decorando; un sistema que se abstiene siempre es inútil. Lo que
se quiere medir es si la decisión de explicar o no responde a la evidencia disponible, y para
medirlo hay que poder retirar la evidencia y observar qué cambia.

La pregunta de investigación que gobierna el trabajo se enuncia así:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la
> evidencia disponible no es suficiente para sostener una explicación en lugar de generar
> una hipótesis sin fundamento?

Se descompone en cuatro subpreguntas, cada una con un experimento y una métrica asignados
antes de ejecutar nada: si el sistema diagnostica a partir de la telemetría (PI.1); si la
explicación es trazable hasta su evidencia (PI.2); si reconoce la insuficiencia de la
evidencia (PI.3); y si rechaza evidencia parecida pero incorrecta (PI.4). La cuarta es la
que distingue este diseño de los trabajos previos revisados: la mayoría comprueba que el
sistema responde mejor cuando hay documentos, y ninguno de los revisados comprueba que
responda peor, y lo sepa, cuando los documentos disponibles son los equivocados.

Tres decisiones de diseño se derivan directamente de la pregunta y conviene enunciarlas
desde el principio, porque explican la arquitectura del artefacto. Primera: el modelo de
lenguaje no diagnostica. Diagnostica un modelo especializado sobre la telemetría, con su
confianza calibrada (Guo et al., 2017, MET-04), y la explicabilidad de ese modelo (Lundberg y
Lee, 2017, MET-03) es la que produce la evidencia observacional. Segunda: la decisión de
explicar o abstenerse no la toma el modelo de lenguaje. La toma un componente determinista,
fuera de él, que aplica un criterio de suficiencia inspirado en la predicción con opción de
rechazo (Chow, 1970, MET-08; Geifman y El-Yaniv, 2017, MET-09). Si la tomara el modelo, la
respuesta a la pregunta dependería de su disposición a admitir que no sabe algo, que es
justamente lo que no puede darse por supuesto. Tercera: el modelo de lenguaje redacta la
decisión ya tomada, con las afirmaciones ya construidas y las citas ya verificadas, y una
barrera externa rechaza cualquier cita que no corresponda a algo que se le entregó.

El trabajo se realiza sobre un vehículo concreto, un Mazda 3 de la generación BK de 2007,
elegido entre tres candidatos por la cobertura de su documentación de taller y por la
especificidad de sus procedimientos de diagnóstico respecto del motor. La documentación del
vehículo es el corpus del sistema de recuperación, y el vehículo es también el objeto de la
telemetría. Esa coherencia importa: un manual de otro motor de la misma gama es evidencia
parecida pero incorrecta, y es precisamente lo que la cuarta subpregunta necesita.

## Presentación del proyecto y sus contenidos

El proyecto es un laboratorio experimental reproducible, construido de cero para responder
a la pregunta, con veinte fases documentadas, criterios de aceptación fijados antes de
ejecutar cada una y un registro por experimento con su commit, semilla, versiones y métricas.
El artefacto que evalúa es un agente compuesto por un modelo de diagnóstico, un módulo de
atribución, un sistema de recuperación sobre base de datos con extensión vectorial, un
verificador de suficiencia y un modelo de lenguaje pequeño ejecutado localmente. El trabajo
sigue el ciclo de la investigación en ciencias del diseño (Peffers et al., 2007, MET-16;
Hevner et al., 2004, MET-17): el artefacto se construye para poder evaluarlo, y la evaluación
es la contribución.

La memoria se organiza conforme a la plantilla de la titulación. El **capítulo 2** enuncia el
objetivo general y los cinco objetivos específicos, cada uno con las fases y métricas que lo
cumplen. El **capítulo 3** revisa el estado del conocimiento en cuatro frentes, diagnóstico
sobre OBD-II, explicabilidad de modelos de diagnóstico, recuperación aumentada sobre
documentación técnica y abstención ante evidencia insuficiente, y delimita el vacío. El
**capítulo 4** describe la población y la muestra, los datos, las variables e instrumentos de
medida, el diseño experimental con sus cuatro condiciones y el modelo de análisis. El
**capítulo 5** presenta los resultados obtenidos y los discute. El **capítulo 6** recoge las
limitaciones, la prospectiva y las consideraciones finales.

Una advertencia recorre toda la memoria y se hace explícita aquí para no tener que
repetirla en cada capítulo. La pregunta de investigación no exige que los datos OBD-II sean
reales; exige que cada resultado declare sobre qué datos se obtuvo. Los datos con que se han
ejecutado los experimentos son sintéticos: los genera un modelo paramétrico cuyas constantes
están ancladas, una por una, a valores del manual de taller del vehículo. Esa calibración está
documentada y hace que los datos se parezcan a los reales en lo que el manual permite
comprobar; no los convierte en una medición. Lo que un resultado sobre ellos sostiene es el
comportamiento del agente ante los mecanismos de fallo representados; no sostiene
comportamiento equivalente en un vehículo real. Esa distinción se mantiene visible en los
capítulos 4, 5 y 6, y la incorporación de datos reales, como validación externa, es la
primera limitación que se declara y el primer trabajo que queda por hacer.

Todo el código, la documentación, los registros de experimentos y este texto están
versionados en un repositorio Git y son reproducibles con las instrucciones que contiene. El
manual de taller del vehículo, sujeto a derechos de su fabricante, no se redistribuye; se
registra su huella criptográfica para que un tercero que disponga de él pueda comprobar que
utiliza el mismo documento.
