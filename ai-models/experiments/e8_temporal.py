"""Experimento E8 (EXP-ANOM-009, EXPLORATORIO) — autoencoders recurrentes (F18).

Hipótesis HX-ML-3 (congelada en `configs/exp-anom-009.yaml` ANTES de ejecutar): un
autoencoder recurrente entrenado solo con normalidad, que observa la SECUENCIA cruda
`[T × PID]` en lugar de estadísticos por ventana, detecta anomalías lentas y relacionales
mejor que los detectores estáticos MANTENIENDO el FPR por escenario normal.

Fases: 0 datasets secuenciales + estáticos con auditoría anti-leakage · 1 brazos
canónicos (LSTM-AE, GRU-AE, AE estático S/M, LOF congelado) · 2 barrido de longitud
(30/60/120 pasos, con duración real declarada) · 3 réplica de seeds 43/44 · 4 BRAZO
CONTROL diagnóstico (cobertura de cuantización del LTFT: prueba directa de la causa
refinada de F17) · 5 ablation fs1-sequence · 6 embeddings D2 · 7 análisis de la
transición de cuantización · 8 XAI feature×time · 9 indicaciones edge.

Umbral SIEMPRE por cuantil (1-FPR) sobre el train del brazo; test jamás interviene.
Sin seeds reservadas (exploratorias 426-599 para el brazo control). LOF y AE estático NO
se reoptimizan. Validez: entorno emulado/sintético.

Uso: python experiments/e8_temporal.py --sessions data/sessions [--seed 42] [--fpr 0.01]
"""

import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from sklearn.metrics import average_precision_score, roc_auc_score

from ai_models.anomaly.recurrent_autoencoder import RecurrentAutoencoderDetector
from ai_models.data.sequence_dataset import (
    SequenceDataset,
    sequences_from_matrices,
)
from ai_models.data.snapshot_matrix import MATRIX_PIDS, matrix_from_snapshots
from ai_models.evaluation.protocol import point_metrics, threshold_from_normal
from ai_models.tracking import peak_rss_mb
from diagnostic_agent.telemetry.snapshots import build_from_ticks
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.session_io import read_session_series
from obd_lab.generate import write_session

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_FILE = Path(__file__).parent / "runs.jsonl"
RESULTS_JSON = Path(__file__).parent / "e8_results.json"
SEVERITY_DIR = REPO_ROOT / "data" / "sessions_f14sev" / "test"
CONTROL_DIR = REPO_ROOT / "data" / "sessions_qcontrol" / "train"

CANON_STEPS, CANON_STRIDE = 60, 30
LENGTHS = (30, 60, 120)
FOCUS_FAULTS = ("joint_slow_drift", "load_coolant_decouple", "corr_break_rpm_maf")
#: Semillas exploratorias (426-599) de autovía cuyo LTFT SÍ cruza una frontera de
#: cuantización — verificado por barrido antes de generarlas (brazo control, fase 4).
CONTROL_SEEDS = (437, 456, 459, 476, 482, 487, 488, 497, 502, 509)
LTFT_IDX = MATRIX_PIDS.index("LONG_FUEL_TRIM_1")


# --------------------------------------------------------------- fase 0: datasets
def _session_items(session_dir: Path) -> list[tuple[Any, dict[str, Any]]]:
    """Sesiones → (WideMatrix, metadatos de escenario) por el camino wide canónico."""
    items = []
    for path in sorted(session_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        n = min(len(v) for v in series.values())
        ticks = [{pid: series[pid][i] for pid in series} for i in range(n)]
        snaps, _links = build_from_ticks(
            ticks,
            session_id=header.session_id,
            vehicle_id=header.vehicle_id,
            device_id=header.device_id,
        )
        sc = header.scenario
        items.append(
            (
                matrix_from_snapshots(snaps),
                {
                    "category": sc.category if sc else "unknown",
                    "fault": sc.fault if sc else None,
                    "fault_start_s": sc.fault_start_s if sc else None,
                    "fault_end_s": sc.fault_end_s if sc else None,
                    "duration_s": sc.duration_s if sc else 0.0,
                },
            )
        )
    return items


def build_sequences(session_dir: Path, steps: int, stride: int) -> SequenceDataset:
    return sequences_from_matrices(_session_items(session_dir), steps, stride)


# ------------------------------------------------------------------- evaluación
def evaluate_seq(  # noqa: PLR0915
    scores: np.ndarray, thr: float, ds: SequenceDataset, headers: dict
) -> dict:
    """Métricas del protocolo + desgloses + métricas temporales para secuencias."""
    flagged = scores > thr
    res: dict = {"point": asdict(point_metrics(ds.y, flagged))}
    n_anom = int(ds.y.sum())
    res["point"]["fn_rate"] = (
        round(float(((ds.y == 1) & ~flagged).sum() / n_anom), 4) if n_anom else None
    )
    if ds.y.any() and (ds.y == 0).any():
        res["pr_auc"] = round(float(average_precision_score(ds.y, scores)), 4)
        res["roc_auc"] = round(float(roc_auc_score(ds.y, scores)), 4)
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
    delays: list[float] = []
    first_positions: list[float] = []
    persistence: list[float] = []
    false_alarm_runs: list[float] = []
    episodes = episodes_detected = 0
    for sid in sorted(set(ds.session_ids)):
        idx = np.array([s == sid for s in ds.session_ids])
        sc = headers.get(sid)
        prof = sc.driving_profile if sc else "unknown"
        if not (idx & (ds.y == 1)).any():
            fpr_by_scenario[f"{prof}:{sid}"] = round(float(flagged[idx].mean()), 4)
            run = 0
            for v in flagged[idx]:
                if v:
                    run += 1
                elif run:
                    false_alarm_runs.append(run * ds.duration_s / 2)
                    run = 0
            if run:
                false_alarm_runs.append(run * ds.duration_s / 2)
            continue
        episodes += 1
        fidx = idx & (ds.y == 1)
        r = float(flagged[fidx].mean())
        fault = next(f for f, m in zip(ds.faults, idx, strict=True) if m and f)
        per_fault.setdefault(fault, []).append(r)
        persistence.append(r)
        f_starts = [ds.starts_s[i] for i in np.where(fidx)[0]]
        hits = [ds.starts_s[i] for i in np.where(fidx & flagged)[0]]
        dur = (sc.fault_end_s or sc.duration_s) - (sc.fault_start_s or 0.0) if sc else 0.0
        recall_by_duration[sid] = {"fault": fault, "duration_s": dur, "recall": round(r, 4)}
        if hits:
            episodes_detected += 1
            delays.append(min(hits) - min(f_starts))
            first_positions.append((min(hits) - min(f_starts)) / max(dur, 1e-9))
    res["per_fault_recall"] = {k: round(float(np.mean(v)), 4) for k, v in sorted(per_fault.items())}
    res["fpr_by_normal_scenario"] = fpr_by_scenario
    res["recall_by_duration"] = recall_by_duration
    res["focus_fault_recalls"] = {f: res["per_fault_recall"].get(f) for f in FOCUS_FAULTS}
    res["event"] = {"episodes_total": episodes, "episodes_detected": episodes_detected}
    res["temporal"] = {
        "mean_detection_delay_s": round(float(np.mean(delays)), 1) if delays else None,
        "time_to_detection_s": round(float(np.median(delays)), 1) if delays else None,
        "first_detection_position_frac": round(float(np.mean(first_positions)), 3)
        if first_positions
        else None,
        "anomaly_score_persistence": round(float(np.mean(persistence)), 4) if persistence else None,
        "mean_false_alarm_duration_s": round(float(np.mean(false_alarm_runs)), 1)
        if false_alarm_runs
        else 0.0,
    }
    return res


def fpr_by_profile(res: dict) -> dict:
    agg: dict = {}
    for key, v in res["fpr_by_normal_scenario"].items():
        agg.setdefault(key.split(":", 1)[0], []).append(v)
    return {p: round(float(np.mean(v)), 4) for p, v in sorted(agg.items())}


def fit_recurrent(
    kind: str, seed: int, tr: SequenceDataset, fpr: float, **kw: Any
) -> tuple[RecurrentAutoencoderDetector, float, float]:
    det = RecurrentAutoencoderDetector(kind=kind, seed=seed, **kw)
    t0 = time.perf_counter()
    det.fit(tr.x, tr.mask)
    fit_s = time.perf_counter() - t0
    thr = threshold_from_normal(det.scores(tr.x, tr.mask), target_fpr=fpr)
    return det, float(thr), fit_s


def arm_record(
    det: RecurrentAutoencoderDetector,
    thr: float,
    fit_s: float,
    ds: SequenceDataset,
    res: dict,
    res_val: dict,
    note: str,
) -> dict:
    t0 = time.perf_counter()
    det.scores(ds.x[:50], ds.mask[:50])
    infer_ms = (time.perf_counter() - t0) / min(50, len(ds.x)) * 1000
    return {
        "note": note,
        "model": det.registry_record(),
        "sequence_steps": ds.steps,
        "sequence_duration_seconds": ds.duration_s,
        "sampling_rate_hz": ds.sample_rate_hz,
        "threshold_method": "cuantil (1-FPR) sobre train del brazo",
        "threshold_partition": "train",
        "threshold_value": round(thr, 6),
        "fit_seconds": round(fit_s, 1),
        "infer_ms_per_sequence": round(infer_ms, 3),
        "peak_rss_mb": peak_rss_mb(),
        "loss_first_last": [round(det.loss_history[0], 6), round(det.loss_history[-1], 6)],
        "val_loss_best": round(min(det.val_history), 6) if det.val_history else None,
        "validation": res_val,
        "test": res,
        "fpr_by_profile_test": fpr_by_profile(res),
    }


class _StaticView:
    """Vista de un WindowDataset con la interfaz que consume ``evaluate_seq``.

    Permite evaluar los brazos estáticos (AE fs1, LOF congelado) con EXACTAMENTE la misma
    función de métricas que los secuenciales: la comparación no depende del evaluador.
    """

    def __init__(self, ds: Any, headers: dict, steps: int = CANON_STEPS, rate: float = 1.0):
        self.y = ds.y
        self.categories = ds.categories
        self.session_ids = ds.session_ids
        self.starts_s = ds.window_starts
        self.steps = steps
        self.sample_rate_hz = rate
        self.faults = [
            headers[s].fault if s in headers and headers[s].fault else None for s in ds.session_ids
        ]

    @property
    def duration_s(self) -> float:
        return self.steps / self.sample_rate_hz


def materialize_control_normals(out: Path) -> dict:
    """Fase 4 — normalidad de autovía que SÍ cruza fronteras de cuantización del LTFT.

    Manipulación diagnóstica DECLARADA (no ajuste de métricas): las semillas se
    seleccionaron por barrido según el criterio «el LTFT cruza al menos una frontera»,
    nunca por su efecto en el resultado. Sirve para probar la causa refinada de F17.
    """
    out.mkdir(parents=True, exist_ok=True)
    for seed in CONTROL_SEEDS:
        spec = ScenarioSpec(
            scenario_id=f"nq-highway-seed{seed}",
            description="normal de autovía con cruce de cuantización de LTFT (brazo control F18)",
            category="normal",
            driving_profile="highway",
            duration_s=1800.0,
            seed=seed,
        )
        target = out / f"{spec.scenario_id}-seed{spec.seed}.jsonl"
        if not target.exists():
            write_session(spec, out)
    return {
        "n_sessions": len(list(out.glob("*.jsonl"))),
        "seeds": list(CONTROL_SEEDS),
        "selection_criterion": "el LTFT cruza >=1 frontera de cuantizacion (barrido 426-599)",
        "provenance": "SIMULATED (obd-lab, determinista por semilla)",
        "purpose": "brazo control diagnostico; NO candidato a adopcion",
    }


def ltft_crossing_step(session_dir: Path, session_id: str) -> float | None:
    """Instante (s) del primer cruce de cuantización del LTFT en una sesión, si existe."""
    for path in sorted(session_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        if header.session_id != session_id:
            continue
        lt = np.asarray(series["LONG_FUEL_TRIM_1"], dtype=np.float64)
        diff = np.diff(lt) != 0
        rate = header.scenario.sample_rate_hz if header.scenario else 1.0
        return float(int(np.argmax(diff)) / rate) if diff.any() else None
    return None


def quantization_analysis(
    scores_by_arm: dict, ds: SequenceDataset, thresholds: dict, crossings: dict
) -> dict:
    """Fase 7 — ¿el modelo distingue adaptación discreta NORMAL de deriva anómala?"""
    normal_idx = ds.y == 0
    post = np.zeros(len(ds.y), dtype=bool)
    for i, (sid, st) in enumerate(zip(ds.session_ids, ds.starts_s, strict=True)):
        c = crossings.get(sid)
        if c is not None and st + ds.duration_s > c:
            post[i] = True
    slow = np.array([f in ("joint_slow_drift", "maf_drift") for f in ds.faults], dtype=bool) & (
        ds.y == 1
    )
    out: dict = {
        "n_normal_post_crossing": int((normal_idx & post).sum()),
        "n_normal_pre_crossing": int((normal_idx & ~post).sum()),
        "n_slow_drift_anomalous": int(slow.sum()),
        "crossings_detected_s": {k: v for k, v in sorted(crossings.items()) if v is not None},
        "note": (
            "la transición de cuantización es comportamiento NORMAL del protocolo/sensor: "
            "marcarla es un falso positivo, no una detección"
        ),
        "by_arm": {},
    }
    for arm, sc in scores_by_arm.items():
        thr = thresholds[arm]
        pre_m = normal_idx & ~post
        post_m = normal_idx & post
        out["by_arm"][arm] = {
            "flag_rate_normal_pre_crossing": round(float((sc[pre_m] > thr).mean()), 4)
            if pre_m.any()
            else None,
            "flag_rate_normal_post_crossing": round(float((sc[post_m] > thr).mean()), 4)
            if post_m.any()
            else None,
            "mean_score_normal_pre": round(float(sc[pre_m].mean()), 6) if pre_m.any() else None,
            "mean_score_normal_post": round(float(sc[post_m].mean()), 6) if post_m.any() else None,
            "mean_score_slow_drift": round(float(sc[slow].mean()), 6) if slow.any() else None,
            "recall_slow_drift": round(float((sc[slow] > thr).mean()), 4) if slow.any() else None,
            "separates_normal_transition_from_drift": bool(
                slow.any() and post_m.any() and sc[slow].mean() > sc[post_m].mean()
            ),
        }
    return out


# --------------------------------------------------------------- fase 8: XAI temporal
def _torch_scorer(det: RecurrentAutoencoderDetector) -> Any:
    """Envoltorio torch de la función EXPLICADA: f(sequence) = reconstruction_error."""
    import torch

    class _Scorer(torch.nn.Module):  # type: ignore[misc, name-defined]
        def __init__(self, model: Any) -> None:
            super().__init__()
            self.model = model

        def forward(self, t: Any) -> Any:
            rec = self.model(t)
            return ((rec - t) ** 2).mean(dim=(1, 2)).unsqueeze(-1)

    s = _Scorer(det._model)
    s.eval()
    return s


def temporal_shap(
    det: RecurrentAutoencoderDetector, bg: np.ndarray, x: np.ndarray
) -> tuple[np.ndarray, dict]:
    """Atribución feature×tiempo con GradientExplainer (compatible con LSTM/GRU en torch).

    Elección DOCUMENTADA: DeepExplainer no soporta las celdas recurrentes (aviso
    «unrecognized nn.Module» + fallo de aditividad) y Permutation sobre la entrada
    aplanada cuesta ~27 s por secuencia a 60×12; GradientExplainer (expected gradients,
    variante SHAP soportada para PyTorch) produce la matriz [T×F] nativamente. La
    elección se VALIDA empíricamente contra Permutation en una submuestra (ver
    `explainer_cross_check`), no se justifica por conveniencia.
    """
    import shap
    import torch

    scorer = _torch_scorer(det)
    ex = shap.GradientExplainer(scorer, torch.from_numpy(bg))
    vals = np.asarray(ex.shap_values(torch.from_numpy(x)))
    if vals.ndim == 4:  # (n, T, F, 1)
        vals = vals[..., 0]
    return np.asarray(vals, dtype=np.float64), {
        "shap_version": shap.__version__,
        "explainer": "shap.GradientExplainer (expected gradients)",
        "explained_function": "f(sequence) = reconstruction_error(sequence)",
        "background_size": int(bg.shape[0]),
        "background_hash": __import__("hashlib")
        .sha256(np.ascontiguousarray(bg).tobytes())
        .hexdigest(),
        "incompatible_explainers": {
            "shap.DeepExplainer": "no soporta celdas LSTM/GRU (aditividad falla)",
            "shap.explainers.Permutation": (
                "compatible pero ~27 s/secuencia a 60x12; se usa como validación cruzada"
            ),
        },
    }


def permutation_cross_check(
    det: RecurrentAutoencoderDetector, bg: np.ndarray, x: np.ndarray, grad_vals: np.ndarray, k: int
) -> dict:
    """Valida la elección del explainer: acuerdo de celdas Top-K Gradient vs Permutation."""
    import shap

    from ai_models.xai.temporal import top_k_cells

    steps, feats = x.shape[1], x.shape[2]
    names = list(MATRIX_PIDS)

    def f(flat: np.ndarray) -> np.ndarray:
        xs = flat.reshape(-1, steps, feats).astype(np.float32)
        return det.scores_standardized(xs)

    masker = shap.maskers.Independent(bg.reshape(bg.shape[0], -1), max_samples=bg.shape[0])
    ex = shap.explainers.Permutation(f, masker, max_evals=2 * steps * feats + 1, seed=0)
    t0 = time.perf_counter()
    pvals = np.asarray(ex(x.reshape(x.shape[0], -1), silent=True).values).reshape(x.shape)
    agree = [
        len(set(top_k_cells(grad_vals[i], names, k)) & set(top_k_cells(pvals[i], names, k)))
        / len(set(top_k_cells(grad_vals[i], names, k)) | set(top_k_cells(pvals[i], names, k)))
        for i in range(x.shape[0])
    ]
    return {
        "n_sequences": int(x.shape[0]),
        "k_cells": k,
        "jaccard_gradient_vs_permutation": round(float(np.mean(agree)), 4),
        "permutation_runtime_seconds": round(time.perf_counter() - t0, 1),
    }


def xai_phase(  # noqa: PLR0915
    models: dict, seed_models: dict, trains: dict, test: SequenceDataset, seed: int
) -> dict:
    """Fase 8 — atribución feature×tiempo sobre los brazos recurrentes finalistas."""
    from ai_models.xai.metrics import random_recall_baseline
    from ai_models.xai.temporal import (
        aggregate_by_feature,
        aggregate_by_time,
        cell_stability_jaccard,
        feature_attribution_recall_at_k,
        feature_time_hit_at_k,
        temporal_attribution_recall_at_k,
        temporal_gt_for,
        top_k_cells,
    )

    names = list(MATRIX_PIDS)
    n_steps, n_feat = test.steps, len(names)
    rng = np.random.default_rng(seed)
    out: dict = {}
    for arm, (det, thr) in models.items():
        tr = trains[arm]
        bg_idx = np.sort(rng.choice(tr.x.shape[0], size=min(60, tr.x.shape[0]), replace=False))
        bg = det._transform(tr.x[bg_idx], tr.mask[bg_idx])
        scores = det.scores(test.x, test.mask)
        flagged = scores > thr
        # muestreo estratificado: TP por fallo (con GT temporal no vacío), FP y TN normales
        sample: dict[str, list[int]] = {}
        for fault in sorted({f for f in test.faults if f}):
            cand = [
                i
                for i in range(len(test.y))
                if test.faults[i] == fault and test.y[i] == 1 and flagged[i]
            ]
            sample[f"TP:{fault}"] = cand[:3]
        norm = [i for i in range(len(test.y)) if test.y[i] == 0]
        sample["FP:normal"] = [i for i in norm if flagged[i]][:6]
        sample["TN:normal"] = [i for i in norm if not flagged[i]][:4]
        idx = sorted({i for v in sample.values() for i in v})
        if not idx:
            out[arm] = {"error": "sin muestras explicables"}
            continue
        xs = det._transform(test.x[idx], test.mask[idx])
        t0 = time.perf_counter()
        vals, meta = temporal_shap(det, bg, xs)
        runtime = time.perf_counter() - t0
        err = det.per_step_feature_error(test.x[idx], test.mask[idx])

        fidelity: dict = {}
        for key, sel in sample.items():
            if not key.startswith("TP:") or not sel:
                continue
            fault = key.split(":", 1)[1]
            fars, tars, fths = [], [], []
            r_far, r_tar, r_fth, gts = [], [], [], []
            skipped = 0
            for i in sel:
                pos = idx.index(i)
                iv = test.fault_intervals[i]
                if iv is None:
                    continue
                gt = temporal_gt_for(
                    fault,
                    sequence_start_s=test.starts_s[i],
                    n_steps=n_steps,
                    sample_rate_hz=test.sample_rate_hz,
                    fault_start_s=iv[0],
                    fault_end_s=iv[1],
                )
                if not gt.time_steps:  # sin GT temporal: se EXCLUYE, no se puntúa 0
                    skipped += 1
                    continue
                nf, nt = len(gt.features), len(gt.time_steps)
                fars.append(feature_attribution_recall_at_k(vals[pos], names, gt.features, 5))
                tars.append(temporal_attribution_recall_at_k(vals[pos], gt.time_steps, 10))
                fths.append(feature_time_hit_at_k(vals[pos], names, gt.features, gt.time_steps, 10))
                # azar hipergeométrico congelado (adenda XAI v1 §8), por muestra
                r_far.append(random_recall_baseline(n_feat, nf, 5))
                r_tar.append(random_recall_baseline(n_steps, nt, 10))
                r_fth.append(random_recall_baseline(n_steps * n_feat, nf * nt, 10))
                gts.append((nf, nt))
            if not fars:
                continue
            fidelity[fault] = {
                "n_explained": len(fars),
                "n_excluded_no_temporal_gt": skipped,
                "gt_features_mean": round(float(np.mean([g[0] for g in gts])), 2),
                "gt_steps_mean": round(float(np.mean([g[1] for g in gts])), 2),
                "FAR@5": round(float(np.mean(fars)), 4),
                "FAR@5_random": round(float(np.mean(r_far)), 4),
                "TAR@10": round(float(np.mean(tars)), 4),
                "TAR@10_random": round(float(np.mean(r_tar)), 4),
                "FTH@10": round(float(np.mean(fths)), 4),
                "FTH@10_random": round(float(np.mean(r_fth)), 4),
            }
        # agreement de celdas con el error de reconstrucción temporal del propio modelo
        agree = [
            len(set(top_k_cells(vals[j], names, 10)) & set(top_k_cells(err[j], names, 10)))
            / len(set(top_k_cells(vals[j], names, 10)) | set(top_k_cells(err[j], names, 10)))
            for j in range(len(idx))
        ]
        # estabilidad entre seeds y bajo perturbación (σ = 0.05·std sobre entrada estandarizada)
        stab: dict = {"n_sequences": len(idx)}
        if seed_models.get(arm):
            per_seed = [vals]
            for det_s in seed_models[arm]:
                xs_s = det_s._transform(test.x[idx], test.mask[idx])
                bg_s = det_s._transform(tr.x[bg_idx], tr.mask[bg_idx])
                per_seed.append(temporal_shap(det_s, bg_s, xs_s)[0])
            stab["between_seeds_cell_jaccard"] = round(
                float(
                    np.mean(
                        [
                            cell_stability_jaccard([m[j] for m in per_seed], names, 10)
                            for j in range(len(idx))
                        ]
                    )
                ),
                4,
            )
        pert = np.random.default_rng(0).standard_normal(xs.shape) * 0.05
        vals_p, _m = temporal_shap(det, bg, (xs + pert).astype(np.float32))
        stab["under_perturbation_cell_jaccard"] = round(
            float(
                np.mean(
                    [
                        cell_stability_jaccard([vals[j], vals_p[j]], names, 10)
                        for j in range(len(idx))
                    ]
                )
            ),
            4,
        )
        # vistas globales derivadas de la matriz (nunca sustitutas)
        gf = aggregate_by_feature(np.abs(vals).mean(axis=0), names)
        gt_time = aggregate_by_time(np.abs(vals).mean(axis=0))
        fp_examples = {
            str(i): {
                "session": test.session_ids[i],
                "start_s": test.starts_s[i],
                "top_cells": [[t, f] for t, f in top_k_cells(vals[idx.index(i)], names, 5)],
            }
            for i in sample["FP:normal"][:4]
        }
        out[arm] = {
            "explainer": meta,
            "samples_explained": len(idx),
            "runtime_seconds": round(runtime, 1),
            "fidelity_by_fault": fidelity,
            "agreement_with_temporal_error": {
                "mean_cell_jaccard10": round(float(np.mean(agree)), 4),
            },
            "stability": stab,
            "global_feature_attribution": {k: round(v, 5) for k, v in gf.items()},
            "global_temporal_attribution_last10": {
                str(t): round(gt_time[t], 5) for t in sorted(gt_time)[-10:]
            },
            "fp_examples": fp_examples,
        }
        # validación cruzada de la elección de explainer (submuestra pequeña por coste)
        out[arm]["explainer_cross_check"] = permutation_cross_check(
            det, bg[:20], xs[:2], vals[:2], 10
        )
    return out


def main() -> int:  # noqa: PLR0915, PLR0912
    import argparse
    import json

    from e4_wide_parity import build_dataset_wide
    from e6_ae_v2 import LOF_FROZEN_THRESHOLD, _headers, materialize_v11
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score

    from ai_models.anomaly.autoencoder import AutoencoderDetector
    from ai_models.anomaly.baselines import make_baselines
    from ai_models.data.sequence_dataset import audit_overlap, sequence_manifest
    from ai_models.tracking import git_sha, record_run

    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--skip-xai", action="store_true")
    args = parser.parse_args()
    t_start = time.perf_counter()
    results: dict = {
        "validity_note": (
            "EXPLORATORIO; validez actual = entorno emulado/sintético (obd-lab). Sin validez "
            "externa hasta HCRL (dataset real/replay) y validación ARM64/RPi5 (dependencias "
            "externas registradas aparte)."
        ),
        "hypothesis": "HX-ML-3 (congelada en configs/exp-anom-009.yaml antes de ejecutar)",
        "datasets": {},
        "arms": {},
        "length_sweep": {},
        "seeds": {},
        "control_arm": {},
        "fs1_sequence_ablation": {},
        "embeddings": {},
        "quantization_analysis": {},
        "xai": {},
    }

    # ---------------------------------------------------------------- fase 0: datasets
    print("fase 0: datasets…", flush=True)
    v11_root = REPO_ROOT / "data" / "sessions_v11"
    v11_meta = materialize_v11(args.sessions, v11_root)
    headers: dict = {}
    for d in (
        args.sessions / "train",
        args.sessions / "validation",
        args.sessions / "test",
        v11_root / "train",
        SEVERITY_DIR,
    ):
        if d.exists():
            headers.update(_headers(d))
    seq: dict[int, dict[str, SequenceDataset]] = {}
    for steps in LENGTHS:
        stride = steps // 2
        seq[steps] = {
            "train": build_sequences(v11_root / "train", steps, stride),
            "validation": build_sequences(args.sessions / "validation", steps, stride),
            "test": build_sequences(args.sessions / "test", steps, stride),
        }
        tr, va, te = seq[steps]["train"], seq[steps]["validation"], seq[steps]["test"]
        for a, b, tag in ((tr, va, "train-val"), (tr, te, "train-test"), (va, te, "val-test")):
            rep = audit_overlap(a, b)
            assert rep.clean, f"leakage {tag} en steps={steps}: {rep}"
        assert not tr.y.any(), "el train secuencial debe ser 100% normal"
        results["datasets"][str(steps)] = sequence_manifest(
            tr,
            dataset_id="sequence-dataset-v1",
            source=f"obd-lab-suite-v1 train v1.1 (hash {v11_meta['dataset_hash'][:12]})",
            provenance="SIMULATED (obd-lab; determinista por semilla)",
            seeds=v11_meta["seeds"],
        ) | {
            "anti_leakage_audited": True,
            "n_test_sequences": int(te.x.shape[0]),
            "n_test_anomalous": int(te.y.sum()),
        }
        print(f"  steps={steps} ({steps}s) train={tr.x.shape} test={te.x.shape}", flush=True)
    seq_sev = (
        build_sequences(SEVERITY_DIR, CANON_STEPS, CANON_STRIDE) if SEVERITY_DIR.exists() else None
    )
    # estáticos (fs1) para los brazos de referencia
    st_train10, _, _ = build_dataset_wide(args.sessions / "train", CANON_STEPS, CANON_STRIDE)
    st_train11, _, _ = build_dataset_wide(v11_root / "train", CANON_STEPS, CANON_STRIDE)
    st_val, _, _ = build_dataset_wide(args.sessions / "validation", CANON_STEPS, CANON_STRIDE)
    st_test, _, _ = build_dataset_wide(args.sessions / "test", CANON_STEPS, CANON_STRIDE)
    v_test = _StaticView(st_test, headers)
    v_val = _StaticView(st_val, headers)

    # ------------------------------------------------- fase 1: brazos canónicos (60 pasos)
    print("fase 1: brazos canónicos…", flush=True)
    tr, va, te = seq[CANON_STEPS]["train"], seq[CANON_STEPS]["validation"], seq[CANON_STEPS]["test"]
    models: dict = {}
    trains_for_arm: dict = {}
    for kind in ("lstm", "gru"):
        det, thr, fit_s = fit_recurrent(
            kind, args.seed, tr, args.fpr, hidden=32, latent=8, epochs=60
        )
        r = evaluate_seq(det.scores(te.x, te.mask), thr, te, headers)
        r_val = evaluate_seq(det.scores(va.x, va.mask), thr, va, headers)
        name = f"{kind}_ae"
        results["arms"][name] = arm_record(
            det,
            thr,
            fit_s,
            te,
            r,
            r_val,
            f"secuencia cruda [60 x 12]; train v1.1; seed {args.seed}",
        )
        if seq_sev is not None:
            rs = evaluate_seq(det.scores(seq_sev.x, seq_sev.mask), thr, seq_sev, headers)
            results["arms"][name]["severity"] = {
                "recall_by_duration": rs["recall_by_duration"],
                "fpr_by_normal_scenario": rs["fpr_by_normal_scenario"],
            }
        models[name] = (det, thr)
        trains_for_arm[name] = tr
        record_run(
            RUNS_FILE,
            {
                "experiment": "e8_temporal",
                "arm": name,
                "git_sha": git_sha(REPO_ROOT),
                "sequence_steps": CANON_STEPS,
                "sequence_duration_seconds": te.duration_s,
                "seed": args.seed,
                "dataset_version": "sequence-dataset-v1",
                "threshold": round(thr, 6),
                "metrics": r["point"],
                "peak_rss_mb": peak_rss_mb(),
            },
        )
        p = r["point"]
        print(
            f"  {name}: F1={p['f1']:.3f} FPR={p['fp_rate_normal']:.3f} "
            f"foco={r['focus_fault_recalls']}",
            flush=True,
        )
    # AE estático fs1 (S y M) — NO se reoptimizan: misma configuración que F17
    for tag, kw in (
        ("static_ae_fs1_s", {}),
        ("static_ae_fs1_m", {"hidden": (64, 32), "latent": 16}),
    ):
        det = AutoencoderDetector(seed=args.seed, scaler_kind="standard", **kw)
        det.fit(st_train11.x)
        thr = threshold_from_normal(det.scores(st_train11.x), target_fpr=args.fpr)
        r = evaluate_seq(det.scores(st_test.x), thr, v_test, headers)
        results["arms"][tag] = {
            "note": "AE estático fs1 conocido (F17), sin reoptimizar",
            "model": {"n_parameters": det.n_parameters},
            "threshold_method": "cuantil (1-FPR) sobre train del brazo",
            "threshold_partition": "train",
            "threshold_value": round(float(thr), 6),
            "validation": evaluate_seq(det.scores(st_val.x), thr, v_val, headers),
            "test": r,
            "fpr_by_profile_test": fpr_by_profile(r),
        }
        models[tag] = (det, float(thr))
        print(
            f"  {tag}: F1={r['point']['f1']:.3f} FPR={r['point']['fp_rate_normal']:.3f}", flush=True
        )
    # LOF congelado
    lof = next(d for d in make_baselines(args.seed) if d.name == "lof")
    lof.fit(st_train10.x)
    thr_lof = threshold_from_normal(lof.scores(st_train10.x), target_fpr=args.fpr)
    assert abs(thr_lof - LOF_FROZEN_THRESHOLD) < 1e-6, "el LOF congelado no se reproduce"
    r = evaluate_seq(lof.scores(st_test.x), thr_lof, v_test, headers)
    results["arms"]["lof_frozen"] = {
        "note": "brazo congelado arms-freeze-v1 (fs1, train v1.0); sin re-entrenar",
        "threshold_value": round(float(thr_lof), 6),
        "validation": evaluate_seq(lof.scores(st_val.x), thr_lof, v_val, headers),
        "test": r,
        "fpr_by_profile_test": fpr_by_profile(r),
    }
    print(
        f"  lof_frozen: F1={r['point']['f1']:.3f} FPR={r['point']['fp_rate_normal']:.3f}",
        flush=True,
    )

    # ------------------------------------------- fase 2: barrido de longitud de secuencia
    print("fase 2: barrido de longitud…", flush=True)
    for steps in LENGTHS:
        for kind in ("lstm", "gru"):
            if steps == CANON_STEPS:
                base = results["arms"][f"{kind}_ae"]
                results["length_sweep"].setdefault(str(steps), {})[kind] = {
                    "sequence_duration_seconds": base["sequence_duration_seconds"],
                    "test_point": base["test"]["point"],
                    "focus_fault_recalls": base["test"]["focus_fault_recalls"],
                    "fpr_by_profile": base["fpr_by_profile_test"],
                }
                continue
            s_tr, s_te = seq[steps]["train"], seq[steps]["test"]
            det, thr, _ = fit_recurrent(
                kind, args.seed, s_tr, args.fpr, hidden=32, latent=8, epochs=60
            )
            rr = evaluate_seq(det.scores(s_te.x, s_te.mask), thr, s_te, headers)
            results["length_sweep"].setdefault(str(steps), {})[kind] = {
                "sequence_duration_seconds": s_te.duration_s,
                "threshold_value": round(thr, 6),
                "test_point": rr["point"],
                "focus_fault_recalls": rr["focus_fault_recalls"],
                "fpr_by_profile": fpr_by_profile(rr),
            }
            print(
                f"  {kind} steps={steps} ({s_te.duration_s:.0f}s): F1={rr['point']['f1']:.3f} "
                f"FPR={rr['point']['fp_rate_normal']:.3f}",
                flush=True,
            )

    # -------------------------------------------------------- fase 3: réplica de seeds
    print("fase 3: seeds 43/44…", flush=True)
    seed_models: dict[str, list] = {"lstm_ae": [], "gru_ae": []}
    for s in (args.seed + 1, args.seed + 2):
        for kind in ("lstm", "gru"):
            det, thr, _ = fit_recurrent(kind, s, tr, args.fpr, hidden=32, latent=8, epochs=60)
            rr = evaluate_seq(det.scores(te.x, te.mask), thr, te, headers)
            results["seeds"].setdefault(f"{kind}_ae", {})[str(s)] = {
                "threshold_value": round(thr, 6),
                "test_point": rr["point"],
                "focus_fault_recalls": rr["focus_fault_recalls"],
                "fpr_by_profile": fpr_by_profile(rr),
            }
            seed_models[f"{kind}_ae"].append(det)

    # -------------------------------------------- fase 4: brazo control (cuantización)
    print("fase 4: brazo control de cuantización…", flush=True)
    ctl_meta = materialize_control_normals(CONTROL_DIR)
    ctl_train, _, _ = build_dataset_wide(CONTROL_DIR, CANON_STEPS, CANON_STRIDE)
    x_ctl = np.vstack([st_train11.x, ctl_train.x])
    det_ctl = AutoencoderDetector(seed=args.seed, scaler_kind="standard")
    det_ctl.fit(x_ctl)
    thr_ctl = threshold_from_normal(det_ctl.scores(x_ctl), target_fpr=args.fpr)
    r_ctl = evaluate_seq(det_ctl.scores(st_test.x), float(thr_ctl), v_test, headers)
    results["control_arm"] = {
        "note": (
            "BRAZO CONTROL DIAGNÓSTICO — no candidato a adopción. Prueba directa de la causa "
            "refinada de F17: AE denso fs1 idéntico al de referencia, entrenado con train v1.1 "
            "MÁS normalidad de autovía que sí cruza fronteras de cuantización del LTFT."
        ),
        "extra_normal_sessions": ctl_meta,
        "n_train_windows": int(x_ctl.shape[0]),
        "threshold_value": round(float(thr_ctl), 6),
        "test": r_ctl,
        "fpr_by_profile_test": fpr_by_profile(r_ctl),
        "reference_static_ae_fpr_by_profile": results["arms"]["static_ae_fs1_s"][
            "fpr_by_profile_test"
        ],
    }
    print(
        f"  control: FPR={r_ctl['point']['fp_rate_normal']:.3f} "
        f"perfil={fpr_by_profile(r_ctl)} "
        f"(ref {results['arms']['static_ae_fs1_s']['fpr_by_profile_test']})",
        flush=True,
    )

    # --------------------------------------- fase 5: ablation fs1-sequence (secundaria)
    print("fase 5: ablation fs1-sequence…", flush=True)
    try:
        from mecanico_contracts.features import feature_vector

        def fs1_seq(session_dir: Path) -> SequenceDataset:
            """Secuencia de 4 sub-ventanas de 15 s × 42 features fs1 (representación previa)."""
            base = build_sequences(session_dir, CANON_STEPS, CANON_STRIDE)
            sub = 15
            xs = np.empty((base.x.shape[0], CANON_STEPS // sub, 42))
            for i in range(base.x.shape[0]):
                for b in range(CANON_STEPS // sub):
                    blk = base.x[i, b * sub : (b + 1) * sub, :]
                    xs[i, b] = feature_vector(
                        {pid: blk[:, j].tolist() for j, pid in enumerate(MATRIX_PIDS)}
                    )
            out = SequenceDataset(
                x=xs,
                mask=np.ones_like(xs, dtype=bool),
                y=base.y,
                session_ids=base.session_ids,
                categories=base.categories,
                starts_s=base.starts_s,
                faults=base.faults,
                fault_intervals=base.fault_intervals,
                sample_rate_hz=1.0 / sub,
                steps=CANON_STEPS // sub,
            )
            return out

        fs1_tr, fs1_te = fs1_seq(v11_root / "train"), fs1_seq(args.sessions / "test")
        det_f, thr_f, _ = fit_recurrent(
            "gru", args.seed, fs1_tr, args.fpr, hidden=32, latent=8, epochs=60
        )
        rf = evaluate_seq(det_f.scores(fs1_te.x, fs1_te.mask), thr_f, fs1_te, headers)
        results["fs1_sequence_ablation"] = {
            "note": "GRU-AE sobre secuencia de 4 sub-ventanas de 15 s × 42 features fs1",
            "shape": list(fs1_tr.x.shape[1:]),
            "threshold_value": round(thr_f, 6),
            "test": rf,
            "fpr_by_profile_test": fpr_by_profile(rf),
        }
        print(
            f"  fs1-seq: F1={rf['point']['f1']:.3f} FPR={rf['point']['fp_rate_normal']:.3f}",
            flush=True,
        )
    except Exception as exc:
        results["fs1_sequence_ablation"] = {"error": f"{type(exc).__name__}: {exc}"}

    # ------------------------------------------------------------ fase 6: embeddings D2
    print("fase 6: embeddings…", flush=True)
    labels = np.array(
        [f if (y == 1 and f) else "normal" for f, y in zip(te.faults, te.y, strict=True)]
    )
    for name in ("lstm_ae", "gru_ae"):
        det, _t = models[name]
        z = det.embed(te.x, te.mask)
        emb: dict = {"latent_dim": int(z.shape[1])}
        anom = labels != "normal"
        emb["silhouette_normal_vs_anomaly"] = round(float(silhouette_score(z, anom)), 4)
        if anom.sum() > 2 and len(set(labels[anom])) > 1:
            emb["silhouette_between_faults"] = round(
                float(silhouette_score(z[anom], labels[anom])), 4
            )
            # consistencia de vecindario: ¿el vecino más cercano comparte tipo de fallo?
            za = z[anom]
            la = labels[anom]
            d = ((za[:, None, :] - za[None, :, :]) ** 2).sum(-1)
            np.fill_diagonal(d, np.inf)
            nn = d.argmin(axis=1)
            emb["neighbour_same_fault_rate"] = round(float((la[nn] == la).mean()), 4)
        pca = PCA(n_components=min(4, z.shape[1]), random_state=0).fit(z)
        emb["pca_var_explained_2c"] = round(float(pca.explained_variance_ratio_[:2].sum()), 4)
        # estabilidad del espacio entre seeds (silhouette de cada réplica)
        sils = []
        for det_s in seed_models.get(name, []):
            zs = det_s.embed(te.x, te.mask)
            if anom.sum() > 2 and len(set(labels[anom])) > 1:
                sils.append(float(silhouette_score(zs[anom], labels[anom])))
        if sils:
            emb["silhouette_between_faults_by_seed"] = [round(v, 4) for v in sils]
        results["embeddings"][name] = emb
    results["embeddings"]["static_reference_f17"] = {
        "silhouette_between_faults_ae_m_fs1": 0.2022,
        "source": "EXP-ANOM-007/008 (referencia estática, no recalculada)",
    }

    # ---------------------------------------- fase 7: análisis de cuantización del LTFT
    print("fase 7: análisis de cuantización…", flush=True)
    crossings = {
        sid: ltft_crossing_step(args.sessions / "test", sid)
        for sid in sorted(set(te.session_ids))
        if headers.get(sid) and headers[sid].fault is None
    }
    scores_by_arm = {
        "lstm_ae": models["lstm_ae"][0].scores(te.x, te.mask),
        "gru_ae": models["gru_ae"][0].scores(te.x, te.mask),
    }
    thresholds = {k: models[k][1] for k in scores_by_arm}
    # los brazos estáticos se evalúan sobre las MISMAS posiciones (ventanas fs1 = mismas)
    for tag in ("static_ae_fs1_s", "lof_frozen"):
        det_or_lof = models[tag][0] if tag in models else lof
        thr_t = models[tag][1] if tag in models else float(thr_lof)
        scores_by_arm[tag] = det_or_lof.scores(st_test.x)
        thresholds[tag] = thr_t
    scores_by_arm["control_arm"] = det_ctl.scores(st_test.x)
    thresholds["control_arm"] = float(thr_ctl)
    seq_view = te
    static_view = v_test
    q_seq = quantization_analysis(
        {k: v for k, v in scores_by_arm.items() if k in ("lstm_ae", "gru_ae")},
        seq_view,
        thresholds,
        crossings,
    )
    q_static = quantization_analysis(
        {k: v for k, v in scores_by_arm.items() if k not in ("lstm_ae", "gru_ae")},
        static_view,
        thresholds,
        crossings,
    )
    results["quantization_analysis"] = {"sequential": q_seq, "static": q_static}

    # --------------------------------------------------------------- fase 8: XAI temporal
    if not args.skip_xai:
        print("fase 8: XAI feature×time…", flush=True)
        results["xai"] = xai_phase(
            {k: models[k] for k in ("lstm_ae", "gru_ae")},
            seed_models,
            {k: tr for k in ("lstm_ae", "gru_ae")},
            te,
            args.seed,
        )

    results["total_runtime_s"] = round(time.perf_counter() - t_start, 1)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print(f"\nresultados → {RESULTS_JSON.name} ({results['total_runtime_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
