# Política de suficiencia y abstención

## Dónde vive la decisión

En un componente determinista, **fuera del modelo de lenguaje**.

El modelo de lenguaje no decide si hay evidencia suficiente. Recibe la decisión
ya tomada y redacta en consecuencia. Si la decisión fuera suya, la respuesta a la
pregunta de investigación dependería de su disposición a admitir que no sabe
algo, que es precisamente lo que no se puede dar por supuesto.

## Señales del criterio

| Señal | Qué aporta |
|---|---|
| Confianza del modelo | cuán segura es la predicción diagnóstica |
| Calibración | si esa confianza significa algo |
| Puntuación de recuperación | cuán próximos son los fragmentos a la consulta |
| Relevancia documental | si los fragmentos tratan realmente del caso |
| Número de fragmentos de apoyo | cuánto respaldo hay |
| Número de fuentes distintas | si el respaldo es independiente o una sola voz repetida |
| Cobertura de afirmaciones | qué proporción de lo afirmado está sostenido |
| Contradicciones | si la evidencia se opone a sí misma |

Ninguna basta por separado. Una confianza alta con recuperación vacía no sostiene
nada. Cinco fragmentos de un mismo documento no son cinco apoyos independientes.

## Forma del criterio

```
confidence      >= t1
AND retrieval_support >= t2
AND coverage    >= t3
AND contradiction == false
```

Conjunción, no promedio ponderado: un promedio permite que un valor alto compense
uno inaceptablemente bajo, y aquí ningún factor es compensable. Sin cobertura de
afirmaciones no hay explicación que sostener, por muy confiado que esté el modelo.

Resultado: `SUPPORTED` o `INSUFFICIENT_EVIDENCE`.

## Calibración de umbrales

Los umbrales `t1`, `t2` y `t3` se calibran **exclusivamente sobre validación**.
El conjunto de test permanece cerrado hasta la evaluación final.

Los valores elegidos, y el procedimiento que llevó a ellos, se registran junto a
los resultados. Un umbral sin justificación registrada es un grado de libertad
oculto.

## La abstención como salida válida

La abstención **no es un fallo**. Es la respuesta correcta cuando la evidencia
disponible no sostiene una explicación.

```json
{
  "decision": "ABSTAIN",
  "reason": "INSUFFICIENT_EVIDENCE"
}
```

En lenguaje natural: *no existe evidencia suficiente para sostener una
explicación diagnóstica*.

Un sistema que nunca se abstiene no es un sistema más capaz: es un sistema que ha
dejado de distinguir entre lo que puede sostener y lo que no.

## Evaluación

| | Verdad: sostenible | Verdad: no sostenible |
|---|---|---|
| **EXPLAIN** | verdadero positivo | falso positivo — explicación sin fundamento |
| **ABSTAIN** | falso negativo — abstención injustificada | verdadero negativo — abstención correcta |

El **falso positivo** es el error grave: el sistema afirma algo que la evidencia
no sostiene. Es el fallo que la pregunta de investigación interroga.

El **falso negativo** es un error de utilidad: el sistema podía explicar y no lo
hizo. Molesta, pero no engaña.

Ambos se reportan. Y ambos deben reportarse junto a la **cobertura**: la
proporción de casos en que el sistema explica. Sin ella, la corrección es
manipulable —un sistema que se abstiene siempre no comete ni un solo falso
positivo, y no sirve para nada.
