"""Figuras de EXP-ANOM-007 a partir de resultados REALES (sin gráficas decorativas)."""

from pathlib import Path

import numpy as np


def make_figures(  # noqa: PLR0915
    results, diagnosis, models, lof, thr_lof, train11, test, labels, shap_by_idx, sample, out: Path
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    champion, champ_thr = models["ae_s_v11"]

    # 1. curvas de pérdida (train) de los brazos AE
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for name, (det, _t) in models.items():
        if det.loss_history:
            ax.plot(det.loss_history, label=name, lw=1.2)
    ax.set_xlabel("época"), ax.set_ylabel("MSE train"), ax.set_yscale("log")
    ax.legend(fontsize=8), ax.set_title("Curvas de pérdida (train)")
    fig.tight_layout(), fig.savefig(out / "loss_curves.png", dpi=120), plt.close(fig)

    # 2. distribución de scores normal vs anomalía (candidato)
    s = champion.scores(test.x)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(s[test.y == 0], bins=40, alpha=0.6, label="normal", density=True)
    ax.hist(s[test.y == 1], bins=40, alpha=0.6, label="anomalía", density=True)
    ax.axvline(champ_thr, color="k", ls="--", lw=1, label=f"umbral {champ_thr:.3f}")
    ax.set_xscale("log"), ax.legend(fontsize=8)
    ax.set_title("ae_s_v11: distribución de scores (test)")
    fig.tight_layout(), fig.savefig(out / "score_distribution.png", dpi=120), plt.close(fig)

    # 3. PR y ROC (candidato vs LOF congelado)
    from sklearn.metrics import precision_recall_curve, roc_curve

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    for name, det, _thr in (("ae_s_v11", champion, champ_thr), ("lof_frozen", lof, thr_lof)):
        sc = det.scores(test.x)
        p, r, _ = precision_recall_curve(test.y, sc)
        fpr, tpr, _ = roc_curve(test.y, sc)
        axes[0].plot(r, p, label=name, lw=1.2)
        axes[1].plot(fpr, tpr, label=name, lw=1.2)
    axes[0].set_xlabel("recall"), axes[0].set_ylabel("precision"), axes[0].set_title("PR")
    axes[1].set_xlabel("FPR"), axes[1].set_ylabel("TPR"), axes[1].set_title("ROC")
    axes[1].plot([0, 1], [0, 1], "k:", lw=0.8)
    for a in axes:
        a.legend(fontsize=8)
    fig.tight_layout(), fig.savefig(out / "pr_roc.png", dpi=120), plt.close(fig)

    # 4. FPR por escenario normal (brazos)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    arms = [a for a in results["arms"] if "fpr_by_profile_test" in results["arms"][a]]
    profs = sorted({p for a in arms for p in results["arms"][a]["fpr_by_profile_test"]})
    width = 0.8 / len(arms)
    for k, a in enumerate(arms):
        vals = [results["arms"][a]["fpr_by_profile_test"].get(p, 0) for p in profs]
        ax.bar(np.arange(len(profs)) + k * width, vals, width, label=a)
    ax.set_xticks(np.arange(len(profs)) + 0.4, profs)
    ax.set_ylabel("FPR"), ax.legend(fontsize=7), ax.set_title("FPR por escenario normal (test)")
    fig.tight_layout(), fig.savefig(out / "fpr_by_scenario.png", dpi=120), plt.close(fig)

    # 5. recall por tipo de anomalía
    fig, ax = plt.subplots(figsize=(7, 3.5))
    faults = sorted(results["arms"]["ae_s_v11"]["test"]["per_fault_recall"])
    width = 0.8 / len(arms)
    for k, a in enumerate(arms):
        pf = results["arms"][a]["test"]["per_fault_recall"]
        ax.bar(np.arange(len(faults)) + k * width, [pf.get(f, 0) for f in faults], width, label=a)
    ax.set_xticks(np.arange(len(faults)) + 0.4, faults, rotation=20, fontsize=7)
    ax.set_ylabel("recall"), ax.legend(fontsize=7), ax.set_title("Recall por anomalía (test)")
    fig.tight_layout(), fig.savefig(out / "recall_by_fault.png", dpi=120), plt.close(fig)

    # 6. PCA del espacio latente
    from sklearn.decomposition import PCA

    z = champion.embed(test.x)
    p2 = PCA(n_components=2, random_state=0).fit_transform(z)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for lab in sorted(set(labels)):
        m = labels == lab
        ax.scatter(p2[m, 0], p2[m, 1], s=6, alpha=0.6, label=lab)
    ax.legend(fontsize=7, markerscale=2), ax.set_title("PCA embeddings ae_s_v11 (test)")
    fig.tight_layout(), fig.savefig(out / "pca_embeddings.png", dpi=120), plt.close(fig)

    # 7. SHAP global (mean |SHAP| top-10)
    g = results["xai"]["global_mean_abs_shap_top10"]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    names = list(g)[::-1]
    ax.barh(names, [g[n] for n in names])
    ax.set_xlabel("mean |SHAP|"), ax.set_title("Atribución global (muestra explicada)")
    fig.tight_layout(), fig.savefig(out / "shap_global.png", dpi=120), plt.close(fig)

    # 8. ejemplo SHAP de un FP y de un TP
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax_, key, title in (
        (axes[0], "FP:normal", "Falso positivo"),
        (
            axes[1],
            next(k for k in sample if k.startswith("TP") and sample[k]),
            "Verdadero positivo",
        ),
    ):
        if sample[key]:
            i = sample[key][0]
            attr = shap_by_idx[i]
            top = sorted(attr, key=lambda f: -abs(attr[f]))[:8][::-1]
            ax_.barh(top, [attr[f] for f in top])
            ax_.set_title(
                f"{title}: {test.session_ids[i]}@{test.window_starts[i]:.0f}s", fontsize=8
            )
    fig.tight_layout(), fig.savefig(out / "shap_examples.png", dpi=120), plt.close(fig)
