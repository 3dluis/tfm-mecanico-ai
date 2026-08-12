# 03 — Modelos LLM

## 1. Funciones y límites

Los LLM cubren funciones agénticas: planificación, triage, generación de hipótesis,
selección de herramientas, interpretación de evidencia, crítica, explicación y reporte.
**Nunca** detección matemática de anomalías (ADR-0009) ni detección de eventos
(ADR-0019). Todo diagnóstico funciona también sin LLM (HeuristicHypothesizer): el brazo
sin-LLM es control experimental permanente.

## 2. Estrategia de adaptación (ADR-0023)

Escalera de [01 §3](01_model_strategy.md): pretrained → quantization → prompt →
context → RAG → tools → LoRA/QLoRA posible → fine-tuning solo con evidencia. **No se
entrena un foundation model desde cero.** Fine-tuning requiere demostrar antes, con el
benchmark interno (§5), que prompting+RAG+contexto+memoria+structured output no bastan.

## 3. Candidatos (sin decisión definitiva todavía)

Ningún LLM está fijado como definitivo. Conjunto inicial razonable para edge (~8 GB RAM
compartida) y desarrollo, pendiente de `make llm-smoke` en el Mac y del benchmark:

| Familia | Tamaños de interés | Por qué candidato |
|---|---|---|
| Qwen 2.5 / 3 | 1.5B–7B | tool-use y JSON sólidos en tamaños pequeños; multilingüe (ES) |
| Llama 3.2 | 1B–3B | ecosistema GGUF maduro; buen ratio calidad/RAM |
| Gemma 2/3 | 2B–4B | fuerte en instrucciones; licencia a revisar |
| Phi (3.5/4-mini) | ~3.8B | razonamiento compacto; validar ES y tool-use |

Cuantización objetivo inicial Q4_K_M (GGUF, runtime Ollama/llama.cpp). La selección usa
la función multicriterio: `calidad + RAM + latencia + tool use + structured output +
contexto + viabilidad edge` — **no** el número de parámetros. Todo descarte se documenta
con motivo (card con status REJECTED en el registro).

## 4. LLM Model Card (campos adicionales a la plantilla)

`provider/source · architecture · parameter_count · quantization ·
quantization_format · context_window · prompt_template_version · system_prompt_version ·
structured_output_support · tool_calling_support · temperature/top_p/max_tokens ·
runtime + runtime_version · memory_usage · disk_size · tokens_per_second ·
time_to_first_token · tested_context_size · languages` — indicando siempre si se evalúa
el modelo original, cuantizado, LoRA, QLoRA o fine-tuned.

## 5. Benchmark interno de Mecánico IA

Los LLM no se evalúan por impresión subjetiva. Suite reproducible en
[`benchmarks/agent-diagnostics/`](../../benchmarks/agent-diagnostics/README.md): casos
con contexto de entrada, ground truth (del catálogo de fallos de obd-lab, NUNCA de las
respuestas de otro LLM), evidencia esperada, hipótesis aceptables y conclusiones no
soportadas prohibidas. Dimensiones mínimas:

- **Diagnostic quality:** top-1/top-k diagnosis, ranking de hipótesis, identificación
  correcta de componente/modo de fallo.
- **Grounding:** cobertura de evidencia, afirmaciones sin soporte, uso de la
  documentación recuperada, corrección de citas cuando aplique.
- **Agent behavior:** selección de herramientas, llamadas innecesarias, recuperación
  ante fallos, cumplimiento de structured output y de stop conditions.
- **Safety:** tasa de fabricación, certeza injustificada, disposición a devolver
  INCONCLUSIVE, intentos de usar herramientas restringidas.
- **Edge performance:** latencia, RAM, CPU, tamaño en disco, tokens/s, time-to-first-token,
  impacto térmico/recursos cuando pueda medirse.

## 6. ModelRouter y capacidades

El registro declara `capabilities` por modelo (`TRIAGE, HYPOTHESIS_GENERATION, CRITIQUE,
REPORTING, TOOL_SELECTION, EMBEDDINGS, ANOMALY_DETECTION, EVENT_DETECTION`). El Agent
Runtime selecciona por capacidad (ModelRouter conceptual de F5, agent-runtime/07). El
routing sofisticado (varios LLM simultáneos) NO se implementa sin necesidad demostrada.

## 7. Provenance de inferencia LLM (auditable, sin chain-of-thought)

Cada llamada relevante del runtime registra: `model_id · model_version · quantization ·
prompt_version · context_builder_version · tool_schema_version · parámetros de
generación`. NO se almacena chain-of-thought (invariante F4): solo lo necesario para
auditoría y reproducibilidad. Diferencia explicación de modelo vs narrativa LLM: la
narrativa debe estar respaldada por salidas de modelos, telemetría, RAG, casos y
verificación determinista; lo no respaldado se etiqueta o se elimina (report labels
OBSERVADO/INFERIDO/PROBABLE/NO CONFIRMADO de F5).
