# ADR-0028 — Estrategia de particionamiento de snapshots

- **Fase:** 11
- **Estado:** Aceptada (candidato evaluado, NO implementado)
- **Contexto documental:** [data-architecture/11 §10](../data-architecture/11_vehicle_telemetry_snapshot.md) · [09](../data-architecture/09_retencion_sincronizacion.md)

## Contexto

`vehicle_telemetry_snapshots` es la tabla de mayor crecimiento del sistema. Medido a 1 Hz con
12 PIDs: 3 600 filas/h ≈ 4.2 MB; 86 400 filas/24 h ≈ 87 MB; **≈2.6 M filas ≈ 2.6 GB por mes y
vehículo**. En cloud, con N vehículos, esa tabla domina el almacenamiento y las consultas por
rango temporal.

## Decisión

1. **Candidato: particionado declarativo por rango sobre `timestamp_utc`, granularidad
   mensual** (`telemetry_2026_08`, `telemetry_2026_09`, …) en PostgreSQL.
2. **No se crean particiones automáticamente.** Se activarán cuando el volumen real lo
   justifique (criterio: >10 M filas en la tabla o degradación medible de las consultas por
   rango), y la creación será explícita y versionada, no implícita.
3. **En el edge no aplica hoy**: SQLite no tiene particionado nativo y la retención corta del
   edge (política [09](../data-architecture/09_retencion_sincronizacion.md)) mantiene la tabla
   en tamaños triviales. Si el edge migrara a PostgreSQL (ADR-0029), heredaría esta misma
   estrategia sin cambio de modelo lógico.
4. El particionado **no cambia la semántica ni las claves**: `snapshot_id` sigue siendo la PK
   lógica global y los índices `(vehicle_id, timestamp_utc)` / `(session_id, timestamp_utc)` /
   `(primary_event_type, timestamp_utc)` se replican por partición.
5. **Nada referenciado por provenance se elimina al desprender una partición**: el `DETACH` de
   una partición antigua exige comprobar antes que ningún caso diagnóstico, `CaseMemory` o
   `LearnedPattern` referencie ese rango; si lo hace, ese intervalo pasa a retención larga.

## Consecuencias

- Purga por `DROP/DETACH PARTITION` en lugar de `DELETE` masivo (orden de magnitud más barato).
- Coste: DDL periódico (creación de particiones futuras) que debe automatizarse con cuidado —
  motivo por el que hoy se documenta como candidato y no se activa.
- Downsampling conceptual asociado (diseñado, no implementado): `RAW alta frecuencia →
  snapshot canónico → agregado 1/60 Hz → resumen por evento → features de largo plazo`.
