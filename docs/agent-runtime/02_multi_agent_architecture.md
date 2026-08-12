# 02 — Arquitectura multiagente

[← Índice](README.md) · Diagrama: [multi-agent.mmd](diagrams/multi-agent.mmd)

## Agentes lógicos vs modelos físicos

Un **agente es un rol lógico**: un nombre, una responsabilidad acotada, un subconjunto del
Tool Registry y (opcionalmente) un acceso a LLM vía ModelRouter. NO hay un modelo por
agente: en RPi 5 (8 GB) el presupuesto realista es UN LLM local compartido + el modelo de
embeddings + los modelos ML ONNX. `Agent Role ≠ LLM instance` (ADR-0015).

| Agente | ¿LLM? | Herramientas principales | Nivel de razonamiento |
|---|---|---|---|
| Supervisor | opcional (v1: política determinista) | — (decide, no ejecuta) | 3 |
| Telemetry | NO | read_pid(s), query_telemetry/session, request_measurement | 1 |
| Anomaly | NO | run_anomaly_model, calculate_feature/statistics, compare_signals | 2 |
| Diagnostic | SÍ | (consume contexto; propone hipótesis estructuradas) | 3 |
| Knowledge | embeddings/léxico | retrieve_document, retrieve_chunks | 3 (recuperación) |
| Recall | embeddings/similitud | search_case_memory, search_learned_patterns | 3 (recuperación) |
| Verification | NO (LLM solo para ELEGIR prueba) | reglas + query_telemetry + run_model | 1-2 |
| Critic | SÍ (criterios estructurados) | — (audita el estado) | 3 |
| Memory | NO | store_case, store_evidence, update_pattern_evidence | 1 |
| Report | SÍ | — (compone desde evidencia) | 3 |

## Modelo de inferencia híbrida (3 niveles)

```
NIVEL 1 Determinista: reglas, cálculos, umbrales, relaciones entre señales
NIVEL 2 ML: detección de anomalías, clustering, reconocimiento de patrones
NIVEL 3 Agéntico/LLM: planificación, hipótesis, selección de herramientas, recuperación, explicación
```

Regla dura: **un nivel superior no invalida silenciosamente a uno inferior.** Si el LLM
discrepa de una regla o de un modelo ML, la discrepancia se registra como evidencia
contradictoria y la resuelve el protocolo (Critic/Verification), nunca una sobrescritura.

## Comunicación

Los agentes NO se llaman entre sí: solo el Supervisor enruta, a través del DiagnosticState
compartido (doc 03). Cada activación de agente = un AgentStep persistido; cada uso de
herramienta = entrada en el historial de ejecución de tools (doc 11).
