# INC-E5-01 — Cuatro artefactos locales de E5 sobrescritos al probar la puerta de auditoría

**Fecha:** 12 de octubre de 2026 · **Detectado por:** el censo de artefactos históricos
(`configs/artefactos_historicos.json`), automáticamente · **Estado:** resuelto, con el defecto de
raíz corregido.

## Qué pasó

Al probar la nueva puerta de auditoría del generador se ejecutó
`mecanico-exp preprocess --dataset-id prueba_auditoria` sobre un conjunto de 24 sesiones generado
para esa prueba. `run_preprocess` escribía sus artefactos con **nombre fijo**, sin el identificador
del conjunto:

- `tables/E5_estudio_ventana.csv`
- `tables/E5_reparto.csv`
- `figures/FIG-E5-01_estudio_ventana.png`
- `figures/FIG-E5-02_particiones.png`

De modo que preprocesar cualquier conjunto pisaba los artefactos de E5 sobre `synthetic_v2`. Los
cuatro quedaron con datos del conjunto de prueba.

## Cómo se detectó

**El censo de artefactos históricos lo señaló en la verificación inmediatamente posterior**, con las
cuatro rutas y sus huellas antes y después. Es exactamente para lo que se había construido tres
commits antes, y es la única forma de haberlo visto: `tables/` y `figures/` están fuera del control
de versiones, de modo que Git no podía avisar.

## Qué se perdió, y qué no

**Nada irrecuperable.** Los cuatro se regeneraron ejecutando
`mecanico-exp preprocess --dataset-id synthetic_v2`, que es la orden que los produjo originalmente,
sobre el conjunto que sigue en disco.

**Las dos tablas quedaron byte a byte idénticas a sus copias publicadas** en `artifacts/tables/`:

| Artefacto | Huella tras regenerar | Copia publicada en `artifacts/` |
|---|---|---|
| `E5_estudio_ventana.csv` | `b8d8d380ff01f045` | `b8d8d380ff01f045` — **idéntica** |
| `E5_reparto.csv` | `68710f9019cdad8a` | `68710f9019cdad8a` — **idéntica** |

Las **dos figuras** se regeneraron de los mismos datos y **no** son byte a byte iguales: la salida
PNG de matplotlib no es reproducible bit a bit entre ejecuciones.

**Y aquí hay que ser preciso, porque la tentación es decir que están restauradas.** No lo están en
el sentido fuerte: no existe una referencia verificable contra la que compararlas. Las copias
publicadas en `artifacts/figures/` tienen huellas distintas de las que el censo esperaba, igual que
las tablas, así que tampoco sirven de referencia byte a byte. Lo que se puede afirmar es más
estrecho y es lo que se afirma:

| | Referencia verificable | Estado |
|---|---|---|
| `E5_estudio_ventana.csv` | sí, `artifacts/tables/` | **idéntica bit a bit** |
| `E5_reparto.csv` | sí, `artifacts/tables/` | **idéntica bit a bit** |
| `FIG-E5-01_estudio_ventana.png` | **no** | regenerada del mismo dato y de la misma orden; **no verificada** |
| `FIG-E5-02_particiones.png` | **no** | ídem |

Las dos figuras se declaran **regeneradas, no restauradas**. Salen de los mismos datos —cuyas tablas
sí están verificadas— y de la misma orden, pero no hay huella contra la que contrastarlas. No se
declara equivalencia porque el gráfico parezca el mismo.

**Una observación que conviene registrar, porque no la causó este incidente:** las huellas que el
censo esperaba para las dos tablas —`c487e25435da9402` y `cffd1ee3d5144a52`— **no coincidían con las
copias publicadas en `artifacts/`**. Es decir, las copias de trabajo en `tables/` ya habían divergido
de las publicadas antes de que este incidente ocurriera, en algún momento anterior al censo. Tras la
regeneración, las dos coinciden. El estado actual es por tanto **más consistente** que el anterior, y
el censo se actualiza a él.

**`artifacts/` no se tocó en ningún momento**, y es la copia que se entrega y que los notebooks leen.

## El defecto de raíz, corregido

`run_preprocess` tiene ahora `destinos_de(dataset_id)` y escribe con el identificador del conjunto en
el nombre, como ya hacían E6, E7 y E9. Los artefactos publicados de E5 conservan su nombre sin sufijo
y **no los regenera nadie**: siguen siendo el registro de la fase.

E5 era el único ejecutor que quedaba con nombres fijos. Se había revisado `run_baseline`,
`run_temporal`, `run_xai`, `run_retrieval_evaluation`, `run_threshold_sweep`, `run_training_data` y
`run_ablations`, y se pasó por alto porque E5 no produce un registro JSON y no aparecía en la
búsqueda de `experiments/`.

## Qué se aprende

1. **El censo funciona, y era necesario.** Detectó en segundos un daño que Git no podía ver y que, sin
   él, se habría descubierto al mirar una figura rara semanas después, o nunca.
2. **La protección se diseñó mirando los registros JSON**, y por eso se le escapó el único ejecutor
   que no produce ninguno. La búsqueda correcta no era «qué escribe en `experiments/`» sino «qué
   escribe en una ruta fija», y así está ahora el test parametrizado de `tests/test_destinos.py`.
3. **La actualización del censo tras un cambio exige pedirlo explícitamente** —`aceptar_cambios=True`—
   y eso obligó a escribir este documento en lugar de absorber el cambio en silencio, que es
   exactamente lo que se buscaba al añadir esa restricción.
