"""Figuras de EXP-ANOM-009 a partir de resultados REALES (sin gráficas decorativas)."""

from pathlib import Path

import numpy as np

ARMS = ("lstm_ae", "gru_ae", "static_ae_fs1_s", "static_ae_fs1_m", "lof_frozen")


def make_figures(results: dict, out: Path) -> None:  # noqa: PLR0915
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    arms = results["arms"]

    # 1. comparación principal: F1 / FPR / recall held-out por brazo (+ brazo control)
    labels = [*ARMS, "control_arm"]
    f1 = [arms[a]["test"]["point"]["f1"] for a in ARMS] + [
        results["control_arm"]["test"]["point"]["f1"]
    ]
    fpr = [arms[a]["test"]["point"]["fp_rate_normal"] for a in ARMS] + [
        results["control_arm"]["test"]["point"]["fp_rate_normal"]
    ]
    held = [arms[a]["test"]["per_category"].get("held_out_recall", 0.0) for a in ARMS] + [
        results["control_arm"]["test"]["per_category"].get("held_out_recall", 0.0)
    ]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.bar(x - 0.27, f1, 0.27, label="F1")
    ax.bar(x, fpr, 0.27, label="FPR normal")
    ax.bar(x + 0.27, held, 0.27, label="recall held-out")
    ax.set_xticks(x, labels, rotation=20, ha="right", fontsize=7)
    ax.legend(fontsize=7), ax.set_title("EXP-ANOM-009 — comparación de brazos (test)")
    fig.tight_layout(), fig.savefig(out / "arms_comparison.png", dpi=120), plt.close(fig)

    # 2. el hallazgo central: FPR normal antes vs después del cruce de cuantización del LTFT
    q = {
        **results["quantization_analysis"]["sequential"]["by_arm"],
        **results["quantization_analysis"]["static"]["by_arm"],
    }
    names = list(q)
    pre = [q[a]["flag_rate_normal_pre_crossing"] or 0.0 for a in names]
    post = [q[a]["flag_rate_normal_post_crossing"] or 0.0 for a in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.bar(x - 0.2, pre, 0.4, label="normal ANTES del cruce")
    ax.bar(x + 0.2, post, 0.4, label="normal DESPUÉS del cruce")
    ax.set_xticks(x, names, rotation=20, ha="right", fontsize=7)
    ax.set_ylabel("fracción de ventanas marcadas"), ax.legend(fontsize=7)
    ax.set_title("Falsas alarmas y transición de cuantización del LTFT (t≈920 s)")
    fig.tight_layout(), fig.savefig(out / "quantization_effect.png", dpi=120), plt.close(fig)

    # 3. barrido de longitud de secuencia (duración real en el eje)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    lengths = sorted(results["length_sweep"], key=int)
    for kind in ("lstm", "gru"):
        durs = [results["length_sweep"][s][kind]["sequence_duration_seconds"] for s in lengths]
        axes[0].plot(
            durs,
            [results["length_sweep"][s][kind]["test_point"]["f1"] for s in lengths],
            "o-",
            label=kind,
        )
        axes[1].plot(
            durs,
            [results["length_sweep"][s][kind]["test_point"]["fp_rate_normal"] for s in lengths],
            "o-",
            label=kind,
        )
    axes[0].axhline(arms["lof_frozen"]["test"]["point"]["f1"], color="r", ls=":", lw=1, label="LOF")
    axes[1].axhline(
        arms["lof_frozen"]["test"]["point"]["fp_rate_normal"], color="r", ls=":", lw=1, label="LOF"
    )
    for a, t in zip(axes, ("F1", "FPR normal"), strict=True):
        a.set_xlabel("duración de secuencia (s)"), a.set_ylabel(t), a.legend(fontsize=7)
    fig.suptitle("Barrido de longitud de secuencia", fontsize=10)
    fig.tight_layout(), fig.savefig(out / "length_sweep.png", dpi=120), plt.close(fig)

    # 4. recall por tipo de fallo: secuenciales vs estáticos vs LOF vs control
    faults = sorted(arms["static_ae_fs1_s"]["test"]["per_fault_recall"])
    show = ["lstm_ae", "gru_ae", "static_ae_fs1_s", "lof_frozen"]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    width = 0.8 / (len(show) + 1)
    for k, a in enumerate(show):
        ax.bar(
            np.arange(len(faults)) + k * width,
            [arms[a]["test"]["per_fault_recall"].get(f, 0.0) for f in faults],
            width,
            label=a,
        )
    ax.bar(
        np.arange(len(faults)) + len(show) * width,
        [results["control_arm"]["test"]["per_fault_recall"].get(f, 0.0) for f in faults],
        width,
        label="control_arm",
    )
    ax.set_xticks(np.arange(len(faults)) + 0.4, faults, rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("recall (test)"), ax.legend(fontsize=7)
    ax.set_title("Recall por fallo — las anomalías lentas siguen sin detectarse")
    fig.tight_layout(), fig.savefig(out / "recall_by_fault.png", dpi=120), plt.close(fig)

    # 5. XAI temporal: fidelidad vs azar y acuerdo entre explainers
    if results.get("xai"):
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
        arm = "gru_ae" if "gru_ae" in results["xai"] else next(iter(results["xai"]))
        fid = results["xai"][arm]["fidelity_by_fault"]
        fl = sorted(fid)
        xi = np.arange(len(fl))
        axes[0].bar(xi - 0.2, [fid[f]["FAR@5"] for f in fl], 0.2, label="FAR@5")
        axes[0].bar(xi, [fid[f]["FAR@5_random"] for f in fl], 0.2, label="azar")
        axes[0].bar(xi + 0.2, [fid[f]["FTH@10"] for f in fl], 0.2, label="FTH@10")
        axes[0].set_xticks(xi, fl, rotation=25, ha="right", fontsize=6)
        axes[0].legend(fontsize=7), axes[0].set_title(f"Fidelidad XAI ({arm})", fontsize=9)
        cc = [
            results["xai"][a]["explainer_cross_check"]["jaccard_gradient_vs_permutation"]
            for a in results["xai"]
        ]
        st = [
            results["xai"][a]["stability"]["under_perturbation_cell_jaccard"]
            for a in results["xai"]
        ]
        sd = [
            results["xai"][a]["stability"].get("between_seeds_cell_jaccard", 0.0)
            for a in results["xai"]
        ]
        xa = np.arange(len(results["xai"]))
        axes[1].bar(xa - 0.25, cc, 0.25, label="acuerdo Gradient↔Permutation")
        axes[1].bar(xa, st, 0.25, label="estabilidad perturbación")
        axes[1].bar(xa + 0.25, sd, 0.25, label="estabilidad seeds")
        axes[1].set_xticks(xa, list(results["xai"]), fontsize=7)
        axes[1].legend(fontsize=6), axes[1].set_title("Fiabilidad de la atribución", fontsize=9)
        fig.tight_layout(), fig.savefig(out / "xai_temporal.png", dpi=120), plt.close(fig)
