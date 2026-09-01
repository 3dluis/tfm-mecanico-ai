# E12 — Evaluación de la recuperación

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Vehículo: Mazda 3 BK 2007, motor Z6 · Corpus: 6 158 fragmentos · K = 10

## Diseño del conjunto anotado

La verdad de referencia **no la decidí yo**: es el propio manual. Para cada
condición del experimento, el documento relevante es el procedimiento diagnóstico
que Mazda publica para el DTC correspondiente, en la variante del motor Z6.

Las consultas describen lo **observado** --lo que E4 y E5 midieron sobre las
señales-- y no nombran el DTC ni la causa. Hay un test que lo comprueba: si la
consulta contuviera la respuesta, la evaluación mediría la consulta.

| Caso | Condición | DTC | Documento relevante | Acción esperada |
|---|---|---|---|---|
| C01 | deriva de caudalímetro | P0102 | `B3E010200100W01` | EXPLAIN |
| C02 | termostato bloqueado | P0125 | `B3E010200100W11` | EXPLAIN |
| C03 | sonda lenta | P0133 | `B3E010200100W13` | EXPLAIN |
| C04 | fallo de encendido | P0300 | `B3E010200300W01` | EXPLAIN |
| C05 | fuga de vacío | — | **ninguno** | **ABSTAIN** |

### El distractor no hubo que fabricarlo

Cada DTC tiene en el corpus **dos** procedimientos: el de `[ZJ, Z6]` y el de
`[LF]`. Mismo código, contenido prácticamente idéntico, motor inaplicable a este
vehículo. Es el distractor perfecto y estaba ya en el manual.

### C05 es el caso que hace honesto al conjunto

~~El modelo clasifica la fuga de vacío a la perfección y el corpus no contiene el
procedimiento que la sustentaría: se buscó P0171 y no está.~~

> **Corrección posterior (E15).** Esta afirmación es **falsa**. Mazda no usa los
> códigos genéricos de mezcla: usa la familia P2177/P2178/P2187/P2188. El corpus
> contiene 30 fragmentos con **P2187 — «Fuel system too lean at idle»**, cuya
> condición de detección vigila los ajustes de combustible en ralentí, que es
> exactamente la firma de esta condición. La evidencia estaba desde el principio;
> busqué el código equivocado. Ver `E15_suficiencia.md`.

El caso se rehízo en E15. La distinción que se quería ilustrar --entre «el modelo
acierta» y «hay evidencia que lo sostenga»-- sigue siendo válida y es la pregunta
de investigación en una línea, pero ahora se construye **retirando** la evidencia
del índice en lugar de darla por ausente. Es mejor diseño: la abstención se
provoca, no se hereda de un descuido.

## Resultados

| Estrategia | P@10 | R@10 | MRR | Hit@10 | nDCG@10 |
|---|---|---|---|---|---|
| `semantic` | 0,000 | 0,000 | 0,000 | **0,00** | 0,224 |
| `semantic+engine` | 0,000 | 0,000 | 0,000 | **0,00** | 0,312 |
| `semantic+authority` | 0,025 | 0,250 | 0,125 | 0,25 | 0,531 |
| `hybrid` (semántica + léxica, fusión RRF) | 0,025 | 0,250 | 0,125 | 0,25 | 0,531 |
| **`diagnosis-guided`** | **0,250** | **1,000** | **0,446** | **1,00** | **0,658** |

Posición del primer documento relevante:

| Caso | semantic | +engine | +authority | hybrid | diagnosis-guided |
|---|---|---|---|---|---|
| C01 caudalímetro | — | — | — | — | **3** |
| C02 termostato | — | — | 2 | 2 | **1** |
| C03 sonda lenta | — | — | — | — | **5** |
| C04 encendido | — | — | — | — | **4** |
| C05 fuga de vacío | — | — | — | — | — |

## Hallazgo 1 — la recuperación semántica no encuentra la evidencia autorizada

**Hit@10 = 0,00.** En ninguno de los cuatro casos con documento relevante la
similitud semántica lo trae en los diez primeros.

Se comprobó que no era un fallo de la evaluación. Para C03, el procedimiento de
P0133 aparece en las posiciones **146 y 197 de 500**. Lo que sí aparece arriba
son secciones genéricas del mismo componente: `HEATED OXYGEN SENSOR (HO2S)
FUNCTION`, `HO2S HEATER CONTROL`, `HO2S INSPECTION`.

La razón es entendible. La consulta describe **síntomas** --amplitud de
oscilación colapsada, frecuencia de conmutación reducida-- mientras el
procedimiento del DTC describe **la lógica de monitorización de la centralita** y
sus pasos de comprobación. Son documentos sobre lo mismo escritos en registros
distintos, y el que más se parece al síntoma es la descripción de funcionamiento,
que no sostiene ningún diagnóstico.

Y algo peor: en C03 el resultado **#1 es `HEATED OXYGEN SENSOR (HO2S) FUNCTION
[LF]`**, del motor equivocado, por encima de su propio equivalente `[ZJ, Z6]`.

## Hallazgo 2 — el diagnóstico del modelo es lo que hace funcionar la recuperación

`diagnosis-guided` pasa de Hit@10 **0,00 a 1,00**. Encuentra el procedimiento
correcto en los cuatro casos que lo tienen.

No es hacer trampa con la respuesta. Usa exactamente la información que el
sistema **posee en ese punto**: el modelo especializado ya ha emitido un
diagnóstico, y la ficha de esa condición nombra los DTC que la documentan. Es la
arquitectura que la pregunta de investigación describe --el modelo diagnostica,
el RAG busca evidencia **para** ese diagnóstico-- y resulta que no es solo más
limpia conceptualmente: es la diferencia entre no encontrar nada y encontrarlo
siempre.

Esto refuerza una decisión tomada en E6: **el LLM no debe diagnosticar a partir
de OBD-II crudo**. Si lo hiciera, no habría diagnóstico que guiara la
recuperación, y el sistema quedaría con la estrategia que puntúa 0,00.

## Hallazgo 3 — la autoridad ayuda, la búsqueda híbrida no añadió nada

Reordenar por jerarquía de evidencia sube el nDCG de 0,224 a 0,531 y rescata C02.
Es una mejora real pero insuficiente: sigue fallando tres de cuatro casos.

La búsqueda híbrida --semántica más texto completo, fusionadas por rango
recíproco-- dio **exactamente los mismos números** que la reordenación por
autoridad. La componente léxica no aportó nada aquí, y la explicación es que las
consultas describen síntomas con vocabulario que no coincide literalmente con el
del procedimiento. La búsqueda léxica brillaría con una consulta que contuviera
«P0133», y esa consulta es precisamente la que `diagnosis-guided` construye.

Se reporta que no aportó, en lugar de retirarla del informe.

## Hallazgo 4 — el caso de abstención se comporta como debe

C05 no recupera documento relevante en **ninguna** estrategia, incluida
`diagnosis-guided`, que se degrada correctamente porque F01 no tiene DTC en el
corpus.

Es el resultado que se buscaba: cuando no hay evidencia, ninguna estrategia la
inventa. El sistema de recuperación deja el hueco, y será el verificador de
suficiencia quien lo convierta en abstención.

## Precisión baja y por qué no preocupa aquí

`diagnosis-guided` alcanza P@10 = 0,250 con Recall@10 = 1,000. La precisión es
baja porque cada caso tiene **un solo** documento relevante y se piden diez
resultados: el máximo alcanzable es 0,1 por documento relevante recuperado, y las
tablas de DTC y la lógica de detección ocupan el resto.

Con un solo documento relevante, la métrica informativa es el rango del primero
--MRR-- y si aparece --Hit Rate--. La precisión se reporta por completitud.

## Registro

Las 25 recuperaciones (5 casos × 5 estrategias) quedaron en `rag.retrieval_run` y
`rag.retrieval_result`, con su consulta, estrategia, parámetros y resultados
puntuados. Cualquiera de ellas se puede reconstruir después.

## Tests

`tests/test_retrieval_eval.py` — 19 casos:

- métricas contra casos construidos: recuperación perfecta, nula, y el efecto de
  encontrar el documento tarde;
- el recall cuenta ficheros distintos, no fragmentos del mismo procedimiento;
- se detecta un **distractor por encima de la evidencia aplicable**, que es el
  fallo más grave de esta fase;
- el conjunto anotado contiene al menos un caso de abstención;
- **`test_la_consulta_no_contiene_la_respuesta`**: ninguna consulta nombra su DTC
  ni la causa.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 53 ficheros |
| `pytest` | **203 casos** en verde |

## Limitaciones

**Cinco casos.** El conjunto es pequeño porque está anclado a las condiciones que
el generador produce y que el manual documenta. Las diferencias entre 0,00 y 1,00
son demasiado grandes para atribuirlas al tamaño, pero las diferencias pequeñas
--como que híbrida y autoridad empaten-- no son concluyentes con esta muestra.

**Un solo modelo de embeddings.** No se ha comprobado si otro modelo cambiaría el
hallazgo 1. Es plausible que uno entrenado en dominio técnico mejorara; no se
afirma que no.

**Granularidad de fichero.** Se evalúa si se encontró el procedimiento, no si se
encontró el fragmento exacto que sostiene la afirmación. Eso corresponde a la
verificación de soporte, no a la recuperación.

## Siguiente

E13 en adelante requieren proveedor LLM. Antes de eso, el verificador de
suficiencia (E15) puede construirse y probarse sin él: es determinista por
diseño, y C05 le da un caso real con el que empezar.
