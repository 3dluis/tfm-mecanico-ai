"""Construye `04_explicabilidad.ipynb`: atribución de Shapley sobre el bosque (E9)."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Explicabilidad: qué señal sostiene cada diagnóstico

**Notebook** `04_explicabilidad` · **versión** 1.0 · **fecha** 13 de octubre de 2026

| | |
|---|---|
| **Experimento** | E9, atribución |
| **Conjunto** | `synthetic_v2`, partición de validación · 18 casos, tres por condición |
| **Protocolo** | `shap.explainers.Permutation` sobre `predict_proba` de la clase predicha |
| **Estado** | cerrado y validado |
| **Pregunta de investigación** | PI.1 —qué sostiene el diagnóstico— y PI.2, porque la atribución es la **observación** que después hay que anclar en un documento |
| **Evidencia original** | `experiments/E9_xai_synthetic_v2.json`, `artifacts/tables/E9_atribuciones_synthetic_v2.csv`, `E9_resumen_synthetic_v2.csv` |

---

## Qué investiga este notebook

Si lo que el modelo mira para decidir coincide con lo que la ficha del fallo dice que debería
mirarse. No es una pregunta estética: el recorrido completo convierte la atribución en las
**observaciones** del informe, y cada observación tiene que anclarse después en un fragmento del
manual. Si el modelo decidiera por una señal que la ficha no menciona, el sistema tendría que
escribir una explicación sobre algo que el manual no documenta.

Hay además un hallazgo que conviene anticipar porque es contraintuitivo: **la deriva del
caudalímetro no se detecta mirando el caudalímetro.**"""),

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
   manual no menciona no puede anclarse, y el sistema tendría que abstenerse."""),

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

**Qué la cuestionaría.** Que la señal principal no esté entre las declaradas. Ocurre en una de las
seis, y es el resultado más interesante del experimento."""),

    md("""\
## 3. Fundamento: valores de Shapley, y qué no son

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
modelo** al cambiar un descriptor, no cuánto cambia la **avería** al cambiar la señal. Si dos señales
están correlacionadas —y aquí varias lo están mucho— la atribución se reparte entre ellas de forma
inestable, y eso es una propiedad del método, no del fallo."""),

    md("""\
## 4. Preparación del entorno"""),

    code(PREAMBULO),

    code('''\
soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "las atribuciones se leen de artifacts/tables/E9_*.csv y del registro; no se recalcula "
    "ninguna. Recalcularlas exigiría reentrenar el bosque y volver a ejecutar el explicador, "
    "y lo que este notebook enseña es lo que E9 midió",
)'''),

    md("""\
## 5. El conjunto y el procedimiento

Dieciocho casos: tres ventanas por cada una de las seis condiciones, tomadas de la partición de
**validación**. De cada uno se explican los **diez descriptores de mayor importancia**, y los **tres
primeros** son los que después viajan al informe como observaciones.

Conviene saber qué se explica exactamente: la función `predict_proba` **de la clase predicha**. No la
probabilidad de la clase verdadera. Es deliberado: lo que hay que justificar es la hipótesis que el
sistema va a sostener, también cuando se equivoca."""),

    code('''\
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
print("de los que los tres primeros viajan al informe como observaciones")'''),

    md("""\
## 6. ¿Mira el modelo donde la ficha del fallo dice?

**Qué queremos investigar.** Si la señal de mayor atribución de cada condición está entre las que su
ficha declara afectadas.

**Qué datos utilizamos.** La tabla resumen de E9, que ya trae esa comparación hecha caso a caso.

**Por qué esta tabla y no un gráfico.** Es una comparación de conjuntos de nombres: una tabla se lee
mejor que cualquier figura."""),

    code('''\
resumen[["predicted_class", "n_cases", "mean_confidence", "top_signals",
         "declared_by_fault", "top_signal_declared"]]'''),

    md("""\
**Lo observado.** En **cinco de las seis** condiciones la señal principal está entre las declaradas.
La excepción es `F00_normal`, que no tiene ficha: no es un fallo, de modo que la columna de señales
declaradas está vacía y la comparación no aplica.

**Qué podemos interpretar.** El modelo no está explotando un atajo del generador: decide sobre las
señales que la física aproximada del fallo predice. Eso es lo que permite que la observación se
ancle después en un fragmento del manual que hable de esa misma señal.

**Qué no podemos afirmar.** Que la coincidencia implique que el modelo «entiende» el fallo. El
generador produjo los datos con esas mismas reglas, así que la coincidencia es, en parte, una
comprobación de que el modelo aprendió lo que se le puso delante. En datos reales la firma podría
estar en otro sitio."""),

    md("""\
## 7. El hallazgo: la deriva del caudalímetro no se ve en el caudalímetro

**Qué queremos investigar.** Qué señales sostienen cada diagnóstico, con su peso, y dónde la
atribución se aparta de lo esperable.

**Qué datos utilizamos.** Las 180 atribuciones, agregadas por condición y señal.

**Por qué un mapa de calor.** Seis condiciones por doce señales es una matriz; el mapa deja ver de
un vistazo dónde se concentra el peso y dónde hay huecos.

**Qué debemos observar.** La fila del caudalímetro."""),

    code('''\
import matplotlib.pyplot as plt
import numpy as np

from mecanico_ia_exp.obd.faults import FAULTS
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.visualization.style import SEQUENTIAL, apply_style

apply_style()

# Peso total de cada señal en cada condición, normalizado por condición para que
# las seis sean comparables entre sí.
# Se agrega el valor ABSOLUTO: una atribución negativa --el descriptor empuja
# en contra de la clase predicha-- también es peso explicativo. Sumar con signo
# dejaría que dos aportes opuestos se cancelaran y la fracción pasara de 1.
atribuciones = atribuciones.assign(peso=atribuciones["importance"].abs())
matriz = (
    atribuciones.groupby(["predicted_class", "signal"])["peso"].sum().unstack(fill_value=0.0)
)
matriz = matriz.reindex(columns=[s for s in SIGNAL_NAMES if s in matriz.columns])
normalizada = matriz.div(matriz.sum(axis=1), axis=0)

fig, eje = plt.subplots(figsize=(9.4, 4.2))
imagen = eje.imshow(normalizada.to_numpy(), cmap=SEQUENTIAL, aspect="auto")
eje.set_xticks(range(len(normalizada.columns)), normalizada.columns, rotation=55,
               ha="right", fontsize=7)
eje.set_yticks(range(len(normalizada.index)), normalizada.index, fontsize=7.5)
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
fig.suptitle(
    "Dónde mira el modelo · el punto marca las señales que la ficha del fallo declara",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E9 atribución · synthetic_v2, validación, 18 casos · "
    "fuente: artifacts/tables/E9_atribuciones_synthetic_v2.csv · "
    "valores de Shapley por permutación, fondo de 100 ventanas sin fallo",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB04-01_mapa_atribucion", subdirectorio="04_explicabilidad")
plt.show()

print("Deriva del caudalímetro · peso de cada señal:")
fila = normalizada.loc["F02_maf_drift"].sort_values(ascending=False)
print(fila[fila > 0.01].round(3).to_string())'''),

    md("""\
**Qué muestra.** El peso se concentra, en cada condición, en pocas señales, y casi siempre sobre las
que la ficha declara —los puntos—. La fila de la **deriva del caudalímetro** es la excepción
llamativa: el peso está en los **ajustes de combustible**, y la señal `maf`, que es el componente que
falla y está declarada en la ficha, **recibe una fracción mínima**.

**Qué podemos interpretar.** Es coherente con el mecanismo físico y es el hallazgo que E4 ya había
anticipado: un caudalímetro contaminado **subestima** el aire que entra, la centralita compensa
inyectando más combustible, y el desajuste aparece en los ajustes a corto y largo plazo. El valor
absoluto del caudal sigue siendo plausible para el régimen y la carga; lo que no es plausible es la
corrección que la centralita necesita.

**La consecuencia práctica, que es lo que importa:** un sistema de diagnóstico que buscara el fallo
del caudalímetro **mirando el caudalímetro** no lo encontraría. La firma de un fallo no está
necesariamente en la señal del componente que falla.

**Qué no podemos afirmar.** Que la atribución sea causal: dice dónde mira el modelo, no qué causa
qué. Y con `ltft_bank1` y `stft_bank1` fuertemente correlacionados, el reparto entre esos dos es
inestable: otra semilla podría asignar más peso a uno u otro sin que cambie nada del fenómeno."""),

    md("""\
## 8. La atribución caso a caso, y su dispersión

**Qué queremos investigar.** Si la atribución es estable entre los tres casos de cada condición o si
cambia de un caso a otro.

**Por qué importa.** Una atribución inestable produciría informes que señalan cosas distintas ante
el mismo fallo, y un mecánico no podría fiarse de ella.

**Por qué un gráfico de puntos y no barras.** Son tres observaciones por condición: dibujarlas una a
una muestra la dispersión, que es justo lo que se quiere ver. Una barra de media la escondería."""),

    code('''\
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
izq.set_yticks(range(len(condiciones)), condiciones, fontsize=7.5)
izq.set_xlabel("importancia de Shapley del descriptor principal (adimensional)")
izq.set_title("Dispersión entre los tres casos de cada condición", fontsize=9)

confianzas = atribuciones.groupby("predicted_class")["confidence"].agg(["min", "mean", "max"])
posiciones = np.arange(len(confianzas))
der.hlines(posiciones, confianzas["min"], confianzas["max"], color="#c3c2b7", linewidth=2.5)
der.scatter(confianzas["mean"], posiciones, s=55, color=CATEGORICAL[0], zorder=3)
der.axvline(0.79, color="#d94f2b", linestyle="--", linewidth=1.0)
der.text(0.795, -0.4, "umbral de\\nconfianza 0,79", fontsize=6.8, color="#d94f2b")
der.set_yticks(posiciones, [""] * len(posiciones))
der.set_xlabel("confianza calibrada (probabilidad, 0–1)")
der.set_title("Confianza: mínimo, media y máximo", fontsize=9)
der.set_xlim(0.3, 1.05)

fig.suptitle(
    "Qué tan estable es la atribución, y con cuánta confianza decide el modelo",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E9 atribución · synthetic_v2, validación · tres casos por condición · "
    "fuente: artifacts/tables/E9_atribuciones_synthetic_v2.csv",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB04-02_dispersion", subdirectorio="04_explicabilidad")
plt.show()

print(confianzas.round(4).to_string())'''),

    md("""\
**Qué muestra.** A la izquierda, la importancia del descriptor principal de cada caso: dentro de una
condición los tres puntos caen cerca, salvo en el fallo de encendido y en la clase sin fallo. A la
derecha, la confianza: el termostato y la sonda deciden por encima del umbral de 0,79; la fuga, la
deriva y el encendido quedan por debajo o alrededor.

**Qué podemos interpretar.** La atribución es razonablemente estable en las condiciones que el modelo
diagnostica con confianza alta, y dispersa en las que no. Es consistente: cuando el modelo no está
seguro, tampoco está seguro de qué lo llevó ahí.

Y conecta directamente con el criterio de abstención: las dos condiciones cuya confianza media queda
por debajo de 0,79 son exactamente las que, en E19, produjeron las dos abstenciones innecesarias.
**No es casualidad: es el mismo umbral actuando sobre la misma debilidad del modelo.**

**Qué no podemos afirmar.** Nada sobre la estabilidad frente a otra semilla o a otro reparto: son
tres casos por condición y una sola ejecución. Tampoco que una atribución estable sea una atribución
correcta."""),

    md("""\
## 9. De la atribución a la observación del informe

Lo que hace que este experimento no sea un ejercicio decorativo: las tres atribuciones principales de
cada caso se convierten en las **observaciones** del paquete de evidencia, con su señal, su
estadístico, su valor y su dirección. Y cada observación tiene que anclarse después en un fragmento
del manual que hable de esa señal."""),

    code('''\
# Las tres primeras: son las que el paquete de evidencia lleva como observaciones.
ejemplo = atribuciones[
    (atribuciones["case_id"] == atribuciones["case_id"].iloc[0]) & (atribuciones["rank"] <= 3)
]
print(f"Caso: {ejemplo['case_id'].iloc[0]}")
print(f"Diagnóstico: {ejemplo['predicted_class'].iloc[0]} "
      f"(confianza {ejemplo['confidence'].iloc[0]:.4f})\\n")
for _, fila in ejemplo.sort_values("rank").iterrows():
    print(f"  OBS00{int(fila['rank'])}  {fila['signal']}.{fila['statistic']} = {fila['value']:.4f}"
          f"  ({fila['direction']}, importancia {fila['importance']:.4f})")'''),

    md("""\
**Lo observado.** Tres observaciones, cada una con señal, estadístico, valor, dirección e
importancia. Es exactamente lo que llega al verificador y lo que el redactor tiene que anclar.

**Por qué esto importa para PI.2.** Una afirmación del informe solo se admite si existe un fragmento
documental que mencione **esa** señal. La atribución decide, por tanto, qué tiene que buscarse en el
manual; si señalara una señal que el manual no documenta, el sistema se quedaría sin respaldo y
tendría que abstenerse. En la práctica no ocurrió, y la ablación `A1` de E18 midió lo que eso vale."""),

    md("""\
## 10. Lo que la ablación `A1` dice de todo esto

E18 retiró la atribución de Shapley y la sustituyó por un criterio estadístico simple —la desviación
tipificada del descriptor frente a la clase sin fallo— manteniendo todo lo demás."""),

    code('''\
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
pd.DataFrame(filas).set_index("partición")'''),

    md("""\
**Qué muestra.** `A1` produce **las mismas decisiones que la configuración canónica**, en validación
y en prueba. Diecisiete de diecisiete, las dos veces.

**Qué podemos interpretar.** La atribución de Shapley, **tal como el recorrido la usa**, no cambia
ninguna decisión. Las observaciones que elige son distintas —la ablación selecciona otros
descriptores— pero el conjunto de fragmentos documentales que llega al verificador es el mismo, y la
decisión también.

Es un resultado negativo sobre el valor de la atribución en este recorrido, y se publica como tal. No
dice que la atribución no sirva: dice que **para decidir** no aporta sobre una alternativa mucho más
barata. Para **explicar** sigue siendo lo que da contenido a las observaciones, y eso es PI.2, no
PI.3.

**Qué no podemos afirmar.** Que un criterio estadístico simple sea equivalente en general. Con
diecisiete casos, cinco de ellos con evidencia completa, lo que se ha medido es que en esta muestra
ninguna decisión cambió."""),

    md("""\
## 11. Resultados negativos y limitaciones

1. **La atribución no cambia ninguna decisión** (`A1`, en validación y en prueba).
2. **Las señales correlacionadas reparten su atribución de forma inestable.** `engine_load`, `map` y
   `throttle_position` están correlacionadas por encima de 0,99 en este generador: cuál de las tres
   recibe el peso es en buena medida arbitrario.
3. **Tres casos por condición.** No hay base para hablar de estabilidad.
4. **El fondo de referencia define el significado.** Son 100 ventanas de la clase sin fallo de
   entrenamiento: toda la atribución mide separación respecto de un motor sano, no importancia
   absoluta. Con otro fondo, otros números.
5. **La atribución no es causal**, y este notebook no la presenta como tal en ningún punto.
6. **El registro de E9 no lleva cabecera de identificación**: le faltan `commit` y `executed_at`,
   como a los de E6 y E7. Es anterior a la convención y no se regenera, porque regenerar cambiaría
   las cifras publicadas."""),

    md("""\
## 12. Discusión

Lo que E9 aporta al trabajo es menos de lo que su nombre sugiere y más de lo que su ablación
indicaría.

**Menos**, porque la atribución no decide: `A1` lo midió y las diecisiete decisiones fueron las
mismas. Si el objetivo fuera solo decidir bien, podría retirarse.

**Más**, porque es lo que convierte una predicción en algo **contrastable**. Sin observaciones no hay
nada que anclar en el manual, y PI.2 —que toda afirmación se ancle en una observación o un fragmento
identificable— dejaría de tener objeto. La atribución no mejora la decisión; hace posible la
explicación.

Y deja un hallazgo que sobrevive a todo lo anterior: **la firma de un fallo no está necesariamente en
la señal del componente que falla.** El caudalímetro contaminado se detecta en los ajustes de
combustible. Un sistema diseñado con la intuición contraria —vigilar cada sensor para detectar su
propio fallo— no habría encontrado esta avería."""),

    md("""\
## 13. Conclusiones

**Qué aprendimos.** Que el modelo decide sobre las señales que la física aproximada del fallo
predice; que la deriva del caudalímetro se detecta en los ajustes de combustible y no en el caudal;
y que la atribución, en este recorrido, explica sin decidir.

**Qué hipótesis recibió apoyo.** Que las señales de mayor atribución coinciden con las declaradas, en
las cinco condiciones de fallo.

**Qué no recibió apoyo.** Nada se refuta, pero `A1` acota el valor de la atribución: no cambia
ninguna decisión.

**Qué permanece sin demostrar.** Que estas atribuciones se parezcan a las que daría telemetría real.
Que sean estables frente a otra semilla. Y que el reparto entre señales correlacionadas tenga algún
significado.

**Cómo contribuye al TFM.** Sostiene el capítulo de explicabilidad y es la pieza que une el
diagnóstico con la evidencia documental: sin observaciones no hay nada que verificar.

## 14. Reproducibilidad

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
| **Artefactos que produce** | dos figuras en `notebooks/salida/04_explicabilidad/`, PNG y SVG |

**Qué no se reproduce aquí.** Las atribuciones: recalcularlas exige reentrenar el bosque y volver a
ejecutar el explicador por permutación, que es lo caro del proceso. En modo FULL,
`mecanico-exp xai --dataset-id synthetic_v2 --etiqueta <nombre>`, que escribe con etiqueta propia y
**no sobrescribe** los artefactos publicados.

## 15. Referencias y trazabilidad

- `docs/experiments/E9_atribucion.md` — informe de la fase
- `experiments/E9_xai_synthetic_v2.json` — registro, con el fondo y su huella
- `artifacts/tables/E9_atribuciones_synthetic_v2.csv` — las 180 atribuciones
- `artifacts/tables/E9_resumen_synthetic_v2.csv` — la comparación con las señales declaradas
- `src/mecanico_ia_exp/xai/attribution.py` — el explicador y la selección de fondo
- `src/mecanico_ia_exp/obd/faults.py` — las fichas con `affected_signals`
- `docs/experiments/E18_ablaciones.md` y `E18_ablaciones_prueba.md` — la ablación `A1`
- `docs/experiments/E4_eda_temporal.md` — donde apareció por primera vez lo del caudalímetro"""),
]

if __name__ == "__main__":
    escribir("04_explicabilidad.ipynb", CELDAS)
