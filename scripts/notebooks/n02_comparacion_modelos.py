"""Construye `02_comparacion_modelos.ipynb`: bosque aleatorio frente a GRU bidireccional."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Comparación de modelos: bosque aleatorio frente a GRU bidireccional

**Notebook** `02_comparacion_modelos` · **versión** 1.1 · **fecha** 14 de noviembre de 2026

| | |
|---|---|
| **Experimentos** | E6 (línea base tabular) y E7 (modelo temporal) |
| **Modalidad** | visualización de evidencia histórica |
| **Conjunto** | `synthetic_v2`, partición de validación · se citan cifras de `synthetic_v3` **marcadas como lo que son** |
| **Protocolo** | el publicado: `E6_v1_bosque_sin_calibrar` y `E7_v1_epoca_sobre_validacion_sin_calibrar` |
| **Estado** | E6 validada; E7 **negativa**, con dos conclusiones retiradas (marcadas `SUPERSEDED`) el 12-10-2026 |
| **Pregunta de investigación** | PI.1: que el diagnóstico a partir de OBD-II supere a la clase mayoritaria y que su confianza se pueda calibrar |
| **Evidencia original** | `experiments/E6_baseline_synthetic_v2.json`, `E7_temporal_synthetic_v2.json`, `artifacts/tables/E6_*.csv`, `E7_*.csv` |

---

## En un minuto

- **Pregunta.** ¿Supera la GRU bidireccional sobre la secuencia cruda al bosque aleatorio sobre 139
  descriptores de ventana? El criterio quedó escrito en E6 antes de medir.
- **Qué se hace.** Se leen los registros de E6 y E7 sobre la partición de validación; no se
  reentrena nada.
- **Resultado.** No: 0,8788 de F1 macro el bosque y 0,8230 la red, −0,0558. Los dos superan
  ampliamente a la clase mayoritaria, 0,0741. **La complejidad añadida del modelo temporal no queda
  justificada en las condiciones evaluadas.**
- **Lectura.** La red solo gana en el termostato, +0,032 sobre 14 ventanas; eso no es evidencia de
  que el contexto temporal aporte.
- **Límite.** Dos recorridos completos, **una sola ejecución**, 98 ventanas. La inversión del orden
  en `synthetic_v3` no se atribuye al volumen: ese conjunto sale de otro generador.

## Cómo leer este notebook

**Modalidad:** visualización de evidencia histórica. Se leen registros y tablas versionados y no se
reentrena nada. **Ejecución:** CPU, sin red, en segundos.

Se comparan **dos recorridos completos y no dos arquitecturas**: cambian a la vez la
**representación** y el **estimador**, así que ninguna diferencia puede atribuirse al contexto
temporal (apartado 3). Por eso esa pregunta sigue abierta.

- **1–3** Introducción, objetivo e hipótesis y fundamento: las dos representaciones y los dos
  estimadores.
- **4–6** Entorno, el conjunto y su partición y las asimetrías del procedimiento.
- **7–10** Resultados agregados y por condición (F1 en 8.1 y área bajo la curva
  precisión-exhaustividad en 8.2), el termostato como límite del generador y las matrices de
  confusión.
- **11–13** Calibración, su forma por tramos y las cifras de `synthetic_v3` como confusor.
- **14–18** Resultados negativos y limitaciones, discusión, conclusiones, reproducibilidad y
  referencias."""),
    md("""\
## 1. Introducción: qué motiva esta comparación

E6 estableció una línea base. Su informe dejó escrito un criterio **antes** de medir nada:

> “Si el modelo temporal no supera la línea base, su complejidad no está justificada.”

El criterio es pre-registrado y no retrospectivo; de él toma sentido E7. La pregunta no era si
una red recurrente funciona (funcionan), sino si **aporta algo** sobre un bosque aleatorio
alimentado con descriptores de ventana, en este problema y con estos datos.

Lo que no sabíamos antes de empezar:

1. Si una representación secuencial captaría firmas que los descriptores agregados pierden.
2. Si la ventaja, de haberla, sería uniforme o se concentraría en condiciones concretas.
3. Si la confianza de los dos modelos sería comparable, condición para usarla después como
   criterio de abstención."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Medir si el recorrido secuencial supera al tabular en diagnóstico sobre ventanas de
OBD-II y caracterizar **dónde** difieren.

**Hipótesis pre-registrada (E6, antes de medir E7).** El modelo temporal supera a la línea base en
F1 macro sobre validación.

**Variables observadas.** F1 macro, exactitud, F1 por clase, matriz de confusión y error de
calibración, todo sobre la misma partición de validación.

**Criterio de evaluación.** El de E6, citado arriba. No hay umbral de margen mínimo y no se inventa uno ahora.

**Qué cuestionaría la hipótesis.** Un F1 macro de la red igual o inferior al del bosque. Eso es lo
que ocurrió."""),
    md("""\
## 3. Fundamento: las dos representaciones y los dos estimadores

Esta sección permite leer el resto: dos representaciones y dos estimadores.

### 3.1 La representación tabular: 139 descriptores de ventana

Cada ventana de 120 segundos y 12 señales (1 440 valores) se resume en **139 números**:

| Familia | Descriptores | Cuántos |
|---|---|---|
| Nivel | `mean` | 12 |
| Dispersión y extremos | `std`, `min`, `max`, `range` | 48 |
| Dinámica intraventana | `slope`, `autocorr1`, `delta_min`, `delta_max`, `crossings`, `n_events` | 72 |
| Razón entre señales | `maf_over_rpm_load` | 1 |
| Correlación cruzada | `corr_*` | 6 |

La tercera fila importa: **la representación tabular no es estática**. Setenta y dos de
los 139 descriptores son dinámica dentro de la ventana: pendiente, autocorrelación, número de cruces,
número de eventos. Decir que el bosque “no ve el tiempo” sería inexacto: ve una descripción resumida
de él. Lo que no ve es el **orden** de las muestras más allá de lo que esos resúmenes capturan.

### 3.2 La representación secuencial: 120 × 12 en crudo

La red recibe la matriz completa, normalizada señal a señal. No hay pérdida de información por
resumen; el coste es que tiene que aprender qué mirar.

### 3.3 Bosque aleatorio

Cuatrocientos árboles, `class_weight="balanced"`, semilla 20260901. *Por qué este estimador como
línea base:* tolera bien descriptores correlacionados (y aquí lo están mucho), no necesita escalado
y con pocos cientos de ventanas es más estable que casi cualquier alternativa.

### 3.4 GRU bidireccional

19 014 parámetros. *Por qué bidireccional:* la ventana está completa cuando se clasifica, no llega en
tiempo real, así que leerla en los dos sentidos es legítimo y permite que el estado final recoja
información de todo el tramo. *Por qué GRU y no LSTM:* menos parámetros con desempeño comparable;
con ventanas de este tamaño la diferencia entre las dos arquitecturas no es lo que limita.

### 3.5 Por qué la comparación no aísla el contexto temporal

| | Representación | Estimador |
|---|---|---|
| **Recorrido A** (E6) | 139 descriptores | bosque aleatorio |
| **Recorrido B** (E7) | secuencia 120 × 12 | GRU bidireccional |

Las dos columnas cambian a la vez. Para atribuir una diferencia al contexto temporal haría falta
mantener una fija y mover la otra (un diseño factorial) y eso **no se hizo** y no se propone hacer,
porque ampliaría el alcance del trabajo. Lo que sí está diseñado, con el estimador fijo, es una
escalera de ablación de la representación: `docs/diseno-pi1/07-ablacion-representacion.md`, **no
ejecutada**."""),
    md("""\
## 4. Preparación del entorno"""),
    code(PREAMBULO),
    code("""\
soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "las cifras se leen de experiments/E6_*.json y E7_*.json y de artifacts/tables/; "
    "no se reentrena ningún modelo. La red se entrenó sobre MPS, cuyas reducciones no son "
    "bit a bit deterministas: reentrenarla aquí daría un número distinto del publicado y "
    "parecería una contradicción donde solo hay no-determinismo del dispositivo",
)"""),
    md("""\
## 5. El conjunto y su partición

`synthetic_v2`: 72 sesiones, 43 200 muestras, seis condiciones equilibradas. Ventanas de 120 s con
paso de 60 s. El reparto es **por sesión**, nunca por ventana.

Un segundo conjunto, `synthetic_v3`, con 216 sesiones, aparece en el informe de E7. **No sale del
mismo generador**: sus cifras van **marcadas** en el apartado 13."""),
    code("""\
import pandas as pd

reparto = soporte.tabla("E5_reparto")
resumen_particion = reparto.groupby("partition")[["sessions", "windows"]].sum()
resumen_particion["% ventanas"] = (
    100 * resumen_particion.windows / resumen_particion.windows.sum()
).round(1)
print("Reparto de synthetic_v2, por sesión (fuente: artifacts/tables/E5_reparto.csv)")
print(resumen_particion.to_string())
print()
print("El conjunto de prueba permaneció CERRADO hasta E19, el 12 de octubre de 2026.")
print("E6 y E7 se midieron sobre validación y así se reportan.")"""),
    md("""\
## 6. Metodología: qué se fijó antes y qué se decidió después

**Decisiones pre-registradas**, escritas antes de medir:

- El criterio de aceptación de E7, en el informe de E6.
- La semilla, 20260901, común a todo el laboratorio.
- El reparto por sesión y el tamaño de ventana, fijados en E5 con su estudio.
- Las métricas que se publican.

**Decisiones del procedimiento que hoy se reconocen como asimétricas** (no eran decisiones
exploratorias, pero condicionan la comparación y no estaban declaradas en su momento):

1. **La época de la red se elige mirando la misma validación sobre la que se reporta.** El bosque no
   tiene paso de selección equivalente. La red llega a la medición habiendo elegido su mejor momento
   contra el conjunto que la mide; el bosque, no. La asimetría **favorece a la red**. Aun así, la
   red pierde, lo que hace el resultado más robusto de lo que sería al revés.
2. **Ninguno de los dos calibra.** Los dos reportan su error de calibración sobre `predict_proba` en
   crudo. La diferencia de ECE entre ellos no es, por tanto, una diferencia entre calibradores.

Las dos se corrigen en el protocolo de PI.1, con tres particiones internas. Ese protocolo **no se ha
ejecutado**; cuando se ejecute, escribirá con etiqueta propia sin sustituir estas cifras."""),
    md("""\
## 7. Resultados agregados

**Qué queremos investigar.** Si la red supera al bosque en F1 macro, la métrica del criterio; lo
que cuenta es el signo de la diferencia.
**Qué datos utilizamos.** Los dos registros JSON, sin recalcular nada.
**Qué variables se representan.** F1 macro, exactitud y ECE."""),
    code("""\
e6 = soporte.registro("E6_baseline_synthetic_v2")
e7 = soporte.registro("E7_temporal_synthetic_v2")

agregado = pd.DataFrame(
    {
        "bosque aleatorio (E6)": {
            "F1 macro": e6["metrics"]["macro_f1"],
            "exactitud": e6["metrics"]["accuracy"],
            "F1 ponderado": e6["metrics"]["weighted_f1"],
            "ECE": e6["metrics"]["calibration"]["ece"],
            "confianza media": e6["metrics"]["calibration"]["mean_confidence"],
        },
        "GRU bidireccional (E7)": {
            "F1 macro": e7["metrics"]["macro_f1"],
            "exactitud": e7["metrics"]["accuracy"],
            "F1 ponderado": e7["metrics"]["weighted_f1"],
            "ECE": e7["metrics"]["calibration"]["ece"],
            "confianza media": e7["metrics"]["calibration"]["mean_confidence"],
        },
        "clase mayoritaria": {
            "F1 macro": e6["majority_baseline"]["macro_f1"],
            "exactitud": e6["majority_baseline"]["accuracy"],
            "F1 ponderado": e6["majority_baseline"]["weighted_f1"],
            "ECE": float("nan"),
            "confianza media": float("nan"),
        },
    }
).T
agregado.round(4)"""),
    code("""\
import matplotlib.pyplot as plt
import numpy as np

from mecanico_ia_exp.visualization.style import CATEGORICAL, apply_style

apply_style()

METRICAS = ["F1 macro", "exactitud", "ECE"]
MODELOS = ["bosque aleatorio (E6)", "GRU bidireccional (E7)"]

fig, ejes = plt.subplots(1, 3, figsize=(9.6, 3.3))
for eje, metrica in zip(ejes, METRICAS, strict=False):
    valores = [agregado.loc[m, metrica] for m in MODELOS]
    barras = eje.bar(["bosque", "GRU"], valores,
                     color=[CATEGORICAL[0], CATEGORICAL[1]], width=0.55)
    for barra, valor in zip(barras, valores, strict=False):
        eje.text(barra.get_x() + barra.get_width() / 2, valor + 0.012,
                 f"{valor:.4f}", ha="center", fontsize=7.5, fontweight="bold")
    if metrica != "ECE":
        mayoritaria = agregado.loc["clase mayoritaria", metrica]
        eje.axhline(mayoritaria, color="#898781", linestyle=":", linewidth=1.0)
        eje.text(-0.45, mayoritaria + 0.015, f"clase mayoritaria {mayoritaria:.3f}",
                 fontsize=6.5, color="#52514e")
    eje.set_title(metrica, fontsize=9)
    eje.set_ylim(0, max(valores) * 1.28)
    eje.set_ylabel("valor (adimensional, 0–1)" if metrica == METRICAS[0] else "")

fig.suptitle(
    "E6 frente a E7 sobre validación: el modelo temporal no supera a la línea base",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "synthetic_v2 · partición de validación, 98 ventanas · "
    "fuente: experiments/E6_baseline_synthetic_v2.json y E7_temporal_synthetic_v2.json · "
    "en ECE, menos es mejor",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-01_agregado", subdirectorio="02_comparacion_modelos")
plt.show()

print(f"diferencia en F1 macro (GRU − bosque): "
      f"{e7['metrics']['macro_f1'] - e6['metrics']['macro_f1']:+.4f}")"""),
    md("""\
**Qué muestra.** El bosque obtiene 0,8788 de F1 macro y la red 0,8230: una diferencia de −0,0558 en
contra de la red. Los dos superan ampliamente a la clase mayoritaria, 0,0741. En error de
calibración la red sale algo mejor, 0,1317 frente a 0,1439.

**Qué podemos interpretar.** El criterio pre-registrado en E6 se resuelve en contra de la hipótesis:
**la complejidad añadida del modelo temporal no queda justificada en las condiciones evaluadas**. Es
un resultado negativo y se reporta como tal.

Que los dos superen a la clase mayoritaria por un orden de magnitud en F1 macro sí responde a lo
que PI.1 pide. Ese suelo es artificialmente bajo, porque la mayoritaria solo acierta una clase; en
exactitud la distancia es menor y sigue siendo amplia: 0,286 frente a 0,878 del bosque.

**Qué no podemos afirmar.**

1. **Que la red sea peor arquitectura.** Lo medido es un recorrido completo contra otro (apartado 3).
2. **Que la diferencia de ECE favorezca a la red por calibrar mejor.** Ninguno de los dos calibra
   (apartado 6): la red tiene algo menos de error por tramos, no una probabilidad mejor ajustada
   tras calibrar. El ECE no lleva signo: los dos
   modelos fallan hacia lados distintos, como se ve en el apartado 11.
3. **Que la diferencia sea significativa.** Es **una sola ejecución** sobre 98 ventanas de
   validación, sin repeticiones ni intervalo de confianza (apartado 14.2)."""),
    md("""\
## 8. Resultados por condición: donde la media esconde lo interesante

### 8.1 F1 por condición

**Qué queremos investigar.** Si la desventaja de la red es uniforme o se concentra; se mira el
signo de la diferencia clase a clase además de su tamaño.
**Qué datos utilizamos.** El F1 por clase de los dos registros."""),
    code("""\
por_clase = pd.DataFrame(
    {
        "bosque": {d["label"]: d["f1"] for d in e6["metrics"]["per_class"]},
        "GRU": {d["label"]: d["f1"] for d in e7["metrics"]["per_class"]},
        "ventanas": {d["label"]: d["support"] for d in e6["metrics"]["per_class"]},
    }
)
por_clase["diferencia"] = por_clase["GRU"] - por_clase["bosque"]
por_clase.round(4)"""),
    code("""\
# La figura la dibuja la función científica del proyecto, que lee las mismas
# tablas por clase que acaba de leerse arriba. No se redibuja aquí: una segunda
# implementación de la misma figura es una segunda verdad.
from mecanico_ia_exp.visualization.memoria import fig_f1_por_clase
from mecanico_ia_exp.visualization.memoria.base import CONDICION

fig = fig_f1_por_clase()
# Rótulos añadidos en el notebook, sin tocar los datos: el panel (b) usa el mismo
# orden de filas que el (a), así que se le copian los nombres de condición.
eje_a, eje_b = fig.axes
eje_a.set_title("(a) F1 de cada condición en los dos modelos", fontsize=9,
                fontweight="bold", loc="left", pad=6)
eje_b.set_title("(b) Diferencia de F1, red menos bosque (positivo: gana la red)",
                fontsize=9, fontweight="bold", loc="left", pad=6)
eje_b.set_yticks(eje_a.get_yticks())
eje_b.set_yticklabels([t.get_text().split("\\n")[0] for t in eje_a.get_yticklabels()],
                      fontsize=7)
fig.tight_layout()
fig.suptitle(
    "F1 por condición sobre validación: bosque aleatorio (E6) frente a GRU bidireccional (E7)",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
soporte.exportar(fig, "FIG-NB02-02_por_clase", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** La red pierde en cinco de las seis condiciones y gana en una: el **termostato
bloqueado**, 0,8148 frente a 0,7826, una diferencia de +0,032. Las pérdidas mayores están en el
fallo de encendido (−0,167) y en la deriva del caudalímetro (−0,077); la clase sin fallo pierde
−0,054.

**Qué podemos interpretar.** Que la métrica agregada esconde comportamientos distintos y que la
condición donde la red gana es aquella cuya firma es temporal en un sentido fuerte:
“algo que debería subir y no sube”.

**Qué no podemos afirmar.** Que esa única victoria sea evidencia de que el contexto temporal
aporta. Leerla así sería un error, por cuatro razones acumulativas:

1. Es **+0,032 sobre 14 ventanas** de validación. Una sola ventana cambiada mueve la cifra mucho más
   que eso.
2. Es **una sola ejecución**, sin repeticiones ni intervalo.
3. Los dos recorridos difieren en **representación y estimador** a la vez.
4. Hay una **explicación alternativa medida**: el fallo del termostato no altera la trayectoria
   mientras el refrigerante no supera su tope; en la sesión de calentamiento de validación, eso
   deja cinco de sus siete ventanas sin ninguna señal (notebook 06, apartado 8). Los errores de los dos modelos en esta clase podrían
   concentrarse ahí; entonces, la diferencia mediría cómo cada uno trata ventanas **sin
   información**, que no es lo mismo que medir sensibilidad temporal.

El cruce que distinguiría las dos explicaciones (predicción por ventana contra expresión por
ventana) está diseñado y **no ejecutado**: `docs/diseno-pi1/08-analisis-por-fallo.md`.

Una observación de signo contrario: la red pierde por 0,167 en el **fallo de encendido**, la
otra condición con estructura temporal marcada (episodios breves). Si la ventaja de la red viniera
de su capacidad de modelar el tiempo, cabría esperar que ganara también ahí."""),
    md("""\
### 8.2 Área bajo la curva precisión-exhaustividad por condición

**Qué queremos investigar.** Si la diferencia por condición depende del corte con el que cada modelo
decide o aparece también en cómo **ordena** sus probabilidades. El F1 mide la clase que el modelo
elige; el área bajo la curva precisión-exhaustividad (PR-AUC) mide, para cada condición tratada
contra todas las demás, si las ventanas de esa condición reciben más probabilidad que el resto, sin
fijar ningún umbral.

**Qué datos utilizamos.** El campo `metrics.per_class[*].pr_auc` de los dos registros, tal como se
guardó. El laboratorio la calcula con `average_precision_score` de scikit-learn, que estima el área
como una suma por escalones (la precisión media) y no por trapecios.

**Por qué PR-AUC y no el área bajo la curva ROC.** Tratada contra todas las demás, cada condición es
minoritaria (14 o 28 de 98 ventanas) y el ROC se deja engañar por la clase abundante: la tasa de
falsos positivos se divide por todas las ventanas negativas, de modo que muchos falsos positivos
apenas la mueven. Es la razón que deja escrita el propio código del laboratorio
(`src/mecanico_ia_exp/evaluation/metrics.py`).

**Por qué no se dibujan las curvas.** Los registros de E6 y E7 **no conservan las probabilidades por
ventana**: guardan solo el área de cada clase. Sin esas probabilidades la curva no se puede
reconstruir, de modo que aquí se muestra el área y no la curva.

**Referencia.** Un clasificador sin información obtiene, en promedio, una precisión media cercana a
la proporción de la clase en la partición: 28/98 para la clase sin fallo y 14/98 para cada fallo. Se
calcula aquí a partir del soporte que guarda el registro."""),
    code("""\
pr_auc = pd.DataFrame(
    {
        "bosque (E6)": {d["label"]: d["pr_auc"] for d in e6["metrics"]["per_class"]},
        "GRU (E7)": {d["label"]: d["pr_auc"] for d in e7["metrics"]["per_class"]},
        "ventanas": {d["label"]: d["support"] for d in e6["metrics"]["per_class"]},
    }
)
pr_auc["diferencia"] = pr_auc["GRU (E7)"] - pr_auc["bosque (E6)"]
pr_auc["proporción de la clase"] = pr_auc["ventanas"] / pr_auc["ventanas"].sum()
pr_auc.round(4)"""),
    code("""\
fig, eje = plt.subplots(figsize=(9.6, 3.8))
x = np.arange(len(pr_auc))
for desplazamiento, columna, color, etiqueta in (
    (-0.19, "bosque (E6)", CATEGORICAL[0], "bosque aleatorio (E6)"),
    (0.19, "GRU (E7)", CATEGORICAL[1], "GRU bidireccional (E7)"),
):
    eje.bar(x + desplazamiento, pr_auc[columna], width=0.36, color=color, label=etiqueta)
    for xi, valor in zip(x + desplazamiento, pr_auc[columna], strict=True):
        eje.text(xi, valor + 0.015, f"{valor:.3f}".replace(".", ","),
                 ha="center", fontsize=6.8)
eje.hlines(pr_auc["proporción de la clase"], x - 0.42, x + 0.42, colors="#52514e",
           linestyles=":", linewidth=1.2,
           label="proporción de la clase (clasificador sin información)")
eje.set_xticks(x, [f"{c.split('_')[0]}\\n{CONDICION[c]}" for c in pr_auc.index], fontsize=7.5)
eje.set_ylabel("PR-AUC de la condición contra\\nel resto (precisión media, 0–1)")
eje.set_ylim(0, 1.32)
eje.set_yticks(np.arange(0, 1.01, 0.2))
eje.legend(loc="upper center", ncols=3, fontsize=7)
fig.suptitle(
    "Área bajo la curva precisión-exhaustividad por condición: bosque (E6) frente a GRU (E7)",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "synthetic_v2 · validación, 98 ventanas · fuente: metrics.per_class[*].pr_auc de "
    "E6_baseline_synthetic_v2.json y E7_temporal_synthetic_v2.json · solo el área: los registros "
    "no guardan las probabilidades por ventana y la curva no puede dibujarse",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-07_pr_auc", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** El bosque alcanza un área de 1,000 en tres condiciones: la fuga de vacío, la deriva
del caudalímetro y la sonda lenta. La red llega a 1,000 solo en la sonda lenta. La red supera al
bosque en una condición, el **termostato bloqueado** (0,922 frente a 0,832, +0,089), empata en la
sonda lenta y pierde en las otras cuatro. Las pérdidas mayores están en el **fallo de encendido**
(0,526 frente a 0,834, −0,308) y en la clase **sin fallo** (0,577 frente a 0,778, −0,201). Todas las
áreas quedan muy por encima de la proporción de su clase, 0,143 para cada fallo y 0,286 sin fallo.

**Qué podemos interpretar.** El reparto se parece al del F1 del apartado 8.1 en dos cosas: la única
condición en que gana la red es la misma y su mayor pérdida también (el fallo de encendido). La
segunda pérdida no coincide: en el área es la clase sin fallo y en el F1 la deriva del caudalímetro.
Como el área no depende de ningún
umbral de decisión, la desventaja de la red en el fallo de encendido y en la clase sin fallo no es
solo efecto de quedarse con la clase más probable: también **ordena peor** las ventanas de esas
condiciones. Un área de 1,000 en el bosque significa que en esa partición todas las ventanas de la
condición reciben más probabilidad que cualquier ventana de otra.

**Qué no podemos afirmar.**

1. **Que las diferencias sean significativas.** Es una sola ejecución con 14 ventanas por fallo y 28
   sin fallo, sin repeticiones ni intervalo; las mismas reservas del apartado 8.1 valen aquí.
2. **Que la ventaja de la red en el termostato muestre que el contexto temporal aporta.** Sigue
   expuesta a la explicación alternativa de las ventanas sin señal (apartado 9).
3. **Nada sobre la forma de la curva** ni sobre un punto de operación concreto: los registros solo
   guardan el área. Dos curvas muy distintas pueden tener la misma área.
4. **Que un área alta implique una probabilidad bien calibrada.** El área mide el orden de las
   probabilidades y no su valor; la calibración se trata en el apartado 11."""),
    md("""\
## 9. El termostato: un límite del generador, no un fallo de aprendizaje

**Qué queremos investigar.** **Por qué** el bosque falla en el termostato, porque la respuesta no
es la que se espera de un modelo que falla. La expresión del fallo en la
señal, ventana a ventana, se mide en el notebook 06.

**Qué datos utilizamos.** Una figura que es un **artefacto histórico**: se produjo durante la ejecución
de E6 y conserva la predicción **ventana a ventana**, que el registro guardado de E6 no almacena. No
se puede regenerar hoy: reproducirla exigiría reejecutar el modelo conservando la predicción de cada
ventana, lo que convertiría una figura en un experimento nuevo. Se muestra tal como se publicó."""),
    code("""\
from IPython.display import Image, display

display(Image(filename=str(soporte.figura("FIG-E6-02_limite_evidencia_f03")), width=760))"""),
    md("""\
**Qué muestra.** Las catorce ventanas de termostato bloqueado de validación, situadas por la
temperatura media del refrigerante y señalando cuáles acertó el modelo. Las **cinco no detectadas**
están todas por debajo del techo de 71 °C que el fallo impone; las nueve detectadas se agrupan junto
a él.

**Qué podemos interpretar.** Solo una coincidencia de recuentos: cinco ventanas falladas y cinco
ventanas sin señal del fallo. Que la señal averiada sea idéntica a la sana mientras el motor no
alcanza el tope es una propiedad del **generador**, tal como la ficha del fallo la declara; no de
los termostatos reales. Su medición ventana a ventana está en el notebook 06, apartado 8.

**Qué no podemos afirmar.** Que las cinco ventanas sin señal sean las mismas cinco falladas.
Como los registros de E6 no guardan la predicción por ventana, la coincidencia de los dos recuentos
es **aritmética y no una identidad medida**.

**Relación con la pregunta de investigación.** Separa dos cosas que una tasa de acierto confunde: la etiqueta de un
caso y la evidencia disponible en él. Es la misma distinción que el verificador de suficiencia
aplica después sobre la evidencia documental; por eso importa para PI.1 y para PI.3."""),
    md("""\
## 10. Matrices de confusión: qué tipo de error comete cada uno

**Qué queremos investigar.** No cuántos errores, sino **hacia dónde** van. En diagnóstico no es lo
mismo decir “no hay fallo” cuando lo hay que confundir un fallo con otro: lo segundo manda al
mecánico a desmontar la pieza equivocada."""),
    code("""\
# Las dos matrices, leídas de sus tablas versionadas: son los datos que la
# figura dibuja y los que la celda siguiente vuelve a usar.
confusion_e6 = soporte.tabla("E6_baseline_confusion_synthetic_v2").set_index("Unnamed: 0")
confusion_e7 = soporte.tabla("E7_temporal_confusion_synthetic_v2").set_index("Unnamed: 0")
print(confusion_e6.to_string())

from mecanico_ia_exp.visualization.memoria import fig_confusiones

fig = fig_confusiones()
# Rótulos añadidos en el notebook: qué modelo es cada panel y el nombre de cada
# código de condición. Los recuentos y los colores son los de la función.
for eje, titulo in zip(
    fig.axes, ["(a) Bosque aleatorio, E6", "(b) Red recurrente GRU, E7"], strict=True
):
    eje.set_title(titulo, fontsize=9, fontweight="bold", loc="left", pad=6)
    eje.set_yticklabels(
        [f"{c.split('_')[0]} {CONDICION[c]}" for c in confusion_e6.index], fontsize=7
    )
    eje.set_ylabel("condición anotada")
fig.tight_layout()
fig.suptitle(
    "Matrices de confusión sobre validación: adónde van los errores de cada modelo",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.005,
    "Cifras: número de ventanas (98 por modelo). Color: fracción de la fila. "
    "Columnas: " + " · ".join(f"{c.split('_')[0]} {n}" for c, n in CONDICION.items()),
    fontsize=6.5, ha="left", va="top", wrap=True,
)
soporte.exportar(fig, "FIG-NB02-03_confusion", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    code("""\
# Dos preguntas concretas sobre la estructura del error, respondidas con las
# matrices: ¿cuántos errores van a la clase sin fallo y cuántos cruzan de un fallo
# a otro? La segunda es la que importa en un taller.
def estructura_del_error(matriz: pd.DataFrame, nombre: str) -> dict[str, object]:
    total = matriz.to_numpy().sum()
    aciertos = int(np.trace(matriz.to_numpy()))
    hacia_normal = int(matriz.loc[matriz.index != "F00_normal", "F00_normal"].sum())
    con_fallo = matriz.loc[matriz.index != "F00_normal"]
    cruzados = int(
        con_fallo.drop(columns=["F00_normal"]).to_numpy().sum()
        - np.trace(con_fallo.drop(columns=["F00_normal"]).to_numpy())
    )
    falsas_alarmas = int(matriz.loc["F00_normal"].drop("F00_normal").sum())
    return {
        "modelo": nombre,
        "ventanas": int(total),
        "errores": int(total - aciertos),
        "fallo → sin fallo (omisión)": hacia_normal,
        "fallo → otro fallo (cruzado)": cruzados,
        "sin fallo → fallo (falsa alarma)": falsas_alarmas,
    }

pd.DataFrame([
    estructura_del_error(confusion_e6, "bosque (E6)"),
    estructura_del_error(confusion_e7, "GRU (E7)"),
]).set_index("modelo")"""),
    md("""\
**Qué muestra.** El bosque concentra sus errores en la omisión: casi todos van a *sin fallo*. La red
reparte más y genera algún diagnóstico cruzado que el bosque no genera.

**Qué podemos interpretar.** Para el uso que este trabajo persigue, **la estructura del error del
bosque es preferible a la de la red**, con independencia del F1. Un error por omisión deja el
problema sin diagnosticar; un diagnóstico cruzado produce una hipótesis **confiada y equivocada**,
el modo de fallo que el criterio de suficiencia existe para evitar. Que el bosque falle “hacia
abajo” no es mérito suyo. Las clases difíciles carecen de señal en parte de sus ventanas y la clase
sin fallo es la respuesta por defecto cuando no se ve nada.

**Qué no podemos afirmar.** Que la estructura del error del bosque sea benigna **en general**: vale
para este conjunto y esta partición, con 98 ventanas. Con otro reparto de clases, o
con fallos que compartieran firma, la estructura podría ser otra. Tampoco se puede afirmar nada
sobre el coste relativo de los dos tipos de error sin un criterio de coste, que este trabajo no
define."""),
    md("""\
## 11. Calibración: por qué importa aquí más que en otros problemas

Todo el criterio de abstención compara la confianza del modelo contra un umbral. Si la confianza
estuviera mal calibrada, el umbral no significaría nada.

**ECE (*expected calibration error*).** Se agrupan las predicciones en diez tramos según su
confianza. En cada tramo se compara la confianza media con el acierto real. El ECE es la media de
esas diferencias, ponderada por cuántas predicciones hay en cada tramo. Un ECE de 0,14 quiere decir
que, de media, el modelo se desvía catorce puntos de lo que su confianza prometía.

**Sesgo de confianza.** La diferencia entre confianza media y acierto, con signo. Positivo quiere
decir que el modelo promete más de lo que cumple; negativo, que promete menos. A diferencia del ECE,
que es un promedio de valores absolutos por tramo, el sesgo puede ser casi nulo aunque los tramos
fallen mucho, si fallan en direcciones opuestas."""),
    code("""\
calibracion = pd.DataFrame(
    {
        "bosque (E6)": e6["metrics"]["calibration"],
        "GRU (E7)": e7["metrics"]["calibration"],
    }
).T
calibracion.round(4)"""),
    md("""\
**Qué queremos investigar.** Si la confianza que el modelo declara coincide con el acierto
que obtiene y **en qué dirección** se desvía si no coincide. La dirección decide qué habría pasado
de haber puesto el umbral del verificador sobre la probabilidad cruda.

**Qué datos utilizamos.** Las 98 ventanas de validación de `synthetic_v2`, con la confianza declarada
por el bosque antes y después de calibrar por regresión isotónica ajustada con validación cruzada
**sobre entrenamiento**, nunca sobre validación. No se reentrena nada: las dos configuraciones están
registradas."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_calibracion

fig = fig_calibracion()
fig.suptitle(
    "Bosque aleatorio (E6) sobre validación: confianza media frente a acierto, "
    "sin calibrar y calibrado",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.005,
    "Cada marca resume las 98 ventanas de validación. Línea punteada: calibración perfecta. "
    "Fuente: experiments/E15_suficiencia.json, campo calibration.",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB02-04_calibracion", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
> **Corrección del 13 de octubre de 2026.** Esta figura se titulaba “Los dos prometen más de lo que
> cumplen” y el párrafo siguiente decía que los dos modelos caen por debajo de la diagonal. Es falso
> para el bosque y lo contrario de lo que el registro guarda. El error se detectó al verificar la
> procedencia de las figuras candidatas a entrar en la memoria. El capítulo 5 no lo heredó: su
> redacción siempre dijo que el modelo estaba infraconfiado.

**Qué muestra.** Dos puntos, los dos del bosque (`E15_suficiencia.json`, campo `calibration`). Sin
calibrar queda **por encima** de la diagonal: acierta el 87,8 % de las ventanas declarando una
confianza media de 0,738, de modo que **promete menos de lo que cumple**; su sesgo, la confianza
media menos el acierto, vale −0,1395, con un ECE de 0,1439. Calibrado, el acierto no cambia y la
confianza media sube a 0,886: queda apenas por debajo de la diagonal, con sesgo +0,0089 y ECE 0,0854.
La red no está en la figura; sus cifras, sin calibrar, son las de la tabla anterior: sesgo +0,0070
y ECE 0,1317.

**Qué podemos interpretar.** Que el sesgo y el ECE miden cosas distintas, como se definió arriba.
Que la red tenga un sesgo casi nulo y a la vez un ECE de 0,1317 significa que sus tramos fallan en
direcciones opuestas y se cancelan al promediar. Ninguno de los dos modelos en crudo puede usarse,
por tanto, como criterio de abstención, que es la razón por la que el recorrido de diagnóstico
**calibra antes de decidir**. En el caso del bosque la dirección importa además por sí misma: un
umbral sobre la confianza cruda habría hecho que el sistema se abstuviera de más de la cuenta. Eso
habría parecido prudencia cuando era mala medición.

**Qué no podemos afirmar.** Que la red esté mejor calibrada **que el bosque calibrado**: la red no
se calibró. Tampoco que el bosque sin calibrar esté bien calibrado porque su sesgo sea negativo: un ECE de 0,1439 dice que los tramos fallan; el signo solo dice hacia dónde fallan
en promedio. Tampoco que el ECE sea estable: con diez tramos y 98 ventanas, cada tramo contiene muy
pocas predicciones y la cifra es frágil. Un solo punto por modelo no muestra en qué
tramos se concentra el error, que es lo que más importaría. Los registros de E6 y E7 **no guardan la confianza por ventana**, de modo que un
diagrama de fiabilidad no puede construirse a partir de ellos. El apartado siguiente lo construye
por otra vía."""),
    md("""\
## 12. La forma de la calibración, recuperada de la curva del barrido

**Qué queremos investigar.** **En qué tramos de confianza** se concentra el desajuste del
modelo calibrado, lo que decide si el umbral del verificador opera en una zona fiable.

**Qué datos utilizamos.** La curva acumulada del barrido del umbral,
`E15b_barrido_umbral.json`: 101 umbrales con, en cada uno, cuántas de las 98 ventanas de validación quedan por encima y con qué precisión se decide entre
ellas. Restando dos umbrales consecutivos salen el número de ventanas y el número de aciertos del
tramo que hay entre ellos.

La reconstrucción solo vale si reproduce lo que el registro del modelo publica. Se comprueba antes
de dibujar nada."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import (
    agrupar,
    comprobacion_de_la_reconstruccion,
    intervalos_de_fiabilidad,
)

comprobacion = comprobacion_de_la_reconstruccion()
pd.Series(comprobacion)"""),
    md("""\
**Qué muestra.** La suma de los tramos recuperados devuelve **98 ventanas y 86
aciertos**, repartidos en 32 tramos de una centésima más la cola de las ventanas cuya confianza
calibrada es 1,0. La exactitud que producen, **0,877551**, coincide dígito a dígito con
la del registro del modelo. La reconstrucción es aritmética exacta sobre una curva acumulada y no
una estimación.

Los tramos de una centésima son exactos y **no se pueden dibujar**: con 98 ventanas repartidas en
33, casi todos contienen una sola y su proporción solo puede valer 0 o 1. Agrupar de cinco en cinco
centésimas es suma de enteros y no pierde exactitud."""),
    code("""\
pd.DataFrame(
    [
        {
            "desde": round(i.desde, 2),
            "hasta": round(i.hasta, 2),
            "ventanas": i.ventanas,
            "aciertos": i.aciertos,
            "exactitud": round(i.exactitud, 3),
        }
        for i in agrupar()
    ]
)"""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_fiabilidad

fig = fig_fiabilidad()
arriba, abajo = fig.axes
arriba.set_title("(a) Acierto observado en cada tramo de confianza calibrada",
                 fontsize=9, fontweight="bold", loc="left", pad=6)
abajo.set_title("(b) Ventanas en cada tramo (gris claro: cuatro o menos)",
                fontsize=9, fontweight="bold", loc="left", pad=6)
fig.tight_layout()
fig.suptitle(
    "Diagrama de fiabilidad del bosque calibrado (E6) sobre validación",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.005,
    "Tramos de 0,05 reconstruidos de experiments/E15b_barrido_umbral.json. "
    "La cifra sobre cada barra es el número de ventanas del tramo.",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB02-05_fiabilidad", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** Los cuatro tramos por encima de 0,80 reúnen **81 de las 98 ventanas**. Los dos
inferiores (0,80–0,90, 21 ventanas) aciertan todas y quedan por encima de la diagonal. Los dos
superiores (0,90–1,00, **60 ventanas**) aciertan 0,864 y 0,947 y quedan **ligeramente por debajo**:
donde se concentran las predicciones, el calibrado promete unos pocos puntos más de lo que cumple.
Por debajo de 0,80 hay siete tramos con cuatro ventanas o menos, cuya proporción salta entre 0 y 1
porque está calculada sobre una o dos observaciones.

**Qué podemos interpretar.** Que el umbral de suficiencia, 0,79, cae en la frontera entre la
zona poblada y la zona vacía de la distribución de confianza. Eso hace defendible una
abstención por confianza baja: por encima del umbral el desvío es de pocos puntos y en el sentido
de prometer algo más de lo que se cumple; por debajo, no hay observaciones suficientes para afirmar
nada. Por eso la confianza alta no basta para explicar: en E19, los dos diagnósticos erróneos con
evidencia completa tenían confianza 0,908 y 0,966 y los paró la cobertura de afirmaciones
(notebook `03_analisis_e19`, apartado 10).

**Qué no podemos afirmar.** La reconstrucción **no conserva la confianza media dentro
de cada tramo**: solo sus bordes, de modo que cada barra ocupa su tramo y no se sitúa en un punto.
Solo existe para la confianza **calibrada**; la anterior a calibrar no se guardó por ventana y su
diagrama no puede dibujarse. **De aquí no sale un error de calibración esperado**: agrupar de otro
modo da otro número. El que vale sigue siendo el del registro, calculado sobre diez tramos. Poner
los dos juntos invitaría a leer una corrección donde solo hay otro agrupamiento."""),
    md("""\
## 13. Las cifras de `synthetic_v3` y por qué no cierran la cuestión

El informe de E7 publicó también resultados sobre `synthetic_v3` (con el triple de sesiones) y
concluyó que el límite era el volumen de datos. **Esa conclusión quedó retirada el 12 de octubre de
2026.** Las cifras se muestran porque forman parte del historial; la lectura que se hacía de ellas,
no."""),
    code("""\
e6_v3 = soporte.registro("E6_baseline_synthetic_v3")
e7_v3 = soporte.registro("E7_temporal_synthetic_v3")

comparacion = pd.DataFrame(
    [
        {
            "conjunto": "synthetic_v2",
            "generado": "14-09-2026",
            "generador": "POST-calibración (ralentí 690 rpm, del manual)",
            "sesiones": 72,
            "bosque F1 macro": e6["metrics"]["macro_f1"],
            "GRU F1 macro": e7["metrics"]["macro_f1"],
            "diferencia": e7["metrics"]["macro_f1"] - e6["metrics"]["macro_f1"],
        },
        {
            "conjunto": "synthetic_v3",
            "generado": "01-09-2026",
            "generador": "PRE-calibración (ralentí 820 rpm, SIN respaldo)",
            "sesiones": 216,
            "bosque F1 macro": e6_v3["metrics"]["macro_f1"],
            "GRU F1 macro": e7_v3["metrics"]["macro_f1"],
            "diferencia": e7_v3["metrics"]["macro_f1"] - e6_v3["metrics"]["macro_f1"],
        },
    ]
).set_index("conjunto")
comparacion.round(4)"""),
    md("""\
**Qué queremos investigar.** Por qué la comparación entre conjuntos no decide nada. La figura sitúa
juntas las cuatro cifras de F1 macro de validación (dos modelos por dos conjuntos, leídas tal como
se guardaron)."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_confusor_de_volumen

fig = fig_confusor_de_volumen()
# La flecha de la función une los dos conjuntos; se rotula qué significa.
fig.axes[0].text(0.5, 0.64, "entre los dos conjuntos\\ncambian a la vez el volumen\\n"
                 "y el generador", ha="center", va="bottom", fontsize=6.8, color="#52514e")
fig.suptitle(
    "F1 macro sobre validación en dos conjuntos: el orden de los modelos se invierte",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
soporte.exportar(fig, "FIG-NB02-06_confusor_volumen", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** Con `synthetic_v3` el orden se invierte: la red pasa de perder por 0,056 a ganar
por 0,012.

**Qué podemos interpretar.** Solo que algo cambia entre los dos conjuntos.

**Qué no podemos afirmar.** Que ese algo sea el volumen.
`synthetic_v3` se generó el 1 de septiembre, **antes** de que las constantes del motor se calibraran
contra el manual; `synthetic_v2`, el 14, después. Entre las dos columnas cambian el número de
sesiones **y el fenómeno simulado**: el ralentí pasa de 820 rpm (un valor sin respaldo documental,
que la calibración retiró) a 690, dentro del rango 640–740 que el manual documenta para este motor;
el avance de encendido cambia en la misma proporción. La constante `GENERATOR_VERSION` valió
`"1.0.0"` en los dos casos y no los distingue; por eso la diferencia pasó desapercibida durante
semanas.

Esto es un **confusor**. Con dos variables moviéndose a la vez y dos puntos de medida,
el experimento no tiene grados de libertad para separarlas. La conclusión “el límite era el volumen
de datos” quedó retirada (marcada `SUPERSEDED`) en el informe de E7, con su texto conservado. La pregunta
volvió a estar abierta.

La forma de responderla sin ese confusor es medir la curva de volumen **dentro de un solo conjunto**,
con subconjuntos anidados de entrenamiento y validación fija. Está diseñada en
`docs/diseno-pi1/04-subconjuntos-anidados.md`, con cuatro puntos y cinco semillas; **no se ha
ejecutado**. Una advertencia que ese diseño ya incorpora: su punto más alto son 132 sesiones de
entrenamiento, las mismas que tiene `synthetic_v3`. La curva **no amplía** el volumen ya
explorado; lo reproduce con el generador calibrado.

La reproducibilidad de `synthetic_v3` se mide en el notebook 06."""),
    md("""\
## 14. Resultados negativos y limitaciones

### 14.1 Resultados negativos

1. **La hipótesis pre-registrada de E7 no recibió apoyo.** El modelo temporal no superó a la línea
   base: −0,0558 en F1 macro.
2. **La explicación que se dio de esa desventaja quedó retirada.** Confundía volumen con calibración
   del generador.
3. **La corrección sobre el fallo de encendido también quedó retirada**, por la misma causa: se
   apoyaba en la misma comparación.
4. **Las dos cifras de temperatura del termostato que circulaban (70,7 y 54,3 °C) no tienen
   registro.** Se calcularon durante el análisis y no se persistieron; están marcadas como no
   utilizables desde el 12 de octubre de 2026.
5. **Ninguno de los dos modelos está bien calibrado** sin calibrar: el error por tramos ronda
   0,13–0,14 en los dos y en sentidos distintos. El bosque **promete menos de lo que cumple** (sesgo
   −0,1395) y la red está casi centrada, +0,0070, con tramos que se cancelan.
6. **La red genera diagnósticos cruzados que el bosque no genera**, lo que para este trabajo es el
   modo de fallo más costoso.

### 14.2 Limitaciones

Además de comparar dos recorridos y no dos arquitecturas (apartado 3):

1. **Una sola ejecución por celda.** No hay repeticiones con semillas distintas, ni intervalos, ni
   contraste estadístico; no se afirma significación en ningún punto. El diseño con cinco semillas
   está en `docs/diseno-pi1/06-plan-replicas.md` y no se ha ejecutado.
2. **Procedimiento asimétrico**: época elegida sobre validación y ningún modelo calibrado
   (apartado 6)."""),
    md("""\
## 15. Discusión

El resultado de E7 se suele resumir como “la red no funcionó”. Es un resumen pobre, porque lo
que el experimento enseña está en otro sitio.

**Primero, el criterio funcionó.** E6 dejó escrito, antes de medir, qué resultado haría injustificada
la complejidad del modelo temporal. Cuando el resultado llegó, el criterio ya estaba fijado y no
hubo que decidir si 0,056 era mucho o poco. Eso distingue un resultado negativo de una
racionalización posterior.

**Segundo, la explicación inicial era más débil que el resultado.** El resultado, que la red no supera al
bosque, se sostiene. La explicación, que faltaban datos, no. Tardó seis semanas en caer, hasta que
alguien comparó las fechas de generación de los dos conjuntos. La diferencia entre las dos cosas es
instructiva. Un resultado negativo bien medido es robusto; una explicación cómoda de un resultado
negativo es frágil, porque nadie examina lo que resulta cómodo.

**Tercero, lo que la comparación no puede decidir sigue sin decidirse.** La pregunta que el tutor
formuló (en qué tipos de fallo el contexto temporal aporta señal diagnóstica adicional y en cuáles
no) no se responde con estos dos recorridos, por mucho que la victoria de la red en el termostato
parezca sugerirla. Ese encaje aparente pide una segunda mirada porque coincide con lo que se
esperaba encontrar. Lo que limita al termostato es el generador, no
la física de un motor real (apartado 9).

**Cómo encaja con el resto del trabajo.** El bosque quedó como modelo de diagnóstico del recorrido
completo. Sobre el conjunto de prueba, en E19, dio 0,836 de F1 macro (0,8469 de exactitud),
frente a los 0,8788 de validación. Que su error sea mayoritariamente por omisión y no cruzado hace viable el
criterio de suficiencia: el sistema se enfrenta sobre todo a “no veo nada” y no a “veo otra cosa con
confianza”."""),
    md("""\
## 16. Conclusiones

**Qué aprendimos.** Que un bosque aleatorio sobre 139 descriptores de ventana obtuvo mayor F1 macro
que una GRU bidireccional sobre la secuencia cruda (0,8788 frente a 0,8230), en este conjunto, con
esta partición y en una sola ejecución, con un procedimiento asimétrico que impide atribuir la
diferencia a la arquitectura; que la diferencia no es uniforme entre condiciones; y que la estructura de sus errores es
distinta de un modo que importa para el uso previsto.

**Qué hipótesis recibió apoyo.** La de PI.1 en su parte medible aquí: el diagnóstico a partir de
ventanas de OBD-II supera a la clase mayoritaria con margen amplio.

**Qué hipótesis no recibió apoyo.** La de E7: que el modelo temporal superase a la línea base.

**Qué permanece sin demostrar.** Si el contexto temporal aporta señal diagnóstica y en qué fallos. Si
la desventaja de la red se debe al volumen de datos. Si la victoria en el termostato es real o
casual. Las tres exigen experimentos que están **diseñados y no ejecutados**.

**Cómo contribuye al TFM.** Sostiene el capítulo de diagnóstico, justifica la elección del bosque
como modelo del recorrido y aporta un resultado negativo bien medido, que es evidencia tanto como
uno positivo."""),
    md("""\
## 17. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb`. **No hace falta `torch`**: la red no se reentrena |
| **Datos** | ninguno: se leen registros y tablas versionados |
| **Configuración** | bosque 400 árboles, `class_weight=balanced`; GRU 19 014 parámetros |
| **Semilla** | 20260901 en los dos |
| **Commit** | el que imprime la celda del apartado 4 |
| **Tiempo** | menos de un minuto |
| **Memoria** | por debajo de 500 MB |
| **Recursos** | CPU |
| **Artefactos que produce** | siete figuras en `notebooks/salida/02_comparacion_modelos/`, PNG y SVG |

**Qué se reproduce y qué no.** Este notebook **no reproduce** E6 ni E7: los lee. Reentrenar el
bosque daría las mismas cifras (es determinista con su semilla); reentrenar la red **no**, por el
no-determinismo de MPS que declara la celda de modalidad: la semilla acota la variación y no la
elimina.

**Reproducción completa, modo FULL.** Exige regenerar `synthetic_v2` (`mecanico-exp generar
--dataset-id synthetic_v2 --sessions-per-fault 12`), preprocesarlo y ejecutar los dos entrenamientos.
Del orden de diez minutos en una máquina con acelerador. **Las ejecuciones nuevas escriben con
etiqueta propia**: los ejecutores se niegan a sobrescribir los artefactos publicados.

## 18. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** Las cifras agregadas son la **Tabla 5.1**; el detalle por
condición, la **Figura 5.7**, con su **Tabla B.2** en el anexo B; adónde van los errores de cada
modelo, la **Figura 5.6**; la comparación entre los dos conjuntos, la **Figura 5.8**; el termostato
ventana a ventana, la **Figura 5.9**; la calibración, la **Tabla 5.2** y la **Figura 5.12**; su
forma por tramos, la **Figura 5.13**.

- `docs/experiments/E6_baseline.md`: informe de la línea base, con el criterio pre-registrado
- `docs/experiments/E7_modelo_temporal.md`: informe del modelo temporal, con sus marcas `SUPERSEDED`
- `experiments/E6_baseline_synthetic_v2.json`, `E6_baseline_synthetic_v3.json`
- `experiments/E7_temporal_synthetic_v2.json`, `E7_temporal_synthetic_v3.json`
- `artifacts/tables/E6_baseline_confusion_synthetic_v2.csv`, `E7_temporal_confusion_synthetic_v2.csv`
- `src/mecanico_ia_exp/features/temporal.py`: los 139 descriptores
- `src/mecanico_ia_exp/models/baseline.py`, `models/temporal.py`
- `src/mecanico_ia_exp/evaluation/metrics.py`: la PR-AUC por clase, como precisión media uno contra el resto
- `docs/diseno-pi1/04-subconjuntos-anidados.md`: la curva de volumen, diseñada y no ejecutada
- `docs/diseno-pi1/05-protocolo-comparacion.md`: el protocolo simétrico
- `docs/diseno-pi1/07-ablacion-representacion.md`: la escalera que sí aísla la representación

**Nota sobre los registros.** Los de E6, E7 y E9 **no llevan cabecera de identificación**: les faltan
`commit`, `executed_at` y `dataset_type`, porque son anteriores a que la convención existiera. No se
regeneran para arreglarlo, porque regenerar cambiaría las cifras publicadas. La carencia está
declarada en `research/reproducibility.md`."""),
]

if __name__ == "__main__":
    escribir("02_comparacion_modelos.ipynb", CELDAS)
