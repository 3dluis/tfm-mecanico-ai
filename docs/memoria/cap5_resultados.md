# Capítulo 5: Presentación de análisis, resultados y discusión
Todos los resultados de este capítulo proceden del vehículo de referencia definido en el capítulo 4, un Mazda 3 BK de 2007 con motor Z6, y de su corpus documental. No se han evaluado otros vehículos ni otras generaciones.

Todas las cifras de este capítulo proceden de la partición de **validación** de la muestra sintética descrita en el capítulo 4; el conjunto de prueba permanece cerrado y no se ha consultado. La procedencia del dato es sintética, y su validez externa se discute en el capítulo 6. Cada tabla cita el registro de ejecución del que sale. Los resultados son parciales: corresponden a las fases ejecutadas hasta la fecha, y la evaluación final sobre el conjunto de prueba, las ablaciones y la demostración integrada quedan pendientes.

Las cifras de recuperación y de suficiencia proceden de una reejecución realizada el 13 y el 14 de septiembre de 2026. El 4 de septiembre se detectó que el índice documental contenía dos representaciones vectoriales por fragmento y que ninguna búsqueda declaraba en cuál buscaba, de modo que la procedencia de cada fragmento recuperado era indeterminada. Se corrigió el defecto, se fijó por escrito y antes de medir qué se compararía y cómo se interpretaría, y se repitieron la recuperación, la suficiencia en sus dos modos, la generación del conjunto de ajuste y la redacción con el modelo de lenguaje sobre el mismo conjunto, modelo, umbral y política. Ninguna de las diecisiete decisiones cambió; los conjuntos de fragmentos recuperados cambiaron en diez de los diecisiete casos, siempre por adición. Con arreglo al criterio fijado de antemano, ese resultado se lee como ausencia de efecto detectable con este instrumento, no como confirmación del criterio de suficiencia. Los registros anteriores se conservan como históricos; la limitación figura como L-20 en el capítulo 6.

Una revisión anterior de este capítulo, el 10 de septiembre de 2026, había localizado cinco discrepancias entre el texto y los registros que citaba. Se resolvieron en esta versión citando en cada caso el registro vigente y dejando constancia del cambio donde aparece: las cifras del modelo de diagnóstico, que difieren de los informes de fase; la tabla de recuperación, regenerada desde el registro; las latencias del modelo de lenguaje, calculadas ahora sobre los registros; el umbral de confianza, que una enmienda posterior había movido; y la matriz de decisiones, que recogía nueve de los diecisiete casos y una celda de una versión anterior del verificador.

Conviene además una advertencia sobre la comparación entre estrategias de recuperación que sigue. La estrategia que gana acota su búsqueda con los códigos de avería que documentan la condición **anotada**, información que el sistema no tiene antes de diagnosticar. Su ventaja mide, por tanto, una cota superior asistida por esa anotación y no una capacidad de recuperación comparable con las demás. La ejecución no oracular, en la que esos códigos se derivan del diagnóstico del modelo y no de la anotación, produjo el mismo vector de decisiones en la fase de suficiencia; se presenta más abajo.

## Análisis descriptivo de la muestra
La muestra sintética consta de 72 sesiones de 600 segundos, 12 por condición, muestreadas a 1 Hz; ventanadas a 120 segundos con solape produce 392 ventanas de entrenamiento y 98 de validación, con 139 descriptores por ventana. El reparto es por sesión, y por eso ninguna ventana de validación comparte sesión con una de entrenamiento.

El análisis exploratorio previo al modelado dejó dos hechos que condicionan la lectura de todo lo demás. El primero es que dos de los cinco fallos no son visibles en las medias de las señales: el fallo de encendido y el termostato bloqueado abierto solo se distinguen de la condición sin fallo por la dispersión o por la evolución temporal, no por el nivel. El segundo es que el termostato tiene un límite físico de detección: mientras el motor no habría superado por sí mismo la temperatura a la que el fallo lo limita, la señal averiada es idéntica a la sana. En esas ventanas la respuesta correcta del sistema es abstenerse, y no hubo que fabricar el caso.

El estudio de ventana del capítulo 4 fijó 120 segundos como longitud en la que los descriptores separables coinciden con los mecanismos físicos declarados para cada fallo. En particular, la deriva del caudalímetro no se detecta en el caudal medido sino en las correcciones de combustible con que la centralita la compensa. Esto condiciona qué puede afirmar legítimamente el agente: «el caudalímetro deriva porque el caudal es bajo» sería falso, y las plantillas de afirmación del verificador no permiten formularlo.

## Resultados obtenidos
Los resultados se presentan por subpregunta, PI.1 a PI.4, y se cierran con la medición del modelo de lenguaje. Primero lo observado; después su interpretación.

### PI.1 · Diagnóstico y calibración
| Modelo | Exactitud | F1 macro | Registro |
| --- | --- | --- | --- |
| Referencia mínima (clase mayoritaria) | 0,286 | 0,074 | `E6_baseline_synthetic_v2.json` |
| Bosque aleatorio, 139 descriptores | 0,878 | 0,879 | `E6_baseline_synthetic_v2.json` |
| GRU bidireccional sobre secuencias | 0,827 | 0,823 | `E7_temporal_synthetic_v2.json` |

Los informes de fase del modelo de diagnóstico daban cifras ligeramente distintas (F1 0,876 para el bosque; exactitud 0,806 y F1 0,822 para la red recurrente), procedentes de una ejecución anterior que una ejecución posterior sustituyó sin que el informe se actualizara. La tabla cita los registros vigentes, y el del bosque se reprodujo bit a bit el 14 de septiembre de 2026 con la misma semilla.

El modelo temporal no supera al tabular. Por clase, sin embargo, gana en el termostato bloqueado, justo donde el análisis exploratorio anticipó que un modelo secuencial podía aportar; con este volumen de datos la complejidad añadida no está justificada en agregado, y se conserva el bosque como modelo de diagnóstico. Todos los errores del bosque van a la condición «sin fallo»: el modelo no produce diagnósticos cruzados, lo que para un sistema que va a explicar es la dirección de error menos dañina.

El fallo de encendido se detecta en la mitad de los casos. El resultado estaba anticipado por escrito antes de medirlo, con su motivo cuantificado en el estudio de ventana, y no se aumentó la severidad del fallo para mejorar la cifra: un trabajo sobre suficiencia de evidencia necesita casos difíciles.

La confianza del bosque estaba mal calibrada, y en la dirección menos habitual:

|  | ECE | Confianza media | Acierto | Sesgo |
| --- | --- | --- | --- | --- |
| Sin calibrar | 0,144 | 0,738 | 0,878 | −0,140 |
| Calibrado (isotónica, validación cruzada sobre entrenamiento) | 0,085 | 0,886 | 0,878 | +0,009 |

Registro: `E15_suficiencia.json`. El modelo estaba infraconfiado. Como esa confianza alimenta el criterio de suficiencia, un umbral sobre la confianza cruda habría hecho que el agente se abstuviera de más, y habría parecido prudencia cuando era mala medición. La calibración pasó de refinamiento a precondición.

### PI.2 · Recuperación y trazabilidad
La recuperación semántica pura no encuentra el procedimiento correcto del manual entre los diez primeros resultados en ningún caso. Guiar la consulta con los códigos de avería que el manual asocia al diagnóstico lo encuentra siempre:

| Estrategia | P@10 | R@10 | MRR | Hit@10 | nDCG@10 |
| --- | --- | --- | --- | --- | --- |
| Semántica | 0,000 | 0,000 | 0,000 | 0,00 | 0,000 |
| Semántica con filtro de motor | 0,020 | 0,200 | 0,040 | 0,20 | 0,149 |
| Semántica con filtro de autoridad | 0,040 | 0,400 | 0,107 | 0,40 | 0,468 |
| Híbrida (semántica y léxica, fusión por rango recíproco) | 0,040 | 0,400 | 0,107 | 0,40 | 0,468 |
| Guiada por el diagnóstico | 0,260 | 1,000 | 0,467 | 1,00 | 0,653 |

Registro: `E12_retrieval.json`, reejecución del 13 de septiembre de 2026 sobre los seis casos anotados de esa fase, de los que cinco se puntúan; el sexto, con la evidencia retirada del índice, se evalúa pero no entra en las métricas porque no tiene fichero relevante. Una tabla anterior de este capítulo, tomada del informe de fase del 1 de septiembre, contenía cuatro estrategias y valores que no se reproducían desde el registro; se sustituye por la del registro. La única celda que cambió con la reejecución fue el nDCG de la estrategia guiada, de 0,642 a 0,653. La lectura es que, sobre documentación técnica, la similitud semántica entre una consulta en lenguaje natural y un procedimiento de taller es baja, y lo que los une es un identificador exacto. El sistema final usa la estrategia guiada, con la híbrida como respaldo.

El idioma de la consulta importa, y el filtro por código de avería lo ocultaba: con el filtro activo, todas las estrategias dan Hit@10 de 1,00 en todos los idiomas. Medido sin filtro, buscando el documento relevante entre los 500 primeros resultados:

| Modelo de embeddings | Consulta | Hallados | Posición mediana |
| --- | --- | --- | --- |
| Monolingüe inglés | inglés | 5/5 | 47 |
| Monolingüe inglés | español | 1/5 | 376 |
| Multilingüe | inglés | 4/5 | 58 |
| Multilingüe | español | 4/5 | 54 |

Esta medición procede del informe de la fase de ingesta y no dispone de un registro de ejecución con versión del código; no se ha reproducido y se presenta como observación descriptiva, no como resultado verificado. El modelo monolingüe seguía devolviendo resultados con puntuaciones de aspecto razonable para consultas en español, y eran casualidad. Es un caso más del patrón que el trabajo estudia: evidencia aparente que no sobrevive al escrutinio.

En cuanto a trazabilidad, sobre el registro vigente de suficiencia el verificador construyó 51 afirmaciones, tres por caso, y las 51 conservan la observación de la telemetría que las origina. De ellas, 12 disponen de un fragmento documental aplicable que las sostiene, y las 12 son las de los cuatro casos con evidencia completa en los que el criterio la encontró; en los doce casos con evidencia parcial, ausente o con distractor, ninguna afirmación obtuvo soporte documental, que es lo que esas condiciones están diseñadas para producir. La proporción de afirmaciones con cita cuya cita las sostiene es de 12 sobre 12: toda afirmación admitida se ancla en una observación existente y en un fragmento aplicable que menciona la señal, tiene contenido diagnóstico y porta un código de la condición. La corrección merece contarse porque fue un error del instrumento y no del sistema: el mapeo inicial asociaba la deriva del caudalímetro a los códigos de tensión del sensor, mientras el modelo la observa en las correcciones de combustible, y la cobertura era 0,00 hasta añadir los códigos de mezcla pobre. Y hubo un segundo error, más instructivo: se afirmó en cuatro informes que el manual no documentaba la fuga de vacío porque no contenía el código genérico P0171; el propio sistema la encontró después bajo el código específico del fabricante, P2187. Los cuatro informes conservan la afirmación falsa tachada.

### PI.3 y PI.4 · Suficiencia, abstención y distractores
Diecisiete casos anotados, con el criterio de suficiencia en su tercera versión y calibrado sobre validación. El umbral de confianza calibrada es 0,79: el criterio original elegía el umbral más bajo con precisión de decisión igual o superior a 0,93, que daba 0,72, y una enmienda fijada antes de reejecutar exigió además que el objetivo se mantuviera en todo el tramo de cinco centésimas siguiente, porque 0,72 lo cumplía por una sola ventana. El umbral de puntuación de recuperación está desactivado porque no discrimina. Una versión anterior de esta tabla publicaba 0,80 y nueve casos.

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

Registro: `E15_suficiencia.json`, modo oracular, reejecución del 13 de septiembre de 2026. Quince decisiones correctas de diecisiete. Los dos tipos de error, contados por separado y con su denominador:

| Error | Definición | Casos | Tasa |
| --- | --- | --- | --- |
| Falsa confianza (T_FC) | explica cuando debía abstenerse | 0 de los 12 casos que debían terminar en abstención | 0,00 |
| Abstención innecesaria (T_AI) | se abstiene cuando debía explicar | 2 de los 5 casos que debían terminar en explicación | 0,40 |

La cobertura de la explicación sobre los casos con evidencia completa es, en consecuencia, de 3 de 5. El modo no oracular, en el que los códigos de avería que acotan la búsqueda y exige el verificador salen del diagnóstico del modelo y no de la anotación, produjo exactamente el mismo vector de decisiones y las mismas dos tasas (registro `E15_suficiencia_non_oracle.json`). En un escenario adverso registrado el 4 de septiembre, sobre las seis ventanas de validación que el modelo clasifica mal con mayor confianza, todas en la condición sin fallo, el sistema se abstuvo en las seis; la falsa confianza fue 0 de 6, pero el análisis de ese escenario reveló que, cuando el diagnóstico no tiene códigos de avería asociados, una de las cuatro comprobaciones de soporte se omite en silencio, defecto registrado y todavía sin medir su corrección.

Lo central está en las filas C05 a C09, y se repite en C10 a C13 y en C14 a C17. Es **el mismo caso**, la misma ventana, el mismo modelo, la misma atribución y la misma confianza calibrada. Lo único que cambia es qué hay en el índice. Con la evidencia, el agente explica; retirada, la recuperación no la encuentra y el agente se abstiene por ausencia de evidencia documental aplicable; con evidencia parcial o con un distractor, el agente encuentra documentos, y se abstiene igual, porque ninguno de ellos sostiene las afirmaciones: la cobertura es 0,00 aunque haya cinco o siete documentos aplicables delante. Ese contraste es el que el diseño aísla, y no depende de la interpretación.

Los dos errores son abstenciones innecesarias en condición FULL, C01 y C04, y ambas por el mismo motivo: la confianza calibrada del modelo queda por debajo del umbral. Son los dos fallos que el análisis exploratorio marcó como difíciles. No son errores del criterio de evidencia sino del modelo de diagnóstico, y la abstención es, en ese caso, la respuesta prudente: el sistema no sabe con suficiente seguridad qué fallo es, y lo dice. Un umbral más bajo habría explicado los cinco casos con evidencia y también habría expuesto al usuario a dos diagnósticos que el modelo no distingue bien; la elección del umbral es una elección de política y se declara como tal.

Sobre los distractores, la recuperación semántica pura coloca un procedimiento del motor LF por encima del correcto de los motores ZJ y Z6 en un caso; con el filtro de motor activo, ninguno. El diagnóstico de la condición, realizado sobre la recuperación reejecutada con dos criterios fijados de antemano, dio un resultado desigual. Con el filtro de motor activo, la condición con distractor recuperó exactamente los mismos fragmentos que la condición parcial en el termostato y en la sonda de oxígeno, y solo en la fuga de vacío entró un fragmento del fichero distractor; en esos dos fallos la condición no manipula, por tanto, ninguna variable distinta de la parcial. Sin el filtro, un fragmento del otro motor entró en los tres fallos, el validador de aplicabilidad lo degradó a coincidencia parcial, que el criterio no admite como evidencia, y el agente se abstuvo en los tres.

Sería tentador leer eso como dos líneas de defensa independientes, y la revisión posterior mostró que no lo son. El filtro de motor no protege como se creía: con él activo, un procedimiento del motor incorrecto puede llegar a examinarse con coincidencia exacta, y lo que lo detiene es el vocabulario de la señal. Lo que sí queda comprobado es que el fragmento del otro motor no llega a sostener una afirmación en ninguno de los casos evaluados; el mecanismo que lo impide es la exigencia de coincidencia exacta al construir las afirmaciones, y no la combinación de filtro y verificador que este pasaje sugería.

### El modelo de lenguaje: respeta la decisión y no inventa citas
El modelo de lenguaje se midió con el mismo motor de inferencia, los mismos parámetros deterministas y las mismas preguntas en tres configuraciones: el modelo base, el modelo con el primer adaptador y el modelo con el segundo. Una primera medición reveló un fallo del esquema de salida, que no admitía los motivos de abstención que emite el verificador; se corrigió y se repitieron las tres mediciones sobre los nueve casos entonces anotados. Tras ampliar el conjunto a diecisiete casos y corregir el índice documental, las tres configuraciones se midieron de nuevo el 14 de septiembre de 2026 con el mismo adaptador, sin reentrenarlo.

| Configuración | Casos | Salidas válidas | Respeta el veredicto | Citas inexistentes | Fallos de esquema | Latencia media |
| --- | --- | --- | --- | --- | --- | --- |
| Base | 9 | 7/9 | 7/7 evaluables | 0 | 2 | 26,8 s |
| Base con adaptador v1 | 9 | 7/9 | 7/7 evaluables | 0 | 2 | 20,7 s |
| Base con adaptador v2 | 9 | 9/9 | 9/9 | 0 | 0 | 26,7 s |
| Base | 17 | 15/17 | 15/15 evaluables | 0 | 2 | 8,7 s |
| Base con adaptador v1 | 17 | 11/17 | 11/11 evaluables | 0 | 6 | 11,1 s |
| Base con adaptador v2 | 17 | 17/17 | 17/17 | 0 | 0 | 13,4 s |

Registros: `E13_agente_transformers*.json` en su versión del 4 de septiembre de 2026, nueve casos, y en la del 14 de septiembre, diecisiete casos. Sobre los nueve casos comunes, la segunda medición reproduce la primera para el modelo base y para el segundo adaptador, y el primer adaptador pierde una salida válida. Una versión anterior de esta tabla decía que el modelo base y el primer adaptador respetaban el veredicto en 9 de 9 casos y publicaba latencias que ningún registro producía; el veredicto no es evaluable en una salida que no cumple el esquema, de modo que la cifra correcta es 7 de 7 evaluables, y las latencias son ahora las medias de los registros. Los dos adaptadores modifican el 0,24 % de los parámetros, solo en las proyecciones de atención, con 55 ejemplos de entrenamiento derivados de ejecuciones del propio pipeline y cero fugas de texto del manual en las salidas de entrenamiento; el conjunto de ajuste se regeneró sobre la recuperación corregida, con 66 ejemplos, y el adaptador no se ha reentrenado sobre él.

Tres lecturas. Primera: **ninguna de las tres configuraciones produjo una cita inexistente**, y no lo consiguió el ajuste, lo garantiza la barrera externa que rechaza cualquier identificador que no corresponda a algo entregado. Segunda: el ajuste cambió la forma de la explicación hacia la buscada. El modelo base, en su único caso explicativo válido, cuelga las cinco observaciones de una misma afirmación y parafrasea el manual como si fuera afirmación propia; el ajustado produce tres afirmaciones, cada una con una observación y dos fragmentos, sin parafrasear y sin atribuir causa, en un tercio del tiempo máximo. Tercera: el primer adaptador no mejoró el recuento porque cambió los fallos de sitio, y la causa estaba en los datos de ajuste, no en el modelo. El objetivo de entrenamiento traducía el motivo de abstención a un vocabulario genérico mientras el prompt mostraba el literal; el modelo intentaba copiar el prompt y deformaba el identificador. El segundo adaptador cambia solo eso, y pasa de 7 a 9; sobre los diecisiete casos, el defecto del primero se manifiesta en seis salidas y el segundo mantiene las diecisiete válidas.

## Discusión y análisis de los resultados
La discusión separa lo que los resultados sostienen de lo que no sostienen, y termina con el patrón que atraviesa el trabajo.

### Lo que los resultados sostienen
Sobre datos sintéticos calibrados contra el manual del vehículo, las cuatro subpreguntas alcanzan estados distintos, y conviene no unificarlos.

**PI.1 queda sostenida.** El modelo diagnostica muy por encima de la referencia mínima y su confianza, una vez calibrada, significa lo que aparenta.

**PI.2 queda sostenida en los casos evaluados.** Toda afirmación admitida se rastrea hasta una observación y un fragmento que la sostienen, y cada comprobación queda registrada por separado. Sobre el registro vigente, las 51 afirmaciones conservan su observación, 12 disponen de soporte documental y las 12 citas sostienen lo afirmado; la distancia entre completitud y soporte, que es donde aparecería una referencia decorativa, es cero en esta muestra. Es una medida de validación sobre diecisiete casos y no se extrapola.

**PI.3 queda sostenida.** La decisión de explicar cambia cuando se retira la evidencia, con todo lo demás idéntico, y lo hace en la dirección correcta en los doce casos que debían terminar en abstención: la falsa confianza es nula en la muestra. El precio está en el otro error, dos abstenciones innecesarias de cinco, y las dos proceden de la confianza del modelo, no del criterio de evidencia. Es el contraste más firme del trabajo, y sobrevivió a las tres versiones del criterio de suficiencia y a la reejecución con el índice corregido.

**PI.4 queda parcialmente sostenida y con una salvedad de diseño.** El procedimiento del motor incorrecto no llega a sostener una afirmación en ningún caso, con o sin filtro de motor. Pero la condición que debía medirlo, con el filtro activo, recupera en dos de los tres fallos exactamente los mismos fragmentos que la condición de evidencia parcial, de modo que en ellos no manipula la variable que decía manipular; solo sin filtro el distractor entra en los tres fallos y es rechazado por el validador de aplicabilidad. La novedad que el capítulo 3 atribuía a esta subpregunta es, en consecuencia, más estrecha, y la condición requiere un rediseño antes de sostener sobre ella una inferencia.

El modelo de lenguaje, que es la pieza en la que los trabajos revisados sitúan el riesgo, respeta la decisión en las ejecuciones cuya salida pudo evaluarse y no inventa citas en ninguna.

### Lo que no sostienen
No sostienen nada sobre el comportamiento en un vehículo real: caracterizan el mecanismo ante los fallos representados en el generador. Es la primera limitación del capítulo 6. Tampoco sostienen que la abstención sea barata: dos de cinco casos con evidencia completa terminan en abstención por falta de confianza del modelo, y esa cobertura, 3 de 5, es el precio de una falsa confianza nula. Un criterio más laxo habría explicado los cinco y habría explicado dos fallos que el modelo no distingue bien. La elección del umbral es una elección de política y está declarada como tal. Ni sostienen que el adaptador del modelo de lenguaje sea definitivo: se entrenó sobre ejemplos generados con la recuperación anterior a la corrección del índice, y aunque su comportamiento no cambió sobre la recuperación corregida, no se ha reentrenado.

### El patrón que atraviesa el trabajo
Casi todos los errores relevantes del trabajo se detectaron mirando cifras que no cuadraban, no ejecutando pruebas automáticas: una exactitud de cero por un tipo de dato, una puntuación de fusión en otra escala, una condición ABSENT que seguía explicando, un código genérico que hacía parecer que la evidencia no existía, un idioma cuyo efecto el filtro tapaba, un esquema que rechazaba respuestas correctas, un índice que mezclaba dos espacios vectoriales. Cada uno quedó registrado con su consecuencia si no se hubiera detectado, y varios habrían producido resultados falsos que parecían correctos. Esa es, en el fondo, la misma observación que motiva la pregunta de investigación, aplicada al propio proceso de investigarla: la evidencia aparente no sobrevive siempre al escrutinio, y un sistema, o un investigador, que no distinga entre tener una referencia y tener soporte producirá texto impecable y falso.

Quedan para la evaluación final tres cosas que este capítulo no puede ofrecer todavía: las ablaciones, que atribuirán el resultado a cada componente; la medición sobre el conjunto de prueba, que dirá si las cifras de validación se mantienen sobre datos no usados para fijar ningún umbral; y la comparación con los trabajos del capítulo 3, que solo tiene sentido sobre resultados finales.