# 02 — Modelos ML

## 1. Familias y estado actual

Inventario completo con estados en [14 §3](14_model_selection.md). Resultados reales de
F3 en [comparisons/anomaly_detectors_v1.md](comparisons/anomaly_detectors_v1.md):
**LOF k=10 seleccionado**; OC-SVM segundo paquete; z-score robusto e Isolation Forest
**rechazados con resultado negativo documentado** (fracaso ante normalidad multimodal —
hallazgo citable). Autoencoders solo si superan a LOF en held-out con FPR ≤ acordado.

## 2. Qué documenta una ML Model Card (además de la plantilla común)

Variables utilizadas, ventana temporal, feature vector (`feature_schema_version`),
estrategia de normalización, tratamiento de missing values, método de entrenamiento,
semilla, umbral y CÓMO se decidió (protocolo ADR-0011: cuantil de train-normal al 1% FPR),
calibración, semántica del score, métricas por escenario, métricas held-out y FPR.

**Métricas mínimas para detección de anomalías:**

```
precision · recall · F1 · FPR · episode recall · held-out episode recall · latency
```

AUROC/AUPRC cuando aplique, pero **nunca depender solo de métricas point-wise**
(el protocolo por episodios de ADR-0011 es el principal; sin point-adjustment).

## 3. Modelos de detección de eventos (Event Intelligence)

Cada detector registra su método:

```
RULE | STATE_MACHINE | STATISTICAL | ML | HYBRID
```

Detectores actuales y previstos (taxonomía v1, docs/event-intelligence/02):

| Evento | Detector actual | Método | Estado |
|---|---|---|---|
| ENGINE_START / ENGINE_STOP | `ed:1` reglas RPM | RULE | validado (slice F6) |
| IDLE / ACCELERATION / DECELERATION / CONSTANT_SPEED | `ed:1` máquina de estados con histéresis | STATE_MACHINE | validado (slice F6) |
| TURNS / HARD_TURN | requiere IMU (ADR-0020) | RULE/STATISTICAL | planificado |
| HARD_BRAKING | derivada de SPEED (+IMU si llega) | RULE | planificado |
| GEAR_SHIFT_INFERRED | relación RPM/velocidad | STATISTICAL | planificado |

Regla experimental: cualquier detector ML de eventos debe compararse contra el baseline
de reglas (`rule baseline vs ML approach`) con las métricas de eventos
(P/R/F1 por tipo con IoU temporal, error de onset/fin — event-intelligence/11). El
detector `ed:1` ES el baseline a batir; card en [model-cards/ml/event-detector.md](model-cards/ml/event-detector.md).

## 4. Modelos de anomalía contextual

Cadena (ADR-0021): `VehicleEvent → EventFeatureVector → EventBaseline → anomalía
contextual (anomaly_scope=EVENT)`. Estos modelos se documentan **separados** de los
detectores por ventana (LOF/OC-SVM sobre ventanas de 60 s), porque el experimento
central ventana-vs-evento (`anomaly_mode`, PI.5/H6) exige poder atribuir resultados a
cada vía. Modelo actual: `event-baseline-z` (z robusto contra baseline por contexto;
card en [model-cards/ml/event-baseline-z.md](model-cards/ml/event-baseline-z.md)).

## 5. Interpretabilidad

Siempre que el modelo lo permita se registran con la inferencia: importancia de
features / contribución por PID (`involved_pids`), vecinos más cercanos y distancias
(LOF), factores de anomalía, distancia al centroide (baselines contextuales) o error de
reconstrucción (si algún autoencoder entra). El Agent Runtime usa esa información como
**evidencia** (`DiagnosticEvidence`): el LLM no inventa por qué el modelo detectó una
anomalía — narra sobre salidas del modelo, telemetría, RAG, casos y verificación
determinista ([03 §7](03_llm_models.md)).
