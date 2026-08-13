# Experimentos — índice

**Estructura (F10):** [`exploratory/`](exploratory/) (clasificaciones e inventarios de
decisiones de los pilotos) · [`preregistered/`](preregistered/) (protocolos CONGELADOS
antes de ejecutar — no se modifican retroactivamente; cambios = versión nueva) ·
[`results/`](results/) (resultados confirmatorios + desviaciones). Regla F10: solo los
experimentos con protocolo congelado ANTES de ejecutar cuentan como evidencia
confirmatoria; el resto es exploratorio (transparencia metodológica).

Registro navegable de los experimentos del TFM. Cada experimento tiene: config
declarativa (`ai-models/configs/`), runner reproducible (`ai-models/experiments/`),
artefactos (CSV/JSON commiteados), registro formal (`ai-models/registry/experiments/` +
evaluaciones) e informe de comparación (`docs/models/comparisons/`). Protocolo general:
[docs/models/07](../models/07_evaluation_protocol.md); reproducibilidad:
[docs/models/13](../models/13_reproducibility.md).

| Experimento | Pregunta | Estado | Informe | Decisión |
|---|---|---|---|---|
| **EXP-ANOM-001** (E1, F3) | ¿Qué baseline no supervisado equilibra mejor detección desconocida y falsas alarmas? | **EXPLORATORY** | [anomaly_detectors_v1](../models/comparisons/anomaly_detectors_v1.md) | LOF k=10 por defecto; OC-SVM 2º; z-score/IForest REJECTED |
| **EXP-ANOM-002** (R1+E1, F8) | ¿La segmentación por eventos mejora la detección frente a ventanas arbitrarias? (H-EVT) | **EXPLORATORY** | [anomaly_window_vs_event_v1](../models/comparisons/anomaly_window_vs_event_v1.md) | LOF sigue por defecto; eventos = señal complementaria (no sustituto); combinación EXPERIMENTAL |
| **EXP-ANOM-003** (F9) | ¿Causa del FPR de eventos? (datos vs scoring vs contextos vs contabilidad) | **EXPLORATORY** | [event_fpr_refinement_v1](../models/comparisons/event_fpr_refinement_v1.md) | Causa: insuficiencia de normalidad. event-baseline-z→0.2.0 (FPR 0.008); scoring robusto RECHAZADO; LOF-v2 NO adoptado; recomendada AM-WE-d (FPR 0.071) |
| **PROTO-CONF-001 / EXP-ANOM-004** | Confirmatorio H-EVT: ¿la combinación mejora manteniendo FPR? | **PRE-REGISTRADO, no ejecutado** | [preregistered/PROTO-CONF-001](preregistered/PROTO-CONF-001.md) | brazos congelados (arms-freeze-v1); datos confirmatorios ocultos |
| R2 / LLM smoke + benchmark | ¿Qué LLM local equilibra calidad diagnóstica y recursos edge? | pendiente (requiere llm-smoke en el Mac) | benchmarks/agent-diagnostics | — |
| A0–A6 (agentes) + H3/H5 | ¿Qué componentes de la arquitectura agéntica aportan? | pospuesto hasta cerrar la representación de entrada (decisión F8) | agent-runtime/12 | — |

Reglas permanentes: held-out intocable (RI1) · umbrales solo con train/validation ·
resultados negativos se documentan igual que los positivos · ningún resultado de la
memoria proviene solo de un notebook.
