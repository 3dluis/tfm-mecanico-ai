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

**Paso 2. Marcar, por ventana, si el fallo está expresado.** Un indicador derivado del generador, no del
modelo:

| Fallo | Indicador de expresión | Umbral |
|---|---|---|
| F03 termostato | el techo actuó en la ventana | máximo de refrigerante ≥ 70,5 °C, es decir el techo menos el ruido declarado |
| F05 encendido | hubo al menos un episodio en la ventana | la columna `fault_active` de los datos crudos, agregada a la ventana |
| F01, F02, F04 | persistentes por definición del catálogo | expresado en toda ventana posterior al instante de aparición |

El indicador del encendido es mejor que el del termostato porque el generador ya marca `fault_active`
por muestra. Para el termostato hay que derivarlo del umbral, y la elección de 70,5 °C se declara aquí,
antes de usarla.

**Paso 3. Separar las métricas por expresión.** Para cada fallo y cada representación: exhaustividad
sobre las ventanas **con** el fallo expresado y sobre las ventanas **sin** expresar, por separado.

Esto es lo que decide la pregunta:

| Resultado posible | Lectura |
|---|---|
| La ventaja de la secuencia está en ventanas **con** el fallo expresado | hay información en la forma de la trayectoria que los descriptores resumen y pierden. Es un resultado a favor del contexto temporal, acotado a ese fallo |
| La ventaja está en ventanas **sin** expresar | no es información temporal: es azar o ajuste a idiosincrasias de las sesiones. **La hipótesis del termostato cae** |
| No hay ventaja al separar | la ventaja agregada venía del reparto entre los dos grupos y no de detectar mejor |

**Paso 4. Dar registro a las dos cifras huérfanas.** Con las predicciones por ventana y el máximo de
refrigerante, las cifras «las ventanas que el modelo falla tienen 54,3 °C de media; las que acierta,
70,7» se regeneran como artefacto o se corrigen. Cierra una de las cinco cifras sin registro de
`EVID-MAJ-019`.

**Paso 5. Repetir lo mismo con el fallo de encendido**, que es la condición más débil en los dos
modelos y sobre prueba —F1 0,4444 en E19— y cuya intermitencia produce el mismo tipo de ventanas sin
señal.

## 8.4 Qué no hace este protocolo

No explica **por qué** una representación aprovecha algo mejor; separa dónde ocurre la diferencia. La
atribución podría decir algo sobre el bosque, pero para la red recurrente no hay atribución implementada
y construirla sería otra fase.

Tampoco resuelve el confusor de `05-protocolo-comparacion.md`. Si la ventaja aparece en ventanas con el
fallo expresado, sigue siendo una diferencia entre dos recorridos; lo que se habrá descartado es la
explicación alternativa más probable, que es que la ventaja viniera de acertar ventanas indetectables.
Descartar eso ya es bastante.

## 8.5 Criterio de parada

Se para si el indicador de expresión no se puede derivar para algún fallo, o si las predicciones por
ventana no se pueden registrar sin tocar código congelado. Nada de esto afecta a E19, que está cerrada
sobre `synthetic_v2` y cuyo código no se toca.
