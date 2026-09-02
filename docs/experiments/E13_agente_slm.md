# E13 — Agente con modelo de lenguaje pequeño

Fecha: 1–2 de septiembre de 2026 · Estado: **cerrada** — dos iteraciones del ajuste, la segunda 9/9 sobre el conjunto anotado
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

Se repitieron **ambas** mediciones con el esquema corregido, porque el cambio
afecta a los dos. Registros: `experiments/E13_agente_transformers.json` y
`..._transformers-lora.json`.

| | Salidas válidas | Respeta veredicto | Citas inventadas | Esquema roto | Latencia media · máx |
|---|---|---|---|---|---|
| Base (`transformers`) | 7/9 | 9/9 | 0 | 2 (C02, C05) | 20,4 s · 100,7 s |
| Base + LoRA v1 | 7/9 | 9/9 | 0 | 2 (C07, C08) | 14,7 s · 38,0 s |

**El base pasa de 5/9 a 7/9 sin tocar el modelo.** Sus dos fallos en C07 y C08
de la primera pasada eran también el fallo de vocabulario. Conviene decirlo:
dos de los cuatro «fallos del modelo base» eran míos.

**Contra el criterio fijado** (después ≥ antes en válidas, cero citas
inventadas, veredicto no peor): se cumple, **en el límite**. Mismo recuento.
Presentarlo como mejora sería inflarlo; presentarlo como fracaso ignoraría lo
que cambió, que el recuento no ve.

### Qué cambió, más allá del recuento

Los dos modelos fallan en cosas distintas:

- **El base falla cuando tiene que escribir mucho.** Sus dos fallos son EXPLAIN
  con el JSON roto: objeto truncado (C02), delimitador perdido en el carácter
  960 (C05). En su único EXPLAIN válido (C03), tardó 100 s, produjo dos
  afirmaciones, y la segunda **cuelga las cinco observaciones** y dice «el
  manual de servicio indica que P0133 se detecta cuando…»: parafrasea el manual
  como si fuera una afirmación propia, y llama al sensor de oxígeno «sensor de
  óxidos de hidrógeno».
- **El ajustado escribe los tres EXPLAIN bien.** Tres afirmaciones por caso,
  **cada una con exactamente una observación y dos fragmentos**, las tres
  distintas, ninguna parafrasea el manual, ninguna afirma causa. Es
  literalmente la forma que se entrenó. Latencia máxima de 100,7 s a 38 s.
- **El ajustado falla en dos ABSTAIN con documentos en contexto**, escribiendo
  `LOW_CLAIM_COVERDGE`. Copia el motivo que ve en el prompt y deforma el token.
  Cita y cifra correctas esta vez (`cobertura 0.00 < 0.80`).

En la tarea que el ajuste apuntaba --anclar cada afirmación a su observación y
sus fragmentos, sin parafrasear el manual-- el cambio es de calidad, y se ve
caso a caso en el cuaderno 10. En el recuento global no se ve porque el ajuste
trajo un fallo nuevo, y ese fallo tiene dos causas que sí se identificaron.

### Por qué deforma el motivo: dos causas, las dos en los datos

1. **Objetivo y prompt no decían lo mismo.** `build_target` traducía los ocho
   motivos del verificador a cuatro genéricos: `LOW_CLAIM_COVERAGE` se convertía
   en `INSUFFICIENT_EVIDENCE`. El prompt, en cambio, mostraba el literal. El
   modelo aprendió dos vocabularios para lo mismo y en inferencia intentó copiar
   el del prompt, que no había entrenado a escribir.
2. **Esa clase tiene un ejemplo.** De los 26 ABSTAIN de entrenamiento, 19 son por
   baja confianza, 6 por falta de evidencia documental y **1** por cobertura de
   afirmaciones. Los casos centrales del experimento --PARTIAL y DISTRACTOR-- se
   abstienen justamente por cobertura, con confianza 0,908. El modelo vio esa
   situación una vez. El equilibrado del conjunto se hizo por variante de
   corpus, no por motivo de abstención, y esto es lo que se le escapó.

## Iteración 2: una sola variable

Se corrige la causa 1 y solo esa: el objetivo dice **el motivo literal del
verificador**, que el esquema ya admite. El resto --datos, reparto, semilla,
hiperparámetros, longitud-- es idéntico, para que la diferencia con la v1 se
deba a una cosa. El adaptador se guarda en `models/slm_lora_v2` y se mide con
`--llm transformers-lora@slm_lora_v2`; la v1 no se pisa.

Distribución de motivos en los objetivos ABSTAIN de entrenamiento:

| Motivo | v1 (traducido) | v2 (literal) |
|---|---|---|
| Baja confianza del modelo | 13 | 19 |
| Sin evidencia documental aplicable | 12 | 6 |
| Cobertura de afirmaciones | 1 | 1 |

La distribución cambia porque la v1 daba prioridad al motivo documental si
aparecía en cualquier posición de la lista, y la v2 toma el primero, que es el
que el verificador considera principal. La cobertura sigue con un ejemplo: la
causa 2 no se toca en esta iteración a propósito.

**Si la v2 sigue fallando en C07 y C08**, la iteración 3 será equilibrar los
ABSTAIN por motivo, no solo por variante. Se decide después de medir, no antes.

### Ajuste v2 ejecutado

75 min, mismos 0,24 % de parámetros, mismos 28 de 55 prompts recortados. Curva
de validación 0,036 → 0,020 → 0,012 → 0,018: indistinguible de la v1. Cambiar
la etiqueta del motivo en 26 objetivos no mueve la pérdida agregada; lo que
mueve es lo que el modelo escribe en el campo `reason`, que la pérdida media
apenas ve. Registro: `models/slm_lora_v2/finetune_config.json`.

## Iteración 2: resultado

Mismo motor, mismas nueve preguntas, mismo esquema unificado. Registro:
`experiments/E13_agente_transformers-lora@slm_lora_v2.json`.

| | Salidas válidas | Respeta veredicto | Citas inventadas | Esquema roto | Latencia media · máx |
|---|---|---|---|---|---|
| Base (`transformers`) | 7/9 | 9/9 | 0 | 2 | 20,4 s · 100,7 s |
| Base + LoRA v1 | 7/9 | 9/9 | 0 | 2 | 14,7 s · 38,0 s |
| **Base + LoRA v2** | **9/9** | 9/9 | 0 | **0** | 13,1 s · 31,3 s |

Caso a caso:

- Los tres EXPLAIN (C02, C03, C05): tres afirmaciones, **cada una con una
  observación y dos fragmentos**, las tres distintas, ninguna parafrasea el
  manual, ninguna afirma causa. Las limitaciones son las dos de rigor: «la
  atribución indica de qué depende la predicción, no qué le ocurre al
  vehículo» y «la evidencia sostiene lo observado, no demuestra la causa».
- Los seis ABSTAIN: motivo **literal y correcto** en todos, incluidos C07 y C08
  (`LOW_CLAIM_COVERAGE`, `cobertura 0.00 < 0.80`), C06
  (`NO_APPLICABLE_DOCUMENTARY_EVIDENCE`) y C09 (`TOO_FEW_SUPPORTING_CHUNKS`).
  Las cifras del campo `missing_evidence` coinciden con las del verificador.

**Contra el criterio fijado**: se cumple con margen. De 7/9 a 9/9 cambiando
una sola cosa, y esa cosa estaba en los datos de ajuste, no en el modelo.

### Lo que dice la comparación v1 → v2

La causa 2 --un solo ejemplo de abstención por cobertura entre 26-- **no hizo
falta corregirla**. Con el objetivo y el prompt diciendo lo mismo, el modelo
copia bien el motivo aunque lo haya visto una vez: no tiene que *recordarlo*,
tiene que *transcribirlo* de un contexto que lo contiene. Es coherente con lo
que el ajuste pretendía desde el principio: enseñar la forma de la tarea, no
su contenido. La desproporción sigue existiendo y se declara como limitación,
porque un motivo que no esté en el prompt sí exigiría haberlo aprendido.

Lo que el recuento no mide, y conviene dejar escrito: **ninguna de las tres
mediciones produjo una cita inventada**, ni antes ni después de ajustar, ni con
el esquema viejo ni con el nuevo. Eso no lo consiguió el ajuste: lo garantiza
`verify_citations`, que se comprueba fuera del modelo. El ajuste consiguió que
el modelo *cumpliera el contrato*; la barrera es la que hace que incumplirlo
no cueste una cita falsa.

## Limitaciones

- **Nueve casos.** Una unidad no separa nada; lo que separa es la estructura
  caso a caso y que el fallo de la v1 tuviera causa identificada y corregible.
- **Datos sintéticos** calibrados con el manual. La PI habla de datos reales.
- **28 de 55 prompts recortados** por la izquierda en ambas iteraciones.
- **Siete ejemplos de validación**: la subida de la pérdida en la época 4 no
  es concluyente en ninguna de las dos curvas.
- **Un motivo de abstención con un ejemplo**; funciona porque el prompt lo
  contiene.
- **Las plantillas describen dirección de contribución, no signo**: «delta_min
  de −1,496, por encima de lo esperable» es correcto como contribución SHAP y
  confuso como frase. Es herencia de las plantillas deterministas de E9, no del
  modelo; corregirlo es trabajo de redacción de plantillas, no de ajuste.
- **Decodificación determinista en un motor** (MPS, bf16). Otro motor daría
  otro «antes».

## Conclusión

Un modelo de 3B local, con la evidencia entregada hecha y la decisión ya
tomada, **redacta respetando el veredicto y citando solo lo que existe** en 9
de 9 casos anotados tras un ajuste del 0,24 % de sus parámetros que no contiene
una palabra del manual. El ajuste no le enseñó qué le pasa a un Mazda; le
enseñó cómo se contesta en esta tarea. Y las dos veces que falló --antes y
entre iteraciones-- el fallo estaba en el instrumento, no en el modelo.

Cierra el paso 13 del experimento. E18 (ablaciones) puede usar la v2 como
redactor. E19 y E20 siguen bloqueadas por los datos reales.
