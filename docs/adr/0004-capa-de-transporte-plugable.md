# ADR-0004 — Capa de transporte plugable (serial | tcp | bluetooth-rfcomm)

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 1

## Contexto

El adaptador real será Bluetooth (RFCOMM), pero el entorno emulado usa pty (local) o TCP (Docker). Emular Bluetooth dentro de contenedores exige BlueZ y mocks frágiles con valor experimental casi nulo: python-OBD trata cualquier adaptador como un puerto serie (limitación L3, decisión D2 de Fase 0, ratificada aquí tras la evaluación práctica).

## Decisión

El módulo `acquisition` define un único punto de configuración de transporte con tres variantes:

- `serial`: ruta de dispositivo (pty del emulador en desarrollo; `/dev/rfcomm0` o USB en real).
- `tcp`: host:puerto (emulador en Docker vía `socket://host:puerto` de pyserial).
- `bluetooth-rfcomm`: **especificada pero no implementada en el TFM** — en Raspberry Pi OS, el emparejamiento BlueZ + `rfcomm bind` expone el adaptador como `/dev/rfcomm0`, reduciéndose al caso `serial`.

La selección es configuración (`MECANICO_TRANSPORT`, pydantic-settings), nunca código condicional disperso.

## Alternativas consideradas

- *Emular RFCOMM con BlueZ en Docker:* frágil, requiere privilegios/hardware, no aporta validez (el flujo de bytes es idéntico); descartada.
- *Solo TCP en todas partes:* simplifica, pero perdería el camino natural al hardware real (serie) y la fidelidad del pty en desarrollo local; descartada.

## Consecuencias

- El paso a hardware real es un cambio de configuración, no de código (verificable solo hasta `serial`; la ruta BT completa queda declarada como limitación L3 en la memoria).
- Los tests parametrizan el transporte; la evaluación E6 (ADR-0003) demuestra el caso `tcp` extremo a extremo.
