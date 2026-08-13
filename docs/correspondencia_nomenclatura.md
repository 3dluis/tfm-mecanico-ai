# Correspondencia de nomenclatura (alineación científica v2, 2026-08-12)

Tabla de trazabilidad entre la nomenclatura anterior (Fase 0 y extensiones de fases) y la vigente tras la decisión de alineación (docs/propuesta_alineacion_final.md, aprobada; PI Opción B). **Regla:** los documentos históricos (informes de fase cerrados, ADRs ya aceptados) NO se reescriben — conservan la nomenclatura de su época y se interpretan mediante esta tabla; los documentos vivos (planes pendientes, protocolo experimental, harness, memoria del TFM) usan la nomenclatura nueva.

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
