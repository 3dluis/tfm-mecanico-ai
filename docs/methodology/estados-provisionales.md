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
