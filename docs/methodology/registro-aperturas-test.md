# Registro de aperturas del conjunto de prueba

**Por qué existe.** La sección 6 del encargo del autor lo pide como registro formal y separa tres
cosas que no son la misma: la **apertura técnica** del conjunto, la **exposición** de etiquetas o
predicciones, y la **utilización efectiva** de resultados para tomar decisiones. Una interrupción no
equivale a una evaluación sin exposición, y conviene que eso esté escrito antes de que alguien lo
pregunte.

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
