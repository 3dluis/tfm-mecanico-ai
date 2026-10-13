# Índice de notebooks

**Actualizado:** 13 de octubre de 2026

Los notebooks son documentos científicos ejecutables. Cada uno se entiende por sí solo, se puede
**leer sin ejecutar nada** —hay una copia en HTML— y declara qué modalidad tiene, porque no todos
hacen lo mismo con la evidencia.

## Las cuatro modalidades, y qué autoriza cada una a afirmar

| Modalidad | Qué hace | Qué permite decir |
|---|---|---|
| **REPRODUCCIÓN** | vuelve a ejecutar el cálculo | «esta cifra se reproduce» |
| **REANÁLISIS** | calcula algo nuevo sobre datos existentes | «esto es lo que se ve en los datos», **no** «esta es la cifra publicada» |
| **VISUALIZACIÓN DE EVIDENCIA HISTÓRICA** | lee un artefacto congelado y lo muestra | «esto es lo que el registro dice» |
| **DEMOSTRACIÓN ILUSTRATIVA** | genera un ejemplo para explicar un concepto | nada sobre ningún resultado |

Confundirlas es fácil y es grave en un documento que se entrega como evidencia. Por eso cada
notebook imprime la suya al ejecutarse, en lugar de declararla solo en una celda de texto que puede
quedar desactualizada.

## Los dos modos de ejecución

**DEMO.** Funciona con un clon del repositorio y nada más: `uv sync --extra nb`, abrir Jupyter y
ejecutar. Sin GPU, sin base de datos, sin descargas. Usa los registros versionados
(`experiments/*.json`), las tablas y figuras de `artifacts/` y la muestra de 18 sesiones de
`data/samples/`.

**FULL.** Reproduce los experimentos completos. Exige lo que no se puede redistribuir: el corpus
documental del manual de taller, los pesos del adaptador LoRA, PostgreSQL con pgvector y, según el
caso, un acelerador. Cada notebook FULL documenta sus requisitos.

## Notebooks entregados

| Notebook | Experimentos | Modalidad | Modo | Qué responde |
|---|---|---|---|---|
| [`00_introduccion`](html/00_introduccion.html) | E1–E19 | visualización histórica + ilustrativa | DEMO | el recorrido completo y el estado de la evidencia |
| [`01_exploracion_obd`](html/01_exploracion_obd.html) | E2, E4, E5 | reanálisis + ilustrativa | DEMO | si las señales contienen estructura diagnóstica y de qué forma |
| [`02_comparacion_modelos`](html/02_comparacion_modelos.html) | E6, E7 | visualización histórica | DEMO | si el modelo temporal supera a la línea base, y por qué la pregunta sigue abierta |
| [`03_analisis_e19`](html/03_analisis_e19.html) | E19 | reanálisis sobre congelado | DEMO | si el criterio de suficiencia evita la falsa confianza sobre el conjunto de prueba |
| [`04_explicabilidad`](html/04_explicabilidad.html) | E9, E18 (`A1`) | visualización histórica | DEMO | qué señal sostiene cada diagnóstico, y cuánto aporta la atribución |
| [`05_suficiencia_y_abstencion`](html/05_suficiencia_y_abstencion.html) | E15, E18 (`A1`–`A4`), **P1** | visualización histórica | DEMO | cuándo el sistema se niega a explicar, qué componente lo decide y qué hace ante evidencia que parece pertinente |
| [`06_expresion_del_fallo`](html/06_expresion_del_fallo.html) | E6, E7, fase G de PI.1 | **reanálisis** | FULL (necesita `synthetic_v2` reconstruido) | `fault_active` frente a `fault_expressed`: por qué el modelo acierta donde acierta, y por qué `synthetic_v2` y `synthetic_v3` no son el mismo instrumento |

Los cinco se ejecutan desde un kernel limpio en menos de dos minutos cada uno y están verificados
por `tests/test_notebooks.py`.

## Notebooks heredados, pendientes de desarrollar

Los dieciséis anteriores siguen en `notebooks/`. Su **portabilidad ya era correcta** —ninguno
contiene rutas absolutas ni credenciales, todos importan del paquete— pero su contenido es la
plantilla original y no cumple el estándar de documentación. No se tiran ni se duplican: se
reescribirán conservando su número y su fase.

| Notebook | Fase | Estado | Qué le falta |
|---|---|---|---|
| `00_environment_check` | E1 | plantilla | secciones sin rellenar |
| `01_synthetic_obd_generation` | E2 | plantilla, con contenido | cubierto por `01_exploracion_obd` |
| `02_real_obd_ingestion` | E3 | **vacío** | el experimento no existe: E3 es trabajo futuro |
| `03_timeseries_eda` | E4 | plantilla | cubierto por `01_exploracion_obd` |
| `04_preprocessing_features` | E5 | plantilla | los 139 descriptores, explicados |
| `05_model_training` | E6 | plantilla | cubierto por `02_comparacion_modelos` |
| `06_model_evaluation` | E7 | plantilla | cubierto por `02_comparacion_modelos` |
| `07_xai` | E9 | plantilla | cubierto por `04_explicabilidad` |
| `08_rag_corpus` | E10, E11 | plantilla | FULL: exige el corpus y pgvector |
| `09_retrieval_evaluation` | E12 | plantilla | FULL: exige pgvector |
| `10_llm_agent` | E13 | plantilla | FULL: exige los pesos del adaptador |
| `11_evidence_sufficiency` | E15 | plantilla | FULL |
| `12_abstention` | E15, E16 | plantilla | FULL |
| `13_integrated_experiment` | E17 | **vacío** | FULL |
| `14_final_evaluation` | E19 | **vacío** | cubierto por `03_analisis_e19` |
| `15_tfm_demo` | E20 | plantilla | la demostración no está cerrada |
| `TFM_EXPERIMENTO_COMPLETO` | E20 | **vacío** | ídem |

## Lo que todavía no tiene notebook, y por qué

**No se crean notebooks vacíos para funcionalidad inexistente.** Faltan:

- **Corpus, recuperación, suficiencia y abstención (E10–E16).** Son FULL: dependen del corpus
  documental, que no se redistribuye. Su notebook puede leer los registros en DEMO y declarar la
  parte no reproducible, y así se hará.
- **Ablaciones (E18).** Cerrado sobre validación; el notebook se escribirá con sus cuatro registros.
- **Las fases de PI.1.** **No tienen resultados**: están diseñadas y no ejecutadas. No habrá
  notebook hasta que los tengan, y no se fabricará ninguna narrativa provisional.

## Cómo se construyen

Los `.ipynb` se escriben desde `scripts/notebooks/n*.py`. La razón es práctica: dieciséis secciones
obligatorias y mucha prosa dentro del JSON de un notebook son incómodas de revisar en un `diff`. Los
`.ipynb` se versionan igualmente —son el entregable— y quien los abra en Jupyter no necesita saber
que existe el constructor.

```bash
# Reconstruir los cuatro notebooks
cd scripts/notebooks && python n00_introduccion.py && python n01_exploracion_obd.py \
  && python n02_comparacion_modelos.py && python n03_analisis_e19.py

# Regenerar las copias en HTML (ejecuta cada uno con kernel limpio)
python scripts/notebooks/exportar_html.py

# Validar
uv run pytest tests/test_notebooks.py                    # todo, con ejecución
uv run pytest tests/test_notebooks.py -m "not notebook"  # solo lo estructural, en segundo
```

## Qué comprueba la validación automática

`tests/test_notebooks.py`, 104 comprobaciones:

- **integridad**: el JSON es un notebook válido, también los heredados;
- **estructura**: las doce secciones obligatorias están en los cuatro entregados;
- **interpretación**: hay al menos tantos bloques «Qué muestra / Qué podemos interpretar / Qué no
  podemos afirmar» como figuras. Un gráfico sin las tres lecturas es un adorno;
- **modalidad**: cada notebook declara la suya;
- **portabilidad**: sin rutas absolutas, sin directorios personales, sin credenciales, con la raíz
  resuelta de forma relativa;
- **protección**: ninguna celda escribe donde viven los artefactos ni invoca una reejecución de E19;
- **coherencia**: las cifras de E19 se recalculan desde la tabla congelada y tienen que dar 0/14,
  2/8 y 6/10; las de E6 y E7 tienen que seguir siendo las citadas en el texto;
- **artefactos**: todo lo que los notebooks leen está versionado;
- **ejecución**: los cuatro se ejecutan enteros, **uno por uno y con kernel limpio**, sin errores.

Lo último es lo que impide el fallo más común: un notebook que funciona porque antes se ejecutó otro.

## Dónde escriben los notebooks

En `notebooks/salida/<notebook>/`, y en ningún otro sitio. Las figuras salen en PNG de alta
resolución **y** en SVG vectorial. `artifacts/figures/` guarda las figuras **publicadas** de los
experimentos y no se sobrescribe: el censo de `configs/artefactos_historicos.json` lo vigila con
huellas SHA-256, y hay un test que lo comprueba después de ejecutar los notebooks.
