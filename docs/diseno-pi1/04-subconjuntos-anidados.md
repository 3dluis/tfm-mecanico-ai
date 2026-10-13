# 4. Control del volumen con subconjuntos anidados (Fase C)

**Lo que este diseño arregla.** La única evidencia de que el volumen limitaba la comparación venía de
comparar `synthetic_v2` con `synthetic_v3`, y entre esos dos conjuntos cambian **cuatro** cosas: el
número de sesiones, la calibración del generador, las realizaciones concretas y la partición de
validación. Repetir la semilla no lo arregla: con otro número de sesiones por condición el constructor
del plan consume números aleatorios distintos y el reparto por sesión vuelve a barajar.

La forma de aislar el volumen es no cambiar nada más que el volumen.

## 4.1 El diseño

Un único conjunto, `synthetic_v4`, con su reparto hecho una sola vez: **22 sesiones de entrenamiento, 7
de validación y 7 de prueba por condición**. Sobre ese reparto, cuatro subconjuntos **de entrenamiento**:

```
T6  ⊂  T12  ⊂  T18  ⊂  T22        sesiones por condición
```

**Fijo en los cuatro puntos:** el conjunto de validación, el de prueba, el generador, las seis
condiciones, el ventanado y el preprocesado, las doce señales, los 139 descriptores y el protocolo de
evaluación. **Variable:** solo cuántas sesiones de entrenamiento entran.

## 4.2 Cómo se construye el anidamiento, y por qué así

Para cada condición, las 22 sesiones de entrenamiento se ordenan por su identificador —orden total y
estable— y se permutan con una **semilla declarada de antemano**, `20260901`. Los subconjuntos se toman
como prefijos de esa permutación: los 6 primeros, los 12 primeros, los 18 primeros, los 22.

Con prefijos de una única permutación, el anidamiento es **estructural**: `T6 ⊂ T12` no es algo que haya
que comprobar después, es una propiedad de cómo se construye. Y como la permutación se fija antes de
mirar cualquier resultado, no hay forma de elegir qué sesiones entran en el subconjunto pequeño para
que la curva salga como conviene.

El número de ventanas de cada punto no se escribe aquí porque depende del conjunto generado, y
escribirlo ahora sería inventarlo. Se registrará con el conjunto. Lo que sí se fija es la regla.

## 4.3 Las tres fugas posibles, y qué las cierra

**Fuga por ventana.** Dos ventanas consecutivas de la misma sesión comparten la mitad de sus muestras.
Si los subconjuntos se construyeran por ventana, una ventana de entrenamiento de `T6` podría solaparse
con una ventana de validación. **Lo cierra:** los subconjuntos se construyen **por sesión**, nunca por
ventana, y la partición ya es por sesión. La auditoría de fuga existente —`audit_masks`— se ejecuta
sobre las máscaras reales de cada punto y no solo sobre el reparto.

**Fuga por normalización.** El modelo temporal normaliza con estadísticos por señal. Si esos
estadísticos se calculasen sobre las 22 sesiones y luego se entrenara con 6, el punto `T6` estaría
usando información de las 16 sesiones que no le corresponden, y la curva saldría más plana de lo que
es. **Lo cierra:** los estadísticos se recalculan **desde cada subconjunto**, con sus sesiones y solo
las suyas. Hay que comprobarlo con una prueba, como ya se hizo en E7 para la fuga entrenamiento →
validación.

**Fuga por calibración.** La calibración isotónica del bosque se ajusta con validación cruzada interna
sobre entrenamiento. Debe ajustarse sobre **el subconjunto**, no sobre el entrenamiento completo, por el
mismo motivo. **Lo cierra:** una comprobación de que el objeto calibrado se ajustó con el número de
ventanas del punto.

## 4.4 Qué mide esta curva, y qué no

Mide cómo cambia el rendimiento de cada recorrido —y la diferencia entre los dos— al aumentar las
sesiones de entrenamiento, con todo lo demás fijo. **No mide** si el contexto temporal aporta: eso sigue
confundido por el estimador, como explica `05-protocolo-comparacion.md`.

Y hay un límite que conviene escribir antes de ver la curva: **con 22 sesiones por condición el punto
más alto está en 132 sesiones de entrenamiento**, menos que las 216 de `synthetic_v3` pero más del
doble de las 48 de `synthetic_v2`. Si la curva sigue subiendo en `T22`, la conclusión honesta es «el
volumen seguía limitando en el rango explorado», no «hace falta más volumen»: lo segundo exige
extrapolar, y la pendiente de cuatro puntos con cinco semillas dirá si eso es defendible.

## 4.5 Criterio de parada de esta fase

Se para y se informa si: el reparto no da 22/7/7 por condición; la auditoría de fuga falla en algún
punto; los estadísticos de normalización de un punto no proceden de su subconjunto; o el anidamiento no
se cumple, que solo puede ocurrir por un error de implementación.

**No** se para por el valor de la curva. Una curva plana es un resultado y una curva creciente es otro.
