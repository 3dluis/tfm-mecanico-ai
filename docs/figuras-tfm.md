# Figuras del TFM: trazabilidad

**Fecha:** 13 de octubre de 2026 · **Qué es:** el registro de cada figura de los capítulos 5 y 6,
con la cadena completa que la une a los datos y al resultado original · **Qué permite:** rastrear
cualquier trazo del documento hasta la configuración que lo produjo, en los dos sentidos ·
**Estado:** las dieciséis están **incorporadas** a los capítulos; las dos de los anexos están
generadas y pendientes de que se aprueben los anexos

```
TFM → figura → notebook o guion → experimento → artefacto → configuración → conjunto
```

## 1. Cómo se regenera cualquiera de ellas

```bash
uv run python scripts/figuras_memoria.py          # las dieciocho
uv run python scripts/figuras_memoria.py 5.4 6.2  # solo esas
```

El guion **no ejecuta ningún experimento, no abre ningún conjunto de prueba y no escribe fuera de
`artifacts/figures/memoria/`**. Lee tablas versionadas de `artifacts/tables/`, registros congelados
de `experiments/` y, en una sola figura, el conjunto procesado `synthetic_v2`, cuyas cuatro huellas
congela `configs/manifest_e19.json` y que se reconstruye bit a bit. Escribe PNG a 300 puntos por
pulgada, para el documento, y SVG, para quien quiera la versión vectorial.

Cuatro figuras no se dibujan sino que se copian, y el registro dice por qué en cada caso. Las dos
que vienen de `artifacts/figures/` no tienen SVG, porque el generador de figuras de los experimentos
solo emitía PNG.

## 2. Qué es cada figura y de dónde sale

| Fig. | Cap. | Sección | Experimento | Conjunto | Estado |
|---|---|---|---|---|---|
| 5.1 | 5 | Análisis descriptivo de la muestra | E5, ventanado y reparto | `synthetic_v2`, las tres particiones | incorporada |
| 5.2 | 5 | Análisis descriptivo de la muestra | E4, análisis exploratorio | `synthetic_v1`, bloques de 60 s | incorporada |
| 5.3 | 5 | PI.1 · Diagnóstico, calibración y atribución | E6 y E7 | `synthetic_v2`, validación | incorporada |
| 5.4 | 5 | PI.1 | E6 y E7 sobre los dos conjuntos | `synthetic_v2` y `synthetic_v3` | incorporada |
| 5.5 | 5 | PI.1 | E6 | `synthetic_v2`, las 14 ventanas de F03 en validación | incorporada |
| 5.6 | 5 | PI.1 | E6, fase G del diseño de PI.1 | `synthetic_v2`, las 70 ventanas con fallo de validación | incorporada |
| 5.7 | 5 | PI.1 | E6, calibrado en E15 | `synthetic_v2`, validación | incorporada |
| 5.8 | 5 | PI.1 | E9, atribución | `synthetic_v2`, 18 casos de validación | incorporada |
| 5.9 | 5 | PI.2 · Recuperación y trazabilidad | E12, reejecución canónica | corpus del vehículo; 6 casos, 5 puntuados | incorporada |
| 5.10 | 5 | PI.3 y PI.4 · Suficiencia, abstención y distractores | E15, verificador v2.1 | `synthetic_v2`, 17 casos sobre 5 ventanas | incorporada |
| 5.11 | 5 | Contribución de cada componente | E18, cuatro ablaciones | `synthetic_v2`, los mismos 17 casos | incorporada |
| 5.12 | 5 | La evaluación final sobre el conjunto de prueba | E19 | `synthetic_v2`, **partición de prueba** | incorporada |
| 5.13 | 5 | La evaluación final sobre el conjunto de prueba | E19 | `synthetic_v2`, **partición de prueba** | incorporada |
| 6.1 | 6 | Conclusiones sobre los objetivos | E1–E19 (etiquetas de etapa) | sin conjunto: es la arquitectura | incorporada |
| 6.2 | 6 | Conclusiones sobre los objetivos | E1–E19 (uno por fila) | sin conjunto: es documental | incorporada |
| 6.3 | 6 | Limitaciones | E15 | `synthetic_v2`, validación | incorporada |
| B.1 | anexo B | Dataset sintético OBD-II | E4 | `synthetic_v1`, sesiones pareadas | generada, pendiente de anexo |
| D.1 | anexo D | Resultados complementarios | E6 y E7 | `synthetic_v2`, validación | generada, pendiente de anexo |

## 3. Protocolo, fichero, procedimiento de generación y límites

| Fig. | Protocolo | Fichero | Lo produce | Limitaciones declaradas en su pie |
|---|---|---|---|---|
| 5.1 | ventana de 120 s con paso de 60 s; reparto **por sesión** | `FIG-5-01_particiones` | `scripts/figuras_memoria.py` ← `data/processed/synthetic_v2_meta.parquet` y `artifacts/tables/E5_reparto.csv` | describe el diseño, no la dificultad de cada clase |
| 5.2 | delta de Cliff frente a la condición sin fallo, por separado sobre nivel y dispersión; se etiqueta el efecto grande, delta de valor absoluto mayor o igual que 0,474 | `FIG-5-02_separabilidad` | `scripts/figuras_memoria.py` ← `artifacts/tables/E4_separabilidad.csv` | ordena pero no explica; bloques de 60 s y no ventanas de 120; **`synthetic_v1` no se reconstruye** (L-25) |
| 5.3 | una ejecución por modelo, semilla 20260901 | `FIG-5-03_confusiones` | `scripts/figuras_memoria.py` ← `E6_baseline_confusion_synthetic_v2.csv` y `E7_temporal_confusion_synthetic_v2.csv` | una ejecución, una semilla, 98 ventanas de 12 sesiones |
| 5.4 | una ejecución por celda | `FIG-5-04_confusor_volumen` | `scripts/figuras_memoria.py` ← `E6_baseline_synthetic_v{2,3}.json` y `E7_temporal_synthetic_v{2,3}.json` | **dos variables cambian a la vez**; la mitad derecha no es reproducible por un tercero |
| 5.5 | cada punto una ventana; el techo de 71 °C es un parámetro **declarado** del generador | `FIG-5-05_limite_evidencia_termostato` | copiada de `artifacts/figures/FIG-E6-02_limite_evidencia_f03.png`; **no se puede redibujar**: necesita la predicción por ventana, que el registro de E6 no guarda | 14 ventanas de 2 sesiones; muestra coincidencia, no causa; sin SVG |
| 5.6 | trayectoria con fallo contra trayectoria sin fallo de la misma semilla; umbral del 10 % de la desviación típica de cada señal | `FIG-5-06_expresion_del_fallo` | notebook `06_expresion_del_fallo.ipynb` | **las cinco ventanas sin señal NO están comprobadas como las cinco falladas** |
| 5.7 | isotónica con validación cruzada de 5 pliegues sobre entrenamiento; ECE sobre 10 tramos | `FIG-5-07_calibracion` | `scripts/figuras_memoria.py` ← `experiments/E15_suficiencia.json` | un punto por configuración no dice en qué tramos falla; 10 tramos sobre 98 ventanas |
| 5.8 | valores de Shapley por permutación, fondo de 100 ventanas sin fallo | `FIG-5-08_mapa_atribucion` | notebook `04_explicabilidad.ipynb` ← `artifacts/tables/E9_atribuciones_synthetic_v2.csv` | fiel al modelo, no al vehículo; 18 casos; la ablación A1 muestra que no interviene en la decisión |
| 5.9 | consulta en inglés, mapa de códigos congelado, 10 primeros resultados | `FIG-5-09_recuperacion` | `scripts/figuras_memoria.py` ← `artifacts/tables/E12_retrieval_por_estrategia.csv` | 5 casos puntuados; la estrategia guiada usa los códigos de la condición **anotada**: su ventaja es una cota asistida |
| 5.10 | modo oracular; las **cinco** condiciones de evidencia | `FIG-5-10_aplicables_vs_cobertura` | notebook `05_suficiencia_y_abstencion.ipynb` ← `artifacts/tables/E15_suficiencia.csv` | 17 ejecuciones sobre 5 ventanas; la cobertura la establecen comprobaciones deterministas, no un juicio externo |
| 5.11 | cada ablación cambia una pieza; ninguna redacta | `FIG-5-11_ablaciones` | `scripts/figuras_memoria.py` ← `experiments/E18_ablacion_A1.json` a `A4.json` | **A2 quedó inconclusa**; 3 y 5 ventanas independientes; el criterio se ajustó sobre estos casos |
| 5.12 | política v2.2, conjunto anotado sellado antes de abrir la partición | `FIG-5-12_evaluacion_final` | notebook `03_analisis_e19.ipynb` ← `artifacts/tables/E19_evaluacion_final_v3.csv` | **0/14 no es riesgo cero**: el intervalo de Wilson llega a 0,215; escalas verticales distintas por panel |
| 5.13 | cada punto una ejecución; dos puntos por fila son sesiones distintas | `FIG-5-13_decisiones_e19` | notebook `03_analisis_e19.ipynb` | la leyenda conserva la categoría de falsa confianza, que **no aparece**, para que se vea que existe y no se observó |
| 6.1 | dibujada desde la descripción de la arquitectura | `FIG-6-01_recorrido_experimental` | notebook `00_introduccion.ipynb` ← `docs/experiment-index.md` | **ilustrativa**: dibuja el diseño, no su comportamiento; la separación no se ablacionó |
| 6.2 | el estado de cada fila es el que el capítulo afirma en prosa | `FIG-6-02_objetivos_y_evidencia` | `scripts/figuras_memoria.py` | no es una medición; «parcial» iguala en una etiqueta situaciones distintas |
| 6.3 | las políticas de referencia se definieron **después** de medir el criterio | `FIG-6-03_compromiso_cobertura_abstencion` | `scripts/figuras_memoria.py` ← `artifacts/tables/E15_suficiencia.csv` | las referencias no son una línea base independiente; 3 y 5 ventanas |
| B.1 | misma semilla y mismo régimen con y sin fallo; antes de la marca las dos series coinciden exactamente | `FIG-B-01_series_normal_vs_fallo` | copiada de `artifacts/figures/FIG-E4-01_series_normal_vs_fallo.png`; **no se puede redibujar**: la función genera sus propias sesiones y el generador cambió el 1-09-2026 | una sesión por condición; `synthetic_v1` no se reconstruye; sin SVG |
| D.1 | una ejecución por modelo | `FIG-D-01_f1_por_clase` | `scripts/figuras_memoria.py` ← `E6_baseline_por_clase_synthetic_v2.csv` y `E7_temporal_por_clase_synthetic_v2.csv` | una ejecución por celda; una diferencia de 0,032 sobre 14 ventanas es ventana y media |

Todas viven en `artifacts/figures/memoria/`, en PNG y, salvo las dos copiadas de `artifacts/figures/`,
también en SVG.

## 4. Procedencia comprobada, una por una

Lo que sigue es lo que se comprobó antes de aceptar cada figura, no lo que su nombre promete.

- **Las cuatro de E6 y E7** —`5.3`, `5.5`, y las que alimentan `5.4` y `D.1`— se cotejaron **celda a
  celda** contra `artifacts/tables/E6_baseline_confusion_synthetic_v2.csv` y
  `E7_temporal_confusion_synthetic_v2.csv`. Coinciden. La comprobación importaba porque la hora de
  generación en disco de las figuras históricas, las 15:44 del 1 de septiembre de 2026, es anterior
  a la calibración del generador, de las 15:46 del mismo día, y porque esos ficheros se escriben sin
  sufijo de conjunto: el nombre no distingue la ejecución sobre `synthetic_v2` de la ejecución sobre
  `synthetic_v3`. Lo que las identifica es su contenido, y su contenido es el de `synthetic_v2`.
- **`5.5`** conserva información que su propio registro perdió: la predicción **por ventana** de las
  catorce ventanas de F03, que el JSON de E6 no guarda.
- **`5.11`** se contó contra la Tabla 5.6 antes de aceptarla, y de ahí salió una corrección: el
  denominador de la falsa confianza daba 6 en lugar de 9, porque la función excluía por prefijo
  todas las condiciones con distractor. La tabla excluye solo la que llevaba filtro de motor.
- **`5.10`** se contó caso a caso contra `artifacts/tables/E15_suficiencia.csv`, y de ahí salió otra:
  dibujaba catorce de los diecisiete, porque la condición `DISTRACTOR_NO_FILTER` no estaba entre las
  cuatro que seleccionaba, mientras su pie declaraba los diecisiete.
- **`5.2`** se cotejó celda a celda contra `artifacts/tables/E4_separabilidad.csv`, y de ese cotejo
  salió `F-8`: el capítulo nombraba mal uno de los dos fallos invisibles en las medias.
- **`6.1`** y **`6.2`** no tienen conjunto de datos y su pie lo dice con esa palabra: son
  ilustrativa y documental, no evidencia.

## 5. Qué ninguna de estas figuras hace

Ninguna sustituye a su tabla: las cifras publicadas siguen siendo las de las tablas 5.1 a 5.8, y una
figura que discrepara de su tabla sería un defecto de la figura. Ninguna procede de datos simulados
para ilustrar un resultado que no se midió. Ninguna reejecuta nada: el guion que las produce lee
registros congelados. Y ninguna modifica los artefactos históricos: las tres figuras que tenían un
defecto de composición se redibujaron con otro nombre, y la versión anterior se conserva intacta en
`artifacts/figures/`.
