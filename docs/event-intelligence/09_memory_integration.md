# 09 — Integración con memoria episódica y evolutiva

[← Índice](README.md) · Diagrama: [event-memory.mmd](diagrams/event-memory.mmd)

- **CaseMemory** gana `related_event_ids` y las firmas de evento relevantes dentro de
  `symptom_signature` — recuperación de casos POR COMPORTAMIENTO (aceleraciones anómalas
  parecidas), no solo por texto/DTC.
- **LearnedPattern** gana `event_types` (un patrón puede asociarse a uno o varios tipos de
  evento) y su `telemetry_signature` puede expresarse en features de evento. Ejemplo
  objetivo: contexto ACCELERATION 40-80 warm; patrón MAF↓ + STFT compensa + relación RPM
  cambia → posible problema de admisión.
- **EventSequence (diseñado, COULD):** para patrones temporales entre eventos
  (aceleración anómala → minutos → ralentí inestable → DTC posterior). Se modela con las
  relaciones existentes PRECEDES/FOLLOWS/CO_OCCURS_WITH (PatternRelation generalizada a
  eventos) — sin minería compleja de secuencias hasta que un caso la exija.
- Los **EventBaseline** son la tercera pata de la memoria evolutiva: normalidad aprendida
  por vehículo y contexto (doc 07), con la misma disciplina de versionado/provenance.
