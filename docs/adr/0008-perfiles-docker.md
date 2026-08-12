# ADR-0008 — Compose único en la raíz con perfiles por actividad

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 2 · **Sustituye a:** compose de Fase 1 (docker/compose.yml)

## Contexto

Con seis proyectos, cada actividad (desarrollar el núcleo, entrenar, probar la nube, validar
edge, integración total) necesita un subconjunto distinto de servicios. Levantarlo todo siempre
es lento y consume la RAM del Mac del autor.

## Decisión

Un único `docker-compose.yml` en la raíz del monorepo, con **perfiles**:

| Perfil | Servicios | Actividad |
|---|---|---|
| `dev` | `obd-emulator` (obd-lab, TCP :35000) · `agent` · `ollama` | desarrollo del núcleo edge |
| `research` | `jupyter` (imagen ai-models) | experimentación/entrenamiento |
| `cloud` | `cloud-api` · `postgres` | desarrollo de la nube |
| `edge` | `agent-edge` (límites 4 vCPU/8 GB, ADR-0002) · `ollama` | validación de recursos |
| `full` | todos | integración extremo a extremo |

Detalles: imágenes por dominio (`<dominio>/Dockerfile`) con contexto raíz (para copiar
`shared/`); base multi-arch `python:3.11-slim`; datos en volúmenes con nombre; configuración por
variables `MECANICO_*` (`.env.example` documenta todas); el emulador se consume por TCP dentro
de la red de compose (los pty no cruzan contenedores, ADR-0004). `make dev|research|cloud|edge|full`
como fachada.

## Alternativas consideradas

- *Un compose por dominio:* duplica definición de redes/volúmenes y complica el perfil `full`
  (múltiples -f frágiles). Descartado.
- *Compose raíz + overrides por entorno:* útil más adelante para el despliegue RPi real
  (`compose.edge.yml` con `platform: arm64`); se pospone hasta esa fase.
- *Devcontainers:* comodidad de IDE, no sustituye a los perfiles; opcional futuro.

## Consecuencias

- `docker compose --profile dev up` es el comando canónico de desarrollo (requisito del autor).
- El compose de Fase 1 (`docker/compose.yml`) se elimina; ADR-0002 y 0005 siguen vigentes en lo
  metodológico (dual arm64/x86-limitado y alcance de validación en sandbox).
