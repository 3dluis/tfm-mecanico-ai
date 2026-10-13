# Reproducir desde un clon limpio

**Actualizado:** 12 de octubre de 2026 · **Comprobado:** clonando el repositorio en un directorio
temporal y ejecutando los seis pasos, no suponiéndolos.

Quien reciba este repositorio no tiene la máquina del autor. Este documento dice exactamente qué
funciona sin ella, qué hay que reconstruir y qué no se puede reproducir en absoluto, con el motivo.

## Los seis pasos

```bash
git clone <repositorio> mecanico-ia-exp
cd mecanico-ia-exp

# 1. Dependencias
uv sync --extra nb --extra ml

# 2. Reconstruir los datos que no se distribuyen
bash scripts/reconstruir_datos.sh

# 3-5. Gate de calidad
uv run pytest
uv run ruff check .
uv run mypy src

# 6. Notebooks de demostración
uv run jupyter lab notebooks/
```

**Resultado esperado**, medido en un clon real:

| Paso | Sin reconstruir | Tras reconstruir |
|---|---|---|
| `pytest` | **815 pasan, 12 se detienen** con instrucciones | **829 pasan** |
| `ruff check` | pasa | pasa |
| `mypy src` | pasa | pasa |
| notebooks DEMO | los cuatro se ejecutan | ídem |

Los doce que se detienen sin reconstruir dicen qué falta y la orden exacta. No es un `skip` de
conveniencia: miden algo real y lo que falta es un dato **reconstruible**.

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
