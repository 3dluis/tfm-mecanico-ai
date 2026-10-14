# Reproducir desde un clon limpio

**Actualizado:** 13 de octubre de 2026 · **Comprobado:** clonando el repositorio en un directorio
temporal y ejecutando los pasos, no suponiéndolos. Última pasada completa: commit `3ab02d2`,
**todos los pasos en verde**, incluidos los siete notebooks y sus versiones HTML. La validación del 13 de octubre **encontró tres
defectos** y están corregidos; lo que sigue es el estado tras corregirlos.

Quien reciba este repositorio no tiene la máquina del autor. Este documento dice exactamente qué
funciona sin ella, qué hay que reconstruir y qué no se puede reproducir en absoluto, con el motivo.

## Los pasos

```bash
git clone <repositorio> mecanico-ia-exp
cd mecanico-ia-exp

# 1. Dependencias. Los cinco extras, no dos: `transformers`, `peft`,
#    `sentence-transformers` y `huggingface-hub` se importan en src, y sin ellos
#    fallan cuatro pruebas y seis comprobaciones de tipado.
uv sync --extra nb --extra ml --extra embeddings --extra finetune --extra llm --extra docx

# 2. Reconstruir el conjunto que no se distribuye y COMPROBAR sus huellas
bash scripts/reconstruir_datos.sh

# 3. Qué se puede ejecutar, y ejecutarlo
uv run python scripts/estado_pruebas.py --ejecutar

# 4. Resto del gate
uv run ruff check .
uv run ruff format --check src tests scripts
uv run mypy src

# 5. Notebooks de demostración
uv run jupyter lab notebooks/
```

**Resultado esperado**, medido en un clon real el 13 de octubre de 2026:

| Paso | Sin reconstruir | Tras reconstruir |
|---|---|---|
| pruebas **inmediatas** | **902 pasan** | 902 pasan |
| pruebas **con preparación** | **17 se detienen** con la orden exacta | **17 pasan** |
| pruebas **con recursos externos** | 15, declaradas y no ejecutables | ídem |
| `ruff check` · `ruff format` | pasan | pasan |
| `mypy src` | pasa | pasa |
| **notebooks DEMO** | los **seis** se ejecutan desde un kernel limpio | ídem |
| **notebook 06 (FULL)** | se detiene: necesita `synthetic_v2` | **se ejecuta** |
| **las siete versiones HTML** | completas, sin rutas locales, con la modalidad visible | ídem |
| comprobaciones del traslado de P2 | **se niegan**, con el motivo medido | ídem |
| censo de artefactos | 0 desviaciones | 0 desviaciones |

`scripts/estado_pruebas.py --ejecutar` devuelve **2** si la segunda categoría no se ha podido
ejecutar, y **1** si falla la primera. No declara satisfactoria una categoría que no ha corrido:
una prueba detenida no es una prueba que pase.

## Lo que la validación del 13 de octubre encontró

Tres defectos que esta máquina no mostraba, y por eso se valida en un clon y no aquí:

| Defecto | Síntoma en el clon | Corregido |
|---|---|---|
| **`transformers` y `huggingface-hub` se importaban sin estar declarados** | 4 pruebas fallaban y `mypy` daba 6 errores de importación; llegaban como dependencia transitiva de `sentence-transformers` | declarados en el extra `finetune`, donde se usan. La versión resuelta no cambia —`transformers` 5.16.1, `huggingface-hub` 1.29.0—, de modo que el entorno que produjo los resultados es el mismo |
| **La orden de instalación documentada era incompleta** | dos extras de cinco | corregida arriba |
| **`synthetic_v3` no es reconstruible y el guion lo intentaba** | producía un conjunto distinto con el mismo nombre, y el censo de artefactos lo detectaba después | el guion se niega; la medición y la causa quedan en `configs/datos_no_reconstruibles.json` y en L-25 |

## Lo que no se puede reproducir, y por qué

Se comprueba muestra a muestra, que es más estricto que contrastar las huellas de los ficheros
procesados: esas pueden coincidir aunque las señales sean otras, porque el ventanado y el reparto
dependen de identificadores e instantes y no de valores.

```bash
uv run python scripts/medir_reconstruccion_cruda.py
# synthetic_v1   NO RECONSTRUIBLE   idénticas 0 de 36 · diferencia máxima 1973.10
# synthetic_v2   RECONSTRUIBLE      idénticas 72 de 72
# synthetic_v3   NO RECONSTRUIBLE   idénticas 0 de 216 · diferencia máxima 1983.48
```


| Qué | Por qué | Consecuencia |
|---|---|---|
| **`synthetic_v1`** | es **pre-calibración**, como `synthetic_v3`, y se comprobó el 13-10-2026: cero de 36 sesiones idénticas, diferencia máxima 1 973 rpm. El control sobre `synthetic_v2` da 72 de 72 | las seis figuras y las cinco tablas de **E4**, el análisis exploratorio, no son reproducibles por un tercero. El guion se niega a regenerarlo |
| **`synthetic_v3`** | es **pre-calibración**: se generó antes del commit que calibró el generador contra el manual de taller. El generador publicado produce otras señales: cero de 216 sesiones idénticas | la comparación de volumen de E6 y E7 **sobre `synthetic_v3`** no es reproducible por un tercero, ni lo son las quince ventanas del conjunto de evaluación independiente del redactor, que salen de su partición de validación. Las cifras publicadas de diagnóstico y la evaluación final **no** salen de este conjunto: salen de `synthetic_v2`, que sí se reconstruye. Se conserva sin regenerar, por decisión documentada |
| **El corpus documental** | 3 055 PDF de un manual con licencia; no se redistribuye | E11–E15 no se pueden ejecutar sin conseguirlo |
| **El índice documental** | se construye del corpus | las pruebas con marcador `db` no se ejecutan |
| **Los pesos del adaptador** | no se distribuyen | las pruebas con marcador `llm` no se ejecutan |
| **Los ejemplos de ajuste del redactor** | se generan con el índice documental | las pruebas con marcador `artefactos` no se ejecutan |

Los diecisiete que se detienen sin reconstruir dicen qué falta y la orden exacta. No es un `skip` de
conveniencia: miden algo real y lo que falta es un dato **reconstruible y verificable por huella**.

## Por qué hay que reconstruir, y por qué eso no es una concesión

`data/raw/**` y `data/processed/**` están en `.gitignore`. `synthetic_v2` son 43 200 muestras y
`synthetic_v3`, 129 600. No se distribuyen porque **no hace falta**: el generador es determinista y
los reconstruye bit a bit.

Y eso se comprueba, no se promete. `scripts/reconstruir_datos.sh` termina llamando a
`scripts/verificar_reconstruccion.py`, que contrasta las cuatro huellas contra las que el manifiesto
de E19 congeló **antes** de abrir el conjunto de prueba:

```
  OK  data/processed/synthetic_v2_x.npy            42e3031653498bf4
  OK  data/processed/synthetic_v2_features.npy     c8fa7068c13a274e
  OK  data/processed/synthetic_v2_meta.parquet     ffef0c525d441988
  OK  data/processed/synthetic_v2_preprocess.json  e63be72934a75f7c

Los 4 ficheros coinciden bit a bit con el estado congelado de E19.
```

Si alguna difiere, el guion **falla**. Un conjunto reconstruido que no coincide con el congelado es
peor que no poder reconstruirlo: las pruebas pasarían midiendo otros datos.

### El esquema histórico, y por qué existe

`synthetic_v1`, `v2` y `v3` se generaron antes de que existieran las columnas de expresión efectiva
del fallo (`docs/methodology/expresion-efectiva-del-fallo.md`). Reconstruirlos con el esquema
vigente produce un `meta.parquet` distinto —las columnas llegan al ventanado— y la verificación de
la congelación de E19 fallaría.

Por eso el guion usa `--esquema historico`, que omite esas tres columnas. **Reproducir un conjunto
congelado incluye reproducir su esquema.** La opción solo se admite para esos tres identificadores;
pedirla para un conjunto nuevo es un error.

Esto se descubrió **haciendo la reconstrucción**, no razonando sobre ella: la primera vez tres de
los cuatro ficheros coincidieron y el cuarto no.

## Lo que no se puede reproducir, y por qué

| Qué | Por qué | Qué se entrega en su lugar |
|---|---|---|
| **El corpus documental** | manual de taller, propiedad del fabricante | los registros de E10–E12 y sus tablas versionadas |
| **Los pesos del adaptador LoRA** | decenas de MB, no versionables con sentido | el registro de su ajuste y su configuración |
| **El bloque documental**: E11–E15, E13, E18 | depende de los dos anteriores y de PostgreSQL con pgvector | sus registros JSON, versionados |
| **Una reejecución de E19** | el conjunto de prueba se abre una vez, y la regla congelada no admite repetirlo por curiosidad | los artefactos congelados, que `03_analisis_e19.ipynb` reanaliza |
| **El reentrenamiento de la GRU** | MPS no es bit a bit determinista | las cifras de su registro |

Las pruebas que dependen de esos recursos llevan marcador: `db` para PostgreSQL, `llm` para un
proveedor de lenguaje, `slow` para ejecuciones largas, `conjunto` para los datos reconstruibles y
`notebook` para la ejecución de los notebooks. Para ejecutar solo lo que funciona sin nada externo:

```bash
uv run pytest -m "not db and not llm and not slow"
```

## El bloque de telemetría, de principio a fin

Es el que se reproduce entero sin base de datos ni manual:

```bash
bash scripts/reproduce_baseline.sh
```

Genera, preprocesa, entrena el bosque, hace el barrido de umbral **con etiqueta propia** y compara
con los registros publicados sin tocarlos. Medido:

- **E6** coincide en los **94 campos** del registro publicado;
- **E15b** coincide en los **952**.

Lo único que difiere es el campo `protocolo`, que el registro antiguo no tenía porque se añadió
después.

## Qué hacer si algo falla

| Síntoma | Causa | Solución |
|---|---|---|
| Doce pruebas se detienen | el conjunto no está reconstruido | `bash scripts/reconstruir_datos.sh` |
| `verificar_reconstruccion.py` dice DIFIERE | se generó con el esquema vigente | borrar `data/raw/synthetic/synthetic_v2.*` y `data/processed/synthetic_v2_*`, y repetir |
| Un ejecutor se niega a escribir | el artefacto publicado ya existe | usar `--etiqueta <nombre>`; es lo correcto, no un obstáculo |
| Pruebas con marcador `db` fallan | no hay PostgreSQL con pgvector | `bash scripts/init_db.sh`, o `-m "not db"` |
| El censo da desviaciones | algo modificó un artefacto histórico | `uv run python -c "from mecanico_ia_exp.experiments.destinos import verificar_historicos as v; [print(d) for d in v()]"` |

## Lo que el censo vigila

146 artefactos con su huella SHA-256 en `configs/artefactos_historicos.json`. `tables/`, `figures/`,
`data/` y `models/` están fuera del control de versiones y no tienen otra protección. Cada entrada
dice si Git la lleva: la ausencia de lo no versionado en un clon **no** es una alarma; la de lo
versionado, sí.

Ha detectado dos daños reales, los dos causados trabajando sobre el repositorio:
`docs/experiments/incidencia-artefactos-e5.md` e `incidencia-artefactos-e15.md`. Ninguno de los dos
habría salido a la luz sin él.
