"""Construye `05_suficiencia_y_abstencion.ipynb`: E15, las ablaciones y P1."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Suficiencia de la evidencia: cuándo el sistema se niega a explicar

**Notebook** `05_suficiencia_y_abstencion` · **versión** 1.0 · **fecha** 13 de octubre de 2026

| | |
|---|---|
| **Experimentos** | E15 (criterio de suficiencia), E18 (cuatro ablaciones), **P1** (rediseño de la condición con distractor) |
| **Conjunto** | `synthetic_v2`, partición de validación · 17 casos anotados + 6 casos nuevos de P1 |
| **Protocolo** | verificador determinista v2.1, umbral de confianza calibrada 0,79, cobertura mínima 0,80 |
| **Estado** | E15 y E18 cerrados; P1 ejecutado el 13-10-2026 |
| **Pregunta de investigación** | PI.3 —reconocer la insuficiencia— y PI.4 —rechazar evidencia impertinente— |
| **Evidencia original** | `experiments/E15_suficiencia.json`, `E18_ablacion_A1..A4.json`, `E15_suficiencia_distractor_v2.json` |

---

## Qué investiga este notebook

Si un sistema de diagnóstico puede **reconocer que no sabe**. No por humildad retórica, sino de una
manera que se pueda comprobar: retirar la evidencia documental, dejar el resto idéntico, y ver si la
decisión cambia.

Y la pregunta más incómoda, que es la de P1: ¿qué hace el sistema cuando le llega evidencia que
**parece** pertinente —del vehículo correcto, con el código de avería correcto, bien puntuada— y no
sostiene lo que se afirma?

Una advertencia antes de empezar, porque condiciona todo lo que sigue. Este notebook **no mide** al
sistema: lee lo que su medición dejó escrito. Las cifras no se recalculan aquí, y por eso la
modalidad está declarada abajo."""),
    md("""\
## 1. Introducción: dos textos indistinguibles

Dos informes de diagnóstico pueden ser igual de convincentes y solo uno estar sostenido. El que lo
está cita un procedimiento del manual que habla de la señal observada; el otro cita un documento que
existe, que resuelve, que es del vehículo correcto y que **no dice nada** sobre lo que se afirma. En
el papel se parecen tanto que la diferencia no se ve leyendo.

Esa es la razón por la que la decisión de explicar o abstenerse **no la toma el modelo de lenguaje**.
Si la tomara él, la respuesta a la pregunta de investigación dependería de su disposición a admitir
que no sabe algo, y eso es precisamente lo que no cabe dar por supuesto.

Lo que no sabemos antes de mirar los registros:

1. **Si la decisión depende de verdad de la evidencia** o si la gobierna la confianza del modelo.
2. **Qué componente hace el trabajo.** Un criterio con cuatro condiciones puede estar sostenido por
   una sola.
3. **Si el sistema distingue evidencia pertinente de evidencia que lo parece.** Hasta el 13 de
   octubre de 2026 esto no se sabía, porque la condición que debía medirlo no medía lo que decía."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Caracterizar cuándo el sistema explica y cuándo se abstiene, y atribuir ese
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
## 3. Fundamento: qué es «suficiente», escrito antes de implementarlo

El criterio tiene cuatro condiciones y todas deben cumplirse. No es una puntuación agregada: es una
conjunción, y eso se decidió así para que el motivo de cada abstención sea legible.

| Condición | Umbral | Qué protege |
|---|---|---|
| Confianza calibrada del diagnóstico | ≥ 0,79 | que no se explique un diagnóstico del que el modelo no está seguro |
| Fragmentos de soporte | ≥ 2 | que una sola coincidencia no sostenga una explicación |
| Fuentes distintas | ≥ 1 | procedencia |
| **Cobertura de afirmaciones** | ≥ 0,80 | que la evidencia hable de **lo que se afirma** |

**La cuarta es la que importa, y la que costó tres versiones.** Un fragmento puede existir,
resolver, pertenecer al vehículo correcto, tener buena puntuación **y no decir nada** sobre la
afirmación que lo cita. La primera versión del criterio aceptaba como soporte cualquier fragmento
que compartiera vocabulario con la afirmación, y explicó 6 de los 12 casos que debían terminar en
abstención. Es el fallo más difícil de ver, porque el texto resultante parece impecable.

Un fragmento sostiene una afirmación solo si menciona la señal con el vocabulario del manual —«short
term fuel trim», no `stft_bank1`—, es contenido diagnóstico y no una descripción de funcionamiento,
y porta un código de avería de la condición diagnosticada.

**Por qué la confianza va calibrada.** El bosque estaba **infraconfiado**: error de calibración
0,144, confianza media 0,738 frente a un acierto de 0,878. Un umbral sobre la confianza cruda habría
hecho que el sistema se abstuviera de más, y **habría parecido prudencia cuando era mala
medición**."""),
    md("""\
## 4. Procedencia de los datos

Todo lo que se muestra sale de artefactos **versionados**, y ninguno se recalcula:

| Artefacto | Qué contiene | Ejecutado |
|---|---|---|
| `E15_suficiencia.json` · `.csv` | las 17 decisiones del criterio canónico | 13-09-2026 (RERUN-A) |
| `E18_ablacion_A1.csv` … `A4.csv` | las cuatro ablaciones, pre-registradas | 1-10-2026 |
| `E15_suficiencia_distractor_v2.csv` | los 6 casos de P1 | 13-10-2026 |

Los registros JSON **sí** viajan con el repositorio; los conjuntos de datos, no. Este notebook no
necesita los datos: necesita los registros, que son la evidencia de cada cifra publicada."""),
    code(PREAMBULO),
    code("""\
# MODALIDAD. Las cuatro posibles están en `soporte.MODALIDADES`, y declarar una
# inventada falla a propósito.
modalidad = soporte.declarar_modalidad(
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA",
    "Se leen los registros de E15, E18 y P1 y se muestran. Ninguna cifra se recalcula: "
    "el recorrido completo exige el índice documental, que no se distribuye. "
    "Lo que aquí se ve son las cifras publicadas, no una reproducción de ellas.",
)"""),
    md("""\
## 5. Carga y comprobación de la evidencia

Primero se comprueba que los artefactos están y que dicen lo que se espera. Si faltara uno, el
notebook falla con un mensaje que explica qué falta y por qué, en lugar de seguir con una tabla
vacía."""),
    code("""\
import pandas as pd

e15 = soporte.tabla("E15_suficiencia")
p1 = soporte.tabla("E15_suficiencia_distractor_v2")
ablaciones = {
    nombre: soporte.tabla(f"E18_ablacion_{nombre}") for nombre in ("A1", "A2", "A3", "A4")
}

print(f"E15: {len(e15)} casos · P1: {len(p1)} casos")
print(f"ablaciones: {', '.join(f'{k} ({len(v)} casos)' for k, v in ablaciones.items())}")
print()
print("condiciones de corpus en E15:")
print(e15.corpus_variant.value_counts().to_string())"""),
    md("""\
## 6. El experimento central, reducido a dos filas

La demostración de PI.3 no necesita diecisiete casos: necesita dos. Mismos datos, mismo modelo,
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
**Qué muestra.** Dos ejecuciones sobre **la misma ventana de telemetría**, con la misma confianza calibrada —0,908— y
decisiones opuestas. En la primera hay documentos aplicables y la cobertura es 1,00; en la segunda,
con la evidencia retirada del índice, no queda ninguno y la cobertura es 0,00.


**Qué podemos interpretar.** Que la decisión **cambió porque cambió la evidencia**, no porque cambiara el vehículo ni la certeza
del modelo. Es la hipótesis de PI.3 reducida a su mínima expresión, y se cumple.


**Qué no podemos afirmar.** Que esto demuestre un comportamiento general. Son dos ejecuciones sobre una ventana. Y hay algo más
débil de lo que parece: la abstención de la segunda fila está **determinada por la construcción de
la condición** —se retiraron del índice todos los fragmentos con los códigos del fallo, así que no
quedaba nada que juzgar—. No pone a prueba el criterio de soporte; solo comprueba que el sistema no
explica sin evidencia. **La condición informativa es la parcial**, y es la de la sección
siguiente."""),
    md("""\
## 7. La condición informativa: hay documentos y aun así se abstiene

Con evidencia parcial el sistema tiene delante cuatro, siete o seis fragmentos aplicables —del
vehículo correcto, con el código correcto— y se abstiene igual. Esa es la medición que distingue
«no hay nada» de «hay algo que no sirve»."""),
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
    dataset="synthetic_v2, validación · 17 casos anotados",
    procedencia="artifacts/tables/E15_suficiencia.csv",
    titulo="Documentos aplicables frente a cobertura de afirmaciones, por condición de evidencia",
    columnas=2,
    ancho=10.0,
    alto=3.4,
)

orden = ["FULL", "PARTIAL", "ABSENT", "DISTRACTOR"]
colores = {"EXPLAIN": "#1b6b4a", "ABSTAIN": "#9c4221"}

for eje, (columna, etiqueta, unidad) in zip(
    ejes,
    [
        ("n_documents_applicable", "Documentos aplicables", "nº de fragmentos"),
        ("claim_coverage", "Cobertura de afirmaciones", "fracción de 0 a 1"),
    ],
    strict=True,
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
    eje.set_xticklabels(orden, fontsize=8)
    eje.set_xlabel("Condición de evidencia")
    eje.set_ylabel(f"{etiqueta} ({unidad})")
    eje.set_title(etiqueta, fontsize=9)

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
soporte.exportar(fig, "FIG-N05-01_aplicables_vs_cobertura", subdirectorio="05_suficiencia")"""),
    md("""\
**Qué muestra.** A la izquierda, cuántos fragmentos **aplicables** —vehículo correcto, código correcto— llegan al
verificador en cada condición. A la derecha, qué fracción de las afirmaciones construidas queda
**sostenida** por ellos. El color es la decisión.

Lo que salta a la vista es que las dos columnas no se parecen. En la condición parcial hay
fragmentos aplicables —entre cuatro y siete— y la cobertura es **cero** en todos los casos.


**Qué podemos interpretar.** Que **tener documentación aplicable delante no equivale a tener soporte**. Las dos magnitudes se
separan exactamente en la condición que el diseño construyó para separarlas, y la decisión sigue a
la cobertura y no al recuento de documentos.


**Qué no podemos afirmar.** Que la cobertura sea un buen estimador de nada fuera de estos casos. Y hay un límite más serio: que
las comprobaciones deterministas de soporte coincidan con lo que un fragmento sostiene **de verdad**
no se ha medido. Haría falta anotar, caso a caso, qué afirmaciones son admisibles y qué evidencia es
mínima exigible, y el conjunto anotado no tiene esa anotación. Lo que está comprobado es que ninguna
cita se asigna fuera de esas comprobaciones, que es menos."""),
    md("""\
## 8. Qué componente hace el trabajo: las cuatro ablaciones

Cuatro configuraciones, pre-registradas el 1 de octubre de 2026 antes de ejecutarse. Cada una cambia
**una** pieza y deja el resto idéntico. Ninguna redacta: miden la decisión y la evidencia, no el
texto.

Y las unidades importan, porque los diecisiete casos **no son diecisiete observaciones
independientes**: salen de cinco ventanas de telemetría. Los recuentos se dan sobre ejecuciones y
sobre ventanas, nunca como una tasa única."""),
    code("""\
def tasas(tabla: pd.DataFrame) -> dict[str, object]:
    \"\"\"Los dos errores, contados por separado porque no son intercambiables.\"\"\"
    debe_abstenerse = tabla[tabla.expected_action == "ABSTAIN"]
    debe_explicar = tabla[tabla.expected_action == "EXPLAIN"]
    # La condición con distractor y filtro se cuenta aparte: su configuración
    # era idéntica a la parcial, de modo que no es una condición independiente.
    sin_distractor = debe_abstenerse[debe_abstenerse.condition != "DISTRACTOR"]
    return {
        "falsa_confianza": f"{int((sin_distractor.decision == 'EXPLAIN').sum())} de {len(sin_distractor)}",
        "abstencion_innecesaria": f"{int((debe_explicar.decision == 'ABSTAIN').sum())} de {len(debe_explicar)}",
        "cobertura_con_evidencia_completa": f"{int((debe_explicar.claim_coverage >= 0.8).sum())} de {len(debe_explicar)}",
    }


nombres = {
    "A1": "sin atribución: observaciones por desviación tipificada",
    "A2": "sin recuperación semántica: solo búsqueda léxica",
    "A3": "sin criterio de suficiencia: explicar si hay fragmento aplicable",
    "A4": "umbral único: solo confianza calibrada",
}
filas = []
for clave, tabla in ablaciones.items():
    filas.append({"ablación": clave, "qué cambia": nombres[clave], **tasas(tabla)})
print(pd.DataFrame(filas).to_string(index=False))"""),
    md("""\
**Qué muestra.** `A4`, que deja solo la puerta de confianza, explica **las nueve ejecuciones que debían terminar en
abstención**, incluidas las tres en que la recuperación no devuelve ningún fragmento. `A3`, que
exige que exista algún fragmento aplicable pero no que lo sostenga, baja a seis de nueve. `A1`, que
sustituye la atribución por un criterio estadístico simple, no cambia ninguna decisión.


**Qué podemos interpretar.** Lo que estas dos ablaciones muestran se enuncia mejor al revés de como suele pensarse un sistema de
diagnóstico: **una confianza diagnóstica alta no basta para sostener una explicación si la evidencia
documental no la sostiene**. La confianza del modelo mide cuán seguro está de su diagnóstico y no
sabe nada de si el manual lo documenta.

Y el cero de `A1` admite una lectura mala que conviene cerrar. **No** significa que la atribución
sea prescindible: significa que **no interviene en la política de abstención**. Su contribución está
en otro plano —la trazabilidad, nombrar qué señal y en qué ventana sostiene cada afirmación—, y esa
dimensión no se ha evaluado aquí.


**Qué no podemos afirmar.** Nada sobre la separación entre decidir y redactar, que no se ablaciona. Y nada que no esté
condicionado por que **las cuatro se miden sobre el conjunto con el que el criterio se ajustó**.
`A2` quedó además **inconclusa**: la ruta léxica no recuperó nada en ningún caso, pero la causa no
es la ablación sino la consulta —una búsqueda de texto completo con treinta palabras unidas por
conjunción—. Se conserva como inconclusa en lugar de reformularse a posteriori."""),
    md("""\
## 9. P1: evidencia que parece pertinente y no lo es

Hasta el 13 de octubre de 2026 la pregunta PI.4 **no tenía respuesta interpretable**, y no por falta
de medición: porque la condición que debía medirla no medía lo que decía. El diagnóstico escrito en
septiembre culpaba al filtro de motor; al comprobarlo, la causa resultó ser otra y más simple.
**Dos de las tres condiciones con distractor tenían exactamente la misma configuración que las
parciales correspondientes.** El único campo que difería no lo lee el recorrido de suficiencia.

El rediseño construye la condición por **exclusión diferencial**: la parcial excluye el
procedimiento de diagnóstico **y** los documentos de alcance equivocado; la del distractor excluye
**solo** el procedimiento. La diferencia entre las dos es exactamente el documento que se quiere
poner a prueba.

Los distractores son del motor correcto y llevan el código del fallo —un esquema de cableado del
sistema de control, un modo de prueba de diagnóstico, un autodiagnóstico KOEO/KOER—, y su razón de
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
**Qué muestra.** Seis abstenciones de seis. Y el dato que decide la lectura: el motivo registrado en las seis es
`LOW_CLAIM_COVERAGE` —la evidencia no sostiene ninguna afirmación— y **ninguna** es
`LOW_MODEL_CONFIDENCE`. Las confianzas son 0,908 y 1,000, **por encima** del umbral de 0,79.


**Qué podemos interpretar.** Que la puerta de confianza **no intervino**: el rechazo lo hizo la verificación de soporte. Era la
condición que el protocolo fijó de antemano para que el resultado apoyara PI.4, y se cumple en su
forma fuerte.

Más aún: el distractor no solo llega al verificador, llega clasificado **`EXACT_MATCH`**. El filtro
de motor no lo bloquea —es del motor correcto— y el validador de aplicabilidad no lo degrada —lleva
el código del fallo—. De los documentos aplicables, uno de cinco, tres de siete y uno de seis eran
distractores. **Las dos primeras líneas de defensa no actúan**, y lo que rechaza es que el fragmento
no habla de la señal observada con el vocabulario del manual.


**Qué no podemos afirmar.** Que exista una tasa de rechazo. Son **tres** situaciones construidas por el autor, con `n = 3`, en
un vehículo, sobre un corpus. Describen tres situaciones y no estiman ninguna probabilidad. Tampoco
que el espacio de distractores alcanzables esté cubierto: para la sonda lambda solo se encontró
**uno**, y así se declaró."""),
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
**Qué muestra.** Tres de las diecisiete salidas de la configuración canónica —la que sostiene el «17/17 válidas ·
17/17 respeta el veredicto · 0 citas inventadas» publicado— contienen un número que el verificador
no produjo. El modelo base, sin adaptador, no presenta ninguna.


**Qué podemos interpretar.** Que una salida puede ser **trazable en sus citas y falsa en sus cifras**. Las barreras comprueban
que el identificador citado se entregara; **ninguna comprueba que el número dicho sea cierto**. Es
un hueco en la trazabilidad —PI.2— que no estaba declarado, y afecta justamente a la parte del texto
que un lector usaría para juzgar la decisión.


**Qué no podemos afirmar.** Que el ajuste empeore la fidelidad numérica. Cero de diecisiete frente a tres de diecisiete es
sugerente y con diecisiete casos es compatible con el azar del muestreo. Tampoco se corrige el
recorrido: añadir una barrera ahora sería cambiar el sistema a la vista del resultado. Queda
declarado como limitación `L-26`, con un guion —`scripts/auditar_cifras_redactadas.py`— para que
cualquiera repita la auditoría."""),
    md("""\
## 11. Resultados negativos e inconclusos

Un notebook que solo mostrara lo que salió bien sería una presentación, no un informe.

| Qué | Qué pasó | Qué se hizo |
|---|---|---|
| **Primera versión del criterio** | explicó 6 de los 12 casos que debían terminar en abstención: aceptaba como soporte cualquier fragmento que compartiera vocabulario | se corrigió, y las tres versiones se conservan con sus registros |
| **Segunda versión** | corrigió ese defecto y **regresionó** la fuga de vacío con evidencia completa | la tercera lo recuperó cambiando solo la granularidad con que se clasifica el papel de un fragmento |
| **Ablación `A2`** | la ruta léxica no recuperó nada en ningún caso, por la consulta y no por la ablación | **inconclusa**, sin reformular a posteriori; la variante queda declarada como medición nueva |
| **Dos abstenciones innecesarias** | `C01` por confianza 0,600 y `C04` por confianza 0,462 **y** cobertura 0,00 | se dejan registradas en lugar de resolverse bajando el umbral |
| **Condición con distractor v1** | no medía lo que decía, y el diagnóstico de su causa también era equivocado | invalidada, conservada con su etiqueta, y rediseñada en P1 |
| **Modo adverso** | el sistema se abstuvo en las seis ejecuciones, y en dos aceptó fragmentos como soporte de afirmaciones de un diagnóstico **erróneo** | queda como limitación: se abstuvo por cobertura 0,67, no por rechazar el soporte |"""),
    md("""\
## 12. Limitaciones

1. **El criterio se revisó dos veces sobre los mismos casos con los que se evalúa.** Las cifras son
   de desarrollo, no de evaluación. La evaluación final sobre la partición de prueba es otra
   medición, con su registro.
2. **Los diecisiete casos salen de cinco ventanas.** No son diecisiete observaciones
   independientes, y por eso no se publica ninguna tasa única ni ningún intervalo.
3. **Las ventanas se eligieron entre las que el modelo clasifica bien.** Las tasas describen el
   comportamiento cuando el diagnóstico de partida es acertado: son **cota superior**.
4. **El modo oracular abre dos canales**: los códigos que acotan la búsqueda y los que exige el
   verificador salen de la etiqueta anotada. El modo no oracular da el mismo vector de decisiones, y
   esa identidad era forzosa porque las ventanas están bien clasificadas: confirma que la
   implementación no introduce diferencias, no que el sistema resista un diagnóstico erróneo.
5. **`n = 3` en P1.** Tres situaciones construidas.
6. **La fidelidad numérica del texto redactado no está verificada** (`L-26`).
7. **Un vehículo, un corpus, telemetría sintética.** Nada de esto dice qué pasaría con otro
   vehículo, otro fabricante o datos de operación real."""),
    md("""\
## 13. Trazabilidad

| Cifra de este notebook | Artefacto | Registro | Informe |
|---|---|---|---|
| las 17 decisiones | `artifacts/tables/E15_suficiencia.csv` | `experiments/E15_suficiencia.json` | `docs/experiments/E15_suficiencia.md` |
| las cuatro ablaciones | `artifacts/tables/E18_ablacion_A*.csv` | `experiments/E18_ablacion_A*.json` | `docs/methodology/preregistro-e18-ablaciones.md` |
| los 6 casos de P1 | `artifacts/tables/E15_suficiencia_distractor_v2.csv` | `experiments/E15_suficiencia_distractor_v2.json` | `docs/experiments/P1_distractor_v2.md` |
| las cifras alteradas | — | `experiments/E13_agente_*.json` | `L-26`, `scripts/auditar_cifras_redactadas.py` |

El umbral 0,79 viene de `experiments/E15b_barrido_umbral.json` y su criterio enmendado está en
`docs/methodology/criterio-umbral-enmienda-01.md`, fechado antes de reejecutar las fases que
dependen del umbral."""),
    md("""\
## 14. Reproducibilidad

Este notebook **lee** artefactos versionados; no recalcula nada, y por eso se ejecuta en un clon
limpio sin más que `uv sync --extra nb`.

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
## 15. Conclusiones

La decisión de explicar o abstenerse **depende de la evidencia** y es auditable sin que intervenga un
generador de texto. Retirar o degradar la evidencia cambia la decisión; tener documentación
aplicable delante no equivale a tener soporte; y una confianza diagnóstica alta no basta cuando el
manual no sostiene lo que se afirma, que es lo que las ablaciones muestran al quitar el criterio
compuesto.

P1 añade la pieza que faltaba: frente a evidencia del vehículo correcto, con el código correcto y
clasificada como plenamente aplicable, el sistema se abstiene **por insuficiencia de la evidencia**
y no por desconfianza en su diagnóstico. Y lo que la rechaza no es ninguna de las dos barreras que
se habían supuesto —el filtro de motor ni el validador de aplicabilidad—, sino la comprobación de
que el fragmento habla de lo que se afirma.

Todo ello sobre tres y cinco ventanas independientes, en un vehículo, con telemetría sintética y un
criterio ajustado sobre los mismos casos que lo miden. Lo que aquí se ve es que el mecanismo
funciona donde se construyó para funcionar; cuánto de eso sobrevive fuera de esas condiciones es una
pregunta distinta, y este notebook no la responde."""),
    md("""\
## 16. Qué queda abierto

1. **La correspondencia entre las comprobaciones deterministas y un juicio independiente** sobre lo
   que cada fragmento sostiene. Exige anotar las afirmaciones admisibles caso a caso.
2. **El comportamiento ante un diagnóstico erróneo**, visto solo en un escenario de dos ventanas
   anterior a la corrección del índice documental.
3. **La fidelidad numérica del texto**, que `L-26` deja declarada y sin corregir.
4. **Ampliar los distractores**: tres casos construidos no agotan el espacio de evidencia que parece
   pertinente, y para un fallo solo se encontró un documento alcanzable.
5. **Una comparación con una abstención decidida por el propio modelo de lenguaje**, que diría si la
   separación entre decidir y redactar aporta algo medible. No se ha hecho, y es la ablación que
   falta."""),
]

if __name__ == "__main__":
    escribir("05_suficiencia_y_abstencion.ipynb", CELDAS)
