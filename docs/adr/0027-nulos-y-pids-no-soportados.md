# ADR-0027 — NULL ≠ 0: PIDs no soportados y calidad por señal

- **Fase:** 11
- **Estado:** Aceptada
- **Contexto documental:** [data-architecture/11 §4](../data-architecture/11_vehicle_telemetry_snapshot.md)

## Contexto

Una representación horizontal tiene, por construcción, columnas que no siempre existen: un
vehículo puede no soportar `fuel_pressure`, el ciclo puede no sondear IMU/GPS, una lectura
puede expirar por timeout o llegar fuera de rango. Almacenar 0 en esos casos corrompería
cualquier estadística (medias, correlaciones, baselines) y sería indistinguible de un valor
físicamente cero (ralentí, vehículo parado).

## Decisión

1. **Una señal no disponible se almacena como `NULL`, jamás como 0.**
2. La causa se registra en `quality_flags` (JSON por fila), con vocabulario cerrado
   `SignalQuality`: `measured` · `stale` · `not_supported` · `not_polled` · `timeout` ·
   `missing` · `invalid`.
3. **Los flags son compactos**: solo se listan las señales cuyo estado ≠ `measured` (una fila
   perfecta lleva `{}`). Los campos que están **fuera del ciclo de sondeo configurado** (hoy
   `fuel_pressure`, IMU y GPS) quedan `NULL` **sin flag por fila**: su estado `not_polled` es
   una propiedad del ciclo, documentada una vez, no repetida en millones de filas.
4. Dos agregados baratos acompañan cada fila: `quality_score` (medidas/esperadas del ciclo) y
   `missing_metric_count`.

## Alternativas descartadas

- **Tabla relacional de calidad por señal** (una fila por señal y snapshot): semánticamente
  más pura pero multiplica ×12 el volumen de filas del edge sin caso de uso que lo justifique.
  Reevaluable si algún día se filtra sistemáticamente por flag.
- **Columna de flag por señal** (`maf_quality`, …): duplica el ancho de la tabla para
  información que es casi siempre `measured`.

## Consecuencias

- Todo consumidor (ML incluido) debe tratar `NULL` explícitamente: imputar es una decisión de
  la fase de features, nunca del almacenamiento.
- `quality_score` permite filtrar sesiones degradadas sin abrir el JSON de flags.
