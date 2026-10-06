# Auditoría previa: ¿en qué fallos aporta el contexto temporal? (PI.1)

**Fecha:** 5 de octubre de 2026 · **Encargo:** el tutor confirma que no se abre una línea nueva sobre
series temporales y pide formalizar dentro de PI.1 la pregunta «en qué tipos de fallo el contexto
temporal aporta señal diagnóstica adicional y en cuáles no». Antes de modificar nada, esta auditoría
responde a los diez puntos pedidos. · **Ningún experimento nuevo.** Todas las cifras salen de
registros ya existentes; las dos comprobaciones descriptivas de la sección 4 se hacen sobre
entrenamiento y validación, nunca sobre el conjunto de prueba.

---

## 1. Qué experimentos existentes responden ya a esta cuestión

| Experimento | Qué aporta a la pregunta | Estado |
|---|---|---|
| **E4** análisis exploratorio | separabilidad univariante por señal y por vía —nivel o dispersión— con delta de Cliff sobre bloques de 60 s. Sitúa al termostato como el único fallo «separable» cuya mejor señal no llega a delta 1,00 | RUN, sin JSON; tablas `tables/E4_*.csv` |
| **E5** preprocesamiento | fija la geometría: ventana de 120 s, paso de 60 s, 139 descriptores, reparto por sesión. Mide el suelo de ruido, que es lo que permite distinguir «efecto pequeño» de «efecto inexistente» | RUN |
| **E6** línea base tabular | bosque aleatorio sobre los 139 descriptores de ventana = **representación B** | VALIDATED |
| **E7** modelo temporal | GRU bidireccional sobre las secuencias crudas = **representación C**, sobre los dos conjuntos | **NEGATIVO** en `synthetic_v2`, **INCONCLUSO** en `synthetic_v3` |
| **E9** atribución | qué descriptores sostienen cada diagnóstico; incluye tres casos de termostato, los tres acertados | RUN |

La comparación tabular ↔ secuencial **ya existe y está ejecutada dos veces**, sobre dos volúmenes de
datos. No hace falta ningún experimento nuevo para responder a la pregunta en su forma agregada ni en
su forma desagregada por fallo. Lo que falta es ensamblarlo y acotar lo que sostiene.

El marco teórico ya declara el problema en estos términos: «no se identificó, entre los trabajos
revisados, evidencia concluyente sobre cuál de las dos familias conviene con ventanas cortas y
volúmenes reducidos, de modo que la comparación entre ambas forma parte del diseño experimental»
(`cap3_marco_teorico.md:37`). La reformulación del tutor no amplía el alcance: lo explicita.

## 2. Métricas exactas, bosque aleatorio frente a GRU bidireccional

Sobre validación, de los registros. `synthetic_v2` es el conjunto oficial; `synthetic_v3` es análisis
de sensibilidad **no adoptado**, idéntico salvo por tener el triple de sesiones.

| Conjunto | Modelo | Exactitud | F1 macro | F1 ponderado | Exactitud equilibrada | ECE | Exceso de confianza | n |
|---|---|---|---|---|---|---|---|---|
| `synthetic_v2` | bosque | **0,8776** | **0,8788** | 0,8709 | 0,8571 | 0,1439 | −0,1395 | 98 |
| `synthetic_v2` | BiGRU | 0,8265 | 0,8230 | 0,8153 | 0,8155 | 0,1317 | +0,0070 | 98 |
| `synthetic_v3` | bosque | 0,9242 | 0,9321 | 0,9239 | 0,9235 | 0,0801 | −0,0644 | 343 |
| `synthetic_v3` | BiGRU | **0,9388** | **0,9446** | 0,9391 | 0,9388 | **0,0163** | +0,0112 | 343 |

Fuentes: `experiments/E6_baseline_synthetic_v{2,3}.json`, `experiments/E7_temporal_synthetic_v{2,3}.json`.
Referencia mínima, clase mayoritaria: F1 macro 0,0741 en los dos conjuntos. GRU: 19 014 parámetros,
mejor época 33 de 74 en `v2` y 27 de 68 en `v3`, semilla 20260901, dispositivo MPS.

**Dos lecturas que no deben perderse.**

La primera es la **asimetría de la comparación**, ya declarada en el informe de E7: la GRU restaura la
época con mejor F1 macro **de validación** y se publica esa misma cifra, de modo que es el máximo de
entre sesenta y setenta y cuatro evaluaciones sobre el conjunto que se reporta; el bosque no
selecciona nada sobre validación. El sesgo favorece a la GRU. Por eso la derrota en `v2` es
**conservadora** —pierde a pesar del sesgo— y la ventaja de 0,0125 en `v3` es **inconclusa**, no
favorable.

La segunda es la **calibración**, que forma parte del criterio de PI.1 y que no suele mirarse en esta
comparación: la GRU está mejor calibrada que el bosque en los dos conjuntos y es prácticamente
insesgada, mientras el bosque es infraconfiado y necesita calibración isotónica posterior para bajar
de 0,1439 a 0,085. En `v3` la GRU alcanza un ECE de 0,0163 sin calibrar. La misma asimetría de la
selección de época afecta también a esta cifra, de modo que no sostiene una afirmación comparativa;
sí sostiene que la ventaja del bosque no es uniforme en todas las dimensiones de M1.

**Discrepancia documental que hay que resolver antes de citar nada.** El informe
`docs/experiments/E7_modelo_temporal.md` publica para `synthetic_v2` cifras que **no son las de sus
propios registros**: agregado 0,876 / 0,822 frente a 0,8788 / 0,8230; por clase, normal 0,836 / 0,702
frente a 0,8235 / 0,7692, termostato 0,783 / 0,857 frente a 0,7826 / 0,8148; y 60 épocas con la mejor
en la 19 frente a 74 con la mejor en la 33. Su columna de `synthetic_v3`, en cambio, coincide con el
registro. La causa está en el historial: los registros de E6 y E7 se regeneraron el 1 de septiembre al
calibrar el generador contra el manual de taller (`770ce70`), posterior a la prosa del informe
(`27b9f8d`), y la tabla de `v2` no se actualizó. El capítulo 5 **sí** cita los registros vigentes
(0,827 / 0,823). Manda el registro; el informe de fase hay que corregirlo.

## 3. Resultados desagregados por tipo de fallo

F1 por clase, validación, de los registros. La columna «mejor» no afirma significación: es el signo de
la diferencia en una sola ejecución.

### `synthetic_v2`, el conjunto oficial — 98 ventanas

| Fallo | Tabular (ventana) | Secuencial | Diferencia | Mejor | Evidencia temporal | Interpretación acotada |
|---|---|---|---|---|---|---|
| sin fallo | **0,8235** | 0,7692 | −0,0543 | tabular | — | la clase más abundante y la que recibe todos los errores de las demás |
| F01 fuga de vacío | **1,0000** | 0,9655 | −0,0345 | tabular | no hay margen | el nivel de los ajustes de combustible la separa por completo (delta 1,00, E4) |
| F02 deriva de caudalímetro | **1,0000** | 0,9231 | −0,0769 | tabular | no hay margen | separable por el nivel de los ajustes, no por el caudal (E4, hallazgo 1) |
| **F03 termostato bloqueado** | 0,7826 | **0,8148** | **+0,0322** | **secuencial** | **sí** | único fallo donde la secuencia gana; ver sección 4 |
| F04 sonda lenta | **1,0000** | 0,9655 | −0,0345 | tabular | no hay margen | separable por la **dispersión** de la sonda (delta 1,00, E4) |
| F05 fallo de encendido | **0,6667** | 0,5000 | −0,1667 | tabular | no, con este volumen | el peor de los dos modelos; episodios intermitentes de 1-3 s |

Exhaustividad, que es donde se ve el mecanismo: en el termostato el bosque recupera 9 de 14 ventanas
(0,6429, precisión 1,0000) y la GRU 11 de 14 (0,7857, precisión 0,8462). La secuencia **detecta dos
ventanas más a cambio de dos falsos positivos** sobre la clase sin fallo.

### `synthetic_v3`, sensibilidad no adoptada — 343 ventanas

| Fallo | Tabular | Secuencial | Diferencia | Mejor |
|---|---|---|---|---|
| sin fallo | 0,8750 | **0,9064** | +0,0314 | secuencial |
| F01 fuga de vacío | **1,0000** | 0,9899 | −0,0101 | tabular |
| F02 deriva de caudalímetro | **1,0000** | 0,9897 | −0,0103 | tabular |
| **F03 termostato bloqueado** | 0,8571 | **0,8911** | +0,0340 | secuencial |
| F04 sonda lenta | **1,0000** | 0,9792 | −0,0208 | tabular |
| **F05 fallo de encendido** | 0,8602 | **0,9111** | +0,0509 | secuencial |

El patrón es **consistente, no aleatorio**: la secuencia gana donde hay margen que ganar —termostato en
los dos conjuntos, y con más datos también el fallo de encendido y la clase sin fallo— y pierde por
poco en los tres fallos donde el tabular ya está en 1,0000 y no hay nada que mejorar. En el termostato
gana en los dos volúmenes, que es el dato más robusto de toda la comparación.

### La estructura del error, que es el hallazgo transversal

Las matrices de confusión concentran **todo** el error en una sola dirección: ventanas con fallo
clasificadas como sin fallo. No hay diagnósticos cruzados entre fallos.

| | Termostato → sin fallo | Encendido → sin fallo |
|---|---|---|
| bosque, `v2` | 5 de 14 | 7 de 14 |
| BiGRU, `v2` | 3 de 14 | 9 de 14 |
| bosque, `v3` | 10 de 49 | 9 de 49 |
| BiGRU, `v3` | 4 de 49 | 8 de 49 |

Para un sistema que va a explicar, es la dirección de error menos dañina, y el capítulo 5 ya lo dice.
Para esta pregunta es además la pista: los dos únicos fallos con error son los dos cuya **señal no está
presente en todas las ventanas que llevan su etiqueta**.

## 4. Evidencia específica del termostato bloqueado

El fallo está definido en el generador como un **techo duro a 71 °C** sobre la temperatura de
refrigerante, con ruido de ±0,5 °C (`obd/faults.py`, `default_params={"temp_cap_c": 71.0}`). Su propia
documentación lo describe así: «la firma es una ausencia —algo que debería subir y no sube— y por eso
es fácil de pasar por alto».

De esa definición se sigue, sin medir nada: **mientras el motor no habría superado 71 °C por sí mismo,
el fallo no modifica ninguna muestra**, y la ventana es idéntica a una ventana sana. La etiqueta, sin
embargo, dice F03. El capítulo 5 ya lo recoge como límite físico de detección.

Las dos comprobaciones descriptivas que siguen son sobre entrenamiento y validación, con los datos ya
generados, sin modelo:

| Partición | Clase | n | Máximo de refrigerante, mediana | Ventanas con máximo < 70 °C |
|---|---|---|---|---|
| entrenamiento | sin fallo | 112 | 82,32 °C | 23 (21 %) |
| entrenamiento | termostato | 56 | 72,20 °C | 4 (7 %) |
| validación | sin fallo | 28 | 82,27 °C | 8 (29 %) |
| validación | termostato | 14 | 72,12 °C | **5 (36 %)** |

Y esas ventanas frías **no están repartidas al azar**: están todas en el régimen de calentamiento, que
es el único que arranca a temperatura ambiente —`initial_coolant_c=None`, «se sustituye por la
ambiente», `obd/regimes.py`—.

| Partición | Régimen | n | Máximo de refrigerante, mediana | Con máximo < 70 °C |
|---|---|---|---|---|
| entrenamiento | `highway` | 14 | 72,23 °C | 0 |
| entrenamiento | `idle` | 21 | 72,29 °C | 0 |
| entrenamiento | `urban` | 14 | 72,19 °C | 0 |
| entrenamiento | `warmup` | 7 | 68,85 °C | 4 |
| validación | `urban` | 7 | 72,24 °C | 0 |
| validación | `warmup` | 7 | 65,32 °C | **5** |

**Cinco ventanas sin señal y cinco ventanas falladas por el bosque.** Los dos recuentos coinciden, y la
coincidencia es coherente con todo lo demás: los tres casos de termostato que E9 atribuye están
acertados con confianza 0,948-0,951 y son los tres del régimen urbano, donde el techo actúa desde la
primera muestra; y la ventana de termostato que el modelo falla en la anotación sellada de E19 es
`F03_thermostat_stuck__warmup__11@120s`, de calentamiento.

**Lo que no puedo afirmar, y hay que decirlo:** que sean *las mismas* cinco ventanas. Los registros de
E6 y E7 guardan la matriz de confusión agregada, **no las predicciones por ventana**, de modo que la
identificación una a una no es comprobable con los artefactos existentes. `docs/matriz_validacion_pi.md`
sí afirma el reparto por temperatura —«las ventanas que el modelo falla tienen 54,3 °C de media; las
que acierta, 70,7»—, pero **esas dos cifras no tienen registro**: son una de las cinco que el hallazgo
`EVID-MAJ-019` del verificador de evidencia tiene abiertas por ese motivo. Para llevar esto al jurado
hay que regenerarlo como artefacto, y eso es una reejecución sobre validación, no un experimento nuevo.

**Qué puede explicar la ventaja de la secuencia, dicho como asociación y no como causa.** Los
descriptores de ventana **no** son ciegos a la dinámica: el bosque usa sobre todo los diferenciales del
refrigerante —`delta_max` es el tercer descriptor más importante de los 139, `autocorr1` el séptimo,
`delta_min` el noveno, `crossings` el decimocuarto— y apenas usa la pendiente lineal, que queda en el
puesto 47 con importancia 0,0041, ni el nivel medio, puesto 28. E9 confirma el mismo cuarteto en los
tres casos de termostato. Lo que esos estadísticos resumen, la secuencia lo tiene entero: **la forma de
la trayectoria dentro de la ventana**, es decir si la subida se aplana o continúa. En una ventana de
calentamiento por debajo de 71 °C, un refrigerante que se aplana antes de lo que correspondería es la
única diferencia posible frente a un calentamiento sano, y es una diferencia de forma, no de nivel ni
de pendiente media. Es la hipótesis compatible con los datos; no está demostrada, y demostrarla exige
localizar los aciertos y fallos de los dos modelos ventana a ventana.

Ninguno de los dos modelos ve el **tiempo desde el arranque**: no hay descriptor de tiempo entre los
139 y la GRU recibe una ventana de 120 s sin su posición en la sesión. El instante de la ventana existe
en los metadatos (`t_start`) y no entra como entrada. Esa es una decisión de diseño con consecuencia
directa sobre este fallo, y conviene declararla.

## 5. Qué parte de PI.1 está demostrada

Sobre **validación** y sobre datos sintéticos:

1. el bosque aleatorio diagnostica muy por encima de la referencia mínima: F1 macro 0,8788 frente a
   0,0741 de la clase mayoritaria, exactitud 0,8776 frente a 0,2857;
2. su confianza queda calibrada: ECE de 0,1439 a 0,085, sesgo de −0,140 a +0,009;
3. la atribución produce, para cada caso, señal, estadístico, valor, dirección y ventana temporal, y
   describe con señales coherentes con el mecanismo la fuga de vacío, el termostato y la sonda;
4. la estructura del error es benigna: todos los errores van a la clase sin fallo, sin diagnósticos
   cruzados;
5. **el contraste con el modelo secuencial está hecho**, con su resultado negativo en agregado sobre
   el conjunto oficial y su ventaja consistente en el termostato en los dos volúmenes.

## 6. Qué parte permanece sin demostrar

1. **La formulación original de PI.1** —«un modelo temporal sobre ventanas OBD-II supera de forma clara
   al baseline y a la clase mayoritaria», `research/traceability-matrix.md:29`— **no se cumple**. Está
   declarado en el capítulo 5 y en el capítulo 4. Conviene además resolver que la matriz de validación
   enuncia el criterio de PI.1 de otra forma —margen sobre la mayoritaria y calibración— y la de
   trazabilidad conserva la original: hay dos enunciados del mismo criterio en el repositorio.
2. **No hay evaluación sobre el conjunto de prueba.** E8 figura como PLANNED y la evaluación final se
   ejecutó el 1 de octubre y quedó interrumpida (`INC-E19-01`), de modo que el diagnóstico sobre prueba
   sigue sin medirse.
3. **Ninguna comparación tiene réplicas ni intervalos.** Una ejecución por modelo y conjunto, una
   semilla. Las diferencias por clase son de dos o tres ventanas sobre catorce.
4. **La comparación es asimétrica** por la selección de época sobre validación. Sin corregirla, ningún
   orden entre los dos modelos es sostenible, ni a favor ni en contra.
5. **La ventaja en el termostato no tiene mecanismo demostrado**, por lo dicho en la sección 4.
6. **No existe la representación puntual.** Solo hay dos modelos en el código, el tabular sobre
   descriptores y el secuencial sobre series; no hay clasificador por muestra.
7. **El fallo de encendido sigue abierto**: 0,6667 en `v2` y 0,8602 en `v3` para el tabular. E7 corrigió
   la cautela de E5 y E6 —la condición sí es clasificable, faltaban datos— pero esa corrección descansa
   en el conjunto no adoptado.

## 7. Qué ablaciones faltan realmente

Las tres representaciones que el tutor plantea están cubiertas así:

| | Representación | Experimento | Estado |
|---|---|---|---|
| **A** | puntual / estado, una muestra | — | **no existe** |
| **B** | descriptores de ventana | E6, bosque aleatorio | ejecutado dos veces |
| **C** | secuencia cruda | E7, GRU bidireccional | ejecutado dos veces |

**B y C no hay que repetirlos.** La comparación existe; lo que falta es presentarla desagregada y
corregir su asimetría.

**A no existe, y antes de construirlo conviene preguntarse qué respondería.** Un clasificador por
muestra sobre doce señales instantáneas no podría detectar, por construcción, los dos fallos definidos
por dispersión o por intermitencia —sonda lenta y fallo de encendido—, y para la fuga de vacío, la
deriva y el termostato daría previsiblemente lo mismo que el nivel, que E4 ya midió señal a señal con
delta de Cliff. Mi recomendación es **no construirlo** y usar en su lugar lo que ya está medido: E4
**es** el análisis de la información puntual, por señal y por vía, y basta citarlo como tal. Si se
quiere el escalón A como modelo, la versión honesta y barata es el mismo bosque sobre un subconjunto de
descriptores de nivel —media, mínimo, máximo—, que aísla «nivel» frente a «dinámica dentro de la
ventana» frente a «secuencia completa» con un solo entrenamiento más y sin arquitectura nueva.

Las ablaciones **A1-A4 de E18 son otro eje**: desmontan el criterio de suficiencia del agente, no la
representación de la telemetría. No se solapan con esto. Y la tercera prioridad del tutor —ablaciones
sobre el conjunto de prueba— es la de E18 repetida sobre prueba, que sigue pendiente.

## 8. ¿Hacen falta más datos sintéticos?

La pregunta correcta no es si hacen falta más, sino **si el volumen es la limitación relevante**, y la
evidencia disponible apunta a que sí, con dos puntos de volumen y una sola semilla cada uno:

| Conjunto | Sesiones | Ventanas de entrenamiento | F1 macro bosque | F1 macro BiGRU | Diferencia |
|---|---|---|---|---|---|
| `synthetic_v2` | 72 | 392 | 0,8788 | 0,8230 | −0,0558 |
| `synthetic_v3` | 216 | 1 078 | 0,9321 | 0,9446 | +0,0125 |

El orden se invierte al triplicar las sesiones, y el salto mayor es el del fallo de encendido en el
modelo secuencial: 0,5000 → 0,9111. Pero dos puntos no son una curva de aprendizaje, la diferencia en
`v3` es menor que el sesgo de la selección de época, y no hay réplicas. **Con lo que hay no se puede
afirmar que el volumen sea la limitación, solo que es la explicación más compatible.**

**No propongo ampliar el conjunto todavía**, y el motivo es que hay dos pasos más baratos y más
informativos que se hacen sobre los datos que ya existen:

1. **Quitar la asimetría.** Seleccionar la época sobre una partición interna de entrenamiento y evaluar
   después sobre validación. Sin esto, ningún número de la comparación es interpretable, con cuantos
   datos sea. Coste: reentrenar la GRU, menos de un minuto por ejecución en `v2`.
2. **Réplicas con semillas distintas** sobre los dos conjuntos que ya existen, cinco por modelo y
   conjunto. Con veinte ejecuciones se obtiene la dispersión de las diferencias por clase y se sabe si
   el +0,0322 del termostato sobrevive al ruido de la semilla. Coste: minutos en `v2`, unos veinte
   en `v3`.

Esos dos pasos pueden convertir la comparación en una afirmación sostenible o en un resultado
declaradamente inconcluso, y en los dos casos el TFM gana. Solo si tras ellos la diferencia sigue
dependiendo del volumen tiene sentido generar más datos.

## 9. Qué cantidad adicional propongo, y por qué

Si tras los dos pasos de la sección 8 hace falta volumen, propongo **una sola realización intermedia y
una variación dirigida**, no una ampliación masiva:

1. **Un punto intermedio de volumen: 144 sesiones, 24 por condición**, entre las 72 de `v2` y las 216
   de `v3`. Con tres volúmenes y réplicas se puede dibujar una curva de aprendizaje por clase y decir
   si la ventaja secuencial crece con los datos o es un artefacto. Es el mínimo que convierte dos
   puntos en una tendencia.
2. **Variación dirigida del régimen de calentamiento, que es donde vive el problema.** La sección 4
   muestra que todo el error del termostato está en las sesiones de calentamiento, y `v2` tiene **siete
   ventanas** de ese régimen en entrenamiento y siete en validación. Generar más realizaciones del
   **mismo escenario** variando solo `ambient_temp_c` y `duration_s` —los dos parámetros que el
   generador expone y que gobiernan cuánto tarda el motor en alcanzar el techo— multiplicaría la
   evidencia justo donde las dos representaciones se diferencian, sin tocar el fenómeno ni añadir
   escenarios. Para el fallo de encendido, el parámetro análogo es `fault_onset_s` junto con `rate`.

Lo que **no** propongo: nuevos escenarios, nuevas arquitecturas, ni adoptar `synthetic_v3` como
conjunto oficial. Adoptarlo obligaría a regenerar E4, E5, E6, E9 y toda la cadena de suficiencia, que
está congelada para E19. `synthetic_v3` debe seguir siendo análisis de sensibilidad declarado.

Cada realización nueva registraría su `SessionSpec` completa —identificador, régimen, duración,
semilla, fallo, instante de aparición, temperatura ambiente y parámetros del fallo—, que es lo que el
generador ya hace reproducible.

## 10. Qué documentos deben actualizarse

Cuando el autor apruebe el enfoque. Ninguno se ha tocado en esta auditoría.

| Documento | Cambio |
|---|---|
| `docs/experiments/E7_modelo_temporal.md` | **corregir las cifras obsoletas de `synthetic_v2`** por las de los registros, y fechar la corrección. Es lo primero, porque hoy el informe contradice a su propio registro |
| `research/traceability-matrix.md` | reconciliar el enunciado de PI.1 con el de la matriz de validación, y recoger el resultado negativo con su cadena E4 → E6 → E7 |
| `docs/matriz_validacion_pi.md` | añadir la desagregación por fallo; dar registro a las cifras 54,3 / 70,7 °C o retirarlas hasta tenerlo (`EVID-MAJ-019`) |
| `docs/experiment-index.md` | E6 y E7 ya declaran el resultado correctamente; añadir la fila de la comparación desagregada cuando exista su artefacto |
| `docs/memoria/cap4_marco_metodologico.md` | declarar explícitamente las tres representaciones como variantes de análisis dentro del mismo diseño, y la asimetría de la selección de época como limitación del contraste |
| `docs/memoria/cap5_resultados.md` | incorporar la tabla desagregada por fallo y la estructura del error; el texto actual ya es correcto y no hay que reinterpretarlo |
| `docs/memoria/cap6_conclusiones.md` | una frase: el modelo más complejo no fue automáticamente mejor, y el valor del contexto temporal depende del patrón diagnóstico |
| `docs/limitations.md` | la asimetría de la comparación, la ausencia de réplicas, el límite físico del termostato y la ausencia del tiempo desde arranque como entrada |
| `JURY_GUIDE.md` | señalar dónde se lee este resultado negativo, que es uno de los más defendibles del trabajo |

## Lo que esta auditoría recomienda decidir

1. **Corregir el informe de E7** y dar registro a las cifras del termostato. Son dos defectos de
   trazabilidad, no de ciencia, y ensucian el resultado más interesante que hay.
2. **No construir la representación puntual** como modelo nuevo: E4 ya la cubre, y si se quiere el
   escalón, hacerlo con el mismo bosque sobre descriptores de nivel.
3. **Quitar la asimetría y añadir réplicas antes de generar un solo dato nuevo.**
4. **Mantener las tres prioridades del tutor por delante**: rediseño del distractor, reentrenamiento
   del adaptador y ablaciones sobre prueba. Y antes que todas ellas, cerrar E19, que está a medias.
5. **Presentar el resultado negativo como resultado**, con su salvedad por fallo. La memoria ya lo
   hace; lo que falta es la tabla desagregada que lo hace comprobable de un vistazo.
