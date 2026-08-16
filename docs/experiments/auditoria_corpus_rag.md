# Auditoría del corpus y del pipeline RAG (paso previo a R3)

**16 de agosto de 2026 · auditoría, no propuesta de solución · ningún cambio ejecutado.**

## 1. Qué hay hoy, medido

| Dimensión | Estado medido |
|---|---|
| Fichero | `diagnostic-agent/knowledge/corpus_v1.yaml` |
| Documentos | **7** |
| Extensión total | **631 palabras** (de 71 a 135 por documento) |
| Procedencia | **Obra propia del proyecto**, redactada a partir de conocimiento técnico general; cero documentos externos |
| Licencia | `CC-BY-4.0` declarada en un comentario de cabecera, «Registrado en CORPUS_MANIFEST.md» |
| Manifiesto de licencias | **NO EXISTE.** `CORPUS_MANIFEST.md` no está en el repositorio |
| Metadatos por documento | Solo `failure_mode` y `component`. **Sin** `source`, `license`, `version`, `date`, `hash` |
| Chunking | **Ninguno**: un chunk por documento (`{doc_id}#0`) |
| Embeddings | **No se usan.** El retriever es **léxico** (solape de términos con ponderación tf), determinista, por decisión de ADR-0014; la recuperación densa quedaba para «la iteración siguiente», que no se ha hecho |
| `top_k` | **3 por defecto**, sobre un corpus de **7** chunks |

## 2. Los cuatro problemas, por orden de gravedad

### 2.1 El corpus está alineado uno a uno con el ground truth de la inyección

Hay **un documento por modo de fallo inyectado** (`vacuum_leak`, `maf_drift`, `thermostat`,
`o2_lag`, `misfire`, anomalías relacionales) más una ficha de interpretación de fuel trims.
El corpus no es una base documental sobre la que el sistema tenga que *encontrar* algo: es
la respuesta, escrita por el propio proyecto, con el nombre del fallo en los metadatos.

Cualquier métrica de recuperación sobre este corpus mide **la circularidad del montaje**, no
la capacidad de recuperación documental. Un `Hit@3` alto aquí no es evidencia de nada.

### 2.2 `top_k = 3` sobre 7 chunks devuelve el 43 % del corpus en cada consulta

Con esa proporción, las métricas de ranking (MRR, nDCG@K) pierden casi todo su poder
discriminativo: el margen entre un recuperador bueno y uno aleatorio se estrecha hasta ser
indistinguible del ruido.

### 2.3 La declaración de licencias no está respaldada

El corpus declara CC-BY-4.0 y remite a un manifiesto **que no existe**. Como todo el
contenido es obra propia el riesgo legal es nulo, pero el entregable **E9 («corpus RAG
empaquetado con manifiesto de licencias»)** no está cumplido, y en cuanto entre un solo
documento externo la ausencia de manifiesto deja de ser un detalle formal.

### 2.4 No hay chunking, así que no hay nada que evaluar sobre chunking

Un documento = un chunk. Las decisiones de tamaño, solape y granularidad —que son parte de
lo que un capítulo de RAG debe justificar— no existen todavía.

## 3. Restricción que impone el pre-registro y que hay que respetar al construir el corpus

El protocolo anti-contaminación de retirada triple (`pre-registro-v1.md` §7) **exige excluir
del corpus RAG todo documento que describa las firmas held-out o sus mecanismos**
—desacoplo RPM↔MAF, dinámica térmica muerta carga↔coolant, deriva lenta conjunta MAF/avance—
incluidas las descripciones de DTC directamente asociables, con la lista de exclusiones y el
hash del corpus congelado registrados **antes** de ejecutar.

Sobre el corpus actual esa retirada eliminaría, entre otros, `doc-relational-anomalies`: es
decir, **una fracción sustancial de un corpus de 7 documentos**. Un corpus que no sobrevive a
su propio protocolo anti-contaminación no es utilizable para el confirmatorio.

## 4. Qué NO se ha hecho aquí

- No se ha construido corpus nuevo, ni descargado documento alguno.
- No se ha tocado el retriever, ni el `top_k`, ni el chunking.
- No se ha diseñado `EXP-RAG-001`: el pre-registro global trata la evaluación del RAG como
  **R3, instrumental y descriptiva** (hit rate, MRR, nDCG, sin criterio de aceptación
  científico), y el contraste con y sin RAG vive dentro de **EXP-EXP-001** como variable
  secundaria. Inventar un experimento paralelo contradiría el pre-registro.
  Ver [F-PREREG_comparacion](preregistered/F-PREREG_comparacion.md) §4.

## 5. Lo que hace falta decidir antes de construir nada

1. **Fuentes admisibles.** Sin scraping masivo ni procedencia dudosa: documentación
   OBD-II/J1979 de uso permitido, documentación pública de sensores y PIDs, y material
   académico ya verificado en el estado del arte, correctamente citado.
2. **Tamaño objetivo.** Suficiente para que `top_k = 3` sea informativo: como orden de
   magnitud, cientos de chunks, no siete.
3. **Registro obligatorio por documento:** `source`, base legal de uso, versión/fecha, hash
   y parámetros de chunking — es decir, el `CORPUS_MANIFEST.md` que hoy falta.
4. **Separación explícita** entre corpus operacional del RAG y bibliografía científica del
   TFM. Son conjuntos distintos y no deben mezclarse.
5. **Consulta de evaluación**: un set de preguntas con relevancia anotada que **no** sea
   «el nombre del fallo» — o la circularidad de §2.1 se reproduce en el nuevo corpus.
