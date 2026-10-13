"""Construye `02_comparacion_modelos.ipynb`: bosque aleatorio frente a GRU bidireccional."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Comparación de modelos: bosque aleatorio frente a GRU bidireccional

**Notebook** `02_comparacion_modelos` · **versión** 1.0 · **fecha** 12 de octubre de 2026

| | |
|---|---|
| **Experimentos** | E6 (línea base tabular) y E7 (modelo temporal) |
| **Conjunto** | `synthetic_v2`, partición de validación · se citan cifras de `synthetic_v3` **marcadas como lo que son** |
| **Protocolo** | el publicado: `E6_v1_bosque_sin_calibrar` y `E7_v1_epoca_sobre_validacion_sin_calibrar` |
| **Estado** | E6 validada; E7 **negativa**, con dos conclusiones `SUPERSEDED` el 12-10-2026 |
| **Pregunta de investigación** | PI.1 — diagnóstico a partir del análisis contextual y longitudinal de OBD-II |
| **Evidencia original** | `experiments/E6_baseline_synthetic_v2.json`, `E7_temporal_synthetic_v2.json`, `artifacts/tables/E6_*.csv`, `E7_*.csv` |

---

## Advertencia que gobierna todo el notebook

Este documento compara **dos recorridos completos**, no dos arquitecturas. Entre el bosque y la red
cambian a la vez la **representación** de los datos y el **estimador**, de modo que ninguna
diferencia entre ellos puede atribuirse al contexto temporal. Esa limitación no es una nota al pie:
es la razón por la que la pregunta sobre el valor del contexto temporal sigue abierta, y el notebook
la repite donde haga falta."""),
    md("""\
## 1. Introducción: qué motiva esta comparación

E6 estableció una línea base. Su informe dejó escrito un criterio **antes** de medir nada:

> «Si el modelo temporal no supera la línea base, su complejidad no está justificada.»

Es un criterio pre-registrado y no retrospectivo, y es lo que da sentido a E7. La pregunta no era si
una red recurrente funciona —funcionan—, sino si **aporta algo** sobre un bosque aleatorio
alimentado con descriptores de ventana, en este problema y con estos datos.

Lo que no sabíamos antes de empezar:

1. Si una representación secuencial captaría firmas que los descriptores agregados pierden.
2. Si la ventaja, de haberla, sería uniforme o se concentraría en condiciones concretas.
3. Si la confianza de los dos modelos sería comparable, que es lo que después permite usarla como
   criterio de abstención."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Medir si el recorrido secuencial supera al tabular en diagnóstico sobre ventanas de
OBD-II, y caracterizar **dónde** difieren.

**Hipótesis pre-registrada (E6, antes de medir E7).** El modelo temporal supera a la línea base en
F1 macro sobre validación.

**Variables observadas.** F1 macro, exactitud, F1 por clase, matriz de confusión y error de
calibración, todo sobre la misma partición de validación.

**Criterio de evaluación.** El declarado en E6: si no la supera, la complejidad no está justificada.
No hay umbral de margen mínimo, y no se inventa uno ahora.

**Qué cuestionaría la hipótesis.** Un F1 macro de la red igual o inferior al del bosque. Eso es lo
que ocurrió."""),
    md("""\
## 3. Fundamento: las dos representaciones y los dos estimadores

Esta sección es la que permite leer el resto. Son cuatro cosas, no dos.

### La representación tabular: 139 descriptores de ventana

Cada ventana de 120 segundos y 12 señales —1 440 valores— se resume en **139 números**:

| Familia | Descriptores | Cuántos |
|---|---|---|
| Nivel | `mean` | 12 |
| Dispersión y extremos | `std`, `min`, `max`, `range` | 48 |
| Dinámica intraventana | `slope`, `autocorr1`, `delta_min`, `delta_max`, `crossings`, `n_events` | 72 |
| Razón entre señales | `maf_over_rpm_load` | 1 |
| Correlación cruzada | `corr_*` | 6 |

Conviene fijarse en la tercera fila: **la representación tabular no es estática**. Setenta y dos de
los 139 descriptores son dinámica dentro de la ventana —pendiente, autocorrelación, número de cruces,
número de eventos—. Decir que el bosque «no ve el tiempo» sería inexacto: ve una descripción resumida
de él. Lo que no ve es el **orden** de las muestras más allá de lo que esos resúmenes capturan.

### La representación secuencial: 120 × 12 en crudo

La red recibe la matriz completa, normalizada señal a señal. No hay pérdida de información por
resumen; el coste es que tiene que aprender qué mirar.

### Bosque aleatorio

Cuatrocientos árboles, `class_weight="balanced"`, semilla 20260901. *Por qué este estimador como
línea base:* tolera bien descriptores correlacionados —y aquí lo están mucho—, no necesita escalado,
y con pocos cientos de ventanas es más estable que casi cualquier alternativa.

### GRU bidireccional

19 014 parámetros. *Por qué bidireccional:* la ventana está completa cuando se clasifica, no llega en
tiempo real, así que leerla en los dos sentidos es legítimo y permite que el estado final recoja
información de todo el tramo. *Por qué GRU y no LSTM:* menos parámetros con desempeño comparable, y
con ventanas de este tamaño la diferencia entre las dos arquitecturas no es lo que limita.

### Por qué la comparación no aísla el contexto temporal

| | Representación | Estimador |
|---|---|---|
| **Recorrido A** (E6) | 139 descriptores | bosque aleatorio |
| **Recorrido B** (E7) | secuencia 120 × 12 | GRU bidireccional |

Las dos columnas cambian a la vez. Para atribuir una diferencia al contexto temporal haría falta
mantener una fija y mover la otra —un diseño factorial— y eso **no se hizo** y no se propone hacer,
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

**Y una distinción que hay que mantener sin excepciones.** Hay un segundo conjunto, `synthetic_v3`,
con 216 sesiones, cuyas cifras aparecen en el informe de E7. **No sale del mismo generador**: se
generó el 1 de septiembre, antes de que las constantes del motor se calibraran contra el manual. Su
ralentí está en 820 rpm, un valor sin ningún respaldo documental; el de `v2` está en 690, dentro del
rango 640–740 que el manual documenta para este motor.

Comparar `v2` con `v3` cambia el **volumen** y el **fenómeno**. Las cifras de `v3` se muestran en
este notebook, porque forman parte del historial, y se muestran **marcadas**."""),
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
print("E6 y E7 se midieron sobre validación, y así se reportan.")"""),
    md("""\
## 6. Metodología: qué se fijó antes y qué se decidió después

**Decisiones pre-registradas**, escritas antes de medir:

- El criterio de aceptación de E7, en el informe de E6.
- La semilla, 20260901, común a todo el laboratorio.
- El reparto por sesión y el tamaño de ventana, fijados en E5 con su estudio.
- Las métricas que se publican.

**Decisiones del procedimiento que hoy se reconocen como asimétricas** —no eran decisiones
exploratorias, pero condicionan la comparación y no estaban declaradas en su momento:

1. **La época de la red se elige mirando la misma validación sobre la que se reporta.** El bosque no
   tiene paso de selección equivalente. La red llega a la medición habiendo elegido su mejor momento
   contra el conjunto que la mide; el bosque, no. La asimetría **favorece a la red**, y aun así la
   red pierde, lo que hace el resultado más robusto de lo que sería al revés.
2. **Ninguno de los dos calibra.** Los dos reportan su error de calibración sobre `predict_proba` en
   crudo. La diferencia de ECE entre ellos no es, por tanto, una diferencia entre calibradores.

Las dos se corrigen en el protocolo de PI.1, con tres particiones internas. Ese protocolo **no se ha
ejecutado**, y cuando se ejecute escribirá con etiqueta propia sin sustituir estas cifras."""),
    md("""\
## 7. Resultados agregados

**Qué queremos investigar.** Si la red supera al bosque en la métrica del criterio.
**Qué datos utilizamos.** Los dos registros JSON, sin recalcular nada.
**Qué variables se representan.** F1 macro, exactitud y ECE.
**Por qué un gráfico de barras agrupadas.** Son tres métricas y dos modelos: la comparación directa
cabe en un panel y no hay serie temporal que mostrar.
**Qué debemos observar.** El signo de la diferencia en F1 macro, que es lo que el criterio mira."""),
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

Que los dos superen a la clase mayoritaria por un orden de magnitud sí responde a lo que PI.1 pide:
el diagnóstico a partir de ventanas de OBD-II es posible con margen amplio.

**Qué no podemos afirmar.** Tres cosas, y conviene nombrarlas:

1. **Que la red sea peor arquitectura.** Lo medido es un recorrido completo contra otro.
2. **Que la diferencia de ECE favorezca a la red por calibrar mejor.** Ninguno de los dos calibra:
   las dos cifras son de `predict_proba` en crudo. Lo que muestran es que la red está menos
   sobreconfiada, no que su probabilidad esté mejor ajustada tras calibrar.
3. **Que la diferencia sea significativa.** Es **una sola ejecución** sobre 98 ventanas de
   validación. No hay repeticiones con semillas distintas ni intervalo de confianza, y por tanto no
   se afirma significación. El diseño con cinco semillas está en `docs/diseno-pi1/06-plan-replicas.md`
   y no se ha ejecutado."""),
    md("""\
## 8. Resultados por condición: donde la media esconde lo interesante

**Qué queremos investigar.** Si la desventaja de la red es uniforme o se concentra.
**Qué datos utilizamos.** El F1 por clase de los dos registros.
**Por qué un gráfico de barras horizontales enfrentadas.** Seis clases y dos modelos; horizontal
porque los nombres de las condiciones son largos y en vertical no se leen.
**Qué debemos observar.** El signo de la diferencia clase a clase, no solo su tamaño."""),
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
NOMBRES = {
    "F00_normal": "sin fallo",
    "F01_vacuum_leak": "fuga de vacío",
    "F02_maf_drift": "deriva del caudalímetro",
    "F03_thermostat_stuck": "termostato bloqueado",
    "F04_o2_lag": "sonda lenta",
    "F05_misfire": "fallo de encendido",
}

orden = por_clase.sort_values("diferencia")
posiciones = np.arange(len(orden))
etiquetas = [f"{NOMBRES[i]}\\n(n={int(orden.loc[i, 'ventanas'])})" for i in orden.index]

fig, (izq, der) = plt.subplots(1, 2, figsize=(9.8, 4.0), width_ratios=[1.5, 1])

alto = 0.38
izq.barh(posiciones + alto / 2, orden["bosque"], alto,
         color=CATEGORICAL[0], label="bosque aleatorio (E6)")
izq.barh(posiciones - alto / 2, orden["GRU"], alto,
         color=CATEGORICAL[1], label="GRU bidireccional (E7)")
izq.set_yticks(posiciones, etiquetas, fontsize=7)
izq.set_xlabel("F1 por clase (adimensional, 0–1)")
izq.set_xlim(0, 1.05)
izq.legend(fontsize=7, loc="lower right")
izq.set_title("F1 de cada condición", fontsize=9)

colores = [CATEGORICAL[1] if d > 0 else CATEGORICAL[0] for d in orden["diferencia"]]
der.barh(posiciones, orden["diferencia"], 0.6, color=colores)
der.axvline(0, color="#52514e", linewidth=0.9)
der.set_yticks(posiciones, [""] * len(posiciones))
der.set_xlabel("F1 de la GRU − F1 del bosque")
der.set_title("Diferencia: a la derecha gana la GRU", fontsize=9)
for pos, valor in zip(posiciones, orden["diferencia"], strict=False):
    der.text(valor + (0.006 if valor > 0 else -0.006), pos, f"{valor:+.3f}",
             va="center", ha="left" if valor > 0 else "right", fontsize=7)

fig.suptitle(
    "La desventaja de la red no es uniforme: pierde en cinco condiciones y gana en una",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E6 y E7 · synthetic_v2, validación · fuente: experiments/E6_baseline_synthetic_v2.json "
    "y E7_temporal_synthetic_v2.json · n = ventanas de la clase en validación",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-02_por_clase", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** La red pierde en cinco de las seis condiciones y gana en una: el **termostato
bloqueado**, 0,8148 frente a 0,7826, una diferencia de +0,032. Las pérdidas mayores están en el
fallo de encendido (−0,167) y en la clase sin fallo (−0,054).

**Qué podemos interpretar.** Que la métrica agregada esconde comportamientos distintos, y que la
condición donde la red gana es precisamente aquella cuya firma es temporal en un sentido fuerte:
«algo que debería subir y no sube».

**Qué no podemos afirmar, y aquí es donde hay que tener más cuidado que en ninguna otra parte del
trabajo.** La tentación es leer esa única victoria como evidencia de que el contexto temporal
aporta. No lo es, por cuatro razones acumulativas:

1. Es **+0,032 sobre 14 ventanas** de validación. Una sola ventana cambiada mueve la cifra mucho más
   que eso.
2. Es **una sola ejecución**, sin repeticiones ni intervalo.
3. Los dos recorridos difieren en **representación y estimador** a la vez.
4. Hay una **explicación alternativa medida**: el fallo del termostato no altera la trayectoria
   mientras el refrigerante no supera su tope, y en calentamiento eso deja 32 de 45 ventanas
   etiquetadas sin ninguna señal observable. Los errores de los dos modelos en esta clase podrían
   concentrarse ahí, y entonces la diferencia mediría cómo cada uno trata ventanas **sin
   información**, que no es lo mismo que medir sensibilidad temporal.

El cruce que distinguiría las dos explicaciones —predicción por ventana contra expresión por
ventana— está diseñado y **no ejecutado**: `docs/diseno-pi1/08-analisis-por-fallo.md`.

Y hay una observación de signo contrario que conviene no olvidar: la red pierde estrepitosamente en
el **fallo de encendido**, que es la otra condición con estructura temporal marcada —episodios
breves—. Si la ventaja de la red viniera de su capacidad de modelar el tiempo, cabría esperar que
ganara también ahí. No lo hace."""),
    md("""\
## 9. Matrices de confusión: qué tipo de error comete cada uno

**Qué queremos investigar.** No cuántos errores, sino **hacia dónde** van. En diagnóstico no es lo
mismo decir «no hay fallo» cuando lo hay que confundir un fallo con otro: lo segundo manda al
mecánico a desmontar la pieza equivocada.

**Por qué un mapa de calor y no una tabla.** Son dos matrices de 6 × 6; los bloques se ven de un
vistazo y se comparan entre sí, que es lo que interesa."""),
    code("""\
from mecanico_ia_exp.visualization.style import SEQUENTIAL

confusion_e6 = soporte.tabla("E6_baseline_confusion_synthetic_v2").set_index("Unnamed: 0")
confusion_e7 = soporte.tabla("E7_temporal_confusion_synthetic_v2").set_index("Unnamed: 0")
corto = [c.split("_")[0] for c in confusion_e6.columns]

fig, ejes = plt.subplots(1, 2, figsize=(9.6, 4.2))
for eje, matriz, titulo in [
    (ejes[0], confusion_e6, "Bosque aleatorio (E6)"),
    (ejes[1], confusion_e7, "GRU bidireccional (E7)"),
]:
    imagen = eje.imshow(matriz.to_numpy(), cmap=SEQUENTIAL)
    eje.set_xticks(range(len(corto)), corto, rotation=45, ha="right", fontsize=7)
    eje.set_yticks(range(len(corto)), corto, fontsize=7)
    eje.set_xlabel("clase predicha")
    eje.set_ylabel("clase verdadera" if titulo.startswith("Bosque") else "")
    eje.set_title(titulo, fontsize=9)
    eje.grid(False)
    maximo = matriz.to_numpy().max()
    for i in range(len(corto)):
        for j in range(len(corto)):
            valor = int(matriz.iloc[i, j])
            if valor:
                eje.text(j, i, valor, ha="center", va="center", fontsize=7.5,
                         color="white" if valor > maximo * 0.55 else "#0b0b0b")

fig.suptitle(
    "Matrices de confusión: filas = verdad, columnas = predicción",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E6 y E7 · synthetic_v2, validación, 98 ventanas · "
    "fuente: artifacts/tables/E6_baseline_confusion_synthetic_v2.csv y "
    "E7_temporal_confusion_synthetic_v2.csv · recuento de ventanas",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-03_confusion", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    code("""\
# Dos preguntas concretas sobre la estructura del error, respondidas con las
# matrices: ¿cuántos errores van hacia «sin fallo» y cuántos cruzan de un fallo
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
**Qué muestra.** El bosque concentra sus errores en la diagonal de omisión: casi todos van a «sin
fallo». La red reparte más, y genera algún diagnóstico cruzado que el bosque no genera.

**Qué podemos interpretar.** Para el uso que este trabajo persigue, **la estructura del error del
bosque es preferible a la de la red**, con independencia del F1. Un error por omisión deja el
problema sin diagnosticar; un diagnóstico cruzado produce una hipótesis **confiada y equivocada**,
que es el modo de fallo que todo el criterio de suficiencia existe para evitar. Que el bosque falle
«hacia abajo» no es una virtud suya: es consecuencia de que las clases difíciles carecen de señal en
parte de sus ventanas, y la clase sin fallo es la respuesta por defecto cuando no se ve nada.

**Qué no podemos afirmar.** Que la estructura del error del bosque sea benigna **en general**. Lo
observado vale para este conjunto y esta partición, con 98 ventanas. Con otro reparto de clases, o
con fallos que compartieran firma, la estructura podría ser otra. Tampoco se puede afirmar nada
sobre el coste relativo de los dos tipos de error sin un criterio de coste, que este trabajo no
define."""),
    md("""\
## 10. Calibración: por qué importa aquí más que en otros problemas

Todo el criterio de abstención compara la confianza del modelo contra un umbral. Si la confianza
estuviera mal calibrada, el umbral no significaría nada.

**ECE (*expected calibration error*).** Se agrupan las predicciones en diez tramos según su
confianza. En cada tramo se compara la confianza media con el acierto real. El ECE es la media de
esas diferencias, ponderada por cuántas predicciones hay en cada tramo. Un ECE de 0,14 quiere decir
que, de media, el modelo se desvía catorce puntos de lo que su confianza prometía.

**Exceso de confianza.** La diferencia entre confianza media y acierto. Positivo quiere decir que el
modelo promete más de lo que cumple."""),
    code("""\
calibracion = pd.DataFrame(
    {
        "bosque (E6)": e6["metrics"]["calibration"],
        "GRU (E7)": e7["metrics"]["calibration"],
    }
).T
calibracion.round(4)"""),
    code("""\
fig, eje = plt.subplots(figsize=(5.4, 4.6))
eje.plot([0, 1], [0, 1], color="#898781", linestyle=":", linewidth=1.0)
eje.text(0.52, 0.46, "calibración perfecta", fontsize=6.8, color="#52514e", rotation=37)

for (nombre, fila), color, marca in zip(
    calibracion.iterrows(), CATEGORICAL, ["o", "s"], strict=False
):
    eje.scatter(fila["mean_confidence"], fila["accuracy"], s=95, color=color,
                marker=marca, label=nombre, zorder=3)
    eje.annotate(
        f"{nombre}\\nECE {fila['ece']:.4f}\\nexceso {fila['overconfidence']:+.4f}",
        (fila["mean_confidence"], fila["accuracy"]),
        textcoords="offset points", xytext=(10, -22), fontsize=7, color=color,
    )

eje.set_xlabel("confianza media (probabilidad declarada, 0–1)")
eje.set_ylabel("acierto observado (fracción, 0–1)")
eje.set_xlim(0.6, 1.0)
eje.set_ylim(0.6, 1.0)
eje.legend(fontsize=7, loc="upper left")
fig.suptitle(
    "Los dos prometen más de lo que cumplen",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E6 y E7 · synthetic_v2, validación · por encima de la diagonal: infraconfianza; "
    "por debajo: exceso de confianza · ninguno de los dos modelos calibra: "
    "las cifras son de predict_proba en crudo",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-04_calibracion", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** Los dos modelos caen por debajo de la diagonal: declaran una confianza media
superior a su acierto. El bosque se desvía 0,1439 y la red 0,1317.

**Qué podemos interpretar.** El exceso de confianza es real y del mismo orden en los dos, y es la
razón por la que el recorrido de diagnóstico **no usa la probabilidad cruda** como criterio de
abstención: la calibra antes. Esa decisión, que podría parecer un tecnicismo, está justificada por
estas dos cifras.

**Qué no podemos afirmar.** Que la red esté mejor calibrada **que el bosque calibrado**. Lo
comparado son dos modelos sin calibrar. Tampoco que el ECE sea estable: con diez tramos y 98
ventanas, cada tramo contiene muy pocas predicciones y la cifra es frágil. Y un solo punto por
modelo —confianza media contra acierto— es un resumen: no muestra si el exceso se concentra en los
tramos de alta confianza, que es donde más daño haría. La curva de fiabilidad completa exigiría las
predicciones por ventana, que los registros de E6 y E7 **no guardan**."""),
    md("""\
## 11. Las cifras de `synthetic_v3`, y por qué no cierran la cuestión

El informe de E7 publicó también resultados sobre `synthetic_v3`, con el triple de sesiones, y
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
    code("""\
fig, eje = plt.subplots(figsize=(7.6, 3.8))
x = np.arange(2)
ancho = 0.34
eje.bar(x - ancho / 2, comparacion["bosque F1 macro"], ancho,
        color=CATEGORICAL[0], label="bosque aleatorio")
eje.bar(x + ancho / 2, comparacion["GRU F1 macro"], ancho,
        color=CATEGORICAL[1], label="GRU bidireccional")
for i, (_, fila) in enumerate(comparacion.iterrows()):
    eje.text(i - ancho / 2, fila["bosque F1 macro"] + 0.008,
             f"{fila['bosque F1 macro']:.4f}", ha="center", fontsize=7.5)
    eje.text(i + ancho / 2, fila["GRU F1 macro"] + 0.008,
             f"{fila['GRU F1 macro']:.4f}", ha="center", fontsize=7.5)
eje.set_xticks(x, [
    "synthetic_v2\\n72 sesiones · generador CALIBRADO",
    "synthetic_v3\\n216 sesiones · generador SIN CALIBRAR",
], fontsize=7.5)
eje.set_ylabel("F1 macro sobre validación\\n(adimensional, 0–1)")
eje.set_ylim(0, 1.08)
eje.legend(fontsize=7.5, loc="lower right")

eje.annotate(
    "entre las dos columnas cambian DOS cosas:\\nel volumen y el fenómeno generado",
    xy=(0.5, 1.0), xytext=(0.5, 0.42), ha="center", fontsize=7.5, color="#52514e",
    arrowprops={"arrowstyle": "-[, widthB=5.2, lengthB=0.5", "color": "#898781", "lw": 1.0},
)

fig.suptitle(
    "El orden se invierte, y la comparación no dice por qué",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E6 y E7 · fuente: experiments/E6_baseline_synthetic_v{2,3}.json y "
    "E7_temporal_synthetic_v{2,3}.json · "
    "la conclusión «el límite era el volumen» quedó SUPERSEDED el 12-10-2026",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB02-05_confusor_volumen", subdirectorio="02_comparacion_modelos")
plt.show()"""),
    md("""\
**Qué muestra.** Con `synthetic_v3` el orden se invierte: la red pasa de perder por 0,056 a ganar
por 0,012.

**Qué podemos interpretar.** Que algo cambia entre los dos conjuntos. Nada más que eso.

**Qué no podemos afirmar, y es el punto entero de esta sección.** Que ese algo sea el volumen.
`synthetic_v3` se generó el 1 de septiembre, **antes** de que las constantes del motor se calibraran
contra el manual, y `synthetic_v2` el 14, después. Entre las dos columnas cambian el número de
sesiones **y el fenómeno simulado**: el ralentí pasa de 820 rpm —un valor que la calibración retiró
por carecer de respaldo documental— a 690, y el avance de encendido cambia en la misma proporción.
La constante `GENERATOR_VERSION` valió `"1.0.0"` en los dos casos y no los distingue, que es por lo
que la diferencia pasó desapercibida durante semanas.

Esto es un **confusor**, no un matiz. Con dos variables moviéndose a la vez y dos puntos de medida,
el experimento no tiene grados de libertad para separarlas. La conclusión «el límite era el volumen
de datos» quedó marcada `SUPERSEDED` en el informe de E7, con su texto conservado, y la pregunta
volvió a estar abierta.

La forma de responderla sin ese confusor es medir la curva de volumen **dentro de un solo conjunto**,
con subconjuntos anidados de entrenamiento y validación fija. Está diseñada en
`docs/diseno-pi1/04-subconjuntos-anidados.md`, con cuatro puntos y cinco semillas, y **no se ha
ejecutado**. Una advertencia que ese diseño ya incorpora: su punto más alto son 132 sesiones de
entrenamiento, que son **exactamente** las de `synthetic_v3`. La curva **no amplía** el volumen ya
explorado; lo reproduce con el generador calibrado."""),
    md("""\
## 12. Resultados negativos, reunidos

1. **La hipótesis pre-registrada de E7 no recibió apoyo.** El modelo temporal no superó a la línea
   base: −0,0558 en F1 macro.
2. **La explicación que se dio de esa desventaja quedó retirada.** Confundía volumen con calibración
   del generador.
3. **La corrección sobre el fallo de encendido también quedó retirada**, por la misma causa: se
   apoyaba en la misma comparación.
4. **Las dos cifras de temperatura del termostato que circulaban —70,7 y 54,3 °C— no tienen
   registro.** Se calcularon durante el análisis y no se persistieron; están marcadas como no
   utilizables desde el 12 de octubre de 2026.
5. **Ninguno de los dos modelos está bien calibrado** sin calibrar: los dos prometen más de lo que
   cumplen, en torno a 0,13–0,14 de ECE.
6. **La red genera diagnósticos cruzados que el bosque no genera**, lo que para este trabajo es el
   modo de fallo más costoso.
7. **Todo lo anterior es una sola ejecución por celda.** No hay repeticiones, ni intervalos, ni
   contraste estadístico, y no se afirma significación en ningún punto."""),
    md("""\
## 13. Discusión

El resultado de E7 se suele resumir como «la red no funcionó». Es un resumen pobre y conviene
desarmarlo, porque lo que el experimento enseña está en otro sitio.

**Primero, el criterio funcionó.** E6 dejó escrito, antes de medir, qué resultado haría injustificada
la complejidad del modelo temporal. Cuando el resultado llegó, el criterio ya estaba fijado y no
hubo que decidir si 0,056 era mucho o poco. Eso es lo que distingue un resultado negativo de una
racionalización posterior.

**Segundo, la explicación inicial era más débil que el resultado.** El resultado —la red no supera al
bosque— se sostiene. La explicación —faltaban datos— no, y tardó seis semanas en caer, hasta que
alguien comparó las fechas de generación de los dos conjuntos. La diferencia entre las dos cosas es
instructiva: un resultado negativo bien medido es robusto; una explicación cómoda de un resultado
negativo es frágil, y precisamente porque es cómoda nadie la examina.

**Tercero, lo que la comparación no puede decidir sigue sin decidirse.** La pregunta que el tutor
formuló —en qué tipos de fallo el contexto temporal aporta señal diagnóstica adicional y en cuáles
no— no se responde con estos dos recorridos, por mucho que la victoria de la red en el termostato
parezca sugerirla. Ese encaje aparente es justamente la clase de evidencia que conviene mirar dos
veces: coincide con lo que se esperaba encontrar.

**Cómo encaja con el resto del trabajo.** El bosque quedó como modelo de diagnóstico del recorrido
completo, y sus 0,8788 de F1 macro sobre validación se sostuvieron después sobre el conjunto de
prueba en E19. Que su error sea mayoritariamente por omisión, y no cruzado, es lo que hace viable el
criterio de suficiencia: el sistema se enfrenta sobre todo a «no veo nada» y no a «veo otra cosa con
confianza»."""),
    md("""\
## 14. Conclusiones de este notebook

**Qué aprendimos.** Que un bosque aleatorio sobre 139 descriptores de ventana diagnostica mejor que
una GRU bidireccional sobre la secuencia cruda, en este conjunto, con esta partición y en una sola
ejecución; que la diferencia no es uniforme entre condiciones; y que la estructura de sus errores es
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
## 15. Reproducibilidad

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
| **Artefactos que produce** | cinco figuras en `notebooks/salida/02_comparacion_modelos/`, PNG y SVG |

**Qué se reproduce y qué no.** Este notebook **no reproduce** E6 ni E7: los lee. Reentrenar el
bosque daría las mismas cifras —es determinista con su semilla— pero reentrenar la red **no**: se
entrenó sobre MPS, y algunas reducciones en ese dispositivo no son bit a bit deterministas. La
semilla acota la variación y no la elimina. Un notebook que reentrenase la red mostraría un número
distinto del publicado y parecería una contradicción donde solo hay no-determinismo del dispositivo.

**Reproducción completa, modo FULL.** Exige regenerar `synthetic_v2` —`mecanico-exp generar
--dataset-id synthetic_v2 --sessions-per-fault 12`—, preprocesarlo y ejecutar los dos entrenamientos.
Del orden de diez minutos en una máquina con acelerador. **Las ejecuciones nuevas escriben con
etiqueta propia**: los ejecutores se niegan a sobrescribir los artefactos publicados.

## 16. Referencias y trazabilidad

- `docs/experiments/E6_baseline.md` — informe de la línea base, con el criterio pre-registrado
- `docs/experiments/E7_modelo_temporal.md` — informe del modelo temporal, con sus marcas `SUPERSEDED`
- `experiments/E6_baseline_synthetic_v2.json`, `E6_baseline_synthetic_v3.json`
- `experiments/E7_temporal_synthetic_v2.json`, `E7_temporal_synthetic_v3.json`
- `artifacts/tables/E6_baseline_confusion_synthetic_v2.csv`, `E7_temporal_confusion_synthetic_v2.csv`
- `src/mecanico_ia_exp/features/temporal.py` — los 139 descriptores
- `src/mecanico_ia_exp/models/baseline.py`, `models/temporal.py`
- `docs/diseno-pi1/04-subconjuntos-anidados.md` — la curva de volumen, diseñada y no ejecutada
- `docs/diseno-pi1/05-protocolo-comparacion.md` — el protocolo simétrico
- `docs/diseno-pi1/07-ablacion-representacion.md` — la escalera que sí aísla la representación

**Nota sobre los registros.** Los de E6, E7 y E9 **no llevan cabecera de identificación**: les faltan
`commit`, `executed_at` y `dataset_type`, porque son anteriores a que la convención existiera. No se
regeneran para arreglarlo, porque regenerar cambiaría las cifras publicadas. La carencia está
declarada en `research/reproducibility.md`."""),
]

if __name__ == "__main__":
    escribir("02_comparacion_modelos.ipynb", CELDAS)
