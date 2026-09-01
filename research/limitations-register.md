# Registro de limitaciones

**Inventario, no redacción.** Este documento recoge limitaciones **encontradas en evidencia
real**, no las que suelen aparecer en un TFM. El apartado 6.1 de la memoria se redacta a
partir de aquí, y no antes de tener resultados.

**Prohibidas las limitaciones ceremoniales.** Cada entrada declara: qué limita · por qué ·
qué resultado afecta · qué consecuencia tiene · cómo podría comprobarse.

**Severidad:** `crítica` (invalida una conclusión) · `alta` (acota el alcance de una
afirmación) · `media` (obliga a matizar) · `baja` (se declara y ya).

Fecha: 1 de septiembre de 2026.

---

## L-01 — Los datos sintéticos no tienen validez externa

| Campo | Contenido |
|---|---|
| **Qué limita** | Toda conclusión sobre el comportamiento del sistema con datos de vehículos reales |
| **Por qué** | El generador de E2 es paramétrico y **no está calibrado contra datos reales**. Lo declara el propio informe: «no aporta validez externa […] ninguna conclusión sobre datos reales puede apoyarse en estos datos» |
| **Evidencia** | `mecanico-ia-exp/docs/experiments/E2_datos_sinteticos.md` |
| **Afecta a** | PI.1 directamente; a PI.2-PI.4 en cuanto a generalización |
| **Consecuencia** | La pregunta de investigación habla de **datos OBD-II reales**. Con solo sintéticos, el trabajo responde a una pregunta más estrecha que la enunciada |
| **Cómo comprobarlo** | Cerrar E3 con una fuente real y repetir al menos E8 y E17 sobre ella |
| **Severidad** | **crítica** |
| **Mitigación** | Si el dato real es escaso, reservarlo íntegro para validación y demostración (previsto en el plan, §6) |

## L-02 — Dos de los cinco fallos son invisibles en las medias

| Campo | Contenido |
|---|---|
| **Qué limita** | La detectabilidad de la sonda lenta y el fallo de encendido si los descriptores se limitan a medias por ventana |
| **Por qué** | Su firma es temporal, no de nivel. La desviación típica de la sonda cae de 0,250 a 0,033 —invisible en media, evidente en varianza—. El fallo de encendido altera el 5,7 % de los instantes, con caída media de −218 rpm, pero en el agregado la desviación típica de la variación de régimen sube solo de 115,4 a 117,1 |
| **Evidencia** | E2, hallazgo 2 |
| **Afecta a** | E5 (descriptores), E6-E8 (aprendibilidad), M1 |
| **Consecuencia** | Los descriptores por ventana **no pueden limitarse a medias**, o dos de las cinco condiciones son indetectables por construcción. Y no se da por supuesto que el fallo de encendido sea aprendible: es una pregunta empírica |
| **Cómo comprobarlo** | Descriptores con varianza, conteo de eventos y extremos en E5; medir por clase en E8 |
| **Severidad** | **alta** |
| **Nota** | Si resulta que no es aprendible, se reporta como tal. **No se subirá su severidad para forzar un resultado favorable** |

## L-03 — Las fichas de fallo no tienen respaldo documental verificado

| Campo | Contenido |
|---|---|
| **Qué limita** | La posibilidad de que una explicación se sostenga sobre la firma declarada de un fallo |
| **Por qué** | Las cinco fichas llevan `source = [EVIDENCE_REQUIRED]`. Ninguna firma tiene todavía respaldo documental |
| **Evidencia** | E2, «respaldo documental pendiente» |
| **Afecta a** | E10 (corpus), E14 (trazabilidad), M4 |
| **Consecuencia** | Un fallo cuya firma no llegue a tener respaldo **no podrá sostener una explicación**, y eso será un resultado, no un defecto |
| **Cómo comprobarlo** | E10: construir el corpus y comprobar cobertura documental por mecanismo |
| **Severidad** | **alta** |

## L-04 — El reparto por régimen de conducción está desequilibrado

| Campo | Contenido |
|---|---|
| **Qué limita** | La interpretación del análisis exploratorio por régimen |
| **Por qué** | Reparto cíclico de 6 sesiones entre 4 regímenes: urbano 12, autovía 12, ralentí 6, calentamiento 6 |
| **Evidencia** | E2, dataset generado |
| **Afecta a** | E4 |
| **Consecuencia** | **Las clases sí están equilibradas**, que es lo que afecta a las métricas. El desequilibrio es de régimen, y solo sesga la lectura por régimen |
| **Cómo comprobarlo** | Reportar por régimen y por clase por separado |
| **Severidad** | **baja** |

## L-05 — Una correlación marginal baja no implica ausencia de relación

| Campo | Contenido |
|---|---|
| **Qué limita** | La interpretación de la atribución en E9 |
| **Por qué** | El caudal depende del **producto** régimen × carga: r(régimen, caudal) va de 0,067 a −0,213 según el régimen, mientras que r(régimen × carga, caudal) llega a 1,000. En autovía la correlación marginal es negativa |
| **Evidencia** | E2, hallazgo 1 |
| **Afecta a** | E9, y la lectura de cualquier diagrama bivariante |
| **Consecuencia** | Una señal puede ser determinante sin destacar en un diagrama bivariante. Si no se tiene presente, **se descartarán como irrelevantes señales que sí lo son** |
| **Cómo comprobarlo** | Comprobar relaciones conjuntas, no solo marginales, antes de descartar una señal |
| **Severidad** | **media** |

## L-06 — La atribución no es causalidad

| Campo | Contenido |
|---|---|
| **Qué limita** | Lo que puede afirmarse a partir de la salida de E9 |
| **Por qué** | La atribución indica de qué depende la salida del modelo, no qué le ocurre al vehículo. Un descriptor puede dominar por estar correlacionado con la causa real sin serlo |
| **Evidencia** | `docs/methodology/evidence-model.md` |
| **Afecta a** | E9, E14, y toda afirmación de la explicación anclada en evidencia observacional |
| **Consecuencia** | Ningún artefacto —código, figura o texto— puede presentar la atribución como causa |
| **Cómo comprobarlo** | Es una restricción de diseño, no una hipótesis. Se verifica por revisión de artefactos |
| **Severidad** | **alta** (de validez de constructo) |

## L-07 — Se abandonó un pre-registro ya congelado

| Campo | Contenido |
|---|---|
| **Qué limita** | La fuerza del compromiso pre-registrado del trabajo |
| **Por qué** | ADR-001 sustituyó el marco experimental. `prereg-v1.0` estaba congelado desde el 2026-08-18 con enmienda ENM-001; el marco canónico todavía no tiene documento congelado equivalente |
| **Evidencia** | `research/prereg-classification.md`, ADR-002 |
| **Afecta a** | La credibilidad de los criterios de aceptación de E15 y E19 |
| **Consecuencia** | Hasta que el pre-registro canónico se congele con fecha, la distancia entre «umbral calibrado sobre validación» y «umbral elegido tras ver resultados» depende de la palabra del autor |
| **Cómo comprobarlo** | Congelar el pre-registro canónico con fecha y hash, y decidir su momento (ADR-002) |
| **Severidad** | **alta** |
| **Nota** | El pre-registro anterior **no se ha reescrito**: se conserva íntegro y se ha clasificado. Esa conservación es lo que permite declarar esta limitación en lugar de ocultarla |

## L-08 — El barrido documental no es un flujo PRISMA formal

| Campo | Contenido |
|---|---|
| **Qué limita** | La afirmación sobre el estado del conocimiento y, por tanto, la fuerza del vacío |
| **Por qué** | La búsqueda se ejecutó mediante buscador web general con verificación en editor. El acceso automatizado a IEEE Xplore y ScienceDirect estuvo parcialmente bloqueado |
| **Evidencia** | `research/references/search-log.md`; entregas 1-3 |
| **Afecta a** | Capítulo 3 y la formulación del vacío |
| **Consecuencia** | Los recuentos (≈1 350 registros, ≈170 consultas, ≈250 candidatos, 153 incluidas) describen el barrido preliminar. El vacío se formula como «no fue identificado en los trabajos analizados», **nunca como inexistencia** |
| **Cómo comprobarlo** | Ejecutar las cadenas en Scopus, WoS e IEEE con acceso institucional; la sintaxis está preparada |
| **Severidad** | **alta** |

## L-09 — Tres trabajos relevantes sin leer a texto completo

| Campo | Contenido |
|---|---|
| **Qué limita** | El detalle de los vacíos, no su formulación integradora |
| **Por qué** | Takara et al. (ESWA 2025), Min et al. (EAAI 2024), Onsu et al. (IoT 2025): metadatos recuperados, texto completo no leído |
| **Evidencia** | `research/references/excluded-sources.md` |
| **Afecta a** | Capítulo 3 |
| **Consecuencia** | Si al leerlos cambiara alguna conclusión sustantiva, se corrige el capítulo y **se declara el cambio** |
| **Cómo comprobarlo** | Leerlos antes del depósito |
| **Severidad** | **media** |

## L-10 — El vacío no cubre la pertinencia de la evidencia

| Campo | Contenido |
|---|---|
| **Qué limita** | La justificación de PI.4 |
| **Por qué** | El vacío vigente enumera cuatro elementos y **no menciona la distinción presencia/pertinencia**, que es lo que mide la condición DISTRACTOR |
| **Evidencia** | `research/traceability-matrix.md` I-03 |
| **Afecta a** | Capítulo 3, y la defensa de PI.4 |
| **Consecuencia** | **PI.4 es hoy una subpregunta sin vacío que la respalde** |
| **Cómo comprobarlo** | Ampliar la revisión al rechazo de distractores en sistemas RAG y reformular el vacío con la búsqueda que lo sostenga |
| **Severidad** | **alta** |

## L-11 — El presupuesto de cómputo se mide sobre hardware de sobremesa

| Campo | Contenido |
|---|---|
| **Qué limita** | Toda afirmación sobre viabilidad en el borde |
| **Por qué** | M6 se mide sobre un MacBook Pro M4 Pro con 24 GB, no sobre hardware embarcado. El despliegue en Raspberry Pi es `FUTURE` en el plan canónico |
| **Evidencia** | `docs/plan_experimental_macbook.md` §3 y §4.6 |
| **Afecta a** | M6 |
| **Consecuencia** | **No se declarará validado en hardware embarcado nada que no se haya probado en él.** Y la propuesta aprobada por la universidad describía un prototipo sobre Raspberry Pi: la diferencia hay que declararla |
| **Cómo comprobarlo** | Ejecutar la medición sobre el dispositivo objetivo |
| **Severidad** | **alta** |

## L-12 — Se desconoce si el juez basado en modelo de lenguaje es fiable aquí

| Campo | Contenido |
|---|---|
| **Qué limita** | La interpretación de M3 |
| **Por qué** | Un juez basado en modelo de lenguaje es un instrumento con sesgos conocidos. El diseño lo restringe a apoyo, con contraste contra anotación manual sobre una submuestra |
| **Evidencia** | `docs/methodology/metrics.md`, M3 |
| **Afecta a** | M3 |
| **Consecuencia** | M3 no puede decidir nada por sí sola. Refuerzo legacy (LEG-E04): 20 de 20 salidas bien formadas con cero información diagnóstica |
| **Cómo comprobarlo** | Medir el acuerdo juez-anotación en la submuestra y reportarlo |
| **Severidad** | **media** |

## L-13 — El alcance ejecutado es más estrecho que el alcance aprobado

| Campo | Contenido |
|---|---|
| **Qué limita** | La correspondencia entre lo comprometido en la propuesta y lo entregado |
| **Por qué** | La propuesta aprobada (14-07-2026) describe un prototipo con Raspberry Pi, aplicación móvil, plataforma en la nube y mantenimiento predictivo, con **13 objetivos específicos**. El trabajo actual investiga el soporte y la abstención de explicaciones diagnósticas, con 5 objetivos |
| **Evidencia** | `Propuesta temática TFM - Luis Daniel Díaz.pdf`; `references/project/propuesta-aprobada.md` |
| **Afecta a** | Capítulos 1, 2 y 6 |
| **Consecuencia** | El recorte está justificado y documentado internamente, pero **la universidad tiene registrado el alcance amplio**. La sesión informativa indica que el título definitivo se consensúa con el director |
| **Cómo comprobarlo** | Comunicarlo al director en la próxima reunión y dejar constancia |
| **Severidad** | **alta** — administrativa, no científica |

---

## Resumen

| Severidad | Entradas |
|---|---|
| crítica | 1 (L-01) |
| alta | 7 (L-02, L-03, L-06, L-07, L-08, L-10, L-11, L-13) |
| media | 3 (L-05, L-09, L-12) |
| baja | 1 (L-04) |

**Ninguna de estas limitaciones es ceremonial.** Todas proceden de un informe de fase, de un
documento de método o de un documento oficial. Ninguna se ha añadido porque «suele aparecer».

## Lo que todavía no se puede registrar

`[EXPERIMENT_REQUIRED]` — las limitaciones que se descubran al ejecutar: comportamiento del
modelo por clase, calidad real de la recuperación, tasa de falsa abstención, coste de la
política. Se añaden aquí cuando existan, no antes.
