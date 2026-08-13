# 11 — VehicleTelemetrySnapshot (representación canónica horizontal)

**Clase: NORMALIZED WIDE / TIME-ALIGNED** (ADR-0025). Cada fila = estado multivariable
observable del vehículo en un instante canónico. NO sustituye nada: la cadena queda

```
OBDObservation (RAW LONG) → TelemetryPoint (NORMALIZED LONG)
→ VehicleTelemetrySnapshot (NORMALIZED WIDE) → TelemetryWindow / VehicleEvent
→ FeatureVector / EventFeatureVector (DERIVED) → ModelInference → DetectedAnomaly (INFERRED)
```

con vuelta garantizada snapshot→observaciones originales (§provenance). El pipeline F3
(long→window→LOF) sigue intacto; el camino wide es PARALELO hasta que ambos estén
validados (compatibilidad experimental).

## 1. Propósito

Consultar directamente `timestamp | event | rpm | speed | maf | map | stft | …` sin
pivotar `TelemetryPoint` en cada consumidor (ML, análisis longitudinal, Event
Intelligence, estadística, detección multivariable, visualización, memoria, diagnóstico).
`snapshots → matriz/dataframe → windowing/event grouping → features → ML` sin
reconstrucción manual del pivot por entrenamiento.

## 2. Semántica y generación

Contrato: `mecanico_contracts.snapshot_model.VehicleTelemetrySnapshot` (45 campos;
JSON Schema autogenerado; diccionario en [02](02_diccionario_datos.md)). Builder:
`diagnostic_agent.telemetry.snapshots` con dos caminos: `build_from_ticks` (rejilla del
laboratorio, alineación identidad) y `build_from_observations` (caso general sync:v1).
**El snapshot NUNCA contiene features** (`rpm_mean_10s`, `maf_std`, correlaciones…):
estado físico alineado ≠ cálculo derivado.

## 3. Política de alineación temporal (sync:v1, ADR-0026)

Rejilla canónica de `snapshot_interval_ms` anclada al inicio de sesión. Por señal:
muestra más cercana dentro de ±`alignment_window_ms` (500 ms) → `measured`; si no,
última muestra dentro de `stale_tolerance_ms` (2000 ms) → valor + flag `stale`; si no →
`None` + `missing`. Cada fila registra `snapshot_interval_ms` y
`synchronization_version`; los parámetros de la ventana quedan definidos por la versión
de la política (cambiarlos = sync:v2). **Timestamps**: `timestamp_utc` para persistencia
e intercambio; la sincronización fina local usa el reloj monotónico del adquisidor
(dual t_mono/UTC de event-intelligence/05 — fuente y precisión documentadas allí).

**Frecuencia canónica:** 1 Hz es la única VALIDADA (adquisición actual: 12 PIDs
secuenciales sobre ELM327 emulado). **5 Hz sigue siendo candidato sin fijar**: exigiría
validar frecuencia real de sondeo, latencia ELM327 por PID (~decenas de ms), nº de PIDs
del ciclo y almacenamiento (a 5 Hz: ×5 el volumen de §9). La arquitectura admite
cualquier intervalo (campo por fila).

## 4. Missing values (NULL ≠ 0, ADR-0027)

Una señal no disponible es `None`, JAMÁS 0. `quality_flags` distingue por señal:
`not_supported / not_polled / timeout / missing / invalid / stale`. El dict es COMPACTO:
solo señales ≠ `measured` (fila perfecta = dict vacío); los campos FUERA del ciclo de
sondeo configurado (p. ej. fuel_pressure, IMU y GPS hoy) quedan `None` sin flag por fila
— su estado `not_polled` es propiedad del ciclo, documentada aquí, no repetida en cada
fila (evita engordar millones de filas). `quality_score` = medidas/esperadas del ciclo;
`missing_metric_count` = nº de señales del ciclo con flag.

## 5. Integración con Event Intelligence

`primary_event_id/primary_event_type` = evento HOJA más específico del instante
(consulta rápida); `trip_id` = TRIP contenedor; `vehicle_state` = máquina de estados.
Pertenencia simultánea (TRIP + ENGINE_WARM + ACCELERATION + …): relación N:M
`SnapshotEventLink` **sin duplicar snapshots**. Estrategia alternativa sin materializar
(rango `seq_start..seq_end` del evento sobre `sequence_number`) disponible cuando el
volumen de enlaces no compense.

## 6. Queries principales (los índices derivan de ESTOS patrones, no al revés)

```sql
-- por evento y rango (la consulta del plan):
SELECT * FROM vehicle_telemetry_snapshots
WHERE vehicle_id=:v AND primary_event_type='ACCELERATION'
  AND timestamp_utc BETWEEN :t0 AND :t1 ORDER BY timestamp_utc;
-- por sesión · por vehículo+rango · por evento concreto vía N:M (join links)
```

Índices creados: `(vehicle_id, timestamp_utc)`, `(session_id, timestamp_utc)`,
`(primary_event_type, timestamp_utc)` + los de `snapshot_event_links`. Nada más sin un
query pattern que lo justifique.

## 7. Ejemplo real (generado por el builder; reproducible seed 7, perfil urbano)

```
00:00:42 (seq 42) · session doc-ej-seed7 · V001
eventos del instante (N:M): TRIP + ACCELERATION (primary = ACCELERATION)
rpm=1901.5  speed=31.0  throttle=45.1  load=45.1
maf=38.42   map=57.0    stft_b1=-1.56  ltft_b1=0.0
coolant=81.0  iat=33.0  o2_s1=0.26  timing=14.0
quality_score=1.0 · quality_flags={} · fuel_pressure=None (fuera del ciclo)
```

Observaciones RAW que lo produjeron: las 12 lecturas OBD del tick 42 de la sesión
(`RPM=1901.5, SPEED=31.0, ENGINE_LOAD=45.1, …, INTAKE_PRESSURE=57.0`) — verificado por
test (`test_snapshot_e2e.py::test_provenance_hacia_atras`: snapshot→seq→TelemetryPoint→
OBDObservation con igualdad de valores).

## 8. Longitudinalidad y memoria evolutiva (papel en la PI)

Meses de snapshots de un vehículo → eventos comparables (`context_signature`) →
baselines históricos (`EventBaseline` versionados) → evolución del comportamiento. Es la
estructura que permite estudiar **cambios graduales anteriores a un DTC** (análisis
contextual y longitudinal de la PI, Opción B). `CaseMemory`/`LearnedPattern`/`EventBaseline`
NUNCA copian snapshots: referencian sesiones, eventos, rangos temporales
(`session_id + seq_start..seq_end`) y features vía provenance. Qué habilita para
investigar: relaciones multivariables por instante, evolución longitudinal, patrones sin
DTC, eventos comparables, baselines por vehículo y anomalías relacionales — **sin
afirmar mejora de resultados hasta evaluarlo** (los experimentos deciden).

## 9. Rendimiento medido (SQLite, sandbox x86 4CPU/8GB proxy RPi; `perf_snapshots.json`)

| Volumen | Filas | BD | Batch insert | Insert unitario | Q sesión (2 000) | Q rango completo | Q evento | CPU user acum. | RSS pico |
|---|---|---|---|---|---|---|---|---|---|
| 1 h | 3 600 | 4.17 MB | 9 626 filas/s | 634/s | 157 ms | 210 ms (3 800) | 35 ms (609) | 1.5 s | 121 MB |
| 8 h | 28 800 | 29.11 MB | 7 556 filas/s | 563/s | 109 ms | 5.0 s (29 000) | 465 ms (4 685) | 9.9 s | 451 MB |
| 24 h | 86 400 | 86.65 MB | 6 632 filas/s | 644/s | 102 ms | 13.7 s (86 600) | 747 ms (13 719) | 35.3 s | 1 204 MB |

(~1 MB/min a 1 Hz con 12 PIDs. Lectura honesta: **el batch insert es el camino prioritario y
es holgado** — una sesión de 30 min se persiste en <0.5 s. La latencia de las consultas
grandes y el RSS pico están dominados por la **materialización ORM→Pydantic de todas las
filas a la vez** (86 600 objetos ⇒ 1.2 GB), no por SQL: es un límite del *cómo se leyó en el
test*, no del motor. Para ML se leerá por columnas/lotes/streaming — pendiente y ya
identificado como el siguiente cuello de botella real a resolver antes de entrenar sobre
snapshots.)

> **Actualización F13:** la mitad in-memory de esa ruta existe y está validada:
> `ai_models.data.snapshot_matrix` convierte los snapshots de una sesión en matriz
> columnar NumPy (NaN para NULL, máscara de validez, rechazo de rejillas mixtas) y
> EXP-ANOM-005 verificó paridad exacta con el pipeline long de F3
> ([informe](../models/comparisons/wide_path_parity_v1.md), ADR-0031). La lectura columnar
> DESDE PostgreSQL (SELECT por columnas / COPY hacia arrays, sin materializar Pydantic)
> sigue pendiente y se abordará cuando los volúmenes de entrenamiento lo exijan.

## 10. Retención, downsampling y particionamiento

Integrado con [09](09_retencion_sincronizacion.md): snapshots recientes → edge;
antiguos → cloud/downsample; intervalos anómalos → retención larga; evidencia de
diagnóstico → referencia permanente (**nada referenciado por provenance se borra sin
estrategia explícita**). Niveles conceptuales (diseñados, NO implementados aún):
`RAW alta frecuencia → snapshot canónico → agregado 1/60 Hz → resumen por evento →
features de largo plazo`. En PostgreSQL (cloud y edge si se adoptara): particionado
mensual por `timestamp_utc` como candidato (ADR-0028) — NO se crean particiones sin
evaluar volumen (a 1 Hz un mes ≈ 2.6 M filas/vehículo ≈ 2.6 GB: el particionado se
justifica en cloud multi-vehículo; en edge la retención corta lo hace innecesario).
