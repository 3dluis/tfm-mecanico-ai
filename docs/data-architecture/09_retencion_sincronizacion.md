# 09 — Retención y sincronización

[← Índice](README.md)

## Política inicial de retención en el edge (RPi, valores a validar con pruebas de almacenamiento)

| Clase | Datos | Retención inicial | Justificación |
|---|---|---|---|
| RAW alta frecuencia | obd_observations | 7 días rodantes | Solo sirve para re-derivar; regenerable en sintético |
| NORMALIZED | telemetry_points | 30 días | Base de re-ventanado y análisis reciente |
| NORMALIZED WIDE | vehicle_telemetry_snapshots + snapshot_event_links | 30 días en edge (medido: ≈87 MB/24 h a 1 Hz) | Entrada canónica de ML/análisis; reconstruible desde los puntos mientras estos vivan ([11](11_vehicle_telemetry_snapshot.md)) |
| DERIVED | ventanas+features | 90 días (metadatos+features; sin puntos) | Barato, útil para re-evaluar modelos |
| Intervalos anómalos | puntos+raw de ventanas flagged ±5 min | prioritaria: 1 año | El material de estudio |
| Evidencia de diagnóstico | casos, hipótesis, evidencias, provenance, runs | permanente | Núcleo explicable del TFM |
| Memoria | case_memory, learned_patterns | permanente | El objeto de investigación |

Estimación de partida (1 Hz × 12 PIDs): raw ≈ 1 M filas/día ≈ decenas de MB/día — la purga
de 7 días mantiene el footprint en cientos de MB. Los valores se justificarán con medición
real en el perfil edge (tarea de la fase de evaluación).

Purga = job local diario; NUNCA borra nada referenciado por DiagnosticEvidence/Provenance
(integridad antes que espacio). Niveles de **downsampling** diseñados (no implementados aún,
ADR-0028): `RAW alta frecuencia → snapshot canónico → agregado 1/60 Hz → resumen por evento →
features de largo plazo`; en cloud, la purga de snapshots antiguos será
`DETACH/DROP PARTITION` mensual, previa comprobación de que ese rango no está referenciado.

## Sincronización (outbox, integra ADR-0009/0012)

Tabla `sync_outbox`: `envelope_id` (UUID = idempotency key), entidad, payload JSON,
checksum, `priority`, timestamps, `attempts`.

- **Prioridades:** 1 diagnostics · 2 anomalies+inferences · 3 evidence/provenance ·
  4 case_memory/resúmenes · 5 telemetría de modelo · 9 raw completo (OPT-IN por configuración).
- **Idempotencia:** upsert por id global en cloud; reenvíos inocuos.
- **Reintentos:** backoff exponencial con jitter; `attempts` acotado, luego cuarentena visible.
- **Conflictos:** last-write-wins por timestamp UTC + log del perdedor.
- **Versionado:** `schema_version` en cada sobre; el cloud rechaza versiones desconocidas
  (el sobre queda en cuarentena hasta actualizar el consumidor).
- Checksum sha256 del payload cuando la entidad transporta artefactos.

No se sincroniza telemetría cruda de forma indiscriminada: el defecto es diagnósticos,
anomalías, evidencia y resúmenes.
