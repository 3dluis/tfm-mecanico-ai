# R2 — smoke y benchmark del modelo de lenguaje local (instrumental, EXPLORATORIO)

**27 de agosto de 2026 · macOS 26.5.2 arm64 · ollama 0.33.0 · Qwen2.5-3B-Instruct Q4_K_M**

R2 es **instrumental**: fija el parámetro diferido **D1** (modelo de lenguaje) del
pre-registro. No contrasta ninguna hipótesis y su resultado no se combina con evidencia
confirmatoria (`pre-registro-v1.md` §11).

Artefactos: `ai-models/experiments/r2/{llm-smoke,llm-benchmark,environment,model-runtime}.json`.

---

## 1. Smoke profundo — **superado**

| Criterio | Medido |
|---|---|
| Conformidad de esquema | **5/5** |
| Respuesta en español | **5/5** |
| Velocidad (mediana) | **76,9 tokens/s** |
| Latencia (mediana) | **1,47 s** |
| Sonda de contexto 2048 / 4096 / 8192 | esquema correcto en las tres; 75,4 → 70,9 → 65,5 t/s |

El modelo produce JSON válido de forma sistemática, responde en el idioma pedido y opera muy
por debajo del límite de 120 s del runtime. **Como runtime, es viable.**

## 2. Benchmark `agent-diagnostics` v1 — resultado **NO INTERPRETABLE**

Ejecutado sobre los 6 casos congelados de `cases_v1.yaml` con el context builder `cb:1`:

```
structured_output_compliance  6/6
top1                          0/6
top3                          0/6
outcome_ok                    3/6
unsupported_certainty_errors  2
```

El `0/6` **no mide capacidad diagnóstica**. Es un defecto del instrumento.

### 2.1 El defecto

`SCHEMA_HINT` de `cb:1` declara `"failure_mode": str` y **no comunica el vocabulario
controlado**. El corrector, en cambio, compara por igualdad exacta contra los identificadores
de `acceptable_hypotheses` (`vacuum_leak`, `maf_drift`, …). El modelo respondió etiquetas en
español —«Fuga de vacío», «Deriva de MAF»—, semánticamente correctas y formalmente no
coincidentes. La métrica midió el formato de la etiqueta, no el acierto.

Es el mismo patrón que AUDIT-DATA-001 estableció como regla: antes de atribuir un resultado
al modelo, hay que descartar que lo explique el instrumento.

### 2.2 Sonda exploratoria con vocabulario declarado

Se repitió el benchmark cambiando **una sola cosa**: declarar en el prompt los identificadores
admitidos. Todo lo demás idéntico. No sustituye a R2 ni escribe sus artefactos.

| | top-1 | top-3 | outcome_ok | certeza no sustentada |
|---|---|---|---|---|
| R2 con `cb:1` | 0/6 | 0/6 | 3/6 | 2 |
| Sonda con vocabulario | **3/6** | **4/6** | 3/6 | 1 |

Confirma que el `0/6` era del instrumento.

### 2.3 Pero el 3/6 tampoco sostiene una decisión

El modelo situó **`vacuum_leak` en primera posición en los seis casos**, incluidos aquel cuyo
ground truth es «ningún fallo» y el de anomalía relacional. Un control trivial que responda
siempre lo mismo obtiene exactamente la misma puntuación:

| Generador | top-1 | top-3 |
|---|---|---|
| Control constante `vacuum_leak` | **3/6** | 3/6 |
| Control constante `maf_drift` | **3/6** | 3/6 |
| Modelo con vocabulario declarado | **3/6** | 4/6 |

**El modelo es indistinguible de un control constante en este banco.** Con n = 6 y unas
`acceptable_hypotheses` que admiten `vacuum_leak` en tres casos, el banco carece de poder
discriminante para separar capacidad de anclaje.

Hipótesis plausible del anclaje, no comprobada: el fragmento de corpus incluido en el prompt
(`CORPUS_SNIPPET`) describe la fuga de vacío en primer lugar y con más detalle que las demás.

## 3. Conclusión: **D1 NO queda fijado**

- **Viabilidad como runtime: demostrada.** Formato, idioma, velocidad y latencia cumplen el
  presupuesto edge. Esta parte de R2 sí es concluyente.
- **Capacidad diagnóstica: indeterminada.** No se ha medido, ni a favor ni en contra.

Fijar D1 sobre este benchmark sería fijarlo sobre una medición que no discrimina. Se declara
**NO CONCLUYENTE** en lugar de promoverse a decisión, conforme a la regla de que la afirmación
nunca supera la evidencia.

## 4. Qué haría falta para decidir D1

1. **Context builder `cb:2`** que declare el vocabulario controlado. Es un cambio de
   instrumento y por tanto lleva versión propia: los resultados con `cb:1` y `cb:2` no son
   comparables entre sí. Requiere aprobación del autor.
2. **Evaluar sobre `cases_v2`** (40 casos, ya congelados) en lugar de `cases_v1` (6). Incluye
   8 casos sin fallo y 6 de evidencia insuficiente, que son precisamente los que penalizan el
   anclaje en una respuesta constante.
3. **Incluir el control constante como brazo declarado.** Si un generador que siempre responde
   lo mismo iguala al modelo, el resultado del modelo no es informativo — y eso debe verse en
   la tabla, no descubrirse después.
4. Comprobar si el anclaje persiste al equilibrar el fragmento de corpus del prompt.

## 5. Qué NO se ha hecho

- No se ha modificado `cases_v1.yaml`, declarado inmutable.
- No se ha modificado `tools/bench_agent_diagnostics.py`: `cb:1` queda como quedó, y sus
  artefactos son los de la ejecución real.
- No se ha comparado con otros modelos: D1b (modelo juez) sigue abierto.
