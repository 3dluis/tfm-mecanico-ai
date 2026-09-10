# Capítulo 5: Presentación de análisis, resultados y discusión

Todos los resultados de este capítulo proceden del vehículo de referencia definido en el
capítulo 4, un Mazda 3 BK de 2007 con motor Z6, y de su corpus documental. No se han evaluado
otros vehículos ni otras generaciones.

Todas las cifras de este capítulo proceden de la partición de **validación** del conjunto
`synthetic_v2`; el conjunto de test permanece cerrado y no se ha consultado. La procedencia del
dato es sintética, y su validez externa se discute en el capítulo 6. Cada tabla cita el registro
del que sale.

Dos magnitudes discrepan entre el informe de fase y su registro, y **no se han resuelto
eligiendo una de las dos**: quedan señaladas donde aparecen, porque la discrepancia es en sí un
resultado sobre la trazabilidad del trabajo.

## Análisis descriptivo de la muestra

La muestra sintética consta de 72 sesiones de 600 segundos, 12 por condición, muestreadas a
1 Hz; ventanadas a 120 segundos con solape produce 392 ventanas de entrenamiento y 98 de
validación, con 139 descriptores por ventana. El reparto es por sesión, y por eso ninguna
ventana de validación comparte sesión con una de entrenamiento.

El análisis exploratorio previo al modelado dejó dos hechos que condicionan la lectura de
todo lo demás. El primero es que dos de los cinco fallos no son visibles en las medias de las
señales: el fallo de encendido y el termostato bloqueado abierto solo se distinguen de la
condición sin fallo por la dispersión o por la evolución temporal, no por el nivel. El
segundo es que el termostato tiene un límite físico de detección: mientras el motor no
habría superado por sí mismo la temperatura a la que el fallo lo limita, la señal averiada
es idéntica a la sana. En esas ventanas la respuesta correcta del sistema es abstenerse, y no
hubo que fabricar el caso.

El estudio de ventana del capítulo 4 fijó 120 segundos como longitud en la que los
descriptores separables coinciden con los mecanismos físicos declarados para cada fallo. En
particular, la deriva del caudalímetro no se detecta en el caudal medido sino en las
correcciones de combustible con que la centralita la compensa. Esto condiciona qué puede
afirmar legítimamente el agente: «el caudalímetro deriva porque el caudal es bajo» sería
falso, y las plantillas de afirmación del verificador no permiten formularlo.

## Resultados obtenidos

Los resultados se presentan por subpregunta, PI.1 a PI.4, y se cierran con la medición del
modelo de lenguaje. En este apartado se describe lo observado; su interpretación va en el
siguiente.

### PI.1 · Diagnóstico y calibración

| Modelo | Exactitud | F1 macro | Registro |
|---|---|---|---|
| Referencia mínima (clase mayoritaria) | 0,286 | 0,074 | `E6_baseline_synthetic_v2.json` |
| Bosque aleatorio, 139 descriptores | **0,878** | **0,879** | `E6_baseline_synthetic_v2.json` |
| GRU bidireccional sobre secuencias | 0,827 | 0,823 | `E7_temporal_synthetic_v2.json` |

`[RECONCILIAR]` El informe `E6_baseline.md` da F1 0,876 y el informe `E7_modelo_temporal.md`
da para la GRU exactitud 0,806 y F1 0,822; los registros JSON dan las cifras de la tabla. Se
citan los registros por regla del proyecto, y la diferencia debe explicarse (probablemente
una ejecución anterior del informe) antes del depósito.

El modelo temporal no supera al tabular. Por clase, sin embargo, gana en el termostato
bloqueado, justo donde el análisis exploratorio anticipó que un modelo secuencial podía
aportar; con este volumen de datos la complejidad añadida no está justificada en agregado, y
se conserva el bosque como modelo de diagnóstico. Todos los errores del bosque van a la
condición «sin fallo»: el modelo no produce diagnósticos cruzados, lo que para un sistema que
va a explicar es la dirección de error menos dañina.

El fallo de encendido se detecta en la mitad de los casos. El resultado estaba anticipado
por escrito antes de medirlo, con su motivo cuantificado en el estudio de ventana, y no se
aumentó la severidad del fallo para mejorar la cifra: un trabajo sobre suficiencia de
evidencia necesita casos difíciles.

La confianza del bosque estaba mal calibrada, y en la dirección menos habitual:

| | ECE | Confianza media | Acierto | Sesgo |
|---|---|---|---|---|
| Sin calibrar | 0,144 | 0,738 | 0,878 | −0,140 |
| Calibrado (isotónica, validación cruzada sobre entrenamiento) | **0,085** | 0,886 | 0,878 | +0,009 |

Registro: `E15_suficiencia.json`. El modelo estaba infraconfiado. Como esa confianza
alimenta el criterio de suficiencia, un umbral sobre la confianza cruda habría hecho que el
agente se abstuviera de más, y habría parecido prudencia cuando era mala medición. La
calibración pasó de refinamiento a precondición.

### PI.2 · Recuperación y trazabilidad

La recuperación semántica pura no encuentra el procedimiento correcto del manual entre los
diez primeros resultados en ningún caso. Guiar la consulta con los códigos de avería que el
manual asocia al diagnóstico lo encuentra siempre:

| Estrategia | P@10 | R@10 | MRR | Hit@10 | nDCG@10 |
|---|---|---|---|---|---|
| Semántica | 0,000 | 0,000 | 0,000 | 0,00 | 0,224 |
| Semántica con filtro de motor | 0,000 | 0,000 | 0,000 | 0,00 | 0,312 |
| Híbrida (semántica y léxica, fusión por rango recíproco) | 0,025 | 0,250 | 0,125 | 0,25 | 0,531 |
| **Guiada por el diagnóstico** | **0,250** | **1,000** | **0,446** | **1,00** | **0,658** |

Registro: `E12_evaluacion_recuperacion.md`, sobre los cinco casos anotados en esa fase. La
lectura es que, sobre documentación técnica, la similitud semántica entre una consulta en
lenguaje natural y un procedimiento de taller es baja, y lo que los une es un identificador
exacto. El sistema final usa la estrategia guiada, con la híbrida como respaldo.

El idioma de la consulta importa, y el filtro por código de avería lo ocultaba: con el
filtro activo, todas las estrategias dan Hit@10 de 1,00 en todos los idiomas. Medido sin
filtro, buscando el documento relevante entre los 500 primeros resultados:

| Modelo de embeddings | Consulta | Hallados | Posición mediana |
|---|---|---|---|
| Monolingüe inglés | inglés | 5/5 | 47 |
| Monolingüe inglés | **español** | **1/5** | **376** |
| Multilingüe | inglés | 4/5 | 58 |
| Multilingüe | **español** | **4/5** | **54** |

Registro: `docs/rag/multilingual.md`. El modelo monolingüe seguía devolviendo resultados con
puntuaciones de aspecto razonable para consultas en español, y eran casualidad. Es un caso
más del patrón que el trabajo estudia: evidencia aparente que no sobrevive al escrutinio.

En cuanto a trazabilidad, tras corregir el mapeo entre diagnóstico y códigos de avería, la
cobertura de afirmaciones con soporte verificado es de 1,00 en las cinco condiciones con
evidencia disponible: toda afirmación admitida se ancla en una observación existente y en un
fragmento aplicable que menciona la señal, tiene contenido diagnóstico y porta un código de
la condición. La corrección merece contarse porque fue un error del instrumento y no del
sistema: el mapeo inicial asociaba la deriva del caudalímetro a los códigos de tensión del
sensor, mientras el modelo la observa en las correcciones de combustible, y la cobertura era
0,00 hasta añadir los códigos de mezcla pobre. Y hubo un segundo error, más instructivo: se
afirmó en cuatro informes que el manual no documentaba la fuga de vacío porque no contenía el
código genérico P0171; el propio sistema la encontró después bajo el código específico del
fabricante, P2187. Los cuatro informes conservan la afirmación falsa tachada.

### PI.3 y PI.4 · Suficiencia, abstención y distractores

Nueve casos anotados, con el criterio de suficiencia calibrado sobre validación (umbral de
confianza calibrada 0,80, elegido como el más bajo con precisión de decisión igual o superior
a 0,93; umbral de puntuación de recuperación desactivado porque no discrimina):

| Caso | Condición | Confianza | Documentos aplicables | Cobertura | Esperado | Decidido |
|---|---|---|---|---|---|---|
| C01 deriva de caudalímetro | FULL | 0,600 | 6 | 1,00 | EXPLAIN | ABSTAIN |
| C02 termostato | FULL | 1,000 | 7 | 1,00 | EXPLAIN | EXPLAIN |
| C03 sonda lenta | FULL | 1,000 | 6 | 1,00 | EXPLAIN | EXPLAIN |
| C04 fallo de encendido | FULL | 0,462 | 4 | 1,00 | EXPLAIN | ABSTAIN |
| C05 fuga de vacío | FULL | 0,908 | 5 | 1,00 | EXPLAIN | EXPLAIN |
| C06 fuga, evidencia retirada | ABSENT | 0,908 | 0 | 0,00 | ABSTAIN | ABSTAIN |
| C07 fuga, evidencia parcial | PARTIAL | 0,908 | 4 | 0,00 | ABSTAIN | ABSTAIN |
| C08 fuga, distractor | DISTRACTOR | 0,908 | 4 | 0,00 | ABSTAIN | ABSTAIN |
| C09 fuga, distractor sin filtro de motor | DISTRACTOR | 0,908 | 1 | 0,00 | ABSTAIN | ABSTAIN |

Registro: `tables/E15_suficiencia.csv`, `experiments/E15_suficiencia.json`. Siete decisiones
correctas de nueve.

Lo central está en las filas C05 a C09. Es **el mismo caso**, la misma ventana, el mismo
modelo, la misma atribución y la misma confianza calibrada de 0,908. Lo único que cambia es
qué hay en el índice. Con la evidencia, el agente explica; retirada, la recuperación no la
encuentra y el agente se abstiene por ausencia de evidencia documental aplicable; con
evidencia parcial o con un distractor, el agente encuentra documentos, y se abstiene igual,
porque ninguno de ellos sostiene las afirmaciones: la cobertura es 0,00 aunque haya cuatro
documentos delante. Ese es el experimento central de defensa, y el contraste se ve sin
explicarlo.

Los dos errores son abstenciones injustificadas en condición FULL, C01 y C04, y ambas por
el mismo motivo: la confianza calibrada del modelo queda por debajo del umbral. Son los dos
fallos que el análisis exploratorio marcó como difíciles. No son errores del criterio de
evidencia sino del modelo de diagnóstico, y la abstención es, en ese caso, la respuesta
honesta: el sistema no sabe con suficiente seguridad qué fallo es, y lo dice. Cobertura de
la explicación sobre los casos con evidencia: 3 de 5.

Sobre los distractores, la recuperación semántica pura coloca un procedimiento del motor LF
por encima del correcto de los motores ZJ y Z6 en un caso; con el filtro de motor activo,
ninguno. Y cuando el filtro se desactiva a propósito, en C09, el validador de aplicabilidad
degrada el fragmento del otro motor a coincidencia parcial, que el criterio no admite como
evidencia, y el agente se abstiene igual. Son dos líneas de defensa independientes.

### El modelo de lenguaje: respeta la decisión y no inventa citas

El modelo de lenguaje se midió tres veces con el mismo motor de inferencia, los mismos
parámetros deterministas y las mismas nueve preguntas: el modelo base, el modelo con el
primer adaptador y el modelo con el segundo. La primera medición reveló un fallo del esquema
de salida, que no admitía los motivos de abstención que emite el verificador; se corrigió y
se repitieron las tres mediciones.

| Configuración | Salidas válidas | Respeta el veredicto | Citas inexistentes | Fallos de esquema | Latencia media |
|---|---|---|---|---|---|
| Base | 7/9 | 9/9 | 0 | 2 | 20,4 s |
| Base con adaptador v1 | 7/9 | 9/9 | 0 | 2 | 14,7 s |
| **Base con adaptador v2** | **9/9** | 9/9 | 0 | **0** | 13,1 s |

Registros: `experiments/E13_agente_transformers*.json`. Los dos adaptadores modifican el
0,24 % de los parámetros, solo en las proyecciones de atención, con 55 ejemplos de
entrenamiento derivados de ejecuciones del propio pipeline y cero fugas de texto del manual
en las salidas de entrenamiento.

Tres lecturas. Primera: **ninguna de las tres configuraciones produjo una cita inexistente**,
y no lo consiguió el ajuste, lo garantiza la barrera externa que rechaza cualquier
identificador que no corresponda a algo entregado. Segunda: el ajuste cambió la forma de la
explicación hacia la buscada. El modelo base, en su único caso explicativo válido, cuelga las
cinco observaciones de una misma afirmación y parafrasea el manual como si fuera afirmación
propia; el ajustado produce tres afirmaciones, cada una con una observación y dos fragmentos,
sin parafrasear y sin atribuir causa, en un tercio del tiempo máximo. Tercera: el primer
adaptador no mejoró el recuento porque cambió los fallos de sitio, y la causa estaba en los
datos de ajuste, no en el modelo. El objetivo de entrenamiento traducía el motivo de
abstención a un vocabulario genérico mientras el prompt mostraba el literal; el modelo
intentaba copiar el prompt y deformaba el identificador. El segundo adaptador cambia solo eso,
y pasa de 7 a 9.

## Discusión y análisis de los resultados

La discusión separa lo que los resultados sostienen de lo que no sostienen, y termina con
el patrón que atraviesa el trabajo.

### Lo que los resultados sostienen

Sobre datos sintéticos calibrados contra el manual del vehículo, las cuatro subpreguntas
quedan sostenidas, con matices que conviene no perder. El modelo diagnostica muy por
encima de la referencia mínima y su confianza, una vez calibrada, significa lo que aparenta
(PI.1). Toda afirmación admitida es trazable hasta una observación y un fragmento que la
sostienen, y la distancia entre completitud y soporte es cero (PI.2). La decisión de explicar
cambia cuando se retira la evidencia, con todo lo demás idéntico (PI.3). Y la evidencia
parecida pero incorrecta no se acepta, ni por la recuperación con filtro ni, sin él, por el
validador de aplicabilidad (PI.4). El modelo de lenguaje, que es la pieza en la que la
literatura sitúa el riesgo, respeta la decisión en todos los casos y no inventa citas en
ninguno.

### Lo que no sostienen

No sostienen nada sobre el comportamiento en un vehículo real: caracterizan el mecanismo
ante los fallos representados en el generador. Es la primera limitación del capítulo 6. Tampoco sostienen que la
abstención sea barata: dos de cinco casos con evidencia completa terminan en abstención por
falta de confianza del modelo, y esa cobertura, 3 de 5, es el precio de que las dos
abstenciones sean honestas. Un criterio más laxo habría explicado los cinco y habría
explicado dos fallos que el modelo no distingue bien. La elección del umbral es una elección
de política y está declarada como tal.

### El patrón que atraviesa el trabajo

Casi todos los errores relevantes del proyecto se detectaron mirando cifras que no
cuadraban, no ejecutando tests: una exactitud de cero por un tipo de dato, una puntuación de
fusión en otra escala, una condición ABSENT que seguía explicando, un código genérico que
hacía parecer que la evidencia no existía, un idioma cuyo efecto el filtro tapaba, un esquema
que rechazaba respuestas correctas. Se listan en el paso a paso del experimento con su
consecuencia si no se hubieran detectado, y varios habrían producido resultados falsos que
parecían correctos. Esa es, en el fondo, la misma observación que motiva la pregunta de
investigación, aplicada al propio proceso de investigarla: la evidencia aparente no
sobrevive siempre al escrutinio, y un sistema, o un investigador, que no distinga entre
tener una referencia y tener soporte producirá texto impecable y falso.

`[Pendiente: E18, ablaciones, para atribuir el resultado a cada componente; E19 sobre el
dataset de evaluación final; comparación con los trabajos del capítulo 3 una vez haya
resultados finales.]`
