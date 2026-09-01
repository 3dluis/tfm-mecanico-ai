"""Métricas de clasificación (grupo M1).

E5 dejó un reparto de 2:1 entre la clase normal y cada fallo. Con ese
desequilibrio la **exactitud global es engañosa**: predecir siempre «normal»
acierta el 28,6 % sin haber aprendido nada. Por eso la métrica principal es el F1
macro, que pesa igual las seis clases, y se reporta el desglose por clase.

La calibración se mide desde aquí y no en E8 porque la confianza del modelo
alimenta el criterio de suficiencia de E15: una confianza sin calibrar haría que
ese criterio decidiera sobre un número que no significa lo que aparenta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd


@dataclass(frozen=True)
class ClassificationReport:
    """Resultado de evaluar un clasificador sobre una partición."""

    partition: str
    n: int
    accuracy: float
    macro_f1: float
    weighted_f1: float
    balanced_accuracy: float
    per_class: pd.DataFrame
    confusion: pd.DataFrame
    labels: tuple[str, ...]
    calibration: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "partition": self.partition,
            "n": self.n,
            "accuracy": round(self.accuracy, 4),
            "macro_f1": round(self.macro_f1, 4),
            "weighted_f1": round(self.weighted_f1, 4),
            "balanced_accuracy": round(self.balanced_accuracy, 4),
            "calibration": {k: round(v, 4) for k, v in self.calibration.items()},
            "per_class": self.per_class.round(4).to_dict(orient="records"),
        }

    def __str__(self) -> str:
        cabecera = (
            f"{self.partition}: n={self.n}  F1 macro={self.macro_f1:.3f}  "
            f"exactitud={self.accuracy:.3f}  exactitud equilibrada="
            f"{self.balanced_accuracy:.3f}"
        )
        return cabecera + "\n" + self.per_class.round(3).to_string(index=False)


def expected_calibration_error(
    confianzas: npt.NDArray[np.float64], aciertos: npt.NDArray[np.bool_], n_bins: int = 10
) -> float:
    """Error de calibración esperado.

    Agrupa las predicciones por confianza y compara, en cada grupo, la confianza
    media con la proporción de aciertos. Cero significa que cuando el modelo dice
    0,8 acierta el 80 % de las veces.

    Se pondera por el tamaño de cada grupo: un grupo con tres predicciones no
    puede pesar lo mismo que uno con doscientas.
    """
    if confianzas.size == 0:
        return float("nan")
    bordes = np.linspace(0.0, 1.0, n_bins + 1)
    total = confianzas.size
    error = 0.0
    for inicio, fin in pairwise(bordes):
        en_bin = (confianzas > inicio) & (confianzas <= fin)
        if not en_bin.any():
            continue
        peso = float(en_bin.sum()) / total
        error += peso * abs(float(aciertos[en_bin].mean()) - float(confianzas[en_bin].mean()))
    return error


def evaluate_classification(
    y_true: npt.NDArray[np.str_],
    y_pred: npt.NDArray[np.str_],
    *,
    partition: str,
    probabilities: npt.NDArray[np.float64] | None = None,
    class_order: tuple[str, ...] | None = None,
) -> ClassificationReport:
    """Evalúa una clasificación multiclase."""
    from sklearn.metrics import (
        average_precision_score,
        balanced_accuracy_score,
        confusion_matrix,
        f1_score,
        precision_recall_fscore_support,
    )

    etiquetas = tuple(class_order) if class_order else tuple(sorted(set(y_true.tolist())))

    precision, recall, f1, soporte = precision_recall_fscore_support(
        y_true, y_pred, labels=list(etiquetas), zero_division=0
    )
    por_clase = pd.DataFrame(
        {
            "label": etiquetas,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": soporte,
        }
    )

    if probabilities is not None:
        # PR-AUC uno-contra-el-resto: con clases desequilibradas informa más que
        # el área bajo la curva ROC, que se deja engañar por la clase abundante.
        pr_auc: list[float] = []
        for i, etiqueta in enumerate(etiquetas):
            positivo = (y_true == etiqueta).astype(int)
            if positivo.sum() == 0 or positivo.sum() == positivo.size:
                pr_auc.append(float("nan"))
            else:
                pr_auc.append(float(average_precision_score(positivo, probabilities[:, i])))
        por_clase["pr_auc"] = pr_auc

    calibracion: dict[str, float] = {}
    if probabilities is not None:
        confianzas = probabilities.max(axis=1)
        aciertos = (y_true == y_pred).astype(bool)
        calibracion = {
            "ece": expected_calibration_error(confianzas, aciertos),
            "mean_confidence": float(confianzas.mean()),
            "accuracy": float(aciertos.mean()),
        }
        # La diferencia entre confianza media y acierto es el sesgo: positivo
        # significa que el modelo se cree más de lo que acierta.
        calibracion["overconfidence"] = calibracion["mean_confidence"] - calibracion["accuracy"]

    matriz = confusion_matrix(y_true, y_pred, labels=list(etiquetas))
    confusion = pd.DataFrame(matriz, index=list(etiquetas), columns=list(etiquetas))

    return ClassificationReport(
        partition=partition,
        n=int(y_true.size),
        accuracy=float((y_true == y_pred).mean()),
        macro_f1=float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        weighted_f1=float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        balanced_accuracy=float(balanced_accuracy_score(y_true, y_pred)),
        per_class=por_clase,
        confusion=confusion,
        labels=etiquetas,
        calibration=calibracion,
    )
