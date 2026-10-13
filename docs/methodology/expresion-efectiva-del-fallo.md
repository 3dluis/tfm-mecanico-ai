# Expresión efectiva del fallo: definición operacional de `fault_expressed`

**Fecha:** 12 de octubre de 2026 · **Implementación:** `src/mecanico_ia_exp/obd/expresion.py` y
`obd/synthetic.py` · **Pruebas:** `tests/test_expresion_fallo.py` · **Estado:** definición cerrada y
medida; se aplica a `synthetic_v4`, que **todavía no se ha generado**.

## 1. El problema que esta columna resuelve

`fault_active` responde a una pregunta del generador: ¿se llamó a la función de fallo en este
instante? No responde a la del experimento, que es si el fallo **produjo una alteración observable**.

No son lo mismo, y la diferencia no es un matiz:

- el **termostato bloqueado** solo recorta la temperatura cuando el refrigerante ya superó su tope,
  de modo que durante el calentamiento la función se aplica y **no cambia ni un valor**;
- el **fallo de encendido** es episódico: fuera de un episodio la función se aplica y devuelve la
  muestra intacta.

Tratar `fault_active` como «el fallo se manifestó» convierte esas muestras en evidencia de algo que
no ocurrió. Y eso ya tuvo consecuencias: la nota de `docs/matriz_validacion_pi.md` sobre el límite
físico del termostato se apoyaba en estadísticos agregados de temperatura por ventana porque no
había forma de saber, ventana a ventana, si el fallo estaba expresado.

## 2. La definición

**Una muestra expresa el fallo cuando su trayectoria difiere de su propio contrafactual en al menos
un umbral de observabilidad de alguna señal.**

Tres piezas, cada una con su por qué.

### 2.1 El contrafactual, y por qué es exacto y no una estimación

El contrafactual de una muestra es **el valor que el motor habría dado en ese mismo instante, con el
mismo estado y la misma semilla, si la función de fallo no se hubiera aplicado**.

No hay que simularlo aparte. `SignalEngine.tick()` devuelve una **copia** del diccionario de valores
y mantiene su estado interno al margen de lo que el fallo haga con esa copia: el estado térmico, la
velocidad, la fase del régimen y el integrador del ajuste a largo plazo avanzan igual con fallo y
sin él. El contrafactual es, literalmente, el valor que la función de fallo recibe antes de mutarlo.

Las funciones de fallo usan además **su propio generador aleatorio** —`FaultRuntime(rng=Random(seed
+ 1))`— distinto del del motor, así que aplicar el fallo no desplaza la secuencia del motor. Por eso
la comparación es exacta y no aproximada.

### 2.2 Después del recorte a rango físico

La comparación se hace **tras recortar las dos trayectorias a su rango físico**, porque ese es el
valor que llega al modelo. Si un fallo empuja una señal fuera de lo posible y el recorte la devuelve
al mismo valor, no hay alteración observable y no debe contarse como tal. Un sensor real satura
igual.

### 2.3 El umbral, y de dónde sale

Una diferencia de 1e-16 es una diferencia aritmética, no una alteración. El umbral se fija **contra
el ruido propio del generador**: cada señal recibe en `obd/engine.py` una perturbación gaussiana con
una desviación típica declarada, y una alteración por debajo de una fracción de ese ruido es
indistinguible del propio proceso de generación.

El umbral de cada señal es el producto de `RATIO_DECLARADO` por esa desviación. Donde el motor usa
dos —el régimen, con 12,0 en ralentí y 35,0 en marcha— se toma **la menor**, que es la elección
conservadora porque hace el umbral más exigente.

| Señal | Desviación del generador | Umbral con razón 0,10 |
|---|---|---|
| `rpm` | 12,0 rpm | 1,2 rpm |
| `vehicle_speed` | 0,3 km/h | 0,03 km/h |
| `engine_load` | 2,0 % | 0,2 % |
| `throttle_position` | 1,5 % | 0,15 % |
| `coolant_temperature` | 0,15 °C | 0,015 °C |
| `intake_air_temperature` | 0,4 °C | 0,04 °C |
| `maf` | 0,35 g/s | 0,035 g/s |
| `map` | 1,2 kPa | 0,12 kPa |
| `stft_bank1` | 1,6 % | 0,16 % |
| `ltft_bank1` | 0,01 % | 0,001 % |
| `oxygen_sensor` | 0,03 V | 0,003 V |
| `ignition_timing` | 0,8° | 0,08° |

**`RATIO_DECLARADO = 0,10` es un parámetro de este protocolo, no una magnitud documentada del
vehículo**, y se declara como tal. Se elige deliberadamente permisivo —una décima parte del ruido—
para no ocultar alteraciones reales. Un test comprueba que cada desviación declarada sigue
apareciendo en `engine.py`, de modo que si el motor cambia su ruido, la declaración deja de cuadrar
y se entera.

### 2.4 Y la decisión no queda horneada en el dato

Junto a `fault_expressed` se guarda `fault_deviation_max`: **la magnitud de la mayor alteración, en
unidades de su propio umbral**. Una lectura más estricta con razón `r` se obtiene comparando esa
columna contra `r / 0,10`, sin regenerar nada. Hay un test que lo comprueba.

`fault_deviation_signal` dice **qué señal** lleva la alteración, lo que permite comprobar que está
donde la ficha del fallo dice que debería estar en lugar de confiar en que lo esté. Un test verifica,
para las cinco condiciones, que toda señal alterada figura en el `affected_signals` de su ficha.

## 3. Para las dos condiciones que importan, el umbral es irrelevante

Esta es la propiedad que hace defendible la definición: por debajo del tope del termostato y fuera
del episodio de encendido, la desviación es **exactamente cero**, no pequeña. La clasificación de
esas muestras **no depende de ningún parámetro**, y eso está comprobado en dos tests.

## 4. Lo que se mide, con la definición puesta

Tres sesiones por combinación, de 600 s, entrada del fallo en 120 s; ventanas de 120 s con paso de
60 s. Medido el 12 de octubre de 2026 con el generador vigente. **No es `synthetic_v4`**: es el
instrumento aplicado a sesiones generadas para esta medición.

| Fallo | Régimen | Muestras expresadas | Ventanas etiquetadas **sin ninguna señal** | Ventanas expresadas por completo |
|---|---|---|---|---|
| F01 fuga de vacío | los cuatro | 1440/1440 (100 %) | 0 de 45 | 100 % |
| F02 deriva de caudalímetro | los cuatro | 1436/1440 (100 %) | 0 de 45 | 96 % |
| F03 termostato | urbano, autopista, ralentí | 1440/1440 (100 %) | 0 de 45 | 100 % |
| **F03 termostato** | **calentamiento** | **340/1440 (24 %)** | **32 de 45** | **16 %** |
| F04 sonda lenta | los cuatro | ≈1439/1440 (100 %) | 0 de 45 | 91–100 % |
| **F05 fallo de encendido** | **los cuatro** | **62/1440 (4 %)** | **12 de 45** | **0 %** |

Cuatro lecturas, y ninguna es una conclusión sobre el modelo:

1. **El termostato solo es un problema en calentamiento.** En los otros tres regímenes el motor
   arranca a 78 °C, por encima del tope de 71, así que el fallo recorta desde la primera muestra. En
   calentamiento arranca a temperatura ambiente y tarda minutos en llegar al tope: ahí **32 de las
   45 ventanas etiquetadas con el fallo no contienen ninguna señal observable de él**. La
   explicación que E6 dio en su día era correcta; ahora está medida ventana a ventana en lugar de
   inferida de un estadístico agregado.

2. **El fallo de encendido no expresa ninguna ventana por completo.** Con episodios de 1 a 3 s y una
   tasa de aparición del 2 % por segundo, una ventana de 120 s contiene a lo sumo unos pocos
   segundos alterados. Ninguna de las 45 llega al 100 %, y 12 no tienen ni una muestra. Una
   exhaustividad baja en esta clase **puede venir de aquí** y no del volumen de datos, que es
   exactamente la atribución que `SUPERSEDED-E7-03` retira.

3. **Las otras tres condiciones se expresan desde el primer instante**, porque añaden ruido a los
   ajustes de combustible de forma incondicional. Eso tiene una consecuencia honesta: para ellas
   `fault_expressed` es verdadero casi siempre y **no aporta información**. La columna es
   informativa para F03 en calentamiento y para F05; para el resto, confirma que no hay nada que
   separar.

4. **F02 al principio altera poco más que ruido.** Su deriva crece con una rampa de 300 s, de modo
   que en la primera muestra `drift × min(1, 0/300) = 0`: el caudal no cambia y lo único que se
   altera es el ruido del ajuste a corto plazo. Está expresado —la trayectoria difiere— pero su
   **firma diagnóstica** aún no está. `fault_deviation_max` permite distinguir los dos casos sin
   cambiar la definición.

## 5. Lo que esta definición NO resuelve

**Expresión no es firma diagnóstica.** Lo que se mide es si la trayectoria se alteró, que es
exactamente lo que el protocolo pidió. Que la alteración sea **suficiente para diagnosticar** es
otra pregunta, y la respuesta depende del modelo; por eso la columna no se usa como criterio de
exclusión.

**Ninguna ventana se descarta por no expresar el fallo.** Se marcan y se conservan: `n_expressed`,
`fraction_expressed`, `fault_expressed` y `deviation_max` entran en los metadatos de cada ventana. El
tratamiento que reciban en el análisis lo fija el protocolo pre-registrado de la fase, no el
ventanado, y eliminarlas aquí las habría escondido.

**Los conjuntos anteriores no tienen estas columnas.** `synthetic_v1`, `v2` y `v3` se conservan tal
como están, sin regenerar. El código que lee las columnas tolera su ausencia, y hay un test que lo
comprueba; la auditoría del generador marca la comprobación como `NO_VERIFICABLE` —que cuenta como
fallo— en lugar de saltarla.

**Añadir las columnas no alteró el generador.** Comprobado de dos maneras: `synthetic_sample` se
regenera **idéntico bit a bit** en las doce señales, y generar la misma semilla con la razón del
umbral variada en cuatro órdenes de magnitud da las mismas series y distinto número de muestras
expresadas.
