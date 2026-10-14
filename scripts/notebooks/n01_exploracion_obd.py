"""Construye `01_exploracion_obd.ipynb`: exploración y análisis temporal de OBD-II."""

from __future__ import annotations

from constructor import PREAMBULO, code, escribir, md

CELDAS = [
    md("""\
# Exploración de datos OBD-II y análisis temporal

**Notebook** `01_exploracion_obd` · **versión** 1.0 · **fecha** 12 de octubre de 2026

| | |
|---|---|
| **Experimentos** | E2 (generación), E4 (exploratorio), E5 (ventanado y reparto) |
| **Conjunto** | `data/samples/synthetic_sample.parquet`, 18 sesiones · sesiones de calentamiento generadas en el notebook |
| **Protocolo** | ventana 120 s, paso 60 s, reparto por sesión |
| **Estado** | E2, E4 y E5 cerradas y validadas |
| **Pregunta de investigación** | PI.1 — el análisis contextual y longitudinal de datos OBD-II |
| **Evidencia original** | `docs/experiments/E4_eda_temporal.md`, `E5_preprocesamiento.md`, `artifacts/tables/E4_*.csv` |

---

## Qué investiga este notebook

Si las señales OBD-II contienen estructura suficiente para distinguir una condición de otra, y qué
forma tiene esa estructura. Es la pregunta previa a cualquier modelo: si las señales de un motor con
fuga de vacío fueran indistinguibles de las de uno sano, no habría nada que aprender y el resto del
trabajo carecería de objeto.

La respuesta no es un sí o un no. Hay condiciones que se ven a simple vista y condiciones cuya firma
es una **ausencia** —algo que debería ocurrir y no ocurre—, y esas son las interesantes."""),
    md("""\
## 1. Introducción: por qué hace falta mirar antes de modelar

Un modelo entrenado sobre datos que nadie ha mirado puede obtener métricas altas por motivos
que no tienen nada que ver con el problema. Si el generador dejara, por ejemplo, una señal que tomara
un valor imposible solo durante un fallo, cualquier clasificador la encontraría y el resultado
mediría la calidad del generador, no la del diagnóstico.

Lo que no sabemos antes de empezar:

1. **Si las relaciones entre señales están presentes.** Un generador de variables independientes al
   azar no tendría estructura que aprender, y la atribución no tendría nada que señalar.
2. **Si alguna condición se separa trivialmente.** Sería un artefacto, no un resultado.
3. **Cuánto dura la firma de cada fallo**, que es lo que determina el tamaño de ventana.
4. **Si todas las condiciones se manifiestan igual en todos los regímenes.** No lo hacen, y esa es
   la observación más consecuente de este notebook."""),
    md("""\
## 2. Objetivo e hipótesis

**Objetivo.** Caracterizar las señales, sus relaciones y la forma temporal de cada condición, y
fijar con evidencia el tamaño de ventana.

**Hipótesis evaluada.** Las condiciones de fallo producen desplazamientos observables en las señales
que su ficha declara afectadas, y ese desplazamiento es suficiente para separarlas de la condición
normal sin que ninguna señal lo haga por sí sola con un umbral.

**Variables observadas.** Las doce señales del catálogo, la condición, el régimen y el tiempo.

**Criterios de evaluación.** Un desplazamiento se considera observable si el tamaño del efecto
—delta de Cliff— lo separa de la condición normal. La separación se considera **trivial**, y por
tanto un defecto, si existe un umbral de una sola señal que clasifique perfectamente una condición.

**Qué cuestionaría la hipótesis.** Que ninguna señal se desplace en una condición, o que alguna la
separe perfectamente. Las dos cosas se comprueban en este notebook."""),
    md("""\
## 3. Fundamento: lo necesario para leer lo que sigue

**OBD-II.** Norma de diagnóstico a bordo obligatoria en los vehículos de pasajeros desde finales de
los noventa. Expone un conjunto de parámetros —*PID*— que la centralita publica a petición: régimen,
velocidad, carga calculada, temperatura de refrigerante, caudal de aire, ajustes de combustible,
tensión de la sonda lambda y avance de encendido, entre otros. Aquí se usan doce, con su
correspondencia a los PID canónicos declarada en `obd/signals.py`.

**Serie temporal y ventana.** Las señales llegan como series muestreadas a 1 Hz. Un clasificador de
ventanas no mira la muestra suelta, sino un **tramo** de duración fija. La elección de esa duración
no es libre: demasiado corta y la firma no cabe; demasiado larga y hay pocas ventanas por sesión.

**Descriptores de ventana.** Resumir un tramo de 120 × 12 valores en un vector de números: media,
desviación, pendiente, autocorrelación, número de cruces. Es una **representación** del tramo, y
cambiarla cambia lo que un modelo puede ver.

**Delta de Cliff.** Medida no paramétrica del tamaño de un efecto: la probabilidad de que un valor
tomado de un grupo supere a uno del otro, menos la probabilidad contraria. Va de −1 a 1. *Por qué
esta y no la diferencia de medias:* no supone normalidad ni igualdad de varianzas, y aquí las
distribuciones no son normales.

**Fuga temporal.** Repartir ventanas de una misma sesión entre entrenamiento y evaluación haría que
el modelo viera en el examen tramos solapados con los que estudió. La evaluación mediría memoria, no
capacidad de generalizar. Por eso la unidad de reparto es la **sesión**."""),
    md("""\
## 4. Preparación del entorno"""),
    code(PREAMBULO),
    code("""\
soporte.declarar_modalidad(
    "REANÁLISIS",
    "los descriptivos se recalculan aquí sobre la muestra versionada de 18 sesiones; "
    "NO son las cifras publicadas de E4, que se midieron sobre synthetic_v1 con 36 sesiones. "
    "Las figuras publicadas de E4 están en artifacts/figures/ y se muestran al final sin recalcularlas",
)"""),
    md("""\
Esa declaración importa más de lo que parece. Lo que sigue **no reproduce** E4: lo recalcula sobre
una muestra distinta. Las cifras que se obtengan no deben citarse como si fueran las publicadas, y
por eso el notebook las nombra siempre junto al conjunto del que salen."""),
    md("""\
## 5. El conjunto: procedencia y estructura

La muestra que viaja con el repositorio son 18 sesiones de 600 s, tres por condición. Sale del mismo
generador y de la misma semilla global que el conjunto oficial.

**Lo que hay que distinguir, y el trabajo tardó en distinguirlo:** hay tres conjuntos sintéticos y
**no salen del mismo generador**.

| Conjunto | Sesiones | Generado | Estado del generador |
|---|---|---|---|
| `synthetic_v1` | 36 | 14-09-2026 | post-calibración |
| `synthetic_v2` | 72 | 14-09-2026 | post-calibración · **conjunto oficial** |
| `synthetic_v3` | 216 | **01-09-2026** | **pre-calibración**: ralentí en 820 rpm, sin respaldo documental |

La constante `GENERATOR_VERSION` valió `"1.0.0"` en los tres casos y no los distingue. Comparar `v2`
con `v3` cambia el volumen **y** el fenómeno, y esa confusión invalidó una conclusión publicada. No
se mezclan aquí."""),
    code("""\
datos = soporte.muestra_redistribuible()

print(f"{len(datos):,} muestras · {datos.session_id.nunique()} sesiones · "
      f"{datos.fault_id.nunique()} condiciones")
print(f"valores ausentes: {int(datos.isna().sum().sum())}")
print()

from mecanico_ia_exp.obd.signals import SIGNAL_NAMES, SIGNALS_BY_NAME

rangos = datos[list(SIGNAL_NAMES)].agg(["min", "max", "mean", "std"]).T
rangos["rango físico"] = [
    f"{SIGNALS_BY_NAME[s].minimum:g} … {SIGNALS_BY_NAME[s].maximum:g}" for s in rangos.index
]
rangos["unidad"] = [SIGNALS_BY_NAME[s].unit for s in rangos.index]
rangos.round(2)"""),
    md("""\
**Lo observado.** Ninguna señal sale de su rango físico y no hay valores ausentes. El recorte a
rango no es decorativo: la inyección de un fallo puede empujar una señal fuera de lo posible —un
ajuste de combustible del 140 %— y dejarla pasar regalaría al modelo una pista que en datos reales
nunca existiría, porque un sensor real satura.

El reparto por condición y régimen, que es donde se ve el equilibrio buscado y una ausencia."""),
    code("""\
import pandas as pd

reparto = (
    datos.drop_duplicates("session_id")
    .pivot_table(index="fault_id", columns="regime", values="session_id", aggfunc="count")
    .fillna(0)
    .astype(int)
)
reparto["total"] = reparto.sum(axis=1)
reparto"""),
    md("""\
**Lo observado.** Tres sesiones por condición, repartidas entre **tres** regímenes: urbano,
autopista y ralentí. **No hay sesiones de calentamiento.**

**Qué podemos interpretar.** Es aritmética, no un sesgo del muestreo: el plan equilibrado recorre
cuatro regímenes en ciclo y con tres sesiones por condición solo alcanza a los tres primeros. El
conjunto oficial, con doce por condición, sí los cubre los cuatro.

**Qué no podemos afirmar.** Nada sobre el comportamiento en calentamiento a partir de esta muestra.
Y resulta que el calentamiento es justo el régimen donde una de las condiciones se comporta de forma
distinta, así que más adelante esas sesiones se **generan** en el notebook y se declara que son
ilustrativas."""),
    md("""\
## 6. Exploración: las señales en el tiempo

Primero lo más directo: qué aspecto tiene una sesión.

**Qué queremos investigar.** Si la estructura de las señales es plausible y si las relaciones que el
generador declara construir —acelerador↔régimen, régimen↔caudal, carga↔presión— se ven.

**Qué datos utilizamos.** Una sesión sana del régimen urbano, completa.

**Qué variables se representan.** Seis de las doce señales, en el tiempo. Seis y no doce porque el
objetivo es que se lean, no que estén todas.

**Por qué esta visualización.** Un gráfico de líneas compartiendo el eje temporal es lo único que
permite ver si dos señales se mueven juntas.

**Qué debemos observar.** Que el régimen siga a la velocidad, que el caudal siga al régimen y que la
temperatura de refrigerante suba y se estabilice."""),
    code("""\
import matplotlib.pyplot as plt

from mecanico_ia_exp.visualization.style import CATEGORICAL, apply_style

apply_style()

SENALES_VISTA = [
    ("vehicle_speed", "Velocidad", "km/h"),
    ("rpm", "Régimen del motor", "rpm"),
    ("engine_load", "Carga calculada", "%"),
    ("maf", "Caudal másico de aire", "g/s"),
    ("coolant_temperature", "Temperatura de refrigerante", "°C"),
    ("stft_bank1", "Ajuste de combustible a corto plazo", "%"),
]

sana = datos[datos.session_id == "F00_normal__urban__00"].sort_values("timestamp")

fig, ejes = plt.subplots(len(SENALES_VISTA), 1, figsize=(9.5, 8.4), sharex=True)
for eje, (senal, titulo, unidad), color in zip(ejes, SENALES_VISTA, CATEGORICAL, strict=False):
    eje.plot(sana.timestamp, sana[senal], color=color, linewidth=0.9)
    eje.set_ylabel(f"{titulo}\\n({unidad})", fontsize=7)
ejes[-1].set_xlabel("tiempo desde el arranque (s)")
fig.suptitle(
    "Sesión sin fallo, régimen urbano: seis de las doce señales OBD-II",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E2 generación · synthetic_sample · sesión F00_normal__urban__00 · 600 muestras a 1 Hz",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB01-01_sesion_sana", subdirectorio="01_exploracion_obd")
plt.show()"""),
    md("""\
**Qué muestra.** La velocidad alterna tramos de marcha y paradas, propio del régimen urbano. El
régimen del motor la sigue con saltos en los cambios de relación y cae a un ralentí plano cuando el
vehículo se detiene. La carga y el caudal acompañan al régimen. La temperatura de refrigerante parte
alta —en este régimen el motor arranca caliente— y se mantiene. El ajuste de combustible a corto
plazo oscila en torno a cero sin desplazamiento.

**Qué podemos interpretar.** Las relaciones entre señales que el generador dice construir están
presentes y son del signo esperado. Un conjunto de variables independientes al azar no tendría esta
estructura, y entonces el problema de clasificación sería de otra naturaleza.

**Qué no podemos afirmar.** Que estas trayectorias se parezcan a las de un vehículo real. El modelo
es paramétrico y **no está calibrado contra datos reales**; sus constantes sí lo están contra el
manual de taller, que es una cosa distinta. Tampoco se puede afirmar nada sobre otros regímenes a
partir de una sesión."""),
    md("""\
## 7. Normal frente a fallo: dónde se ve la firma

Lo interesante no es cómo se ve una sesión, sino en qué se diferencian dos.

**Qué queremos investigar.** Si la firma declarada de cada fallo aparece donde su ficha dice.

**Qué datos utilizamos.** Para cada condición, una sesión del mismo régimen que la sana, de modo que
la única diferencia sea la condición.

**Qué variables se representan.** La señal que la ficha del fallo declara como principal.

**Por qué esta visualización.** Superponer la trayectoria sana y la averiada en el mismo eje es lo
único que permite ver el desplazamiento sin que la escala engañe.

**Qué debemos observar.** Un desplazamiento en la señal declarada, y **su forma en el tiempo**: no
todas las firmas son un escalón."""),
    code("""\
from mecanico_ia_exp.obd.faults import FAULTS

# Para cada fallo, su señal principal declarada y una sesión del mismo régimen.
PRINCIPAL = {
    "F01_vacuum_leak": ("stft_bank1", "Ajuste a corto plazo", "%"),
    "F02_maf_drift": ("ltft_bank1", "Ajuste a largo plazo", "%"),
    "F03_thermostat_stuck": ("coolant_temperature", "Temperatura de refrigerante", "°C"),
    "F04_o2_lag": ("oxygen_sensor", "Tensión de la sonda lambda", "V"),
    "F05_misfire": ("rpm", "Régimen del motor", "rpm"),
}

fig, ejes = plt.subplots(len(PRINCIPAL), 1, figsize=(9.5, 8.8), sharex=True)
for eje, (fid, (senal, titulo, unidad)) in zip(ejes, PRINCIPAL.items(), strict=False):
    con_fallo = datos[datos.session_id == f"{fid}__urban__00"].sort_values("timestamp")
    eje.plot(sana.timestamp, sana[senal], color=CATEGORICAL[0],
             linewidth=0.9, label="sin fallo", alpha=0.85)
    eje.plot(con_fallo.timestamp, con_fallo[senal], color=CATEGORICAL[1],
             linewidth=0.9, label=FAULTS[fid].fault_name)
    inicio = float(con_fallo.loc[con_fallo.fault_active, "timestamp"].min())
    eje.axvline(inicio, color="#898781", linestyle="--", linewidth=0.8)
    eje.set_ylabel(f"{titulo}\\n({unidad})", fontsize=7)
    eje.legend(loc="upper left", fontsize=6.5, ncols=2)
ejes[-1].set_xlabel("tiempo desde el arranque (s)")
fig.suptitle(
    "La firma de cada condición en la señal que su ficha declara principal",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E2 generación · synthetic_sample · régimen urbano · "
    "línea discontinua: instante de entrada del fallo (120 s)",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB01-02_normal_vs_fallo", subdirectorio="01_exploracion_obd")
plt.show()"""),
    md("""\
**Qué muestra.** Cinco formas distintas de manifestarse:

- **Fuga de vacío**: el ajuste a corto plazo salta a positivo y se queda. Un escalón.
- **Deriva del caudalímetro**: el ajuste a largo plazo sube en **rampa**, no de golpe. El integrador
  aprende durante minutos.
- **Termostato bloqueado**: la temperatura queda **recortada** a un techo.
- **Sonda lenta**: la oscilación característica se **amortigua**; el valor medio no se mueve.
- **Fallo de encendido**: caídas **breves y aisladas** del régimen. La mayor parte del tiempo la
  señal es indistinguible de la sana.

**Qué podemos interpretar.** Cada firma tiene una forma temporal distinta, y eso tiene una
consecuencia práctica directa: un descriptor de **nivel medio** captura bien la fuga de vacío y es
casi ciego al fallo de encendido, cuyos episodios se diluyen en la media de la ventana. La
representación que se elija no es neutral respecto a qué fallos se pueden detectar.

**Qué no podemos afirmar.** Que estas cinco sesiones sean representativas de su condición: es una
sesión por fallo. Tampoco que la firma sea igual en otros regímenes —el termostato, en particular,
no lo es, y eso se ve a continuación—. Y en el fallo de encendido conviene no engañarse: lo que se
ve es una sesión concreta con sus episodios en unos instantes concretos; otra semilla los pondría
en otros."""),
    md("""\
## 8. Una firma que es una ausencia: el termostato

Este es el caso que más enseña, y el que más se ha prestado a interpretaciones apresuradas.

El fallo consiste en imponer un **techo** de 71 °C a la temperatura del refrigerante. Mientras el
motor no habría superado ese techo por sí mismo, el fallo **no impone nada**: la señal de un motor
averiado es idéntica, valor a valor, a la de uno sano.

En los regímenes urbano, autopista y ralentí el motor arranca ya caliente, por encima del techo, de
modo que el recorte actúa desde el primer instante. En **calentamiento** arranca a temperatura
ambiente y tarda minutos en llegar.

Como la muestra versionada no tiene sesiones de calentamiento, se **regeneran** aquí. Conviene ser
preciso sobre qué es esto y qué no es: **no es un escenario nuevo ni un experimento**. Es el mismo
generador, con sus parámetros por omisión y una semilla del laboratorio, reproduciendo el fenómeno
que ya está medido y documentado en `docs/methodology/expresion-efectiva-del-fallo.md`. No se
persiste ningún fichero, no se crea ningún conjunto y no se mide ninguna cifra nueva: se dibuja una
que ya existe. Modalidad de esta sección: **demostración ilustrativa**."""),
    code("""\
from mecanico_ia_exp.obd.synthetic import SessionSpec, generate_session

# Dos sesiones de calentamiento con la MISMA semilla: la única diferencia es la
# condición. Eso es lo que permite comparar trayectorias sin más confusores.
SEMILLA_ILUSTRATIVA = 20260901

sana_w = generate_session(SessionSpec(
    session_id="ilustrativa_sana", regime="warmup", duration_s=600.0,
    seed=SEMILLA_ILUSTRATIVA, fault_id="F00_normal",
))
fallo_w = generate_session(SessionSpec(
    session_id="ilustrativa_termostato", regime="warmup", duration_s=600.0,
    seed=SEMILLA_ILUSTRATIVA, fault_id="F03_thermostat_stuck", fault_onset_s=120.0,
))

TECHO = FAULTS["F03_thermostat_stuck"].default_params["temp_cap_c"]

fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(9.5, 5.4), sharex=True,
                                    height_ratios=[2.1, 1])
# La sana va debajo y más gruesa: durante los primeros minutos las dos
# trayectorias son la MISMA, y si se dibujaran igual de finas la de arriba
# taparía a la de abajo y parecería que solo hay una línea.
arriba.plot(sana_w.timestamp, sana_w.coolant_temperature, color=CATEGORICAL[0],
            label="sin fallo", linewidth=2.6, alpha=0.55)
arriba.plot(fallo_w.timestamp, fallo_w.coolant_temperature, color=CATEGORICAL[1],
            label="termostato bloqueado", linewidth=1.0)
arriba.axhline(TECHO, color="#898781", linestyle=":", linewidth=0.9)
arriba.text(8, TECHO + 1.5, f"techo del fallo: {TECHO:g} °C", fontsize=6.8, color="#52514e")
arriba.axvline(120, color="#898781", linestyle="--", linewidth=0.8)
arriba.text(126, 30, "entrada del fallo", fontsize=6.8, color="#52514e")
arriba.set_ylabel("Temperatura de\\nrefrigerante (°C)", fontsize=7.5)
arriba.legend(loc="lower right", fontsize=7)

# Abajo: la desviación frente al contrafactual, que es cero mientras el fallo no
# impone nada. No es una estimación: es la diferencia con la trayectoria que el
# mismo motor habría seguido con la misma semilla.
abajo.fill_between(fallo_w.timestamp, 0, fallo_w.fault_deviation_max,
                   color=CATEGORICAL[1], alpha=0.35)
abajo.axhline(1.0, color="#898781", linestyle=":", linewidth=0.9)
abajo.text(8, 1.6, "umbral de observabilidad", fontsize=6.5, color="#52514e")
abajo.set_ylabel("Alteración frente al\\ncontrafactual (umbrales)", fontsize=7.5)
abajo.set_xlabel("tiempo desde el arranque (s)")
abajo.set_yscale("symlog", linthresh=1.0)
abajo.set_ylim(bottom=0)

fig.suptitle(
    "El termostato bloqueado no altera nada hasta que el motor alcanza su techo",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E2 generación · DEMOSTRACIÓN ILUSTRATIVA: sesiones generadas en este notebook, "
    f"semilla {SEMILLA_ILUSTRATIVA}, régimen warmup · no son cifras publicadas",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB01-03_termostato_calentamiento",
                 subdirectorio="01_exploracion_obd")
plt.show()

activas = fallo_w[fallo_w.fault_active]
print(f"muestras con el fallo aplicado:   {len(activas)}")
print(f"muestras que alteran la señal:    {int(activas.fault_expressed.sum())} "
      f"({activas.fault_expressed.mean():.0%})")"""),
    md("""\
**Qué muestra.** Arriba, las dos trayectorias son **la misma línea** durante unos trescientos
segundos tras la entrada del fallo, y se separan solo cuando la sana alcanza el techo. Abajo, la
alteración frente al contrafactual es **exactamente cero** en ese tramo.

**Qué podemos interpretar.** La firma de este fallo es una ausencia, y la ausencia solo es
observable cuando hay algo que ausentarse. Durante el calentamiento la etiqueta dice «termostato
bloqueado» y la señal no contiene ninguna información que lo distinga de un motor sano. Ningún
clasificador puede separar dos señales idénticas, y eso ocurriría igual en un coche real.

**Qué no podemos afirmar.** Que esto explique por sí solo los errores que los modelos cometen en esta
condición: lo que establece es que **existe** un tramo sin señal, no cuántos de los errores caen en
él. La identificación una a una exige cruzar las predicciones con la expresión ventana a ventana, y
ese cruce está diseñado y **no ejecutado** (`docs/diseno-pi1/08-analisis-por-fallo.md`).

Y hay algo que específicamente **no** debe concluirse de aquí: que el contexto temporal sea valioso
porque esta condición lo requiera. Es una tentación razonable —la firma es temporal, y el modelo
recurrente obtiene en esta clase 0,8148 frente a 0,7826 del bosque— pero esa diferencia es de 0,03
en una clase de 14 ventanas, medida una sola vez, entre dos modelos que difieren a la vez en
representación y en estimador."""),
    md("""\
## 9. ¿Separa alguna señal por sí sola?

**Qué queremos investigar.** Si existe una señal delatora: un umbral único que clasifique
perfectamente alguna condición. Sería un artefacto del generador y haría trivial el problema.

**Qué datos utilizamos.** Las doce señales sobre las 18 sesiones, muestra a muestra.

**Por qué esta comprobación y no un gráfico.** Un umbral que separe perfectamente existe si y solo si
los rangos de las dos clases son **disjuntos**. Comprobarlo cuesta dos extremos por señal y
condición, y da un sí o un no, no una impresión visual."""),
    code("""\
from mecanico_ia_exp.obd.auditoria import auditar

# La auditoría del generador, la misma que se ejecuta antes de entrenar.
# Doce comprobaciones; aquí se muestran todas, también las que pasan.
for comprobacion in auditar(datos):
    print(comprobacion)"""),
    md("""\
**Qué muestra.** Las doce comprobaciones con su estado. Tres salen `NO_VERIFICABLE` porque esta
muestra no trae manifiesto de procedencia —se generó antes de que existiera— y dos son
`INFORMATIVA` a propósito.

**Qué podemos interpretar.** Ninguna de las doce señales separa por sí sola ninguna de las cinco
condiciones con un solo umbral: el problema no es trivial. Las relaciones entre señales están
presentes con el signo esperado. Y el ralentí sin fallo cae dentro del rango que el manual documenta
para este motor, 640–740 rpm, que es exactamente la comprobación que habría detectado el problema de
`synthetic_v3` el día que se generó.

**Qué no podemos afirmar.** Que no exista una **combinación** de señales que separe trivialmente.
La comprobación es de una señal y un umbral; una regla de dos señales no la detectaría. Tampoco que
el conjunto oficial pase igual: se ha comprobado sobre esta muestra.

Dos comprobaciones merecen comentario porque son informativas y no aprobatorias:

- **La expresión efectiva de los fallos** se mide y se publica, no se aprueba. Una condición que se
  exprese poco no es un defecto del conjunto: es el fenómeno. Lo que sería un defecto es tratar la
  etiqueta como prueba de que el fallo se manifestó.
- **La variabilidad entre sesiones** se informa por el mismo motivo."""),
    md("""\
## 10. Correlaciones: la estructura que un modelo puede explotar

**Qué queremos investigar.** Qué señales se mueven juntas, porque eso determina cuánta información
independiente hay realmente en las doce.

**Qué datos utilizamos.** Las sesiones **sin fallo**, para que la estructura sea la del motor y no
la de las inyecciones.

**Por qué un mapa de calor.** Doce por doce son 66 pares; una tabla sería ilegible y un mapa de
calor deja ver los bloques de un vistazo.

**Qué debemos observar.** Si hay pares con correlación cercana a 1, que indicarían redundancia."""),
    code("""\
import numpy as np

from mecanico_ia_exp.visualization.style import DIVERGING

sanas = datos[datos.fault_id == "F00_normal"]
correlacion = sanas[list(SIGNAL_NAMES)].corr()

fig, eje = plt.subplots(figsize=(7.4, 6.2))
imagen = eje.imshow(correlacion, cmap=DIVERGING, vmin=-1, vmax=1)
eje.set_xticks(range(len(SIGNAL_NAMES)), SIGNAL_NAMES, rotation=55, ha="right", fontsize=7)
eje.set_yticks(range(len(SIGNAL_NAMES)), SIGNAL_NAMES, fontsize=7)
eje.grid(False)
for i in range(len(SIGNAL_NAMES)):
    for j in range(len(SIGNAL_NAMES)):
        valor = correlacion.iloc[i, j]
        if abs(valor) >= 0.55 and i != j:
            eje.text(j, i, f"{valor:.2f}", ha="center", va="center",
                     fontsize=6, color="#0b0b0b")
barra = fig.colorbar(imagen, ax=eje, shrink=0.8)
barra.set_label("coeficiente de Pearson (adimensional)", fontsize=7)
fig.suptitle(
    "Correlación entre señales en sesiones sin fallo",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E4 exploratorio (recalculado) · synthetic_sample, 3 sesiones sanas · "
    "se anotan los pares con |r| ≥ 0,55",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB01-04_correlaciones", subdirectorio="01_exploracion_obd")
plt.show()

altas = (
    correlacion.where(~np.eye(len(correlacion), dtype=bool))
    .stack()
    .sort_values(ascending=False)
)
print("pares más correlacionados:")
print(altas[altas > 0.9].drop_duplicates().to_string())"""),
    md("""\
**Qué muestra.** Un bloque de señales fuertemente acopladas —velocidad, régimen, carga, mariposa,
caudal y presión de colector— y un grupo casi independiente: temperatura de refrigerante,
temperatura de admisión, sonda lambda y los dos ajustes de combustible.

**Qué podemos interpretar.** Las doce señales **no aportan doce dimensiones de información**. La
carga y la posición de la mariposa están correlacionadas por encima de 0,98, y la carga con la
presión de colector por encima de 0,99: en el generador, la mariposa y la presión son funciones
afines de la carga más ruido. Eso tiene una consecuencia metodológica concreta: buena parte de los
139 descriptores de ventana son redundantes entre sí, y una atribución que reparta importancia entre
señales acopladas la reparte de forma inestable.

**Qué no podemos afirmar.** Que esta estructura de correlaciones sea la de un vehículo real. Es la
que el generador construye, por diseño. Tampoco que la redundancia perjudique al bosque aleatorio
—que la tolera bien— ni que la correlación implique que una señal cause la otra: aquí las dos
dependen de la misma variable latente, la demanda del conductor."""),
    md("""\
## 11. Por qué la ventana dura 120 segundos

E5 no eligió el tamaño de ventana por costumbre. Lo midió: para cada duración candidata, cuántas
ventanas salen por sesión y cuánta separabilidad hay entre condiciones. La tabla está versionada."""),
    code("""\
estudio = soporte.tabla("E5_estudio_ventana")
estudio"""),
    code("""\
fig, (izq, der) = plt.subplots(1, 2, figsize=(9.6, 3.6))

# Izquierda: el tamaño del efecto de cada condición frente a la duración.
for color, (fid, grupo) in zip(CATEGORICAL, estudio.groupby("fault_id"), strict=False):
    orden = grupo.sort_values("length_s")
    izq.plot(orden.length_s, orden.best_delta, marker="o", markersize=3.5,
             color=color, label=fid.split("_", 1)[0], linewidth=1.1)
suelo = float(estudio.noise_floor_p90.iloc[0])
izq.axhline(suelo, color="#898781", linestyle=":", linewidth=0.9)
izq.text(12, suelo + 0.02, f"suelo de ruido (p90) = {suelo:.2f}", fontsize=6.5, color="#52514e")
izq.axvline(120, color="#898781", linestyle="--", linewidth=0.9)
izq.set_xlabel("duración de la ventana (s)")
izq.set_ylabel("delta de Cliff del mejor descriptor\\n(adimensional, 0–1)")
izq.set_title("Separabilidad por condición", fontsize=8.5)
izq.legend(fontsize=6.5, ncols=2)

# Derecha: cuántas ventanas quedan. Es la otra mitad del compromiso.
ventanas = estudio.drop_duplicates("length_s").sort_values("length_s")
der.plot(ventanas.length_s, ventanas.n_windows, marker="o", markersize=3.5,
         color=CATEGORICAL[0], linewidth=1.1)
der.axvline(120, color="#898781", linestyle="--", linewidth=0.9)
der.set_xlabel("duración de la ventana (s)")
der.set_ylabel("ventanas obtenidas (recuento)")
der.set_title("Ventanas disponibles", fontsize=8.5)
der.set_yscale("log")

fig.suptitle(
    "Por qué 120 s: más separabilidad cuesta menos ventanas",
    fontsize=10.5, fontweight="bold", x=0.0, ha="left",
)
fig.supxlabel(
    "E5 preprocesamiento · synthetic_v2 · fuente: artifacts/tables/E5_estudio_ventana.csv "
    "(cifras publicadas, no recalculadas aquí) · línea discontinua: duración elegida",
    fontsize=6.5, x=0.0, ha="left",
)
fig.tight_layout()
soporte.exportar(fig, "FIG-NB01-05_estudio_ventana", subdirectorio="01_exploracion_obd")
plt.show()"""),
    md("""\
**Qué muestra.** A la izquierda, el tamaño del efecto del mejor descriptor de cada condición frente
a la duración de la ventana, con el suelo de ruido medido como referencia. A la derecha, cuántas
ventanas quedan —en escala logarítmica, porque el recuento cae un orden de magnitud—.

**Qué podemos interpretar.** Los dos paneles son las dos mitades del mismo compromiso y hay que
leerlos juntos. Cuatro de las cinco condiciones ya superan el suelo de ruido con ventanas cortas;
la que decide es la quinta. Alargar la ventana compra separabilidad y cuesta ventanas, y cada
ventana perdida hace la evaluación más frágil. 120 s es el punto en que las cinco condiciones están
por encima del suelo sin haber vaciado el conjunto.

**Qué no podemos afirmar.** Que 120 s sea óptimo para todas. Para el fallo de encendido, que es
episódico, una ventana larga **diluye** la firma: los pocos segundos alterados se promedian con los
que no lo están. La elección es un compromiso global y perjudica a esa condición en concreto.
Tampoco que el suelo de ruido sea un umbral de detectabilidad: es el percentil 90 del efecto medido
entre pares de sesiones **sanas**, es decir cuánto separa el azar."""),
    md("""\
## 12. El reparto sin fuga

La unidad de reparto es la sesión. No es un detalle de implementación: es lo que separa una
evaluación de un examen con las respuestas."""),
    code("""\
reparto_publicado = soporte.tabla("E5_reparto")
reparto_publicado"""),
    md("""\
**Qué muestra.** Cuántas sesiones y ventanas van a cada partición, por condición, en el conjunto
oficial.

**Qué podemos interpretar.** Ninguna sesión aparece en dos particiones, y cada condición está
presente en las tres. Dos ventanas consecutivas de una misma sesión comparten la mitad de sus
muestras —el paso es de 60 s sobre ventanas de 120 s—, de modo que repartir por ventana habría
filtrado información de entrenamiento a evaluación de forma invisible para cualquier métrica.

**Qué no podemos afirmar.** Que el reparto por sesión elimine toda dependencia. Las sesiones de una
misma condición comparten generador, parametrización y plan: no son independientes en sentido
estadístico, solo disjuntas. La evaluación mide generalización **a sesiones nuevas del mismo
generador**, no a vehículos nuevos."""),
    md("""\
## 13. Las figuras publicadas de E4

Lo anterior es reanálisis sobre una muestra. Estas son las figuras de E4 tal como se publicaron, sin
recalcular: **visualización de evidencia histórica**."""),
    code("""\
from IPython.display import Image, display

for nombre, pie in [
    ("FIG-E4-01_series_normal_vs_fallo",
     "E4 · synthetic_v1 · series normales frente a series con fallo"),
    ("FIG-E4-02_separabilidad",
     "E4 · synthetic_v1 · separabilidad por señal y condición, delta de Cliff"),
]:
    print(pie)
    display(Image(filename=str(soporte.figura(nombre)), width=760))"""),
    md("""\
**Qué muestran.** La primera, las series normales frente a las series con fallo tal como E4 las
publicó. La segunda, el tamaño del efecto por señal y condición.

**Qué podemos interpretar.** Que el hallazgo central de E4 se sostiene: la deriva del caudalímetro
**no se ve en el caudalímetro**. El efecto aparece en los ajustes de combustible, porque la
centralita compensa la subestimación del aire inyectando más. La firma de un fallo no está
necesariamente en la señal del componente que falla.

**Qué no podemos afirmar.** Estas figuras salen de `synthetic_v1`, con 36 sesiones, y no de
`synthetic_v2`. No deben leerse como si fueran del conjunto oficial."""),
    md("""\
## 14. Resultados negativos y limitaciones

**Lo que no salió como se esperaba, o conviene decir:**

1. **El fallo de encendido apenas altera la señal.** Con episodios de 1 a 3 s y una tasa de
   aparición del 2 % por segundo, una fracción muy pequeña de las muestras etiquetadas difiere de su
   contrafactual. La etiqueta cubre la sesión; el fenómeno, no.
2. **El termostato no es observable en calentamiento** hasta que el motor alcanza su techo.
3. **Seis de las doce señales son casi redundantes entre sí.** La dimensionalidad efectiva es menor
   que la nominal.
4. **La muestra versionada no cubre el régimen de calentamiento.** Las sesiones usadas aquí para
   ilustrarlo se generaron en el notebook y están declaradas como ilustrativas.
5. **Las cifras de este notebook no son las publicadas de E4.** Se recalculan sobre otra muestra, y
   el notebook lo declara en su modalidad.

**Limitaciones del diseño que no se pueden resolver mirando más datos:**

- El conjunto es sintético. La validez externa no está establecida y no se afirma.
- El generador es paramétrico y no está calibrado contra datos reales; sus constantes sí contra el
  manual, que es distinto.
- Las sesiones de una condición no son independientes entre sí."""),
    md("""\
## 15. Discusión

Lo que esta exploración aporta a la pregunta de investigación es una respuesta parcial y una
advertencia.

**La respuesta parcial.** Hay estructura: las señales se relacionan como el modelo físico aproximado
dice, las condiciones desplazan las señales que sus fichas declaran, y ninguna condición se separa
trivialmente. Un modelo de diagnóstico tiene algo que aprender, y eso es la precondición de PI.1.

**La advertencia, que es lo más útil.** La relación entre **etiqueta** y **señal** no es uno a uno.
Hay ventanas etiquetadas con un fallo que no contienen información del fallo. Un modelo que falle en
ellas no está equivocándose: está respondiendo correctamente a lo que ve. Y una métrica agregada que
las cuente como errores está midiendo, en parte, el límite físico del fenómeno y no la calidad del
modelo.

Esto conecta con el resto del trabajo de forma directa. La capacidad de **abstenerse** —PI.3— tiene
aquí su justificación empírica: existen situaciones en que la evidencia es genuinamente insuficiente
por la física del problema, no por un defecto del sistema. Un sistema que explicara con confianza en
esas ventanas estaría inventando."""),
    md("""\
## 16. Conclusiones de este notebook

**Qué aprendimos.** Que las doce señales tienen la estructura que el diseño del generador declara;
que las cinco condiciones producen firmas de **cinco formas temporales distintas**, lo que hace que
la elección de representación no sea neutral; y que al menos dos condiciones tienen ventanas
etiquetadas sin señal observable del fallo.

**Qué hipótesis recibió apoyo.** Que las condiciones desplazan las señales declaradas sin que
ninguna señal las separe por sí sola con un umbral.

**Qué no recibió apoyo.** Nada se refuta aquí, pero queda matizado que el desplazamiento sea
observable **en toda la ventana de actividad del fallo**: en dos de las cinco condiciones, no lo es.

**Qué permanece sin demostrar.** Si estas firmas aparecen igual en telemetría real. Si la forma
temporal de la firma hace que una representación secuencial sea preferible: eso cambia dos cosas a
la vez y se trata en `02_comparacion_modelos.ipynb`.

**Cómo contribuye al TFM.** Es la base empírica del capítulo de datos y la justificación del tamaño
de ventana y del reparto por sesión."""),
    md("""\
## 17. Reproducibilidad

| | |
|---|---|
| **Python** | 3.11 |
| **Dependencias** | `uv sync --extra nb` |
| **Datos** | `data/samples/synthetic_sample.parquet` (versionado) y dos sesiones generadas en el notebook |
| **Semilla** | 20260901 para las sesiones ilustrativas |
| **Configuración** | ventana 120 s, paso 60 s (la de E5) |
| **Commit** | el que imprime la celda del apartado 4 |
| **Tiempo** | menos de dos minutos |
| **Memoria** | por debajo de 1 GB |
| **Recursos** | CPU; no hace falta acelerador |
| **Artefactos que produce** | cinco figuras en `notebooks/salida/01_exploracion_obd/`, en PNG y SVG |

**Qué se reproduce y qué no.** Las sesiones ilustrativas de calentamiento se regeneran idénticas:
el generador es determinista por semilla. Las cifras de E4 y E5 **no se reproducen**, se leen de sus
tablas versionadas. Las figuras de E4 se muestran tal cual, sin recalcularlas.

## 18. Referencias y trazabilidad

**Dónde aparece esto en la memoria.** El reparto de la muestra es la **Figura 5.1** y la separabilidad por señal, la **Figura 5.2**, las dos en el análisis descriptivo del capítulo 5. Las doce señales y las cinco condiciones están tabuladas en el anexo A, apartados A.2 y A.3, y la serie testigo de cada fallo es la **Figura A.1**.

- `docs/experiments/E2_datos_sinteticos.md`, `E4_eda_temporal.md`, `E5_preprocesamiento.md`
- `artifacts/tables/E4_descriptivos.csv`, `E4_separabilidad.csv`, `E5_estudio_ventana.csv`, `E5_reparto.csv`
- `artifacts/figures/FIG-E4-01_series_normal_vs_fallo.png`, `FIG-E4-02_separabilidad.png`
- `configs/calibracion_mazda3_bk.yaml` — cada constante del generador con su cita
- `src/mecanico_ia_exp/obd/` — generador, catálogo de fallos, auditoría de doce comprobaciones
- `docs/methodology/expresion-efectiva-del-fallo.md` — la definición de alteración observable
- `docs/diseno-pi1/08-analisis-por-fallo.md` — el cruce pendiente entre errores y expresión"""),
]

if __name__ == "__main__":
    escribir("01_exploracion_obd.ipynb", CELDAS)
