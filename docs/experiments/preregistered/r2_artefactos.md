# R2 — Artefactos y esquema (harness CONGELADO en freeze-v1)

El piloto R2 (Qwen2.5-3B-Instruct Q4_K_M) produce **4 artefactos** en
`ai-models/experiments/r2/`, suficientes para reconstruir el experimento. Al recibirlos,
los resultados se importan al registro **sin recalcular ni reinterpretar** (generando
ModelEvaluation, HardwareValidation, Model Card EXPERIMENTAL, comparación
`llm_qwen25_3b_pilot_v1.md` y actualización del registry). El harness
(`tools/llm_smoke_deep.py`, `tools/bench_agent_diagnostics.py`) y el benchmark
(`cases_v1.yaml`, INMUTABLE) están congelados con sha256 en `arms-freeze-v1.json`.

## llm-smoke.json (producido por `make llm-smoke-deep`)

```
model · context_builder_version (cb:1) · measured_at · host
artifact_size_bytes · load_plus_first_gen_s · ram_bytes · ttft_s
runs[] (latency_s, tokens_per_s, prompt_tokens, schema_ok, spanish_ok, confianza)
schema_compliance "N/5" · spanish_compliance "N/5"
tokens_per_s_median · latency_s_median
context_probe {2048|4096|8192 → run}
```

Criterios de paso del smoke (previos a ejecutar; si falla alguno → mini-comparación de
2–3 LLM antes de integrar): carga sin error · schema_compliance ≥ 4/5 ·
spanish_compliance ≥ 4/5 · RAM ≤ 3.5 GB · TTFT ≤ 5 s (Mac; en RPi se re-medirá) ·
tokens/s ≥ 8 (Mac) · estabilidad (sin errores en 5+3 generaciones).

## llm-benchmark.json (producido por `make llm-bench`, solo si el smoke pasa)

```
model · benchmark ("agent-diagnostics v1 (INMUTABLE)") · context_builder_version
structured_output_compliance · top1 · top3 · outcome_ok
unsupported_certainty_errors (nº — cada uno es un ERROR explícito)
results[] por caso: case_id, latency_s, tokens_per_s, prompt_tokens, structured_ok,
  top1_ok, top3_ok, ranking, outcome, outcome_ok, unsupported_certainty,
  evidence_coverage, informacion_faltante, manual_review{forbidden_conclusions,
  model_mechanisms}
```

La revisión de `manual_review` (conclusiones prohibidas) es humana y se documenta en el
informe piloto.

## environment.json

`platform · machine · python · ollama_version · measured_at`

## model-runtime.json

`model (tag exacto) · details (familia, parámetros, cuantización según /api/show) ·
parameters_head · license_head`

## Ejecución en el Mac

```bash
ollama pull qwen2.5:3b-instruct-q4_K_M
make llm-smoke-deep      # → llm-smoke.json + environment.json + model-runtime.json
make llm-bench           # → llm-benchmark.json (solo si el smoke pasa)
```

Regla: si Ollama no puede ejecutarse en un entorno, NO se generan resultados sintéticos
— simplemente no hay artefactos.
