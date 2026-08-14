"""Auditoría E9 (AUDIT-DATA-001, F19) — detectabilidad y validez del banco sintético.

**No entrena modelos ni modifica el generador.** Responde una pregunta previa a cualquier
arquitectura: ¿las anomalías sintéticas son distinguibles del comportamiento normal
generado? El protocolo, las clases y los umbrales están congelados en
`configs/audit-data-001.yaml` (commit anterior a esta ejecución).

Fases: 1 formalización de la cuantización J1979 por PID · 2 contrafactuales pareados con
brazo SHAM (separa desincronización del RNG del efecto real de la inyección) · 3
distancias por señal y multivariables en los tres niveles (tick, ventana fs1,
multivariable) · 4 auditoría temporal de las lentas · 5 severidad LOW/MID/HIGH · 6
cobertura de normalidad y matriz TRAIN/VAL/TEST · 7 integridad del ground truth y traza
del pipeline · 8 clasificación final.

Instrumento declarado (F19 §2): el fallo comparte el RNG del motor
(`FaultRuntime(rng=engine.rng)`), así que el gemelo se desincroniza tras `fault_start`.
El brazo SHAM ejecuta el MISMO ``apply`` del catálogo y descarta sus modificaciones, de
modo que consume idénticas extracciones aleatorias sin alterar valores. Vive aquí, en la
auditoría: el catálogo del laboratorio no se toca.

Uso: python experiments/e9_anomaly_audit.py --sessions data/sessions
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from sklearn.decomposition import PCA

from ai_models.audit.detectability import (
    auc,
    classify_detectability,
    cohens_d,
    correlation_shift,
    coverage_bucket,
    coverage_gap,
    mahalanobis_scores,
    nearest_neighbour_ratio,
    overlap_coefficient,
    quantization_absorption,
    signal_to_normal_ratio,
    standardized_shift,
)
from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import CANONICAL_PIDS, FEATURE_NAMES, feature_vector
from mecanico_contracts.session_io import read_session_header, read_session_series
from obd_lab.emulator.encoding import quantize
from obd_lab.generate import generate_ticks
from obd_lab.injection.faults import CATALOG, FaultDef
from obd_lab.scenarios.loader import load_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_JSON = Path(__file__).parent / "e9_audit_results.json"
SEVERITY_SUITE = REPO_ROOT / "obd-lab" / "scenarios" / "suite_f14_severity.yaml"
SUITE_V1 = REPO_ROOT / "obd-lab" / "scenarios" / "suite_v1.yaml"

WINDOW, STRIDE = 60, 30
#: Semilla exploratoria dedicada a la auditoría (bloque 426-599; 510-519 sin usar).
AUDIT_SEEDS = (510, 511, 512)
#: Pares de señales cuya RELACIÓN es la firma de las anomalías relacionales.
RELATIONAL_PAIRS = (
    ("RPM", "MAF"),
    ("ENGINE_LOAD", "MAF"),
    ("ENGINE_LOAD", "COOLANT_TEMP"),
    ("SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1"),
    ("THROTTLE_POS", "MAF"),
)


# --------------------------------------------------- fase 1: cuantización J1979
def quantization_steps() -> dict[str, dict[str, float]]:
    """Paso efectivo de cuantización por PID, medido sobre la codificación real."""
    probes = {
        "RPM": 2000.0,
        "SPEED": 60.0,
        "ENGINE_LOAD": 40.0,
        "COOLANT_TEMP": 87.0,
        "INTAKE_TEMP": 30.0,
        "MAF": 20.0,
        "THROTTLE_POS": 35.0,
        "SHORT_FUEL_TRIM_1": 0.0,
        "LONG_FUEL_TRIM_1": 0.0,
        "O2_B1S1": 0.45,
        "TIMING_ADVANCE": 12.0,
        "INTAKE_PRESSURE": 40.0,
    }
    out: dict[str, dict[str, float]] = {}
    for pid, base in probes.items():
        q0 = quantize(pid, base)
        step = None
        delta = 1e-6
        for _ in range(80):  # búsqueda del menor incremento que cambia el valor codificado
            delta *= 1.5
            if abs(quantize(pid, base + delta) - q0) > 1e-12:
                step = abs(quantize(pid, base + delta) - q0)
                break
        out[pid] = {
            "probe_value": base,
            "effective_step": round(float(step if step else 0.0), 6),
            "encoded_at_probe": round(float(q0), 6),
        }
    return out


# ------------------------------------------- fase 2: contrafactuales con SHAM
def _sham_def(real: FaultDef) -> FaultDef:
    """Fallo SHAM: consume las MISMAS extracciones aleatorias y descarta el efecto."""

    def _apply(v: dict[str, float], t: float, p: dict[str, float], rt: Any) -> dict[str, float]:
        real.apply(dict(v), t, p, rt)  # consume RNG y avanza rt.memory; se descarta
        return v

    return FaultDef(
        name=f"sham_{real.name}",
        category=real.category,
        description="control de auditoría: consume el mismo RNG sin alterar valores",
        expected_signature="ninguna (control)",
        apply=_apply,
        default_params=dict(real.default_params),
    )


def _spec(fault: str | None, seed: int, profile: str = "urban", duration: float = 900.0):
    return ScenarioSpec(
        scenario_id=f"aud-{fault or 'normal'}",
        description="auditoría F19 (contrafactual pareado)",
        category="normal" if fault is None else CATALOG[fault.replace("sham_", "")].category,
        driving_profile=profile,
        duration_s=duration,
        seed=seed,
        fault=fault,
        fault_start_s=300.0 if fault else None,
        fault_end_s=duration if fault else None,
    )


def _series(ticks: list[dict[str, float]]) -> dict[str, np.ndarray]:
    return {pid: np.array([t[pid] for t in ticks], dtype=float) for pid in CANONICAL_PIDS}


def _windows(ticks: list[dict[str, float]], t0: float, rate: float = 1.0) -> np.ndarray:
    """Vectores fs1 de las ventanas que caen ENTERAMENTE dentro del intervalo del fallo."""
    n = len(ticks)
    rows = []
    for start in range(0, n - WINDOW + 1, STRIDE):
        if start / rate < t0:
            continue
        block = {
            pid: [ticks[i][pid] for i in range(start, start + WINDOW)] for pid in CANONICAL_PIDS
        }
        rows.append(feature_vector(block))
    return np.asarray(rows, dtype=float)


def paired_counterfactual(fault: str, seeds: tuple[int, ...]) -> dict[str, Any]:
    """Genera normal / SHAM / anómalo con el MISMO seed y descompone el efecto."""
    sham_name = f"sham_{fault}"
    CATALOG[sham_name] = _sham_def(CATALOG[fault])
    try:
        per_seed = []
        for seed in seeds:
            normal = generate_ticks(_spec(None, seed))
            sham = generate_ticks(_spec(sham_name, seed))
            anom = generate_ticks(_spec(fault, seed))
            per_seed.append((normal, sham, anom))
    finally:
        CATALOG.pop(sham_name, None)

    t_start = 300.0
    idx0 = int(t_start)
    pre_identical = all(
        np.array_equal(_series(n)[pid][:idx0], _series(a)[pid][:idx0])
        for n, _s, a in per_seed
        for pid in CANONICAL_PIDS
    )
    # efecto por señal, en tres comparaciones: total, desincronización y real
    sig: dict[str, Any] = {}
    for pid in CANONICAL_PIDS:
        norm = np.concatenate([_series(n)[pid][idx0:] for n, _s, _a in per_seed])
        shm = np.concatenate([_series(s)[pid][idx0:] for _n, s, _a in per_seed])
        anm = np.concatenate([_series(a)[pid][idx0:] for _n, _s, a in per_seed])
        sig[pid] = {
            "auc_total_normal_vs_anom": round(auc(norm, anm), 4),
            "auc_desync_normal_vs_sham": round(auc(norm, shm), 4),
            "auc_injection_sham_vs_anom": round(auc(shm, anm), 4),
            "cohens_d_injection": round(cohens_d(shm, anm), 4),
            "standardized_shift_injection": round(standardized_shift(shm, anm), 4),
            "overlap_injection": round(overlap_coefficient(shm, anm), 4),
            "mean_delta_injection": round(float(anm.mean() - shm.mean()), 5),
            "normal_std": round(float(norm.std(ddof=1)), 5),
            "signal_to_normal_ratio": round(
                signal_to_normal_ratio(float(anm.mean() - shm.mean()), float(norm.std(ddof=1))), 4
            ),
        }
    # nivel ventana (fs1) — el que ven los detectores
    w_norm = np.vstack([_windows(n, t_start) for n, _s, _a in per_seed])
    w_sham = np.vstack([_windows(s, t_start) for _n, s, _a in per_seed])
    w_anom = np.vstack([_windows(a, t_start) for _n, _s, a in per_seed])
    feat_auc = {
        FEATURE_NAMES[j]: round(auc(w_sham[:, j], w_anom[:, j]), 4) for j in range(w_anom.shape[1])
    }
    best_feat = max(feat_auc, key=lambda k: abs(feat_auc[k] - 0.5))
    j_best = list(FEATURE_NAMES).index(best_feat)
    # multivariable (sin usar los modelos principales)
    maha_n = mahalanobis_scores(w_norm, w_sham)
    maha_a = mahalanobis_scores(w_norm, w_anom)
    pca = PCA(n_components=min(4, w_norm.shape[1]), random_state=0).fit(w_norm)
    pca_shift = float(
        np.linalg.norm(pca.transform(w_anom).mean(axis=0) - pca.transform(w_sham).mean(axis=0))
    )
    rel = {}
    for a_pid, b_pid in RELATIONAL_PAIRS:
        rel[f"{a_pid}~{b_pid}"] = correlation_shift(
            np.concatenate([_series(n)[a_pid][idx0:] for n, _s, _a in per_seed]),
            np.concatenate([_series(n)[b_pid][idx0:] for n, _s, _a in per_seed]),
            np.concatenate([_series(a)[a_pid][idx0:] for _n, _s, a in per_seed]),
            np.concatenate([_series(a)[b_pid][idx0:] for _n, _s, a in per_seed]),
        )
    return {
        "seeds": list(seeds),
        "pre_fault_windows_identical": bool(pre_identical),
        "per_signal": sig,
        "window_level": {
            "n_windows_per_arm": int(w_anom.shape[0]),
            "best_feature": best_feat,
            "best_feature_auc_injection": feat_auc[best_feat],
            "best_feature_cohens_d": round(cohens_d(w_sham[:, j_best], w_anom[:, j_best]), 4),
            "top5_features_by_auc": sorted(feat_auc.items(), key=lambda kv: -abs(kv[1] - 0.5))[:5],
        },
        "multivariate": {
            "auc_mahalanobis_sham_vs_anom": round(auc(maha_n, maha_a), 4),
            "mahalanobis_mean_sham": round(float(maha_n.mean()), 4),
            "mahalanobis_mean_anom": round(float(maha_a.mean()), 4),
            "pca_mean_shift": round(pca_shift, 4),
            "nn_ratio_anom": round(nearest_neighbour_ratio(w_norm, w_anom), 4),
            "nn_ratio_sham": round(nearest_neighbour_ratio(w_norm, w_sham), 4),
        },
        "relational": rel,
    }


# ------------- fase 3b: separabilidad frente a la POBLACIÓN normal (lo que ve el detector)
def population_separability(fault: str, seeds: tuple[int, ...], train_dir: Path) -> dict[str, Any]:
    """Separabilidad de las ventanas anómalas frente a la POBLACIÓN de normales de train.

    La comparación pareada mantiene escenario y semilla constantes; el detector, en
    cambio, debe separar la ventana anómala del conjunto de TODAS las ventanas normales
    (perfiles, regímenes y sesiones distintos). Esta fase mide esa segunda separabilidad,
    que es la que gobierna el recall real, SIN usar ningún modelo entrenado.
    """
    pop = []
    for path in sorted(train_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        if header.scenario and header.scenario.fault is not None:
            continue
        n = min(len(v) for v in series.values())
        for start in range(0, n - WINDOW + 1, STRIDE):
            block = {pid: list(series[pid][start : start + WINDOW]) for pid in CANONICAL_PIDS}
            pop.append(feature_vector(block))
    w_norm = np.asarray(pop, dtype=float)
    sham_name = f"sham_{fault}"
    CATALOG[sham_name] = _sham_def(CATALOG[fault])
    try:
        w_sham = np.vstack([_windows(generate_ticks(_spec(sham_name, s)), 300.0) for s in seeds])
    finally:
        CATALOG.pop(sham_name, None)
    w_anom = np.vstack([_windows(generate_ticks(_spec(fault, s)), 300.0) for s in seeds])
    feat_auc = {FEATURE_NAMES[j]: auc(w_norm[:, j], w_anom[:, j]) for j in range(w_anom.shape[1])}
    feat_sham = {FEATURE_NAMES[j]: auc(w_norm[:, j], w_sham[:, j]) for j in range(w_sham.shape[1])}
    best = max(feat_auc, key=lambda k: abs(feat_auc[k] - 0.5))
    maha_n = mahalanobis_scores(w_norm, w_norm)
    maha_a = mahalanobis_scores(w_norm, w_anom)
    maha_s = mahalanobis_scores(w_norm, w_sham)
    auc_anom = max(auc(maha_n, maha_a), 1 - auc(maha_n, maha_a))
    auc_sham = max(auc(maha_n, maha_s), 1 - auc(maha_n, maha_s))
    return {
        "n_normal_windows_population": int(w_norm.shape[0]),
        "n_anomalous_windows": int(w_anom.shape[0]),
        "best_feature": best,
        "best_feature_auc": round(max(feat_auc[best], 1 - feat_auc[best]), 4),
        "best_feature_auc_sham_control": round(max(feat_sham[best], 1 - feat_sham[best]), 4),
        "auc_mahalanobis_population": round(auc_anom, 4),
        "auc_mahalanobis_sham_control": round(auc_sham, 4),
        "scenario_confound": bool(auc_sham >= 0.7),
        "injection_gain_over_sham": round(auc_anom - auc_sham, 4),
        "nn_ratio_vs_population": round(nearest_neighbour_ratio(w_norm, w_anom), 4),
        "nn_ratio_sham_control": round(nearest_neighbour_ratio(w_norm, w_sham), 4),
        "top5_features_by_auc": [
            (k, round(v, 4))
            for k, v in sorted(feat_auc.items(), key=lambda kv: -abs(kv[1] - 0.5))[:5]
        ],
    }


# ----------------------------------------------- fase 4: auditoría temporal lenta
def temporal_audit(fault: str, seeds: tuple[int, ...], steps: dict) -> dict[str, Any]:
    """¿La trayectoria inyectada supera la deriva normal de esa misma señal?"""
    sham_name = f"sham_{fault}"
    CATALOG[sham_name] = _sham_def(CATALOG[fault])
    try:
        pairs = [
            (generate_ticks(_spec(sham_name, s)), generate_ticks(_spec(fault, s))) for s in seeds
        ]
    finally:
        CATALOG.pop(sham_name, None)
    idx0 = 300
    out: dict[str, Any] = {}
    for pid in CANONICAL_PIDS:
        accum, slopes, norm_drifts = [], [], []
        for sham, anom in pairs:
            s_arr, a_arr = _series(sham)[pid][idx0:], _series(anom)[pid][idx0:]
            accum.append(float(a_arr[-60:].mean() - a_arr[:60].mean()))
            norm_drifts.append(float(s_arr[-60:].mean() - s_arr[:60].mean()))
            t = np.arange(a_arr.size, dtype=float)
            slopes.append(float(np.polyfit(t, a_arr - s_arr, 1)[0]))
        acc, ndrift = float(np.mean(accum)), float(np.mean(norm_drifts))
        step = steps[pid]["effective_step"] or 1e-9
        out[pid] = {
            "accumulated_change_anom": round(acc, 5),
            "accumulated_change_normal_drift": round(ndrift, 5),
            "injected_slope_per_s": round(float(np.mean(slopes)), 8),
            "duration_s": 600.0,
            "change_vs_normal_drift_ratio": round(abs(acc) / max(abs(ndrift), 1e-9), 3),
            "change_in_quanta": round(quantization_absorption(acc, step), 3),
        }
    return out


# ------------------------------------------------------- fase 5: severidad
def severity_audit(steps: dict) -> dict[str, Any]:
    """LOW / MID / HIGH por separado sobre la suite F14 (solo evaluación, sin modelos)."""
    suite = load_suite(SEVERITY_SUITE)["test"]
    out: dict[str, Any] = {}
    normals = [s for s in suite if s.fault is None]
    for spec in suite:
        if spec.fault is None:
            continue
        base = next((n for n in normals if n.driving_profile == spec.driving_profile), normals[0])
        sham_name = f"sham_{spec.fault}"
        CATALOG[sham_name] = _sham_def(CATALOG[spec.fault])
        try:
            sham_spec = spec.model_copy(update={"fault": sham_name})
            sham = generate_ticks(sham_spec)
            anom = generate_ticks(spec)
        finally:
            CATALOG.pop(sham_name, None)
        t0 = int(spec.fault_start_s or 0)
        w_s, w_a = _windows(sham, float(t0)), _windows(anom, float(t0))
        if w_s.size == 0 or w_a.size == 0:
            continue
        feat_auc = [auc(w_s[:, j], w_a[:, j]) for j in range(w_a.shape[1])]
        j = int(np.argmax([abs(v - 0.5) for v in feat_auc]))
        d = cohens_d(w_s[:, j], w_a[:, j])
        verdict = classify_detectability(auc_best=max(feat_auc[j], 1 - feat_auc[j]), d_best=d)
        out[spec.scenario_id] = {
            "fault": spec.fault,
            "params": spec.fault_params,
            "baseline_normal": base.scenario_id,
            "best_feature": FEATURE_NAMES[j],
            "auc_best": round(max(feat_auc[j], 1 - feat_auc[j]), 4),
            "cohens_d_best": round(d, 4) if np.isfinite(d) else "inf",
            "n_windows": int(w_a.shape[0]),
            "label": verdict.label,
        }
    return out


# --------------------------------------- fase 6: cobertura de normalidad
def _regime(v: dict[str, np.ndarray], i: int) -> str:
    sp, ld = v["SPEED"][i], v["ENGINE_LOAD"][i]
    if sp < 2.0:
        return "idle"
    if sp < 50.0:
        return "urban"
    if ld > 45.0:
        return "high_load_cruise"
    return "cruise"


def coverage_audit(session_dirs: dict[str, Path]) -> dict[str, Any]:
    """Inventario de comportamientos NORMALES por partición + matriz de cobertura."""
    behaviours = [
        "idle",
        "urban",
        "cruise",
        "high_load_cruise",
        "warmup_cold_ECT(<60C)",
        "stable_ECT(>=80C)",
        "LTFT_quantization_crossing",
        "LTFT_nonzero_level",
        "high_load(>60%)",
        "low_load(<15%)",
        "STFT_wide_swing(>6%)",
    ]
    counts: dict[str, dict[str, int]] = {b: {k: 0 for k in session_dirs} for b in behaviours}
    detail: dict[str, Any] = {}
    for split, d in session_dirs.items():
        sessions = 0
        for path in sorted(d.glob("*.jsonl")):
            header = read_session_header(path)
            if header.scenario and header.scenario.fault is not None:
                continue  # cobertura de NORMALIDAD
            sessions += 1
            _h, series = read_session_series(path)
            v = {pid: np.asarray(series[pid], float) for pid in CANONICAL_PIDS}
            n = min(len(x) for x in v.values())
            regimes = {_regime(v, i) for i in range(0, n, 5)}
            for r in ("idle", "urban", "cruise", "high_load_cruise"):
                if r in regimes:
                    counts[r][split] += 1
            if (v["COOLANT_TEMP"] < 60.0).any():
                counts["warmup_cold_ECT(<60C)"][split] += 1
            if (v["COOLANT_TEMP"] >= 80.0).any():
                counts["stable_ECT(>=80C)"][split] += 1
            if (np.diff(v["LONG_FUEL_TRIM_1"]) != 0).any():
                counts["LTFT_quantization_crossing"][split] += 1
            if (np.abs(v["LONG_FUEL_TRIM_1"]) > 1e-9).any():
                counts["LTFT_nonzero_level"][split] += 1
            if (v["ENGINE_LOAD"] > 60.0).any():
                counts["high_load(>60%)"][split] += 1
            if (v["ENGINE_LOAD"] < 15.0).any():
                counts["low_load(<15%)"][split] += 1
            if float(v["SHORT_FUEL_TRIM_1"].std()) > 6.0:
                counts["STFT_wide_swing(>6%)"][split] += 1
        detail[split] = {"n_normal_sessions": sessions}
    matrix = {
        b: {
            **{
                split: {"count": counts[b][split], "bucket": coverage_bucket(counts[b][split])}
                for split in session_dirs
            },
            **coverage_gap(counts[b].get("train", 0), counts[b].get("test", 0)),
        }
        for b in behaviours
    }
    gaps = [b for b, row in matrix.items() if row["coverage_gap"]]
    return {"sessions_per_split": detail, "matrix": matrix, "coverage_gaps": gaps}


# ------------------------------ fase 7: traza del pipeline e integridad del GT
def pipeline_trace(fault: str, seed: int) -> dict[str, Any]:
    """Sigue el efecto etapa por etapa: ¿dónde cambia o desaparece la inyección?

    Compara el brazo SHAM (mismo RNG, sin inyección) con el anómalo en cada eslabón:
    señal cruda pre-cuantización → post-J1979 → snapshot → matriz → ventana → features.
    """
    from ai_models.data.snapshot_matrix import iter_windows, matrix_from_snapshots
    from diagnostic_agent.telemetry.snapshots import build_from_ticks

    sham_name = f"sham_{fault}"
    CATALOG[sham_name] = _sham_def(CATALOG[fault])
    try:
        sham = generate_ticks(_spec(sham_name, seed))
        anom = generate_ticks(_spec(fault, seed))
    finally:
        CATALOG.pop(sham_name, None)
    gt_pids = sorted(
        {
            p
            for p in CANONICAL_PIDS
            if abs(float(np.mean(_series(anom)[p][300:]) - np.mean(_series(sham)[p][300:]))) > 1e-9
        }
    )
    stages: dict[str, Any] = {
        "declared_gt_pids_from_catalog": None,
        "observed_changed_pids": gt_pids,
    }
    # etapa post-J1979 (los ticks del generador YA salen cuantizados: es la salida real)
    diffs_tick = {
        p: round(float(np.mean(np.abs(_series(anom)[p][300:] - _series(sham)[p][300:]))), 6)
        for p in CANONICAL_PIDS
    }
    stages["mean_abs_diff_post_quantization"] = diffs_tick
    # etapa snapshot → matriz
    mats = {}
    for tag, ticks in (("sham", sham), ("anom", anom)):
        snaps, _l = build_from_ticks(ticks, session_id=f"trace-{tag}", vehicle_id="veh-sim")
        mats[tag] = matrix_from_snapshots(snaps)
    diffs_matrix = {
        p: round(
            float(np.mean(np.abs(mats["anom"].values[300:, j] - mats["sham"].values[300:, j]))),
            6,
        )
        for j, p in enumerate(mats["anom"].pids)
    }
    stages["mean_abs_diff_matrix"] = diffs_matrix
    stages["matrix_preserves_effect"] = bool(
        all(
            abs(diffs_matrix[p] - diffs_tick[p]) < 1e-9 for p in CANONICAL_PIDS if p in diffs_matrix
        )
    )
    # etapa ventana → features fs1
    w_s = np.asarray(
        [feature_vector(w) for st, w in iter_windows(mats["sham"], WINDOW, STRIDE) if st >= 300]
    )
    w_a = np.asarray(
        [feature_vector(w) for st, w in iter_windows(mats["anom"], WINDOW, STRIDE) if st >= 300]
    )
    feat_diff = {
        FEATURE_NAMES[j]: round(float(np.mean(np.abs(w_a[:, j] - w_s[:, j]))), 6)
        for j in range(w_a.shape[1])
    }
    stages["top_feature_abs_diff"] = dict(sorted(feat_diff.items(), key=lambda kv: -kv[1])[:8])
    stages["n_features_changed"] = int(sum(1 for v in feat_diff.values() if v > 1e-9))
    return stages


def ground_truth_integrity(fault: str, trace: dict[str, Any]) -> dict[str, Any]:
    """¿El GT declarado (features afectadas) coincide con lo que ocurre tras el pipeline?"""
    from ai_models.xai.ground_truth import FAULT_AFFECTED_PIDS

    declared = set(FAULT_AFFECTED_PIDS[fault])
    observed = {p for p, v in trace["mean_abs_diff_post_quantization"].items() if v > 1e-9}
    return {
        "declared_affected_pids": sorted(declared),
        "observed_affected_pids": sorted(observed),
        "declared_not_observed": sorted(declared - observed),
        "observed_not_declared": sorted(observed - declared),
        "ground_truth_consistent": bool(declared == observed),
    }


# ------------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    args = parser.parse_args()
    t0 = time.perf_counter()
    results: dict[str, Any] = {
        "audit_id": "AUDIT-DATA-001",
        "validity_note": (
            "EXPLORATORIO; auditoría del banco sintético (obd-lab). Los hallazgos sobre "
            "realismo (¿existe el patrón de cuantización fuera del emulador?) requieren HCRL."
        ),
        "protocol": "configs/audit-data-001.yaml (congelado antes de medir)",
        "no_models_trained": True,
        "generator_unmodified": True,
    }

    print("fase 1: cuantización J1979…", flush=True)
    steps = quantization_steps()
    results["quantization_steps"] = steps

    print("fase 2-3: contrafactuales pareados con brazo SHAM…", flush=True)
    catalogue: dict[str, Any] = {}
    for fault in sorted(CATALOG):
        cf = paired_counterfactual(fault, AUDIT_SEEDS)
        catalogue[fault] = {"counterfactual": cf}
        print(
            f"  {fault:22s} pre-idéntico={cf['pre_fault_windows_identical']} "
            f"AUC_ventana={cf['window_level']['best_feature_auc_injection']} "
            f"({cf['window_level']['best_feature']}) "
            f"maha={cf['multivariate']['auc_mahalanobis_sham_vs_anom']}",
            flush=True,
        )

    print("fase 3b: separabilidad frente a la población normal de train…", flush=True)
    for fault in sorted(CATALOG):
        ps = population_separability(
            fault, AUDIT_SEEDS, REPO_ROOT / "data" / "sessions_v11" / "train"
        )
        catalogue[fault]["population"] = ps
        print(
            f"  {fault:22s} maha_anom={ps['auc_mahalanobis_population']} "
            f"maha_sham={ps['auc_mahalanobis_sham_control']} "
            f"ganancia={ps['injection_gain_over_sham']} confound={ps['scenario_confound']}",
            flush=True,
        )

    print("fase 4: auditoría temporal de las lentas…", flush=True)
    for fault in ("joint_slow_drift", "load_coolant_decouple", "maf_drift", "vacuum_leak"):
        catalogue[fault]["temporal"] = temporal_audit(fault, AUDIT_SEEDS, steps)

    print("fase 5: severidad…", flush=True)
    results["severity"] = severity_audit(steps)

    print("fase 6: cobertura de normalidad…", flush=True)
    results["coverage"] = coverage_audit(
        {
            "train": args.sessions / "train",
            "validation": args.sessions / "validation",
            "test": args.sessions / "test",
            "train_v11": REPO_ROOT / "data" / "sessions_v11" / "train",
        }
    )

    print("fase 7: traza del pipeline e integridad del ground truth…", flush=True)
    for fault in sorted(CATALOG):
        tr = pipeline_trace(fault, AUDIT_SEEDS[0])
        catalogue[fault]["pipeline_trace"] = tr
        catalogue[fault]["ground_truth"] = ground_truth_integrity(fault, tr)

    print("fase 8: clasificación…", flush=True)
    for fault, data in catalogue.items():
        cf = data["counterfactual"]
        w = cf["window_level"]
        auc_w = max(w["best_feature_auc_injection"], 1 - w["best_feature_auc_injection"])
        auc_m = cf["multivariate"]["auc_mahalanobis_sham_vs_anom"]
        pop = data["population"]
        # si el brazo SHAM ya se separa de la población, esa separabilidad es del ESCENARIO,
        # no de la inyección: se usa entonces la ganancia atribuible a la inyección
        auc_pop = (
            pop["auc_mahalanobis_population"]
            if not pop["scenario_confound"]
            else 0.5 + max(0.0, pop["injection_gain_over_sham"])
        )
        auc_best = min(max(auc_w, auc_m, 1 - auc_m), auc_pop)  # manda la más exigente
        d_best = w["best_feature_cohens_d"]
        # ¿la inyección queda por debajo de un cuanto en TODAS las señales que toca?
        touched = [
            p
            for p, v in data["pipeline_trace"]["mean_abs_diff_post_quantization"].items()
            if v > 1e-9
        ]
        absorbed = len(touched) == 0
        gt_broken = not data["ground_truth"]["ground_truth_consistent"]
        verdict = classify_detectability(
            auc_best=auc_best,
            d_best=d_best if np.isfinite(d_best) else 10.0,
            absorbed_by_quantization=absorbed,
            ground_truth_broken=False,  # se reporta aparte: no invalida por sí solo
        )
        data["verdict"] = {
            "label": verdict.label,
            "auc_best": round(auc_best, 4),
            "cohens_d_best": d_best,
            "rationale": verdict.rationale,
            "ground_truth_mismatch": gt_broken,
            "n_pids_actually_changed": len(touched),
            "auc_paired": round(max(auc_w, auc_m, 1 - auc_m), 4),
            "auc_population": round(auc_pop, 4),
            "paired_minus_population": round(max(auc_w, auc_m, 1 - auc_m) - auc_pop, 4),
        }
        print(f"  {fault:22s} → {verdict.label} (AUC {auc_best:.3f})", flush=True)
    results["catalogue"] = catalogue
    results["total_runtime_s"] = round(time.perf_counter() - t0, 1)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )
    print(f"\nresultados → {RESULTS_JSON.name} ({results['total_runtime_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
