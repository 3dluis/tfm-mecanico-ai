# Informe de cambios: incorporación de figuras a los capítulos 5 y 6

**Fecha:** 13 de octubre de 2026 · **Qué cubre:** todo lo hecho desde la aprobación de la propuesta
de figuras · **Qué no hace:** no queda ninguna tarea del encargo sin ejecutar ni ninguna decisión
tomada en lugar del autor

## 1. Lo primero, porque no es una figura

Verificar de dónde salía cada figura destapó **cinco defectos**, tres de ellos en material ya
entregado. Ninguno cambia una cifra publicada; todos cambian lo que con esas cifras se podía decir.

| # | Dónde estaba | Qué decía | Qué es cierto | Estado |
|---|---|---|---|---|
| `F-7` | capítulo 6, OE2 | «`synthetic_v3`, **del que salen E6, E7 y la evaluación final**, no es reconstruible» | las tres ejecuciones declaran `synthetic_v2`, que se reconstruye bit a bit. El complemento «sobre `synthetic_v3`» se perdió al resumir el registro, y el sufijo `_v3` del fichero de E19 —que numera el **tercer intento**— ayudó a la confusión | **corregido** |
| `F-8` | capítulo 5, análisis descriptivo | «dos de los cinco fallos no son visibles en las medias: el fallo de encendido y **el termostato bloqueado**» | el termostato es el **más** visible: 69,2 °C frente a 81,4, delta de Cliff −0,75 por nivel. El segundo invisible es la **sonda lenta**, −1,00 por dispersión | **corregido** |
| — | notebook 02 y su HTML | la figura de calibración se titulaba «Los dos prometen más de lo que cumplen» | el bosque **promete menos**: confianza 0,738, acierto 0,878, sesgo −0,1395. El capítulo 5 nunca lo heredó | **corregido** |
| — | notebook 05 y su HTML | la figura de suficiencia declaraba 17 casos | dibujaba **14**: seleccionaba cuatro condiciones por nombre exacto y dejaba fuera `DISTRACTOR_NO_FILTER`, la única en la que entran fragmentos de otro motor | **corregido** |
| `L-25` | limitaciones, y todo lo derivado | un conjunto no reconstruible | son **dos**. Medido muestra a muestra: `synthetic_v1`, 0 de 36 sesiones idénticas; `synthetic_v3`, 0 de 216; `synthetic_v2`, como control, **72 de 72**. De `synthetic_v1` salen las seis figuras y las cinco tablas de E4 | **declarado y bloqueado** |

El quinto apareció al preguntarse si la figura pareada de E4 podía redibujarse. No podía: la función
que la genera no lee el conjunto, genera sus propias sesiones con el generador vigente, y el
generador cambió el 1 de septiembre de 2026. De ahí la pregunta que nadie había hecho —si
`synthetic_v1` reconstruye— y la medición que la responde, en `scripts/medir_reconstruccion_cruda.py`.
El guion de reconstrucción se niega ahora con los dos conjuntos, igual que ya se negaba con uno.

## 2. Las figuras

Dieciocho generadas, **dieciséis incorporadas** y dos reservadas para anexos.

| | Cuántas | Cuáles |
|---|---|---|
| Dibujadas desde registros congelados | 12 | 5.1, 5.2, 5.3, 5.4, 5.7, 5.9, 5.11, 6.2, 6.3, y D.1 |
| Copiadas, con el motivo declarado | 6 | 5.5, 5.6, 5.8, 5.10, 5.12, 5.13, 6.1, B.1 |
| En el capítulo 5 | 13 | 5.1 a 5.13 |
| En el capítulo 6 | 3 | 6.1 a 6.3 |
| Trasladadas a anexos tras la revisión de pertinencia | 2 | B.1 y D.1 |

**Ninguna ejecución nueva.** El guion `scripts/figuras_memoria.py` lee tablas de `artifacts/tables/`,
registros de `experiments/` y, en una figura, el conjunto procesado `synthetic_v2`. No abre ningún
conjunto de prueba y escribe solo en `artifacts/figures/memoria/`. **Los artefactos históricos no se
tocan:** las tres figuras con defecto de composición se redibujaron con otro nombre y la versión
anterior se conserva intacta.

**Las dos que no pasaron la revisión de pertinencia.** La serie pareada de señales, porque su
instrumento ya no existe y ocupa una página entera; y el F1 por clase, porque la figura de matrices
de confusión, dos párrafos antes, ya muestra adónde van los errores de cada modelo. Las dos están
generadas y propuestas como `B.1` y `D.1`.

## 3. Lo que las figuras condicionadas exigieron escribir antes

| Entrada | Qué hizo falta | Dónde está |
|---|---|---|
| `A-3` | el capítulo atribuía al volumen de datos la desventaja del modelo temporal. Entre los dos conjuntos cambian el volumen **y** el generador | cap. 5, PI.1, y Figura 5.4 |
| `N-2` | la distinción entre llevar la etiqueta de un fallo y contener señal observable de él, con su medición y con la advertencia de que las cinco ventanas sin señal **no** están comprobadas como las cinco falladas | cap. 5, PI.1, y Figura 5.6 |
| `N-1` | el apartado de la evaluación final: 0 de 14, 2 de 8 y 6 de 10, con sus denominadores, los intervalos de Wilson —la falsa confianza es compatible con cualquier tasa hasta 0,215— y la salvedad de `L-26` | cap. 5, apartado propio, y Figuras 5.12 y 5.13; cap. 6, OE3, OE5 y objetivo general |

## 4. Dos errores que la revisión de las propias figuras encontró

Las figuras se cotejaron contra su tabla antes de aceptarlas, y de ese cotejo salieron dos cosas que
habrían entrado al documento:

- **La figura de ablaciones daba 0/6** de falsa confianza para la configuración canónica, donde la
  Tabla 5.6 da **0/9**. La función excluía por prefijo todas las condiciones con distractor; la
  tabla excluye solo la que llevaba filtro de motor, cuya configuración era idéntica a la parcial.
- **La figura de suficiencia mostraba 14 de 17 casos** declarando los diecisiete, como se recoge
  arriba.

## 5. Validación

| Comprobación | Resultado |
|---|---|
| `ruff check` · `ruff format --check` · `mypy src` | sin incidencias, 79 ficheros |
| Suite completa sin recursos externos | **912 pruebas** en verde |
| `tests/test_memoria_figuras.py` | numeración correlativa, las dieciséis existen a 300 ppp, ningún pie omite un campo, ninguna imagen sin texto alternativo ni sin interpretación, ninguna ruta local, todas mencionadas en prosa por su número y todas presentes en el guion que las genera |
| `tests/test_memoria_afirmaciones.py` | las ocho frases retiradas no vuelven como afirmación; el capítulo 6 atribuye cada conjunto a su ejecución |
| Los siete notebooks, reejecutados y reexportados | en verde |
| Censo de artefactos históricos | **0 desviaciones**, antes y después |

## 6. Lo que queda, y de quién depende

| Qué | De quién depende |
|---|---|
| **Los anexos**: tres recomendados de seis, con su motivo | decisión del autor, en `propuesta-anexos.md` |
| **La vía de conversión a DOCX**: pandoc o guion propio; ninguna instalada | decisión del autor, en `entrega-docx.md` |
| **El reentrenamiento del adaptador**, detenido por memoria insuficiente | una máquina de 48–64 GB, o la decisión de cerrarlo como limitación |
| **`N-3` a `N-6` y las entradas `A-` restantes** de la matriz de impacto | decisión del autor |
| **Comprobar si las cinco ventanas sin señal del termostato son las cinco falladas** | exige reejecutar E6 conservando la predicción por ventana, que es una ejecución nueva y no está autorizada |

La entrega definitiva no se monta todavía, y la razón está escrita: hacerlo ahora obligaría a
montarla dos veces, con el riesgo de que una corrección se quede solo en una de las dos versiones.
