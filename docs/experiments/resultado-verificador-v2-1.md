# Resultado del verificador v2.1 y comparación de las tres versiones

**Fecha:** 4 de septiembre de 2026 · **Commit de ejecución:** `a34bab2`, árbol limpio ·
**Política:** `docs/methodology/politica-suficiencia-v2-1.md`, escrita y registrada **antes**
de implementar y de medir · **Artefacto:** `experiments/E15_suficiencia_verifier_v2_1.json`.

Los tres resultados se conservan. Ninguno sustituye a otro: son tres mediciones del mismo
experimento con tres versiones del instrumento, y la secuencia completa es parte del
resultado.

## 1. Lo que cambió entre versiones, y solo eso

| | v1 → v2 | v2 → v2.1 |
|---|---|---|
| Qué cambia | qué cuenta como soporte: se añade el papel del fragmento | la **granularidad** con que se decide el papel: fragmento → sección |
| Conjunto de datos, casos, corpus, embeddings, modelo, calibración, umbrales, filtro de motor | sin tocar | sin tocar |
| Umbral de confianza | 0,79 | 0,79 |

## 2. Comparación caso a caso

`OK` = la decisión coincide con la anotada; `!!` = no coincide.

| Caso | Esperado | v1 | v2 | v2.1 |
|---|---|---|---|---|
| C01 deriva del caudalímetro | EXPLICA | ABSTIENE !! | ABSTIENE !! | ABSTIENE !! |
| C02 termostato bloqueado | EXPLICA | EXPLICA OK | EXPLICA OK | EXPLICA OK |
| C03 sonda lenta | EXPLICA | EXPLICA OK | EXPLICA OK | EXPLICA OK |
| C04 fallo de encendido | EXPLICA | ABSTIENE !! | ABSTIENE !! | ABSTIENE !! |
| C05 fuga de vacío | EXPLICA | EXPLICA OK | **ABSTIENE !!** | **EXPLICA OK** |
| C06 fuga, evidencia retirada | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C07 fuga, evidencia parcial | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C08 fuga, distractor | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C09 fuga, distractor sin filtro | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C10 termostato, retirada | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C11 termostato, parcial | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |
| C12 termostato, distractor | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |
| C13 termostato, distractor sin filtro | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |
| C14 sonda, retirada | ABSTIENE | ABSTIENE OK | ABSTIENE OK | ABSTIENE OK |
| C15 sonda, parcial | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |
| C16 sonda, distractor | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |
| C17 sonda, distractor sin filtro | ABSTIENE | **EXPLICA !!** | ABSTIENE OK | ABSTIENE OK |

## 3. Las cinco magnitudes acordadas

La comparación **no se juzga por la exactitud agregada**, porque una política que abstiene
siempre la mejora en unas dimensiones a costa de vaciar el sistema de utilidad.

| Magnitud | v1 | v2 | v2.1 |
|---|---|---|---|
| Decisiones correctas | 9/17 | 14/17 | **15/17** |
| Cobertura de explicación, casos con evidencia completa | 3/5 | 2/5 | **3/5** |
| Abstenciones correctas | 6 | 12 | 12 |
| Abstenciones falsas | 2 | 3 | **2** |
| Explicaciones sin soporte suficiente | 6 | 0 | **0** |

Por condición, v2.1: evidencia completa 3/5 · retirada 3/3 · parcial 3/3 · distractor 3/3 ·
distractor sin filtro 3/3.

## 4. Lectura

**La predicción declarada antes de ejecutar se cumplió exactamente.** C05 vuelve a explicar y
los seis casos que v2 corrigió siguen absteniéndose. No aparece ninguna regresión nueva. Las
abstenciones falsas vuelven a dos y las explicaciones sin soporte siguen en cero, que es la
única combinación de las tres versiones en que ninguna de las dos magnitudes empeora respecto
de las otras.

**Esto no prueba que la regla sea general.** Acertar la predicción dice que la corrección hace
lo que se propuso en siete casos conocidos, y la regla se diseñó sabiendo cuál fallaba. La
evidencia de generalidad la aportan las pruebas con códigos de frenos, dirección, red y
`airbag`, y con señales que no aparecen en ningún caso del banco, en
`tests/test_support_policy_v2_1.py`: la clasificación es idéntica sustituyendo el asunto del
texto, y no existe rama alguna que dependa de `P2187`, del ajuste de combustible, del
termostato ni de la sonda.

**Precio de la regla, declarado.** El encabezado manda sobre el texto. Si el manual titulase
una sección de tabla como procedimiento, v2.1 la clasificaría mal, y v2 no. Se acepta porque
la organización del documento es una decisión editorial estable y el troceado no lo es.

## 5. Los dos casos que siguen fallando no son del verificador

C01 y C04 se abstienen en las **tres** versiones, con la misma causa registrada: confianza
calibrada 0,600 y 0,462, por debajo del umbral 0,79. En C04 además la cobertura de
afirmaciones es 0,00. Son límites del modelo especializado y del corpus para esos dos fallos,
no de la política de suficiencia, y ninguna versión del verificador los toca.

La abstención en esos dos casos es, de hecho, **el comportamiento que el sistema promete**:
con confianza insuficiente no se explica. Están anotados como EXPLICA porque el fallo es el
correcto y la evidencia está disponible; el sistema no llega a esa confianza y calla. Se
reporta como límite de utilidad, no como acierto.

## 6. Qué se puede afirmar ahora

**Se sostiene**, sobre tres fallos y cuatro condiciones:

> Retirar del índice la evidencia relevante provoca la abstención del agente, y aportar
> evidencia presente pero no pertinente —parcial, distractora, o del motor incorrecto— también.
> Los datos, el modelo, la atribución y la confianza calibrada se mantienen constantes.

**Sigue sin sostenerse** que el sistema distinga presencia de pertinencia *en general*: se ha
comprobado en tres fallos de un vehículo, con un corpus, y con un instrumento corregido dos
veces después de observar sus fallos. La secuencia v1 → v2 → v2.1 se publica entera por eso.
