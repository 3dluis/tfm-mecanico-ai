# 7. Ablación de representación (Fase F)

## 7.1 Las tres representaciones

| | Nombre, tal como se publicará | Entrada | Estimador |
|---|---|---|---|
| **A** | **ablación de representación reducida basada en nivel medio de ventana** | la **media** de cada una de las doce señales: 12 valores por ventana | bosque aleatorio, el mismo de B |
| **B** | descriptores completos de ventana | los **139** descriptores | bosque aleatorio |
| **C** | secuencia temporal completa | 120 × 12 muestras crudas | red recurrente bidireccional |

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
| **A frente a B** | solo la representación; el estimador, el conjunto, la partición y el protocolo son los mismos | **Sí.** Es el único eslabón limpio de toda la cadena |
| **B frente a C** | la representación **y** el estimador | **No.** Una diferencia puede venir del sesgo inductivo de la red, de su capacidad o de su regularización |
| **A frente a C** | la representación y el estimador, con más distancia aún | **No**, y por el mismo motivo |

De aquí sale una consecuencia que conviene aceptar antes de medir: **lo que el diseño puede sostener es
cuánto aporta la dinámica dentro de la ventana frente al nivel**, porque eso es `A` frente a `B` con el
mismo estimador. Lo que la secuencia completa añade sobre los descriptores **no** queda aislado, y se
enunciará como diferencia entre dos recorridos.

Esto tiene una lectura positiva que vale la pena decir: `A` frente a `B` ya responde una parte real de
la pregunta del tutor. Si en el termostato el salto grande está entre el nivel y los descriptores, la
información diagnóstica temporal relevante está **dentro de la ventana** y los descriptores la capturan;
si el salto está entre los descriptores y la secuencia, está en la forma de la trayectoria, que los
descriptores resumen. La primera mitad es demostrable con este diseño.

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
