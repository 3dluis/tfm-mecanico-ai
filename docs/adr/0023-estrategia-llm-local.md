# ADR-0023 — Estrategia LLM: local cuantizado, escalera de adaptación, benchmark propio

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 7

## Decisión

1. **NO se entrena un foundation model desde cero** (explícito). Escalera de adaptación:
   pretrained → quantization → prompt → context → RAG → tools → LoRA/QLoRA posible →
   fine-tuning **solo con evidencia** de que los peldaños anteriores no bastan
   (demostrada con el benchmark interno). No se entrena un LLM para engordar el TFM.
2. **LLM local cuantizado** (GGUF, Q4_K_M de referencia; runtime Ollama/llama.cpp) como
   vía por defecto para el edge — coherente con edge-first (ADR-0003) y los 8 GB de RPi 5.
3. **Ningún LLM fijado como definitivo**: conjunto de candidatos (Qwen 2.5/3 1.5–7B,
   Llama 3.2 1–3B, Gemma 2/3 2–4B, Phi 3.5/4-mini) evaluados con la función
   multicriterio calidad+RAM+latencia+tool use+structured output+contexto+viabilidad
   edge; jamás por nº de parámetros. Descartes documentados con motivo.
4. **Benchmark interno pre-registrado** (`benchmarks/agent-diagnostics/`): ground truth
   del catálogo de fallos (nunca de otro LLM); 5 dimensiones (calidad, grounding,
   comportamiento agéntico, seguridad, recursos edge); casos definidos ANTES de evaluar.
5. **Provenance de inferencia LLM** sin chain-of-thought: model_id/version/quantization/
   prompt_version/context_builder_version/tool_schema_version/parámetros de generación.
6. **Capacidades en el registro** para el ModelRouter (routing sofisticado pospuesto).

## Alternativas descartadas

- **API cloud (GPT/Claude/Gemini)** como motor principal: rompe el requisito edge/offline
  y la reproducibilidad del experimento; admisible solo como referencia comparativa
  claramente etiquetada.
- **Fine-tuning inmediato**: sin benchmark previo sería complejidad sin evidencia,
  y consumiría el cronograma de septiembre.
- **Fijar qwen2.5:3b ya** (venía como candidato desde F3): contradiría la selección
  multicriterio; queda como PRIMER candidato a evaluar, no como decisión.
