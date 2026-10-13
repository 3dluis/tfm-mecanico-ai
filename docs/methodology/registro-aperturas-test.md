# Registro de aperturas del conjunto de prueba

**Por qué existe.** El encargo del autor lo pide como registro formal, y pide además que no se
confundan cosas que no son la misma. En la revisión del 13 de octubre de 2026 la distinción se
afina de tres niveles a **cinco**, porque tres mezclaban casos que merecen nombres distintos.

## Los cinco niveles, de menos a más

| Nivel | Qué es | Qué consume |
|---|---|---|
| **1 · Apertura técnica** | la partición se cargó: `allow_test=True` con razón por escrito | el registro. Nada más, si no pasa de aquí |
| **2 · Lectura de identificadores** | se leyeron `session_id`, recuentos o el reparto, sin ver ninguna señal ni etiqueta | casi nada en información, pero **sí** el argumento de que no se tocó |
| **3 · Exposición de etiquetas** | se vio qué fallo tenía cada ventana | la posibilidad de construir una hipótesis sin saber la respuesta |
| **4 · Exposición de predicciones** | se vio qué predijo el modelo, y por tanto en qué acierta y en qué falla | lo que hace de la prueba una prueba: ya no se puede diseñar a ciegas |
| **5 · Utilización de resultados** | alguna decisión —un umbral, un diseño, una interpretación— se tomó a la vista de lo que la prueba dijo | la independencia, de verdad y sin remedio |

**La diferencia entre el 4 y el 5 es la que sostiene este trabajo.** Hubo exposición de predicciones
—niveles 3 y 4— en tres aperturas, y eso no se puede deshacer. Lo que se defiende es que no hubo
utilización: que ninguna decisión se tomó mirando el resultado. Y eso es verificable, no una
declaración de intenciones: el instrumento no cambió entre la primera apertura y la medición, y el
comando que lo comprueba está más abajo.

**Una interrupción no equivale a una evaluación sin exposición.** Las dos primeras aperturas
murieron sin calcular ninguna métrica, y aun así llegaron al nivel 4.

El cierre técnico está en `src/mecanico_ia_exp/data/dataset.py`: pedir la partición de prueba exige
`allow_test=True` y una razón por escrito, que se imprime en la salida de la ejecución. Cada fila de
esta tabla corresponde a una de esas aperturas.

| # | Fecha y hora (UTC) | Intento | Motivo | Configuración | Alcance | Exposición | Métricas | ¿Influyó en decisiones? |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-02, ~02:31 | `v1` | evaluación final autorizada el 1-10 con `OPEN_TEST_AND_RUN_E19` | commit `5b64504`, política v2.2, reglas ancladas en `de6207f` | apertura, predicciones del bosque, anotación sellada; el proceso murió después | **sí**: etiquetas y clase predicha de las 10 ventanas elegidas, incluidas las 2 mal diagnosticadas | **no**: ninguna métrica llegó a calcularse | una sola vez, y se retiró: ver abajo |
| 2 | 2026-10-06, ~02:19 | `v2` | intento tras la interrupción de `v1` | commit `8ee2dd8`, sin cambios en el diseño congelado | idéntico a `v1`; también interrumpido | **sí**, la misma información; la anotación resultó idéntica a la de `v1` salvo la cabecera | **no** | no |
| 3 | 2026-10-12, 21:38 → 21:50 | `v3` | intento tras la interrupción de `v2`, bajo `launchd` | commit `8ee2dd8` | evaluación completa, 35 ejecuciones | sí | **sí**, todas | es la medición |
| 4 | 2026-10-13, 04:12 | `prueba` | **P3**, pendiente del tutor: repetir sobre prueba las cuatro ablaciones de E18, definidas y congeladas el 1-10, **antes** de la primera apertura | commit `bdf8640`, política v2.1, umbrales congelados sin cambios desde el 4-09 | las cuatro ablaciones sobre los 17 casos anotados, modo oracular, sin proveedor de lenguaje | sí: etiquetas y predicciones de las ventanas elegidas en prueba | **sí**, las del pre-registro de E18 | **no**, y es condición de la ejecución: sus resultados no se usan para rediseñar P1, ajustar P2, mover un umbral ni cambiar la política |
| 5 | 2026-10-13, ~05:0x | — | **accidental**: la comprobación de contaminación de P2 llamaba a `load_partition("test")` para leer los identificadores de sesión | commit de la rama `fase3/p2-adaptador-v3` | solo `session_id` de las 12 sesiones de prueba | **no**: ninguna etiqueta, ninguna predicción, ninguna ventana | **no**: no se calculó ninguna | **no**. Corregido en el acto: la comprobación lee ahora el reparto de `synthetic_v2_preprocess.json`, que tiene la misma información sin abrir nada |

## Las cinco aperturas clasificadas por nivel

| # | 1 · Apertura | 2 · Identificadores | 3 · Etiquetas | 4 · Predicciones | 5 · Utilización | Nivel alcanzado |
|---|---|---|---|---|---|---|
| 1 · E19 `v1` | sí | sí | **sí** | **sí** | no (una vez citada y **retirada**) | **4** |
| 2 · E19 `v2` | sí | sí | **sí** | **sí** | no | **4** |
| 3 · E19 `v3` | sí | sí | **sí** | **sí** | es la medición declarada | **4**, y el 5 por diseño |
| 4 · P3 | sí | sí | **sí** | **sí** | no, y es condición de la ejecución | **4** |
| 5 · accidental | sí | **sí** | no | no | no | **2** |

La tercera es el único caso donde el nivel 5 es legítimo, porque esa apertura **era** la medición
autorizada: utilizar su resultado es a lo que se abrió.

## Qué limitan las aperturas acumuladas, y qué no

La pregunta es si cinco aperturas dejan algo que pueda llamarse evaluación independiente. Revisada
una a una, la respuesta tiene dos partes y ninguna es «sí, intacto».

**Lo que sigue en pie.** La medición de E19 conserva su carácter de independiente en el sentido que
importa: **el instrumento no se modificó entre la primera apertura y la medición**. Umbrales, casos
elegibles, reglas de selección, política, métricas publicables y código: ni una línea. Eso es
comprobable con un comando y no depende de la palabra de nadie. Las tres primeras aperturas son el
mismo intento repetido, no tres miradas distintas.

**Lo que ya no puede decirse.**

1. **Que el conjunto esté intacto.** No lo está. Se abrió cinco veces, y en cuatro hubo exposición
   de etiquetas y predicciones.
2. **Que una evaluación futura sobre esta partición sea plenamente independiente.** No lo sería. El
   analista ha visto qué ventanas de prueba el modelo diagnostica mal. Cualquier medición nueva
   sobre `synthetic_v3`/prueba arrastra ese conocimiento, y declararla independiente sería falso.
   Por eso el conjunto de evaluación del redactor **no sale de la partición de prueba**:
   [`evaluacion-independiente-redactor.md`](evaluacion-independiente-redactor.md).
3. **Que la cuarta apertura sea una estimación operativa.** Lo dice su propia revisión de
   independencia: describe un estrato favorable, no una tasa poblacional.

**Lo que esto significa para el tribunal.** La partición de prueba de este trabajo es un recurso
**gastado**, no un recurso intacto. Rindió una medición —E19— y una comprobación pre-registrada
—P3—, las dos con su exposición declarada, y no queda margen para una tercera pregunta que
necesite independencia. Quien lea los resultados tiene derecho a saberlo, y por eso está escrito
aquí y en las limitaciones, no solo en el informe de E19.

## Sobre la quinta, que no debió ocurrir

Se registra aunque su exposición fuera mínima, porque el criterio de este trabajo es registrar **la
apertura**, no el daño.

Al implementar la comprobación de contaminación de P2 —que los ejemplos de ajuste del redactor no
toquen validación ni prueba— la primera versión cargaba las dos particiones con
`load_partition(..., allow_test=True)` para leer sus identificadores de sesión. Funcionaba, y abría
el conjunto de prueba para obtener una información que **ya estaba en otro sitio**: el reparto por
sesión está en `data/processed/synthetic_v2_preprocess.json`, que no es una partición sino un mapa.

Lo que se expuso: los `session_id` de las doce sesiones de prueba. Ninguna etiqueta, ninguna
predicción, ninguna ventana, ninguna métrica. No influyó en ninguna decisión: el resultado de la
comprobación fue el mismo antes y después de corregirla —cero solape—.

**Corregido en el acto**, y la lección es la que vale: una apertura innecesaria es peor que inútil,
porque gasta lo único que no se repone. Antes de leer una partición reservada hay que preguntarse si
la información que se busca está en un artefacto derivado, y aquí lo estaba.

## Sobre la cuarta apertura

Las tres primeras son la misma medición, E19, intentada tres veces. La cuarta es **otra cosa** y
conviene no confundirlas.

**Qué la justifica.** Las cuatro ablaciones de E18 se congelaron el 1 de octubre, **antes** de que el
conjunto de prueba se abriera por primera vez, y midieron sobre validación qué aporta cada componente
del criterio. La pregunta que quedaba —si eso se sostiene fuera de la partición con la que el
criterio se ajustó— solo se responde sobre prueba.

**Qué la acota.** La revisión de independencia está en
[`revision-independencia-p3.md`](revision-independencia-p3.md), con las siete condiciones verificadas
una a una **antes** de ejecutar. Dos salvedades se declaran allí y se repiten aquí porque importan:

1. **El analista ya ha visto los resultados de E19.** No se puede deshacer. Las ablaciones están
   pre-registradas y el código congelado, de modo que no hay ninguna decisión que contaminar en
   tiempo de ejecución; lo que ocurre con conocimiento previo es la interpretación, y por eso la
   lectura de cada desenlace posible quedó escrita antes de medir.
2. **No es una estimación operativa.** La regla de selección elige ventanas que el modelo clasifica
   bien, consultando sus predicciones. Describe el comportamiento en condiciones favorables, como el
   estrato comparativo de E19, y no estima ninguna tasa poblacional.

**Lo que esta apertura no autoriza:** usar sus resultados para rediseñar la condición con distractor,
ajustar el reentrenamiento del adaptador, mover un umbral o cambiar la política. Es condición de la
ejecución, no una recomendación.

## La única influencia detectada, y qué se hizo con ella

En el borrador de la auditoría de PI.1 se citó una ventana de prueba mal diagnosticada
—`F03_thermostat_stuck__warmup__11@120s`, conocida por la anotación del intento `v1`— como
corroboración de una hipótesis construida sobre entrenamiento y validación. La revisión del diff lo
señaló antes de fusionar, y **se retiró de la inferencia**: el documento final la menciona separada y
declara que no la sostiene. De ahí no se derivó ninguna decisión experimental.

## Por qué la evaluación conserva su carácter de medición independiente

Porque el instrumento no cambió entre la primera apertura y la medición, y eso se comprueba con un
comando:

```
git diff --stat 5b64504..8ee2dd8 -- src/ configs/ tests/ Makefile pyproject.toml
```

está **vacío**. Entre las dos fechas solo cambiaron cuatro ficheros: el informe de la incidencia, la
sección de desenlace de la declaración de apertura, la auditoría de PI.1 y la anotación sellada del
intento `v1`. Ningún fichero congelado —umbrales, casos elegibles, reglas de selección, política,
métricas publicables— y ninguna línea de código.

## Lo que no puede decirse

Que el conjunto se abrió una sola vez. Se abrió tres, y hubo exposición de etiquetas y predicciones en
las dos primeras. Esa circunstancia forma parte del informe de E19 y de sus limitaciones, y debe estar
ante el tribunal.
