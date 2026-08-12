# ADR-0002 — Emulación dual de la Raspberry Pi (compatibilidad vs. rendimiento)

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 1

## Contexto

No hay hardware físico disponible (decisión del autor, Fase 0). Se necesita (a) garantizar que el software funcionará en ARM64/Raspberry Pi OS y (b) obtener mediciones de rendimiento significativas para la hipótesis H4, sabiendo que QEMU no reproduce el rendimiento real de un Cortex-A76 (limitación L2).

## Decisión

Separar explícitamente los dos objetivos en dos perfiles del mismo `docker/compose.yml`:

| Perfil | Qué valida | Cómo |
|---|---|---|
| `arm64` | **Compatibilidad**: ruedas Python disponibles para ARM64, binarios, imports | `docker buildx build --platform linux/arm64` (QEMU/binfmt) + smoke test de importación |
| `dev` | **Rendimiento aproximado**: latencia/memoria del pipeline | Contenedor en arquitectura nativa del host con `cpus: 4`, `mem_limit: 8g` (perfil RPi 5 8 GB) |

Las mediciones del perfil `dev` se reportarán en la memoria como **cota aproximada con método declarado**, nunca como rendimiento real de RPi. Si se obtiene hardware antes de la entrega (OS3), se repetirán las mediciones clave; alternativa intermedia: una instancia cloud ARM (Ampere/Graviton) para una medición más representativa de la ISA.

El servicio `ollama` corre en contenedor separado con límites propios; en el dispositivo real compartiría presupuesto con el edge, y así se declarará al interpretar H4.

## Alternativas consideradas

- *Todo bajo QEMU (emulación completa):* fidelidad de ISA pero rendimiento absurdamente degradado y no representativo (la inferencia LLM sería inviable); solo serviría para compatibilidad, que ya cubre el perfil `arm64` con mucho menos coste. Descartada como entorno de medición (riesgo R2).
- *Solo límites de recursos sin build ARM64:* dejaría sin detectar dependencias sin rueda ARM64 hasta el despliegue real. Descartada.
- *Alquilar RPi remota / cloud ARM desde ya:* añade coste y dependencia externa en la fase crítica; se pospone como mejora opcional de la Fase 4.

## Consecuencias

- `docker compose --profile dev up` y `--profile arm64 build` quedan como comandos canónicos.
- Verificado en Fase 1: ambos perfiles pasan `docker compose config`; el build de imagen no pudo completarse en el sandbox de desarrollo por bloqueo del registro Docker Hub (limitación del entorno, no del diseño) — **pendiente de validar en la máquina del autor** (acción A2 del informe de fase).
- La memoria del TFM debe incluir la tabla de este ADR y la declaración metodológica de L2.
