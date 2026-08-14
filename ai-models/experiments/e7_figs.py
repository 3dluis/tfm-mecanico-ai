"""Figuras de EXP-ANOM-008 a partir de resultados REALES (sin gráficas decorativas)."""

from pathlib import Path

import numpy as np

AE_ARMS = ("fs1+AE-S", "fs1+AE-M", "fs2-lite+AE-S", "fs2-lite+AE-M")


def make_figures(results: dict, out: Path) -> None:  # noqa: PLR0915
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    arms = results["arms"]
    all_arms = [*AE_ARMS, "lof_frozen"]

    # 1. FPR por perfil normal y por brazo (la métrica que motiva el experimento)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    profs = sorted({p for a in all_arms for p in arms[a]["fpr_by_profile_test"]})
    width = 0.8 / len(all_arms)
    for k, a in enumerate(all_arms):
        vals = [arms[a]["fpr_by_profile_test"].get(p, 0.0) for p in profs]
        ax.bar(np.arange(len(profs)) + k * width, vals, width, label=a)
    ax.set_xticks(np.arange(len(profs)) + 0.4, profs)
    ax.set_ylabel("FPR (test)"), ax.legend(fontsize=7)
    ax.set_title("FPR por escenario normal — fs1 vs fs2-lite vs LOF congelado")
    fig.tight_layout(), fig.savefig(out / "fpr_by_profile.png", dpi=120), plt.close(fig)

    # 2. recall por tipo de fallo (test) por brazo
    faults = sorted(
        {f for a in all_arms for f in arms[a]["test"].get("per_fault_recall", {})},
    )
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    width = 0.8 / len(all_arms)
    for k, a in enumerate(all_arms):
        vals = [arms[a]["test"]["per_fault_recall"].get(f, 0.0) for f in faults]
        ax.bar(np.arange(len(faults)) + k * width, vals, width, label=a)
    ax.set_xticks(np.arange(len(faults)) + 0.4, faults, rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("recall (test)"), ax.legend(fontsize=7)
    ax.set_title("Recall por fallo — atención a lentos/relacionales")
    fig.tight_layout(), fig.savefig(out / "recall_by_fault.png", dpi=120), plt.close(fig)

    # 3. severidad: recall por sesión de la suite F14 (candidatas vs LOF)
    if "severity" in arms.get("fs2-lite+AE-S", {}):
        fig, ax = plt.subplots(figsize=(8.5, 3.8))
        sev_arms = [a for a in all_arms if "severity" in arms[a]]
        sids = sorted(arms[sev_arms[0]]["severity"]["recall_by_duration"])
        width = 0.8 / len(sev_arms)
        for k, a in enumerate(sev_arms):
            rbd = arms[a]["severity"]["recall_by_duration"]
            vals = [rbd[s]["recall"] if s in rbd else 0.0 for s in sids]
            ax.bar(np.arange(len(sids)) + k * width, vals, width, label=a)
        ax.set_xticks(np.arange(len(sids)) + 0.4, sids, rotation=35, ha="right", fontsize=6)
        ax.set_ylabel("recall"), ax.legend(fontsize=7)
        ax.set_title("Barrido de severidad/duración (suite F14, solo evaluación)")
        fig.tight_layout(), fig.savefig(out / "severity_sweep.png", dpi=120), plt.close(fig)

    # 4. variabilidad entre seeds: F1 y FPR por brazo (seed 42 + réplicas)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    for ax, metric, label in ((axes[0], "f1", "F1"), (axes[1], "fp_rate_normal", "FPR")):
        for j, a in enumerate(AE_ARMS):
            pts = [arms[a]["test"]["point"][metric]] + [
                results["seeds"][a][s]["test_point"][metric] for s in sorted(results["seeds"][a])
            ]
            ax.scatter([j] * len(pts), pts, s=18)
            ax.plot([j - 0.2, j + 0.2], [float(np.mean(pts))] * 2, "k-", lw=1)
        if "lof_frozen" in arms:
            ax.axhline(
                arms["lof_frozen"]["test"]["point"][metric], color="r", ls=":", lw=1, label="LOF"
            )
        ax.set_xticks(range(len(AE_ARMS)), AE_ARMS, rotation=15, fontsize=7)
        ax.set_ylabel(f"{label} (test)"), ax.legend(fontsize=7)
    fig.suptitle("Variabilidad entre seeds (42/43/44)", fontsize=10)
    fig.tight_layout(), fig.savefig(out / "seed_variability.png", dpi=120), plt.close(fig)

    # 5. XAI: AR@K vs azar por fallo, finalista fs2 vs homólogo fs1
    fin = results["xai"].get("finalists", {})
    if fin:
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), sharey=True)
        for ax, key in zip(axes, ("fs2", "fs1"), strict=True):
            arm = fin[key]
            fid = results["xai"][arm]["fidelity_by_fault"]
            faults = sorted(fid)
            x = np.arange(len(faults))
            # claves como str: el dict llega re-leído de JSON (results serializado)
            ax.bar(x - 0.15, [fid[f]["AR"]["5"] for f in faults], 0.3, label="AR@5")
            ax.bar(x + 0.15, [fid[f]["random_baseline"]["5"] for f in faults], 0.3, label="azar@5")
            ax.set_xticks(x, faults, rotation=30, ha="right", fontsize=6)
            ax.set_title(arm, fontsize=9), ax.legend(fontsize=7)
        axes[0].set_ylabel("attribution recall @5")
        fig.suptitle("Fidelidad XAI vs baseline aleatorio (TP explicados)", fontsize=10)
        fig.tight_layout(), fig.savefig(out / "xai_fidelity.png", dpi=120), plt.close(fig)
