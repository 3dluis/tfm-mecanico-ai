# Enmienda ENM-U01 al criterio de selección del umbral de confianza

**Fecha:** 4 de septiembre de 2026 · **Enmienda a:** `docs/methodology/criterio-umbral.md`
(commit `081c309`, 4 de septiembre de 2026, 00:08:25 −04:00) · **Posterior a:** el primer
barrido, commit `f9c5c0c`, 4 de septiembre de 2026, 00:10:49 −04:00 · **Estado:** aceptada.

Esta enmienda es **posterior al resultado del primer barrido**. No lo oculta ni lo sustituye:
el criterio original, su resultado y su fragilidad quedan registrados y se publican junto al
criterio revisado.

## 1. Qué dio el criterio original

| | |
|---|---|
| **Criterio original** | El umbral más bajo con precisión de decisión ≥ 0,93 sobre validación, medida por ventana |
| **Resultado** | **0,72** |
| **Precisión en 0,72** | 0,930233 = **80 aciertos de 86 ventanas cubiertas** |
| **Cobertura en 0,72** | 0,877551 por ventana · 0,877315 por sesión |
| **Observación** | Cumplimiento **marginal**: el objetivo se supera por 0,000233, es decir, por una ventana. Los umbrales inmediatamente superiores —0,74 a 0,78— **dejan de cumplirlo** |

Artefactos: `experiments/E15b_barrido_umbral.json`, `tables/E15b_barrido_umbral.csv`.

## 2. Por qué se enmienda

La necesidad de exigir estabilidad **no se identificó al escribir el criterio original: se
identificó al observar su resultado.** El criterio seleccionaba un punto aislado, y un punto de
operación que depende de una sola observación no describe la forma de la curva sino el ruido
de una muestra concreta. Con 98 ventanas de validación procedentes de 12 sesiones, reclasificar
una ventana bastaría para que 0,72 dejara de ser elegible.

Ese es un defecto del criterio, no del resultado. Un criterio de selección debe producir un
punto que sobreviva a una perturbación pequeña del conjunto sobre el que se calcula; el
original no lo exigía.

## 3. Declaración de conocimiento previo

Al escribir esta enmienda se conoce el resultado del primer barrido **y la lista completa de
umbrales que cumplen el criterio original**. La regla que sigue se define sin referencia a
ningún valor de umbral y se aplica de forma mecánica; su resultado se acepta sea cual sea, y
**no se enmendará una segunda vez para obtener un valor determinado**.

Se declara este conocimiento previo porque ocultarlo sería exactamente el defecto que esta
enmienda corrige.

## 4. Regla de estabilidad, definida de forma general

Sea una curva de precisión y cobertura evaluada sobre una rejilla de umbrales de paso `p`, y
sea `π` la precisión objetivo declarada en el criterio original.

> **E-1 · Estabilidad.** Un umbral candidato `t` es **estable** si **todos** los umbrales de la
> rejilla contenidos en el intervalo cerrado `[t, t + w]` alcanzan la precisión objetivo `π`.
>
> **E-2 · Selección.** Entre los umbrales estables se elige el **más bajo**, que es el que menos
> abstiene. Este punto no cambia respecto del criterio original.
>
> **E-3 · Salida vacía.** Si ningún umbral es estable, la regla **no se relaja**: se reporta la
> ausencia y la decisión escala al autor.

**Parámetros, fijados aquí:** `w = 0,05` en la escala de confianza; `p = 0,01`, de modo que el
intervalo abarca seis puntos consecutivos de la rejilla. `π = 0,93`, sin cambios.

**Justificación de `w`, independiente del resultado.** La anchura debe ser del orden de la
perturbación que una variación pequeña del conjunto de validación induciría en el punto de
corte. Con 98 ventanas, desplazar el umbral 0,05 modifica el conjunto cubierto en torno al 5 %
de la muestra. Un punto de operación que no sobrevive a esa perturbación está determinado por
un puñado de observaciones y no por la forma de la curva. No se fija un valor mayor porque
exigir mesetas más anchas descartaría regiones legítimas en curvas construidas sobre pocas
observaciones, y la regla debe seguir siendo aplicable a conjuntos de este tamaño.

**Aplicabilidad general.** E-1, E-2 y E-3 no mencionan ningún valor de umbral ni ninguna
propiedad de esta curva concreta. Se aplican a cualquier curva de precisión y cobertura sobre
cualquier partición de validación, sin conocer de antemano qué punto se desea obtener.

## 5. Lo que esta enmienda no cambia

- **La precisión objetivo `π = 0,93`** sigue siendo la misma política declarada en el criterio
  original: como máximo siete errores de decisión por cada cien explicaciones emitidas.
- **La partición.** Se usa exclusivamente validación. El conjunto de test permanece cerrado y
  no se consulta para elegir entre candidatos, ni antes ni después.
- **La preferencia por abstener menos.** Entre umbrales admisibles se sigue eligiendo el más
  bajo.
- **La obligación de reportar el resultado sea cual sea**, y de reejecutar las fases que
  dependan del umbral si cambia.

## 6. Análisis de sensibilidad

Junto al umbral seleccionado se registra un análisis de sensibilidad por remuestreo **por
sesión**, que es la unidad de independencia. Su función es **caracterizar la robustez del punto
elegido**, no volver a seleccionarlo: el punto se fija con E-1 y E-2, y el remuestreo solo
describe cuánto varía su precisión y su cobertura si el conjunto de validación hubiera sido
otro. Ninguna cifra del remuestreo puede usarse para cambiar la elección.

## 7. Qué se publicará

En la memoria y en el informe de fase, la secuencia completa y en este orden: criterio
original → barrido → fragilidad observada → esta enmienda → criterio revisado → selección
definitiva. Con la precisión y la cobertura de ambos puntos y el impacto sobre las decisiones
experimentales.

**No se presentará como una mejora de los resultados.** Si el cambio de umbral no modifica
ninguna decisión de los casos evaluados, se dirá así: la enmienda afecta al criterio de
selección del punto de operación y a nada más.
