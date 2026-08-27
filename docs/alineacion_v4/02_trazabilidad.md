# Alineación científica v4 — Trazabilidad científica

**2026-08-27.** Matriz completa PI → objetivo → hipótesis → experimento → métrica →
evidencia, y reinterpretación de la evidencia ya producida.

**Regla de lectura, vinculante:** si un elemento del repositorio no puede conectarse con
una fila de la matriz §1, no pertenece al núcleo científico — es artefacto, instrumento o
ingeniería, y así debe presentarse. **Toda hipótesis tiene al menos un experimento; todo
experimento responde a una hipótesis o a un objetivo; toda métrica declara qué propiedad
mide. No hay experimentos huérfanos.**

---

## 1. Matriz de trazabilidad

| PI (parte) | SD | Objetivo | Hipótesis | Experimento | Métricas primarias | Estado de la evidencia |
|---|---|---|---|---|---|---|
| **PI.a** — ¿es pertinente la evidencia recuperada? | SD2 | OE-C2 | H-GRD | **EXP-RET-001** | M3 Recall@k · M4 Precision@k · M6 recuperación no pertinente (control) | no ejecutado; bloqueado por R3 (corpus) |
| **PI.b** — ¿puede establecerse y verificarse la correspondencia afirmación→evidencia? | SD3 | OE-C3 | H-TRC | **EXP-EVID-001** (B3 vs B0-attr) | M11 corrección de citación · M12 completitud · M13 profundidad de traza hasta el dato | no ejecutado; bloqueado por R2 y R3 |
| **PI.c** — ¿reduce la verificación las afirmaciones no sustentadas? | SD3 | OE-C3 | H-GRD | **EXP-EVID-001** (B1 vs B2 vs B3, Escenario A) | M8 recuento de afirmaciones no sustentadas · M7 groundedness · M9 fidelidad | no ejecutado |
| **PI.d** — ¿reconoce el sistema la evidencia insuficiente y se abstiene? | SD4 | OE-C4 | H-ABS | **EXP-EVID-001** (Escenario A vs B, C-B y C-B′) | M15 abstención correcta · M17 falsa aceptación · M16 falsa abstención | no ejecutado |
| **PI.e** — ¿mejora la abstención lo que el sistema sí afirma? | SD4 | OE-C5 | H-SEL | **EXP-EVID-001** (curva riesgo-cobertura) | M19 exactitud selectiva · M18 cobertura · M20 AURC | no ejecutado |
| **PI completa** (end-to-end) | SD2+SD3+SD4 | OE-C5 | **H-MAIN v4** | **EXP-EVID-001** + controles CN1–CN4, CN7–CN9 | Q1=M1 · Q2=M7 · Q3=M11 · Q4=M15 · Q5=M17 | no ejecutado |
| **Precondición** — ¿existe un contexto diagnóstico verificable? | SD1 | OE-C1 | (instrumental, sin hipótesis) | **EXP-SEG-001**; serie EXP-ANOM-001…010-R2 + AUDIT-DATA-001 | F1/IoU de segmentación; FPR y recall por episodio | **parcialmente cerrada**: 14 estudios ejecutados (F3–F22); EXP-SEG-001 pendiente |
| **PI.f** — ¿cabe en el presupuesto edge? | transversal | OE-C5 | (criterio de aceptación, no hipótesis) | medición en todo experimento | M22 latencia · M23 RSS · M24 tokens | instrumento corregido (B0.2); sin medición del razonador |

### 1.1 Cobertura inversa (ningún experimento huérfano)

| Experimento | ¿A qué responde? | ¿Se conserva? |
|---|---|---|
| EXP-SEG-001 | OE-C1 (precondición instrumental) | sí, pre-registrado |
| EXP-RET-001 *(nuevo)* | H-GRD + validación del control de disponibilidad | sí |
| EXP-EVID-001 *(nuevo, central)* | H-MAIN, H-GRD, H-TRC, H-ABS, H-SEL | sí |
| EXP-ANOM-001…010-R2, AUDIT-DATA-001 | OE-C1 (evidencia instrumental ya producida) | sí, cerrados |
| EXP-ANOM-004 (E0–E4) | H-EVT → línea instrumental sobre SD1 | conservado, **no condiciona la PI** |
| EXP-PERS-001 | H-PERS → línea instrumental sobre SD1 | conservado, condicionado a D2 |
| EXP-EXP-001 | absorbido por EXP-EVID-001 (brazos B1/B2/B3) | fusionado |
| EXP-COV-001 | absorbido por EXP-EVID-001 (Escenario B) | fusionado |
| EXP-MAS-001 (A0–A6) | H-MAS | **fuera de alcance**, diseño conservado |
| EXP-MEM-001 (M0/M1/M2) | H-MEM | **fuera de alcance**, diseño conservado |
| EXP-MAIN-001 | sustituido por EXP-EVID-001 | reemplazado; su protocolo de exclusión se reutiliza |

De ocho experimentos pendientes en la alineación v3 se pasa a **tres** (EXP-SEG-001,
EXP-RET-001, EXP-EVID-001), dos de ellos ejecutables en una sola sesión de cómputo una vez
resueltos R2 y R3.

---

## 2. Reinterpretación de la evidencia ya producida

**Nada se renumera, se reescribe ni se borra.** Los catorce estudios ejecutados siguen
midiendo lo que midieron; cambia el papel que juegan en el argumento.

| Experimento (fase) | Qué evaluó | Papel bajo la PI v3 | Papel bajo la PI v4 |
|---|---|---|---|
| EXP-ANOM-001 (F3) | selección de detector; LOF elegido | precondición de H-EVT | **instrumento**: fija el detector que produce el contexto diagnóstico |
| EXP-ANOM-002 (F8) | ventana vs evento | piloto de H-EVT | instrumento; motiva la representación del contexto |
| EXP-ANOM-003 (F9) | causa del FPR por eventos | piloto de H-EVT | instrumento |
| EXP-ANOM-005 (F13) | paridad del camino wide (ancla 0.163197) | control de integridad | **se conserva íntegro**: control de integridad de toda la serie |
| EXP-ANOM-006 (F14) | AE vs LOF — AE denegado | negativo | negativo instrumental |
| EXP-ANOM-007 (F16) | XAI sobre la detección; AR@K ≫ azar | primera evidencia XAI | **sube de valor**: la atribución de features es la base de la evidencia telemétrica de M13 |
| EXP-ANOM-008 (F17) | representación fs2-lite — KEEP fs1 | negativo | negativo instrumental |
| EXP-ANOM-009 (F18) | autoencoders temporales — peores | negativo mayor | negativo instrumental |
| AUDIT-DATA-001 (F19) | validez del banco; 7/8 anomalías separables sin modelos | metodológico | **se conserva**: fundamenta que un fallo de detección es del modelo, no del banco |
| F20 (benchmark v2) | cobertura declarada | metodológico | conservado |
| EXP-ANOM-010 (F21) | cobertura declarada ≠ cobertura efectiva | negativo mayor | **hallazgo metodológico reutilizable**, independiente de la PI |
| EXP-ANOM-010-R2 (F22) | con cobertura efectiva, FPR 0.0086 | cierra H1 | **instrumento**: fija la calidad del contexto de entrada |
| F24 — auditoría de contaminación B0.5 | `corpus_v1` viola E-RAG | **hallazgo negativo bloqueante** | **se convierte en punto de partida**: define C-A y motiva la construcción de C-B |
| F25 — `suite_v2` y `cases_v2` congelados | bancos confirmatorios | material de H-MAIN v3 | **material de EXP-EVID-001 sin modificación** |

Tres lecturas que la estructura v4 añade sin tocar ninguna cifra:

1. **La serie F3–F22 deja de ser un fin y pasa a ser el instrumento.** Su conclusión —el
   techo de los detectores densos era la cobertura efectiva de la normalidad, no la
   arquitectura— sigue siendo un resultado metodológico publicable, ahora presentado como
   caracterización del instrumento y no como aportación central.
2. **Los cuatro negativos mayores (F14, F17, F18, F21) son evidencia de disciplina de
   abstención aplicada al propio trabajo.** Bajo la PI v4 esta lectura se refuerza: el
   trabajo estudia precisamente cuándo *no* afirmar, y su propio historial lo ejemplifica.
3. **El hallazgo de F24 cambia de signo.** Que el corpus describiera los mecanismos de las
   clases held-out era un defecto bajo la PI v3 y es la condición de partida bajo la v4: el
   corpus completo existe, y la manipulación experimental consiste en retirar de él lo que
   se quiere que falte.

**Lo que sigue sin evidencia propia:** todo el tramo 4–6 de la cadena (recuperación,
verificación del soporte, decisión). La memoria del TFM debe citar únicamente diseño, no
resultados, sobre explicación, trazabilidad y abstención, hasta que EXP-RET-001 y
EXP-EVID-001 se ejecuten.

---

## 3. Matriz de cobertura de los antecedentes

Los mismos quince trabajos verificados en el corpus de la revisión; las columnas se
recodifican por las capacidades que interroga la PI v4. Codificación: ✔ cubre · ◐ parcial ·
«·» no tratado.

| # | Trabajo | Diagnóstico OBD-II / telemetría física | Explicación | RAG / evidencia recuperada | Trazabilidad y citación verificable | Fidelidad evaluada | Detección de evidencia insuficiente | Abstención declarada | Evaluación conjunta |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Mahale et al. 2025 | ✔ | ✔ | ✔ | ◐ | · | · | · | · |
| 2 | Lin & Miao 2025 | · | ✔ | ◐ | · | ◐ | · | · | · |
| 3 | CADD — Chen et al. 2024 | ✔ | · | · | · | · | ◐ | · | · |
| 4 | DDAS — Murphey et al. 2003 | ✔ | ◐ | · | · | · | · | ◐ | · |
| 5 | SAGE — Kang et al. 2026 [preprint] | ◐ | ✔ | ◐ | · | · | · | · | · |
| 6 | MA-RCA — Fu et al. 2025 | · | ✔ | ✔ | ◐ | ◐ | · | · | · |
| 7 | Giannoulidis et al. 2024 | ✔ | · | · | · | · | ◐ | · | · |
| 8 | Cherdo et al. 2023 | ✔ | · | · | · | · | ◐ | · | · |
| 9 | PARAM — Harbola & Purwar 2025 [preprint] | ◐ | ✔ | ✔ | ◐ | · | · | · | · |
| 10 | Park et al. 2025 | · | ✔ | ✔ | ◐ | ◐ | · | · | · |
| 11 | HDSO — Shang & Yang 2026 [preprint] | · | ✔ | ◐ | · | ◐ | · | · | · |
| 12 | FaultExplainer — Khan et al. 2024 [preprint] | ✔ | ✔ | ◐ | · | · | · | · | · |
| 13 | RAAD-LLM — Russell-Gilbert et al. 2025 [preprint] | ✔ | ✔ | ✔ | ◐ | ◐ | · | · | · |
| 14 | Das et al. 2025 | ◐ | ✔ | · | · | · | · | · | · |
| 15 | DriveAgent — Hou et al. 2025 [preprint] | ◐ | ✔ | · | · | · | · | · | · |

**Lectura de la matriz, obligatoria en la memoria:**

- **Bien cubierto:** el diagnóstico a partir de telemetría (3, 4, 7, 8, 12, 13), la
  explicación mediante modelos de lenguaje (prácticamente todos) y la recuperación de
  evidencia con RAG (1, 6, 9, 10, 13). **No se afirma que falten sistemas RAG para
  diagnóstico vehicular: existen, y Mahale et al. 2025 es el antecedente más próximo**
  (telemetría → ML → RAG → modelo de lenguaje).
- **Parcialmente cubierto:** la trazabilidad. Varios trabajos citan las fuentes
  recuperadas, pero **en los estudios analizados no fue identificada una verificación de
  que la cita sostenga efectivamente la afirmación**, ni una traza que alcance el dato de
  origen. La fidelidad se evalúa en algunos casos (2, 6, 10, 11, 13) y de forma
  mayoritariamente cualitativa.
- **Casi vacío:** las dos últimas columnas útiles. La detección de evidencia insuficiente
  aparece solo como validación de la detección (3, 7, 8), no de la explicación; la
  abstención declarada apenas se trata (4, de forma parcial). **Estas dos columnas son la
  bisagra de V4\* y el foco de PI.d y PI.e.**
- **Evaluación conjunta:** ninguno de los quince recorre la combinación completa
  —diagnóstico OBD-II real, explicación por RAG, trazabilidad verificable y comportamiento
  ante evidencia insuficiente— con evaluación experimental conjunta. Esta es la única
  afirmación de ausencia que la matriz sostiene, y se formula siempre como *«no fue
  identificado en los trabajos revisados»*.

**Antecedentes que obligan a la prudencia y deben citarse dentro de la propia formulación
del vacío:** Mahale et al. 2025 (cubre a+b+c sin trazabilidad verificable ni abstención);
RAAD-LLM (a+b+c con fidelidad, sin trazabilidad ni abstención); MA-RCA y Park et al. 2025
(b+c con atribución parcial, fuera del dominio vehicular con telemetría física).

---

## 4. Estructura argumental del estado del arte

| Bloque | Pregunta | Contenido |
|---|---|---|
| **A. Qué se sabe** | capacidades suficientemente estudiadas | diagnóstico OBD-II con aprendizaje automático · detección no supervisada · RAG técnico · modelos de lenguaje pequeños en el borde |
| **B. Qué se sabe parcialmente** | mecanismos que resuelven partes | explicación con modelos de lenguaje sin verificación del soporte · atribución de citas · evaluación de fidelidad · predicción selectiva e incertidumbre fuera del dominio |
| **C. Qué sigue sin resolverse** | V4\* | la combinación de §3, y en particular las dos columnas casi vacías |
| **D. Por qué importa** | consecuencias | una explicación diagnóstica fluida y no sostenida es más peligrosa que la ausencia de explicación, porque transmite confianza injustificada al usuario final |
| **E. Qué estudia este TFM** | posicionamiento | explicación trazable hasta la evidencia y abstención verificable ante evidencia insuficiente, sobre diagnóstico OBD-II |
