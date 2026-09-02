# E13 — Agente con modelo de lenguaje pequeño

Fecha: 1–2 de septiembre de 2026 · Estado: **en curso** — ajuste ejecutado; segunda medición antes/después en marcha
Modelo: Qwen2.5-3B-Instruct, local, sin clave de API

## Reparto de responsabilidades

| Quién | Qué hace |
|---|---|
| Modelo especializado (bosque / GRU) | Diagnostica a partir de OBD-II |
| Atribución SHAP | Convierte la predicción en observaciones localizadas |
| Herramienta `retrieve_evidence` | Trae evidencia documental **del vehículo** |
| Verificador determinista (E15) | Decide EXPLAIN o ABSTAIN |
| **SLM** | **Redacta la decisión ya tomada, en lenguaje natural** |

El modelo de lenguaje no diagnostica, no decide si la evidencia basta y no
aporta conocimiento propio como fuente. Si decidiera él, la respuesta a la PI
dependería de su disposición a admitir que no sabe algo.

Lo que sí hace, y es medible: **respetar o no el veredicto**.

## Por qué un modelo local, y por qué pequeño

Local: sin clave, sin red tras la descarga, reproducible por un tercero sin darse
de alta en nada. Pequeño (3B): si un modelo pequeño basta cuando la evidencia se
le da hecha, ese es el resultado interesante; un modelo grande lo haría más
fácil y diría menos.

## Contrato de salida

Dos formas válidas y ninguna más: `EXPLAIN` con afirmaciones referenciadas, o
`ABSTAIN` con motivo. **Que la abstención sea una forma válida del esquema es
deliberado**: si solo pudiera explicar, abstenerse le exigiría desobedecer el
formato.

El validador rechaza además afirmaciones que declaren causa demostrada («está
causado por», «demuestra que»). La cadena OBD-II → modelo → atribución sostiene
observaciones, no causas.

**Barrera contra la cita inventada.** `verify_citations` comprueba que cada
referencia existe en lo que se entregó al modelo. Un identificador con la forma
correcta que no corresponde a nada se parece a una cita y resuelve a la nada.

## Medición sin ajuste fino

Nueve casos del conjunto anotado, dos proveedores:

| Proveedor | Salidas válidas | Respeta veredicto | Citas inventadas | Esquema roto |
|---|---|---|---|---|
| Plantilla determinista | 9/9 | **4/9** | 0 | 0 |
| Qwen2.5-3B sin ajustar | **2/9** | 7/9 | 0 | **7** |

**Cero citas inventadas en ambos**: la barrera se comprueba fuera del modelo, y
funciona.

Pero ninguno sirve tal cual. La plantilla explica siempre que hay evidencia
porque no lee el veredicto. El SLM sin ajustar:

- ignora el veredicto de abstención en los dos casos donde produjo salida;
- repite la misma afirmación **diez veces** cambiando dos palabras;
- cuelga las **cinco observaciones de todas las afirmaciones**, sin discriminar
  qué observación sostiene qué;
- confunde la semántica («demasiado rico» donde P2177 es *too lean*);
- rompe el esquema en 7 de 9: JSON truncado, campos fuera de límite.

Eso delimita el trabajo del ajuste: **no le falta conocimiento del vehículo**
--ese viaja en el prompt--, le falta saber *cómo se responde en esta tarea*.

## Qué se ajusta y qué no

**Se ajusta el formato de la tarea. No se ajusta el contenido del manual.**

La distinción sostiene el experimento central. Si el modelo memorizara los
procedimientos de Mazda, en la condición ABSENT --donde se retira la evidencia
del índice-- los recordaría de sus pesos y explicaría igual, con una cita de
aspecto correcto. El contraste FULL/ABSENT dejaría de medir la evidencia y
pasaría a medir la memoria. Sería exactamente el fallo que el trabajo estudia,
cometido por nuestro propio diseño.

Tres mecanismos lo garantizan, y los tres están comprobados:

1. **El texto del manual solo aparece en el prompt**, en la respuesta de la
   herramienta. La salida esperada contiene identificadores de fragmento, que sin
   el fragmento delante no dicen nada.
2. **`verify_no_manual_content_in_targets`** busca secuencias de ocho palabras
   compartidas entre la entrada y la salida esperada de cada ejemplo. Resultado
   sobre los 62 ejemplos: **0 fugas**. Hay un test que copia un trozo del manual
   a una salida a propósito y comprueba que se detecta.
3. **La pérdida se calcula solo sobre los tokens de la completion.** Los del
   prompt se enmascaran con `-100`. El gradiente no toca lo que el modelo ve del
   manual.

## Conjunto de entrenamiento

Derivado de **ejecuciones auténticas del pipeline**: ventanas reales de
validación, atribución, recuperación, ensamblado y verificación. Ninguno escrito
a mano ni generado por otro modelo.

Cada caso se genera en tres variantes de corpus --FULL, ABSENT, PARTIAL-- porque
si el modelo solo viera casos con evidencia aprendería que siempre se explica.

**Equilibrado a propósito.** El reparto crudo salía **124 ABSTAIN frente a 32
EXPLAIN** (79 %). Entrenar con eso enseñaría a abstenerse *por costumbre*, no
por evidencia: parecería prudente y sería inútil. Es uno de los desenlaces
adversos que el plan enumeró de antemano --abstención trivial, cobertura
próxima a cero--. Se submuestrearon las abstenciones conservando la proporción
entre variantes.

| | Ejemplos |
|---|---|
| FULL / EXPLAIN | 27 |
| PARTIAL / EXPLAIN | 5 |
| FULL / ABSTAIN | 10 |
| PARTIAL / ABSTAIN | 10 |
| ABSENT / ABSTAIN | 10 |
| **Total** | **62** · 55 entrenamiento, 7 validación |

Reparto **por caso**, no por ejemplo: dos variantes del mismo caso comparten
observaciones, y separarlas al azar filtraría información entre particiones
igual que ocurriría con las ventanas.

**La salida esperada ancla una afirmación por observación**, citando solo *su*
observación y los fragmentos que la sostienen. Es lo contrario de lo que hace el
modelo sin ajustar.

## Por qué PyTorch y no MLX

Se empezó con MLX --más rápido en Apple Silicon-- y se descartó por una razón que
pesa más: **MLX solo funciona en Apple Silicon**. Un tercero con Linux y NVIDIA
no podría reproducir el ajuste. PyTorch corre en cualquier sitio, es el stack
declarado del proyecto y es el mismo con el que se entrenó el modelo temporal.

Coste asumido: en MPS no hay cuantización a 4 bits, así que el modelo va en bf16
(unos 6 GB). Cabe en 24 GB y con 55 ejemplos el tiempo es irrelevante.

## Configuración del ajuste

| | |
|---|---|
| Método | LoRA (PEFT), rango 16, alpha 32 |
| Módulos | `q_proj`, `k_proj`, `v_proj`, `o_proj` — solo atención |
| Épocas | 4 |
| Tasa de aprendizaje | 2e-4 |
| Longitud máxima | 3 072 tokens; el prompt se recorta por la izquierda |
| Semilla | 20260901 |

**Solo las proyecciones de atención.** Es lo que decide a qué atiende el modelo
dentro del contexto --qué observación va con qué fragmento--, que es exactamente
lo que hay que enseñar. Las capas de alimentación, donde reside más conocimiento
factual, se dejan intactas: una razón más para que el manual no acabe en los
pesos.

**El recorte es por la izquierda.** Lo que se pierde en los prompts largos es el
principio del sistema y del contexto, nunca la evidencia recuperada ni la
completion, que están al final. Se cuenta cuántos se recortan.

**Por qué 3 072 y no 4 096.** El primer intento, a 4 096 tokens y sin
*gradient checkpointing*, agotó los 30 GiB de MPS (29,72 GiB ocupados). Se
activó el checkpointing, que recalcula activaciones en lugar de guardarlas, y se
bajó la longitud. El fallo pasó desapercibido en la primera ejecución porque
la salida iba por una tubería (`| grep`) que enmascaraba el código de salida:
se corrigió con `pipefail` y se anotó en la tabla de errores del paso a paso.

## Ajuste ejecutado

| | |
|---|---|
| Duración | 88 min (5 283 s) en MPS, bf16 |
| Parámetros entrenables | 7 372 800 de 3 093 311 488 — **0,24 %** |
| Ejemplos | 55 entrenamiento · 7 validación |
| Prompts recortados | **28 de 55** (por la izquierda) |

Pérdida por época, solo sobre tokens de la completion:

| Época | Entrenamiento | Validación |
|---|---|---|
| 1 | 0,480 | 0,040 |
| 2 | 0,058 | 0,020 |
| 3 | 0,031 | **0,013** |
| 4 | 0,027 | 0,018 |

**Lectura.** La pérdida cae un orden de magnitud en la primera época: el
formato es fácil de aprender. En la cuarta la de validación sube ligeramente
(0,013 → 0,018): con siete ejemplos de validación esa diferencia no es
concluyente, pero indica que una época menos habría bastado. Se conserva el
adaptador de la cuarta porque fue el que se midió; no se eligió a posteriori.

**28 de 55 prompts recortados** es mucho. Lo que se pierde es el principio del
prompt de sistema y de la lista de observaciones, no la evidencia recuperada ni
la salida esperada. Es una limitación conocida del hardware y se declara.

## Medición antes/después: primera pasada

Mismo motor (`transformers`, MPS, bf16, decodificación determinista), mismas
nueve preguntas. Eso es lo que hace comparable el antes y el después: la
medición inicial con Ollama usaba un modelo cuantizado a 4 bits y otro motor,
y no serviría de línea base.

| | Salidas válidas | Respeta veredicto | Citas inventadas | Esquema roto |
|---|---|---|---|---|
| Base (`transformers`) | 5/9 | 9/9 | 0 | 4 |
| Base + LoRA | **6/9** | 9/9 | 0 | 3 |

Registros: `experiments/E13_agente_transformers_esquema_v1.json` y
`..._transformers-lora_esquema_v1.json`.

Dos cosas que la tabla no dice:

- **El base con `transformers` respeta el veredicto 9/9**, frente a 7/9 con
  Ollama. La cuantización y el motor cambiaban el resultado más que el modelo.
- **El ajuste arregló los tres EXPLAIN y rompió un ABSTAIN.** El base rompía el
  JSON en los casos con explicación (C02, C05: objeto truncado, delimitador
  perdido a los 960 caracteres). El ajustado los produce bien y cita solo lo
  que existe. Los tres fallos restantes son los ABSTAIN *con documentos en el
  contexto* (C07, C08, C09), y son todos el mismo fallo.

### El fallo era de diseño, y lo encontró el modelo

Salida literal del modelo ajustado en un ABSTAIN por cobertura:

```json
{"decision": "ABSTAIN", "reason": "LOW_CLAIM_COVERGENCE",
 "missing_evidence": ["0.9 < 0.80"], "notes": "..."}
```

El verificador había emitido `LOW_CLAIM_COVERAGE` y el modelo lo vio en el
prompt. Pero el esquema de salida solo admitía cuatro motivos genéricos
(`INSUFFICIENT_EVIDENCE`, `NO_APPLICABLE_DOCUMENTATION`, …) que **no
coincidían con los ocho que emite el verificador**. Incluso una copia perfecta
habría sido rechazada. Dos vocabularios para el mismo concepto: fallo mío.

Se unificó el esquema para admitir literalmente los motivos del verificador
(commit `e2d7c59`), con un test que recorre los ocho.

Lo que **no** se hizo: un normalizador tolerante que acepte «COVERGENCE» como
«COVERAGE». El modelo también deforma el identificador y mangla la cifra
(`0.9` donde la cobertura era `0.00`). Son defectos reales de un 3B copiando
tokens que no tiene, y un normalizador los ocultaría en lugar de medirlos.

## Medición antes/después: segunda pasada (esquema unificado)

Pendiente: en ejecución. Se repiten **ambas** mediciones, base y ajustado, con
el esquema corregido, porque el cambio afecta a los dos. No se edita el
resultado a mano.

## Pendiente

Rellenar `10_llm_agent.ipynb` con la segunda pasada y cerrar el informe.
