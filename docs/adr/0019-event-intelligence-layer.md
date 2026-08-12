# ADR-0019 — Capa Vehicle Event Intelligence (eventos como unidad formal de análisis)

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 6 · **Docs:** docs/event-intelligence/

## Decisión

1. Se incorpora la capa **Vehicle Event Intelligence** entre normalización y detección:
   fusión de sensores → detección/segmentación de eventos → features de evento → detección
   contextual. Los eventos son entidades de primera clase (VehicleEvent, jerárquicos vía
   parent_event_id: trip/evento/microevento), NUNCA etiquetas decorativas.
2. **Independiente del LLM**: detección por reglas + máquina de estados + procesamiento de
   señal + estadística; ML solo si supera a ese baseline (misma disciplina que ADR-0011).
   El LLM consume eventos, no detecta eventos físicos.
3. **Clases de conocimiento** observed/inferred/estimated + confidence + detection_method +
   detector_version + sensores fuente en TODO evento: un evento inferido jamás se presenta
   como hecho (extiende la regla RAW/INFERRED de ADR-0012).
4. Taxonomía v1 versionada (9 categorías; docs/event-intelligence/02); máquina de estados
   tolerante a pérdidas de bus y estados inesperados; PARKED retrospectivo.
5. Los eventos REFERENCIAN telemetría por session_id+seq_start/seq_end (sin duplicación;
   tablas puente solo si una consulta real lo exige — evaluado eficiente en SQLite con
   índices por sesión/tiempo).
6. **Compatibilidad**: el camino ventana→LOF (F3) queda intacto y coexiste con el camino
   evento→baseline para comparación experimental (window vs event vs both).
7. Retención específica: IMU cruda de alta frecuencia = retención corta (agregados por tick
   + segmentos crudos solo de eventos anómalos = prioridad); metadatos de eventos y
   EventFeatureVector = largo plazo (extiende data-architecture/09).

## Alternativas consideradas

- *Etiquetar ventanas con contexto (sin entidad evento):* barato pero pierde jerarquía,
  duraciones reales y comparabilidad entre eventos; descartado.
- *ML end-to-end para segmentar:* sin ground truth real ni volumen todavía; los baselines
  deterministas son evaluables y explicables. Se re-evalúa con datos (ADR-0011 aplica).

## Consecuencias

Impacto académico positivo: habilita la subpregunta PI.5/H6 (segmentación contextual vs
ventanas) sin cambiar la pregunta principal. Riesgo de alcance controlado por MUST/SHOULD/
COULD (informe F6 §roadmap): MUST solo eventos OBD-only + baseline + experimento.
