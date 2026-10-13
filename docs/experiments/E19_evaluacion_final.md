# E19 — Evaluación final sobre el conjunto de prueba

**Fecha:** 12 de octubre de 2026 · **Estado: cerrada, medida en el tercer intento.** · **Commit:**
`8ee2dd8` · **Política del verificador:** v2.2, que pasa a canónica con esta evaluación · **Reglas
congeladas:** `docs/methodology/congelacion-anotacion-e19.md`, ancladas en el commit `de6207f` ·
**Declaración de apertura:** `docs/methodology/declaracion-apertura-e19.md`, aprobada por el autor el
1 de octubre de 2026.

Este informe presenta lo medido, no lo deseable. El resultado primario está separado de los dos
análisis descriptivos, los errores se enumeran todos y las limitaciones van al final sin atenuar.

## 1. Estado final y los tres intentos

| Intento | Fecha | Hasta dónde llegó | Artefactos |
|---|---|---|---|
| `v1` | 2 de octubre, 02:31:30 UTC | abrió la partición, predijo, **selló su anotación**; el proceso murió después, sin mediciones | `E19_anotacion.json`, huella `57d0e3c33e9ef82f` |
| `v2` | 6 de octubre, 02:19:27 UTC | lo mismo; también interrumpido | `E19_anotacion_v2.json`, huella `70d5f6b7ca6de184` |
| **`v3`** | **12 de octubre, 21:38:21 → 21:50:19 UTC** | **completó las 35 ejecuciones y escribió el registro** | `E19_anotacion_v3.json` (`7964f97fcdc21160`), `E19_evaluacion_final_v3.json`, `artifacts/tables/E19_evaluacion_final_v3.csv` |

Los tres se conservan. Las anotaciones de `v1` y `v2` son **idénticas byte a byte salvo la cabecera**,
lo que acredita que el recorrido hasta el sellado es determinista. La incidencia de los dos primeros
intentos está documentada en `docs/experiments/incidencia-e19-01.md`.

## 2. Integridad de la ejecución

Las diez comprobaciones que la sección 3 del encargo exige, verificadas **antes** de interpretar:

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Congelación original | **PASS**, diez de diez comprobaciones dentro del registro |
| 2 | Identidad del código y de la configuración | ninguna línea de `src/`, `configs/`, `tests/`, `Makefile` ni `pyproject.toml` cambió entre la primera apertura (`5b64504`) y la medición (`8ee2dd8`). `git diff --stat 5b64504..8ee2dd8 -- src/ configs/ tests/` está **vacío** |
| 3 | Huellas de los conjuntos | las cuatro de `synthetic_v2` coinciden con las congeladas |
| 4 | Integridad de la anotación sellada | huella en disco `7964f97fcdc21160`, idéntica a la que el registro cita |
| 5 | Correspondencia anotación ↔ evaluación | los denominadores del registro son **idénticos** a los de la anotación en los tres estratos |
| 6 | Denominadores | **Declarados antes de abrir:** 22 ejecuciones, 10 ventanas y 10 sesiones en el estrato operativo, que es lo que la declaración fija; y como **cotas superiores** «hasta 11» en el comparativo y «hasta 5» en el adverso. Los tres se cumplen: 22/10/10, 11 y 2. **Fijados en la anotación sellada, después de abrir y antes de medir:** el reparto 8 deben explicar / 14 deben abstenerse, y los recuentos exactos de los dos estratos descriptivos. La declaración lo advertía: ese reparto depende de cuántas ventanas clasifique bien el modelo y no podía escribirse de antemano |
| 7 | Ejecuciones completadas | 35 de 35: 22 + 11 + 2 |
| 8 | Duplicados | ninguno; los 35 identificadores son únicos |
| 9 | Resultados parciales tratados como completos | ninguno; no existe artefacto de ejecución no completada para `v3` |
| 10 | Modificaciones posteriores a la apertura | solo documentación y artefactos: la incidencia, la sección de desenlace de la declaración, la auditoría de PI.1 y la anotación de `v1`. Ningún fichero congelado, ningún fichero de código |

Índice verificado: 6 158 fragmentos de 3 055 ficheros, 6 158 vectores en el espacio declarado, huella
de contenido `7ac722bdda12595d` y de vectores `ad0b27a17798d042`. Revisiones de los dos modelos de
inferencia, coincidentes con las congeladas.

**Lo que `dirty: true` significa aquí.** Los tres artefactos de salida estaban sin seguimiento cuando
se escribió el registro, y la cabecera lo refleja. **Ningún fichero con seguimiento estaba
modificado**, que es la condición que la declaración exige y que se comprobó con
`git status --porcelain --untracked-files=no`, vacío.

## 3. Registro del proceso

| | |
|---|---|
| Identificador de proceso | 636 |
| Proceso padre | `launchd`, mediante `launchctl submit -l tfm.e19.v3` |
| Inicio | 12 de octubre, ~21:33 UTC (lanzamiento); anotación sellada 21:38:21 |
| Final | 21:50:19 UTC, al escribir el registro |
| Código de salida | 0; el recorrido llegó a su última instrucción y escribió los tres artefactos |
| Señal de terminación | ninguna |
| Consumo máximo de memoria | **no muestreado en `v3`.** La reproducción equivalente sobre validación registró un máximo de 1,93 GB de memoria residente |
| Trabajo de control | vivo durante toda la ventana de medición, de 21:38:04 a 21:50:38, sesenta latidos de diez segundos |
| Último hito completado | el registro y la tabla, es decir todos |
| Integridad de los artefactos | comprobada; sección 2 |

**`launchd` relanzó el trabajo tres veces** al terminar, porque reinicia por omisión lo que se le
envía. Las tres reejecuciones fueron **rechazadas por el propio ejecutor** antes de escribir nada, con
`RepeticionSinIdentificadorError`: los destinos del intento `v3` ya estaban ocupados. Es la regla de la
sección 11 del documento de congelación funcionando sin intervención. Los trabajos se retiraron después.

**La causa raíz de las dos interrupciones no se declara resuelta.** Lo descartado con evidencia: no
hubo informe de caída, ni presión de memoria —el registro del sistema conserva la ventana y no
contiene un solo evento `jetsam`—, ni sueño ni apagado, y la reproducción del recorrido completo con
el redactor real sobre validación terminó con código 0. Lo observado: los dos intentos murieron pocos
minutos después de lanzarse, coincidiendo con el cierre de la sesión de trabajo, pese a ir
desacoplados con `setsid`; y el que corrió bajo `launchd`, con el sistema como padre, completó. Queda
como **hipótesis ambiental sobre el ciclo de vida del proceso**, no como causa demostrada. La
alternativa —una condición del recorrido completo todavía no identificada— no se puede descartar,
porque `v3` no se instrumentó con muestreo de memoria y porque el trabajo de control de esta ejecución
corrió en una sesión que permaneció viva.

## 4. Registro de accesos al conjunto de prueba

| Fecha | Intento | Motivo | Alcance | ¿Se observaron etiquetas o predicciones? | ¿Se observaron métricas? | ¿Influyó en decisiones posteriores? |
|---|---|---|---|---|---|---|
| 2-10-2026 | `v1` | evaluación final autorizada | apertura técnica, predicciones, anotación sellada | **Sí.** Etiquetas y clase predicha de las diez ventanas elegidas, incluidas las dos mal diagnosticadas | No. Ninguna métrica de suficiencia, trazabilidad o redacción llegó a calcularse | Ver más abajo |
| 6-10-2026 | `v2` | intento tras la interrupción | idéntico | **Sí**, la misma información; la anotación resultó idéntica a la de `v1` | No | No |
| 12-10-2026 | `v3` | intento tras la segunda interrupción | evaluación completa | Sí | **Sí**, todas | Es la medición |

**Qué se hizo con esa exposición, dicho sin rodeos.** La anotación de `v1` se publicó en el
repositorio, y su contenido —qué ventanas se eligieron, qué etiqueta tiene cada una y qué predijo el
bosque— se describió en el informe de la incidencia. Entre esa primera apertura y la medición de `v3`
**no cambió ni una línea de código, de configuración o de pruebas**, lo que es comprobable con un solo
comando y es la evidencia más fuerte de que la exposición no alteró el instrumento. Tampoco se tocó
ningún fichero congelado: umbrales, casos elegibles, reglas de selección, política y métricas
publicables son los mismos.

**Una excepción, y queda declarada.** En el borrador de la auditoría de PI.1 se citó una ventana de
prueba mal diagnosticada —`F03_thermostat_stuck__warmup__11@120s`, conocida por la anotación de
`v1`— como corroboración de una hipótesis construida sobre validación. La revisión del diff lo
señaló y **se retiró de la inferencia** antes de fusionar nada: el documento final la menciona
separada y declara expresamente que no la sostiene. No se derivó de ahí ninguna decisión
experimental.

**Qué sigue siendo cierto y qué no.** El conjunto de prueba se abrió tres veces y hubo exposición de
etiquetas y de predicciones en las dos primeras, sin mediciones. El instrumento no cambió entre
aperturas. Por tanto la evaluación conserva su carácter de medición sobre datos no usados para
ajustar nada; lo que **no** puede decirse es que el conjunto se abriera una sola vez. Esa
circunstancia es parte del informe y debe estar ante el tribunal, no omitirse.

## A. Resultado primario

**Estrato operativo**, el único que responde a la pregunta: 22 ejecuciones, once condiciones de
evidencia sobre las dos sesiones de prueba de cada fallo, diez ventanas de diez sesiones distintas,
sin solape.

Las dos métricas estaban preregistradas con su definición y su unidad de análisis. Sus
**denominadores, no**: dependen de cuántas ventanas clasifique bien el modelo sobre prueba, y la
declaración de apertura lo dejó escrito. Quedaron fijados en la anotación sellada, después de abrir y
**antes** de calcular una sola métrica, y el registro lo acredita con su huella.

| Métrica, preregistrada en su definición | Numerador | Denominador | Valor | Ventanas | Sesiones |
|---|---|---|---|---|---|
| **Falsa confianza** `T_FC` | 0 | 14 | **0,0000** | 7 | 7 |
| **Abstención innecesaria** `T_AI` | 2 | 8 | **0,2500** | 8 | 8 |
| Cobertura con evidencia completa | 6 | 10 | 0,6000 | 10 | 10 |

**Criterio de aceptación, y aquí hay que ser preciso.** La formulación original de PI.3 fijaba
umbrales numéricos para estas dos tasas, y esos umbrales **nunca llegaron a fijarse**: el capítulo 4
lo declara. El criterio vigente es por tanto **cualitativo** —la decisión cambia al retirar la
evidencia— más la comparación con las dos políticas triviales de referencia, que sí estaba
preregistrada. No hay un número contra el que contrastar las tasas, y no se va a inventar ahora.

**Cuatro cosas distintas, que no deben confundirse.** El **resultado observado** son las tres cifras
de la tabla anterior. La **comparación experimental** es la de las políticas triviales, que cumple sus
seis condiciones. La **interpretación** es el párrafo del final de esta sección, acotado a lo
observado. Y el **cumplimiento de un criterio preregistrado** no se puede declarar, porque el criterio
numérico no existía: no hay éxito formal de hipótesis que anunciar, y presentarlo como tal sería
atribuir al experimento una validación que su propio diseño no fijó.

**Frente al criterio cualitativo.** La decisión cambia: con evidencia completa y diagnóstico correcto el sistema
explica en 6 de 8 casos, y en las 14 ejecuciones en que la evidencia no sostiene la explicación se
abstiene en las 14. Contra las referencias:

| Política | `T_FC` | `T_AI` |
|---|---|---|
| Abstenerse siempre | 0,0000 | 1,0000 |
| **Explicar si el modelo confía** (≥ 0,79) | **1,0000** | 0,2500 |
| **Criterio compuesto** | **0,0000** | 0,2500 |

La puerta de confianza sola habría explicado **las catorce** ejecuciones que debían terminar en
abstención. El criterio compuesto no explica ninguna, con la misma abstención innecesaria. Es la
misma lección que las ablaciones de E18 dieron sobre validación, ahora sobre el conjunto reservado.

**Esta comparación se documenta como evidencia experimental, y no como análisis exploratorio, porque
las seis condiciones exigidas se cumplen y son comprobables en el registro:**

| | Condición | Comprobación |
|---|---|---|
| 1 | Las tres políticas usan exactamente las mismas ejecuciones | sí: la función de referencia recibe la lista de decisiones del estrato, no una muestra aparte |
| 2 | Los umbrales estaban definidos antes de observar resultados | sí: 0,79 vive en `configs/manifest_e19.json`, anclado en `de6207f`, y procede del barrido de E15b con su criterio escrito antes |
| 3 | Ninguna política se ajustó después | sí: las dos triviales se calculan en código a partir de ese umbral congelado; no hay parámetro ajustable |
| 4 | Denominadores equivalentes | sí: 14 y 8 en las tres, con 7 y 8 ventanas independientes en las tres |
| 5 | Las diferencias están respaldadas por registros individuales | sí: **las catorce** ejecuciones que debían abstenerse tienen confianza calibrada ≥ 0,79 —seis de ellas exactamente 1,0000—, de modo que la puerta de confianza las habría explicado una por una, no por agregación |
| 6 | No mezcla operativo con descriptivo | sí: el bloque de políticas de referencia existe **dentro de cada estrato** y se calcula con sus propias ejecuciones |

**Dónde se ve mejor.** Dos ejecuciones con evidencia completa en el índice y diagnóstico **incorrecto**
—el modelo dice «sin fallo» con confianza 0,9076 y 0,9660— terminan en abstención con cobertura de
afirmaciones 0,00. La confianza alta no bastó porque la evidencia documental no sostenía lo que el
modelo proponía. Esa es la afirmación central del trabajo, medida sobre datos que el sistema no había
visto.

**Interpretación, acotada a lo observado.** En las condiciones evaluadas, el mecanismo de decisión
evitó emitir explicaciones incorrectas en los casos observados, incluidos dos diagnósticos erróneos con
confianza elevada. **Este resultado no permite establecer que la tasa de falsa confianza sea nula fuera
del conjunto experimental.**

Lo que **no** puede decirse, y conviene escribirlo para no decirlo por descuido: que el sistema elimina
los diagnósticos incorrectos, ni que garantiza que nunca explicará una avería equivocada. Lo medido son
catorce ejecuciones procedentes de siete sesiones.

**Y el coste de esa protección se analiza junto al beneficio, no después.** Dos abstenciones
innecesarias de ocho ejecuciones que debían explicar, y cobertura de 6 de 10 ejecuciones con evidencia
completa: de cada diez situaciones en que el manual documentaba la avería y el sistema podía haber
respondido, respondió en seis. La seguridad diagnóstica de este criterio se paga en capacidad efectiva
de dar respuesta, y las dos cifras tienen que leerse juntas. Con ocho ejecuciones en el denominador de
`T_AI` y catorce en el de `T_FC` el intervalo de incertidumbre es amplio y no se calcula: un solo caso
movería `T_AI` en 0,125.

## B. Resultados descriptivos

**No redefinen el éxito del experimento y no se mezclan con lo anterior.**

**Estrato comparativo** —la ventana que la regla de validación habría elegido, es decir la primera que
el modelo clasifica bien—. Existe para separar el efecto de la partición del efecto de haber cambiado
la regla de selección. 11 ejecuciones, 5 ventanas, 5 sesiones.

| Métrica | Numerador/denominador | Valor | Ventanas | Sesiones |
|---|---|---|---|---|
| Falsa confianza | 0/6 | 0,0000 | 3 | 3 |
| Abstención innecesaria | 2/5 | 0,4000 | 5 | 5 |
| Cobertura con evidencia completa | 3/5 | 0,6000 | 5 | 5 |

**Estrato adverso** —ventanas que el modelo clasifica mal, con evidencia completa en el índice—. 2
ejecuciones, 2 ventanas, 2 sesiones; tres de los cinco casos quedan **no evaluables por ausencia de
ventanas**, porque el modelo no falla ninguna ventana de esas tres condiciones en prueba.

| Métrica | Numerador/denominador | Valor |
|---|---|---|
| Falsa confianza | 0/2 | 0,0000 |
| Abstención innecesaria | 0/0 | **no definida** |
| Cobertura con evidencia completa | 0/2 | 0,0000 |

Con dos ejecuciones este estrato no sostiene ninguna tasa. Lo que muestra es cualitativo: ante un
diagnóstico incorrecto, ninguna afirmación obtuvo soporte.

**Diagnóstico sobre las 98 ventanas de prueba.** Exactitud 0,8469 · F1 macro **0,8360** · F1 ponderado
0,8292 · exactitud equilibrada 0,8214, frente a 0,0741 de F1 macro de la clase mayoritaria, que es
`F00_normal` tanto en la partición como en entrenamiento. Por clase: fuga de vacío, deriva de
caudalímetro y sonda lenta en 1,0000; sin fallo 0,7887; termostato 0,7826; **fallo de encendido
0,4444**. Calibración: ECE 0,0972 sin calibrar y 0,0919 calibrado, con el sesgo pasando de −0,097 a
+0,034. Sobre prueba la calibración isotónica **apenas mejora** el error de calibración, a diferencia
de lo que ocurría en validación, donde bajaba de 0,144 a 0,085; lo que hace es cambiar el signo del
sesgo, de infraconfiado a ligeramente sobreconfiado.

## C. Análisis de errores

Las 35 ejecuciones, por categoría del protocolo.

| Categoría | Operativo | Comparativo | Adverso |
|---|---|---|---|
| Explicación correcta | 6 | 3 | 0 |
| Abstención correcta | 14 | 6 | 2 |
| **Explicación incorrecta** (falsa confianza) | **0** | **0** | **0** |
| **Abstención incorrecta** (innecesaria) | **2** | **2** | 0 |
| Diagnóstico cruzado entre fallos | **0** | **0** | **0** |
| Fallo de recuperación | **0** | **0** | **0** |
| Fallo de generación | **0** | **0** | **0** |
| Error de ejecución | **0** | **0** | **0** |

**Las dos abstenciones incorrectas del estrato primario, con su causa.** Las dos tienen evidencia
completa y diagnóstico correcto:

| Ejecución | Motivos registrados | Confianza | Fragmentos | Cobertura |
|---|---|---|---|---|
| `C01_maf_drift@F02_maf_drift__highway__05@120s` | confianza baja | 0,5731 | 6 | 1,00 |
| `C04_misfire@F05_misfire__highway__05@120s` | confianza baja **y** cobertura baja | 0,4905 | 4 | 0,00 |

En la primera la evidencia estaba y la abstención es solo del umbral de confianza; un umbral más bajo
la habría explicado. En la segunda concurren dos causas, y bajar el umbral no habría bastado: ninguno
de sus cuatro fragmentos aplicables sostiene una afirmación. Es el mismo par de causas que en
validación y vuelve a ser el fallo de encendido el caso difícil.

**Diagnósticos del modelo incorrectos: seis ejecuciones, sobre dos ventanas.**
`F03_thermostat_stuck__warmup__11@120s` y `F05_misfire__highway__01@120s`, las dos clasificadas como
«sin fallo». No son diagnósticos cruzados: el modelo no confunde un fallo con otro en ninguna de las
35 ejecuciones. **No se descartan ni se tratan aparte**: son las que hacen que ocho ejecuciones deban
explicar y catorce abstenerse, y las seis terminaron en abstención correcta. La ventana de termostato
fallada es, otra vez, del régimen de **calentamiento**, coherente con el límite físico de detección que
la auditoría de PI.1 dejó abierto.

**Ocho ejecuciones con cero fragmentos aplicables.** Las ocho son de la condición de **evidencia
ausente**, donde el índice se vacía a propósito: cero fragmentos es el comportamiento esperado y no un
fallo de recuperación. **Ninguna ejecución con evidencia completa se quedó sin fragmentos.**

Conviene no confundir las dos cosas en ninguna dirección. Una ausencia deliberada de evidencia no es un
fallo del recuperador; y **cero fallos de recuperación en treinta y cinco ejecuciones no prueba que el
recuperador funcione en cualquier escenario**. Lo medido es que, en este corpus, con estas once
condiciones de evidencia y estas consultas, el recuperador devolvió fragmentos aplicables siempre que
el índice los contenía. Nada más.

**Redacción.** 35 de 35 salidas válidas de esquema, 35 de 35 respetan el veredicto del verificador,
**cero citas fuera de lo entregado**, cero fallos de esquema.

**Trazabilidad de las afirmaciones.** En el estrato primario, 66 afirmaciones: 66 con observación, 21
con cita y 21 con soporte. Acotado a las ejecuciones con evidencia completa, 21 de 30 con soporte,
0,70. El soporte sigue siendo una propiedad del verificador y no una anotación independiente, de modo
que esta cifra describe su comportamiento y no acredita la verdad de lo afirmado.

## D. Trazabilidad

Cada cifra de este informe se sigue hasta su origen por esta cadena:

```
E19  →  sesión (session_id de synthetic_v2, partición test)
     →  ventana (session_id@t_start)
     →  ejecución (estrato:caso@ventana, 35 identificadores únicos)
     →  anotación sellada (E19_anotacion_v3.json, huella 7964f97fcdc21160,
                           escrita antes de la primera medición)
     →  configuración congelada (configs/manifest_e19.json, anclada en de6207f:
                           política v2.2, umbral 0,79, cobertura 0,80, semilla 20260901,
                           corpus 0.1.0, embeddings y adaptador por huella)
     →  evidencia (bundle y support_checks de cada caso, con chunk_id)
     →  resultado (experiments/E19_evaluacion_final_v3.json y, fila a fila,
                           artifacts/tables/E19_evaluacion_final_v3.csv, que se versiona
                           porque `tables/` no lo esta y el jurado tiene que poder leerla)
     →  interpretación (este informe)
```

**Un hueco que declaro.** La cabecera del registro trae `prompt_version: null`: el ejecutor de la
evaluación final no lo pasa al escribir la cabecera, aunque el bloque de redacción sí registra
`agent-2026-09-04`. El dato está, pero no donde la convención lo pide. Es un defecto de la cabecera,
no de la medición.

## Limitaciones

1. **El tamaño.** Diez sesiones, 22 ejecuciones, 8 en el denominador de la abstención innecesaria.
   Un solo caso movería `T_AI` en 0,125. No se calculan intervalos y no se debe leer ninguna tasa
   como una estimación precisa.
2. **Sin criterio numérico preregistrado** para las dos tasas, por lo dicho en la sección A.
3. **Datos sintéticos.** La evaluación mide el comportamiento del sistema sobre el conjunto que nunca
   vio, no su comportamiento sobre un vehículo.
4. **El conjunto de prueba se abrió tres veces**, con exposición de etiquetas y predicciones en las dos
   primeras. El instrumento no cambió entre aperturas, y está comprobado, pero la circunstancia es
   parte del informe.
5. **La condición con distractor queda fuera** y PI.4 sigue sin poder interpretarse.
6. **El texto de consulta no es ciego:** lo escribió una persona que conocía el fallo, de modo que en
   una ventana mal clasificada la consulta sigue describiendo la condición verdadera. El registro lo
   declara junto a los canales de oráculo cerrados. No se puede atribuir al sistema una robustez ante
   diagnósticos incorrectos que este diseño no permite aislar.
7. **El estrato adverso no sostiene tasas** con dos ejecuciones, y su abstención innecesaria no está
   definida.
8. **La cobertura de afirmaciones no es una anotación independiente.**
9. **El consumo de memoria de `v3` no se muestreó**, y la causa de las dos interrupciones anteriores
   queda como hipótesis.
10. **La coincidencia con validación está explicada y no implica generalización.** Ver la sección
    siguiente. En resumen: cuatro de las seis cifras están forzadas por el diseño o son función
    algebraica de las otras, y las dos restantes coinciden porque fallan los mismos dos casos
    anotados. No debe presentarse como «el sistema se comporta igual en prueba que en validación».

## Auditoría de la coincidencia entre validación y prueba

Las seis tasas de los estratos operativo y comparativo salieron idénticas a las del ensayo sobre
validación. Se auditaron los artefactos existentes, **sin reejecutar nada**, para determinar si había
un error de agregación, una referencia cruzada incorrecta o una reutilización accidental de resultados.
No hay nada de eso, y la coincidencia tiene una explicación verificable.

**Los artefactos son distintos.** Particiones distintas, commits distintos —`afbcfd1` y `8ee2dd8`—,
marcas de tiempo separadas por diez días, y **cero solape de ventanas**: ninguna de las diez ventanas
del estrato operativo de prueba aparece en el de validación, ni ninguna de las cinco del comparativo.
Las anotaciones selladas son distintas. No hay reutilización.

**Cuatro de las seis cifras no podían ser otras.**

| Cifra | Por qué coincide |
|---|---|
| Denominador de `T_FC`, 14 | Forzado por el diseño: 22 ejecuciones menos las 8 que deben explicar. Las 22 son once condiciones de evidencia por dos sesiones, que la regla congelada fija |
| Denominador de `T_AI`, 8 | Diez ejecuciones con evidencia completa menos las que tienen diagnóstico incorrecto. En **las dos** particiones el modelo falla exactamente dos de las diez ventanas elegidas, y en las dos falla **en las mismas dos condiciones**: termostato en una sesión de calentamiento y encendido en una de autopista. Las sesiones son distintas —`warmup__03` frente a `warmup__11`, `highway__09` frente a `highway__01`— pero el patrón de error del modelo es el mismo |
| Cobertura, 6/10 | **Función algebraica de las otras dos**: con ocho ejecuciones que deben explicar, diez con evidencia completa y dos abstenciones innecesarias, la cobertura es necesariamente (8 − 2)/10. No aporta información independiente |
| Denominadores del comparativo, 5 y 6 | **Forzados por la propia regla de selección**, que elige ventanas que el modelo clasifica bien: las cinco ejecuciones con evidencia completa tienen siempre diagnóstico correcto, de modo que el reparto 5/6 es el único posible en cualquier partición |

**Las dos que sí coinciden de verdad, y por qué.** Los numeradores: cero falsa confianza y dos
abstenciones innecesarias en las dos particiones. Y las dos abstenciones innecesarias son, en las dos,
**los mismos dos casos anotados**: `C01_maf_drift` y `C04_misfire`. Pero no por la misma causa:

| Caso | Validación | Prueba |
|---|---|---|
| `C01_maf_drift` | confianza 0,5999 · cobertura 1,00 | confianza 0,5731 · cobertura 1,00 |
| `C04_misfire` | confianza 0,9333 · **cobertura 0,3333** | **confianza 0,4905** · cobertura 0,00 |

En `C01` la causa es la misma en las dos: la confianza del modelo sobre la deriva del caudalímetro se
queda por debajo del umbral, con la evidencia documental completa. En `C04`, no: en validación el
sistema abstuvo **con confianza alta** porque la cobertura de afirmaciones no llegaba al umbral, y en
prueba abstuvo por las dos cosas a la vez. El mismo caso anotado falla en las dos particiones, y el
motivo registrado no es idéntico.

**Qué concluye esta auditoría.** La coincidencia no es un error ni una reutilización, y **tampoco es
evidencia de estabilidad ni de generalización**. Es el resultado de un diseño con denominadores
pequeños y en buena parte forzados, sobre un conjunto de datos cuyas dos condiciones difíciles —el
termostato en calentamiento y el fallo de encendido— se comportan igual en las dos particiones porque
las genera el mismo generador con la misma parametrización. Lo que la coincidencia sí sugiere, sin
demostrarlo, es que los dos fallos difíciles lo son por una propiedad del fenómeno simulado y no por
una peculiaridad de las sesiones de validación.

## Incidentes registrados

| Identificador | Qué pasó | Estado |
|---|---|---|
| `INC-E19-01` | Los intentos `v1` y `v2` quedaron interrumpidos poco después de sellar su anotación, sin mediciones | documentado; anotaciones conservadas; causa raíz no declarada resuelta |
| — | `launchd` relanzó `v3` tres veces al terminar; el ejecutor rechazó las tres antes de escribir nada | resuelto; trabajos retirados |

## Conclusión científica

Lo que estos datos permiten sostener, y nada más:

**Sobre el conjunto de prueba, con la política de suficiencia v2.2, el criterio compuesto no produjo
ninguna explicación sin soporte documental en catorce ejecuciones que debían terminar en abstención,
procedentes de siete sesiones, mientras que una puerta de confianza sola habría explicado las catorce.
El coste medido de ese criterio son dos abstenciones innecesarias en ocho ejecuciones que debían
explicar. Las dos ejecuciones con diagnóstico incorrecto y evidencia completa en el índice terminaron
en abstención con cobertura de afirmaciones nula, pese a una confianza del modelo de 0,91 y 0,97.**

El diagnóstico sobre prueba alcanza 0,8360 de F1 macro frente a 0,0741 de la clase mayoritaria, con el
fallo de encendido como condición débil, 0,4444. El redactor respetó el veredicto en las 35
ejecuciones y no citó nada fuera de lo entregado.

Lo que **no** se sostiene con esto: ninguna tasa como estimación precisa, ninguna afirmación sobre
vehículos reales, ninguna sobre la condición con distractor, y ninguna sobre robustez ante
diagnósticos incorrectos más allá de lo observado en dos ejecuciones cuyo texto de consulta no era
ciego.
