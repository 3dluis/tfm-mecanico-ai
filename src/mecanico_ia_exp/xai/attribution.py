"""Atribución sobre el modelo especializado.

Convierte una predicción en **evidencia observacional localizable**: qué señales
la sostienen, con qué magnitud, en qué dirección y en qué ventana temporal.

Cuatro reglas, y ninguna es opcional.

**Se declara siempre qué función se explica.** Aquí, la probabilidad que el
modelo asigna a la clase predicha. Explicar «el modelo» sin decir qué salida no
es explicar.

**El fondo sale solo de entrenamiento.** SHAP compara contra una referencia; si
esa referencia incluyera validación o test, la atribución llevaría información de
particiones que el modelo no debería haber visto.

**La selección del fondo es determinista.** Misma semilla, mismas muestras,
misma atribución. Sin eso, dos ejecuciones producen explicaciones distintas para
el mismo caso y ninguna es verificable.

**La atribución NO es causalidad.** Dice de qué depende la salida del modelo, no
qué le ocurre al vehículo. Un descriptor puede dominar por estar correlacionado
con la causa sin serlo: E4 lo midió --la deriva del caudalímetro se detecta en el
ajuste de combustible, no en el caudal--. Ningún artefacto de este módulo
presenta la atribución como causa.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import numpy.typing as npt

#: Función explicada. Se registra con cada atribución.
FUNCION_EXPLICADA = "predict_proba[clase_predicha]"

Direccion = Literal["increases", "decreases", "neutral"]


@dataclass(frozen=True)
class SignalAttribution:
    """Contribución de un descriptor a una predicción."""

    feature: str
    signal: str
    """Señal OBD-II de la que procede el descriptor."""

    statistic: str
    """Estadístico calculado sobre la ventana: mean, std, delta_min…"""

    importance: float
    """Valor SHAP. Su signo es la dirección; su magnitud, el peso."""

    direction: Direccion
    value: float
    """Valor del descriptor en este caso."""

    def to_dict(self) -> dict[str, object]:
        return {
            "feature": self.feature,
            "signal": self.signal,
            "statistic": self.statistic,
            "importance": round(self.importance, 6),
            "direction": self.direction,
            "value": round(self.value, 6),
        }


@dataclass(frozen=True)
class CaseAttribution:
    """Atribución completa de un caso, con su procedencia."""

    explanation_id: str
    case_id: str
    model_id: str
    explained_function: str
    predicted_class: str
    confidence: float
    attributions: tuple[SignalAttribution, ...]

    window_start_s: float | None = None
    window_end_s: float | None = None
    session_id: str | None = None
    background_hash: str = ""
    """Huella de las muestras de fondo. Identifica contra qué se comparó."""

    explainer: str = ""
    seed: int = 0

    def top(self, n: int = 5) -> tuple[SignalAttribution, ...]:
        return tuple(sorted(self.attributions, key=lambda a: abs(a.importance), reverse=True)[:n])

    def signals_involved(self, n: int = 5) -> tuple[str, ...]:
        vistos: list[str] = []
        for a in self.top(n * 3):
            if a.signal not in vistos:
                vistos.append(a.signal)
            if len(vistos) >= n:
                break
        return tuple(vistos)

    def to_dict(self) -> dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "case_id": self.case_id,
            "model_id": self.model_id,
            "explained_function": self.explained_function,
            "predicted_class": self.predicted_class,
            "confidence": round(self.confidence, 4),
            "session_id": self.session_id,
            "window_start_s": self.window_start_s,
            "window_end_s": self.window_end_s,
            "explainer": self.explainer,
            "seed": self.seed,
            "background_hash": self.background_hash,
            "attributions": [a.to_dict() for a in self.top(10)],
        }


def split_feature_name(nombre: str) -> tuple[str, str]:
    """Separa un descriptor en (señal, estadístico).

    Los nombres se construyen como ``senal_estadistico`` y ambos pueden llevar
    guiones bajos, así que se parte por el sufijo conocido y no por el primero
    que aparezca: ``coolant_temperature_delta_min`` es la señal
    ``coolant_temperature`` con el estadístico ``delta_min``.
    """
    from mecanico_ia_exp.features.temporal import ESTADISTICOS, PAREJAS, RATIO_NAME

    if nombre == RATIO_NAME:
        return "maf", "ratio_rpm_load"
    for a, b in PAREJAS:
        if nombre == f"corr_{a}_{b}":
            return f"{a}+{b}", "correlation"
    for estadistico in sorted(ESTADISTICOS, key=len, reverse=True):
        if nombre.endswith(f"_{estadistico}"):
            return nombre[: -len(estadistico) - 1], estadistico
    return nombre, "unknown"


def _direccion(valor: float, umbral: float) -> Direccion:
    if abs(valor) < umbral:
        return "neutral"
    return "increases" if valor > 0 else "decreases"


def select_background(
    x_train: npt.NDArray[np.float64],
    y_train: npt.NDArray[np.str_],
    *,
    normal_label: str,
    n: int = 100,
    seed: int = 20260901,
) -> tuple[npt.NDArray[np.float64], str]:
    """Muestras de fondo: **solo normales de entrenamiento**, selección determinista.

    Se toman normales y no una mezcla porque la pregunta que la atribución
    responde es «qué aparta este caso de la normalidad», y el fondo define esa
    normalidad. Un fondo con fallos dentro difuminaría precisamente el contraste
    que se quiere medir.

    Devuelve las muestras y su huella, que identifica contra qué se comparó.
    """
    normales = np.flatnonzero(y_train == normal_label)
    if normales.size == 0:
        msg = f"No hay muestras de la clase {normal_label!r} en entrenamiento"
        raise ValueError(msg)

    rng = np.random.default_rng(seed)
    elegidas = np.sort(rng.choice(normales, size=min(n, normales.size), replace=False))
    fondo = np.asarray(x_train[elegidas], dtype=np.float64)
    huella = hashlib.sha256(fondo.tobytes()).hexdigest()[:16]
    return fondo, huella


def explain_cases(
    modelo: Any,
    x: npt.NDArray[np.float64],
    *,
    feature_names: tuple[str, ...],
    background: npt.NDArray[np.float64],
    background_hash: str,
    case_ids: list[str],
    model_id: str,
    meta: Any = None,
    seed: int = 20260901,
    max_evals: int = 400,
) -> list[CaseAttribution]:
    """Atribuye la probabilidad de la clase predicha, caso a caso.

    Se usa el explainer de permutación: es agnóstico al modelo, adecuado para
    descriptores tabulares y no obliga a fijar el algoritmo al tipo de modelo,
    de modo que el mismo código explicará el modelo temporal cuando toque.
    """
    import shap

    clases = list(modelo.classes_)
    probabilidades = np.asarray(modelo.predict_proba(x), dtype=np.float64)
    predichas = probabilidades.argmax(axis=1)

    resultados: list[CaseAttribution] = []
    for i, indice_clase in enumerate(predichas):
        # La función explicada se declara y se construye explícitamente: la
        # probabilidad de la clase que el modelo predijo para ESTE caso.
        def objetivo(datos: npt.NDArray[np.float64], j: int = int(indice_clase)) -> Any:
            return np.asarray(modelo.predict_proba(datos), dtype=np.float64)[:, j]

        explainer = shap.explainers.Permutation(objetivo, background, seed=seed)
        valores = explainer(x[i : i + 1], max_evals=max_evals).values[0]

        umbral = float(np.abs(valores).max()) * 0.02
        atribuciones = []
        for j, nombre in enumerate(feature_names):
            senal, estadistico = split_feature_name(nombre)
            atribuciones.append(
                SignalAttribution(
                    feature=nombre,
                    signal=senal,
                    statistic=estadistico,
                    importance=float(valores[j]),
                    direction=_direccion(float(valores[j]), umbral),
                    value=float(x[i, j]),
                )
            )

        fila = meta.iloc[i] if meta is not None else None
        resultados.append(
            CaseAttribution(
                explanation_id=f"{model_id}:{case_ids[i]}",
                case_id=case_ids[i],
                model_id=model_id,
                explained_function=FUNCION_EXPLICADA,
                predicted_class=str(clases[indice_clase]),
                confidence=float(probabilidades[i, indice_clase]),
                attributions=tuple(atribuciones),
                session_id=str(fila["session_id"]) if fila is not None else None,
                window_start_s=float(fila["t_start"]) if fila is not None else None,
                window_end_s=float(fila["t_end"]) if fila is not None else None,
                background_hash=background_hash,
                explainer="shap.explainers.Permutation",
                seed=seed,
            )
        )
    return resultados
