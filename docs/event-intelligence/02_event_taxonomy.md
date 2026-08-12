# 02 — Taxonomía de eventos (v1, versionada)

[← Índice](README.md)

`taxonomy_version = 1` (campo en VehicleEvent vía detector_version; cambios = nueva versión).
Clases de conocimiento: **OBSERVED** (directamente medible: p. ej. IDLE desde RPM/velocidad),
**INFERRED** (deducido de firmas: GEAR_SHIFT_INFERRED), **ESTIMATED** (aproximado con
incertidumbre alta: PARKED retrospectivo). Un evento no OBSERVED nunca se presenta como hecho.

| Categoría | Evento | Clase | Fuente mínima | Estado F6 |
|---|---|---|---|---|
| POWER | IGNITION_ON / IGNITION_OFF | estimated¹ | OBD (presencia de bus/tensión) | diseñado |
| ENGINE | ENGINE_START / ENGINE_STOP | observed | OBD (RPM 0→>400 / →0) | ✅ slice |
| ENGINE | COLD_START / WARM_START | observed | OBD (coolant en el arranque; umbral vs ambiente) | diseñado |
| ENGINE | WARM_ENGINE (estado) | observed | OBD (coolant ≥ ~80 °C) | ✅ slice (contexto) |
| ENGINE | IDLE | observed | OBD (RPM>0, v≈0, duración mín.) | ✅ slice |
| MOTION | VEHICLE_START_MOVING / VEHICLE_STOPPED | observed | OBD (velocidad + histéresis) | ✅ slice |
| MOTION | ACCELERATION / DECELERATION / CONSTANT_SPEED | observed | OBD (dv/dt + throttle; IMU mejora) | ✅ slice |
| MANEUVER | HARD_BRAKING / RAPID_ACCELERATION | inferred | OBD (umbral dv/dt) · IMU mejora mucho | diseñado |
| MANEUVER | TURN_LEFT / TURN_RIGHT / HARD_TURN | inferred | **IMU requerida** (gyro yaw; GPS heading opc.) | diseñado |
| TRANSMISSION | GEAR_SHIFT_INFERRED (UP/DOWN) | inferred | OBD (RPM/speed ratio + caída rápida de RPM) | diseñado |
| ENVIRONMENT | VIBRATION / IMPACT | inferred | **IMU requerida** (aceleración alta frecuencia) | diseñado |
| ANOMALY | CONTEXTUAL_ANOMALY (evento anómalo) | inferred | detector contextual (doc 08) | ✅ slice |
| TRIP | TRIP_START / TRIP_END / TRIP (contenedor) | observed | OBD (engine start→stop con movimiento) | ✅ slice |
| TRIP | STOPPED vs PARKED | estimated | OBD (+GPS opc.); PARKED es retrospectivo (doc 04) | diseñado |

¹ Con solo OBD, IGNITION_ON sin arranque es difícil de distinguir del inicio de sesión de
captura: se declara estimated y se documenta la limitación (el adaptador se alimenta del
puerto y aparece con el contacto).

Ajustes sobre la propuesta original: ENVIRONMENT recoge VIBRATION/IMPACT (física del
entorno/chasis); WARM_ENGINE se modela como ESTADO de contexto más que como evento puntual
(alimenta EventContext); DRIVING se subsume en MOTION+MANEUVER para evitar solapes.

Jerarquía (requisito 8): `parent_event_id` — TRIP contiene eventos; un evento puede contener
subeventos (p. ej. ACCELERATION conteniendo GEAR_SHIFT_INFERRED). Microeventos (<1 s, p. ej.
impactos IMU) se admiten con la misma entidad: la jerarquía de 3 niveles
trip/evento/microevento es convención, no esquema distinto.
