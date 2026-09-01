# Skills auxiliares disponibles

Estado de esta máquina a 1 de septiembre de 2026. **Es estado local**: cambia entre máquinas
y se vuelve a comprobar en cada una.

| Skill | Ubicación | Estado | Para qué se usa | Comprobado |
|---|---|---|---|---|
| `uax-tfm-ai-researcher` | `TFM/.claude/skills/` | instalado | orquestador académico | 2026-09-01 |
| `clean-user-facing-text` | plugin `watermarks-remover` 0.5.0 | disponible | limpieza estilística final; fase de humanización | 2026-09-01 |
| `remove-ai-marks` | plugin `watermarks-remover` 0.5.0 | disponible **con reserva** | higiene documental autorizada | 2026-09-01 |
| `find-docs` | `~/.claude/skills/` | disponible | documentación actual de librerías para el capítulo 4 | 2026-09-01 |
| `humanizer` | plugin `humanizer` | disponible, **no previsto** | PHILIP-K-MODERATE ya cubre la fase de voz | 2026-09-01 |

## Reserva sobre `remove-ai-marks`

Es un **cliente HTTP**: exige un servicio local en `WATERMARKS_SERVICE_URL` (por defecto
`http://127.0.0.1:8765`). Si el servicio no responde, el propio skill indica que **no debe
haber respaldo local**. En ese caso la fase se omite y se declara. No se ha comprobado que el
servicio esté levantado.

## Cuándo se usan

Ninguno todavía. Todos pertenecen a la fase de humanización, que **no se ejecuta antes del
gate académico**. A 1 de septiembre de 2026 hay dos gates en `FAIL` y cinco en `BLOCKED`.
