# E13 — Agente con modelo de lenguaje pequeño

Fecha: 1 de septiembre de 2026 · Estado: **en curso** — ajuste fino pendiente de ejecutar
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
| Longitud máxima | 4 096 tokens; el prompt se recorta por la izquierda |
| Semilla | 20260901 |

**Solo las proyecciones de atención.** Es lo que decide a qué atiende el modelo
dentro del contexto --qué observación va con qué fragmento--, que es exactamente
lo que hay que enseñar. Las capas de alimentación, donde reside más conocimiento
factual, se dejan intactas: una razón más para que el manual no acabe en los
pesos.

**El recorte es por la izquierda.** Lo que se pierde en los prompts largos es el
principio del sistema y del contexto, nunca la evidencia recuperada ni la
completion, que están al final. Se cuenta cuántos se recortan.

## Pendiente

Ejecutar el ajuste, medir el después con las mismas nueve preguntas del antes, y
rellenar `10_llm_agent.ipynb`.
