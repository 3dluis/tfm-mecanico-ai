# Auditoría de procedencia de las figuras científicas

**Fecha:** 14 de octubre de 2026 · **Qué comprueba:** de dónde sale cada figura del documento, con
qué código, sobre qué datos y si sus cifras coinciden con los registros · **Cómo:** abriendo el
código que la produce y recalculando sus números desde el registro, no leyendo lo que su pie declara

## 1. La respuesta primero

**Ninguna de las dieciocho figuras del documento está generada por un modelo de imágenes, ni dibujada
a partir de una descripción, ni contiene un valor escrito a mano.** Las dieciocho salen de ejecutar
código Python sobre registros de experimentos o sobre tablas congeladas.

Se comprobó de tres formas independientes, y las tres se mantienen como pruebas:

| Comprobación | Resultado |
|---|---|
| Las cifras de cada figura, recalculadas desde su registro | **coinciden**, las ocho dibujadas |
| Las dieciocho regeneradas dos veces seguidas | **bit a bit idénticas**, 18 de 18 |
| Búsqueda de datos escritos a mano en el código de dibujo | **ninguna línea** con valores literales |

## 2. La matriz: figura → experimento → notebook → datos

| Fig. | Qué representa | Experimento | Conjunto · partición | Registro con sus datos | Qué la dibuja | Librería | ¿Regenerable? | ¿Coincide con el registro? | Clase |
|---|---|---|---|---|---|---|---|---|---|
| 5.1 | ventanas por clase y partición | E5 | `synthetic_v2` · las tres | `synthetic_v2_meta.parquet`, `E5_reparto.csv` | `visualization.memoria.datos` | Matplotlib | **sí** | sí: 112/28/28 y 56/14/14 | **C** |
| 5.2 | separabilidad por señal | E4 | `synthetic_v1` · bloques de 60 s | `E4_separabilidad.csv` | `visualization.memoria.datos` | Matplotlib | **sí**, la figura; **no** el conjunto | sí: 8 celdas con efecto grande | **C** |
| 5.3 | adónde van los errores | E6 y E7 | `synthetic_v2` · validación | las dos matrices de confusión | `visualization.memoria.diagnostico` | Matplotlib | **sí** | sí: 12 y 17 errores | **C** |
| 5.4 | el confusor de volumen | E6 y E7 | `synthetic_v2` y `v3` · validación | los cuatro registros de F1 macro | `visualization.memoria.diagnostico` | Matplotlib | **sí**, la figura | sí: 0,8788 · 0,8230 · 0,9321 · 0,9446 | **C** |
| 5.5 | límite de evidencia del termostato | E6 | `synthetic_v2` · validación, F03 | predicción por ventana, **solo en la figura** | la ejecución de E6, en 2026-09-01 | Matplotlib | **no** | no verificable: su dato no se conservó | **D** |
| 5.6 | expresión efectiva del fallo | E6, fase G | `synthetic_v2` · validación | se recalcula en el notebook | notebook `06_expresion_del_fallo` | Matplotlib | **sí** | sí: 5 ventanas sin señal en F03 | **B** |
| 5.7 | calibración antes y después | E6, calibrado en E15 | `synthetic_v2` · validación | `E15_suficiencia.json`, bloque de calibración | `visualization.memoria.calibracion` | Matplotlib | **sí** | sí: ECE 0,1439 → 0,0854; sesgo −0,1395 → +0,0089 | **C** |
| 5.8 | mapa de atribución | E9 | `synthetic_v2` · validación, 18 casos | `E9_atribuciones_synthetic_v2.csv` | notebook `04_explicabilidad` | Matplotlib sobre valores **SHAP** ya calculados | **sí** | sí | **B** |
| 5.9 | recuperación por estrategia | E12 | corpus · 6 casos, 5 puntuados | `E12_retrieval_por_estrategia.csv` | `visualization.memoria.recuperacion` | Matplotlib | **sí** | sí: 0,00 y 1,00 de acierto | **C** |
| 5.10 | aplicables frente a cobertura | E15 | `synthetic_v2` · validación | `E15_suficiencia.csv` | notebook `05_suficiencia_y_abstencion` | Matplotlib | **sí** | sí: 17 casos, 5 condiciones | **B** |
| 5.11 | efecto de cada ablación | E18 | `synthetic_v2` · validación | `E18_ablacion_A1..A4.json` | `visualization.memoria.ablaciones` | Matplotlib | **sí** | sí: 0/9, 0/9, 6/9, 9/9 | **C** |
| 5.12 | las tres cifras finales | E19 | `synthetic_v2` · **prueba** | `E19_evaluacion_final_v3.csv` | notebook `03_analisis_e19` | Matplotlib | **sí** | sí: 0/14, 2/8, 6/10 | **B** |
| 5.13 | decisión por ejecución | E19 | `synthetic_v2` · **prueba** | el mismo | notebook `03_analisis_e19` | Matplotlib | **sí** | sí: 22 ejecuciones | **B** |
| 6.1 | recorrido experimental | — | sin conjunto | el índice de experimentos | notebook `00_introduccion` | Matplotlib | **sí** | no aplica: es un esquema | **E** |
| 6.2 | objetivos y evidencia | — | sin conjunto | el propio capítulo 6 | `visualization.memoria.sintesis` | Matplotlib | **sí** | no aplica: es un mapa documental | **E** |
| 6.3 | compromiso entre los dos errores | E15 | `synthetic_v2` · validación | `E15_suficiencia.csv` | `visualization.memoria.sintesis` | Matplotlib | **sí** | sí: 0/9 y 2/5 | **C** |
| A.1 | señal testigo por condición | E4 | `synthetic_v1` · sesiones pareadas | ninguno: la rutina genera sus sesiones | la ejecución de E4, en 2026-09-01 | Matplotlib | **no** | no verificable: su generador cambió | **D** |
| B.1 | F1 por condición | E6 y E7 | `synthetic_v2` · validación | las dos tablas por clase | `visualization.memoria.diagnostico` | Matplotlib | **sí** | sí: +0,032 y −0,167 | **C** |

**Clases:** **B** la produce un notebook desde resultados experimentales · **C** la dibuja el paquete
desde registros congelados · **D** artefacto histórico no reproducible · **E** esquema conceptual.
**Ninguna figura cae en la clase F**, que es la de procedencia no verificable.

## 3. Las dos que no se pueden regenerar

| Figura | Por qué | Qué se hace |
|---|---|---|
| **5.5** límite de evidencia del termostato | necesita la predicción **por ventana** de las catorce ventanas de F03, y el registro de E6 guarda solo los agregados. Ese dato existió durante la ejecución del 1 de septiembre de 2026 y no se persistió | **se conserva** como artefacto histórico. Su pie declara el experimento, el conjunto y el protocolo; el parámetro que dibuja —el techo de 71 °C— es un valor **declarado del generador**, no ajustado a los datos |
| **A.1** señal testigo de cada condición | la rutina que la dibuja **genera sus propias sesiones** con el generador vigente, y el generador se calibró contra el manual el 1 de septiembre de 2026 a las 15:46. Ejecutarla hoy daría otra figura: el ralentí, por ejemplo, estaría en el rango documentado y no en los 820 rpm que la figura muestra | **se conserva** como artefacto histórico, y su pie lo dice con esas palabras. **No se sustituye por una figura nueva** sin autorización |

Las dos pertenecen a `synthetic_v1`, que no se reconstruye con el generador publicado, y las dos lo
declaran en su pie.

## 4. Lo que esta auditoría cambió en el código

**El código de dibujo vivía fuera del paquete.** Estaba en un guion de `scripts/`, sin comprobación
de tipos, y un notebook no podía importarlo. Eso dejaba abierta la puerta a lo que el encargo quiere
cerrar: que la misma figura acabara dibujada dos veces de dos maneras distintas.

Ahora vive en `mecanico_ia_exp.visualization.memoria`, en seis módulos temáticos —`base`, `datos`,
`diagnostico`, `calibracion`, `recuperacion`, `ablaciones` y `sintesis`—, bajo comprobación estricta
de tipos. El guion quedó en 188 líneas: el registro de qué figura lleva cada número y la orden de
consola. Una prueba comprueba que no vuelva a contener código de dibujo.

**Y el montaje del documento se detiene si falta una figura.** Antes, el conversor avisaba y seguía:
el documento habría salido con un hueco donde debía ir un gráfico. Ahora falla, dice cuál falta y
con qué orden se genera. Un hueco en un entregable es peor que un fallo de montaje, porque el fallo
se ve.

## 5. Sobre las librerías

Todas las figuras usan **Matplotlib**, que es lo que corresponde: series, matrices, barras, planos y
mapas de calor. La de atribución dibuja con Matplotlib **valores SHAP ya calculados** por la fase de
atribución, no los recalcula. **Seaborn** está declarado como dependencia y no se usa en ninguna
figura del documento; **Plotly** no se usa, y para las figuras de un documento impreso no aporta
nada, porque su ventaja es la interacción. No se ha añadido ninguna dependencia nueva.

## 6. Una regresión que esta auditoría encontró

Al escribir la prueba que comprueba que las figuras de conjuntos no reconstruibles lo declaren en su
pie, la prueba falló: la **Figura 5.2** había perdido esa advertencia en la revisión de autonomía
documental del día anterior, cuando se acortaron los pies para sacar las rutas del cuerpo. La
información seguía en el texto del capítulo, pero no en el pie, y una figura se lee suelta.
Restaurada en su pie y en el de la **A.1**.

Es el tipo de defecto que motiva estas pruebas: no se ve leyendo, no rompe el montaje y cambia lo
que una figura afirma de sí misma.
