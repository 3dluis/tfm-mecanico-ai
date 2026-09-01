# E5 — Preprocesamiento, ventanado y particionado

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Datos: `synthetic_v2` (43 200 muestras, 72 sesiones)

## Objetivo

Fijar la unidad de análisis --la ventana--, los descriptores que la resumen y un
reparto en entrenamiento, validación y test que no filtre información.

## Conjunto de datos nuevo

`synthetic_v1` servía para explorar. Para modelar se genera `synthetic_v2`, con
12 sesiones por condición en lugar de 6, por dos razones:

1. Con 6 sesiones, el test se quedaba en **una sola sesión por clase**. Cualquier
   métrica calculada sobre eso sería anecdótica.
2. El reparto cíclico de 6 sesiones entre 4 regímenes producía el desequilibrio
   que E4 anotó. Con 12 el cruce condición × régimen queda en **3 sesiones
   exactas en las 24 combinaciones**.

## Descriptores

139 por ventana, en orden fijo y explícito: 11 estadísticos × 12 señales, más 6
correlaciones entre parejas y un cociente.

Los estadísticos responden al requisito de E4 --las medias no bastan--: media,
desviación, mínimo, máximo, recorrido, pendiente, salto mínimo, salto máximo,
número de eventos, autocorrelación de retardo 1 y cruces por la mediana.

- **Cruces por la mediana** cuenta oscilaciones con independencia de la amplitud:
  es lo que distingue una sonda sana de una lenta.
- **Número de eventos** cuenta saltos que se apartan más de tres desviaciones de
  lo habitual *en esa misma ventana*. El umbral es relativo y no absoluto: uno
  fijo en rpm contaría como evento cualquier aceleración en autovía.
- **`maf_over_rpm_load`** es un descriptor informado por la física, respuesta
  directa al hallazgo de E4. Lleva marca `[VERIFY_ON_REAL_DATA]`: la constante de
  proporcionalidad depende del motor, y en datos reales habría que comprobar que
  el cociente es estable en condiciones normales antes de usarlo como evidencia.

## Hallazgo 1 — el suelo de ruido de «el mejor descriptor entre 139»

Elegir el descriptor con mayor tamaño de efecto entre 139 produce un máximo
inflado: con suficientes comparaciones, algo destaca siempre. Sin una referencia,
un valor moderado se confunde con evidencia.

Se midió el control: se toma **solo la condición normal**, se parte en dos
mitades **por sesión** y se calcula el mismo estadístico. No hay fallo de por
medio, así que todo lo que salga es ruido. Treinta repeticiones, percentil 90:

| Ventana | Suelo de ruido (p90) |
|---|---|
| 10 s | 0,369 |
| 30 s | 0,399 |
| 60 s | 0,438 |
| 120 s | 0,512 |

El suelo **sube** con la ventana, porque hay menos ventanas y cada estimación es
más ruidosa. Comparar tamaños de efecto entre longitudes sin corregir por esto
llevaría a conclusiones invertidas.

El control queda como función reutilizable, `noise_floor_max_delta`, no como un
cálculo de una vez.

## Hallazgo 2 — la evidencia aparente del fallo de encendido era ruido

Con ventana de 30 s, el mejor descriptor para el fallo de encendido resultó ser
`coolant_temperature_slope`, con delta 0,396. Sus ocho mejores descriptores eran
**todos** variantes de la temperatura de refrigerante.

El fallo de encendido no toca la temperatura de refrigerante. Su ficha declara
régimen, carga, ajuste a corto plazo y sonda lambda.

Y 0,396 queda **por debajo** del suelo de ruido de esa longitud (0,399).

Es decir: a 30 s la condición es indistinguible de la normal, y lo que parecía
señal era exactamente lo que el ruido predice. La temperatura difiere entre
sesiones porque cada una arranca con una temperatura ambiente distinta; con 12
sesiones por condición, esa variación entre sesiones basta para producir un
efecto aparente.

Este hallazgo es el mismo fenómeno que la pregunta de investigación interroga, en
miniatura: **evidencia con buen aspecto que no sobrevive al escrutinio**.

## Decisión de longitud de ventana

| Ventana | Suelo | F01 | F02 | F03 | F04 | F05 | Mejor descriptor de F05 |
|---|---|---|---|---|---|---|---|
| 10 s | 0,369 | 1,00 | 0,96 | 0,83 | 1,00 | 0,38 | temperatura — **no declarada** |
| 30 s | 0,399 | 1,00 | 0,99 | 0,80 | 1,00 | 0,40 ↓ | temperatura — **no declarada** |
| 60 s | 0,438 | 1,00 | 1,00 | 0,79 | 1,00 | 0,52 | sonda lambda — declarada |
| 120 s | 0,512 | 1,00 | 1,00 | 0,82 | 1,00 | 0,73 | sonda lambda — declarada |

↓ = por debajo del suelo de ruido.

**Elegida: 120 s, paso 60 s (solape 0,5).**

El criterio no es «el número más alto» sino la **concordancia con el mecanismo**.
Cuatro de las cinco condiciones se separan igual de bien a cualquier longitud, así
que la decisión la determina la quinta. A 10 s y 30 s el efecto aparente de F05
cae sobre una señal que el fallo no toca; a 60 s y 120 s cae sobre la sonda
lambda, que su ficha sí declara. A 120 s aparecen además `oxygen_sensor_max`,
`oxygen_sensor_range` y `rpm_min`, todas declaradas.

Un efecto sobre una señal sin mecanismo detrás es ruido con buena puntuación,
aunque el número sea mayor.

**Coste declarado.** 120 s deja 588 ventanas frente a las 8 508 de 10 s, y
localiza peor en el tiempo, lo que limitará lo que E9 pueda señalar. Se asume
porque la alternativa es medir una condición que a longitudes cortas no existe.

**Aviso para E6-E8.** Incluso a 120 s, el efecto de F05 (0,734) es solo 1,43 veces
el suelo de ruido (0,512). Es real pero débil. **No se da por supuesto que sea
clasificable.** Si el modelo no lo consigue, se reportará como resultado y no se
subirá la severidad del fallo para forzar un número favorable.

## Reparto sin fuga

**Se reparten sesiones, nunca ventanas.** Dos ventanas de la misma sesión
comparten el vehículo, el trayecto y --con solape-- muestras literales.
Repartirlas entre entrenamiento y test convierte la evaluación en un examen con
las respuestas delante, y el síntoma es que las métricas *mejoran*.

Estratificado por condición, semilla 20260901:

| Partición | Ventanas | Sesiones |
|---|---|---|
| train | 392 | 48 |
| validation | 98 | 12 |
| test | 98 | 12 |

Ocho sesiones de entrenamiento, dos de validación y dos de test por cada una de
las seis condiciones.

Auditoría: *ninguna sesión aparece en dos particiones*. Las tres contienen las
seis clases.

Las ventanas que **cruzan la entrada del fallo se descartan**: 60 de 648. Un
tramo mitad normal y mitad averiado no pertenece a ninguna clase, y etiquetarlo
por mayoría metería ruido justo en la transición, que es donde más se juega. El
descarte se cuenta y se publica; un descarte silencioso es una pérdida de datos
que nadie audita.

## Desequilibrio de clases declarado

| Clase | Ventanas | % |
|---|---|---|
| normal | 168 | 28,6 |
| cada fallo | 84 | 14,3 |

Dos a uno. No es un defecto del reparto: las sesiones averiadas aportan también
sus ventanas anteriores a la entrada del fallo, correctamente etiquetadas como
normales. Es además la situación realista.

**Consecuencia para E8.** La exactitud global es engañosa con este reparto. Se
reportará F1 macro y PR-AUC, y se considerará ponderación de clases en el
entrenamiento.

## Tests

`tests/test_preprocessing.py` — 24 casos. Los que sostienen la fase:

- `test_timeseries_windowing`: forma, procedencia y geometría declarada.
- `test_no_temporal_leakage`: ninguna sesión en dos particiones.
- `test_el_auditor_detecta_un_reparto_aleatorio_por_ventana`: se **provoca** el
  error clásico y se exige que el auditor lo señale. Un test que solo comprueba
  el caso correcto no demuestra que el detector funcione.
- ninguna ventana cruza una sesión ni mezcla normal con fallo;
- las ventanas previas al fallo de una sesión averiada se etiquetan como
  normales;
- una condición con muy pocas sesiones se rechaza con mensaje útil en lugar de
  devolver una partición vacía.

### Nota sobre el auditor

`audit_split` no puede detectar una fuga: su entrada es un diccionario
`sesión → partición`, donde una sesión no puede estar en dos sitios. Eso es una
garantía estructural, más fuerte que una comprobación, pero solo cubre los
repartos construidos con `split_by_session`.

Se añadió `audit_masks`, que audita máscaras de ventanas vengan de donde vengan.
Ese es el caso que sí ocurre: alguien reparte ventanas con la utilidad genérica
de turno y las de una misma sesión acaban a ambos lados. El test lo provoca y
comprueba que se detecta.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `ruff format --check` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 34 ficheros |
| `pytest` | 99 casos en verde |

## Artefactos

- `data/raw/synthetic/synthetic_v2.parquet` + ficha
- `data/processed/synthetic_v2_{x,features}.npy`, `_meta.parquet`,
  `_preprocess.json` (incluye la asignación completa de sesiones y la semilla)
- `tables/E5_estudio_ventana.csv`, `tables/E5_reparto.csv`
- `figures/FIG-E5-01_estudio_ventana.png`, `FIG-E5-02_particiones.png`
- `uv run mecanico-exp preprocess`

## Siguiente

E6 — baseline. Bosque aleatorio sobre los 139 descriptores, con el conjunto de
test cerrado hasta E19.
