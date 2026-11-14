"""Construye `04_explicabilidad.ipynb`: atribución de Shapley sobre el bosque (E9)."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Explicabilidad: qué señal sostiene cada diagnóstico

**Notebook** `04_explicabilidad` · **versión** 1.1 · **fecha** 14 de noviembre de 2026

| | |
|---|---|
| **Experimento** | E9, atribución |
| **Conjunto** | `synthetic_v2`, partición de validación · 18 casos, tres por condición |
| **Protocolo** | `shap.explainers.Permutation` sobre `predict_proba` de la clase predicha |
| **Estado** | cerrado y validado |
| **Modalidad** | visualización de evidencia histórica |
| **Pregunta de investigación** | PI.1 (qué sostiene el diagnóstico) y PI.2, porque la atribución es la **observación** que después hay que anclar en un documento |
| **Evidencia original** | `experiments/E9_xai_synthetic_v2.json`, `artifacts/tables/E9_atribuciones_synthetic_v2.csv`, `E9_resumen_synthetic_v2.csv` |

---

## En un minuto

- **Pregunta.** Si lo que el modelo mira para decidir coincide con lo que la ficha del fallo dice
  que debería mirarse; la atribución da después las **observaciones** del informe.
- **Qué se hace.** Se leen las atribuciones de Shapley que E9 calculó sobre el bosque aleatorio.
- **Resultado.** En las **cinco** condiciones de fallo la señal de mayor atribución está entre las
  declaradas. En la deriva del caudalímetro el modelo recupera la regla de compensación que el
  generador implementa y la detecta en los ajustes de combustible y no en el caudal.
- **Lectura.** Sin atribución (ablación `A1` de E18, que la sustituye por un criterio estadístico)
  las diecisiete decisiones son las mismas en validación; en prueba se repiten, sin valor de
  confirmación independiente. La atribución **explica sin decidir**.
- **Límite.** Atribución no causal, tres casos por condición y una sola ejecución, sobre datos
  sintéticos.

## Cómo leer este notebook

Modalidad: visualización de evidencia histórica; lee los artefactos de E9 y E18 sin recalcular
nada. CPU, sin red, menos de un minuto.

- **1–5** Introducción, objetivo e hipótesis, fundamento (qué es y qué no es un valor de Shapley),
  entorno y el conjunto con lo que se explica.
- **6–8** Señal principal frente a las declaradas; el mapa de atribución y la regla de
  compensación del caudalímetro; dispersión caso a caso y confianza sin calibrar.
- **9** La importancia global del bosque por impureza y en qué se diferencia de Shapley.
- **10** De la atribución a la observación del informe.
- **11** La ablación `A1`: qué cambia al retirar la atribución.
- **12–16** Resultados negativos y limitaciones, discusión, conclusiones, reproducibilidad y
  referencias."""),
    md("""\
## 1. Introducción: por qué una predicción no basta

Un bosque aleatorio que dice `F02_maf_drift` con confianza 0,66 no ha dicho nada que un mecánico
pueda comprobar. Para que la hipótesis sea **verificable** hace falta saber **sobre qué** se
sostiene: qué señales, en qué dirección y con cuánto peso.

Lo que no sabemos antes de empezar:

1. **Si el modelo usa las señales que la física del fallo predice.** Podría estar explotando una
   correlación espuria del generador.
2. **Si la atribución es estable** entre casos de la misma condición.
3. **Si las señales que elige tienen respaldo documental.** Una observación sobre una señal que el
   manual no menciona no puede anclarse: el sistema tendría que abstenerse."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Caracterizar en qué señales se apoya cada diagnóstico y contrastarlo con la firma
declarada en el catálogo de fallos.

**Hipótesis.** Las señales de mayor atribución coinciden con las que la ficha de cada fallo declara
como afectadas.

**Variables observadas.** Importancia de Shapley por descriptor, su signo, el valor del descriptor y
la confianza de la predicción.

**Criterio.** Para cada condición, la señal de mayor atribución debe estar entre las declaradas en
`affected_signals`. El experimento registra esa comparación caso a caso, de modo que el criterio no
se decide después.

**Qué la cuestionaría.** Que la señal principal no esté entre las declaradas. No ocurre en ninguna
de las cinco condiciones de fallo (en `F00_normal` la comparación no aplica, apartado 6). En la
deriva del caudalímetro la señal principal está declarada, pero **no es el caudalímetro**
(apartado 7)."""),
    md("""\
## 3. Fundamento: valores de Shapley y qué no son

**De dónde vienen.** Son un reparto de la teoría de juegos cooperativos: dado un resultado producido
por varios jugadores, ¿cuánto aportó cada uno? Trasladado a un clasificador, los jugadores son los
descriptores y el resultado es la probabilidad de la clase predicha.

**Cómo se calcula aquí.** Con `shap.explainers.Permutation`: se permuta el valor de cada descriptor
por el de un **fondo de referencia** y se mide cuánto cambia la probabilidad. El fondo son 100
ventanas de la clase **sin fallo** tomadas de entrenamiento, con su huella registrada
(`8757d917835e3981`). Esa elección define el significado de toda la atribución: lo que se mide es
**cuánto se aparta este caso de un motor sano**, no una importancia absoluta.

**Por qué permutación y no el estimador exacto para árboles.** El exacto es más rápido, pero depende
de la estructura interna del modelo. El de permutación trata al clasificador como una caja negra, de
modo que la misma atribución serviría si mañana el bosque se sustituyera por otra cosa. La
comparación entre recorridos es lo que el trabajo necesita.

**Qué NO es un valor de Shapley.** No es una relación causal. Dice cuánto cambia la **predicción del
modelo** al cambiar un descriptor, no cuánto cambia la **avería** al cambiar la señal. Entre señales
correlacionadas la atribución se reparte de forma inestable. Eso es una propiedad del método, no
del fallo (apartado 12)."""),
    md("""\
## 4. Preparación del entorno"""),
    code(PREAMBULO),
    code("""\
soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "las atribuciones se leen de artifacts/tables/E9_*.csv y del registro; no se recalcula "
    "ninguna. Recalcularlas exigiría reentrenar el bosque y volver a ejecutar el explicador "
    "y lo que este notebook enseña es lo que E9 midió",
)"""),
    md("""\
## 5. El conjunto y el procedimiento

Dieciocho casos: tres ventanas por cada una de las seis condiciones, tomadas de la partición de
**validación**. De cada uno se explican los **diez descriptores de mayor importancia**. Los **tres
primeros** son los que después viajan al informe como observaciones.

Lo que se explica es la función `predict_proba` **de la clase predicha** y no la probabilidad de la
clase verdadera. Es deliberado: lo que hay que justificar es la hipótesis que el
sistema va a sostener, también cuando se equivoca."""),
    code("""\
import pandas as pd

registro = soporte.registro("E9_xai_synthetic_v2")
atribuciones = soporte.tabla("E9_atribuciones_synthetic_v2")
resumen = soporte.tabla("E9_resumen_synthetic_v2")

print(f"explicador        {registro['explainer']}")
print(f"función explicada {registro['explained_function']}")
print(f"modelo            {registro['model_id']}")
print(f"casos             {registro['n_cases']}")
print(f"fondo             {registro['background']['n']} ventanas de "
      f"{registro['background']['source']}, huella {registro['background']['hash']}")
print()
print(f"{len(atribuciones)} atribuciones = {registro['n_cases']} casos × "
      f"{len(atribuciones) // registro['n_cases']} descriptores explicados cada uno")
print("de los que los tres primeros viajan al informe como observaciones")"""),
    md("""\
## 6. ¿Mira el modelo donde la ficha del fallo dice?

**Qué queremos investigar.** Si la señal de mayor atribución de cada condición está entre las que su
ficha declara afectadas.

**Qué datos utilizamos.** La tabla resumen de E9, con esa comparación hecha caso a caso. Al ser una
comparación de conjuntos de nombres, se lee mejor en tabla que en una figura."""),
    code("""\
resumen[["predicted_class", "n_cases", "mean_confidence", "top_signals",
         "declared_by_fault", "top_signal_declared"]]"""),
    md("""\
**Qué muestra.** En **cinco de las seis** condiciones la señal principal está entre las declaradas.
La excepción es `F00_normal`, que no tiene ficha: no es un fallo, de modo que la columna de señales
declaradas está vacía y la comparación no aplica.

**Qué podemos interpretar.** En las cinco condiciones la señal de mayor atribución es una de las
que declara la ficha del generador, aunque en el fallo de encendido parte del peso (un 13 %) cae en
señales no declaradas (apartado 7). Eso permite anclar después la observación en el manual.

**Qué no podemos afirmar.** Que la coincidencia implique que el modelo *entiende* el fallo. El
generador produjo los datos con esas mismas reglas, así que la coincidencia es, en parte, una
comprobación de que el modelo aprendió lo que se le puso delante. En datos reales la firma podría
estar en otro sitio."""),
    md("""\
## 7. El mapa de atribución: la deriva del caudalímetro no se ve en el caudalímetro

**Qué queremos investigar.** Qué señales sostienen cada diagnóstico (con su peso) y dónde la
atribución se aparta de lo esperable, sobre todo en la fila del caudalímetro.

**Qué datos utilizamos.** Las 180 atribuciones, agregadas por condición y señal. Seis condiciones
por las señales que aparecen en la atribución (diez de las doce, más el descriptor compuesto
`stft_bank1+ltft_bank1`) forman una matriz; el mapa de calor deja ver dónde se concentra el peso y
dónde hay huecos."""),
    code("""\
import matplotlib.pyplot as plt
import numpy as np

from mecanico_ia_exp.obd.faults import FAULTS
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.visualization.memoria.base import CONDICION
from mecanico_ia_exp.visualization.style import SEQUENTIAL, apply_style

apply_style()

# Nombres en español de las señales y de las condiciones. Solo cambian los rótulos.
NOMBRE_SENAL = {
    "rpm": "régimen del motor",
    "vehicle_speed": "velocidad",
    "engine_load": "carga calculada",
    "throttle_position": "posición de mariposa",
    "coolant_temperature": "temperatura del refrigerante",
    "intake_air_temperature": "temperatura del aire de admisión",
    "maf": "caudal de aire (MAF)",
    "map": "presión del colector (MAP)",
    "stft_bank1": "ajuste a corto plazo (STFT)",
    "ltft_bank1": "ajuste a largo plazo (LTFT)",
    "oxygen_sensor": "sonda lambda",
    "ignition_timing": "avance del encendido",
    "stft_bank1+ltft_bank1": "correlación STFT y LTFT",
}


def nombre_condicion(clase: str) -> str:
    return f"{clase.split('_')[0]} {CONDICION.get(clase, clase)}"


# Peso total de cada señal en cada condición, normalizado por condición para que
# las seis sean comparables entre sí.
# Se agrega el valor ABSOLUTO: una atribución negativa --el descriptor empuja
# en contra de la clase predicha-- también es peso explicativo. Sumar con signo
# dejaría que dos aportes opuestos se cancelaran y la fracción pasara de 1.
atribuciones = atribuciones.assign(peso=atribuciones["importance"].abs())
matriz = (
    atribuciones.groupby(["predicted_class", "signal"])["peso"].sum().unstack(fill_value=0.0)
)
# Las señales COMPUESTAS --descriptores de correlación cruzada como
# `stft_bank1+ltft_bank1`-- se conservan. Reindexar solo por SIGNAL_NAMES las
# descartaba en silencio antes de calcular el total de cada condición, de modo
# que inflaba la fracción de las demás con el peso que acababa de tirar.
simples = [s for s in SIGNAL_NAMES if s in matriz.columns]
compuestas = sorted(c for c in matriz.columns if c not in simples)
matriz = matriz.reindex(columns=simples + compuestas)
normalizada = matriz.div(matriz.sum(axis=1), axis=0)

fig, eje = plt.subplots(figsize=(5.9, 4.4))
imagen = eje.imshow(normalizada.to_numpy(), cmap=SEQUENTIAL, aspect="auto")
eje.set_xticks(range(len(normalizada.columns)),
               [NOMBRE_SENAL.get(c, c) for c in normalizada.columns], rotation=55,
               ha="right", fontsize=7)
if compuestas:
    # Una línea separa las doce señales de los descriptores compuestos.
    eje.axvline(len(simples) - 0.5, color="#52514e", linewidth=1.0)
    eje.text(len(simples) - 0.35, -0.75, "descriptor compuesto", fontsize=6.5,
             color="#52514e")
eje.set_yticks(range(len(normalizada.index)),
               [nombre_condicion(c) for c in normalizada.index], fontsize=7.5)
eje.grid(False)

# Se marca con un punto la señal que la ficha del fallo DECLARA afectada: así se
# ve si el peso cae donde debería.
for i, condicion in enumerate(normalizada.index):
    declaradas = FAULTS[condicion].affected_signals if condicion in FAULTS else ()
    for j, senal in enumerate(normalizada.columns):
        if senal in declaradas:
            eje.plot(j, i, marker="o", markersize=3.5, color="#d94f2b", zorder=3)

barra = fig.colorbar(imagen, ax=eje, shrink=0.85)
barra.set_label("fracción del peso explicativo total de la condición", fontsize=7)
from matplotlib.lines import Line2D

eje.legend(
    handles=[Line2D([], [], marker="o", linestyle="none", markersize=4, color="#d94f2b",
                    label="señal que la ficha del fallo declara afectada")],
    loc="lower left", bbox_to_anchor=(0.0, 1.0), fontsize=7, frameon=False,
    borderaxespad=0.2,
)
eje.set_xlabel("señal a la que pertenece el descriptor")
eje.set_ylabel("condición predicha")
fig.tight_layout()
fig.suptitle(
    "Atribución de Shapley del bosque (E9) por condición predicha y señal",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.02,
    "E9 · synthetic_v2, validación, 18 casos · suma del valor absoluto de las atribuciones de "
    "cada señal, dividida por el total de la fila · F00 sin fallo no tiene ficha ni puntos\\n"
    "Faltan dos de las doce señales, entre ellas el caudal (MAF), porque no figuran en "
    "ninguna atribución",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB04-01_mapa_atribucion", subdirectorio="04_explicabilidad")
plt.show()

print(f"señales simples: {len(simples)} · compuestas conservadas: {compuestas}")
print("\\nDeriva del caudalímetro · peso de cada señal:")
fila = normalizada.loc["F02_maf_drift"].sort_values(ascending=False)
print(fila[fila > 0.01].round(3).to_string())"""),
    md("""\
**Qué muestra.** En cada condición, el peso se concentra en pocas señales y casi siempre sobre las
que la ficha declara (los puntos). En la fila de la **deriva del caudalímetro** el peso está en los
**ajustes de combustible**; la señal `maf`, que es el componente que falla y está declarada en la
ficha, no figura entre los diez descriptores principales de ningún caso.

**Qué podemos interpretar.** Que el modelo recupera la regla de compensación que el generador
implementa, la misma que E4 ya había visto: el caudalímetro contaminado **subestima** el aire que
entra, la centralita compensa inyectando más combustible y el desajuste aparece en los ajustes a
corto y largo plazo, mientras el caudal sigue siendo plausible para el régimen y la carga. La firma
de un fallo no está necesariamente en la señal del componente que falla.

**Qué no podemos afirmar.** Que sea causal (apartado 3), ni que un caudalímetro real se comporte
así: es la regla del generador. Con `ltft_bank1` y
`stft_bank1` fuertemente correlacionados, el reparto entre esos dos es inestable: otra semilla
podría asignar más peso a uno u otro sin que cambie nada del fenómeno."""),
    md("""\
## 8. La atribución caso a caso y su dispersión

**Qué queremos investigar.** Si la atribución es estable entre los tres casos de cada condición o si
cambia de un caso a otro. Una atribución inestable produciría informes que señalan cosas distintas
ante el mismo fallo y un mecánico no podría fiarse de ella. Por eso se dibujan los tres casos uno a
uno: una barra de media escondería la dispersión."""),
    code("""\
from mecanico_ia_exp.visualization.style import CATEGORICAL

principales = (
    atribuciones[atribuciones["rank"] == 1]
    .groupby(["predicted_class", "signal"])
    .size()
    .rename("casos")
    .reset_index()
)

fig, (izq, der) = plt.subplots(1, 2, figsize=(9.8, 4.0), width_ratios=[1.25, 1])

condiciones = sorted(atribuciones["predicted_class"].unique())
for i, condicion in enumerate(condiciones):
    sub = atribuciones[(atribuciones["predicted_class"] == condicion) & (atribuciones["rank"] == 1)]
    izq.scatter(sub["importance"], [i] * len(sub), s=55, alpha=0.8,
                color=CATEGORICAL[i % len(CATEGORICAL)])
izq.set_yticks(range(len(condiciones)), [nombre_condicion(c) for c in condiciones],
               fontsize=7.5)
izq.set_xlabel("importancia de Shapley del descriptor principal (adimensional)")
izq.set_title("Dispersión entre los tres casos de cada condición", fontsize=9)

confianzas = atribuciones.groupby("predicted_class")["confidence"].agg(["min", "mean", "max"])
posiciones = np.arange(len(confianzas))
der.hlines(posiciones, confianzas["min"], confianzas["max"], color="#c3c2b7", linewidth=2.5)
der.scatter(confianzas["mean"], posiciones, s=55, color=CATEGORICAL[0], zorder=3)
# NO se dibuja el umbral de 0,79 de E19: esta confianza es la de
# `predict_proba` en CRUDO --xai_runner entrena un bosque sin calibrar-- y aquel
# umbral se aplica a la probabilidad calibrada. Son magnitudes distintas y
# superponerlas invitaría a una comparación que no se sostiene.
der.set_yticks(posiciones, [""] * len(posiciones))
der.set_xlabel("confianza SIN calibrar (predict_proba, 0–1)")
der.set_title("Confianza sin calibrar: mínimo, media y máximo", fontsize=9)
der.set_xlim(0.3, 1.05)

fig.suptitle(
    "Qué tan estable es la atribución y con cuánta confianza decide el modelo",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E9 atribución · synthetic_v2, validación · tres casos por condición · "
    "fuente: artifacts/tables/E9_atribuciones_synthetic_v2.csv · "
    "la confianza es de predict_proba SIN calibrar: E9 no calibra",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB04-02_dispersion", subdirectorio="04_explicabilidad")
plt.show()

print(confianzas.round(4).to_string())"""),
    md("""\
**Qué muestra.** A la izquierda, la importancia del descriptor principal de cada caso: dentro de una
condición los tres puntos caen cerca, salvo en el fallo de encendido y en la clase sin fallo. A la
derecha, la confianza sin calibrar: el termostato y la sonda por encima de 0,91 de media; la fuga, la
deriva y el encendido entre 0,64 y 0,72.

**Qué podemos interpretar.** La atribución es razonablemente estable en las condiciones que el modelo
diagnostica con confianza alta y dispersa en las que no. Es consistente: cuando el modelo no está
seguro, tampoco está seguro de qué lo llevó ahí.

**Qué no podemos afirmar.** Que estas cifras expliquen las abstenciones de E19. **Son otra magnitud**: `xai_runner` entrena un bosque
**sin calibrar** y lo que aquí se dibuja es `predict_proba` en crudo, mientras el umbral de 0,79 de
E19 se aplica a la probabilidad **calibrada**, que puede reordenar. Ponerlas juntas por compartir
escala sería comparar dos cifras que miden cosas distintas.

Lo que sí puede decirse es más débil de lo que parecía: las condiciones con menos confianza aquí
son cuatro (sin fallo, fuga, caudalímetro y encendido), no dos. Cualquier conexión con las
abstenciones de E19 exigiría comparar las confianzas **calibradas** de las mismas ventanas. Esos
valores están en el registro de E19, no en el de E9.

Tampoco se puede afirmar nada sobre la estabilidad frente a otra semilla o a otro reparto: son tres
casos por condición y una sola ejecución. Ni que una atribución estable sea una atribución correcta."""),
    md("""\
## 9. La importancia global del bosque y en qué se diferencia de Shapley

**Qué queremos investigar.** Qué descriptores pesan más en el bosque **en conjunto**, sin mirar
ningún caso concreto. También si esa lectura global coincide con la local de Shapley.

**Qué datos utilizamos.** `artifacts/tables/E6_baseline_importancias_synthetic_v2.csv`, que E6
escribió al entrenar el bosque: la importancia por **impureza** de los 139 descriptores (el atributo
`feature_importances_` de scikit-learn). Para cada descriptor promedia, sobre los 400 árboles,
cuánto reduce la impureza de Gini cada división que lo usa, ponderada por el peso de las ventanas de
**entrenamiento** que llegan a ese nodo (con las clases equilibradas por `class_weight`). Las 139
cifras suman 1.

**En qué se diferencia de Shapley.**

| | Importancia por impureza (E6) | Valores de Shapley (E9) |
|---|---|---|
| Alcance | **global**: una cifra por descriptor para todo el modelo | **local**: una cifra por descriptor y por caso |
| Qué mide | cuánto ordena el descriptor las ventanas de entrenamiento al dividir | cuánto cambia la probabilidad de la clase predicha al sustituir el descriptor por el fondo sano |
| Datos | entrenamiento, durante el ajuste | 18 ventanas de validación |
| Signo | no tiene | sí: a favor o en contra de la clase |
| Sesgo conocido | favorece a los descriptores con muchos valores distintos, porque ofrecen más cortes posibles | depende del fondo elegido |

Ninguna de las dos es causal. Con descriptores correlacionados, las dos reparten el peso entre ellos
de forma inestable."""),
    code("""\
importancias = soporte.tabla("E6_baseline_importancias_synthetic_v2")

ESTADISTICO = {
    "mean": "media", "std": "desviación típica", "min": "mínimo", "max": "máximo",
    "range": "rango", "slope": "pendiente", "delta_min": "mayor bajada entre muestras",
    "delta_max": "mayor subida entre muestras", "n_events": "saltos anómalos",
    "autocorr1": "autocorrelación de retardo 1", "crossings": "cruces por la mediana",
}


def senal_y_estadistico(descriptor: str) -> tuple[str, str]:
    # El nombre es señal_estadístico; se busca la señal más larga que encaje.
    for senal in sorted(SIGNAL_NAMES, key=len, reverse=True):
        if descriptor.startswith(senal + "_"):
            return senal, descriptor[len(senal) + 1:]
    # Correlaciones cruzadas y la razón entre señales no pertenecen a una sola señal.
    return "entre señales", descriptor


importancias[["señal", "estadístico"]] = [
    senal_y_estadistico(d) for d in importancias["feature"]
]
importancias = importancias.sort_values("importance", ascending=False).reset_index(drop=True)
importancias["acumulada"] = importancias["importance"].cumsum()
top = importancias.head(15)

print(f"descriptores: {len(importancias)} · suma de importancias: "
      f"{importancias.importance.sum():.4f}")
print(f"las 15 primeras reúnen {top.importance.sum():.3f} del total")
print()
print("Importancia por señal (suma de sus descriptores, los 139):")
print(importancias.groupby("señal")["importance"].sum().sort_values(ascending=False)
      .round(3).to_string())
top[["feature", "señal", "estadístico", "importance", "acumulada"]].round(4)"""),
    code("""\
fig, eje = plt.subplots(figsize=(7.4, 4.6))
etiquetas = [
    f"{NOMBRE_SENAL.get(f.señal, f.feature)} · {ESTADISTICO.get(f.estadístico, f.estadístico)}"
    for f in top.itertuples()
]
y = np.arange(len(top))
eje.barh(y, top["importance"], color=CATEGORICAL[0], height=0.62)
for yi, valor in zip(y, top["importance"], strict=True):
    eje.text(valor + 0.0006, yi, f"{valor:.3f}".replace(".", ","), va="center", fontsize=6.8)
eje.set_yticks(y, etiquetas, fontsize=7.2)
eje.invert_yaxis()
eje.set_xlabel("importancia por impureza (reducción media de Gini, fracción del total, 0–1)")
eje.grid(axis="y", visible=False)
fig.suptitle(
    "Los 15 descriptores con mayor importancia global en el bosque aleatorio (E6)",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E6 · synthetic_v2, entrenamiento · fuente: artifacts/tables/"
    "E6_baseline_importancias_synthetic_v2.csv · importancia global por impureza, no Shapley: "
    "no tiene signo ni dice nada de un caso concreto",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB04-03_importancia_impureza", subdirectorio="04_explicabilidad")
plt.show()"""),
    md("""\
**Qué muestra.** Ningún descriptor domina: el primero, el máximo del ajuste a largo plazo, se queda
en 0,046 y los quince primeros reúnen algo más de la mitad del peso total (0,509) entre 139. Los
quince pertenecen a cinco señales: la sonda lambda (seis descriptores), la temperatura del
refrigerante (cuatro), los dos ajustes de combustible (dos cada uno) y el régimen del motor (uno,
su mínimo). El caudal de aire no aparece entre ellos. Sumando los descriptores de cada señal, la
sonda reúne 0,218, el ajuste a largo plazo 0,187, el refrigerante 0,184 y el ajuste a corto plazo
0,154; el caudal, 0,030.

**Qué podemos interpretar.** La lectura global es coherente con la local del apartado 7: las
señales que más pesan son señales que alguna ficha de fallo declara (ajustes de combustible para la
fuga y la deriva, refrigerante para el termostato, sonda para su retardo, régimen para el fallo de
encendido) y el caudal sigue sin aparecer, como en Shapley. Que muchos de los quince sean
dinámica intraventana (subidas y bajadas entre muestras, autocorrelación, cruces) respalda que la
representación tabular describe el tiempo dentro de la ventana, como se dijo en el notebook 02.

**Qué no podemos afirmar.**

1. **Que un descriptor importante cause el diagnóstico** ni que la señal cause el fallo. La
   impureza dice qué cortes usó el bosque para separar las ventanas de entrenamiento, no qué
   ocurre en el motor.
2. **Que el orden entre descriptores próximos sea fiable.** Entre puestos consecutivos las cifras
   se separan por unas milésimas; con descriptores correlacionados (los dos ajustes, las variantes de la
   sonda) otra semilla podría reordenarlos. Es una sola ejecución.
3. **Que la importancia por impureza mida lo mismo que Shapley.** Es global, sin signo y se
   calcula sobre entrenamiento; Shapley es local, con signo y sobre validación. Además favorece a
   los descriptores continuos con muchos valores distintos frente a recuentos como los cruces o los
   saltos anómalos, que ofrecen menos cortes.
4. **Nada sobre un caso concreto**: para eso están los apartados 7 y 8."""),
    md("""\
## 10. De la atribución a la observación del informe

Las tres atribuciones principales de cada caso se convierten en las **observaciones** del paquete
de evidencia."""),
    code("""\
# Las tres primeras: son las que el paquete de evidencia lleva como observaciones.
ejemplo = atribuciones[
    (atribuciones["case_id"] == atribuciones["case_id"].iloc[0]) & (atribuciones["rank"] <= 3)
]
print(f"Caso: {ejemplo['case_id'].iloc[0]}")
print(f"Diagnóstico: {ejemplo['predicted_class'].iloc[0]} "
      f"(confianza {ejemplo['confidence'].iloc[0]:.4f})\\n")
for _, fila in ejemplo.sort_values("rank").iterrows():
    print(f"  OBS00{int(fila['rank'])}  {fila['signal']}.{fila['statistic']} = {fila['value']:.4f}"
          f"  ({fila['direction']}, importancia {fila['importance']:.4f})")"""),
    md("""\
**Qué muestra.** Tres observaciones, cada una con señal, estadístico, valor, dirección e
importancia. Es lo que llega al verificador y lo que el redactor tiene que anclar.

**Relación con la pregunta de investigación.** En PI.2, una afirmación del informe solo se admite si existe un fragmento
documental que mencione **esa** señal. La atribución decide, por tanto, qué tiene que buscarse en el
manual; si señalara una señal que el manual no documenta, el sistema tendría que abstenerse
(apartado 1). En la práctica no ocurrió; la ablación `A1` de E18 midió lo que eso vale."""),
    md("""\
## 11. Lo que la ablación `A1` dice de todo esto

E18 retiró la atribución de Shapley y la sustituyó por un criterio estadístico simple (la desviación
tipificada del descriptor frente a la clase sin fallo), manteniendo todo lo demás."""),
    code("""\
import json

filas = []
for suf, particion in (("", "validación"), ("_prueba", "prueba")):
    try:
        d = soporte.registro(f"E18_ablacion_A1{suf}")
    except Exception:
        continue
    r = d["summary"]
    filas.append({
        "partición": particion,
        "falsa confianza": f"{r['false_confidence']['numerator']}/"
                           f"{r['false_confidence']['denominator']}",
        "abstención innecesaria": f"{r['unnecessary_abstention']['numerator']}/"
                                  f"{r['unnecessary_abstention']['denominator']}",
        "cobertura": f"{r['coverage_full_evidence']['numerator']}/"
                     f"{r['coverage_full_evidence']['denominator']}",
    })
pd.DataFrame(filas).set_index("partición")"""),
    md("""\
**Qué muestra.** `A1` produce **las mismas decisiones que la configuración canónica** en validación,
diecisiete de diecisiete. En prueba repite esas mismas decisiones, lo que no es una confirmación
independiente: la decisión la fijan la condición de evidencia y la puerta de códigos, que no cambian
al cambiar de partición.

**Qué podemos interpretar.** La atribución, **tal como el recorrido la usa**, no cambia ninguna
decisión. Las observaciones que elige son distintas (la ablación selecciona otros
descriptores), pero el conjunto de fragmentos documentales que llega al verificador es el mismo y la
decisión también.

Es un resultado negativo sobre el valor de la atribución en este recorrido y se publica como tal:
**para decidir** no aporta sobre una alternativa mucho más barata. Lo que sí aporta (el contenido
de las observaciones, que es PI.2 y no PI.3) se discute en el apartado 13.

**Qué no podemos afirmar.** Que un criterio estadístico simple sea equivalente en general. Con
diecisiete casos, cinco de ellos con evidencia completa, lo que se ha medido es que en esta muestra
ninguna decisión cambió."""),
    md("""\
## 12. Resultados negativos y limitaciones

1. **La atribución no cambia ninguna decisión** (`A1`, en validación; su repetición en prueba no es
   independiente).
2. **Las señales correlacionadas reparten su atribución de forma inestable.** `engine_load`, `map` y
   `throttle_position` están correlacionadas por encima de 0,99 en este generador (Pearson sobre
   las sesiones sin fallo de la muestra, el mapa de correlación de `01_exploracion_obd`): cuál de
   las tres recibe el peso es en buena medida arbitrario.
3. **Tres casos por condición.** No hay base para hablar de estabilidad.
4. **El fondo de referencia define el significado** (apartado 3): la atribución mide separación
   respecto de un motor sano, no importancia absoluta. Con otro fondo, otros números.
5. **La atribución no es causal** (apartado 3) y este notebook no la presenta como tal en ningún
   punto.
6. **El registro de E9 no lleva cabecera de identificación**: le faltan `commit` y `executed_at`,
   como a los de E6 y E7. Es anterior a la convención y no se regenera, porque regenerar cambiaría
   las cifras publicadas."""),
    md("""\
## 13. Discusión

E9 aporta menos de lo que su nombre sugiere y más de lo que su ablación indicaría.

**Menos**, porque la atribución no decide: `A1` lo midió y las diecisiete decisiones fueron las
mismas. Si el objetivo fuera solo decidir bien, podría retirarse.

**Más**, porque es lo que convierte una predicción en algo **contrastable**. Sin observaciones no hay
nada que anclar en el manual; PI.2 dejaría de tener objeto. La atribución no mejora la decisión; hace posible la
explicación.

Deja una lectura que sobrevive a todo lo anterior, la del apartado 7: en este generador, un
sistema que vigilara cada sensor para detectar su propio fallo no habría encontrado la deriva del
caudalímetro."""),
    md("""\
## 14. Conclusiones

**Qué aprendimos.** Que la señal principal de cada fallo es una de las que declara su ficha; que el
modelo recupera la regla de compensación del generador y detecta la deriva del caudalímetro en los
ajustes de combustible y no en el caudal;
y que la atribución, en este recorrido, explica sin decidir.

**Qué hipótesis recibió apoyo.** Que las señales de mayor atribución coinciden con las declaradas, en
las cinco condiciones de fallo.

**Qué no recibió apoyo.** Nada se refuta, pero `A1` acota el valor de la atribución: no cambia
ninguna decisión.

**Qué permanece sin demostrar.** Que estas atribuciones se parezcan a las que daría telemetría real.
Que sean estables frente a otra semilla. Que el reparto entre señales correlacionadas tenga algún
significado.

**Cómo contribuye al TFM.** Sostiene el capítulo de explicabilidad y es la pieza que une el
diagnóstico con la evidencia documental: sin observaciones no hay nada que verificar.

## 15. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb` |
| **Datos** | ninguno: se leen artefactos versionados |
| **Semilla** | 20260901 |
| **Fondo** | 100 ventanas de la clase sin fallo, huella `8757d917835e3981` |
| **Commit** | el que imprime la celda del apartado 4 |
| **Tiempo** | menos de un minuto |
| **Recursos** | CPU |
| **Artefactos que produce** | tres figuras en `notebooks/salida/04_explicabilidad/`, PNG y SVG |

**Qué no se reproduce aquí.** Las atribuciones (véase la modalidad en el apartado 4). En modo FULL,
`mecanico-exp xai --dataset-id synthetic_v2 --etiqueta <nombre>`, que escribe con etiqueta propia y
**no sobrescribe** los artefactos publicados.

## 16. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** El mapa de atribución es la **Figura 5.15** del capítulo 5, en el apartado de PI.1. El resumen por diagnóstico está en el anexo B, **Tabla B.3**. La lectura de la ablación `A1` que este notebook discute aparece junto a la **Figura 5.18**.

- `docs/experiments/E9_atribucion.md`: informe de la fase
- `experiments/E9_xai_synthetic_v2.json`: registro, con el fondo y su huella
- `artifacts/tables/E9_atribuciones_synthetic_v2.csv`: las 180 atribuciones
- `artifacts/tables/E9_resumen_synthetic_v2.csv`: la comparación con las señales declaradas
- `artifacts/tables/E6_baseline_importancias_synthetic_v2.csv`: la importancia por impureza de los 139 descriptores
- `src/mecanico_ia_exp/experiments/baseline_runner.py`: dónde se escribe esa tabla, a partir de `feature_importances_`
- `src/mecanico_ia_exp/xai/attribution.py`: el explicador y la selección de fondo
- `src/mecanico_ia_exp/obd/faults.py`: las fichas con `affected_signals`
- `docs/experiments/E18_ablaciones.md` y `E18_ablaciones_prueba.md`: la ablación `A1`
- `docs/experiments/E4_eda_temporal.md`: donde apareció por primera vez la compensación del caudalímetro"""),
]

if __name__ == "__main__":
    escribir("04_explicabilidad.ipynb", CELDAS)
