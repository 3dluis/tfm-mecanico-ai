# ADR-0021 — Detección contextual de anomalías y baselines por vehículo

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 6

## Decisión

1. **EventContext/context_signature**: discretización estable (tipo|rango velocidad|estado
   térmico|carga|duración) que define qué eventos son comparables entre sí.
2. **EventBaseline**: distribución acumulada (online) de EventFeatureVectors por vehículo ×
   contexto, con sample_count, percentiles, versión y confidence — la normalidad aprendida
   específica del vehículo (requisito 19). Formato físico v1: JSON por feature (re-evaluable).
3. **Detector contextual v1 determinista**: z-robusto por feature vs baseline + distancia a
   centroide; exige sample_count mínimo; si no hay baseline suficiente NO evalúa (honestidad).
4. **DetectedAnomaly extendida sin romper F3**: `anomaly_scope` (POINT/WINDOW/EVENT/SESSION/
   CROSS_EVENT, default WINDOW), `event_id`/`baseline_id` opcionales, `window_id` pasa a
   opcional. Consumidores existentes intactos.
5. **Experimento window-vs-event** integrado al diseño A0–A6 como dimensión `anomaly_mode`
   (window|event|both), con métricas de eventos propias (P/R/F1 por solape + IoU temporal +
   errores de onset/fin/duración + calibración de confidence para inferidos).
6. CaseMemory += related_event_ids; LearnedPattern += event_types (ambos aditivos).

## Consecuencias

La memoria episódica se vuelve recuperable por comportamiento; la subpregunta PI.5/H6 es
medible con la infraestructura existente; el ground truth de eventos lo produce obd-lab (el
detector nunca lo ve en inferencia — misma disciplina held-out de ADR-0011).
