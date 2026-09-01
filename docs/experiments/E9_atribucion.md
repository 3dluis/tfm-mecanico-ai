# E9 — Atribución sobre el modelo especializado

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Modelo: bosque aleatorio · Conjunto: `synthetic_v2` · 18 casos de validación

## Qué produce

Convierte una predicción en **evidencia observacional localizable**: qué señales
la sostienen, con qué magnitud, en qué dirección y en qué ventana temporal.

| | |
|---|---|
| Función explicada | `predict_proba[clase_predicha]` |
| Explainer | `shap.explainers.Permutation` |
| Fondo | 100 ventanas **normales de entrenamiento** |
| Huella del fondo | `8757d917835e3981` |
| Semilla | 20260901 |

**La función explicada se declara siempre.** Explicar «el modelo» sin decir qué
salida no es explicar. **El fondo sale solo de entrenamiento**: si incluyera
validación, la atribución llevaría información de particiones que el modelo no
debía ver. **La selección es determinista**: sin eso, dos ejecuciones producen
explicaciones distintas del mismo caso y ninguna es verificable.

Se toman normales como fondo y no una mezcla porque la pregunta que la atribución
responde es «qué aparta este caso de la normalidad», y el fondo define esa
normalidad.

## Resultados

| Condición | Señales más atribuidas | Confianza media |
|---|---|---|
| normal | oxygen_sensor, rpm, ignition_timing, intake_air_temperature | 0,554 |
| F01 fuga de vacío | **ltft_bank1, stft_bank1, map, rpm** | 0,721 |
| F02 deriva de caudalímetro | **ltft_bank1, stft_bank1**, corr(stft,ltft) | 0,656 |
| F03 termostato bloqueado | **coolant_temperature** | 0,948 |
| F04 sonda lenta | **oxygen_sensor, stft_bank1** | 0,916 |
| F05 fallo de encendido | oxygen_sensor, rpm, coolant_temperature, intake_air_temperature | 0,649 |

Contraste con la ficha de cada fallo, sobre las 6 señales principales:

| Condición | Declaradas | No declaradas | Ajenas |
|---|---|---|---|
| F01 | 4 | 0 | — |
| F02 | 2 | 2 | corr(stft,ltft), map |
| F03 | 1 | 0 | — |
| F04 | 2 | 0 | — |
| F05 | 2 | **4** | coolant_temperature, map, intake_air_temperature |

## Hallazgo 1 — la atribución redescubre por su cuenta el hallazgo de E4

Para la deriva del caudalímetro, **`maf` no aparece en la atribución**. Ni una
vez. Las contribuciones son:

| Señal | Importancia acumulada |
|---|---|
| ltft_bank1 | 0,875 |
| stft_bank1 | 0,619 |
| corr(stft, ltft) | 0,158 |
| map | 0,077 |
| **maf** | **—** |

La ficha del fallo declara `maf` entre sus señales afectadas. El modelo **no la
usa para detectarlo**.

Es el mismo hallazgo tres veces, por caminos independientes:

1. **E4**, midiendo separabilidad: delta de Cliff 0,13 en `maf` frente a 1,00 en
   `stft_bank1`.
2. **E9**, atribuyendo la decisión del modelo: `maf` no contribuye.
3. **E12**, evaluando recuperación: la consulta sobre síntomas del caudalímetro
   no encuentra el procedimiento del caudalímetro.

**Consecuencia para el modelo de evidencia.** Una explicación que dijera «el
caudalímetro está derivado **porque el caudal es bajo**» sería falsa: el caudal no
es bajo de forma detectable, y el modelo no lo mira. Lo que la evidencia
observacional sostiene es «los ajustes de combustible están desplazados de forma
compatible con una subestimación del aire admitido». Más débil y verdadero.

## Hallazgo 2 — la atribución de F05 arrastra las mismas señales espurias

Cuatro de las seis señales principales del fallo de encendido **no están
declaradas** en su ficha: temperatura de refrigerante, presión de colector y
temperatura de admisión. La condición no toca ninguna.

Son exactamente las señales que E5 encontró **por debajo del suelo de ruido**
cuando el efecto de F05 era indistinguible del azar. Y su confianza media, 0,649,
es la más baja de las cinco condiciones.

La atribución hereda la debilidad del modelo. Cuando el modelo detecta una
condición con poco margen, su explicación señala lo que encuentra, y lo que
encuentra incluye ruido con buena puntuación. **Una explicación puede ser fiel al
modelo y aun así no describir el vehículo.**

Esto es directamente relevante para el verificador de suficiencia: la atribución
de F05 no debería sostener una explicación con la misma fuerza que la de F03.

## Hallazgo 3 — las condiciones limpias producen atribuciones limpias

F01, F03 y F04 atribuyen **exclusivamente** a señales que sus fichas declaran, y
son las tres con mayor confianza entre los fallos separables. F03 se explica con
una sola señal y confianza 0,948.

Cuando la evidencia observacional es sólida, la atribución lo refleja sin ruido.

## Lo que no se afirma

**La atribución no es causalidad.** Dice de qué depende la salida del modelo, no
qué le ocurre al vehículo. F02 lo demuestra: el modelo depende de los ajustes de
combustible, y la avería está en el caudalímetro. Quien leyera la atribución como
causa concluiría que el problema es la mezcla.

Ningún artefacto de esta fase presenta la atribución como causa.

## Limitación de localización temporal

La ventana atribuida es la ventana completa: **120 s**. La atribución no localiza
dentro de ella.

Para F03 --un techo sostenido de temperatura-- es irrelevante. Para F05 --con
episodios de uno a tres segundos-- significa que la evidencia observacional puede
decir «en esta ventana de dos minutos» pero no «en el segundo 47». Es el coste
que E5 declaró al elegir 120 s, y aquí se materializa.

## Tests

`tests/test_xai.py` — 13 casos:

- `test_xai_output_schema`: la salida identifica siempre la función explicada;
- el fondo sale solo de muestras normales, y hay un test que lo comprueba fila a
  fila;
- la selección del fondo es determinista, y semillas distintas dan fondos
  distintos;
- las señales se ordenan por magnitud **absoluta**: una contribución negativa
  grande importa tanto como una positiva;
- la ventana temporal viaja con la atribución --sin ella, la observación no se
  rastrea hasta el dato;
- los nombres de descriptor se separan por sufijo conocido y no por el primer
  guion bajo: `coolant_temperature_delta_min` es la señal `coolant_temperature`.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 55 ficheros |
| `pytest` | **216 casos** en verde |

## Artefactos

- `experiments/E9_xai_synthetic_v2.json` — función explicada, explainer, fondo y
  su huella, semilla, y las 10 principales atribuciones de cada caso
- `tables/E9_atribuciones_synthetic_v2.csv`, `E9_resumen_synthetic_v2.csv`
- `uv run mecanico-exp xai`

## Siguiente

E15 — verificador de suficiencia. Ya tiene sus dos entradas: la evidencia
observacional de esta fase y la documental de E11-E12. Y tiene tres casos
interesantes de partida: F03 con evidencia sólida por ambos lados, F05 con
atribución ruidosa, y F01 con atribución limpia y **sin ningún respaldo
documental**.
