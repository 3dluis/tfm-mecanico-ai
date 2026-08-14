"""Experimento E7 (EXP-ANOM-008, EXPLORATORIO) — ablation fs2-lite vs fs1 (F17).

Pregunta: ¿la corrección a nivel de REPRESENTACIÓN (fs2-lite: deriva de trims relativa a
la propia sesión EN SUSTITUCIÓN de los absolutos + std multiescala + correlaciones lag-1)
corrige el FPR del AE identificado en EXP-ANOM-007 y mejora la representación (D2), sin
degradar la explicabilidad (D3)? fs2-lite NO se promueve a contrato antes de resultados.

Brazos (cambio único = esquema de features; mismo train v1.1, misma normalización
embedded-standard-scaler, mismo protocolo ADR-0011):
  fs1+AE-S · fs1+AE-M · fs2-lite+AE-S · fs2-lite+AE-M · LOF CONGELADO (arms-freeze-v1,
  fs1, train v1.0, umbral 0.163197 — jamás re-entrenado ni reajustado).

Fases: 0 datasets (fs1 y fs2-lite desde el MISMO camino wide canónico; referencia de
sesión = primeros 120 s de la propia sesión) · 1 brazos seed 42 con desgloses completos
(FPR por escenario normal, recall por fallo/severidad/duración, fallos foco:
joint_slow_drift, load_coolant_decouple, corr_break_rpm_maf, degradación progresiva) ·
2 réplica seeds 43/44 de los 4 brazos · 3 embeddings (D2) · 4 XAI comparado en
finalistas (AR@K vs azar con GT por esquema, agreement, estabilidad seeds/perturbación,
features dominantes inesperadas, sonda fingerprint) · 5 resumen.

Umbrales SIEMPRE por cuantil (1-FPR) sobre el train del brazo; test jamás interviene.
Sin seeds reservadas. Contrafactual NO se repite (validado en F16; maquinaria intacta).
Validez declarada: entorno emulado/sintético (sin HCRL ni ARM64 todavía).

Uso: python experiments/e7_fs2_ablation.py --sessions data/sessions [--seed 42] [--fpr 0.01]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from e4_wide_parity import build_dataset_wide
from e6_ae_v2 import (
    CANON_S,
    CANON_W,
    LOF_FROZEN_THRESHOLD,
    _headers,
    evaluate,
    fpr_by_profile,
    materialize_v11,
)
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from ai_models.anomaly.autoencoder import AutoencoderDetector
from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import WindowDataset, _label
from ai_models.data.snapshot_matrix import iter_windows, matrix_from_snapshots
from ai_models.evaluation.protocol import threshold_from_normal
from ai_models.features.fs2_lite import FS2_LITE_NAMES, fs2lite_vector, session_reference
from ai_models.features.schema import FS1, FS2_LITE, validate_fs2_lite_against_extraction
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from ai_models.xai.ground_truth import gt_features_for
from ai_models.xai.metrics import (
    agreement_class,
    attribution_recall_at_k,
    jaccard_at_k,
    random_recall_baseline,
    rank_correlation,
    stability_jaccard,
    top_k,
)
from ai_models.xai.shap_runner import ShapExplainer, attributions_as_dict, select_background
from diagnostic_agent.telemetry.snapshots import build_from_ticks
from mecanico_contracts.features import FEATURE_NAMES
from mecanico_contracts.session_io import read_session_series

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_JSON = Path(__file__).parent / "e7_results.json"
SEVERITY_DIR = REPO_ROOT / "data" / "sessions_f14sev" / "test"

#: Fallos foco de la instrucción F17 (anomalías lentas/relacionales + degradación).
FOCUS_FAULTS = ("joint_slow_drift", "load_coolant_decouple", "corr_break_rpm_maf")

SCHEMA_NAMES = {"fs1": list(FEATURE_NAMES), "fs2-lite": list(FS2_LITE_NAMES)}
SCHEMA_OBJ = {"fs1": FS1, "fs2-lite": FS2_LITE}
ARCH = {"AE-S": {}, "AE-M": {"hidden": (64, 32), "latent": 16}}


# ------------------------------------------------------------------ datasets fs2-lite
def build_dataset_fs2lite(session_dir: Path, size: int = CANON_W, stride: int = CANON_S):
    """Camino wide canónico (JSONL → snapshots → matriz → ventanas) con features fs2-lite.

    La referencia de trims de cada sesión se calcula de SUS primeros 120 s (fs2_lite.REF_S)
    — nunca de otra sesión ni de otro split (anti-leakage; computable en streaming).
    """
    xs, ys, sids, cats, starts = [], [], [], [], []
    for path in sorted(session_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        n = min(len(v) for v in series.values())
        ref = session_reference(
            list(series["LONG_FUEL_TRIM_1"][:n]), list(series["SHORT_FUEL_TRIM_1"][:n])
        )
        ticks = [{pid: series[pid][i] for pid in series} for i in range(n)]
        snapshots, _links = build_from_ticks(
            ticks,
            session_id=header.session_id,
            vehicle_id=header.vehicle_id,
            device_id=header.device_id,
        )
        matrix = matrix_from_snapshots(snapshots)
        rate = header.scenario.sample_rate_hz if header.scenario else 1.0
        for start_idx, window in iter_windows(matrix, size, stride):
            start_s = start_idx / rate
            xs.append(fs2lite_vector(window, ref))
            ys.append(_label(header, start_s, size / rate))
            sids.append(header.session_id)
            cats.append(header.scenario.category if header.scenario else "unknown")
            starts.append(start_s)
    return WindowDataset(
        x=np.asarray(xs, dtype=np.float64),
        y=np.asarray(ys, dtype=np.int64),
        session_ids=sids,
        categories=cats,
        window_starts=starts,
    )


def focus_recalls(res: dict) -> dict:
    """Recalls de los fallos foco de F17 desde un resultado de evaluate()."""
    return {f: res["per_fault_recall"].get(f) for f in FOCUS_FAULTS}


def fit_arm(schema: str, arch: str, seed: int, train_x: np.ndarray, fpr: float):
    det = AutoencoderDetector(seed=seed, scaler_kind="standard", **ARCH[arch])
    t0 = time.perf_counter()
    det.fit(train_x)
    fit_s = time.perf_counter() - t0
    thr = threshold_from_normal(det.scores(train_x), target_fpr=fpr)
    return det, float(thr), fit_s


# ------------------------------------------------------------------------ fase 4: XAI
def xai_compare(  # noqa: PLR0915
    finalists: dict,
    trains: dict,
    tests: dict,
    labels: np.ndarray,
    headers: dict,
    seed_models: dict,
    seed: int,
) -> dict:
    """XAI comparado por esquema (adenda XAI v1): fidelidad, agreement, estabilidad, FP."""
    out: dict = {}
    rng = np.random.default_rng(seed)

    def pick(mask: np.ndarray, n: int) -> list[int]:
        idx = np.where(mask)[0]
        return (
            idx.tolist() if len(idx) <= n else np.sort(rng.choice(idx, n, replace=False)).tolist()
        )

    for arm_name, (det, thr) in finalists.items():
        schema = "fs2-lite" if arm_name.startswith("fs2") else "fs1"
        names = SCHEMA_NAMES[schema]
        test = tests[schema]
        bg, bg_meta = select_background(trains[schema].x, size=100, seed=seed)
        t0 = time.perf_counter()
        explainer = ShapExplainer(det, bg)
        scores = det.scores(test.x)
        flagged = scores > thr
        sample: dict[str, list[int]] = {}
        for fault in sorted({f for f in labels if f != "normal"}):
            fm = labels == fault
            sample[f"TP:{fault}"] = pick(fm & flagged, 3)
        sample["FP:normal"] = pick((labels == "normal") & flagged, 6)
        sample["TN:normal"] = pick((labels == "normal") & ~flagged, 4)
        all_idx = sorted({i for v in sample.values() for i in v})
        vals = explainer.explain(test.x[all_idx])
        shap_by_idx = {
            i: attributions_as_dict(vals[j], feature_names=names) for j, i in enumerate(all_idx)
        }
        pfe = det.per_feature_error(test.x[all_idx])
        pfe_by_idx = {i: dict(zip(names, pfe[j], strict=True)) for j, i in enumerate(all_idx)}
        runtime = time.perf_counter() - t0

        fidelity: dict = {}
        for fault in sorted({f for f in labels if f != "normal"}):
            idxs = sample[f"TP:{fault}"]
            if not idxs:
                continue
            gt = gt_features_for(fault, schema=SCHEMA_OBJ[schema])
            fidelity[fault] = {
                "gt_size": len(gt),
                "n_explained": len(idxs),
                "AR": {
                    str(k): round(
                        float(
                            np.mean([attribution_recall_at_k(shap_by_idx[i], gt, k) for i in idxs])
                        ),
                        4,
                    )
                    for k in (1, 3, 5)
                },
                "random_baseline": {
                    str(k): round(random_recall_baseline(len(names), len(gt), k), 4)
                    for k in (1, 3, 5)
                },
            }
        agreements = [
            agreement_class(jaccard_at_k(shap_by_idx[i], pfe_by_idx[i], 5))
            for key, idxs in sample.items()
            if key.startswith(("TP", "FP"))
            for i in idxs
        ]
        j5s = [
            jaccard_at_k(shap_by_idx[i], pfe_by_idx[i], 5)
            for key, idxs in sample.items()
            if key.startswith(("TP", "FP"))
            for i in idxs
        ]
        rhos = [
            rank_correlation(shap_by_idx[i], pfe_by_idx[i])
            for key, idxs in sample.items()
            if key.startswith(("TP", "FP"))
            for i in idxs
        ]
        mean_abs = np.abs(vals).mean(axis=0)
        top_global = {names[j]: round(float(mean_abs[j]), 5) for j in np.argsort(-mean_abs)[:10]}
        fp_top = {
            str(i): {
                "session": test.session_ids[i],
                "start_s": test.window_starts[i],
                "shap_top5": top_k(shap_by_idx[i], 5),
            }
            for i in sample["FP:normal"]
        }
        # estabilidad: seeds (solo hay réplicas del brazo finalista fs2) y perturbación
        stab_windows = (
            sample["FP:normal"][:2]
            + [v[0] for k, v in sample.items() if k.startswith("TP") and v][:4]
        )
        stability: dict = {"n_windows": len(stab_windows)}
        if arm_name in seed_models:
            per_seed: list[list[dict[str, float]]] = []
            for det_s in seed_models[arm_name]:
                ex = ShapExplainer(det_s, bg)
                vs = ex.explain(test.x[stab_windows])
                per_seed.append([attributions_as_dict(v, feature_names=names) for v in vs])
            stability["between_seeds_jaccard5"] = round(
                float(
                    np.mean(
                        [
                            stability_jaccard([per_seed[s][w] for s in range(len(per_seed))], 5)
                            for w in range(len(stab_windows))
                        ]
                    )
                ),
                4,
            )
        pert_rng = np.random.default_rng(0)
        std = trains[schema].x.std(axis=0)
        xw = test.x[stab_windows]
        vals_p = explainer.explain(xw + 0.05 * std * pert_rng.standard_normal(xw.shape))
        stability["under_perturbation_jaccard5"] = round(
            float(
                np.mean(
                    [
                        jaccard_at_k(
                            shap_by_idx[stab_windows[w]],
                            attributions_as_dict(vals_p[w], feature_names=names),
                            5,
                        )
                        for w in range(len(stab_windows))
                    ]
                )
            ),
            4,
        )
        # sonda fingerprint: perfil de atribución en normales por escenario
        tn = sample["TN:normal"] + sample["FP:normal"]
        by_prof: dict[str, list] = {}
        for i in tn:
            prof = headers[test.session_ids[i]].driving_profile
            by_prof.setdefault(prof, []).append(np.abs(np.array(list(shap_by_idx[i].values()))))
        probe: dict = {"windows_used": len(tn), "profiles": sorted(by_prof)}
        if len(by_prof) == 2:
            pa, pb = (np.mean(by_prof[p], axis=0) for p in sorted(by_prof))
            probe["cosine_similarity_between_profiles"] = round(
                float(pa @ pb / (np.linalg.norm(pa) * np.linalg.norm(pb) + 1e-12)), 4
            )
        out[arm_name] = {
            "schema": schema,
            "background": bg_meta,
            "explainer": explainer.registry_record(),
            "samples_explained": len(all_idx),
            "runtime_seconds": round(runtime, 1),
            "fidelity_by_fault": fidelity,
            "agreement": {
                "mean_jaccard5": round(float(np.mean(j5s)), 3),
                "mean_spearman": round(float(np.mean(rhos)), 3),
                "class_counts": {
                    c: agreements.count(c) for c in ("AGREE", "PARTIAL_AGREEMENT", "DISAGREE")
                },
            },
            "stability": stability,
            "global_mean_abs_shap_top10": top_global,
            "fp_explanations": fp_top,
            "fingerprint_probe": probe,
        }
    return out


# ------------------------------------------------------------------------------- main
def main() -> int:  # noqa: PLR0915, PLR0912
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--skip-figs", action="store_true")
    args = parser.parse_args()
    t_start = time.perf_counter()
    validate_fs2_lite_against_extraction()

    # fase 0 — datasets por esquema (mismo camino wide; cambio único = features)
    v11_root = REPO_ROOT / "data" / "sessions_v11"
    v11_meta = materialize_v11(args.sessions, v11_root)
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
    train10_fs1, _, _ = build_dataset_wide(args.sessions / "train", CANON_W, CANON_S)
    trains = {"fs1": build_dataset_wide(v11_root / "train", CANON_W, CANON_S)[0]}
    vals = {"fs1": build_dataset_wide(args.sessions / "validation", CANON_W, CANON_S)[0]}
    tests = {"fs1": build_dataset_wide(args.sessions / "test", CANON_W, CANON_S)[0]}
    trains["fs2-lite"] = build_dataset_fs2lite(v11_root / "train")
    vals["fs2-lite"] = build_dataset_fs2lite(args.sessions / "validation")
    tests["fs2-lite"] = build_dataset_fs2lite(args.sessions / "test")
    sevs = {}
    if SEVERITY_DIR.exists():
        sevs["fs1"] = build_dataset_wide(SEVERITY_DIR, CANON_W, CANON_S)[0]
        sevs["fs2-lite"] = build_dataset_fs2lite(SEVERITY_DIR)
    for schema, tr in trains.items():
        assert not tr.y.any(), f"train {schema} debe ser 100% normal"
        assert tr.x.shape[1] == len(SCHEMA_NAMES[schema])
    assert tests["fs1"].session_ids == tests["fs2-lite"].session_ids, "mismas ventanas exactas"
    assert list(tests["fs1"].y) == list(tests["fs2-lite"].y)
    print(
        f"datasets: train v1.1 {trains['fs1'].x.shape}/{trains['fs2-lite'].x.shape} "
        f"test {tests['fs1'].x.shape}/{tests['fs2-lite'].x.shape}"
    )

    results: dict = {
        "dataset_v11": v11_meta,
        "validity_note": (
            "EXPLORATORIO; validez actual = entorno emulado/sintético (obd-lab). Sin "
            "validez externa hasta HCRL (dataset real/replay) y validación ARM64/RPi5 "
            "(tareas dependientes registradas aparte, F17)"
        ),
        "arms": {},
        "seeds": {},
        "embeddings": {},
        "xai": {},
    }

    # fase 1 — brazos seed 42 (2 esquemas × 2 arquitecturas) + LOF congelado
    models: dict = {}
    for schema in ("fs1", "fs2-lite"):
        for arch in ("AE-S", "AE-M"):
            name = f"{schema}+{arch}"
            det, thr, fit_s = fit_arm(schema, arch, args.seed, trains[schema].x, args.fpr)
            r = evaluate(det, thr, tests[schema], headers)
            arm = {
                "note": f"cambio único = esquema ({schema}); train v1.1; seed {args.seed}",
                "n_features": trains[schema].x.shape[1],
                "n_parameters": det.n_parameters,
                "threshold": round(thr, 6),
                "fit_seconds": round(fit_s, 2),
                "validation": evaluate(det, thr, vals[schema], headers),
                "test": r,
                "fpr_by_profile_test": fpr_by_profile(r),
                "focus_fault_recalls": focus_recalls(r),
            }
            if schema in sevs:
                rs = evaluate(det, thr, sevs[schema], headers)
                arm["severity"] = {
                    "recall_by_duration": rs["recall_by_duration"],
                    "fpr_by_normal_scenario": rs["fpr_by_normal_scenario"],
                }
            results["arms"][name] = arm
            models[name] = (det, thr)
            record_run(
                RUNS_FILE,
                {
                    "experiment": "e7_fs2_ablation",
                    "arm": name,
                    "git_sha": git_sha(REPO_ROOT),
                    "window": CANON_W,
                    "stride": CANON_S,
                    "seed": args.seed,
                    "feature_schema": schema,
                    "dataset_version": "1.1",
                    "dataset_hash": v11_meta["dataset_hash"],
                    "threshold": arm["threshold"],
                    "metrics": r["point"],
                    "peak_rss_mb": peak_rss_mb(),
                },
            )
            tp = r["point"]
            print(
                f"  {name:14s} F1={tp['f1']:.3f} FPR={tp['fp_rate_normal']:.3f} "
                f"autovia={arm['fpr_by_profile_test'].get('highway')} "
                f"foco={arm['focus_fault_recalls']}"
            )
    # LOF congelado: fs1, train v1.0, umbral del freeze — jamás re-entrenado/reajustado
    lof = next(d for d in make_baselines(args.seed) if d.name == "lof")
    lof.fit(train10_fs1.x)
    thr_lof = threshold_from_normal(lof.scores(train10_fs1.x), target_fpr=args.fpr)
    assert abs(thr_lof - LOF_FROZEN_THRESHOLD) < 1e-6, "el LOF congelado no se reproduce"
    r = evaluate(lof, thr_lof, tests["fs1"], headers)
    results["arms"]["lof_frozen"] = {
        "note": "brazo congelado arms-freeze-v1 (fs1, train v1.0; sin re-entrenar)",
        "threshold": round(float(thr_lof), 6),
        "validation": evaluate(lof, thr_lof, vals["fs1"], headers),
        "test": r,
        "fpr_by_profile_test": fpr_by_profile(r),
        "focus_fault_recalls": focus_recalls(r),
    }
    if "fs1" in sevs:
        rs = evaluate(lof, thr_lof, sevs["fs1"], headers)
        results["arms"]["lof_frozen"]["severity"] = {
            "recall_by_duration": rs["recall_by_duration"],
            "fpr_by_normal_scenario": rs["fpr_by_normal_scenario"],
        }

    # fase 2 — réplica seeds 43/44 de los 4 brazos AE (variabilidad de la comparación)
    seed_models: dict[str, list] = {n: [d] for n, (d, _t) in models.items()}
    for s in (args.seed + 1, args.seed + 2):
        for schema in ("fs1", "fs2-lite"):
            for arch in ("AE-S", "AE-M"):
                name = f"{schema}+{arch}"
                det, thr, _ = fit_arm(schema, arch, s, trains[schema].x, args.fpr)
                rt = evaluate(det, thr, tests[schema], headers)
                results["seeds"].setdefault(name, {})[str(s)] = {
                    "threshold": round(thr, 6),
                    "test_point": rt["point"],
                    "fpr_by_profile": fpr_by_profile(rt),
                    "focus_fault_recalls": focus_recalls(rt),
                    "held_out_recall": rt["per_category"].get("held_out_recall"),
                }
                seed_models[name].append(det)

    # fase 3 — embeddings (D2) por brazo
    labels = np.array(
        [
            (headers[sid].fault or "normal") if y == 1 else "normal"
            for sid, y in zip(tests["fs1"].session_ids, tests["fs1"].y, strict=True)
        ]
    )
    for name, (det, _thr) in models.items():
        schema = "fs2-lite" if name.startswith("fs2") else "fs1"
        z = det.embed(tests[schema].x)
        emb: dict = {"latent_dim": int(z.shape[1])}
        anom = labels != "normal"
        emb["silhouette_all_vs_normal"] = round(float(silhouette_score(z, labels != "normal")), 4)
        if anom.sum() > 2 and len(set(labels[anom])) > 1:
            emb["silhouette_between_faults"] = round(
                float(silhouette_score(z[anom], labels[anom])), 4
            )
        pca = PCA(n_components=min(4, z.shape[1]), random_state=0).fit(z)
        emb["pca_var_explained_2c"] = round(float(pca.explained_variance_ratio_[:2].sum()), 4)
        results["embeddings"][name] = emb

    # fase 4 — XAI comparado: mejor brazo fs2-lite + su homólogo fs1 (misma arquitectura)
    def fpr_of(n: str) -> float:
        return results["arms"][n]["test"]["point"]["fp_rate_normal"]

    def f1_of(n: str) -> float:
        return results["arms"][n]["test"]["point"]["f1"]

    fs2_best = min(("fs2-lite+AE-S", "fs2-lite+AE-M"), key=lambda n: (fpr_of(n), -f1_of(n)))
    fs1_twin = fs2_best.replace("fs2-lite", "fs1")
    print(f"fase 4: XAI en finalistas {fs2_best} vs {fs1_twin}…")
    results["xai"] = xai_compare(
        {n: models[n] for n in (fs2_best, fs1_twin)},
        trains,
        tests,
        labels,
        headers,
        {fs2_best: seed_models[fs2_best], fs1_twin: seed_models[fs1_twin]},
        args.seed,
    )
    results["xai"]["finalists"] = {"fs2": fs2_best, "fs1": fs1_twin}

    results["total_runtime_s"] = round(time.perf_counter() - t_start, 1)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print(f"\nresultados → {RESULTS_JSON.name} ({results['total_runtime_s']}s)")

    if not args.skip_figs:
        from e7_figs import make_figures

        figs = REPO_ROOT / "docs" / "fase17" / "figs"
        make_figures(results, figs)
        print(f"figuras → {figs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
