# 04 — Detección de eventos: criterios y técnicas

[← Índice](README.md)

Método v1 por evento (umbrales INICIALES a validar experimentalmente — requisito 11; ningún
valor es definitivo hasta el estudio de sensibilidad con ground truth de obd-lab):

- **ACCELERATION / DECELERATION**: dv/dt suavizado (media móvil 3 s) con umbral ±0,8 km/h/s,
  histéresis (entrada 0,8 / salida 0,4), duración mínima 3 s, y fusión de eventos separados
  <2 s. Con IMU: confirmación por aceleración longitudinal (mejora onset ~1 s y confidence).
- **IDLE**: RPM>400 ∧ v<2 km/h ∧ duración ≥10 s. Refinamientos posteriores: throttle bajo,
  carga estable, contexto térmico.
- **ENGINE_START/STOP**: flanco RPM 0→>400 (START; STARTING si dura <2 s) y >400→0 (STOP).
  COLD_START: coolant en el arranque < ambiente+15 °C; WARM_START en caso contrario.
  Difíciles con solo OBD-1 Hz: cranking fino (<1 s) y distinción IGNITION/START — declarado.
- **VEHICLE_START_MOVING / STOPPED**: v cruza 3 km/h con histéresis y 3 s mínimos.
- **STOPPED vs PARKED**: STOPPED = v≈0 con motor encendido. PARKED = decisión RETROSPECTIVA:
  ENGINE_STOP + sin movimiento durante ≥N min (v1: 5 min) + fin de sesión o IGNITION_OFF;
  con GPS, además sin desplazamiento. Se emite al expirar la ventana, nunca en caliente.
- **GEAR_SHIFT_INFERRED**: sobre el ratio RPM/velocidad: subida de RPM → caída rápida de RPM
  (>400 rpm en <2 s) con velocidad mantenida/creciente → shift (UPSHIFT si el ratio cae).
  Técnicas evaluadas: reglas (v1) → clustering de ratios (identifica mesetas de marcha) →
  change-point detection (ruptures/PELT) → HMM. **No se promete identificar el número de
  marcha**; salida = GEAR_SHIFT_INFERRED con confidence.
- **TURN_LEFT/RIGHT/HARD_TURN**: SOLO con IMU (gyro-z/yaw rate; umbrales 15/45 °/s) — no se
  intenta desde OBD estándar. **VIBRATION/IMPACT**: IMU alta frecuencia (RMS y picos de
  aceleración). Ambos diseñados; llegan con la IMU (ADR-0020).
- **TRIP**: contenedor ENGINE_START→ENGINE_STOP que incluya movimiento; ver doc 07 §trips.

Postprocesado común: filtrado de ruido (mediana 3), fusión, resolución de solapes por
prioridad de categoría, y asignación de confidence según margen sobre el umbral y calidad de
datos (pérdidas en el segmento la reducen). ML posterior (HMM, change-point, clasificación)
solo si supera a este baseline en el ground truth (ADR-0019).
