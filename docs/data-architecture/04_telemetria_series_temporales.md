# 04 — Telemetría y series temporales

[← Índice](README.md) · Diagrama: [telemetry-flow.mmd](diagrams/telemetry-flow.mmd)

## La cadena, paso a paso

1. **TelemetrySession** se abre al iniciar captura (real, emulada, replay…). Su `source`,
   `random_seed`, `scenario_id`, `generator_version` y `software_version` hacen el
   experimento reproducible byte a byte.
2. **OBDObservation (RAW)**: cada respuesta OBD tal como llegó (PID, valor, unidad, timestamp).
   Nunca se corrige ni se filtra: es el registro empírico.
3. **TelemetryPoint (NORMALIZED)**: el tick validado (rangos físicos, unidades canónicas),
   con `discarded_pids` explícito — la pérdida de datos es información, no silencio.
4. **TelemetryWindow (DERIVED)**: ventana deslizante (60 muestras, solape 50 % por defecto,
   gobernado por el `ModelManifest` activo) con referencia a su rango de puntos (`seq_start..seq_end`).
5. **FeatureVector (DERIVED)**: las 42 features canónicas (`mecanico_contracts.features`,
   versionadas con `feature_set_version`) — el contrato exacto entrenamiento↔inferencia.
6. **ModelInference (INFERRED)**: TODA ejecución de modelo se persiste (score, umbral,
   modelo@versión, latencia), se dispare o no — sin esto no hay análisis de falsos negativos.
7. **DetectedAnomaly (INFERRED)**: la inferencia que superó el umbral, con `inference_id` y
   `session_id` para trazabilidad, PIDs implicados y las features de la ventana.

## Trazabilidad inversa (requisito verificado)

```
DetectedAnomaly → ModelInference → FeatureVector → TelemetryWindow → TelemetryPoints → OBDObservations
```

Implementada solo con claves foráneas — sin heurísticas — y verificada por
`tests-integration/test_traceability_e2e.py::test_trazabilidad_learned_pattern_hasta_raw`,
que navega desde un LearnedPattern hasta las observaciones crudas de uno de sus casos.

## Notas de diseño

- La cuantización J1979 se aplica también a datos sintéticos offline (ADR-0010 §4): la
  resolución de los datos es parte de su semántica.
- El gating de calentamiento (primeras N ventanas sin puntuar) es configuración del pipeline,
  no borrado de datos: las ventanas existen, solo no se evalúan.
- `RecordedSession` (cabecera de archivo JSONL) es la serialización portable de una
  TelemetrySession + inventario del archivo; misma semántica, distinto medio.
