"""Figuras de la auditoría F19 a partir de resultados REALES."""

from pathlib import Path

import numpy as np


def make_figures(results: dict, out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    cat = results["catalogue"]
    faults = sorted(cat)

    # 1. separabilidad pareada vs poblacional (con el control SHAM)
    paired = [cat[f]["verdict"]["auc_paired"] for f in faults]
    pop = [cat[f]["population"]["auc_mahalanobis_population"] for f in faults]
    sham = [cat[f]["population"]["auc_mahalanobis_sham_control"] for f in faults]
    x = np.arange(len(faults))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x - 0.27, paired, 0.27, label="pareado (mismo escenario y semilla)")
    ax.bar(x, pop, 0.27, label="frente a la población normal de train")
    ax.bar(x + 0.27, sham, 0.27, label="control SHAM (solo desincronización)")
    ax.axhline(0.5, color="k", ls=":", lw=1)
    ax.set_xticks(x, faults, rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("AUC (sin modelos entrenados)"), ax.legend(fontsize=7)
    ax.set_title("F19 — separabilidad de cada anomalía sin usar detectores")
    fig.tight_layout(), fig.savefig(out / "separability.png", dpi=120), plt.close(fig)

    # 2. matriz de cobertura de normalidad
    matrix = results["coverage"]["matrix"]
    behaviours = list(matrix)
    splits = ["train", "validation", "test", "train_v11"]
    grid = np.array([[matrix[b][s]["count"] for s in splits] for b in behaviours], dtype=float)
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(grid, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(splits)), splits, fontsize=8)
    ax.set_yticks(range(len(behaviours)), behaviours, fontsize=7)
    for i in range(len(behaviours)):
        for j in range(len(splits)):
            ax.text(
                j,
                i,
                int(grid[i, j]),
                ha="center",
                va="center",
                color="w" if grid[i, j] < grid.max() / 2 else "k",
                fontsize=7,
            )
    fig.colorbar(im, ax=ax, label="sesiones normales")
    ax.set_title("Cobertura de normalidad por partición", fontsize=10)
    fig.tight_layout(), fig.savefig(out / "coverage_matrix.png", dpi=120), plt.close(fig)

    # 3. severidad
    sev = results["severity"]
    order = sorted(sev, key=lambda k: (sev[k]["fault"], k))
    vals = [sev[k]["auc_best"] for k in order]
    colors = {
        "DETECTABLE": "tab:green",
        "WEAKLY_DETECTABLE": "tab:orange",
        "NEEDS_MORE_EVIDENCE": "tab:red",
        "INDISTINGUISHABLE": "tab:gray",
        "INVALID_BY_CONSTRUCTION": "k",
    }
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.bar(range(len(order)), vals, color=[colors[sev[k]["label"]] for k in order])
    ax.axhline(0.9, color="k", ls="--", lw=1, label="umbral DETECTABLE")
    ax.axhline(0.7, color="k", ls=":", lw=1, label="umbral WEAKLY")
    ax.set_xticks(range(len(order)), order, rotation=35, ha="right", fontsize=6)
    ax.set_ylabel("AUC mejor feature"), ax.legend(fontsize=7)
    ax.set_title("Detectabilidad por severidad (LOW / MID / HIGH)")
    fig.tight_layout(), fig.savefig(out / "severity.png", dpi=120), plt.close(fig)
