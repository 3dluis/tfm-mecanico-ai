# 08 — Detección contextual de anomalías

[← Índice](README.md) · Diagrama: [contextual-anomaly.mmd](diagrams/contextual-anomaly.mmd)

## Dos caminos coexistentes (requisito 46)

```
(F3, intacto)   TelemetryWindow → FeatureVector → LOF → DetectedAnomaly(scope=WINDOW)
(F6, nuevo)     VehicleEvent → EventFeatureVector → EventBaseline comparable
                    → detector contextual → DetectedAnomaly(scope=EVENT)
```

Detector contextual v1 (determinista y explicable): z-score robusto por feature contra la
distribución del baseline del contexto (|z|>3 en ≥2 features → anómalo) + distancia global
al centroide. Requiere `sample_count ≥ n_min` (v1: 10); por debajo, el evento NO se evalúa
contextualmente (se registra "sin baseline suficiente" — jamás se fuerza). Ejemplo objetivo:
aceleración #927 con MAF −18 % vs sus 47 aceleraciones comparables, trims compensando, sin
DTC → CONTEXTUAL_ANOMALY con las features desviadas como evidencia.

## Extensión de DetectedAnomaly (compatible con F3)

Nuevos campos opcionales: `event_id`, `baseline_id`, `anomaly_scope ∈ {POINT, WINDOW,
EVENT, SESSION, CROSS_EVENT}` (default WINDOW = comportamiento F3); `window_id` pasa a
opcional (una anomalía de evento no tiene ventana fija). Los consumidores existentes no
cambian; el agente gana contexto: "la anomalía ocurrió DURANTE una aceleración, comparada
con 47 equivalentes".
