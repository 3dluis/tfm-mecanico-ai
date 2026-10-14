# Anexos: selección, justificación y verificación de límites

**Fecha:** 13 de octubre de 2026 · **Qué es:** por qué los anexos son estos tres y no otros, qué
contiene cada uno, qué figura y qué tabla usa, de dónde sale cada artefacto y si el conjunto cabe
dentro de los límites de la plantilla · **Estado:** los tres están **escritos** en
`docs/memoria/anexos.md`, a la espera de la revisión final del documento completo

## 1. Índice propuesto

| | Anexo | Apartados | Figuras | Tablas |
|---|---|---|---|---|
| **A** | Arquitectura y datos experimentales | A.1 arquitectura por etapas · A.2 las doce señales · A.3 las cinco condiciones · A.4 la calibración contra el manual · A.5 los tres conjuntos y su reconstructibilidad · A.6 la señal testigo | A.1 | 5 |
| **B** | Evidencia experimental complementaria | B.1 estatuto de cada resultado · B.2 rendimiento por condición · B.3 dónde se apoya el modelo · B.4 el barrido del umbral · B.5 las cinco aperturas del conjunto de prueba | B.1 | 4 |
| **C** | Reproducibilidad | C.1 qué hace falta · C.2 las cinco órdenes · C.3 los notebooks · C.4 los guiones de verificación · C.5 lo que no se puede reproducir | — | 5 |

## 2. Por qué estos tres

El criterio es el mismo para los seis candidatos: un anexo se justifica cuando el material **existe y
está verificado**, el cuerpo **lo necesita pero no lo soporta** —por extensión o por nivel de
detalle—, y un lector que no lo abra **sigue entendiendo el capítulo**. Si falla la primera, no es
material; si falla la segunda, su sitio es el cuerpo; y si falla la tercera, el capítulo está
incompleto y el anexo lo estaría tapando.

### Anexo A · Arquitectura y datos experimentales

| | |
|---|---|
| **Por qué es necesario** | el capítulo 5 afirma cosas sobre lo que cada fallo deja ver y sobre lo que no, y sobre qué conjunto sostiene qué cifra. Un lector no puede juzgar ninguna de las dos sin la ficha del instrumento. Es, además, la respuesta a la primera pregunta que un tribunal hace ante datos sintéticos: ¿qué hay exactamente dentro? |
| **Qué aporta** | la trazabilidad del dato hasta su fuente documental. Cada constante del generador lleva el fichero del manual del que sale y la cita literal que la respalda, de modo que «sintético» deja de significar «inventado» y pasa a significar «parametrizado contra una fuente» |
| **Qué contiene** | las ocho etapas con el experimento que mide cada una; las doce señales con unidad y rango físico; las cinco condiciones con señales declaradas, patrón temporal y observación esperada; la tabla de calibración con las citas del manual; la tabla de los tres conjuntos con su reconstructibilidad medida; y la figura de la señal testigo |
| **Qué capítulo complementa** | capítulo 4 —población y muestra, instrumentos— y el análisis descriptivo del capítulo 5 |
| **Qué evidencia utiliza** | `configs/calibracion_mazda3_bk.yaml`, `src/mecanico_ia_exp/obd/signals.py` y `faults.py`, `configs/datos_no_reconstruibles.json` y la medición del 13-10-2026 |
| **Extensión** | ≈ 1 500 palabras, 4 páginas |

### Anexo B · Evidencia experimental complementaria

| | |
|---|---|
| **Por qué es necesario** | el capítulo da los agregados y cita el detalle en prosa. Quien quiera comprobar la frase «la red gana solo en el termostato» necesita la tabla por condición; quien quiera discutir el umbral necesita saber de dónde salió; y quien quiera saber si el conjunto de prueba sigue siendo una prueba necesita las cinco aperturas con su nivel de exposición |
| **Qué aporta** | sobre todo, el **estatuto de cada resultado**. El trabajo acumula resultados canónicos, negativos, afectados por contaminación, no canónicos, exploratorios y pendientes, y confundirlos es el error más fácil de cometer al leerlo. La tabla B.1 fija cuál es cuál, y es lo que impide usar un resultado contaminado como evidencia de generalización |
| **Qué contiene** | la tabla de estatutos; la figura y la tabla del F1 por condición; el resumen de atribución; el barrido del umbral con su enmienda fechada; y los cinco niveles de apertura del conjunto de prueba con lo que consume cada uno |
| **Qué capítulo complementa** | capítulo 5, PI.1 y contribución de cada componente; y el apartado de limitaciones del capítulo 6 |
| **Qué evidencia utiliza** | `artifacts/tables/E6_baseline_por_clase_synthetic_v2.csv`, `E7_temporal_por_clase_synthetic_v2.csv`, `E9_resumen_synthetic_v2.csv`, `E15b_barrido_umbral.csv`, `docs/methodology/registro-aperturas-test.md` y `docs/experiment-index.md` |
| **Extensión** | ≈ 1 300 palabras, 4 páginas |

### Anexo C · Reproducibilidad

| | |
|---|---|
| **Por qué es necesario** | es la parte verificable del trabajo. Convierte «los resultados son reproducibles» en una afirmación comprobable en lugar de una promesa, y es donde quedan declarados en un solo sitio los límites de reproducibilidad que el capítulo 6 menciona de pasada |
| **Qué aporta** | al jurado, una vía de entrada de cinco órdenes y una vía de lectura sin instalar nada, que son las dos cosas que el encargo pide. Al trabajo, la declaración explícita de qué no se puede reproducir y por qué |
| **Qué contiene** | repositorio y commit de referencia; entorno; las cinco órdenes, con la que comprueba las huellas; los siete notebooks con su modalidad y sus versiones HTML; los seis guiones de verificación; y la tabla de lo no reproducible |
| **Qué capítulo complementa** | capítulo 6, objetivo específico 2 |
| **Qué evidencia utiliza** | `docs/reproducir-desde-cero.md`, validado desde un clon limpio el 13-10-2026 con todos los pasos en verde |
| **Extensión** | ≈ 1 200 palabras, 3 páginas |

## 3. Por qué los otros tres no

| Candidato | Por qué no | Dónde queda su contenido |
|---|---|---|
| **Arquitectura experimental como anexo propio** | el capítulo 4 la describe y la Figura 6.1 la dibuja. Un anexo con lo mismo en más páginas no añade comprensión: añade volumen, y el volumen de los anexos cuenta contra el límite sin puntuar | lo imprescindible —las ocho etapas con su experimento— entra como apartado **A.1**, en una tabla |
| **Protocolos experimentales** | son treinta y cinco documentos, y lo que los hace valiosos es **cuándo** se escribió cada uno respecto de cuándo se midió. Llevarlos al documento los congelaría en una versión y perdería justo eso | permanecen en el repositorio. Los dos casos en que la secuencia es parte del argumento —el umbral y las aperturas del conjunto de prueba— entran como **B.4** y **B.5** |
| **Validación de hipótesis y abstención** | es el núcleo de PI.3 y PI.4 y está en el cuerpo, con las tablas 5.5 a 5.8 y las figuras 5.10 y 5.11. Un anexo aquí movería evidencia principal fuera del texto que la argumenta, que es exactamente lo que un anexo no debe hacer | se queda en el capítulo 5 |

## 4. Las dos figuras, con su procedencia

| Fig. | Título | Fuente | Experimento | Conjunto | Qué explica | Limitaciones |
|---|---|---|---|---|---|---|
| **A.1** | Señal testigo de cada condición, comparada con la misma sesión sin fallo | `artifacts/figures/FIG-E4-01_series_normal_vs_fallo.png`, copiada sin modificar | E4 | `synthetic_v1`, sesiones pareadas | qué forma tiene cada fallo en la señal que lo delata, con la comparación pareada que aísla la condición del estilo de conducción | **no es reproducible desde cero**: la rutina genera sus propias sesiones con el generador vigente, y el generador cambió el 1-09-2026. Es un artefacto histórico y el anexo lo dice con esas palabras. Una sesión por condición. Sin SVG |
| **B.1** | F1 por condición de los dos modelos y diferencia entre ellos | `scripts/figuras_memoria.py` ← tablas por clase de E6 y E7 | E6 y E7 | `synthetic_v2`, validación | cuánto pesa cada condición en la diferencia agregada de 0,056 en F1 macro: se concentra en el fallo de encendido, −0,167 | una ejecución por celda, sin repeticiones ni intervalos; +0,032 sobre catorce ventanas es ventana y media |

Ninguna de las dos duplica una figura del capítulo 5. La A.1 no tiene equivalente en el cuerpo. La
B.1 convive con la Figura 5.3 y dice otra cosa: aquella muestra **adónde** van los errores de cada
modelo, esta **cuánto** pesa cada condición.

## 5. Referencias cruzadas con los capítulos

| Apartado del anexo | Lo que sostiene en el cuerpo |
|---|---|
| A.2, A.3 | el análisis descriptivo del capítulo 5 y la Figura 5.2: qué señal separa cada condición y por qué vía |
| A.3, parámetro `temp_cap_c` | la línea de 71 °C de la Figura 5.5, que es un parámetro declarado y no un ajuste |
| A.4 | la afirmación del capítulo 4 de que la muestra está parametrizada contra documentación del vehículo |
| A.5 | el objetivo específico 2 del capítulo 6, y la nota de la Figura 5.2 sobre `synthetic_v1` |
| A.6 | el primer hecho del análisis descriptivo: qué fallos no se ven en las medias |
| B.1 | las salvedades de contaminación del capítulo 5 y las limitaciones del capítulo 6 |
| B.2 | «el modelo temporal no supera al tabular» y «acierta dos ventanas más en el termostato» |
| B.3 | el párrafo de atribución del capítulo 5 y la Figura 5.8 |
| B.4 | el umbral de 0,79 y la frase «el criterio se enmendó después de ver el primer barrido» |
| B.5 | las cinco aperturas que el primer párrafo del capítulo 5 declara |
| C.5 | los dos límites de reproducibilidad del objetivo específico 2 |

## 6. Qué permanece solo en los notebooks y en el repositorio

| Qué | Por qué no entra |
|---|---|
| Los siete notebooks | están pensados para ejecutarse, y su versión HTML ya es la vía de lectura sin instalar nada. Copiarlos al documento sería convertir el anexo en un segundo documento experimental |
| Los treinta y cinco documentos de metodología | su valor está en la fecha de cada uno; en el documento perderían la secuencia |
| Las tablas completas de atribución, confusión y suficiencia caso a caso | el anexo da la fila que el texto necesita y cita el fichero. La tabla íntegra es material de verificación, no de lectura |
| Los registros de ejecución en JSON | son la fuente, y se citan por nombre en cada pie |
| El historial de Git | es la trazabilidad misma, y no cabe en un documento |

## 7. Riesgos de redundancia, y cómo se han evitado

| Riesgo | Cómo queda resuelto |
|---|---|
| **A.1 repitiendo la Figura 6.1** | A.1 es una tabla de ocho filas con el experimento que mide cada etapa; la 6.1 es el esquema. La tabla dice qué lo mide, el esquema dice cómo se encadena |
| **B.2 repitiendo la Figura 5.3** | se declara explícitamente en el propio anexo: una muestra adónde van los errores, la otra cuánto pesa cada condición |
| **B.5 repitiendo el primer párrafo del capítulo 5** | el capítulo dice que fueron cinco y en cuántas hubo exposición; el anexo da los cinco niveles y qué consume cada uno |
| **C repitiendo `docs/reproducir-desde-cero.md`** | es el riesgo real. El anexo da las cinco órdenes y la tabla de lo no reproducible; el documento del repositorio da los seis pasos con su salida esperada y se actualiza cuando cambia una orden. **Si el director prefiere, C puede sustituirse por una referencia al repositorio**, y el documento perdería tres páginas sin perder información |

## 8. Verificación de los límites de la plantilla

Medido sobre el texto fuente en Markdown, que aproxima pero no iguala el recuento del documento de
Word:

| | Palabras | Observación |
|---|---|---|
| Resumen y abstract | 702 | |
| Capítulos 1 a 6 | 31 665 | el capítulo 5 son 12 997 y el 4, 8 493 |
| Bibliografía | 1 142 | |
| **Cuerpo del trabajo** | **33 509** | |
| **Anexos** | **4 095** | **12,2 % del cuerpo**, dentro del 20 % que la plantilla toma como referencia |

**Hay un problema de extensión, y no está en los anexos.** La nota al pie de la plantilla fija un
mínimo de 50 000 palabras y un máximo de 60 000. El cuerpo tiene 33 509, es decir **16 491 por debajo
del mínimo**. Los anexos no lo resuelven: no puntúan, y la sesión informativa del curso fija su
mínimo «sin anexos», de modo que ampliarlos para alcanzar la cifra sería contraproducente además de
inútil.

Esta es la decisión abierta **D-01**, registrada desde la primera revisión y todavía sin resolver:
hay **tres cifras oficiales incompatibles** —50 000 a 60 000 palabras en la nota al pie de la
plantilla; 31 a 73 páginas en las recomendaciones por capítulo; y un mínimo de 60 páginas sin anexos
en la sesión informativa del curso, con «no apto» aparejado—. Según cuál rija, el trabajo cumple o
no cumple, y este documento no puede resolverlo. Lo que sí puede decir es que **el recuento de
palabras ha pasado de 12 550 a 33 509** desde que la cuestión se planteó, y que el margen que queda
hasta el mínimo de palabras corresponde al cuerpo, no a los anexos.

La comprobación definitiva se hace sobre el documento montado: `scripts/verificar_docx.py` informa
del recuento de palabras del DOCX, que es el que la titulación mide.

## 9. Lo que esta propuesta no hace

No escribe conclusiones nuevas: cada afirmación de los anexos está discutida antes en el cuerpo o es
una ficha del instrumento. No mueve evidencia principal fuera de los capítulos. No reconstruye
`synthetic_v1` ni `synthetic_v3` por aproximación para ilustrar nada: la única figura que procede de
un conjunto no reconstruible se identifica como artefacto histórico. Y no resuelve D-01.
