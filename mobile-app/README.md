# mobile-app

Aplicación Flutter (pospuesta: objetivo secundario OS1 del TFM; ver docs/02 §2.3 y docs/07 §7.3).

## Arquitectura prevista

- **Offline-first:** cache local (drift/sqlite) de estado, telemetría, diagnósticos e historial.
- **Edge directo:** la app habla con la API local de la Raspberry Pi en LAN (v1: IP configurada
  manualmente; mejora futura: descubrimiento mDNS). La nube es complementaria (histórico,
  multi-dispositivo).
- **Modelos de datos generados** desde `shared/schemas/*.schema.json` (ADR-0007) — nunca escritos
  a mano.

Pantallas v1: estado del vehículo · telemetría · anomalías · diagnóstico con explicación del
agente · recomendaciones · historial.

`flutter create` se ejecutará cuando esta fase se apruebe, para no versionar scaffolding muerto.
