"""Tests de la definición canónica de features (contrato entrenamiento↔inferencia)."""

from mecanico_contracts.features import (
    CANONICAL_PIDS,
    FEATURE_NAMES,
    extract_features,
    feature_vector,
)


def _window(n: int = 60) -> dict[str, list[float]]:
    return {
        pid: [float(i % 7) + k for i, _ in enumerate(range(n))]
        for k, pid in enumerate(CANONICAL_PIDS)
    }


def test_orden_estable_y_completo() -> None:
    feats = extract_features(_window())
    assert set(feats) == set(FEATURE_NAMES)
    vec = feature_vector(_window())
    assert len(vec) == len(FEATURE_NAMES)
    assert vec == [feats[n] for n in FEATURE_NAMES]


def test_correlacion_series_iguales() -> None:
    w = _window()
    w["MAF"] = list(w["RPM"])
    feats = extract_features(w)
    assert abs(feats["corr_RPM_MAF"] - 1.0) < 1e-9


def test_serie_constante_correlacion_cero() -> None:
    w = _window()
    w["MAF"] = [5.0] * 60
    assert extract_features(w)["corr_RPM_MAF"] == 0.0


def test_pid_ausente_no_rompe() -> None:
    w = _window()
    del w["O2_B1S1"]
    feats = extract_features(w)
    assert feats["O2_B1S1_mean"] == 0.0
