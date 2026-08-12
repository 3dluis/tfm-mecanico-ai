# 01 — Overview

[← Índice](README.md)

## Por qué eventos

Una ventana de 60 s puede mezclar ralentí y adelantamiento: su "normalidad" es ambigua. Un
evento (p. ej. ACELERACIÓN 40→80 km/h con motor caliente) tiene semántica física: puede
compararse contra las demás aceleraciones equivalentes DEL MISMO VEHÍCULO. Los resultados de
F3 apuntan aquí: las anomalías relacionales held-out se detectan a nivel de episodio pero
con recall bajo por ventana — el contexto es la variable que falta.

## Fuentes de datos

- **OBD-II (disponible hoy):** RPM, velocidad, throttle, carga, refrigerante, MAF, MAP,
  trims, tensión. Suficiente para: encendido/arranque/parada, ralentí, inicio de marcha,
  aceleración/deceleración/velocidad constante, detención, arranque frío/caliente, cambio de
  marcha INFERIDO, trip. A 1 Hz la resolución limita eventos breves (<2-3 s).
- **IMU (SHOULD-have; ADR-0020):** acelerómetro XYZ + giróscopo XYZ (magnetómetro opcional).
  Habilita/mejora: frenada (y frenada brusca), giros, vibración/impacto, inclinación,
  aceleración con mejor precisión temporal. Simulable en obd-lab desde ya.
- **GPS (COULD; opcional, jamás dependencia):** velocidad independiente, rumbo, contexto de
  trayecto.

## Principios

1. Detección determinista primero (reglas + state machine + señal); ML solo si supera al
   baseline (ADR-0019, coherente con ADR-0011).
2. Todo evento inferido lleva confidence + detection_method + detector_version + evidencia +
   sensores fuente. Clase declarada: observado / inferido / estimado.
3. Los eventos REFERENCIAN telemetría (timestamps/seq), no la duplican.
4. Edge-first: toda la detección corre en la RPi; cloud solo consolida baselines (futuro).
5. Compatibilidad: el camino ventana→LOF de F3 sigue intacto; el camino evento→baseline se
   añade en paralelo para poder compararlos experimentalmente (requisito 46).
