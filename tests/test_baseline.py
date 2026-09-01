"""Baseline, métricas y la llave del conjunto de test."""

from __future__ import annotations

import numpy as np
import pytest

from mecanico_ia_exp.data.dataset import LockedPartitionError, load_partition
from mecanico_ia_exp.evaluation.metrics import (
    evaluate_classification,
    expected_calibration_error,
)
from mecanico_ia_exp.models.baseline import (
    BaselineConfig,
    train_baseline,
    train_majority_baseline,
)

CLASES = ("A", "B", "C")


# --------------------------------------------------------- llave del test


def test_pedir_el_test_sin_declararlo_falla() -> None:
    """El test está cerrado hasta E19. Un descuido debe producir una excepción,
    no un resultado inválido que nadie note."""
    with pytest.raises(LockedPartitionError, match="cerrado"):
        load_partition("test")


def test_pedir_el_test_sin_razon_escrita_falla() -> None:
    with pytest.raises(LockedPartitionError, match="razón"):
        load_partition("test", allow_test=True)


def test_el_mensaje_de_bloqueo_indica_la_alternativa() -> None:
    """Un error que no dice qué hacer en su lugar invita a saltárselo."""
    with pytest.raises(LockedPartitionError, match="validación"):
        load_partition("test")


# -------------------------------------------------------------- baseline


def _datos_separables(n: int = 90, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = np.vstack(
        [
            rng.normal(0.0, 0.4, (n // 3, 4)),
            rng.normal(4.0, 0.4, (n // 3, 4)),
            rng.normal(8.0, 0.4, (n // 3, 4)),
        ]
    )
    y = np.array(["A"] * (n // 3) + ["B"] * (n // 3) + ["C"] * (n // 3), dtype=np.str_)
    return x, y


def test_model_prediction_schema() -> None:
    """La salida del modelo debe tener la forma que el resto del pipeline espera:
    una etiqueta por ventana, y probabilidades que sumen uno por fila."""
    x, y = _datos_separables()
    modelo = train_baseline(x, y)

    predicciones = modelo.predict(x)
    assert predicciones.shape == (x.shape[0],)
    assert set(predicciones.tolist()) <= set(CLASES)

    probabilidades = modelo.predict_proba(x)
    assert probabilidades.shape == (x.shape[0], len(CLASES))
    assert np.allclose(probabilidades.sum(axis=1), 1.0)
    assert (probabilidades >= 0.0).all()
    assert tuple(modelo.classes_) == CLASES


def test_el_entrenamiento_es_reproducible() -> None:
    x, y = _datos_separables()
    a = train_baseline(x, y, BaselineConfig(n_estimators=50))
    b = train_baseline(x, y, BaselineConfig(n_estimators=50))
    assert np.array_equal(a.predict(x), b.predict(x))


def test_la_referencia_minima_devuelve_la_clase_mas_frecuente() -> None:
    y = np.array(["A"] * 10 + ["B"] * 3, dtype=np.str_)
    assert train_majority_baseline(y) == "A"


def test_la_referencia_minima_conserva_el_identificador_completo() -> None:
    """Un dtype mal elegido trunca las etiquetas a su primera letra y produce
    una exactitud de cero que parece un resultado."""
    y = np.array(["F00_normal"] * 5 + ["F01_vacuum_leak"] * 2)
    mayoritaria = train_majority_baseline(y)
    assert mayoritaria == "F00_normal"
    predicho = np.full(y.shape, mayoritaria, dtype=y.dtype)
    assert float((y == predicho).mean()) == pytest.approx(5 / 7)


# --------------------------------------------------------------- métricas


def test_una_clasificacion_perfecta_da_f1_uno() -> None:
    y = np.array(["A", "B", "C", "A"], dtype=np.str_)
    informe = evaluate_classification(y, y, partition="v", class_order=CLASES)
    assert informe.macro_f1 == pytest.approx(1.0)
    assert informe.accuracy == pytest.approx(1.0)
    assert np.array_equal(np.diag(informe.confusion.to_numpy()), np.array([2, 1, 1]))


def test_el_f1_macro_penaliza_ignorar_una_clase_minoritaria() -> None:
    """Es la razón de usarlo con un reparto desequilibrado: la exactitud premia
    predecir siempre la clase abundante y el F1 macro no."""
    y = np.array(["A"] * 8 + ["B"] * 2, dtype=np.str_)
    siempre_a = np.array(["A"] * 10, dtype=np.str_)
    informe = evaluate_classification(y, siempre_a, partition="v", class_order=("A", "B"))
    assert informe.accuracy == pytest.approx(0.8)
    assert informe.macro_f1 < 0.5


def test_la_matriz_de_confusion_orienta_filas_a_la_verdad() -> None:
    """Transponerla es un error clásico que invierte precisión y exhaustividad."""
    y_true = np.array(["A", "A", "B"], dtype=np.str_)
    y_pred = np.array(["A", "B", "B"], dtype=np.str_)
    informe = evaluate_classification(y_true, y_pred, partition="v", class_order=("A", "B"))
    assert informe.confusion.loc["A", "B"] == 1
    assert informe.confusion.loc["B", "A"] == 0


def test_una_prediccion_perfectamente_calibrada_tiene_error_cero() -> None:
    confianzas = np.array([1.0] * 10)
    aciertos = np.ones(10, dtype=bool)
    assert expected_calibration_error(confianzas, aciertos) == pytest.approx(0.0)


def test_el_error_de_calibracion_detecta_el_exceso_de_confianza() -> None:
    """Confianza 0,9 con la mitad de aciertos: el error debe rondar 0,4."""
    confianzas = np.full(10, 0.9)
    aciertos = np.array([True] * 5 + [False] * 5)
    assert expected_calibration_error(confianzas, aciertos) == pytest.approx(0.4)


def test_el_error_de_calibracion_pondera_por_tamano_de_grupo() -> None:
    """Un grupo de tres predicciones no puede pesar como uno de cien."""
    confianzas = np.array([0.95] * 99 + [0.15])
    aciertos = np.array([True] * 99 + [True])
    error = expected_calibration_error(confianzas, aciertos)
    assert error < 0.06, f"el grupo minoritario domina el resultado: {error:.3f}"


def test_sin_probabilidades_no_se_reporta_calibracion() -> None:
    y = np.array(["A", "B"], dtype=np.str_)
    informe = evaluate_classification(y, y, partition="v", class_order=("A", "B"))
    assert informe.calibration == {}


def test_el_informe_serializa_sin_perder_las_metricas_clave() -> None:
    x, y = _datos_separables(seed=3)
    modelo = train_baseline(x, y, BaselineConfig(n_estimators=40))
    informe = evaluate_classification(
        y,
        np.asarray(modelo.predict(x), dtype=np.str_),
        partition="v",
        probabilities=np.asarray(modelo.predict_proba(x), dtype=np.float64),
        class_order=CLASES,
    )
    datos = informe.to_dict()
    assert set(datos) >= {"partition", "n", "accuracy", "macro_f1", "calibration", "per_class"}
    assert len(datos["per_class"]) == len(CLASES)
