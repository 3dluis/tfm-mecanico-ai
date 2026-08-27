# 09 — Integración con memoria episódica y evolutiva

> **⚠ Fuera del alcance experimental del TFM (ADR-0036, 27-ago-2026).** Tras la
> acotación de la pregunta de investigación a explicación diagnóstica trazable y
> abstención ante evidencia insuficiente, la integración de eventos con la memoria no forma parte de la validación
> experimental de este trabajo. **El diseño y el código se conservan** y siguen siendo
> correctos; simplemente no se evalúan. Catálogo completo y justificación:
> [`docs/alineacion_v4/05_fuera_de_alcance.md`](../alineacion_v4/05_fuera_de_alcance.md).

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
