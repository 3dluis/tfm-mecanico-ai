"""Construye `03_analisis_e19.ipynb`: análisis de la evaluación final sobre prueba."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# E19 — Evaluación final sobre el conjunto de prueba

**Notebook** `03_analisis_e19` · **versión** 1.0 · **fecha** 12 de octubre de 2026

| | |
|---|---|
| **Experimento** | E19, evaluación final |
| **Conjunto** | `synthetic_v2`, **partición de prueba**, abierta una sola vez el 12-10-2026 |
| **Protocolo** | política de suficiencia v2.2, umbrales congelados antes de abrir el test |
| **Estado** | **COMPLETED — WITH DOCUMENTED LIMITATIONS** |
| **Preguntas de investigación** | PI.1, PI.2 y sobre todo **PI.3** — el reconocimiento de insuficiencia |
| **Evidencia original** | `experiments/E19_evaluacion_final_v3.json`, `E19_anotacion_v3.json`, `artifacts/tables/E19_evaluacion_final_v3.csv` |

---

> **Este notebook no reejecuta E19 y no puede hacerlo.** Lee los artefactos congelados. El conjunto
> de prueba se abrió una sola vez, con las reglas fijadas y ancladas a un commit **antes** de
> abrirlo, y la regla congelada dice que un resultado desfavorable no es motivo para repetir. Todo
> lo que sigue es **reanálisis sobre artefactos congelados**: ninguna celda escribe en
> `experiments/`, ninguna toca la anotación sellada y ninguna recalcula una métrica histórica con
> otra configuración."""),
    md("""\
## 1. Introducción: qué se jugaba en esta medición

Durante todo el trabajo, las cifras salieron de la partición de **validación**. Eso tiene un límite
conocido: los umbrales, el conjunto anotado y las reglas se habían visto contra esos mismos datos,
aunque fuera indirectamente. Una medición sobre datos que el diseño nunca tocó es otra cosa.

Lo que no sabíamos antes de abrir:

1. **Si el criterio de suficiencia evita la falsa confianza fuera de validación.** Es la pregunta de
   PI.3 y la que vertebra el trabajo.
2. **Cuánto cuesta esa protección** en capacidad de dar respuesta.
3. **Si el recorrido completo funciona de extremo a extremo** sobre datos nuevos: diagnóstico,
   atribución, recuperación, verificación y redacción.

El procedimiento fue deliberadamente rígido, y conviene saber por qué: con un conjunto de prueba se
puede medir una vez. Si se mide, se ajusta y se vuelve a medir, deja de ser un conjunto de prueba y
pasa a ser un segundo conjunto de validación, sin que nada en los números lo delate."""),
    md("""\
## 2. Objetivo, hipótesis y lo que se congeló antes

**Objetivo.** Medir, sobre datos que el diseño no vio, con qué frecuencia el sistema explica cuando
debería abstenerse y con qué frecuencia se abstiene cuando debería explicar.

**Hipótesis evaluada (PI.3).** El criterio de suficiencia evita que el sistema produzca hipótesis
diagnósticas con confianza alta cuando la evidencia no las sostiene.

**Las dos tasas, definidas antes de mirar nada:**

- **Falsa confianza (`T_FC`)** — numerador: ejecuciones que **explican** debiendo abstenerse.
  Denominador: ejecuciones cuya decisión esperada es abstenerse.
- **Abstención innecesaria (`T_AI`)** — numerador: ejecuciones que **se abstienen** debiendo
  explicar. Denominador: ejecuciones cuya decisión esperada es explicar.

**No se suman ni se promedian.** Miden cosas distintas sobre denominadores distintos, y una tasa
combinada escondería cuál de las dos se está pagando.

**La decisión esperada se fijó sin circularidad**, que es el punto más delicado del diseño. Se
determina con **exactamente tres entradas**: la etiqueta verdadera, la clase predicha por el bosque
**sin calibrar** y la variante de corpus del caso. **La salida del verificador no interviene.** Si la
decisión esperada se derivase del mismo criterio de suficiencia que después se evalúa, el
experimento mediría su propia consistencia y no su acierto.

**Lo que quedó congelado antes de abrir:** las reglas de anotación, el conjunto de casos elegibles,
la regla de selección de ventanas, los umbrales, la política canónica, las versiones exactas de
modelo, corpus, índice y redactor, las condiciones de invalidez técnica y el compromiso de que un
resultado desfavorable no justifica repetir. Está en
`docs/methodology/congelacion-anotacion-e19.md`, anclado en `configs/congelacion-e19.anchor.json`."""),
    md("""\
## 3. Fundamento: qué es «suficiencia de evidencia» aquí

El sistema no decide si explicar mirando solo su confianza. Aplica un **criterio compuesto** con
cuatro condiciones, y basta que una falle para que se abstenga:

| Condición | Umbral congelado | Qué protege |
|---|---|---|
| Confianza calibrada del diagnóstico | ≥ 0,79 | que el modelo esté razonablemente seguro |
| Cobertura de afirmaciones | ≥ 0,80 | que lo que se afirma esté anclado en evidencia |
| Fragmentos documentales aplicables | ≥ 2 | que la evidencia no dependa de un solo párrafo |
| Fuentes distintas | ≥ 1 | que haya un documento identificable detrás |

**Por qué compuesto y no un umbral único.** Un umbral único sobre la confianza deja pasar el caso
más peligroso: un modelo seguro de un diagnóstico que el manual no documenta. La ablación `A4` de
E18 lo midió: con umbral único, la falsa confianza sube a 9 de 9.

**Qué es la cobertura de afirmaciones.** El redactor produce un informe con afirmaciones
individuales; cada una se contrasta contra los fragmentos recuperados. La cobertura es la fracción
de afirmaciones ancladas. Mide PI.2 y entra en el criterio de PI.3.

**Los tres estratos de E19,** fijados antes de medir:

- **operativo** — el resultado **primario**. Ventanas elegidas sin consultar al modelo: la primera
  ventana etiquetada con la condición de cada sesión. 22 ejecuciones.
- **comparativo** — **descriptivo**. Ventanas que el modelo clasifica bien. 11 ejecuciones.
- **adverso** — **descriptivo**. El error más confiado del conjunto. 2 ejecuciones.

Los dos últimos **no responden a la pregunta de investigación** y no se mezclan con el primero."""),
    md("""\
## 4. Preparación del entorno"""),
    code(PREAMBULO),
    code("""\
soporte.declarar_modalidad(
    "REANÁLISIS",
    "los recuentos se recalculan a partir de la tabla congelada E19_evaluacion_final_v3.csv "
    "y se comprueban contra el registro JSON; no se reejecuta E19, no se abre ninguna "
    "partición y no se escribe en experiments/",
)"""),
    md("""\
## 5. Los artefactos congelados

Antes de leer una cifra, comprobar que se está leyendo lo que se cree. La anotación se selló **antes
de cualquier medición** y lleva su propia huella."""),
    code("""\
import json
from pathlib import Path

import pandas as pd

registro = soporte.registro("E19_evaluacion_final_v3")
casos = soporte.tabla("E19_evaluacion_final_v3")

cabecera = {k: v for k, v in registro.items() if not isinstance(v, (dict, list))}
for clave, valor in cabecera.items():
    print(f"{clave:24s} {valor}")
print()
print(f"filas en la tabla congelada: {len(casos)}")
print(f"estratos: {sorted(casos.stratum.unique())}")"""),
    code("""\
# La anotación sellada: se escribió y se le tomó huella ANTES de ejecutar
# ningún caso. Es lo que impide que los denominadores se hayan elegido viendo
# los resultados.
anotacion = json.loads(
    (soporte.raiz() / "experiments" / "E19_anotacion_v3.json").read_text("utf-8")
)
print("Anotación sellada · claves de primer nivel:")
for clave in anotacion:
    print(f"  {clave}")

import hashlib

contenido = (soporte.raiz() / "experiments" / "E19_anotacion_v3.json").read_bytes()
print()
print(f"huella de la anotación (sha256:16): {hashlib.sha256(contenido).hexdigest()[:16]}")"""),
    md("""\
**Qué muestra.** La cabecera del registro y la anotación sellada con su huella.

**Qué podemos interpretar.** Los denominadores de las dos tasas estaban fijados antes de ejecutar un
solo caso. Eso es lo que da sentido a las cifras: un denominador elegido después de ver los
resultados puede producir cualquier tasa.

**Qué no podemos afirmar.** Que el reparto concreto 8/14 estuviera **pre-registrado**. No lo estaba,
y se trata en el apartado 11. Lo que estaba fijado es la **regla** que lo produce; el reparto que esa
regla produjo depende de cuántos casos el modelo diagnostica bien, que es un hecho medido."""),
    md("""\
## 6. Resultado primario

**Qué queremos investigar.** Las dos tasas sobre el estrato operativo, con sus denominadores.
**Qué datos utilizamos.** La tabla congelada, filtrada al estrato primario.
**Por qué se calculan aquí en lugar de leerse del registro.** Porque recalcularlos desde la tabla de
casos y comprobar que coinciden con el registro es una verificación: si no coincidieran, habría un
error de agregación en alguna parte."""),
    code("""\
operativo = casos[casos.stratum == "operativo"]

deben_abstenerse = operativo[operativo.expected_decision == "ABSTAIN"]
deben_explicar = operativo[operativo.expected_decision == "EXPLAIN"]

falsa_confianza = deben_abstenerse[deben_abstenerse.decision == "EXPLAIN"]
abstencion_innecesaria = deben_explicar[deben_explicar.decision == "ABSTAIN"]

con_evidencia = operativo[operativo.corpus_variant == "FULL"]
explicadas = con_evidencia[con_evidencia.decision == "EXPLAIN"]

primario = pd.DataFrame(
    [
        {
            "tasa": "falsa confianza (T_FC)",
            "numerador": len(falsa_confianza),
            "denominador": len(deben_abstenerse),
            "valor": len(falsa_confianza) / len(deben_abstenerse),
            "ventanas independientes": deben_abstenerse.window_id.nunique(),
            "sesiones": deben_abstenerse.session_id.nunique(),
        },
        {
            "tasa": "abstención innecesaria (T_AI)",
            "numerador": len(abstencion_innecesaria),
            "denominador": len(deben_explicar),
            "valor": len(abstencion_innecesaria) / len(deben_explicar),
            "ventanas independientes": deben_explicar.window_id.nunique(),
            "sesiones": deben_explicar.session_id.nunique(),
        },
        {
            "tasa": "cobertura con evidencia completa",
            "numerador": len(explicadas),
            "denominador": len(con_evidencia),
            "valor": len(explicadas) / len(con_evidencia),
            "ventanas independientes": con_evidencia.window_id.nunique(),
            "sesiones": con_evidencia.session_id.nunique(),
        },
    ]
).set_index("tasa")
primario.round(4)"""),
    code("""\
import matplotlib.pyplot as plt
import numpy as np

from mecanico_ia_exp.visualization.style import CATEGORICAL, apply_style

apply_style()

fig, ejes = plt.subplots(1, 3, figsize=(9.8, 3.6))
COLORES = [CATEGORICAL[2], CATEGORICAL[1], CATEGORICAL[0]]

for eje, (nombre, fila), color in zip(ejes, primario.iterrows(), COLORES, strict=False):
    numerador, denominador = int(fila.numerador), int(fila.denominador)
    eje.bar(["casos"], [denominador], color="#e1e0d9", width=0.5, label="denominador")
    eje.bar(["casos"], [numerador], color=color, width=0.5, label="numerador")
    eje.text(0, denominador + 0.35, f"{numerador}/{denominador}",
             ha="center", fontsize=13, fontweight="bold", color=color)
    eje.set_title(nombre, fontsize=8.5)
    eje.set_ylim(0, denominador * 1.42)
    eje.set_ylabel("ejecuciones (recuento)" if nombre.startswith("falsa") else "")
    eje.set_xticks([])
    eje.text(
        0, -denominador * 0.16,
        f"{int(fila['ventanas independientes'])} ventanas · {int(fila.sesiones)} sesiones",
        ha="center", fontsize=6.8, color="#52514e",
    )

fig.suptitle(
    "E19, estrato operativo: las tres cifras con su numerador y su denominador",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "synthetic_v2, partición de PRUEBA · política de suficiencia v2.2 · "
    "fuente: artifacts/tables/E19_evaluacion_final_v3.csv · "
    "0/14 NO significa riesgo cero: ver la interpretación",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB03-01_primario", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Falsa confianza **0 de 14**, procedentes de 7 sesiones. Abstención innecesaria
**2 de 8**. Cobertura con evidencia completa **6 de 10**.

**Qué podemos interpretar.** En las catorce ejecuciones en que el sistema debía abstenerse —porque
el diagnóstico era incorrecto, porque la evidencia estaba retirada o porque era parcial— se abstuvo
en todas. Es lo que PI.3 pedía, sobre datos que el diseño no vio.

**Qué no podemos afirmar, y es lo más importante de este notebook.** Que el riesgo de falsa
confianza sea cero. La celda siguiente calcula el intervalo en lugar de describirlo: con 0 de 14, la
evidencia disponible es compatible con una tasa real de **hasta el 21,5 %**. Lo medido es que **en
esta muestra no ocurrió**, no que no pueda ocurrir. El experimento está
marcado `COMPLETED — WITH DOCUMENTED LIMITATIONS` por esto, y `VALIDATED` no se usa como sinónimo
de hipótesis demostrada.

Tampoco se puede leer la cobertura 6/10 como «cuatro oportunidades perdidas». De esas diez
ejecuciones con evidencia completa, **dos llevaban diagnóstico incorrecto**, y en ellas abstenerse
era lo que debía hacer. La parte evitable del coste es la otra cifra: **2 de 8**."""),
    code('''\
# El intervalo se calcula, no se describe. Con numeradores de 0 y denominadores
# de 14, el intervalo de Wald da [0, 0] --un artefacto conocido-- de modo que se
# usa el de **Wilson**, que no colapsa en los extremos.
from math import sqrt


def wilson(exitos: int, total: int, z: float = 1.959963985) -> tuple[float, float]:
    """Intervalo de Wilson al 95 % para una proporción."""
    p = exitos / total
    centro = (p + z * z / (2 * total)) / (1 + z * z / total)
    radio = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return max(0.0, centro - radio), min(1.0, centro + radio)


intervalos = []
for nombre, fila in primario.iterrows():
    bajo, alto = wilson(int(fila.numerador), int(fila.denominador))
    intervalos.append({
        "tasa": nombre,
        "medido": f"{int(fila.numerador)}/{int(fila.denominador)}",
        "valor": round(float(fila.valor), 4),
        "IC 95 % (Wilson)": f"[{bajo:.3f}, {alto:.3f}]",
        "amplitud": round(alto - bajo, 3),
    })
pd.DataFrame(intervalos).set_index("tasa")'''),
    md("""\
**Qué muestra.** Los tres intervalos, y son anchos. La falsa confianza de 0/14 es compatible con
cualquier tasa real entre **0 y 0,215**; la abstención innecesaria de 2/8, con cualquiera entre
**0,071 y 0,591**; la cobertura de 6/10, entre **0,313 y 0,832**.

**Qué podemos interpretar.** Que el experimento acota poco. Decir «hasta un 21,5 % de falsa
confianza es compatible con lo medido» es una afirmación más fuerte que no decir nada, porque
delimita exactamente lo que no se ha demostrado. Y la amplitud del intervalo de la abstención
innecesaria —más de medio punto— explica por qué el informe de la fase se niega a llamarla
«estimación».

**Qué no podemos afirmar.** Que el intervalo sea exacto. Supone observaciones independientes, y las
catorce proceden de siete sesiones del mismo generador: dos ejecuciones de la misma sesión no son
independientes, de modo que el intervalo real es **más ancho** que el que sale aquí. Tampoco cubre
la incertidumbre de que el conjunto sea sintético, que no es estadística."""),
    md("""\
## 7. Qué decidió el sistema, caso a caso

**Qué queremos investigar.** No las tasas, sino el detalle: qué decidió en cada ejecución y por qué.
**Por qué un mapa de decisiones.** Veintidós ejecuciones caben en una cuadrícula, y así se ve de un
vistazo dónde están los aciertos, los errores y la estructura por condición de evidencia."""),
    code("""\
vista = operativo[[
    "case_id_gold", "fault_id", "corpus_variant", "predicted_class",
    "prediction_correct", "expected_decision", "decision", "correct",
    "confidence", "claim_coverage", "n_documents_applicable", "reasons",
]].copy()
vista["sesión"] = operativo.session_id.str.rsplit("__", n=1).str[-1]
vista = vista.sort_values(["corpus_variant", "case_id_gold"])
vista.reset_index(drop=True)"""),
    code("""\
ORDEN_VARIANTE = ["FULL", "PARTIAL", "ABSENT"]
fig, eje = plt.subplots(figsize=(9.8, 5.4))

marcadores = {("EXPLAIN", True): "o", ("ABSTAIN", True): "s",
              ("EXPLAIN", False): "X", ("ABSTAIN", False): "D"}
colores = {True: CATEGORICAL[0], False: CATEGORICAL[1]}

casos_ordenados = sorted(operativo.case_id_gold.unique())
posicion_y = {c: i for i, c in enumerate(casos_ordenados)}

for _, fila in operativo.iterrows():
    x = ORDEN_VARIANTE.index(fila.corpus_variant) + (
        0.16 if fila.session_id.endswith(tuple("13579")) else -0.16
    )
    eje.scatter(
        x, posicion_y[fila.case_id_gold],
        marker=marcadores[(fila.decision, bool(fila.correct))],
        s=140, color=colores[bool(fila.correct)],
        edgecolor="white", linewidth=0.7, zorder=3,
    )

eje.set_yticks(range(len(casos_ordenados)), casos_ordenados, fontsize=7.5)
eje.set_xticks(range(len(ORDEN_VARIANTE)), [
    "FULL\\nevidencia completa", "PARTIAL\\nevidencia parcial", "ABSENT\\nevidencia retirada",
], fontsize=8)
eje.set_xlim(-0.6, 2.6)
eje.set_xlabel("condición de evidencia del caso anotado")
eje.grid(axis="x", linestyle=":", linewidth=0.6)

from matplotlib.lines import Line2D

eje.legend(handles=[
    Line2D([], [], marker="o", color="w", markerfacecolor=CATEGORICAL[0],
           markersize=9, label="explicó, y debía (correcto)"),
    Line2D([], [], marker="s", color="w", markerfacecolor=CATEGORICAL[0],
           markersize=9, label="se abstuvo, y debía (correcto)"),
    Line2D([], [], marker="D", color="w", markerfacecolor=CATEGORICAL[1],
           markersize=9, label="se abstuvo, y debía explicar (abstención innecesaria)"),
    Line2D([], [], marker="X", color="w", markerfacecolor=CATEGORICAL[1],
           markersize=10, label="explicó, y debía abstenerse (falsa confianza) — no ocurre"),
], fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5))

fig.suptitle(
    "Las 22 ejecuciones del estrato operativo: dos sesiones por caso anotado",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E19 · synthetic_v2, partición de prueba · "
    "fuente: artifacts/tables/E19_evaluacion_final_v3.csv · "
    "cada punto es una ejecución; los dos puntos de una fila son sesiones distintas",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB03-02_decisiones", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Veintidós puntos: once casos anotados por dos sesiones. Ningún aspa —ninguna falsa
confianza—. Dos rombos: las dos abstenciones innecesarias, las dos en la columna de evidencia
completa.

**Qué podemos interpretar.** La estructura del resultado es la que el diseño buscaba: el sistema se
abstiene en las columnas de evidencia parcial y retirada sin excepción, y en la de evidencia
completa explica en la mayoría de los casos. Los dos fallos son del tipo «conservador de más», no
del tipo «confiado de menos».

**Qué no podemos afirmar.** Que el comportamiento sea estable. Cada fila tiene **dos** puntos; una
sola ejecución distinta cambiaría la fila entera. Y las dos sesiones de una fila no son
independientes en sentido estadístico: salen del mismo generador y la misma parametrización."""),
    md("""\
## 8. Las dos abstenciones innecesarias, en detalle

El cero de falsa confianza es el titular, pero lo que enseña está en los dos fallos."""),
    code("""\
detalle = abstencion_innecesaria[[
    "case_id_gold", "session_id", "predicted_class", "confidence",
    "model_confidence", "claim_coverage", "n_documents_applicable",
    "n_distinct_sources", "reasons",
]]
detalle.reset_index(drop=True)"""),
    code("""\
UMBRAL_CONFIANZA = 0.79
UMBRAL_COBERTURA = 0.80

fig, eje = plt.subplots(figsize=(6.6, 4.8))

eje.axvspan(UMBRAL_CONFIANZA, 1.04, ymin=0, ymax=1, color=CATEGORICAL[0], alpha=0.07)
eje.axhspan(UMBRAL_COBERTURA, 1.08, xmin=0, xmax=1, color=CATEGORICAL[0], alpha=0.07)
eje.axvline(UMBRAL_CONFIANZA, color="#898781", linestyle="--", linewidth=1.0)
eje.axhline(UMBRAL_COBERTURA, color="#898781", linestyle="--", linewidth=1.0)
eje.text(UMBRAL_CONFIANZA + 0.01, 0.02, f"umbral de confianza {UMBRAL_CONFIANZA}",
         fontsize=6.8, color="#52514e", rotation=90)
eje.text(0.02, UMBRAL_COBERTURA + 0.015, f"umbral de cobertura {UMBRAL_COBERTURA}",
         fontsize=6.8, color="#52514e")

for _, fila in deben_explicar.iterrows():
    fallo = fila.decision == "ABSTAIN"
    eje.scatter(fila.confidence, fila.claim_coverage,
                s=130 if fallo else 70,
                color=CATEGORICAL[1] if fallo else CATEGORICAL[0],
                marker="D" if fallo else "o",
                edgecolor="white", linewidth=0.7, zorder=3)
    if fallo:
        eje.annotate(fila.case_id_gold, (fila.confidence, fila.claim_coverage),
                     textcoords="offset points", xytext=(9, 7),
                     fontsize=7, color=CATEGORICAL[1], fontweight="bold")

eje.set_xlabel("confianza calibrada del diagnóstico (probabilidad, 0–1)")
eje.set_ylabel("cobertura de afirmaciones (fracción anclada, 0–1)")
eje.set_xlim(0.3, 1.04)
eje.set_ylim(-0.04, 1.08)
eje.legend(handles=[
    Line2D([], [], marker="o", color="w", markerfacecolor=CATEGORICAL[0],
           markersize=8, label="explicó (correcto)"),
    Line2D([], [], marker="D", color="w", markerfacecolor=CATEGORICAL[1],
           markersize=9, label="se abstuvo debiendo explicar"),
], fontsize=7.5, loc="lower left")

fig.suptitle(
    "Las ocho ejecuciones que debían explicar, frente a los dos umbrales",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E19 · synthetic_v2, prueba · política v2.2, umbrales congelados antes de abrir el test · "
    "zona sombreada: donde se cumplen los dos umbrales · "
    "el criterio exige además ≥2 fragmentos aplicables y ≥1 fuente",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB03-03_abstenciones", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Las ocho ejecuciones que debían explicar, situadas por confianza y cobertura. Las
seis que explicaron caen en la zona donde se cumplen los dos umbrales. Las dos que se abstuvieron
caen fuera, y **por motivos distintos**: una por confianza insuficiente con la evidencia documental
completa; otra por las dos cosas a la vez.

**Qué podemos interpretar.** Las dos abstenciones innecesarias no son fallos del criterio de
suficiencia: el criterio hizo exactamente lo que dice hacer. Son consecuencia de que **el modelo de
diagnóstico no estaba suficientemente seguro** en esas dos ventanas. Mejorar esta cifra pasa por el
diagnóstico, no por relajar el umbral —y relajarlo subiría la falsa confianza, que es el error que
se quiere evitar—.

**Qué no podemos afirmar.** Que 2 de 8 sea una estimación de la tasa real. Un solo caso mueve la
cifra en 0,125. Tampoco que estos dos casos sean intrínsecamente difíciles: son dos ventanas
concretas, y las dos corresponden a casos que también fallaron en el ensayo sobre validación, lo que
se discute en el apartado 11."""),
    md("""\
## 9. Los diagnósticos incorrectos, que no se descartan

De las diez ejecuciones con evidencia documental completa, en **dos** el modelo diagnosticó mal. No
se descartan ni se esconden: se informan, porque son parte del resultado."""),
    code("""\
incorrectos = operativo[~operativo.prediction_correct.astype(bool)]
incorrectos_con_evidencia = incorrectos[incorrectos.corpus_variant == "FULL"]

print(f"ejecuciones del estrato operativo:            {len(operativo)}")
print(f"con diagnóstico incorrecto:                   {len(incorrectos)}")
print(f"  de ellas, con evidencia completa (FULL):    {len(incorrectos_con_evidencia)}")
print(f"  de ellas, con evidencia parcial o retirada: "
      f"{len(incorrectos) - len(incorrectos_con_evidencia)}")
print()
print(f"de las {len(con_evidencia)} ejecuciones con evidencia completa, "
      f"{len(incorrectos_con_evidencia)} llevan diagnóstico incorrecto")
print(f"en todas ellas el sistema se abstuvo: "
      f"{(incorrectos.decision == 'ABSTAIN').all()}")
print()
incorrectos[[
    "case_id_gold", "session_id", "label", "predicted_class",
    "model_confidence", "expected_decision", "decision", "correct", "reasons",
]].reset_index(drop=True)"""),
    md("""\
**Qué muestra.** Las ejecuciones en que la clase predicha no coincide con la verdadera, con su
confianza y lo que el sistema decidió. Son **cuatro de las veintidós**: dos entre las que tienen
evidencia documental completa —que son las que reducen el denominador de la abstención innecesaria a
ocho— y dos más en casos de evidencia parcial o retirada, donde el sistema debía abstenerse de todos
modos.

**Qué podemos interpretar.** El sistema **se abstuvo en todas ellas**. Es el caso que más importa:
un diagnóstico equivocado del que además se explicara con confianza sería el peor resultado posible,
y es exactamente lo que el criterio existe para impedir. Que en las dos ocasiones en que el modelo
se equivocó el sistema callara es evidencia directa a favor de PI.3.

**Qué no podemos afirmar.** Que el sistema detecte los diagnósticos incorrectos. No los detecta: no
tiene forma de saber que son incorrectos. Lo que ocurre es que en esos dos casos la **confianza** del
modelo era baja, y el umbral los filtró. Un diagnóstico incorrecto **con confianza alta** y evidencia
documental aparente no sería filtrado por este mecanismo, y ese escenario es justamente el que el
estrato adverso intentó provocar."""),
    md("""\
## 10. Los dos análisis descriptivos, separados del primario

El estrato comparativo y el adverso **no responden a la pregunta de investigación** y no deben
mezclarse con el resultado primario: sus ventanas se eligieron **consultando al modelo**, de modo
que están sesgadas por construcción. Se informan porque forman parte de lo medido."""),
    code("""\
descriptivos = []
for estrato in ["comparativo", "adverso"]:
    sub = casos[casos.stratum == estrato]
    if sub.empty:
        continue
    abst = sub[sub.expected_decision == "ABSTAIN"]
    expl = sub[sub.expected_decision == "EXPLAIN"]
    descriptivos.append({
        "estrato": estrato,
        "ejecuciones": len(sub),
        "ventanas": sub.window_id.nunique(),
        "falsa confianza": f"{len(abst[abst.decision == 'EXPLAIN'])}/{len(abst)}",
        "abstención innecesaria": f"{len(expl[expl.decision == 'ABSTAIN'])}/{len(expl)}",
        "cómo se eligieron las ventanas": (
            "las que el modelo clasifica bien" if estrato == "comparativo"
            else "el error más confiado del conjunto"
        ),
    })
pd.DataFrame(descriptivos).set_index("estrato")"""),
    md("""\
**Qué muestra.** Los recuentos de los dos estratos descriptivos y, al lado, cómo se eligieron sus
ventanas.

**Qué podemos interpretar.** El estrato comparativo describe el comportamiento en condiciones
favorables; el adverso, en la condición más desfavorable que el diseño supo construir: la ventana
que el modelo clasifica mal **con más confianza**.

**Qué no podemos afirmar.** Nada sobre tasas poblacionales a partir de ellos. Sus ventanas se
eligieron mirando las predicciones del modelo, lo que es exactamente lo que el estrato operativo
evita. Mezclarlos con el primario produciría una cifra sin significado. Y el adverso tiene **dos**
ejecuciones: describe dos casos, no una tendencia."""),
    md("""\
## 11. Una coincidencia que hubo que auditar

Las seis tasas de los estratos operativo y comparativo salieron **idénticas** a las del ensayo
previo sobre validación. Una coincidencia así obliga a comprobar que no hay un error de agregación
ni una reutilización accidental de resultados.

La auditoría se hizo sobre los artefactos existentes, **sin reejecutar nada**, y está en el informe
de la fase. Su resultado, resumido: los artefactos son distintos —particiones, commits y marcas de
tiempo separadas por diez días— y **ninguna ventana se repite entre los dos ensayos**."""),
    code("""\
# Comprobación directa de que no hay solape de ventanas entre los dos ensayos.
# Si lo hubiera, la coincidencia se explicaría por reutilización y las cifras no
# valdrían nada.
ensayo = Path(soporte.raiz() / "experiments" / "E19_evaluacion_final_validation.json")
if ensayo.is_file():
    previo = json.loads(ensayo.read_text("utf-8"))

    # El registro del ensayo no guarda `window_id` como campo propio: lo lleva
    # dentro del identificador de ejecución, con la forma
    # `estrato:caso@sesión@inicio`. Se extrae de ahí en lugar de suponer que el
    # campo existe, que es lo que haría que la comprobación saliera vacía y
    # pareciera que no hay solape cuando lo que no hay es dato.
    def ventanas_de(documento: dict, estrato: str) -> set[str]:
        return {
            str(c["run_id"]).split(":", 1)[1].split("@", 1)[1]
            for c in documento["strata"][estrato]["cases"]
        }

    for estrato in ("operativo", "comparativo"):
        previas = ventanas_de(previo, estrato)
        actuales = {
            str(r).split(":", 1)[1].split("@", 1)[1]
            for r in casos.loc[casos.stratum == estrato, "run_id"]
        }
        print(f"{estrato}:")
        print(f"  ventanas sobre validación: {len(previas)}")
        print(f"  ventanas sobre prueba:     {len(actuales)}")
        print(f"  SOLAPE:                    {len(previas & actuales)}")

    print()
    print(f"commit del ensayo sobre validación: {previo['commit'][:7]}")
    print(f"commit de la medición sobre prueba: {registro['commit'][:7]}")
    print(f"fecha del ensayo:  {previo['executed_at'][:10]}")
    print(f"fecha de la medición: {registro['executed_at'][:10]}")
else:
    print("el registro del ensayo sobre validación no está en este clon")"""),
    md("""\
**Lo que la auditoría concluyó, y conviene no simplificar.** Hay que separar tres cosas:

**Fijado por el diseño, en cualquier partición.** Las **22 ejecuciones** —once condiciones de
evidencia elegibles por dos sesiones— y, dentro de ellas, las **diez con evidencia completa**. Estas
dos cifras no podían ser otras y no aportan coincidencia alguna.

**Fijado por la regla de selección.** Los denominadores del estrato comparativo, 5 y 6: esa regla
elige ventanas que el modelo clasifica bien, así que el reparto es el único posible.

**Función algebraica.** La cobertura 6/10, que se deriva de las otras dos y no aporta información
independiente.

**No fijado — observado.** Los denominadores **8 y 14**. Ninguno sale del diseño: ambos se derivan de
un mismo hecho medido, que de las diez ejecuciones con evidencia completa el modelo diagnostica mal
exactamente dos. El reparto 8/14 **no estaba pre-registrado** —así consta en las limitaciones— y
habría sido 9/13 o 7/15 con un error menos o uno más.

Y lo que de verdad coincide: en **las dos** particiones el modelo falla exactamente dos de las diez
ventanas, y en las dos falla **en las mismas dos condiciones** —termostato en calentamiento y
encendido en autopista—, aunque en sesiones distintas. Las dos abstenciones innecesarias son también
los mismos dos casos anotados, `C01` y `C04`, pero **no por la misma causa**: en validación `C04` se
abstuvo con confianza alta por cobertura insuficiente, y en prueba por las dos cosas a la vez.

**Qué no se puede afirmar de esa coincidencia.** Que el sistema se comporte igual en prueba que en
validación. Con `n = 2` en ambos recuentos, la repetición es compatible con que el modelo falle
sistemáticamente en esas dos condiciones y también con el azar; los artefactos no permiten
distinguirlo y no se afirma lo primero."""),
    md("""\
## 12. La comparación con políticas triviales

Una cifra de falsa confianza de 0/14 no dice nada por sí sola si una política trivial la obtiene
igual. Abstenerse **siempre** da 0 de falsa confianza y 8 de 8 de abstención innecesaria."""),
    code("""\
politicas = pd.DataFrame([
    {
        "política": "criterio compuesto (la evaluada)",
        "falsa confianza": f"{len(falsa_confianza)}/{len(deben_abstenerse)}",
        "abstención innecesaria": f"{len(abstencion_innecesaria)}/{len(deben_explicar)}",
        "cobertura": f"{len(explicadas)}/{len(con_evidencia)}",
    },
    {
        "política": "abstenerse siempre",
        "falsa confianza": f"0/{len(deben_abstenerse)}",
        "abstención innecesaria": f"{len(deben_explicar)}/{len(deben_explicar)}",
        "cobertura": f"0/{len(con_evidencia)}",
    },
    {
        "política": "explicar siempre",
        "falsa confianza": f"{len(deben_abstenerse)}/{len(deben_abstenerse)}",
        "abstención innecesaria": f"0/{len(deben_explicar)}",
        "cobertura": f"{len(con_evidencia)}/{len(con_evidencia)}",
    },
]).set_index("política")
politicas"""),
    md("""\
**Qué muestra.** Las tres políticas sobre los mismos denominadores.

**Qué podemos interpretar.** El criterio evaluado obtiene la falsa confianza de la política más
conservadora —cero— reteniendo seis de las diez respuestas que la política conservadora perdería
todas. Esa es la aportación: no es que evite la falsa confianza, que abstenerse siempre también lo
hace; es que la evita **sin renunciar a responder**.

**Qué no podemos afirmar.** Que el criterio domine a las triviales en cualquier conjunto. Con estos
denominadores, la comparación describe esta muestra. Y no se define aquí ningún criterio numérico de
«cuánta cobertura justifica cuánta protección»: eso exigiría un modelo de coste que este trabajo no
tiene."""),
    md("""\
## 13. Resultados negativos y limitaciones

1. **Dos abstenciones innecesarias de ocho.** El coste evitable de la protección, con un denominador
   que no permite estimarlo con precisión.
2. **Dos diagnósticos incorrectos de diez** entre las ejecuciones con evidencia completa.
3. **Los denominadores son pequeños**: 14, 8 y 10. Un solo caso mueve `T_AI` en 0,125.
4. **El reparto 8/14 no estaba pre-registrado.** La regla sí; el reparto que produjo, no.
5. **La condición con distractor quedó fuera** de los casos elegibles, porque no medía lo que decía
   medir: dos de las tres tenían la misma configuración que la condición parcial. **Se rediseñó y se
   ejecutó aparte el 13 de octubre de 2026** —seis abstenciones de seis, las seis por insuficiencia de
   la evidencia y ninguna por confianza baja—, y esa medición **no forma parte de E19**:
   `docs/experiments/P1_distractor_v2.md`.
6. **El conjunto de prueba se abrió cinco veces**, no tres. Las tres de E19 —contando los dos intentos
   interrumpidos—, una comprobación pre-registrada de las ablaciones el 13 de octubre y una **apertura
   accidental** que solo leyó identificadores de sesión. Las cinco están registradas en
   `docs/methodology/registro-aperturas-test.md`, clasificadas en **cinco niveles**: apertura técnica,
   lectura de identificadores, exposición de etiquetas, exposición de predicciones y utilización de
   resultados. En cuatro de las cinco hubo exposición de etiquetas y de predicciones. **No se afirma
   que el conjunto permanezca intacto.**
7. **Siete de las treinta y cinco salidas del redactor contienen una cifra que el verificador no
   produjo** (`L-26`): 3 de 26 abstenciones y 8 de 27 afirmaciones. El peor caso está en
   `operativo/C07_partial`, donde el redactor escribió «cobertura 0.852 < 0.90» y el verificador había
   escrito «cobertura 0.00 < 0.80»: inventó el valor **y** el umbral, y la comparación resultante es
   aritméticamente cierta, así que nada en la frase delata el error. **Ninguna de las dos tasas cambia
   por ello**, porque las produce el verificador determinista; lo que cambia es que el texto de la
   evaluación final no es numéricamente fiel. Las tres barreras lo dejan pasar.
8. **El adaptador del redactor se ajustó sobre ventanas de validación** (`L-23`). E19 mide sobre
   prueba y su solape con los ejemplos de ajuste es **cero ventanas y cero sesiones**, de modo que sus
   cifras de redacción no están contaminadas por esa vía. Lo que sigue siendo cierto es que el
   adaptador no se ha reentrenado, y el reentrenamiento está **detenido por memoria insuficiente**:
   necesita más de 17 GB por paso (`docs/experiments/incidencia-p2-02.md`).
9. **`synthetic_v3`, el conjunto de esta evaluación, no es reconstruible** con el generador publicado
   (`L-25`): es pre-calibración y ninguna de sus 216 sesiones se reproduce. Las cifras de E19 son
   correctas y **no son reproducibles por un tercero** sin los ficheros procesados, que no se
   distribuyen por tamaño.
10. **Todo es sintético.** La validez externa no está establecida.
11. **Una sola ejecución.** No hay repeticiones ni intervalos de confianza."""),
    md("""\
## 14. Discusión

Lo que E19 aporta a la pregunta de investigación es una respuesta acotada y verificable a PI.3: el
criterio de suficiencia, sobre datos que el diseño no vio, no produjo ninguna explicación cuando
debía callar, y lo hizo reteniendo seis de las diez respuestas que una política conservadora habría
perdido.

Dos cosas conviene subrayar sobre **cómo** se obtuvo, porque importan tanto como la cifra.

**La primera es que las reglas se congelaron antes.** Las reglas de anotación, los umbrales, el
conjunto de casos, la regla de selección de ventanas y las condiciones de invalidez se escribieron,
se les tomó huella y se anclaron a un commit **antes** de abrir el conjunto. Y dentro de ellas, la
decisión esperada de cada caso se fijó con tres entradas que **no incluyen la salida del
verificador**. Sin esa precaución el experimento habría medido su propia consistencia.

**La segunda es que la medición se interrumpió dos veces.** Los dos primeros intentos murieron tras
sellar la anotación, por una causa ambiental que no llegó a demostrarse. La regla congelada obligaba
a conservar el registro de cada intento inválido con su motivo, y a que la repetición llevara
identificador propio en lugar de sustituir al anterior. Tres reinicios automáticos fueron rechazados
por el ejecutor con una excepción escrita para eso. El incidente está documentado.

**Y una cosa que este experimento no resuelve.** Que el sistema no produjera falsa confianza en
catorce ejecuciones no permite afirmar que no la produzca. Es la diferencia entre no haber observado
un suceso y haber establecido que es improbable, y con catorce observaciones solo se puede afirmar lo
primero."""),
    md("""\
## 15. Conclusiones del experimento

**Qué aprendimos.** Que el recorrido completo funciona de extremo a extremo sobre datos que el
diseño no vio, y que su criterio de suficiencia obtuvo la falsa confianza de la política más
conservadora sin renunciar a responder en seis de diez casos.

**Qué hipótesis recibió apoyo.** La de PI.3, en los términos medidos y con el denominador declarado.

**Qué no recibió apoyo.** Nada se refuta aquí; lo que queda acotado es el alcance de lo afirmable.

**Qué permanece sin demostrar.** Que la tasa de falsa confianza sea baja en población. Que el
sistema rechace evidencia no pertinente —PI.4—, mientras la condición con distractor no se rediseñe.
La validez externa de todo ello.

**Cómo contribuye al TFM.** Es la única medición sobre el conjunto de prueba y el cierre del
capítulo de resultados. Su valor no está en la cifra sino en el procedimiento: unas reglas
congeladas y verificables, una apertura declarada y una conclusión que no va más allá de lo que
catorce observaciones permiten."""),
    md("""\
## 16. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb` |
| **Datos** | ninguno: se leen artefactos congelados versionados |
| **Configuración** | política v2.2; umbrales 0,79 de confianza, 0,80 de cobertura, 2 fragmentos, 1 fuente |
| **Semilla** | 20260901 |
| **Commit** | el que imprime la celda del apartado 4 |
| **Tiempo** | menos de un minuto |
| **Memoria** | por debajo de 500 MB |
| **Recursos** | CPU |
| **Artefactos que produce** | tres figuras en `notebooks/salida/03_analisis_e19/`, PNG y SVG |

**Qué se puede reproducir y qué no.** Los recuentos de este notebook se recalculan desde la tabla
congelada y se pueden verificar contra el registro JSON; eso está automatizado en
`tests/test_notebooks.py`. **E19 no se reejecuta**: exigiría el corpus documental —que no se
redistribuye—, los pesos del adaptador LoRA, una base PostgreSQL con pgvector y una nueva apertura
del conjunto de prueba, que la regla congelada no autoriza por un resultado desfavorable ni por
curiosidad.

## 17. Referencias y trazabilidad

- `docs/experiments/E19_evaluacion_final.md` — informe completo de la fase
- `docs/methodology/congelacion-anotacion-e19.md` — las reglas, congeladas antes de abrir
- `configs/congelacion-e19.anchor.json` — el anclaje al commit de congelación
- `configs/manifest_e19.json` — el estado congelado: modelos, corpus, umbrales, casos
- `docs/methodology/declaracion-apertura-e19.md` — la declaración formal de apertura
- `docs/methodology/registro-aperturas-test.md` — las tres aperturas del conjunto de prueba
- `docs/experiments/incidencia-e19-01.md` — los dos intentos interrumpidos
- `experiments/E19_evaluacion_final_v3.json`, `E19_anotacion_v3.json`
- `artifacts/tables/E19_evaluacion_final_v3.csv`
- `docs/experiments/E18_ablaciones.md` — qué aporta cada componente del criterio"""),
]

if __name__ == "__main__":
    escribir("03_analisis_e19.ipynb", CELDAS)
