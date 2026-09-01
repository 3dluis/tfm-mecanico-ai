# Diseño experimental

## Qué se manipula y qué se mantiene fijo

El experimento central manipula **una sola variable**: qué evidencia documental
está disponible en el corpus. Todo lo demás —los datos OBD-II, el modelo, las
semillas, la atribución, el prompt, el proveedor y sus parámetros— se mantiene
idéntico entre condiciones.

Esa restricción es lo que permite atribuir un cambio de comportamiento del agente
a la disponibilidad de evidencia y no a cualquier otra cosa.

## Condiciones

| Condición | Corpus | Comportamiento esperado |
|---|---|---|
| **FULL** | contiene la evidencia correcta | EXPLAIN, con cada afirmación trazada |
| **PARTIAL** | evidencia incompleta | ABSTAIN, salvo que el criterio admita una explicación limitada declarada como tal |
| **ABSENT** | la evidencia relevante ha sido retirada | ABSTAIN |
| **DISTRACTOR** | contiene evidencia parecida pero incorrecta | rechazo del distractor; ABSTAIN si no queda otra evidencia suficiente |

La condición DISTRACTOR es la más exigente. FULL y ABSENT prueban que el sistema
responde a la *presencia* de evidencia; DISTRACTOR prueba que responde a su
*pertinencia*. Un sistema que confunda similitud con soporte pasará las tres
primeras y fallará esta.

## Experimento central de defensa

El mismo caso real, dos veces.

**Condición 1.** OBD-II real → modelo → atribución → recuperación → la evidencia
resulta suficiente → EXPLAIN → explicación trazable hasta su origen.

**Condición 2.** Los mismos datos, el mismo modelo, la misma atribución. Se
retira del corpus la evidencia relevante → la recuperación no la encuentra → la
evidencia resulta insuficiente → ABSTAIN.

El contraste debe verse sin necesidad de explicarlo. Es la escenificación directa
de la pregunta de investigación.

## Casos de referencia

Cada caso lleva anotado, antes de ejecutar nada:

```
case_id
expected_diagnosis
relevant_signals
relevant_windows
relevant_documents
relevant_chunks
allowed_claims
minimum_evidence
expected_action          # EXPLAIN | ABSTAIN
```

`allowed_claims` delimita qué se puede afirmar legítimamente con la evidencia
disponible. Una afirmación fuera de esa lista es una afirmación sin soporte,
aunque resulte ser cierta.

## Particiones

Entrenamiento, validación y test, separados por vehículo, trayecto, sesión,
episodio o evento según lo que los datos permitan. Nunca por partición aleatoria
de ventanas consecutivas: dos ventanas contiguas comparten casi toda su
información, y repartirlas entre entrenamiento y test convierte la evaluación en
un espejo.

El conjunto de test permanece **cerrado** hasta E19. Los umbrales del criterio de
suficiencia se calibran únicamente con validación. Un umbral ajustado mirando el
test dejaría de ser una predicción y pasaría a ser una descripción.

## Ablaciones

Cada ablación cambia exactamente un factor: sin atribución, sin recuperación
densa, sin criterio de suficiencia, con un único umbral en lugar del criterio
compuesto. Sirven para saber qué parte del resultado aporta cada pieza.

## Reproducibilidad

Toda ejecución registra `experiment_id`, commit, versión del dataset, versión del
corpus, versión del modelo, modelo de embeddings, proveedor y modelo de lenguaje,
versión del prompt, semilla, parámetros y métricas. Se guarda en JSON y CSV.

## Criterios de refutación

Se fijan **antes** de la evaluación final, en
[`../matriz_validacion_pi.md`](../matriz_validacion_pi.md). La respuesta a la
pregunta de investigación admite tres valores: sostenida, parcialmente sostenida
y no sostenida.

Un experimento que solo pueda dar resultado positivo no es un experimento. En
particular, los siguientes desenlaces son posibles y se reportarían como tales:

- el agente explica con la misma soltura cuando la evidencia está y cuando no;
- el agente se abstiene casi siempre, y la abstención resulta trivial;
- el agente acepta distractores como soporte;
- las referencias existen pero no sostienen lo que se afirma con ellas.
