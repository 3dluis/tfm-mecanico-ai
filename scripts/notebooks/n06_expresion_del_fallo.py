"""Construye `06_expresion_del_fallo.ipynb`: fault_active frente a fault_expressed."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# La etiqueta dice que hay un fallo. ¿Lo hay en la señal?

**Notebook** `06_expresion_del_fallo` · **versión** 1.0 · **fecha** 13 de octubre de 2026

| | |
|---|---|
| **Experimentos** | E6 (línea base de diagnóstico), E7 (modelo temporal), fase G del diseño de PI.1 |
| **Conjunto** | `synthetic_v2`, partición de validación · las 70 ventanas etiquetadas con un fallo |
| **Protocolo** | comparación contrafactual por muestra, con el umbral declarado en `obd/expresion.py` |
| **Estado** | la medición es del 12–13 de octubre de 2026; los experimentos que reinterpreta están cerrados |
| **Pregunta de investigación** | PI.1 —qué puede diagnosticarse y qué no— y el alcance de lo que una matriz de confusión significa |
| **Evidencia original** | `experiments/E6_baseline_synthetic_v2.json`, `E7_temporal_synthetic_v2.json`, `docs/methodology/expresion-efectiva-del-fallo.md` |

---

## Qué investiga este notebook

Una pregunta que parece trivial y no lo es: **cuando el conjunto de datos dice que una ventana tiene
un fallo, ¿hay algo observable en la señal?**

La respuesta, en la cuarta parte de las ventanas de dos condiciones, es **no**. Y eso cambia lo que
una matriz de confusión significa: un «falso negativo» sobre una ventana donde el fallo no alteró
nada no es un error del modelo. Es una etiqueta que el dato no sostiene.

**Lo que este notebook no hace:** no modifica ninguna etiqueta histórica. Las etiquetas de
`synthetic_v2` son las que son y las cifras publicadas se midieron con ellas. Lo que se añade es un
segundo indicador, derivado del generador, que dice **cuánto** de cada ventana etiquetada es
observable."""),
    md("""\
## 1. Introducción: dos cosas que el mismo dato no distingue

El generador asigna una condición a una sesión y marca cada muestra posterior a la entrada del fallo
con `fault_active = True`. Eso es una decisión del plan de generación: a esta sesión le toca el
termostato bloqueado a partir del segundo 120.

Lo que `fault_active` **no** dice es si la función de fallo cambió algo. Y hay dos mecanismos, en este
mismo catálogo de cinco fallos, en los que no cambia nada:

1. **El termostato bloqueado abierto** limita la temperatura del refrigerante a 71 °C. Si el motor
   todavía no había llegado ahí por sí mismo —arranque en frío—, la señal averiada es **idéntica** a
   la sana. No parecida: la misma.
2. **El fallo de encendido** es **episódico**: episodios de 1 a 3 segundos con una tasa de aparición
   del 2 % por segundo. Entre episodios, el motor se comporta como uno sano.

Lo que no sabemos antes de medir:

- **Cuántas ventanas etiquetadas no contienen ninguna señal del fallo.**
- **Si eso explica los errores por clase** que E6 y E7 publican.
- **Si el modelo temporal gana donde hay algo que ver o donde no lo hay.**"""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Medir, ventana a ventana, qué fracción de las muestras etiquetadas con un fallo **altera
de verdad la trayectoria** respecto de la que el motor habría seguido sin el fallo, y contrastar esa
medida con el rendimiento por clase de los dos modelos.

**Hipótesis.** Las condiciones que el modelo de diagnóstico acierta por completo son las que están
plenamente expresadas, y las que falla son las que tienen un problema de expresión.

**Variables observadas.** Por ventana: número de muestras con desviación por encima del umbral,
magnitud máxima de la desviación y señal en la que se observa.

**Criterio.** No hay umbral que aprobar: la medición es descriptiva y su valor está en que es
**independiente del modelo**. El indicador se deriva del generador.

**Qué la cuestionaría.** Que las condiciones plenamente expresadas se fallaran igual, o que las que
tienen ventanas sin señal se acertaran por completo. Ninguna de las dos ocurre."""),
    md("""\
## 3. Fundamento: el contrafactual, y por qué se puede calcular exactamente

Comparar «con fallo» frente a «sin fallo» suele exigir simular dos veces, y entonces la comparación
arrastra la diferencia de los dos recorridos de números aleatorios. Aquí no hace falta, por cómo está
construido el motor:

- `SignalEngine.tick()` **devuelve una copia** y el estado del motor avanza **al margen** del fallo;
- la función de fallo usa su **propio** generador aleatorio, `Random(semilla + 1)`.

De modo que **el valor que la función de fallo recibe es exactamente la trayectoria sana de ese
instante**. El contrafactual no se simula: se tiene.

**El umbral.** Una desviación cuenta como observable si supera el 10 % de la desviación típica que el
motor declara para esa señal —`RATIO_DECLARADO`, en `obd/expresion.py`—. La comparación se hace
**después** del recorte a rango físico, porque es el valor que llega al modelo.

**Y hay un caso en el que el umbral no importa.** Para el termostato por debajo de su tope y para el
encendido fuera de un episodio, la desviación es **exactamente cero**, no pequeña. Esa clasificación
no depende de dónde se ponga el umbral.

**Qué no es este indicador.** No es una medida de detectabilidad ni de dificultad. Dice si la señal
cambió, no si un modelo podía notarlo."""),
    md("""\
## 4. Procedencia de los datos

| Artefacto | Qué aporta | Versionado |
|---|---|---|
| `experiments/E6_baseline_synthetic_v2.json` | el rendimiento por clase del bosque | **sí** |
| `experiments/E7_temporal_synthetic_v2.json` | el del modelo temporal | **sí** |
| `data/processed/synthetic_v2_meta.parquet` | qué ventanas hay en validación y con qué etiqueta | no: se reconstruye |
| el generador | el indicador de expresión, recalculado desde el `SessionSpec` | — |

`synthetic_v2` **no viaja** con el repositorio y **se reconstruye bit a bit**: sus cuatro huellas
están congeladas en el manifiesto de E19 y se comprueban al reconstruirlo. Las celdas que lo necesitan
lo dicen y fallan con un mensaje claro si falta."""),
    code(PREAMBULO),
    code("""\
modalidad = soporte.declarar_modalidad(
    "REANÁLISIS",
    "Se calcula algo NUEVO sobre datos existentes: el indicador de expresión del fallo sobre las "
    "ventanas de validación de synthetic_v2. Estas cifras NO están publicadas en la memoria y no "
    "pueden citarse como si lo estuvieran. El rendimiento por clase de E6 y E7, en cambio, se LEE "
    "de sus registros.",
)"""),
    md("""\
## 5. El rendimiento por clase, leído de los registros

Primero lo que ya está medido y publicado. Los aciertos por clase no figuran como tal en los
registros: se derivan de la exhaustividad por el soporte, que es la misma operación que el capítulo 5
hace para citar «11 de 14 frente a 9 de 14»."""),
    code("""\
import pandas as pd

e6 = soporte.registro("E6_baseline_synthetic_v2")
e7 = soporte.registro("E7_temporal_synthetic_v2")


def aciertos_por_clase(registro: dict) -> pd.DataFrame:
    filas = [
        {
            "clase": c["label"],
            "soporte": c["support"],
            "aciertos": round(c["recall"] * c["support"]),
            "exhaustividad": c["recall"],
            "f1": c["f1"],
        }
        for c in registro["metrics"]["per_class"]
    ]
    return pd.DataFrame(filas).set_index("clase")


bosque = aciertos_por_clase(e6)
temporal = aciertos_por_clase(e7)
comparacion = pd.DataFrame(
    {
        "soporte": bosque.soporte,
        "bosque": bosque.aciertos.astype(str) + " de " + bosque.soporte.astype(str),
        "temporal": temporal.aciertos.astype(str) + " de " + temporal.soporte.astype(str),
        "diferencia": temporal.aciertos - bosque.aciertos,
    }
)
print(comparacion.to_string())
print()
print(f"F1 macro · bosque {e6['metrics']['macro_f1']:.4f} · temporal {e7['metrics']['macro_f1']:.4f}")"""),
    md("""\
**Qué muestra.** El modelo temporal gana **dos** ventanas en el termostato y pierde **seis**
repartidas en tres clases: tres en la condición sin fallo, dos en el caudalímetro y dos en el
encendido. En agregado es peor: 0,8230 de F1 macro frente a 0,8788.

**Qué podemos interpretar.** Que la frase «el modelo temporal acierta dos ventanas más en el
termostato» es cierta y, por sí sola, **engañosa**: omite que pierde seis en otras clases. El capítulo
5 la cita junto a la conclusión correcta —que el modelo temporal no supera al tabular— y conviene que
el saldo completo esté a la vista.

**Qué no podemos afirmar.** Nada sobre arquitecturas. Son dos ejecuciones únicas, con una semilla cada
una, sobre 98 ventanas de 12 sesiones, y el procedimiento de las dos **no es simétrico**: el modelo
temporal selecciona su época mirando validación y el bosque no selecciona nada. Esa asimetría es una
de las tres cosas que la auditoría de PI.1 identificó como invalidantes de la comparación."""),
    md("""\
## 6. La medición nueva: cuánto de cada ventana etiquetada es observable

Se reconstruyen las sesiones de validación desde su `SessionSpec` —el mismo plan, la misma semilla— con
las tres columnas de expresión activadas, y se cuenta, ventana a ventana, cuántas de sus 120 muestras
superan el umbral."""),
    code("""\
from mecanico_ia_exp.obd.synthetic import build_balanced_specs, generate_session

meta = pd.read_parquet(soporte.raiz() / "data" / "processed" / "synthetic_v2_meta.parquet")
validacion = meta[meta.partition == "validation"]
especificaciones = {s.session_id: s for s in build_balanced_specs(seed=20260901, sessions_per_fault=12)}

filas = []
for clase in sorted(c for c in validacion.label.unique() if c != "F00_normal"):
    ventanas = validacion[validacion.label == clase]
    for sesion, grupo in ventanas.groupby("session_id"):
        sesion_df = generate_session(especificaciones[sesion], con_expresion=True)
        for _, v in grupo.iterrows():
            tramo = sesion_df[
                (sesion_df.timestamp >= v.t_start) & (sesion_df.timestamp <= v.t_end)
            ]
            filas.append(
                {
                    "clase": clase,
                    "sesion": sesion,
                    "regimen": v.regime,
                    "t_start": int(v.t_start),
                    "expresadas": int(tramo["fault_expressed"].sum()),
                    "muestras": len(tramo),
                }
            )

expresion = pd.DataFrame(filas)
expresion["fraccion"] = expresion.expresadas / expresion.muestras
print(f"{len(expresion)} ventanas etiquetadas con un fallo en validación\\n")

resumen = (
    expresion.assign(
        sin_senal=lambda d: d.expresadas == 0,
        plena=lambda d: d.expresadas == d.muestras,
    )
    .groupby("clase")
    .agg(
        ventanas=("expresadas", "size"),
        sin_senal=("sin_senal", "sum"),
        plenas=("plena", "sum"),
        fraccion_mediana=("fraccion", "median"),
    )
)
resumen["parciales"] = resumen.ventanas - resumen.sin_senal - resumen.plenas
resumen["aciertos_bosque"] = [bosque.aciertos.get(c, pd.NA) for c in resumen.index]
print(resumen[["ventanas", "sin_senal", "parciales", "plenas", "fraccion_mediana", "aciertos_bosque"]].to_string())"""),
    code("""\
fig, ejes = soporte.lienzo(
    experimento="E6 · fase G del diseño de PI.1",
    dataset="synthetic_v2, validación · 70 ventanas etiquetadas con un fallo",
    procedencia="generador reconstruido desde SessionSpec; aciertos de E6_baseline_synthetic_v2.json",
    titulo="Expresión efectiva del fallo por ventana, y aciertos del modelo de diagnóstico",
    filas=2,
    ancho=5.9,
    alto=3.6,
)

import numpy as np

clases = list(resumen.index)
etiquetas = [c.split("_", 1)[1].replace("_", " ") for c in clases]

# Izquierda: fracción de muestras expresadas, ventana a ventana.
for i, clase in enumerate(clases):
    sub = expresion[expresion.clase == clase]
    ejes[0].scatter(
        np.full(len(sub), i) + (np.arange(len(sub)) % 5 - 2) * 0.05,
        sub.fraccion,
        s=34,
        color="#9c4221",
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5,
    )
ejes[0].set_xticks(range(len(clases)))
ejes[0].set_xticklabels(etiquetas, fontsize=7.5, rotation=20, ha="right")
ejes[0].set_ylabel("Muestras alteradas / 120 (fracción de 0 a 1)")
ejes[0].set_xlabel("Condición de fallo")
ejes[0].set_title("Cuánto de cada ventana es observable", fontsize=9)
ejes[0].axhline(0, color="#1b6b4a", linewidth=0.8, linestyle=":")

# Derecha: ventanas sin señal frente a ventanas falladas por el bosque.
ancho = 0.38
posicion = np.arange(len(clases))
ejes[1].bar(
    posicion - ancho / 2,
    resumen.sin_senal,
    ancho,
    label="ventanas sin ninguna señal",
    color="#9c4221",
)
ejes[1].bar(
    posicion + ancho / 2,
    resumen.ventanas - resumen.aciertos_bosque,
    ancho,
    label="ventanas que el bosque falla",
    color="#2c5282",
)
ejes[1].set_xticks(posicion)
ejes[1].set_xticklabels(etiquetas, fontsize=7.5, rotation=20, ha="right")
ejes[1].set_ylabel("Número de ventanas (de 14)")
ejes[1].set_xlabel("Condición de fallo")
ejes[1].set_title("Sin señal frente a falladas", fontsize=9)
ejes[1].legend(fontsize=7)

destino = soporte.exportar(
    fig, "FIG-N06-01_expresion_y_aciertos", subdirectorio="06_expresion"
)
# Ruta RELATIVA: la absoluta es la de esta máquina y acabaría en el HTML entregado.
print(f"figura exportada en PNG y SVG: {destino.relative_to(soporte.raiz())}")"""),
    md("""\
**Qué muestra la figura.** A la izquierda, cada punto es una de las 70 ventanas etiquetadas, situada
en la fracción de sus 120 muestras que altera la trayectoria. Tres condiciones tienen todos sus puntos
en 1,0; el termostato los tiene repartidos entre 0,0 y 1,0; el fallo de encendido los tiene **todos
pegados al cero**, entre 0,017 y 0,13. A la derecha, las ventanas sin ninguna señal frente a las que
el bosque falla.

**Qué podemos interpretar.** Las tres condiciones que el bosque acierta **por completo** —fuga de
vacío, caudalímetro y sonda lenta— son las tres que están plenamente expresadas. Las dos que falla son
las dos únicas con un problema de expresión, y de clases distintas: el termostato tiene **cinco
ventanas sin ninguna señal**, las cinco de la misma sesión de calentamiento y consecutivas; el
encendido **no tiene ninguna ventana plenamente expresada**. El rendimiento por clase se ordena igual
que la expresión.

**Qué no podemos afirmar.** Que las cinco ventanas que el bosque falla sean **las mismas cinco** que
no tienen señal. El número coincide —falla cinco, cinco están vacías— y los registros de E6 **no
guardan las predicciones por ventana**, de modo que no se sabe cuáles falló. Comprobarlo cuesta una
reejecución con destino propio y no está hecho. Tampoco podemos afirmar que el modelo temporal gane
sus dos ventanas del termostato donde no hay nada que ver: es la hipótesis que esto sugiere y exige la
misma comprobación."""),
    md("""\
## 7. La forma en el tiempo de cada fallo, y la trayectoria contrafactual

**Introducción al problema.** El apartado anterior cuenta, ventana a ventana, qué fracción lleva
señal observable. Queda sin responder una pregunta anterior: **qué forma** tiene esa señal a lo
largo de la sesión. Un fallo que altera la trayectoria en todo momento deja firma en cualquier
ventana; uno que la altera durante tres segundos de cada ciento veinte deja la mayoría de sus
ventanas sin nada que aprender.

**Objetivo del análisis.** Medir esa diferencia sin comparar sesiones distintas, que confundiría el
efecto del fallo con el del perfil de conducción, y dejar el resultado en un artefacto con
procedencia y huella.

**Procedencia de los datos.** El análisis contrafactual T2, que produce
`scripts/contrafactual_t2.py` y vive en `artifacts/contrafactual/`. Cinco sesiones de la partición
de **entrenamiento**, una por condición, elegidas por regla declarada: la primera en orden
alfabético en que el fallo llega a expresarse. El guion verifica **antes de escribir nada** que cada
sesión original se reproduce muestra a muestra frente al conjunto congelado, con tolerancia 1e-9, y
que las dos trayectorias de cada pareja coinciden antes del instante de entrada; si alguna
comprobación falla, se detiene sin escribir.

**Qué estatuto tiene el artefacto.** Derivado, y solo para análisis visual: no entra en
entrenamiento, validación ni prueba, no modifica ninguna métrica histórica, no se usa para ajustar
ningún modelo, no es una evaluación nueva y no es un conjunto de datos, porque no tiene ventanado ni
particiones."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import recuento_de_expresion

# Cuántas muestras del tramo con fallo se expresan, y si el recuento depende del
# umbral: el dato guardado está en unidades del umbral, de modo que releerlo con
# una exigencia diez veces mayor no regenera nada.
print(recuento_de_expresion().to_string(index=False))"""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_forma_del_fallo

fig_forma_del_fallo()"""),
    md("""\
**Descripción objetiva de lo que se ve.** Cuatro condiciones alteran entre el 99,8 % y el 100 % de
las 480 muestras del tramo con fallo; el fallo de encendido altera 16, el 3,3 %, repartidas en siete
episodios de uno a tres segundos. La deriva del caudalímetro sube en rampa durante cinco minutos
hasta una meseta; la fuga de vacío sube más deprisa hasta otra más baja; el termostato salta a un
valor constante en el instante de entrada; la sonda lenta oscila en una banda ancha; y la desviación
del fallo de encendido vuelve a **cero exacto** entre episodio y episodio.

**Interpretación.** Las cinco condiciones tienen tres formas temporales distintas —rampa, tope y
episodio— y eso explica por qué no se detectan igual: en buena parte de las ventanas del fallo de
encendido no hay nada que detectar. El recuento no depende del umbral declarado: exigiendo diez
veces más, una desviación típica completa del ruido del generador en lugar de una décima, los
recuentos pasan de 480, 479, 480, 480 y 16 a 480, 471, 480, 463 y 16.

**Limitaciones.** Es **una sesión por condición**, elegida por regla declarada y no una muestra; la
proporción del fallo de encendido depende de su tasa de aparición, que es aleatoria. El umbral de
observabilidad es un parámetro declarado de este protocolo y no una magnitud del vehículo. Y esto
describe **el instrumento**: muestra que el generador produce las formas que sus fichas declaran, lo
cual comprueba el instrumento y no descubre nada sobre vehículos reales.

**Relación con la pregunta de investigación.** Fija, para PI.1, el techo observacional por debajo
del cual ningún modelo podría haber hecho mejor. En la memoria es la **Figura 5.4**."""),
    md("""\
Y la misma pareja, en unidades físicas y superpuesta señal a señal, es la comparación que la
**Figura A.1** del anexo A hacía sobre `synthetic_v1` y ya no se puede regenerar."""),
    md("""\
**Objetivo del análisis.** Ver en **unidades físicas**, señal a señal, lo que el apartado anterior
resume en unidades del umbral: qué hace cada avería a la señal que la delata, y desde cuándo."""),
    code("""\
from mecanico_ia_exp.visualization.memoria import fig_pareja_contrafactual

fig_pareja_contrafactual()"""),
    md("""\
**Descripción objetiva.** Antes de la marca de entrada las dos series de cada panel coinciden
exactamente. Después, el ajuste a largo plazo se despega en la fuga de vacío y en la deriva; la
temperatura del refrigerante cae a su tope de 71 °C mientras la sana sigue en torno a 81; la
amplitud de la sonda se reduce a una banda estrecha mientras la sana sigue oscilando entero; y en el
fallo de encendido las dos series siguen coincidiendo salvo en dieciséis muestras.

**Un detalle que solo la comparación pareada deja ver.** La ficha de la fuga de vacío declara cuatro
señales afectadas y en la sesión dibujada **solo tres se alteran**: el régimen no cambia, porque el
generador solo lo perturba por debajo de 5 km/h y la sesión es de autopista. La firma declarada de
una condición no se expresa entera en todos los regímenes.

**Limitaciones.** Datos sintéticos y comparación contrafactual controlada. **Una desviación
observable no implica que un clasificador pueda detectar el fallo**, y la ausencia de desviación
detectable en un tramo **no demuestra que el diagnóstico sea imposible**: dice que en ese tramo,
bajo el criterio declarado, no hay señal.

**Relación con la pregunta de investigación.** En la memoria es la **Figura A.2** del anexo A."""),
    md("""\
## 8. El termostato, ventana a ventana

La condición merece verse de cerca, porque sus dos sesiones de validación se comportan de forma
opuesta y eso dice de dónde viene el problema."""),
    code("""\
termostato = expresion[expresion.clase == "F03_thermostat_stuck"].sort_values(["sesion", "t_start"])
print(termostato[["sesion", "regimen", "t_start", "expresadas", "muestras", "fraccion"]].to_string(index=False))
print()
for sesion, grupo in termostato.groupby("sesion"):
    cero = int((grupo.expresadas == 0).sum())
    print(f"  {sesion:34} {grupo.regimen.iloc[0]:8} {cero} de {len(grupo)} ventanas sin señal")"""),
    md("""\
**Qué muestra.** `__urban__08` tiene sus siete ventanas plenamente expresadas. `__warmup__03` tiene
**cinco de siete sin ninguna señal** —de los 120 a los 479 segundos— y las dos últimas apenas: 9 y 69
muestras de 120.

**Qué podemos interpretar.** La causa es física y estaba descrita antes de medirla: en régimen urbano
el motor arranca a 78 °C, por encima del tope de 71 que el fallo impone, de modo que el fallo recorta
desde la primera muestra. En calentamiento arranca a temperatura ambiente y tarda minutos en llegar
al tope; hasta entonces no hay nada que distinguir. **El problema del termostato no es el termostato:
es el régimen.**

**Qué no podemos afirmar.** Que esto sea una propiedad de los termostatos reales. Es una propiedad del
mecanismo tal como la ficha del fallo lo declara y el generador lo implementa, y las fichas del
generador **no tienen respaldo documental verificado** (`L-03`). Lo que se mide es el conjunto de
datos, no el vehículo."""),
    md("""\
## 9. Por qué no se corrigen las etiquetas

La tentación es evidente: reetiquetar como «sin fallo» las ventanas sin señal y volver a medir. **No se
hace**, por tres razones y en este orden:

1. **Cambiaría todas las cifras publicadas.** E6, E7, E9, el ventanado de E5, el reparto, el conjunto
   de ajuste del redactor y la cadena completa de suficiencia se midieron con las etiquetas que hay.
2. **Sería decidir la verdad de referencia a la vista del resultado.** El indicador de expresión se
   construyó **después** de conocer los errores por clase. Usarlo para reescribir las etiquetas
   convertiría un instrumento descriptivo en una justificación.
3. **La etiqueta no es falsa.** La sesión **tiene** el termostato bloqueado: eso es cierto durante los
   600 segundos. Lo que no es cierto es que la ventana contenga una manifestación observable, y para
   eso está el segundo indicador. Dos indicadores dicen más que uno corregido.

**Lo que sí se hace:** declararlo. La distinción entra en la discusión metodológica, en las
limitaciones y en la lectura de las matrices de confusión."""),
    md("""\
## 10. `synthetic_v2` y `synthetic_v3` no son el mismo instrumento

Hay un segundo asunto de procedencia que conviene no mezclar con el anterior, porque afecta a qué
comparaciones son legítimas. El trabajo usa dos conjuntos y **no salen del mismo generador**."""),
    code("""\
import json

for conjunto in ("synthetic_v2", "synthetic_v3"):
    ruta = soporte.raiz() / "data" / "raw" / "synthetic" / f"{conjunto}.meta.json"
    if not ruta.is_file():
        print(f"{conjunto}: no está en este clon (data/raw no se versiona)")
        continue
    meta_gen = json.loads(ruta.read_text("utf-8"))
    print(
        f"{conjunto}: generado {meta_gen['created_at']} · semilla {meta_gen['seed']} · "
        f"{meta_gen['n_sessions']} sesiones · versión declarada {meta_gen['version']}"
    )

no_reconstruibles = json.loads(
    (soporte.raiz() / "configs" / "datos_no_reconstruibles.json").read_text("utf-8")
)
v3 = no_reconstruibles["synthetic_v3"]
print(f"\\nestado de synthetic_v3: {v3['estado']}")
print(f"causa: {v3['causa']}")
print("\\nmedición del 13-10-2026:")
for clave, valor in v3["medicion_del_13_10_2026"].items():
    print(f"  {clave}: {valor}")"""),
    md("""\
**Qué muestra.** Los dos declaran la misma semilla —20260901— y la misma versión de generador —1.0.0—,
y **no son comparables**: `synthetic_v3` se generó el 1 de septiembre a las 14:58 locales y la
calibración del generador contra el manual de taller es el commit de las 15:46 del **mismo día**.
`synthetic_v2` se regeneró después. `GENERATOR_VERSION` no distingue a los dos porque es una constante
escrita a mano.

Y la consecuencia medida: con el generador publicado, **cero de las 216 sesiones de `synthetic_v3` se
reproducen**. Lo que sí reproduce bit a bit es su `meta.parquet` y su reparto, porque dependen de
identificadores e instantes y no de valores.

**Qué podemos interpretar.** Que cualquier comparación entre los dos conjuntos **cambia dos cosas a la
vez**: el volumen y la calibración del fenómeno. El informe de E7 concluía que «el límite era el
volumen de datos, no la arquitectura» comparando `v2` con `v3`, y ese hallazgo está marcado
`SUPERSEDED`: la comparación no lo establece.

Y que la no reproducibilidad de `v3` es **peligrosa, no solo incómoda**: su ventanado y su reparto
reproducen, así que una reconstrucción ingenua pasaría las pruebas midiendo otras señales. El guion de
reconstrucción **se niega** a regenerarlo por eso.

**Qué no podemos afirmar.** Que las cifras de E6, E7 y E19 sobre `synthetic_v3` sean incorrectas. **No
lo son**: se midieron sobre el conjunto que hay, y su registro lo acredita. Lo que no son es
**reproducibles por un tercero** sin los ficheros procesados, que no se distribuyen por tamaño
(`L-25`)."""),
    md("""\
## 11. Resultados negativos e inconclusos

| Qué | Qué pasó |
|---|---|
| **El fallo de encendido no se puede detectar bien, y ahora se sabe por qué** | 0 de 45 ventanas plenamente expresadas en la medición de calentamiento, 0 de 14 en validación. El bosque acierta 7 de 14 y el modelo temporal, 5 |
| **El hallazgo «el límite era el volumen de datos»** | `SUPERSEDED`: comparaba dos generadores distintos |
| **La corrección de E7 sobre el fallo de encendido** | `SUPERSEDED`, misma causa |
| **Las cifras 54,3 °C y 70,7 °C del termostato** | citadas en la matriz de validación y **sin registro**. Marcadas como no utilizables: dependen de las predicciones por ventana, que no existen |
| **La coincidencia de los cinco** | cinco ventanas sin señal y cinco falladas. **No se afirma que sean las mismas** |
| **`synthetic_v4`** | diseñado, pre-registrado y **no generado**. La curva de volumen queda sin medir |"""),
    md("""\
## 12. Limitaciones

1. **El indicador depende de un umbral declarado**, el 10 % de la desviación típica de cada señal.
   Para el termostato por debajo de su tope y para el encendido fuera de un episodio la desviación es
   **exactamente cero** y la clasificación no depende de él; en los casos intermedios, sí.
2. **La medición es sobre un conjunto sintético.** Dice cómo se comporta el generador, no un vehículo.
3. **Las fichas de fallo del generador no tienen respaldo documental verificado** (`L-03`): el
   mecanismo que se mide es el que la ficha declara.
4. **Dos sesiones por condición en validación.** Que el termostato tenga una sesión de calentamiento y
   otra urbana es el reparto que salió, no un diseño: con dos sesiones, el régimen y la condición
   quedan confundidos.
5. **No hay predicciones por ventana** en los registros de E6 y E7, de modo que la relación entre
   expresión y error queda en el nivel de los recuentos por clase.
6. **Ejecución única.** Las cifras de E6 y E7 son de una semilla cada una, y el capítulo 5 las publica
   sin incertidumbre.
7. **El procedimiento de los dos modelos no es simétrico**: el temporal selecciona época en
   validación."""),
    md("""\
## 13. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** La expresión efectiva del fallo es la **Figura 5.9** del capítulo 5, en el apartado de PI.1, junto al límite de evidencia del termostato de la **Figura 5.8**. La diferencia entre los tres conjuntos sintéticos está tabulada en el anexo A, apartado A.5.

| Cifra de este notebook | De dónde sale |
|---|---|
| aciertos y F1 por clase | `experiments/E6_baseline_synthetic_v2.json`, `E7_temporal_synthetic_v2.json` |
| expresión por ventana | recalculada aquí con `obd/expresion.py` sobre sesiones reconstruidas desde `SessionSpec` |
| el umbral del 10 % | `RATIO_DECLARADO` en `src/mecanico_ia_exp/obd/expresion.py` |
| la medición de referencia | `docs/methodology/expresion-efectiva-del-fallo.md` §4 |
| la lectura por fallo | `docs/diseno-pi1/14-cierre-alcance-reducido.md` §2 |
| `synthetic_v3` no reconstruible | `configs/datos_no_reconstruibles.json`, `L-25` |"""),
    md("""\
## 14. Reproducibilidad

Este notebook **recalcula** el indicador de expresión, de modo que necesita `synthetic_v2`
preprocesado. En un clon limpio:

```bash
uv sync --extra nb --extra ml --extra embeddings --extra finetune --extra llm
bash scripts/reconstruir_datos.sh      # reconstruye y COMPRUEBA las cuatro huellas
uv run jupyter lab notebooks/06_expresion_del_fallo.ipynb
```

`synthetic_v3` **no se reconstruye** y el guion se niega: la celda que lo nombra lee su registro de no
reconstructibilidad, no el conjunto."""),
    code("""\
print(modalidad)
print()
for clave, valor in soporte.entorno().items():
    print(f"  {clave}: {valor}")"""),
    md("""\
## 15. Conclusiones

**Una etiqueta de fallo y una manifestación observable del fallo no son la misma cosa**, y en este
conjunto de datos se separan lo bastante para cambiar la lectura de dos de las cinco condiciones. En
las tres condiciones donde no se separan, el modelo de diagnóstico acierta todas las ventanas. En las
dos donde sí —el termostato por el régimen de calentamiento, el encendido por ser episódico— es donde
están todos sus errores.

Eso no mejora ninguna cifra: las deja donde estaban y cambia qué significan. Un «falso negativo» sobre
una ventana cuya señal es idéntica a la de un motor sano no mide un fallo del modelo; mide el límite
de lo que el dato contiene. Y distinguir las dos cosas es exactamente el tipo de cuidado que el resto
del trabajo exige al sistema: no dar por evidencia lo que solo lo parece.

Lo que queda sin saber es si los errores concretos coinciden con las ventanas vacías. El número
coincide, la hipótesis es plausible y la comprobación es barata. Mientras no se haga, lo que hay es
una ordenación consistente entre expresión y rendimiento, que es menos de lo que parece y más de lo
que había."""),
    md("""\
## 16. Qué queda abierto

1. **Las predicciones por ventana de E6**, que convertirían la coincidencia de los cinco en una
   comprobación. Una reejecución con destino propio, sin tocar el registro histórico.
2. **Si el modelo temporal gana donde no hay señal.** La misma reejecución, aplicada a E7.
3. **El indicador en el conjunto de ajuste del redactor**: si algunos de sus ejemplos vienen de
   ventanas sin expresión, el redactor habría aprendido a explicar lo que no se ve.
4. **`synthetic_v4`** y la curva de volumen, diseñados y aplazados, que es lo que permitiría separar
   el volumen de la calibración.
5. **Un reparto con más sesiones por condición**, que desharía la confusión entre régimen y condición
   que dos sesiones imponen."""),
]

if __name__ == "__main__":
    escribir("06_expresion_del_fallo.ipynb", CELDAS)
