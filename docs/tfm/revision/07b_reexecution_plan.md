# 07b · Plan de reejecución

**Fecha:** 3 de septiembre de 2026 · **Nada se ha ejecutado.** Este documento identifica cada
reejecución, con qué se ejecuta y qué se espera de ella.

**Regla que gobierna todas:** ninguna presupone que el resultado será igual. Cada ficha
declara el resultado esperado **y** qué se hace si no coincide. Un resultado distinto del
esperado es un hallazgo, no un fallo de la reejecución.

**Precondición común, sin excepción:** antes de la primera reejecución se implementa la
cabecera de identificación de registros (P-01, causa raíz). Ninguna reejecución escribe un
registro que no lleve `experiment_id`, `commit`, `executed_at`, `seed`, `dataset_id`,
`dataset_type`, versión de corpus y modelo cuando apliquen. De otro modo se repite el defecto
que originó todo P-01.

**El conjunto de test permanece cerrado.** Ninguna reejecución lo abre. `load_partition("test")`
seguirá lanzando excepción.

---

## Resumen

| ID | Qué | Clasificación | Origen | Bloqueado por |
|---|---|---|---|---|
| `RX-00` | Cabecera de identificación en todos los registros | precondición | P-01 causa raíz | — |
| `RX-01` | E15 con la plantilla de afirmaciones corregida, la calibración registrada y `source_file` serializado | `REEXECUTE_SAME_EXPERIMENT` | P-06A, P-01 nº 4, P-11 | `RX-00` |
| `RX-02` | E13 con el respeto al veredicto corregido | `REEXECUTE_SAME_EXPERIMENT` | P-06B | `RX-00`, `RX-01` |
| `RX-03` | Medición translingüe con registro | `REEXECUTE_SAME_EXPERIMENT` | P-01 nº 3 | `RX-00` |
| `RX-04` | Barrido de umbrales como artefacto | `REEXECUTE_SAME_EXPERIMENT`, opcional | P-07 | `RX-00`, decisión D-05 |
| `RX-05` | Comparación entre modelos con réplicas | `REEXECUTE_SAME_EXPERIMENT`, opcional | P-04, P-06C | decisión D-02 |
| `NX-01` | Recuperación guiada por la predicción del modelo | `NEW_EXPERIMENT` | P-02 | decisión D-03 |
| `NX-02` | Escenario adverso con diagnóstico incorrecto | `NEW_EXPERIMENT` | P-08 | decisión D-08 |
| `NX-03` | Ampliación del conjunto anotado a más fallos por condición | `NEW_EXPERIMENT` | P-03 | decisión D-04 |
| `NX-04` | Brazo con citas generadas por el modelo | `NEW_EXPERIMENT`, trabajo futuro | P-05 | decisión D-09 |

**Cuatro reejecuciones del mismo experimento** en el camino corto (`RX-00` a `RX-03`), dos
opcionales y cuatro experimentos nuevos, todos condicionados a una decisión.

---

## RX-00 · Cabecera de identificación de registros

| Campo | Contenido |
|---|---|
| **Tipo** | Precondición. No produce resultados científicos |
| **Qué cambia** | Una función común que escribe en cada registro: `experiment_id`, `commit` (de `git rev-parse HEAD`), `executed_at` en UTC, `seed`, `dataset_id` y `dataset_type`, versión de corpus e identificador de ingesta, modelo y versión, y versión del conjunto anotado cuando aplique |
| **Artefactos afectados** | Los quince ficheros de `experiments/`, en cuanto cada uno se vuelva a escribir. **No se reescriben los existentes**: los antiguos se conservan tal cual y se marcan como anteriores a la cabecera |
| **Tests** | Uno que compruebe que un registro recién escrito lleva los campos obligatorios; uno que falle si el árbol tiene cambios sin confirmar al escribir un registro, o que lo anote |
| **Riesgo** | Ninguno científico |

---

## RX-01 · E15 con instrumento corregido, calibración registrada y procedencia completa

| Campo | Contenido |
|---|---|
| **experiment_id actual** | `E15_sufficiency` |
| **Script** | `uv run mecanico-exp sufficiency` → `src/mecanico_ia_exp/experiments/sufficiency_runner.py` |
| **Entrada** | `configs/goldset_mazda3_bk.yaml` (9 casos), partición de validación de `synthetic_v2`, índice de pgvector con el modelo multilingüe |
| **Semilla** | `20260901` (la del baseline y la de la selección de fondo de atribución) |
| **Dataset** | `synthetic_v2`, `dataset_type: synthetic` |
| **Modelo** | Bosque aleatorio de `BaselineConfig` más calibración isotónica con validación cruzada de 5 pliegues sobre entrenamiento |
| **Configuración** | `SufficiencyThresholds()` **sin cambios**: `min_confidence` sigue en 0,80. Esta reejecución **no toca umbrales** |
| **Qué se corrige antes** | (1) la plantilla de afirmaciones de `evidence/assembly.py:155-160`, para que el texto no contradiga el signo del valor que cita; (2) el runner escribe el bloque de calibración en el registro; (3) `evidence/model.py` serializa `source_file` y `document_version_id` |
| **Resultado que se espera regenerar** | Los 9 veredictos, los paquetes de evidencia con textos corregidos, las 63 comprobaciones de soporte, la tabla de suficiencia y el bloque de calibración |
| **Qué se espera** | Las **decisiones** no deberían cambiar: no dependen del texto de la afirmación ni del umbral en el intervalo verificado. Las **cifras de calibración** deberían reproducir 0,144 → 0,085 por ser ejecución determinista con semilla. Los **textos** cambiarán |
| **Qué se hace si no coincide** | Si alguna decisión cambia, se detiene y se investiga: significaría que el texto de la afirmación influye en el soporte, lo que sería un hallazgo nuevo. Si la calibración no reproduce, se investiga la fuente de no determinismo antes de publicar nada |
| **Artefactos afectados** | `experiments/E15_suficiencia.json`, `tables/E15_suficiencia.csv`, y en cascada `cap5` §PI.1, §PI.2, §PI.3-PI.4, la matriz de validación y el informe de la fase |
| **Tests de regresión** | Texto de afirmación coherente con el signo del valor; registro con bloque de calibración; evidencia serializada con `source_file` |

---

## RX-02 · E13 con el respeto al veredicto corregido

| Campo | Contenido |
|---|---|
| **experiment_id actual** | `E13_agent`, tres configuraciones |
| **Script** | `uv run mecanico-exp sufficiency --llm transformers` · `--llm transformers-lora` · `--llm transformers-lora@slm_lora_v2` |
| **Entrada** | Los mismos 9 casos y los paquetes de evidencia que produzca `RX-01` |
| **Semilla** | Decodificación determinista (`do_sample=False`); semilla del pipeline `20260901` |
| **Dataset** | `synthetic_v2` |
| **Modelo** | Modelo base de 3 000 millones de parámetros y los adaptadores existentes en `models/slm_lora` y `models/slm_lora_v2`. **No se reentrena nada** |
| **Configuración** | Sin cambios en generación. Se corrige el cálculo del respeto al veredicto en `llm/agent.py` |
| **Resultado que se espera regenerar** | Los 27 registros de ejecución del agente (9 casos × 3 configuraciones) y la tabla comparativa |
| **Qué se espera** | Las salidas válidas y las citas inexistentes no deberían cambiar. El **respeto al veredicto** cambiará de denominador: dejará de ser 9/9 en las configuraciones con fallos de esquema. Los textos de las afirmaciones cambian porque cambia el prompt (viene de `RX-01`), lo que **podría** alterar alguna salida del modelo |
| **Qué se hace si no coincide** | Si una configuración pierde salidas válidas respecto de la ejecución anterior, se reporta el cambio y se investiga si procede del texto corregido. **No se elige la ejecución más favorable**: se publica la nueva y se declara la anterior |
| **Artefactos afectados** | `experiments/E13_agente_transformers.json`, `..._transformers-lora.json`, `..._transformers-lora@slm_lora_v2.json`; `cap5` §modelo de lenguaje; informe de la fase; cuaderno del agente |
| **Tests de regresión** | Fallo de esquema no deja el campo en verdadero; el denominador publicado coincide con las salidas válidas |
| **Coste** | Unos 20 minutos de inferencia por configuración en el equipo del autor |

---

## RX-03 · Medición translingüe con registro

| Campo | Contenido |
|---|---|
| **experiment_id actual** | **Ninguno.** La medición no tiene identificador de fase. Se propone `E12b_multilingual` |
| **Script** | **No existe.** Hay que escribirlo antes: la medición se hizo de forma manual. Recupera la lógica descrita en `docs/rag/multilingual.md` |
| **Entrada** | Los cinco casos con documento relevante conocido; consultas en español y en inglés |
| **Semilla** | No aplica (recuperación determinista) |
| **Dataset** | Corpus documental indexado, no telemetría |
| **Modelo** | Dos índices de embeddings: el monolingüe en inglés y el multilingüe, ambos sobre los mismos fragmentos |
| **Configuración** | Profundidad 500, **sin filtro por código de avería** (el filtro es lo que ocultaba el efecto) |
| **Resultado que se espera regenerar** | Documentos hallados y posición mediana, por modelo e idioma |
| **Qué se espera** | Reproducir el orden cualitativo publicado: el modelo monolingüe se degrada con consultas en español. Las cifras exactas **pueden no coincidir**: el índice se ha reingerido desde entonces |
| **Qué se hace si no coincide** | Se publica lo que salga. Si el efecto desaparece, se retira la afirmación del capítulo y se declara |
| **Alternativa** | Si el autor prefiere no invertir aquí, la tabla se **retira** del capítulo 5 hasta que exista registro. La afirmación «el idioma importa» no puede publicarse sin artefacto |

---

## RX-04 · Barrido de umbrales como artefacto · opcional, condicionado a D-05

| Campo | Contenido |
|---|---|
| **experiment_id propuesto** | `E15b_threshold_sweep` |
| **Script** | A escribir en `scripts/` o como subcomando; hoy la tabla vive en un docstring |
| **Entrada** | Probabilidades calibradas y aciertos por ventana de la partición de **validación**, con `session_id` |
| **Semilla** | `20260901` |
| **Dataset** | `synthetic_v2`, validación. **El test no se usa bajo ninguna circunstancia** |
| **Configuración** | Barrido sobre el rango de umbrales; se reportan cobertura y precisión **por ventana y por sesión** |
| **Condición previa innegociable** | El criterio de selección se escribe y se fecha **antes** de leer la tabla. Si el criterio fechado no selecciona 0,80, se reporta y se decide antes de la evaluación final |
| **Resultado que se espera regenerar** | La tabla del docstring, ahora como artefacto |
| **Qué se espera** | Reproducir cobertura 0,929 / 0,867 / 0,827 / 0,612 y precisión 0,912 / 0,929 / 0,938 / 0,917 |
| **Qué se hace si no coincide** | Se publica lo que salga y se revisa si el docstring describía otra ejecución |
| **Nota** | Si la decisión D-05 es «declarar heurístico», esta reejecución **no hace falta** |

---

## RX-05 · Comparación entre modelos con réplicas · opcional, condicionado a D-02

| Campo | Contenido |
|---|---|
| **experiment_id actual** | `E7_temporal` |
| **Script** | `uv run mecanico-exp train-temporal --dataset-id …` con modificación para varias semillas |
| **Entrada** | Predicciones por ventana de ambos modelos, con `session_id`, en `synthetic_v2` y `synthetic_v3` |
| **Semillas** | Cinco, declaradas de antemano; se reporta mediana y rango, nunca la mejor |
| **Configuración** | Selección de época sobre partición **interna de entrenamiento**, no sobre la validación que se reporta; el bosque, sin cambios |
| **Resultado que se espera regenerar** | Diferencia por sesión, apareada, con intervalo por remuestreo por sesión, en los dos conjuntos |
| **Qué se espera** | En `synthetic_v2`, diferencia a favor del bosque; en `synthetic_v3`, a favor de la red. **En ambos casos es plausible que el intervalo incluya el cero**, lo que daría `INCONCLUSIVE` |
| **Qué se hace si no coincide** | Se publica el intervalo, sea cual sea. No se elige el conjunto que favorece a una conclusión |
| **Cuándo hace falta** | Solo si el autor quiere sostener un **orden** entre los dos modelos. Si el texto pasa a inconcluso con las dos cifras, no hace falta |

---

## Experimentos nuevos, todos condicionados a una decisión

### NX-01 · Recuperación guiada por la predicción del modelo · D-03

Sustituye la etiqueta anotada por la clase que predice el modelo en la construcción de la
consulta. Se reporta por separado el subconjunto con diagnóstico correcto —debe reproducir la
cota superior actual—, el subconjunto con diagnóstico incorrecto y el agregado. La etiqueta
solo se usa para **evaluar**, nunca para consultar. Coste: bajo; reutiliza el pipeline.

### NX-02 · Escenario adverso · D-08

Invierte la selección de `sufficiency_runner.py:112` para tomar ventanas **mal clasificadas**.
Exige anotar qué se espera de cada caso adverso y fijar el criterio de éxito **antes** de
ejecutar. Coste: medio. Valor científico alto. Comparte casi toda la implementación con
`NX-01`, así que conviene decidirlos juntos. **Resultado plausible: que el sistema falle**;
sería publicable y coherente con el trabajo.

### NX-03 · Ampliación del conjunto anotado · D-04

Tres fallos más con las cuatro condiciones y dos ventanas por fallo: entre 12 y 24 casos
nuevos que anotar. El pipeline no cambia. Coste: media jornada de anotación más una ejecución.
Riesgo declarado: los casos nuevos pueden no reproducir el contraste, y eso sería un resultado.

### NX-04 · Brazo con citas generadas · D-09, trabajo futuro

Un brazo en que el modelo de lenguaje produzca sus propias citas, para que la distancia entre
completitud y soporte pueda tomar un valor distinto de cero y la métrica mida lo que pretende.
Coste: medio-alto. Se propone como trabajo futuro, no para esta entrega.

---

## Orden de ejecución si se aprueban

```
RX-00  cabecera de registros
  └─ RX-01  E15 corregido           → cambia textos, registra calibración y procedencia
       └─ RX-02  E13 corregido      → depende de los paquetes de RX-01
  └─ RX-03  medición translingüe    → independiente
  └─ RX-04  barrido                 → solo si D-05 = (b)
  └─ RX-05  réplicas                → solo si D-02 exige sostener un orden
NX-01 y NX-02 juntos, si se aprueban; NX-03 en paralelo con la anotación; NX-04 fuera de esta entrega
```

Ninguna de estas ejecuciones abre el conjunto de test. La evaluación final sobre test sigue
reservada a su fase, con el pre-registro congelado antes (decisión D-11).
