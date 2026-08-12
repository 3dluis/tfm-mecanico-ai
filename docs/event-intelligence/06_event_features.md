# 06 — EventFeatureVector

[← Índice](README.md)

Vector de características de un EVENTO COMPLETO (no de una ventana fija): la unidad
comparable entre eventos equivalentes. Versionado triple obligatorio:
`feature_schema_version` (definición del vector) · `preprocessing_version` (fusión/limpieza)
· `detector_version` (quién segmentó el evento) — dos vectores solo son comparables si las
tres versiones coinciden (política de data-architecture/07).

Contenido v1 (por tipo de evento; ejemplo ACCELERATION):

- Cinemática: start_speed, end_speed, delta_speed, duration_s, accel_mean, accel_peak.
- Motor: rpm_mean/max/slope, throttle_mean/peak, engine_load_mean.
- Aire/combustible: maf_mean, maf_response (Δmaf/Δthrottle), map_mean, stft_mean, ltft_mean.
- Térmica/contexto: coolant_mean (alimenta EventContext, no compara).
- IMU (cuando exista): long_accel_peak, yaw_rate_mean, vibration_rms.

Los eventos de otros tipos comparten el esquema con features no aplicables a 0 y un vector
de presencia — MISMA decisión que las features de ventana (orden estable, contrato en
`shared`). Implementación v1 en el slice: `event_features()` para
ACCELERATION/DECELERATION/IDLE/CONSTANT_SPEED con 18 features.
