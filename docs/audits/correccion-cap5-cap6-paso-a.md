# Paso A · Propuesta de corrección de las seis afirmaciones no respaldadas

**Fecha:** 13 de octubre de 2026 · **Qué es:** la propuesta que el encargo pide **antes** de tocar
los capítulos, con las cinco columnas exigidas: afirmación original, evidencia disponible, motivo de
invalidez, redacción corregida e impacto sobre las conclusiones · **Procede de:**
[`matriz-impacto-cap5-cap6.md`](matriz-impacto-cap5-cap6.md), entradas `F-1` a `F-6` ·
**Prioridad:** `F-1` y `F-2`, las dos que están en el primer párrafo de su capítulo

**Cómo se aplica (Paso B).** La corrección **no borra** el texto anterior: cada una entra como una
nota fechada que cita lo que el capítulo decía, de modo que la evolución experimental quede visible.
Es la misma convención con que se corrigió el «9/9» del respeto al veredicto en septiembre: *la
cifra antigua se cita en la nota, no se borra*.

---

## F-1 · «el conjunto de prueba permanece cerrado y no se ha consultado» — **PRIORITARIA**

| | |
|---|---|
| **Dónde** | `cap5_resultados.md`, párrafo 2 (el segundo del capítulo) |
| **Afirmación original** | «Las cifras proceden de la partición de **validación** de la muestra sintética descrita en el capítulo 4; **el conjunto de prueba permanece cerrado y no se ha consultado**.» |
| **Evidencia disponible** | `docs/methodology/registro-aperturas-test.md`: cinco aperturas registradas, con su fecha, su motivo y su nivel de exposición. El cierre técnico en `src/mecanico_ia_exp/data/dataset.py:77` exige `allow_test=True` y una razón escrita, y las cinco veces se pasó |
| **Motivo de invalidez** | **falsa.** El conjunto se abrió cinco veces: tres intentos de E19, la comprobación pre-registrada P3 y una accidental. En cuatro de las cinco hubo exposición de etiquetas y de predicciones |
| **Redacción corregida** | «Las cifras de este capítulo proceden de la partición de **validación** de la muestra sintética descrita en el capítulo 4. El conjunto de prueba **se abrió cinco veces** y las mediciones que produjo se presentan aparte: tres intentos de la evaluación final, de los que el tercero es la medición publicada; una comprobación pre-registrada de las ablaciones; y una apertura accidental que solo leyó identificadores de sesión. En cuatro de las cinco hubo exposición de etiquetas y de predicciones. El registro completo, con los cinco niveles de exposición que se distinguen, está en el capítulo 4 y en `docs/methodology/registro-aperturas-test.md`. Lo que sí se sostiene, y se comprueba con un comando, es que **el instrumento no cambió entre la primera apertura y la medición**: umbrales, casos elegibles, reglas de selección, política y código son los mismos.» |
| **Impacto sobre las conclusiones** | **ninguno sobre las cifras de validación**, que son las del capítulo. Sí sobre lo que el capítulo promete: deja de decir que la prueba está intacta y remite al registro. Y obliga a `F-6`, porque no se puede decir que la prueba se abrió sin decir qué midió |

---

## F-2 · «la evaluación final sobre el conjunto de prueba, que sigue cerrado» — **PRIORITARIA**

| | |
|---|---|
| **Dónde** | `cap6_conclusiones.md`, párrafo 1 (el primero del capítulo) |
| **Afirmación original** | «…separan lo que los resultados parciales ya permiten observar de lo que requiere la evaluación final sobre el conjunto de prueba, **que sigue cerrado**. Ninguna cifra de este capítulo procede de ese conjunto.» |
| **Evidencia disponible** | la misma de `F-1`, más `experiments/E19_evaluacion_final_v3.json` |
| **Motivo de invalidez** | **falsa** en su primera mitad. La segunda —«ninguna cifra de este capítulo procede de ese conjunto»— **sigue siendo cierta** del texto actual, y deja de serlo en cuanto se incorpore E19 |
| **Redacción corregida** | «…separan lo que los resultados sobre validación permiten observar de lo que añade la evaluación final sobre el conjunto de prueba, **ejecutada el 12 de octubre de 2026 en el tercero de tres intentos**. El conjunto de prueba **no sigue cerrado**: se abrió cinco veces, y el registro de aperturas acompaña a sus cifras.» |
| **Impacto sobre las conclusiones** | el capítulo deja de ser «una entrega intermedia» en lo relativo a la prueba. Las conclusiones por objetivo **no cambian de sentido**; cambia que dejan de remitir a una medición pendiente para remitir a una hecha |

---

## F-3 · «el conjunto de prueba está cerrado por construcción» (OE2)

| | |
|---|---|
| **Dónde** | `cap6_conclusiones.md`, OE2 |
| **Afirmación original** | «El generador es determinista, los conjuntos se reparten por sesión, **el conjunto de prueba está cerrado por construcción**, el corpus conserva su huella y el registro de la línea base de diagnóstico se reprodujo bit a bit.» |
| **Evidencia disponible** | `dataset.py:77`, el registro de aperturas y `configs/datos_no_reconstruibles.json` |
| **Motivo de invalidez** | **confunde dos cosas.** El **cierre técnico** sí es por construcción y sigue vigente: el programa falla sin `allow_test=True` y sin razón escrita. Que el conjunto **esté** cerrado es otra afirmación, y es falsa |
| **Redacción corregida** | «El generador es determinista, los conjuntos se reparten por sesión, **el conjunto de prueba está cerrado en el código —pedirlo exige una autorización explícita y una razón por escrito, que queda registrada— y se abrió cinco veces bajo esa condición**, el corpus conserva su huella y el registro de la línea base de diagnóstico se reprodujo bit a bit. Dos límites de la reproducibilidad que este objetivo declaraba de forma incompleta: `synthetic_v3`, del que salen E6, E7 y la evaluación final, **no es reconstruible** con el generador publicado porque es anterior a su calibración; y cuatro pruebas y seis comprobaciones de tipado dependían de dos paquetes que se importaban sin estar declarados, lo que solo se vio al validar el procedimiento desde un clon limpio.» |
| **Enmienda del 13-10-2026** | esta redacción corregida contenía a su vez un error, detectado el mismo día al verificar la procedencia de las figuras: decía «`synthetic_v3`, **del que salen E6, E7 y la evaluación final**». Las tres ejecuciones publicadas declaran `synthetic_v2`. La enmienda está en `propuesta-figuras-cap5-cap6.md` (`F-7`) y aplicada en el capítulo. Se conserva aquí la redacción original de la propuesta, que es lo que se aprobó entonces |
| **Impacto sobre las conclusiones** | OE2 pasa de «cumplido parcialmente» con una lista de logros a «cumplido parcialmente» con sus dos límites nombrados. **La calificación no cambia**; cambia que el lector sabe dónde falla |

---

## F-4 · la causa atribuida al fallo de la condición con distractor

| | |
|---|---|
| **Dónde** | `cap5_resultados.md`, §PI.3 y PI.4, párrafo de los distractores (línea 139), y la nota de la Tabla 5.5 (línea 115) |
| **Afirmación original** | «Con el filtro activo, la condición con distractor recuperó en el termostato y en la sonda **exactamente los mismos fragmentos** que la condición parcial… **En ninguno de los tres fallos, por tanto, la condición con distractor y filtro añade un distractor que la parcial no tuviera.**» Y la nota: «Las filas de la condición con distractor y filtro de motor se cuentan aparte, **porque el diagnóstico de esa condición… las deja como diagnóstico y no como condición puntuable**» |
| **Evidencia disponible** | `docs/methodology/protocolo-distractor-v2.md` §1: medido que `C11` y `C12` excluyen **el mismo fichero** y que `C15` y `C16` también. El único campo que difería, `distractor_files`, **no lo lee el recorrido de suficiencia**: solo lo usa E12 como etiqueta para puntuar la recuperación |
| **Motivo de invalidez** | **la conclusión es correcta y la causa es falsa.** El texto atribuye el fallo al filtro de motor, que bloquearía el procedimiento del otro motor antes de ordenarlo. La causa medida es más simple y peor: **las dos condiciones tenían la misma configuración**, de modo que no había nada que bloquear |
| **Redacción corregida** | «Con el filtro activo, la condición con distractor recuperó en el termostato y en la sonda exactamente los mismos fragmentos que la condición parcial. La causa, comprobada en octubre de 2026, **no es el filtro de motor**: `C12` y `C16` tenían **la misma configuración** que `C11` y `C15` —el único campo que difería, el fichero distractor declarado, no lo lee el recorrido de suficiencia, que construye la condición por exclusión de fragmentos del índice—. Esas dos condiciones nunca fueron distintas de la parcial, y no porque un filtro bloqueara algo, sino porque no había nada que bloquear. En la fuga de vacío la condición sí difería, en dos fragmentos. La invalidación de la condición sigue siendo correcta; su diagnóstico anterior, que culpaba al filtro, queda corregido.» |
| **Impacto sobre las conclusiones** | **ninguno sobre la invalidación**, que se mantiene. Cambia la causa, y eso importa porque la causa es la que dicta el rediseño: buscar distractores de otro motor era inútil, y los que sirven son del motor correcto con el código correcto y **alcance equivocado** |

---

## F-5 · «PI.4 seguirá sin poder interpretarse»

| | |
|---|---|
| **Dónde** | `cap6_conclusiones.md`, objetivo general (línea 21) y OE5 (línea 15) |
| **Afirmación original** | «**El rediseño de la condición con distractor no forma parte de esa evaluación final y queda como trabajo posterior: mientras no se haga, PI.4 seguirá sin poder interpretarse**, y la respuesta global seguirá siendo parcial por ese motivo…» Y en OE5: «…**necesita un rediseño antes de sostener sobre ella una inferencia**» |
| **Evidencia disponible** | `docs/experiments/P1_distractor_v2.md`; `experiments/E15_suficiencia_distractor_v2.json`; la comprobación previa de alcanzabilidad en `scripts/comprobar_distractor_v2.py` |
| **Motivo de invalidez** | **falsa desde el 13 de octubre de 2026.** El rediseño se hizo y se ejecutó: seis casos, seis abstenciones, las seis por insuficiencia de la evidencia y **ninguna** por baja confianza del modelo |
| **Redacción corregida** | «El rediseño de la condición con distractor no formaba parte de la evaluación final y **se ejecutó aparte, el 13 de octubre de 2026**, con los cuatro requisitos de alcanzabilidad comprobados antes de observar ningún veredicto. En los tres casos construidos el sistema se abstuvo, y el motivo registrado fue la insuficiencia de la evidencia y no la falta de confianza en el diagnóstico: las confianzas, entre 0,908 y 1,000, estaban por encima del umbral. El distractor llegó al verificador clasificado como **plenamente aplicable** —del motor correcto y con el código del fallo—, de modo que ni el filtro de motor ni el validador de aplicabilidad intervinieron: lo que rechazó la evidencia fue la comprobación de que el fragmento hablara de la señal observada. Con tres situaciones construidas, el resultado **describe esas tres y no estima ninguna tasa**; PI.4 pasa de no tener respuesta interpretable a tener una medición acotada a sus casos.» |
| **Impacto sobre las conclusiones** | PI.4 deja de ser el motivo por el que la respuesta global es parcial. **La calificación de «parcialmente sostenida» no cambia**: P1 la refuerza en PI.4 y `L-26` la debilita en PI.2, y no hay razón para moverla en ninguna dirección |

---

## F-6 · «la evaluación final… queda pendiente»

| | |
|---|---|
| **Dónde** | `cap5_resultados.md`, párrafo 2, y `cap6_conclusiones.md`, párrafo 1 |
| **Afirmación original** | «Son resultados parciales: **la evaluación final sobre el conjunto de prueba y la demostración integrada quedan pendientes**.» |
| **Evidencia disponible** | `experiments/E19_evaluacion_final_v3.json`, ejecutada el 12-10-2026 bajo las reglas congeladas; `docs/experiments/` con su informe: falsa confianza **0 de 14**, abstención innecesaria **2 de 8** |
| **Motivo de invalidez** | **falsa.** La evaluación final se ejecutó. La **demostración integrada** sigue pendiente, y eso hay que conservarlo |
| **Redacción corregida** | «Los resultados de este capítulo son los de validación. **La evaluación final sobre el conjunto de prueba se ejecutó el 12 de octubre de 2026**, en el tercero de tres intentos, y sus cifras se presentan en su propio apartado: falsa confianza 0 de 14 ejecuciones y abstención innecesaria 2 de 8, sobre un conjunto anotado sellado antes de abrir la partición. Con catorce y ocho ejecuciones en los denominadores, el intervalo de incertidumbre es amplio y no se publica. **La demostración integrada sigue pendiente.**» |
| **Impacto sobre las conclusiones** | obliga a incorporar E19 al capítulo 5 (entrada `N-1` de la matriz), que es la tarea más grande que queda. **Mientras no se incorpore, la corrección de `F-6` se limita a decir que la evaluación existe y dónde está su informe**, sin trasladar sus cifras al capítulo: trasladarlas es escribir el apartado, no corregir una frase |

---

## Resumen de lo que cambia y lo que no

| | |
|---|---|
| **Cifras modificadas** | **ninguna.** Las tablas 5.1 a 5.8 quedan intactas |
| **Conclusiones por objetivo que cambian de sentido** | **ninguna.** OE1 a OE5 conservan su calificación |
| **Calificación de la pregunta** | **sin cambios**: parcialmente sostenida |
| **Texto que se borra** | **ninguno.** Cada corrección cita lo que el capítulo decía |
| **Lo que queda pendiente tras el Paso B** | el apartado de E19 en el capítulo 5 (`N-1`), y las diez entradas `A-1` a `A-10` de la matriz, que son matices y no falsedades |

## Orden de aplicación del Paso B

1. `F-1` y `F-2`, por estar en los primeros párrafos.
2. `F-6`, que `F-1` y `F-2` obligan a tocar.
3. `F-3`.
4. `F-4` y `F-5`, el bloque del distractor.
