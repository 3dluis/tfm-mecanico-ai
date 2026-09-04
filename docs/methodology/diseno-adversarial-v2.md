# Rediseño del escenario adverso: canales de información

**Fecha:** 4 de septiembre de 2026 · **Motivado por:** `RAG-MAJ-031`, `EXP-MAJ-101` y
`RAG-MIN-035` · **Estado:** diseño, **sin implementar y sin ejecutar**. Pendiente de auditoría.

## 1. Por qué el escenario anterior no podía observar lo que buscaba

El escenario adverso pregunta si un diagnóstico incorrecto produce una explicación incorrecta
aparentemente bien respaldada. Para que eso sea observable, el sistema tiene que **buscar
evidencia del diagnóstico falso**. No lo hizo:

- el diagnóstico incorrecto no tiene códigos asociados, así que la búsqueda **degradó a la
  estrategia mixta**, hecho que no estaba declarado;
- la consulta de texto describe los síntomas de la condición **real**;
- las exclusiones de corpus se derivan de la **etiqueta anotada**.

De modo que el sistema buscó evidencia de la condición verdadera mientras diagnosticaba otra
cosa. El desenlace peligroso era **inobservable por construcción**, y su ausencia no informa.

## 2. Tabla de canales, que es lo que faltaba

Cada canal por el que puede entrar información al sistema, con su estado. Los estados son
`OPEN`, `CLOSED`, `INVERTED` y `NOT_APPLICABLE`.

| Canal | Qué transporta | Estado en el adverso ejecutado | Estado exigido al rediseño |
|---|---|---|---|
| **O-1** selección de ventana | qué observación se evalúa | `INVERTED`: se exige predicción incorrecta | `INVERTED` |
| **O-2** construcción de la consulta | el texto con que se busca | `OPEN`: describe los síntomas de la condición real, redactado conociéndola | **`CLOSED`** |
| **O-3** códigos de avería | qué códigos acotan la búsqueda y exige el verificador | `CLOSED`: derivados de la predicción | `CLOSED` |
| **O-4** síntomas y descriptores | qué observaciones se pasan al ensamblador | `CLOSED`: salen de la atribución sobre la ventana | `CLOSED` |
| **O-5** metadatos derivados de la etiqueta | exclusiones de corpus, filtro de motor | `OPEN`: `exclude_dtc` y `exclude_files` salen de la etiqueta anotada | **`CLOSED`** o `NOT_APPLICABLE` |

Los dos canales abiertos, O-2 y O-5, son los que hacen inobservable el desenlace. El escenario
adverso ejecutado se reporta con esta tabla al lado.

## 3. Qué exige el rediseño

**O-2.** La consulta debe construirse **a partir de las observaciones del modelo**, no de un
texto escrito por una persona que conocía el fallo. El sistema en ejecución dispone de los
descriptores, su magnitud y su dirección; con eso se compone la consulta. Es además la única
forma de que la consulta corresponda al **diagnóstico emitido** y no a la condición real.

**O-5.** El escenario adverso se ejecuta sobre el **corpus completo, sin exclusiones**. Las
exclusiones existen para crear las condiciones de disponibilidad de evidencia del experimento
central; en el adverso no tienen función y solo introducen la etiqueta por la puerta de atrás.

**Consecuencia esperada, declarada ahora:** al retirar las exclusiones, las abstenciones por
ausencia total de soporte deberían desaparecer, porque el corpus vuelve a contener todo. Lo que
quede será atribuible al sistema y no al montaje.

## 4. Lo que el rediseño no puede arreglar

En esta partición **no existe ningún error de sustitución**: los doce errores del clasificador
del experimento son fallo hacia normal. Ninguna cantidad de rediseño crea casos que no están,
y **no se inventarán**.

Por tanto el escenario adverso, rediseñado o no, solo puede evaluar el **error por omisión**.
Se declara así, y `P-08` permanece parcialmente cerrado por esta razón, que es del conjunto de
datos y no del diseño.

## 5. Unidad de análisis

Los seis casos adversos anteriores eran **dos ventanas**. El rediseño reporta ventanas
independientes, y aprovecha las ventanas mal clasificadas por encima del umbral que la
selección anterior descartaba por tomar una sola por caso anotado.
