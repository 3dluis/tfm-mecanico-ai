# ADR-0020 — Incorporación de IMU (evaluación y decisión)

**Fecha:** 2026-08-12 · **Estado:** Aceptada (SHOULD-have; compra pospuesta) · **Fase:** 6

## Evaluación

| Criterio | MPU-6050 | **ICM-20948 (recomendada)** | BNO055 |
|---|---|---|---|
| DoF | 6 (acc+gyro) | 9 (acc+gyro+mag) | 9 + fusión on-chip |
| Precio aprox. | 3–6 € | 12–18 € | 25–35 € |
| Interfaz RPi | I2C (driver smbus2, muy documentado) | I2C/SPI (drivers Python: Adafruit/SparkFun) | I2C (driver Adafruit) |
| Muestreo útil | hasta ~1 kHz | hasta ~1,1 kHz (acc) | ~100 Hz (fusionado) |
| Precisión/ruido | correcto (diseño antiguo, EOL anunciado por Invensense) | mejor ruido y estabilidad; sucesor soportado | orientación directa (quaternion) pero ODR baja |
| Consumo | ~4 mA | ~3 mA | ~12 mA |
| Sincronización | timestamp del host (sin reloj propio útil) — igual en las tres; resuelto por diseño de fusión (docs/event-intelligence/05) | | |

**Decisión:** diseñar para **ICM-20948** como referencia (moderna, 9-DoF, drivers Python
maduros, margen de frecuencia) con **MPU-6050 como alternativa de bajo coste** totalmente
compatible con el diseño (la capa de fusión solo exige acc XYZ + gyro XYZ con timestamps del
host). BNO055 descartada como principal: la fusión on-chip es cómoda pero opaca (queremos
las señales crudas para los detectores) y su ODR limita vibración/impacto.

**Estado en el TFM:** SHOULD-have. La compra/integración física se decide tras el vertical
slice de eventos OBD-only; mientras tanto obd-lab SIMULA la IMU (acelerómetro/giróscopo
sintéticos derivados de la dinámica: aceleración desde dv/dt + ruido, yaw en curvas
sintéticas, vibración/impacto como transitorios) — suficiente para validar pipeline y
detectores iniciales (requisito 29), declarando la limitación.

## Consecuencias

Eventos que REQUIEREN IMU (giros, vibración, impacto, frenada fina) quedan diseñados y
bloqueados solo por hardware; sincronización temporal especificada (t_mono + UTC + deriva
documentada) antes de que llegue el sensor — el error clásico que se evita es integrar la
IMU sin plan de relojes.
