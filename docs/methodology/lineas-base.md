# Líneas base del experimento central

**Fecha:** 4 de septiembre de 2026 · **Motivadas por:** `STAT-MAJ-001` y `RAG-MAJ-034`, que
señalan por separado que el experimento se publicaba **sin línea base**.

Sin una línea base, una tasa de decisiones correctas no distingue al sistema de una política
trivial. Este documento fija cuáles se reportan y por qué, y **ninguna es decorativa**: las dos
que se incluyen acotan los dos extremos entre los que el sistema tiene que demostrar que hace
algo.

## 1. Las dos políticas triviales

| Política | Qué hace | Por qué está aquí |
|---|---|---|
| `ALWAYS_ABSTAIN` | se abstiene siempre, sin mirar nada | **Obligatoria.** Es la política que maximiza la prudencia y no explica nunca. Si el sistema no la supera, «abstenerse mucho» no es un resultado |
| `ALWAYS_EXPLAIN_WHEN_MODEL_CONFIDENT` | explica si la confianza calibrada alcanza el umbral de operación, se abstiene si no | Es el sistema **sin verificador de evidencia**: solo la calibración. Aísla cuánto aporta la vía documental sobre la puerta de confianza |

Se registra también `ALWAYS_EXPLAIN` como referencia del extremo contrario, aunque no informa
por sí sola.

## 2. Resultado, sobre los diecisiete casos anotados

Calculado desde `experiments/E15_suficiencia_verifier_v2_1.json` y
`configs/goldset_mazda3_bk.yaml`, con el umbral de operación 0,79.

| Política | Decisiones correctas | En las doce condiciones sin evidencia completa |
|---|---|---|
| `ALWAYS_EXPLAIN_WHEN_MODEL_CONFIDENT` | 3 / 17 | 0 / 12 |
| `ALWAYS_EXPLAIN` | 5 / 17 | 0 / 12 |
| **`ALWAYS_ABSTAIN`** | **12 / 17** | **12 / 12** |
| **Sistema, verificador v2.1** | **15 / 17** | **12 / 12** |

## 3. Lectura, que es lo que importa

**En las doce condiciones sin evidencia completa el sistema empata con el abstencionista
trivial: 12 de 12 los dos.** Ninguna de esas doce decisiones distingue al sistema de una
política que no mira nada.

**Toda la ventaja del sistema está en los cinco casos con evidencia completa**, donde explica
correctamente en tres y el abstencionista acierta cero. La diferencia entre 15 y 12 es
exactamente esa.

De ahí se sigue una consecuencia que hay que escribir en la memoria: **la afirmación defendible
no es que el sistema se abstenga bien, sino que se abstiene bien *y además* explica cuando debe
hacerlo**. La primera mitad la consigue cualquiera; la segunda es la que cuesta, y es donde el
sistema falla dos de cinco veces, ambas por confianza insuficiente del modelo especializado.

La política que explica cuando el modelo está seguro obtiene 3 de 17 y **cero** en las doce
condiciones adversas: la puerta de confianza por sí sola no sirve para abstenerse por falta de
evidencia. Eso sí es una contribución de la vía documental, y es medible.

## 4. Lo que estas líneas base no resuelven

No corrigen la pseudorreplicación: las cuatro filas se calculan sobre los mismos diecisiete
registros, que provienen de cinco ventanas. Una línea base mal expresada sigue estando mal
expresada. La unidad de inferencia la fija el revisor estadístico y estas cifras se reexpresarán
en ella.
