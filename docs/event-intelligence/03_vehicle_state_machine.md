# 03 — Máquina de estados vehicular

[← Índice](README.md)

Estados de alto nivel (el detector de eventos la usa como espina dorsal; los eventos son
transiciones o segmentos de permanencia):

```
OFF → IGNITION → STARTING → IDLE ⇄ MOVING → STOPPED → IDLE → ENGINE_OFF → OFF
                              ↑______________________________|
```

- **OFF**: sin datos/bus. **IGNITION**: bus vivo, RPM=0. **STARTING**: RPM 0→arranque
  (<2 s). **IDLE**: RPM>400, v≈0. **MOVING**: v>umbral con histéresis (sub-modos:
  aceleración/deceleración/constante). **STOPPED**: v≈0 con motor girando (semáforo).
  **ENGINE_OFF**: RPM→0 con bus aún vivo. PARKED se decide RETROSPECTIVAMENTE (doc 04).
- **Transiciones inesperadas** contempladas: pérdida de bus en MOVING (corte de captura, no
  ENGINE_STOP: se emite DATA_LOSS y el estado queda UNKNOWN hasta re-observación); RPM=0 con
  v>0 (calado/remolque → evento ANOMALY candidato); reconexión a mitad de trip (el estado se
  re-infiere de los valores actuales, no se asume OFF).
- **No depende solo de la conexión OBD**: el estado se deriva de los VALORES (RPM, v,
  tensión), no de la mera presencia del socket; con IMU, la vibración del motor será señal
  adicional de ENGINE_ON aunque el bus se degrade.

Implementación v1 (slice): autómata determinista con histéresis y duración mínima por
estado, ejecutado sobre TelemetryPoints a 1 Hz; cada permanencia/transición relevante emite
un VehicleEvent con su clase y confianza.
