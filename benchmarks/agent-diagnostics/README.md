# Benchmark interno — agent-diagnostics

Suite reproducible para evaluar LLMs (y arquitecturas A0–A6) en diagnóstico vehicular
**sin impresión subjetiva** (docs/models/03 §5, docs/models/07).

## Principios

- El **ground truth proviene del catálogo de fallos de obd-lab** (el fallo inyectado ES
  la verdad) y de las firmas documentadas en el corpus — **nunca de las respuestas de
  otro LLM**.
- Cada caso es regenerable (scenario_id + seed) y declara: contexto de entrada, verdad,
  evidencia esperada, hipótesis aceptables y conclusiones prohibidas (no soportadas).
- Un mismo caso sirve para todos los brazos (heurístico, LLM-X, LLM-Y, A2/A3/A6):
  la comparación es válida porque el caso no cambia.

## Formato de caso (`cases_v1.yaml`)

```yaml
- case_id: BENCH-001
  scenario: {scenario_id: ..., seed: ..., fault: ..., profile: ...}
  input_context: qué recibe el agente (anomalía + ventana; nunca el nombre del fallo)
  ground_truth: {failure_mode: ..., component: ...}
  expected_evidence: [afirmaciones verificables que un buen diagnóstico debe citar]
  acceptable_hypotheses: [modos de fallo aceptables en top-k]
  forbidden_conclusions: [afirmaciones sin soporte que puntúan como fabricación]
  expected_outcome: probable | inconclusive | insufficient_data
```

`expected_outcome: inconclusive` en casos deliberadamente ambiguos: la disposición a NO
concluir es métrica de seguridad, no un fallo.

## Métricas (definidas en docs/models/03 §5)

Diagnostic quality (top-1/top-k, ranking) · Grounding (cobertura de evidencia,
afirmaciones sin soporte) · Agent behavior (herramientas, structured output, stop
conditions) · Safety (fabricación, certeza injustificada, INCONCLUSIVE cuando toca,
intentos de herramientas restringidas) · Edge performance (latencia, RAM, tokens/s, TTFT).

## Estado

`cases_v1.yaml` contiene los primeros 6 casos (2 vacuum, 1 maf_drift, 1 held-out, 1
normal-trampa, 1 ambiguo). El runner se implementará en R2 junto al primer LLM real; los
casos se definen ANTES de ver salidas de ningún modelo (pre-registro).
