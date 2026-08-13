# ADR-0025 — Representación canónica horizontal de telemetría (VehicleTelemetrySnapshot)

- **Fase:** 11
- **Estado:** Aceptada
- **Contexto documental:** [data-architecture/11](../data-architecture/11_vehicle_telemetry_snapshot.md)

## Contexto

La telemetría se modela hoy en formato largo: `OBDObservation` (RAW LONG, una fila por
lectura de PID) → `TelemetryPoint` (NORMALIZED LONG, una fila por métrica y `seq`). Todo
consumidor multivariable — ML, Event Intelligence, análisis estadístico, visualización,
análisis longitudinal, diagnóstico — necesita el estado **conjunto** del vehículo en un
instante, de modo que cada uno reconstruía su propio pivot long→wide. Eso es trabajo
repetido, no reproducible entre consumidores y sin política común de alineación temporal ni
de valores ausentes.

## Decisión

Se incorpora `VehicleTelemetrySnapshot` como **representación canónica horizontal**: una
fila = estado multivariable observable del vehículo en un instante de la rejilla canónica.

1. **Clase propia: NORMALIZED WIDE / TIME-ALIGNED.** No es DERIVED (no calcula nada nuevo) y
   **no es INFERRED** (no es producto de un modelo): es el mismo hecho observado, pivotado y
   alineado.
2. **No sustituye a nada.** `OBDObservation` sigue siendo el RAW y `TelemetryPoint` el
   NORMALIZED LONG. La cadena queda
   `OBDObservation → TelemetryPoint → VehicleTelemetrySnapshot → TelemetryWindow/VehicleEvent
   → FeatureVector → ModelInference → DetectedAnomaly`.
3. **Provenance bidireccional obligatoria:** desde un snapshot se vuelve a las observaciones
   que lo produjeron por `(session_id, sequence_number)`; verificado por test
   (`test_snapshot_e2e.py::test_provenance_hacia_atras`).
4. **Sin features dentro del snapshot.** Estado físico alineado ≠ cálculo derivado: medias,
   desviaciones y correlaciones pertenecen a `FeatureVector`/`EventFeatureVector`.
5. **Compatibilidad experimental:** el camino F3 vigente (long → window → LOF) sigue
   funcionando sin cambios; el camino wide se añade en **paralelo**. La migración de
   consumidores será gradual y solo cuando ambos estén validados.

## Consecuencias

- Contrato Pydantic versionado + JSON Schema autogenerado; tabla `vehicle_telemetry_snapshots`
  en el Edge Store (esquema DB v4) con inserción por lotes como camino prioritario.
- Coste de almacenamiento adicional medido: ~1 MB/min a 1 Hz con 12 PIDs (≈87 MB por 24 h),
  aceptable frente a la retención corta del edge.
- Riesgo asumido: dos representaciones normalizadas conviviendo. Se mitiga con la regla de que
  el snapshot **se deriva siempre** de los puntos/observaciones y nunca es fuente primaria.
