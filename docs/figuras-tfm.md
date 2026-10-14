# Figuras del TFM: trazabilidad

**Fecha:** 13 de octubre de 2026 · **Qué es:** el registro de cada figura de los capítulos 5 y 6,
con la cadena completa que la une a los datos y al resultado original · **Qué permite:** rastrear
cualquier trazo del documento hasta la configuración que lo produjo, en los dos sentidos ·
**Estado:** las veintitrés están **incorporadas**: veinte en los capítulos 5 y 6, y tres en los
anexos A y B

```
TFM → figura → notebook o guion → experimento → artefacto → configuración → conjunto
```

## 1. Cómo se regenera cualquiera de ellas

```bash
uv run python scripts/figuras_memoria.py          # las veintitrés
uv run python scripts/figuras_memoria.py 5.4 6.2  # solo esas
uv run python scripts/figuras_memoria.py --trazabilidad  # la matriz de abajo
```

El guion **no ejecuta ningún experimento, no abre ningún conjunto de prueba y no escribe fuera de
`artifacts/figures/memoria/`**. Lee tablas versionadas de `artifacts/tables/`, registros congelados
de `experiments/` y, en una sola figura, el conjunto procesado `synthetic_v2`, cuyas cuatro huellas
congela `configs/manifest_e19.json` y que se reconstruye bit a bit. Escribe PNG a 300 puntos por
pulgada, para el documento, y SVG, para quien quiera la versión vectorial.

Cuatro figuras no se dibujan sino que se copian, y el registro dice por qué en cada caso. Las dos
que vienen de `artifacts/figures/` no tienen SVG, porque el generador de figuras de los experimentos
solo emitía PNG.

## 2. La matriz de procedencia

**Esta tabla no se escribe a mano: la emite el registro.** Al renumerar el capítulo 5 para dar
sitio a las figuras nuevas, la versión anterior de este documento quedó describiendo figuras que ya
no llevaban ese número, y nada lo detectó. Ahora el número, el fichero, la función que la dibuja y
su huella salen del mismo sitio que produce la figura, de modo que no pueden discrepar:

```bash
uv run python scripts/figuras_memoria.py --trazabilidad
```

La cadena que la tabla recorre es la que el trabajo exige:

```
experimento → conjunto → partición → notebook → función de visualización → figura → capítulo
```

La página del PDF se lee del entregable: se busca el **pie** de cada figura, que es texto, y no la
imagen. La huella es el SHA-256 del PNG, truncado a dieciséis caracteres. Las figuras son **deterministas**:
regenerarlas sin tocar el registro del que leen devuelve el mismo fichero byte a byte, de modo que
una huella distinta significa que el dato de origen cambió.

| Fig. | Experimento | Conjunto | Partición | Notebook | Función o copia | Fichero | Huella (SHA-256, 16) | Ubicación | Pág. PDF |
|---|---|---|---|---|---|---|---|---|---|
| 5.1 | E5, ventanado y reparto | `synthetic_v2` | las tres | `01_exploracion_obd` | `datos.fig_particiones()` | `FIG-5-01_particiones.png` | `6f3d6d68c9cd9198` | cap. 5 · Análisis descriptivo de la muestra | 54 |
| 5.2 | E4, análisis exploratorio | `synthetic_v1` | bloques de 60 s | `01_exploracion_obd` | `datos.fig_separabilidad()` | `FIG-5-02_separabilidad.png` | `bbf28e8e0340d3f0` | cap. 5 · Análisis descriptivo de la muestra | 57 |
| 5.3 | análisis contrafactual T2, derivado de E2 y E5 | `synthetic_v2` | entrenamiento | `06_expresion_del_fallo` | `temporal.fig_forma_del_fallo()` | `FIG-5-03_forma_del_fallo.png` | `3d7cf77bd3a4391b` | cap. 5 · Análisis descriptivo de la muestra | 59 |
| 5.4 | E4 y E5 | `synthetic_v2` | entrenamiento | `01_exploracion_obd` | `mezcla_pobre.fig_mezcla_pobre()` | `FIG-5-04_mezcla_pobre.png` | `8839199cb5fd04f6` | cap. 5 · Análisis descriptivo de la muestra | 62 |
| 5.5 | E6 y E7 | `synthetic_v2` | validación | `02_comparacion_modelos` | `diagnostico.fig_confusiones()` | `FIG-5-05_confusiones.png` | `1b804c53d2272d76` | cap. 5 · PI.1 · Diagnóstico, calibración y atribución | 66 |
| 5.6 | E6 y E7 sobre los dos conjuntos | `synthetic_v2 y synthetic_v3` | validación | `02_comparacion_modelos` | `diagnostico.fig_confusor_de_volumen()` | `FIG-5-06_confusor_volumen.png` | `2294121e76175798` | cap. 5 · PI.1 | 68 |
| 5.7 | E6 | `synthetic_v2` | validación, las 14 ventanas de F03 | `02_comparacion_modelos` | copiada de `FIG-E6-02_limite_evidencia_f03.png` | `FIG-5-07_limite_evidencia_termostato.png` | `e80ea0ab1290c673` | cap. 5 · PI.1 | 69 |
| 5.8 | E6, fase G del diseño de PI.1 | `synthetic_v2` | validación, las 70 ventanas con fallo | `06_expresion_del_fallo` | copiada de `FIG-N06-01_expresion_y_aciertos.png` | `FIG-5-08_expresion_del_fallo.png` | `b7ae3b6b3d88d920` | cap. 5 · PI.1 | 71 |
| 5.9 | E5 y E6 | `synthetic_v2` | entrenamiento, una ventana | `01_exploracion_obd` | `temporal.fig_ventana_y_descriptor()` | `FIG-5-09_ventana_y_descriptor.png` | `31f797dae0785205` | cap. 5 · PI.1 | 73 |
| 5.10 | E6, calibrado en E15 | `synthetic_v2` | validación | `02_comparacion_modelos` | `calibracion.fig_calibracion()` | `FIG-5-10_calibracion.png` | `4a58b07d8124a50d` | cap. 5 · PI.1 | 76 |
| 5.11 | E9, atribución | `synthetic_v2` | validación, 18 casos | `04_explicabilidad` | copiada de `FIG-NB04-01_mapa_atribucion.png` | `FIG-5-11_mapa_atribucion.png` | `7513c9ef7ea5e8dd` | cap. 5 · PI.1 | 78 |
| 5.12 | E12, reejecución canónica | `corpus del vehículo` | 6 casos, 5 puntuados | `no tiene notebook propio` | `recuperacion.fig_recuperacion()` | `FIG-5-12_recuperacion.png` | `1e88235ef0f63fa9` | cap. 5 · PI.2 · Recuperación y trazabilidad | 80 |
| 5.13 | E15, verificador v2.1 | `synthetic_v2` | 17 casos sobre 5 ventanas | `05_suficiencia_y_abstencion` | copiada de `FIG-N05-01_aplicables_vs_cobertura.png` | `FIG-5-13_aplicables_vs_cobertura.png` | `1f3e12cc72c4c7b7` | cap. 5 · PI.3 y PI.4 | 85 |
| 5.14 | E18, cuatro ablaciones | `synthetic_v2` | los mismos 17 casos | `04_explicabilidad` | `ablaciones.fig_ablaciones()` | `FIG-5-14_ablaciones.png` | `f9adce6db2bfb383` | cap. 5 · Contribución de cada componente | 92 |
| 5.15 | E19, tercer intento | `synthetic_v2` | **prueba** | `03_analisis_e19` | copiada de `FIG-NB03-01_primario.png` | `FIG-5-15_evaluacion_final.png` | `1fd19e73ee4e7e0e` | cap. 5 · La evaluación final sobre el conjunto de prueba | 97 |
| 5.16 | E19, tercer intento | `synthetic_v2` | **prueba** | `03_analisis_e19` | copiada de `FIG-NB03-02_decisiones.png` | `FIG-5-16_decisiones_e19.png` | `43466ceaeb89f890` | cap. 5 · La evaluación final sobre el conjunto de prueba | 98 |
| 5.17 | E19, tercer intento | `synthetic_v2` | **prueba** | `03_analisis_e19` | `decision.fig_decisiones_y_umbral()` | `FIG-5-17_decisiones_y_umbral.png` | `1cec118daf16d607` | cap. 5 · La evaluación final sobre el conjunto de prueba | 100 |
| 6.1 | E1–E19 (etiquetas de etapa) | `sin conjunto: es la arquitectura` | — | `00_introduccion` | copiada de `FIG-NB00-01_recorrido.png` | `FIG-6-01_recorrido_experimental.png` | `bc597db112e7b4a6` | cap. 6 · Conclusiones sobre los objetivos | 107 |
| 6.2 | E1–E19 (uno por fila) | `sin conjunto: es documental` | — | `no tiene notebook propio` | `sintesis.fig_objetivos()` | `FIG-6-02_objetivos_y_evidencia.png` | `23b55c185ef7ffbd` | cap. 6 · Conclusiones sobre los objetivos | 112 |
| 6.3 | E15 | `synthetic_v2` | validación | `05_suficiencia_y_abstencion` | `sintesis.fig_compromiso()` | `FIG-6-03_compromiso_cobertura_abstencion.png` | `e482ede01d9ec9da` | cap. 6 · Limitaciones | 117 |
| A.1 | E4 | `synthetic_v1` | sesiones pareadas | `01_exploracion_obd` | copiada de `FIG-E4-01_series_normal_vs_fallo.png` | `FIG-A-01_series_normal_vs_fallo.png` | `4d357282d5e1a58d` | anexo A · §A.6 | 132 |
| A.2 | análisis contrafactual T2, derivado de E2 y E5 | `synthetic_v2` | entrenamiento | `06_expresion_del_fallo` | `temporal.fig_pareja_contrafactual()` | `FIG-A-02_pareja_contrafactual.png` | `d0ff79dd2feb7606` | anexo A · §A.7 | 134 |
| B.1 | E6 y E7 | `synthetic_v2` | validación | `02_comparacion_modelos` | `diagnostico.fig_f1_por_clase()` | `FIG-B-01_f1_por_clase.png` | `b1ac8ba9ea221d31` | anexo B · §B.2 | 138 |

| Fig. | Limitaciones declaradas en su pie |
|---|---|
| 5.1 | describe el diseño, no la dificultad de cada clase |
| 5.2 | ordena pero no explica; `synthetic_v1` no se reconstruye (L-25) |
| 5.3 | una sesión por condición; describe el instrumento, no un motor real |
| 5.4 | efecto descriptivo sin contraste; separabilidad no es rendimiento demostrado |
| 5.5 | una ejecución por modelo, sin repeticiones ni intervalos |
| 5.6 | cambian dos cosas a la vez: volumen y generador; `synthetic_v3` no se reconstruye |
| 5.7 | no regenerable: necesita la predicción por ventana, que E6 no guarda |
| 5.8 | no está comprobado que las cinco ventanas sin señal sean las cinco falladas |
| 5.9 | una ventana como ilustración; en ralentí la caída queda truncada por el suelo físico |
| 5.10 | dos puntos, no una curva de fiabilidad: E6 no guarda la confianza por ventana |
| 5.11 | atribución no es causalidad; solo las diez principales por caso |
| 5.12 | n = 5 casos puntuados: recuentos, no tasas |
| 5.13 | 17 casos de 5 ventanas: no son observaciones independientes |
| 5.14 | A2 quedó INCONCLUSA; denominadores de 9 y de 5 ejecuciones |
| 5.15 | recuentos con intervalo de Wilson; cero observado no es riesgo cero |
| 5.16 | 22 ejecuciones del estrato operativo, que repiten casos |
| 5.17 | observación descriptiva sobre dos errores; el umbral no se revisa a su vista |
| 6.1 | ilustrativa: no es evidencia |
| 6.2 | documental: no es evidencia |
| 6.3 | el compromiso se dibuja sobre 17 casos |
| A.1 | no regenerable: su generador cambió el 1-09-2026 |
| A.2 | una sesión por condición; una desviación observable no implica detectabilidad |
| B.1 | una ejecución por modelo, sin repeticiones |

## 3. Procedencia comprobada, una por una

Lo que sigue es lo que se comprobó antes de aceptar cada figura, no lo que su nombre promete.

- **Las cuatro de E6 y E7** —`5.5`, `5.7`, y las que alimentan `5.6` y `B.1`— se cotejaron **celda a
  celda** contra `artifacts/tables/E6_baseline_confusion_synthetic_v2.csv` y
  `E7_temporal_confusion_synthetic_v2.csv`. Coinciden. La comprobación importaba porque la hora de
  generación en disco de las figuras históricas, las 15:44 del 1 de septiembre de 2026, es anterior
  a la calibración del generador, de las 15:46 del mismo día, y porque esos ficheros se escriben sin
  sufijo de conjunto: el nombre no distingue la ejecución sobre `synthetic_v2` de la ejecución sobre
  `synthetic_v3`. Lo que las identifica es su contenido, y su contenido es el de `synthetic_v2`.
- **`5.7`** conserva información que su propio registro perdió: la predicción **por ventana** de las
  catorce ventanas de F03, que el JSON de E6 no guarda.
- **`5.14`** se contó contra la Tabla 5.6 antes de aceptarla, y de ahí salió una corrección: el
  denominador de la falsa confianza daba 6 en lugar de 9, porque la función excluía por prefijo
  todas las condiciones con distractor. La tabla excluye solo la que llevaba filtro de motor.
- **`5.13`** se contó caso a caso contra `artifacts/tables/E15_suficiencia.csv`, y de ahí salió otra:
  dibujaba catorce de los diecisiete, porque la condición `DISTRACTOR_NO_FILTER` no estaba entre las
  cuatro que seleccionaba, mientras su pie declaraba los diecisiete.
- **`5.2`** se cotejó celda a celda contra `artifacts/tables/E4_separabilidad.csv`, y de ese cotejo
  salió `F-8`: el capítulo nombraba mal uno de los dos fallos invisibles en las medias.
- **`6.1`** y **`6.2`** no tienen conjunto de datos y su pie lo dice con esa palabra: son
  ilustrativa y documental, no evidencia.

## 4. Qué ninguna de estas figuras hace

Ninguna sustituye a su tabla: las cifras publicadas siguen siendo las de las tablas 5.1 a 5.8, y una
figura que discrepara de su tabla sería un defecto de la figura. Ninguna procede de datos simulados
para ilustrar un resultado que no se midió. Ninguna reejecuta nada: el guion que las produce lee
registros congelados. Y ninguna modifica los artefactos históricos: las tres figuras que tenían un
defecto de composición se redibujaron con otro nombre, y la versión anterior se conserva intacta en
`artifacts/figures/`.
