"""Construye `05_suficiencia_y_abstencion.ipynb`: E15, las ablaciones y P1."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Suficiencia de la evidencia: cuándo el sistema se niega a explicar

**Notebook** `05_suficiencia_y_abstencion` · **versión** 1.1 · **fecha** 14 de noviembre de 2026

| | |
|---|---|
| **Experimentos** | E15 (criterio de suficiencia), E18 (cuatro ablaciones), **P1** (rediseño de la condición con distractor) |
| **Conjunto** | `synthetic_v2`, partición de validación · 17 casos anotados + 6 ejecuciones de P1 (tres situaciones construidas) |
| **Protocolo** | verificador determinista v2.1, umbral de confianza calibrada 0,79, cobertura mínima 0,80 |
| **Estado** | E15 y E18 cerrados; P1 ejecutado el 13-10-2026 |
| **Modalidad** | visualización de evidencia histórica |
| **Pregunta de investigación** | PI.3 (reconocer la insuficiencia) y PI.4 (rechazar evidencia impertinente) |
| **Evidencia original** | `experiments/E15_suficiencia.json`, `E18_ablacion_A1..A4.json`, `E15_suficiencia_distractor_v2.json` |

---

## En un minuto

- **Pregunta.** Si el sistema reconoce de forma comprobable cuándo no puede sostener una explicación
  (PI.3) y si rechaza evidencia que parece pertinente sin serlo (PI.4).
- **Qué se hace.** Se leen los registros de E15, de las ablaciones de E18 y de P1 (rediseño de la
  condición con distractor); no se recalcula nada.
- **Resultado.** La decisión depende de la evidencia. Sin exigir que el fragmento sostenga lo
  afirmado (ablación `A3`), la falsa confianza pasa de 0 de 9 a **6 de 9**; con la confianza sola
  (`A4`), a 9 de 9. Las seis ejecuciones de P1 (tres situaciones construidas) se abstienen por
  cobertura de afirmaciones insuficiente, ninguna por baja confianza.
- **Límite.** Tres y cinco ventanas independientes, un vehículo, telemetría sintética y un criterio
  ajustado sobre los casos que lo miden. El texto puede llevar cifras que el verificador no produjo
  (limitación `L-26`); el adaptador se ajustó sobre tres de las cinco ventanas que lo miden (`L-23`).

## Cómo leer este notebook

**Modalidad:** visualización de evidencia histórica; lee lo que la medición dejó escrito y no
recalcula nada. **Ejecución:** CPU, sin red, segundos.

- **1–4.** Problema, hipótesis y criterio de suficiencia; entorno, modalidad y carga de los registros.
- **5.** La recuperación de E12.
- **6–7.** PI.3: el par mínimo y la condición parcial.
- **8–9.** Las cuatro ablaciones; P1 y PI.4.
- **10–11.** Cifras alteradas y contaminación del redactor.
- **12–13.** El compromiso entre errores y el barrido del umbral.
- **14–18.** Resultados negativos y limitaciones, conclusiones, cuestiones abiertas, reproducibilidad
  y trazabilidad."""),
    md("""\
## 1. Introducción: dos textos indistinguibles

Dos informes de diagnóstico pueden ser igual de convincentes y solo uno estar sostenido. El que lo
está cita un procedimiento del manual que habla de la señal observada; el otro cita un documento que
existe, que resuelve, que es del vehículo correcto y que **no dice nada** sobre lo que se afirma. En
el papel se parecen tanto que la diferencia no se ve leyendo.

Esa es la razón por la que la decisión de explicar o abstenerse **no la toma el modelo de lenguaje**.
Si la tomara él, la respuesta a la pregunta de investigación dependería de su disposición a admitir
que no sabe algo. Y eso no cabe darlo por supuesto.

Lo que no sabemos antes de mirar los registros:

1. **Si la decisión depende de verdad de la evidencia** o si la gobierna la confianza del modelo.
2. **Qué componente hace el trabajo.** Un criterio con cuatro condiciones puede estar sostenido por
   una sola.
3. **Si el sistema distingue evidencia pertinente de evidencia que lo parece.** Hasta el 13 de
   octubre de 2026 esto no se sabía, porque la condición que debía medirlo no medía lo que decía."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Caracterizar cuándo el sistema explica y cuándo se abstiene; atribuir ese
comportamiento a los componentes que lo producen.

**Hipótesis de PI.3.** Si se retira o se degrada la evidencia documental dejando todo lo demás
igual, la decisión pasa de explicar a abstenerse.

**Hipótesis de PI.4.** Si la evidencia disponible es plausible pero de alcance equivocado, el
sistema se abstiene **por insuficiencia de la evidencia** y no por falta de confianza en el
diagnóstico.

**Variables observadas.** Decisión, motivo registrado, confianza calibrada, documentos aplicables y
cobertura de afirmaciones.

**Criterio, fijado antes de medir.** Para PI.3, que las decisiones de las condiciones con evidencia
retirada o parcial sean `ABSTAIN`. Para PI.4, que las tres del distractor sean `ABSTAIN` **y que el
motivo no sea la baja confianza**: si el sistema se abstuviera por confianza, la condición habría
medido otra vez la puerta de confianza y no el rechazo de evidencia impertinente.

**Qué lo cuestionaría.** Para PI.3, que la decisión no cambiara al retirar la evidencia. Para PI.4,
que el informe citara el distractor como respaldo."""),
    md("""\
## 3. Fundamento: qué es suficiente, escrito antes de implementarlo

El criterio tiene cuatro condiciones y todas deben cumplirse. Es una conjunción y no una puntuación
agregada, para que el motivo de cada abstención sea legible.

| Condición | Umbral | Qué protege |
|---|---|---|
| Confianza calibrada del diagnóstico | ≥ 0,79 | que no se explique un diagnóstico del que el modelo no está seguro |
| Fragmentos de soporte | ≥ 2 | que una sola coincidencia no sostenga una explicación |
| Fuentes distintas | ≥ 1 | procedencia |
| **Cobertura de afirmaciones** | ≥ 0,80 | que la evidencia hable de **lo que se afirma** |

**La cuarta es la que importa y la que costó tres versiones.** Un fragmento puede existir,
resolver, pertenecer al vehículo correcto, tener buena puntuación **y no decir nada** sobre la
afirmación que lo cita. La primera versión del criterio aceptaba como soporte cualquier fragmento
que compartiera vocabulario con la afirmación y explicó 6 de los 12 casos que debían terminar en
abstención. Es el fallo más difícil de ver, porque el texto resultante parece impecable.

Un fragmento sostiene una afirmación solo si menciona la señal con el vocabulario del manual (“short
term fuel trim”, no `stft_bank1`), es contenido diagnóstico (no una descripción de funcionamiento)
y porta un código de avería de la condición diagnosticada.

**Por qué la confianza va calibrada.** El bosque estaba **infraconfiado**: error de calibración
0,144, confianza media 0,738 frente a un acierto de 0,878. Un umbral sobre la confianza cruda habría
hecho que el sistema se abstuviera de más. **Habría parecido prudencia cuando era mala
medición**.

**Versión del verificador.** Este notebook usa la v2.1, la de validación. E19 usó la v2.2, que solo
añade una regla: si el diagnóstico está declarado sin códigos que lo documenten (el motor sano),
ningún fragmento cuenta como soporte. Sobre los diecisiete casos de E15 da las mismas decisiones
(`E15_suficiencia_v2_2.json`); donde cambia algo es en el modo adverso (apartado 14.1)."""),
    md("""\
## 4. Preparación del entorno y procedencia de la evidencia

Todo lo que se muestra sale de artefactos **versionados** y ninguno se recalcula:

| Artefacto | Qué contiene | Ejecutado |
|---|---|---|
| `E15_suficiencia.json` · `.csv` | las 17 decisiones del criterio canónico | 13-09-2026 (RERUN-A, reejecución tras corregir la mezcla de espacios de embeddings) |
| `E18_ablacion_A1.csv` … `A4.csv` | las cuatro ablaciones, pre-registradas | 1-10-2026 |
| `E15_suficiencia_distractor_v2.csv` | las 6 ejecuciones de P1 | 13-10-2026 |

Los registros JSON **sí** viajan con el repositorio; los conjuntos de datos, no. Al notebook le
bastan los registros, que son la evidencia de cada cifra publicada."""),
    code(PREAMBULO),
    code("""\
# MODALIDAD. Las cuatro posibles están en `soporte.MODALIDADES`; declarar una
# inventada falla a propósito.
modalidad = soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "Se leen los registros de E15, E18 y P1 y se muestran. Ninguna decisión se recalcula: "
    "el recorrido completo exige el índice documental, que no se distribuye. "
    "Lo que aquí se ve son las cifras publicadas, no una reproducción de ellas.",
)"""),
    md("""\
Se comprueba que los artefactos están y que dicen lo que se espera. Si faltara uno,
el notebook falla con un mensaje que explica qué falta y por qué, en lugar de seguir con una tabla
vacía."""),
    code("""\
import pandas as pd

e15 = soporte.tabla("E15_suficiencia")
p1 = soporte.tabla("E15_suficiencia_distractor_v2")
ablaciones = {
    nombre: soporte.tabla(f"E18_ablacion_{nombre}") for nombre in ("A1", "A2", "A3", "A4")
}

print(f"E15: {len(e15)} casos · P1: {len(p1)} ejecuciones")
print(f"ablaciones: {', '.join(f'{k} ({len(v)} casos)' for k, v in ablaciones.items())}")
print()
print("condiciones de corpus en E15:")
print(e15.corpus_variant.value_counts().to_string())"""),
    md("""\
## 5. De dónde sale la evidencia: la recuperación de E12

La suficiencia se decide sobre los documentos que el agente **recibe**, que elige la fase de
recuperación medida en E12. Para evaluar si el criterio rechaza evidencia insuficiente hay que saber
antes si la evidencia pertinente llega a estar disponible; por eso E12 va antes de usar su salida.

Se mide si el procedimiento relevante del manual aparece entre los documentos recuperados con dos
estrategias de consulta: la **semántica pura** (que busca con el texto de la pregunta) y la **guiada
por el diagnóstico**, que acota la búsqueda con el código de avería y la señal observada. El registro
de E12 sobre el corpus del vehículo de referencia tiene seis casos, cinco de ellos puntuados (uno no
tiene procedimiento aplicable en el manual). Para cada caso se mira si el procedimiento correcto está
entre los diez primeros resultados y se calculan MRR, nDCG y precisión. Las cifras se leen del
registro sin reejecutar la recuperación."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_recuperacion

fig = fig_recuperacion()
# Rótulos añadidos en el notebook; los datos son los de la función.
fig.axes[0].set_title("(a) Casos con el procedimiento entre los 10 primeros (de 5)",
                      fontsize=9, fontweight="bold", loc="left", pad=6)
fig.axes[1].set_title("(b) Métricas de ordenación sobre los 5 casos puntuados",
                      fontsize=9, fontweight="bold", loc="left", pad=6)
fig.tight_layout()
fig.suptitle(
    "E12: recuperación del procedimiento del manual según la estrategia de consulta",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
soporte.exportar(fig, "FIG-NB05-01_recuperacion", subdirectorio="05_suficiencia_y_abstencion")
fig"""),
    md("""\
**Qué muestra.** La recuperación semántica pura encuentra el procedimiento en **cero** de los cinco
casos puntuados. La guiada por el diagnóstico lo encuentra en **cinco de cinco**. Las tres métricas
de ordenación acompañan ese salto.

**Qué podemos interpretar.** Que la consulta en prosa no basta sobre un manual de taller: sus
procedimientos están indexados por código de avería y por componente, no por la descripción que un
usuario haría del síntoma. El diagnóstico no sirve aquí solo para decidir qué decir, sino para
**acotar dónde buscar**. Esa es la aportación concreta a PI.2 (la trazabilidad de la explicación).

**Qué no podemos afirmar.** Que la ventaja se generalice. Son **cinco casos puntuados** sobre un
único manual y un único vehículo: los recuentos se publican como recuentos y no como tasas. No
hay intervalo porque no hay muestra de la que estimarlo. Tampoco se afirma que la ruta semántica sea
mala en general, solo **con esta consulta y este corpus**. La ablación `A2` (búsqueda solo léxica,
apartado 8) quedó inconclusa por confundir las dos cosas.

**Relación con la pregunta de investigación.** Es la medición de PI.2: la trazabilidad de una explicación depende de
que el documento que la respalda llegue a estar entre los recuperados. Aquí se ve con qué
estrategia llega y con cuál no."""),
    md("""\
## 6. El experimento central, reducido a dos filas

Para mostrar PI.3 bastan dos de los diecisiete casos. Mismos datos, mismo modelo,
misma atribución, **misma confianza**. Lo único que cambia es que se retira del índice la evidencia
documental."""),
    code("""\
columnas = [
    "case_id_gold",
    "corpus_variant",
    "confidence",
    "n_documents_applicable",
    "claim_coverage",
    "decision",
    "reasons",
]
nucleo = e15[e15.case_id_gold.isin(["C05_vacuum_leak", "C06_vacuum_leak_evidencia_retirada"])]
print(nucleo[columnas].to_string(index=False))"""),
    md("""\
**Qué muestra.** Dos ejecuciones sobre **la misma ventana de telemetría**, con la misma confianza
calibrada (0,908) y decisiones opuestas. En la primera hay documentos aplicables y la cobertura de
afirmaciones es 1,00; en la segunda, con la evidencia retirada del índice, no queda ninguno y la cobertura es 0,00.

**Qué podemos interpretar.** Que la decisión **cambió porque cambió la evidencia**, no porque
cambiara el vehículo ni la certeza del modelo. Es la hipótesis de PI.3 reducida a su mínima
expresión y se cumple.

**Qué no podemos afirmar.** Que esto demuestre un comportamiento general. Son dos ejecuciones sobre
una ventana. Y hay algo más débil de lo que parece. La abstención de la segunda fila está
**determinada por la construcción de la condición**: se retiraron del índice todos los fragmentos
con los códigos del fallo, así que no quedaba nada que juzgar. No pone a prueba el criterio de
soporte; solo comprueba que el sistema no explica sin evidencia. **La condición informativa es la
parcial**, la del apartado siguiente."""),
    md("""\
## 7. La condición informativa: hay documentos y aun así se abstiene

Una tasa de abstención confunde dos situaciones: que no haya documentos o que los haya y no cubran
lo que se quiere afirmar. Solo la segunda demuestra que el criterio mide suficiencia y no
disponibilidad.

Para separarlas se toman los diecisiete casos de E15 bajo las cinco condiciones de evidencia, con dos
magnitudes registradas por caso: cuántos documentos **aplicables** se recuperaron y qué **cobertura
de afirmaciones** alcanzó el verificador. No se recalcula ninguna decisión."""),
    code("""\
informativas = e15[e15.corpus_variant.isin(["PARTIAL", "ABSENT", "FULL"])]
resumen = (
    informativas.groupby("corpus_variant")
    .agg(
        casos=("decision", "size"),
        explica=("decision", lambda s: int((s == "EXPLAIN").sum())),
        se_abstiene=("decision", lambda s: int((s == "ABSTAIN").sum())),
        docs_aplicables_medios=("n_documents_applicable", "mean"),
        cobertura_media=("claim_coverage", "mean"),
    )
    .reindex(["FULL", "PARTIAL", "ABSENT"])
)
print(resumen.round(2).to_string())"""),
    code("""\
fig, ejes = soporte.lienzo(
    experimento="E15 · verificador v2.1",
    dataset="synthetic_v2, validación · los 17 casos anotados, en sus 5 condiciones",
    procedencia="artifacts/tables/E15_suficiencia.csv",
    titulo="Documentos aplicables frente a cobertura de afirmaciones, por condición de evidencia",
    filas=2,
    ancho=5.9,
    alto=3.2,
    para_la_memoria=True,
)

# Las CINCO condiciones del conjunto. Hasta el 13-10-2026 esta lista tenía
# cuatro y dejaba fuera DISTRACTOR_NO_FILTER, de modo que la figura dibujaba 14
# de los 17 casos mientras su pie declaraba los diecisiete.
orden = ["FULL", "PARTIAL", "ABSENT", "DISTRACTOR", "DISTRACTOR_NO_FILTER"]
etiquetas_x = ["FULL", "PARTIAL", "ABSENT", "DISTRACTOR", "DISTRACTOR\\nSIN FILTRO"]
colores = {"EXPLAIN": "#1b6b4a", "ABSTAIN": "#9c4221"}

for letra, (eje, (columna, etiqueta, unidad)) in zip(
    "ab",
    zip(
    ejes,
    [
        ("n_documents_applicable", "Documentos aplicables", "nº de fragmentos"),
        ("claim_coverage", "Cobertura de afirmaciones", "fracción de 0 a 1"),
    ],
    strict=True,
),
    strict=False,
):
    for i, condicion in enumerate(orden):
        sub = e15[e15.corpus_variant == condicion]
        for _, fila in sub.iterrows():
            eje.scatter(
                i + (hash(fila.case_id_gold) % 7 - 3) * 0.035,
                fila[columna],
                color=colores[fila.decision],
                s=42,
                alpha=0.85,
                edgecolor="white",
                linewidth=0.6,
            )
    eje.set_xticks(range(len(orden)))
    eje.set_xticklabels(etiquetas_x, fontsize=7.5)
    eje.set_xlabel("Condición de evidencia")
    eje.set_ylabel(f"{etiqueta} ({unidad})")
    eje.set_title(f"({letra}) {etiqueta} por condición de evidencia", fontsize=9,
                  fontweight="bold", loc="left", pad=6)

dibujados = int(e15.corpus_variant.isin(orden).sum())
assert dibujados == len(e15), f"la figura dibuja {dibujados} de {len(e15)} casos"
print(f"condiciones dibujadas: {len(orden)} · casos dibujados: {dibujados} de {len(e15)}")

from matplotlib.lines import Line2D

ejes[1].legend(
    handles=[
        Line2D([], [], marker="o", color="none", markerfacecolor=c, markersize=7, label=d)
        for d, c in colores.items()
    ],
    title="Decisión",
    fontsize=7,
    title_fontsize=7,
    loc="center right",
)
fig.suptitle(
    "E15 sobre validación: fragmentos aplicables y cobertura de los 17 casos",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.01,
    "Cada punto es un caso; dentro de cada condición se desplazan a los lados para que no se "
    "tapen. Color: decisión del sistema.",
    fontsize=6.5, ha="left", va="top",
)
destino = soporte.exportar(
    fig, "FIG-NB05-02_aplicables_vs_cobertura", subdirectorio="05_suficiencia_y_abstencion"
)
# Se imprime la ruta RELATIVA a la raíz: la absoluta sería la de esta máquina,
# y el HTML que se entrega la llevaría dentro.
print(f"figura exportada en PNG y SVG: {destino.relative_to(soporte.raiz())}")"""),
    md("""\
**Qué muestra.** A la izquierda, cuántos fragmentos **aplicables** (vehículo correcto, código
correcto) llegan al verificador en cada condición. A la derecha, qué fracción de las afirmaciones
construidas queda **sostenida** por ellos. El color es la decisión.

Las dos columnas no se parecen. En la condición parcial hay
fragmentos aplicables (cinco, seis y siete) y la cobertura es **cero** en los tres casos. Con el
distractor y el filtro de motor activo, los mismos tres recuentos y la misma cobertura cero; sin el
filtro, entran fragmentos de otro motor y el recuento **baja** a tres, cuatro y tres, porque el
validador de aplicabilidad los degrada a coincidencia parcial y dejan de contar como aplicables. La
cobertura sigue siendo cero. Solo la condición completa alcanza cobertura 1,00, en cuatro de sus
cinco casos; uno de ellos, `C01_maf_drift`, se abstiene igualmente por confianza (0,600).

**Qué podemos interpretar.** Que **tener documentación aplicable delante no equivale a tener
soporte**. Las dos magnitudes se separan en la condición que el diseño construyó para
separarlas. La decisión sigue a la cobertura y no al recuento de documentos.

**Qué no podemos afirmar.** Que la cobertura sea un buen estimador de nada fuera de estos casos. Y
hay un límite más serio: que las comprobaciones deterministas de soporte coincidan con lo que un
fragmento sostiene **de verdad** no se ha medido. Haría falta anotar, caso a caso, qué afirmaciones
son admisibles y qué evidencia es mínima exigible; el conjunto anotado no tiene esa anotación. Lo
que está comprobado es que ninguna cita se asigna fuera de esas comprobaciones, que es menos.

> **Corrección del 13 de octubre de 2026.** Esta figura dibujaba cuatro de las cinco condiciones
> (dejaba fuera `DISTRACTOR_NO_FILTER`, el distractor sin filtro de motor) y su pie declaraba los diecisiete casos: mostraba catorce.
> Ninguna conclusión cambiaba, porque los tres omitidos se abstienen con cobertura cero, pero la
> condición que faltaba es la única en la que entran fragmentos de otro motor. La celda
> comprueba ahora, antes de exportar, que no falte ningún caso."""),
    md("""\
## 8. Qué componente hace el trabajo: las cuatro ablaciones

Falta saber **qué componente** del recorrido sostiene la ausencia de falsa confianza: el criterio
compuesto de suficiencia, la puerta de confianza sola, la atribución o la ruta de recuperación.

Se comparan los diecisiete casos de E15 bajo la configuración canónica y bajo las cuatro ablaciones
(`A1` a `A4`), pre-registradas el 1 de octubre de 2026 antes de ejecutarse. Cada ablación cambia
**una** pieza y deja el resto idéntico. Ninguna redacta: miden la decisión y la evidencia, no el
texto. Los dos errores se cuentan por separado sobre sus propios denominadores, en ejecuciones y
ventanas y nunca como una tasa única (los casos no son independientes; véase el apartado 14.2)."""),
    code("""\
def tasas(registro: dict) -> dict[str, str]:
    \"\"\"Los dos errores y la cobertura, leídos del resumen del registro; no se recuentan.

    La falsa confianza deja fuera la condición con distractor y filtro: su
    configuración era idéntica a la parcial (el registro la da aparte, en
    `including_distractor_with_filter`). La cobertura es el campo
    `coverage_full_evidence`: casos con evidencia completa que el sistema explica.
    \"\"\"
    resumen = registro["summary"]
    return {
        columna: f"{resumen[campo]['numerator']} de {resumen[campo]['denominator']}"
        for columna, campo in (
            ("falsa_confianza", "false_confidence"),
            ("abstencion_innecesaria", "unnecessary_abstention"),
            ("cobertura_con_evidencia_completa", "coverage_full_evidence"),
        )
    }


nombres = {
    "A1": "sin atribución: observaciones por desviación tipificada",
    "A2": "sin recuperación semántica: solo búsqueda léxica",
    "A3": "sin criterio de suficiencia: explicar si hay fragmento aplicable",
    "A4": "umbral único: solo confianza calibrada",
}
filas = []
for clave in ablaciones:
    registro_ablacion = soporte.registro(f"E18_ablacion_{clave}")
    filas.append({"ablación": clave, "qué cambia": nombres[clave], **tasas(registro_ablacion)})
print(pd.DataFrame(filas).to_string(index=False))"""),
    md("""\
**Qué muestra.** `A4`, que deja solo la puerta de confianza, explica **las nueve ejecuciones que
debían terminar en abstención**, incluidas las tres en que la recuperación no devuelve ningún
fragmento. `A3`, que exige que exista algún fragmento aplicable pero no que lo sostenga, baja a seis
de nueve. `A1`, que sustituye la atribución por un criterio estadístico simple, no cambia ninguna
decisión.

**Qué podemos interpretar.** El nueve de nueve de `A4` es una comprobación esperable: una puerta
de confianza sola ignora la evidencia y estos casos están bien clasificados con confianza alta. La
ablación informativa es `A3`. Lo que las dos muestran se enuncia mejor al revés de como
suele pensarse un sistema de diagnóstico: **una confianza diagnóstica alta no basta para sostener
una explicación si la evidencia documental no la sostiene**. La confianza del modelo mide cuán
seguro está de su diagnóstico y no sabe nada de si el manual lo documenta.

**Qué no podemos afirmar.** Nada sobre la separación entre decidir y redactar, que no se ablaciona.
Y nada que no esté condicionado por que **las cuatro se miden sobre el conjunto con el que el
criterio se ajustó**. `A2` quedó además **inconclusa**. La ruta léxica no recuperó nada en ningún
caso por la consulta y no por la ablación: una búsqueda de texto completo con treinta palabras unidas
por conjunción. Se conserva como inconclusa en lugar de reformularse a posteriori.

La figura siguiente pone los dos errores lado a lado, configuración a configuración, para ver qué
componente sostiene el resultado y cuál es sustituible."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_ablaciones

fig = fig_ablaciones()
arriba, abajo = fig.axes
arriba.set_title("(a) Falsa confianza: explicó cuando debía abstenerse",
                 fontsize=9, fontweight="bold", loc="left", pad=6)
abajo.set_title("(b) Abstención innecesaria: se abstuvo cuando debía explicar",
                fontsize=9, fontweight="bold", loc="left", pad=6)
arriba.tick_params(labelbottom=True)
from matplotlib.patches import Patch

abajo.get_legend().remove()
abajo.legend(
    handles=[
        Patch(color="#c3c2b7", label="ejecuciones evaluadas"),
        Patch(color=arriba.patches[-1].get_facecolor(), label="falsa confianza"),
        Patch(color=abajo.patches[-1].get_facecolor(), label="abstención innecesaria"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=3, fontsize=7, frameon=False,
)
fig.tight_layout()
fig.suptitle(
    "E15 y E18 sobre validación: los dos errores de la configuración canónica y de cada ablación",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
soporte.exportar(fig, "FIG-NB05-03_ablaciones", subdirectorio="05_suficiencia_y_abstencion")
fig"""),
    md("""\
**Qué muestra.** La configuración canónica no produce ninguna falsa confianza (0 de 9 ejecuciones) y
se abstiene de más en 2 de 5. Al sustituir el criterio compuesto por una puerta de confianza sola,
la falsa confianza pasa a **9 de 9**. Retirar la atribución no cambia ninguna de las dos cifras.
`A2` quedó inconclusa: la ruta léxica no recuperó nada por la consulta, no por la ablación.

**Qué podemos interpretar.** Lo que evita la falsa confianza es la **comprobación de que la
evidencia documental cubre lo que se va a afirmar**, no la confianza del modelo de diagnóstico ni la
atribución. La atribución entra en el informe como explicación, no como barrera.

**Qué no podemos afirmar.** Que la atribución sea prescindible: no interviene en la abstención,
pero sí en la trazabilidad (qué señal y qué ventana sostienen cada afirmación), que aquí no se evalúa. Y los denominadores
son 9 y 5 **ejecuciones** procedentes de 3 y 5 ventanas: no son tasas estimadas.

**Relación con la pregunta de investigación.** Es la prueba de atribución de PI.3: el resultado se debe al criterio
de suficiencia declarado y no al conjunto del sistema indistintamente."""),
    md("""\
## 9. P1: evidencia que parece pertinente y no lo es

Hasta el 13 de octubre de 2026 la pregunta PI.4 **no tenía respuesta interpretable**. No faltaba
medición; la condición que debía medirla no medía lo que decía. El diagnóstico escrito en
septiembre culpaba al filtro de motor; al comprobarlo, la causa resultó ser otra y más simple.
**Dos de las tres condiciones con distractor tenían la misma configuración que las
parciales correspondientes.** El único campo que difería no lo lee el recorrido de suficiencia.

El rediseño construye la condición por **exclusión diferencial**: la parcial excluye el
procedimiento de diagnóstico **y** los documentos de alcance equivocado; la del distractor excluye
**solo** el procedimiento. La diferencia entre las dos es el documento que se quiere
poner a prueba.

Los distractores son del motor correcto y llevan el código del fallo: un esquema de cableado del
sistema de control, un modo de prueba de diagnóstico, un autodiagnóstico KOEO/KOER (con llave en contacto, motor parado o en marcha). Su razón de
insuficiencia se declaró **antes** de medir: **alcance equivocado**. Un esquema es un plano, no un
procedimiento de diagnóstico."""),
    code("""\
columnas_p1 = [
    "case_id_gold",
    "corpus_variant",
    "confidence",
    "n_documents_applicable",
    "claim_coverage",
    "decision",
    "reasons",
]
print(p1[columnas_p1].to_string(index=False))
print()
print(f"decisiones correctas: {int(p1.correct.sum())} de {len(p1)}")
print(f"motivos registrados:  {sorted(set(p1.reasons.dropna()))}")
print(f"confianzas:           {sorted(set(p1.confidence.round(3)))}  (umbral 0,79)")"""),
    md("""\
**Qué muestra.** Seis abstenciones de seis. Y el dato que decide la lectura: el motivo registrado en
las seis es `LOW_CLAIM_COVERAGE` (la evidencia no sostiene ninguna afirmación) y **ninguna** es
`LOW_MODEL_CONFIDENCE`. Las confianzas son 0,908 y 1,000, **por encima** del umbral de 0,79.

**Qué podemos interpretar.** Que la puerta de confianza **no intervino**: el rechazo lo hizo la
verificación de soporte. Era la condición que el protocolo fijó de antemano para que el resultado
apoyara PI.4. Se cumple en las tres situaciones construidas, sin que eso estime ninguna tasa. Y con una
salvedad: la parcial y la del distractor dan el mismo resultado observable, abstención con cobertura
0,0. Lo que las distingue no se ve en la decisión, sino en que el distractor estaba entre los
fragmentos aplicables y aun así no sostuvo ninguna afirmación.

El distractor, además, llega al verificador clasificado **`EXACT_MATCH`** (plenamente aplicable). El filtro
de motor no lo bloquea (es del motor correcto) y el validador de aplicabilidad no lo degrada (lleva
el código del fallo). De los documentos aplicables, uno de cinco, tres de siete y uno de seis eran
distractores. **Las dos primeras líneas de defensa no actúan**: lo que rechaza es que el fragmento
no habla de la señal observada con el vocabulario del manual.

**Qué no podemos afirmar.** Que exista una tasa de rechazo. Son **tres** situaciones construidas por
el autor, con `n = 3`, en un vehículo, sobre un corpus: no estiman ninguna probabilidad. Tampoco que
el espacio de distractores alcanzables esté cubierto: para la sonda lambda solo se encontró **uno**
y así se declaró."""),
    md("""\
## 10. Un hallazgo que no se buscaba: una cifra falsa que todas las barreras dejan pasar

Al revisar lo que el modelo de lenguaje redactó en los casos de P1, apareció esto:

```
verificador:  "cobertura 0.00 < 0.80"
redactor:     "cobertura 0.908 < 0.80"
```

La frase del redactor es **internamente falsa**: 0,908 no es menor que 0,80. El número que escribió
es la confianza calibrada, no la cobertura. Y las tres barreras del trabajo la dejaron pasar: esquema
válido, veredicto respetado, cero citas inventadas.

Al auditar los registros ya publicados, no es un caso aislado **ni es nuevo**."""),
    code("""\
import json
import re

DECIMAL = re.compile(r"\\d+\\.\\d+")


def cifras(valor):
    texto = " ".join(valor) if isinstance(valor, list) else str(valor or "")
    return {str(float(x)) for x in DECIMAL.findall(texto)}


pares = [
    ("E15_suficiencia", "E13_agente_transformers", "modelo base, sin adaptador"),
    ("E15_suficiencia", "E13_agente_transformers-lora", "adaptador v1"),
    ("E15_suficiencia", "E13_agente_transformers-lora@slm_lora_v2", "adaptador v2, el canónico"),
]
for suf_nombre, ag_nombre, etiqueta in pares:
    suf = soporte.registro(suf_nombre)
    ag = soporte.registro(ag_nombre)
    por_gold = {c["case_id"]: c for c in suf["cases"]}
    alteradas = []
    for run in ag["runs"]:
        caso = por_gold.get(run.get("gold_case_id"))
        if caso is None:
            continue
        extra = cifras((run.get("output") or {}).get("missing_evidence")) - cifras(
            caso["verdict"].get("missing_evidence")
        )
        if extra:
            alteradas.append(run["gold_case_id"])
    print(f"{etiqueta:28} {len(ag['runs']):3} casos · cifras alteradas en {len(alteradas)}")
    for caso in alteradas:
        print(f"    {caso}")"""),
    md("""\
**Qué muestra.** Al menos tres de las diecisiete salidas de la configuración canónica (la que
sostiene el “17/17 válidas · 17/17 respeta el veredicto · 0 citas inventadas” publicado) contienen un
número que el verificador no produjo. El modelo base, sin adaptador, no presenta ninguna.

Esta celda compara, caso a caso, el conjunto de números de los motivos de abstención con el de los
números recibidos: encuentra tres. El guion `scripts/auditar_cifras_redactadas.py`, que mira también
las afirmaciones y agrupa por caso, encuentra **cuatro** de diecisiete (añade `C03_o2_slow_response`)
y una más entre las seis ejecuciones de P1. Alineando cada motivo con su motivo aparece una quinta:
`C04_misfire` escribe “confianza 0.462 < 0.80” cuando el umbral es 0,79. La comparación por
conjuntos no lo ve porque el 0,80 figura en el otro motivo, el de cobertura. De ahí las **seis de
veintitrés** del apartado de limitaciones: cinco de diecisiete más una de seis en P1. Es la misma
diferencia de agrupación que separa el siete y el nueve de E19 (notebook `03_analisis_e19`).

**Qué podemos interpretar.** Que una salida puede ser **trazable en sus citas y falsa en sus
cifras**. Las barreras comprueban que el identificador citado se entregara; **ninguna comprueba que
el número dicho sea cierto**. Es un hueco en la trazabilidad (PI.2) que no estaba declarado y
afecta a la parte del texto que un lector usaría para juzgar la decisión.

**Qué no podemos afirmar.** Que el ajuste empeore la fidelidad numérica. Cero de diecisiete frente
a entre tres y cinco de diecisiete es sugerente y con diecisiete casos es compatible con el azar
del muestreo.
Tampoco se corrige el recorrido: añadir una barrera ahora sería cambiar el sistema a la vista del
resultado. Queda declarado como limitación `L-26`, con un guion (`scripts/auditar_cifras_redactadas.py`)
para que cualquiera repita la auditoría."""),
    md("""\
## 11. La contaminación del adaptador, que afecta a estas mismas cifras

Las cifras de redacción de este notebook (y las de E13 y E15 que el capítulo 5 publica) están
**afectadas por contaminación**. Hay que tenerlo presente al leerlas.

Los ejemplos con que se ajustó el adaptador `slm_lora_v2` se generaron desde la **partición de
validación**, que es donde se mide la calidad de redacción. El reparto por sesión se diseñó para el
modelo de diagnóstico (entrenamiento para ajustar, validación para medir) y cuando se añadió el redactor, sus ejemplos se tomaron de donde había
predicciones correctas y evidencia ya montada, sin reparar en que esa partición era también donde se
le iba a medir."""),
    code("""\
# Medido contra los ficheros de ajuste y el registro del agente. Los identificadores
# de ventana están registrados en la congelación del conjunto independiente, de modo
# que esto se puede comprobar en un clon sin los ficheros de ajuste.
congelacion = json.loads(
    (soporte.raiz() / "configs" / "evaluacion-independiente-redactor.json").read_text("utf-8")
)
entradas = congelacion["entradas_de_la_regla"]
ajuste = set(entradas["ventanas_de_ajuste_de_slm_lora_v2"])
evaluacion = set(entradas["ventanas_de_evaluacion_de_E15"])

agente = soporte.registro("E13_agente_transformers-lora@slm_lora_v2")
vistos = [r for r in agente["runs"] if r["case_id"] in ajuste]

print(f"ventanas con que se ajustó el adaptador : {len(ajuste)}")
print(f"ventanas de la evaluación de E15        : {len(evaluacion)}")
print(f"solape de ventanas                      : {len(ajuste & evaluacion)} de {len(evaluacion)}")
print()
print(f"casos de E13 sobre ventanas vistas      : {len(vistos)} de {len(agente['runs'])}")
print(f"casos sobre ventanas NO vistas          : {len(agente['runs']) - len(vistos)}")
print(f"ventanas distintas en los no vistos     : "
      f"{len({r['case_id'] for r in agente['runs'] if r['case_id'] not in ajuste})}")
print()
for subconjunto, nombre in ((vistos, "vistos"), (
    [r for r in agente["runs"] if r["case_id"] not in ajuste], "no vistos")):
    validas = sum(1 for r in subconjunto if r["valid"])
    respetan = sum(1 for r in subconjunto if r["respected_verdict"])
    inventadas = sum(len(r["fake_citations"]) for r in subconjunto)
    print(f"  {nombre:10} n={len(subconjunto):2} · válidas {validas} · "
          f"respetan {respetan} · citas inventadas {inventadas}")"""),
    md("""\
**Qué muestra.** Tres de las cinco ventanas de evaluación de E15 son **las mismas** con que el
adaptador se ajustó; al nivel del caso son **once de los diecisiete**. El resultado no cambia entre
los dos subconjuntos: el adaptador redacta igual de bien sobre lo que vio y sobre lo que no.

**Qué podemos interpretar.** Solo que no se observa degradación en el subconjunto no visto. Los seis casos limpios cubren **dos** ventanas distintas. Cinco de los seis son el mismo
paquete de evidencia bajo cinco condiciones de corpus: las observaciones que el redactor recibe son
casi las mismas. Lo que de verdad hay son **dos** situaciones no vistas, no seis.

**Qué no podemos afirmar.** Que las cifras de redacción de E13 y E15 estimen cómo redacta el sistema
ante evidencia nueva; por eso se conservan marcadas como históricas afectadas por
contaminación y no como evidencia canónica de generalización. Corregirlo exige reentrenar el
adaptador. Ese reentrenamiento está preparado, congelado y detenido por memoria insuficiente
(`docs/experiments/incidencia-p2-02.md`). El conjunto sobre el que se medirá el adaptador nuevo
(quince ventanas de validación de `synthetic_v3` que ninguno de los dos ha visto) está congelado desde
el 13 de octubre de 2026 y **sin ejecutar**."""),
    md("""\
## 12. El compromiso entre los dos errores

Hasta aquí los dos errores se han contado por separado, pero forman un **compromiso**. Callar menos
explica más casos y acerca la falsa confianza; callar más la aleja y deja sin explicar casos que
podían explicarse. El umbral elige un punto de esa curva.

La figura toma las decisiones registradas de los diecisiete casos de E15 bajo el criterio vigente,
separando los que debían explicarse de los que debían callarse. No se recalcula ninguna política."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_compromiso

fig = fig_compromiso()
fig.suptitle(
    "E15 sobre validación: falsa confianza frente a abstención innecesaria de tres políticas",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
fig.text(
    0.01, -0.005,
    "Falsa confianza sobre las 9 ejecuciones que debían abstenerse; abstención innecesaria "
    "sobre las 5 que debían explicar. Abajo a la izquierda, ningún error.",
    fontsize=6.5, ha="left", va="top",
)
soporte.exportar(fig, "FIG-NB05-04_compromiso", subdirectorio="05_suficiencia_y_abstencion")
fig"""),
    md("""\
**Qué muestra.** Dónde cae la configuración elegida respecto de los dos errores que no se pueden
minimizar a la vez.

**Qué podemos interpretar.** Que el punto elegido es **deliberadamente conservador**: prefiere
callar de más antes que explicar sin evidencia, porque los dos errores no cuestan lo mismo en un
taller. Una explicación equivocada orienta una reparación; una abstención devuelve el caso a la
persona.

**Qué no podemos afirmar.** Que este sea el punto óptimo. Con estos casos (véase el apartado 14.2) no se estima
ninguna curva: lo que se muestra es dónde quedó la configuración, no que otra fuera peor.

**Relación con la pregunta de investigación.** Explicita el precio de PI.3: la ausencia de falsa confianza observada
se compra con abstenciones innecesarias. Ese precio se publica en lugar de esconderse."""),
    md("""\
## 13. Lo que cuesta subir la puerta de confianza

El criterio de suficiencia es compuesto: exige confianza **y** soporte
documental. Esta sección mira solo la mitad de confianza y pregunta qué se gana y qué se pierde al
mover su umbral.

Se lee `experiments/E15b_barrido_umbral.json`, el barrido ejecutado el 4 de
septiembre de 2026 sobre las 98 ventanas de validación de `synthetic_v2`, procedentes de doce
sesiones. El registro guarda 101 umbrales con la cobertura y la precisión de la decisión
diagnóstica en cada uno (**por ventana y por sesión**) y un remuestreo de 1 000 réplicas en los dos
umbrales de la política. El campo `test_used` vale `false`: el conjunto de prueba no interviene."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import compromiso_del_umbral

compromiso = compromiso_del_umbral()
pd.DataFrame(
    [
        {
            "umbral": u,
            "cobertura (ventanas)": round(cv, 4),
            "precisión (ventanas)": round(pv, 4),
            "cobertura (sesiones)": round(cs, 4),
        }
        for u, cv, pv, cs in zip(
            compromiso["umbrales"],
            compromiso["cobertura_ventanas"],
            compromiso["precision_ventanas"],
            compromiso["cobertura_sesiones"],
            strict=True,
        )
        if abs(u - compromiso["umbral_original"]) < 1e-9
        or abs(u - compromiso["umbral_vigente"]) < 1e-9
        or round(u * 100) % 10 == 0
    ]
)"""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_riesgo_cobertura

fig = fig_riesgo_cobertura()
izq, der = fig.axes[:2]
izq.set_title("(a) Cobertura y precisión según el umbral", fontsize=9, fontweight="bold", loc="left", pad=6)
der.set_title("(b) Precisión frente a cobertura", fontsize=9, fontweight="bold", loc="left", pad=6)
fig.tight_layout()
fig.suptitle(
    "E15b sobre validación: qué cuesta subir el umbral de confianza calibrada (98 ventanas)",
    fontsize=9.5, fontweight="bold", x=0.01, y=1.0, ha="left", va="bottom",
)
soporte.exportar(fig, "FIG-NB05-05_riesgo_cobertura", subdirectorio="05_suficiencia_y_abstencion")
fig"""),
    md("""\
**Qué muestra.** Con el umbral vigente, 0,79, la decisión diagnóstica cubre el 82,7 % de las
ventanas con una precisión de 0,938; con el anterior, 0,72, cubre el 87,8 % con 0,930. La enmienda
del umbral costó cinco puntos de cobertura y ganó menos de uno de precisión.

**Qué podemos interpretar.** Dos cosas que la tabla de dos filas no deja ver. La primera: la curva
**no es monótona**. En veintiuno de los cien pasos, subir el umbral **empeora** la precisión; el
caso más marcado está entre 0,91 y 0,92, donde la cobertura cae del 58,2 % al 52,0 % y la precisión
baja de 0,912 a 0,902, porque entre las seis ventanas descartadas hay más aciertos que errores. Un
umbral de confianza no es un dial en el que más siempre sea mejor. La segunda: las barras de
remuestreo de los dos umbrales **se solapan por completo** y llegan las dos hasta 1,0, de modo que
con esta muestra los dos puntos de operación son indistinguibles.

**Qué no podemos afirmar.** Que esto describa **la
política de abstención del agente**: mueve solo la mitad de confianza del criterio compuesto; la
mitad documental permanece fija. Que sea una exploración de la política completa: barrer la
cobertura de afirmaciones exigida pediría una medición que no existe. Que la elección del umbral fuera un
**pre-registro ciego**: el criterio se escribió antes del barrido y después de ver una tabla
anterior de cuatro puntos; el documento que lo fija lo declara. Que las observaciones sean
independientes: 98 ventanas proceden de doce sesiones. Y que de aquí salga un umbral mejor: es
análisis descriptivo posterior, no una validación independiente; el umbral **no se revisa a su
vista**."""),
    md("""\
## 14. Resultados negativos y limitaciones

### 14.1 Resultados negativos e inconclusos

| Qué | Qué pasó | Qué se hizo |
|---|---|---|
| **Primera versión del criterio** | explicó 6 de los 12 casos que debían terminar en abstención: aceptaba como soporte cualquier fragmento que compartiera vocabulario | se corrigió; las tres versiones se conservan con sus registros |
| **Segunda versión** | corrigió ese defecto y **regresionó** la fuga de vacío con evidencia completa | la tercera lo recuperó cambiando solo la granularidad con que se clasifica el papel de un fragmento |
| **Ablación `A2`** | la ruta léxica no recuperó nada en ningún caso, por la consulta y no por la ablación | **inconclusa**, sin reformular a posteriori; la variante queda declarada como medición nueva |
| **Dos abstenciones innecesarias** | `C01` por confianza 0,600 y `C04` por confianza 0,462 **y** cobertura 0,00 | se dejan registradas en lugar de resolverse bajando el umbral |
| **Condición con distractor v1** | no medía lo que decía; el diagnóstico de su causa también era equivocado | invalidada, conservada con su etiqueta y rediseñada en P1 |
| **Modo adverso** | el sistema se abstuvo en las seis ejecuciones; en dos aceptó fragmentos como soporte de afirmaciones de un diagnóstico **erróneo** | queda como limitación: con la política v2.1 se abstuvo por cobertura de afirmaciones 0,67, no por rechazar el soporte; con la v2.2, la de E19, esos dos casos dan 0,00 (`E15_suficiencia_adverse_v2_2.json`) |

### 14.2 Limitaciones

1. **El criterio se revisó dos veces sobre los mismos casos con los que se evalúa.** Las cifras son
   de desarrollo, no de evaluación. La evaluación final sobre la partición de prueba es otra
   medición, con su registro.
2. **Los diecisiete casos salen de cinco ventanas.** No son diecisiete observaciones
   independientes; por eso no se publica ninguna tasa única ni ningún intervalo.
3. **Las ventanas se eligieron entre las que el modelo clasifica bien.** Las tasas describen el
   comportamiento cuando el diagnóstico de partida es acertado: son **cota superior**.
4. **El modo oracular abre dos canales**: los códigos que acotan la búsqueda y los que exige el
   verificador salen de la etiqueta anotada. El modo no oracular da el mismo vector de decisiones;
   esa identidad era forzosa porque las ventanas están bien clasificadas: confirma que la
   implementación no introduce diferencias, no que el sistema resista un diagnóstico erróneo.
5. **`n = 3` en P1.** Tres situaciones construidas, seis ejecuciones.
6. **La fidelidad numérica del texto redactado no está verificada** (`L-26`): seis de las
   veintitrés salidas del adaptador canónico contienen una cifra que no procede de los datos que
   recibió, alineando motivo con motivo; el guion, que agrupa por caso, da cinco (apartado 10).
7. **El adaptador se ajustó sobre tres de las cinco ventanas en que se le midió** (`L-23`): once de
   los diecisiete casos (apartado 11).
8. **Un vehículo, un corpus, telemetría sintética.** Nada de esto dice qué pasaría con otro
   vehículo, otro fabricante o datos de operación real."""),
    md("""\
## 15. Conclusiones

La decisión de explicar o abstenerse **depende de la evidencia** y es auditable sin que intervenga un
generador de texto. Retirar o degradar la evidencia cambia la decisión; tener documentación
aplicable delante no equivale a tener soporte; y una confianza diagnóstica alta no basta cuando el
manual no sostiene lo que se afirma. La ablación que lo muestra es `A3`: sin el criterio de
suficiencia, la falsa confianza pasa de 0 de 9 a 6 de 9. El 9 de 9 de `A4`, con la confianza sola,
era esperable y no añade evidencia.

P1 añade la pieza que faltaba, acotada a tres situaciones construidas: frente a evidencia del vehículo correcto, con el código correcto y
clasificada como plenamente aplicable, el sistema se abstiene **por insuficiencia de la evidencia**
y no por desconfianza en su diagnóstico. Y lo que la rechaza no es ninguna de las dos barreras que
se habían supuesto (el filtro de motor ni el validador de aplicabilidad), sino la comprobación de
que el fragmento habla de lo que se afirma.

Todo ello sobre tres y cinco ventanas independientes, en un vehículo, con telemetría sintética y un
criterio ajustado sobre los mismos casos que lo miden. Lo que aquí se ve es que el mecanismo
funciona donde se construyó para funcionar; cuánto de eso sobrevive fuera de esas condiciones es una
pregunta distinta. Este notebook no la responde."""),
    md("""\
## 16. Qué queda abierto

1. **La correspondencia entre las comprobaciones deterministas y un juicio independiente** sobre lo
   que cada fragmento sostiene. Exige anotar las afirmaciones admisibles caso a caso.
2. **El comportamiento ante un diagnóstico erróneo**, visto solo en un escenario de dos ventanas
   anterior a la corrección del índice documental.
3. **La fidelidad numérica del texto**, que `L-26` deja declarada y sin corregir.
4. **Ampliar los distractores**: tres situaciones construidas no agotan el espacio de evidencia que parece
   pertinente; para un fallo solo se encontró un documento alcanzable.
5. **Una comparación con una abstención decidida por el propio modelo de lenguaje**, que diría si la
   separación entre decidir y redactar aporta algo medible. No se ha hecho: es la ablación que
   falta."""),
    md("""\
## 17. Reproducibilidad

Este notebook **lee** artefactos versionados; no recalcula ninguna decisión. Por eso se ejecuta en
un clon limpio sin más que `uv sync --extra nb`.

| | |
|---|---|
| **Dependencias** | `uv sync --extra nb` |
| **Datos** | ninguno: se leen registros versionados |
| **Commit** | el que imprime la última celda |
| **Recursos** | CPU, sin red, segundos |
| **Artefactos que produce** | cinco figuras (`FIG-NB05-01` a `FIG-NB05-05`) en `notebooks/salida/05_suficiencia_y_abstencion/`, PNG y SVG |

Reproducir las mediciones que lo sostienen es otra cosa y exige el índice documental, que no se
distribuye:

```bash
uv run mecanico-exp sufficiency --mode oracle
uv run mecanico-exp ablations
uv run python scripts/comprobar_distractor_v2.py
uv run mecanico-exp sufficiency --goldset goldset_mazda3_bk_distractor_v2.yaml \\
  --etiqueta distractor_v2 --mode oracle
```"""),
    code("""\
print(modalidad)
print()
for clave, valor in soporte.entorno().items():
    print(f"  {clave}: {valor}")"""),
    md("""\
## 18. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** Las decisiones caso a caso son la **Tabla 5.5**; los dos
errores y las políticas triviales, la **Tabla 5.6**; los documentos aplicables frente a la
cobertura, la **Figura 5.17**; y las ablaciones, la **Tabla 5.8** y la **Figura 5.18**.

| Cifra de este notebook | Artefacto | Registro | Informe |
|---|---|---|---|
| las 17 decisiones | `artifacts/tables/E15_suficiencia.csv` | `experiments/E15_suficiencia.json` | `docs/experiments/E15_suficiencia.md` |
| las cuatro ablaciones | `artifacts/tables/E18_ablacion_A*.csv` | `experiments/E18_ablacion_A*.json` | `docs/methodology/preregistro-e18-ablaciones.md` |
| las 6 ejecuciones de P1 | `artifacts/tables/E15_suficiencia_distractor_v2.csv` | `experiments/E15_suficiencia_distractor_v2.json` | `docs/experiments/P1_distractor_v2.md` |
| las cifras alteradas | ninguno | `experiments/E13_agente_*.json` | `L-26`, `scripts/auditar_cifras_redactadas.py` |

El umbral 0,79 viene de `experiments/E15b_barrido_umbral.json` (cuyo barrido completo dibuja la
**Figura 5.14** de la memoria) y su criterio enmendado está en
`docs/methodology/criterio-umbral-enmienda-01.md`, fechado antes de reejecutar las fases que
dependen del umbral."""),
]

if __name__ == "__main__":
    escribir("05_suficiencia_y_abstencion.ipynb", CELDAS)
