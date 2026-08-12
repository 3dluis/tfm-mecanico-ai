# 06 — Loop Engineering y stop conditions

[← Índice](README.md) · Diagrama: [investigation-loop.mmd](diagrams/investigation-loop.mmd) · ADR: [0017](../adr/0017-loop-y-context-engineering.md)

## El ciclo

```
OBJECTIVE → OBSERVE → ANALYZE → PLAN → ACT → VERIFY → CRITIQUE
   → ¿evidencia suficiente? → NO: NEXT ACTION → (loop) | YES: REPORT
```

El runtime decide dinámicamente: necesito otro PID · una ventana mayor · comparar con casos
· consultar documentación · otra prueba · rechazar una hipótesis · generar una nueva.
La re-planificación muta `current_plan` en el estado y queda persistida en AgentRun/AgentStep
(ejemplo canónico del plan del autor: fuel trims → H1/H2/H3 → evidencia insuficiente →
nuevo plan: adquirir MAP/MAF, observar a 2500 rpm, comparar trims, re-verificar).

## Stop conditions (todas configurables; valores v1 del slice)

```
max_iterations        4      max_tool_calls   20
max_execution_time    120 s  max_tool_retries 2
max_hypotheses        5      max_llm_calls    8
minimum_evidence      2 piezas de soporte para la hipótesis top
minimum_confidence    0.6 (PROBABLE) / 0.8 + feedback externo (CONFIRMED)
```

## Resultados válidos (outcome)

`CONFIRMED` (solo con verificación + feedback externo) · `PROBABLE` (SUPPORTED con evidencia
y confianza suficientes) · `INCONCLUSIVE` (evidencia mixta tras agotar el plan) ·
`INSUFFICIENT_DATA` (faltan datos y no se pueden adquirir) · `ESCALATE` (requiere humano/
taller) · `FAILED` (error del runtime). **INCONCLUSIVE e INSUFFICIENT_DATA son resultados
correctos**: el runtime nunca fuerza una respuesta — es un requisito de honestidad
epistemológica, no una carencia.
