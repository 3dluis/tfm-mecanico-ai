"""Construye `03_analisis_e19.ipynb`: análisis de la evaluación final sobre prueba."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# E19: evaluación final sobre el conjunto de prueba

**Notebook** `03_analisis_e19` · **versión** 1.1 · **fecha** 14 de noviembre de 2026

| | |
|---|---|
| **Experimento** | E19, evaluación final |
| **Conjunto** | `synthetic_v2`, **partición de prueba**; el conjunto se abrió cinco veces (apartado 14.2); E19 es su única evaluación primaria |
| **Modalidad** | reanálisis |
| **Protocolo** | política de suficiencia v2.2, umbrales congelados antes de abrir el test |
| **Estado** | **Completado con limitaciones documentadas** |
| **Preguntas de investigación** | PI.1, PI.2 y sobre todo **PI.3**: el reconocimiento de insuficiencia |
| **Evidencia original** | `experiments/E19_evaluacion_final_v3.json`, `E19_anotacion_v3.json`, `artifacts/tables/E19_evaluacion_final_v3.csv` |

---

## En un minuto

- **Pregunta.** Si el criterio de suficiencia evita la falsa confianza (PI.3) sobre una partición
  que no se usó para fijarlo y cuánto cuesta esa protección en capacidad de dar respuesta.
- **Qué se hace.** Se recalculan las tasas de E19 desde la tabla congelada y se comprueban contra
  el registro.
- **Resultado.** Falsa confianza **0 de 14**, abstención innecesaria **2 de 8**, respuesta con
  evidencia completa **6 de 10**. El criterio iguala la falsa confianza de la política trivial más
  conservadora (apartado 13) y aun así responde en seis de diez casos.
- **Límite.** Con 0 de 14, el intervalo de Wilson al 95 % llega al **21,5 %** y el real es más
  ancho, porque las catorce ejecuciones proceden de siete ventanas de siete sesiones. Lo medido es
  que **en esta muestra no ocurrió**.

## Cómo leer este notebook

**Modalidad:** reanálisis. No reejecuta E19 ni puede hacerlo, porque la regla congelada dice que
un resultado desfavorable no es motivo para repetir; ninguna celda escribe en `experiments/`, toca
la anotación sellada ni recalcula una métrica histórica con otra configuración. **Ejecución:** CPU,
sin red, en segundos.

- **1–4** Introducción, objetivo e hipótesis, fundamento (criterio y estratos) y entorno.
- **5–6** Artefactos congelados y qué datos entran; resultado primario, con intervalos.
- **7–9** Decisiones caso a caso, las dos abstenciones innecesarias y las 35 ejecuciones frente al
  umbral.
- **10–13** Diagnósticos incorrectos, estratos descriptivos, la coincidencia con validación y las
  políticas triviales.
- **14–18** Resultados negativos y limitaciones, discusión, conclusiones, reproducibilidad y
  referencias."""),
    md("""\
## 1. Introducción: qué se jugaba en esta medición

Durante todo el trabajo, las cifras salieron de la partición de **validación**. Eso tiene un límite
conocido: los umbrales, el conjunto anotado y las reglas se habían visto contra esos mismos datos,
aunque fuera indirectamente. Una medición sobre una partición que no se usó para fijar el criterio
es otra cosa.

Lo que no sabíamos antes de abrir:

1. **Si el criterio de suficiencia evita la falsa confianza fuera de validación.** Es la pregunta de
   PI.3 y la que vertebra el trabajo.
2. **Cuánto cuesta esa protección** en capacidad de dar respuesta.
3. **Si el recorrido completo funciona de extremo a extremo** sobre datos nuevos: diagnóstico,
   atribución, recuperación, verificación y redacción.

El procedimiento fue deliberadamente rígido porque con un conjunto de prueba se puede medir una
vez. Si se mide, se ajusta y se vuelve a medir, deja de ser un conjunto de prueba y pasa a ser un
segundo conjunto de validación, sin que nada en los números lo delate."""),
    md("""\
## 2. Objetivo, hipótesis y lo que se congeló antes

**Objetivo.** Medir, sobre una partición que no se usó para fijar el criterio, con qué frecuencia el sistema explica cuando
debería abstenerse y con qué frecuencia se abstiene cuando debería explicar.

**Hipótesis evaluada (PI.3).** El criterio de suficiencia evita que el sistema produzca hipótesis
diagnósticas con confianza alta cuando la evidencia no las sostiene.

**Las dos tasas, definidas antes de mirar nada:**

- **Falsa confianza (`T_FC`).** Numerador: ejecuciones que **explican** debiendo abstenerse.
  Denominador: ejecuciones cuya decisión esperada es abstenerse.
- **Abstención innecesaria (`T_AI`).** Numerador: ejecuciones que **se abstienen** debiendo
  explicar. Denominador: ejecuciones cuya decisión esperada es explicar.

**No se suman ni se promedian.** Miden cosas distintas sobre denominadores distintos; una tasa
combinada escondería cuál de las dos se está pagando.

**La decisión esperada se fijó sin circularidad.** Se determina con **tres entradas**: la etiqueta verdadera, la clase predicha por el bosque
**sin calibrar** y la variante de corpus del caso. **La salida del verificador no interviene.** Si la
decisión esperada se derivase del mismo criterio de suficiencia que después se evalúa, el
experimento mediría su propia consistencia y no su acierto.

**Lo que quedó congelado antes de abrir:** las reglas de anotación, el conjunto de casos elegibles,
la regla de selección de ventanas, los umbrales, la política canónica, las versiones exactas de
modelo, corpus, índice y redactor, las condiciones de invalidez técnica y el compromiso de que un
resultado desfavorable no justifica repetir. Está en
`docs/methodology/congelacion-anotacion-e19.md`, anclado en `configs/congelacion-e19.anchor.json`."""),
    md("""\
## 3. Fundamento: qué es suficiencia de evidencia aquí

El sistema no decide si explicar mirando solo su confianza. Aplica un **criterio compuesto** con
cuatro condiciones y basta que una falle para que se abstenga.

| Condición | Umbral congelado | Qué protege |
|---|---|---|
| Confianza calibrada del diagnóstico | ≥ 0,79 | que el modelo esté razonablemente seguro |
| Cobertura de afirmaciones | ≥ 0,80 | que lo que se afirma esté anclado en evidencia |
| Fragmentos documentales aplicables | ≥ 2 | que la evidencia no dependa de un solo párrafo |
| Fuentes distintas | ≥ 1 | que haya un documento identificable detrás |

**Por qué compuesto y no un umbral único.** Un umbral único sobre la confianza deja pasar el caso
más peligroso: un modelo seguro de un diagnóstico que el manual no documenta. La ablación `A4` de
E18 (decidir solo con la confianza) lo midió: con umbral único, la falsa confianza sube a 9 de 9.

**Qué es la cobertura de afirmaciones.** El redactor produce un informe con afirmaciones
individuales; cada una se contrasta contra los fragmentos recuperados. La cobertura de afirmaciones es la
fracción de afirmaciones ancladas. Mide PI.2 y entra en el criterio de PI.3.

**Los tres estratos de E19,** fijados antes de medir:

- **operativo:** el resultado **primario**. Ventanas elegidas sin consultar al modelo: la primera
  ventana etiquetada con la condición de cada sesión. 22 ejecuciones.
- **comparativo:** **descriptivo**. Ventanas que el modelo clasifica bien. 11 ejecuciones.
- **adverso:** **descriptivo**. El error más confiado del conjunto. 2 ejecuciones.

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

**Qué datos entran.** Todas las figuras y cifras salen de un único registro: la evaluación final de
E19 en su **tercer intento**, el que llegó al final; los dos anteriores se interrumpieron y están
declarados. El sufijo `_v3` del fichero es el número de intento y **no** una versión del conjunto de
datos. Son 35 ejecuciones sobre la partición de **prueba** de `synthetic_v2`, repartidas en tres
estratos y procedentes de once ventanas de diez sesiones (la sesión de calentamiento 11 del termostato
bloqueado aporta dos ventanas). **No son 35 observaciones independientes:** repiten casos
entre estratos y las sesiones de un mismo caso salen del mismo generador y la misma
parametrización.

Antes de leer una cifra se comprueba que se está leyendo lo que se cree. La anotación se
selló **antes de cualquier medición** y lleva su propia huella."""),
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
**Qué muestra.** La cabecera del registro y la anotación sellada con su huella. La cabecera imprime
`dirty True`: el árbol de trabajo tenía cambios sin commit al ejecutar y el registro no dice cuáles.
Las reglas estaban ancladas en `configs/congelacion-e19.anchor.json` y las diez comprobaciones de
`freeze_verification` del registro dan `PASS`, entre ellas que ningún commit posterior a la
congelación toca lo congelado.

**Qué podemos interpretar.** Los denominadores de las dos tasas estaban fijados antes de ejecutar un
solo caso. Eso es lo que da sentido a las cifras: un denominador elegido después de ver los
resultados puede producir cualquier tasa.

**Qué no podemos afirmar.** Que el reparto concreto 8/14 estuviera **pre-registrado**. No lo estaba;
se trata en el apartado 12. Lo que estaba fijado es la **regla** que lo produce; el reparto que esa
regla produjo depende de cuántos casos el modelo diagnostica bien, que es un hecho medido."""),
    md("""\
## 6. Resultado primario

**Qué queremos investigar.** Las dos tasas sobre el estrato operativo, con sus denominadores.
**Qué datos utilizamos.** La tabla congelada, filtrada al estrato primario. Las tasas se
recalculan desde la tabla de casos y se comprueban contra el registro: si no coincidieran, habría
un error de agregación en alguna parte."""),
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

fig, ejes = plt.subplots(1, 3, figsize=(5.9, 3.0))
COLORES = [CATEGORICAL[2], CATEGORICAL[1], CATEGORICAL[0]]
# Qué tasa es cada panel: la letra sola no lo decía.
TITULOS = [
    "falsa confianza\\nexplicó debiendo abstenerse",
    "abstención innecesaria\\nse abstuvo debiendo explicar",
    "cobertura\\nexplicó con evidencia completa",
]

for letra, (eje, (nombre, fila), color, titulo) in zip(
    "abc", zip(ejes, primario.iterrows(), COLORES, TITULOS, strict=False), strict=False
):
    numerador, denominador = int(fila.numerador), int(fila.denominador)
    eje.bar(["casos"], [denominador], color="#e1e0d9", width=0.5, label="denominador")
    eje.bar(["casos"], [numerador], color=color, width=0.5, label="numerador")
    eje.text(0, denominador + 0.35, f"{numerador}/{denominador}",
             ha="center", fontsize=13, fontweight="bold", color=color)
    eje.set_title(f"({letra}) {titulo}", fontsize=7.5, fontweight="bold", loc="left", pad=6)
    eje.set_ylim(0, denominador * 1.42)
    eje.set_ylabel("ejecuciones (recuento)" if nombre.startswith("falsa") else "")
    eje.set_xticks([])
    eje.text(
        0, -denominador * 0.16,
        f"{int(fila['ventanas independientes'])} ventanas · {int(fila.sesiones)} sesiones",
        ha="center", fontsize=6.8, color="#52514e",
    )

fig.tight_layout()
fig.suptitle(
    "E19 sobre prueba: las tres tasas del criterio primario",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.01,
    "E19 · synthetic_v2, prueba · barra gris: ejecuciones evaluadas (denominador); "
    "barra de color: las que cumplen la tasa (numerador)",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB03-01_primario", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Falsa confianza **0 de 14**, procedentes de siete ventanas de siete sesiones.
Abstención innecesaria **2 de 8**. Respuesta con evidencia completa **6 de 10**.

**Qué podemos interpretar.** De las catorce ejecuciones en que el sistema debía abstenerse, doce lo
debían por construcción: la condición retiraba la evidencia (seis) o la dejaba parcial (seis); en dos
de ellas el diagnóstico era además erróneo. Las otras dos tenían la evidencia completa y un
diagnóstico erróneo. Se abstuvo en las catorce. Es lo que PI.3 pedía, sobre una partición que no se
usó para fijar el criterio.

**Qué no podemos afirmar.** Que el riesgo de falsa
confianza sea cero. La celda siguiente calcula el intervalo en lugar de describirlo: con 0 de 14, el
intervalo de Wilson al 95 % llega al **21,5 %** y el real es más ancho, porque las catorce
ejecuciones proceden de siete ventanas de siete sesiones. Lo medido es que **en
esta muestra no ocurrió**, no que no pueda ocurrir. Por eso el experimento consta como
completado con limitaciones documentadas y no como validado, que no se usa como sinónimo de
hipótesis demostrada.

Tampoco se puede leer la respuesta con evidencia completa 6/10 como “cuatro oportunidades perdidas”. De esas diez
ejecuciones con evidencia completa, **dos llevaban diagnóstico incorrecto**: en ellas, abstenerse
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
**Qué muestra.** Los tres intervalos. Son anchos. El de la falsa confianza de 0/14 va de **0 a
0,215**; el de la abstención innecesaria de 2/8, entre
**0,071 y 0,591**; el de la respuesta con evidencia completa de 6/10, entre **0,313 y 0,832**.

**Qué podemos interpretar.** Que el experimento acota poco. Decir “el intervalo de la falsa
confianza llega al 21,5 %” es una afirmación más fuerte que no decir nada, porque
delimita lo que no se ha demostrado. Y la amplitud del intervalo de la abstención
innecesaria (0,519, casi 52 puntos porcentuales) explica por qué el informe de la fase se niega a
llamarla estimación.

**Qué no podemos afirmar.** Que el intervalo sea exacto. Supone observaciones independientes; las
catorce proceden de siete ventanas de siete sesiones (apartado 5), de modo que el intervalo real es **más ancho** que
el que sale aquí. Tampoco cubre
la incertidumbre de que el conjunto sea sintético, que no es estadística."""),
    md("""\
## 7. Qué decidió el sistema, caso a caso

**Qué queremos investigar.** No las tasas, sino el detalle: qué decidió en cada ejecución y por qué.
**Qué datos utilizamos.** Las 22 ejecuciones del estrato operativo, con su caso anotado, su
condición de evidencia y la decisión que el sistema tomó. Los dos puntos de una misma fila son
**sesiones distintas** del mismo caso y no repeticiones de la misma medición."""),
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
# Más ancho que la página: con 5,9 pulgadas la leyenda dejaba al eje tan estrecho
# que los rótulos de las tres columnas se montaban.
fig, eje = plt.subplots(figsize=(7.8, 5.0))

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
    "FULL\\ncompleta", "PARTIAL\\nparcial", "ABSENT\\nretirada",
], fontsize=7.5)
eje.set_xlim(-0.6, 2.6)
eje.set_xlabel("condición de evidencia del caso anotado")
eje.grid(axis="x", linestyle=":", linewidth=0.6)

from matplotlib.lines import Line2D

eje.legend(handles=[
    Line2D([], [], marker="o", color="w", markerfacecolor=CATEGORICAL[0],
           markersize=9, label="explicó y debía (correcto)"),
    Line2D([], [], marker="s", color="w", markerfacecolor=CATEGORICAL[0],
           markersize=9, label="se abstuvo y debía (correcto)"),
    Line2D([], [], marker="D", color="w", markerfacecolor=CATEGORICAL[1],
           markersize=9, label="se abstuvo y debía explicar (abstención innecesaria)"),
    Line2D([], [], marker="X", color="w", markerfacecolor=CATEGORICAL[1],
           markersize=10, label="explicó y debía abstenerse (falsa confianza): no ocurre"),
], fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5))

fig.tight_layout()
fig.suptitle(
    "E19 sobre prueba: la decisión de cada ejecución del estrato operativo, caso a caso",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.01,
    "Cada fila es un caso anotado con dos sesiones; cada marca se desplaza a un lado según su "
    "sesión y dos marcas pueden superponerse (C01, C02, C04, C10 y C11). "
    "Azul: decisión correcta; naranja: error.",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB03-02_decisiones", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Veintidós puntos: once casos anotados por dos sesiones. Ningún aspa (ninguna falsa
confianza). Dos rombos: las dos abstenciones innecesarias, las dos en la columna de evidencia
completa.

**Qué podemos interpretar.** La estructura del resultado es la que el diseño buscaba: el sistema se
abstiene en las columnas de evidencia parcial y retirada sin excepción; en la de evidencia
completa explica en la mayoría de los casos. Los dos fallos son del tipo “conservador de más”, no
del tipo “confiado de más”.

**Qué no podemos afirmar.** Que el comportamiento sea estable. Cada fila tiene **dos** puntos y una
sola ejecución distinta cambiaría la fila entera. Las dos sesiones de una fila no son
independientes (apartado 5)."""),
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
eje.text(0.31, UMBRAL_COBERTURA + 0.015, f"umbral de cobertura {UMBRAL_COBERTURA}",
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
], fontsize=7.5, loc="center left")

fig.suptitle(
    "Las ocho ejecuciones que debían explicar, frente a los dos umbrales",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E19 · synthetic_v2, prueba · política v2.2, umbrales congelados antes de abrir el test · "
    "zona más oscura: donde se cumplen los dos umbrales; bandas claras: solo uno · "
    "el criterio exige además ≥2 fragmentos aplicables y ≥1 fuente",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB03-03_abstenciones", subdirectorio="03_analisis_e19")
plt.show()"""),
    md("""\
**Qué muestra.** Las ocho ejecuciones que debían explicar, situadas por confianza y cobertura. Las
seis que explicaron caen en la zona donde se cumplen los dos umbrales. Las dos que se abstuvieron
caen fuera **por motivos distintos**: una por confianza insuficiente con la evidencia documental
completa; otra por las dos cosas a la vez.

**Qué podemos interpretar.** Las dos abstenciones innecesarias no son fallos del criterio de
suficiencia: el criterio hizo lo que dice hacer. Son consecuencia de que **el modelo de
diagnóstico no estaba suficientemente seguro** en esas dos ventanas. Mejorar esta cifra pasa por el
diagnóstico, no por relajar el umbral. Relajarlo, además, subiría la falsa confianza, que es el error que
se quiere evitar.

**Qué no podemos afirmar.** Que 2 de 8 sea una estimación de la tasa real (apartado 14.2, punto 4).
Tampoco que estos dos casos sean intrínsecamente difíciles: son dos ventanas concretas. Las dos
corresponden a casos que también fallaron en el ensayo sobre validación, lo que se discute en el
apartado 12."""),
    md("""\
## 9. Las 35 ejecuciones frente al umbral

**Qué queremos investigar.** Dónde queda cada una de las 35 ejecuciones registradas (no solo las
22 del estrato operativo) respecto del umbral de confianza de 0,79. Esa distancia distingue un
acierto holgado de uno que estuvo cerca de no serlo. Cada ejecución lleva marcado si la decisión fue
correcta, si el diagnóstico del modelo lo era, cuánta cobertura de afirmaciones alcanzó y cuántos
documentos aplicables recibió.

**Qué datos utilizamos.** Los del apartado 5 (`artifacts/tables/E19_evaluacion_final_v3.csv`)."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import decisiones_de_e19

# El nombre `registro` ya está tomado en este notebook por el JSON de E19: esta
# tabla es otra cosa y lleva otro nombre.
ejecuciones = decisiones_de_e19()
bajo_umbral = ejecuciones[ejecuciones.confidence < 0.79]
print(f"ejecuciones registradas: {len(ejecuciones)}")
print(f"por debajo del umbral de 0,79: {len(bajo_umbral)}")
print(f"de ellas, abstenciones innecesarias: {int(bajo_umbral.abstencion_innecesaria.sum())}")
print()
print(ejecuciones.groupby(["stratum", "expected_decision", "decision"]).size().to_string())"""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_decisiones_y_umbral

fig_decisiones_y_umbral()"""),
    md("""\
**Qué muestra.** Cuatro de las 35 ejecuciones quedan por debajo del umbral y son las cuatro de
las dos abstenciones innecesarias: la deriva del caudalímetro a
0,573 y el fallo de encendido a 0,491, cada una repetida en dos ejecuciones. Ninguna decisión
correcta queda por debajo del umbral y ninguna abstención indebida por encima. Las seis ejecuciones
con el diagnóstico del modelo incorrecto, cuatro del estrato operativo y las dos del adverso,
terminan en abstención correcta.

**Qué podemos interpretar.** Confirma lo visto en el apartado 8: la puerta de confianza no está
mal situada y el modelo estaba poco seguro en esas dos ventanas. El otro lado del mismo mecanismo también se ve: donde el diagnóstico era
incorrecto pero la confianza alta, lo que evitó la explicación equivocada fue el criterio de
suficiencia documental y no la confianza.

Hay además un detalle descriptivo. El caso de la deriva aparece sobre dos sesiones: en autopista
da 0,573 y se abstiene cuando debía explicar; en calentamiento da 0,851 y explica bien. Las dos
abstenciones innecesarias están las dos en sesiones de autopista, donde están también las dos
confianzas más bajas; en ralentí y calentamiento ninguna baja de 0,85.

**Qué no podemos afirmar.** Que la conducción en autopista cause una reducción de la
confianza. Es una **observación descriptiva sobre dos errores**; con `n = 2` no hay contraste
posible y la coincidencia podría deberse al caso, a la ventana o al azar. Las 35 ejecuciones no son
independientes (apartado 5). Y el umbral
**no se revisa** a la vista de esta figura: la política está congelada desde antes de abrir el
conjunto de prueba; moverla ahora sería ajustar el criterio a los datos reservados.

**Relación con la pregunta de investigación.** El límite del sistema para PI.3 está en la confianza
del modelo de diagnóstico sobre las dos condiciones de señal más pobre, no en el criterio. En la memoria es la
**Figura 5.21**."""),
    md("""\
## 10. Los diagnósticos incorrectos, que no se descartan

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
evidencia documental completa (que son las que reducen el denominador de la abstención innecesaria a
ocho) y dos más en casos de evidencia parcial o retirada, donde el sistema debía abstenerse de todos
modos.

**Qué podemos interpretar.** El sistema **se abstuvo en todas ellas**. Es el caso que más importa,
porque explicar con confianza un diagnóstico equivocado sería el peor resultado posible y es lo que
el criterio existe para impedir. Que en las dos ejecuciones con evidencia
completa en que el modelo se equivocó el sistema callara es evidencia directa a favor de PI.3.

**Qué no podemos afirmar.** Que el sistema detecte los diagnósticos incorrectos. No los detecta: no
tiene forma de saber que son incorrectos. Y no fue la puerta de confianza la que los paró: la
confianza **calibrada**, que es la que compara el verificador, era de 0,908 y 0,966, por encima del
umbral de 0,79 (la columna `model_confidence` de la tabla es la probabilidad sin calibrar). El motivo
registrado en los dos es `LOW_CLAIM_COVERAGE` (cobertura de afirmaciones insuficiente): los fragmentos recuperados para el diagnóstico
equivocado no sostenían ninguna afirmación. Un diagnóstico incorrecto con confianza alta **y**
evidencia documental que sí cubriera lo afirmado no sería filtrado por este mecanismo. Ese escenario
es el que el estrato adverso intentó provocar."""),
    md("""\
## 11. Los dos análisis descriptivos, separados del primario

Como se fijó en el apartado 3, el estrato comparativo y el adverso **no responden a la pregunta de
investigación**: sus ventanas se eligieron **consultando al modelo**, de modo que están sesgadas por
construcción. Se informan porque forman parte de lo medido."""),
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

**Qué no podemos afirmar.** Nada sobre tasas poblacionales a partir de ellos: elegir ventanas
mirando las predicciones es lo que el estrato operativo evita. Mezclarlos con el
primario produciría una cifra sin significado. Y el adverso tiene **dos**
ejecuciones: describe dos casos, no una tendencia."""),
    md("""\
## 12. Una coincidencia que hubo que auditar

Las seis tasas de los estratos operativo y comparativo salieron **idénticas** a las del ensayo
previo sobre validación. Una coincidencia así obliga a comprobar que no hay un error de agregación
ni una reutilización accidental de resultados.

La auditoría se hizo sobre los artefactos existentes, **sin reejecutar nada** y está en el informe
de la fase. Su resultado, resumido: los artefactos son distintos (particiones, commits y marcas de
tiempo separadas por diez días) y **ninguna ventana se repite entre los dos ensayos**."""),
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
**Lo que la auditoría concluyó.** Hay que separar lo fijado de lo observado.

**Fijado por el diseño, en cualquier partición.** Las **22 ejecuciones** (once condiciones de
evidencia elegibles por dos sesiones) y, dentro de ellas, las **diez con evidencia completa**. Estas
dos cifras no podían ser otras y no aportan coincidencia alguna.

**Fijado por la regla de selección.** Los denominadores del estrato comparativo, 5 y 6: esa regla
elige ventanas que el modelo clasifica bien, así que el reparto es el único posible.

**Función algebraica.** La cobertura 6/10, que se deriva de las otras dos y no aporta información
independiente.

**No fijado: observado.** Los denominadores **8 y 14**. Ninguno sale del diseño: ambos se derivan de
un mismo hecho medido, que de las diez ejecuciones con evidencia completa el modelo diagnostica mal
dos. El reparto 8/14 **no estaba pre-registrado** (así consta en las limitaciones) y
habría sido 9/13 o 7/15 con un error menos o uno más.

Y lo que de verdad coincide: en **las dos** particiones el modelo falla dos de las diez
ventanas; en las dos falla **en las mismas dos condiciones** (termostato en calentamiento y
encendido en autopista), aunque en sesiones distintas. Las dos abstenciones innecesarias son también
los mismos dos casos anotados (`C01` y `C04`) **por las mismas causas** en las dos particiones:
`C01` por confianza insuficiente y `C04` por confianza baja y cobertura nula a la vez (en validación,
confianza 0,462; en prueba, 0,490).

**Qué no se puede afirmar de esa coincidencia.** Que el sistema se comporte igual en prueba que en
validación. Con `n = 2` en ambos recuentos, la repetición es compatible con que el modelo falle
sistemáticamente en esas dos condiciones y también con el azar; los artefactos no permiten
distinguirlo y no se afirma lo primero."""),
    md("""\
## 13. La comparación con políticas triviales

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

# La política de solo confianza no se recalcula: se lee tal como E19 la registró.
def fraccion(tasa: dict) -> str:
    return f"{tasa['numerator']}/{tasa['denominator']}"

solo_confianza = registro["strata"]["operativo"]["reference_policies"][
    "explain_if_model_is_confident"
]
politicas.loc[f"explicar si confianza ≥ {solo_confianza['min_confidence']} (registro)"] = [
    fraccion(solo_confianza["false_confidence"]),
    fraccion(solo_confianza["unnecessary_abstention"]),
    fraccion(solo_confianza["coverage_full_evidence"]),
]
politicas"""),
    md("""\
**Qué muestra.** Cuatro políticas sobre los mismos denominadores. La última la calculó y la registró
E19: explicar siempre que la confianza calibrada alcance el umbral, sin mirar la evidencia.

**Qué podemos interpretar.** El criterio evaluado obtiene la falsa confianza de la política más
conservadora (cero) reteniendo seis de las diez respuestas que la política conservadora perdería
todas. Esa es la aportación. Abstenerse siempre también evita la falsa confianza; lo propio del criterio
es evitarla **sin renunciar a responder**. La política de solo confianza retiene más respuestas,
ocho de diez, pero explica en las catorce ejecuciones en que debía callar. El cero lo da la
evidencia y no la confianza.

**Qué no podemos afirmar.** Que el criterio domine a las triviales en cualquier conjunto. Con estos
denominadores, la comparación describe esta muestra. Y no se define aquí ningún criterio numérico de
“cuántas respuestas justifican cuánta protección”: eso exigiría un modelo de coste que este trabajo no
tiene."""),
    md("""\
## 14. Resultados negativos y limitaciones

### 14.1 Resultados negativos

1. **Dos abstenciones innecesarias de ocho.** El coste evitable de la protección, con un denominador
   que no permite estimarlo con precisión.
2. **Dos diagnósticos incorrectos de diez** entre las ejecuciones con evidencia completa.
3. **Nueve de las treinta y cinco salidas del redactor contienen una cifra que el verificador no
   produjo** (`L-26`, la limitación declarada de cifras del texto sin verificar): cinco de las 26 abstenciones y cuatro de las 9 explicaciones, con 8 de sus 27
   afirmaciones afectadas (seis distintas sobre tres ventanas). Una primera auditoría dio siete
   porque agrupaba los números de cada caso; el guion distribuido `scripts/auditar_cifras_redactadas.py`
   agrupa por caso y reproduce el siete. Esa agrupación esconde dos abstenciones en las que el
   umbral mal citado coincide con el de otro motivo del mismo caso
   (`docs/audits/fidelidad-numerica-e19-01-11-2026.md`). El peor caso está en
   `operativo/C07_partial`, donde el redactor escribió “cobertura 0.852 < 0.90” y el verificador había
   escrito “cobertura 0.00 < 0.80”: inventó el valor **y** el umbral. La comparación resultante es
   aritméticamente cierta, así que nada en la frase delata el error. **Ninguna de las dos tasas cambia
   por ello**, porque las produce el verificador determinista; lo que cambia es que el texto de la
   evaluación final no es numéricamente fiel. Las tres barreras lo dejan pasar.

### 14.2 Limitaciones

4. **Los denominadores son pequeños**: 14, 8 y 10. Un solo caso mueve `T_AI` en 0,125.
5. **El reparto 8/14 no estaba pre-registrado.** La regla sí; el reparto que produjo, no.
6. **La condición con distractor quedó fuera** de los casos elegibles, porque no medía lo que decía
   medir: dos de las tres tenían la misma configuración que la condición parcial. **Se rediseñó y se
   ejecutó aparte el 13 de octubre de 2026** (P1, el rediseño de la condición con distractor, con tres
   situaciones construidas y seis ejecuciones): seis abstenciones de seis, las seis por insuficiencia de
   la evidencia y ninguna por confianza baja. Esa medición **no forma parte de E19**:
   `docs/experiments/P1_distractor_v2.md`.
7. **El conjunto de prueba se abrió cinco veces**, no tres. Las tres de E19 (contando los dos intentos
   interrumpidos), una comprobación pre-registrada de las ablaciones el 13 de octubre y una **apertura
   accidental** que solo leyó identificadores de sesión. Las cinco están registradas en
   `docs/methodology/registro-aperturas-test.md`, clasificadas en **cinco niveles**: apertura técnica,
   lectura de identificadores, exposición de etiquetas, exposición de predicciones y utilización de
   resultados. En cuatro de las cinco hubo exposición de etiquetas y de predicciones. **No se afirma
   que el conjunto permanezca intacto.**
8. **El adaptador del redactor se ajustó sobre ventanas de validación** (limitación declarada `L-23`). E19 mide sobre
   prueba y su solape con los ejemplos de ajuste es **cero ventanas y cero sesiones**, de modo que sus
   cifras de redacción no están contaminadas por esa vía. Lo que sigue siendo cierto es que el
   adaptador no se ha reentrenado. El reentrenamiento está **detenido por memoria insuficiente**:
   necesita más de 17 GB por paso (`docs/experiments/incidencia-p2-02.md`).
9. **Reejecutar esta evaluación exige lo que no se distribuye**, que no es el conjunto. E19 mide sobre
   `synthetic_v2`, partición de prueba. Ese conjunto **se reconstruye bit a bit**: las cuatro
   huellas se comprobaron desde un clon limpio contra las que el manifiesto congeló antes de abrirlo.
   Lo que no se distribuye son el corpus del manual, el índice documental y los pesos del adaptador;
   sin ellos, un tercero no puede repetir la medición. Aparte queda `synthetic_v3`, que **no** es
   reconstruible (limitación declarada `L-25`) y del que no sale ninguna cifra de esta evaluación: de él salen la
   comparación de volumen de E7 y el conjunto de evaluación independiente del redactor, sin ejecutar.
   Corregido el 13-10-2026: este punto decía que `synthetic_v3` era “el conjunto de esta evaluación”.
10. **Todo es sintético.** La validez externa no está establecida.
11. **Una sola ejecución.** No hay repeticiones: los intervalos de Wilson del apartado 6 describen la
   incertidumbre de esa única medición, no la variabilidad entre ejecuciones.
12. **Las consultas no son ciegas** (`query_text_not_blind` en el registro): se reutilizan
   literalmente del conjunto anotado y las escribió una persona que conocía el fallo
   (`docs/methodology/congelacion-anotacion-e19.md`, sección 2)."""),
    md("""\
## 15. Discusión

Lo que E19 aporta a la pregunta de investigación es una respuesta acotada y verificable a PI.3: el
criterio de suficiencia, sobre una partición que no se usó para fijar el criterio, no produjo ninguna explicación cuando
debía callar (apartados 6 y 13).

Sobre **cómo** se obtuvo hay dos cosas que importan tanto como la cifra.

**La primera es que las reglas se congelaron antes** de abrir el conjunto (apartado 2). La decisión
esperada de cada caso se fijó con tres entradas que **no incluyen la salida del verificador**.

**La segunda es que la medición se interrumpió dos veces.** Los dos primeros intentos murieron tras
sellar la anotación, por una causa ambiental que no llegó a demostrarse. La regla congelada obligaba
a conservar el registro de cada intento inválido con su motivo y a que la repetición llevara
identificador propio en lugar de sustituir al anterior. Tres reinicios automáticos fueron rechazados
por el ejecutor con una excepción escrita para eso. El incidente está documentado.

**Y una cosa que este experimento no resuelve.** No haber observado falsa confianza en catorce
ejecuciones no es haber establecido que sea improbable. Con catorce observaciones solo se puede
afirmar lo primero."""),
    md("""\
## 16. Conclusiones del experimento

**Qué aprendimos.** Que el recorrido completo se ejecutó de extremo a extremo sobre una partición que
no se usó para fijar el criterio (35 salidas con esquema válido y sin citas inventadas, nueve de
ellas con alguna cifra ajena, `L-26`) y que su criterio de suficiencia obtuvo la falsa confianza de la política más
conservadora sin renunciar a responder en seis de diez casos.

**Qué hipótesis recibió apoyo.** La de PI.3, en los términos medidos y con el denominador declarado.

**Qué no recibió apoyo.** Nada se refuta aquí; lo que queda acotado es el alcance de lo afirmable.

**Qué permanece sin demostrar.** Que la tasa de falsa confianza sea baja en población. Que el
sistema rechace evidencia no pertinente en general (PI.4): el rediseño de la condición con
distractor (P1, 13-10-2026, fuera de E19) da una respuesta acotada a tres situaciones construidas y seis
ejecuciones, sin estimar ninguna tasa.
La validez externa de todo ello.

**Cómo contribuye al TFM.** Es la única evaluación primaria sobre el conjunto de prueba y el cierre del
capítulo de resultados. Su valor no está en la cifra sino en el procedimiento: unas reglas
congeladas y verificables, una apertura declarada y una conclusión que no va más allá de lo que
catorce observaciones permiten."""),
    md("""\
## 17. Reproducibilidad

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
`tests/test_notebooks.py`. **E19 no se reejecuta**: exigiría lo que no se distribuye (apartado 14.2,
punto 9), una base PostgreSQL con pgvector y una nueva apertura del conjunto de prueba, que la regla
congelada no autoriza.

## 18. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** Este notebook sostiene el apartado *La evaluación final sobre el conjunto de prueba* del capítulo 5, con la **Figura 5.19** (las tres cifras con sus denominadores) y la **Figura 5.20** (la decisión de cada una de las 22 ejecuciones). Lo que la evaluación cambia en los objetivos está en el capítulo 6, en OE3, OE5 y el objetivo general.

- `docs/experiments/E19_evaluacion_final.md`: informe completo de la fase
- `docs/methodology/congelacion-anotacion-e19.md`: las reglas, congeladas antes de abrir
- `configs/congelacion-e19.anchor.json`: el anclaje al commit de congelación
- `configs/manifest_e19.json`: el estado congelado: modelos, corpus, umbrales, casos
- `docs/methodology/declaracion-apertura-e19.md`: la declaración formal de apertura
- `docs/methodology/registro-aperturas-test.md`: las cinco aperturas del conjunto de prueba
- `docs/experiments/incidencia-e19-01.md`: los dos intentos interrumpidos
- `experiments/E19_evaluacion_final_v3.json`, `E19_anotacion_v3.json`
- `artifacts/tables/E19_evaluacion_final_v3.csv`
- `docs/experiments/E18_ablaciones.md`: qué aporta cada componente del criterio"""),
]

if __name__ == "__main__":
    escribir("03_analisis_e19.ipynb", CELDAS)
