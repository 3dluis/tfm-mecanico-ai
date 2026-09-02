# El experimento, paso a paso

Guía de reproducción completa. Cada paso indica **qué comando ejecutar**, **qué
produce** y **qué se encontró al ejecutarlo**.

Todo lo que aparece aquí se ha ejecutado. Ninguna cifra está estimada.

> **Estado:** pasos 0 a 9 ejecutados. Los pasos 10 y siguientes requieren
> decisiones del autor que están abiertas: la fuente de datos OBD-II reales y el
> proveedor de modelo de lenguaje.

---

## Paso 0 · Preparar el entorno

```bash
cd mecanico-ia-exp
uv sync --all-extras
cp .env.example .env          # rellenar DATABASE_USER
uv run mecanico-exp doctor
```

**Produce:** entorno verificado.

**Debe mostrar:** Python 3.11, plataforma arm64, torch con dispositivo `mps`,
PostgreSQL y pgvector.

**Encontrado:** M4 Pro, Python 3.11.14, PyTorch 2.13 con MPS comprobado mediante
una multiplicación real de matrices --no basta con `is_available()`--,
PostgreSQL 14.15 y pgvector 0.8.0.

Detalle: [`experiments/E1_entorno.md`](experiments/E1_entorno.md)

---

## Paso 1 · Crear la base de datos y su esquema

```bash
bash scripts/init_db.sh          # crea mecanico_ia_exp y aplica migraciones
uv run alembic upgrade head
```

**Produce:** base `mecanico_ia_exp` con extensiones `vector` y `pg_trgm`, y el
esquema `rag` con 9 tablas: vehículo, documento, versión, fragmento, embedding,
ingesta, recuperación, resultado y enlace afirmación-evidencia.

**Nota:** el script es conservador. Si la base existe, no la recrea, y no toca
ninguna otra base del servidor.

---

## Paso 2 · Generar los datos OBD-II sintéticos

```bash
uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 \
    --sessions-per-fault 12 --duration-s 600
```

**Produce:** 43 200 muestras en 72 sesiones · 6 condiciones equilibradas ·
3 sesiones por cada cruce condición × régimen.

**Calibrado contra el manual del vehículo.** Cada constante del generador lleva
la cita del manual de la que sale:

| Parámetro | Valor | Fuente |
|---|---|---|
| Ralentí | 640–740 rpm | `srvc/B3E011002000W01.pdf` |
| Termostato | apertura 80–84 °C | `srvc/B3E010002000T03.pdf` |
| Caudal en ralentí | 2,5 g/s | `srvc/B3E014018880W14.pdf` |
| Avance de encendido | 9–11 BTDC° | `srvc/B3E011002000W01.pdf` |

**Encontrado:** los cuatro parámetros del generador anterior estaban **fuera de
especificación** --ralentí +15 %, caudal +24 %, avance +40 %--. Era coherente
consigo mismo y no correspondía a ningún vehículo.

**Advertencia que no desaparece:** calibrar contra el manual documenta los
parámetros; **no convierte los datos en reales**.

Detalle: [`experiments/E2_datos_sinteticos.md`](experiments/E2_datos_sinteticos.md) ·
[`methodology/calibracion-datos-sinteticos.md`](methodology/calibracion-datos-sinteticos.md)

---

## Paso 3 · Análisis exploratorio

```bash
uv run mecanico-exp eda
```

**Produce:** 6 figuras y 5 tablas.

**Encontrado:**

- **La deriva del caudalímetro no se ve en el caudalímetro**: delta de Cliff 0,13
  en `maf` frente a 1,00 en el ajuste de combustible.
- Dos de las cinco condiciones son **invisibles en las medias** y solo aparecen
  en la dispersión.
- Siete de las doce señales no separan nada por sí solas, **y ninguna se
  descarta**: una señal puede ser determinante en combinación y nula en solitario.

Detalle: [`experiments/E4_eda_temporal.md`](experiments/E4_eda_temporal.md)

---

## Paso 4 · Ventanear y repartir sin fuga

```bash
uv run mecanico-exp preprocess --dataset-id synthetic_v2
```

**Produce:** 588 ventanas de 120 s con 139 descriptores · reparto 392/98/98
auditado · 60 ventanas descartadas por cruzar la entrada del fallo.

**Debe mostrar:** `Reparto sin fuga: ninguna sesión aparece en dos particiones.`

**Encontrado:** se midió el **suelo de ruido** del estadístico «mejor descriptor
entre 139», partiendo la condición normal contra sí misma. Con ese control, el
efecto aparente del fallo de encendido a 30 s (0,396) quedó **por debajo del
ruido** (0,399), y sobre una señal que el fallo no toca.

La ventana se fijó en 120 s por **concordancia con el mecanismo**, no por tener
el número más alto.

Detalle: [`experiments/E5_preprocesamiento.md`](experiments/E5_preprocesamiento.md)

---

## Paso 5 · Entrenar el modelo especializado

```bash
uv run mecanico-exp train-baseline --dataset-id synthetic_v2
uv run mecanico-exp train-temporal --dataset-id synthetic_v2
```

**Produce:** bosque aleatorio y GRU bidireccional, con sus métricas y matrices de
confusión.

**Encontrado:**

| Modelo | F1 macro |
|---|---|
| Referencia mínima | 0,074 |
| Bosque aleatorio | **0,879** |
| GRU bidireccional | 0,823 |

La GRU **no supera** al baseline con este volumen de datos. Con el triple de
sesiones el orden se invierte (0,945 frente a 0,932): el límite era el **volumen
de datos**, no la arquitectura.

**Límite físico encontrado:** las ventanas de termostato bloqueado que el modelo
falla tienen 54,3 °C de media; las que acierta, 70,7. El fallo impone un techo de
71 °C: mientras el motor no lo habría superado, **la señal de un motor averiado
es idéntica a la de uno sano**. Ningún clasificador puede distinguirlas.

Detalle: [`experiments/E6_baseline.md`](experiments/E6_baseline.md) ·
[`experiments/E7_modelo_temporal.md`](experiments/E7_modelo_temporal.md)

---

## Paso 6 · Atribuir la decisión del modelo

```bash
uv run mecanico-exp xai
```

**Produce:** atribución SHAP de 18 casos, con función explicada declarada, fondo
de 100 ventanas normales de entrenamiento y su huella.

**Encontrado:** para la deriva del caudalímetro, **`maf` no aparece en la
atribución**. Ni una vez. Las contribuciones son `ltft_bank1` (0,875) y
`stft_bank1` (0,619).

Es el hallazgo del paso 3 **redescubierto por un camino independiente**.

Detalle: [`experiments/E9_atribucion.md`](experiments/E9_atribucion.md)

---

## Paso 7 · Registrar el vehículo y su documentación

```bash
# El manual se obtiene legítimamente y se coloca en:
#   corpus/vehicles/mazda-3-bk-2007/raw/user-provided/workshop-manual
uv run python -m mecanico_ia_exp.rag.ingest \
  --vehicle mazda-3-bk-2007 \
  --manifest corpus/vehicles/mazda-3-bk-2007/manifest.yaml
```

**Produce:** informe de ingesta con documentos registrados, descargados, omitidos
y fallidos.

**Reglas que el descargador no rompe:** solo URLs declaradas en el manifiesto con
`download: true` y acceso público. No salta autenticación, no automatiza
descargas por suscripción, no almacena credenciales y no evade restricciones.

Un documento ausente aparece como `MISSING_LICENSED_DOCUMENT` y **nunca** se
sustituye por una fuente de menor autoridad.

Detalle: [`rag/vehicle-corpus.md`](rag/vehicle-corpus.md) ·
[`rag/ingestion.md`](rag/ingestion.md) ·
[`rag/vehicle-document-candidates.md`](rag/vehicle-document-candidates.md)

---

## Paso 8 · Cargar el corpus en pgvector

```bash
uv run python scripts/ingest_mazda.py multilingual
```

**Produce:** 3 055 ficheros → **6 158 fragmentos** embebidos en 68 s sobre MPS ·
981 con DTC · **320 códigos distintos**.

**Encontrado:** la **similitud semántica rankea la evidencia autorizada por
debajo de la genérica**. Una consulta sobre la sonda devuelve
`HO2S INSPECTION` con 0,616 mientras el procedimiento del DTC P0133 --la
evidencia que sostiene la afirmación-- puntúa 0,436.

**Multilingüe:** el modelo por defecto es
`paraphrase-multilingual-MiniLM-L12-v2`. Con el monolingüe inglés, una consulta
en español encontraba el documento relevante en **1 de 5** casos; con el
multilingüe, 4 de 5 al mismo nivel que en inglés.

Detalle: [`experiments/E11_carga_rag.md`](experiments/E11_carga_rag.md) ·
[`rag/multilingual.md`](rag/multilingual.md)

---

## Paso 9 · Evaluar la recuperación

```bash
uv run mecanico-exp eval-retrieval
```

**Produce:** cinco estrategias evaluadas sobre el conjunto anotado, en dos
idiomas.

**Encontrado:**

| Estrategia | Hit@10 | MRR |
|---|---|---|
| semántica pura | **0,00** | 0,000 |
| + filtro de motor | 0,00 | 0,000 |
| + jerarquía de autoridad | 0,25 | 0,125 |
| híbrida (semántica + léxica) | 0,25 | 0,125 |
| **guiada por el diagnóstico** | **1,00** | 0,446 |

La recuperación semántica **nunca** encuentra el procedimiento correcto en los
diez primeros. Guiarla con el diagnóstico del modelo la lleva a encontrarlo
siempre.

Eso refuerza una decisión de arquitectura: **si el LLM diagnosticara sobre
OBD-II crudo, no habría diagnóstico previo que guiara la búsqueda**, y el sistema
se quedaría con la estrategia que puntúa cero.

Detalle: [`experiments/E12_evaluacion_recuperacion.md`](experiments/E12_evaluacion_recuperacion.md)

---

## Paso 10 · Verificar la suficiencia de la evidencia

```bash
uv run mecanico-exp sufficiency
```

**Produce:** veredicto EXPLAIN o ABSTAIN por caso, con todas las señales del
criterio y el rastro de por qué cada cita se aceptó o se descartó.

**Sin modelo de lenguaje.** Ni una llamada.

**El experimento central del TFM, en dos casos:**

| Caso | Confianza | Docs aplicables | Cobertura | Decisión |
|---|---|---|---|---|
| Evidencia presente | 0,908 | 4 | 1,00 | **EXPLAIN** |
| Evidencia retirada | 0,908 | **0** | 0,00 | **ABSTAIN** |

Mismos datos, mismo modelo, misma atribución, **misma confianza**. Solo cambia el
corpus. La decisión cambia porque cambió la evidencia.

**La pieza que faltaba:** verificar que la cita **sostiene** lo afirmado. Un
fragmento puede existir, resolver, pertenecer al vehículo correcto y tener buena
puntuación **sin decir nada** sobre lo que se afirma.

Detalle: [`experiments/E15_suficiencia.md`](experiments/E15_suficiencia.md) ·
[`methodology/abstention-policy.md`](methodology/abstention-policy.md)

---

---

## Paso 11 · Redactar con un modelo de lenguaje pequeño

```bash
ollama pull qwen2.5:3b-instruct-q4_K_M     # una vez; no se descarga solo
uv run mecanico-exp sufficiency --llm echo     # referencia inferior: plantilla
uv run mecanico-exp sufficiency --llm ollama   # SLM local sin ajustar
```

**Produce:** para cada caso, la salida redactada, si respeta el veredicto, si
cumple el esquema y si inventó alguna cita.

**El SLM solo redacta.** No diagnostica ni decide: eso ya lo hicieron el modelo
especializado y el verificador. Es medible si respeta la decisión que se le
comunica.

**Encontrado:**

| Proveedor | Válidas | Respeta veredicto | Citas inventadas |
|---|---|---|---|
| Plantilla | 9/9 | 4/9 | **0** |
| Qwen2.5-3B sin ajustar | 2/9 | 7/9 | **0** |

Cero citas inventadas: la barrera se comprueba **fuera** del modelo. Pero el SLM
sin ajustar rompe el esquema en 7 de 9, ignora el veredicto de abstención y cuelga
las cinco observaciones de cada afirmación.

Detalle: [`experiments/E13_agente_slm.md`](experiments/E13_agente_slm.md)

---

## Paso 12 · Generar el conjunto de ajuste del SLM

```bash
uv run mecanico-exp training-data
uv run python scripts/prepare_finetune.py
```

**Produce:** 62 ejemplos derivados de ejecuciones reales del pipeline, en tres
variantes de corpus, **equilibrados** entre explicar y abstenerse.

**Se entrena el formato de la tarea, no el contenido del manual.** El texto del
manual va en el prompt, nunca en la salida esperada. Se comprueba buscando
secuencias de ocho palabras compartidas: **0 fugas** en 62 ejemplos.

**Encontrado:** el reparto crudo era 124 ABSTAIN frente a 32 EXPLAIN. Entrenar así
enseñaría a abstenerse por costumbre. Se equilibró a propósito.

---

## Paso 13 · Ajustar el SLM con LoRA

```bash
uv run mecanico-exp finetune-slm --epochs 4
uv run mecanico-exp sufficiency --llm transformers        # antes: base
uv run mecanico-exp sufficiency --llm transformers-lora   # después: base + adaptador
```

**Produce:** adaptador LoRA en `models/slm_lora` (binario fuera de Git; su
configuración e historial de pérdida, dentro) y los registros
`experiments/E13_agente_transformers*.json`.

PyTorch + PEFT en MPS, bf16, *gradient checkpointing*. La pérdida solo actúa
sobre la completion: los tokens del prompt van enmascarados. Se descartó MLX
por funcionar solo en Apple Silicon.

**Antes y después con el mismo motor.** La medición inicial con Ollama
(cuantizado a 4 bits) no sirve como línea base del ajuste: cambiar el motor
cambia el resultado. El «antes» se mide cargando el modelo base con
`transformers`, el mismo que carga el adaptador.

**Resultado del ajuste:** 88 min, 0,24 % de parámetros, pérdida de validación
0,040 → 0,018 (mínimo 0,013 en la época 3), 28 de 55 prompts recortados.

**Primera medición** (esquema v1): válidas 5/9 → 6/9. Tres de los fallos eran
míos: el esquema no admitía los motivos que emite el verificador.

**Segunda medición** (esquema unificado): base 7/9, ajustado 7/9, veredicto
respetado 9/9 en ambos, cero citas inventadas en ambos. Mismo recuento, fallos
distintos: el base rompe el JSON en los EXPLAIN largos y cuelga cinco
observaciones de una afirmación; el ajustado escribe los EXPLAIN con una
observación y dos fragmentos por afirmación, y deforma el motivo en dos ABSTAIN
(«LOW_CLAIM_COVERDGE»). Causas, en los datos: objetivo y prompt usaban
vocabularios distintos, y esa clase de abstención tiene **un** ejemplo de 26.
Ver informe E13.

**Iteración 2:** objetivo con el motivo literal, todo lo demás igual
(`--adapter-dir slm_lora_v2`, medido con `--llm transformers-lora@slm_lora_v2`).
Resultado: **9/9 válidas, 9/9 veredicto, 0 citas inventadas, 0 fallos de
esquema**, latencia media 13,1 s. Los seis ABSTAIN con motivo y cifra
correctos; los tres EXPLAIN con una observación y dos fragmentos por afirmación.
Una sola variable cambiada, de 7/9 a 9/9. La iteración 3 (equilibrar por
motivo) no hizo falta y queda declarada como limitación.

**Estado:** cerrado. El redactor del sistema es `models/slm_lora_v2`.

## Pasos pendientes, y de qué dependen

| Paso | Qué falta | De quién depende |
|---|---|---|
| Calibrar umbrales de suficiencia | Se pusieron por criterio, no sobre validación | Trabajo pendiente |
| Corregir mapeo diagnóstico→DTC de F02 | La observación habla de ajustes y el procedimiento de tensión de circuito | Trabajo pendiente |
| FULL / PARTIAL / ABSENT / DISTRACTOR | Extender las cuatro condiciones a todos los casos | Trabajo pendiente |
| **Datos OBD-II reales** | **La PI dice «reales» y los actuales son sintéticos** | **Decisión del autor** |
| Evaluación final y demostración | Dependen de las dos anteriores | **Decisión del autor** |

---

## Errores cometidos y corregidos

Se listan porque forman parte del método, y porque varios de ellos habrían
producido resultados falsos que parecían correctos.

| Error | Cómo se detectó | Consecuencia si no |
|---|---|---|
| `dtype=np.str_` truncaba las etiquetas a su primera letra | Exactitud 0,000, imposible | Cifra falsa en el informe del baseline |
| Registros con nombre fijo se sobrescribían entre datasets | Al comparar dos ejecuciones | Cifras publicadas de otro experimento |
| La fusión devolvía puntuaciones de otra escala | Un caso puntuaba 0,016 y el resto 0,26–0,52 | Abstenciones por artefacto |
| La condición ABSENT no retiraba toda la evidencia | El caso seguía explicando sin ella | **Falso positivo en el experimento central** |
| Se afirmó que faltaba evidencia buscando el código genérico P0171 | El propio sistema la encontró bajo P2187 | Un caso de abstención inventado |
| La medición multilingüe se hizo con el filtro por DTC activo | Daba 1,00 en todo | Se habría concluido que el idioma da igual |
| El ajuste agotó la memoria de MPS y la tubería `\| grep` ocultó el código de salida | El adaptador no existía al terminar | «Entrenado» sin haber entrenado |
| El esquema de salida no admitía los motivos del verificador | El modelo ajustado copiaba el motivo y se le rechazaba | Se habría atribuido al modelo un fallo de diseño propio |
| El objetivo de entrenamiento traducía el motivo y el prompt mostraba el literal | El ajustado escribía «LOW_CLAIM_COVERDGE» | Un modelo entrenado contra dos vocabularios |
| Los ABSTAIN se equilibraron por variante de corpus, no por motivo | Un solo ejemplo de abstención por cobertura, la del experimento central | El ajuste no podía aprender el caso que más importa |

El patrón se repite: **casi todos se detectaron mirando cifras que no cuadraban**,
no ejecutando tests. Los tests protegen lo que ya se sabe; las cifras raras
avisan de lo que no.

---

## Reproducción completa

```bash
uv run mecanico-exp doctor
bash scripts/init_db.sh
uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 --sessions-per-fault 12
uv run mecanico-exp eda
uv run mecanico-exp preprocess --dataset-id synthetic_v2
uv run mecanico-exp train-baseline --dataset-id synthetic_v2
uv run mecanico-exp train-temporal --dataset-id synthetic_v2
uv run mecanico-exp xai
uv run python scripts/ingest_mazda.py multilingual
uv run mecanico-exp eval-retrieval
uv run mecanico-exp sufficiency
uv run mecanico-exp sufficiency --llm ollama
uv run mecanico-exp training-data
uv run python scripts/prepare_finetune.py
uv run mecanico-exp finetune-slm
uv run mecanico-exp sufficiency --llm transformers
uv run mecanico-exp sufficiency --llm transformers-lora                # iteración 1
uv run mecanico-exp finetune-slm --adapter-dir slm_lora_v2             # iteración 2
uv run mecanico-exp sufficiency --llm transformers-lora@slm_lora_v2
```

Gates, tras cualquier cambio:

```bash
uv run ruff check . && uv run mypy src && uv run pytest
```
