# Experimentos — índice

Registro navegable de los experimentos del TFM. Cada experimento tiene: config
declarativa (`ai-models/configs/`), runner reproducible (`ai-models/experiments/`),
artefactos (CSV/JSON commiteados), registro formal (`ai-models/registry/experiments/` +
evaluaciones) e informe de comparación (`docs/models/comparisons/`). Protocolo general:
[docs/models/07](../models/07_evaluation_protocol.md); reproducibilidad:
[docs/models/13](../models/13_reproducibility.md).

| Experimento | Pregunta | Estado | Informe | Decisión |
|---|---|---|---|---|
| **EXP-ANOM-001** (E1, F3) | ¿Qué baseline no supervisado equilibra mejor detección desconocida y falsas alarmas? | cerrado | [anomaly_detectors_v1](../models/comparisons/anomaly_detectors_v1.md) | LOF k=10 por defecto; OC-SVM 2º; z-score/IForest REJECTED |
| **EXP-ANOM-002** (R1+E1, F8) | ¿La segmentación por eventos mejora la detección frente a ventanas arbitrarias? (PI.5/H6) | cerrado (v1) | [anomaly_window_vs_event_v1](../models/comparisons/anomaly_window_vs_event_v1.md) | LOF sigue por defecto; eventos = señal complementaria (no sustituto); combinación EXPERIMENTAL |
| EXP-ANOM-003 (propuesto) | ¿Se corrige el FPR de eventos con más train normal por contexto + métrica por-evento? ¿Global vs por-vehículo? | pendiente de aprobación | — | — |
| R2 / LLM smoke + benchmark | ¿Qué LLM local equilibra calidad diagnóstica y recursos edge? | pendiente (requiere llm-smoke en el Mac) | benchmarks/agent-diagnostics | — |
| A0–A6 (agentes) + H3/H5 | ¿Qué componentes de la arquitectura agéntica aportan? | pospuesto hasta cerrar la representación de entrada (decisión F8) | agent-runtime/12 | — |

Reglas permanentes: held-out intocable (RI1) · umbrales solo con train/validation ·
resultados negativos se documentan igual que los positivos · ningún resultado de la
memoria proviene solo de un notebook.
