# E18 — Ablaciones: qué aporta cada componente

**Fecha de ejecución:** 1 de octubre de 2026 · **Commit:** `d5fc372` · **Pre-registro:**
`docs/methodology/preregistro-e18-ablaciones.md`, congelado antes de medir · **Conjunto:**
los diecisiete casos anotados de `synthetic_v2`, modo oracular · **Política del verificador:**
v2.1 en las cuatro ablaciones.

Las cuatro ablaciones salen de la misma configuración canónica y cambian **una** pieza cada una.
Ninguna redacta: se ejecutan sin proveedor de lenguaje, porque lo que miden es la decisión y la
evidencia. Los registros son `experiments/E18_ablacion_A{1..4}.json` y las tablas
`tables/E18_ablacion_A{1..4}.csv`. Los cuatro llevan `dirty: true` por un borrador de la entrega
sin confirmar en el árbol de trabajo; ningún fichero de código o de configuración difería del
commit declarado.

## Resultado

| Ablación | Falsa confianza | Abstención innecesaria | Cobertura con evidencia completa | Decisiones distintas de la canónica |
|---|---|---|---|---|
| **Canónica** (criterio compuesto, umbral 0,79) | 0 de 9 | 2 de 5 | 3 de 5 | — |
| `A1` sin atribución | 0 de 9 | 2 de 5 | 3 de 5 | **0 de 17** |
| `A2` sin recuperación semántica | 0 de 9 | 5 de 5 | 0 de 5 | 3 de 17 |
| `A3` sin criterio de suficiencia | **6 de 9** | 0 de 5 | 5 de 5 | 11 de 17 |
| `A4` umbral único | **9 de 9** | 2 de 5 | 3 de 5 | 12 de 17 |

La falsa confianza se cuenta sobre las nueve ejecuciones que deben terminar en abstención sin
contar la condición con distractor y filtro de motor, que el diagnóstico de esa condición dejó
como diagnóstico y no como condición puntuable. Incluyéndola, `A3` da 9 de 12 y `A4`, 12 de 12.
Las nueve ejecuciones proceden de tres ventanas de telemetría y las cinco con evidencia completa,
de cinco: las tasas describen esta muestra y no estiman nada.

## A1 · sin atribución: no cambia nada, y se explica por qué

Sustituir la importancia de Shapley por la desviación tipificada del descriptor frente a la clase
sin fallo **no cambió ninguna decisión ni ningún conjunto de evidencia**: los diecisiete bundles
contienen exactamente los mismos fragmentos que la configuración canónica, y la cobertura de
afirmaciones es idéntica caso a caso.

Las observaciones sí cambian. En la deriva del caudalímetro la ruta canónica elige el máximo y la
media de las correcciones de combustible a largo plazo y la pendiente de las de corto; la
ablación elige el rango, la desviación típica y la pendiente de las de largo plazo y la media y
la pendiente de las de corto. En el fallo de encendido coinciden las tres primeras y difieren las
dos últimas.

La razón de que eso no mueva el resultado está en el diseño, no en el azar: la recuperación la
guía el **diagnóstico**, no la atribución, de modo que los fragmentos no dependen de qué
descriptor se haya elegido; y el soporte se comprueba sobre la **señal**, no sobre el
estadístico, de modo que dos rutas que eligen distintos estadísticos de la misma señal producen
el mismo resultado de soporte. Las dos rutas coinciden en las señales principales de los cinco
fallos.

Lo que esto permite afirmar es estrecho: **en esta muestra, y para la decisión, la atribución de
Shapley es sustituible por un criterio estadístico simple**. Lo que no permite afirmar es que la
atribución sea prescindible: es la que produce la evidencia observacional que el lector de la
explicación recibe, y su calidad se juzga por lo que describe, no por si cambia la decisión. El
contraste entre las dos rutas no se ha evaluado en ese plano.

## A2 · sin recuperación semántica: inconcluso, y por un motivo instructivo

La ruta léxica **no recupera ningún fragmento en ninguno de los diecisiete casos**. Sin evidencia
documental aplicable, el verificador se abstiene en todos, de modo que los tres casos que
explicaban dejan de hacerlo, la cobertura cae a 0 de 5 y la abstención innecesaria sube a 5 de 5.

La causa no es la ablación, es la consulta. La búsqueda de texto completo de PostgreSQL usa
`plainto_tsquery`, que une **todos** los términos con conjunción: una consulta de treinta
palabras exige que las treinta aparezcan en el mismo fragmento, y ninguno las contiene. Se
comprobó por separado, llamando a la búsqueda léxica con la consulta del primer caso y sin
filtros de motor ni de código: devuelve cero resultados.

Por tanto **esta ablación no aísla la contribución de la similitud semántica**. Compara la
recuperación semántica con una ruta léxica que, con la consulta tal como está formulada, no puede
coincidir con nada. El resultado se publica como **inconcluso**, no como «la semántica aporta
todo», y la enmienda `ENM-E18-01` del pre-registro declara la variante que lo mediría.

De paso, deja una observación sobre el sistema completo: la estrategia híbrida que el capítulo 5
usa como respaldo combina semántica y léxica por fusión de rangos, y la mitad léxica de esa fusión
aporta, para consultas en prosa, menos de lo que su presencia sugiere.

## A3 · sin criterio de suficiencia: seis explicaciones sin soporte

Retirado el criterio compuesto, el sistema explica siempre que hay al menos un fragmento
aplicable. Explica los cinco casos con evidencia completa —incluidos los dos en que el modelo no
alcanza el umbral de confianza— y explica además las nueve ejecuciones con evidencia parcial o con
distractor, donde ningún fragmento sostiene ninguna afirmación. Solo se abstiene en las tres de
evidencia retirada, porque ahí no hay ningún fragmento que recuperar.

Es la cifra que da sentido al criterio: **seis explicaciones sin soporte que el criterio compuesto
evita**, nueve si se cuenta la condición con distractor y filtro. El precio del criterio son dos
abstenciones innecesarias; su beneficio, estas seis.

## A4 · umbral único: la puerta de confianza sola es insegura

Decidiendo solo por la confianza calibrada, el sistema explica **las doce ejecuciones que debían
terminar en abstención**, incluidas las tres en que la recuperación no devuelve nada: la confianza
del modelo no sabe nada del corpus. Conserva la misma cobertura y las mismas dos abstenciones
innecesarias que la configuración canónica, porque esas dos proceden precisamente de la confianza.

Estas cifras coinciden exactamente con la política de referencia «explicar siempre que el modelo
confía» que el capítulo 5 publica —9 de 9 y 12 de 12 de falsa confianza, 2 de 5 de abstención
innecesaria—, calculada por otro camino sobre el registro. El pre-registro fijaba que una
discrepancia obligaría a parar y localizar el defecto; no hay discrepancia.

## Lo que las cuatro ablaciones permiten decir, y lo que no

El comportamiento observado en el capítulo 5 **no se debe a la atribución** —sustituible en esta
muestra—, **sí se debe al criterio compuesto de suficiencia** —seis explicaciones sin soporte
evitadas respecto de no tenerlo, y doce respecto de decidir solo por confianza— y **depende de la
recuperación**, aunque cuánto no puede cuantificarse con la ablación ejecutada.

Ninguna de las cuatro sostiene nada sobre la separación entre decidir y redactar, que es la otra
afirmación de diseño del trabajo: las ablaciones no cambian de redactor ni prueban una abstención
decidida por el modelo de lenguaje. Y todas se miden sobre el conjunto con el que el criterio fue
ajustado, de modo que son cifras de desarrollo.
