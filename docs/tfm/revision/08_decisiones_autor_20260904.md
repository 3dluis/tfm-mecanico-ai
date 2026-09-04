# Decisiones del autor tras las cinco auditorías del 4 de septiembre de 2026

**Origen:** auditorías `EVIDENCE-VERIFICATION-20260904`, `EXPERIMENT-AUDIT-20260904-NX`,
`STATISTICAL-REVIEW-20260904-NX`, `RAG-EVALUATION-20260904-NX`, `TUTOR-REPORT-20260904-NX`.
**Estado del ciclo:** la iteración **no está cerrada**. Diseño experimental, RAG y estadística
quedaron en `FAIL`, y no se pasa al grupo 3 hasta que dejen de estarlo.

Ninguna cifra publicada resultó falsa en las cinco auditorías. Lo que falla es la unidad de
análisis, el alcance y la propagación.

| # | Decisión | Estado |
|---|---|---|
| 1 | Clasificador canónico: el que el experimento usa, sin recalibrar. **12 errores fallo → normal, 0 sustituciones** | adoptada |
| 2 | El resultado central se expresa sobre la unidad experimental independiente. 15/17 pasa a **recuento descriptivo** | adoptada; la unidad primaria la fija el revisor estadístico |
| 3 | Línea base `ALWAYS_ABSTAIN` **obligatoria** junto al sistema, más una complementaria del extremo opuesto | adoptada y medida |
| 4 | La condición de distractor actual **no es una condición independiente**. Se conserva etiquetada y se rediseña o se elimina | adoptada |
| 5 | `P-02 = CLOSED_WITH_SCOPE`, con alcance **por experimento** | adoptada |
| 6 | No reejecutar el escenario adverso hasta cerrar los canales de información | adoptada |
| 7 | v2.2: primero pruebas, después medición | adoptada |
| 8 | Filtro de motor: problema separado, con política de aplicabilidad explícita **auditada antes de implementarse** | adoptada |
| 9 | La afirmación más sólida sigue siendo el reconocimiento de insuficiencia **por ausencia** de evidencia, sin sobregeneralizar | adoptada |
| 10 | La memoria **no** se reescribe todavía: solo se registra el impacto | adoptada |

## Criterio del autor sobre la unidad de análisis

> Para inferencia estadística se usa la unidad que corresponde al **origen independiente de la
> observación**, no al número de transformaciones que hacemos sobre ella. Si varias condiciones
> reutilizan la misma ventana, no se convierten en observaciones independientes por cambiar el
> corpus.

Los recuentos de 17 decisiones y de 14 configuraciones no duplicadas se conservan como
**descriptivos**. La unidad primaria de inferencia la fija y la justifica el revisor
estadístico.

## Gate del valor p propuesto

La prueba de permutación con `p = 0,008` **no entra en la memoria** hasta que el revisor
estadístico confirme, por escrito: qué se permuta, cuál es la unidad de permutación, cuál es la
hipótesis nula, que no hay pseudorreplicación, y que el cálculo es reproducible desde
artefactos congelados.

## Impacto documental registrado, sin aplicar todavía

| Elemento | Cambio |
|---|---|
| 15/17 | pasa a recuento descriptivo de decisiones |
| Línea base `ALWAYS_ABSTAIN` | obligatoria junto a cualquier cifra del experimento central |
| Condición de distractor actual | deja de ser condición independiente |
| `P-02` | `CLOSED_WITH_SCOPE`, con estado por experimento |
| `P-03` | exige unidad estadística explícita |
| `P-08` | limitado a error por omisión |
| «el filtro de motor funciona» | **`REFUTED`** |
| Cifra 0,579 | se retira y se corrige a 12 errores, 0 sustituciones |
