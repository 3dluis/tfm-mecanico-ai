# Registro de limitaciones

**Inventario, no redacción.** Este documento recoge limitaciones **encontradas en evidencia
real**, no las que suelen aparecer en un TFM. El apartado 6.1 de la memoria se redacta a
partir de aquí, y no antes de tener resultados.

**Prohibidas las limitaciones ceremoniales.** Cada entrada declara: qué limita · por qué ·
qué resultado afecta · qué consecuencia tiene · cómo podría comprobarse.

**Severidad:** `crítica` (invalida una conclusión) · `alta` (acota el alcance de una
afirmación) · `media` (obliga a matizar) · `baja` (se declara y ya).

Fecha: 1 de septiembre de 2026, 15:00 (actualizado tras el cierre de E4, E5 y E6).

---

## L-01 — Los datos sintéticos no tienen validez externa

| Campo | Contenido |
|---|---|
| **Qué limita** | Toda conclusión sobre el comportamiento del sistema con datos de vehículos reales |
| **Por qué** | El generador de E2 es paramétrico y **no está calibrado contra datos reales**. Lo declara el propio informe: «no aporta validez externa […] ninguna conclusión sobre datos reales puede apoyarse en estos datos» |
| **Evidencia** | `mecanico-ia-exp/docs/experiments/E2_datos_sinteticos.md` |
| **Afecta a** | PI.1 directamente; a PI.2-PI.4 en cuanto a generalización |
| **Consecuencia** | La pregunta de investigación no exige datos reales (ADR-003, 3-09-2026), pero un resultado sobre sintéticos caracteriza el comportamiento ante los mecanismos representados, no ante un vehículo real. Toda conclusión se acota a la procedencia declarada del dato |
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

## L-10 — La afirmación de novedad sobre PI.4 es más estrecha de lo que parecía · **resuelta parcialmente**

| Campo | Contenido |
|---|---|
| **Qué limita** | Lo que puede afirmarse como novedoso en PI.4 |
| **Por qué** | La búsqueda del 1 de septiembre **refutó** la hipótesis de que la distinción presencia/pertinencia estuviera poco cubierta. Está estudiada, tiene banco público (RGB) y vocabulario establecido: «rechazo negativo» y «robustez contrafactual» (Chen et al., 2024) |
| **Evidencia** | `references/project/gaps.md` GAP-02; `search-log.md` iteración 5 |
| **Afecta a** | Capítulo 3 y la defensa de PI.4 |
| **Consecuencia** | **PI.4 gana motivación y pierde novedad amplia.** No es «nadie lo mide»: es «no fue identificada esa medición a nivel de afirmación, con doble rama de evidencia, en diagnóstico vehicular». El proyecto debe **adoptar el vocabulario existente** en lugar de inventar el suyo |
| **Cómo comprobarlo** | Leer a texto completo los cuatro trabajos identificados y confirmar que ninguno cubre las tres condiciones |
| **Severidad** | **media** (era alta) |
| **Estado** | GATE-02 pasa de `FAIL` a `PASS_WITH_OBSERVATIONS` |

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

## L-14 — La confianza del baseline está mal calibrada

| Campo | Contenido |
|---|---|
| **Qué limita** | El criterio de suficiencia de E15, que toma la confianza del modelo como una de sus cuatro señales |
| **Por qué** | Error de calibración esperado **0,140**, con el modelo **infra**confiado: confianza media 0,738 frente a 0,878 de acierto. Es lo habitual en un conjunto de árboles, donde la probabilidad es una proporción de votos |
| **Evidencia** | E6, hallazgo 3 |
| **Afecta a** | E15, M5, y por tanto PI.3 |
| **Consecuencia** | Un umbral sobre la confianza **se abstendría más de lo debido**. El sistema parecería prudente cuando en realidad está mal medido, y la tasa de falsa abstención mediría el defecto del instrumento, no la política |
| **Cómo comprobarlo** | Calibrar las probabilidades **sobre validación** antes de fijar el umbral, y volver a medir el ECE |
| **Severidad** | **alta** |

## L-15 — Dos de las seis condiciones no son plenamente detectables, y por motivos distintos

| Campo | Contenido |
|---|---|
| **Qué limita** | La exhaustividad alcanzable en F03 y F05, y con ella el techo de M1 |
| **Por qué** | **F03 (termostato bloqueado)**: límite **físico**. El fallo impone un techo de 71 °C; mientras el motor no lo habría superado por sí mismo, la señal averiada es **idéntica** a la sana. Detectadas 70,7 °C de media, no detectadas 54,3 °C; urbano 7/7, calentamiento 2/7. **F05 (fallo de encendido)**: efecto 0,734 frente a un suelo de ruido de 0,512, apenas 1,43 veces |
| **Evidencia** | E6, hallazgos 1 y 2; E5, hallazgo 1 |
| **Afecta a** | M1 (exhaustividad 0,643 y 0,500), y el techo de E7 |
| **Consecuencia** | **F03 no es una debilidad del modelo: es un límite de la evidencia.** Ningún clasificador puede distinguir dos señales idénticas. F05 sí es difícil por relación señal-ruido, y estaba anticipado por escrito antes de medirlo |
| **Cómo comprobarlo** | E7 puede ganar margen en F03 y F05 —son las dos de firma temporal—; en las otras cuatro no queda margen |
| **Severidad** | **media** |
| **Nota** | **No se sube la severidad de ningún fallo para mejorar el número.** Un experimento sobre suficiencia de evidencia necesita casos difíciles |

## L-16 — El descriptor informado por la física no está validado con datos reales

| Campo | Contenido |
|---|---|
| **Qué limita** | La transferibilidad de `maf_over_rpm_load`, tercer descriptor más influyente del baseline |
| **Por qué** | Se construyó para responder al hallazgo de E4 sobre la dependencia conjunta régimen × carga, y está marcado `[VERIFY_ON_REAL_DATA]` |
| **Evidencia** | E6, descriptores más influyentes |
| **Afecta a** | M1, y la interpretación de E9 |
| **Consecuencia** | Un descriptor derivado del modelo generativo puede funcionar bien precisamente porque el generador lo produjo así. Con datos reales podría no aportar nada |
| **Cómo comprobarlo** | Repetir E6 sobre el conjunto real de E3 |
| **Severidad** | **media** |

## L-17 — Todas las cifras disponibles son de validación

| Campo | Contenido |
|---|---|
| **Qué limita** | Lo que puede afirmarse hoy sobre el rendimiento del sistema |
| **Por qué** | El conjunto de test está **cerrado hasta E19**, por diseño y con cierre técnico: `load_partition("test")` lanza excepción salvo `allow_test=True` más una razón escrita que se imprime |
| **Evidencia** | E6, «El test, bajo llave» |
| **Afecta a** | Toda cifra publicada antes de E19 |
| **Consecuencia** | **Ninguna cifra actual es un resultado del TFM**: son la referencia contra la que se medirá. Reportarlas como resultado sería describir datos ya vistos |
| **Cómo comprobarlo** | E19 |
| **Severidad** | **baja** — es una restricción deliberada, no un defecto. Se registra para que nadie confunda validación con resultado |


---

---

## L-18 — Dos ejecuciones con resultado negativo no llegaron al capítulo de resultados

| Campo | Contenido |
|---|---|
| **Qué limita** | La cobertura de lo publicado respecto de lo ejecutado |
| **Por qué** | El experimento de suficiencia se ejecutó también en una variante que retira el conocimiento de la etiqueta anotada (NX-01) y en un escenario adverso donde el modelo especializado se equivoca (NX-02). El capítulo 5 quedó congelado antes de que ninguna de las dos se incorporase |
| **Evidencia** | `experiments/E15_suficiencia_non_oracle.json`, `docs/experiments/resultado-no-oracular-y-adverso.md`, `docs/methodology/politica-evaluacion-no-oracular.md` |
| **Afecta a** | El quinto objetivo, que se compromete expresamente a documentar los resultados negativos |
| **Consecuencia** | La variante no oracular acota de dónde procede el auxilio del oráculo y el escenario adverso contiene evidencia de comportamiento ante un diagnóstico incorrecto; ninguna de las dos cosas puede leerse en el capítulo de resultados |
| **Cómo comprobarlo** | Incorporarlas cuando el capítulo 5 deje de estar congelado |
| **Severidad** | **alta** — omite evidencia negativa que el propio objetivo obliga a publicar |

---

## L-19 — Los resultados describen un solo vehículo

| Campo | Contenido |
|---|---|
| **Qué limita** | El alcance de generalización de toda cifra publicada |
| **Por qué** | El trabajo se apoya en un Mazda 3 BK de 2007 con motor Z6 y en su manual de taller. La elección garantiza por construcción la coherencia entre telemetría, códigos de avería y procedimientos documentales, que es exactamente lo que no puede darse por supuesto en otro vehículo |
| **Evidencia** | Capítulo 4, selección del vehículo entre tres candidatos; ficha de calibración |
| **Afecta a** | Todos los resultados del capítulo 5 |
| **Consecuencia** | Los resultados no se generalizan a otros modelos, a otras generaciones del mismo modelo ni a los otros dos motores documentados en el corpus: otro fabricante puede usar códigos distintos para la misma condición, estructurar sus procedimientos de otra forma o no publicar un manual accesible |
| **Cómo comprobarlo** | Repetir el trabajo sobre un vehículo con documentación equivalente |
| **Severidad** | **alta** — acota el alcance de toda afirmación del trabajo |

---

---

## L-21 — El catálogo de fallos del modelo de diagnóstico es cerrado

| Campo | Contenido |
|---|---|
| **Qué limita** | El alcance de lo que el sistema puede diagnosticar |
| **Por qué** | El modelo es un clasificador supervisado sobre cinco clases de fallo etiquetadas. Una avería ajena a ese catálogo no puede asignarse a ninguna clase |
| **Evidencia** | `CANONICAL_SIGNALS` y `fault_ids` del generador; búsqueda de `out_of_distribution`, `unseen`, `open_set` en `src/`: cero coincidencias |
| **Afecta a** | La generalización a averías no representadas en el conjunto de entrenamiento |
| **Consecuencia** | El trabajo no examina el comportamiento del sistema ante fallos fuera del catálogo. No es un resultado negativo: queda fuera del alcance acordado con la dirección el 12 de septiembre de 2026 |
| **Cómo comprobarlo** | Una condición experimental que retenga una clase fuera del entrenamiento y del diccionario de recuperación. Diseñada en `docs/methodology/diseno-gates-pi-pendientes.md`, fuera del alcance de este TFM |
| **Severidad** | **media** — acota el alcance, no invalida ningún resultado |

---

## L-27 — Tres de los cuatro criterios de aceptación se reformularon después de ver resultados

| Campo | Contenido |
|---|---|
| **Qué limita** | La fuerza confirmatoria del dictamen sobre la pregunta de investigación |
| **Por qué** | Los criterios de las cuatro subpreguntas se congelaron el 1-09-2026 a las 13:21 (`eaee16c`), antes de entrenar. A las 15:06 entraron E6 y E7 (`27b9f8d`): bosque aleatorio 0,879 de F1 macro frente a 0,823 del GRU bidireccional, de modo que el modelo temporal no superó a la línea base y el criterio original de PI.1 no se cumplió. El 2-09-2026 a las 14:28 (`3f8eac3`) la Tabla 4.6 se escribió sin esa exigencia. Los de PI.2 y PI.3 remitían a umbrales que la primera versión dejó en blanco a propósito y que nunca se escribieron |
| **Evidencia** | `docs/methodology/criterio-pi1-enmienda-01.md`; `docs/matriz_validacion_pi.md` en `eaee16c`; `experiments/E6_baseline_synthetic_v2.json` y `experiments/E7_temporal_synthetic_v2.json` |
| **Afecta a** | El dictamen global y los criterios de PI.1, PI.2 y PI.3. PI.4 se conserva en sustancia |
| **Consecuencia** | Los tres criterios pasaron de una exigencia cuantitativa y comparada a una cualitativa y existencial, de modo que el trabajo responde a una pregunta más estrecha que la del pre-registro. El dictamen «sostenida» describe cumplimiento de criterios operativos y no es una confirmación independiente del protocolo original. Con los criterios originales no existe valor aplicable de la regla de respuesta global, porque la calificación parcial exige que PI.1 se cumpla |
| **Cómo comprobarlo** | Un pre-registro con umbrales escritos y réplicas suficientes para evaluar un margen, fijado antes de cualquier medición y no modificado después. Fuera del alcance de este trabajo, cuyos registros ya existen |
| **Severidad** | **alta** — no invalida ninguna cifra y acota lo que el dictamen puede afirmar |

---

## Resumen

| Severidad | Entradas |
|---|---|
| crítica | 2 — L-01, **L-20** |
| alta | 11 — L-02, L-03, L-06, L-07, L-08, L-10, L-11, L-13, **L-14**, **L-18**, **L-19** |
| media | 6 — L-05, L-09, L-12, **L-15**, **L-16**, **L-21** |
| baja | 2 — L-04, **L-17** |

Veintiuna entradas. L-18 y L-19 se dieron de alta el 10 de septiembre de 2026 al redactarse el
apartado 6.1, y L-20 el 4 de septiembre. **L-22, sobre la incorporación de conocimiento
reutilizable, se retiró el 12 de septiembre**: pertenecía a una formulación de la pregunta que
la dirección descartó, y lo que no está en la pregunta no puede ser una limitación de su
respuesta. L-21 se reformula en los mismos términos y baja a severidad media.

**Ninguna de estas limitaciones es ceremonial.** Todas proceden de un informe de fase, de un
documento de método o de un documento oficial. Ninguna se ha añadido porque «suele aparecer».

## Lo que todavía no se puede registrar

`[EXPERIMENT_REQUIRED]` — las limitaciones que se descubran al ejecutar: comportamiento del
modelo por clase, calidad real de la recuperación, tasa de falsa abstención, coste de la
política. Se añaden aquí cuando existan, no antes.

---

## L-20 · Espacios de embeddings mezclados en toda la recuperación

**Severidad:** crítica · **Fecha:** 4 de septiembre de 2026 · **Estado:** corregida en código,
reejecución canónica pendiente · **Hallazgo:** `MIXED-EMBEDDING-SPACE`.

El índice contiene dos representaciones vectoriales de cada uno de los 6 158 fragmentos,
procedentes de dos modelos distintos, y ninguna búsqueda declaraba en cuál de los dos buscaba.
Cada consulta ordenó por proximidad sobre 12 316 vectores de dos espacios semánticos
incompatibles.

**Alcance:** las tres rutas que recuperan —suficiencia, recuperación y agente, y generación de
datos de ajuste—. Cuatro tablas del capítulo 5 dependen de ellas.

**Consecuencia:** la procedencia de cada fragmento recuperado es indeterminada. Las cifras
publicadas son reproducibles y no canónicas.

**Documentación:** `docs/methodology/politica-espacio-de-embeddings.md`,
`docs/methodology/preregistro-rerun-a.md`.
