# Propuesta de figuras para los capítulos 5 y 6

**Fecha:** 13 de octubre de 2026 · **Qué es:** la propuesta de qué figuras entran en los capítulos
de resultados y de conclusiones, dónde exactamente, con qué pie y con qué lectura · **Qué NO es:**
una incorporación. **No se ha modificado ni una línea de los dos capítulos**, por instrucción del
encargo · **Qué la precede:** la lectura de los dos capítulos, de la plantilla oficial de la
titulación, de la matriz de impacto, de los informes de E1 a E19, de los siete notebooks y de las
treinta figuras existentes, abriendo una por una las que se proponen

La trazabilidad de cada fichero está en [`../figuras-tfm.md`](../figuras-tfm.md). Aquí está el
criterio.

---

## 0. Tres cosas que la revisión encontró antes de proponer nada

Las tres son anteriores a la cuestión de las figuras y las tres afectan a lo que puede afirmarse
con ellas. Se declaran primero porque dos están **en los capítulos** y la tercera en un entregable.
Ninguna se ha corregido: este documento propone, no aplica.

### 0.1 · `F-7` · El capítulo 6 atribuye hoy los resultados canónicos a un conjunto que no es el suyo

| | |
|---|---|
| **Afirmación actual** | cap. 6, OE2: «**`synthetic_v3`, del que salen E6, E7 y la evaluación final, no es reconstruible** con el generador publicado» |
| **Evidencia disponible** | `experiments/E6_baseline_synthetic_v2.json`, `E7_temporal_synthetic_v2.json` y `E19_evaluacion_final_v3.json` declaran los tres `dataset_id: synthetic_v2`. El manifiesto `configs/manifest_e19.json` congela las huellas de `synthetic_v2`. La validación desde un clon limpio del 13-10-2026 reconstruyó `synthetic_v2` **bit a bit** contra esas cuatro huellas |
| **Motivo de invalidez** | la frase dice que los resultados publicados salen del conjunto no reconstruible, y salen del reconstruible. El origen del error es rastreable: `configs/datos_no_reconstruibles.json` dice, con precisión, «las cifras de E6, E7 y E19 **sobre `synthetic_v3`** no son reproducibles»; al resumirse en `L-25`, y de ahí en `A-4` y en la redacción corregida del paso A, se perdió el complemento «sobre `synthetic_v3`». El sufijo `_v3` de `E19_evaluacion_final_v3.json`, que numera el **tercer intento** y no el conjunto, facilitó la confusión |
| **Redacción corregida propuesta** | «…Dos límites de la reproducibilidad que este objetivo declaraba de forma incompleta: **`synthetic_v3` no es reconstruible** con el generador publicado, porque es anterior a su calibración, y lo que lo hace peligroso es que su ventanado y su reparto sí reproducen, de modo que una reconstrucción ingenua pasaría las pruebas midiendo otras señales. De ese conjunto sale la **comparación de volumen** entre `synthetic_v2` y `synthetic_v3` que el capítulo 5 discute, no las cifras publicadas de diagnóstico ni la evaluación final: esas tres ejecuciones son sobre `synthetic_v2`, cuyas cuatro huellas se reconstruyeron bit a bit desde un clon limpio. Y cuatro pruebas y seis comprobaciones de tipado dependían de dos paquetes que se importaban sin estar declarados…» |
| **Impacto sobre las conclusiones** | **mejora** la posición del trabajo y por eso conviene no dejarlo así: tal como está, el capítulo 6 le dice a un tribunal que las cifras centrales del TFM no son reproducibles por un tercero, cuando sí lo son. El límite real sigue en pie y sigue siendo serio, pero alcanza a la comparación de volumen y al conjunto de evaluación independiente del redactor, no al resultado publicado |

La misma corrección alcanza a `L-25` en `docs/limitations.md` y a la entrada `A-4` de la matriz, que
son de donde la frase llegó al capítulo. **No se ha aplicado nada:** es una propuesta, y el
procedimiento de los seis hallazgos anteriores —paso A propone, paso B aplica tras verificación—
vale igual aquí.

### 0.2 · La figura de calibración del notebook 02 invierte el sentido de lo que mide

`FIG-NB02-04_calibracion.png` se titula «**Los dos prometen más de lo que cumplen**», y su bloque de
lectura dice «los dos modelos caen por debajo de la diagonal: declaran una confianza media superior
a su acierto». El registro dice lo contrario para el bosque:

| Modelo | Confianza media | Acierto | Sesgo registrado |
|---|---|---|---|
| Bosque aleatorio (E6) | 0,738 | 0,878 | **−0,1395** |
| GRU bidireccional (E7) | 0,834 | 0,827 | +0,0070 |

El bosque **acierta más de lo que promete**: está infraconfiado, que es exactamente lo que el
capítulo 5 dice y razona —«un umbral sobre la confianza cruda habría hecho que el agente se
abstuviera de más, y habría parecido prudencia cuando era mala medición»—. La red, en agregado,
está casi centrada; su ECE de 0,1317 procede de errores por tramo que se cancelan, no de un exceso
de confianza global. Lo que sí es cierto, y conviene conservar, es que **ninguno de los dos está
bien calibrado**: el error por tramos es grande en ambos.

La afirmación aparece tres veces en el notebook 02: en el título de la figura, en su bloque «Qué
muestra» y en el punto 5 del apartado de resultados negativos. Está también en el HTML entregado. La
figura queda **bloqueada** para la memoria hasta que se corrija, y la corrección del notebook es una
tarea aparte de la incorporación de figuras, con su propia regeneración de HTML.

El capítulo 5 **no** hereda el error: su Tabla 5.2 y su párrafo son correctos. Por eso la figura de
calibración que se propone para la memoria (`5.6`) no es esta, sino una nueva desde el registro de
E15, que además muestra lo que a la memoria le interesa y la del notebook no tiene: el antes y el
después de calibrar.

### 0.3 · `F-8` · El capítulo 5 nombra mal uno de los dos fallos invisibles en las medias

| | |
|---|---|
| **Afirmación actual** | cap. 5, análisis descriptivo: «dos de los cinco fallos no son visibles en las medias de las señales: **el fallo de encendido y el termostato bloqueado abierto** solo se distinguen de la condición sin fallo por la dispersión o por la evolución temporal, no por el nivel» |
| **Evidencia disponible** | E2, hallazgo 2, medias sobre los instantes con fallo activo: la temperatura del refrigerante con el termostato bloqueado es **69,2 °C frente a 81,4 °C** en la condición sin fallo, la firma más clara de toda la tabla. Los dos fallos que esa tabla deja sin firma en medias son la **sonda lenta** y el **fallo de encendido**: la desviación típica de la sonda cae de 0,250 a 0,033, y los episodios de encendido alteran el 5,7 % de los instantes. E4 lo confirma con la delta de Cliff en `artifacts/tables/E4_separabilidad.csv`: termostato **−0,75 por nivel**; sonda lenta **−1,00 por dispersión** con nivel +0,29; encendido **+0,58 por nivel** |
| **Motivo de invalidez** | el termostato es, de los cinco, el más visible en la media, y la frase lo pone entre los invisibles. El fallo que falta nombrar es la sonda lambda de respuesta lenta. El párrafo mezcla además dos cosas distintas: que un fallo no tenga firma en el nivel, y que el termostato tenga un techo físico por debajo del cual no deja firma de ninguna clase. Lo segundo es cierto y es la frase siguiente del propio párrafo |
| **Redacción corregida propuesta** | «El primero es que dos de los cinco fallos no son visibles en las medias de las señales: la sonda lambda de respuesta lenta y el fallo de encendido. La sonda se distingue por la dispersión y no por el nivel —su oscilación se amortigua casi por completo, de una desviación típica de 0,250 a 0,033—, y el fallo de encendido queda diluido en el agregado porque sus episodios alteran el 5,7 % de los instantes de la sesión. El segundo es que el termostato bloqueado abierto, que sí tiene firma clara en la media de la temperatura del refrigerante, tiene un límite físico de detección: mientras el motor no habría superado por sí mismo la temperatura a la que el fallo lo limita, la señal averiada es idéntica a la sana. En esas ventanas la respuesta correcta del sistema es abstenerse, y no hubo que fabricar el caso.» |
| **Impacto sobre las conclusiones** | **ninguno sobre las cifras**, y por eso conviene corregirlo: no cambia ninguna métrica, ningún resultado y ninguna conclusión. Cambia el nombre de un fallo en una frase descriptiva, y evita que un lector que abra `E4_separabilidad.csv` encuentre lo contrario de lo que el capítulo afirma. Afecta además a `docs/diseno-pi1/09-matriz-conclusiones-afectadas.md`, que revisó esta misma frase y la marcó **válida** |

Es el defecto que la incorporación de figuras habría hecho inevitable de todos modos: la figura 5.3
se coloca justo debajo de esa frase y mide lo contrario de lo que la frase dice.

---

---

## 1. Convención de figura

La plantilla oficial de la titulación no trae estilo de pie de figura; sí trae estilo de tabla de
ilustraciones, de modo que un índice de figuras es admisible dentro de ella. La convención que se
propone es la que el inventario editorial ya fijó para las tablas y la que los capítulos aplican hoy
(`docs/audits/full_memory_review/14_TABLES_FIGURES_INVENTORY.md`): numeración por capítulo, título
descriptivo tras el número, procedencia debajo del elemento y mención en el cuerpo **por su número,
nunca por su posición**.

```
**Figura 5.4. Matrices de confusión del bosque aleatorio y de la red recurrente sobre validación.**

[imagen]

*Fuente: elaboración propia. Experimento: E6 y E7. Conjunto: `synthetic_v2`, partición de
validación, 98 ventanas de 12 sesiones. Protocolo: una ejecución por modelo, semilla 20260901,
reparto por sesión. Artefactos: `artifacts/figures/FIG-E6-01_confusion_baseline.png` y
`FIG-E7-01_confusion_temporal.png`; registros `E6_baseline_synthetic_v2.json` y
`E7_temporal_synthetic_v2.json`.*
```

Esa línea única cubre los siete elementos que el encargo exige —número, título, fuente, experimento,
conjunto, protocolo y referencia al artefacto— sin convertir el pie en documentación técnica, que es
lo que la política de expresión académica pide en su regla 32.

Antes de cada figura, una frase que diga **qué se evalúa**. Después, en prosa continua y no en
epígrafes, cuatro cosas: qué muestra, qué interpretación permite, qué limitaciones tiene y cómo se
relaciona con la pregunta. El formato de tres bloques en negrita de los notebooks **no se traslada**
a la memoria: allí es una convención del cuaderno, aquí sería un cuerpo extraño.

---

## 2. Capítulo 5

Quince figuras, de las que cuatro están condicionadas a que entre antes el texto del que dependen,
de modo que las incondicionales son once.
La columna de prioridad separa lo que sostiene un resultado de lo que ayuda a entenderlo, para que
recortar sea fácil si el capítulo crece demasiado.

### 2.1 · Análisis descriptivo de la muestra

#### Figura 5.1 · Ventanas por clase y partición

| | |
|---|---|
| **Ubicación** | tras el primer párrafo del apartado, el que dice «La muestra sintética consta de 72 sesiones de 600 segundos…» (hoy, línea 13) |
| **Título** | **Figura 5.1. Ventanas por clase y partición de la muestra sintética.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E5, ventanado y reparto. Conjunto: `synthetic_v2`, 72 sesiones de 600 s a 1 Hz. Protocolo: ventana de 120 s con paso de 60 s; el reparto es por sesión, nunca por ventana. Artefactos: `artifacts/figures/FIG-E5-02_particiones.png` y `artifacts/tables/E5_reparto.csv`.* |
| **Qué se evalúa antes** | cómo se reparte la muestra y por qué la clase sin fallo dobla a cada condición de fallo |
| **Qué evidencia respalda** | las cifras del párrafo que la precede: 392 ventanas de entrenamiento, 98 de validación, 14 por condición de fallo y 28 sin fallo. Muestra además, sin decirlo, por qué: las sesiones averiadas aportan sus ventanas anteriores a la entrada del fallo |
| **Limitaciones** | es una descripción del diseño, no un resultado. No dice nada sobre dificultad ni sobre balance de información: dos clases con el mismo número de ventanas pueden ser muy desiguales en lo que se puede aprender de ellas |
| **Prioridad** | núcleo |
| **Estado** | `REGENERAR`. El contenido es correcto; la leyenda se dibuja **encima de la barra de la clase sin fallo**. Se corrige moviendo la leyenda, sin tocar ningún dato |

#### Figura 5.2 · Señal testigo de cada condición

| | |
|---|---|
| **Ubicación** | tras el párrafo «El análisis exploratorio previo al modelado dejó dos hechos…» (hoy, línea 15) |
| **Título** | **Figura 5.2. Señal testigo de cada condición de fallo, comparada con la misma sesión sin fallo.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E4, análisis exploratorio. Conjunto: `synthetic_v1`, sesiones pareadas. Protocolo: misma semilla y mismo régimen de conducción con y sin fallo; antes del instante de entrada las dos series coinciden exactamente, de modo que toda divergencia posterior es la condición. Artefacto: `artifacts/figures/FIG-E4-01_series_normal_vs_fallo.png`.* |
| **Qué se evalúa antes** | qué forma tiene cada fallo en la señal que lo delata, y si esa forma es un cambio de nivel o de otra cosa |
| **Qué evidencia respalda** | el primero de los dos hechos del párrafo: que el fallo de encendido y el termostato no se distinguen por el nivel. En el panel del encendido las dos series son casi indistinguibles a simple vista; en el de la sonda, la averiada es la de **menos** oscilación, no la de distinto nivel |
| **Limitaciones** | es **una sesión por condición**, elegida como testigo, y procede de `synthetic_v1`, que es el conjunto del análisis exploratorio y no el de los modelos. No cuantifica nada: para eso está la 5.3 |
| **Prioridad** | complementaria, y la que más ayuda a un lector que no haya visto nunca telemetría OBD-II |
| **Estado** | `REGENERAR`. La leyenda se superpone al final del subtítulo. Ocupa además una página entera: conviene reducirla a los dos o tres paneles que el texto usa, o aceptarla a página completa |

#### Figura 5.3 · Separabilidad de cada señal por condición

| | |
|---|---|
| **Ubicación** | inmediatamente después de la 5.2 |
| **Título** | **Figura 5.3. Separabilidad de cada señal por condición, en nivel y en dispersión.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E4. Conjunto: `synthetic_v1`, bloques de 60 s. Protocolo: delta de Cliff de cada señal frente a la condición sin fallo, calculada por separado sobre la media del bloque y sobre su desviación; se etiquetan las celdas con efecto grande. Artefactos: `artifacts/figures/FIG-E4-02_separabilidad.png` y `artifacts/tables/E4_separabilidad.csv`.* |
| **Qué se evalúa antes** | si cada fallo deja una firma en el nivel de alguna señal, en su dispersión, o en ninguna de las dos |
| **Qué evidencia respalda** | el mismo hecho que la 5.2, ahora con una medida. Las cinco mejores celdas, una por condición, son: fuga de vacío y deriva de caudalímetro en el ajuste de combustible a corto plazo, las dos por nivel y las dos con 1,00; termostato en la temperatura del refrigerante, por nivel, −0,75; **sonda lenta en la propia sonda, por dispersión, −1,00, con un nivel de solo +0,29**; y fallo de encendido en la sonda, por nivel, +0,58, el efecto grande más débil de los cinco. La vía por la que cada fallo se separa es tan informativa como la magnitud |
| **Limitaciones** | la delta de Cliff ordena, no explica. Un efecto grande en una señal no implica que el modelo la use, y la 5.10 muestra un caso en que no la usa. Es `synthetic_v1`, y con bloques de 60 s, no las ventanas de 120 s con que se entrena. Y la figura **no sostiene** la frase que hoy tiene encima: ver `F-8` |
| **Prioridad** | núcleo |
| **Estado** | `REGENERAR`. El subtítulo se imprime **encima** de los títulos de los dos paneles y los dos textos quedan ilegibles. Se corrige con un margen superior, sin tocar ningún valor |

### 2.2 · PI.1 · Diagnóstico, calibración y atribución

#### Figura 5.4 · Matrices de confusión de los dos modelos

| | |
|---|---|
| **Ubicación** | tras el párrafo «El modelo temporal no supera al tabular…» (hoy, línea 35), que es donde se afirma que todos los errores del bosque van a la condición sin fallo |
| **Título** | **Figura 5.4. Matrices de confusión del bosque aleatorio y de la red recurrente sobre la partición de validación.** |
| **Pie** | el del apartado 1 de este documento |
| **Qué se evalúa antes** | adónde van los errores de cada modelo, que es una pregunta distinta de cuántos son |
| **Qué evidencia respalda** | la afirmación más fuerte del apartado y la que la Tabla 5.1 no puede mostrar: el bosque **no produce diagnósticos cruzados** —sus 12 errores son 5 del termostato y 7 del encendido, y los 12 van a «sin fallo»— mientras la red sí los produce: dos ventanas sin fallo que llama termostato, una que llama encendido, una deriva de caudalímetro que llama fuga de vacío y otra que llama sonda. Para un sistema que va a explicar, esa diferencia pesa más que los 0,05 de F1 |
| **Limitaciones** | una sola ejecución por modelo y una sola semilla; 98 ventanas de 12 sesiones. Las dos matrices se leen por fila y los totales de fila son 14, salvo la de sin fallo, que es 28 |
| **Prioridad** | núcleo |
| **Estado** | `DISPONIBLE`. Las dos figuras existen por separado y se cotejaron celda a celda contra sus tablas. Entrarían como panel doble, lo que exige componerlas en un solo fichero o colocarlas una junto a otra con un único pie |

#### Figura 5.5 · F1 por clase y diferencia entre los dos modelos

| | |
|---|---|
| **Ubicación** | junto a la 5.4, en el mismo párrafo |
| **Título** | **Figura 5.5. F1 por condición de los dos modelos de diagnóstico y diferencia entre ellos.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E6 y E7. Conjunto: `synthetic_v2`, validación. Protocolo: una ejecución por modelo; n es el número de ventanas de la clase en validación. Artefacto: `notebooks/salida/02_comparacion_modelos/FIG-NB02-02_por_clase.png`; registros `E6_baseline_synthetic_v2.json` y `E7_temporal_synthetic_v2.json`.* |
| **Qué se evalúa antes** | si la desventaja agregada de la red se reparte por igual entre las condiciones |
| **Qué evidencia respalda** | que no: la red gana **solo** en el termostato (+0,032) y pierde en las otras cinco, con el máximo en el fallo de encendido (−0,167). Es la base de la frase del capítulo «por clase acierta dos ventanas más en el termostato bloqueado, 11 de 14 frente a 9 de 14» |
| **Limitaciones** | una ejecución por celda, sin repeticiones ni intervalos. Una diferencia de 0,032 en una clase de 14 ventanas es, como mucho, una ventana y media |
| **Prioridad** | complementaria |
| **Estado** | `COPIAR` a `artifacts/figures/` con su fila de procedencia |

#### Figura 5.6 · Calibración antes y después

| | |
|---|---|
| **Ubicación** | tras la Tabla 5.2 y su párrafo (hoy, línea 50) |
| **Título** | **Figura 5.6. Confianza declarada frente a acierto observado, antes y después de calibrar.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E6, con la calibración ajustada en E15. Conjunto: `synthetic_v2`, validación, 98 ventanas. Protocolo: regresión isotónica con validación cruzada de cinco pliegues sobre entrenamiento; error de calibración esperado sobre diez tramos. Artefacto: registro `experiments/E15_suficiencia.json`, bloque `calibration`.* |
| **Qué se evalúa antes** | si la confianza que el modelo declara se corresponde con la frecuencia con que acierta, y en qué dirección falla |
| **Qué evidencia respalda** | las cuatro cifras de la Tabla 5.2, y sobre todo **la dirección**: el punto sin calibrar queda por encima de la diagonal, acierto 0,878 con confianza declarada 0,738. El modelo prometía menos de lo que cumplía. Después de calibrar, 0,886 frente a 0,878. Esa dirección es la que justifica el párrafo siguiente del capítulo: un umbral sobre la confianza cruda habría producido abstenciones que parecerían prudencia |
| **Limitaciones** | un punto por configuración es un resumen: no dice si el error se concentra en los tramos de confianza alta, que es donde más daño haría. La curva de fiabilidad completa exigiría las predicciones por ventana, que el registro de E6 no guarda. El ECE se calcula con diez tramos sobre 98 ventanas y se publica sin incertidumbre |
| **Prioridad** | núcleo |
| **Estado** | `EXPORTAR`. No existe. Se dibuja desde el registro congelado, sin ejecutar nada. **No se propone reutilizar `FIG-NB02-04`,** por lo dicho en el apartado 0.2 |

#### Figura 5.7 · Límite de evidencia del termostato

| | |
|---|---|
| **Ubicación** | tras el párrafo del fallo de encendido (hoy, línea 37), con una referencia cruzada desde el apartado descriptivo, donde el límite físico se enuncia |
| **Título** | **Figura 5.7. Acierto del modelo en cada ventana del termostato bloqueado, frente a la temperatura media del refrigerante.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E6. Conjunto: `synthetic_v2`, las 14 ventanas de validación de la condición F03. Protocolo: cada punto es una ventana; la línea marca el techo de temperatura que el fallo impone, 71 °C, que es un parámetro declarado del generador. Artefacto: `artifacts/figures/FIG-E6-02_limite_evidencia_f03.png`.* |
| **Qué se evalúa antes** | si los errores del modelo en el termostato se concentran donde el fallo no deja firma |
| **Qué evidencia respalda** | que sí: **las cinco ventanas no detectadas están todas por debajo del techo**, entre 43 y 65 °C, y las nueve detectadas están pegadas a él. Mientras el motor no habría superado por sí mismo la temperatura a la que el fallo lo limita, la señal averiada y la sana son la misma, y ninguna arquitectura las separa. Es el resultado negativo mejor explicado del trabajo, y el que da sentido a que la respuesta correcta en esas ventanas sea abstenerse |
| **Limitaciones** | 14 ventanas de dos sesiones. La figura muestra una coincidencia entre dos cosas —estar bajo el techo y no ser detectada— y no prueba que la primera **cause** la segunda; lo que sostiene la causa es que el techo es un parámetro declarado del generador y no una línea ajustada a los datos. Varios puntos se solapan cerca del techo |
| **Prioridad** | núcleo |
| **Estado** | `DISPONIBLE` |

#### Figura 5.8 · Expresión efectiva del fallo *(condicionada a `N-2`)*

| | |
|---|---|
| **Ubicación** | solo si entra `N-2` de la matriz: al final del apartado de PI.1, o en el capítulo 6 entre las limitaciones |
| **Título** | **Figura 5.8. Fracción de cada ventana en la que el fallo deja señal observable, y ventanas que el modelo falla.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E6, fase G del diseño de PI.1. Conjunto: `synthetic_v2`, validación, las 70 ventanas etiquetadas con un fallo. Protocolo: para cada ventana se compara la trayectoria con fallo y la trayectoria sin fallo de la misma semilla, y se cuenta la muestra como alterada si la diferencia supera el 10 % de la desviación de esa señal. Artefacto: `notebooks/salida/06_expresion/FIG-N06-01_expresion_y_aciertos.png`.* |
| **Qué se evalúa antes** | que una ventana lleve la etiqueta de un fallo no garantiza que contenga ninguna huella de él |
| **Qué evidencia respalda** | la fuga de vacío, la deriva y la sonda expresan el fallo en toda su ventana; el termostato deja **cinco ventanas sin ninguna señal**, y el fallo de encendido no expresa por completo ninguna de las catorce. Es la cuantificación de lo que el capítulo llama hoy «límite físico de detección» sin medirlo |
| **Limitaciones** | **y esta es la limitación que obliga a escribir el pie con cuidado.** El panel derecho pone una junto a otra dos cuentas: cinco ventanas sin señal y cinco ventanas falladas, en la misma condición. **No son necesariamente las mismas cinco**, y los registros de E6 no guardan la predicción de cada ventana, de modo que la identidad no está comprobada. El pie debe decirlo. Comprobarlo exigiría reejecutar E6 con la opción por ventana, que existe en el código y no se ha usado, y eso es una ejecución nueva que no está autorizada |
| **Prioridad** | núcleo si `N-2` entra; irrelevante si no |
| **Estado** | `COPIAR`, condicionada |

#### Figura 5.9 · El confusor de volumen y calibración *(condicionada a `A-3`)*

| | |
|---|---|
| **Ubicación** | solo si se aplica `A-3`: junto al párrafo del conjunto tres veces mayor (hoy, dentro de la línea 35) |
| **Título** | **Figura 5.9. Comparación entre los dos conjuntos: entre las dos columnas cambian el volumen y el generador.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E6 y E7 sobre los dos conjuntos. Conjuntos: `synthetic_v2`, 72 sesiones con el generador calibrado contra el manual, y `synthetic_v3`, 216 sesiones con el generador anterior a esa calibración. Protocolo: una ejecución por celda. Artefacto: `notebooks/salida/02_comparacion_modelos/FIG-NB02-05_confusor_volumen.png`.* |
| **Qué se evalúa antes** | por qué la comparación que parecía responder a la pregunta del volumen no la responde |
| **Qué evidencia respalda** | que el orden entre los dos modelos se invierte al pasar de un conjunto al otro, y que entre los dos conjuntos cambian **dos** cosas a la vez. Con dos puntos de medida y dos variables, el experimento no tiene grados de libertad para separarlas |
| **Limitaciones** | es una figura sobre un resultado retirado, y debe presentarse como tal. `synthetic_v3` no es reconstruible con el generador publicado, de modo que esta comparación no puede rehacerla un tercero |
| **Prioridad** | complementaria, y **de riesgo si se incorpora sin `A-3`**: el párrafo que hoy tiene encima atribuye la desventaja del modelo temporal al volumen de datos, que es justo lo que la figura desmiente. Una figura que contradice al párrafo que la introduce es peor que ninguna figura |
| **Estado** | `COPIAR`, condicionada |

#### Figura 5.10 · Dónde mira el modelo

| | |
|---|---|
| **Ubicación** | tras el párrafo de la atribución por valores de Shapley (hoy, línea 52) |
| **Título** | **Figura 5.10. Peso explicativo de cada señal por condición, y señales que el generador declara para cada fallo.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E9, atribución. Conjunto: `synthetic_v2`, 18 casos de validación. Protocolo: valores de Shapley por permutación, con un fondo de cien ventanas sin fallo de entrenamiento; el punto marca las señales que la ficha del fallo declara. Artefactos: `notebooks/salida/04_explicabilidad/FIG-NB04-01_mapa_atribucion.png` y `artifacts/tables/E9_atribuciones_synthetic_v2.csv`.* |
| **Qué se evalúa antes** | si las señales en que el modelo se apoya son las que el mecanismo del vehículo justifica |
| **Qué evidencia respalda** | las tres lecturas del párrafo, y una de ellas de un vistazo: en la deriva del caudalímetro la columna del caudal medido está **vacía** y el peso está en las dos correcciones de combustible. El modelo detecta la deriva por cómo la centralita la compensa, no por el caudal. Es la observación que impide al agente afirmar «el caudalímetro deriva porque el caudal es bajo», y es la que une este apartado con las plantillas de afirmación del verificador |
| **Limitaciones** | la atribución es fiel al modelo, no al vehículo: dice en qué se apoya el bosque, no qué causa el fallo. 18 casos. Y la ablación `A1` mostró que esta atribución **no interviene** en la política de abstención: su contribución está en la trazabilidad, no en la decisión |
| **Prioridad** | núcleo. Es la única figura de SHAP del trabajo y el encargo la pide expresamente |
| **Estado** | `COPIAR` |

### 2.3 · PI.2 · Recuperación y trazabilidad

#### Figura 5.11 · Recuperación por estrategia

| | |
|---|---|
| **Ubicación** | tras la Tabla 5.3 y su párrafo (hoy, línea 69) |
| **Título** | **Figura 5.11. Recuperación del procedimiento relevante del manual según la estrategia de consulta.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E12, reejecución canónica del 13 de septiembre de 2026. Conjunto: corpus documental del vehículo de referencia; seis casos anotados, cinco puntuados, con la consulta en inglés y el mapa de códigos de avería congelado. Protocolo: diez primeros resultados; el sexto caso, con la evidencia retirada del índice, se evalúa y no entra en las métricas porque no tiene fichero relevante. Artefactos: `artifacts/tables/E12_retrieval_por_estrategia.csv` y registro `experiments/E12_retrieval.json`.* |
| **Qué se evalúa antes** | si la similitud semántica basta para encontrar el procedimiento de taller que corresponde a un diagnóstico |
| **Qué evidencia respalda** | que no basta y que la diferencia no es de grado: la recuperación semántica pura encuentra el procedimiento en **cero** de los cinco casos, y guiada por el código de avería lo encuentra en los cinco. Entre una consulta en lenguaje natural y un procedimiento de taller la similitud es baja, y lo que los une es un identificador exacto |
| **Limitaciones** | cinco casos puntuados. Y la salvedad que el capítulo ya declara y que el pie debe repetir: la estrategia guiada acota la búsqueda con los códigos que documentan la condición **anotada**, información que el sistema no tiene antes de diagnosticar. Su ventaja es una cota asistida por esa anotación, no una capacidad de recuperación comparable con las demás |
| **Prioridad** | núcleo. PI.2 es hoy la única subpregunta sin ninguna figura |
| **Estado** | `EXPORTAR`. Se dibuja desde la tabla congelada |

### 2.4 · PI.3 y PI.4 · Suficiencia, abstención y distractores

#### Figura 5.12 · Documentos aplicables frente a cobertura

| | |
|---|---|
| **Ubicación** | tras la Tabla 5.5 y el párrafo de las cinco ventanas (hoy, línea 119) |
| **Título** | **Figura 5.12. Documentos aplicables recuperados y cobertura de afirmaciones alcanzada, por condición de evidencia.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E15, verificador en su tercera versión. Conjunto: `synthetic_v2`, los 17 casos anotados sobre 5 ventanas de validación. Protocolo: modo oracular; el color distingue la decisión tomada. Artefactos: `notebooks/salida/05_suficiencia/FIG-N05-01_aplicables_vs_cobertura.png` y `artifacts/tables/E15_suficiencia.csv`.* |
| **Qué se evalúa antes** | si tener documentación aplicable delante equivale a tener soporte para lo que se afirma |
| **Qué evidencia respalda** | la distinción que vertebra el trabajo entero, y aquí se ve sin leer una cifra: en la condición parcial y en la del distractor el sistema recibe entre **tres y siete** fragmentos aplicables, y la cobertura de afirmaciones es **0,00** en todos ellos. La columna de evidencia retirada tiene cero fragmentos y cero cobertura, y por eso es la condición que no pone a prueba nada. La informativa es la parcial. Es la misma frontera que la ablación `A3` mide por el otro lado |
| **Limitaciones** | 17 ejecuciones sobre 5 ventanas: no son 17 observaciones independientes. La cobertura 0,00 es una propiedad de las comprobaciones deterministas del verificador, no un juicio externo sobre lo que cada fragmento sostiene; medir eso exigiría anotar las afirmaciones admisibles, y el conjunto no las tiene |
| **Prioridad** | núcleo. Si el capítulo 5 admitiera una sola figura, sería esta |
| **Estado** | `REGENERAR`, por un defecto encontrado al cotejarla con su tabla. La figura dibuja **cuatro** condiciones —`FULL`, `PARTIAL`, `ABSENT`, `DISTRACTOR`— y el conjunto tiene **cinco**: `DISTRACTOR_NO_FILTER` queda fuera por una comparación exacta de nombre, de modo que la figura muestra 14 de los 17 casos mientras su pie declara los diecisiete. Ninguna conclusión cambia —los tres omitidos tienen 3, 4 y 3 documentos aplicables, cobertura 0,00 y abstención—, pero el pie dice más de lo que la figura contiene, y la condición omitida es justamente la única en la que entran fragmentos de otro motor. Se corrige añadiendo la quinta columna. Segundo reparo, de accesibilidad: las dos decisiones se distinguen **solo por color**, verde y rojizo; conviene darles además forma distinta antes de imprimir |

#### Figura 5.13 · Efecto de retirar o degradar cada componente

| | |
|---|---|
| **Ubicación** | tras la Tabla 5.8 (hoy, línea 189) |
| **Título** | **Figura 5.13. Falsa confianza y abstención innecesaria de la configuración canónica y de las cuatro ablaciones.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E18, ablaciones pre-registradas y ejecutadas el 1 de octubre de 2026. Conjunto: `synthetic_v2`, los mismos 17 casos. Protocolo: cada ablación cambia una pieza y deja el resto idéntico; ninguna redacta. La falsa confianza se cuenta sobre nueve ejecuciones de tres ventanas y la abstención innecesaria sobre cinco ejecuciones de cinco ventanas. Artefactos: registros `experiments/E18_ablacion_A1.json` a `A4.json`.* |
| **Qué se evalúa antes** | cuál de las piezas del sistema sostiene el resultado, y cuál es prescindible |
| **Qué evidencia respalda** | el contraste más instructivo del capítulo: con una puerta de confianza sola, la falsa confianza pasa de 0 de 9 a **9 de 9**, y sustituir la atribución por una desviación tipificada no cambia **ninguna** decisión. Las dos barras extremas dicen lo mismo desde lados opuestos: lo que sostiene el comportamiento es el criterio de suficiencia, no el método de atribución |
| **Limitaciones** | tres ventanas y cinco ventanas, sobre el conjunto con el que el criterio fue ajustado. La ablación `A2` quedó **inconclusa** —la ruta léxica no recupera nada con una consulta en prosa, y la causa no es la ablación sino la consulta—, y la figura debe marcarla como tal y no como un cero medido |
| **Prioridad** | núcleo. El encargo pide ablaciones y falsa confianza, y esta figura cubre las dos |
| **Estado** | `EXPORTAR`. Se dibuja desde los cuatro registros |

### 2.5 · Evaluación final *(condicionadas a `N-1`)*

El capítulo no tiene todavía apartado de E19. Mientras no lo tenga, estas dos figuras no tienen
dónde ir; escribir ese apartado es la tarea que la matriz numera `N-1` y que sigue pendiente de
decisión.

#### Figura 5.14 · Las tres cifras de la evaluación final

| | |
|---|---|
| **Título** | **Figura 5.14. Falsa confianza, abstención innecesaria y cobertura en la evaluación final, con sus denominadores.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E19, evaluación final ejecutada el 12 de octubre de 2026 en el tercero de tres intentos. Conjunto: `synthetic_v2`, **partición de prueba**. Protocolo: política de suficiencia v2.2, conjunto anotado sellado antes de abrir la partición; estrato operativo. Artefactos: `notebooks/salida/03_analisis_e19/FIG-NB03-01_primario.png` y `artifacts/tables/E19_evaluacion_final_v3.csv`.* |
| **Qué evidencia respalda** | 0 de 14, 2 de 8 y 6 de 10, cada una con su denominador a la vista y con el número de ventanas y de sesiones debajo |
| **Limitaciones** | la figura lo dice en su propio pie, y conviene conservarlo: **un cero sobre catorce no es riesgo cero**. Con esos denominadores el intervalo de incertidumbre es amplio y no se publica. Los tres paneles tienen escalas verticales distintas y deben leerse por su fracción, no por la altura relativa. Y la salvedad de `L-26`: siete de las 35 salidas de esta evaluación contienen una cifra que el verificador no produjo, sin que **ninguna de las dos tasas cambie**, porque las produce el verificador determinista y no el redactor |
| **Estado** | `COPIAR`, condicionada a `N-1` |

#### Figura 5.15 · Las 22 ejecuciones, caso a caso

| | |
|---|---|
| **Título** | **Figura 5.15. Decisión del sistema en cada una de las 22 ejecuciones del estrato operativo.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E19. Conjunto: `synthetic_v2`, partición de prueba. Protocolo: cada punto es una ejecución y los dos puntos de una fila son sesiones distintas del mismo caso anotado. Artefacto: `notebooks/salida/03_analisis_e19/FIG-NB03-02_decisiones.png`.* |
| **Qué evidencia respalda** | que las dos abstenciones innecesarias son `C01` y `C04` —las mismas dos condiciones que fallaban en validación, y por las mismas causas— y que la casilla de la falsa confianza está vacía |
| **Limitaciones** | la leyenda incluye una categoría que **no aparece** en la figura, la de falsa confianza, y eso es deliberado: muestra que el error existe como categoría y no se observó. Conviene conservarlo y no retirarlo por limpieza |
| **Estado** | `COPIAR`, condicionada a `N-1` |

---

## 3. Capítulo 6

Tres figuras, ninguna repetida del capítulo 5. El criterio del encargo es que solo entren figuras de
síntesis, y la tentación que hay que resistir es repetir aquí la 5.12 o la 5.14 porque son buenas.

#### Figura 6.1 · Objetivos, evidencia y estado

| | |
|---|---|
| **Ubicación** | tras el párrafo del objetivo general (hoy, línea 27), antes de las limitaciones |
| **Título** | **Figura 6.1. Objetivos específicos, experimentos que los sostienen y estado de cumplimiento.** |
| **Pie** | *Fuente: elaboración propia a partir del índice de experimentos y de este capítulo. Sin conjunto de datos: es un esquema documental. Artefactos: `docs/experiment-index.md` y los informes de fase citados en cada celda.* |
| **Qué se evalúa antes** | qué sostiene cada objetivo y hasta dónde |
| **Qué evidencia respalda** | la cadena que el capítulo recorre en prosa: cada objetivo específico, los experimentos que lo miden, la métrica y el estado —cumplido, cumplido parcialmente, pendiente—. Un tribunal que la lea sabe en un golpe de vista qué sostiene qué |
| **Limitaciones** | **no es una medición**: es un resumen del propio capítulo, y una figura así puede dar una impresión de completitud que la evidencia no tiene. Las celdas de estado deben decir «parcialmente» donde el texto dice parcialmente, y no redondear hacia arriba |
| **Prioridad** | núcleo. Es la figura que el encargo pide en primer lugar para este capítulo |
| **Estado** | `EXPORTAR`. No existe |

#### Figura 6.2 · Falsa confianza frente a abstención innecesaria

| | |
|---|---|
| **Ubicación** | en el apartado de limitaciones, junto al párrafo del número de casos anotados (hoy, línea 39), o al cierre de OE5 |
| **Título** | **Figura 6.2. Los dos errores del sistema y los de las dos políticas triviales, sobre los mismos casos.** |
| **Pie** | *Fuente: elaboración propia. Experimento: E15. Conjunto: `synthetic_v2`, validación, 17 ejecuciones sobre 5 ventanas. Protocolo: las dos políticas de referencia se definieron el 4 de septiembre de 2026, después de medir las tres versiones del criterio sobre estos mismos casos, y se calculan sobre ellos. Artefacto: registro `experiments/E15_suficiencia.json`; equivale a la Tabla 5.6.* |
| **Qué se evalúa antes** | qué precio tiene la falsa confianza nula |
| **Qué evidencia respalda** | el compromiso, que en prosa cuesta tres frases y aquí son tres puntos: abstenerse siempre da falsa confianza cero y no explica nada; explicar siempre que el modelo confía explica todo y falla las nueve; el sistema conserva el cero de la primera y la cobertura de la segunda sobre los casos con evidencia completa. Cada política trivial iguala al sistema en un error y lo empeora en el otro |
| **Limitaciones** | tres y cinco ventanas independientes; ningún intervalo acotaría lo que el diseño pretende afirmar, y el pie debe decirlo. Las políticas de referencia se definieron **después** de ver los resultados del criterio, y eso también debe estar en el pie. Si se añade el punto de E19, debe quedar marcado como de **otra partición** y no unido por una línea a los de validación |
| **Prioridad** | núcleo |
| **Estado** | `EXPORTAR`. No existe |

#### Figura 6.3 · Recorrido experimental

| | |
|---|---|
| **Ubicación** | al principio del capítulo, antes del recorrido por los objetivos |
| **Título** | **Figura 6.3. Recorrido experimental, del dato OBD-II a la decisión de explicar o abstenerse.** |
| **Pie** | *Fuente: elaboración propia. Sin conjunto de datos: es la arquitectura, dibujada desde su descripción. Las etiquetas de la derecha indican qué experimentos cubren cada etapa. Artefacto: `notebooks/salida/00_introduccion/FIG-NB00-01_recorrido.png`.* |
| **Qué evidencia respalda** | ninguna: es ilustrativa, y su pie debe decirlo con esa palabra. Lo que aporta es que las ocho etapas y los experimentos que las miden queden a la vista cuando se afirma que la separación entre observar, inferir, recuperar, verificar y decidir es lo que el trabajo sostiene |
| **Limitaciones** | dibuja el diseño, no su comportamiento. Que las etapas estén separadas en el esquema no implica que la separación produzca el resultado: eso es justamente lo que las ablaciones **no** midieron |
| **Prioridad** | complementaria. Y una observación de sitio: por contenido pertenece al capítulo 4, donde se describe el método. Si el autor prefiere llevarla allí, el capítulo 6 se queda con dos figuras y no pierde nada |
| **Estado** | `COPIAR` |

---

## 4. Lo que hay que hacer antes de incorporar nada

| Qué | Cuántas | Qué supone |
|---|---|---|
| **Regenerar** por defecto de composición | 3 (`5.1`, `5.2`, `5.3`) | mover una leyenda y añadir un margen. No cambia ningún valor; las figuras se reescriben ejecutando de nuevo el generador de figuras de E4 y E5, que es determinista |
| **Regenerar** por cobertura incompleta | 1 (`5.12`) | añadir la quinta condición que la figura omite. Se dibuja desde la misma tabla congelada |
| **Exportar** desde registros congelados | 5 (`5.6`, `5.11`, `5.13`, `6.1`, `6.2`) | dibujar desde ficheros que ya existen. **Ningún experimento nuevo**, ninguna reapertura de conjunto |
| **Copiar** a `artifacts/figures/` | 7 | `notebooks/salida/` está excluido del control de versiones. Una figura de la memoria que viva ahí no se entrega. Cada copia añade su fila a la tabla de procedencia de `artifacts/README.md` |
| **Componer** panel doble | 1 (`5.4`) | dos ficheros, un pie |
| **Corregir** antes de poder usarse | 1 | el notebook 02 y su HTML, por el apartado 0.2. No entra en la memoria en ningún caso |

Sobre el formato: las figuras de los notebooks se exportan ya en PNG y en SVG; las de E4, E5, E6 y
E7 solo en PNG, a 300 puntos por pulgada. Para el entregable en DOCX el PNG a esa resolución es
suficiente y es lo que la plantilla admite sin fricción; conviene, de todos modos, añadir la salida
en SVG al generador de figuras de los experimentos cuando se regeneren las tres primeras, porque no
cuesta nada y deja la puerta abierta a una versión vectorial.

Y una consecuencia de procedimiento que conviene decir ahora: **no existe hoy ninguna cadena que
convierta los capítulos en DOCX.** Los capítulos son Markdown, el entregable es un documento de
Word, y en el repositorio no hay conversor ni está instalado ninguno. Incorporar figuras a los
ficheros Markdown deja la memoria lista para esa conversión, pero no la hace; decidir cómo se monta
el documento final —a mano sobre la plantilla, o con una herramienta— es una decisión aparte, y es
donde se aplican la numeración automática, el índice de figuras y las referencias cruzadas que el
encargo pide en su apartado 10.

## 5. Lo que no se propone, y por qué

| Qué | Por qué no |
|---|---|
| `FIG-NB02-04_calibracion.png` | invierte el sentido del sesgo medido. Apartado 0.2 |
| `FIG-E4-03`, `FIG-E4-04`, `FIG-E4-05`, `FIG-E4-06` | describen la muestra con más detalle del que el capítulo 5 usa. Su sitio, si alguno, es el capítulo 4 o un anexo |
| `FIG-E5-01_estudio_ventana` y `FIG-NB01-05` | el estudio de ventana es del capítulo 4, donde la Tabla 4.3 ya lo recoge |
| `FIG-E7-02_entrenamiento` | la curva de entrenamiento de la red documenta la ejecución, no un resultado del trabajo |
| `FIG-NB01-01` a `FIG-NB01-04` | se solapan con las figuras de E4 ya propuestas |
| `FIG-NB03-03_abstenciones` | desglosa los motivos de abstención de E19; entraría solo si el apartado de `N-1` lo pide, y entonces como tercera figura de ese apartado |
| `FIG-NB04-02_dispersion` | complementa a la 5.10 sin añadir una lectura que el capítulo necesite |
| Cualquier figura de P1, del conjunto de evaluación independiente o de la contribución metodológica | son `N-3`, `N-5` y `N-4` de la matriz: contenido que el capítulo todavía no tiene. Las figuras llegan después del texto, no antes |

## 6. Qué decide el autor

1. **Si se corrigen `F-7` y `F-8`** y en qué orden respecto de lo demás. Son lo único de este
   documento que toca afirmaciones ya escritas en los capítulos, y las dos son correcciones de
   hecho, no de interpretación: ninguna mueve una cifra.
2. **Cuántas figuras** entran en el capítulo 5: las once incondicionales, o solo las siete de
   prioridad núcleo. El capítulo recomienda de 5 a 15 páginas y hoy tiene 268 líneas de prosa densa.
3. **Si entran las cuatro condicionadas**, que dependen de `N-1`, `N-2` y `A-3`. Ninguna de ellas
   debe entrar antes que el texto del que depende.
4. **Dónde va la 6.3**: capítulo 6 o capítulo 4.
5. **Si se añade un índice de figuras**: la plantilla trae el estilo que lo permite, pero su propio
   índice de ejemplo no lo incluye.

Lo que este documento no hace, por instrucción: no modifica los capítulos, no genera ninguna figura,
no reejecuta ningún experimento y no abre ningún conjunto.
