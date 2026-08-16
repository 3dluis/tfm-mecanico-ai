"""Cobertura **efectiva** de normalidad en el espacio de features — F22.

Este módulo existe por un resultado negativo concreto. EXP-ANOM-010 (F21) demostró que el
banco v2 cerraba «sobre el papel» un hueco de cobertura que **no aportaba ni una sola
ventana útil**: F20 declaró la cobertura con un contador de SESIÓN y binario (¿algún tick
cambia?, ¿algún tick es ≠ 0?) mientras que el modelo consume VENTANAS de features. La
taxonomía de fallos ganó por ello una variante nueva:

    cobertura declarada ≠ cobertura efectiva

La regla que este módulo hace operativa: **un hueco de cobertura se mide en el espacio de
representación que el modelo consume, con el mismo instrumento que después lo verifica.**
Por eso `ltft_level_coverage` es la ÚNICA implementación del criterio en el repositorio;
tanto la construcción del banco v3 como el runner de la réplica la importan de aquí en vez
de recalcularla. Dos instrumentos distintos para la misma magnitud es exactamente el
mecanismo que produjo el fallo de F20/F21.

No es un detector: no se ajusta a nada, no tiene umbral operativo y no compite con ningún
modelo. Depende solo de numpy (regla de dependencias §9.4): no importa obd-lab.
"""

from typing import Any

import numpy as np

#: Cuanto J1979 del LTFT (%). La codificación del proyecto es ``int(v · 128/100)``, que
#: **trunca hacia cero** (``obd_lab/emulator/encoding.py``): el valor emitido solo cambia
#: de nivel cuando el paseo aleatorio supera un cuanto COMPLETO, no medio. F20 razonó con
#: medio cuanto y por eso infradimensionó la expansión (informe F21 §3).
LTFT_QUANTUM = 0.78125

#: Corte para declarar «nivel sostenido» en la MEDIA de la ventana. Medio cuanto: una
#: ventana cuya media supera 0.390625 solo puede provenir de ticks mayoritariamente en el
#: cuanto ±0.78125, que es justo la región que dispara los falsos positivos de F21.
LTFT_HALF_QUANTUM = LTFT_QUANTUM / 2

#: Feature que el informe de causa de F21 identificó como dominante del error de
#: reconstrucción en los falsos positivos (MSE medio 190.2, un orden de magnitud sobre la
#: siguiente). El criterio de cobertura de v3 se define sobre ella y solo sobre ella.
LTFT_FEATURE = "LONG_FUEL_TRIM_1_mean"


def ltft_level_coverage(x: np.ndarray, ltft_index: int) -> dict[str, float]:
    """Cobertura efectiva del nivel de LTFT en un conjunto de ventanas de features.

    ``x`` es la matriz ventanas × features tal y como la consume el modelo, y
    ``ltft_index`` la posición de :data:`LTFT_FEATURE` en ``FEATURE_NAMES``. Devuelve la
    fracción de ventanas cuyo nivel medio de LTFT está en un cuanto **positivo** y en uno
    **negativo** sostenido, separadas por signo: la asimetría importa, porque los falsos
    positivos de F21 son íntegramente de signo positivo (0.8276 de nivel +, 0.0 de nivel −)
    y un banco puede cubrir el lado negativo sin aportar nada al positivo — que fue
    literalmente lo que ocurrió con v1.1 + v2.
    """
    if x.ndim != 2:  # pragma: no cover - contrato de forma
        msg = f"se esperaba una matriz ventanas × features, recibido {x.shape}"
        raise ValueError(msg)
    if x.shape[0] == 0:
        return {"n_windows": 0.0, "positive_level_share": 0.0, "negative_level_share": 0.0}
    level = x[:, ltft_index]
    return {
        "n_windows": float(x.shape[0]),
        "min": round(float(level.min()), 4),
        "p50": round(float(np.median(level)), 4),
        "max": round(float(level.max()), 4),
        "positive_level_share": round(float((level >= LTFT_HALF_QUANTUM).mean()), 4),
        "negative_level_share": round(float((level <= -LTFT_HALF_QUANTUM).mean()), 4),
    }


def check_coverage_criterion(
    measured: dict[str, float],
    min_positive_share: float,
    min_negative_share: float,
) -> dict[str, Any]:
    """Contrasta la cobertura medida contra el criterio declarado **a priori**.

    Devuelve el veredicto completo (no solo un booleano) para que el manifiesto del banco
    y el informe registren qué se exigió y qué se obtuvo, aunque el criterio se cumpla.
    Un criterio que solo se guarda cuando falla no es auditable.
    """
    positive_ok = measured["positive_level_share"] >= min_positive_share
    negative_ok = measured["negative_level_share"] >= min_negative_share
    return {
        "criterion": {
            "positive_level_share>=": min_positive_share,
            "negative_level_share>=": min_negative_share,
            "declared": "a priori, antes de generar el banco (config exp-anom-010-r2.yaml)",
        },
        "measured": {
            "positive_level_share": measured["positive_level_share"],
            "negative_level_share": measured["negative_level_share"],
            "n_windows": measured["n_windows"],
        },
        "positive_ok": positive_ok,
        "negative_ok": negative_ok,
        "passes": bool(positive_ok and negative_ok),
    }
