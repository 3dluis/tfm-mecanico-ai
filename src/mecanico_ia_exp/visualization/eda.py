"""Figuras del análisis exploratorio.

Cada función responde a una pregunta declarada en su docstring. Una figura que
no responda a una pregunta no entra en la memoria.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from mecanico_ia_exp.data.exploration import (
    correlation_matrix,
    cross_correlation,
    separability,
)
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import SessionSpec, generate_session
from mecanico_ia_exp.visualization.style import (
    BASELINE,
    COLOR_FALLO,
    COLOR_NORMAL,
    DIVERGING,
    INK_MUTED,
    INK_SECONDARY,
    SEQUENTIAL,
    apply_style,
    save,
)

#: Señal más representativa de cada condición, según su ficha de fallo.
SENAL_TESTIGO: dict[str, str] = {
    "F01_vacuum_leak": "stft_bank1",
    "F02_maf_drift": "maf",
    "F03_thermostat_stuck": "coolant_temperature",
    "F04_o2_lag": "oxygen_sensor",
    "F05_misfire": "rpm",
}


def _titulo(ax: Axes, texto: str, subtitulo: str = "") -> None:
    ax.set_title(texto, color="#0b0b0b", pad=10 if subtitulo else 6)
    if subtitulo:
        ax.text(
            0.0,
            1.02,
            subtitulo,
            transform=ax.transAxes,
            fontsize=7,
            color=INK_SECONDARY,
            va="bottom",
        )


SEMILLA_FIGURA = 4242
DURACION_FIGURA_S = 600.0
INICIO_FALLO_S = 120.0


def fig_series_normal_vs_fallo(_datos: pd.DataFrame, destino: Path) -> Path:
    """¿Se distingue una sesión con fallo de una normal mirando la señal testigo?

    La comparación es **pareada**: misma semilla, mismo régimen y mismo perfil de
    conducción, con y sin el fallo. Sin parear, la mayor parte de la diferencia
    visible sería la forma de conducir y no la condición, y la figura afirmaría
    algo que los datos no sostienen.

    Por eso esta figura genera sus propias sesiones en lugar de tomarlas del
    conjunto: el conjunto asigna una semilla distinta a cada sesión, que es lo
    correcto para entrenar y lo inadecuado para comparar.
    """
    apply_style()

    fig, axes = plt.subplots(5, 1, figsize=(7.2, 9.6), sharex=True)
    for ax, (fault_id, senal) in zip(axes, SENAL_TESTIGO.items(), strict=True):
        base = SessionSpec(
            session_id="par_normal",
            regime="urban",
            duration_s=DURACION_FIGURA_S,
            seed=SEMILLA_FIGURA,
        )
        con_fallo = SessionSpec(
            session_id="par_fallo",
            regime="urban",
            duration_s=DURACION_FIGURA_S,
            seed=SEMILLA_FIGURA,
            fault_id=fault_id,
            fault_onset_s=INICIO_FALLO_S,
        )
        serie_normal = generate_session(base)
        serie_fallo = generate_session(con_fallo)

        ax.plot(
            serie_normal["timestamp"],
            serie_normal[senal],
            color=COLOR_NORMAL,
            lw=1.0,
            alpha=0.9,
            label="sin fallo",
        )
        ax.plot(
            serie_fallo["timestamp"],
            serie_fallo[senal],
            color=COLOR_FALLO,
            lw=1.2,
            label="con fallo",
        )
        ax.axvline(INICIO_FALLO_S, color=INK_MUTED, lw=0.8, ls=(0, (3, 3)))
        ax.annotate(
            "entra el fallo",
            xy=(INICIO_FALLO_S, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(3, -9),
            textcoords="offset points",
            fontsize=6.5,
            color=INK_MUTED,
        )
        ax.set_ylabel(senal, fontsize=7)
        # El nombre de la condición va en el título del panel; repetirlo en la
        # leyenda solo añadiría ruido sobre los datos.
        _titulo(ax, FAULTS[fault_id].fault_name)

    axes[-1].set_xlabel("tiempo de sesión (s)")

    # Una sola leyenda para toda la figura, fuera del área de datos: dentro
    # tapaba las series en cuatro de los cinco paneles.
    manejadores, etiquetas = axes[0].get_legend_handles_labels()
    fig.legend(
        manejadores,
        etiquetas,
        loc="upper right",
        bbox_to_anchor=(0.99, 0.982),
        ncol=2,
    )
    fig.text(
        0.02,
        0.988,
        "Señal testigo de cada condición, comparación pareada",
        fontsize=11,
        weight="bold",
        va="top",
    )
    fig.text(
        0.02,
        0.967,
        "Misma semilla y mismo régimen urbano con y sin fallo. Antes de la marca "
        "las dos series coinciden exactamente: toda divergencia posterior es la condición.",
        fontsize=7.5,
        color=INK_SECONDARY,
        va="top",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.952))
    return save(fig, destino)


def fig_separabilidad(datos: pd.DataFrame, destino: Path) -> Path:
    """¿Qué señal separa cada condición, y lo hace en nivel o en dispersión?

    Dos paneles con el mismo mapa divergente. El gris central es ausencia de
    efecto; el azul y el rojo, direcciones opuestas. Mirar solo el panel de
    nivel llevaría a descartar señales que sí separan.
    """
    apply_style()
    tabla = separability(datos)
    fallos = sorted(tabla["fault_id"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=True)
    for ax, columna, titulo in zip(
        axes,
        ("delta_level", "delta_dispersion"),
        ("Nivel (media del bloque)", "Dispersión (desviación del bloque)"),
        strict=True,
    ):
        matriz = (
            tabla.pivot(index="signal", columns="fault_id", values=columna)
            .reindex(index=list(SIGNAL_NAMES), columns=fallos)
            .to_numpy()
        )
        im = ax.imshow(matriz, cmap=DIVERGING, vmin=-1.0, vmax=1.0, aspect="auto")
        ax.set_xticks(range(len(fallos)))
        ax.set_xticklabels([f.split("_", 1)[0] for f in fallos], fontsize=7)
        ax.set_yticks(range(len(SIGNAL_NAMES)))
        ax.set_yticklabels(SIGNAL_NAMES, fontsize=7)
        ax.grid(visible=False)
        # Etiqueta directa sobre cada celda con efecto apreciable: el contraste
        # del mapa no basta por sí solo para leer un valor.
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                v = matriz[i, j]
                if abs(v) >= 0.33:
                    ax.text(
                        j,
                        i,
                        f"{v:+.2f}",
                        ha="center",
                        va="center",
                        fontsize=6.2,
                        color="#0b0b0b",
                    )
        _titulo(ax, titulo)

    barra = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
    barra.set_label("delta de Cliff frente a la condición normal", fontsize=7.5)
    barra.outline.set_edgecolor(BASELINE)
    fig.suptitle(
        "Separabilidad de cada señal por condición",
        x=0.02,
        ha="left",
        fontsize=11,
        weight="bold",
    )
    fig.text(
        0.02,
        0.905,
        "Se etiquetan las celdas con efecto medio o mayor. La sonda lambda no "
        "separa en nivel y separa por completo en dispersión.",
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    return save(fig, destino)


def fig_correlaciones(datos: pd.DataFrame, destino: Path) -> Path:
    """¿Qué señales aportan información redundante entre sí?

    Correlación de Spearman: varias relaciones del motor son monótonas pero no
    lineales, y Pearson las subestimaría.
    """
    apply_style()
    matriz = correlation_matrix(datos)
    valores = matriz.to_numpy()

    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    im = ax.imshow(valores, cmap=DIVERGING, vmin=-1.0, vmax=1.0)
    ax.set_xticks(range(len(SIGNAL_NAMES)))
    ax.set_xticklabels(SIGNAL_NAMES, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(SIGNAL_NAMES)))
    ax.set_yticklabels(SIGNAL_NAMES, fontsize=7)
    ax.grid(visible=False)
    for i in range(valores.shape[0]):
        for j in range(valores.shape[1]):
            if i != j and abs(valores[i, j]) >= 0.7:
                ax.text(
                    j,
                    i,
                    f"{valores[i, j]:+.2f}",
                    ha="center",
                    va="center",
                    fontsize=6.0,
                    color="#0b0b0b",
                )
    barra = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    barra.set_label("rho de Spearman", fontsize=7.5)
    barra.outline.set_edgecolor(BASELINE)
    _titulo(
        ax,
        "Correlación entre señales",
        "Se etiquetan las parejas con |rho| >= 0,70. Conjunto completo, todas las condiciones.",
    )
    return save(fig, destino)


def fig_distribuciones(datos: pd.DataFrame, destino: Path) -> Path:
    """¿Cuánto se solapan las distribuciones normal y con fallo?

    El solape es lo que un clasificador tendrá que resolver. Una separación
    visible aquí no garantiza que el modelo acierte, pero su ausencia sí
    anticipa dificultad.
    """
    apply_style()
    normal = datos[datos["fault_id"] == NORMAL_ID]

    fig, axes = plt.subplots(2, 3, figsize=(10.4, 5.6))
    for ax, (fault_id, senal) in zip(axes.flat, SENAL_TESTIGO.items(), strict=False):
        activo = datos[(datos["fault_id"] == fault_id) & datos["fault_active"]]
        bins = np.histogram_bin_edges(
            np.concatenate([normal[senal].to_numpy(), activo[senal].to_numpy()]), bins=45
        )
        ax.hist(
            normal[senal],
            bins=bins,
            color=COLOR_NORMAL,
            alpha=0.75,
            label="normal",
            density=True,
            edgecolor="none",
        )
        ax.hist(
            activo[senal],
            bins=bins,
            color=COLOR_FALLO,
            alpha=0.70,
            label="con fallo",
            density=True,
            edgecolor="none",
        )
        ax.set_xlabel(senal, fontsize=7.5)
        ax.set_yticks([])
        _titulo(ax, fault_id.split("_", 1)[0] + " " + FAULTS[fault_id].fault_name[:26])
        ax.legend(loc="upper right")

    axes.flat[-1].axis("off")
    fig.suptitle(
        "Distribución de la señal testigo: normal frente a fallo activo",
        x=0.02,
        ha="left",
        fontsize=11,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    return save(fig, destino)


def fig_correlacion_cruzada(datos: pd.DataFrame, destino: Path) -> Path:
    """¿La mariposa se adelanta al régimen, o se mueven a la vez?

    Un desfase distinto de cero distinguiría una respuesta de una coincidencia.
    Una sola serie: el título la nombra y no hace falta leyenda.
    """
    apply_style()
    normal = datos[(datos["fault_id"] == NORMAL_ID) & (datos["regime"] == "urban")]
    sesion = normal[normal["session_id"] == normal["session_id"].iloc[0]]
    tabla = cross_correlation(
        sesion["throttle_position"].to_numpy(), sesion["rpm"].to_numpy(), max_lag=30
    )

    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.axhline(0.0, color=BASELINE, lw=0.7)
    ax.plot(tabla["lag"], tabla["r"], color=COLOR_NORMAL, lw=1.6)
    desfases = tabla["lag"].to_numpy(dtype=float)
    erres = tabla["r"].to_numpy(dtype=float)
    mejor = int(np.nanargmax(erres))
    desfase = float(desfases[mejor])
    r_mejor = float(erres[mejor])
    ax.plot([desfase], [r_mejor], "o", color=COLOR_NORMAL, ms=6)
    ax.annotate(
        f"máximo en desfase {desfase:.0f} s (r = {r_mejor:.2f})",
        xy=(desfase, r_mejor),
        xytext=(8, -14),
        textcoords="offset points",
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    ax.set_xlabel("desfase aplicado al régimen (s)")
    ax.set_ylabel("correlación")
    ax.grid(visible=True, axis="both")
    _titulo(
        ax,
        "Correlación cruzada entre mariposa y régimen",
        "Sesión urbana sin fallo. Un desfase positivo indicaría que el régimen va retrasado.",
    )
    return save(fig, destino)


def fig_balance(datos: pd.DataFrame, destino: Path) -> Path:
    """¿Está equilibrado el conjunto, por condición y por régimen?

    Un desequilibrio no declarado se confunde después con un resultado.
    """
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4))

    por_condicion = datos.groupby("fault_id")["session_id"].nunique().sort_index()
    ejes = axes[0]
    barras = ejes.bar(
        range(len(por_condicion)),
        por_condicion.to_numpy(),
        color=SEQUENTIAL(0.55),
        width=0.68,
    )
    ejes.bar_label(barras, fontsize=7, color=INK_SECONDARY, padding=2)
    ejes.set_xticks(range(len(por_condicion)))
    ejes.set_xticklabels([i.split("_", 1)[0] for i in por_condicion.index], fontsize=7)
    ejes.set_ylabel("sesiones")
    _titulo(ejes, "Por condición", "Equilibrio perfecto: es lo que afecta a las métricas.")

    por_regimen = datos.groupby("regime")["session_id"].nunique().sort_values()
    ejes = axes[1]
    barras = ejes.barh(
        range(len(por_regimen)),
        por_regimen.to_numpy(),
        color=SEQUENTIAL(0.55),
        height=0.62,
    )
    ejes.bar_label(barras, fontsize=7, color=INK_SECONDARY, padding=3)
    ejes.set_yticks(range(len(por_regimen)))
    ejes.set_yticklabels(por_regimen.index, fontsize=7)
    ejes.set_xlabel("sesiones")
    ejes.grid(visible=True, axis="x")
    _titulo(ejes, "Por régimen", "Desequilibrado por el reparto cíclico; se declara.")

    fig.suptitle("Composición del conjunto sintético", x=0.02, ha="left", fontsize=11, weight="600")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return save(fig, destino)
