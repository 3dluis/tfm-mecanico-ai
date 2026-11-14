"""Construye `00_introduccion.ipynb`: el recorrido experimental para el jurado."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Introducción y recorrido experimental

**Notebook** `00_introduccion` · **versión** 1.1 · **fecha** 14 de noviembre de 2026

| | |
|---|---|
| **Experimentos que recorre** | E1 a E19 |
| **Conjunto** | `data/samples/synthetic_sample.parquet` (18 sesiones) y los registros de `experiments/` |
| **Protocolo** | ninguno propio: este notebook no mide nada |
| **Estado** | vigente |
| **Modalidad** | visualización de evidencia histórica |
| **Pregunta de investigación** | la principal y el mapa de cómo las cuatro subpreguntas la componen |
| **Evidencia original** | `docs/experiment-index.md`, `docs/matriz_validacion_pi.md`, `experiments/*.json` |

---

## En un minuto

- **Pregunta.** ¿Puede un agente con RAG explicar un diagnóstico a partir de datos OBD-II, rastrear
  cada explicación hasta su evidencia y reconocer cuándo no basta?
- **Qué se hace.** Quince experimentos sobre datos **sintéticos**, del diagnóstico a la decisión
  de explicar o abstenerse.
- **Resultado.** En la evaluación final (E19, conjunto de prueba): **falsa confianza 0 de 14**,
  abstención innecesaria 2 de 8 y respuesta con evidencia completa 6 de 10.
- **Lectura.** El modelo temporal no superó a la línea base; el valor del contexto temporal sigue
  abierto.
- **Límite.** Con 0 de 14, el intervalo de Wilson al 95 % llega al 21,5 % y el real es más ancho:
  las catorce ejecuciones salen de siete ventanas de siete sesiones. Tres de los cuatro criterios
  se reformularon conociendo parte de los resultados. La trazabilidad alcanza a los identificadores
  de la evidencia, no a las cifras del texto (limitación L-26: 9 de 35 salidas).

## Cómo leer este notebook

Es el punto de entrada. Modalidad: visualización de evidencia histórica, con una demostración
ilustrativa (el diagrama). CPU, sin red, menos de un minuto.

- **1–3** La pregunta y sus subpreguntas; qué se desconocía al empezar; preparación del entorno.
- **4–5** El recorrido en un diagrama; los datos, qué son y qué no son.
- **6–8** Qué se midió y qué significan las métricas; qué sostiene cada objetivo; la evaluación
  final, E19.
- **9–10** Resultados negativos y limitaciones; discusión de la formulación amplia de la pregunta.
- **11–14** Conclusiones; qué queda abierto (el contexto temporal); reproducibilidad; referencias.

**El resto del paquete:** `01_exploracion_obd` (datos y ventanas: E2, E4, E5) ·
`02_comparacion_modelos` (E6, E7) · `03_analisis_e19` (evaluación final) · `04_explicabilidad` (E9)
· `05_suficiencia_y_abstencion` (E15, E18, P1) · `06_expresion_del_fallo` (si el fallo etiquetado
se ve en la señal).

**Códigos que aparecen en los notebooks**

| Código | Qué designa |
|---|---|
| PI.1–PI.4 | las cuatro subpreguntas de la pregunta de investigación (apartado 1) |
| OE1–OE5 | los objetivos específicos de la memoria: estado del conocimiento, entorno experimental, diagnóstico y su confianza, agente que contrasta hipótesis con evidencia y comportamiento integrado bajo las condiciones de evidencia |
| E1–E19 | los experimentos del plan (`docs/experiment-index.md`); E19 es la evaluación final sobre el conjunto de prueba |
| A1–A4 | las ablaciones de E18: sin atribución (A1), sin recuperación semántica (A2), sin criterio de suficiencia (A3) y con la confianza calibrada como único criterio (A4) |
| P1 | el rediseño de la condición con distractor: tres situaciones construidas, seis ejecuciones |
| L-23 | limitación declarada: el adaptador del redactor se ajustó sobre ventanas de validación en las que después se le mide |
| L-25 | limitación declarada: `synthetic_v3` no se puede reconstruir |
| L-26 | limitación declarada: el texto redactado contiene cifras que el verificador no produjo |
| ADR-004 | la decisión de arquitectura que fija la formulación acotada de la pregunta |
| SUPERSEDED | marca de un informe o una explicación retirados y sustituidos |
| RERUN-A | la reejecución con pre-registro tras corregir el espacio de embeddings mezclado |"""),
    md("""\
## 1. La pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

Es la formulación **acotada**, fijada por la decisión de arquitectura `ADR-004` el 12 de septiembre de 2026; por qué no la más
amplia que circuló antes se explica en el apartado 10.

La pregunta tiene tres verbos y ninguno es decorativo: **explicar**, **rastrear** y **reconocer**.
Cada uno se evalúa por separado, porque un sistema puede acertar el diagnóstico y sostenerlo con
evidencia que no viene al caso, o anclarlo en un documento que no aplica a ese motor.

| Subpregunta | Qué evalúa | Experimentos |
|---|---|---|
| **PI.1** | que el diagnóstico a partir de OBD-II supere a la clase mayoritaria con margen amplio y que su confianza se pueda calibrar | E5, E6, E7, E19 |
| **PI.2** | que toda afirmación se ancle en una observación o un fragmento identificable | E14, E15, E19 |
| **PI.3** | que el sistema **reconozca cuándo no sabe**: al retirar la evidencia, pasa de explicar a abstenerse | E15, E16, E18, E19 |
| **PI.4** | que rechace evidencia no pertinente | E17, con **una condición invalidada** (apartado 9) y su rediseño P1 |

La tercera es la que vertebra el trabajo. Un sistema de diagnóstico que acierta el 90 % de las veces
y afirma con confianza en el 10 % restante es peor, en un taller, que uno que acierta el 70 % y
calla en el resto."""),
    md("""\
## 2. Qué desconocíamos antes de empezar

Tres cuestiones que se movieron durante el trabajo:

1. **Si un modelo puede diagnosticar a partir de ventanas de OBD-II con verdad de referencia
   conocida.** Respuesta: sí, con margen amplio sobre la clase mayoritaria. Así se sostiene sobre
   el conjunto de prueba.
2. **Si el criterio de suficiencia de evidencia evita la falsa confianza.** Respuesta: en la
   medición final no hubo ninguna falsa confianza, con un denominador pequeño que se declara.
3. **Si el contexto temporal aporta señal diagnóstica.** Respuesta: **no se sabe**; el apartado 12
   explica por qué la comparación que parecía responderlo no lo hacía.

La tercera merece atención porque es el ejemplo más claro de algo que este trabajo encontró más de
una vez: un resultado que parecía concluyente y dejó de parecerlo al mirar de dónde venían los
datos."""),
    md("""\
## 3. Preparación del entorno

La celda siguiente ancla la raíz del repositorio y deja en la salida la versión de Python, la
plataforma y el commit. Eso último importa: dos ejecuciones de este notebook en commits
distintos no son comparables. La única forma de saberlo es que el commit quede impreso."""),
    code(PREAMBULO),
    md("""\
## 4. El recorrido, en un diagrama

Antes de los números, el camino: la cadena completa, en la que cada etapa recibe algo, hace una cosa
y entrega algo a la siguiente.

**Qué queremos investigar.** Que el recorrido se entienda sin leer el código. Una lista de fases no
mostraría que la decisión de abstenerse ocurre **después** de recuperar la evidencia, que es el
punto del diseño.

**Qué datos utilizamos.** Ninguno. Es un **diagrama conceptual** de la arquitectura implementada,
sin ninguna medición; sus etiquetas son los experimentos que miden cada etapa (Tabla A.1 del
anexo A)."""),
    code("""\
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from mecanico_ia_exp.visualization.style import (
    CATEGORICAL,
    INK_MUTED,
    INK_PRIMARY,
    apply_style,
)

apply_style()

ETAPAS = [
    ("Datos OBD-II", "12 señales a 1 Hz\\nsesión = unidad de reparto", "E2"),
    ("Análisis temporal", "ventanas de 120 s, paso 60 s\\n139 descriptores", "E4, E5"),
    ("Detección y diagnóstico", "bosque aleatorio\\ny GRU bidireccional", "E6, E7"),
    ("Hipótesis diagnóstica", "clase + confianza calibrada\\n+ atribución", "E9"),
    ("Recuperación de evidencia", "corpus del manual\\nfiltrado por motor", "E10-E12"),
    ("Validación de suficiencia", "confianza, cobertura,\\nfuentes, aplicabilidad", "E15, E18"),
    ("Explicar o abstenerse", "EXPLAIN / ABSTAIN\\ncon motivo registrado", "E15, E19"),
    ("Resultado experimental", "falsa confianza,\\nabstención innecesaria", "E19"),
]

# Ancho de la página de la memoria, 5,9 pulgadas: dibujar a esa medida
# evita que Word escale la figura y encoja sus rótulos.
fig, ax = plt.subplots(figsize=(5.9, 7.0))
ax.set_xlim(0, 10)
ax.set_ylim(0, len(ETAPAS) * 1.05)
ax.axis("off")

for i, (titulo, detalle, fases) in enumerate(ETAPAS):
    y = (len(ETAPAS) - 1 - i) * 1.05 + 0.1
    color = CATEGORICAL[i % len(CATEGORICAL)]
    ax.add_patch(
        FancyBboxPatch(
            (1.2, y), 6.4, 0.78,
            boxstyle="round,pad=0.04",
            facecolor=color, alpha=0.16, edgecolor=color, linewidth=1.1,
        )
    )
    # El detalle son DOS líneas a 7 puntos con interlineado 1,5: ocupan unas
    # 0,25 unidades de datos. Anclado en y+0,22 la segunda caía fuera de la caja.
    ax.text(1.45, y + 0.56, titulo, fontsize=9.5, fontweight="bold", color=INK_PRIMARY)
    ax.text(1.45, y + 0.38, detalle, fontsize=7.0, color=INK_MUTED, linespacing=1.5, va="top")
    ax.text(7.75, y + 0.36, fases, fontsize=7.5, color=color, fontweight="bold", va="center")
    if i < len(ETAPAS) - 1:
        ax.add_patch(
            FancyArrowPatch(
                (4.4, y - 0.02), (4.4, y - 0.30),
                arrowstyle="-|>", mutation_scale=11, color=INK_MUTED, linewidth=1.0,
            )
        )

soporte.exportar(fig, "FIG-NB00-01_recorrido", subdirectorio="00_introduccion")
plt.show()"""),
    md("""\
**Qué muestra.** Ocho etapas en serie, con el experimento que cubre cada una. La cadena entra por el
dato crudo y sale por una decisión con dos valores posibles.

**Qué podemos interpretar.** Que la decisión de abstenerse no es un filtro previo sobre la confianza
del modelo: ocurre al final, después de recuperar la evidencia. Por eso puede distinguir “no estoy
seguro” de “estoy seguro pero el manual no lo respalda”. Las dos cosas terminan en abstención y por
motivos distintos. El motivo queda registrado.

**Qué no podemos afirmar.** Que el recorrido funcione así en un vehículo real: todo lo medido es
sintético (apartado 5). El diagrama describe el diseño, no su validez externa."""),
    md("""\
## 5. Los datos: qué son y qué no son

El conjunto es **sintético** por decisión de diseño, con una razón y un coste.

**La razón:** la pregunta exige conocer la verdad de referencia y poder manipularla. Hace falta saber
cuándo empieza un fallo, con qué intensidad y en qué señales, para poder comprobar si la
explicación del sistema se corresponde con lo que de verdad ocurrió. Con telemetría real sin
etiquetar eso no se puede hacer.

**El coste:** la validez externa queda sin establecer. La validación con telemetría real sigue
siendo trabajo posterior. Así está declarado desde el primer día.

El generador produce doce señales a 1 Hz y cinco condiciones de fallo más la normal. Sus constantes
están **calibradas contra el manual de taller** de un Mazda 3 BK con motor Z6. Cada una lleva su
cita: `configs/calibracion_mazda3_bk.yaml`. Calibrar contra el manual de un vehículo real **no
convierte los datos en reales**; lo que cambia es que los parámetros dejan de ser arbitrarios."""),
    code("""\
# Cargamos la muestra que viaja con el repositorio: 18 sesiones, 3 por condición.
# No es `synthetic_v2` --el conjunto oficial, que no se versiona por tamaño--
# pero sale del mismo generador y con la misma semilla global.
datos = soporte.muestra_redistribuible()

print(f"{len(datos):,} muestras · {datos.session_id.nunique()} sesiones")
print(f"frecuencia: {1 / datos.groupby('session_id').timestamp.diff().median():.0f} Hz")
print(f"duración por sesión: {datos.groupby('session_id').timestamp.max().median():.0f} s")
print()
print("condiciones:")
print(datos.groupby("fault_id").session_id.nunique().to_string())
print()
print("regímenes de conducción:")
print(datos.groupby("regime").session_id.nunique().to_string())"""),
    md("""\
**Una ausencia que hay que señalar.** La muestra versionada no contiene sesiones del régimen de
**calentamiento**: el plan equilibrado recorre los cuatro regímenes en ciclo y con tres sesiones por
condición solo alcanza a los tres primeros. Es una consecuencia aritmética del muestreo. Importa
porque el calentamiento es el régimen en que el fallo del termostato se
comporta de forma distinta. Donde haga falta, los notebooks **generan** esas sesiones en el momento
(el generador es determinista) y lo declaran como demostración ilustrativa."""),
    md("""\
**Qué muestra.** Dieciocho sesiones de 600 s, tres por cada una de las seis condiciones,
repartidas entre tres regímenes de conducción (sin calentamiento, por lo dicho arriba). El reparto
es equilibrado a propósito: en datos sintéticos, un desbalance sería un artefacto elegido por quien
genera y no una propiedad del problema.

Las doce señales y por qué están, en una tabla; la columna de rango físico es la que el validador
usa para rechazar valores imposibles."""),
    code("""\
import pandas as pd

from mecanico_ia_exp.obd.signals import CANONICAL_SIGNALS, PID_EQUIVALENTE

pd.DataFrame(
    [
        {
            "señal": s.name,
            "PID OBD-II": PID_EQUIVALENTE[s.name],
            "unidad": s.unit,
            "rango físico": f"{s.minimum:g} … {s.maximum:g}",
            "qué mide": s.description,
        }
        for s in CANONICAL_SIGNALS
    ]
)"""),
    md("""\
## 6. Qué se midió y con cuánta firmeza

La tabla siguiente es el estado de la evidencia. Sale de los registros, no de los informes: si un
informe y su registro discreparan, manda el registro. Ocurrió una vez (con las cifras
de E7) y se corrigió en octubre dejando constancia."""),
    code("""\
# Cada cifra se lee de su registro JSON. Ninguna está escrita a mano en este
# notebook: si un registro cambiara, la tabla cambiaría con él.
e6 = soporte.registro("E6_baseline_synthetic_v2")
e7 = soporte.registro("E7_temporal_synthetic_v2")
e19 = soporte.registro("E19_evaluacion_final_v3")

resumen = pd.DataFrame(
    [
        {
            "experimento": "E6 línea base (bosque)",
            "conjunto": e6["dataset_id"],
            "partición": "validación",
            "F1 macro": f"{e6['metrics']['macro_f1']:.4f}",
            "exactitud": f"{e6['metrics']['accuracy']:.4f}",
            "ECE": f"{e6['metrics']['calibration']['ece']:.4f}",
            "registro": "E6_baseline_synthetic_v2.json",
        },
        {
            "experimento": "referencia: clase mayoritaria",
            "conjunto": e6["dataset_id"],
            "partición": "validación",
            "F1 macro": f"{e6['majority_baseline']['macro_f1']:.4f}",
            "exactitud": f"{e6['majority_baseline']['accuracy']:.4f}",
            "ECE": "—",
            "registro": "E6_baseline_synthetic_v2.json",
        },
        {
            "experimento": "E7 modelo temporal (GRU)",
            "conjunto": e7["dataset_id"],
            "partición": "validación",
            "F1 macro": f"{e7['metrics']['macro_f1']:.4f}",
            "exactitud": f"{e7['metrics']['accuracy']:.4f}",
            "ECE": f"{e7['metrics']['calibration']['ece']:.4f}",
            "registro": "E7_temporal_synthetic_v2.json",
        },
    ]
)
resumen"""),
    md("""\
### 6.1 Qué significan esas métricas

**F1 macro.** Media no ponderada del F1 de cada clase, siendo el F1 la media armónica de precisión y
exhaustividad. *Por qué esta y no la exactitud:* la media **no ponderada** da el mismo peso a una
clase con 14 ventanas que a una con 28, de modo que fallar sistemáticamente la clase difícil se
nota. La exactitud no lo notaría. *Su límite:* resume en un número seis comportamientos distintos. Por
eso el trabajo publica siempre las métricas por clase al lado.

**Exactitud.** Fracción de ventanas clasificadas correctamente. *Su límite:* con seis clases
equilibradas el azar da 0,17, así que 0,88 dice poco por sí solo; la referencia útil es la clase
mayoritaria, que está en la tabla anterior.

**Clase mayoritaria.** Predecir siempre la clase más frecuente del entrenamiento. Es el suelo: un
modelo que no lo supere no ha aprendido nada. Su F1 macro de 0,0741 es bajo porque la
media no ponderada castiga acertar una sola clase.

**ECE (*expected calibration error*).** Se agrupan las predicciones en diez tramos según su
confianza y se mide, en cada tramo, la diferencia entre la confianza media y el acierto real; el ECE
es la media de esas diferencias, ponderada por cuántas predicciones hay en cada tramo. *Por qué
importa aquí más que en otros problemas:* todo el criterio de abstención compara la confianza contra
un umbral. Si la confianza estuviera mal calibrada, el umbral no significaría nada. *Su límite:* con
diez tramos y pocas ventanas, cada tramo tiene pocas predicciones y la cifra es inestable."""),
    md("""\
## 7. Qué sostiene cada objetivo, visto de una vez

**Qué queremos investigar.** Qué objetivos se cumplen en su alcance y cuáles solo en parte. Es el
mapa que evita el error más común al leer un trabajo de este tipo, que es tomar lo implementado por
demostrado.

**Qué datos utilizamos.** Ninguna medición: es un **diagrama documental** y cada fila sale del
registro de experimentos y del estado declarado de cada objetivo."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_objetivos

fig = fig_objetivos()
soporte.exportar(fig, "FIG-NB00-02_objetivos", subdirectorio="00_introduccion")
plt.show()"""),
    md("""\
**Qué muestra.** Cada objetivo con los experimentos que lo miden y su estado: OE1, OE3 y OE5
**cumplidos** en su alcance; OE2 y OE4 **parciales**. Es lo que fija la Tabla 6.1 de la memoria.

**Qué podemos interpretar.** Que el respaldo es desigual y está declarado: unos objetivos tienen
medición sobre el conjunto de prueba y otros solo sobre validación.

**Qué no podemos afirmar.** Que *cumplido* signifique validado fuera de los datos sintéticos, ni
que una capacidad implementada funcione: lo que no se ha evaluado no tiene evidencia a su favor ni
en su contra.

**Relación con la pregunta de investigación.** Acota el alcance de las conclusiones: lo que la pregunta de
investigación puede dar por respondido es lo que tiene evidencia, no lo que tiene código."""),
    md("""\
## 8. El resultado de la evaluación final

E19 es la única medición sobre el **conjunto de prueba**, que permaneció cerrado por excepción hasta
el 12 de octubre de 2026. Llegó al final en el **tercer intento** (los dos anteriores se
interrumpieron y están declarados en el apartado 9), con las reglas congeladas y ancladas a un commit
antes de abrirlo.

Las tres cifras primarias, leídas de su registro con numerador y denominador. El campo `status`
del registro dice `EVALUACION_FINAL`; el índice de experimentos lo da por
completado con limitaciones documentadas."""),
    code("""\
print("Registro:", "experiments/E19_evaluacion_final_v3.json")
print("Estado: ", e19["status"])
print()

tabla_e19 = soporte.tabla("E19_evaluacion_final_v3")
operativo = tabla_e19[tabla_e19.stratum == "operativo"]

deben_abstenerse = operativo[operativo.expected_decision == "ABSTAIN"]
deben_explicar = operativo[operativo.expected_decision == "EXPLAIN"]
falsa_confianza = deben_abstenerse[deben_abstenerse.decision == "EXPLAIN"]
abstencion_innecesaria = deben_explicar[deben_explicar.decision == "ABSTAIN"]
con_evidencia = operativo[operativo.corpus_variant == "FULL"]
explicadas = con_evidencia[con_evidencia.decision == "EXPLAIN"]

print(f"ejecuciones del estrato operativo:  {len(operativo)}")
print(f"ventanas independientes:            {operativo.window_id.nunique()}")
print(f"sesiones distintas:                 {operativo.session_id.nunique()}")
print()
print(f"falsa confianza:                   {len(falsa_confianza)}/{len(deben_abstenerse)}")
print(f"abstención innecesaria:            {len(abstencion_innecesaria)}/{len(deben_explicar)}")
print(f"respuesta con evidencia completa:  {len(explicadas)}/{len(con_evidencia)}")"""),
    md("""\
**Qué muestra.** Falsa confianza 0 de 14. Abstención innecesaria 2 de 8. Respuesta con evidencia
completa 6 de 10.

**Qué podemos interpretar.** En las catorce ejecuciones en que debía abstenerse, el sistema se
abstuvo en todas: el resultado que PI.3 pedía.

**Qué no podemos afirmar.** Que el riesgo de falsa confianza sea cero. El denominador es **14**,
procedentes de **siete ventanas de siete sesiones**. Con 0 de 14, el intervalo de Wilson al 95 %
llega al 21,5 %; el real es más ancho porque las catorce ejecuciones no son independientes. Lo que
se ha medido es que en esta muestra no ocurrió. Por eso el índice lo da por
completado con limitaciones documentadas y no por validado, que no se usa como sinónimo de
hipótesis demostrada.

El análisis completo, con los diagnósticos incorrectos y los dos análisis descriptivos, está en
`03_analisis_e19.ipynb`."""),
    md("""\
## 9. Resultados negativos y limitaciones: lo que no salió

Un recorrido que solo enseñara lo que funcionó no serviría como evidencia. Esto es lo que no
funcionó y en varios casos es más informativo que lo que sí.

| Qué | Qué pasó | Dónde está |
|---|---|---|
| **El modelo temporal no superó a la línea base** | GRU 0,8230 frente a 0,8788 del bosque, en validación | `E7_temporal_synthetic_v2.json` |
| **Y la explicación que se dio era inválida** | se atribuyó la desventaja al volumen de datos comparando dos conjuntos que además se generaron con el motor **sin calibrar** y **con** calibrar. La comparación cambia dos cosas a la vez | retirada, marcada `SUPERSEDED 2026-10-12` en `docs/experiments/E7_modelo_temporal.md` |
| **La recuperación semántica pura no funcionó** | Hit-rate 0,00, con un distractor por encima del fragmento relevante | `E12_retrieval.json` |
| **La condición con distractor no medía lo que decía** | en dos de los tres fallos tenía **la misma configuración** que la condición parcial; solo en la fuga de vacío llegaban dos fragmentos del distractor (corregido el 13-10-2026) | `politica-condicion-distractor.md` |
| **Un espacio de embeddings mezclado** | las búsquedas no declaraban qué modelo las había producido; se corrigió y se reejecutó con pre-registro (RERUN-A) | `resultado-rerun-a.md` |
| **El verificador regresionó al corregirlo** | la política v2 arregló seis casos y rompió uno que antes acertaba | `E15_suficiencia_verifier_v2.json`, campos `corrected_vs_v1` y `regression_vs_v1` |
| **Cifras del texto generado que nadie produjo** (`L-26`) | nueve de las treinta y cinco salidas de E19 contienen un número que el verificador no produjo: la trazabilidad alcanza a los identificadores de la evidencia, no a las cifras | `docs/limitations.md`, `L-26` |
| **Dos cifras publicadas sin registro** | las medias de temperatura del termostato se calcularon en el análisis y no se guardaron: hoy no se pueden verificar | marcadas **no utilizables** el 12-10-2026 |
| **El conjunto de prueba se abrió cinco veces** | tres intentos de E19 (dos interrumpidos), una para repetir las ablaciones y **una accidental**, al leer identificadores de sesión que ya estaban en otro sitio | `docs/methodology/registro-aperturas-test.md`, con qué se expuso en cada una |
| **Dos artefactos dañados por el propio trabajo** | una tabla de E5 sobrescrita y otra de E15 borrada por un patrón demasiado amplio; las detectó el censo | `incidencia-artefactos-e5.md` e `incidencia-artefactos-e15.md`; la segunda **no se declara restaurada** |

Sobre el cuarto punto, que afecta a lo que PI.4 puede afirmar: hasta el rediseño del 13 de octubre
(P1) las condiciones realmente independientes eran **cuatro y no cinco**; P1 añade la quinta con
tres situaciones construidas y seis ejecuciones.

Sobre el conjunto de prueba: **cinco aperturas no son tres**. La cuarta
repite unas ablaciones definidas antes de la primera; la quinta **no debió ocurrir** y está
registrada como lo que fue, un descuido corregido en el acto. Ninguna cambió una decisión de diseño."""),
    md("""\
## 10. Discusión: la formulación amplia y por qué no es la pregunta de este trabajo

Se discute aquí porque el lector puede encontrarla en material anterior. El trabajo circuló
hasta septiembre de 2026 con una formulación más ambiciosa:

> ¿Puede un sistema inteligente híbrido **identificar patrones de fallo no representados en su
> conocimiento disponible**, generar hipótesis diagnósticas a partir del análisis contextual y
> longitudinal de datos OBD-II y validarlas mediante evidencia antes de **incorporarlas como
> conocimiento reutilizable**?

Una auditoría la examinó término a término y encontró que **de sus cinco componentes, uno tenía
evidencia**. Los dos marcados en negrita (identificar patrones no representados e incorporar
conocimiento reutilizable) **no tenían implementación ni fase** en el plan de veinte experimentos.
`ADR-004` fijó en consecuencia la formulación acotada como canónica.

Lo que sí está construido de esa formulación amplia no se retira ni se esconde y sirve a la pregunta
acotada:

| Componente | Qué hay | Estado |
|---|---|---|
| Detección de anomalías | E6, E7 | **necesario** para el diagnóstico |
| Análisis longitudinal | E4, E5, E7 y el diseño de PI.1 | **necesario** en lo medido; **exploratorio** en lo diseñado y no ejecutado |
| Generación de hipótesis | E9: la atribución produce las observaciones | **necesario** para la trazabilidad |
| Identificar patrones no representados | nada | **línea futura**, sin evidencia |
| Memoria evolutiva de conocimiento | nada | **línea futura**, sin evidencia |

Los dos últimos son trabajo posterior: proponerlos formalmente exigiría resultados verificables que
hoy no existen. Presentarlos como logrados sería el tipo de afirmación sin evidencia que
este trabajo se propone detectar."""),
    md("""\
## 11. Conclusiones de este recorrido

**Qué quedó sostenido.** PI.1 a PI.4 cumplen su criterio vigente, con validez desigual y con una
salvedad que hay que decir primero: tres de los cuatro criterios se reformularon con parte de los
resultados ya conocida. La pregunta queda sostenida en las condiciones evaluadas, no confirmada
frente al protocolo inicial. Que el diagnóstico a partir de ventanas de OBD-II supera a la clase
mayoritaria con margen amplio y que su confianza se puede calibrar (PI.1): en validación el error
baja de 0,144 a 0,085; en prueba apenas cambia, de 0,097 a 0,092. Que cada afirmación admitida
cita observaciones y fragmentos identificables (PI.2); que el fragmento sostenga lo afirmado lo
establece el propio verificador, sin anotación independiente. La trazabilidad tampoco alcanza a las
cifras del texto: nueve de las treinta y cinco salidas de E19 contienen un número que el verificador
no produjo (`L-26`). Que el sistema cambia de explicar a abstenerse al retirarle la evidencia, con
los datos, el modelo y la confianza idénticos (PI.3).

**Qué no recibió apoyo.** Que el modelo temporal supere a la línea base. Y la explicación que se dio
de esa desventaja quedó retirada, no confirmada.

**Qué permanece sin demostrar.** Si el contexto temporal aporta señal diagnóstica y en qué fallos
(apartado 12). Si el sistema rechaza evidencia no pertinente en general: PI.4 se responde con el
rediseño de la condición con distractor (P1, 13-10-2026), acotado a tres situaciones construidas y
seis ejecuciones, sin estimar ninguna tasa. Y la validez externa de todo lo anterior, que exigiría telemetría real.

**Cómo contribuye al TFM.** Este notebook es el mapa: dice dónde está cada pieza de evidencia y con
cuánta firmeza se sostiene. Dentro de la entrega, la correspondencia entre notebooks y resultados
está en la **Tabla C.2** del anexo C de la memoria y la de cada figura y tabla con su artefacto en
la **Tabla C.5**; la matriz completa pregunta → objetivo → experimento → notebook → figura está en
`docs/notebook-traceability.md`, en el repositorio del laboratorio."""),
    md("""\
## 12. Qué queda abierto: el contexto temporal y por qué

**¿En qué tipos de fallo el contexto temporal aporta señal diagnóstica adicional y en cuáles no?**

Parecía respondida. No lo está, por dos confusores que se identificaron auditando lo publicado:

1. **Volumen y calibración del generador cambian juntos.** La comparación `synthetic_v2` frente a
   `synthetic_v3` tenía el triple de sesiones *y* un fenómeno distinto: `v3` se generó el 1 de
   septiembre, **antes** de que las constantes del motor se calibraran contra el manual. Su ralentí
   está en 820 rpm, un valor sin ningún respaldo documental. Por qué la constante
   `GENERATOR_VERSION` no distingue los dos conjuntos se explica en `02_comparacion_modelos`,
   apartado 13.

2. **Representación y estimador cambian juntos.** El bosque recibe 139 descriptores de ventana; la
   red, la secuencia de 120 × 12 en crudo. Ninguna diferencia entre los dos puede atribuirse al
   contexto temporal: podría venir de la representación, del estimador o de su interacción. Lo que
   esa comparación mide es la diferencia entre **dos recorridos completos**.

Que la red gane en el termostato bloqueado (0,8148 frente a 0,7826), la condición cuya firma es
temporal, no confirma nada; el porqué está en `02_comparacion_modelos`, apartado 8. Hay además una
explicación alternativa, medida en octubre: el fallo del termostato **no altera la trayectoria**
mientras el refrigerante no supera su tope, de modo que en la sesión de calentamiento de validación
**cinco de sus siete** ventanas etiquetadas con el fallo no contienen ninguna señal observable de él
(`06_expresion_del_fallo`, apartado 8).

El diseño para responder la pregunta sin abrir una línea nueva está en `docs/diseno-pi1/` y
**no se ha ejecutado**."""),
    md("""\
## 13. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb` para este notebook; `--extra ml` para el de comparación |
| **Datos** | `data/samples/synthetic_sample.parquet`, versionado |
| **Semilla** | 20260901, la del laboratorio |
| **Commit** | el que imprime la celda del apartado 3 |
| **Tiempo** | menos de un minuto |
| **Memoria** | por debajo de 1 GB |
| **Artefactos que produce** | dos figuras en `notebooks/salida/00_introduccion/`, PNG y SVG: `FIG-NB00-01_recorrido` y `FIG-NB00-02_objetivos` |

**Modalidad** (véase *Cómo leer*): no reproduce ningún cálculo. Si un registro estuviera mal, este
notebook lo mostraría igual de mal. Por eso la verificación de que las cifras del notebook
coinciden con sus artefactos está automatizada en `tests/test_notebooks.py`.

**Qué no se puede reproducir en una máquina cualquiera:** nada de lo que depende del corpus
documental del manual (no se redistribuye, es propiedad del fabricante) ni de los pesos del
adaptador LoRA. Los notebooks que los necesitan están marcados como FULL en el índice."""),
    code("""\
soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "las cifras se leen de experiments/*.json y artifacts/tables/*.csv; "
    "el diagrama del apartado 4 es una demostración ilustrativa y no mide nada",
)"""),
    md("""\
## 14. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** El esquema de este notebook es la **Figura A.1** del anexo A. Las ocho etapas que recorre se describen en el capítulo 4 y en la **Tabla A.1**.

**Documentación del trabajo**
- `docs/experiment-index.md`: índice de los diecinueve experimentos con su estado
- `docs/matriz_validacion_pi.md`: respuesta a cada subpregunta con su criterio
- `docs/limitations.md`: registro de limitaciones
- `docs/notebook-traceability.md`: qué notebook corresponde a cada resultado
- `docs/notebooks/auditoria-portabilidad.md`: qué se puede ejecutar sin el equipo del autor

**Registros citados en este notebook**
- `experiments/E6_baseline_synthetic_v2.json`
- `experiments/E7_temporal_synthetic_v2.json`
- `experiments/E19_evaluacion_final_v3.json`
- `artifacts/tables/E19_evaluacion_final_v3.csv`

**Decisiones metodológicas**
- `configs/calibracion_mazda3_bk.yaml`: cada constante del generador con su cita del manual
- `configs/manifest_e19.json`: el estado congelado de la evaluación final
- `docs/methodology/congelacion-anotacion-e19.md`: las reglas, fijadas antes de abrir el test
- `docs/methodology/registro-aperturas-test.md`: cada acceso al conjunto de prueba
- `docs/methodology/expresion-efectiva-del-fallo.md`: cuándo un fallo altera de verdad la señal"""),
]

if __name__ == "__main__":
    escribir("00_introduccion.ipynb", CELDAS)
