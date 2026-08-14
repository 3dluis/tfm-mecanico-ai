"""Extracción fs2-lite — ablation de features EXP-ANOM-008 (NO es esquema canónico).

Implementa EXCLUSIVAMENTE las tres candidatas ya documentadas y justificadas
(fs2-draft, F13; causa raíz confirmada en EXP-ANOM-007 por diagnóstico + SHAP):

1. **Deriva de trims relativa a la propia sesión** — ``LTFT_session_drift`` y
   ``total_trim_session_drift`` SUSTITUYEN a ``LONG_FUEL_TRIM_1_mean`` y
   ``total_trim_mean``. Justificación de la sustitución (decisión de diseño declarada,
   no silenciosa): el nivel ABSOLUTO de LTFT es la dimensión espuria identificada — un
   offset de sesión legítimo que el AE marca como anomalía; mantener el absoluto junto
   al relativo dejaría la patología intacta por construcción (el error de reconstrucción
   sigue incluyendo la feature absoluta). La deriva relativa conserva la señal de fallo
   (vacuum/maf mueven el LTFT DENTRO de la sesión respecto a su propio arranque).
2. **std multiescala** (sub-bloques de 15 muestras) para RPM, MAF, COOLANT_TEMP y LTFT
   (ADR-0011: «señal intermitente por ventana en held-out temporales»).
3. **Correlaciones lag-1** RPM(t)↔MAF(t-1) y THROTTLE_POS(t)↔MAF(t-1) (respuesta
   retardada demanda→flujo; convención: primera señal en t, segunda en t-1).

Referencia de sesión: media de LTFT/(STFT+LTFT) de los primeros ``REF_S`` segundos de la
PROPIA sesión (a 1 Hz = primeras REF_S muestras). No usa ninguna otra sesión ni split:
no introduce leakage entre sesiones y es computable en streaming en el edge.

fs1 sigue siendo el esquema canónico; fs2-lite vive SOLO en ai-models hasta que la
ablation justifique (o no) proponer su promoción como contrato (Protocolo ML v1 §4).
"""

from dataclasses import dataclass

import numpy as np

from mecanico_contracts.features import FEATURE_NAMES, extract_features

#: Segundos iniciales de la sesión que definen la referencia de trims (a 1 Hz).
REF_S = 120

#: Tamaño de sub-bloque de la std multiescala.
MULTISCALE_BLOCK = 15

#: PIDs con std multiescala (fs2-draft, justificados por ADR-0011/F9).
MULTISCALE_PIDS = ("RPM", "MAF", "COOLANT_TEMP", "LONG_FUEL_TRIM_1")

#: Pares lag-1: primera señal en t, segunda en t-1.
LAG1_PAIRS = (("RPM", "MAF"), ("THROTTLE_POS", "MAF"))

#: Features de fs1 SUSTITUIDAS por sus contrapartes relativas a la sesión.
REPLACED = ("LONG_FUEL_TRIM_1_mean", "total_trim_mean")

#: Orden EXACTO y estable de las features fs2-lite (48).
FS2_LITE_NAMES: list[str] = (
    [n for n in FEATURE_NAMES if n not in REPLACED]
    + ["LTFT_session_drift", "total_trim_session_drift"]
    + [f"{pid}_std_15" for pid in MULTISCALE_PIDS]
    + [f"corr_lag1_{a}_{b}" for a, b in LAG1_PAIRS]
)


@dataclass(frozen=True)
class SessionTrimReference:
    """Referencia de trims del arranque de la PROPIA sesión (sin datos de otras)."""

    ltft_ref: float
    total_trim_ref: float


def session_reference(ltft_series: list[float], stft_series: list[float]) -> SessionTrimReference:
    """Referencia desde las primeras REF_S muestras de la sesión (1 Hz)."""
    n = min(REF_S, len(ltft_series))
    if n == 0:
        msg = "sesión vacía: no hay referencia de trims"
        raise ValueError(msg)
    ltft0 = float(np.mean(ltft_series[:n]))
    total0 = float(
        np.mean([s + lt for s, lt in zip(stft_series[:n], ltft_series[:n], strict=True)])
    )
    return SessionTrimReference(ltft_ref=ltft0, total_trim_ref=total0)


def _multiscale_std(xs: list[float]) -> float:
    """Media de std muestrales de sub-bloques consecutivos de MULTISCALE_BLOCK muestras."""
    n_blocks = len(xs) // MULTISCALE_BLOCK
    if n_blocks == 0:
        msg = f"ventana demasiado corta para multiescala ({len(xs)} < {MULTISCALE_BLOCK})"
        raise ValueError(msg)
    stds = [
        float(np.std(xs[i * MULTISCALE_BLOCK : (i + 1) * MULTISCALE_BLOCK], ddof=1))
        for i in range(n_blocks)
    ]
    return float(np.mean(stds))


def _lag1_corr(a: list[float], b: list[float]) -> float:
    """Pearson entre a(t) y b(t-1); 0.0 si alguna serie es constante (convención fs1)."""
    x, y = np.asarray(a[1:]), np.asarray(b[:-1])
    if x.std() == 0.0 or y.std() == 0.0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def fs2lite_features(window: dict[str, list[float]], ref: SessionTrimReference) -> dict[str, float]:
    """Vector fs2-lite (dict) para una ventana, dada la referencia de SU sesión."""
    base = extract_features(window)
    out = {n: base[n] for n in FEATURE_NAMES if n not in REPLACED}
    ltft = window["LONG_FUEL_TRIM_1"]
    stft = window["SHORT_FUEL_TRIM_1"]
    out["LTFT_session_drift"] = float(np.mean(ltft)) - ref.ltft_ref
    total = [s + lt for s, lt in zip(stft, ltft, strict=True)]
    out["total_trim_session_drift"] = float(np.mean(total)) - ref.total_trim_ref
    for pid in MULTISCALE_PIDS:
        out[f"{pid}_std_15"] = _multiscale_std(window[pid])
    for a, b in LAG1_PAIRS:
        out[f"corr_lag1_{a}_{b}"] = _lag1_corr(window[a], window[b])
    return out


def fs2lite_vector(window: dict[str, list[float]], ref: SessionTrimReference) -> list[float]:
    """Vector fs2-lite en el orden estable FS2_LITE_NAMES."""
    feats = fs2lite_features(window, ref)
    return [feats[n] for n in FS2_LITE_NAMES]
