"""Figuras del preprocesamiento."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from mecanico_ia_exp.visualization.style import (
    CATEGORICAL,
    INK_MUTED,
    INK_SECONDARY,
    apply_style,
    save,
)


def fig_estudio_ventana(estudio: pd.DataFrame, destino: Path) -> Path:
    """¿Qué longitud de ventana sostiene evidencia para cada condición?

    El eje vertical es el mayor tamaño de efecto entre 139 descriptores. Ese
    máximo está inflado por construcción --con suficientes comparaciones algo
    destaca siempre-- así que se dibuja junto a su suelo de ruido, medido
    dividiendo la condición normal contra sí misma.

    Lo que está por debajo de la banda gris no es evidencia de nada.
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 4.6))

    suelo = estudio.groupby("length_s")["noise_floor_p90"].first().sort_index()
    ax.fill_between(
        suelo.index,
        0.0,
        suelo.to_numpy(),
        color=INK_MUTED,
        alpha=0.16,
        linewidth=0,
        label="suelo de ruido (p90)",
    )
    ax.plot(suelo.index, suelo.to_numpy(), color=INK_MUTED, lw=1.0, ls=(0, (3, 3)))

    # Marcador distinto por condición: F01 y F04 valen exactamente 1,00 en las
    # cuatro longitudes, así que sus líneas se superponen por completo. Sin una
    # segunda vía de identificación, una de las dos sería invisible y el lector
    # concluiría que solo hay cuatro condiciones.
    marcadores = ("o", "s", "^", "D", "v")
    trazos = ((0, ()), (0, (5, 1.5)), (0, ()), (0, (1.5, 1.5)), (0, ()))
    etiquetas_derecha: list[tuple[float, str, str]] = []

    for i, (clave, grupo) in enumerate(estudio.groupby("fault_id")):
        # La clave de agrupación llega con tipo abierto; se fija a texto.
        fault_id = str(clave)
        grupo = grupo.sort_values("length_s")
        color = CATEGORICAL[i]
        corto = fault_id.split("_", 1)[0]
        ax.plot(
            grupo["length_s"],
            grupo["best_delta"],
            color=color,
            lw=1.6,
            ls=trazos[i % len(trazos)],
            marker=marcadores[i % len(marcadores)],
            ms=5.0,
            label=corto,
        )
        # Un relleno hueco marca los puntos cuyo mejor descriptor cae sobre una
        # señal que la ficha del fallo no declara: efecto sin mecanismo detrás.
        sin_mecanismo = grupo[~grupo["feature_declared_by_fault"]]
        if not sin_mecanismo.empty:
            ax.plot(
                sin_mecanismo["length_s"],
                sin_mecanismo["best_delta"],
                marcadores[i % len(marcadores)],
                ms=10.0,
                markerfacecolor="none",
                markeredgecolor=color,
                markeredgewidth=1.5,
                linestyle="none",
            )
        etiquetas_derecha.append((float(grupo.iloc[-1]["best_delta"]), corto, color))

    # Las etiquetas directas se separan verticalmente cuando coinciden: dos
    # nombres impresos en el mismo punto no se leen ninguno de los dos.
    separacion = 0.035
    etiquetas_derecha.sort()
    y_previa = -1.0
    for valor, corto, color in etiquetas_derecha:
        y = max(valor, y_previa + separacion)
        ax.annotate(
            corto,
            xy=(120.0, valor),
            xytext=(150.0, y),
            textcoords="data",
            fontsize=7.5,
            color=color,
            va="center",
        )
        y_previa = y

    ax.set_xscale("log")
    ax.set_xlim(9.0, 210.0)
    ax.set_xticks(sorted(estudio["length_s"].unique()))
    ax.set_xticklabels([f"{int(v)} s" for v in sorted(estudio["length_s"].unique())])
    ax.set_xlabel("longitud de ventana")
    ax.set_ylabel("mayor |delta de Cliff| entre 139 descriptores")
    ax.set_ylim(0.0, 1.08)
    ax.grid(visible=True, axis="both")
    # Abajo a la izquierda: es la única zona del lienzo que ninguna serie ocupa.
    ax.legend(loc="lower left", ncol=3)

    ax.set_title(
        "Evidencia disponible según la longitud de ventana",
        color="#0b0b0b",
        pad=18,
    )
    ax.text(
        0.0,
        1.045,
        "Marcador hueco: el mejor descriptor cae sobre una señal que la ficha del fallo "
        "no declara. F01 y F04 valen 1,00 en las cuatro longitudes y se superponen.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    return save(fig, destino)


def fig_balance_particiones(meta: pd.DataFrame, destino: Path) -> Path:
    """¿Cómo quedan repartidas las clases entre las tres particiones?

    El desequilibrio entre la clase normal y cada fallo no es un defecto del
    reparto: las sesiones averiadas aportan también las ventanas anteriores a la
    entrada del fallo. Se declara porque condiciona qué métricas son legibles.
    """
    apply_style()
    tabla = pd.crosstab(meta["label"], meta["partition"])
    orden = ["train", "validation", "test"]
    tabla = tabla[[c for c in orden if c in tabla.columns]]

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    abajo = pd.Series(0.0, index=tabla.index)
    for i, particion in enumerate(tabla.columns):
        valores = tabla[particion]
        ax.barh(
            range(len(tabla)),
            valores.to_numpy(),
            left=abajo.to_numpy(),
            height=0.62,
            color=CATEGORICAL[i],
            label=particion,
            # Separación de 2 px entre segmentos: sin ella, dos colores
            # contiguos se leen como una sola barra.
            edgecolor="#fcfcfb",
            linewidth=1.4,
        )
        for j, (valor, base) in enumerate(zip(valores, abajo, strict=True)):
            if valor > 0:
                ax.text(
                    base + valor / 2,
                    j,
                    str(int(valor)),
                    ha="center",
                    va="center",
                    fontsize=6.8,
                    color="#0b0b0b",
                )
        abajo = abajo + valores

    ax.set_yticks(range(len(tabla)))
    ax.set_yticklabels([str(i).split("_", 1)[0] for i in tabla.index], fontsize=7.5)
    ax.set_xlabel("ventanas")
    ax.grid(visible=True, axis="x")
    ax.legend(loc="lower right", ncol=3)
    ax.set_title("Ventanas por clase y partición", color="#0b0b0b", pad=18)
    ax.text(
        0.0,
        1.05,
        "El reparto es por sesión, nunca por ventana. La clase normal dobla a "
        "cada fallo porque las sesiones averiadas aportan sus ventanas previas.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    return save(fig, destino)
