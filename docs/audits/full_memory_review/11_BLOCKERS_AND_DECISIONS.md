# 11 · Bloqueantes y decisiones que requieren intervención

**Fecha:** 10 de septiembre de 2026 · **Estado del repositorio:** `b0e13e2`.

---

## `SCIENTIFIC_DECISION_REQUIRED` · SD-01 — Dos preguntas de investigación en circulación

Registrado conforme a la sección 36 del encargo de revisión integral. **No se ha elegido
ninguna versión.**

### Las dos versiones encontradas

| | Enunciado | Dónde consta |
|---|---|---|
| **A · la de la memoria** | ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin fundamento? | `cap1_introduccion.md:21`; `ADR-001` enmendado por `ADR-003` (aceptado el 3 de septiembre de 2026, decide el autor) |
| **B · la del mandato** | ¿Puede un sistema inteligente híbrido identificar patrones de fallo no representados en su conocimiento disponible, generar hipótesis diagnósticas a partir del análisis contextual y longitudinal de datos OBD-II y validarlas mediante evidencia antes de incorporarlas como conocimiento reutilizable? | encargos de revisión de septiembre de 2026, declarada `LOCKED` |

### Evidencia sobre cada componente de la versión B

Auditado conforme a las secciones 12, 13, 14 y 20 del encargo.

| Componente | Estado | Evidencia |
|---|---|---|
| **PI-A** patrón no representado | **AUSENTE** | El modelo especializado clasifica en **cinco clases conocidas y etiquetadas**. No existe definición operacional de «no representado», ni mecanismo de detección fuera de distribución, ni condición experimental que la construya. Búsqueda de `unknown`, `out_of_distribution`, `novel`, `unseen` en el modelo y en la abstención: sin resultados aplicables |
| **PI-B** generación de hipótesis | **AUSENTE** | Búsqueda de `hipótesis` y `hypothesis` en todo el código: **cero coincidencias**. El modelo clasifica y el agente redacta; ningún componente genera una hipótesis diagnóstica en el sentido de la pregunta |
| **PI-C** contexto longitudinal | **PARCIAL, y desconectado** | Existe un modelo temporal recurrente sobre las series de la ventana. Pero el agente **no lo usa**: `sufficiency_runner` diagnostica con el bosque aleatorio. El componente longitudinal existe y no alimenta el diagnóstico que el agente explica |
| **PI-D** validación por evidencia | **PRESENTE** | Es el núcleo del trabajo: recuperación, verificación determinista, criterio de suficiencia y abstención |
| **PI-E** conocimiento reutilizable | **AUSENTE** | Ninguna implementación. La única aparición de «memoria evolutiva» en la memoria es la frase que declara que el estado del arte de agosto respondía a **una pregunta anterior** |

**Uno de cinco componentes tiene evidencia.**

### Impacto de adoptar cada versión

**Si la canónica es A.** El trabajo responde a su pregunta con el alcance que las auditorías ya
han acotado. El aparato experimental —veinte fases, seis grupos de métricas, cuatro condiciones—
está construido para ella. Es la que el director validó en su revisión de septiembre.

**Si la canónica es B.** Cuatro de sus cinco componentes quedan sin evidencia, y la sección 9 del
mandato («`RESEARCH_QUESTION_COMPONENT ∈ {PI.1..PI.5}` o `OUT_OF_SCOPE`») dejaría fuera de
alcance casi todo lo ejecutado, incluido lo que el director aprobó. El TFM tendría que declarar
que no puede responder cuatro quintas partes de su propia pregunta.

### Un dato que no depende de la decisión

La versión B contiene exactamente los elementos que el propio autor ordenó buscar y retirar como
**restos de formulaciones anteriores**, en el encargo del 10 de septiembre de 2026, sección 2:
generación automática de conocimiento, conversión de hipótesis en conocimiento, descubrimiento de
fallos desconocidos como objetivo principal, validación automática de hipótesis e incorporación
automática de conocimiento.

Y el capítulo 3 declara, desde antes de esta revisión, que el estado del arte de agosto «responde
a la pregunta de investigación **anterior** (memoria evolutiva, multiagente, edge) y **no se
reutiliza como texto**».

### Recomendación

**Conservar A como canónica**, y tratar B como visión de largo plazo cuyos componentes ausentes
pertenecen a la prospectiva. Es coherente con `ADR-003`, con la memoria, con el aparato
experimental y con la validación del director.

Si la decisión fuera adoptar B, el camino correcto **no** es reescribir la memoria para que la
mencione, sino un ADR que derogue `ADR-001` y `ADR-003`, reconstruir el aparato experimental
para cubrir identificación, generación de hipótesis e incorporación de conocimiento, y
comunicarlo al director, cuya validación se refiere al diseño actual.

### Qué queda detenido y qué continúa

**Detenido:** toda afirmación sobre cobertura de la pregunta, el capítulo 6 en su respuesta a la
pregunta, y la matriz de trazabilidad en su columna de componentes.

**Continúa:** las auditorías científicas, la corrección de afirmaciones sobreextendidas, la
bibliografía, la expresión académica y todo lo que no dependa de cuál sea la canónica. Ninguna
de esas correcciones cambia de sentido según la decisión.

---

## `BLOCKED_REQUIRES_EVIDENCE` · Pendientes de la reejecución canónica

| Elemento | Qué falta |
|---|---|
| Cifras de recuperación y suficiencia | reejecución tras corregir la mezcla de espacios de embeddings |
| Magnitudes agregadas de trazabilidad | no calculadas en ningún artefacto |
| Condición con distractor | diagnóstico con recuperación limpia |
| Datos de ajuste del redactor | regeneración y comparación con el conjunto anterior |

## `BLOCKED_REQUIRES_DECISION` · Pendientes del autor o del director

| Elemento | Decisión |
|---|---|
| Objetivo general | un verbo y sin cláusula embarcada (P-01) |
| Tercer objetivo específico | de no supervisado a supervisado (P-02) |
| Acotación del alcance | constancia formal (P-03) |
| Edición de las normas de citación | sexta o séptima (P-04) |
| Capítulo 1 | reescritura previa sin confirmar, ya corregida en sus cuatro defectos |

---

> **Superado por `ADR-004`, 12 de septiembre de 2026.** La dirección resolvió `SD-01` a favor de
> la pregunta acotada y descartó la formulación amplia. Lo que este documento registra sobre los
> componentes de esa formulación era cierto cuando se escribió y se conserva como tal; ya no
> describe el alcance vigente del trabajo.
