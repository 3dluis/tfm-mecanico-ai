# 05 — Sensor fusion y sincronización temporal

[← Índice](README.md) · ADR: [0020](../adr/0020-incorporacion-imu.md)

## Problema

OBD ~1–5 Hz (polling), IMU 50–100 Hz, GPS 1 Hz — relojes y latencias distintas. La capa de
fusión produce una **línea temporal coherente sin destruir el raw** (cada fuente conserva su
tabla de observaciones crudas con su timestamp original).

## Diseño

1. **Timestamps duales**: cada observación registra `t_mono` (reloj monotónico local del
   proceso de captura, para deltas y correlación) y `timestamp` UTC (persistencia e
   intercambio). La correspondencia mono↔UTC se ancla al inicio de sesión y se re-ancla
   periódicamente; el offset y su deriva se guardan como metadatos de sesión.
2. **Fuente de reloj**: RPi sin RTC → hora por NTP cuando haya red; sin red, el reloj local
   es la referencia y la sesión lo declara (`clock_source`). Precisión objetivo: ±10 ms
   entre fuentes locales (suficiente: el evento más corto que tratamos dura ~0,5 s).
3. **Alineación**: rejilla canónica a la frecuencia del maestro (OBD 1 Hz hoy); la IMU se
   AGREGA por intervalo (media, RMS, picos, min/max por eje) en lugar de interpolarse —
   la alta frecuencia se conserva solo como agregados + segmentos crudos de eventos
   (retención, doc data-architecture/09). GPS se interpola linealmente solo para contexto,
   nunca para detección fina.
4. **Huecos y calidad**: los missing por fuente se marcan (nunca se rellenan en silencio);
   un segmento con >20 % de pérdida degrada la confidence de los eventos que toque.
5. **Deriva**: si |offset NTP| detectado > 100 ms se registra un evento de re-anclaje; las
   comparaciones entre sesiones usan solo duraciones y formas, no timestamps absolutos.

`SensorObservation` (generalización de OBDReading para IMU/GPS) queda DISEÑADA: misma forma
(timestamp, canal, valor, unidad, fuente) con `source_kind ∈ {obd, imu, gps}`; se materializa
como contrato cuando la IMU entre (evita tabla vacía hoy; decisión en ADR-0020).
