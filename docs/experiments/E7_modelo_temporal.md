# E7 — Modelo temporal
Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Dispositivo: **MPS** (Apple M4 Pro) · 19 014 parámetros

> **Nota del 4 de septiembre de 2026 (P-06C).** La GRU restaura la época con
> mejor F1 macro **de validación** y la cifra que se reporta es la F1 macro sobre
> esa misma validación: es el máximo de entre sesenta y setenta y cuatro
> evaluaciones sobre el conjunto que se publica. El bosque no selecciona nada
> sobre validación, de modo que la comparación es **asimétrica** y el sesgo
> favorece a la GRU.
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

> **`CORRECTED 2026-10-12`.** Las cifras de `synthetic_v2` publicadas aquí hasta esta fecha eran
> anteriores a la regeneración del 1 de septiembre, cuando el generador se calibró contra el manual
> de taller (`770ce70`): el conjunto se regeneró y el informe no se actualizó, de modo que
> contradecía a su propio registro. Las que siguen son las del registro vigente,
> `experiments/E7_temporal_synthetic_v2.json` y `experiments/E6_baseline_synthetic_v2.json`. Las
> anteriores se conservan en la tabla de más abajo, porque la discrepancia es parte de la historia
> del trabajo y no un error que convenga borrar. **La columna de `synthetic_v3` no se corrige:** ese
> conjunto se generó después de la calibración y nunca se regeneró, así que sus cifras ya coincidían
> con su registro.

`synthetic_v2` · 392 ventanas de entrenamiento · 98 de validación.

| Modelo | F1 macro | Exactitud |
| --- | --- | --- |
| Baseline (bosque aleatorio) | **0,8788** | **0,8776** |
| GRU bidireccional | **0,8230** | **0,8265** |

**La GRU no supera al baseline: −0,056.** Con estos datos, la complejidad añadida
no está justificada.

Por clase, sin embargo, el reparto es revelador:

| Clase | Baseline F1 | GRU F1 |
| --- | --- | --- |
| normal | **0,8235** | **0,7692** |
| F01 fuga de vacío | **1,0000** | **0,9655** |
| F02 deriva de caudalímetro | **1,0000** | **0,9231** |
| F03 termostato bloqueado | **0,7826** | **0,8148** |
| F04 sonda lenta | **1,0000** | **0,9655** |
| F05 fallo de encendido | **0,6667** | **0,5000** |

La GRU **gana en F03**, justo donde E6 predijo que un modelo temporal podía
ganar. Pierde en todo lo demás. El entrenamiento muestra sobreajuste claro, y la
parada temprana se disparó en la época **74** con el mejor estado en la **33**.

### Las cifras que este informe publicaba antes de la corrección

Se conservan para que la corrección sea auditable. Ninguna debe citarse.

| Cifra | Publicada antes | En el registro vigente |
|---|---|---|
| F1 macro del bosque | 0,876 | 0,8788 |
| F1 macro de la GRU | 0,822 | 0,8230 |
| Exactitud de la GRU | 0,806 | 0,8265 |
| Normal, bosque / GRU | 0,836 / 0,702 | 0,8235 / 0,7692 |
| Fuga, bosque / GRU | 1,000 / 0,929 | 1,0000 / 0,9655 |
| Caudalímetro, bosque / GRU | 1,000 / 0,929 | 1,0000 / 0,9231 |
| Termostato, bosque / GRU | 0,783 / 0,857 | 0,7826 / 0,8148 |
| Sonda, bosque / GRU | 1,000 / 1,000 | 1,0000 / 0,9655 |
| Encendido, bosque / GRU | 0,636 / 0,518 | 0,6667 / 0,5000 |
| Épocas / mejor época | 60 / 19 | 74 / 33 |
| Segundos de entrenamiento | 44,5 | 50,81 |

## Hallazgo — el límite era el volumen de datos, no la arquitectura

> **`SUPERSEDED 2026-10-12`.** El texto se conserva íntegro; la conclusión **no se sostiene**. La
> comparación entre `synthetic_v2` y `synthetic_v3` cambia **dos cosas a la vez**, no una:
>
> | | `synthetic_v2` | `synthetic_v3` |
> |---|---|---|
> | Generado | 14 de septiembre, 00:37 | **1 de septiembre**, 18:58 |
> | Ralentí sin fallo, mediana | 690 rpm | **820 rpm** |
> | Respaldo del ralentí | rango 640-740 del manual para el Z6 | **ninguno**; es el valor que la calibración retiró |
> | Avance de encendido, primera muestra | 10,15° | 15,05° |
> | Sesiones | 72 | 216 |
>
> `v3` es por tanto **anterior a la calibración del generador**: tiene el triple de sesiones y
> además un fenómeno distinto. `GENERATOR_VERSION` valió `1.0.0` en los dos casos y no los
> distingue, que es por lo que la diferencia pasó desapercibida. La comparación **confunde volumen
> con calibración del fenómeno** y no establece que el volumen fuera la limitación. La pregunta
> queda **abierta**, y el diseño para responderla —una curva de volumen medida **dentro de un solo
> conjunto**, con subconjuntos anidados— está en `docs/diseno-pi1/04-subconjuntos-anidados.md`.
>
> `synthetic_v3` **se conserva tal como está**, sin renombrar y sin modificar, igual que las
> ejecuciones no canónicas de E12 y E13: es la evidencia del resultado anterior.

Concluir «la GRU no sirve» habría sido ambiguo: no distingue entre una
arquitectura inadecuada y una arquitectura sin datos suficientes. Se comprobó
generando `synthetic_v3`, idéntico salvo por tener el triple de sesiones (216
frente a 72), y entrenando **los dos modelos** sobre él.

| Conjunto | Ventanas de entrenamiento | Baseline | GRU | Diferencia |
| --- | --- | --- | --- | --- |
| `synthetic_v2` | 392 | 0,876 | 0,822 | −0,053 |
| `synthetic_v3` | 1 078 | 0,932 | 0,945 | +0,012 |

El orden se invierte. Con el triple de datos la GRU alcanza y supera al baseline.

Lo más informativo está por clase:

| Clase | GRU con v2 | GRU con v3 |
| --- | --- | --- |
| normal | 0,702 | 0,906 |
| F01 | 0,929 | 0,990 |
| F02 | 0,929 | 0,990 |
| F03 | 0,857 | 0,891 |
| F04 | 1,000 | 0,979 |
| F05 fallo de encendido | 0,518 | 0,911 |

## Corrección de una conclusión anterior

> **`SUPERSEDED 2026-10-12`.** Misma causa que el hallazgo anterior: la corrección se apoya en la
> comparación `v2` frente a `v3`, que cambia volumen y calibración del generador a la vez. Que el
> fallo de encendido sea clasificable con más datos **no queda establecido** por esta vía. Lo que
> sí se conserva sin reservas es el valor del control de suelo de ruido de E5, que no depende de esa
> comparación.
>
> Hay además una razón independiente para mirar esta condición con cuidado, medida después: el
> fallo de encendido es **episódico**, y en una sesión solo una fracción pequeña de las muestras
> etiquetadas altera de verdad la trayectoria —ver `docs/methodology/expresion-efectiva-del-fallo.md`—.
> Una exhaustividad baja en esta clase puede venir de ahí y no del volumen.

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
No se afirma que la GRU sea superior: se afirma que **deja de ser inferior**.

> **`SUPERSEDED 2026-10-12`** la segunda mitad de esa frase. Decía además «y que la desventaja
> observada con `synthetic_v2` se explica por el volumen de datos», y eso **no se sostiene**: la
> comparación cambia volumen y calibración del generador a la vez.

Establecer superioridad exigiría repeticiones con semillas distintas e intervalos
de confianza. No se ha hecho, y por tanto no se afirma.

### Lo que esta comparación no puede aislar, y por qué

Añadido el 12 de octubre de 2026, como limitación que el informe no declaraba.

El bosque recibe **139 descriptores de ventana** y la red, la **secuencia de 120 × 12** en crudo.
Entre los dos recorridos cambian **la representación y el estimador a la vez**, de modo que ninguna
diferencia entre ellos puede atribuirse al contexto temporal: podría venir de la representación, del
estimador o de su interacción. Lo que esta comparación mide es la diferencia entre **dos recorridos
completos**, y así debe enunciarse.

Aislar el efecto del contexto temporal exigiría un diseño factorial que cruzara las dos cosas; no se
propone, porque ampliaría el alcance del trabajo. Lo que sí se aísla, con el estimador fijo, es la
contribución de la **dinámica intraventana**, y para eso está la escalera de ablación de
`docs/diseno-pi1/07-ablacion-representacion.md`.

Hay dos asimetrías más, de procedimiento, que la comparación arrastra y que el protocolo de PI.1
corrige: la **época de la red se elige mirando la misma validación sobre la que se reporta**, y el
bosque no tiene paso de selección equivalente; y **ninguno de los dos calibra**, de modo que la
diferencia de ECE entre ellos —0,1317 frente a 0,1439 en `v2`— no es una diferencia entre
calibradores.

## Decisión pendiente del autor
`synthetic_v3` produce mejores resultados en ambos modelos. Adoptarlo como
conjunto oficial **cambiaría las cifras de E4, E5 y E6**, que habría que
regenerar.

No se toma esa decisión aquí. `synthetic_v2` sigue siendo el conjunto oficial y
`synthetic_v3` queda como análisis de sensibilidad. Los registros de ambos se
conservan por separado.

## Un error corregido durante la fase

> **Nota del 12 de octubre de 2026.** Este error volvió, en una forma más estrecha: el identificador
> del conjunto entró en el nombre, pero el del **experimento y su protocolo** no, de modo que
> reejecutar E6 o E7 con un protocolo revisado habría vuelto a sobrescribir los artefactos
> publicados. Ahora toda ejecución lleva **etiqueta** y los ejecutores **se niegan a escribir** si el
> destino existe (`src/mecanico_ia_exp/experiments/destinos.py`).

Los ejecutores escribían su registro con nombre fijo (`E6_baseline.json`), de modo
que la ejecución sobre `synthetic_v3` **sobrescribió los registros oficiales de
**`synthetic_v2`. Se detectó al comparar, y se corrigió incluyendo el
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
| --- | --- | --- |
| `synthetic_v2` | **50,81 s** | **74** (parada temprana, mejor en **33**) |
| `synthetic_v3` | 134,63 s | 68 (parada temprana, mejor en 27) |

Las cifras de `v2` también estaban sin actualizar tras la regeneración: antes decían 44,5 s y 60
épocas con la mejor en la 19. `CORRECTED 2026-10-12`.

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
| --- | --- |
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