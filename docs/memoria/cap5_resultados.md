# Capítulo 5: Presentación de análisis, resultados y discusión
Todos los resultados de este capítulo proceden del vehículo de referencia definido en el capítulo 4, un Mazda 3 BK de 2007 con motor Z6, y de su corpus documental. No se han evaluado otros vehículos ni otras generaciones.

Las cifras de este capítulo proceden de la partición de **validación** de la muestra sintética descrita en el capítulo 4. El conjunto de prueba **se abrió cinco veces**: tres intentos de la evaluación final, de los que el tercero es la medición publicada; una comprobación pre-registrada de las ablaciones; y una apertura accidental que solo leyó identificadores de sesión. En cuatro de las cinco hubo exposición de etiquetas y de predicciones. El registro completo, con los cinco niveles de exposición que se distinguen, está en `docs/methodology/registro-aperturas-test.md`. Lo que sí se sostiene, y se comprueba con un comando, es que el instrumento no cambió entre la primera apertura y la medición: umbrales, casos elegibles, reglas de selección, política y código son los mismos. La procedencia del dato es sintética, y su validez externa se discute en el capítulo 6. Cada tabla cita el registro de ejecución del que sale. **La evaluación final sobre el conjunto de prueba se ejecutó el 12 de octubre de 2026** y su informe es `docs/experiments/E19_evaluacion_final.md`: falsa confianza 0 de 14 ejecuciones y abstención innecesaria 2 de 8, con un conjunto anotado sellado antes de abrir la partición; con esos denominadores el intervalo de incertidumbre es amplio y no se publica. Sus cifras no se han incorporado todavía a este capítulo. **La demostración integrada sigue pendiente.**

> **Corrección del 13 de octubre de 2026.** El texto de este párrafo decía antes: «el conjunto de prueba permanece cerrado y no se ha consultado […] Son resultados parciales: la evaluación final sobre el conjunto de prueba y la demostración integrada quedan pendientes». Las dos afirmaciones eran falsas en el momento de revisarlas: el conjunto se había abierto cinco veces y la evaluación final ya se había ejecutado. La propuesta de corrección, con su evidencia, está en `docs/audits/correccion-cap5-cap6-paso-a.md` (`F-1` y `F-6`).

Las cifras de recuperación, de suficiencia y del modelo de lenguaje proceden de una reejecución realizada el 13 y el 14 de septiembre de 2026. El 4 de septiembre se detectó que el índice documental contenía dos representaciones vectoriales por fragmento y que ninguna búsqueda declaraba en cuál buscaba, de modo que la procedencia de cada fragmento recuperado era indeterminada. Se corrigió el defecto, se fijó por escrito y antes de medir qué se compararía y cómo se interpretaría, y se repitieron la recuperación, la suficiencia en sus dos modos, la generación del conjunto de ajuste y la redacción con el modelo de lenguaje con el mismo modelo, umbral y política. Ninguna de las diecisiete decisiones cambió; los conjuntos de fragmentos recuperados cambiaron en diez de los diecisiete casos, siempre por adición. Con arreglo al criterio fijado de antemano, ese resultado se lee como ausencia de efecto detectable con este instrumento, no como confirmación del criterio de suficiencia. Los registros anteriores se conservan como históricos; las filas de nueve casos de la Tabla 5.7 y el escenario adverso proceden de ellos, del 4 de septiembre.

Tres rasgos del diseño condicionan todo lo que sigue sobre el agente. El criterio de suficiencia, su umbral, las anotaciones de los casos, la ampliación del conjunto y el adaptador del modelo de lenguaje se fijaron o revisaron sobre los mismos diecisiete casos con que se evalúan, de modo que las cifras del agente son de desarrollo y no de evaluación. Los diecisiete casos se construyeron sobre ventanas de validación que el modelo clasifica correctamente, de modo que las tasas de decisión describen el comportamiento del agente cuando el diagnóstico de partida es acertado y deben leerse como cota superior. Y la estrategia de recuperación con mejores valores acota su búsqueda con los códigos de avería que documentan la condición **anotada**, información que el sistema no tiene antes de diagnosticar; su ventaja mide una cota asistida por esa anotación y no una capacidad de recuperación comparable con las demás.

## Análisis descriptivo de la muestra
La muestra sintética consta de 72 sesiones de 600 segundos, 12 por condición, muestreadas a 1 Hz; ventanadas a 120 segundos con solape producen 392 ventanas de entrenamiento y 98 de validación, con 139 descriptores por ventana. Las 98 ventanas de validación proceden de 12 sesiones, dos por condición: cada condición de fallo aporta 14 ventanas, y las 28 sin fallo incluyen las anteriores a la entrada del fallo en las sesiones con fallo. El reparto es por sesión, y por eso ninguna ventana de validación comparte sesión con una de entrenamiento.

El análisis exploratorio previo al modelado dejó dos hechos que condicionan la lectura de todo lo demás. El primero es que los cinco fallos no se separan de la condición sin fallo por la misma vía, y que dos de ellos no lo hacen por el nivel de ninguna señal. La fuga de vacío y la deriva del caudalímetro se separan por el nivel del ajuste de combustible a corto plazo, con delta de Cliff 1,00 las dos; el termostato bloqueado, por el nivel de la temperatura del refrigerante, con −0,75, y es el fallo con la firma más clara en medias, 69,2 °C frente a 81,4 de la condición sin fallo. La sonda lambda de respuesta lenta, en cambio, **no se separa por el nivel sino por la dispersión**: su oscilación se amortigua casi por completo, de una desviación típica de 0,250 a 0,033, y la delta de Cliff es −1,00 en dispersión frente a +0,29 en nivel. Y el fallo de encendido queda diluido en el agregado porque sus episodios alteran el 5,7 % de los instantes de la sesión: la caída media de régimen durante ellos es de −218 revoluciones, pero la desviación típica de la variación de régimen de toda la sesión sube solo de 115,4 a 117,1. Su mejor separación medida sobre bloques de 60 segundos, +0,58 en el nivel de la sonda lambda, es el efecto grande más débil de los cinco. El segundo hecho es de otra naturaleza y afecta solo al termostato, que tiene un límite físico de detección: mientras el motor no habría superado por sí mismo la temperatura a la que el fallo lo limita, la señal averiada es idéntica a la sana. En esas ventanas la respuesta correcta del sistema es abstenerse, y no hubo que fabricar el caso.

> **Corrección del 13 de octubre de 2026.** Este párrafo decía antes: «dos de los cinco fallos no son visibles en las medias de las señales: **el fallo de encendido y el termostato bloqueado abierto** solo se distinguen de la condición sin fallo por la dispersión o por la evolución temporal, no por el nivel». El termostato es, de los cinco, el **más** visible en la media de una señal, y el fallo que faltaba nombrar es la sonda lambda de respuesta lenta. El párrafo mezclaba además dos cosas: no tener firma en el nivel, y tener un techo físico por debajo del cual no se deja firma de ninguna clase, que es lo propio del termostato y es la frase siguiente. Ninguna cifra del capítulo cambia. La propuesta, con su evidencia, está en `docs/audits/propuesta-figuras-cap5-cap6.md` (`F-8`).

El estudio de ventana del capítulo 4 fijó 120 segundos como longitud en la que los descriptores separables coinciden con los mecanismos físicos declarados para cada fallo. En particular, la deriva del caudalímetro no se detecta en el caudal medido sino en las correcciones de combustible con que la centralita la compensa. Esto condiciona qué puede afirmar legítimamente el agente: «el caudalímetro deriva porque el caudal es bajo» sería falso, y las plantillas de afirmación del verificador no permiten formularlo.

## Resultados obtenidos
Los resultados se presentan por subpregunta, PI.1 a PI.4, siguen con la medición del modelo de lenguaje y terminan con la contribución de cada componente. Primero lo observado; después su interpretación.

### PI.1 · Diagnóstico, calibración y atribución
**Tabla 5.1. Rendimiento del modelo de diagnóstico sobre la partición de validación.**

| Modelo | Exactitud | F1 macro | Registro |
| --- | --- | --- | --- |
| Referencia mínima (clase mayoritaria) | 0,286 | 0,074 | `E6_baseline_synthetic_v2.json` |
| Bosque aleatorio, 139 descriptores | 0,878 | 0,879 | `E6_baseline_synthetic_v2.json` |
| GRU bidireccional sobre secuencias | 0,827 | 0,823 | `E7_temporal_synthetic_v2.json` |

*Fuente: elaboración propia.*

Los informes de fase del modelo de diagnóstico daban cifras ligeramente distintas (F1 0,876 para el bosque; exactitud 0,806 y F1 0,822 para la red recurrente), procedentes de una ejecución anterior que una ejecución posterior sustituyó sin que el informe se actualizara. La tabla cita los registros vigentes; el del bosque se reprodujo bit a bit el 14 de septiembre de 2026 con la misma semilla. Ninguno de los dos registros incluye el identificador de la versión del código, que solo se hizo obligatorio a partir del 4 de septiembre.

El modelo temporal no supera al tabular. Por clase acierta dos ventanas más en el termostato bloqueado, 11 de 14 frente a 9 de 14, sobre dos sesiones y una sola semilla; con este volumen de datos la complejidad añadida no está justificada en agregado, y se conserva el bosque como modelo de diagnóstico. Con un conjunto tres veces mayor, generado como análisis de sensibilidad y no adoptado, el orden se invierte por un margen de 0,012 en F1 macro en una sola ejecución, de modo que la desventaja del modelo temporal se atribuye al volumen de datos y no se toma como resultado sobre la arquitectura. Todos los errores del bosque van a la condición «sin fallo»: el modelo no produce diagnósticos cruzados, lo que para un sistema que va a explicar es la dirección de error menos dañina.

El fallo de encendido se detecta en 7 de las 14 ventanas de validación de esa condición, procedentes de dos sesiones. El resultado estaba anticipado por escrito antes de medirlo, con su motivo cuantificado en el estudio de ventana, y no se aumentó la severidad del fallo para mejorar la cifra.

La confianza del bosque estaba mal calibrada, y en la dirección menos habitual:

**Tabla 5.2. Calibración de la confianza del modelo de diagnóstico.**

|  | ECE | Confianza media | Acierto | Sesgo |
| --- | --- | --- | --- | --- |
| Sin calibrar | 0,144 | 0,738 | 0,878 | −0,140 |
| Calibrado (isotónica, validación cruzada sobre entrenamiento) | 0,085 | 0,886 | 0,878 | +0,009 |

*Fuente: elaboración propia a partir de *`E15_suficiencia.json`*.*

El modelo estaba infraconfiado. Como esa confianza alimenta el criterio de suficiencia, un umbral sobre la confianza cruda habría hecho que el agente se abstuviera de más, y habría parecido prudencia cuando era mala medición. El error de calibración se calcula con diez intervalos sobre 98 ventanas y se publica sin incertidumbre; la mejora es clara en esta muestra, pero no se cuantifica su variabilidad.

La atribución por valores de Shapley, calculada sobre dieciocho casos de validación con un fondo de cien ventanas sin fallo de entrenamiento, produce la evidencia observacional que las etapas posteriores consumen. Contrastada con las señales que el generador declara para cada fallo, se comporta de forma desigual. En la fuga de vacío, el termostato y la sonda de oxígeno, todas las señales atribuidas entre las seis principales son señales declaradas. En la deriva del caudalímetro el caudal medido no aparece: el modelo detecta el fallo por las correcciones de combustible, lo que coincide con el análisis exploratorio. En el fallo de encendido, cuatro de las seis señales principales no están declaradas para esa condición, entre ellas la temperatura del refrigerante, cuya separación aparente el estudio de ventana había situado por debajo del suelo de ruido; las dos señales declaradas que aparecen concentran, con todo, varias veces más importancia acumulada que las cuatro no declaradas. La atribución es fiel al modelo y, en ese fallo, mezcla el mecanismo del vehículo con señales que no le pertenecen. El registro de esta fase, `E9_xai_synthetic_v2.json`, es anterior a la obligatoriedad del identificador de versión.

### PI.2 · Recuperación y trazabilidad
La recuperación semántica pura no encuentra el procedimiento correcto del manual entre los diez primeros resultados en ningún caso. Guiar la consulta con los códigos de avería que el manual asocia al diagnóstico lo encuentra en los cinco casos puntuados:

**Tabla 5.3. Recuperación sobre el corpus documental por estrategia.**

| Estrategia | P@10 | R@10 | MRR | Hit@10 | nDCG@10 |
| --- | --- | --- | --- | --- | --- |
| Semántica | 0,000 | 0,000 | 0,000 | 0,00 | 0,000 |
| Semántica con filtro de motor | 0,020 | 0,200 | 0,040 | 0,20 | 0,149 |
| Semántica con filtro de autoridad | 0,040 | 0,400 | 0,107 | 0,40 | 0,468 |
| Híbrida (semántica y léxica, fusión por rango recíproco) | 0,040 | 0,400 | 0,107 | 0,40 | 0,468 |
| Guiada por el diagnóstico | 0,260 | 1,000 | 0,467 | 1,00 | 0,653 |

*Fuente: elaboración propia a partir de *`E12_retrieval.json`*.*

La tabla procede de la reejecución del 13 de septiembre de 2026 sobre los seis casos anotados de esa fase, con la consulta en inglés y el mapa de códigos de avería congelado para esta comparación. Cinco casos se puntúan; el sexto, con la evidencia retirada del índice, se evalúa pero no entra en las métricas porque no tiene fichero relevante. El informe de fase del 1 de septiembre recogía cuatro estrategias con valores que no se reproducen desde el registro, y la tabla cita el registro. Respecto de la ejecución anterior a la corrección del índice cambiaron dos celdas de la estrategia guiada: la precisión, de 0,240 a 0,260, y el nDCG, de 0,642 a 0,653. Las métricas se publican por estrategia y no por condición de evidencia, porque los cinco casos puntuados tienen todos la evidencia completa. Sobre documentación técnica, la similitud semántica entre una consulta en lenguaje natural y un procedimiento de taller es baja, y lo que los une es un identificador exacto. El sistema final usa la estrategia guiada, con la híbrida como respaldo.

Una medición descriptiva sugiere que el idioma de la consulta también importa. Sin filtro por código de avería, buscando el documento relevante entre los 500 primeros resultados:

**Tabla 5.4. Recuperación translingüe sin filtro por código de avería.**

| Modelo de embeddings | Consulta | Hallados | Posición mediana |
| --- | --- | --- | --- |
| Monolingüe inglés | inglés | 5/5 | 47 |
| Monolingüe inglés | español | 1/5 | 376 |
| Multilingüe | inglés | 4/5 | 58 |
| Multilingüe | español | 4/5 | 54 |

*Fuente: elaboración propia a partir del informe de la fase de ingesta.*

Esta medición no dispone de un registro de ejecución con versión del código; no se ha reproducido y se presenta como observación descriptiva, no como resultado verificado. Con el modelo monolingüe, las consultas en español devolvían puntuaciones de aspecto razonable que no correspondían al documento relevante. Todas las demás mediciones de este capítulo usan la consulta en inglés.

En cuanto a trazabilidad, sobre el registro vigente de suficiencia el verificador construyó 51 afirmaciones, tres por caso, y las 51 conservan la observación de la telemetría que las origina. Doce de ellas, las de los cuatro casos con evidencia completa en los que el criterio encontró soporte, llevan citados fragmentos documentales aplicables; en los doce casos con evidencia parcial, ausente o con distractor ninguna afirmación obtuvo cita, que es lo que esas condiciones están diseñadas para producir. La proporción de afirmaciones con cita cuya cita las sostiene es de 12 sobre 12, pero esa igualdad es una propiedad del procedimiento y no una medición: el verificador solo asigna como cita un fragmento que ya ha superado las comprobaciones de soporte, es decir, que menciona la señal, tiene contenido diagnóstico y porta un código de la condición. Medir si esas comprobaciones deterministas coinciden con lo que un fragmento sostiene de verdad exige anotar, para cada caso, las afirmaciones admisibles y la evidencia mínima exigible, anotación que el conjunto actual no tiene. Lo que sí queda comprobado es que cada afirmación admitida conserva su observación de origen y sus fragmentos, y que ninguna cita se asigna fuera de esas comprobaciones.

Dos errores del instrumento se detectaron por el camino. El mapeo inicial asociaba la deriva del caudalímetro a los códigos de tensión del sensor, mientras el modelo la observa en las correcciones de combustible, y la cobertura era 0,00 hasta añadir los códigos de mezcla pobre. Y se afirmó en cuatro informes de fase que el manual no documentaba la fuga de vacío porque no contenía el código genérico P0171; el propio sistema la encontró después bajo el código específico del fabricante, P2187. Los cuatro informes conservan la afirmación falsa tachada.

### PI.3 y PI.4 · Suficiencia, abstención y distractores
El criterio de suficiencia está en su tercera versión y se evalúa sobre diecisiete casos. El umbral de confianza calibrada es 0,79. El criterio original, fijado sobre una curva de la que ya se conocían cuatro puntos, elegía el umbral más bajo con precisión de decisión por ventana igual o superior a 0,93, que daba 0,72; una enmienda escrita tras ver ese resultado, y antes de reejecutar las fases que dependen del umbral, exigió además que el objetivo se mantuviera en todo el tramo de cinco centésimas siguiente, porque 0,72 lo cumplía por una sola ventana. Agregada por sesión, que es la unidad independiente, la precisión en 0,79 queda en 0,90, y en remuestreo el objetivo de 0,93 se cumple en el 60 % de las réplicas; el criterio se escribió por ventana y así se aplicó. Las diecisiete decisiones no cambian para ningún umbral comprendido entre 0,60 y 0,90, de modo que el resultado de los casos anotados no depende de la elección entre 0,72 y 0,79. El umbral de puntuación de recuperación está desactivado porque no discrimina.

**Tabla 5.5. Decisiones del verificador de suficiencia sobre los diecisiete casos anotados.**

| Caso | Condición | Confianza | Documentos aplicables | Cobertura | Esperado | Decidido |
| --- | --- | --- | --- | --- | --- | --- |
| C01 deriva de caudalímetro | FULL | 0,600 | 6 | 1,00 | EXPLAIN | ABSTAIN |
| C02 termostato bloqueado | FULL | 1,000 | 8 | 1,00 | EXPLAIN | EXPLAIN |
| C03 sonda lenta | FULL | 1,000 | 6 | 1,00 | EXPLAIN | EXPLAIN |
| C04 fallo de encendido | FULL | 0,462 | 4 | 0,00 | EXPLAIN | ABSTAIN |
| C05 fuga de vacío | FULL | 0,908 | 7 | 1,00 | EXPLAIN | EXPLAIN |
| C06 fuga, evidencia retirada | ABSENT | 0,908 | 0 | 0,00 | ABSTAIN | ABSTAIN |
| C07 fuga, evidencia parcial | PARTIAL | 0,908 | 5 | 0,00 | ABSTAIN | ABSTAIN |
| C08 fuga, distractor | DISTRACTOR | 0,908 | 5 | 0,00 | ABSTAIN | ABSTAIN |
| C09 fuga, distractor sin filtro de motor | DISTRACTOR | 0,908 | 3 | 0,00 | ABSTAIN | ABSTAIN |
| C10 termostato, evidencia retirada | ABSENT | 1,000 | 0 | 0,00 | ABSTAIN | ABSTAIN |
| C11 termostato, evidencia parcial | PARTIAL | 1,000 | 7 | 0,00 | ABSTAIN | ABSTAIN |
| C12 termostato, distractor | DISTRACTOR | 1,000 | 7 | 0,00 | ABSTAIN | ABSTAIN |
| C13 termostato, distractor sin filtro | DISTRACTOR | 1,000 | 4 | 0,00 | ABSTAIN | ABSTAIN |
| C14 sonda, evidencia retirada | ABSENT | 1,000 | 0 | 0,00 | ABSTAIN | ABSTAIN |
| C15 sonda, evidencia parcial | PARTIAL | 1,000 | 6 | 0,00 | ABSTAIN | ABSTAIN |
| C16 sonda, distractor | DISTRACTOR | 1,000 | 6 | 0,00 | ABSTAIN | ABSTAIN |
| C17 sonda, distractor sin filtro | DISTRACTOR | 1,000 | 3 | 0,00 | ABSTAIN | ABSTAIN |

*Fuente: elaboración propia a partir de *`E15_suficiencia.json`*, modo oracular.*

Los diecisiete casos no son diecisiete observaciones independientes. Proceden de cinco ventanas de telemetría: cada uno de los cinco casos con evidencia completa tiene la suya, y los doce restantes aplican cuatro condiciones a las ventanas de la fuga de vacío, el termostato y la sonda de oxígeno. Por eso los dos tipos de error se publican con el número de ejecuciones y el de ventanas, y junto a dos políticas de referencia definidas el 4 de septiembre de 2026, después de medir las tres versiones del criterio sobre estos casos. Las filas de la condición con distractor y filtro de motor se cuentan aparte, porque esa condición no manipulaba lo que decía manipular: su configuración era idéntica a la de la condición parcial, como se describe más abajo, de modo que valen como diagnóstico y no como condición puntuable.

> **Corrección del 13 de octubre de 2026.** El texto de este párrafo decía antes: «porque el diagnóstico de esa condición, que se describe más abajo, las deja como diagnóstico y no como condición puntuable». La conclusión era correcta y la causa atribuida, falsa: se culpaba al filtro de motor y lo medido es que dos condiciones tenían la misma configuración. La propuesta de corrección, con su evidencia, está en `docs/audits/correccion-cap5-cap6-paso-a.md` (`F-4`).

**Tabla 5.6. Falsa confianza y abstención innecesaria del sistema y de dos políticas de referencia.**

| Política | Falsa confianza (T_FC): explica cuando debía abstenerse | Abstención innecesaria (T_AI): se abstiene cuando debía explicar |
| --- | --- | --- |
| Verificador de suficiencia | 0 de 9 ejecuciones, sobre 3 ventanas (0 de 12 incluyendo las tres del distractor con filtro) | 2 de 5 ejecuciones, sobre 5 ventanas |
| Abstenerse siempre | 0 de 9 (0 de 12) | 5 de 5 |
| Explicar siempre que el modelo confía | 9 de 9 (12 de 12) | 2 de 5 |

*Fuente: elaboración propia a partir de *`E15_suficiencia.json`*; las políticas de referencia se calculan sobre los mismos casos.*

Ninguna de las tres filas se resume en una tasa de acierto única: el recuento de decisiones que coinciden con la anotada, 15 de 17, agrega dos errores que no son intercambiables y no se usa como resultado. Lo que la tabla muestra es que el verificador conserva la falsa confianza nula de la política que se abstiene siempre y la cobertura de la que explica siempre que el modelo confía: de las dos políticas triviales, cada una iguala al sistema en un error y lo empeora en el otro. Las tasas describen la muestra anotada y no estiman una tasa poblacional: con tres y cinco ventanas independientes no se publica ningún intervalo, porque ninguno acotaría lo que el diseño pretende afirmar.

El modo no oracular, en el que los códigos de avería que acotan la búsqueda y exige el verificador salen del diagnóstico del modelo y no de la anotación, produjo exactamente el mismo vector de decisiones (registro `E15_suficiencia_non_oracle.json`). Esa identidad era forzosa: como las diecisiete ventanas se eligieron entre las bien clasificadas, el diagnóstico del modelo coincide con la etiqueta en todas y los códigos derivados de uno y de otra son los mismos. Confirma que la implementación no oracular no introduce diferencias, no que el sistema resista un diagnóstico erróneo.

Ese segundo aspecto solo se ha examinado en un escenario adverso registrado el 4 de septiembre, antes de la corrección del índice, sobre las dos ventanas de validación que el modelo clasifica mal con mayor confianza: una del termostato, evaluada bajo cinco condiciones de evidencia, y una del fallo de encendido, ambas diagnosticadas como funcionamiento sin fallo. El sistema se abstuvo en las seis ejecuciones. En las dos con evidencia completa, sin embargo, aceptó fragmentos como soporte de dos de las tres afirmaciones construidas para el diagnóstico erróneo, y se abstuvo solo porque la cobertura, 0,67, no alcanzó el umbral de 0,80. El análisis de ese escenario reveló además que, cuando el diagnóstico no tiene códigos de avería asociados, una de las cuatro comprobaciones de soporte se omitía; ese defecto está corregido y su corrección, medida, como se recoge al final de este apartado. El escenario prueba el error por omisión y no el de sustitución de un fallo por otro, porque en validación no existe ningún error de ese segundo tipo por encima del umbral.

Las filas C05 a C08 y sus equivalentes para el termostato y la sonda comparten ventana, modelo, atribución y confianza calibrada; lo único que cambia entre ellas es el contenido del índice, y la decisión cambia con él. Con la evidencia completa, el agente explica. Con la evidencia retirada, la recuperación devuelve cero fragmentos, porque la condición excluye del índice los fragmentos con los códigos de avería de la condición, y el agente se abstiene por ausencia de evidencia documental aplicable; esa abstención está determinada por la construcción de la condición y no pone a prueba el criterio de soporte. La condición informativa es la parcial: el agente tiene delante cinco, siete o seis fragmentos aplicables, y se abstiene igual, porque ninguno sostiene las afirmaciones y la cobertura es 0,00.

Los dos errores son abstenciones innecesarias en condición completa, C01 y C04, y no tienen la misma causa. En C01 el único motivo registrado es la confianza calibrada, 0,600, por debajo del umbral. En C04 concurren dos: la confianza, 0,462, y una cobertura de afirmaciones de 0,00, porque ninguno de sus cuatro fragmentos aplicables supera las comprobaciones: el procedimiento del código de fallo de encendido, recuperado en tercera posición, otro procedimiento de los códigos por cilindro y una referencia de lógica de detección no nombran la sonda de oxígeno, que es la señal que la atribución señala para ese caso, y el cuarto es una tabla de códigos que el criterio no admite como procedimiento. Un umbral de confianza más bajo habría explicado C01 y no C04. En ambos casos la confianza calibrada del modelo no alcanza el umbral y la salida declara ese motivo de abstención; en C04, además, la evidencia documental no sostiene lo que la atribución del modelo propone.

El criterio de suficiencia no llegó a esta tabla sin revisiones. Su primera versión, medida sobre los mismos diecisiete casos, explicó 6 de los 12 casos que debían terminar en abstención, porque aceptaba como soporte cualquier fragmento que compartiera vocabulario con la afirmación; la segunda corrigió ese defecto y se abstuvo en la fuga de vacío con evidencia completa; la tercera recuperó ese caso cambiando solo la granularidad con que se clasifica el papel de un fragmento. Las tres versiones abstienen en los tres casos con evidencia retirada. La falsa confianza nula de la tabla procede, por tanto, de un criterio revisado sobre el mismo conjunto que lo mide, y la evaluación final sobre el conjunto de prueba es la que dirá si se mantiene.

Sobre los distractores, la recuperación semántica pura coloca un procedimiento del motor LF por encima del correcto de los motores ZJ y Z6 en un caso; con el filtro de motor activo, ninguno. El diagnóstico de la condición, con dos criterios fijados antes de medir, se hizo sobre la recuperación reejecutada. Con el filtro activo, la condición con distractor recuperó en el termostato y en la sonda exactamente los mismos fragmentos que la condición parcial, y en ninguno de los dos entró un fragmento del fichero distractor. **La causa, comprobada en octubre de 2026, no es el filtro de motor:** las dos condiciones tenían la misma configuración que la parcial correspondiente, porque el único campo que las distinguía —el fichero distractor declarado— no lo lee el recorrido de suficiencia, que construye la condición excluyendo fragmentos del índice. Nunca fueron condiciones distintas, y no porque un filtro bloqueara algo, sino porque no había nada que bloquear. En la fuga de vacío el criterio la clasificó como válida, pero la condición parcial de esa misma ventana ya contenía los dos fragmentos del fichero distractor, con coincidencia exacta de motor, y lo único que distingue una condición de la otra son dos fragmentos del motor Z6. En ninguno de los tres fallos, por tanto, la condición con distractor y filtro añade un distractor que la parcial no tuviera.

Sin filtro de motor, los fragmentos de otro motor entran en los tres fallos y la vía por la que se rechazan no es la misma. En el termostato y en la sonda, el validador de aplicabilidad los degrada a coincidencia parcial, que el criterio no admite como evidencia. En la fuga de vacío llegan también fragmentos del motor LF con coincidencia exacta, y los detiene que no mencionan la señal atribuida. Lo que queda comprobado es que ningún fragmento de otro motor sostuvo una afirmación en ninguno de los casos evaluados; la protección procede en dos fallos de la aplicabilidad y en el tercero del vocabulario de la señal, y no de la combinación de filtro y verificador que se había supuesto al diseñar la condición.

### El modelo de lenguaje: respeta la decisión y no cita lo que no recibió
El modelo de lenguaje recibe el diagnóstico, la confianza, la decisión del verificador con sus motivos, las observaciones de la telemetría y los fragmentos del corpus con coincidencia exacta de aplicabilidad, y redacta la salida en un esquema fijo; una barrera externa rechaza cualquier identificador documental que no esté entre los entregados. Se midió con el mismo motor de inferencia, los mismos parámetros deterministas y las mismas preguntas en tres configuraciones: el modelo base, el modelo con el primer adaptador y el modelo con el segundo. Una primera medición reveló un fallo del esquema de salida, que no admitía los motivos de abstención que emite el verificador; se corrigió y se repitieron las tres mediciones sobre los nueve casos entonces anotados. Tras ampliar el conjunto a diecisiete casos y corregir el índice documental, las tres configuraciones se midieron de nuevo el 14 de septiembre de 2026 con los mismos adaptadores, sin reentrenarlos.

**Tabla 5.7. Salidas del modelo de lenguaje por configuración.**

| Configuración | Casos | Salidas válidas | Respeta el veredicto | Citas inexistentes | Fallos de esquema | Latencia media |
| --- | --- | --- | --- | --- | --- | --- |
| Base | 9 | 7/9 | 7/7 evaluables | 0 | 2 | 26,8 s |
| Base con adaptador v1 | 9 | 7/9 | 7/7 evaluables | 0 | 2 | 20,7 s |
| Base con adaptador v2 | 9 | 9/9 | 9/9 | 0 | 0 | 26,7 s |
| Base | 17 | 15/17 | 15/15 evaluables | 0 | 2 | 8,7 s |
| Base con adaptador v1 | 17 | 11/17 | 11/11 evaluables | 0 | 6 | 11,1 s |
| Base con adaptador v2 | 17 | 17/17 | 17/17 | 0 | 0 | 13,4 s |

*Fuente: elaboración propia a partir de *`E13_agente_transformers*.json`*, versiones del 4 de septiembre (nueve casos) y del 14 de septiembre (diecisiete casos).*

Sobre los nueve casos comunes, la segunda medición reproduce la primera para el modelo base y para el segundo adaptador, y el primer adaptador pierde una salida válida. El veredicto no es evaluable en una salida que no cumple el esquema: para el modelo base y el primer adaptador la cifra es 7 de 7 evaluables, no 9 de 9. «Respeta el veredicto» mide que la decisión escrita coincide con la que el modelo recibe en la entrada. Las latencias son medias de distribuciones muy asimétricas y las de las dos fechas no son comparables entre sí.

Los adaptadores modifican el 0,24 % de los parámetros, solo en las proyecciones de atención, con 55 ejemplos de entrenamiento derivados de ejecuciones del propio pipeline sobre ventanas de validación y cero fugas de texto del manual en las salidas de entrenamiento. Esa procedencia tiene una consecuencia que se declara: el conjunto con que se ajustaron los adaptadores no registró las ventanas de origen de sus ejemplos, pero los valores de las observaciones permiten identificarlas: las ventanas de C02 y C03 están en su partición de entrenamiento y la de C04 en su partición de validación, y las dos primeras sirven a diez de las diecisiete ejecuciones de la tabla. El segundo adaptador, además, se eligió por su resultado de 9 de 9 sobre los mismos casos que la tabla publica. Los resultados del adaptador describen, por tanto, su comportamiento sobre casos que pudo haber visto, no su generalización.

Tres lecturas. Primera: **ninguna configuración citó un fragmento que no se le hubiera entregado**, y eso no lo consiguió el ajuste; lo garantiza la barrera externa. Lo que la barrera no garantiza es que el modelo cite solo los fragmentos que el verificador aceptó como soporte: en los tres casos que el segundo adaptador explica, seis de sus nueve afirmaciones citan algún fragmento aplicable que el verificador no había asignado a ninguna afirmación. La correspondencia verificada entre afirmación y evidencia es, por tanto, la de las afirmaciones del verificador, y no se extiende sin más al texto que redacta el modelo. Segunda: el ajuste cambió la forma de la explicación hacia la buscada. El modelo base, en su único caso explicativo válido de la primera medición, cuelga las cinco observaciones de una misma afirmación y parafrasea el manual como si fuera afirmación propia; el ajustado produce tres afirmaciones, cada una con una observación y dos fragmentos, y sin atribuir causa. Pero sus afirmaciones califican el valor observado, «por encima de lo esperable», cuando la observación solo registra hacia dónde empuja la predicción del modelo; la calificación procede de las plantillas del conjunto de ajuste y no está sostenida por el dato. Tercera: el primer adaptador no mejoró el recuento porque cambió los fallos de sitio, y la causa estaba en los datos de ajuste. El objetivo de entrenamiento traducía el motivo de abstención a un vocabulario genérico mientras la entrada mostraba el literal; el modelo intentaba copiar la entrada y deformaba el identificador. El segundo adaptador cambia solo eso y pasa de 7 a 9 salidas válidas; sobre los diecisiete casos, el defecto del primero se manifiesta en seis salidas y el segundo mantiene las diecisiete válidas.

### Contribución de cada componente
Cuatro ablaciones, pre-registradas y ejecutadas el 1 de octubre de 2026 sobre los mismos
diecisiete casos, cambian una pieza cada una y dejan el resto idéntico. Ninguna redacta: miden la
decisión y la evidencia, no el texto. Las unidades de análisis son las de la Tabla 5.6: la falsa
confianza se cuenta sobre nueve ejecuciones procedentes de tres ventanas de telemetría, y la
abstención innecesaria sobre cinco ejecuciones de cinco ventanas; entre paréntesis, el recuento
que incluye las tres ejecuciones de la condición con distractor y filtro de motor.

**Tabla 5.8. Efecto de retirar o degradar cada componente.**

| Configuración | Falsa confianza | Abstención innecesaria | Cobertura con evidencia completa | Decisiones distintas de la canónica |
| --- | --- | --- | --- | --- |
| Canónica: criterio compuesto, umbral 0,79 | 0 de 9 | 2 de 5 | 3 de 5 | — |
| A1 sin atribución: observaciones por desviación tipificada | 0 de 9 | 2 de 5 | 3 de 5 | 0 de 17 |
| A2 sin recuperación semántica: solo búsqueda léxica | 0 de 9 | 5 de 5 | 0 de 5 | 3 de 17 |
| A3 sin criterio de suficiencia: explicar si hay fragmento aplicable | 6 de 9 | 0 de 5 | 5 de 5 | 11 de 17 |
| A4 umbral único: solo confianza calibrada | 9 de 9 | 2 de 5 | 3 de 5 | 12 de 17 |

*Fuente: elaboración propia a partir de `E18_ablacion_A1.json` a `E18_ablacion_A4.json`.*

Sustituir la atribución por un criterio estadístico simple no cambió ninguna decisión ni ningún
conjunto de evidencia. La explicación está en el diseño: la recuperación la guía el diagnóstico y
no la atribución, y el soporte se comprueba sobre la señal y no sobre el estadístico, de modo que
dos rutas que eligen distintos descriptores de las mismas señales llegan al mismo sitio.

La lectura correcta de ese cero es estrecha y conviene fijarla, porque admite una mala. La
atribución **no interviene en la política de abstención**: para decidir si se explica o no, en
esta muestra, es sustituible por un criterio estadístico simple. Su contribución está en otro
plano, el de la trazabilidad y la explicación de la predicción: es la que nombra qué señal, con
qué estadístico, en qué dirección y en qué ventana temporal sostiene cada afirmación, y es lo que
el lector de la explicación recibe y puede comprobar. Esa dimensión no se ha evaluado aquí, y el
resultado de la ablación no dice nada sobre ella.

La ablación de la recuperación semántica quedó **inconclusa**, y conviene decir por qué. La ruta
léxica no recuperó ningún fragmento en ninguno de los diecisiete casos, pero la causa no es la
ablación sino la consulta: la búsqueda de texto completo une los términos con conjunción y una
consulta de treinta palabras exige que las treinta aparezcan en el mismo fragmento. Se comprobó
por separado, sin filtros, y devuelve cero resultados. La comparación no aísla, por tanto, la
contribución de la similitud semántica. El resultado se conserva como inconcluso, sin reformular
la ablación a posteriori: una enmienda fechada y separada del pre-registro original declara una
variante con la consulta formada por los códigos de avería y los nombres de las señales, que será
una **medición nueva** con su propio criterio de validez, y no una corrección de esta.

Las dos ablaciones de la regla de decisión son las que dan sentido al criterio compuesto, y lo que
muestran se enuncia mejor al revés de como suele pensarse un sistema de diagnóstico: **una
confianza diagnóstica alta no basta para sostener una explicación si la evidencia documental no la
sostiene**. Con una puerta de confianza sola, el sistema explica **las doce ejecuciones que debían
terminar en abstención**, incluidas las tres en que la recuperación no devuelve ningún fragmento:
la confianza del modelo mide cuán seguro está de su diagnóstico y no sabe nada de si el manual lo
documenta. Sin criterio compuesto pero con la exigencia de que exista algún fragmento aplicable,
las explicaciones sin soporte bajan a **seis de nueve**, nueve de doce contando la condición con
distractor y filtro: tener documentación delante tampoco equivale a tener soporte. Las cifras de
la puerta de confianza sola coinciden celda a celda con la política de referencia que la Tabla 5.6
publica, calculada por otro camino; el pre-registro fijaba que una discrepancia obligaría a parar,
y no la hubo.

Ninguna de las cuatro dice nada sobre la separación entre decidir y redactar, que no se ablaciona,
y todas se miden sobre el conjunto con el que el criterio fue ajustado.

Por último, la corrección de la puerta de códigos de avería, implementada en septiembre y sin
medir hasta ahora, se midió con una segunda versión de la política en los tres modos. El cambio es
uno: el requisito de que el fragmento porte un código de avería del diagnóstico deja de exigirse
siempre y pasa a leerse de cómo esté declarado ese diagnóstico, que puede estar documentado con
códigos, documentado sin ellos o no estar declarado en absoluto.

Sobre los diecisiete casos no cambia ninguna decisión ni ningún motivo, porque los cinco
diagnósticos del conjunto están documentados con códigos y el requisito era ya el más estricto. Lo
que la nueva versión mejora es el **control de aplicabilidad ante un diagnóstico incorrecto**, y
ahí el efecto es grande. En el escenario adverso el modelo diagnostica «sin fallo», que el mapa no
declara: con la regla anterior la comprobación del código simplemente no se ejecutaba, y el
sistema aceptaba como soporte dos de las tres afirmaciones que había construido para un
diagnóstico equivocado, con una cobertura de 0,67; con la regla nueva el requisito se declara no
aplicable y ninguna afirmación obtiene soporte, de modo que la cobertura pasa a 0,00. Las seis
ejecuciones se abstenían antes y se abstienen después, pero antes se abstenían por un margen
—0,67 frente al umbral de 0,80— sobre evidencia que no debía haberse aceptado, y ahora se
abstienen porque no hay evidencia aplicable que aceptar. La prueba de regresión del repositorio
conserva las dos conductas a la vista, la anterior y la corregida.

## Discusión y análisis de los resultados
La discusión separa lo que los resultados sostienen de lo que no sostienen, y termina con el patrón que atraviesa el trabajo.

### Lo que los resultados sostienen
Sobre datos sintéticos parametrizados con el manual del vehículo y sobre la partición de validación, las cuatro subpreguntas alcanzan estados distintos, y conviene no unificarlos.

**PI.1 queda sostenida en su forma actual y no en la original.** El bosque aleatorio diagnostica por encima de la referencia mínima, con una exactitud de 0,878 frente a 0,286, y su confianza, infraconfiada en origen, queda calibrada, con un error de calibración que baja de 0,144 a 0,085. La formulación original de esta subpregunta, escrita antes de entrenar, pedía además que un modelo temporal superase a la línea base con un margen no atribuible al azar, y eso no ocurrió. La atribución describe bien tres de los cinco fallos y, en el fallo de encendido, arrastra señales que el mecanismo no justifica.

**PI.2 queda sostenida como trazabilidad, no como soporte medido.** Toda afirmación que el verificador admite conserva la observación que la origina y los fragmentos citados, y cada comprobación queda registrada por separado. Que esos fragmentos sostengan lo afirmado lo establecen las comprobaciones deterministas del propio verificador, no una medición independiente: si coinciden con un juicio externo no se ha medido, porque el conjunto anotado no incluye las afirmaciones admisibles. El vacío que motiva el trabajo, medir si cada afirmación se sostiene en su fragmento, queda así abordado por construcción y no por medición. En la explicación que redacta el modelo de lenguaje la correspondencia es más débil: no cita nada que no haya recibido, pero cita fragmentos que el verificador no aceptó.

**PI.3 queda sostenida en la muestra de validación, con dos salvedades.** La decisión cambia con la evidencia en la dirección correcta: sin evidencia documental aplicable, o con documentación que no sostiene las afirmaciones, el sistema se abstiene, y no explicó ninguno de los casos que debían terminar en abstención. La primera salvedad es que la condición de evidencia retirada produce la abstención por construcción, y el contraste que pone a prueba el criterio es el de la evidencia parcial. La segunda es que el criterio se revisó dos veces sobre los mismos casos, y su primera versión explicaba la mitad de los que debían abstenerse. El precio está en el otro error, dos abstenciones innecesarias de cinco, una por la confianza del modelo y otra por la confianza y por falta de soporte documental. Todo ello sobre cinco ventanas bien diagnosticadas; la evaluación final dirá si se mantiene.

**PI.4 no queda sostenida con el diseño actual.** Ningún fragmento de otro motor sostuvo una afirmación, con o sin filtro de motor. Pero la condición que debía medirlo, con el filtro activo, no añade en ninguno de los tres fallos un distractor que la condición parcial no tuviera, de modo que no manipula la variable que decía manipular. Sin filtro el distractor sí entra, y se rechaza por aplicabilidad en dos fallos y por vocabulario de la señal en el tercero. La novedad que el capítulo 3 atribuía a esta subpregunta es, en consecuencia, más estrecha, y la condición requiere un rediseño antes de sostener sobre ella una inferencia.

Aplicada la regla que el capítulo 4 fijó para la respuesta global, con PI.1, PI.2 y PI.3 en su forma actual y PI.4 sin sostener, la respuesta a la pregunta de investigación es **parcialmente sostenida**, con carácter provisional y sobre validación. La calificación descansa en criterios reescritos tras los primeros resultados, en una PI.2 que se cumple por construcción y en cifras de desarrollo; la evaluación final puede cambiarla. De los cinco desenlaces que la refutarían, el de la abstención trivial no se produjo: el sistema se abstiene en catorce de diecisiete casos, pero doce debían terminar en abstención y en los cinco con evidencia completa explica tres.

### Lo que no sostienen
No sostienen nada sobre el comportamiento en un vehículo real: caracterizan el mecanismo ante los fallos representados en el generador. Es la primera limitación del capítulo 6. No sostienen el comportamiento del agente cuando el diagnóstico de partida es erróneo, salvo en el escenario adverso descrito, anterior a la corrección del índice y construido sobre dos ventanas; con la política v2.2 ese escenario deja de aceptar soporte falso, y sigue siendo de dos ventanas. Tampoco sostienen que la abstención sea barata: dos de cinco casos con evidencia completa terminan en abstención, y esa cobertura, 3 de 5, es el precio de una falsa confianza nula en esta muestra. Un criterio más laxo en la confianza habría explicado cuatro de los cinco casos, entre ellos C01, cuyo diagnóstico el modelo acierta pero con una confianza calibrada de 0,60; la elección del umbral es una elección de política y se declara como tal. Ni sostienen que el adaptador del modelo de lenguaje generalice: se entrenó sobre ejemplos generados con la recuperación anterior a la corrección del índice y con ventanas que incluyen las de tres casos evaluados, dos en entrenamiento y una en validación, y no se ha reentrenado. Tampoco sostienen que el comportamiento observado se deba a separar la decisión de la redacción: sin ablaciones y sin una comparación con una abstención decidida por el propio modelo de lenguaje, lo medido es el comportamiento de un sistema que implementa esa separación.

### El patrón que atraviesa el trabajo
Varios de los errores relevantes del trabajo se detectaron mirando cifras que no cuadraban, no ejecutando pruebas automáticas: una exactitud de cero por un tipo de dato, una puntuación de fusión en otra escala, una condición ABSENT que seguía explicando, un código genérico que hacía parecer que la evidencia no existía, un efecto aparente del idioma que el filtro tapaba, un esquema que rechazaba respuestas correctas, un índice que mezclaba dos espacios vectoriales. Cada uno quedó registrado con su consecuencia si no se hubiera detectado, y varios habrían producido resultados falsos que parecían correctos. Es la misma observación que motiva la pregunta de investigación, aplicada al propio proceso de investigarla: la evidencia aparente no sobrevive siempre al escrutinio, y un sistema, o un investigador, que no distinga entre tener una referencia y tener soporte producirá afirmaciones con referencia y sin soporte.

Quedan para la evaluación final dos cosas que este capítulo no puede ofrecer todavía: la medición sobre el conjunto de prueba, que dirá si las cifras de validación se mantienen sobre datos no usados para fijar ningún umbral ni revisar el criterio, y la comparación con los trabajos del capítulo 3, que solo tiene sentido sobre resultados finales. De las ablaciones queda pendiente la variante de la recuperación léxica que la enmienda declara.