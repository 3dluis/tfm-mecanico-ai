"""Experimento E11 (EXP-ANOM-010, EXPLORATORIO) — réplica del efecto de cobertura (F21).

Pregunta: ¿el efecto que midió el brazo control de EXP-ANOM-009 (FPR 0.129 → 0.0216,
F1 0.727) sobrevive cuando la normalidad añadida se define **a priori desde el mecanismo
del generador** (F20) en lugar de diagnosticando los falsos positivos sobre el test?

Brazos — el ÚNICO cambio entre los dos brazos AE son los datos de entrenamiento:
  lof_frozen (arms-freeze-v1, control de integridad) · ae_v11 (train v1.1, línea base) ·
  ae_v2 (train v1.1 + expansión v2, candidato) · lof_v2 (informativo).

Fases: 0 verificación del freeze del banco + datasets · 1 control de integridad del
pipeline (P4: el LOF congelado debe reproducir F18 exactamente) · 2 brazos AE multi-seed
(42/43/44) · 3 LOF v2 informativo · 4 contraste de las predicciones P1-P3 y del criterio
D1 declarados en `configs/exp-anom-010.yaml` · 5 embeddings (D2) · 6 resumen.

Umbral SIEMPRE por cuantil (1-FPR) sobre el train del propio brazo (ADR-0011); el test
histórico jamás interviene en el ajuste. Sin seeds reservadas. El banco está congelado por
hash: el runner aborta si los datos no coinciden con el freeze.

**F22 — réplica sobre el banco v3 (EXP-ANOM-010-R2).** El runner se parametriza por banco
(``--benchmark v2|v3``) en lugar de duplicarse: un fork sería indistinguible de un cambio
silencioso de protocolo, mientras que aquí «no cambia nada más» se comprueba por diff. Con
``v3`` el brazo candidato pasa a ser ``ae_v3`` y se añade una verificación previa: el train
debe cumplir el criterio de cobertura EFECTIVA declarado a priori, medido en el espacio de
features con el mismo instrumento que construyó el banco. Esa comprobación es la que faltó
en F20/F21, donde un banco congelado por hash no contenía la cobertura que declaraba.

Uso:
    python experiments/e11_replica.py --sessions data/sessions [--benchmark v2|v3]
                                      [--seed 42] [--fpr 0.01]
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

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
from sklearn.preprocessing import StandardScaler

from ai_models.anomaly.autoencoder import AutoencoderDetector
from ai_models.anomaly.baselines import make_baselines
from ai_models.audit.coverage import (
    LTFT_FEATURE,
    check_coverage_criterion,
    ltft_level_coverage,
)
from ai_models.audit.detectability import nearest_neighbour_ratio
from ai_models.data.dataset import WindowDataset
from ai_models.evaluation.protocol import threshold_from_normal
from ai_models.tracking import git_sha, peak_rss_mb, record_run
from mecanico_contracts.features import FEATURE_NAMES
from obd_lab.emulator.encoding import quantize

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from freeze_benchmark import verify  # noqa: E402

RUNS_FILE = Path(__file__).parent / "runs.jsonl"
V11_ROOT = REPO_ROOT / "data" / "sessions_v11"
V2_TRAIN = REPO_ROOT / "data" / "sessions_v2" / "train"

#: Bancos que puede replicar este runner. El código es el MISMO para los dos: lo único que
#: cambia son los datos de entrenamiento del brazo candidato, que es exactamente lo que la
#: réplica exige. Mantener `v2` como valor por defecto preserva la reproducibilidad de los
#: resultados publicados en F21 (`e11_results.json`) sin duplicar el runner —un fork sería
#: indistinguible de un cambio silencioso de protocolo.
BENCHMARKS: dict[str, dict[str, Any]] = {
    "v2": {
        "experiment": "EXP-ANOM-010",
        "config": "ai-models/configs/exp-anom-010.yaml (congelada antes de ejecutar)",
        "freeze": REPO_ROOT / "ai-models" / "configs" / "benchmark-v2-freeze.json",
        "expansion_dir": V2_TRAIN,
        "results": Path(__file__).parent / "e11_results.json",
        "train_label": "v1.1 + expansión v2 (34)",
        "coverage_criterion": None,  # v2 no declaró criterio de cobertura efectiva
    },
    "v3": {
        "experiment": "EXP-ANOM-010-R2",
        "config": "ai-models/configs/exp-anom-010-r2.yaml (congelada antes de ejecutar)",
        "freeze": REPO_ROOT / "ai-models" / "configs" / "benchmark-v3-freeze.json",
        "expansion_dir": REPO_ROOT / "data" / "sessions_v3" / "train",
        "results": Path(__file__).parent / "e12_results.json",
        "train_label": "v1.1 + expansión v3 (45)",
        "coverage_criterion": {"positive": 0.03, "negative": 0.03},
    },
}
#: Normalidad del brazo control de F18 (elegida DESPUÉS de diagnosticar test): aquí solo
#: se usa como referencia de medición en el informe de causa, nunca para entrenar.
CONTROL_DIR = REPO_ROOT / "data" / "sessions_qcontrol" / "train"

SEEDS = (42, 43, 44)

#: Referencias de F18 sobre el MISMO test histórico (informe EXP-ANOM-009).
F18_REFERENCE = {
    "lof_frozen": {"f1": 0.6448, "fp_rate_normal": 0.0345},
    "ae_v11": {"f1": 0.7019, "fp_rate_normal": 0.1293},
    "control_arm": {"f1": 0.7273, "fp_rate_normal": 0.0216, "highway_fpr": 0.0847},
}
#: Anomalías lentas/relacionales de la predicción negativa P3.
SLOW_FAULTS = ("joint_slow_drift", "load_coolant_decouple")


def _median(values: list[float]) -> float:
    return round(float(statistics.median(values)), 4)


def fit_ae(x_train: np.ndarray, seed: int, fpr: float) -> tuple[AutoencoderDetector, float]:
    """AE denso fs1 idéntico al de F17/F18 (AE-S, scaler standard). Único cambio: los datos."""
    det = AutoencoderDetector(seed=seed, scaler_kind="standard")
    det.fit(x_train)
    thr = float(threshold_from_normal(det.scores(x_train), target_fpr=fpr))
    return det, thr


def arm_summary(res: dict[str, Any]) -> dict[str, Any]:
    """Subconjunto comparable de métricas de un brazo (lo que entra en las decisiones)."""
    return {
        "point": res["point"],
        "event": res["event"],
        "pr_auc": res.get("pr_auc"),
        "roc_auc": res.get("roc_auc"),
        "per_fault_recall": res["per_fault_recall"],
        "fpr_by_profile": fpr_by_profile(res),
        "fpr_by_normal_scenario": res["fpr_by_normal_scenario"],
        "temporal": res["temporal"],
    }


def embeddings_report(det: AutoencoderDetector, test: WindowDataset) -> dict[str, Any]:
    """D2: ¿el espacio latente separa normal/anomalía? (silhouette + varianza PCA)."""
    z = det.embed(test.x)
    if len(set(test.y.tolist())) < 2:  # pragma: no cover - test siempre tiene ambas clases
        return {"note": "test sin ambas clases"}
    pca = PCA(n_components=2, random_state=0).fit(z)
    return {
        "latent_dim": int(z.shape[1]),
        "silhouette_normal_vs_anomaly": round(float(silhouette_score(z, test.y)), 4),
        "pca_explained_variance_ratio": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "reference_static_f16": 0.202,
    }


def cause_report(
    det: AutoencoderDetector,
    threshold: float,
    test: WindowDataset,
    headers: dict[str, Any],
    train_v11: np.ndarray,
    expansion: np.ndarray,
    control_f18: np.ndarray | None,
) -> dict[str, Any]:
    """Diagnóstico OBLIGATORIO cuando D1 ≠ PROMOTE_CANDIDATE (regla de parada b).

    Mide, sin tocar el modelo ni los datos: (1) qué features dominan el error de
    reconstrucción en los falsos positivos del brazo candidato (con SU propio umbral),
    (2) a qué distancia caen esos FP de cada conjunto normal —en unidades estandarizadas
    comunes, para que la comparación entre conjuntos sea legítima— y (3) qué nivel de LTFT
    cubre cada conjunto **en el espacio de features que el modelo consume**, separando
    nivel positivo y negativo. Esta última medida es la que distingue *cobertura declarada
    a nivel de sesión* de *cobertura efectiva a nivel de ventana*.
    """
    normal_idx = np.array([headers[s].fault is None for s in test.session_ids]) & (test.y == 0)
    fp_idx = normal_idx & (det.scores(test.x) > threshold)
    fp_x = test.x[fp_idx]
    report: dict[str, Any] = {
        "threshold_used": round(float(threshold), 6),
        "threshold_origin": "cuantil (1-FPR) sobre el train del propio brazo candidato (v2)",
        "false_positive_windows": int(fp_idx.sum()),
        "normal_test_windows": int(normal_idx.sum()),
    }
    if fp_idx.sum() == 0:  # pragma: no cover - no ocurre con D1 = REJECT
        return report
    err = det.per_feature_error(fp_x).mean(axis=0)
    order = np.argsort(err)[::-1][:8]
    report["dominant_error_features"] = [
        {"feature": FEATURE_NAMES[i], "mean_squared_error": round(float(err[i]), 4)} for i in order
    ]

    # distancias en un espacio común: estandarizado con el train del brazo candidato
    train_v2 = np.vstack([train_v11, expansion])
    scaler = StandardScaler().fit(train_v2)
    sets: dict[str, np.ndarray] = {"train_v11": train_v11, "expansion_v2": expansion}
    if control_f18 is not None:
        sets["control_f18"] = control_f18
    sets["train_v2"] = train_v2
    fp_z = scaler.transform(fp_x)
    report["distance_to_normal_sets"] = {
        name: {
            "median_nn_distance_std_units": round(
                float(
                    np.median(
                        np.linalg.norm(
                            fp_z[:, None, :] - scaler.transform(arr)[None, :, :], axis=-1
                        ).min(axis=1)
                    )
                ),
                3,
            ),
            "nn_ratio_intra_set": round(
                float(nearest_neighbour_ratio(scaler.transform(arr), fp_z)), 3
            ),
        }
        for name, arr in sets.items()
    }
    report["distance_note"] = (
        "distancia euclídea en unidades estandarizadas por el train del brazo candidato "
        "(comparable entre conjuntos); el ratio adicional normaliza por la dispersión "
        "interna de cada conjunto y NO es comparable entre conjuntos de tamaño distinto"
    )

    ltft = FEATURE_NAMES.index(LTFT_FEATURE)
    coverage_sets = dict(sets)
    coverage_sets["false_positives"] = fp_x
    #: instrumento ÚNICO (ai_models.audit.coverage), el mismo que construye y valida el
    #: banco v3: medir la misma magnitud con dos implementaciones fue la causa raíz del
    #: falso cierre de hueco de F20 (informe F21 §3).
    report["ltft_mean_coverage"] = {
        name: ltft_level_coverage(arr, ltft) for name, arr in coverage_sets.items()
    }
    report["ltft_note"] = (
        "0.390625 % = medio cuanto J1979 del LTFT. `positive_level_share` es la fracción de "
        "VENTANAS cuyo nivel medio de LTFT es un cuanto positivo sostenido — exactamente lo "
        "que el modelo ve. El contador de cobertura de F19/F20 es de SESIÓN y binario (¿algún "
        "tick cambia?, ¿algún tick es != 0?), no distingue signo, magnitud ni persistencia."
    )
    return report


def quantization_probe(
    seed: int = 572,
    n_walks: int = 4000,
    durations: tuple[int, ...] = (1800, 2400, 3600, 5400),
) -> dict[str, Any]:
    """Monte Carlo del MECANISMO del LTFT (no genera sesiones ni toca el banco).

    El LTFT del emulador es un paseo aleatorio simétrico ``gauss(0, 0.01)`` por tick
    (``obd_lab/signals.py``). La cuantización J1979 **no redondea**: codifica con
    ``int(v * 128/100)``, que trunca hacia cero (``obd_lab/emulator/encoding.py``), así que
    el valor emitido solo cambia de nivel cuando el paseo supera un cuanto COMPLETO
    (±0.78125 %), no medio cuanto. Esta sonda usa el cuantizador REAL del proyecto —no una
    reimplementación— para responder a lo que F20 no se preguntó: ¿con qué probabilidad
    una sesión de duración T produce un nivel **positivo sostenido**, que es lo que el
    modelo ve como ``LONG_FUEL_TRIM_1_mean`` de una ventana?

    Semilla 572 (bloque exploratorio 401-599, no gastada); reservadas intactas.
    """
    rng = np.random.default_rng(seed)
    quantum, window = 0.78125, 60
    quant = np.vectorize(lambda v: quantize("LONG_FUEL_TRIM_1", float(v)))
    out: dict[str, Any] = {}
    for duration in durations:
        walks = np.cumsum(rng.normal(0.0, 0.01, size=(n_walks, duration)), axis=1)
        quantized = quant(walks)
        usable = (duration // window) * window
        window_means = quantized[:, :usable].reshape(n_walks, -1, window).mean(axis=2)
        pos_windows = (window_means >= quantum / 2).mean(axis=1)
        neg_windows = (window_means <= -quantum / 2).mean(axis=1)
        p_pos = float((pos_windows > 0).mean())
        out[str(duration)] = {
            "p_any_positive_level_window": round(p_pos, 4),
            "p_any_negative_level_window": round(float((neg_windows > 0).mean()), 4),
            "median_positive_window_share_when_present": round(
                float(np.median(pos_windows[pos_windows > 0])) if p_pos > 0 else 0.0, 4
            ),
            "p_zero_positive_sessions_in_12": round(float((1.0 - p_pos) ** 12), 4),
        }
    out["note"] = (
        "simulación del mecanismo declarado en obd_lab/signals.py (paseo simétrico σ=0.01 "
        "%/tick, cuanto 0.78125 %); NO sustituye a medir las sesiones reales, sirve para "
        "dimensionar cuántas sesiones y de qué duración hacen falta"
    )
    return out


def h1_exploratory_status(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    d1: str,
    p4_holds: bool,
    coverage_ok: bool,
    seed_categories: set[str],
) -> dict[str, Any]:
    """Estado EXPLORATORIO de la línea H1, con la regla declarada a priori (F22).

    Traduce el resultado numérico a una de las cuatro etiquetas fijadas en
    ``exp-anom-010-r2.yaml`` §h1_exploratory_status. No sustituye al resultado
    confirmatorio de la hipótesis H1 del TFM, que exige el freeze del pre-registro y una
    serie posterior: son dos cosas distintas y el informe debe decirlo.
    """
    fpr_base = baseline["fp_rate_normal_median"]
    fpr_cand = candidate["fp_rate_normal_median"]
    delta = (fpr_base - fpr_cand) / fpr_base if fpr_base > 0 else 0.0
    stable = len(seed_categories) == 1

    if not p4_holds or not coverage_ok or not stable:
        status = "INCONCLUSIVE"
    elif d1 == "PROMOTE_CANDIDATE":
        status = "SUPPORTED"
    elif delta >= 0.50 and candidate["f1_median"] >= 0.65:
        status = "PARTIALLY_SUPPORTED"
    elif delta < 0.25:
        status = "NOT_SUPPORTED"
    else:
        status = "INCONCLUSIVE"

    return {
        "status": status,
        "relative_fpr_reduction": round(float(delta), 4),
        "inputs": {
            "fpr_median_baseline": fpr_base,
            "fpr_median_candidate": fpr_cand,
            "f1_median_candidate": candidate["f1_median"],
            "D1": d1,
            "P4_holds": p4_holds,
            "coverage_criterion_met": coverage_ok,
            "d1_category_stable_across_seeds": stable,
        },
        "scope": (
            "EXPLORATORIO y referido a la pregunta de F22 (¿cobertura efectiva o límite del "
            "detector?). NO es el resultado confirmatorio de la hipótesis H1 del TFM."
        ),
    }


def _d1_category(fpr: float, f1: float, all_seeds_ok: bool) -> str:
    """Criterio D1 declarado en la config congelada (idéntico en F21 y F22)."""
    if fpr <= 0.03 and all_seeds_ok and f1 >= 0.70 and f1 > 0.6448:
        return "PROMOTE_CANDIDATE"
    if fpr > 0.05 or f1 < 0.6448:
        return "REJECT"
    return "PARTIAL" if (fpr <= 0.05 and f1 >= 0.65) else "REJECT"


def check_predictions(results: dict[str, Any], candidate: str) -> dict[str, Any]:
    """Contrasta P1-P4 y D1 EXACTAMENTE como se declararon en la config congelada."""
    ae2 = results["arms"][candidate]["aggregate"]
    ae11 = results["arms"]["ae_v11"]["aggregate"]
    lof = results["arms"]["lof_frozen"]["test"]["point"]

    p4 = (
        abs(lof["f1"] - F18_REFERENCE["lof_frozen"]["f1"]) < 1e-4
        and abs(lof["fp_rate_normal"] - F18_REFERENCE["lof_frozen"]["fp_rate_normal"]) < 1e-4
    )
    slow = {
        f: results["arms"][candidate]["per_fault_recall_median"].get(f, 0.0) for f in SLOW_FAULTS
    }
    checks = {
        "P1_fpr_baja_respecto_a_v11": {
            "holds": ae2["fp_rate_normal_median"] < ae11["fp_rate_normal_median"],
            "ae_v2": ae2["fp_rate_normal_median"],
            "ae_v11": ae11["fp_rate_normal_median"],
        },
        "P2_fpr_highway_leq_0.10": {
            "holds": ae2["highway_fpr_median"] is not None and ae2["highway_fpr_median"] <= 0.10,
            "value": ae2["highway_fpr_median"],
        },
        "P3_lentas_siguen_bajo_0.10": {
            "holds": all(v < 0.10 for v in slow.values()),
            "recalls": slow,
            "note": "predicción NEGATIVA declarada a priori: la cobertura no arregla lo lento",
        },
        "P4_lof_congelado_reproduce_F18": {
            "holds": bool(p4),
            "observed": lof,
            "expected": F18_REFERENCE["lof_frozen"],
        },
    }

    fpr_med, f1_med = ae2["fp_rate_normal_median"], ae2["f1_median"]
    all_seeds_ok = ae2["fp_rate_normal_max"] <= 0.05
    d1 = _d1_category(fpr_med, f1_med, all_seeds_ok)
    #: la MISMA regla aplicada semilla a semilla: si la categoría cambia entre semillas, la
    #: decisión no es estable y el estado de H1 se declara INCONCLUSIVE (regla a priori F22)
    per_seed_categories = {
        seed: _d1_category(
            s["point"]["fp_rate_normal"], s["point"]["f1"], s["point"]["fp_rate_normal"] <= 0.05
        )
        for seed, s in results["arms"][candidate]["seeds"].items()
    }
    return {
        "predictions": checks,
        f"D1_{candidate}": {
            "decision": d1,
            "criteria_evaluated": {
                "median_fpr<=0.03": fpr_med <= 0.03,
                "all_seeds_fpr<=0.05": bool(all_seeds_ok),
                "median_f1>=0.70": f1_med >= 0.70,
                "median_f1>0.6448": f1_med > 0.6448,
            },
            "observed": {
                "median_fpr": fpr_med,
                "max_fpr": ae2["fp_rate_normal_max"],
                "median_f1": f1_med,
            },
            "per_seed_category": per_seed_categories,
            "meaning": (
                "PROMOTE_CANDIDATE = candidato a adopción, NO adopción: la adopción exige un "
                "confirmatorio posterior al freeze del pre-registro"
            ),
        },
    }


def main() -> int:  # noqa: PLR0912, PLR0915
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fpr", type=float, default=0.01)
    parser.add_argument("--benchmark", choices=sorted(BENCHMARKS), default="v2")
    args = parser.parse_args()
    t0 = time.perf_counter()
    tag = args.benchmark
    bench = BENCHMARKS[tag]
    candidate, lof_arm = f"ae_{tag}", f"lof_{tag}"
    freeze_path, results_json = bench["freeze"], bench["results"]
    expansion_dir = bench["expansion_dir"]
    results: dict[str, Any] = {
        "experiment": bench["experiment"],
        "study_type": "exploratory",
        "config": bench["config"],
        "arms": {},
    }

    # ------------------------------------------------- fase 0: freeze + datasets
    print(f"fase 0: verificando el freeze del banco {tag}…", flush=True)
    ok, problems = verify(freeze_path)
    if not ok:
        for p in problems[:10]:
            print(f"  ✗ {p}")
        print("ABORTADO: los datos no coinciden con el banco congelado")
        return 1
    freeze_manifest = json.loads(freeze_path.read_text(encoding="utf-8"))
    results["benchmark"] = {
        "version": freeze_manifest["benchmark_version"],
        "benchmark_sha256": freeze_manifest["benchmark_sha256"],
        "verified": True,
    }
    materialize_v11(args.sessions, V11_ROOT)  # idempotente: no regenera si ya existe

    print("fase 0: construyendo datasets fs1 (camino wide canónico)…", flush=True)
    train10, _, _ = build_dataset_wide(args.sessions / "train", CANON_W, CANON_S)
    train11, _, _ = build_dataset_wide(V11_ROOT / "train", CANON_W, CANON_S)
    expansion, _, _ = build_dataset_wide(expansion_dir, CANON_W, CANON_S)
    test, _, _ = build_dataset_wide(args.sessions / "test", CANON_W, CANON_S)
    x_v2 = np.vstack([train11.x, expansion.x])
    headers = {**_headers(args.sessions / "test"), **_headers(args.sessions / "train")}
    results["datasets"] = {
        "train_v11_windows": int(train11.x.shape[0]),
        f"expansion_{tag}_windows": int(expansion.x.shape[0]),
        f"train_{tag}_windows": int(x_v2.shape[0]),
        "test_windows": int(test.x.shape[0]),
        "test_anomalous_windows": int(test.y.sum()),
        "note": "test histórico intacto; el escalador de cada brazo se ajusta solo con su train",
    }
    print(
        f"  train v1.1={train11.x.shape[0]} · expansión={expansion.x.shape[0]} · "
        f"train {tag}={x_v2.shape[0]} · test={test.x.shape[0]}",
        flush=True,
    )

    # Re-verificación del criterio de cobertura EFECTIVA sobre el train que se va a usar,
    # con el mismo instrumento que construyó el banco. Es el control que F20/F21 no tenían:
    # el banco puede estar congelado por hash y aun así no contener la cobertura declarada.
    coverage_ok = True
    criterion = bench["coverage_criterion"]
    if criterion is not None:
        ltft_idx = FEATURE_NAMES.index(LTFT_FEATURE)
        measured = ltft_level_coverage(x_v2, ltft_idx)
        verdict = check_coverage_criterion(measured, criterion["positive"], criterion["negative"])
        coverage_ok = bool(verdict["passes"])
        results["coverage_criterion"] = verdict
        print(
            f"  cobertura efectiva del train {tag}: nivel+ {measured['positive_level_share']} "
            f"· nivel− {measured['negative_level_share']} → "
            f"{'CUMPLE' if coverage_ok else 'NO CUMPLE'}",
            flush=True,
        )
        if not coverage_ok:
            results["stop_rule_triggered"] = (
                "el train no alcanza el criterio de cobertura efectiva declarado a priori"
            )
            results_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
            print("ABORTADO: el banco no cumple su propio criterio de cobertura")
            return 1

    # ------------------------------- fase 1: control de integridad del pipeline (P4)
    print("fase 1: LOF congelado (arms-freeze-v1)…", flush=True)
    lof = next(d for d in make_baselines(args.seed) if d.name == "lof")
    lof.fit(train10.x)
    thr_lof = float(threshold_from_normal(lof.scores(train10.x), target_fpr=args.fpr))
    frozen_ok = abs(thr_lof - LOF_FROZEN_THRESHOLD) < 1e-6
    r_lof = evaluate(lof, thr_lof, test, headers)
    results["arms"]["lof_frozen"] = {
        "note": "brazo congelado arms-freeze-v1 (fs1, train v1.0); jamás re-entrenado",
        "threshold_value": round(thr_lof, 6),
        "threshold_matches_freeze": frozen_ok,
        "test": arm_summary(r_lof),
    }
    print(
        f"  umbral={thr_lof:.6f} (freeze {LOF_FROZEN_THRESHOLD}) · "
        f"F1={r_lof['point']['f1']:.4f} FPR={r_lof['point']['fp_rate_normal']:.4f}",
        flush=True,
    )
    if not frozen_ok:
        results["stop_rule_triggered"] = "P4: el LOF congelado no reproduce el umbral del freeze"
        results_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
        print("ABORTADO por regla de parada (a): deriva de pipeline")
        return 1

    # --------------------------------------------- fase 2: brazos AE multi-seed
    print(f"fase 2: AE denso fs1 — train v1.1 vs train {tag} (seeds 42/43/44)…", flush=True)
    trains = {"ae_v11": train11.x, candidate: x_v2}
    finalists: dict[str, AutoencoderDetector] = {}
    finalist_thresholds: dict[str, float] = {}
    for arm, x_train in trains.items():
        per_seed: dict[str, Any] = {}
        f1s, fprs, highway, recalls = [], [], [], []
        fault_recalls: dict[str, list[float]] = {}
        for seed in SEEDS:
            det, thr = fit_ae(x_train, seed, args.fpr)
            res = evaluate(det, thr, test, headers)
            summary = arm_summary(res)
            per_seed[str(seed)] = {"threshold_value": round(thr, 6), **summary}
            f1s.append(res["point"]["f1"])
            fprs.append(res["point"]["fp_rate_normal"])
            recalls.append(res["point"]["recall"])
            prof = fpr_by_profile(res)
            if "highway" in prof:
                highway.append(prof["highway"])
            for fault, value in res["per_fault_recall"].items():
                fault_recalls.setdefault(fault, []).append(value)
            if seed == args.seed:
                finalists[arm] = det
                finalist_thresholds[arm] = thr
        results["arms"][arm] = {
            "train": "v1.1 (22 sesiones)" if arm == "ae_v11" else bench["train_label"],
            "architecture": "AE-S denso fs1 (42→32→16→8→…); idéntica en ambos brazos",
            "n_train_windows": int(x_train.shape[0]),
            "seeds": per_seed,
            "aggregate": {
                "f1_median": _median(f1s),
                "f1_min": round(min(f1s), 4),
                "f1_max": round(max(f1s), 4),
                "fp_rate_normal_median": _median(fprs),
                "fp_rate_normal_min": round(min(fprs), 4),
                "fp_rate_normal_max": round(max(fprs), 4),
                "recall_median": _median(recalls),
                "highway_fpr_median": _median(highway) if highway else None,
            },
            "per_fault_recall_median": {k: _median(v) for k, v in sorted(fault_recalls.items())},
            "f18_reference": F18_REFERENCE.get(arm),
        }
        agg = results["arms"][arm]["aggregate"]
        print(
            f"  {arm}: F1={agg['f1_median']:.4f} FPR={agg['fp_rate_normal_median']:.4f} "
            f"(máx {agg['fp_rate_normal_max']:.4f}) highway={agg['highway_fpr_median']}",
            flush=True,
        )

    # ------------------------------------------------- fase 3: LOF v2 informativo
    print(f"fase 3: LOF re-entrenado con el banco {tag} (informativo)…", flush=True)
    lof2 = next(d for d in make_baselines(args.seed) if d.name == "lof")
    lof2.fit(x_v2)
    thr_lof2 = float(threshold_from_normal(lof2.scores(x_v2), target_fpr=args.fpr))
    r_lof2 = evaluate(lof2, thr_lof2, test, headers)
    results["arms"][lof_arm] = {
        "note": "INFORMATIVO — no candidato a adopción; el brazo congelado sigue siendo el control",
        "threshold_value": round(thr_lof2, 6),
        "test": arm_summary(r_lof2),
    }
    print(
        f"  {lof_arm}: F1={r_lof2['point']['f1']:.4f} FPR={r_lof2['point']['fp_rate_normal']:.4f}",
        flush=True,
    )

    # ------------------------------- fase 4: predicciones y criterio D1 declarados
    print("fase 4: contraste de predicciones y criterio D1…", flush=True)
    results["hypothesis_test"] = check_predictions(results, candidate)
    d1_block = results["hypothesis_test"][f"D1_{candidate}"]
    for name, check in results["hypothesis_test"]["predictions"].items():
        print(f"  {name}: {'SE CUMPLE' if check['holds'] else 'FALLA'}", flush=True)
    print(f"  D1 = {d1_block['decision']}", flush=True)

    # Estado exploratorio de H1 (cierre de línea): solo para el banco que declara criterio
    # de cobertura, porque la regla exige saber si el antecedente se cumplió.
    if criterion is not None:
        results["h1_exploratory_status"] = h1_exploratory_status(
            results["arms"][candidate]["aggregate"],
            results["arms"]["ae_v11"]["aggregate"],
            d1_block["decision"],
            bool(
                results["hypothesis_test"]["predictions"]["P4_lof_congelado_reproduce_F18"]["holds"]
            ),
            coverage_ok,
            set(d1_block["per_seed_category"].values()),
        )
        h1 = results["h1_exploratory_status"]
        print(
            f"  H1 exploratory status = {h1['status']} "
            f"(reducción relativa de FPR = {h1['relative_fpr_reduction']})",
            flush=True,
        )

    # ------------------------------------------------------ fase 5: embeddings (D2)
    print("fase 5: embeddings (D2)…", flush=True)
    results["embeddings"] = {arm: embeddings_report(det, test) for arm, det in finalists.items()}

    # ------------------------- fase 6: informe de causa (obligatorio si D1 = REJECT)
    if d1_block["decision"] != "PROMOTE_CANDIDATE":
        print("fase 6: informe de causa (regla de parada b)…", flush=True)
        control_x = None
        if CONTROL_DIR.is_dir() and any(CONTROL_DIR.glob("*.jsonl")):
            control_ds, _, _ = build_dataset_wide(CONTROL_DIR, CANON_W, CANON_S)
            control_x = control_ds.x
        results["cause_report"] = cause_report(
            finalists[candidate],
            finalist_thresholds[candidate],
            test,
            headers,
            train11.x,
            expansion.x,
            control_x,
        )
        cr = results["cause_report"]
        print(
            f"  FP: {cr['false_positive_windows']}/{cr['normal_test_windows']} ventanas · "
            f"features dominantes {[f['feature'] for f in cr['dominant_error_features'][:3]]}",
            flush=True,
        )
        cr["quantization_mechanism_probe"] = quantization_probe()
        probe = cr["quantization_mechanism_probe"]
        print(
            "  sonda del mecanismo (P de nivel positivo sostenido): "
            + " · ".join(
                f"{d}s={probe[d]['p_any_positive_level_window']}"
                for d in ("1800", "2400", "3600", "5400")
            ),
            flush=True,
        )
        for name, cov in cr["ltft_mean_coverage"].items():
            print(
                f"  LTFT_mean {name}: nivel+ {cov['positive_level_share']} · "
                f"nivel− {cov['negative_level_share']} · max {cov['max']}",
                flush=True,
            )

    # ------------------------------------------------------------- fase 7: resumen
    results["validity_note"] = (
        "EXPLORATORIO; entorno emulado/sintético (sin HCRL ni ARM64). El test histórico no se "
        "tocó y conserva el distribution shift de AUDIT-DATA-001. PROMOTE_CANDIDATE, si se da, "
        "no es adopción: exige confirmatorio tras el freeze del pre-registro."
    )
    results["total_runtime_s"] = round(time.perf_counter() - t0, 1)
    results["peak_rss_mb"] = peak_rss_mb()
    results["git_sha"] = git_sha(REPO_ROOT)
    results_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    record_run(
        RUNS_FILE,
        {
            "experiment": bench["experiment"],
            "seed": args.seed,
            "target_fpr": args.fpr,
            "decision_d1": d1_block["decision"],
            "h1_exploratory_status": results.get("h1_exploratory_status", {}).get("status"),
            "benchmark_sha256": results["benchmark"]["benchmark_sha256"],
        },
    )
    print(f"\nresultados → {results_json.name} ({results['total_runtime_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
