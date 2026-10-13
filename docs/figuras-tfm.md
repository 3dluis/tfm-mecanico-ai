# Figuras del TFM: trazabilidad

**Fecha:** 13 de octubre de 2026 · **Qué es:** el registro de cada figura candidata a entrar en los
capítulos 5 y 6, con la cadena que la une a los datos y al resultado original · **Qué NO es:** una
declaración de que las figuras estén incorporadas. **La memoria no contiene todavía ninguna
figura**, y este documento no la modifica · **Por qué existe:** el encargo pide que cada figura
pueda rastrearse hasta los datos y resultados originales antes de usarla

La numeración `Figura X.Y` es la **propuesta** de
[`propuesta-figuras-cap5-cap6.md`](audits/propuesta-figuras-cap5-cap6.md), donde está el pie
completo de cada una y lo que se puede y no se puede afirmar con ella. Si el autor retira alguna,
las demás se renumeran.

## Estados

| Estado | Qué significa |
|---|---|
| `DISPONIBLE` | el fichero existe, se ha abierto y su contenido coincide con el registro que dice su procedencia |
| `COPIAR` | existe, pero vive en `notebooks/salida/`, que `.gitignore` excluye. Entrar en la memoria exige copiarlo a `artifacts/figures/` con su fila de procedencia |
| `REGENERAR` | el contenido es correcto y la composición tiene un defecto de legibilidad medido. No cambia ninguna cifra |
| `EXPORTAR` | la figura **no existe**. Se dibujaría desde un registro ya congelado, sin ejecutar ningún experimento nuevo |
| `BLOQUEADA` | no puede usarse hasta corregir un defecto de contenido |

## Capítulo 5

| Figura | Capítulo | Experimento | Dataset | Artefacto | Estado |
|---|---|---|---|---|---|
| 5.1 Ventanas por clase y partición | 5 | E5 | `synthetic_v2`, las tres particiones | `artifacts/figures/FIG-E5-02_particiones.png` · `artifacts/tables/E5_reparto.csv` | `REGENERAR` |
| 5.2 Señal testigo de cada condición, comparación pareada | 5 | E4 | `synthetic_v1`, sesiones pareadas | `artifacts/figures/FIG-E4-01_series_normal_vs_fallo.png` | `REGENERAR` |
| 5.3 Separabilidad de cada señal por condición | 5 | E4 | `synthetic_v1`, bloques de 60 s | `artifacts/figures/FIG-E4-02_separabilidad.png` · `artifacts/tables/E4_separabilidad.csv` | `REGENERAR` |
| 5.4 Matrices de confusión del bosque y de la red | 5 | E6 y E7 | `synthetic_v2`, validación, 98 ventanas | `FIG-E6-01_confusion_baseline.png` · `FIG-E7-01_confusion_temporal.png` · `E6_baseline_synthetic_v2.json` · `E7_temporal_synthetic_v2.json` | `DISPONIBLE` |
| 5.5 F1 por clase de los dos modelos y su diferencia | 5 | E6 y E7 | `synthetic_v2`, validación | `notebooks/salida/02_comparacion_modelos/FIG-NB02-02_por_clase.png` | `COPIAR` |
| 5.6 Calibración de la confianza, antes y después | 5 | E6, calibrado en E15 | `synthetic_v2`, validación, 98 ventanas, 10 tramos | `experiments/E15_suficiencia.json`, bloque `calibration` | `EXPORTAR` |
| 5.7 Límite de evidencia del termostato bloqueado | 5 | E6 | `synthetic_v2`, las 14 ventanas de F03 en validación | `artifacts/figures/FIG-E6-02_limite_evidencia_f03.png` | `DISPONIBLE` |
| 5.8 Expresión efectiva del fallo por ventana | 5 | E6, fase G del diseño de PI.1 | `synthetic_v2`, validación, 70 ventanas con fallo | `notebooks/salida/06_expresion/FIG-N06-01_expresion_y_aciertos.png` | `COPIAR` · condicionada a `N-2` |
| 5.9 El confusor de volumen y calibración del generador | 5 | E6 y E7 | `synthetic_v2` y `synthetic_v3` | `notebooks/salida/02_comparacion_modelos/FIG-NB02-05_confusor_volumen.png` | `COPIAR` · condicionada a `A-3` |
| 5.10 Dónde mira el modelo: atribución frente a señales declaradas | 5 | E9 | `synthetic_v2`, 18 casos de validación | `notebooks/salida/04_explicabilidad/FIG-NB04-01_mapa_atribucion.png` · `artifacts/tables/E9_atribuciones_synthetic_v2.csv` | `COPIAR` |
| 5.11 Recuperación por estrategia | 5 | E12 (RERUN-A) | corpus del vehículo, 6 casos anotados, 5 puntuados | `artifacts/tables/E12_retrieval_por_estrategia.csv` · `experiments/E12_retrieval.json` | `EXPORTAR` |
| 5.12 Documentos aplicables frente a cobertura de afirmaciones | 5 | E15 | `synthetic_v2`, 17 casos sobre 5 ventanas | `notebooks/salida/05_suficiencia/FIG-N05-01_aplicables_vs_cobertura.png` · `artifacts/tables/E15_suficiencia.csv` | `REGENERAR`: dibuja 4 de las 5 condiciones y el pie declara 17 casos |
| 5.13 Efecto de retirar o degradar cada componente | 5 | E18 | `synthetic_v2`, los mismos 17 casos | `experiments/E18_ablacion_A1.json` a `A4.json` | `EXPORTAR` |
| 5.14 Las tres cifras de la evaluación final con sus denominadores | 5 | E19 | `synthetic_v2`, **partición de prueba** | `notebooks/salida/03_analisis_e19/FIG-NB03-01_primario.png` · `artifacts/tables/E19_evaluacion_final_v3.csv` | `COPIAR` · condicionada a `N-1` |
| 5.15 Las 22 ejecuciones del estrato operativo | 5 | E19 | `synthetic_v2`, **partición de prueba** | `notebooks/salida/03_analisis_e19/FIG-NB03-02_decisiones.png` | `COPIAR` · condicionada a `N-1` |
| — Calibración de los dos modelos sin calibrar | 5 | E6 y E7 | `synthetic_v2`, validación | `notebooks/salida/02_comparacion_modelos/FIG-NB02-04_calibracion.png` | `BLOQUEADA`: su título y su lectura invierten el sentido del sesgo medido |

## Capítulo 6

| Figura | Capítulo | Experimento | Dataset | Artefacto | Estado |
|---|---|---|---|---|---|
| 6.1 Objetivos específicos, evidencia que los sostiene y estado | 6 | E1–E19 | sin conjunto: es documental | `docs/experiment-index.md` · `docs/memoria/cap6_conclusiones.md` | `EXPORTAR` |
| 6.2 Falsa confianza frente a abstención innecesaria: el sistema y las dos políticas triviales | 6 | E15 | `synthetic_v2`, validación, 17 casos sobre 5 ventanas | `experiments/E15_suficiencia.json` · Tabla 5.6 | `EXPORTAR` |
| 6.3 Recorrido experimental, del dato OBD-II a la decisión | 6 | E1–E19 | sin conjunto: es la arquitectura | `notebooks/salida/00_introduccion/FIG-NB00-01_recorrido.png` | `COPIAR` |

## Procedencia comprobada, una por una

Lo que sigue es lo que se comprobó antes de proponer cada figura, no lo que su nombre promete.

- **Las cuatro figuras de E6 y E7** (`5.4`, y la de `5.7`) se cotejaron **celda a celda** contra
  `artifacts/tables/E6_baseline_confusion_synthetic_v2.csv` y
  `E7_temporal_confusion_synthetic_v2.csv`. Coinciden. La comprobación importaba porque la hora de
  generación en disco, las 15:44 del 1 de septiembre de 2026, es **anterior** a la calibración del
  generador, de las 15:46 del mismo día, y porque los ficheros se escriben sin sufijo de conjunto:
  el nombre no distingue la ejecución sobre `synthetic_v2` de la ejecución sobre `synthetic_v3`. Lo
  que las identifica es su contenido, y su contenido es el de `synthetic_v2`.
- **`5.7`** dibuja, para cada una de las 14 ventanas de F03 en validación, si el modelo acertó,
  contra la temperatura media del refrigerante de esa ventana. Son predicciones **por ventana**,
  que el registro JSON de E6 no guarda y esta figura sí conserva.
- **`5.12`**, **`5.14`** y **`5.15`** declaran en su propio pie el fichero del que salen, y ese
  fichero está en `artifacts/tables/`.
- **`5.12`** se contó caso a caso contra `artifacts/tables/E15_suficiencia.csv`: dibuja catorce de los
  diecisiete, porque la condición `DISTRACTOR_NO_FILTER` no está entre las cuatro que selecciona.
  Ninguna conclusión cambia; el pie, sí.
- **`5.3`** se cotejó celda a celda contra `artifacts/tables/E4_separabilidad.csv`, y de ese cotejo
  salió `F-8`: el capítulo nombra mal uno de los dos fallos invisibles en las medias.
- **`5.9`** cruza dos conjuntos a la vez, y por eso su figura dice en el eje qué cambia entre ellos.
- **`6.3`** no tiene conjunto de datos: es un dibujo de la arquitectura hecho desde su descripción.
  Se marca como ilustrativa y no como evidencia.

## Lo que ninguna figura de esta lista hace

Ninguna sustituye a su tabla: las cifras publicadas siguen siendo las de las tablas 5.1 a 5.8, y
una figura que discrepara de su tabla sería un defecto de la figura. Ninguna procede de datos
simulados para ilustrar un resultado que no se midió. Y ninguna de las cuatro condicionadas entra
en la memoria antes de que entre el texto del que depende: una figura que contradiga al párrafo que
tiene encima es peor que no tener figura.
