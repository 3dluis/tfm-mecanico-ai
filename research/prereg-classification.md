# Clasificación del pre-registro heredado

**Fuente:** `mecanico-ia/docs/experiments/pre-registro-v1.md` (`prereg-v1.0`, congelado el
2026-08-18; enmienda vigente **ENM-001**). 490 líneas.

**Regla de esta clasificación, no negociable:** el pre-registro antiguo **no se reescribe, no
se recorta y no se ajusta** para hacerlo coincidir con el marco actual. Se conserva íntegro
en el repositorio legacy. Lo que se hace aquí es **etiquetar** cada elemento según su
vigencia bajo el marco canónico (ADR-001).

**La evolución metodológica también es evidencia del proceso de investigación.** Un
pre-registro que dejó de aplicarse, con el motivo escrito, dice más sobre el rigor del
trabajo que uno reescrito para que encaje.

## Etiquetas

| Etiqueta | Significado |
|---|---|
| `STILL_APPLICABLE` | Sigue vigente tal cual bajo el marco canónico |
| `SUPERSEDED` | Sustituido por un elemento del marco canónico |
| `PARTIALLY_APPLICABLE` | Parte vigente, parte no; se indica cuál |
| `OUT_OF_SCOPE` | Fuera del alcance actual; diseño conservado, no evaluado |
| `REQUIRES_DECISION` | El autor debe decidir; el skill no lo resuelve |

---

## §2 — Principios vinculantes

| Elemento | Etiqueta | Nota |
|---|---|---|
| Pre-registrar antes de ejecutar | `STILL_APPLICABLE` | Principio, no diseño. El marco canónico lo aplica en la matriz de validación y en E15/E19 |
| **Held-out intocable**: splits congelados, nunca usados para ajustar modelos, umbrales, prompts, corpus ni memoria | `STILL_APPLICABLE` | Equivale al «test cerrado hasta E19» del marco canónico. **Es el mismo principio con otro nombre** |
| Benchmark inmutable, congelado antes de ver salidas | `STILL_APPLICABLE` | Se aplicará al conjunto de casos de referencia de E17 |
| Sin paradas opcionales ni repesca; no añadir n; no repetir runs «para confirmar»; no cambiar de métrica tras ver datos (§8) | `STILL_APPLICABLE` | Principio estadístico, independiente del marco. **Se adopta literalmente** |
| Los casos `FAILED` cuentan como diagnóstico incorrecto y **no se excluyen del denominador** (§9) | `STILL_APPLICABLE` | Regla de honestidad en el recuento. Se adopta |

## §1 y §6 — Definiciones operativas congeladas

| Elemento | Etiqueta | Nota |
|---|---|---|
| Definición de «patrón no representado» mediante triple exclusión **E-DET / E-RAG / E-MEM** | `PARTIALLY_APPLICABLE` | **E-RAG** es el antecedente directo de la condición `ABSENT` y se conserva en su lógica. **E-DET** equivale al aislamiento del conjunto de test. **E-MEM** queda `OUT_OF_SCOPE`: el marco canónico no tiene memoria evolutiva |
| «No se afirma descubrimiento de fallos desconocidos para la ingeniería automotriz» | `STILL_APPLICABLE` | Prudencia de alcance. Sigue vigente y es coherente con las cuatro afirmaciones prohibidas del plan canónico |
| Criterios de segmentación de eventos, taxonomía v1, detector `ed:1` | `OUT_OF_SCOPE` | El marco canónico no segmenta eventos: ventana temporal y descriptores (E5) |
| Banco `cases_v2`, `suite_v2`, splits congelados | `PARTIALLY_APPLICABLE` | Son datos legacy. **No son el banco canónico.** Candidatos a import como material de contraste; ver `legacy-map.md` |
| **Juez basado en modelo de lenguaje calibrado**: juez ≠ generador, prompts congelados, orden aleatorizado con semilla, temperatura 0 | `STILL_APPLICABLE` | El marco canónico exige lo mismo en M3, más contraste con anotación manual sobre submuestra. **Se adopta y se refuerza** |

## §3.4 — Criterio transversal edge

| Elemento | Etiqueta | Nota |
|---|---|---|
| Presupuesto de cómputo del perfil edge como criterio de aceptación transversal | `REQUIRES_DECISION` | El marco canónico mide latencia, tamaño de modelo y coste de recuperación (M6) **sobre un MacBook M4 Pro**, no sobre hardware embarcado. El presupuesto edge era un criterio de aceptación del marco anterior. **¿Sigue siendo criterio de aceptación, o pasa a ser una medición descriptiva?** `[AUTHOR_DECISION_REQUIRED]` |

Esta decisión no es menor: si el presupuesto edge deja de ser criterio, la pregunta de
investigación pierde su componente transversal y hay que decirlo. Si se mantiene, hace falta
declarar sobre qué hardware se comprueba.

## §4 — Hipótesis confirmatorias

| Hipótesis | Etiqueta | Motivo |
|---|---|---|
| **H-EVT** — el contexto por eventos mejora la detección | `OUT_OF_SCOPE` | Línea instrumental sobre la segmentación de eventos, que el marco canónico no usa |
| **H-MEM** — la memoria validada mejora el razonamiento | `OUT_OF_SCOPE` | Ya declarada fuera de alcance en la alineación v4 (ADR-0036). El marco canónico la excluye explícitamente como `FUTURE` |
| **H-MAS** — la descomposición multiagente aporta valor | `OUT_OF_SCOPE` | Ídem |
| **H-PERS** — la personalización por vehículo mejora frente al modelo global | `OUT_OF_SCOPE` | Condicionada a una decisión (D2) que ya no se toma |
| **H-EXP** — la verificación de hipótesis mejora la exactitud factual | `SUPERSEDED` | Sustituida por **PI.2** (trazabilidad) y las métricas **M4**. La idea sobrevive; el diseño no |
| **H-MAIN** — el sistema integrado señala, hipotetiza y explica patrones held-out | `SUPERSEDED` | Sustituida dos veces: por H-MAIN v4 en la alineación v4, y ahora por **PI.1-PI.4** |
| **EXP-SEG-001** — precondición de calidad de segmentación | `OUT_OF_SCOPE` | Precondición del marco anterior |

**Nota importante.** Cuatro de las seis hipótesis del pre-registro estaban ya fuera de alcance
antes de esta clasificación, por decisión propia del proyecto (alineación v4, ADR-0036). La
canonicalización no las descarta: **confirma un recorte que ya se había hecho**.

## §4.6 — Controles negativos CN1-CN9

| Elemento | Etiqueta | Nota |
|---|---|---|
| Catálogo CN1-CN9 congelado | `PARTIALLY_APPLICABLE` | **Candidato de import de alto valor.** En particular el control de **anclaje en distractor**, que el marco legacy ya contemplaba y que conecta directamente con la condición `DISTRACTOR` canónica |
| Controles ligados a memoria y multiagente | `OUT_OF_SCOPE` | Sin sujeto en el marco canónico |

Revisar CN1-CN9 uno a uno al diseñar E17 y E18 es trabajo con retorno: parte del catálogo ya
está pensado y validado.

## §7 — Protocolo anti-contaminación (retirada triple)

| Elemento | Etiqueta | Nota |
|---|---|---|
| Lógica de retirada del corpus con lista de documentos excluidos y hash registrados antes de ejecutar | `STILL_APPLICABLE` | **Es exactamente el mecanismo que construye la condición `ABSENT`.** El plan canónico lo clasifica como `REUSE`: «existe el mecanismo de excluir documentos explícitamente para construir corpus con evidencia completa, parcial o ausente» |
| Auditor ejecutable `tools/contamination_audit.py` con especificación declarativa | `STILL_APPLICABLE` | **Candidato de import prioritario.** Instrumento probado, con hallazgo real a su favor (detectó la violación de E-RAG en `corpus_v1`) |
| Búsqueda por similitud de embeddings sobre el corpus (top-k por firma) con revisión manual | `STILL_APPLICABLE` | Necesaria en cuanto E11 tenga recuperación densa |
| Regla: positivo ⇒ se retira el elemento, se re-audita, se documenta; el run afectado se invalida y se repite | `STILL_APPLICABLE` | Se adopta |
| Retirada de memoria (E-MEM) | `OUT_OF_SCOPE` | Sin memoria en el marco canónico |
| Estado declarado: `corpus_v1` viola E-RAG | `SUPERSEDED` como bloqueo | El corpus canónico se construye de nuevo en E10. **El hallazgo se conserva como evidencia metodológica** |

## §10 — Tabla maestra de experimentos

`SUPERSEDED` en bloque. Sustituida por las fases E1-E20 del plan canónico.

## §11 — Evidencia exploratoria previa

`PARTIALLY_APPLICABLE`. Es evidencia real, producida y publicada, pero bajo otro marco. Cada
estudio pasa por el control de relevancia de `legacy-map.md`. Ninguno entra por defecto.

## ENM-001

`SUPERSEDED`. Enmendaba el marco legacy incorporando `EXP-RET-001`. Ese experimento no existe
en el marco canónico.

**La enmienda no se retira ni se anula retroactivamente:** queda como parte del historial.

---

## Consecuencia: ¿hace falta un pre-registro nuevo?

**Sí, y es una decisión pendiente.**

El marco canónico tiene ya sus criterios de refutación escritos por adelantado
(`docs/matriz_validacion_pi.md`) y su regla de que los umbrales se calibran solo con
validación. Eso es la sustancia de un pre-registro. Lo que **no** tiene todavía es:

1. Los **umbrales numéricos**, que por diseño se fijan al cerrar E15 y no antes.
2. Un **documento congelado con fecha y hash** equivalente a `prereg-v1.0`.
3. El **catálogo de controles negativos** de E17/E18.

`[AUTHOR_DECISION_REQUIRED]` — Cuándo se congela el pre-registro canónico. Congelarlo antes
de E15 obligaría a dejar los umbrales en blanco; congelarlo después de E15 significa que los
umbrales entran por enmienda. La segunda opción es la que el propio plan describe, pero **hay
que declararla explícitamente**, porque la diferencia entre «umbral calibrado sobre
validación» y «umbral elegido después de ver resultados» es toda la diferencia.

## Resumen

| Etiqueta | Elementos |
|---|---|
| `STILL_APPLICABLE` | 11 |
| `PARTIALLY_APPLICABLE` | 4 |
| `SUPERSEDED` | 4 |
| `OUT_OF_SCOPE` | 7 |
| `REQUIRES_DECISION` | 2 |

Lo que sobrevive del pre-registro heredado no son sus hipótesis: son sus **principios
metodológicos** y su **instrumento de control de evidencia**. Eso, y no los resultados, es lo
más valioso que el marco legacy aporta al canónico.
