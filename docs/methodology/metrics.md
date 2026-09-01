# Métricas

Seis grupos. No todas las métricas de cada grupo se calculan siempre: se reporta
la que corresponde al problema, y se dice cuál se ha usado.

## M1 — Diagnóstico

Rendimiento del modelo especializado sobre test aislado: exactitud, precisión,
exhaustividad, F1, PR-AUC, ROC-AUC y **calibración**.

La calibración no es opcional aquí: la confianza del modelo alimenta el criterio
de suficiencia. Una confianza sin calibrar hace que ese criterio decida sobre un
número que no significa lo que aparenta.

Con clases desbalanceadas, PR-AUC informa más que ROC-AUC.

## M2 — Recuperación

Precision@K, Recall@K, MRR, tasa de acierto y nDCG, sobre un conjunto de
referencia anotado.

Se reportan **por condición de corpus**, no solo en agregado: el agregado
promedia condiciones que fueron diseñadas para diferir, y oculta lo único que se
quería observar.

## M3 — Explicación

Calidad de la explicación producida: adecuación al esquema, tasa de salidas
válidas y legibilidad.

Aquí, y solo aquí, cabe un juez basado en modelo de lenguaje —como apoyo, nunca
como instrumento único. Cuando se use se registran proveedor, modelo, prompt,
temperatura y versión, y su veredicto se contrasta con anotación manual sobre una
submuestra.

## M4 — Trazabilidad

| Métrica | Qué mide |
|---|---|
| `citation correctness` | proporción de referencias que existen y resuelven |
| `citation completeness` | proporción de afirmaciones que llevan referencia |
| `claim support rate` | proporción de afirmaciones cuya referencia **sostiene** lo afirmado |
| `unsupported claim rate` | complemento de la anterior |
| profundidad de traza | cuántos eslabones de la cadena se reconstruyen |

La distancia entre `citation completeness` y `claim support rate` es informativa
por sí misma: mide cuántas afirmaciones vienen acompañadas de una referencia que
no las respalda. Es el fallo más difícil de detectar a simple vista, porque el
texto resultante parece impecable.

Todas se calculan de forma determinista, sin juez.

## M5 — Abstención

Abstención correcta, abstención injustificada, tasa de explicación sin
fundamento, y la matriz completa de
[`abstention-policy.md`](abstention-policy.md).

Siempre acompañadas de **cobertura**. Corrección y cobertura solo significan algo
juntas.

## M6 — Rendimiento

Latencia por etapa, latencia extremo a extremo, tamaño del modelo y coste de la
recuperación. Se registra el dispositivo real de cada etapa: MPS y CPU no son
intercambiables y no se reportan como si lo fueran.

## Métricas de atención prioritaria

De todo lo anterior, lo que responde directamente a la pregunta de investigación:

- `unsupported claim rate`
- `citation correctness`
- `citation completeness`
- `claim support rate`
- `correct abstention`
- `false abstention`
- `unsupported explanation rate`

## Salida

`results/summary.json`, `results/summary.csv`,
`results/metrics_by_experiment.csv`, `results/claims.csv`,
`results/evidence_trace.csv`, `results/abstention.csv`,
`results/retrieval.csv`, y la lectura en `results/RESULTADOS_TFM.md`.

Todo valor publicado procede de una ejecución registrada. Ninguno se estima, se
redondea de memoria ni se completa a mano.
