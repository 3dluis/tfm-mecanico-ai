# Autonomía documental de la memoria: inventario, clasificación y propuesta

**Fecha:** 14 de octubre de 2026 · **Qué es:** qué referencias al repositorio contiene la memoria,
qué función cumple cada una y cuáles obligan al lector a salir del documento para entender algo ·
**Estado: aplicada.** Las correcciones de los apartados 4, 5 y 6 están en el documento ·
**Criterio:** el tribunal debe poder leer la memoria entera, comprender la investigación y juzgar
sus límites **sin abrir el repositorio**; el repositorio sirve para comprobar **cómo** se obtuvo lo
que la memoria explica, no para explicar lo que la memoria dejó a medias

## 1. Inventario

Medido sobre los nueve ficheros de la memoria: **100 referencias técnicas en línea, 71 distintas**.

| Dónde | Cuántas | Qué función cumplen |
|---|---|---|
| Capítulo 5 | 63 | pies de figura y de tabla, sobre todo; seis notas de corrección y cuatro remisiones en prosa |
| Capítulo 6 | 15 | cinco notas de corrección y tres pies de figura |
| Anexos | 22 | pies de tabla, y el anexo C, donde las rutas son el contenido |
| Capítulos 1 a 4, resumen y bibliografía | **0** | ninguna |

Las más repetidas son el guion que genera las figuras, diez veces; la ficha de las correcciones del
13 de octubre, seis; y los registros de E6, E7 y E15, tres o cuatro cada uno.

## 2. Clasificación

### A · Información esencial que el lector necesita y hoy está fuera — **5 referencias**

| # | Dónde | Qué dice ahora | Por qué es un problema | Qué se hace |
|---|---|---|---|---|
| A1 | cap. 5, párrafo 2 | «El registro completo, con los cinco niveles de exposición que se distinguen, está en `docs/methodology/registro-aperturas-test.md`» | los cinco niveles son lo que permite juzgar si el conjunto de prueba sigue siendo una prueba. **Ya están en la memoria**, en el anexo B | remitir **al anexo B**, no a la ruta |
| A2 | cap. 6, párrafo 1 | la misma remisión | ídem | ídem |
| A3 | cap. 5, párrafo 1 | «su informe es `docs/experiments/E19_evaluacion_final.md`» | la evaluación final **tiene ya su propio apartado** en el capítulo 5, con sus tres cifras y sus intervalos | remitir al apartado, no al fichero |
| A4 | cap. 5, cierre de E19 | «la propuesta de corrección […] está en `docs/methodology/propuesta-validador-numerico.md`» | el lector no sabe **qué propone**. La memoria dice dónde está, no qué dice | enunciar en una frase qué comprobaría el validador, y llevar la ruta al anexo C |
| A5 | cap. 5, nota de `F-4` | «la causa atribuida, falsa: se culpaba al filtro de motor» con remisión a la ficha | la corrección se entiende, pero el lector no puede comprobar **con qué evidencia** sin salir | añadir la evidencia en la propia nota: dos condiciones tenían configuración idéntica |

### B · Información complementaria cuya síntesis va al anexo — **3 referencias**

| # | Dónde | Qué se hace |
|---|---|---|
| B1 | anexo B, pie del barrido de umbral | el criterio y su enmienda se citan por **nombre y fecha**, no por ruta; la ruta pasa a la tabla de correspondencia del anexo C |
| B2 | anexo B, pie de la tabla de estatutos | ídem con el índice de experimentos y el registro de limitaciones |
| B3 | anexo B, pie de las aperturas | ídem |

### C · Información técnica de reproducción, que **se conserva** — **71 referencias**

Son las que el criterio final del encargo manda mantener: el repositorio debe permitir comprobar
cómo se obtuvo cada resultado. Dentro de esta categoría hay dos situaciones distintas:

| Situación | Cuántas | Qué se hace |
|---|---|---|
| **Rutas en el anexo C**, donde localizar el artefacto **es** el contenido del apartado | 12 | **se quedan tal cual.** El encargo lo autoriza expresamente |
| **Rutas dentro de pies de figura y de tabla** del cuerpo | 41 | el pie conserva **experimento, conjunto, protocolo y el identificador del registro**, que es la procedencia científica; la **ruta del fichero** pasa a una tabla de correspondencia nueva en el anexo C |
| **Identificadores de registro** citados en prosa —`E6_baseline_synthetic_v2.json` y equivalentes | 18 | **se quedan**: son el nombre del registro que sostiene una cifra, no una dependencia documental. Se explican la primera vez que aparecen |

### D · Referencias bibliográficas — **39 entradas**

No se tocan. Ninguna es una dependencia interna.

## 3. La distinción que gobierna la propuesta

Una ruta de fichero en un pie de figura **no** obliga a salir del documento: dice de dónde salió la
figura, y el lector que no quiera comprobarlo sigue leyendo sin perder nada. Una frase que dice «los
detalles están en `docs/...`» **sí** obliga, porque lo que falta es el detalle, no la comprobación.

Por eso la propuesta no elimina las referencias técnicas: **mueve las rutas al sitio donde su
presencia no interrumpe —el anexo C— y convierte en texto las cinco remisiones que hoy esconden
contenido.** Las cifras, los denominadores, las limitaciones y las correcciones no cambian.

## 4. Qué se incorpora al cuerpo

| Dónde | Qué se añade |
|---|---|
| cap. 5, cierre del apartado de E19 | una frase con **qué comprobaría** el validador numérico propuesto: nombre de la métrica, valor, umbral, operador de comparación y coherencia entre el texto y los datos estructurados; y que es **prospectivo y sin implementar** |
| cap. 5, nota de corrección de `F-4` | la evidencia que sostiene la corrección: dos de las tres condiciones con distractor tenían **configuración idéntica** a la parcial |
| cap. 5 y cap. 6 | las remisiones a los registros pasan a ser remisiones **al anexo B o al apartado correspondiente** |

## 5. Qué se traslada al anexo C

Una tabla de correspondencia nueva, **C.5**, con cuatro columnas:

> referencia académica → experimento → artefacto → ruta en el repositorio

Recoge las dieciocho figuras, las ocho tablas del capítulo 5 y los registros que sostienen las
cifras. Es el sitio donde un lector que quiera verificar encuentra la ruta exacta, y el sitio del
que se retira del cuerpo.

## 6. Qué referencias técnicas se conservan donde están

- Las doce del anexo C en prosa: guiones de verificación, procedimiento de reproducción, registro de
  conjuntos no reconstruibles y versiones HTML de los notebooks.
- Los identificadores de registro citados en prosa en el capítulo 5, porque son el nombre propio de
  la medición que sostiene cada cifra.
- Las rutas de los ficheros de código en los pies del anexo A, porque ahí el objeto descrito **es**
  la especificación que ese fichero contiene.

## 7. Impacto estimado sobre la extensión

| Concepto | Palabras |
|---|---|
| Lo que se añade al cuerpo (A4 y A5) | **+281** |
| Apartado C.6 y tabla de correspondencia C.5 | **+898** |
| Lo que se retira de los pies al acortarlos | **−160** |
| **Neto medido** | **cuerpo 36 455 → 36 736; anexos 4 237 → 5 135** |

Los anexos pasan del 11,6 % al **14,0 %** del cuerpo, dentro del 20 % que la plantilla toma como
referencia.

El efecto sobre la extensión del cuerpo es despreciable, y el crecimiento está en el anexo, que es
donde debía estar. El efecto sobre la lectura no es despreciable: los pies de figura pasan de tres
líneas de rutas a una línea de procedencia científica.

## 8. Lo que esta propuesta no hace

No elimina ninguna cifra, ningún denominador, ninguna limitación ni ninguna corrección. No retira
las notas fechadas que conservan lo que el texto decía antes. No oculta la contaminación, las
aperturas del conjunto de prueba, los resultados negativos ni los problemas de reproducibilidad:
los tres primeros están en el cuerpo y el cuarto, en el cuerpo y en el anexo. Y no convierte el
documento en un informe de desarrollo: va en la dirección contraria.
