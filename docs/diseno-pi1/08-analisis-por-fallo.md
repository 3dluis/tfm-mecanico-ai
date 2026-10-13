# 8. Protocolo de análisis por tipo de fallo (Fase G)

**La regla que gobierna esta fase:** no se asume que la red recurrente aproveche mejor la temporalidad
en el termostato. Se comprueba. Y hay una posibilidad real de que la comprobación diga que no.

## 8.1 Lo que hoy no se puede comprobar, y por qué

El informe de E7 observa que la red gana en el termostato: 11 de 14 ventanas frente a 9 de 14 en el
conjunto oficial. Pero los registros de E6 y E7 guardan **la matriz de confusión agregada, no las
predicciones por ventana**. De modo que no se puede saber *qué* ventanas acierta cada modelo, y de ahí
se siguen tres cosas que no se pueden decidir:

1. si las dos ventanas de ventaja son de las que contienen señal del fallo;
2. si la mejora en el conjunto grande —45 aciertos frente a 39 de 49— es una recuperación de las
   falladas o una mejora neta con intercambios en las dos direcciones;
3. si las cifras 54,3 °C y 70,7 °C de la matriz de validación son correctas, porque no tienen registro.

## 8.2 El hecho del generador que condiciona todo el análisis del termostato

El fallo es un **techo duro a 71 °C** con ruido de ±0,5: `default_params={"temp_cap_c": 71.0}`. Mientras
el refrigerante no habría superado ese valor por sí mismo, el fallo **no modifica ninguna muestra**, y
la ventana es idéntica a una ventana sana del mismo régimen. La etiqueta, sin embargo, dice F03.

Y esas ventanas no están repartidas al azar: están en el régimen de **calentamiento**, el único que
arranca a la temperatura ambiente. En la validación del conjunto oficial, **5 de las 7 ventanas de
termostato de calentamiento** tienen un máximo de refrigerante por debajo de 70 °C, y **ninguna** de las
7 urbanas. El bosque falla exactamente 5.

**La consecuencia incómoda, dicha antes de medir:** si esas cinco son las cinco que el bosque falla, las
dos ventanas de ventaja de la red estarían entre ventanas **sin señal del fallo**, y acertarlas no sería
leer mejor la evolución temporal. Sería azar, o sobreajuste a las siete ventanas de calentamiento que
el conjunto oficial tiene en entrenamiento.

## 8.3 El protocolo

**Paso 1. Guardar las predicciones por ventana.** Todas las celdas de la rejilla registran, por ventana
de validación: identificador de ventana, sesión, régimen, etiqueta, clase predicha, acierto y confianza.
Es un campo nuevo en el registro, no un experimento nuevo.

**Paso 2. Marcar, por ventana, si el fallo está expresado.** Y aquí hay que corregir un error de la
primera versión de este protocolo, porque proponía dos indicadores que **no identifican lo que dicen
identificar**.

**La columna `fault_active` no sirve.** El generador la calcula como `t >= fault_onset_s`: significa que
la función del fallo **se aplicó**, no que el fallo **modificara** la muestra. Para el fallo de
encendido, cuyos episodios se deciden al azar dentro de la propia función, una ventana entera sin ningún
episodio lleva `fault_active` en cierto en todas sus muestras. Agregar esa columna etiquetaría como
expresadas precisamente las ventanas sin señal, que son las que el análisis quiere separar.

**Y el máximo de refrigerante tampoco sirve como umbral simple.** Que una ventana de termostato alcance
70,5 °C no establece que el techo actuara: el techo solo modifica muestras **por encima de 71 °C**, de
modo que una ventana cuyo refrigerante sube de 69 a 70,8 no sufre ninguna alteración y pasaría por
expresada. En el otro sentido, el ruido del techo —±0,5 °C— puede dejar alguna muestra recortada por
debajo del umbral.

**Lo que sí sirve: que el generador lo registre.** Se añade una columna de metadatos, `fault_expressed`,
que cada función de fallo escribe diciendo si **modificó** la muestra: el techo, si recortó; el
encendido, si había episodio activo; los tres persistentes, siempre que se apliquen. Es un booleano que
la función ya calcula internamente, no consume números aleatorios y no cambia ningún valor de señal, de
modo que no altera el fenómeno. Entra en el protocolo de `synthetic_v4` como el cuarto cambio de
procedencia.

**Consecuencia sobre el orden del trabajo, y es importante.** El análisis decisivo **solo puede hacerse
sobre `synthetic_v4`**, porque `synthetic_v2` y `synthetic_v3` se generaron sin esa columna y no se van a
regenerar. Sobre el conjunto oficial se puede hacer una versión **acotada y declaradamente aproximada**,
y conviene saber hasta dónde llega:

**Sobre `synthetic_v2` no hay indicador de expresión que se sostenga, y conviene decirlo sin rodeos.**
Se intentó acotarlo con bandas del máximo de refrigerante y no funciona en ninguno de los dos extremos:

- Un máximo **por encima** de 71,5 °C sí indica que el techo actuó, pero solo porque se ha comprobado que
  ninguna ventana con etiqueta de fallo contiene muestras anteriores al instante de aparición: el plan
  fija ese instante en **120 s**, el preprocesado etiqueta como sin fallo la ventana que termina ahí y
  descarta la que lo cruza, y de las **350 ventanas etiquetadas con fallo** en entrenamiento y validación
  **ninguna** empieza antes de 120 s. Sin esa comprobación, una sesión urbana arranca con el motor
  caliente y una muestra previa al fallo superaría 71 °C sin que el techo hubiera actuado.
- Un máximo **por debajo** de 70,0 °C **no** indica que el techo no actuara. La función del fallo no fija
  el valor en 71: lo sustituye por `71 + gauss(0, 0.5)`, que puede caer por debajo de 70. Una ventana con
  pocas muestras recortadas —las del propio tránsito— podría quedar entera por debajo del umbral y pasar
  por no expresada siendo expresada. La probabilidad es baja y no es cero, y meter ventanas expresadas en
  el grupo de las no expresadas invalidaría justo la comparación que el análisis busca.
- Para el **fallo de encendido** no hay observable que identifique los episodios sin heurística, y una
  heurística aquí contaminaría el resultado que se quiere medir.

**Conclusión operativa: el análisis por expresión se hace íntegramente sobre `synthetic_v4`**, con la
columna que el generador escribe. Sobre el conjunto oficial solo es posible el estadístico descriptivo
del paso 4, que no necesita indicador de expresión. Y la propiedad de que ninguna ventana con etiqueta de
fallo contenga muestras previas **hay que volver a comprobarla** sobre `v4` en lugar de suponerla.

**Paso 3. Separar las métricas por expresión.** Para cada fallo y cada representación: exhaustividad
sobre las ventanas **con** el fallo expresado y sobre las ventanas **sin** expresar, por separado.

Esto es lo que decide la pregunta:

| Resultado posible | Lectura |
|---|---|
| La ventaja de la secuencia está en ventanas **con** el fallo expresado | hay información en la forma de la trayectoria que los descriptores resumen y pierden. Es un resultado a favor del contexto temporal, acotado a ese fallo |
| La ventaja está en ventanas **sin** expresar | no es información temporal: es azar o ajuste a idiosincrasias de las sesiones. **La hipótesis del termostato cae** |
| No hay ventaja al separar | la ventaja agregada venía del reparto entre los dos grupos y no de detectar mejor |

**Paso 4. Dar registro a las cifras del termostato, sobre el conjunto que describen y con el
estadístico que usaron.** Y aquí hay que empezar por una corrección: esas cifras no son huérfanas en el
sentido de inventadas. Proceden de un análisis que el informe de E6 documenta, con su tabla completa:

| | n | Temperatura media | Rango |
|---|---|---|---|
| Detectadas | 9 | 70,7 °C | 68,6 – 71,1 |
| No detectadas | 5 | 54,3 °C | 42,8 – 64,9 |

y con un desglose que no había tenido en cuenta y que importa mucho: **por régimen, urbano 7 de 7 y
calentamiento 2 de 7**. Es decir que el análisis por ventana **se hizo** en su momento y localizó los
cinco errores en el calentamiento; lo que no se persistió fue el artefacto intermedio. Las cinco
ventanas no detectadas son las cinco de calentamiento que el conjunto tiene por debajo del techo, y eso
corrobora la hipótesis desde un análisis anterior e independiente.

Lo que hay que hacer, por tanto, es una **reejecución de E6 sobre `synthetic_v2`** —su semilla, su
configuración— registrando esta vez las predicciones por ventana, y recalcular **el mismo estadístico**:
la media de `coolant_temperature_mean` de cada grupo, con su rango, y el desglose por régimen. **No el
máximo**: usar otro estadístico daría otro número y podría llevar a retirar como no reproducible una
cifra que sí lo es.

Se compara contra las cuatro cifras publicadas y los dos rangos. No es un experimento nuevo: es volver a
ejecutar lo ya publicado, y trae una comprobación de regalo —si las métricas agregadas no reproducen el
registro de E6, hay que pararse ahí—.

Este paso no necesita `synthetic_v4` y puede hacerse en la Fase A. Si la reejecución no reproduce E6, o
si el estadístico sale distinto, las cifras **se retiran** de la matriz de validación en lugar de
corregirse en silencio, y se dice por qué.

**Paso 5. Repetir lo mismo con el fallo de encendido**, que es la condición más débil en los dos
modelos y sobre prueba —F1 0,4444 en E19— y cuya intermitencia produce el mismo tipo de ventanas sin
señal. Este paso **solo existe sobre `synthetic_v4`**, por lo dicho en el paso 2.

## 8.4 Qué no hace este protocolo

No explica **por qué** una representación aprovecha algo mejor; separa dónde ocurre la diferencia. La
atribución podría decir algo sobre el bosque, pero para la red recurrente no hay atribución implementada
y construirla sería otra fase.

Tampoco resuelve el confusor de `05-protocolo-comparacion.md`. Si la ventaja aparece en ventanas con el
fallo expresado, sigue siendo una diferencia entre dos recorridos; lo que se habrá descartado es la
explicación alternativa más probable, que es que la ventaja viniera de acertar ventanas indetectables.
Descartar eso ya es bastante.

## 8.5 Criterio de parada

Se para si la columna `fault_expressed` no reproduce el fenómeno —se comprueba regenerando una sesión y
verificando que los valores de señal son idénticos a los de la misma semilla sin la columna—, si las
predicciones por ventana no se pueden registrar sin tocar código congelado, o si la banda ambigua del
análisis acotado sobre `synthetic_v2` se come tantas ventanas que no queda nada que comparar, cosa que
hay que contar **antes** de interpretar.

Nada de esto afecta a E19, que está cerrada sobre `synthetic_v2` y cuyo código no se toca.
