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
