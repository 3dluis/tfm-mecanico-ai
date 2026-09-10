# 15 · Contenido retirado del capítulo 4 y pendiente de insertar en el capítulo 5

El capítulo 5 está congelado. Este documento **custodia literalmente** el contenido que salió
del capítulo 4 por ser resultado experimental, para que se inserte cuando se levante la
congelación. Ningún valor se ha modificado.

> **Aviso.** Mientras la congelación siga vigente, estos cuatro valores **no aparecen en el
> cuerpo de la memoria**. Siguen registrados en `docs/experiments/E5_preprocesamiento.md`.

## Tabla propuesta · selección de la ventana temporal

**Ubicación prevista:** capítulo 5, junto a los resultados de diagnóstico.

**Título propuesto:** *Tabla 5.X. Umbral de ruido del máximo delta de Cliff entre 139
descriptores, según la longitud de la ventana temporal.*

| Ventana | Umbral de ruido (percentil 90 del máximo delta de Cliff entre 139 descriptores) |
|---|---|
| 10 s | 0,369 |
| 30 s | 0,399 |
| 60 s | 0,438 |
| 120 s | 0,512 |

*Fuente: elaboración propia a partir del registro de la fase E5.*

### Por qué no se adopta «nivel de referencia de variabilidad»

El estadístico **sí está formalmente definido**, en `E5_preprocesamiento.md`, hallazgo 1, y
existe como función reutilizable `noise_floor_max_delta`. Su definición: se toma únicamente la
condición sin fallo, se parte en dos mitades por sesión, se calcula el **delta de Cliff** de cada
uno de los 139 descriptores entre ambas mitades, se retiene el máximo, se repite treinta veces y
se toma el percentil 90.

De ahí se siguen dos cosas. La primera es que **no mide variabilidad**: es el umbral de una
distribución nula construida por partición, es decir, cuánto llega a valer el mayor tamaño de
efecto cuando por construcción no hay ningún efecto. Llamarlo «nivel de referencia de
variabilidad» describiría mal lo que contiene. La segunda es que **la magnitud es el delta de
Cliff**, adimensional y acotado, de modo que la columna no lleva unidad y el eje Y de cualquier
figura derivada tampoco debe llevarla.

`METRIC_DEFINITION_REQUIRED` **no se activa**: la definición existe y es anterior al uso.

### Interpretación retirada del capítulo 4, para insertar con la tabla

> Con ventanas cortas, el mejor descriptor de un fallo de encendido resultaba ser una variante
> de la temperatura del refrigerante, señal que ese fallo no toca, y su tamaño de efecto quedaba
> por debajo del suelo de ruido. Es el fenómeno que el trabajo estudia, en miniatura: evidencia
> aparente que no sobrevive al escrutinio. Con 60 y 120 segundos el mejor descriptor de ese
> fallo pasa a ser la sonda de oxígeno, que sí está en su mecanismo declarado, y con 120
> segundos los mecanismos físicos declarados y los descriptores separables coinciden en todas
> las condiciones detectables.

Cuatro elementos que son hallazgo y no diseño: la temperatura del refrigerante como descriptor
aparente, la sonda de oxígeno como descriptor real, la diferencia entre las cuatro longitudes y
la coincidencia entre mecanismos declarados y descriptores separables.

### Qué se conserva en el capítulo 4

Las cuatro longitudes evaluadas, el estadístico empleado, el procedimiento de contraste contra
la referencia nula, el criterio doble de selección —superar el umbral y coincidir con el
mecanismo declarado— y la configuración adoptada de 120 segundos con solape.

## Renumeración aplicada

Al salir la antigua Tabla 4.3, las diez siguientes se renumeraron a 4.3-4.12 y sus referencias
cruzadas se actualizaron. El capítulo queda con trece tablas sin saltos ni duplicados.

---

# `UNREPRESENTED_PATTERN_VALIDATION = BLOCKED`

Comprobación del aislamiento entre las fuentes de conocimiento, pedida antes de aceptar que
generar sintéticamente un fallo demuestre que el patrón era «no representado en el conocimiento
disponible». Verificada contra el código y los registros el 10 de septiembre de 2026.

| Fuente de conocimiento | Contenido | Aislamiento respecto del generador |
|---|---|---|
| **Generador sintético** | seis clases: `F00_normal`, `F01_vacuum_leak`, `F02_maf_drift`, `F03_thermostat_stuck`, `F04_o2_lag`, `F05_misfire` | — |
| **Detector** | las **mismas seis clases**, etiquetadas | **NINGUNO** |
| **Corpus RAG** | manual del vehículo; la recuperación se guía por `DIAGNOSTICO_A_DTC`, que asocia cada clase del generador a sus códigos de avería | **NINGUNO** |
| **Ajuste del redactor** | 62 ejemplos sobre 44 casos, `dataset_id: synthetic_v2`, separación por `case_id` | parcial: separa casos, no clases |
| **Conocimiento paramétrico del LLM** | no medido | no comprobado |
| **Casos held-out** | partición de test cerrada hasta E19, con **las mismas seis clases** | **ninguna clase excluida** |

Búsqueda de `holdout`, `held_out`, `excluded_class`, `leave_one_class` y `clase_excluida` en
`src/`: **cero coincidencias**.

## Consecuencia

El detector se entrena sobre exactamente las mismas clases que el generador produce, y la
recuperación se guía por un diccionario que asocia esas mismas clases a sus códigos de avería.
Un fallo generado sintéticamente está, **por construcción**, representado en el conocimiento del
detector y en el del corpus. La partición de test cierra casos, no clases: no hay ninguna clase
retenida.

Por tanto, el diseño actual **no puede demostrar** que un patrón sea no representado en el
conocimiento disponible, y ningún resultado de esta memoria debe leerse como si lo hiciera. El
aislamiento necesario no existe y no puede construirse renombrando ni reinterpretando lo
ejecutado.

Se registra como bloqueo. **No se modifica la pregunta de investigación ni se reinterpreta
ningún resultado.** Concuerda con `L-21` y con la sección 02 de esta revisión.

Cerrar el bloqueo exigiría, como mínimo: una definición operacional de «no representado»; una
condición experimental que retenga al menos una clase fuera del entrenamiento del detector y
fuera del diccionario de recuperación; y una medida de si el conocimiento paramétrico del modelo
de lenguaje cubre esa clase. Nada de eso figura en las veinte fases del plan.

## Estado de cierre de la primera entrega

| Control | Estado |
|---|---|
| `POPULATION_DEFINITION` | PASS |
| `REFERENCE_VEHICLE_DEFINITION` | PASS — declarado como configuración mecánica de referencia, con la telemetría explícitamente no procedente de un vehículo físico |
| `SYNTHETIC_SAMPLE_DESCRIPTION` | PASS |
| `DATA_PROVENANCE` | PASS |
| `METHOD_RESULTS_SEPARATION` | PASS en el capítulo 4; la inserción en el 5 queda pendiente de la congelación |
| `TABLE_FORMAT` | PASS — trece tablas, sin saltos ni duplicados, todas mencionadas |
| `EXTERNAL_VALIDITY_SCOPE` | PASS |
| `PI_ALIGNMENT` | **BLOCKED** — `UNREPRESENTED_PATTERN_VALIDATION` |

`SYNTHETIC_DATA_STATUS = EXPERIMENTAL_BASE` · `REAL_OBD_DATA_STATUS = EXTERNAL_VALIDATION_PENDING`
