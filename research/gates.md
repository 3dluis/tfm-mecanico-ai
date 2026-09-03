# Registro de quality gates

Un gate no se reevalúa de memoria: se vuelve a comprobar. Cada fila cita su evidencia.

**Reevaluado el 1 de septiembre de 2026 a las 15:00**, tras el cierre de E4, E5 y E6.
**GATE-01 reevaluado el 3 de septiembre de 2026** tras la enmienda de la PI (ADR-003); el
resto de filas conserva la fecha de su última comprobación. Auditoría independiente del cambio:
`tutor-reports/TUTOR-REPORT-20260903.md` (`PASS_WITH_OBSERVATIONS` tras reevaluación).

| Gate | Fecha | Estado | Evidencia | Observaciones |
|---|---|---|---|---|
| **GATE-01** Pregunta de investigación | 2026-09-03 | `PASS` | `research/decisions/ADR-003-pi-sin-requisito-de-datos-reales.md`; `docs/matriz_validacion_pi.md` | Reevaluado tras la enmienda ADR-003: la PI ya no exige datos reales; I-07 resuelta. La validez externa sigue registrada como L-01 (crítica) y no como observación de la PI. Anterior: `PASS_WITH_OBSERVATIONS` (2026-09-01) |
| **GATE-02** Vacío | 2026-09-01 16:00 | `PASS_WITH_OBSERVATIONS` | `references/project/gaps.md` GAP-02 revisado; `search-log.md` iteración 5 | Era `FAIL`. La búsqueda dirigida **refutó la hipótesis de vacío**: la distinción presencia/pertinencia está estudiada (RGB, Chen et al. 2024). Vacío reformulado más estrecho y respaldado. Observación: pendiente de lectura a texto completo |
| **GATE-03** Objetivos | 2026-09-01 | **`FAIL`** | `traceability-matrix.md` I-01, I-02; `objective-coverage.md` | OE-M3 y OE-M5 describen el marco legacy. Además el objetivo general lleva dos verbos, contra la regla UAX |
| **GATE-04** Metodología | 2026-09-01 | `PASS_WITH_OBSERVATIONS` | `docs/methodology/`, `docs/plan_experimental_macbook.md` | Diseño coherente, con una variable manipulada y todo lo demás fijo. Pendiente: I-05 (M6 sin subpregunta) |
| **GATE-05** Evidencia | 2026-09-01 | `BLOCKED` | `research/references/evidence-matrix.md` | No hay claims redactados que evaluar. Se evalúa al redactar |
| **GATE-06** Integridad experimental | 2026-09-01 15:00 | `PASS_WITH_OBSERVATIONS` | `reproducibility.md`; E1-E6 | Cinco fases reproducibles. **El cierre del test es técnico, no de palabra**: `load_partition("test")` lanza excepción. E5 mide el suelo de ruido antes de interpretar tamaños de efecto, y E6 encontró un error propio por test. Observación: el pre-registro canónico no está congelado (L-07) |
| **GATE-07** Resultados | 2026-09-01 15:00 | `PASS_WITH_OBSERVATIONS` | E6, `experiments/E6_baseline.json` | Hay cifras verificables y reproducibles (baseline F1 macro 0,876). **Todas son de validación**: el test está cerrado hasta E19 (L-17). Ninguna es todavía un resultado del TFM |
| **GATE-08** Discusión | 2026-09-01 | `BLOCKED` | — | Sin resultados no hay discusión |
| **GATE-09** Conclusiones | 2026-09-01 | `BLOCKED` | — | Ídem |
| **GATE-10** Referencias | 2026-09-01 16:00 | `PASS_WITH_OBSERVATIONS` | `research/references/`; iteración 6 del `search-log` | **110 de 144 identificadores verificados en Crossref/DataCite; 0 rotos.** Recuperados 28 títulos y 52 venues. Observaciones: 34 sin identificador, 7 discrepancias de año, contenido sin verificar, PRISMA formal pendiente |
| **GATE-11** UAX | 2026-09-01 | `BLOCKED` | `references/uax/conflictos-uax.md` | Tres cifras de extensión incompatibles entre documentos oficiales. Decisión del autor con el tutor |
| **GATE-12** Humanización | — | no procede | — | No se ejecuta antes del gate académico |
| **GATE-13** Integridad global | 2026-09-01 | `PASS` | este directorio | Ninguna evidencia inventada. Todos los huecos marcados. Ningún resultado adaptado a las hipótesis |

## Regla de parada

Los dos `FAIL` son de **coherencia**, no de integridad: se corrigen reformulando objetivos y
ampliando la revisión documental, no experimentando. **Pero se corrigen antes de redactar los
capítulos 2 y 3.**

Ningún gate de integridad (05, 06, 07, 10, 13) está en `FAIL`.
