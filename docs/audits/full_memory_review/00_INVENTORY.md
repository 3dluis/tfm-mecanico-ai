# 00 · Inventario del trabajo

**Fecha:** 10 de septiembre de 2026 · **Estado:** `835a317` · **Alcance:** repositorio completo.

Autoridad, de mayor a menor: pregunta canónica vigente · decisiones registradas · evidencia
experimental congelada · observaciones del director · requisitos de la titulación · metodología
de investigación · documentación científica · skills de auditoría · mejoras editoriales.

## Memoria

| Fichero | Función | Estado | Relación con la pregunta | Observaciones |
|---|---|---|---|---|
| `00_resumen.md` | resumen | borrador | toda | se reescribe con la evaluación final |
| `cap1_introduccion.md` | problema, pregunta, alcance | redactado | enuncia la pregunta | contiene una reescritura previa sin confirmar; sus cuatro defectos corregidos el 10-09 |
| `cap2_objetivos.md` | objetivo general y OE1–OE5 | redactado, 3,1 páginas | traduce la pregunta en compromisos | tres enunciados divergen del aprobado: P-01, P-02, P-03 |
| `cap3_marco_teorico.md` | cuatro frentes y vacío | redactado | funda los conceptos | cada frente cierra con su límite de lo afirmable |
| `cap4_marco_metodologico.md` | población, variables, instrumentos, diseño | redactado, 13,5 páginas | describe cómo se responde | **el capítulo mejor alineado con el estado real** |
| `cap5_resultados.md` | resultados y discusión | **congelado** | evidencia | congelado por `MIXED-EMBEDDING-SPACE`; cinco discrepancias declaradas |
| `cap6_conclusiones.md` | conclusiones, limitaciones, prospectiva | redactado | responde | 20 limitaciones; conclusión acotada el 10-09 |
| `bibliografia.md` | referencias citadas | redactado | soporte | 34 identificadores, todos resueltos; cero marcas pendientes |
| `LEEME.md` | estado del trabajo | vigente | — | recoge lo que se retiró del cuerpo |
| `preguntas-abiertas-al-director.md` | decisiones pendientes | vigente | — | P-01 a P-04 |

## Decisiones registradas

| Documento | Qué decide | Estado |
|---|---|---|
| `ADR-001` | marco canónico: pregunta, subpreguntas, fases, métricas | vigente, enmendado por ADR-003 |
| `ADR-002` | evolución del diseño experimental | vigente |
| `ADR-003` | la pregunta deja de exigir datos reales | vigente |

## Metodología · 22 documentos

Cuatro grupos. **Criterios y sus enmiendas**: umbral y `ENM-U01`; suficiencia v2 y v2.1; puerta
de códigos; evaluación no oracular y `ENM-A01`. **Políticas de instrumento**: espacio de
embeddings, condición de distractor, vocabulario de señales, abstención, evidencia, métricas.
**Pre-registros**: `RERUN-A` con `ENM-S01`, `S02` y `S03`; evaluación multilingüe. **Transversal**:
diseño experimental, calibración del generador, líneas base, expresión académica, estados
provisionales, plan de reejecución.

## Experimentos

30 registros y 31 tablas. Los de suficiencia conservan **siete variantes congeladas**: tres
versiones del verificador, dos modos de oráculo y dos selecciones adversas. Ocho artefactos
previos a la corrección del espacio vectorial se conservan aparte con su procedencia marcada
como indeterminada.

## Código y pruebas

69 módulos y 25 ficheros de prueba. Las pruebas incluyen las que reproducen los tres hallazgos
del patrón recurrente —ausencia de información tratada como ausencia de restricción— y las que
fijan el contrato de la reejecución.

## Auditorías previas

Nueve informes de la evaluación integral del 10 de septiembre, en los directorios de informes del
escritorio: experimento, RAG, evidencia, estadística, referencias, autenticidad, tutor y
tribunal, más las iteraciones de OE4.

## Lectura del inventario

El trabajo tiene **más documentación metodológica que memoria**: 22 documentos de método frente a
8 capítulos. Esa proporción explica el diagnóstico compartido por tres auditorías: **las
salvaguardas están escritas y no siempre llegan al capítulo donde se afirma.**
