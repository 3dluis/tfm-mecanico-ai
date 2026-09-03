# ADR-003 — La pregunta de investigación deja de exigir que los datos OBD-II sean reales

**Fecha:** 3 de septiembre de 2026 · **Estado:** aceptado
**Ámbito:** pregunta · dataset · alcance
**Decide:** Luis Daniel Díaz (autor)
**Registro:** ADR académico. Enmienda fechada y no retroactiva sobre la PI del marco
canónico (ADR-001). Los documentos anteriores a esta fecha conservan el enunciado anterior
como registro histórico y no se reescriben.

## Contexto

La PI del marco canónico (ADR-001, 1 de septiembre de 2026) exigía «datos OBD-II reales».
La fase que los incorpora (E3) lleva bloqueada desde el inicio por falta de una fuente con
fallos etiquetados y documentación de taller aplicable (`research/e3-candidatos-datos.md`).
Mientras tanto, E1–E17 se han ejecutado sobre `synthetic_v2`, un conjunto sintético cuyas
constantes están ancladas una por una al manual del vehículo
(`docs/methodology/calibracion-datos-sinteticos.md`).

La consecuencia estaba registrada como bloqueante: I-07 en la matriz de trazabilidad, L-01
en el registro de limitaciones y observación de GATE-01. La matriz de validación respondía
a una «versión condicional» de la pregunta, y `research/e3-candidatos-datos.md` advertía
que, sin datos reales etiquetados, «la PI debe reformularse antes de seguir, no después».

## Problema

¿Debe la validez de la pregunta de investigación depender de que los datos OBD-II sean
exclusivamente reales, cuando lo que la pregunta interroga es la capacidad del agente de
explicar con trazabilidad y de abstenerse ante evidencia insuficiente?

## Opciones consideradas

| Opción | A favor | En contra | Coste |
|---|---|---|---|
| A. Mantener «reales» y esperar a E3 | La PI no cambia; máxima validez externa | E3 sin fuente; toda la evidencia acumulada responde a una pregunta «condicional»; riesgo de llegar al depósito sin poder responder la PI literal | Calendario: informe 1 el 18 o 30 de septiembre |
| B. Mantener «reales» y evaluar sobre sintéticos | Ningún cambio documental | Sería presentar como respuesta a una pregunta lo que responde a otra: el defecto que el propio trabajo estudia | Integridad |
| **C. Eliminar «reales» de la PI y declarar la procedencia de cada dataset** | La pregunta interroga capacidades del agente (explicación, trazabilidad, suficiencia, abstención) que no dependen del origen del dato; la procedencia pasa a ser una variable declarada y una limitación de validez externa, no una precondición | Se pierde la promesa de validez externa en el enunciado; hay que impedir que un resultado sintético se lea como comportamiento en vehículo real | Actualización transversal controlada; ADR; matriz; capítulos |
| D. Reformular la PI sobre «datos sintéticos» | Máxima honestidad literal | Cerraría la puerta a datos reales, que siguen siendo valiosos; la pregunta no es sobre el tipo de dato | Alcance |

## Decisión

La pregunta de investigación oficial pasa a ser, exactamente:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una
> hipótesis sin fundamento?

Sustituye a la versión con «datos OBD-II reales». La palabra «reales» no vuelve a la PI.

Reglas que acompañan a la decisión:

1. **Cada dataset declara su procedencia** con una taxonomía cerrada: `real`, `synthetic`,
   `simulated`, `public_dataset` (`src/mecanico_ia_exp/data/metadata.py`). Ningún resultado
   se publica sin la procedencia del dato sobre el que se obtuvo.
2. **Los datos sintéticos no se presentan nunca como reales.** Sirven para desarrollo,
   inyección controlada de fallos, equilibrio de escenarios, ablaciones y las cuatro
   condiciones FULL / PARTIAL / ABSENT / DISTRACTOR. Un resultado sobre sintéticos
   caracteriza el comportamiento del agente ante los mecanismos representados; no
   demuestra comportamiento equivalente en un vehículo real, y así se dice en metodología,
   resultados y limitaciones.
3. **Los datos reales siguen siendo un objetivo.** E3 deja de ser precondición de la PI y
   pasa a ser fase de validación externa: si se obtienen, se usan como evidencia adicional,
   con vehículo, sesión, señales, frecuencia, condiciones, procedimiento de adquisición y
   limitaciones declarados.
4. **El problema científico no cambia.** Una explicación plausible sigue sin ser una
   explicación sustentada; el experimento central sigue siendo FULL / PARTIAL / ABSENT /
   DISTRACTOR sobre el mismo caso; el alcance no se amplía hacia descubrimiento autónomo,
   memoria evolutiva ni aprendizaje continuo.

## Justificación

Las cuatro subpreguntas interrogan propiedades del agente, no del dato: si diagnostica
(PI.1), si la explicación es trazable (PI.2), si reconoce la insuficiencia (PI.3) y si
rechaza evidencia engañosa (PI.4). De ellas, solo PI.1 depende materialmente del realismo
de la telemetría; PI.2, PI.3 y PI.4 se deciden manipulando la evidencia documental con
datos, modelo y atribución fijos, y la matriz de validación ya señalaba (E2) que son las
que menos cambiarían con datos reales. Exigir «reales» en el enunciado condicionaba las
cuatro a una precondición que solo afecta a una.

La alternativa B queda descartada por integridad: responder sobre sintéticos a una
pregunta que dice «reales» es tener una referencia sin tener soporte.

## Impacto

| Elemento | Impacto |
|---|---|
| Pregunta de investigación | enunciado sustituido en todas sus apariciones vivas; el histórico se conserva |
| Subpreguntas PI.1–PI.4 | sin cambio de fondo; PI.1 se lee «a partir de OBD-II» sin adjetivo |
| Objetivo general | la reformulación propuesta (opción A, 1 de septiembre) ya escribía «datos OBD-II»; deja de estar «a la espera de E3» |
| Objetivos específicos | OE2 deja de estar bloqueado por E3; E3 pasa a validación externa |
| Hipótesis | la columna «dataset» pasa de «real» a «procedencia declarada»; ninguna hipótesis se modifica en su predicción ni en su criterio |
| Vacío | GAP-01 se reformula sin «reales»; el tipo de dataset no es el vacío |
| Experimentos | E3 cambia de rol; E19 y E20 dejan de estar bloqueadas por E3 y pasan a depender de la decisión del autor sobre el dataset de evaluación final |
| Métricas | sin cambio; los registros añaden `dataset_type` cuando se reporten |
| Matriz de validación | la «versión condicional» desaparece; la condición pasa a ser una columna de procedencia y una limitación |
| Capítulos | 1, 2, 4, 5, 6 y resumen: se retiran las frases que condicionaban la respuesta al enunciado anterior; se conservan las que declaran la limitación de validez externa |
| Limitaciones | L-01 sigue siendo crítica como validez externa; deja de ser «la PI dice reales» |
| Pre-registro | no hay pre-registro congelado del marco canónico (L-07, ADR-002); esta enmienda se registra aquí y se citará en el pre-registro cuando se congele |

## Evidencia

| Tipo | Fuente |
|---|---|
| E2 | `docs/matriz_validacion_pi.md` — dependencia de cada subpregunta respecto del realismo del dato |
| E2 | `docs/methodology/calibracion-datos-sinteticos.md` — anclaje de cada constante al manual |
| E4 | `research/e3-candidatos-datos.md` — ausencia de fuente con fallos etiquetados |
| E4 | `research/propuestas-objetivos.md` §1 — reformulación del OG ya sin «reales» |

## Reversibilidad

Basta reponer «reales» en el enunciado y volver a marcar E3 como precondición. Se perdería
la posibilidad de responder la PI con la evidencia acumulada hasta que E3 se resuelva. Los
resultados no cambian: cambia qué pregunta responden.

## Registro de aplicación

La actualización transversal, con la clasificación de cada aparición y el changelog, está
en `docs/tfm/cambio_pi_eliminacion_datos_reales.md`.
