# 05 — Diagnósticos y evidencias

[← Índice](README.md) · Diagrama: [diagnostic-memory-flow.mmd](diagrams/diagnostic-memory-flow.mmd)

## Estructura

**DiagnosticCase** (unidad de trabajo, disparada por anomalías y/o DTCs) →
**DiagnosticHypothesis** (varias por caso, en competencia) → **DiagnosticEvidence**
(varias por hipótesis, a favor Y en contra). La explicación final del caso es una
*proyección* de estas estructuras (nodo `report`), nunca la fuente de verdad.

## Hipótesis

Campos clave: `rank` (1 = ganadora tras verify), `confidence` (ajustada por la evidencia),
`suspected_component`, `failure_mode` (vocabulario compartido con el catálogo de obd-lab y
las reglas de verify), `status`:

`PROPOSED → SUPPORTED | CONTRADICTED | INCONCLUSIVE` (los fija `verify`, determinista)
`→ CONFIRMED | REJECTED` (solo con feedback externo — jamás los fija el agente solo).

## Evidencias

Cada evidencia es una **afirmación verificable** (`statement`, p. ej.
"total_trim_mean=+9.4% (esperado >+4% con fuga de vacío)") con: `kind` (telemetry, dtc,
document, case, pattern, feedback, maintenance), `role` (supports/contradicts/neutral),
`strength`, `produced_by` (nodo) y `reference_id` al objeto citado. Las contradicciones se
registran con el mismo rigor que los apoyos: son las que protegen contra la alucinación.

## Feedback e intervenciones

`DiagnosticFeedback` captura la verdad externa (ground truth del simulador/dataset,
validación humana/mecánico, resultado de reparación) con veredicto
correct/partially_correct/incorrect/unknown — el insumo de la evaluación H3.
`MaintenanceEvent` registra intervenciones para estudiar la secuencia
anomalía→diagnóstico→intervención→cambio en telemetría→resolución, que se convertirá en
evidencia fuerte (kind=maintenance) para confirmar o rechazar hipótesis.
