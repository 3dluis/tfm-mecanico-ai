# ADR-0026 — Política de alineación temporal de snapshots (`sync:v1`)

- **Fase:** 11
- **Estado:** Aceptada
- **Contexto documental:** [data-architecture/11 §3](../data-architecture/11_vehicle_telemetry_snapshot.md)

## Contexto

Los PIDs no se adquieren en el mismo instante: el ciclo ELM327 los sondea secuencialmente
(`09:15:31.120 RPM · .137 MAF · .151 STFT · .168 MAP`). Construir una fila horizontal exige
**decidir y registrar** cómo se agrupan muestras de instantes distintos. Sin política
explícita, cada consumidor alinearía a su manera y los resultados dejarían de ser comparables.

## Decisión

Política `sync:v1`, registrada por fila en `synchronization_version`:

1. **Rejilla canónica** de `snapshot_interval_ms`, anclada al inicio de la sesión.
2. Por señal: muestra más cercana dentro de ±`alignment_window_ms` (500 ms) → `measured`;
   si no hay, última muestra dentro de `stale_tolerance_ms` (2000 ms) → valor + flag `stale`;
   si tampoco → `None` + flag `missing`.
3. **Los parámetros son parte de la versión de la política**: cambiarlos significa `sync:v2`,
   no un ajuste silencioso. Cada fila persiste `snapshot_interval_ms` para que la frecuencia
   sea un dato, no una suposición.
4. **Relojes:** `timestamp_utc` para persistencia e intercambio; la sincronización fina local
   se apoya en el reloj monotónico del adquisidor (par `t_mono`/UTC ya definido en
   event-intelligence/05, con fuente y precisión documentadas allí).
5. **Frecuencia canónica:** 1 Hz es la única **validada** (12 PIDs secuenciales sobre ELM327
   emulado). **5 Hz queda como candidato SIN fijar**: requiere validar frecuencia real de
   sondeo, latencia ELM327 por PID, número de PIDs del ciclo, hardware y almacenamiento (×5
   el volumen). La arquitectura admite cualquier intervalo.

## Consecuencias

- Dos caminos de construcción: `build_from_ticks` (rejilla del laboratorio, alineación
  identidad) y `build_from_observations` (caso general `sync:v1` con cursores por señal).
- La comparabilidad entre estudios queda condicionada a la versión de sincronización: dos
  conjuntos con `sync` distinto no se mezclan sin declararlo.
- Riesgo: una ventana demasiado ancha mezclaría estados transitorios distintos (p. ej. durante
  una aceleración brusca). Por eso `stale` es un flag visible y no un valor silencioso.
