# 11 — Observabilidad del runtime

[← Índice](README.md)

Todo lo necesario para la evaluación científica se registra en el modelo de datos v2
existente (sin tablas nuevas):

| Métrica | Dónde |
|---|---|
| Duración del diagnóstico | AgentRun.latency_ms |
| Iteraciones / agentes usados | AgentStep (node, seq) + DiagnosticState.iteration en outputs |
| Tool calls (cuáles, cuántas, errores, duración) | AgentStep.tools_used + metrics |
| LLM calls, tokens, modelos | AgentRun.tokens_in/out, llm_model, config (mapa router) |
| Memoria/documentos recuperados (y usados) | RetrievalEvent (retrieved vs used_in_hypothesis_ids) |
| Hipótesis generadas/rechazadas | HypothesisRow por caso (status) |
| Resultado y confianza | AgentRun.result_status + DiagnosticCase.severity + outcome en outputs del último step |
| Errores | AgentStep.status=error + error |
| CPU/RAM (aprox) | metrics del step (ru_maxrss; perfil edge con límites Docker) |
| Energía | fuera de alcance en emulación; en RPi física vía medidor externo (COULD) |

Regla: si una métrica del diseño experimental (doc 12) no puede computarse SOLO desde la
base de datos, falta instrumentación — se corrige antes de ejecutar experimentos.
