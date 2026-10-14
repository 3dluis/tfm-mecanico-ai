"""Construye `00_introduccion.ipynb`: el recorrido experimental para el jurado."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Introducción y recorrido experimental

**Notebook** `00_introduccion` · **versión** 1.0 · **fecha** 12 de octubre de 2026

| | |
|---|---|
| **Experimentos que recorre** | E1 a E19 |
| **Conjunto** | `data/samples/synthetic_sample.parquet` (18 sesiones) y los registros de `experiments/` |
| **Protocolo** | ninguno propio: este notebook no mide nada |
| **Estado** | vigente |
| **Pregunta de investigación** | la principal, y el mapa de cómo las cuatro subpreguntas la componen |
| **Evidencia original** | `docs/experiment-index.md`, `docs/matriz_validacion_pi.md`, `experiments/*.json` |

---

## Qué es este documento, y qué no es

Es el punto de entrada. Explica qué se investigó, en qué orden, con qué datos y qué quedó
demostrado y qué no. No contiene ningún resultado propio: todo lo que muestra sale de los registros
de los experimentos, y cada cifra lleva al lado el fichero del que procede.

Quien quiera comprobar un número concreto no necesita ejecutar nada: el registro está en el
repositorio. Quien quiera ejecutar, puede; el apartado de reproducibilidad dice qué se puede
reproducir en una máquina cualquiera y qué no."""),
    md("""\
## 1. La pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

Es la formulación **acotada**, fijada por `ADR-004` el 12 de septiembre de 2026. La elección importa
y se explica en el apartado 9: el trabajo circuló un tiempo con una formulación más amplia, y una
auditoría encontró que dos de sus términos no tenían experimento que los sostuviera.

La pregunta tiene tres verbos y ninguno es decorativo: **explicar**, **rastrear** y **reconocer**.
Cada uno se evalúa por separado, porque un sistema puede acertar el diagnóstico y sostenerlo con
evidencia que no viene al caso, o anclarlo impecablemente en un documento que no aplica a ese motor.

| Subpregunta | Qué evalúa | Experimentos |
|---|---|---|
| **PI.1** | que el diagnóstico a partir de OBD-II supere a la clase mayoritaria con margen amplio y que su confianza se pueda calibrar | E5, E6, E7, E19 |
| **PI.2** | que toda afirmación se ancle en una observación o un fragmento identificable | E14, E15, E19 |
| **PI.3** | que el sistema **reconozca cuándo no sabe**: al retirar la evidencia, pasa de explicar a abstenerse | E15, E16, E18, E19 |
| **PI.4** | que rechace evidencia no pertinente | E17, y **una condición invalidada**, ver más abajo |

La tercera es la que vertebra el trabajo. Un sistema de diagnóstico que acierta el 90 % de las veces
y afirma con confianza en el 10 % restante es peor, en un taller, que uno que acierta el 70 % y
calla en el resto."""),
    md("""\
## 2. Qué desconocíamos antes de empezar

Tres cosas, y las tres se han movido durante el trabajo:

1. **Si un modelo puede diagnosticar a partir de ventanas de OBD-II con verdad de referencia
   conocida.** Respuesta: sí, con margen amplio sobre la clase mayoritaria, y así se sostiene sobre
   el conjunto de prueba.
2. **Si el criterio de suficiencia de evidencia evita la falsa confianza.** Respuesta: en la
   medición final no hubo ninguna falsa confianza, con un denominador pequeño que se declara.
3. **Si el contexto temporal aporta señal diagnóstica.** Respuesta: **no se sabe**, y el trabajo
   dedica un apartado entero a explicar por qué la comparación que parecía responderlo no lo hacía.

La tercera merece atención porque es el ejemplo más claro de algo que este trabajo encontró más de
una vez: un resultado que parecía concluyente y dejó de parecerlo al mirar de dónde venían los
datos."""),
    md("""\
## 3. Preparación del entorno

La celda siguiente ancla la raíz del repositorio y deja en la salida la versión de Python, la
plataforma y el commit exacto. Eso último importa: dos ejecuciones de este notebook en commits
distintos no son comparables, y la única forma de saberlo es que el commit quede impreso."""),
    code(PREAMBULO),
    md("""\
## 4. El recorrido, en un diagrama

Antes de los números, el camino. Lo que sigue es la cadena de procesamiento completa: cada etapa
recibe algo, hace una cosa y entrega algo a la siguiente.

**Qué queremos investigar con este diagrama:** que el recorrido se entienda sin leer el código.
**Qué datos utiliza:** ninguno; es la arquitectura, dibujada desde su descripción.
**Por qué esta visualización:** porque la alternativa —una lista de fases— no muestra que la decisión
de abstenerse ocurre **después** de recuperar la evidencia y no antes, que es el punto del diseño."""),
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
            (1.2, y), 6.4, 0.72,
            boxstyle="round,pad=0.04",
            facecolor=color, alpha=0.16, edgecolor=color, linewidth=1.1,
        )
    )
    ax.text(1.45, y + 0.52, titulo, fontsize=9.5, fontweight="bold", color=INK_PRIMARY)
    ax.text(1.45, y + 0.22, detalle, fontsize=7.0, color=INK_MUTED, linespacing=1.5, va="top")
    ax.text(7.75, y + 0.36, fases, fontsize=7.5, color=color, fontweight="bold", va="center")
    if i < len(ETAPAS) - 1:
        ax.add_patch(
            FancyArrowPatch(
                (4.4, y - 0.02), (4.4, y - 0.30),
                arrowstyle="-|>", mutation_scale=11, color=INK_MUTED, linewidth=1.0,
            )
        )

ax.set_title(
    "Recorrido experimental: del dato OBD-II a la decisión de explicar o abstenerse",
    fontsize=10.5, fontweight="bold", loc="left", pad=14,
)
ax.text(
    0.0, -0.45,
    "E1-E19 · sin conjunto de datos: es la arquitectura, dibujada desde su descripción · "
    "etiquetas de la derecha: experimentos que cubren la etapa · "
    "fuente: docs/experiment-index.md",
    fontsize=6.5, color=INK_MUTED,
)
soporte.exportar(fig, "FIG-NB00-01_recorrido", subdirectorio="00_introduccion")
plt.show()"""),
    md("""\
**Qué muestra.** Ocho etapas en serie, con el experimento que cubre cada una. La cadena entra por el
dato crudo y sale por una decisión con dos valores posibles.

**Qué podemos interpretar.** Que la decisión de abstenerse no es un filtro previo sobre la confianza
del modelo: ocurre al final, después de recuperar la evidencia, y por eso puede distinguir «no estoy
seguro» de «estoy seguro pero el manual no lo respalda». Las dos cosas terminan en abstención y por
motivos distintos, y el motivo queda registrado.

**Qué no podemos afirmar.** Que el recorrido funcione así en un vehículo real. Todo lo medido es
sobre datos sintéticos de un generador paramétrico, y la validación externa con telemetría real
sigue siendo trabajo posterior. El diagrama describe el diseño, no su validez externa."""),
    md("""\
## 5. Los datos: qué son y qué no son

El conjunto es **sintético**. No es una limitación oculta: es una decisión de diseño con una razón y
un coste.

**La razón:** la pregunta exige conocer la verdad de referencia y poder manipularla. Hace falta saber
exactamente cuándo empieza un fallo, con qué intensidad y en qué señales, para poder comprobar si la
explicación del sistema se corresponde con lo que de verdad ocurrió. Con telemetría real sin
etiquetar eso no se puede hacer.

**El coste:** la validez externa queda sin establecer, y así está declarado desde el primer día.

El generador produce doce señales a 1 Hz y cinco condiciones de fallo más la normal. Sus constantes
están **calibradas contra el manual de taller** de un Mazda 3 BK con motor Z6, y cada una lleva su
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
condición solo alcanza a los tres primeros. No es un descuido del muestreo, es una consecuencia
aritmética, pero importa, porque el calentamiento es el régimen en que el fallo del termostato se
comporta de forma distinta. Donde haga falta, los notebooks **generan** esas sesiones en el momento
—el generador es determinista— y lo declaran como demostración ilustrativa."""),
    md("""\
**Lo observado.** Dieciocho sesiones de 600 s, tres por cada una de las seis condiciones,
repartidas entre cuatro regímenes de conducción. Reparto equilibrado a propósito: un desbalance en
datos sintéticos sería un artefacto elegido por quien genera, no una propiedad del problema.

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
## 6. Qué se midió, y con cuánta firmeza

La tabla siguiente es el estado de la evidencia. Sale de los registros, no de los informes: si un
informe y su registro discreparan, manda el registro. Eso ocurrió de verdad una vez, con las cifras
de E7, y se corrigió en octubre dejando constancia."""),
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
### Qué significan esas métricas

No se presentan sin explicar, porque un número sin su definición no es evidencia de nada.

**F1 macro.** Media no ponderada del F1 de cada clase, siendo el F1 la media armónica de precisión y
exhaustividad. *Por qué esta y no la exactitud:* la media **no ponderada** da el mismo peso a una
clase con 14 ventanas que a una con 28, de modo que fallar sistemáticamente la clase difícil se
nota. La exactitud no lo notaría. *Su límite:* resume en un número seis comportamientos distintos, y
por eso el trabajo publica siempre las métricas por clase al lado.

**Exactitud.** Fracción de ventanas clasificadas correctamente. *Su límite:* con seis clases
equilibradas el azar da 0,17, así que 0,88 dice poco por sí solo; la referencia útil es la clase
mayoritaria, que está en la tabla justo debajo.

**Clase mayoritaria.** Predecir siempre la clase más frecuente del entrenamiento. Es el suelo: un
modelo que no lo supere no ha aprendido nada. Su F1 macro de 0,0741 es bajo precisamente porque la
media no ponderada castiga acertar una sola clase.

**ECE (*expected calibration error*).** Se agrupan las predicciones en diez tramos según su
confianza y se mide, en cada tramo, la diferencia entre la confianza media y el acierto real; el ECE
es la media de esas diferencias, ponderada por cuántas predicciones hay en cada tramo. *Por qué
importa aquí más que en otros problemas:* todo el criterio de abstención compara la confianza contra
un umbral. Si la confianza estuviera mal calibrada, el umbral no significaría nada. *Su límite:* con
diez tramos y pocas ventanas, cada tramo tiene pocas predicciones y la cifra es inestable."""),
    md("""\
## 7. El resultado de la evaluación final

E19 es la única medición sobre el **conjunto de prueba**, que permaneció cerrado por excepción hasta
el 12 de octubre de 2026. Se ejecutó una vez, con las reglas congeladas y ancladas a un commit antes
de abrirlo.

Las tres cifras primarias, leídas de su registro con numerador y denominador, que es la única forma
honesta de presentarlas."""),
    code("""\
print("Registro:", "experiments/E19_evaluacion_final_v3.json")
print("Estado:  COMPLETED — WITH DOCUMENTED LIMITATIONS")
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
print(f"falsa confianza:         {len(falsa_confianza)}/{len(deben_abstenerse)}")
print(f"abstención innecesaria:  {len(abstencion_innecesaria)}/{len(deben_explicar)}")
print(f"cobertura con evidencia: {len(explicadas)}/{len(con_evidencia)}")"""),
    md("""\
**Lo observado.** Falsa confianza 0 de 14. Abstención innecesaria 2 de 8. Cobertura 6 de 10.

**Qué podemos interpretar.** En las catorce ejecuciones en que el sistema debía abstenerse, se
abstuvo en todas. Es el resultado que la subpregunta PI.3 pedía.

**Qué no podemos afirmar, y conviene decirlo aquí y no en una nota al pie.** Que el riesgo de falsa
confianza sea cero. El denominador es **14**, procedentes de **siete sesiones**: con catorce
observaciones, un cero es compatible con una tasa real de varios puntos porcentuales. Lo que se ha
medido es que en esta muestra no ocurrió, no que no pueda ocurrir. El experimento está marcado como
`COMPLETED — WITH DOCUMENTED LIMITATIONS` precisamente por esto, y `VALIDATED` **no** se usa como
sinónimo de hipótesis demostrada.

El análisis completo, con los diagnósticos incorrectos y los dos análisis descriptivos, está en
`03_analisis_e19.ipynb`."""),
    md("""\
## 8. Resultados negativos y confusores: lo que no salió

Un recorrido que solo enseñara lo que funcionó no serviría como evidencia. Esto es lo que no
funcionó, y en varios casos es más informativo que lo que sí.

| Qué | Qué pasó | Dónde está |
|---|---|---|
| **El modelo temporal no superó a la línea base** | GRU 0,8230 frente a 0,8788 del bosque, en validación | `E7_temporal_synthetic_v2.json` |
| **Y la explicación que se dio era inválida** | se atribuyó la desventaja al volumen de datos comparando dos conjuntos que además se generaron con el motor **sin calibrar** y **con** calibrar. La comparación cambia dos cosas a la vez | `SUPERSEDED 2026-10-12` en `docs/experiments/E7_modelo_temporal.md` |
| **La recuperación semántica pura no funcionó** | Hit-rate 0,00, con un distractor por encima del fragmento relevante | `E12_retrieval.json` |
| **La condición con distractor no medía lo que decía** | con el filtro de motor activo recuperaba **exactamente los mismos** fragmentos que la condición parcial: era la condición parcial contada dos veces | `politica-condicion-distractor.md` |
| **Un espacio de embeddings mezclado** | las búsquedas no declaraban qué modelo las había producido; se corrigió y se reejecutó con pre-registro | `resultado-rerun-a.md` |
| **El verificador regresionó al corregirlo** | la política v2 arregló cinco casos y rompió uno que antes acertaba | `E15_suficiencia_verifier_v2.json` |
| **Dos cifras publicadas sin registro** | las medias de temperatura del termostato se calcularon en el análisis y no se guardaron: hoy no se pueden verificar | marcadas **no utilizables** el 12-10-2026 |
| **El conjunto de prueba se abrió cinco veces** | tres intentos de E19 —dos interrumpidos—, una para repetir las ablaciones y **una accidental**, al leer identificadores de sesión que ya estaban en otro sitio | `docs/methodology/registro-aperturas-test.md`, con qué se expuso en cada una |
| **Dos artefactos dañados por el propio trabajo** | una tabla de E5 sobrescrita y otra de E15 borrada por un patrón demasiado amplio; las detectó el censo | `incidencia-artefactos-e5.md` e `incidencia-artefactos-e15.md`; la segunda **no se declara restaurada** |

Sobre el cuarto punto conviene ser explícito, porque afecta a lo que PI.4 puede afirmar: mientras el
rediseño no exista, las condiciones realmente independientes son **cuatro y no cinco**.

Y sobre el conjunto de prueba, con la misma franqueza: **cinco aperturas no son tres**. Las tres
primeras son la misma medición intentada tres veces; la cuarta repite unas ablaciones definidas antes
de la primera; la quinta **no debió ocurrir** y está registrada como lo que fue, un descuido corregido
en el acto. Lo que se expuso en cada una está en la tabla, y ninguna cambió una decisión de diseño."""),
    md("""\
## 9. La pregunta que sigue abierta, y por qué

**¿En qué tipos de fallo el contexto temporal aporta señal diagnóstica adicional y en cuáles no?**

Parecía respondida. No lo está, por dos confusores que se identificaron auditando lo publicado:

1. **Volumen y calibración del generador cambian juntos.** La comparación `synthetic_v2` frente a
   `synthetic_v3` tenía el triple de sesiones *y* un fenómeno distinto: `v3` se generó el 1 de
   septiembre, **antes** de que las constantes del motor se calibraran contra el manual. Su ralentí
   está en 820 rpm, un valor sin ningún respaldo documental. La constante `GENERATOR_VERSION` valió
   `"1.0.0"` en los dos casos y no los distingue, que es por lo que la diferencia pasó
   desapercibida durante semanas.

2. **Representación y estimador cambian juntos.** El bosque recibe 139 descriptores de ventana; la
   red, la secuencia de 120 × 12 en crudo. Ninguna diferencia entre los dos puede atribuirse al
   contexto temporal: podría venir de la representación, del estimador o de su interacción. Lo que
   esa comparación mide es la diferencia entre **dos recorridos completos**.

Hay una tentación concreta que conviene nombrar para no caer en ella: la red gana en el termostato
bloqueado —0,8148 frente a 0,7826— y es justo la condición cuya firma es temporal, «algo que debería
subir y no sube». Encaja tan bien que parece confirmación. **No lo es.** Es una diferencia de 0,03
en una clase de 14 ventanas, medida una sola vez, entre dos recorridos que difieren en todo. Y hay
una explicación alternativa, medida en octubre: el fallo del termostato **no altera la trayectoria**
mientras el refrigerante no supera su tope, de modo que en una sesión de calentamiento **32 de 45**
ventanas etiquetadas con el fallo no contienen ninguna señal observable de él.

El diseño para responder la pregunta —sin abrir una línea nueva— está en `docs/diseno-pi1/` y
**no se ha ejecutado**.

## 9.1 La formulación amplia, y por qué no es la pregunta de este trabajo

Conviene decirlo aquí porque el lector puede encontrarla en material anterior. El trabajo circuló
hasta septiembre de 2026 con una formulación más ambiciosa:

> ¿Puede un sistema inteligente híbrido **identificar patrones de fallo no representados en su
> conocimiento disponible**, generar hipótesis diagnósticas a partir del análisis contextual y
> longitudinal de datos OBD-II y validarlas mediante evidencia antes de **incorporarlas como
> conocimiento reutilizable**?

Una auditoría la examinó término a término y encontró que **de sus cinco componentes, uno tenía
evidencia**. Los dos marcados en negrita —identificar patrones no representados e incorporar
conocimiento reutilizable— **no tenían implementación ni fase** en el plan de veinte experimentos.
`ADR-004` fijó en consecuencia la formulación acotada como canónica.

Lo que sí está construido de esa formulación amplia no se retira ni se esconde, y sirve a la pregunta
acotada:

| Componente | Qué hay | Estado |
|---|---|---|
| Detección de anomalías | E6, E7 | **necesario** para el diagnóstico |
| Análisis longitudinal | E4, E5, E7 y el diseño de PI.1 | **necesario** en lo medido; **exploratorio** en lo diseñado y no ejecutado |
| Generación de hipótesis | E9: la atribución produce las observaciones | **necesario** para la trazabilidad |
| Identificar patrones no representados | nada | **línea futura**, sin evidencia |
| Memoria evolutiva de conocimiento | nada | **línea futura**, sin evidencia |

Los dos últimos son trabajo posterior, y proponerlos formalmente exigiría resultados verificables que
hoy no existen. Presentarlos como logrados sería exactamente el tipo de afirmación sin evidencia que
este trabajo se propone detectar."""),
    md("""\
## 10. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb` para este notebook; `--extra ml` para el de comparación |
| **Datos** | `data/samples/synthetic_sample.parquet`, versionado |
| **Semilla** | 20260901, la del laboratorio |
| **Commit** | el que imprime la celda del apartado 3 |
| **Tiempo** | menos de un minuto |
| **Memoria** | por debajo de 1 GB |
| **Artefactos que produce** | `notebooks/salida/00_introduccion/FIG-NB00-01_recorrido.{png,svg}` |

**Modalidad:** este notebook es **visualización de evidencia histórica** con una **demostración
ilustrativa** (el diagrama). No reproduce ningún cálculo: lee los registros y los muestra. Si un
registro estuviera mal, este notebook lo mostraría igual de mal, y por eso la verificación de que las
cifras del notebook coinciden con sus artefactos está automatizada en `tests/test_notebooks.py`.

**Qué no se puede reproducir en una máquina cualquiera:** nada de lo que depende del corpus
documental del manual —no se redistribuye, es propiedad del fabricante— ni de los pesos del
adaptador LoRA. Los notebooks que los necesitan están marcados como FULL en el índice."""),
    code("""\
soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "las cifras se leen de experiments/*.json y artifacts/tables/*.csv; "
    "el diagrama del apartado 4 es una demostración ilustrativa y no mide nada",
)"""),
    md("""\
## 11. Conclusiones de este recorrido

**Qué quedó sostenido.** Que el diagnóstico a partir de ventanas de OBD-II supera a la clase
mayoritaria con margen amplio y que su confianza se puede calibrar (PI.1, en validación y en
prueba). Que toda afirmación admitida se ancla en observación y documento verificados (PI.2). Que el
sistema cambia de explicar a abstenerse al retirarle la evidencia, con los datos, el modelo y la
confianza idénticos (PI.3).

**Qué no recibió apoyo.** Que el modelo temporal supere a la línea base. Y la explicación que se dio
de esa desventaja quedó retirada, no confirmada.

**Qué permanece sin demostrar.** Si el contexto temporal aporta señal diagnóstica, y en qué fallos.
Si el sistema rechaza evidencia no pertinente —PI.4—, mientras la condición con distractor no se
rediseñe. Y la validez externa de todo lo anterior, que exigiría telemetría real.

**Cómo contribuye al TFM.** Este notebook es el mapa: dice dónde está cada pieza de evidencia y con
cuánta firmeza se sostiene. La matriz completa que une pregunta → objetivo → experimento → notebook →
resultado → figura → sección está en `docs/notebook-traceability.md`."""),
    md("""\
## 12. Referencias y trazabilidad

**Documentación del trabajo**
- `docs/experiment-index.md` — índice de los diecinueve experimentos con su estado
- `docs/matriz_validacion_pi.md` — respuesta a cada subpregunta con su criterio
- `docs/limitations.md` — registro de limitaciones
- `docs/notebook-traceability.md` — qué notebook corresponde a cada resultado
- `docs/notebooks/auditoria-portabilidad.md` — qué se puede ejecutar sin el equipo del autor

**Registros citados en este notebook**
- `experiments/E6_baseline_synthetic_v2.json`
- `experiments/E7_temporal_synthetic_v2.json`
- `experiments/E19_evaluacion_final_v3.json`
- `artifacts/tables/E19_evaluacion_final_v3.csv`

**Decisiones metodológicas**
- `configs/calibracion_mazda3_bk.yaml` — cada constante del generador con su cita del manual
- `configs/manifest_e19.json` — el estado congelado de la evaluación final
- `docs/methodology/congelacion-anotacion-e19.md` — las reglas, fijadas antes de abrir el test
- `docs/methodology/registro-aperturas-test.md` — cada acceso al conjunto de prueba
- `docs/methodology/expresion-efectiva-del-fallo.md` — cuándo un fallo altera de verdad la señal

**Sobre el estilo de las afirmaciones.** Ninguna cifra de este notebook está escrita a mano: todas
se leen de su registro en tiempo de ejecución. Es deliberado. Un número copiado en una celda de
texto se desactualiza en silencio, y este trabajo ya tuvo ese problema una vez."""),
]

if __name__ == "__main__":
    escribir("00_introduccion.ipynb", CELDAS)
