# E7 — Modelo temporal

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Dispositivo: **MPS** (Apple M4 Pro) · 19 014 parámetros

> **Nota del 4 de septiembre de 2026 (P-06C).** La GRU restaura la época con
> mejor F1 macro **de validación** y la cifra que se reporta es la F1 macro sobre
> esa misma validación: es el máximo de entre sesenta y setenta y cuatro
> evaluaciones sobre el conjunto que se publica. El bosque no selecciona nada
> sobre validación, de modo que la comparación es **asimétrica** y el sesgo
> favorece a la GRU.
>
> Sobre `synthetic_v2` la GRU pierde **a pesar** del sesgo, así que el resultado
> negativo es conservador. Sobre `synthetic_v3` gana por 0,0125, margen inferior
> al sesgo plausible: ese resultado es **inconcluso**, no favorable. Para
> sostener cualquier orden entre los dos modelos haría falta seleccionar la época
> sobre una partición interna de entrenamiento y evaluar con réplicas.

## Elección de arquitectura: GRU

El plan pide elegir **una** arquitectura y justificarla. Se elige GRU
bidireccional:

- **Frente a LSTM.** Tres puertas en lugar de cuatro, alrededor de un 25 % menos
  de parámetros por unidad. Con 392 ventanas de entrenamiento el riesgo dominante
  es el exceso de capacidad, no su falta. Y con secuencias de 120 pasos, la
  memoria de largo alcance que aporta la LSTM no tiene nada que aprovechar.
- **Frente a CNN-1D.** Captaría bien los episodios breves del fallo de encendido,
  pero peor la deriva lenta del caudalímetro y el techo sostenido del termostato,
  que son fenómenos de escala larga.

La cabeza combina media y máximo sobre el tiempo a propósito: la media capta
niveles sostenidos, el máximo capta episodios. E4 y E5 mostraron que las
condiciones se manifiestan de ambas formas, y quedarse con el último estado
oculto perdería una de las dos.

Se declara la elección para poder contrastarla: si el modelo no supera al
baseline, la conclusión no será «hacía falta otra arquitectura».

## Normalización sin fuga

Los estadísticos por señal se ajustan **solo con entrenamiento**. Ajustarlos
sobre el conjunto completo filtraría a entrenamiento la media y la escala de
validación y test. Es una fuga sutil: no la detecta el auditor de particiones de
E5, y mejora las métricas. Hay un test que la provoca y comprueba que no ocurre.

## Resultado con el conjunto oficial

`synthetic_v2` · 392 ventanas de entrenamiento · 98 de validación.

| Modelo | F1 macro | Exactitud |
|---|---|---|
| Baseline (bosque aleatorio) | **0,876** | 0,878 |
| GRU bidireccional | 0,822 | 0,806 |

**La GRU no supera al baseline: −0,053.** Con estos datos, la complejidad añadida
no está justificada.

Por clase, sin embargo, el reparto es revelador:

| Clase | Baseline F1 | GRU F1 |
|---|---|---|
| normal | 0,836 | 0,702 |
| F01 fuga de vacío | 1,000 | 0,929 |
| F02 deriva de caudalímetro | 1,000 | 0,929 |
| F03 termostato bloqueado | 0,783 | **0,857** |
| F04 sonda lenta | 1,000 | 1,000 |
| F05 fallo de encendido | 0,636 | 0,518 |

La GRU **gana en F03**, justo donde E6 predijo que un modelo temporal podía
ganar. Pierde en todo lo demás. El entrenamiento muestra sobreajuste claro: en la
época 50 la pérdida de entrenamiento era 0,141 y la de validación 0,773, subiendo
desde 0,659. La parada temprana se disparó en la época 60 con el mejor estado en
la 19.

## Hallazgo — el límite era el volumen de datos, no la arquitectura

Concluir «la GRU no sirve» habría sido ambiguo: no distingue entre una
arquitectura inadecuada y una arquitectura sin datos suficientes. Se comprobó
generando `synthetic_v3`, idéntico salvo por tener el triple de sesiones (216
frente a 72), y entrenando **los dos modelos** sobre él.

| Conjunto | Ventanas de entrenamiento | Baseline | GRU | Diferencia |
|---|---|---|---|---|
| `synthetic_v2` | 392 | 0,876 | 0,822 | **−0,053** |
| `synthetic_v3` | 1 078 | 0,932 | **0,945** | **+0,012** |

El orden se invierte. Con el triple de datos la GRU alcanza y supera al baseline.

Lo más informativo está por clase:

| Clase | GRU con v2 | GRU con v3 |
|---|---|---|
| normal | 0,702 | 0,906 |
| F01 | 0,929 | 0,990 |
| F02 | 0,929 | 0,990 |
| F03 | 0,857 | 0,891 |
| F04 | 1,000 | 0,979 |
| F05 fallo de encendido | 0,518 | **0,911** |

## Corrección de una conclusión anterior

E5 registró que el efecto del fallo de encendido era 1,43 veces el suelo de ruido
y que **no se daría por supuesto que fuera clasificable**. E6 lo confirmó con
exhaustividad 0,500.

Con el triple de datos, F1 pasa de 0,518 a **0,911**. La condición **sí es
clasificable**; lo que faltaba eran datos, no señal. La formulación prudente de
E5 y E6 era correcta como cautela, pero la conclusión que sugería --que la
condición podía ser indetectable-- queda corregida.

Esto refuerza el valor del control de suelo de ruido de E5: un efecto pequeño
pero real se distingue de uno inexistente aumentando la muestra, y el suelo de
ruido dice cuál de los dos se está mirando.

## Lo que no se afirma

La ventaja de la GRU sobre el baseline con `synthetic_v3` es de **0,012 sobre 343
ventanas de validación**, medida en **una sola ejecución**. Es un margen pequeño.
No se afirma que la GRU sea superior: se afirma que **deja de ser inferior**, y
que la desventaja observada con `synthetic_v2` se explica por el volumen de datos.

Establecer superioridad exigiría repeticiones con semillas distintas e intervalos
de confianza. No se ha hecho, y por tanto no se afirma.

## Decisión pendiente del autor

`synthetic_v3` produce mejores resultados en ambos modelos. Adoptarlo como
conjunto oficial **cambiaría las cifras de E4, E5 y E6**, que habría que
regenerar.

No se toma esa decisión aquí. `synthetic_v2` sigue siendo el conjunto oficial y
`synthetic_v3` queda como análisis de sensibilidad. Los registros de ambos se
conservan por separado.

## Un error corregido durante la fase

Los ejecutores escribían su registro con nombre fijo (`E6_baseline.json`), de modo
que la ejecución sobre `synthetic_v3` **sobrescribió los registros oficiales de
`synthetic_v2`**. Se detectó al comparar, y se corrigió incluyendo el
identificador del conjunto en el nombre de todos los registros, tablas y figuras.
Ambos registros se regeneraron.

Es el tipo de fallo que no da la cara: nada falla, y las cifras publicadas pasan
a corresponder a otro experimento.

## Reproducibilidad en MPS

Las semillas se fijan para NumPy, PyTorch y MPS. Se hace constar que **algunas
reducciones en MPS no son bit a bit deterministas** entre ejecuciones: la semilla
acota la variación pero no la elimina. No se promete una reproducibilidad exacta
que el dispositivo no ofrece.

El dispositivo empleado se registra en cada ejecución. En ninguna de las
ejecutadas hubo que caer a CPU.

## Rendimiento

| Conjunto | Tiempo de entrenamiento | Épocas |
|---|---|---|
| `synthetic_v2` | 44,5 s | 60 (parada temprana, mejor en 19) |
| `synthetic_v3` | 134,6 s | 68 (parada temprana, mejor en 27) |

19 014 parámetros. El modelo cabe holgadamente en memoria y entrena en minutos.

## Tests

`tests/test_temporal.py` — 12 casos:

- la normalización deja media cero y escala uno, y no divide por cero con una
  señal constante;
- **los estadísticos salen solo de entrenamiento**: el test construye una
  validación desplazada y comprueba que no queda centrada, que es lo que
  ocurriría si la normalización la hubiera visto;
- el dispositivo nunca es CUDA y queda registrado;
- probabilidades que suman uno y respetan el orden de clases declarado;
- se restaura el mejor estado y no el último.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `ruff format --check` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 42 ficheros |
| `pytest` | 126 casos en verde |

## Artefactos

- `experiments/E7_temporal_synthetic_v2.json`, `E7_temporal_synthetic_v3.json`
- `experiments/E6_baseline_synthetic_v2.json`, `E6_baseline_synthetic_v3.json`
- `tables/E7_temporal_{por_clase,confusion}_synthetic_v*.csv`
- `figures/FIG-E7-01_confusion_temporal.png`, `FIG-E7-02_entrenamiento.png`
- `uv run mecanico-exp train-temporal --dataset-id synthetic_v2`

## Siguiente

La fase documental del corpus por vehículo, que sustituye al plan original de
E10 y condiciona E11 y E12.
