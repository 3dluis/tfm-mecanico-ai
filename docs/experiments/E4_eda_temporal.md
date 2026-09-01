# E4 — Análisis exploratorio temporal

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
Datos: `synthetic_v1` (21 600 muestras, 36 sesiones, 6 condiciones)

## Objetivo

Caracterizar las señales como series temporales y decidir, con evidencia, qué es
utilizable como base de una observación.

## Método

La separabilidad de cada señal frente a la condición normal se mide con el
**delta de Cliff**, calculado sobre bloques consecutivos de 60 s que no cruzan
sesiones. Se eligió frente a una diferencia de medias estandarizada porque no
supone normalidad ni varianzas iguales, y aquí no se cumple ninguna de las dos:
los ajustes de combustible bajo fallo son marcadamente asimétricos.

Se mide **por separado sobre el nivel y sobre la dispersión** del bloque. Es
consecuencia directa del hallazgo de E2: dos condiciones no aparecen en las
medias. Un análisis que solo mirase el nivel las declararía indetectables siendo
una de ellas perfectamente separable.

El ventanado de 60 s es instrumental para poder medir dispersión, que sobre una
muestra suelta no está definida. **El ventanado definitivo se decide en E5.**

## Separabilidad medida

Efecto máximo de cada señal, sobre cualquier condición:

| Señal | delta máx. | Condición | Vía | Veredicto |
|---|---|---|---|---|
| oxygen_sensor | 1,00 | F04 | dispersión | separa |
| stft_bank1 | 1,00 | F01 | nivel | separa |
| ltft_bank1 | 1,00 | F01 | nivel | separa |
| coolant_temperature | 0,75 | F03 | nivel | separa |
| intake_air_temperature | 0,34 | F03 | nivel | separa |
| map | 0,16 | F01 | nivel | sin aporte univariante |
| maf | 0,13 | F02 | nivel | sin aporte univariante |
| ignition_timing | 0,11 | F01 | nivel | sin aporte univariante |
| engine_load | 0,10 | F05 | dispersión | sin aporte univariante |
| rpm | 0,10 | F02 | dispersión | sin aporte univariante |
| vehicle_speed | 0,10 | F01 | nivel | sin aporte univariante |
| throttle_position | 0,06 | F03 | nivel | sin aporte univariante |

Mejor señal de cada condición:

| Condición | Mejor señal | delta | Vía |
|---|---|---|---|
| F01 fuga de vacío | stft_bank1 | 1,00 | nivel |
| F02 deriva de caudalímetro | stft_bank1 | 1,00 | nivel |
| F03 termostato bloqueado | coolant_temperature | 0,75 | nivel |
| F04 sonda lenta | oxygen_sensor | 1,00 | dispersión |
| F05 fallo de encendido | oxygen_sensor | 0,58 | nivel |

## Hallazgo 1 — la deriva del caudalímetro no se ve en el caudalímetro

La señal que mejor separa una deriva del caudalímetro **no es el caudal de aire**
(delta 0,13, indistinguible del ruido) sino el ajuste de combustible a corto
plazo (delta 1,00).

La razón es que el caudal depende del producto régimen × carga, que varía en un
orden de magnitud a lo largo de una sesión urbana. Una reducción multiplicativa
del 18 % queda sepultada bajo esa variación. En cambio la centralita compensa el
déficit, y esa compensación sí es visible porque los ajustes oscilan en torno a
cero en condiciones normales.

**Consecuencia para el modelo de evidencia (E16).** La evidencia observacional de
un fallo puede residir en una señal distinta de la averiada. Una explicación que
dijese «el caudalímetro está derivado porque el caudal es bajo» sería falsa aquí:
el caudal no es bajo de forma detectable. La afirmación sostenible es «los ajustes
de combustible están desplazados de forma compatible con una subestimación del
aire admitido», que es una afirmación más débil y más honesta.

## Hallazgo 2 — la ficha de un fallo no predice qué señal lo detecta

La ficha de F05 declara `affected_signals = (rpm, engine_load, stft_bank1,
oxygen_sensor)`. En bloques de 60 s, el régimen alcanza delta 0,10 y la señal más
útil resulta ser la sonda lambda, con 0,58.

La ficha no miente --E2 comprobó que el fallo altera esas señales-- pero
«alterada» y «detectable en una ventana de 60 s» son cosas distintas. Los
episodios duran de 1 a 3 s y ocupan el 5,7 % de la sesión: promediados en 60 s,
casi desaparecen.

**Consecuencia para E5.** Los descriptores por ventana necesitan extremos y
conteos de eventos, no solo medias y desviaciones. Y **la longitud de ventana no
es neutral**: 60 s puede ser demasiado para una condición episódica. La elección
en E5 debe justificarse por condición, no en agregado.

## Hallazgo 3 — siete señales sin aporte univariante, y ninguna se descarta

Solo cinco de las doce señales separan alguna condición por sí solas. Las otras
siete se quedan.

No es una concesión: E2 midió que el caudal de aire tiene correlación marginal de
−0,21 con el régimen en autovía y de 1,00 con el producto régimen × carga. Una
señal puede ser determinante en combinación y no aportar nada en solitario.
Descartar por irrelevancia marginal eliminaría precisamente el contexto que
permite decir que un caudal es bajo **para ese régimen y esa carga**.

Lo que sí queda establecido es qué señales pueden sostener una observación
univariante en una explicación, que son cinco. Las demás pueden aparecer como
contexto, no como evidencia por sí mismas.

## Ausencias y equilibrio

Ausencias: **0,00 en todas las columnas**, por construcción. Se mide y se declara
porque los datos reales tendrán huecos --tramas perdidas, sensores que no
responden-- y un pipeline que nunca los ha visto fallará al encontrarlos. Es un
requisito para E3.

Clases: seis sesiones por condición, equilibrio perfecto. Regímenes: urbano 12,
autovía 12, ralentí 6, calentamiento 6, por el reparto cíclico de seis sesiones
entre cuatro regímenes. Afecta a la comparación entre regímenes, no a las
métricas de clasificación.

## Figuras

Todas en `figures/`, 300 ppp, con su tabla correspondiente en `tables/`.

| Figura | Pregunta que responde |
|---|---|
| FIG-E4-01 | ¿Se distingue una sesión con fallo mirando la señal testigo? |
| FIG-E4-02 | ¿Qué señal separa cada condición, y en nivel o en dispersión? |
| FIG-E4-03 | ¿Qué señales aportan información redundante entre sí? |
| FIG-E4-04 | ¿Cuánto se solapan las distribuciones normal y con fallo? |
| FIG-E4-05 | ¿La mariposa se adelanta al régimen? |
| FIG-E4-06 | ¿Está equilibrado el conjunto? |

**FIG-E4-01 se rehízo.** La primera versión comparaba una sesión normal con una
sesión con fallo tomadas del conjunto, que tienen semillas distintas: buena parte
de la diferencia visible era la forma de conducir, no la condición. La versión
publicada genera las dos series con la misma semilla y el mismo régimen, de modo
que antes de la marca de entrada coinciden exactamente y toda divergencia
posterior es atribuible al fallo.

La paleta se validó antes de usarla: banda de luminosidad, suelo de croma,
separación bajo daltonismo (peor pareja adyacente ΔE 9,1 en protanopia) y suelo
de visión normal (19,6). Tres ranuras quedan por debajo de 3:1 de contraste
contra la superficie, lo que obliga a etiquetas visibles y a que exista la tabla:
ambas cosas se cumplen.

## Tests

`tests/test_exploration.py` (19) y `tests/test_visualization.py` (9). Lo relevante:

- el delta de Cliff se contrasta contra su definición literal, cuadrática, para
  cinco muestras aleatorias: la versión rápida por ordenación debe coincidir
  hasta 1e-12;
- casos límite: muestra consigo misma, sin solape, todo empates, muestra vacía;
- la correlación cruzada localiza un desfase conocido, y su convención de signo
  queda declarada;
- los bloques no cruzan sesiones;
- la sonda lenta separa por dispersión y no por nivel --el hallazgo de E2,
  convertido en test;
- cada figura declara en su docstring la pregunta que responde.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `ruff format --check` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 29 ficheros |
| `pytest` | 75 casos en verde |

## Qué queda abierto

La longitud de ventana definitiva (E5), que este análisis deja como decisión con
evidencia en contra de un valor único: 60 s sirve para cuatro condiciones y
diluye la quinta.

## Siguiente

E5 — preprocesamiento, ventanado y particionado sin fuga temporal.
