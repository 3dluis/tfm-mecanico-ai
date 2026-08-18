# Alineación científica v3 — Entregable 1: Informe de auditoría

**2026-08-18 · previa a cualquier modificación · TFM «Sistema inteligente para el
diagnóstico y mantenimiento predictivo de vehículos» (UAX, septiembre 2026)**

Auditoría de toda la documentación científica del proyecto antes del refactor alrededor de
la Pregunta de Investigación oficial (PI v3), el vacío central V\* y la cadena
epistemológica. Regla rectora: **se refactoriza la jerarquía argumental; no se borra
evidencia** — ningún experimento, resultado negativo, referencia verificada ni decisión
registrada se elimina.

## 1. Hallazgo principal: tres generaciones de PI coexisten

| Generación | Enunciado (resumen) | Dónde vive hoy |
|---|---|---|
| **PI v1** (Fase 0) | «¿Puede un *agente* híbrido, que combine LLM + no supervisado + memoria + RAG, descubrir y explicar patrones no documentados…?» — un catálogo tecnológico dentro de la pregunta | `docs/01_comprension_del_problema.md` §1.3 |
| **PI v2** («Opción B», alineación 12-ago) | «¿Puede un sistema inteligente híbrido descubrir y explicar patrones de fallo previamente no documentados mediante análisis contextual y longitudinal de OBD-II?» | `docs/experiments/pre-registro-v1.md` §1 · `estado_del_arte_y_metodologia_tutor.md` · Parte II §4 del documento consolidado v1.0 (12-ago) |
| **PI v3** (oficial desde esta revisión) | «¿Puede un sistema inteligente híbrido **identificar patrones de fallo no representados en su conocimiento disponible, generar hipótesis diagnósticas** a partir del análisis contextual y longitudinal de datos OBD-II **y validarlas mediante evidencia antes de incorporarlas como conocimiento reutilizable**?» | Resumen ejecutivo y Parte I del documento consolidado v1.0 — **pero no en su Parte II ni en ningún documento del repositorio** |

El documento consolidado v1.0 (12-ago) es internamente inconsistente: su Parte I ya razona
con la PI v3 y con «no representado», mientras su Parte II (§4 Pregunta, §5 Hipótesis)
conserva la PI v2 y el §14 conserva V1–V7 con V7 como «central». El repositorio está una
generación más atrás en `docs/01` (PI v1). **Decisión: PI v3 es la única oficial; v1 y v2
pasan a la tabla de correspondencia de nomenclatura con su historia.**

Diferencias sustantivas de v3 frente a v2 (no son estilo):

1. «descubrir y explicar» → **«identificar + generar hipótesis + validar + incorporar»**:
   la pregunta ya contiene la cadena epistemológica completa, incluida la consolidación.
2. «previamente no documentados» → **«no representados en su conocimiento disponible»**:
   la novedad es *relativa al sistema* y operacionalizable por exclusión, no un absoluto.
3. La validación mediante evidencia **antes** de incorporar como conocimiento reutilizable
   entra en el enunciado: la memoria validada deja de ser un mecanismo más y pasa a ser
   parte de aquello que se pregunta.

## 2. Inventario auditado

Documentación científica revisada (commit `b39bf14`): `docs/01`, `docs/02`, `docs/03`,
`docs/06`; `docs/estado_del_arte/*` (12 ficheros, corpus ≈153 referencias verificadas);
documento consolidado v1.0 (.docx, 21 800 palabras); `docs/experiments/pre-registro-v1.md`
(no vinculante aún) + `PROTO-CONF-001` + reconciliación F-PREREG; `protocolo_ml_v1` + 2
adendas XAI; `correspondencia_nomenclatura.md`; `afirmaciones_novedad.md`;
`auditoria_alineacion_investigacion.md` + `propuesta_alineacion_final.md` (v2, 12-ago);
`docs/memoria/*` (8 capítulos, borrador M1); informes de fase F3–F22; 11 configs
`exp-anom-*.yaml` congeladas; ADRs 0001–0035; 14 experimentos ejecutados
(EXP-ANOM-001…010-R2, AUDIT-DATA-001) con sus resultados JSON.

## 3. Matriz de auditoría (elemento → problema → decisión → nueva ubicación → justificación)

| # | Elemento actual | Problema | Decisión | Nueva ubicación | Justificación |
|---|---|---|---|---|---|
| A1 | PI v1 en `docs/01` §1.3 | Catálogo tecnológico dentro de la pregunta; dos generaciones por detrás | **Reformular** a PI v3 | `docs/01` §1.3 + `01_nucleo_cientifico.md` §1 | La PI no debe depender de que cada tecnología funcione (la refutación de H-MAS no puede invalidar la pregunta) |
| A2 | PI v2 en `pre-registro-v1.md` §1 | Desalineada con la PI oficial; el pre-registro NO está congelado (F-PREREG §0) | **Reformular** vía enmienda pre-congelación, fechada | `pre-registro-v1.md` §1 | Cambio legítimo: B «no vincula» hasta el tag `prereg-v1.0`; la reconciliación F-PREREG ya exige actualizarlo antes de congelar |
| A3 | V1–V7 como siete vacíos coordinados (`capitulo2` §2.15, tutor §14, docx §14) | Dispersa el TFM; V7 «central» compite con V2 y V6; la «formulación integradora» argumenta novedad-por-integración (prohibida como argumento principal) | **Subordinar**: un único V\* + dimensiones S1–S6 | `01_nucleo_cientifico.md` §3; reescritura de §14 del consolidado; tabla V→S en `correspondencia_nomenclatura.md` | Un solo vacío alineado con la PI; V1–V7 conservan su evidencia como dimensiones, no como siete contribuciones en pie de igualdad |
| A4 | «Formulación integradora» (≈«nadie reúne los cinco ejes») | Novedad de ingeniería presentada como científica | **Degradar** a observación de cobertura en la matriz de antecedentes; nunca argumento principal | Matriz de cobertura del EdA | El principio rector: la integración es artefacto, no tesis |
| A5 | H-MAIN (docx §5, pre-registro §4.6) | Cubre (i)–(iv) pero no llega a consolidación/abstención; no exige criterios de validación previos; nombrada sobre PI v2 | **Reformular** según §8 del mandato, conservando VD co-primarias P1–P4 ya operacionalizadas | `01_nucleo_cientifico.md` §5; enmienda de `pre-registro-v1.md` §4.6 | La cadena que la PI v3 enuncia debe estar entera en la hipótesis integradora; lo ya operacionalizado (rúbrica GT, juez calibrado) se conserva |
| A6 | H-EVT, H-MEM, H-MAS, H-PERS, H-EXP | Válidas y bien construidas; les falta subordinación explícita a H-MAIN y lectura por etapa de la cadena | **Conservar y reordenar** como subordinadas, mapeadas a S1–S6 | `01_nucleo_cientifico.md` §5 | Ya tienen criterios de refutación y brazos; solo cambia la jerarquía |
| A7 | Criterio transversal edge (antes H4) | Correcto; el instrumento `peak_rss_mb()` mide mal fuera de Linux (hallazgo F22) | **Conservar**; bloquear su uso confirmatorio hasta corregir el instrumento | Sin cambio de ubicación | Ya decidido en F-PREREG §2.5 |
| A8 | Objetivos OE1–OE8 (+OS1–OS3) | Mezclan nivel científico, instrumental e ingeniería con etiquetas [C]/[M]/[X]/[A]/[I] pero jerarquía plana | **Reestructurar** en 3 niveles: científicos (OG + OE-C1…C4) / instrumentales / ingeniería-administración; conservar OE1–OE8 como capa instrumental con correspondencia | `01_nucleo_cientifico.md` §4; `docs/02` | El mandato §10; además la plantilla UAX exige 4–6 específicos — los 4 científicos resuelven también esa contradicción documentada en `memoria/README.md` |
| A9 | Definición «no documentado» (pre-registro «precisión terminológica»; docx prosa) | Existente pero informal; convive con «desconocido/nuevo/no visto» en textos antiguos | **Formalizar** la definición operacional por exclusión triple (detector, RAG, memoria) con mecanismos anti-contaminación | `01_nucleo_cientifico.md` §2 | Mandato §6; la base ya existía (H-EA5, protocolo held-out/open-set triple) — se eleva a definición canónica |
| B1 | Cadena de 7 elementos «telemetría → … → conocimiento validado» (docx, passim) | Le faltan dos transiciones que la PI v3 exige: *reconocer insuficiencia* y *consolidar o abstenerse* | **Sustituir** por la cadena oficial de 8 pasos | `01_nucleo_cientifico.md` §0; propagar a docx v2.0 | Mandato §7; las etapas añadidas son precisamente las que separan hipótesis de conocimiento |
| B2 | Estados de la memoria (prosa dispersa: «observado/inferido/hipótesis/validado») | Sin definición formal de estados, transiciones, quién promueve, trazabilidad | **Crear** tabla de estados epistemológicos (OBSERVED…REFUTED) | `01_nucleo_cientifico.md` §7 | Mandato §16; da semántica única a memoria, verificador y métricas de contaminación |
| B3 | Controles negativos | No existen como diseño (solo la idea de «sesiones normales para FP») | **Crear** batería de controles negativos + métrica de abstención correcta | `01_nucleo_cientifico.md` §8.3 | Mandato §15; sin ellos la abstención no es medible |
| B4 | Matriz de contaminación | Parcial (particiones por sesión; principios RI1) | **Crear** matriz componente × etapa (qué puede ver cada cosa) | `01_nucleo_cientifico.md` §9 | Mandato §20; consolida reglas que ya se cumplen de facto (P4 lo demuestra) más las nuevas para RAG/memoria/juez |
| B5 | Matriz de antecedentes (15 trabajos × 9 columnas tecnológicas) | Columnas orientadas a componentes, no a la cadena | **Reformar** columnas: Detección / Contexto / Longitudinal / Hipótesis / Evidencia / Verificación / Memoria validada / Open-set / Consolidación | `02_trazabilidad.md` §3 + docx v2.0 | Mandato §12; permite ver quién cubre pasos, combinaciones o la cadena completa — sin fabricar el vacío |
| B6 | Métricas (pre-registro §5, docx §9) | Completas para detección/IR/juez; falta la familia «reconocimiento de novedad relativa» y la unidad explícita por métrica en algunos textos | **Ampliar**: métricas de insuficiencia-de-conocimiento (tasa de "no cubierto" correcta, identificación confiada errónea, AURC/abstención); tabla métrica→unidad | `01_nucleo_cientifico.md` §8.4 | Mandato §18–19; P2/P3 de H-MAIN ya lo insinuaban — se les da familia propia |
| B7 | DSR (docx Parte II §1–3) | Correcto y bien separado del diseño experimental | **Conservar** con ajuste menor (mapear fases DSR a la cadena) | Sin cambio | Mandato §26 ya satisfecho en lo esencial |
| B8 | Resultados y fases F3–F22 (14 experimentos, 4 negativos mayores) | Ninguno evaluaba aún generación de hipótesis/verificación/memoria; riesgo de releerlos como si tocaran H-EVT u otras familias (aviso F-PREREG §2.1) | **Conservar intactos**; añadir tabla de reinterpretación: qué etapa de la cadena informa cada uno | `02_trazabilidad.md` §2 | Mandato §29; los negativos (F17, F18, F21) son evidencia metodológica de primer orden para S1 y para la disciplina de abstención |
| B9 | `afirmaciones_novedad.md` | Válido; usa «literatura analizada» y clasifica novedad sobre V1–V7 | **Conservar** + adenda v3: remapear A1–A7 a V\*/S y sustituir «literatura» | Adenda en el propio fichero | Mandato §11/§31; el sistema de clases A/B/C/D se conserva porque es exactamente «la afirmación nunca supera la evidencia» |
| B10 | Uso de «literatura» (11 ficheros + 1 vez en docx) | Regla de estilo del mandato §11 | **Sustituir** por «trabajos revisados/analizados», «estado del conocimiento», según contexto, en documentos vivos; los históricos no se reescriben | Documentos vivos | Coherencia con la regla de que los informes cerrados conservan su época |
| B11 | Contribuciones (C-EVT, C-MEM, C-INT, C-EXP, C-PERS) | Fijadas por adelantado como catálogo | **Condicionar**: candidatas C1–C3 del mandato §27 + las actuales reexpresadas como resultados posibles, nunca prometidos | `01_nucleo_cientifico.md` §11 | «Solo es contribución lo que los resultados permitan defender» |
| B12 | Separación tesis/artefacto/ingeniería | Implícita (etiquetas [C]/[I], OE7 declarado no-contribución) | **Explicitar** clasificación de tres niveles y aplicarla | `01_nucleo_cientifico.md` §6 | Mandato §13 |
| B13 | Delimitaciones (L1…; docx §11) | Buenas; faltan los «NO debe afirmar» completos del mandato §25 | **Ampliar** tabla puede-demostrar / no-debe-afirmar | `01_nucleo_cientifico.md` §12 | Mandato §25 |
| B14 | Memoria del TFM (borrador M1, caps. 1–3) | Escrita sobre PI v2/v1 según capítulo | **Propagar** PI v3 y nueva jerarquía tras aprobar el núcleo | `docs/memoria/01, 02, 03, 04` | Orden correcto: fuente científica primero, derivados después (mandato §32) |
| B15 | Pre-registro A (PROTO-CONF-001) | Congelado para H-EVT; no menciona PI | **Conservar** sin tocar | Sin cambio | Documento congelado; la reconciliación F-PREREG ya resolvió su relación con B |
| B16 | Implementación (código, arquitectura) | Ninguna exigencia científica nueva requiere cambio de código | **No tocar** | — | Mandato §33: el artefacto actual ya permite probar la nueva estructura; los cambios pendientes (p. ej. `peak_rss_mb`) ya estaban decididos por F-PREREG |

## 4. Clasificación resumida

- **Se conservan sin cambio:** los 14 experimentos y sus resultados; PROTO-CONF-001;
  protocolo ML v1 + adendas; ADRs; informes de fase; referencias verificadas; DSR;
  estructura de splits y semillas; regla de resultados negativos.
- **Se reformulan:** PI (v1/v2 → v3); H-MAIN; §14 vacíos del consolidado; docs/01 §1.3–1.4;
  docs/02; matriz de antecedentes (columnas).
- **Se subordinan:** V1–V7 → S1–S6 bajo V\*; H-EVT/H-MEM/H-MAS/H-PERS/H-EXP bajo H-MAIN;
  arquitectura multiagente → condición habilitante (S5) con hipótesis propia secundaria.
- **Se fusionan:** «precisión terminológica» + H-EA5 + protocolo triple → definición
  operacional única de «no representado».
- **Dejan de ser contribuciones científicas:** integración tecnológica per se; demostrador
  (OE7); infraestructura (ya declarado, se mantiene).
- **Pasan a ingeniería de soporte:** PostgreSQL/pgvector, FastAPI, contenedores, outbox,
  CI/CD, UI/app — ya clasificados así; se explicita en la tabla de tres niveles.

## 5. Riesgos controlados en este refactor

1. **No romper el pre-registro A** (congelado): no se toca.
2. **No contaminar la capa confirmatoria:** nada de lo aquí decidido ejecuta experimentos;
   el tag `prereg-v1.0` sigue sin crearse.
3. **No reescribir historia:** informes de fase e híbridos cerrados conservan su
   nomenclatura; la lectura moderna vive en `correspondencia_nomenclatura.md`.
4. **No inventar:** toda afirmación de ausencia se mantiene como «en los trabajos revisados
   no se identificó…»; los pendientes PRISMA/textos completos siguen declarados.

## 6. Orden de ejecución de los cambios

1. `01_nucleo_cientifico.md` (fuente canónica: PI, definición, V\*, S, cadena, objetivos,
   hipótesis, estados, protocolo H-MAIN, controles, contaminación, métricas,
   delimitaciones, contribuciones).
2. `02_trazabilidad.md` (matriz PI→…→contribución; reinterpretación de los 14 experimentos;
   matriz de cobertura del EdA reformada).
3. `03_backlog_experimental.md` (qué falta para responder H-MAIN).
4. Propagación: `docs/01`, `docs/02`, `correspondencia_nomenclatura.md`,
   `pre-registro-v1.md` (enmienda pre-congelación), `afirmaciones_novedad.md` (adenda),
   `estado_del_arte_y_metodologia_tutor.md`, `docs/memoria/01–04`.
5. Documento consolidado v2.0 (.docx) con las secciones reformadas.
