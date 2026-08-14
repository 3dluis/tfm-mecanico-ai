"""Experimento E6 (EXP-ANOM-007, EXPLORATORIO) — AE v2 + train v1.1 + XAI/SHAP.

Resuelve las tres decisiones abiertas de EXP-ANOM-006 (Adenda XAI v1 §12):
D1 (detector: corregir FPR), D2 (representación: ¿espacio latente útil?),
D3 (XAI: primera evaluación formal — AR@K vs azar, agreement, estabilidad).

Fases: 0 materializa train v1.1 (22 normales, seeds 101-106+111-142) · 1 diagnóstico
reproducible de los FP de E5 (antes de cambiar nada) · 2 brazos ablation a 60/30
(AE-S v1.0 ref, AE-S v1.1, AE-M v1.1, AE-S v1.1+wd, LOF CONGELADO con umbral 0.163197
sin re-entrenar en v1.1) · 3 barrido de ventanas del candidato · 4 seeds 43/44 ·
5 embeddings (D2) · 6 SHAP (D3) · 7 contrafactual · 8 sonda de fingerprint sintético ·
9 figuras. Umbrales SIEMPRE por cuantil 1% FPR sobre el train del brazo (ADR-0011);
test jamás interviene. Sin seeds reservadas; arms-freeze-v1 intacto.

Uso: python experiments/e6_ae_v2.py --sessions data/sessions [--seed 42] [--fpr 0.01]
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from e4_wide_parity import build_dataset_wide
from sklearn.decomposition import PCA
from sklearn.metrics import average_precision_score, roc_auc_score, silhouette_score

from ai_models.anomaly.autoencoder import AutoencoderDetector
from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import WindowDataset
from ai_models.evaluation.protocol import event_metrics, point_metrics, threshold_from_normal
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from ai_models.xai.ground_truth import gt_features_for
from ai_models.xai.metrics import (
    agreement_class,
    attribution_precision_at_k,
    attribution_recall_at_k,
    jaccard_at_k,
    random_recall_baseline,
    rank_correlation,
    stability_jaccard,
    top_k,
)
from ai_models.xai.shap_runner import (
    ShapExplainer,
    attributions_as_dict,
    explanation_artifact,
    select_background,
)
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import FEATURE_NAMES
from mecanico_contracts.session_io import read_session_header
from obd_lab.generate import generate_ticks, write_session
from obd_lab.scenarios.loader import load_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_JSON = Path(__file__).parent / "e6_results.json"
DIAG_JSON = Path(__file__).parent / "e6_diagnosis.json"
EXPL_JSON = Path(__file__).parent / "e6_explanations.json"
TMP = Path(__file__).parent / "tmp"
FIGS = REPO_ROOT / "docs" / "fase16" / "figs"
TRAIN_EXT_SUITE = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1_train_ext.yaml"
SEVERITY_DIR = REPO_ROOT / "data" / "sessions_f14sev" / "test"

CANON_W, CANON_S = 60, 30
LOF_FROZEN_THRESHOLD = 0.163197  # arms-freeze-v1 (AM-W-v1); LOF NO se re-entrena en v1.1


# --------------------------------------------------------------- fase 0: dataset v1.1
def materialize_v11(v1_sessions: Path, out: Path) -> dict:
    """train v1.1 = 6 normales de suite v1 + 16 de la extensión F9 (provenance completa)."""
    train_dir = out / "train"
    train_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted((v1_sessions / "train").glob("*.jsonl")):
        dst = train_dir / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
    import yaml

    raw = yaml.safe_load(TRAIN_EXT_SUITE.read_text(encoding="utf-8"))
    specs = [ScenarioSpec(**e) for e in raw["train_extension"]]
    for spec in specs:
        target = train_dir / f"{spec.scenario_id}-seed{spec.seed}.jsonl"
        if not target.exists():
            write_session(spec, train_dir)
    files = sorted(train_dir.glob("*.jsonl"))
    digest = hashlib.sha256()
    for f in files:
        digest.update(f.read_bytes())
    return {
        "dataset_id": "obd-lab-suite-v1",
        "dataset_version": "1.1",
        "n_sessions": len(files),
        "seeds": sorted(read_session_header(f).scenario.seed for f in files),
        "provenance": "SIMULATED (obd-lab; generación determinista por semilla)",
        "dataset_hash": digest.hexdigest(),
        "generator_config": {
            "suites": ["suite_v1.yaml (train)", "suite_v1_train_ext.yaml"],
            "profiles": sorted({read_session_header(f).scenario.driving_profile for f in files}),
        },
    }


def _headers(session_dir: Path) -> dict:
    out = {}
    for p in sorted(session_dir.glob("*.jsonl")):
        h = read_session_header(p)
        out[h.session_id] = h.scenario
    return out


# --------------------------------------------------------- fase 1: diagnóstico de E5
def diagnose_e5(
    train10: WindowDataset,
    val: WindowDataset,
    test: WindowDataset,
    headers: dict,
    seed: int,
    fpr: float,
) -> dict:
    """Reproduce el AE-standard de E5 y disecciona sus falsos positivos."""
    ae = AutoencoderDetector(seed=seed, scaler_kind="standard")
    ae.fit(train10.x)
    thr = threshold_from_normal(ae.scores(train10.x), target_fpr=fpr)
    diag: dict = {"threshold": round(float(thr), 6)}
    # ¿overfitting? comparar error de reconstrucción en train vs normales de validación
    tr_err = ae.scores(train10.x)
    val_norm = val.x[val.y == 0]
    val_err = ae.scores(val_norm)
    diag["overfitting_check"] = {
        "train_recon_error_mean": round(float(tr_err.mean()), 5),
        "val_normal_recon_error_mean": round(float(val_err.mean()), 5),
        "generalization_ratio_val_over_train": round(float(val_err.mean() / tr_err.mean()), 3),
        "loss_curve_last10_delta": round(ae.loss_history[-10] - ae.loss_history[-1], 6),
    }
    # contaminación
    diag["train_contamination"] = {"n_fault_windows_in_train": int(train10.y.sum())}
    # FP por sesión/escenario/ventana/feature
    fp_detail = {}
    per_scen_fpr = {}
    for split_name, ds in (("validation", val), ("test", test)):
        scores = ae.scores(ds.x)
        flagged = scores > thr
        for sid in sorted(set(ds.session_ids)):
            sc = headers[sid]
            if sc.category != "normal":
                continue
            idx = np.array([s == sid for s in ds.session_ids])
            n_fp = int(flagged[idx].sum())
            per_scen_fpr[sid] = {
                "split": split_name,
                "profile": sc.driving_profile,
                "fp_rate": round(float(flagged[idx].mean()), 4),
                "n_windows": int(idx.sum()),
            }
            if n_fp:
                fp_idx = np.where(idx & flagged)[0]
                pfe = ae.per_feature_error(ds.x[fp_idx])
                mean_pfe = pfe.mean(axis=0)
                top = [FEATURE_NAMES[j] for j in np.argsort(-mean_pfe)[:5]]
                fp_detail[sid] = {
                    "profile": sc.driving_profile,
                    "n_fp": n_fp,
                    "window_starts_s": [float(ds.window_starts[i]) for i in fp_idx],
                    "top_error_features": top,
                }
    diag["fp_by_normal_session"] = per_scen_fpr
    diag["fp_detail"] = fp_detail
    # drift train vs normales de test (medias estandarizadas con stats de train)
    mu, sd = train10.x.mean(axis=0), train10.x.std(axis=0) + 1e-9
    test_norm = test.x[test.y == 0]
    shift = np.abs((test_norm.mean(axis=0) - mu) / sd)
    order = np.argsort(-shift)[:8]
    diag["train_test_normal_drift_top"] = {
        FEATURE_NAMES[j]: round(float(shift[j]), 3) for j in order
    }
    # desbalance operacional del train v1.0
    prof_counts: dict = {}
    for sid in set(train10.session_ids):
        prof = headers[sid].driving_profile
        prof_counts[prof] = prof_counts.get(prof, 0) + 1
    diag["train_v10_profile_counts"] = prof_counts
    return diag


# --------------------------------------------------------------- evaluación de brazos
def evaluate(det, thr: float, ds: WindowDataset, headers: dict) -> dict:  # noqa: PLR0912
    scores = det.scores(ds.x)
    flagged = scores > thr
    res: dict = {
        "point": asdict(point_metrics(ds.y, flagged)),
        "event": asdict(event_metrics(ds, flagged)),
    }
    if ds.y.any():
        res["pr_auc"] = round(float(average_precision_score(ds.y, scores)), 4)
        res["roc_auc"] = round(float(roc_auc_score(ds.y, scores)), 4)
    # por categoría, fallo, escenario normal, duración y temporales
    per_cat: dict = {}
    for cat in sorted(set(ds.categories)):
        idx = np.array([c == cat for c in ds.categories])
        if cat == "normal":
            per_cat["normal_fp_rate"] = round(float(flagged[idx].mean()), 4)
        else:
            fidx = idx & (ds.y == 1)
            if fidx.any():
                per_cat[f"{cat}_recall"] = round(float(flagged[fidx].mean()), 4)
    res["per_category"] = per_cat
    per_fault: dict = {}
    fpr_by_scenario: dict = {}
    recall_by_duration: dict = {}
    false_alarm_runs: list[float] = []
    persistence: list[float] = []
    delays: list[float] = []
    for sid in sorted(set(ds.session_ids)):
        sc = headers[sid]
        idx = np.array([s == sid for s in ds.session_ids])
        if sc.fault is None:
            fpr_by_scenario[f"{sc.driving_profile}:{sid}"] = round(float(flagged[idx].mean()), 4)
            # duración de falsas alarmas: rachas consecutivas de ventanas marcadas
            f = flagged[idx]
            run = 0
            for v in f:
                if v:
                    run += 1
                elif run:
                    false_alarm_runs.append(run * CANON_S)
                    run = 0
            if run:
                false_alarm_runs.append(run * CANON_S)
            continue
        fidx = idx & (ds.y == 1)
        if not fidx.any():
            continue
        r = float(flagged[fidx].mean())
        per_fault.setdefault(sc.fault, []).append(r)
        dur = (sc.fault_end_s or sc.duration_s) - (sc.fault_start_s or 0.0)
        recall_by_duration[sid] = {"fault": sc.fault, "duration_s": dur, "recall": round(r, 4)}
        persistence.append(r)
        hits = [ds.window_starts[i] for i in np.where(fidx & flagged)[0]]
        if hits:
            delays.append(min(hits) - min(ds.window_starts[i] for i in np.where(fidx)[0]))
    res["per_fault_recall"] = {k: round(float(np.mean(v)), 4) for k, v in sorted(per_fault.items())}
    res["fpr_by_normal_scenario"] = fpr_by_scenario
    res["recall_by_duration"] = recall_by_duration
    res["temporal"] = {
        "mean_detection_delay_s": round(float(np.mean(delays)), 1) if delays else None,
        "anomaly_score_persistence": round(float(np.mean(persistence)), 4) if persistence else None,
        "mean_false_alarm_duration_s": round(float(np.mean(false_alarm_runs)), 1)
        if false_alarm_runs
        else 0.0,
    }
    return res


def fpr_by_profile(res: dict) -> dict:
    agg: dict = {}
    for key, v in res["fpr_by_normal_scenario"].items():
        prof = key.split(":", 1)[0]
        agg.setdefault(prof, []).append(v)
    return {p: round(float(np.mean(v)), 4) for p, v in sorted(agg.items())}


def main() -> int:  # noqa: PLR0915, PLR0912
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--skip-figs", action="store_true")
    args = parser.parse_args()
    t_start = time.perf_counter()

    # fase 0 — datasets
    v11_root = REPO_ROOT / "data" / "sessions_v11"
    v11_meta = materialize_v11(args.sessions, v11_root)
    print(f"train v1.1: {v11_meta['n_sessions']} sesiones hash={v11_meta['dataset_hash'][:12]}")
    headers = {}
    for d in (
        args.sessions / "train",
        args.sessions / "validation",
        args.sessions / "test",
        v11_root / "train",
        SEVERITY_DIR,
    ):
        if d.exists():
            headers.update(_headers(d))
    train10, _, _ = build_dataset_wide(args.sessions / "train", CANON_W, CANON_S)
    train11, _, _ = build_dataset_wide(v11_root / "train", CANON_W, CANON_S)
    val, _, _ = build_dataset_wide(args.sessions / "validation", CANON_W, CANON_S)
    test, _, _ = build_dataset_wide(args.sessions / "test", CANON_W, CANON_S)
    assert not train10.y.any() and not train11.y.any(), "train debe ser 100% normal"

    results: dict = {
        "dataset_v11": v11_meta,
        "arms": {},
        "windows": {},
        "seeds": {},
        "embeddings": {},
        "xai": {},
        "counterfactual": {},
        "fingerprint": {},
    }

    # fase 1 — diagnóstico
    print("fase 1: diagnóstico de E5…")
    diagnosis = diagnose_e5(train10, val, test, headers, args.seed, args.fpr)
    DIAG_JSON.write_text(json.dumps(diagnosis, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    # fase 2 — brazos a 60/30 (ablation de un cambio por brazo)
    arms_spec = [
        ("ae_s_v10", dict(seed=args.seed), train10, "referencia E5 (train v1.0)"),
        ("ae_s_v11", dict(seed=args.seed), train11, "cambio ÚNICO: train v1.1"),
        (
            "ae_m_v11",
            dict(seed=args.seed, hidden=(64, 32), latent=16),
            train11,
            "ablation capacidad (AE-M)",
        ),
        (
            "ae_s_v11_wd",
            dict(seed=args.seed, weight_decay=1e-4),
            train11,
            "ablation regularización (weight decay)",
        ),
    ]
    models: dict = {}
    for name, kw, tr, note in arms_spec:
        det = AutoencoderDetector(scaler_kind="standard", **kw)
        t0 = time.perf_counter()
        det.fit(tr.x)
        fit_s = time.perf_counter() - t0
        thr = threshold_from_normal(det.scores(tr.x), target_fpr=args.fpr)
        t0 = time.perf_counter()
        r = evaluate(det, thr, test, headers)
        infer_s = (time.perf_counter() - t0) / len(test.x) * 1000
        r_val = evaluate(det, thr, val, headers)
        arm = {
            "note": note,
            "threshold": round(float(thr), 6),
            "fit_seconds": round(fit_s, 2),
            "n_parameters": det.n_parameters,
            "infer_ms_per_window": round(infer_s, 3),
            "loss_first_last": [round(det.loss_history[0], 5), round(det.loss_history[-1], 5)],
            "validation": r_val,
            "test": r,
            "fpr_by_profile_test": fpr_by_profile(r),
        }
        results["arms"][name] = arm
        models[name] = (det, thr)
        record_run(
            RUNS_FILE,
            {
                "experiment": "e6_ae_v2",
                "arm": name,
                "git_sha": git_sha(REPO_ROOT),
                "window": CANON_W,
                "stride": CANON_S,
                "seed": args.seed,
                "dataset_version": "1.1" if tr is train11 else "1.0",
                "dataset_hash": v11_meta["dataset_hash"] if tr is train11 else None,
                "threshold": arm["threshold"],
                "metrics": r["point"],
                "peak_rss_mb": peak_rss_mb(),
            },
        )
        tp = r["point"]
        print(
            f"  {name:14s} thr={thr:8.4f} F1={tp['f1']:.3f} FPR={tp['fp_rate_normal']:.3f} "
            f"held={r['per_category'].get('held_out_recall')}"
        )
    # LOF congelado (umbral fijo del freeze; entrenado SOLO con train v1.0 como en E1)
    lof = next(d for d in make_baselines(args.seed) if d.name == "lof")
    lof.fit(train10.x)
    thr_lof = threshold_from_normal(lof.scores(train10.x), target_fpr=args.fpr)
    assert abs(thr_lof - LOF_FROZEN_THRESHOLD) < 1e-6, "el LOF congelado no se reproduce"
    r = evaluate(lof, thr_lof, test, headers)
    results["arms"]["lof_frozen"] = {
        "note": "brazo congelado arms-freeze-v1 (SIN re-entrenar en v1.1)",
        "threshold": round(float(thr_lof), 6),
        "test": r,
        "validation": evaluate(lof, thr_lof, val, headers),
        "fpr_by_profile_test": fpr_by_profile(r),
    }

    # severidad (solo evaluación) para candidato y LOF congelado
    if SEVERITY_DIR.exists():
        sev, _, _ = build_dataset_wide(SEVERITY_DIR, CANON_W, CANON_S)
        for name in ("ae_s_v11", "lof_frozen"):
            det, thr = models.get(name, (lof, thr_lof))
            results["arms"][name]["severity"] = evaluate(det, thr, sev, headers)[
                "recall_by_duration"
            ] | {"fpr": evaluate(det, thr, sev, headers)["fpr_by_normal_scenario"]}

    # fase 3 — barrido de ventanas del candidato (evidencia E5: {30,60} útiles; 10 y 120
    # se mantienen en el barrido del candidato para no descartar por métricas, ADR §10)
    for w in (10, 30, 120):
        s = w // 2
        tr, _, _ = build_dataset_wide(v11_root / "train", w, s)
        te, _, _ = build_dataset_wide(args.sessions / "test", w, s)
        det = AutoencoderDetector(seed=args.seed, scaler_kind="standard")
        det.fit(tr.x)
        thr = threshold_from_normal(det.scores(tr.x), target_fpr=args.fpr)
        rt = evaluate(det, thr, te, headers)
        results["windows"][str(w)] = {
            "threshold": round(float(thr), 6),
            "test_point": rt["point"],
            "held_out_recall": rt["per_category"].get("held_out_recall"),
            "fpr_by_profile": fpr_by_profile(rt),
        }
        print(f"  w={w:3d} F1={rt['point']['f1']:.3f} FPR={rt['point']['fp_rate_normal']:.3f}")

    # fase 4 — seeds (variabilidad + estabilidad XAI)
    seed_models = {args.seed: models["ae_s_v11"]}
    for s in (args.seed + 1, args.seed + 2):
        det = AutoencoderDetector(seed=s, scaler_kind="standard")
        det.fit(train11.x)
        thr = threshold_from_normal(det.scores(train11.x), target_fpr=args.fpr)
        rt = evaluate(det, thr, test, headers)
        seed_models[s] = (det, thr)
        results["seeds"][str(s)] = {
            "threshold": round(float(thr), 6),
            "test_point": rt["point"],
            "held_out_recall": rt["per_category"].get("held_out_recall"),
        }

    # fase 5 — embeddings (D2)
    faults_by_sid = {sid: (sc.fault or "normal") for sid, sc in headers.items()}
    labels = np.array(
        [
            faults_by_sid[s] if y == 1 else "normal"
            for s, y in zip(test.session_ids, test.y, strict=True)
        ]
    )
    for name in ("ae_s_v10", "ae_s_v11", "ae_m_v11"):
        det, _ = models[name]
        z = det.embed(test.x)
        emb: dict = {"latent_dim": int(z.shape[1])}
        if len(set(labels)) > 1:
            emb["silhouette_all_vs_normal"] = round(
                float(silhouette_score(z, labels, random_state=0)), 4
            )
        anom = labels != "normal"
        if anom.sum() > 2 and len(set(labels[anom])) > 1:
            emb["silhouette_between_faults"] = round(
                float(silhouette_score(z[anom], labels[anom], random_state=0)), 4
            )
        pca = PCA(n_components=min(4, z.shape[1]), random_state=0).fit(z)
        emb["pca_var_explained_2c"] = round(float(pca.explained_variance_ratio_[:2].sum()), 4)
        results["embeddings"][name] = emb

    # fase 6 — SHAP (D3) sobre el candidato
    print("fase 6: SHAP…")
    champion, champ_thr = models["ae_s_v11"]
    bg, bg_meta = select_background(train11.x, size=100, seed=args.seed)
    t0 = time.perf_counter()
    explainer = ShapExplainer(champion, bg)
    scores = champion.scores(test.x)
    flagged = scores > champ_thr
    rng = np.random.default_rng(args.seed)

    def pick(mask: np.ndarray, n: int) -> list[int]:
        idx = np.where(mask)[0]
        if len(idx) <= n:
            return idx.tolist()
        return np.sort(rng.choice(idx, size=n, replace=False)).tolist()

    sample: dict[str, list[int]] = {}
    for fault in sorted({f for f in labels if f != "normal"}):
        fm = labels == fault
        sample[f"TP:{fault}"] = pick(fm & flagged, 4)
        sample[f"FN:{fault}"] = pick(fm & ~flagged, 2)
    sample["FP:normal"] = pick((labels == "normal") & flagged, 8)
    sample["TN:normal"] = pick((labels == "normal") & ~flagged, 4)
    all_idx = sorted({i for v in sample.values() for i in v})
    shap_vals = explainer.explain(test.x[all_idx])
    shap_by_idx = {i: attributions_as_dict(shap_vals[j]) for j, i in enumerate(all_idx)}
    pfe_all = champion.per_feature_error(test.x[all_idx])
    pfe_by_idx = {
        i: dict(zip(FEATURE_NAMES, pfe_all[j], strict=True)) for j, i in enumerate(all_idx)
    }
    shap_runtime = time.perf_counter() - t0

    # métricas de fidelidad por fallo (sobre TP)
    fidelity: dict = {}
    for fault in sorted({f for f in labels if f != "normal"}):
        idxs = sample[f"TP:{fault}"]
        if not idxs:
            continue
        gt = gt_features_for(fault)
        ar = {
            k: round(
                float(np.mean([attribution_recall_at_k(shap_by_idx[i], gt, k) for i in idxs])), 4
            )
            for k in (1, 3, 5)
        }
        rnd = {
            k: round(random_recall_baseline(len(FEATURE_NAMES), len(gt), k), 4) for k in (1, 3, 5)
        }
        prec = {}
        for k in (1, 3, 5):
            if len(gt) >= k:
                prec[k] = round(
                    float(
                        np.mean([attribution_precision_at_k(shap_by_idx[i], gt, k) for i in idxs])
                    ),
                    4,
                )
        fidelity[fault] = {
            "gt_size": len(gt),
            "n_explained": len(idxs),
            "AR": ar,
            "random_baseline": rnd,
            "precision": prec,
        }
    # agreement SHAP ↔ per-feature error
    agreements = []
    examples: dict = {"AGREE": None, "PARTIAL_AGREEMENT": None, "DISAGREE": None}
    for key, idxs in sample.items():
        if key.startswith(("TP", "FP")):
            for i in idxs:
                j5 = jaccard_at_k(shap_by_idx[i], pfe_by_idx[i], 5)
                rho = rank_correlation(shap_by_idx[i], pfe_by_idx[i])
                cls = agreement_class(j5)
                agreements.append(
                    {
                        "case": key,
                        "window": i,
                        "jaccard5": round(j5, 3),
                        "spearman": round(rho, 3),
                        "class": cls,
                    }
                )
                if examples[cls] is None:
                    examples[cls] = {
                        "case": key,
                        "window": i,
                        "shap_top5": top_k(shap_by_idx[i], 5),
                        "pfe_top5": top_k(pfe_by_idx[i], 5),
                    }
    # estabilidad entre seeds (mismas ventanas, modelos equivalentes)
    stab_windows = (
        sample["FP:normal"][:2] + [v[0] for k, v in sample.items() if k.startswith("TP") and v][:4]
    )
    seed_rankings: dict[int, list] = {}
    for s, (det, _t) in seed_models.items():
        ex = ShapExplainer(det, select_background(train11.x, size=100, seed=args.seed)[0])
        vals = ex.explain(test.x[stab_windows])
        seed_rankings[s] = [attributions_as_dict(v) for v in vals]
    seed_stability = round(
        float(
            np.mean(
                [
                    stability_jaccard([seed_rankings[s][w] for s in seed_rankings], 5)
                    for w in range(len(stab_windows))
                ]
            )
        ),
        4,
    )
    # estabilidad ante perturbación (ruido 0.05·std de train, semilla fija)
    pert_rng = np.random.default_rng(0)
    std = train11.x.std(axis=0)
    xw = test.x[stab_windows]
    xp = xw + 0.05 * std * pert_rng.standard_normal(xw.shape)
    vals_p = explainer.explain(xp)
    pert_stability = round(
        float(
            np.mean(
                [
                    jaccard_at_k(shap_by_idx[stab_windows[w]], attributions_as_dict(vals_p[w]), 5)
                    for w in range(len(stab_windows))
                ]
            )
        ),
        4,
    )
    # global + FP
    mean_abs = np.abs(shap_vals).mean(axis=0)
    top_global = {
        FEATURE_NAMES[j]: round(float(mean_abs[j]), 5) for j in np.argsort(-mean_abs)[:10]
    }
    fp_top: dict = {}
    for i in sample["FP:normal"]:
        fp_top[str(i)] = {
            "session": test.session_ids[i],
            "start_s": test.window_starts[i],
            "shap_top5": top_k(shap_by_idx[i], 5),
        }
    results["xai"] = {
        "background": bg_meta,
        "explainer": explainer.registry_record(),
        "samples_explained": len(all_idx),
        "runtime_seconds": round(shap_runtime, 1),
        "fidelity_by_fault": fidelity,
        "agreement": {
            "cases": agreements,
            "mean_jaccard5": round(float(np.mean([a["jaccard5"] for a in agreements])), 3),
            "class_counts": {
                c: sum(1 for a in agreements if a["class"] == c)
                for c in ("AGREE", "PARTIAL_AGREEMENT", "DISAGREE")
            },
            "examples": examples,
        },
        "stability": {
            "between_seeds_jaccard5": seed_stability,
            "under_perturbation_jaccard5": pert_stability,
            "n_windows": len(stab_windows),
        },
        "global_mean_abs_shap_top10": top_global,
        "fp_explanations": fp_top,
    }
    # artefactos de explicación (contrato F15)
    artifacts = [
        explanation_artifact(
            window_id=f"{test.session_ids[i]}@{test.window_starts[i]:.0f}s",
            session_id=test.session_ids[i],
            model_id="ae_s_v11@e6",
            anomaly_score=float(scores[i]),
            threshold=float(champ_thr),
            shap_values=shap_by_idx[i],
            per_feature_error=pfe_by_idx[i],
            background_meta=bg_meta,
            explainer_record=explainer.registry_record(),
        )
        for i in all_idx[:12]
    ]
    EXPL_JSON.write_text(json.dumps(artifacts, indent=1, ensure_ascii=False) + "\n")

    # fase 7 — contrafactual (gemelo sin fallo; exacto pre-fallo, aproximado después)
    cf_spec = next(
        s
        for s in load_suite(REPO_ROOT / "obd-lab" / "scenarios" / "suite_f14_severity.yaml")["test"]
        if s.scenario_id == "sev-corrbreak-high"
    )
    twin_spec = cf_spec.model_copy(
        update={"fault": None, "fault_params": {}, "fault_start_s": None, "scenario_id": "cf-twin"}
    )
    from ai_models.data.snapshot_matrix import iter_windows, matrix_from_snapshots
    from diagnostic_agent.telemetry.snapshots import build_from_ticks
    from mecanico_contracts.features import feature_vector

    def windows_of(spec):
        ticks = generate_ticks(spec)
        snaps, _ = build_from_ticks(ticks, session_id=spec.scenario_id, vehicle_id="veh-sim")
        m = matrix_from_snapshots(snaps)
        return [(st, feature_vector(w)) for st, w in iter_windows(m, CANON_W, CANON_S)]

    wf, wt = windows_of(cf_spec), windows_of(twin_spec)
    pre = [i for i, (st, _v) in enumerate(wf) if st + CANON_W <= (cf_spec.fault_start_s or 0)]
    post = [i for i, (st, _v) in enumerate(wf) if st >= (cf_spec.fault_start_s or 0)]
    xf = np.array([v for _s, v in wf])
    xt = np.array([v for _s, v in wt])
    pre_equal = bool(np.array_equal(xf[pre], xt[pre])) if pre else None
    sf, st_ = champion.scores(xf), champion.scores(xt)
    if post:
        i = post[len(post) // 2]
        pair_shap = explainer.explain(np.stack([xf[i], xt[i]]))
        cf_pair = {
            "window_start_s": wf[i][0],
            "score_fault": round(float(sf[i]), 4),
            "score_twin": round(float(st_[i]), 4),
            "shap_top5_fault": top_k(attributions_as_dict(pair_shap[0]), 5),
            "shap_top5_twin": top_k(attributions_as_dict(pair_shap[1]), 5),
        }
    results["counterfactual"] = {
        "scenario": cf_spec.scenario_id,
        "pre_fault_windows_identical": pre_equal,
        "mean_score_pre_fault": round(float(sf[pre].mean()), 4) if pre else None,
        "mean_score_post_fault": round(float(sf[post].mean()), 4) if post else None,
        "mean_score_twin_post": round(float(st_[post].mean()), 4) if post else None,
        "paired_example": cf_pair,
        "caveat": (
            "gemelo EXACTO antes de fault_start; aproximado después (el fallo "
            "comparte el generador aleatorio del motor de señales)"
        ),
    }

    # fase 8 — sonda de fingerprint sintético: perfil de atribución en normales TN
    tn = sample["TN:normal"] + sample["FP:normal"]
    by_prof: dict[str, list] = {}
    for i in tn:
        prof = headers[test.session_ids[i]].driving_profile
        by_prof.setdefault(prof, []).append(np.abs(np.array(list(shap_by_idx[i].values()))))
    profs = sorted(by_prof)
    fp_probe: dict = {"windows_used": len(tn), "profiles": profs}
    if len(profs) == 2:
        a = np.mean(by_prof[profs[0]], axis=0)
        b = np.mean(by_prof[profs[1]], axis=0)
        cos = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
        fp_probe["cosine_similarity_between_profiles"] = round(cos, 4)
        fp_probe["nota"] = (
            "similitud alta = el perfil de atribución en normales no depende "
            "del escenario; baja = posible huella de generador/escenario. "
            "Sonda limitada: sin datos reales aún, comparación intra-simulador"
        )
    results["fingerprint"] = fp_probe

    results["total_runtime_s"] = round(time.perf_counter() - t_start, 1)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print(
        f"\nresultados → {RESULTS_JSON.name} · diagnóstico → {DIAG_JSON.name} "
        f"· explicaciones → {EXPL_JSON.name} ({results['total_runtime_s']}s)"
    )

    if not args.skip_figs:
        from e6_figs import make_figures  # separado para mantener main() acotado

        make_figures(
            results,
            diagnosis,
            models,
            lof,
            thr_lof,
            train11,
            test,
            labels,
            shap_by_idx,
            sample,
            FIGS,
        )
        print(f"figuras → {FIGS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
