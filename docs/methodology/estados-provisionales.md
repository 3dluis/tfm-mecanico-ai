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
