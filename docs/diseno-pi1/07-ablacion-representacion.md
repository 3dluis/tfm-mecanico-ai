# 7. Ablación de representación (Fase F)

## 7.1 Las tres representaciones

| | Nombre, tal como se publicará | Entrada | Estimador |
|---|---|---|---|
| **A** | **ablación de representación reducida basada en nivel medio de ventana** | la **media** de cada una de las doce señales: 12 valores por ventana | bosque aleatorio, el mismo de B |
| **B** | descriptores completos de ventana | los **139** descriptores | bosque aleatorio |
| **C** | secuencia temporal completa | 120 × 12 muestras crudas | red recurrente bidireccional |

**Y una escalera intermedia, porque sin ella `A` frente a `B` no dice lo que parece.** Entre los doce
descriptores de `A` y los 139 de `B` hay 127 más, y **no todos son dinámica**: hay extremos, dispersión,
una razón entre señales y seis correlaciones cruzadas. Atribuir a la dinámica intraventana la diferencia
entre `A` y `B` sería atribuirle también lo que aportan los otros. La escalera, con los recuentos
verificados sobre el conjunto:

| Escalón | Qué añade respecto del anterior | Descriptores | Acumulado |
|---|---|---|---|
| `A1` | la **media** de cada señal | 12 | **12** |
| `A2` | dispersión y extremos: `std`, `min`, `max`, `range` | 48 | **60** |
| `A3` | **dinámica intraventana**: `slope`, `autocorr1`, `delta_min`, `delta_max`, `crossings`, `n_events` | 72 | **132** |
| `A4` | la razón entre señales `maf_over_rpm_load` | 1 | **133** |
| `B` | las seis correlaciones entre señales | 6 | **139** |

El escalón que responde a la pregunta es **`A2` → `A3`**, con el estimador fijo: ahí y solo ahí se añade
dinámica intraventana y nada más. `A1` → `A2` mide qué aporta mirar la dispersión y los extremos, que es
otra pregunta y también interesante, porque E4 midió que dos de los cinco fallos se separan por
dispersión y no por nivel.

Cinco escalones del bosque cuestan segundos cada uno. No es coste; es precisión.

**A no es una observación puntual, y no se llamará así.** Es un resumen de ventana, solo que de un
único estadístico. Un clasificador por muestra sería otra cosa: exigiría decidir cómo agregar las
ciento veinte decisiones de una ventana en una, lo que añade un mecanismo nuevo para responder a la
misma pregunta. **No se propone.** Si el tutor quiere la comparación puntual en sentido estricto, hay
que decir que no existe y que construirla es una ablación nueva con su propio protocolo.

## 7.2 Por qué la media y no media, mínimo y máximo

Porque el mínimo y el máximo de una ventana **no son nivel**: son extremos, y conservan información
sobre cambios y sobre episodios breves. De hecho el bosque los usa así: `oxygen_sensor_max` y
`rpm_min` están entre sus cinco descriptores más importantes. Un subconjunto con extremos no aislaría
«nivel» de «dinámica dentro de la ventana».

La media de cada señal es el único subconjunto que se aproxima a nivel puro. Doce descriptores de los
139.

## 7.3 Qué comparación aísla qué — la tabla que hay que mirar antes de interpretar

| Comparación | Qué cambia | ¿Aísla la representación? |
|---|---|---|
| **`A2` frente a `A3`** | solo los 72 descriptores de dinámica intraventana; mismo estimador | **Sí, y es la única que aísla la dinámica.** El eslabón limpio de toda la cadena |
| `A1` frente a `A2` | solo dispersión y extremos | sí, aísla **eso**, que no es dinámica |
| `A3` frente a `B` | la razón y las correlaciones cruzadas | sí, aísla **eso** |
| `A` frente a `B` sin escalones | los 127 descriptores a la vez: dinámica, dispersión, extremos y relaciones | **No para la dinámica.** Aísla el conjunto añadido completo, que es otra afirmación |
| **B frente a C** | la representación **y** el estimador | **No.** Una diferencia puede venir del sesgo inductivo de la red, de su capacidad o de su regularización |
| **A frente a C** | la representación y el estimador, con más distancia aún | **No**, y por el mismo motivo |

De aquí sale una consecuencia que conviene aceptar antes de medir: **lo que el diseño puede sostener es
cuánto aporta la dinámica dentro de la ventana frente al nivel y la dispersión**, porque eso es `A2`
frente a `A3` con el mismo estimador. Lo que la secuencia completa añade sobre los descriptores **no**
queda aislado, y se enunciará como diferencia entre dos recorridos.

Esto tiene una lectura positiva que vale la pena decir: la escalera ya responde una parte real de la
pregunta del tutor. Si en el termostato el salto grande está en `A2` → `A3`, la información diagnóstica
temporal relevante está **dentro de la ventana** y los descriptores la capturan; si está entre los
descriptores y la secuencia, está en la forma de la trayectoria, que los descriptores resumen. La
primera mitad es demostrable con este diseño; la segunda, no.

## 7.4 Qué se registra

Por cada celda —representación × punto de volumen × réplica—: el registro con su cabecera completa, las
métricas agregadas y por clase, la calibración, y **las predicciones por ventana**, que es lo que hoy no
existe y lo que hace falta para el análisis por fallo de `08-analisis-por-fallo.md`.

## 7.5 Qué se espera, dicho como predicción refutable y no como resultado deseado

Con el nivel medio solo, los dos fallos definidos por dispersión o por intermitencia —sonda lenta y
fallo de encendido— deberían caer mucho, porque E4 midió que su separación univariante no está en el
nivel: la sonda separa por dispersión con delta 1,00 y su nivel no aparece. Si **no** cayeran, habría
que buscar por dónde entra la información, y sería un hallazgo.

El termostato, cuya mejor señal es de **nivel** con delta 0,75, debería sobrevivir mejor a la reducción.
Si tampoco cayera la fuga de vacío ni la deriva del caudalímetro, que separan por nivel de los ajustes
de combustible con delta 1,00, el diseño quedaría confirmado en su parte esperada y la atención se
concentraría en los dos fallos difíciles.

Se escribe ahora para que no se pueda ajustar después.
