# Correspondencia de nomenclatura (alineaciones científicas v2, v3 y v4)

Tabla de trazabilidad entre nomenclaturas. **Regla:** los documentos históricos (informes de fase cerrados, ADRs aceptados) NO se reescriben — conservan la nomenclatura de su época y se interpretan mediante esta tabla; los documentos vivos usan la nomenclatura vigente (v3). Fuente canónica de la estructura vigente: `docs/alineacion_v4/01_nucleo_cientifico.md` (la v3 pasa a histórica; su correspondencia con la v4 está en el §11 de ese documento).

## 0. Pregunta de investigación (historia)

| Versión | Enunciado (resumen) | Vigencia | Dónde puede aparecer |
|---|---|---|---|
| **PI v1** | «¿Puede un agente híbrido, que combine LLM + no supervisado + memoria + RAG, descubrir y explicar patrones no documentados…?» | Fase 0 → 12-ago-2026 | docs/01 v1, informes F0–F9 |
| **PI v2** («Opción B») | «¿Puede un sistema híbrido descubrir y explicar patrones de fallo previamente no documentados mediante análisis contextual y longitudinal de OBD-II?» | 12-ago → 18-ago-2026 | propuesta_alineacion_final, pre-registro-v1 (§1 hasta su enmienda), estado_del_arte_y_metodologia_tutor, consolidado v1.0 Parte II |
| **PI v3** (OFICIAL) | «¿Puede un sistema híbrido **identificar** patrones **no representados en su conocimiento disponible**, **generar hipótesis** diagnósticas a partir del análisis contextual y longitudinal de OBD-II y **validarlas mediante evidencia antes de incorporarlas como conocimiento reutilizable**?» | 18-ago → 27-ago-2026 | `alineacion_v3/`, pre-registro v1 (ENM-000), memoria cap. 1–3 |

| **PI v4** (OFICIAL) | «¿Puede un **agente con RAG explicar** el diagnóstico de un vehículo a partir de datos OBD-II reales, **rastreando cada explicación hasta su evidencia de origen**, y **reconocer cuándo la evidencia disponible no es suficiente** para sostener una explicación en lugar de generar una hipótesis sin fundamento?» | desde 27-ago-2026 | docs/01 v4, `alineacion_v4/`, todo documento vivo |

Cambios sustantivos v3→v4 (acordados con el tutor, 27-ago-2026): (1) el enunciado se acota de la cadena de ocho pasos a la de seis (observar → contextualizar → diagnosticar → recuperar evidencia → verificar el soporte → explicar o abstenerse); (2) salen del núcleo la generación de hipótesis como resultado, la validación de hipótesis y la consolidación en memoria; (3) entran como exigencias explícitas la **trazabilidad verificable** afirmación→evidencia→dato y la **abstención** ante evidencia insuficiente; (4) la exclusión E-RAG deja de ser una restricción y pasa a ser la variable independiente principal. Justificación completa: `docs/alineacion_v4/04_historial_pi.md`. Lo retirado no se borra: `docs/alineacion_v4/05_fuera_de_alcance.md`.

Cambios sustantivos v2→v3: (1) la cadena completa entra en el enunciado (identificar + hipotetizar + validar + incorporar); (2) «no documentado» → «no representado en su conocimiento disponible» (novedad relativa al sistema, operacionalizable por exclusión triple); (3) la consolidación validada deja de ser un mecanismo y pasa a ser parte de la pregunta. «Patrón no documentado» en textos históricos se lee como «patrón no representado» sin cambio de significado experimental (la definición operacional por exclusión triple ya era la vigente).

## 1. Hipótesis

| Anterior | Vigente | Nota |
|---|---|---|
| H1 (detector no supervisado detecta fallos incipientes) | Precondición de **H-EVT** (brazos E0/E1) | Ya satisfecha operativamente en F3; deja de ser hipótesis independiente |
| H2 (RAG mejora explicaciones vs LLM solo) | Integrada en **H-EXP** (brazo LLM vs +RAG) | H-EXP añade el brazo +RAG+verificación |
| H2b (held-out de conocimiento en corpus/memoria) | **H-MAIN** (protocolo held-out/open-set triple: datos+corpus+memoria) | El experimento central |
| H3 (memoria mejora casos repetidos) | Subsumida en **H-MEM** | |
| H4 (viabilidad Raspberry Pi) | **Criterio transversal edge** (docs/01 §1.4.3) | Deja de ser hipótesis; restricción de aceptación medible en todo experimento |
| H5 (memoria+loop mejoran fallos no observados) | **H-MEM** (y alimenta H-MAIN) | |
| H6 / PI.5-antigua (eventos vs ventanas) | **H-EVT** | = experimento E0–E4; en F6 aparece como PI.5/H6 y dimensión `anomaly_mode` |
| — | **H-MAS (secundaria)** | Nueva: ablación A0–A6; su refutación NO afecta a C-INT |
| — | **H-PERS** | Nueva: brazo E4 global vs individual vs jerárquico |

## 2. Subpreguntas de investigación

| Anterior (docs/01 v1) | Vigente (docs/01 v2) |
|---|---|
| PI.1 (detección pre-DTC) | PI.1 (igual; precondición de H-EVT) |
| PI.2 (RAG vs LLM solo) | PI.3 (ampliada con verificación → H-EXP) |
| PI.3 (memoria) | PI.4 (ampliada con validación → H-MEM) |
| PI.4 (viabilidad RPi) | PI.7 (→ criterio transversal) |
| PI.5 añadida en F6 (eventos vs ventanas) | PI.2 (→ H-EVT) |
| — | PI.5 nueva (multiagente → H-MAS) |
| — | PI.6 nueva (personalización → H-PERS) |

## 3. Objetivos específicos

| Anterior (docs/02 v1) | Vigente (docs/02 v2) | Nota |
|---|---|---|
| OE1 (estado del arte) | OE1 | CV actualizado (RQ1–RQ17, V1–V7, pendientes) |
| OE2 (entorno emulado) + OE3 (adquisición) | OE2 | Banco [M] separado de infraestructura [I] |
| OE4 (detección de anomalías) + OE-EVT propuesto | OE3 | Ahora: segmentación con evaluación propia + comparación E0–E4 + brazo C-PERS |
| OE5 (RAG) + OE6 (agente) | OE4 | RAG como instrumento del bloque de razonamiento; multiagente con ablación A0–A6 |
| OE7 (memoria de casos) | OE5 | Ahora: ciclo de 7 estados + memoria de eventos + validación |
| OE8 (evaluación H1–H4) | OE6 | Ahora: seis familias, H-MAIN integradora, pre-registro |
| OE9 (API/interfaz) | OE7 | Declarado ingeniería/producto, sin RQ |
| OS1–OS3 | OS1–OS3 | Sin cambios (OE9→OE7 en la referencia de OS1) |

## 4. Documentos que referencian nomenclatura antigua (estado)

- **docs/01, docs/02** — actualizados a v2 (este cambio). Nota: en el disco del autor están evictados por iCloud; si la escritura remota falló, aplicar desde el chat/zip en el Mac y hacer commit.
- **docs/07_cronograma_y_entregables.md** — referencia "H1–H4" y "Fase 4": interpretar por esta tabla; actualizar cuando se revise el cronograma (no urgente).
- **docs/agent-runtime/** (F5) y **ADR-0018** — usan "H5" y A0–A6: históricos, interpretar H5→H-MEM; A0–A6 sigue vigente con el mismo nombre.
- **docs/event-intelligence/** (F6) y **ADR-0021** — usan "PI.5/H6" y `anomaly_mode`: históricos, interpretar PI.5/H6→H-EVT (PI.2 nueva); `anomaly_mode` sigue vigente.
- **Capítulo 2 (estado del arte)** — ya usa las familias H-* y E0–E4/A0–A6; única corrección aplicable en la siguiente revisión: §2.16.3 menciona "H2b", interpretar → H-MAIN.
- **Protocolo experimental (a crear, pre-registro)** — usará EXCLUSIVAMENTE la nomenclatura nueva y fijará los umbrales ◊ de docs/auditoria_alineacion_investigacion.md §4 antes de ejecutar R1/E1.
- **Planes R1–R5 y E1–E4** (pendientes de aprobación) — al aprobarse, sus documentos de ejecución referenciarán las familias nuevas (R5/E3-experimento ≡ H-MAIN; E1 ≡ primer brazo de H-EVT).

## 5. Próximo paso acordado

Pre-registrar el protocolo experimental (familias H con umbrales numéricos definitivos, escenarios, semillas, splits held-out y plan de análisis) **antes** de ejecutar cualquier experimento — transición de diseño de investigación a validación científica.

---

## 6. Adición F10 (2026-08-13) — brazos de detección F8/F9 ↔ H-EVT

*Sección añadida en F10 al incorporar este documento al repositorio (antes vivía solo en
el disco del autor, sin control de versiones). Las secciones 1–5 se conservan VERBATIM.*

Los experimentos EXP-ANOM-002 (F8) y EXP-ANOM-003 (F9) — ambos clasificados
**PILOT/EXPLORATORY** por decisión del autor (docs/experiments/exploratory/) — usan la
dimensión `anomaly_mode` y se interpretan dentro de **H-EVT** así:

| Brazo F8/F9 | Interpretación H-EVT | Nota |
|---|---|---|
| AM-W (LOF ventana) | brazo de referencia ventana (≈ E1 del diseño E0–E4) | detector primario vigente |
| AM-E / AM-E-d (eventos+contexto) | brazo evento-contextual (≈ E2/E3) | v0.1.0 → v0.2.0 en F9 |
| AM-E-NOCTX | ablación del contexto dentro de H-EVT | |
| AM-WE / AM-WE-d | brazo combinado | configuración recomendada exploratoria |
| brazo global-vs-por-vehículo (E4) | **NO ejecutado** (requiere 2º perfil de vehículo) | alimentará H-PERS |

El protocolo confirmatorio pre-registrado de H-EVT es
**[PROTO-CONF-001](experiments/preregistered/PROTO-CONF-001.md)** (F10): usa
exclusivamente la nomenclatura nueva y datos confirmatorios nunca vistos.

## 7. Adición F13 (2026-08-13) — línea experimental ML ↔ familias vigentes

*Sección añadida en F13 (apertura de la línea de entrenamiento y evaluación de modelos
ML). Las secciones 1–6 se conservan VERBATIM.*

La instrucción de fase proponía una serie `EXP-ML-001…014`; se integra en la nomenclatura
canónica `EXP-<FAMILIA>-<NNN>` (mapeo completo en
[Protocolo ML v1 §7](experiments/protocolo_ml_v1.md)). Correspondencias con las familias
de hipótesis:

| Elemento F13 | Familia vigente | Nota |
|---|---|---|
| EXP-ANOM-005 (paridad camino wide) | infraestructura de H-EVT/H-MAIN | valida la entrada canónica de ML; no evalúa hipótesis |
| EXP-ANOM-006 (autoencoder) / EXP-ANOM-007 (LSTM/GRU-AE) | precondición reforzada de H-EVT; alimenta H-MAIN | mismos splits/protocolo que E1; condición ADR-0011 |
| EXP-PAT-001/002 (embeddings + HDBSCAN, patrones candidatos) | evidencia de diseño hacia **H-MAIN** (capacidad de descubrimiento) | los patrones candidatos solo cuentan para la PI tras el criterio §10 del protocolo y, en lo confirmatorio, tras EXP-MAIN-001 |
| Hipótesis exploratorias HX-ML-1…6 | NO son familias H-* | verificables, con refutación declarada; nunca se promedian con evidencia confirmatoria |
| `HX-ML-4-R2` (nombre en `exp-anom-010-r2.yaml`, congelado antes de ejecutar) | **`HX-ML-5`** — denominación canónica fijada por el autor (F22) | **Alineación de nomenclatura, NO cambio de criterios**: enunciado, umbrales y predicciones son literalmente los del YAML congelado. Estado: **SUPPORTED** (exploratorio) |
| Serie EXP-EMB-* | reservada para embeddings de RAG (ADR-0024/R3) | los embeddings de comportamiento van en EXP-PAT-* |

## 5. Vacíos de investigación (v3): V1–V7 → V\* + S1–S6

Desde la alineación v3 existe **un único vacío central V\*** con seis dimensiones
subordinadas. V1–V7 conservan su evidencia; dejan de presentarse como siete vacíos
independientes de igual rango.

| Anterior | Vigente (v3) | Nota |
|---|---|---|
| V7 (diagnóstico basado en eventos; «central» en v2) | **S1** (detección contextual) + parte de S6 | la comparación evento-vs-continuo sigue siendo el contraste de H-EVT |
| V3 (personalización por vehículo) | **S1** (dimensión longitudinal/personalizada) | |
| V4 (de anomalía a explicación comprobable) | **S2** (generación de hipótesis) + **S3** (verificación con evidencia) | |
| V2 (memoria con validación de hipótesis) | **S4** (memoria longitudinal validada) | |
| V6 (multiagente vehicular híbrido en edge) | **S5** (condición habilitante / artefacto; contribución solo si A0–A6 lo demuestra) | |
| V1 (integración end-to-end) | absorbido por **V\*** (la integración es artefacto, no vacío por sí misma) | la «formulación integradora» deja de usarse como argumento principal |
| V5 (evaluación con fallos reproducibles) | **S6** (patrones no representados como escenario; banco held-out) | |

## 6. Hipótesis exploratorias de la línea ML (serie HX-ML)

| Código | Fase | Estado | Nota |
|---|---|---|---|
| HX-ML-1/2 | F14/F16 | resueltas (negativas) | AE denso no supera a LOF sin cobertura |
| HX-ML-3 | F18 | REFUTADA | temporales no superan a estáticos |
| HX-ML-4 | F21 | REFUTADA | cobertura declarada ≠ efectiva |
| HX-ML-5 (= HX-ML-4-R2 en el YAML congelado) | F22 | SUPPORTED | cobertura efectiva verificada ⇒ FPR 0.0086; cierra H1 exploratoria |

Toda la serie HX-ML pertenece a los pasos 1–3 de la cadena epistemológica y a la
precondición de H-EVT; ninguna responde H-EVT ni las familias de los pasos 4–8.
