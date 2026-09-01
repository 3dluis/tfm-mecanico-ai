# E6 — Baseline

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Datos: `synthetic_v2`, ventana de 120 s · **solo entrenamiento y validación**

## Objetivo

Una referencia contra la que medir el modelo temporal de E7. Si el modelo
temporal no la supera, su complejidad añadida no está justificada.

## El test, bajo llave

`load_partition("test")` lanza una excepción. Para abrirlo hacen falta
`allow_test=True` **y** una razón por escrito, que se imprime en la salida de la
ejecución.

No es ceremonia. Si los umbrales de suficiencia o la elección de modelo se
ajustan mirando el test, las cifras finales dejan de ser una predicción y pasan a
describir datos ya vistos. La disciplina no se confía a la memoria de quien
escribe el código: un descuido produce una excepción, no un resultado inválido
que nadie note. Tres tests comprueban el cierre, incluido que el mensaje de error
indique usar validación en su lugar.

## Resultados en validación

98 ventanas · 392 de entrenamiento · 139 descriptores.

| | Exactitud | F1 macro |
|---|---|---|
| Referencia mínima (siempre «normal») | 0,286 | 0,074 |
| Bosque aleatorio | **0,878** | **0,876** |

Exactitud equilibrada 0,857.

| Clase | Precisión | Exhaustividad | F1 | PR-AUC | n |
|---|---|---|---|---|---|
| normal | 0,718 | 1,000 | 0,836 | 0,881 | 28 |
| F01 fuga de vacío | 1,000 | 1,000 | **1,000** | 1,000 | 14 |
| F02 deriva de caudalímetro | 1,000 | 1,000 | **1,000** | 1,000 | 14 |
| F03 termostato bloqueado | 1,000 | 0,643 | 0,783 | 0,847 | 14 |
| F04 sonda lenta | 1,000 | 1,000 | **1,000** | 1,000 | 14 |
| F05 fallo de encendido | 0,875 | 0,500 | 0,636 | 0,822 | 14 |

Ninguna condición se confunde con otra: **todos los errores van a «normal»**,
salvo un caso de F03 clasificado como F05. El modelo no inventa diagnósticos
cruzados; cuando no ve la firma, dice que no hay fallo.

## Hallazgo 1 — el termostato bloqueado tiene un límite físico de detección

De las 14 ventanas de F03, acierta 9. Los cinco errores no están repartidos:

| | n | Temperatura media | Rango |
|---|---|---|---|
| Detectadas | 9 | 70,7 °C | 68,6 – 71,1 |
| No detectadas | 5 | 54,3 °C | 42,8 – 64,9 |

Por régimen: urbano **7/7**, calentamiento **2/7**.

La explicación es física. El fallo consiste en imponer un techo de 71 °C a la
temperatura del refrigerante. Mientras el motor no habría superado ese techo por
sí mismo --durante el calentamiento-- el fallo **no impone nada**, y la señal de
un motor averiado es idéntica a la de uno sano.

Esto no es una debilidad del modelo. **Es un límite de la evidencia disponible.**
Ningún clasificador, por bueno que sea, puede distinguir dos señales idénticas.

**Consecuencia para E15 y E16.** Aquí hay una fuente de casos de abstención
fundamentada en la física del problema, no fabricada para el experimento: existen
ventanas donde la evidencia es genuinamente insuficiente, y en ellas la respuesta
correcta del agente es abstenerse, no elegir la clase más plausible. Es
exactamente el escenario que la pregunta de investigación interroga, y aparece
solo por haber mirado dónde falla el modelo en lugar de quedarse en la cifra
agregada.

## Hallazgo 2 — el fallo de encendido queda a la mitad, como estaba previsto

Exhaustividad 0,500: siete de catorce ventanas van a «normal». Sin patrón claro
por régimen (autovía 3/7, urbano 4/7).

E5 lo había anticipado y dejado escrito: el efecto de F05 a 120 s es 0,734 frente
a un suelo de ruido de 0,512, apenas 1,43 veces. Se registró entonces que **no se
daría por supuesto que fuera clasificable**. No lo es del todo, y se reporta como
resultado.

No se sube la severidad del fallo para mejorar el número. Un fallo de encendido
intermitente que afecta al 5,7 % de los instantes es un caso difícil de verdad, y
un experimento sobre suficiencia de evidencia necesita casos difíciles.

## Hallazgo 3 — el modelo peca de prudente, no de confiado

| | |
|---|---|
| Error de calibración esperado | 0,140 |
| Confianza media | 0,738 |
| Acierto | 0,878 |
| Exceso de confianza | **−0,140** |

El bosque está **infra**confiado: acierta más de lo que dice. Es lo habitual en un
conjunto de árboles, donde la probabilidad es una proporción de votos.

**Consecuencia para E15.** Un criterio de suficiencia con un umbral sobre la
confianza del modelo se abstendría más de lo debido con estas probabilidades.
Habrá que calibrarlas --sobre validación-- antes de fijar el umbral, o el sistema
parecerá prudente cuando en realidad está mal medido.

## Descriptores más influyentes

| Descriptor | Importancia |
|---|---|
| coolant_temperature_delta_max | 0,043 |
| ltft_bank1_max | 0,040 |
| maf_over_rpm_load | 0,039 |
| stft_bank1_mean | 0,038 |
| oxygen_sensor_max | 0,038 |
| rpm_min | 0,038 |

Las importancias están muy repartidas: el más influyente no llega al 4,4 % de
139. Es coherente con seis condiciones que se detectan por vías distintas.

`maf_over_rpm_load` --el descriptor informado por la física que responde al
hallazgo de E4-- aparece en tercer lugar. Sigue marcado `[VERIFY_ON_REAL_DATA]`:
su validez con datos reales está sin comprobar.

**La importancia de un bosque no es explicación causal.** Mide cuánto usa el
modelo cada descriptor, no qué le ocurre al vehículo. La atribución propiamente
dicha es E9.

## Tests

`tests/test_baseline.py` — 15 casos:

- el test cerrado falla sin declaración explícita, sin razón escrita, y su
  mensaje indica la alternativa;
- `test_model_prediction_schema`: una etiqueta por ventana, probabilidades no
  negativas que suman uno, orden de clases declarado;
- la referencia mínima conserva el identificador completo --un `dtype` mal
  elegido lo trunca a la primera letra y produce una exactitud de cero que
  parece un resultado;
- el F1 macro penaliza ignorar una clase minoritaria y la exactitud no;
- la matriz de confusión orienta filas a la verdad;
- el error de calibración detecta el exceso de confianza y pondera por tamaño de
  grupo.

### Un error encontrado por el propio test

La primera ejecución dio exactitud 0,000 para la referencia mínima, lo cual es
imposible: predecir siempre la clase mayoritaria acierta al menos su proporción.
La causa era `np.full(..., dtype=np.str_)`, que produce `<U1` y truncaba
`"F00_normal"` a `"F"`. Habría puesto una cifra falsa en este informe. Queda
cubierto por un test.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `ruff format --check` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 39 ficheros |
| `pytest` | 114 casos en verde |

## Artefactos

- `experiments/E6_baseline.json` — configuración, semilla y métricas
- `tables/E6_baseline_{por_clase,confusion,importancias}.csv`
- `figures/FIG-E6-01_confusion_baseline.png`, `FIG-E6-02_limite_evidencia_f03.png`
- `uv run mecanico-exp train-baseline`

## Umbral para E7

El modelo temporal debe superar **F1 macro 0,876** en validación para justificar
su complejidad. Donde puede ganar es en F03 y F05, las dos condiciones cuya firma
es temporal: en las otras cuatro no queda margen.

Si no lo supera, se reportará así y el baseline quedará como modelo del
experimento.

## Siguiente

E7 — modelo temporal sobre MPS.
