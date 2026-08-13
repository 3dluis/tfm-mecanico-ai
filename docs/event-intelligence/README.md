# Vehicle Event Intelligence

**Capa de detección, segmentación y análisis de eventos vehiculares** (F6, ADR-0019…0021):
evoluciona el análisis desde ventanas temporales arbitrarias hacia contextos de conducción
con significado (ralentí, aceleración, arranque en frío…), que se convierten en **unidad
formal de análisis** del sistema — no en etiquetas decorativas.

Nombre: se adopta *Vehicle Event Intelligence* (alternativa evaluada: "Contextual Telemetry
Layer" — descriptiva pero pierde el matiz de detección activa; se mantiene la propuesta).

```
Raw Sensors → Normalization → Sensor Fusion → Event Detection → Event Segmentation
  → Event Features → Contextual Anomaly Detection → Agent Runtime → Memory
```

**Independiente del LLM**: detección por reglas, máquinas de estados, procesamiento de
señales y estadística (ML solo cuando supere a esos baselines). El LLM consume eventos;
jamás detecta eventos físicos.

| Documento | Contenido |
|---|---|
| [01 Overview](01_overview.md) | Motivación, fuentes de datos (OBD/IMU/GPS), principios |
| [02 Taxonomía](02_event_taxonomy.md) | Taxonomía versionada v1; observado/inferido/estimado |
| [03 Máquina de estados](03_vehicle_state_machine.md) | Estados de alto nivel y transiciones |
| [04 Detección de eventos](04_event_detection.md) | Criterios por evento; qué exige IMU; técnicas |
| [05 Sensor fusion](05_sensor_fusion.md) | Fusión multi-frecuencia + sincronización temporal |
| [06 Event features](06_event_features.md) | EventFeatureVector versionado |
| [07 Baselines](07_event_baselines.md) | EventContext, EventBaseline, baseline por vehículo |
| [08 Anomalías contextuales](08_contextual_anomalies.md) | Detección event-aware; anomaly_scope |
| [09 Memoria](09_memory_integration.md) | CaseMemory/LearnedPattern con eventos; EventSequence |
| [10 Agent Runtime](10_agent_runtime_integration.md) | Event Detection Service + tools |
| [11 Diseño experimental](11_experimental_design.md) | Métricas de eventos (P/R/F1, IoU temporal); ventana vs evento; subpregunta |

Diagramas: [sensor-pipeline](diagrams/sensor-pipeline.mmd) · [event-hierarchy](diagrams/event-hierarchy.mmd) ·
[contextual-anomaly](diagrams/contextual-anomaly.mmd) · [event-memory](diagrams/event-memory.mmd)

Cruces: [data-architecture](../data-architecture/README.md) (modelo de datos; VehicleEvent
y compañía se integran allí) ·
[VehicleTelemetrySnapshot](../data-architecture/11_vehicle_telemetry_snapshot.md) (F11: cada
snapshot lleva `primary_event_id`/`primary_event_type` para consulta rápida y se enlaza N:M
con TODOS los eventos simultáneos vía `SnapshotEventLink`, **sin duplicar snapshots**; sigue
valiendo la regla de que los eventos REFERENCIAN telemetría por `seq`, nunca la copian) ·
[agent-runtime](../agent-runtime/README.md) (tools de eventos)
· [deteccion-dual](../diagrams/deteccion-dual.mmd) (F10: papel COMPLEMENTARIO junto al
LOF primario; fusión OR auditable configurable)
· [models](../models/README.md) (F7: el detector `ed:1` y `event-baseline-z` son modelos ML
registrados con card y ciclo de vida; comparación rule-vs-ML prevista en models/02 §3)
· [PostgreSQL + pgvector en el edge](../data-architecture/13_postgresql_pgvector_edge.md)
(F12: los eventos viven en el schema `events`; los snapshots se enlazan N:M desde
`telemetry`; el `EventRepository` es la única frontera con la base — el LLM nunca consulta SQL)
· ADRs [0019](../adr/0019-event-intelligence-layer.md), [0020](../adr/0020-incorporacion-imu.md),
[0021](../adr/0021-deteccion-anomalias-contextual.md), [0030](../adr/0030-postgresql-pgvector-edge.md).

**Regla fundamental:** la telemetría original nunca se pierde y un evento inferido nunca se
confunde con un hecho observado. Cadena trazable (ida y vuelta):
`Raw → Normalized → VehicleEvent → EventFeatureVector → ModelInference → DetectedAnomaly →
DiagnosticCase → LearnedPattern`.
