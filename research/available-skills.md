# Skills auxiliares disponibles

Estado de esta máquina a 3 de septiembre de 2026. **Es estado local**: cambia entre máquinas
y se vuelve a comprobar en cada una.

| Skill | Ubicación | Estado | Para qué se usa | Comprobado |
|---|---|---|---|---|
| `uax-tfm-ai-researcher` | `TFM/.claude/skills/` | instalado; SKILL.md, referencias, flujos y scripts leídos íntegros | orquestador académico; aplicado en la enmienda de la PI (ADR-003) | 2026-09-03 |
| `uax-tfm-ai-tutor` | listado en la sesión | disponible | evaluación independiente PASS / FAIL de trabajo del researcher; simulacro de tribunal | 2026-09-03 |
| `clean-user-facing-text` | plugin `watermarks-remover` 0.5.0 | disponible | limpieza estilística final; fase de humanización | 2026-09-01 |
| `remove-ai-marks` | plugin `watermarks-remover` 0.5.0 | disponible **con reserva** | higiene documental autorizada | 2026-09-01 |
| `find-docs` | `~/.claude/skills/` | disponible | documentación actual de librerías para el capítulo 4 | 2026-09-01 |
| `humanizer` | plugin `humanizer` 2.11.2 | disponible, **no previsto** | PHILIP-K-MODERATE ya cubre la fase de voz; solo con la lista de preservación | 2026-09-03 |
| `tfm-format-auditor` | `TFM/.claude/skills/` | construido y ejecutado sobre la memoria completa | auditoría editorial y estructural: numeración, rótulos, procedencia, referencias cruzadas, ubicación definición/resultado, índices de la plantilla | 2026-09-10 |

## Scripts del researcher ejecutados el 3 de septiembre de 2026

`validate_structure.py`, `validate_citations.py`, `validate_references.py`,
`validate_traceability.py`, `word_count.py` sobre `docs/memoria/` y
`research/traceability-matrix.md`. Resultados y lectura manual en
`docs/tfm/cambio_pi_eliminacion_datos_reales.md` §16.

## Reserva sobre `remove-ai-marks`

Es un **cliente HTTP**: exige un servicio local en `WATERMARKS_SERVICE_URL` (por defecto
`http://127.0.0.1:8765`). Si el servicio no responde, el propio skill indica que **no debe
haber respaldo local**. En ese caso la fase se omite y se declara. No se ha comprobado que el
servicio esté levantado.

## Cuándo se usan los de humanización

Todavía no. Pertenecen a la fase de humanización, que **no se ejecuta antes del gate
académico**. A 3 de septiembre de 2026 GATE-03 está en `FAIL` (objetivos pendientes de
consenso) y GATE-05, 08, 09 y 11 en `BLOCKED`.
