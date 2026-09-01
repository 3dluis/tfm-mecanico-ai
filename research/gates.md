# Registro de quality gates

Un gate no se reevalúa de memoria: se vuelve a comprobar. Cada fila cita su evidencia.

| Gate | Fecha | Estado | Evidencia | Observaciones |
|---|---|---|---|---|
| **GATE-01** Pregunta de investigación | 2026-09-01 | `PASS_WITH_OBSERVATIONS` | `docs/matriz_validacion_pi.md` | Clara, evaluable, con desenlaces de refutación escritos. Observación: PI.1 habla de datos reales y E3 está bloqueada (L-01, I-07) |
| **GATE-02** Vacío | 2026-09-01 | **`FAIL`** | `traceability-matrix.md` I-03; `limitations-register.md` L-10 | **PI.4 no tiene vacío que la justifique.** El vacío vigente no cubre la distinción presencia/pertinencia |
| **GATE-03** Objetivos | 2026-09-01 | **`FAIL`** | `traceability-matrix.md` I-01, I-02; `objective-coverage.md` | OE-M3 y OE-M5 describen el marco legacy. Además el objetivo general lleva dos verbos, contra la regla UAX |
| **GATE-04** Metodología | 2026-09-01 | `PASS_WITH_OBSERVATIONS` | `docs/methodology/`, `docs/plan_experimental_macbook.md` | Diseño coherente, con una variable manipulada y todo lo demás fijo. Pendiente: I-05 (M6 sin subpregunta) |
| **GATE-05** Evidencia | 2026-09-01 | `BLOCKED` | `research/references/evidence-matrix.md` | No hay claims redactados que evaluar. Se evalúa al redactar |
| **GATE-06** Integridad experimental | 2026-09-01 | `PASS_WITH_OBSERVATIONS` | `reproducibility.md`; E1, E2 | E1 y E2 reproducibles y verificadas. Observación: el pre-registro canónico no está congelado (L-07) |
| **GATE-07** Resultados | 2026-09-01 | `BLOCKED` | `results/RESULTADOS_TFM.md` | «Estado: sin resultados». Nada que verificar |
| **GATE-08** Discusión | 2026-09-01 | `BLOCKED` | — | Sin resultados no hay discusión |
| **GATE-09** Conclusiones | 2026-09-01 | `BLOCKED` | — | Ídem |
| **GATE-10** Referencias | 2026-09-01 | `PASS_WITH_OBSERVATIONS` | `research/references/` | 144 entradas consolidadas, todas localizadas en el texto, 0 huérfanas. Observaciones: 31 títulos elididos, 33 sin identificador persistente, discrepancia 144 vs 153 declaradas, PRISMA formal pendiente |
| **GATE-11** UAX | 2026-09-01 | `BLOCKED` | `references/uax/conflictos-uax.md` | Tres cifras de extensión incompatibles entre documentos oficiales. Decisión del autor con el tutor |
| **GATE-12** Humanización | — | no procede | — | No se ejecuta antes del gate académico |
| **GATE-13** Integridad global | 2026-09-01 | `PASS` | este directorio | Ninguna evidencia inventada. Todos los huecos marcados. Ningún resultado adaptado a las hipótesis |

## Regla de parada

Los dos `FAIL` son de **coherencia**, no de integridad: se corrigen reformulando objetivos y
ampliando la revisión documental, no experimentando. **Pero se corrigen antes de redactar los
capítulos 2 y 3.**

Ningún gate de integridad (05, 06, 07, 10, 13) está en `FAIL`.
