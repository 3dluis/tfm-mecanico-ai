"""Definición CANÓNICA de features de ventana (parte del contrato entrenamiento↔inferencia).

Este módulo vive en `shared` deliberadamente (ADR-0010): la lista y el cálculo de features
determinan `ModelManifest.expected_features`, por lo que son un contrato entre `ai-models`
(entrenamiento) y `diagnostic-agent` (inferencia). Implementación en Python puro (sin numpy)
para mantener `shared` ligero; a 1 Hz con ventanas de 60 muestras el coste es despreciable.

Entrada: ventana como ``dict[pid, list[float]]`` con las series alineadas por tick.
Salida: ``dict[feature_name, float]`` con TODAS las features de ``FEATURE_NAMES``.
"""

import math

#: PIDs canónicos del subconjunto del TFM (docs/03 §3.1) usados por las features.
CANONICAL_PIDS: list[str] = [
    "RPM",
    "SPEED",
    "ENGINE_LOAD",
    "COOLANT_TEMP",
    "INTAKE_TEMP",
    "MAF",
    "THROTTLE_POS",
    "SHORT_FUEL_TRIM_1",
    "LONG_FUEL_TRIM_1",
    "O2_B1S1",
    "TIMING_ADVANCE",
    "INTAKE_PRESSURE",
]

#: PIDs sobre los que se calculan estadísticos univariantes.
_STAT_PIDS: list[str] = CANONICAL_PIDS

#: Pares para correlaciones (capturan relaciones multivariables; clave para la PI).
_CORR_PAIRS: list[tuple[str, str]] = [
    ("RPM", "MAF"),
    ("ENGINE_LOAD", "MAF"),
    ("RPM", "SPEED"),
    ("ENGINE_LOAD", "COOLANT_TEMP"),
    ("THROTTLE_POS", "RPM"),
]

#: Orden EXACTO y estable de las features (ModelManifest.expected_features).
FEATURE_NAMES: list[str] = (
    [f"{pid}_mean" for pid in _STAT_PIDS]
    + [f"{pid}_std" for pid in _STAT_PIDS]
    + [f"{pid}_slope" for pid in _STAT_PIDS]
    + [f"corr_{a}_{b}" for a, b in _CORR_PAIRS]
    + ["total_trim_mean"]
)


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _slope(xs: list[float]) -> float:
    """Pendiente por mínimos cuadrados sobre índice temporal (unidades: valor/muestra)."""
    n = len(xs)
    if n < 2:
        return 0.0
    mean_t = (n - 1) / 2.0
    mean_x = _mean(xs)
    num = sum((t - mean_t) * (x - mean_x) for t, x in enumerate(xs))
    den = sum((t - mean_t) ** 2 for t in range(n))
    return num / den if den else 0.0


def _pearson(xs: list[float], ys: list[float]) -> float:
    """Correlación de Pearson; 0.0 si alguna serie es constante (sin relación medible)."""
    n = min(len(xs), len(ys))
    if n < 2:
        return 0.0
    mx, my = _mean(xs[:n]), _mean(ys[:n])
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs[:n]))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys[:n]))
    if sx == 0.0 or sy == 0.0:
        return 0.0
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return cov / (sx * sy)


def extract_features(window: dict[str, list[float]]) -> dict[str, float]:
    """Calcula el vector de features canónico de una ventana.

    Los PIDs ausentes en la ventana producen 0.0 en sus features (y deben tratarse
    aguas arriba como pérdida de datos, no silenciarse en producción).
    """
    out: dict[str, float] = {}
    for pid in _STAT_PIDS:
        xs = window.get(pid, [])
        out[f"{pid}_mean"] = _mean(xs)
        out[f"{pid}_std"] = _std(xs)
        out[f"{pid}_slope"] = _slope(xs)
    for a, b in _CORR_PAIRS:
        out[f"corr_{a}_{b}"] = _pearson(window.get(a, []), window.get(b, []))
    stft = window.get("SHORT_FUEL_TRIM_1", [])
    ltft = window.get("LONG_FUEL_TRIM_1", [])
    n = min(len(stft), len(ltft))
    out["total_trim_mean"] = _mean([stft[i] + ltft[i] for i in range(n)]) if n else 0.0
    return out


def feature_vector(window: dict[str, list[float]]) -> list[float]:
    """Vector en el orden exacto de ``FEATURE_NAMES`` (entrada de los modelos)."""
    feats = extract_features(window)
    return [feats[name] for name in FEATURE_NAMES]
