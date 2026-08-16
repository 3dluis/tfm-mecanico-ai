# Propuesta final de alineación: pregunta, objetivos e hipótesis

**TFM Mecánico IA · UAX · 2026-08-12.** Documento de decisión para la reunión con el tutor. Consolida la auditoría de alineación (docs/auditoria_alineacion_investigacion.md) en una propuesta única y coherente. **Ningún documento oficial se ha modificado**: tras elegir la PI, docs/01 y docs/02 se actualizarán de una sola vez con el contenido de este documento para evitar inconsistencias.

---

## 1. Pregunta principal — dos opciones para decidir

**Opción A — ajuste mínimo (representa fielmente la arquitectura actual):**

> ¿Puede un sistema inteligente híbrido y multiagente, que combine aprendizaje no supervisado, análisis contextual basado en eventos, modelos de lenguaje, RAG y memoria evolutiva con validación, descubrir y explicar patrones de fallo vehicular previamente no documentados a partir de datos OBD-II?

**Opción B — más limpia científicamente (recomendada para la defensa):**

> ¿Puede un sistema inteligente híbrido descubrir y explicar patrones de fallo vehicular previamente no documentados mediante el análisis contextual y longitudinal de datos OBD-II?
>
> *Especificación metodológica:* el sistema se implementa mediante aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente, modelos de lenguaje, RAG y memoria evolutiva con validación de hipótesis.

**Análisis comparativo.** Ambas conservan intacto el núcleo (descubrir y explicar patrones no documentados con OBD-II) y ambas son compatibles con las seis familias de hipótesis. La diferencia decisiva es de robustez ante los propios resultados: en la Opción A, "multiagente" forma parte de aquello que debe funcionar para responder la pregunta — si H-MAS se refuta y el agente monolítico resulta equivalente o mejor, la pregunta queda parcialmente mal formulada; en la Opción B, los mecanismos son medios declarados en la especificación metodológica, de modo que **cualquier resultado de H-MAS (positivo o negativo) responde la pregunta en lugar de amenazarla**. Además, "análisis contextual y longitudinal" codifica con lenguaje científico los dos rasgos diferenciales del sistema (el evento como contexto; el historial y la memoria como dimensión longitudinal) sin convertir la pregunta en un catálogo tecnológico. Coste de B: la arquitectura queda fuera del enunciado, por lo que el objetivo general debe cargar con ella explícitamente (así se redacta en §2). **Recomendación: Opción B como principal, con A como alternativa si el tutor prefiere que la pregunta anuncie la arquitectura.**

## 2. Objetivo general recomendado (válido para ambas opciones)

> Diseñar, implementar y evaluar un sistema inteligente híbrido Edge–Cloud que, sobre telemetría OBD-II segmentada en eventos operativos, detecte anomalías contextuales mediante aprendizaje no supervisado y genere diagnósticos explicables mediante una arquitectura multiagente con modelos de lenguaje, recuperación aumentada por generación y una memoria evolutiva por vehículo con validación de hipótesis, ejecutable en una plataforma de recursos limitados equivalente a una Raspberry Pi, evaluando experimentalmente la aportación de cada mecanismo con criterios pre-registrados — incluida su capacidad de señalar, hipotetizar y explicar patrones de fallo no cubiertos por el conocimiento disponible del sistema.

## 3. Objetivos específicos consolidados (8: 6 científico-experimentales + 2 de soporte declarado)

Cada objetivo indica clase ([C] científico · [M] metodológico · [X] experimental · [A] arquitectónico · [I] ingeniería), qué parte de la pregunta responde, vacío que lo justifica, hipótesis que contrasta y criterio de verificación (CV). Consolidación respecto a los OE1–OE10 originales: 10+1 → 8 (correspondencia en §6).

**OE1 [M] — Estado del arte y posicionamiento.** Mantener la revisión sistemática (RQ1–RQ17, V1–V7, corpus verificado) como fundamento de todos los demás objetivos, con sus cuatro pendientes declarados (PRISMA formal, tres textos completos, vigilancia adversarial, niveles de novedad).
*CV: capítulo 2 aprobado por el tutor; pendientes cerrados antes del depósito.* — Justifica: toda la PI.

**OE2 [M+I] — Banco experimental reproducible.** Consolidar el entorno emulado (plataforma edge con límites de recursos + emulación OBD-II), el banco de fallos parametrizable con fallos conocidos y held-out, el ground truth de eventos derivado del generador, y la captura y persistencia de telemetría. La parte metodológica (banco reproducible con ground truth, carencia real del área) es instrumento de C-EXP; la infraestructura (Docker, adquisición, esquemas) se declara ingeniería habilitadora.
*CV: suite reproducible byte a byte con ≥5 fallos conocidos + 3 held-out y GT de eventos; pérdida de muestras <1 %.* — Justifica: V5. Habilita: todas las H.

**OE3 [X/C] — Detección contextual basada en eventos.** Segmentar la telemetría en eventos operativos con evaluación propia de la segmentación (P/R/F1 por tipo, error de inicio/fin, IoU temporal contra el GT del emulador) y comparar experimentalmente las representaciones de detección E0–E4 (punto / ventana / régimen / evento / evento+vehículo), incluyendo el brazo de personalización (global vs individual vs jerárquico).
*CV: segmentación con calidad suficiente pre-registrada para sostener E3/E4; comparación E0–E4 completa con las métricas mínimas (P, R, F1, FPR, retardo, F1 por evento, recursos edge).* — Justifica: **V7**, V3. Contrasta: **H-EVT, H-PERS**. Contribuciones: C-EVT, C-PERS.

**OE4 [A+X] — Razonamiento diagnóstico multiagente con recuperación y verificación.** Implementar el sistema multiagente orquestado (roles lógicos sobre SLM compartido: eventos, anomalías, historial, RAG, hipótesis, crítico/verificador, explicación; vía rápida mono-agente) con su pipeline RAG sobre corpus técnico (métricas IR propias: hit rate, MRR, nDCG), y someter la descomposición a la ablación A0–A6 y la cadena de explicación a la comparación LLM / +RAG / +RAG+verificación.
*CV: ablación A0–A6 ejecutada con las nueve métricas acordadas y compromiso de reportar si el monolítico gana; evaluación de explicaciones en dos capas (juez calibrado ≠ generador + submuestra validada manualmente).* — Justifica: **V6**, V4. Contrasta: **H-MAS, H-EXP**. Contribuciones: C-INT, C-EXP.

**OE5 [C] — Memoria evolutiva con validación.** Implementar la memoria por vehículo con ciclo de estados de evidencia (observación → anomalía → patrón candidato → hipótesis → validación → confirmada/descartada → conocimiento), indexación por eventos (Event Memory con baseline histórico por tipo de evento y vehículo) y gates de admisión; evaluarla frente a sin-memoria y frente a memoria sin validación, incluyendo escenarios de propagación de errores.
*CV: ablación de memoria con métricas de mejora diagnóstica y de consolidaciones erróneas evitadas; resultados reportados aunque sean negativos.* — Justifica: **V2**. Contrasta: **H-MEM**. Contribución: C-MEM.

**OE6 [X] — Evaluación integradora end-to-end.** Evaluar el sistema completo frente a la hipótesis integradora H-MAIN con el protocolo held-out/open-set aplicado simultáneamente a datos, corpus RAG y memoria (H2b), bajo los criterios transversales edge, con protocolo experimental pre-registrado y análisis de amenazas a la validez.
*CV: capítulo de resultados con las seis familias resueltas (aceptadas o refutadas), tablas, análisis de errores y discusión de validez.* — Justifica: V1, V5. Contrasta: **H-MAIN** (y cierra todas las parciales). Contribuciones: C-INT, C-EXP.

**OE7 [I] — Sistema demostrador.** API REST documentada e interfaz mínima para visualizar estado, alertas y diagnósticos de extremo a extremo. **Ingeniería habilitadora y entregable de producto: no responde a ninguna RQ y no se presentará como contribución** (igual que Docker, contratos, Tool Registry, ciclo ONNX y gobernanza de modelos, que se documentan como decisiones de ingeniería).
*CV: demostración funcional de un caso completo.* — Justifica: usabilidad del prototipo.

**OE8 [adm.] — Memoria del TFM.** Redactar la memoria conforme a la plantilla UAX, con estilo científico, decisiones justificadas, limitaciones declaradas y las afirmaciones de novedad ajustadas a `afirmaciones_novedad.md`.
*CV: documento completo entregado en plazo.*

*Objetivos secundarios OS1–OS3 (app móvil, sincronización cloud, Raspberry Pi física) se mantienen tal cual: no condicionan la aprobación.*

## 4. Hipótesis: una integradora y cinco parciales

**H-MAIN es la hipótesis integradora — el contraste directo de la pregunta principal.** Las cinco parciales explican *por qué* el sistema integrado funciona o no: cada una aísla un mecanismo y su refutación no invalida la pregunta, sino que precisa qué parte del diseño aporta y cuál no. Especificación completa (VI/VD/baseline/escenario/métricas/umbral/refutación) en la auditoría §4; los umbrales ◊ se pre-registran en el protocolo E3 antes del primer experimento.

**H-MAIN (integradora):** el sistema integrado detecta como anómalos, señala como no cubiertos, formula hipótesis plausibles y explica patrones held-out/open-set retirados simultáneamente del detector, del corpus RAG y de la memoria — en lugar de identificarlos erróneamente con confianza. *Refutación: identificación confiada errónea de los held-out o hipótesis no mejores que el azar → respuesta negativa a la parte fuerte de la PI, reportada con análisis.*

**H-EVT (parcial — mecanismo de contexto):** el baseline por evento (y por evento+vehículo) reduce falsos positivos y mejora la detección de anomalías contextuales frente a la detección global por puntos o ventanas (E0–E4). *Refutación: sin mejora sobre E1 → el evento queda como representación semántica para el razonador, no como mejora de detección.*

**H-MEM (parcial — mecanismo de memoria):** la memoria con ciclo de validación mejora el diagnóstico en casos repetidos/variantes y consolida menos errores que la memoria sin validación, sin degradar casos nuevos. *Refutación: la validación no reduce consolidaciones erróneas o su coste anula la mejora → C-MEM queda como mecanismo de seguridad con resultado negativo documentado.*

**H-MAS (parcial — mecanismo arquitectónico):** la descomposición multiagente aporta valor frente al agente monolítico en los casos complejos, a coste (latencia/tokens) acotado; existe un punto identificable de la curva calidad-coste donde deja de pagar. *Refutación: el monolítico iguala en todos los estratos → se reporta como resultado principal y la arquitectura se justifica solo por mantenibilidad/seguridad.*

**H-PERS (parcial — mecanismo de personalización):** el baseline jerárquico (flota→vehículo, por evento) iguala o supera al individual y supera al global en FPR, con arranque en frío acotado. *Refutación: el global no es peor → se declara la limitación del entorno sintético para esta pregunta.*

**H-EXP (parcial — mecanismo de explicación):** la verificación determinista de hipótesis contra las features reduce las afirmaciones factualmente incorrectas de las explicaciones frente a LLM solo y LLM+RAG sin verificación, manteniendo utilidad. *Refutación: sin reducción de errores factuales → C-EXP queda como propuesta de diseño con resultado negativo.*

## 5. Criterios transversales Edge (antes H4 — restricciones de aceptación, no hipótesis)

Todo experimento reporta latencia por etapa, memoria RAM, y tokens/throughput del SLM cuando aplique, en el perfil de recursos emulado equivalente a Raspberry Pi 5 (8 GB); un resultado que viole el presupuesto edge se reporta como no viable aunque gane en calidad; la viabilidad agregada del pipeline completo (PI.4) se responde con el conjunto de estas mediciones; y la diferencia metodológica emulación-vs-hardware-real se declara (OS3 la cierra si hay tiempo).

## 6. Mapa Pregunta → Objetivos → Hipótesis

```text
PREGUNTA PRINCIPAL (A o B): descubrir y explicar patrones no documentados
        │
OBJETIVO GENERAL (§2: sistema Edge-Cloud, eventos, multiagente, memoria validada)
        │
        ├── OE1 Estado del arte [M] ──────────── fundamenta RQ1-RQ17 · V1-V7
        ├── OE2 Banco experimental [M+I] ─────── habilita todas las H (V5)
        │
        ├── OE3 Detección por eventos [X/C] ──── H-EVT · H-PERS   (V7, V3 → C-EVT, C-PERS)
        ├── OE4 Multiagente + verificación [A+X]─ H-MAS · H-EXP    (V6, V4 → C-INT, C-EXP)
        ├── OE5 Memoria validada [C] ─────────── H-MEM             (V2 → C-MEM)
        │
        ├── OE6 Evaluación integradora [X] ───── H-MAIN  ◄── integra H-EVT/H-MEM/H-MAS/H-PERS/H-EXP
        │                                        (V1, V5 → C-INT, C-EXP)
        ├── OE7 Demostrador [I] ──────────────── sin RQ (producto)
        └── OE8 Memoria del TFM [adm.]
        
CRITERIOS TRANSVERSALES EDGE: aplican a OE3-OE6 (latencia, RAM, coste; PI.4)
```

**Correspondencia con los objetivos originales:** OE1←OE1 · OE2←OE2+OE3 · OE3←OE4+OE-EVT(nuevo)+brazo C-PERS · OE4←OE5+OE6 · OE5←OE7 · OE6←OE8 · OE7←OE9 · OE8←OE10. **Correspondencia de hipótesis:** H1→precondición de H-EVT · H2→dentro de H-EXP · H2b→H-MAIN · H3/H5→H-MEM · H6/PI.5→H-EVT · H4→criterios transversales. Subpreguntas: PI.1–PI.5 se conservan; PI.6 (multiagente) y PI.7 (personalización) se añaden solo si se adopta la Opción A o si el tutor las quiere explícitas — con la Opción B pueden vivir como preguntas operativas del plan experimental.

## 7. Procedimiento de actualización (tras la decisión)

Elegida la PI: (1) reescribir docs/01 §1.3–1.4 (PI + subpreguntas + seis familias H + criterios transversales) y docs/02 (OG + OE1–OE8 + OS1–OS3) en un único commit; (2) pre-registrar los umbrales ◊ en el protocolo E3; (3) propagar la numeración nueva a los planes R1-R5/E1-E4 y al harness (renombrar referencias H1–H6 → familias); (4) verificar que el capítulo 2 §2.16–2.17 no requiere más cambio que la referencia a la numeración final. Nada de esto se ejecuta antes de la decisión.
