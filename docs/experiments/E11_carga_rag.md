# E11 — Carga del RAG en pgvector

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Vehículo: Mazda 3 BK 2007, motor Z6 · Corpus: manual de taller, 3 055 ficheros

## Qué se cargó

| | |
|---|---|
| Ficheros procesados | 3 055 · 243 MB |
| Ficheros sin texto extraíble | **0** |
| Fragmentos creados | **6 158** |
| Embeddings almacenados | 6 158 |
| Fragmentos con DTC | 981 |
| **Códigos DTC distintos** | **320** |
| Fragmentos con motor declarado | 1 983 |
| Tiempo total | **68,3 s** en MPS |
| Huella de la colección | `9a90d2f6a9515a89…` |

Reparto por capítulo: `srvc` 5 026 · `mission` 574 · `engine` 543 ·
`esi_common` 8 · `introduction` 7.

Clasificación de sistema: OTHER 1 975 · ELECTRICAL 1 162 · TRANSMISSION 943 ·
OBD 803 · EMISSIONS 349 · ENGINE 310. Toda clasificación va marcada como
`derived` o `unknown`: es una conjetura por términos, no un dato del manual, y
quien lea el fragmento debe poder distinguirlo.

## El hallazgo de la fase: la similitud rankea la evidencia autorizada por debajo

Consulta sobre respuesta lenta de la sonda lambda, que corresponde a la condición
F04 y cuya evidencia documentada es el procedimiento del **DTC P0133**.

| Modo | Primer resultado | Puntuación | ¿Lleva DTC? |
|---|---|---|---|
| Solo similitud semántica | `FRONT HEATED OXYGEN SENSOR (HO2S) INSPECTION` | **0,616** | — |
| Solo similitud semántica | `HEATED OXYGEN SENSOR (HO2S) FUNCTION` | 0,601 | — |
| Filtrando por `P0133` | `DTC P0133`, procedimiento real | **0,436** | P0133 |

El procedimiento diagnóstico que **sí** sostiene la afirmación puntúa **por
debajo** de secciones genéricas sobre el mismo componente. Un sistema que
ordenara por similitud lo dejaría fuera del top-3 y explicaría el fallo citando
una descripción de funcionamiento en lugar del procedimiento aplicable.

Es la tesis del trabajo, demostrada con números sobre documentación real:
**similitud no es evidencia**. Y justifica que la jerarquía de autoridad y el
filtrado por metadata pesen por encima de la puntuación del vector.

## Aislamiento entre vehículos

`vehicle_id` es **parámetro obligatorio** de `search`, no un filtro opcional. No
existe una búsqueda global entre vehículos que se pueda invocar por descuido.

| Comprobación | Resultado |
|---|---|
| Búsqueda con `vehicle_id` de otro vehículo | **0 resultados** |
| Filtro por motor `(Z6, ZJ)` sobre 200 resultados | 36 fragmentos de otro motor → **0** |

Un fragmento **sin** motor declarado no se descarta: puede ser información
general del vehículo. Se descarta el que declara motores y ninguno coincide.

## Procedencia: el gate de la fase

Desde cualquier resultado se reconstruye la cadena completa. Ejemplo real:

```
consulta
  → retrieval_run 0c7909f3-c310-4478-adad-aaedd779161d
  → fragmento mazda3-bk-workshop-manual-local@9a90d2f6a951:002910
  → documento mazda3-bk-workshop-manual-local
  → vehículo mazda-3-bk-2007 (Mazda3 BK 2007, motor Z6)
  → sección «HEATED OXYGEN SENSOR (HO2S) FUNCTION [ZJ, Z6]», página 1
  → fichero srvc/B3E014018860T01.pdf
  → editor Mazda Motor Corporation
  → https://www.mazdatechinfo.com/
```

La cita se genera con `RetrievedChunk.provenance()` y **nunca** produce «según el
manual» sin decir cuál.

## Decisiones de diseño

**Un manual es un documento, no miles.** 3 055 PDF son un solo manual de taller,
con una revisión y una cadena de procedencia. Su huella es la de la colección:
SHA-256 sobre la lista ordenada de (ruta relativa, huella del fichero). Cambiar
un solo fichero la cambia, y la idempotencia funciona a nivel de manual.

**Un fragmento no abandona su página.** El rango `page_start`-`page_end` siempre
corresponde al texto que contiene. Si un fragmento cruzara páginas sin
registrarlo, la cita señalaría un sitio donde el texto no está.

**Troceado estructural, no por longitud.** Se parte en fronteras del manual
--`DETECTION CONDITION`, `Diagnostic procedure`, `POSSIBLE CAUSE`…-- y solo se
recurre al corte por frase cuando no hay marcador. Un procedimiento partido a
mitad de su condición de detección produce dos fragmentos que, por separado, no
sostienen nada.

**La dimensión del vector está fijada en el esquema.** `vector(384)` obliga a
migrar para cambiar de modelo de embeddings. Parece rigidez y es lo contrario:
dos corpus indexados con modelos distintos no son comparables, y un esquema
permisivo dejaría mezclarlos sin que nada fallara.

**Sin índice aproximado.** Búsqueda exacta. Un índice HNSW introduciría
recuperaciones no reproducibles justo donde se mide la recuperación. Si el
volumen lo justifica se añadirá, y quedará registrado porque altera resultados.

**Los DTC se extraen literalmente.** No se infieren asociaciones entre un síntoma
y un código: eso sería fabricar la evidencia que el experimento verifica. Un test
comprueba que un texto que describe un síntoma sin código no genera código.

## Embeddings

Dos proveedores tras la misma interfaz:

| Proveedor | Uso | Red |
|---|---|---|
| `hashing` (**por defecto**) | Tests, CI, referencia inferior | Ninguna |
| `sentence-transformers` | Corpus real, MiniLM-L6-v2, MPS | Solo la primera descarga |

Ambos con 384 dimensiones a propósito: son intercambiables sin migrar el esquema.
El de hashing no captura sinonimia y existe también como referencia: si el modelo
aprendido no lo supera, no está aportando semántica.

Por defecto es `hashing`, de modo que un checkout recién clonado no descarga
modelos ni toca la red hasta que alguien lo pide.

## Tests

`tests/test_rag_pipeline.py` — 30 casos, 10 de ellos marcados `db` y ejecutados
contra el corpus realmente ingerido:

- `test_chunk_provenance`, `test_page_provenance`: la página citada contiene el
  texto del fragmento;
- `test_dtc_metadata` y `test_no_se_inventan_dtc_donde_no_los_hay`;
- `test_no_cross_vehicle_retrieval`, `test_vehicle_metadata_filter`;
- `test_pgvector_extension`, `test_embedding_storage`, `test_vector_search`;
- `test_retrieval_logging`: la consulta, sus parámetros y sus resultados quedan
  en la base;
- `test_la_exclusion_de_documentos_construye_las_variantes_del_corpus`: retirar
  evidencia es explícito y auditable, que es lo que necesitan las condiciones
  ABSENT y PARTIAL;
- `test_html_loader`: scripts y estilos no acaban en el texto ni en las citas.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 51 ficheros |
| `pytest` | **184 casos** en verde |

## Limitaciones

**El corpus no está verificado.** `verified: false`. El contenido es genuino pero
la copia es una conversión de terceros; falta confirmar número de manual y
revisión contra el catálogo oficial de Mazda.

**Los datos OBD-II siguen sin ser reales.** Están calibrados contra este mismo
manual, lo que hace sus parámetros documentados, no medidos.

~~**La condición F01 sigue sin respaldo.** P0171 no aparece en el corpus.~~

> **Corrección posterior (E15).** Esta afirmación es **falsa**. Mazda no usa los
> códigos genéricos de mezcla: usa la familia P2177/P2178/P2187/P2188. El corpus
> contiene 30 fragmentos con **P2187 — «Fuel system too lean at idle»**, cuya
> condición de detección vigila los ajustes de combustible en ralentí, que es
> exactamente la firma de esta condición. La evidencia estaba desde el principio;
> busqué el código equivocado. Ver `E15_suficiencia.md`.

## Siguiente

E12 — evaluación de la recuperación con conjunto anotado. El hallazgo de esta
fase le da su pregunta principal: cuánto mejora la recuperación al añadir
filtrado por metadata y jerarquía de autoridad sobre la similitud desnuda.
