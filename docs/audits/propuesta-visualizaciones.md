# Propuesta de visualizaciones científicas adicionales

**Fecha:** 14 de octubre de 2026 · **Qué es:** qué se puede ver con los datos que ya existen y hoy
no se ve · **Qué NO hace:** no ejecuta ningún experimento, no regenera ningún conjunto histórico y no
modifica ninguna conclusión. **Nada de esto está implementado todavía** · **Regla que gobierna la
propuesta:** se propone solo lo que se puede dibujar con lo que hay en disco

---

## 0. Lo primero: qué datos hay, porque determina qué se puede proponer

Antes de proponer una sola figura conviene saber qué permite el material. Esto es lo medido hoy.

| Fuente | Qué contiene | Qué permite |
|---|---|---|
| `synthetic_v2` crudo | **72 sesiones × 600 s**, 12 señales a 1 Hz, con `regime`, `fault_id` y **`fault_active` muestra a muestra** | series temporales completas, y el instante exacto en que entra el fallo |
| `synthetic_v2_x.npy` | **(588, 120, 12)**: las ventanas de 120 s **tal como el modelo las recibe** | enseñar lo que el modelo ve, no una reconstrucción de ello |
| `synthetic_v2_features.npy` | (588, **139**) descriptores por ventana: 36 de nivel, 96 de variación, 6 correlaciones y 1 cociente | qué resume cada descriptor y qué pierde |
| `meta.parquet` | ventana → sesión, régimen, `t_start`, `t_end`, partición, etiqueta | situar cada ventana sobre su sesión |
| `E9_atribuciones` | 180 atribuciones, 18 casos, 50 descriptores | qué descriptores usa el modelo, por condición |
| `E15` y `E19` | confianza y cobertura **por caso**: 17 y 35 | distribuciones de decisión |

### Dos límites que hay que declarar antes de proponer nada

**No hay sesiones pareadas en el conjunto canónico.** Las 72 sesiones de `synthetic_v2` tienen
**72 semillas distintas**, una cada una. No existe en el conjunto una sesión sana y otra averiada con
la misma semilla y el mismo perfil de conducción. Comparar una sesión normal con una averiada compara
**dos conducciones distintas**, y la mayor parte de lo que se vería sería el perfil, no el fallo. La
única figura pareada del trabajo —la A.1— procede de E4, que **generaba sus propias sesiones**, y es
el artefacto histórico que no se puede regenerar.

**No hay confianzas por ventana.** Los registros de E6 y E7 guardan agregados y la matriz de
confusión, no la probabilidad de cada una de las 98 ventanas. Hay confianzas **por caso anotado**,
17 en validación y 35 en la evaluación final, y nada más. Eso descarta la curva de fiabilidad y el
histograma de confianzas sobre validación.

---

## 1. Lo que ya existe

**En la memoria**, dieciocho figuras, auditadas y con la cadena de procedencia verificada: cuatro
dibujadas a mano en el paquete de visualización, once calculadas desde un artefacto congelado y tres
históricas que no se regeneran.

**En los cinco notebooks entregables**, dieciséis celdas que construyen una figura —una en el de
introducción, cinco en el de exploración, cinco en el de comparación de modelos, tres en el de la
evaluación final y dos en el de explicabilidad—. Parte de ellas son las mismas que la memoria
incorpora, porque invocan el paquete; el resto vive solo en el notebook. Los notebooks 05 y 06 no
construyen ninguna figura propia: toman las del paquete.

**Ninguna propuesta de este documento duplica una existente.** Donde una figura nueva se acercaría a
otra, se dice y se descarta.

---

## 2. Series temporales OBD-II · el bloque prioritario

### T1 · Lo que el modelo ve frente a lo que ocurrió — **PRIORITARIA**

| | |
|---|---|
| **Qué analiza** | qué pierde un descriptor agregado respecto de la ventana de la que sale |
| **Experimento** | E5 y E6 |
| **Datos** | `synthetic_v2_x.npy` —la ventana literal que entra al modelo— junto a la sesión completa del parquet crudo, y el descriptor correspondiente de `features.npy` |
| **Librería** | Matplotlib |
| **Notebook** | `01_exploracion_obd` |
| **Qué mostraría** | tres paneles de una ventana de fallo de encendido: la señal de régimen a 1 Hz con sus episodios marcados; la misma ventana con su media y su desviación superpuestas; y el valor de los dos descriptores que de ahí salen. Cada episodio dura entre uno y tres segundos sobre una ventana de ciento veinte |
| **Valor científico** | es la explicación visual de por qué el bosque detecta el fallo de encendido en **7 de 14 ventanas** de validación —recuerdo 0,50, y los otros 7 van a «sin fallo»—. Hoy esa asimetría está en la Tabla 5.1 y en la Figura 5.3 como número, y no se ve de dónde sale |
| **Ubicación** | **capítulo 5**, apartado de PI.1, junto a la Figura 5.6 |
| **Limitaciones** | una ventana elegida como ilustración, no una muestra. La cifra del 5,7 % de instantes alterados que el capítulo 5 cita **procede de `synthetic_v1`** y no debe aparecer en el pie de una figura dibujada sobre `synthetic_v2`: la proporción se recalcularía sobre la sesión dibujada, o no se cita |
| **¿Ejecuta código experimental?** | **no**: lee tres ficheros del disco |

### T2 · La entrada del fallo dentro de una misma sesión — **PRIORITARIA**

| | |
|---|---|
| **Qué analiza** | cómo cambia cada señal cuando el fallo entra, sin comparar sesiones distintas |
| **Experimento** | E2 y E4 |
| **Datos** | parquet crudo, usando `fault_active` para marcar el instante de entrada |
| **Librería** | Matplotlib |
| **Notebook** | `01_exploracion_obd` |
| **Qué mostraría** | una sesión por condición, con las dos o tres señales que su ficha declara, y la línea vertical del instante de entrada. El contraste es **dentro de la misma sesión**, de modo que el perfil de conducción no cambia |
| **Valor científico** | sustituye con datos canónicos lo que hoy solo muestra la Figura A.1, que es histórica, de `synthetic_v1` y no reconstruible. **No la reemplaza**: la acompaña |
| **Ubicación** | **anexo A**, junto a A.1 |
| **Limitaciones** | no es una comparación pareada: antes y después del fallo también cambia el estado del motor —temperatura, por ejemplo—. Lo que se ve es la evolución, no el efecto aislado |
| **¿Ejecuta código experimental?** | **no** |

### T3 · Persistente frente a episódico — **PRIORITARIA**

| | |
|---|---|
| **Qué analiza** | que los cinco fallos no tienen la misma forma temporal, y que eso explica sus resultados |
| **Experimento** | E2, E4 y E6 |
| **Datos** | parquet crudo, una sesión de cada condición |
| **Librería** | Matplotlib |
| **Notebook** | `06_expresion_del_fallo` |
| **Qué mostraría** | cinco paneles alineados en el tiempo: la deriva del caudalímetro como rampa de cinco minutos, el termostato como techo constante, la sonda como amortiguación de la oscilación, la fuga como desplazamiento persistente y el encendido como episodios de uno a tres segundos |
| **Valor científico** | es el argumento visual de la Figura 5.6 y del límite de evidencia de la 5.5. Conecta la forma del fallo con su detectabilidad, que es la parte de PI.1 que hoy se sostiene solo en prosa |
| **Ubicación** | **capítulo 5**, análisis descriptivo |
| **Limitaciones** | una sesión por condición; las formas son las que el generador declara, de modo que la figura **ilustra el instrumento** y no descubre nada sobre vehículos reales |
| **¿Ejecuta código experimental?** | **no** |

### T4 · Las ventanas de análisis sobre la sesión — **RECOMENDABLE**

| | |
|---|---|
| **Qué analiza** | cómo el ventanado de 120 s con paso de 60 corta una sesión, y qué ventanas quedan a caballo de la entrada del fallo |
| **Experimento** | E5 |
| **Datos** | `meta.parquet` con `t_start` y `t_end`, sobre la serie cruda |
| **Librería** | Matplotlib |
| **Notebook** | `01_exploracion_obd` |
| **Valor científico** | hace visible el solape y, sobre todo, que **las ventanas anteriores a la entrada del fallo se etiquetan como sin fallo**, que es la razón de que la clase normal doble a las demás en la Figura 5.1 |
| **Ubicación** | **anexo A** |
| **Limitaciones** | descriptiva: describe el diseño, no mide nada |
| **¿Ejecuta código experimental?** | **no** |

### T5 · Cómo se distinguen entre sí los dos fallos de mezcla pobre — **PRIORITARIA**

Esta propuesta cambió de contenido al comprobarla, y a mejor.

| | |
|---|---|
| **Qué analiza** | qué separa la fuga de vacío de la deriva del caudalímetro, cuando las dos se separan de la condición sin fallo por lo mismo |
| **Experimento** | E4 y E5, sobre datos canónicos |
| **Datos** | `synthetic_v2_features.npy` y `meta.parquet`; parquet crudo para las series |
| **Librería** | **Seaborn** —densidad conjunta y, debajo, barras de separación por descriptor— |
| **Notebook** | `01_exploracion_obd` |

**Qué se midió al comprobarla.** Las dos condiciones son **casi indistinguibles en el agregado**:
frente a la condición sin fallo, las dos dan delta de Cliff **+1,00** en el nivel del ajuste a corto
plazo, y +1,00 y +0,93 en el de largo plazo. El cociente informado por la física
—`maf_over_rpm_load`, construido precisamente para delatar un caudalímetro que subestima— **no las
separa tampoco**: media 0,0004 en las dos y en la condición sin fallo, con los recorridos solapados.

Lo que sí las separa, medido entre sus ventanas, es de otra naturaleza:

| Descriptor | &#124;delta de Cliff&#124; | Qué es |
|---|---|---|
| `map_min` | 0,616 | presión de colector: la fuga la eleva, la deriva no la toca |
| `ltft_bank1_n_events` | 0,587 | **forma** del ajuste a largo plazo dentro de la ventana |
| `stft_bank1_slope` | 0,569 | **pendiente** del ajuste a corto plazo |
| `ltft_bank1_delta_min` | 0,562 | salto descendente máximo |
| `ltft_bank1_autocorr1` | 0,549 | persistencia de la señal |

| | |
|---|---|
| **Valor científico** | tres cosas a la vez. Primero, explica por qué el modelo acierta las dos al 100 % cuando el agregado no las distingue: lo hace con **descriptores de variación y con una señal que una condición toca y la otra no**. Segundo, documenta que el cociente informado por la física no cumple en este conjunto lo que su comentario de diseño esperaba, que es un resultado negativo útil y hoy no está escrito en ninguna parte. Y tercero, es la respuesta defendible a la pregunta del tutor que `P1` no podía dar: no «qué modelo usa el tiempo», sino **qué pares de condiciones solo se separan con descriptores de variación** |
| **Ubicación** | **capítulo 5**, análisis descriptivo; la tabla de descriptores, al **anexo B** |
| **Limitaciones** | 84 ventanas por condición, procedentes de 12 sesiones: las ventanas de una misma sesión **no son independientes**, de modo que la delta de Cliff se publica como tamaño de efecto descriptivo y **no se acompaña de contraste ni de intervalo**. Ningún descriptor llega a separar por sí solo —el mayor es 0,616—: lo que separa es la combinación, y la figura no debe sugerir que basta uno |
| **¿Ejecuta código experimental?** | **no**: lee dos ficheros del preprocesado |

### T6 · Exploración interactiva de una sesión — **OPCIONAL**

| | |
|---|---|
| **Qué analiza** | permite recorrer una sesión completa con zoom sobre cualquier tramo |
| **Librería** | **Plotly** |
| **Notebook** | `01_exploracion_obd`, **solo en el notebook** |
| **Valor científico** | para la defensa: permite responder «¿qué pasa en el segundo 340?» sin salir del notebook. En papel no aporta nada |
| **Ubicación** | **ningún capítulo ni anexo**: una figura interactiva impresa es una captura |
| **Limitaciones** | añade una dependencia a los notebooks y engorda el HTML entregado. Habría que medir cuánto |
| **¿Ejecuta código experimental?** | **no** |

---

## 3. Análisis temporal de PI.1 · lo que el tutor pidió mirar

### P1 · Cuánto del peso atribuido depende de la variación, y por qué no se puede ordenar — **RECOMENDABLE**

Esta era la propuesta que iba a ser la pieza central del documento. Al medirla se cae como respuesta
y se sostiene como límite, y conviene explicar exactamente por qué.

| | |
|---|---|
| **Qué analiza** | si las atribuciones permiten ordenar los fallos según cuánto dependen de la variación dentro de la ventana |
| **Experimento** | E9, cruzado con la definición de los 139 descriptores de E5 |
| **Datos** | `E9_atribuciones_synthetic_v2.csv` —180 atribuciones, 18 casos— y `FEATURE_NAMES` |
| **Librería** | Matplotlib |
| **Notebook** | `04_explicabilidad` |

**Qué se midió.** De los 139 descriptores, 36 son de nivel —media, mínimo y máximo de cada una de
las 12 señales—, 96 son de variación, 6 son correlaciones dentro de la ventana y 1 es un cociente.
Sumando el peso atribuido que va a los de variación, por condición predicha, el resultado depende de
**dónde se traza la línea**, y depende tanto que cambia la respuesta:

| Condición predicha | definición estricta | definición amplia |
|---|---|---|
| sin fallo | 65,0 % | 98,6 % |
| fuga de vacío | 13,9 % | 69,9 % |
| deriva del caudalímetro | 35,1 % | 76,4 % |
| termostato bloqueado | 81,4 % | 93,6 % |
| sonda lambda lenta | 70,7 % | 100,0 % |
| fallo de encendido | 26,3 % | 89,3 % |

La estricta cuenta como variación la desviación, el rango, la pendiente, los saltos, los eventos, la
autocorrelación y los cruces. La amplia añade el mínimo, el máximo y las correlaciones, que también
necesitan la ventana para existir. **Las dos son defendibles.** Y entre una y otra el fallo de
encendido pasa de 26,3 % a 89,3 % —63 puntos— y **la ordenación de los cinco fallos cambia**.

**Valor científico, que no es el que yo esperaba.** No responde a la pregunta del tutor sobre en qué
fallos aporta el contexto temporal: **muestra que las atribuciones disponibles no permiten
responderla**, porque el número que se publicaría sería un artefacto de una decisión del analista y
no una propiedad del modelo. Lo único que se sostiene en las dos definiciones es que **la sonda
lambda lenta está arriba en ambas** —70,7 % y 100,0 %—, que coincide con lo que la Figura 5.2 mide
por un camino independiente: esa condición se separa por la dispersión y no por el nivel. Es un
resultado negativo bien delimitado, y como tal tiene sitio.

| | |
|---|---|
| **Ubicación** | **anexo B**, como límite de la atribución, **no** en el capítulo 5 como medición |
| **Limitaciones** | mide lo que usa **el bosque**, que ya trabaja sobre descriptores calculados sobre una ventana: **no dice nada sobre si un modelo de secuencias lo haría mejor**. Son 18 casos y las diez atribuciones principales de cada uno, no el reparto completo |
| **¿Ejecuta código experimental?** | **no**: lee una tabla y una lista de nombres |

**Lo que esto implica para la recomendación del tutor.** Con los artefactos que existen, la pregunta
«en qué fallos aporta el contexto temporal» **no tiene respuesta medible**: haría falta un
experimento que comparase el mismo estimador sobre representaciones con y sin dimensión temporal, y
eso es ejecutar un experimento nuevo. Esto debe decirse así, y no sustituirse por la tabla de arriba
leída como si ordenara los fallos.

### P2 · El suelo de ruido por longitud de ventana, sobre datos canónicos — **RECOMENDABLE**

| | |
|---|---|
| **Qué analiza** | por qué la ventana son 120 segundos y no 10, 30 o 60 |
| **Experimento** | E5 |
| **Datos** | `E5_estudio_ventana.csv` |
| **Librería** | Matplotlib |
| **Notebook** | `01_exploracion_obd` |
| **Valor científico** | el capítulo 4 justifica la longitud de ventana en una tabla; la curva muestra el compromiso. Es además donde se ve que el fallo de encendido **no cruza el suelo de ruido en ninguna longitud** |
| **Ubicación** | **anexo A**, o sustituir la tabla del capítulo 4 si el director lo prefiere |
| **Limitaciones** | el estudio es de E5 y su figura histórica existe; esta sería una redibujada a la medida de la página |
| **¿Ejecuta código experimental?** | **no** |

### P3 · Comparación Random Forest frente a BiGRU — **NO JUSTIFICADA**

Ya está, y tres veces: la Tabla 5.1 con los agregados, la Figura 5.3 con el destino de los errores y
la Figura B.1 con el detalle por condición. **Una cuarta visualización de lo mismo no añade
evidencia**, y la comparación tiene un confusor declarado —entre los dos conjuntos cambian el volumen
y el generador— que ninguna figura nueva resuelve. Lo que falta no es un gráfico: son réplicas.

---

## 4. Resultados de aprendizaje automático

### M1 · Dónde cae cada decisión de E19 respecto del umbral, y en qué régimen — **PRIORITARIA**

| | |
|---|---|
| **Qué analiza** | qué separa las decisiones correctas de las dos abstenciones innecesarias de la evaluación final |
| **Experimento** | E19, tercer intento |
| **Datos** | `E19_evaluacion_final_v3.csv`: 35 filas, con confianza calibrada, cobertura de afirmaciones, decisión esperada, decisión tomada, motivo y sesión |
| **Librería** | **Seaborn** —puntos con dispersión controlada, una fila por condición— |
| **Notebook** | `03_analisis_e19` |

**Qué se midió al comprobar la propuesta.** Las confianzas calibradas de las 35 filas toman ocho
valores distintos entre 0,490 y 1,000. **Cuatro filas caen por debajo del umbral de 0,79, y son
exactamente las cuatro de las dos abstenciones innecesarias**: la deriva del caudalímetro a 0,5731 y
el fallo de encendido a 0,4905, cada una repetida en dos ejecuciones. Ninguna decisión correcta queda
por debajo del umbral y ninguna abstención innecesaria queda por encima. La puerta de confianza
separa los dos errores de forma limpia, y el motivo registrado en las cuatro empieza por
`LOW_MODEL_CONFIDENCE`.

**Y hay un segundo hecho, que no estaba buscando.** El caso de la deriva del caudalímetro aparece
sobre **dos sesiones distintas de la misma condición**: en `highway` da confianza 0,5731 y se abstiene
cuando debía explicar; en `warmup` da 0,8514 y explica correctamente. Mirando las ocho sesiones de la
evaluación, **las dos abstenciones innecesarias están las dos en sesiones de autopista**, que es
también donde se dan las dos confianzas más bajas de toda la tabla; en ralentí y en calentamiento
ninguna baja de 0,85. La figura hace visible esa coincidencia.

| | |
|---|---|
| **Valor científico** | responde a «¿de qué depende que el sistema se calle cuando no debía?» con los datos que ya existen, y es una de las preguntas que un tribunal haría sobre la Tabla 5.7. Complementa la Figura 5.10 sin repetirla: aquella enfrenta documentos con cobertura, esta enfrenta confianza con decisión y con régimen |
| **Ubicación** | **capítulo 5**, apartado de la evaluación final |
| **Limitaciones, y son estrictas** | **ocho sesiones y dos errores**: la coincidencia con el régimen de autopista es una **observación sobre dos casos**, no un efecto estimado, y no se puede publicar como «el sistema falla en autopista». Con `n = 2` no hay contraste posible, y el pie de la figura debe decirlo. Las 35 filas no son independientes: proceden de ocho ventanas y de tres ejecuciones que reutilizan casos |
| **¿Ejecuta código experimental?** | **no** |

### M2 · Diagrama de enjambre de atribuciones al estilo SHAP — **OPCIONAL**

| | |
|---|---|
| **Qué analiza** | la dispersión de cada atribución entre casos, no solo su media |
| **Datos** | `E9_atribuciones`: 180 filas, **las diez principales de cada caso** |
| **Librería** | **SHAP**, o Matplotlib si la biblioteca exige su propio objeto de explicación |
| **Limitaciones, y pesan** | la tabla guarda **solo las diez atribuciones principales por caso**, no las 139. Un enjambre construido así **no es el enjambre de SHAP**: está truncado, y presentarlo con el aspecto del gráfico canónico de la biblioteca induciría a leerlo como si fuera completo. Reconstruirlo entero exigiría **recalcular las atribuciones**, que es ejecutar un experimento |
| **Ubicación** | **notebook** `04_explicabilidad`, y solo si se etiqueta como truncado |
| **¿Ejecuta código experimental?** | **no**, si se acepta truncado; **sí**, si se quiere completo |

### M3 · Curva de fiabilidad por tramos — **NO JUSTIFICADA, por falta de datos**

Requiere la **probabilidad de cada una de las 98 ventanas de validación**, y los registros de E6 y E7
no la guardan: conservan los agregados, el error de calibración por tramos ya calculado y la matriz
de confusión. Dibujarla exigiría reejecutar el modelo conservando las predicciones, que es ejecutar
un experimento. **Se descarta**, y conviene que conste por qué: el notebook 02 ya lo declara como
límite de la Figura 5.7.

### M4 · Histograma de confianzas sobre validación — **NO JUSTIFICADA**, por la misma razón.

---

## 5. Resumen y recomendación

| Propuesta | Clase | Dónde | ¿Ejecuta algo? |
|---|---|---|---|
| **T1** lo que el modelo ve frente a lo que ocurrió | **prioritaria** | capítulo 5 | no |
| **T2** la entrada del fallo dentro de una sesión | **prioritaria** | anexo A | no |
| **T3** persistente frente a episódico | **prioritaria** | capítulo 5 | no |
| **M1** dónde cae cada decisión de E19, y en qué régimen | **prioritaria** | capítulo 5 | no |
| **T5** cómo se distinguen entre sí los dos fallos de mezcla pobre | **prioritaria** | capítulo 5 + anexo B | no |
| **T4** las ventanas sobre la sesión | recomendable | anexo A | no |
| **P1** el peso de la variación, y por qué no ordena | recomendable | anexo B | no |
| **P2** suelo de ruido por longitud de ventana | recomendable | anexo A | no |
| **T6** exploración interactiva | opcional | solo notebook | no |
| **M2** enjambre de atribuciones truncado | opcional | solo notebook | no |
| **P3** cuarta comparación de modelos | **no justificada** | — | — |
| **M3** y **M4** curva de fiabilidad e histograma | **no justificada** | — | exigirían reejecutar |

**Si hubiera que elegir una sola, sería `M1`**, y no la que yo tenía previsto recomendar. Al
comprobar las cifras resultó que la puerta de confianza separa exactamente los dos errores de la
evaluación final, y que los dos caen en sesiones de autopista. Eso es material nuevo sobre el
resultado principal del trabajo, obtenido de una tabla que ya estaba en disco.

**Si hubiera que elegir dos, la segunda sería `T5`**, que al comprobarla resultó contener un resultado negativo que el trabajo no tiene escrito —el cociente informado por la física no separa las dos condiciones para las que se construyó— y la respuesta defendible a la pregunta del tutor.

**Y si hubiera que elegir tres, la tercera sería `T1`**: es la que convierte en visible el argumento que
el capítulo repite en prosa, que un agregado puede esconder lo que ocurrió dentro de la ventana —el
fallo de encendido se detecta en 7 de 14 ventanas, y las otras 7 se leen como «sin fallo»—.

Las cinco prioritarias añadirían **cinco figuras al cuerpo** —cuatro al capítulo 5 y una al anexo
A—, más una tabla al anexo B, lo que llevaría el documento de 18 a 23 figuras y de 135 a unas 141
páginas.

## 6. Lo que esta propuesta no hace, y una decisión que no es mía

No propone ninguna figura que exija ejecutar un experimento, reentrenar un modelo, abrir el conjunto
de prueba o regenerar un conjunto histórico. No propone sustituir ninguna figura existente, ni la
A.1 ni la 5.5, que son artefactos históricos. No propone generar sesiones sintéticas nuevas para
ilustrar un comportamiento: **todas las series salen de las 72 sesiones que el experimento ya
produjo**. Y descarta cuatro visualizaciones que serían útiles y que los datos no sostienen.

**La decisión que corresponde al autor.** La comparación más clara que se podría dibujar —la misma
conducción con y sin fallo, que aislaría el efecto de la avería del perfil de conducción— exige
**regenerar la contrafactual declarada** de una sesión existente: la misma semilla y el mismo perfil,
con el fallo desactivado. El mecanismo ya se usa en el trabajo: es el que produce la Figura 5.6 en el
notebook 06. No genera una serie nueva en el sentido de inventar un comportamiento, porque la
contrafactual está determinada por la ficha de la sesión; pero **produce muestras que no están en el
conjunto congelado**, y por eso no lo doy por autorizado. Si el autor lo autoriza, `T2` pasaría de
«evolución dentro de una sesión» a una comparación pareada propiamente dicha, que es bastante más
fuerte. Si no, `T2` se queda como está propuesta, que ya es correcta.

## 7. Una corrección sobre esta propuesta

La versión con la que llegué a este documento daba `P1` por pieza central y prioritaria, con la idea
de que medía en qué fallos aporta la dimensión temporal. Al comprobar las cifras contra la tabla de
atribuciones, el resultado se movía hasta 63 puntos según dónde se trazara la línea entre descriptor
de nivel y descriptor de variación, y la ordenación de los cinco fallos cambiaba con ella. La
propuesta queda recalificada a recomendable y reformulada como lo que es, un límite de la atribución.
Lo dejo escrito porque el documento habría afirmado, con aspecto de medición, algo que la evidencia
no sostiene.

Lo mismo pasó en la otra dirección con `T5` y con `M1`. `T5` iba a mostrar cómo se relacionan las dos
correcciones de combustible; al medirlo resultó que las dos condiciones son **casi indistinguibles**
por esa vía y que el descriptor construido para distinguirlas tampoco lo hace, lo que convirtió una
figura descriptiva en un resultado negativo con contenido. Y `M1` iba a ser una figura de apoyo en el
anexo; al comprobar las confianzas resultó que la puerta separa exactamente los dos errores y que los
dos caen en autopista, y pasó a ser la primera recomendación del documento.

**Las tres cosas salieron de comprobar las cifras antes de escribir la propuesta, no después.** Es el
único motivo por el que este documento no recomienda hoy lo que iba a recomendar.
