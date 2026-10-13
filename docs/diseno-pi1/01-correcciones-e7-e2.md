# 1. Correcciones documentales de E7 y E2 (Fase A)

**Regla que gobierna estas correcciones:** no se borra la afirmación anterior cuando forma parte de la
evolución científica del trabajo. Se marca con `SUPERSEDED`, `NON-CANONICAL` o `CORRECTED`, se fecha, y
se dice qué evidencia la sustituye. Los registros experimentales originales **no se tocan**.

## 1.1 Informe de E7 — tres correcciones

### CORRECTED-E7-01 · Las cifras de `synthetic_v2` no son las de su registro

`docs/experiments/E7_modelo_temporal.md` publica para el conjunto oficial cifras anteriores a la
regeneración del 1 de septiembre, cuando el generador se calibró contra el manual (`770ce70`). El
registro vigente es posterior y el capítulo 5 ya cita el registro, no el informe.

| Cifra | En el informe | En el registro `E7_temporal_synthetic_v2.json` |
|---|---|---|
| F1 macro del bosque | 0,876 | **0,8788** |
| F1 macro de la GRU | 0,822 | **0,8230** |
| Exactitud de la GRU | 0,806 | **0,8265** |
| Normal, bosque / GRU | 0,836 / 0,702 | **0,8235 / 0,7692** |
| Fuga, bosque / GRU | 1,000 / 0,929 | **1,0000 / 0,9655** |
| Caudalímetro, bosque / GRU | 1,000 / 0,929 | **1,0000 / 0,9231** |
| Termostato, bosque / GRU | 0,783 / 0,857 | **0,7826 / 0,8148** |
| Sonda, bosque / GRU | 1,000 / 1,000 | **1,0000 / 0,9655** |
| Encendido, bosque / GRU | 0,636 / 0,518 | **0,6667 / 0,5000** |
| Épocas / mejor época | 60 / 19 | **74 / 33** |
| Segundos de entrenamiento | 44,5 | **50,81** |

La columna de `synthetic_v3` del informe **sí** coincide con su registro, porque ese conjunto se generó
después de la calibración y nunca se regeneró. **Acción:** sustituir las cifras de `v2` por las del
registro, marcar la tabla anterior como `CORRECTED 2026-10-xx` con una nota de dos líneas que explique
la causa —regeneración por calibración del generador— y no borrar la explicación.

### SUPERSEDED-E7-02 · El hallazgo «el límite era el volumen de datos, no la arquitectura»

El informe concluye que la desventaja de la red recurrente se explica por el volumen, comparando
`synthetic_v2` con `synthetic_v3`. Esa comparación **cambia dos cosas a la vez**:

| | `synthetic_v2` | `synthetic_v3` |
|---|---|---|
| Generado | **14 de septiembre**, 00:37 | **1 de septiembre**, 18:58 |
| Ralentí sin fallo, mediana | **690 rpm** | **820 rpm** |
| Respaldo documental del ralentí | rango 640-740 del manual para el Z6 | ninguno; es el valor que la calibración retiró |
| Avance de encendido, primera muestra | 10,15° | 15,05° |
| Sesiones | 72 | 216 |

`GENERATOR_VERSION` siguió valiendo `1.0.0` en los dos casos y no los distingue. **Acción:** marcar el
hallazgo como `SUPERSEDED 2026-10-xx`, conservar el texto, y añadir la nota: la comparación confunde
volumen con calibración del fenómeno, de modo que no establece que el volumen fuera la limitación; la
pregunta queda abierta y su diseño está en `04-subconjuntos-anidados.md`.

### SUPERSEDED-E7-03 · La corrección sobre el fallo de encendido

El informe corrige a E5 y E6 —«la condición sí es clasificable; lo que faltaba eran datos»— apoyándose
en el mismo conjunto sin calibrar. **Acción:** misma marca y misma nota. Lo que sí se conserva sin
reservas es el valor del control de suelo de ruido de E5, que no depende de esa comparación.

## 1.2 Fila E2 del índice — una corrección

### CORRECTED-E2-01 · Procedencia de `synthetic_v3`

La fila describe los tres conjuntos bajo un «generador paramétrico calibrado contra el manual», y `v3`
es **anterior** a esa calibración. **Acción:** separar los tres conjuntos con su fecha de generación y
etiquetar `v3` como **pre-calibración**, conservándolo sin renombrar y sin modificar, igual que se
conservaron las ejecuciones no canónicas de E12 y E13.

## 1.3 Las demás inconsistencias identificadas

| Id | Dónde | Qué | Acción propuesta |
|---|---|---|---|
| `TRAZ-PI1-01` | `research/traceability-matrix.md:29` y `docs/matriz_validacion_pi.md:37` | Dos enunciados distintos del criterio de PI.1: la matriz de trazabilidad conserva el original —«un modelo temporal supera de forma clara al baseline»— y la de validación usa otro —margen sobre la mayoritaria y calibración— | Reconciliar: dejar el original marcado como `SUPERSEDED` con la fecha de su reescritura, y el vigente como único criterio, que es lo que el capítulo 4 ya explica |
| `TRAZ-PI1-02` | `docs/matriz_validacion_pi.md:59-60` | Las cifras 54,3 °C y 70,7 °C del termostato **no tienen registro**; es uno de los cinco casos de `EVID-MAJ-019`, abierto | Marcar como **no utilizables** hasta regenerarlas como artefacto. El protocolo está en `08-analisis-por-fallo.md` |
| `TRAZ-PI1-03` | `docs/experiments/E7_modelo_temporal.md` | El informe no declara que la comparación confunde representación y estimador | Añadirlo como limitación, con la misma redacción que `05-protocolo-comparacion.md` |
| `TRAZ-PI1-04` | `experiments/E6_*.json`, `E7_*.json`, `E9_*.json` | Sin cabecera de identificación: ni `commit`, ni `executed_at`, ni `dataset_type`. Son anteriores a que la convención existiera | **No regenerar** para arreglarlo: eso cambiaría las cifras publicadas. Declararlo en el índice y en la reproducibilidad, y exigir la cabecera a los registros nuevos de PI.1 |

## 1.4 Orden y criterio de aceptación de la Fase A

Primero `CORRECTED-E7-01`, porque mientras el informe contradiga a su propio registro cualquier cita de
E7 es ambigua. Después las dos marcas `SUPERSEDED` de E7, después la fila E2, después las cuatro de la
tabla anterior.

**Criterio de aceptación:** ninguna cifra del informe de E7 difiere de su registro; ninguna afirmación
sobre el volumen aparece sin su marca; `v3` no se describe en ningún documento como calibrado; y las
dos cifras del termostato no se citan en ningún sitio como utilizables. Se comprueba leyendo, no
ejecutando.
