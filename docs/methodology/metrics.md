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

### Clasificación: qué es medida y qué es invariante del diseño

Una métrica que no puede tomar más de un valor no informa de nada. Distinguirlas
es obligatorio, y en este grupo hay de las dos clases.

| Métrica | Clase | Motivo |
|---|---|---|
| `claim support rate` por condición de corpus | **medida** | Toma valores distintos entre condiciones: 1,00 con evidencia completa y 0,00 con evidencia parcial o con distractor, teniendo cuatro documentos aplicables delante |
| `citation correctness` | **medida** | La barrera de citas se comprueba fuera del generador y puede fallar |
| Profundidad de traza | **medida** | Depende de qué conserve cada fragmento |
| **Distancia entre `citation completeness` y `claim support rate`** | **`INVARIANT`** | **Es cero por construcción.** El ensamblador da cita a una afirmación solo si la comprobación de soporte la acepta, y la marca sostenida si y solo si tiene cita. La diferencia no puede ser distinta de cero mientras las afirmaciones las construya el verificador |

**Consecuencia.** La distancia **no es un resultado del experimento** y no se
reporta como tal. Es una **comprobación de implementación**: si alguna vez dejara
de ser cero, habría un defecto en el ensamblador. Se conserva con esa función y
con ese nombre.

La distancia recuperaría su valor informativo si las citas las generara el modelo
de lenguaje en lugar del verificador. Ese brazo no está implementado y se declara
como trabajo pendiente, no como medición hecha.

Todas se calculan de forma determinista, sin juez.

## M5 — Abstención

Abstención correcta, abstención injustificada, tasa de explicación sin
fundamento, y la matriz completa de
[`abstention-policy.md`](abstention-policy.md).

Siempre acompañadas de **cobertura**. Corrección y cobertura solo significan algo
juntas.

**Comprobación de implementación, no resultado.** El «cero documentos aplicables»
de la condición sin evidencia está garantizado por construcción: la condición
retira del índice los mismos códigos con que la búsqueda va acotada. Sirve como
`SANITY_CHECK` de que la exclusión funciona, y así se reporta. Lo que **sí** es
resultado es la condición con evidencia parcial y la de distractor, donde hay
cuatro documentos aplicables delante y la cobertura de soporte es 0,00: ahí el
sistema responde a la pertinencia y no a la presencia, y podría no hacerlo.

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
