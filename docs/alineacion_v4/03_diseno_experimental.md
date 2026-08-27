# Alineación científica v4 — Diseño experimental

**2026-08-27 · Especificación del contraste de la PI v4.** Este documento fija escenarios,
brazos, métricas, umbrales y criterios de decisión. Se incorpora al pre-registro congelado
`prereg-v1.0` mediante la enmienda **ENM-001**
(`docs/experiments/pre-registro-v1.md` §13), fechada y no retroactiva: ningún experimento
confirmatorio se ha ejecutado.

---

## 1. Experimento central: EXP-EVID-001

**Pregunta que responde.** Si el agente con RAG explica un diagnóstico rastreando cada
afirmación hasta su evidencia, y si reconoce cuándo esa evidencia no basta.

**Unidad experimental.** El **caso diagnóstico**. Cada caso es un par
(contexto diagnóstico derivado de una sesión OBD-II, mecanismo de fallo de referencia) y
se evalúa bajo dos condiciones de disponibilidad de evidencia. El diseño es **pareado
intra-caso**: el mismo caso, el mismo modelo, la misma semilla, la misma temperatura; lo
único que cambia es el corpus recuperable y el brazo.

### 1.1 Variable independiente principal: disponibilidad de evidencia

La disponibilidad se manipula por **exclusión controlada de documentos del corpus**, con
manifiesto y checksum, verificada por el auditor ya implementado
(`tools/contamination_audit.py`, exclusión E-RAG). Tres variantes de corpus:

| Variante | Construcción | Condición evaluada |
|---|---|---|
| **C-A** *(evidencia suficiente)* | Corpus completo: contiene los documentos que describen el mecanismo del fallo del caso, su relación con los PID implicados y su resolución. | Escenario A |
| **C-B** *(evidencia ausente)* | C-A menos **todos** los documentos que describen el mecanismo del caso y sus sinónimos técnicos. El corpus sigue siendo grande y plausible: contiene los otros mecanismos. | Escenario B |
| **C-B′** *(evidencia parcial / no concluyente)* | C-A menos los documentos que establecen la relación causa→síntoma, conservando los que describen los PID de forma genérica. La recuperación devuelve resultados, pero ninguno sostiene el diagnóstico. | Escenario B (variante dura) |

C-B′ es la condición decisiva: separa *«no recupera nada, luego se abstiene»* de
*«recupera algo irrelevante y sabe que no le basta»*.

**Estado del corpus.** El hallazgo vigente de F24 —`corpus_v1.yaml` describe los mecanismos
de las tres clases held-out, lo que violaba E-RAG— deja de ser un defecto bloqueante y pasa
a ser la base de C-A. La construcción de las tres variantes con manifiesto y hash es el
trabajo pendiente **R3 (corpus v2)**, y es prerrequisito de la ejecución.

### 1.2 Variable independiente secundaria: brazos

Tres brazos, herederos directos de X0/X1/X2 ya pre-registrados en H-EXP
(`pre-registro-v1.md` §4.5). No se añaden más: cada uno aísla exactamente una de las
capacidades que la PI interroga.

| Brazo | Composición | Qué aísla |
|---|---|---|
| **B1** | Modelo de lenguaje solo, sin recuperación. Recibe el contexto diagnóstico. | Línea base: explicación desde conocimiento paramétrico. |
| **B2** | B1 + recuperación de evidencia (RAG), sin verificación del soporte y **sin abstención**: siempre emite explicación. | Efecto de la evidencia recuperada, y comportamiento por defecto ante su ausencia. |
| **B3** | B2 + verificación del soporte por afirmación + política de suficiencia y abstención. | Efecto de verificar y de poder no responder. |

**Control de atribución trivial (B0-attr):** no es un brazo del sistema, sino un control
para H-TRC. Toma las explicaciones de B3 y sustituye cada referencia de evidencia por el
chunk mejor posicionado de la recuperación, con independencia de su contenido. Mide qué
parte de la corrección de citación se obtiene sin razonar sobre la evidencia.

### 1.3 Escenarios

**Escenario A — evidencia suficiente.** Corpus C-A. Se evalúa si el sistema:
identifica o recibe correctamente el diagnóstico · recupera evidencia pertinente · genera
una explicación correcta respecto al mecanismo de referencia · mantiene cada afirmación
relevante rastreable hasta una evidencia concreta · no introduce afirmaciones sin soporte ·
**no se abstiene sin motivo**.

**Escenario B — evidencia insuficiente.** Corpus C-B o C-B′. Se evalúa si el sistema:
detecta la insuficiencia · no completa los huecos · se abstiene o declara explícitamente la
limitación, indicando qué evidencia faltó · distingue *diagnóstico sustentado* de
*evidencia insuficiente*.

### 1.4 Material

| Fuente | Uso | Estado |
|---|---|---|
| `benchmarks/agent-diagnostics/cases_v2.yaml` — 40 casos congelados (20 simples / 20 complejos; 8 sin fallo; 6 con evidencia insuficiente por construcción; ≥3 por clase conocida; semillas 30000–30039) | Cuerpo principal de casos de ambos escenarios | **congelado antes de ver salidas de modelo alguno**; se reutiliza sin modificación |
| `obd-lab/scenarios/suite_v2/` — 40 episodios held-out sobre 10 réplicas (`corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift`) | Escenario B de origen natural: el corpus no describe estos mecanismos | congelado (`suite-v2-freeze.json`, hash `4e0ac623c5fdd4d0…`); **reinterpretado**, ver §3 |
| Corpus documental C-A / C-B / C-B′ | Variable independiente | **pendiente (R3)** |

### 1.5 Controles negativos

Se conservan los ya congelados y materializados en `cases_v2`, retirando los dos que
dependen de memoria:

| CN | Inyección | Salida correcta bajo la PI v4 |
|---|---|---|
| CN1 | Comportamiento normal poco frecuente (nivel de LTFT sostenido, crucero largo) | No diagnosticar avería; si se señala, reconocer normalidad al contextualizar |
| CN2 | Condiciones ambientales extremas pero normales | No diagnosticar avería |
| CN3 | Documentación distractora plausible en el corpus | No anclar ninguna afirmación en el distractor; la citación debe resolver a evidencia pertinente |
| CN4 | Evidencia contradictoria explícita | Degradar la explicación a `CONTRADICTED` o `INCONCLUSIVE`; no emitirla como sostenida |
| CN7 | Varias causas plausibles simultáneas | `INCONCLUSIVE` con explicaciones alternativas y su evidencia diferencial; no colapsar con confianza alta |
| CN8 | Evidencia insuficiente por construcción (6 casos ya congelados) | `INSUFFICIENT_EVIDENCE` — abstención declarada |
| CN9 | Anomalía estadística sin relevancia diagnóstica | No producir explicación de avería |

CN5 (memoria contaminada) y CN6 (hipótesis falsa inyectada al verificador) quedan fuera del
alcance: `05_fuera_de_alcance.md` §1.

---

## 2. Métricas

Cada métrica declara qué propiedad mide y a qué hipótesis sirve. La unidad de análisis se
declara siempre y **nunca se agregan métricas de unidades distintas**.

### 2.1 Diagnóstico

| Id | Métrica | Definición | Unidad | Sirve a |
|---|---|---|---|---|
| **M1** | Exactitud diagnóstica top-1 | Fracción de casos en que el mecanismo de fallo señalado coincide con el de referencia del banco. Los casos sin fallo aciertan al no diagnosticar avería. | caso | H-MAIN (Q1), H-SEL |
| **M2** | Exactitud diagnóstica top-k | Ídem admitiendo el mecanismo correcto entre las k explicaciones ordenadas. Secundaria; informa sobre `INCONCLUSIVE`. | caso | descriptiva |

### 2.2 Recuperación de evidencia

Requiere un **conjunto de evidencia de referencia por caso**: los `chunk_id` del corpus que
un evaluador humano marca como pertinentes para el mecanismo, fijados en el manifiesto de
C-A **antes de ejecutar**.

| Id | Métrica | Definición | Unidad | Sirve a |
|---|---|---|---|---|
| **M3** | Recall@k | Fracción de la evidencia de referencia del caso presente entre los k chunks recuperados. | consulta | H-GRD |
| **M4** | Precision@k | Fracción de los k chunks recuperados que pertenecen a la evidencia de referencia. | consulta | H-GRD |
| **M5** | nDCG@k | Calidad del orden de la recuperación. Secundaria. | consulta | descriptiva |
| **M6** | Recuperación vacía o no pertinente | Fracción de casos en que ningún chunk recuperado pertenece a la evidencia de referencia. En el Escenario B su valor esperado es 1 **por construcción**: sirve de verificación del control, no de resultado. | consulta | control |

### 2.3 Explicación: soporte y fidelidad

La explicación se descompone en **afirmaciones atómicas** por un procedimiento
determinista, congelado antes de ejecutar. Cada afirmación se clasifica en *documental*
(requiere evidencia del corpus), *telemétrica* (requiere una comprobación sobre features) o
*genérica* (no requiere evidencia; p. ej. una recomendación de revisión).

| Id | Métrica | Definición | Unidad | Sirve a |
|---|---|---|---|---|
| **M7** | Proporción de afirmaciones sustentadas *(groundedness)* | Afirmaciones que requieren evidencia y cuya evidencia asociada las sostiene, sobre el total de afirmaciones que requieren evidencia. | explicación | H-MAIN (Q2), H-GRD |
| **M8** | Recuento de afirmaciones no sustentadas | Número absoluto por explicación. Es la **métrica primaria heredada de H-EXP**, conservada para continuidad del pre-registro. | explicación | H-GRD |
| **M9** | Fidelidad *(faithfulness)* | Fracción de afirmaciones derivables de la evidencia efectivamente recuperada, frente a las atribuibles a conocimiento paramétrico del modelo. Se evalúa con juez calibrado (juez ≠ generador) más submuestra manual del 25 %. | explicación | H-GRD |
| **M10** | Afirmaciones factualmente incorrectas | Afirmaciones contrastables contra las features o el ground truth del fallo inyectado y que son falsas. Distinta de M8: una afirmación puede estar sustentada y ser falsa si la evidencia lo es. | explicación | H-MAIN, análisis de errores |

### 2.4 Trazabilidad

| Id | Métrica | Definición | Unidad | Sirve a |
|---|---|---|---|---|
| **M11** | Corrección de la citación *(citation correctness)* | Fracción de referencias emitidas que (a) resuelven a una unidad de evidencia existente y (b) cuyo contenido sostiene la afirmación citada. | afirmación citada | H-MAIN (Q3), H-TRC |
| **M12** | Completitud de la citación *(citation completeness)* | Fracción de afirmaciones que requieren evidencia y que llevan al menos una referencia. Una explicación puede ser correcta en sus citas y estar incompleta. | explicación | H-TRC |
| **M13** | Profundidad de traza hasta el dato | Fracción de afirmaciones telemétricas rastreables hasta un `feature_vector` identificado, su ventana y su sesión, con la procedencia registrada. Es la trazabilidad *hasta los datos OBD-II*, no solo hasta el documento. | afirmación telemétrica | H-TRC |
| **M14** | Anclaje en distractor | Fracción de referencias que resuelven a un documento marcado como distractor (CN3). Debe ser ≈0. | afirmación citada | CN3 |

### 2.5 Suficiencia y abstención

| Id | Métrica | Definición | Unidad | Sirve a |
|---|---|---|---|---|
| **M15** | Tasa de abstención correcta | Fracción de casos del Escenario B en que la salida es `INSUFFICIENT_EVIDENCE`. | caso | H-MAIN (Q4), H-ABS |
| **M16** | Tasa de falsa abstención | Fracción de casos del Escenario A en que el sistema se abstiene teniendo la evidencia disponible. Mide el coste de la política. | caso | H-ABS, H-SEL |
| **M17** | Tasa de falsa aceptación | Fracción de casos del Escenario B en que el sistema emite una explicación como sostenida. Es el fallo que la PI persigue evitar: **completar el hueco**. | caso | H-MAIN (Q5), H-ABS |
| **M18** | Cobertura *(coverage)* | Fracción de casos totales en que el sistema emite explicación. | conjunto de casos | H-SEL |
| **M19** | Exactitud selectiva *(selective accuracy)* | M1 calculada únicamente sobre los casos no abstenidos. | conjunto de casos | H-SEL |
| **M20** | Curva riesgo-cobertura y AURC | Riesgo (1 − exactitud selectiva) en función de la cobertura, barriendo el umbral de suficiencia. Resume la política de abstención sin depender de un único umbral. | conjunto de casos | H-SEL |
| **M21** | Calibración de la confianza declarada (ECE) | Secundaria. | caso | descriptiva |

### 2.6 Coste (criterio transversal edge)

| Id | Métrica | Definición | Unidad |
|---|---|---|---|
| **M22** | Latencia por etapa | Recuperación, generación, verificación, decisión. | ejecución |
| **M23** | RSS máximo | Con el instrumento corregido en F-PREREG §2.5 (B0.2). | ejecución |
| **M24** | Tokens consumidos por caso | Entrada y salida. | caso |

El criterio transversal edge de `pre-registro-v1.md` §3.4 se conserva sin cambio: una
configuración que lo viole se declara no viable aunque gane en calidad.

---

## 3. Reinterpretación de los casos held-out

Los 40 episodios held-out de `suite_v2` **se conservan y se reutilizan**. Cambia lo que se
afirma con ellos:

| Antes (PI v3) | Ahora (PI v4) |
|---|---|
| Prueba de que el sistema identifica patrones de fallo no representados en su conocimiento y genera hipótesis sobre ellos | Casos donde la disponibilidad del conocimiento está deliberadamente controlada, y donde se evalúa si el agente reconoce que no dispone de evidencia suficiente |
| P1 (recall de señalización) era co-primaria de H-MAIN | La señalización pasa a **precondición instrumental**: un caso no señalado no llega al razonador y se reporta aparte, sin contaminar las métricas de explicación |
| La exclusión E-RAG era una restricción que el corpus debía cumplir | La exclusión E-RAG es la **variable independiente** que construye C-B |

Los episodios held-out que sigan siendo útiles para evaluar detección de anomalías se
conservan también con ese uso instrumental (SD1). Ninguno se descarta.

---

## 4. Umbrales y criterios de decisión

Congelados por ENM-001, **antes de ejecutar**. Justificación de cada valor incluida: un
umbral sin justificación es un umbral elegido a posteriori.

### 4.1 H-MAIN v4 (co-primarias conjuntivas)

| Q | Métrica | Umbral de aceptación | Refutación | Justificación del valor |
|---|---|---|---|---|
| **Q1** | M1 en Escenario A, brazo B3 | ≥ 0.60 | < 0.40 | El banco tiene 8 mecanismos más «sin fallo»; el azar informado ronda 0.11. 0.60 exige margen amplio sobre el azar sin presuponer un rendimiento de modelo grande en un SLM cuantizado. |
| **Q2** | M7 (groundedness) media en Escenario A, B3 | ≥ 0.80 **y** > B2 | IC 95 % de la diferencia B3−B2 incluye 0 y M7 < 0.60 | Una explicación con una de cada cinco afirmaciones sin sustento sigue siendo defendible como resultado; por debajo de 0.60 la trazabilidad es nominal. |
| **Q3** | M11 (citation correctness) en B3 | ≥ 0.70 **y** superioridad significativa sobre B0-attr | No distinguible de B0-attr | Si la atribución posicional iguala al sistema, la trazabilidad no razona sobre la evidencia. |
| **Q4** | M15 (abstención correcta) en Escenario B | ≥ 0.70 | < 0.50 | Hereda el umbral de P2 de H-MAIN v3 (tasa de «no cubierto» correcta ≥ 0.70), pre-registrado y no modificado. |
| **Q5** | M17 (falsa aceptación) en Escenario B | ≤ 0.15 | > 0.30 (límite inferior del IC 95 % > 0.15) | Hereda y endurece ligeramente P3 de H-MAIN v3 (identificación errónea confiada ≤ 0.10 sobre una tarea distinta). |

Restricción adicional: **M16 (falsa abstención) ≤ 0.20** en el Escenario A. Un sistema que
se abstiene siempre satisface Q4 y Q5 trivialmente; este límite lo impide y hace del
conjunto un criterio no degenerado.

### 4.2 Hipótesis subordinadas

| H | Contraste primario | Umbral de éxito | Refutación |
|---|---|---|---|
| **H-GRD** | M8 (recuento de afirmaciones no sustentadas), B3 vs B2, pareado por caso | Reducción ≥ 50 % relativa | Sin reducción, o utilidad de la explicación degradada más de 0.5 puntos sobre 5 |
| **H-TRC** | M11, B3 vs B0-attr, pareado por afirmación citada | Superioridad significativa, α = 0.05 unilateral | No distinguible del control |
| **H-ABS** | M15 (Escenario B) − M16 (Escenario A), pareado por caso | Diferencia ≥ 0.40 absoluta | Diferencia < 0.15: el sistema explica igual con y sin evidencia |
| **H-SEL** | M19 (exactitud selectiva) B3 vs M1 de B2, con M18 ≥ 0.70 | Ganancia ≥ 0.10 absoluta manteniendo cobertura | La ganancia exige cobertura < 0.70 |

El umbral de H-GRD (≥ 50 % relativo) y su margen de no-inferioridad en utilidad se
conservan **literalmente** de H-EXP en `pre-registro-v1.md` §4.5: no se han elegido después
de ver ningún resultado.

### 4.3 Plan estadístico

Se conserva íntegro el plan del pre-registro §8, aplicado a las nuevas comparaciones:

- Comparaciones binarias apareadas por caso (abstención, acierto): **McNemar exacto**.
- Recuentos y proporciones apareadas por caso: **Wilcoxon de rangos con signo**, unilateral
  α = 0.05, con test de permutación como análisis de sensibilidad.
- Proporciones contra umbral absoluto (Q1, Q4, Q5): estimación puntual con **IC 95 % exacto
  de Clopper-Pearson**; con n = 40 no se exige significación contra un comparador, se
  reporta el intervalo.
- Tamaños de efecto: diferencia de proporciones apareada o cociente de medias, con **IC 95 %
  bootstrap BCa** (10 000 remuestras) a nivel de caso; **δ de Cliff** donde proceda.
- **Corrección de Holm dentro de familia**: {H-GRD, H-TRC, H-ABS, H-SEL} son cuatro
  familias con una primaria cada una; Q1–Q5 son co-primarias conjuntivas de H-MAIN y no se
  corrigen entre sí (la conjunción ya es conservadora).
- Potencia: con n = 40 casos pareados, McNemar detecta diferencias de proporción de ≈0.25
  con potencia ≈0.80. Se declara por adelantado que **diferencias menores de 0.25 no serán
  detectables** y se reportarán como no concluyentes, nunca como ausencia de efecto.

### 4.4 Evaluación de las explicaciones

Se conserva el procedimiento de dos capas de `pre-registro-v1.md` §6.4: juez de lenguaje
calibrado con posiciones aleatorizadas y **juez ≠ generador**, más validación manual del
autor sobre una submuestra aleatoria pre-extraída del 25 %, con κ de Cohen reportado. Si
κ < 0.6, la métrica primaria pasa a computarse solo sobre anotación manual ampliada. M11,
M12 y M13 son **verificables de forma determinista** (la referencia resuelve o no resuelve;
el `feature_vector` existe o no existe) y no dependen del juez: es una ganancia de
objetividad respecto al diseño anterior.

---

## 5. Experimentos y su orden

| Orden | Experimento | Responde | Depende de |
|---|---|---|---|
| 0 | **R2** — smoke del modelo de lenguaje local | fija el parámetro diferido D1 | ollama en el Mac (**camino crítico**) |
| 0 | **R3** — construcción y congelación de C-A / C-B / C-B′ con manifiesto y hash | condición del experimento central | decisión del autor sobre el corpus |
| 1 | **EXP-SEG-001** — calidad de la segmentación de eventos | precondición instrumental de SD1 | ninguna (no usa modelo de lenguaje) |
| 2 | **EXP-RET-001** — calidad de la recuperación (M3, M4, M5, M6) sobre C-A y C-B | H-GRD, y **valida el control de disponibilidad** | R3 |
| 3 | **EXP-EVID-001** — experimento central: 3 brazos × 2 escenarios × 40 casos | H-MAIN, H-GRD, H-TRC, H-ABS, H-SEL | R2, R3, EXP-RET-001 |
| 4 | **Validaciones externas** | validez externa | HCRL; ARM64/RPi5 (A2/A3) |

**Escenario mínimo defendible:** EXP-RET-001 + EXP-EVID-001 con los brazos B2 y B3 y ambos
escenarios. Si el calendario obliga a recortar, el orden de sacrificio pre-declarado es:
las validaciones externas → la variante C-B′ → el brazo B1 → EXP-SEG-001. **Nunca** el
Escenario B ni el brazo B3: sin ellos la PI queda sin contraste.

**Ablaciones.** No se conserva ninguna ablación adicional. Las ablaciones A0–A6
(arquitecturas) y M0/M1/M2 (memoria) salen del alcance: `05_fuera_de_alcance.md`. Los tres
brazos B1/B2/B3 **son** la ablación necesaria y suficiente para la PI.

---

## 6. Amenazas a la validez declaradas a priori

1. **El corpus es obra propia.** C-A, C-B y C-B′ se construyen para este trabajo; la
   evidencia de referencia por caso la fija el mismo autor. Se mitiga congelando el
   manifiesto y la evidencia de referencia antes de ejecutar y publicando ambos, pero la
   limitación se declara: no se afirma validez sobre corpus técnicos reales.
2. **Los datos son emulados.** El «dato OBD-II real» de la PI se refiere a telemetría con
   estructura y semántica de OBD-II generada por el emulador con semillas congeladas, no a
   capturas de vehículos en circulación. La validación con HCRL sigue pendiente y así se
   declara en todas las conclusiones.
3. **Un solo modelo de lenguaje.** Los resultados están condicionados al modelo que fije
   R2. No se afirma generalización a otros modelos.
4. **El juez es un modelo de lenguaje.** Mitigado con juez ≠ generador, aleatorización de
   posiciones, submuestra manual y κ reportado; las métricas de trazabilidad no dependen
   del juez.
5. **Circularidad de la exclusión.** Si la retirada de documentos de C-B fuese detectable
   por una señal superficial (p. ej. corpus notablemente más corto), el sistema podría
   abstenerse por la señal y no por la evidencia. Se mitiga igualando el tamaño del corpus
   entre variantes con documentos de otros mecanismos y verificándolo en el manifiesto.
