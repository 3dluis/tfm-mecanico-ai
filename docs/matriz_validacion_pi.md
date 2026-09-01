# Matriz de validación de la pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de
> datos OBD-II reales, rastreando cada explicación hasta su evidencia de origen,
> y reconocer cuándo la evidencia disponible no es suficiente para sostener una
> explicación en lugar de generar una hipótesis sin fundamento?

La pregunta se descompone en cuatro subpreguntas evaluables por separado. Cada
una tiene su criterio fijado **antes** de la evaluación final, y cada una puede
resultar no sostenida sin arrastrar a las demás.

Las columnas «Resultado» y «Decisión» se rellenan en E19, no antes.

| PI | Objetivo | Hipótesis | Dataset | Experimento | Métrica | Criterio | Resultado | Decisión |
|---|---|---|---|---|---|---|---|---|
| **PI.1** Diagnóstico a partir de OBD-II real | Que un modelo especializado produzca un diagnóstico útil sobre datos reales | Un modelo temporal sobre ventanas OBD-II supera de forma clara al baseline y a la clase mayoritaria | Real, test aislado | E8 | M1: F1 macro, PR-AUC, calibración | Supera al baseline con margen no atribuible al azar, y la confianza está calibrada | _pendiente_ | _pendiente_ |
| **PI.2** Explicación trazable | Que cada afirmación se siga hasta su evidencia | Toda afirmación de una explicación se ancla en una observación o en un fragmento identificable | Real, condición FULL | E14, E17 | M4: `citation correctness`, `citation completeness`, `claim support rate` | Corrección y completitud de citación por encima del umbral fijado, y `unsupported claim rate` por debajo del suyo | _pendiente_ | _pendiente_ |
| **PI.3** Reconocimiento de insuficiencia | Que el agente se abstenga cuando la evidencia no basta | Al retirar la evidencia relevante del corpus, el agente pasa de explicar a abstenerse sobre el mismo caso | Real, condiciones FULL / PARTIAL / ABSENT | E16, E17 | M5: abstención correcta, abstención injustificada, cobertura | La tasa de abstención difiere sustantivamente entre FULL y ABSENT, y la explicación sin fundamento se mantiene por debajo del umbral | _pendiente_ | _pendiente_ |
| **PI.4** Rechazo de evidencia engañosa | Que la similitud no se confunda con soporte | Ante evidencia parecida pero incorrecta, el agente no la acepta como soporte | Real, condición DISTRACTOR | E17 | M5 sobre DISTRACTOR; M2 por condición | El distractor no aparece como soporte de ninguna afirmación admitida; en ausencia de otra evidencia suficiente, el agente se abstiene | _pendiente_ | _pendiente_ |

## Umbrales

Los valores numéricos de cada criterio se fijan al cerrar E15, sobre validación,
y quedan registrados en el informe de esa fase antes de tocar el conjunto de
test. Hasta entonces esta sección está deliberadamente vacía: escribir aquí un
número después de ver los resultados anularía el propósito de la matriz.

## Criterios de refutación

La respuesta global admite tres valores:

| Valor | Cuándo |
|---|---|
| **Sostenida** | Las cuatro subpreguntas cumplen su criterio |
| **Parcialmente sostenida** | PI.1 y PI.2 se cumplen, pero PI.3 o PI.4 no |
| **No sostenida** | PI.2 o PI.3 no se cumplen |

PI.2 y PI.3 son las que sostienen el trabajo. Sin trazabilidad no hay explicación
verificable; sin reconocimiento de insuficiencia, el sistema es un generador de
hipótesis con buena presentación.

## Desenlaces que refutarían la pregunta

Se enumeran de antemano para que el experimento pueda fallar:

- la tasa de abstención es indistinguible entre FULL y ABSENT: el agente no
  reacciona a la disponibilidad de evidencia;
- las referencias existen y resuelven, pero no sostienen lo afirmado: la
  trazabilidad es aparente;
- el distractor se acepta como soporte: el sistema confunde similitud con
  pertinencia;
- el agente se abstiene también en FULL, con cobertura próxima a cero: la
  abstención es trivial y no informa de nada;
- el modelo especializado no supera al baseline: no hay diagnóstico que explicar.

Cualquiera de estos desenlaces se reporta tal cual, sin reinterpretarlo como
éxito parcial.
