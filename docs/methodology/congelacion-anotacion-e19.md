# Congelación de las reglas de selección y anotación de los casos de prueba (E19)

**Fecha:** 1 de octubre de 2026 · **Estado:** congelado **antes** de abrir el conjunto de
prueba y antes de cualquier medición sobre él. · **Qué cierra:** la octava comprobación del
gate de `docs/methodology/plan-e19-evaluacion-final.md`, la única que faltaba. · **Qué no
hace:** no abre el conjunto de prueba ni autoriza abrirlo. La apertura es una declaración
posterior del autor, y este documento es uno de sus requisitos, no su sustituto.

**Una precisión posterior, del 1 de octubre de 2026 y anterior a cualquier medición.** La regla
primaria decía «la primera ventana en orden canónico» de cada sesión, y al implementarla apareció
una ambigüedad real: en una sesión con fallo, las primeras ventanas están etiquetadas como
funcionamiento normal, porque la avería se inyecta después de un calentamiento. La regla pasa a
decir **la primera ventana etiquetada con esa condición**, que es la única lectura con sentido:
una ventana sin el fallo no puede explicarse con la documentación de ese fallo. El cambio se hace
con el conjunto de prueba cerrado, el número de ejecuciones no varía, y se ve en el historial como
dos commits —el que edita lo congelado y el que mueve el anclaje—, que es exactamente el
procedimiento que la sección 12 describe.

**Tres correcciones de la revisión previa a la congelación** quedan incorporadas en esta versión,
que es la revisada y la que el anclaje fija: la fuente de la clase predicha, que debe ser la que
usa el recorrido evaluado y no la del modelo calibrado (sección 5); el anclaje de las huellas, que
no puede depender de un fichero editable; y su alcance, que debe cubrir también el estado
congelado y no solo este documento (sección 12). La cadena de la sección 12 coloca la revisión
**antes** de que la congelación surta efecto, precisamente para que correcciones así entren dentro
de lo congelado y no después.

Este documento existe por una razón que conviene decir sin rodeos: si las reglas con que se
eligen y se anotan los casos se escribieran después de ver la partición de prueba, la
evaluación final dejaría de ser una predicción y sería una descripción de datos ya vistos. El
plan de E19 ponía esa congelación como primer paso de su orden de ejecución y al mismo tiempo
declaraba el gate superado sin ella; la revisión del diff lo señaló y el gate pasó a tener una
comprobación pendiente. Esta es.

## 0. Qué se ha leído de la partición de prueba para escribir esto

La honestidad del procedimiento depende de poder decir exactamente qué se miró. Para redactar
estas reglas se ha leído **solo el reparto de sesiones** de
`data/processed/synthetic_v2_preprocess.json`, es decir el diccionario `split_assignment` que
asigna cada identificador de sesión a una partición, y los recuentos que se derivan de él:

| | Sesiones | Ventanas | Sesiones por condición |
|---|---|---|---|
| Entrenamiento | 48 | 392 | 8 |
| Validación | 12 | 98 | 2 |
| **Prueba** | **12** | **98** | **2** |

El reparto se estratifica por condición y es simétrico entre validación y prueba, de modo que
estos números no informan de nada que el diseño del reparto no fijara ya: son la aritmética de
`split_by_session` con la semilla 20260901, publicada desde E5. **No se ha leído** ninguna
señal, ninguna ventana, ningún descriptor, ninguna etiqueta por ventana ni ninguna salida del
modelo sobre prueba. El cargador lo impide: pedir la partición de prueba exige `allow_test=True`
y una razón por escrito, y ninguna de las órdenes ejecutadas para escribir este documento la
pidió.

## 1. Unidad experimental

Hay tres unidades distintas y confundirlas es el error que más fácilmente infla un resultado.

| Unidad | Qué es | Para qué se usa |
|---|---|---|
| **Ventana de telemetría** | 120 s de las doce señales a 1 Hz, con paso de 60 s, identificada por `session_id@t_start` | unidad del diagnóstico: las métricas de PI.1 se calculan sobre las 98 ventanas de prueba |
| **Ejecución de caso** | una ventana recorrida de punta a punta bajo una condición de evidencia: recuperación, verificación de soporte, decisión y, cuando corresponde, redacción | unidad de la decisión: cada fila del registro de suficiencia es una de estas |
| **Unidad de independencia** | la **sesión** de la que proviene la ventana | única unidad sobre la que puede hablarse de casos independientes |

La unidad experimental de E19, en el sentido de aquello que se manipula, es la **ejecución de
caso**. La unidad de independencia es la **sesión**, no la ejecución: tres ejecuciones que
comparten ventana comparten datos, modelo, atribución y confianza, y solo difieren en lo que hay
en el índice documental. Toda tasa que se publique llevará su numerador, su denominador en
ejecuciones y el número de ventanas y de sesiones distintas que hay detrás.

## 2. Conjunto exacto de casos elegibles

Los casos de prueba **reutilizan el conjunto anotado de validación**, sin escribir ni una
consulta nueva. `configs/goldset_mazda3_bk.yaml` está congelado y su huella es
`7fadc49fc7daaad1`; de sus diecisiete casos, E19 toma once:

| Condición de fallo | DTC | Evidencia completa | Evidencia parcial | Evidencia ausente |
|---|---|---|---|---|
| `F01_vacuum_leak` | P2187 | `C05` | `C07` | `C06` |
| `F02_maf_drift` | P0102 | `C01` | — | — |
| `F03_thermostat_stuck` | P0125 | `C02` | `C11` | `C10` |
| `F04_o2_lag` | P0133 | `C03` | `C15` | `C14` |
| `F05_misfire` | P0300 | `C04` | — | — |

Cinco casos con evidencia completa, tres con evidencia parcial y tres con evidencia ausente.

**Lo que se excluye, y por qué.** Los seis casos de la condición con distractor quedan fuera:
tres con el filtro de motor activo (`C08`, `C12`, `C16`) y tres sin él (`C09`, `C13`, `C17`). Con
el filtro activo no añaden ningún distractor que la condición parcial no tuviera, de modo que no
miden lo que su nombre dice; sin filtro miden la segunda línea de defensa, que es el validador de
aplicabilidad, y no la primera. PI.4 no podrá interpretarse hasta que la condición se rediseñe. Medirlos sobre prueba produciría
cifras que después habría que retirar. Tampoco se construyen condiciones parcial y ausente para
`F02_maf_drift` y `F05_misfire`: sus listas de exclusión no existen, y escribirlas ahora
significaría decidir qué cuenta como evidencia insuficiente en la misma semana en que se mide,
que es exactamente la libertad que esta congelación retira. Las dos ausencias se declararán
junto a los resultados: el diseño de E19 no está equilibrado entre condiciones de fallo, y ese
desequilibrio viene de validación, no de prueba.

**Las consultas se reutilizan literalmente**, con su limitación heredada: las escribió una
persona que conocía el fallo. Describen síntomas y no nombran el diagnóstico ni el código, pero
su redacción no es ciega, y eso se declara con los resultados igual que se declaró con los de
validación.

## 3. Reglas de inclusión y exclusión de ventanas

La selección es determinista y no consulta al modelo. **Orden canónico:** `session_id`
ascendente y, dentro de cada sesión, `t_start` ascendente.

**Regla primaria (estrato operativo).** De cada una de las dos sesiones de prueba de cada
condición de fallo se toma **la primera ventana, en orden canónico, que esté etiquetada con esa
condición**. La precisión importa: en una sesión con avería las primeras ventanas llevan etiqueta
de funcionamiento normal, porque el fallo se inyecta tras un calentamiento, y una ventana sin el
fallo no puede explicarse con la documentación de ese fallo. Son diez ventanas, de diez sesiones
distintas, dos por condición. Cada una se ejecuta bajo todas las condiciones de
evidencia que su fallo tenga en la tabla anterior: las de `F01`, `F03` y `F04` dan tres
ejecuciones cada una, y las de `F02` y `F05`, una. Total: **veintidós ejecuciones sobre diez
ventanas de diez sesiones**.

Esta regla cambia algo respecto de validación y conviene decirlo antes de medir. En validación
la ventana de cada caso era la primera que el modelo **clasificaba bien**, lo que hacía de la
selección un canal de oráculo —el `O-1` de la política de evaluación no oracular— y reducía la
falsa confianza a nueve ejecuciones sobre tres ventanas. La regla primaria de E19 no pregunta al
modelo si acierta: evalúa el sistema sobre ventanas elegidas por su posición, que es lo que
ocurriría en funcionamiento, y multiplica por tres las unidades de independencia disponibles.

**Regla secundaria (estrato comparativo, descriptivo).** Las mismas once condiciones de
evidencia se ejecutan además sobre la ventana que la regla de validación habría elegido: la
primera, en orden canónico, que el modelo clasifica correctamente, con el mismo criterio de acierto
que usa el recorrido evaluado, es decir la predicción del bosque **sin calibrar**. Existe por una
razón
estrictamente metodológica: sin ella, cualquier diferencia entre las cifras de prueba y las del
capítulo 5 confundiría el efecto de la partición con el efecto de haber cambiado la regla de
selección. Es un estrato **descriptivo** y no responde a ninguna subpregunta.

**Estrato adverso (descriptivo).** Como en validación, se ejecutan las cinco condiciones de
evidencia completa sobre la ventana de cada fallo que el modelo **clasifica mal**, eligiendo entre los errores
la de mayor probabilidad calibrada máxima, conforme a la regla `A-1` de
`politica-evaluacion-no-oracular-enmienda-01.md`. Si una condición no tiene ninguna ventana mal
clasificada en prueba, el caso se declara **no evaluable por ausencia de ventanas**, que es un
hecho de la partición y no un error de ejecución.

**Exclusiones.** Las dos sesiones de `F00_normal` no generan casos anotados: no hay condición
documental que explicar cuando no hay fallo. Entran, como todas las demás, en las 98 ventanas
sobre las que se miden el diagnóstico y la calibración. Ninguna ventana se excluye por su
resultado, ni antes ni después de conocerlo.

## 4. Tratamiento de ventanas repetidas

Dos cosas distintas se llaman repetición, y las reglas son distintas.

**Solape entre ventanas de una misma sesión.** Con ventana de 120 s y paso de 60 s, dos ventanas
consecutivas comparten la mitad de sus muestras. La regla primaria toma **una sola ventana por
sesión**, de modo que entre las diez ventanas elegidas no hay solape alguno. Si una ejecución
hubiera de repetirse sobre otra ventana de la misma sesión, esa ventana no cuenta como unidad
independiente nueva: la sesión sigue siendo una.

**La misma ventana bajo varias condiciones de evidencia.** Es deliberado y es el experimento
central: los datos, el modelo, la atribución y la confianza son idénticos, y lo único que cambia
es qué hay en el índice. Si la decisión no cambiara, el sistema no estaría usando la evidencia.
Esas ejecuciones son **medidas repetidas sobre la misma unidad** y no se tratan como
independientes: cada tasa declara ejecuciones, ventanas y sesiones; ninguna prueba inferencial
ni intervalo de confianza las trata como observaciones independientes; y cuando se dé un
intervalo, se remuestrearán **sesiones**, como en el análisis de sensibilidad del umbral, con la
advertencia de que describe el punto medido y no lo elige.

## 5. Decisión esperada de cada caso, y por qué no es circular

La decisión esperada de una ejecución es `EXPLICA` si y solo si se cumplen **las dos**
condiciones siguientes, y `ABSTIENE` en cualquier otro caso:

1. **Hay en el índice evidencia documental admisible para la condición que generó la ventana**,
   entendiendo por tal el procedimiento diagnóstico que Mazda publica para el DTC de esa
   condición en la variante del motor Z6. Esto lo fija la condición de evidencia del caso, que es
   una manipulación del índice decidida por construcción: completa lo deja, parcial retira los
   procedimientos y conserva las tablas de códigos, ausente retira todo fragmento que porte los
   códigos de la familia.
2. **El diagnóstico con que el sistema va a buscar y a verificar designa la condición que
   realmente generó la ventana**, es decir la clase predicha coincide con la etiqueta.

La segunda condición es la que hace que el estrato adverso tenga decisión esperada `ABSTIENE`
incluso con evidencia completa en el índice: cuando el diagnóstico es incorrecto, no existe
evidencia documental admisible para la afirmación que el sistema iba a hacer, por mucho que el
manual documente bien otra cosa.

**De qué modelo sale esa clase predicha, y por qué importa.** El recorrido evaluado tiene una
asimetría deliberada: el **diagnóstico** con que se acota la recuperación y se verifica el soporte
es el argumento máximo del bosque **sin calibrar**, y la **confianza** que se compara con el umbral
es la probabilidad calibrada de esa misma clase. La calibración isotónica puede reordenar clases,
de modo que el argumento máximo del modelo calibrado no siempre coincide con el del bosque. Si la
anotación se derivara del modelo calibrado, podría declarar que un caso debía explicarse por una
clase que el sistema no está usando, y los denominadores de las dos tasas quedarían mal. La regla
es por tanto inequívoca: la decisión esperada se anota con la **misma** clase que el recorrido usa,
y donde las dos predicciones difieran, manda el recorrido. Cuántos casos difieren es un resultado
que se registrará, no un supuesto.

**La no circularidad, dicha de forma comprobable.** La decisión esperada se instancia a partir
de tres entradas y de ninguna más:

| Entrada permitida | De dónde sale |
|---|---|
| la etiqueta verdadera de la ventana | `meta.label` de la partición |
| la clase predicha **por el recorrido evaluado** | `predicted_class` de la atribución, que es el argumento máximo del bosque **sin calibrar** |
| la condición de evidencia del caso | el campo `corpus_variant` del conjunto anotado |

Queda **prohibido** que intervenga cualquier salida del verificador de suficiencia: el veredicto,
los motivos, la cobertura de afirmaciones, el número de fragmentos aplicables o de fuentes
distintas, el resultado de las cuatro comprobaciones de soporte, el requisito de la puerta de
códigos. Si la anotación se derivara de ellos, se estaría midiendo la política contra sí misma y
el acuerdo sería una tautología. La anotación es el referente **contra el que** se mide la
política.

**Cuándo se instancia.** La regla está congelada ahora; su instanciación exige la clase predicha
sobre prueba y por tanto solo puede ocurrir después de la apertura. El procedimiento es: abrir,
calcular las predicciones, escribir la anotación completa a un artefacto, **registrar su huella**
y solo entonces ejecutar la verificación de suficiencia. Entre la anotación y la primera cifra de
suficiencia hay un artefacto con huella, de modo que la acusación de haber ajustado la anotación
a los resultados es verificable y no una cuestión de palabra.

## 6. Falsa confianza y abstención innecesaria

Las dos definiciones son las del capítulo 4 y no cambian:

- **Falsa confianza** `T_FC` = ejecuciones que explican entre las que debían abstenerse, dividido
  por el número de ejecuciones cuya decisión esperada es `ABSTIENE`.
- **Abstención innecesaria** `T_AI` = ejecuciones que se abstienen entre las que debían explicar,
  dividido por el número de ejecuciones cuya decisión esperada es `EXPLICA`.

Se publican **por separado**, nunca sumadas ni promediadas en un único número de acierto, porque
los dos errores no cuestan lo mismo: explicar sin soporte entrega al mecánico un procedimiento
que el manual no respalda; abstenerse de más le devuelve un «no lo sé» que no le sirve pero no
le engaña. Cada una se da con numerador, denominador en ejecuciones, y ventanas y sesiones
distintas. Los denominadores quedan determinados por la regla de la sección 5 y **no se conocen
todavía**: cuántas ejecuciones deben explicar depende de cuántas ventanas clasifique bien el
modelo sobre prueba, que es precisamente lo que no se ha mirado. El denominador se registra como
resultado, no se fija aquí.

Ambas tasas se acompañan de las dos políticas triviales de referencia recalculadas sobre las
mismas ejecuciones: abstenerse siempre, que da `T_FC` 0 y `T_AI` 1, y explicar cuando el modelo
confía, que es la puerta de confianza sola.

## 7. Reglas de anotación de la evidencia suficiente

El anclaje no es el criterio de quien anota: es el manual. Para cada condición de fallo, la
evidencia relevante es el **procedimiento diagnóstico que Mazda publica para su DTC en la
variante del motor Z6**, ya identificado fichero a fichero en el conjunto anotado y sin cambios
para E19. La evidencia de apoyo son las tablas de códigos y la lógica de detección, que
mencionan la condición sin decir cómo se diagnostica. La condición parcial se construye
retirando los procedimientos y dejando el apoyo; la ausente, retirando todo fragmento que porte
los códigos de la familia, no solo el fichero del procedimiento principal.

Lo que esta anotación **no** es: no es una anotación independiente de qué afirmaciones son
admisibles. El soporte de cada afirmación sigue siendo una propiedad que calcula el verificador,
y mientras no haya una anotación humana independiente de afirmaciones, la cobertura de
afirmaciones describe el comportamiento del verificador y no acredita la verdad de las
afirmaciones. Esta limitación ya figura en la memoria y se repetirá junto a las cifras de E19;
levantarla no forma parte de E19.

## 8. Empates, casos no evaluables y errores de esquema

| Situación | Regla, fijada ahora |
|---|---|
| Empate en la elección de ventana por el orden canónico | imposible: `session_id` y `t_start` son únicos y el orden es total |
| Empate en la confianza calibrada entre errores del modelo, en el estrato adverso | gana el menor `session_id` y, a igualdad, el menor `t_start` |
| La condición no tiene ninguna ventana del tipo que la regla pide | la ejecución se declara **no evaluable por ausencia de ventanas**, se registra como tal y **no** entra en ningún numerador ni denominador. No se sustituye por otra ventana |
| El modelo de lenguaje devuelve una salida que el esquema rechaza | la ejecución **cuenta** y su decisión de suficiencia es válida: el verificador es determinista y precede a la redacción. El fallo se registra en la métrica de salidas válidas, que es la que lo mide. No se reintenta la generación |
| El redactor cita fuera de lo entregado | la ejecución cuenta y la cita indebida se registra en su métrica. No se corrige la salida |
| Falta un artefacto de entrada: índice, modelo, manifiesto, adaptador | la ejecución no llega a empezar; es un fallo de preparación, no un resultado, y se resuelve antes de ejecutar |
| Una ejecución produce una excepción | se registra el caso como **no completado**, con la traza y la causa, y se aplica el criterio de validez de la sección 11 |

Ninguna de estas reglas permite retirar una ejecución por el valor de su resultado.

## 9. Métricas que se publicarán y agregaciones permitidas

Nada se publica que no esté en esta lista, y nada de esta lista se omite por su valor.

| Bloque | Métricas |
|---|---|
| Diagnóstico, sobre las 98 ventanas de prueba | exactitud, F1 macro, F1 ponderado, exactitud equilibrada, métricas por clase, frente a la clase mayoritaria de la propia partición |
| Calibración | error de calibración esperado con 10 tramos, confianza media, acierto y sesgo, sin calibrar y calibrado |
| Suficiencia | vector de decisiones por ejecución; motivo de cada abstención; `T_FC` y `T_AI` con numerador, denominador, ventanas y sesiones; cobertura de afirmaciones en las ejecuciones con evidencia completa; número de fragmentos aplicables y de fuentes distintas; las dos políticas de referencia sobre las mismas ejecuciones |
| Trazabilidad | afirmaciones con observación, con cita y con soporte, con su denominador |
| Redacción | salidas válidas frente al esquema, respeto del veredicto de abstención, citas fuera de lo entregado |

**Agregaciones permitidas:** recuentos y proporciones con denominador explícito; desglose por
condición de fallo y por condición de evidencia; promedio no ponderado entre condiciones de fallo
cuando se diga que lo es.

**Agregaciones prohibidas:** mezclar ejecuciones que comparten ventana como si fueran
independientes; agregar en un único número de acierto las dos tasas de error; mezclar las cifras
de validación con las de prueba en una misma media; comparar una cifra de prueba del estrato
operativo con una de validación sin advertir que la regla de selección es distinta; dar
intervalos que presupongan ejecuciones independientes.

## 10. Política canónica y versiones exactas

| Pieza | Valor congelado |
|---|---|
| Política del verificador | **v2.2**, que pasa a canónica **con esta evaluación** y solo con ella |
| Umbrales | confianza 0,79; fragmentos de soporte 2; fuentes distintas 1; cobertura de afirmaciones 0,80; puntuación de recuperación desactivada en 0,0; aplicabilidad aceptada, solo coincidencia exacta |
| Semilla | 20260901, única, en reparto, bosque, fondo de atribución y muestreos |
| Conjunto de datos | `synthetic_v2`, 588 ventanas, 139 descriptores, `dataset_type: synthetic` |
| Modelo de diagnóstico | bosque aleatorio, 400 árboles, hoja mínima 2, pesos equilibrados, calibración isotónica con validación cruzada de 5 pliegues ajustada **sobre entrenamiento** |
| Corpus | `mazda-3-bk-2007`, versión 0.1.0, 6 158 fragmentos de 3 055 ficheros, sin reindexar |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones, identidad de espacio `sentence-transformers[mps]/.../d384/v1.0.0`, en el mismo dispositivo que produjo los vectores indexados |
| Recuperación | guiada por el diagnóstico, profundidad 10, filtros de vehículo y motor, reordenación por autoridad |
| Redactor | `transformers-lora@slm_lora_v2`, prompt `agent-2026-09-04`, sin reentrenar |
| Código | el commit que se registre en el artefacto, con el árbol limpio |

**Canales de oráculo, cerrados.** E19 se ejecuta con el recorrido no oracular: los códigos que
acotan la recuperación y los que un fragmento debe portar para sostener una afirmación se derivan
de la **clase predicha**, nunca de la etiqueta anotada. Es lo que los canales `O-2` y `O-3` de la
política de evaluación no oracular describen, y cerrarlos es imprescindible aquí: en el estrato
operativo hay ventanas que el modelo puede clasificar mal, y derivar la búsqueda de la etiqueta
ocultaría precisamente el comportamiento que se quiere medir. El canal `O-1`, la selección de
ventana condicionada al acierto del modelo, queda cerrado en el estrato operativo y abierto, por
definición, en el comparativo; en el adverso se invierte.

El manifiesto `configs/manifest_e19.json` enumera estos valores con sus huellas, incluida la de
este documento, y las pruebas comprueban que el documento no ha cambiado desde que se congeló.

**Árbol limpio.** Los artefactos anteriores se produjeron con `dirty: true` y eso quedó
registrado. Los de E19 se producirán con el árbol limpio; si no fuera posible, el motivo se
escribe en el informe de fase.

## 11. Criterio para declarar una ejecución inválida y repetirla

Una ejecución puede declararse inválida **solo** por causas ajenas al resultado, y la lista es
cerrada: versión de una pieza distinta de la congelada en la sección 10; índice incompleto o en
un espacio vectorial distinto del declarado; dispositivo de embeddings distinto del que produjo
los vectores; artefacto de entrada ausente o corrupto; interrupción del proceso; defecto
demostrable en el código de instrumentación que no afecta a la política evaluada.

Lo que **no** invalida una ejecución: que las cifras sean peores de lo esperado, que una
hipótesis no se sostenga, que aparezca un defecto en el sistema evaluado. Un defecto en el
sistema evaluado **es** el resultado.

Cuando una ejecución se repite, el registro inválido **se conserva**, con el motivo escrito y la
causa documentada, y la repetición se publica como **nueva versión experimental** con su propio
identificador. Si el defecto apareciera después de haber abierto el conjunto y afectara a la
política evaluada, la ejecución se conserva igualmente, el defecto se declara, y cualquier
medición posterior es una versión nueva y no una corrección de esta.

## 12. Punto de no retorno

**Dónde están ancladas las huellas.** Una huella guardada dentro del fichero que certifica no
prueba nada: editar los dos a la vez pasaría cualquier comprobación. El anclaje es por eso el
**commit** que introduce la congelación, cuyo contenido es inmutable, y se declara en un fichero
aparte, `configs/congelacion-e19.anchor.json`, escrito **después** de ese commit y que por tanto
puede nombrarlo.

Cubre **dos** ficheros, no uno: este documento, que son las reglas, y `configs/manifest_e19.json`,
que es el estado congelado —umbrales, versiones, conjunto elegible, métricas publicables—. Anclar
solo las reglas dejaría el estado libre, y es ahí donde un umbral o un caso elegible podrían
moverse sin que nada fallara. Para cada uno de los dos, las pruebas comparan el fichero del árbol
de trabajo con el objeto del commit de congelación y comprueban que **ningún commit posterior lo
toca**.

Lo que esto garantiza y lo que no. No impide un cambio posterior: impide que sea silencioso. Todo
cambio después de la congelación exige dos commits visibles —uno que edite el fichero y otro que
mueva el anclaje—, y eso es precisamente lo que un revisor busca. Hacerlo sin dejar rastro exigiría
reescribir el historial, que queda a la vista en la rama de archivo y en el mapa de SHA que el
repositorio publica.

La cadena es esta, y ningún eslabón puede adelantarse:

```
reglas congeladas (este documento)
  → huella y versionado (configs/manifest_e19.json y las pruebas que lo verifican)
  → revisión del diff contra main
  → PASS, sin hallazgos bloqueantes ni mayores
  → declaración formal de apertura del conjunto de prueba, con razón escrita
  → ejecución de E19
```

El código que E19 necesita —parametrizar la partición y la regla de selección de ventana— se
escribe y se revisa **antes** de la declaración de apertura, de modo que ninguna línea de ese
código se escriba teniendo delante un resultado de prueba.

Una vez declarada la apertura **no se modifican**: los umbrales, las reglas de anotación, la
selección de casos, el conjunto elegible, la política canónica ni las métricas publicables, en
respuesta a ningún resultado. Lo que esté mal ajustado se queda así y se declara. Si apareciera
un defecto que invalide la evaluación, se conserva la ejecución, se documenta el motivo y
cualquier medición nueva se trata como versión experimental nueva.

## 13. Lo que esta congelación no resuelve

Las consultas del conjunto anotado no son ciegas. El desequilibrio entre condiciones de fallo
—tres con las tres condiciones de evidencia y dos solo con evidencia completa— viene de
validación. La condición con distractor queda fuera y PI.4 seguirá sin poder interpretarse. La
cobertura de afirmaciones sigue siendo una propiedad del verificador y no una anotación
independiente. Y los datos siguen siendo sintéticos: la evaluación final mide el comportamiento
del sistema sobre el conjunto que nunca vio, no su comportamiento sobre un vehículo.
