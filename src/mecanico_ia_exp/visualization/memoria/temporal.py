"""Las figuras que necesitan el eje del tiempo: forma del fallo y contrafactual.

Las tres leen el artefacto derivado de `scripts/contrafactual_t2.py` o el
conjunto procesado `synthetic_v2`. Ninguna ejecuta un experimento, ninguna
genera una serie nueva y ninguna escribe un valor a mano.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.features.temporal import FEATURE_NAMES
from mecanico_ia_exp.obd.expresion import RATIO_DECLARADO
from mecanico_ia_exp.obd.faults import FAULTS
from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    BASELINE,
    CATEGORICAL,
    COLOR_MAL,
    CONDICION,
    CONTRAFACTUAL,
    INK_SECONDARY,
    estilo_para_impresion,
    numero,
    panel,
)

#: Las cinco condiciones de fallo, en el orden del catálogo.
FALLOS: tuple[str, ...] = tuple(c for c in CONDICION if c != "F00_normal")

#: Múltiplos del umbral declarado con que se relee la expresión del fallo. El
#: primero es el criterio vigente y los otros tres comprueban si el recuento
#: depende de él. El dato guardado está en unidades del umbral, de modo que
#: releerlo con otra exigencia no regenera nada.
MULTIPLOS: tuple[float, ...] = (1.0, 2.5, 5.0, 10.0)
EXIGENCIAS: tuple[float, ...] = tuple(RATIO_DECLARADO * m for m in MULTIPLOS)


def _contrafactual() -> pd.DataFrame:
    if not CONTRAFACTUAL.is_file():
        msg = (
            f"falta el artefacto del análisis contrafactual: "
            f"{CONTRAFACTUAL.relative_to(paths.ROOT)}. "
            "Lo produce `uv run python scripts/contrafactual_t2.py`."
        )
        raise FileNotFoundError(msg)
    return pd.read_parquet(CONTRAFACTUAL)


def recuento_de_expresion() -> pd.DataFrame:
    """Cuántas muestras del tramo con fallo se expresan, según cuánto se exija.

    Es la tabla que acompaña a la figura de la forma del fallo, y la que dice si
    el recuento es un hecho o una consecuencia del umbral elegido.
    """
    tabla = _contrafactual()
    con_fallo = tabla[tabla.traza == "con_fallo"]
    filas: list[dict[str, object]] = []
    for fault_id in FALLOS:
        sesion = con_fallo[con_fallo.fault_id == fault_id]
        if sesion.empty:
            continue
        inicio = float(sesion.timestamp[sesion.fault_active].min())
        tramo = sesion[sesion.timestamp >= inicio]
        fila: dict[str, object] = {
            "fault_id": fault_id,
            "session_id": str(sesion.session_id.iloc[0]),
            "regime": str(sesion.regime.iloc[0]),
            "muestras_del_tramo": len(tramo),
        }
        for exigencia in EXIGENCIAS:
            umbral = exigencia / RATIO_DECLARADO
            fila[f"expresa_r{exigencia:.2f}"] = int((tramo.fault_deviation_max >= umbral).sum())
        filas.append(fila)
    return pd.DataFrame(filas)


def fig_forma_del_fallo() -> Figure:
    """Cuánto se aparta cada fallo de su propia trayectoria sana, instante a instante.

    La magnitud dibujada es la desviación frente al contrafactual **en unidades
    del umbral de observabilidad**, de modo que las cinco condiciones son
    comparables entre sí aunque sus señales no lo sean. El eje es simétrico y
    logarítmico porque el recorrido va de cero exacto a más de cien.
    """
    tabla = _contrafactual()
    con_fallo = tabla[tabla.traza == "con_fallo"]
    sin_fallo = tabla[tabla.traza == "contrafactual"]

    estilo_para_impresion()
    fig, ejes = plt.subplots(
        2, 1, figsize=(ANCHO_DE_PAGINA, 5.6), gridspec_kw={"height_ratios": [1.45, 1.0]}
    )

    for i, fault_id in enumerate(FALLOS):
        sesion = con_fallo[con_fallo.fault_id == fault_id]
        if sesion.empty:
            continue
        ejes[0].plot(
            sesion.timestamp.to_numpy(float),
            sesion.fault_deviation_max.to_numpy(float),
            color=CATEGORICAL[i],
            lw=1.0,
            label=CONDICION[fault_id],
        )
    ejes[0].axhline(1.0, color=INK_SECONDARY, lw=0.8, ls="--")
    ejes[0].annotate(
        "umbral de observabilidad",
        xy=(8.0, 1.25),
        fontsize=6.5,
        color=INK_SECONDARY,
    )
    ejes[0].axvline(120.0, color=BASELINE, lw=0.9)
    ejes[0].annotate(
        "entra el fallo",
        xy=(126.0, 0.012),
        fontsize=6.5,
        color=INK_SECONDARY,
    )
    ejes[0].set_yscale("symlog", linthresh=1.0)
    ejes[0].set_ylim(0.0, float(con_fallo.fault_deviation_max.max()) * 2.0)
    ejes[0].set_xlim(0.0, 600.0)
    ejes[0].set_ylabel("desviación frente al\ncontrafactual (umbrales)")
    panel(ejes[0], "a")
    ejes[0].legend(loc="upper left", bbox_to_anchor=(0.0, -0.22), ncol=3, fontsize=6.8)
    ejes[0].grid(visible=True, axis="y")
    ejes[0].set_axisbelow(True)

    # Abajo, el fallo de encendido en su propia escala: es el único cuya
    # trayectoria vuelve exactamente a la sana entre episodio y episodio.
    misfire = con_fallo[con_fallo.fault_id == "F05_misfire"]
    # El contrafactual se selecciona por **sesión**, no por `fault_id`: todas las
    # trazas contrafactuales llevan la condición sin fallo, de modo que filtrar
    # por ella devolvería las cinco y compararía sesiones distintas.
    sano = sin_fallo[sin_fallo.session_id == str(misfire.session_id.iloc[0])]
    ejes[1].plot(
        sano.timestamp.to_numpy(float),
        sano.rpm.to_numpy(float),
        color=BASELINE,
        lw=2.0,
        label="contrafactual: la misma sesión sin el fallo",
    )
    ejes[1].plot(
        misfire.timestamp.to_numpy(float),
        misfire.rpm.to_numpy(float),
        color=COLOR_MAL,
        lw=0.9,
        label="con el fallo de encendido",
    )
    episodios = misfire[misfire.fault_expressed]
    ejes[1].plot(
        episodios.timestamp.to_numpy(float),
        episodios.rpm.to_numpy(float),
        "o",
        ms=2.6,
        color=COLOR_MAL,
    )
    ejes[1].set_xlim(0.0, 600.0)
    ejes[1].set_xlabel("tiempo de la sesión (s)")
    ejes[1].set_ylabel("régimen (min⁻¹)")
    panel(ejes[1], "b")
    ejes[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.52), ncol=2, fontsize=6.8)
    ejes[1].grid(visible=True, axis="y")
    ejes[1].set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_pareja_contrafactual() -> Figure:
    """Las dos trayectorias de cada condición, en unidades físicas y superpuestas.

    Una fila por condición, con la señal que más se aparta de su contrafactual.
    Es la figura que hace visible el mecanismo: antes del instante de entrada las
    dos líneas son **la misma**, y no parecidas.
    """
    tabla = _contrafactual()
    estilo_para_impresion()
    fig, ejes = plt.subplots(len(FALLOS), 1, figsize=(ANCHO_DE_PAGINA, 7.2), sharex=True)

    for letra, (eje, fault_id) in zip("abcde", zip(ejes, FALLOS, strict=True), strict=True):
        con = tabla[(tabla.traza == "con_fallo") & (tabla.fault_id == fault_id)]
        sesion = str(con.session_id.iloc[0])
        sin = tabla[(tabla.traza == "contrafactual") & (tabla.session_id == sesion)]
        expresadas = con[con.fault_expressed]
        señal = (
            str(expresadas.fault_deviation_signal.value_counts().index[0])
            if not expresadas.empty
            else str(FAULTS[fault_id].affected_signals[0])
        )
        eje.plot(
            sin.timestamp.to_numpy(float),
            sin[señal].to_numpy(float),
            color=BASELINE,
            lw=1.2,
            label="sin el fallo (contrafactual)",
        )
        eje.plot(
            con.timestamp.to_numpy(float),
            con[señal].to_numpy(float),
            color=CATEGORICAL[FALLOS.index(fault_id)],
            lw=0.9,
            label="con el fallo",
        )
        inicio = float(con.timestamp[con.fault_active].min())
        eje.axvline(inicio, color=INK_SECONDARY, lw=0.8, ls=":")
        eje.set_ylabel(señal, fontsize=7)
        # La condición y el régimen son la categoría del panel, no un título:
        # sin ellos no se sabe qué sesión se está mirando. El recuento de
        # muestras alteradas va al pie de la figura, en el documento.
        eje.set_title(
            f"({letra}) {CONDICION[fault_id]} · {con.regime.iloc[0]!s}",
            fontsize=8,
            fontweight="bold",
            loc="left",
            pad=4,
        )
        eje.grid(visible=True, axis="y")
        eje.set_axisbelow(True)

    ejes[0].legend(loc="upper left", fontsize=6.8, ncol=2)
    ejes[-1].set_xlabel("tiempo de la sesión (s)")
    ejes[-1].set_xlim(0.0, 600.0)
    fig.tight_layout()
    return fig


def fig_ventana_y_descriptor() -> Figure:
    """Lo que el modelo recibe frente a lo que ocurrió dentro de la ventana.

    Tres paneles sobre la misma ventana de fallo de encendido: la sesión con la
    ventana señalada, la ventana tal como entra al modelo, y los descriptores
    que de ella salen comparados con los de las ventanas sin fallo.
    """
    x = np.load(paths.DATA_PROCESSED / "synthetic_v2_x.npy")
    rasgos = np.load(paths.DATA_PROCESSED / "synthetic_v2_features.npy")
    meta = pd.read_parquet(paths.DATA_PROCESSED / "synthetic_v2_meta.parquet")
    tabla = _contrafactual()

    # La ventana: la primera de entrenamiento etiquetada como fallo de encendido
    # en la sesión que el análisis contrafactual ya seleccionó, de modo que las
    # dos figuras hablan de la misma sesión.
    sesion = str(
        tabla[(tabla.traza == "con_fallo") & (tabla.fault_id == "F05_misfire")].session_id.iloc[0]
    )
    candidatas = meta[(meta.session_id == sesion) & (meta.label == "F05_misfire")]
    if candidatas.empty:
        msg = f"ninguna ventana de fallo de encendido en {sesion}"
        raise ValueError(msg)
    indice = int(candidatas.index[0])
    fila = meta.loc[indice]
    inicio = float(meta.t_start.to_numpy(float)[indice])
    fin = float(meta.t_end.to_numpy(float)[indice])

    serie = tabla[(tabla.traza == "con_fallo") & (tabla.session_id == sesion)]
    canal = 0  # rpm es la primera señal del orden declarado
    ventana = x[indice, :, canal]

    estilo_para_impresion()
    fig, ejes = plt.subplots(
        3, 1, figsize=(ANCHO_DE_PAGINA, 6.4), gridspec_kw={"height_ratios": [1.0, 1.0, 1.1]}
    )

    ejes[0].plot(
        serie.timestamp.to_numpy(float), serie.rpm.to_numpy(float), color=COLOR_MAL, lw=0.8
    )
    ejes[0].axvspan(inicio, fin, color=CATEGORICAL[3], alpha=0.22)
    ejes[0].set_xlim(0.0, 600.0)
    ejes[0].set_ylabel("régimen (min⁻¹)")
    panel(ejes[0], "a")
    ejes[0].grid(visible=True, axis="y")
    ejes[0].set_axisbelow(True)

    t = np.arange(len(ventana)) + inicio
    ejes[1].plot(t, ventana, color=COLOR_MAL, lw=1.1, label="la ventana que entra al modelo")
    media = float(ventana.mean())
    desviacion = float(ventana.std())
    ejes[1].axhline(media, color=INK_SECONDARY, lw=1.0, ls="--", label="su media")
    ejes[1].fill_between(
        t,
        media - desviacion,
        media + desviacion,
        color=INK_SECONDARY,
        alpha=0.12,
        label="± su desviación típica",
    )
    en_ventana = serie[
        (serie.timestamp >= inicio) & (serie.timestamp < fin) & serie.fault_expressed
    ]
    if not en_ventana.empty:
        ejes[1].plot(
            en_ventana.timestamp.to_numpy(float),
            en_ventana.rpm.to_numpy(float),
            "o",
            ms=4.0,
            color=CATEGORICAL[1],
            label=f"{len(en_ventana)} muestras alteradas por el fallo",
        )
    ejes[1].set_ylabel("régimen (min⁻¹)")
    panel(ejes[1], "b")
    ejes[1].legend(loc="upper left", bbox_to_anchor=(0.0, -0.18), fontsize=6.5, ncol=2)
    ejes[1].grid(visible=True, axis="y")
    ejes[1].set_axisbelow(True)

    # Los descriptores de régimen de esta ventana, frente a las ventanas SIN
    # FALLO DEL MISMO RÉGIMEN. Compararlas con todas las ventanas sin fallo
    # mediría el régimen de conducción y no el fallo: la media de régimen en
    # ralentí es 690 y en el conjunto entero 1371.
    nombres = ("rpm_mean", "rpm_std", "rpm_min", "rpm_delta_min", "rpm_n_events")
    regimen = str(fila.regime)
    referencia = ((meta.label == "F00_normal") & (meta.regime == regimen)).to_numpy()
    posiciones = [FEATURE_NAMES.index(n) for n in nombres]
    valores = rasgos[indice, posiciones]
    base = rasgos[referencia][:, posiciones]
    medianas = np.median(base, axis=0)
    # Escala robusta: la desviación absoluta mediana, reescalada para que en una
    # normal equivalga a la desviación típica. Si es cero, se usa la típica.
    mad = np.median(np.abs(base - medianas), axis=0) * 1.4826
    escala = np.where(mad > 0, mad, base.std(axis=0))
    apartamiento = np.where(escala > 0, (valores - medianas) / escala, 0.0)

    y = np.arange(len(nombres))
    colores = [COLOR_MAL if abs(v) >= 3.0 else BASELINE for v in apartamiento]
    ejes[2].barh(y, apartamiento, color=colores, height=0.58)
    for i, (a, v, med) in enumerate(zip(apartamiento, valores, medianas, strict=True)):
        ejes[2].text(
            a + (0.25 if a >= 0 else -0.25),
            i,
            f"{numero(float(v), 1)} frente a {numero(float(med), 1)}",
            va="center",
            ha="left" if a >= 0 else "right",
            fontsize=6.5,
            color=INK_SECONDARY,
        )
    ejes[2].axvline(0.0, color=INK_SECONDARY, lw=0.8)
    ejes[2].set_yticks(y)
    ejes[2].set_yticklabels(nombres, fontsize=7)
    ejes[2].invert_yaxis()
    ejes[2].set_xlim(-14.0, 11.0)
    ejes[2].set_xlabel(
        f"cuánto se aparta de las {int(referencia.sum())} ventanas sin fallo del mismo "
        "régimen (escalas robustas)"
    )
    panel(ejes[2], "c")
    ejes[2].grid(visible=True, axis="x")
    ejes[2].set_axisbelow(True)
    fig.tight_layout()
    return fig
