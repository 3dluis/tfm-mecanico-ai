# Model Card — event-detector (`ed:1`, máquina de estados)

**Fuente:** informe F6 §3 · tests-integration/test_event_slice.py · ADR-0019.

## Identificación
- **model_id:** `event-detector` · **version:** ed:1 · **status: VALIDATED**
- **model_type:** ml (familia state_machine — la taxonomía ML incluye detectores sin
  pesos) · **detection_method:** STATE_MACHINE (+RULE para ENGINE_START/STOP)
- **purpose:** segmentación de telemetría en VehicleEvents (IDLE, ACCELERATION,
  DECELERATION, CONSTANT_SPEED, ENGINE_START/STOP, TRIP)
- **owner:** `diagnostic-agent:events`

## Origen y configuración
- **algorithm:** máquina de estados sobre SPEED suavizada (3 ticks) y su derivada, con
  histéresis (entrada 0.9 / salida 0.45 km/h/s), duración mínima 3 ticks y fusión de
  segmentos; sin entrenamiento (umbrales analíticos de la física del simulador,
  **marcados a validar con datos reales**)
- **features de entrada:** SPEED + RPM cuantizados J1979 · **no usa etiquetas jamás**
- **artifact:** python puro (`diagnostic_agent/events/detector.py`); sin checksum de
  artefacto — la versión `ed:1` se versiona por código (git)

## Métricas (vs ground truth obd-lab, trip urbano 600 s, IoU ≥ 0.5; informe F6)
| Evento | P | R | F1 | IoU medio | onset err |
|---|---|---|---|---|---|
| ENGINE_START / TRIP | 1.00 | 1.00 | 1.00 | 1.00 | 0 |
| IDLE | 1.00 | 0.86 | 0.92 | 0.74 | 6.8 ticks |
| CONSTANT_SPEED | 0.75 | 1.00 | 0.86 | 0.81 | 8.7 ticks |
| DECELERATION | 0.83 | 0.83 | 0.83 | 0.59 | 0 |
| ACCELERATION | 0.71 | 0.83 | 0.77 | 0.78 | 0.4 ticks |

## Limitaciones y modos de fallo (✍)
- Umbrales calibrados a la dinámica del SIMULADOR; sin validación con conducción real.
- Los errores de onset en IDLE/CONSTANT_SPEED reflejan la diferencia GT-comandado vs
  dinámica-resultante (documentada en informe F6 §3) — decisión pendiente antes del
  experimento formal.
- ENGINE_STOP a fin de stream es ESTIMATED (conf 0.5): la parada no se observa.
- Sin IMU no detecta giros/frenadas finas (ADR-0020).
- **Unsupported:** eventos MANEUVER/ENVIRONMENT (requieren IMU); tráfico denso
  stop-and-go no simulado.

## Rol experimental
Es el **rule baseline a batir**: cualquier detector ML/CPD/HMM de eventos debe superarlo
bajo las mismas métricas para justificar su complejidad ([02 §3](../../02_ml_models.md)).
