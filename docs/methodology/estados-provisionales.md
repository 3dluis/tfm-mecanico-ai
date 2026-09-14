# Estados provisionales del ciclo de corrección

**Fecha:** 4 de septiembre de 2026 · **Vigente hasta** que termine la reejecución canónica y
sus auditorías.

## Hallazgo crítico

| | |
|---|---|
| `MIXED-EMBEDDING-SPACE` | **corrección implementada y probada · reejecución pendiente · NO cerrado** |

Corregir el código **no** cierra un hallazgo científico. Se cerrará cuando estén completas:
corrección, pruebas, reejecución, auditoría y propagación aguas abajo.

## Artefactos y modelos

| Elemento | Estado |
|---|---|
| Resultados que dependen de recuperación | `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` |
| `TRAINING_DATASET_V1` | `SUPERSEDED_PENDING_CONFIRMATION` |
| Adaptador vigente | `NON_CANONICAL_PENDING_REGENERATION` |
| Condición de distractor | `PENDING_CANONICAL_RETRIEVAL_DIAGNOSIS` |
| Medición translingüe | `NOT_VERIFIABLE` |
| Prevalencia de duplicados | `UNIT_UNDEFINED_IN_LEGACY_RESULT` |
| Memoria del TFM | actualización **bloqueada** |

**`SUPERSEDED` no significa que las cifras fueran inventadas.** Significa: fueron reproducibles
bajo una implementación cuyo espacio vectorial no estaba correctamente restringido. Esa
distinción se mantiene en todos los documentos.

## Claims congelados hasta cerrar el ciclo

Calidad de la recuperación · pertinencia documental · la condición de distractor · la progresión
v1 → v2 → v2.1 · el 15 de 17 · el efecto del filtro de motor · la evaluación translingüe · el
conjunto de ajuste.

## Lo único que se puede sostener hoy

- Las cifras anteriores son **reproducibles**.
- Existía mezcla de espacios de embeddings.
- El problema afectaba a **tres rutas**: suficiencia, recuperación y agente, y datos de ajuste.
- La suite de integración **no lo detectaba**, y ella misma reproducía el patrón.
- La corrección elimina la posibilidad de omitir el espacio desde la interfaz.
- **Todavía no se sabe el efecto sobre los resultados científicos.**

Nada más. Ninguna anticipación.

## La pregunta de investigación no cambia

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

## Resultados sin artefacto canónico

| Elemento | Estado |
|---|---|
| Tabla de recuperación del capítulo 5, cinco filas | `LEGACY_RESULT_WITHOUT_CANONICAL_ARTIFACT` |

Las cinco filas publicadas **no corresponden** al único artefacto de recuperación del
repositorio: aquella ejecución fue sobrescrita y no existe. **No se reconstruyen para hacerlas
coincidir.** Su afirmación queda `NOT_VERIFIABLE` hasta la ejecución canónica, y la tabla futura
se generará **exclusivamente** desde ella. Ninguna cifra antigua se reutiliza por parecerse.

## Contradicción registrada, sin resolver

Dos afirmaciones incompatibles sobre la condición sin filtro de motor, ambas de documentos
propios:

| | Afirmación |
|---|---|
| **A** | el distractor no llega al verificador; la condición no cumple su requisito de entrada |
| **B** | el artefacto muestra que sus fragmentos **sí** llegan al verificador |

**No se elige redacción.** La contradicción se resuelve con recuperación canónica, siguiendo el
recorrido completo del fragmento —consulta, conjunto de candidatos, corte por posición, filtro
posterior, entrada al verificador— y determinando en qué punto entra o desaparece. Queda
registrada hasta entonces.

## Aprendizaje metodológico de esta revisión

Tres intentos consecutivos de fijar «una sola variable» revelaron **tres variables derivadas**
distintas, ninguna de las cuales estaba en la lista de lo que creíamos controlar:

| Intento | Variable descubierta | Cómo se descubrió |
|---|---|---|
| 1 | versión del verificador, v2.1 frente a v2.2 | auditoría de recuperación |
| 2 | conjunto de casos, 6 frente a 17 | auditoría de recuperación |
| 3 | mapa de códigos de avería | auditoría de recuperación |

Las tres son del mismo tipo: **estado del proyecto que derivó después de producirse el
artefacto** con el que se quiere comparar. Ninguna se detectó leyendo el código; las tres
aparecieron al intentar reproducir una ejecución antigua.

> **Principio que sustituye a «todo lo demás permanece idéntico».**
>
> Todo estado experimental capaz de modificar una salida debe estar **enumerado, versionado o
> con huella** antes de la ejecución. Una comparación no es de una variable porque el autor lo
> afirme, sino porque el resto del estado esté fijado y comprobable.

De ahí nace `configs/manifest_rerun_a.json`, que separa el estado controlado de la variable
manipulada y da huella a cada pieza. La frase deja de ser una declaración de intenciones y pasa
a ser una lista verificable.

Este aprendizaje pertenece a la contribución metodológica del trabajo, junto al patrón de
«ausencia de información tratada como ausencia de restricción». Son dos caras de lo mismo: en un
caso el sistema no declaraba lo que no sabía; en el otro, el experimento no declaraba lo que
había cambiado.

## Cuarta variable, y la introdujo el propio remedio

**Fecha:** 4 de septiembre de 2026 · **Hallazgo:** `RAG-MAJ-074`, detectado **antes** de medir.

La configuración que creé para congelar el mapa de códigos **omitía una entrada**:
`F04_o2_lag: ("P0133",)`. La construí desde una extracción por expresión regular que se saltó
esa línea, y **no la verifiqué contra el módulo**.

Consecuencia si se hubiera medido: el caso de la sonda de oxígeno tiene ese fallo, así que
habría recibido una lista de códigos vacía y **degradado a la estrategia mixta**. Su
recuperación habría cambiado por una causa ajena a la variable manipulada, y la caída se habría
leído como efecto del espacio vectorial.

> **La maniobra de control introdujo la variable que pretendía eliminar.** Es la cuarta variable
> derivada en cuatro intentos, y la primera causada por el propio remedio.

**Qué falló, y no es la expresión regular.** Falló verificar el artefacto de control contra su
fuente en lugar de contra mi propia extracción, y publicar una huella como **literal copiado**
que ningún código recalculaba: por ese hueco pasó la omisión sin que nada fallara.

**Correcciones aplicadas:**

| | |
|---|---|
| Extracción | por análisis sintáctico del módulo, no por expresión regular |
| Huella | se **recalcula** desde el contenido con la forma canónica declarada en el propio fichero |
| Prueba estructural | todo fallo de los seis casos debe tener entrada en el mapa: falla ante cualquier omisión futura, no solo ante esta |
| Prueba de fuente | el mapa congelado se compara con el del commit que produjo el artefacto |
| Commit de origen | `7a0d714`, no `4437d07`: el artefacto registra el modelo multilingüe, que no existía en el segundo |
| Manifiesto | el mapa se declara **por experimento**: la suficiencia usa el vigente, y aplicarle el congelado introduciría allí la variable que se está eliminando de la recuperación |

**Refuerzo del principio.** No basta enumerar el estado: **cada pieza de ese inventario debe ser
verificable contra su fuente y recomputable**. Un inventario copiado a mano es una cuarta
variable esperando su turno.


---

## Cierre parcial tras RERUN-A (13 y 14 de septiembre de 2026)

Añadido al final para no reescribir el estado del 4 de septiembre, que sigue siendo el
registro de lo que se sabía entonces. Resultado y comparación en
`docs/experiments/resultado-rerun-a.md`.

| Elemento | Estado del 4-09 | Estado tras RERUN-A |
|---|---|---|
| `MIXED-EMBEDDING-SPACE` | corrección implementada · reejecución pendiente · NO cerrado | reejecutado: **cerrado para recuperación, suficiencia y agente**; abierto para el adaptador (no reentrenado) |
| Resultados que dependen de recuperación | `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` | registros canónicos del 13/14-09 en `experiments/`; los anteriores quedan en `pre_mixed_embedding_fix/` como `NON-CANONICAL` (históricos) |
| `TRAINING_DATASET_V1` | `SUPERSEDED_PENDING_CONFIRMATION` | superseded por el conjunto del 13-09 (66 ejemplos); segunda variable (regla de reparto) declarada |
| Adaptador vigente | `NON_CANONICAL_PENDING_REGENERATION` | sin cambios; medido sobre evidencia canónica con resultado idéntico en los 9 casos comunes y 17/17 sobre el conjunto ampliado |
| Condición de distractor | `PENDING_CANONICAL_RETRIEVAL_DIAGNOSIS` | diagnosticada: `VALID_CONDITION` (C08) · `REDUNDANT_WITH_PARTIAL` (C12, C16) con filtro; válida en los tres fallos sin filtro |
| Medición translingüe | `NOT_VERIFIABLE` | sin cambios (paso C no ejecutable sin código nuevo) |
| Prevalencia de duplicados | `UNIT_UNDEFINED_IN_LEGACY_RESULT` | con la unidad del pre-registro §7: 0/300 en el artefacto canónico; el anterior sigue sin unidad |
| Tabla de recuperación del capítulo 5 | `LEGACY_RESULT_WITHOUT_CANONICAL_ARTIFACT` | existe artefacto canónico (`experiments/E12_retrieval.json`, 13-09) con las mismas cinco cifras de hit-rate; la tabla puede regenerarse desde él |
| Contradicción A/B sobre la condición sin filtro | registrada, sin resolver | resuelta a favor de **B**: en las tres condiciones sin filtro entra al menos un fragmento del fichero distractor (D-1 = sí) |
| Memoria del TFM | actualización bloqueada | desbloqueada para las cifras de recuperación y suficiencia; el capítulo 5 sigue sin incorporar RERUN-A salvo la corrección de E13 |
