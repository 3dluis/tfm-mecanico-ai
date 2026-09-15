# Auditoría diferencial: versión v2.0 (18-08-2026) → pregunta acotada

**Fecha:** 15 de septiembre de 2026 · **Base histórica:** «TFM UAX — Estado del Arte y
Metodología de Investigación v2.0 18ago2026.docx» (fuera del repositorio; solo lectura) ·
**Intermedia:** «TFM - Luis Daniel Diaz Diaz - v20260828-01.docx» (plantilla con capítulos
1–3, 28-08-2026) · **Versión actual:** `docs/memoria/`, commit `ebca11e` y siguientes.

La v2.0 no es fuente canónica. Se usa solo para detectar qué ha sobrevivido de una
investigación que ya no es la que la memoria responde. La autoridad es el feedback del
director de septiembre de 2026 y ADR-004 (la pregunta canónica es la acotada).

## 1. Cambio de investigación

| Elemento | Versión v2.0 (18-08) | Versión actual | ¿Sigue en alcance? | Acción |
|---|---|---|---|---|
| Pregunta de investigación | «¿Puede un sistema inteligente híbrido identificar patrones de fallo no representados en su conocimiento disponible, generar hipótesis diagnósticas a partir del análisis contextual y longitudinal de datos OBD-II y validarlas mediante evidencia antes de incorporarlas como conocimiento reutilizable?» | La acotada del capítulo 1: explicar el diagnóstico rastreando cada explicación hasta su evidencia y reconocer cuándo la evidencia no basta | Solo la acotada | Escrita una vez, en el capítulo 1; el resto remite a ella. Verificado: el texto de la pregunta aparece una sola vez en la memoria |
| Descomposición | PI.a detección contextual y longitudinal · PI.b reconocer que el conocimiento no cubre el patrón · PI.c hipótesis y contraste · PI.d consolidación validada o abstención · PI.e | PI.1 diagnóstico y calibración · PI.2 trazabilidad · PI.3 reconocer la insuficiencia · PI.4 rechazar evidencia engañosa | PI.1–PI.4 | PI.a, PI.b y PI.d no aparecen en la memoria |
| Objetivo general | Estudiar la transición anomalía → hipótesis → conocimiento reutilizable en un sistema híbrido Edge–Cloud | Evaluar experimentalmente un agente de recuperación aumentada por evidencia en su capacidad de explicar con correspondencia verificable y de abstenerse | El actual, bloqueado | Sin cambios |
| OE1 | Estado del arte sobre RQ1–RQ17, vacío V* y dimensiones S1–S6 | Revisión en cuatro frentes para delimitar el vacío | Sí | LEGACY_VALID (reformulado en agosto-septiembre) |
| OE2 | Banco con fallos conocidos y *held-out*, eventos con verdad de referencia y restricciones de un dispositivo *edge* | Entorno reproducible con telemetría, corpus del vehículo y condiciones de evidencia | Sí, sin *held-out* ni *edge* | LEGACY_VALID en su parte de reproducibilidad; *held-out* y *edge* no aparecen |
| OE3 | Detección contextual basada en eventos; modelos personalizados por vehículo (H-EVT, H-PERS) | Hasta el 14-09: «identificar y caracterizar patrones de comportamiento»; desde el 15-09: evaluar el diagnóstico del modelo y caracterizar su confianza y sus señales | Sí, en su versión actual | **LEGACY_SCOPE_LEAK corregido** el 15-09: «identificar patrones» arrastraba el verbo de la PI amplia |
| OE4 | Arquitectura multiagente, ablaciones A0–A6, tres niveles LLM / LLM+RAG / LLM+RAG+verificación (H-MAS, H-EXP) | Agente que contrasta hipótesis con evidencia observacional y documental con criterio explícito de suficiencia | Sí | LEGACY_VALID: la verificación y la separación LLM / decisión proceden de H-EXP; lo multiagente no aparece |
| OE5 | Memoria evolutiva validada que distinga observación, anomalía, hipótesis y conocimiento confirmado (H-MEM) | Hasta el 14-09: cuatro condiciones «y la contribución de sus principales componentes»; desde el 15-09: cuatro condiciones distinguiendo explicaciones sostenidas, sin soporte y abstenciones innecesarias | Sí, en su versión actual | La memoria evolutiva no aparece. **REMOVE_OR_REWRITE corregido** el 15-09: «contribución de sus principales componentes» exigía ablaciones no ejecutadas como condición del objetivo; las ablaciones quedan como trabajo pendiente del diseño |
| OE6 | Evaluación integral *held-out/open-set* con exclusión triple y decisión de consolidación o abstención (H-MAIN) | — | No | No aparece. La evaluación final sobre el conjunto de prueba es otra cosa (partición cerrada del mismo catálogo) |
| OE7, OE8 | Demostrador con API REST · memoria del TFM | — | No como objetivos | No aparecen |
| Hipótesis | H-MAIN, H-EVT, H-PERS, H-MEM, H-MAS, H-EXP | Una por subpregunta, con desenlaces de sostenimiento y refutación (Tabla 4.6) | Las actuales | Ningún identificador H-* en la memoria |
| Vacío | V*: cómo pasar de un patrón no representado a hipótesis verificable y a conocimiento reutilizable | Diagnóstico OBD-II que termina en la clasificación; RAG técnico que mide la respuesta y no la correspondencia afirmación ↔ fragmento; abstención como disposición del modelo | El actual | **LEGACY_SCOPE_LEAK corregido** el 15-09 en §Propósito y procedimiento de la revisión («cuándo ese patrón no está en el conocimiento del sistema») y en §Vacío y posicionamiento («para que una hipótesis no se convierta en conocimiento… lo que acaba conservándose») |
| Contribución | C1 operacionalización de «patrón no representado»; C2 protocolo anomalía → hipótesis contrastada; C3 consolidación | Evidencia experimental sobre el comportamiento del agente bajo condiciones controladas de evidencia (capítulo 4, apertura) | La actual | C1–C3 no aparecen |
| Diseño experimental | Eventos E0–E4, personalización, ablaciones A0–A6, *held-out/open-set*, nueve controles negativos, dispositivo *edge* | Mismo caso bajo FULL / PARTIAL / ABSENT / DISTRACTOR con todo lo demás constante | El actual | LEGACY_VALID: la documentación distractora plausible era uno de los nueve controles negativos de la v2.0 y se conserva como condición DISTRACTOR |
| Variables | Contexto, historial, personalización, estado de la memoria | Una manipulada (evidencia documental disponible) y las controladas del capítulo 4 | Las actuales | Sin restos |
| Métricas | Acierto, abstención correcta y resistencia a la contaminación | M1–M6; M5 con T_FC y T_AI separadas | Las actuales | LEGACY_VALID: «abstención correcta» procede de la v2.0 y se mantiene dentro de M5 |
| Fases | F0–F22 del repositorio de ingeniería | E1–E20 del laboratorio | E1–E20 | Sin restos de F* en la memoria |
| Resultados | Ninguno | Parciales sobre validación (capítulo 5) | — | — |
| Discusión | — | Por subpregunta PI.1–PI.4 | — | Sin restos |
| Conclusiones | — | Hasta el 14-09: una respuesta condicionada; desde el 15-09: por objetivo, de OE1 a OE5 y después el general | Las actuales | Sin requisitos de la PI amplia |
| Trabajo futuro | — | Datos reales, otros vehículos, casos más difíciles, plataforma embarcada, reutilización de explicaciones validadas | Como prospectiva | Ver §2 |

## 2. Apariciones en la memoria actual y su clasificación

| Sección | Aparición | Clase | Acción |
|---|---|---|---|
| 3.1 Propósito y procedimiento de la revisión | «Una primera revisión… respondía a una formulación de la pregunta que después cambió» | LEGACY_VALID | Se conserva: explica de dónde procede el corpus de referencias |
| 3.1 | «cuándo ese patrón no está en el conocimiento del sistema» | LEGACY_SCOPE_LEAK | Retirado el 15-09 |
| 3.6 Vacío y posicionamiento | «que una hipótesis no se convierta en conocimiento… lo que acaba conservándose» | LEGACY_SCOPE_LEAK | Reescrito el 15-09: «no se dé por validada… lo que finalmente se afirma» |
| 2.2 Objetivos específicos, OE3 y Tabla 2.1 | «identificar y caracterizar patrones de comportamiento» | LEGACY_SCOPE_LEAK | Reescrito el 15-09 |
| 2.2, OE5 | «así como la contribución de sus principales componentes» | REMOVE_OR_REWRITE | Reescrito el 15-09 |
| 1.2 Presentación | «Un modelo especializado analiza la telemetría y caracteriza los patrones observados» | LEGACY_SCOPE_LEAK (léxico) | Reescrito en esta iteración: el modelo obtiene un diagnóstico y estima su confianza |
| 1.1 y 3.2, 3.6 | «detectan anomalías» referido a los trabajos revisados | LEGACY_VALID | Describe antecedentes, no el alcance |
| 3.3 Explicabilidad | «detección contextual de anomalías» (Li y van Leeuwen, 2023) | LEGACY_VALID | Antecedente citado |
| 4.3.4 Instrumentos | «La detección de fallos ajenos al catálogo queda fuera del alcance de este trabajo» | LEGACY_VALID | Declaración explícita de exclusión |
| 4.3.3 Variables medidas, M6 | «el despliegue embarcado… quedó fuera del alcance ejecutado» | LEGACY_SCOPE_LEAK (léxico) | «alcance ejecutado» sugería un alcance mayor aprobado; se escribe «queda fuera del alcance de este trabajo» |
| 6.2 Limitaciones | «catálogo cerrado… se recoge entre las líneas futuras» | LEGACY_FUTURE | Se conserva. La prospectiva no lo recogía: se añade una línea |
| 6.3 Prospectiva | Plataforma embarcada | LEGACY_FUTURE | Se conserva como línea posterior |
| 6.3 Prospectiva | «conservar las explicaciones que superaron la validación para reutilizarlas» | LEGACY_FUTURE | Se conserva: es la única huella del conocimiento reutilizable y está formulada como pregunta abierta, con sus riesgos, fuera del alcance |
| Resumen, capítulos 4 y 5 | — | — | Ninguna aparición de patrones no representados, conocimiento reutilizable, memoria evolutiva, consolidación, eventos, personalización, multiagente, *held-out*, *open-set* ni Edge–Cloud |

## 3. Numeración de la versión intermedia (28-08-2026)

El DOCX del 28-08 tenía cinco errores de numeración en el capítulo 3, que el texto fuente en
Markdown no tiene porque la numeración la pone la plantilla al componer: 3.2.3 como primer
subapartado de 3.2; 3.2.4 repetido; «Modelos de lenguaje y recuperación aumentada» como
subapartado 3.3.1 cuando es un apartado; salto de 3.3.2 a 3.3.4; y el resto del capítulo
desplazado un nivel. La numeración correcta, derivada de la jerarquía del texto fuente, está en
`docs/memoria/LEEME.md` §Numeración para la composición.
