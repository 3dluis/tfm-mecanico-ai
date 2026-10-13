"""Ventanado de las series OBD-II.

Una **ventana** es la unidad que ve el modelo: un tramo contiguo de una sesión.
Dos reglas la gobiernan, y ninguna es negociable.

**Una ventana nunca cruza una sesión.** Dos sesiones son vehículos o trayectos
distintos; una ventana a caballo entre ambas describiría algo que no ocurrió.

**Una ventana nunca cruza la entrada del fallo.** Un tramo mitad normal y mitad
averiado no pertenece a ninguna de las dos clases. Etiquetarlo por mayoría
introduciría ruido en las etiquetas justo en la transición, que es la zona donde
el modelo más se juega. Se descartan, y se cuenta cuántos: un descarte silencioso
es una pérdida de datos que nadie audita.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from mecanico_ia_exp.obd.faults import NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES


@dataclass(frozen=True)
class WindowConfig:
    """Geometría del ventanado."""

    length_s: float = 60.0
    stride_s: float = 30.0
    sample_rate_hz: float = 1.0

    def __post_init__(self) -> None:
        if self.length_s <= 0 or self.stride_s <= 0:
            msg = "Longitud y paso deben ser positivos"
            raise ValueError(msg)
        if self.stride_s > self.length_s:
            msg = (
                f"Un paso ({self.stride_s} s) mayor que la ventana ({self.length_s} s) "
                "dejaría huecos sin observar"
            )
            raise ValueError(msg)

    @property
    def n_steps(self) -> int:
        """Muestras por ventana."""
        return round(self.length_s * self.sample_rate_hz)

    @property
    def stride_steps(self) -> int:
        return round(self.stride_s * self.sample_rate_hz)

    @property
    def overlap_fraction(self) -> float:
        """Solape entre ventanas consecutivas.

        Importa al leer las métricas: con solape, dos ventanas contiguas
        comparten información y no son observaciones independientes.
        """
        return 1.0 - self.stride_s / self.length_s


@dataclass(frozen=True)
class WindowedData:
    """Ventanas, etiquetas y su procedencia.

    ``meta`` conserva de qué sesión sale cada ventana. Sin eso no se puede hacer
    un reparto sin fuga, ni rastrear una predicción hasta su origen.
    """

    x: np.ndarray
    """(n_ventanas, n_pasos, n_señales)"""
    y: np.ndarray
    """(n_ventanas,) — identificador de condición"""
    meta: pd.DataFrame
    """(n_ventanas, ...) — session_id, regime, t_start, t_end, fault_active y, si el
    conjunto las trae, ``n_expressed``, ``fraction_expressed``, ``fault_expressed``
    y ``deviation_max``: cuántas muestras de la ventana alteraron de verdad la
    trayectoria. Ninguna ventana se descarta por no expresar el fallo."""
    signals: tuple[str, ...]
    config: WindowConfig
    n_discarded: int
    """Ventanas descartadas por cruzar la entrada del fallo."""

    def __len__(self) -> int:
        return int(self.x.shape[0])


def make_windows(datos: pd.DataFrame, config: WindowConfig | None = None) -> WindowedData:
    """Trocea las series en ventanas etiquetadas."""
    cfg = config or WindowConfig()
    n_pasos, paso = cfg.n_steps, cfg.stride_steps
    columnas = list(SIGNAL_NAMES)

    bloques: list[np.ndarray] = []
    etiquetas: list[str] = []
    filas_meta: list[dict[str, object]] = []
    descartadas = 0

    for session_id, grupo in datos.groupby("session_id", sort=True):
        grupo = grupo.sort_values("timestamp")
        valores = grupo[columnas].to_numpy(dtype=np.float32)
        activo = grupo["fault_active"].to_numpy(dtype=bool)
        tiempos = grupo["timestamp"].to_numpy(dtype=float)
        # La expresión efectiva solo existe desde `synthetic_v4`. Cuando está,
        # cada ventana se queda con qué fracción de sus muestras alteró de
        # verdad la trayectoria. **No se descarta ninguna por eso**: una ventana
        # etiquetada con el fallo y sin señal observable es un caso del
        # análisis, no un dato defectuoso, y eliminarla aquí la escondería.
        expresado = (
            grupo["fault_expressed"].to_numpy(dtype=bool)
            if "fault_expressed" in grupo.columns
            else None
        )
        desviacion = (
            grupo["fault_deviation_max"].to_numpy(dtype=float)
            if "fault_deviation_max" in grupo.columns
            else None
        )
        fault_id = str(grupo["fault_id"].iloc[0])
        regime = str(grupo["regime"].iloc[0])

        for inicio in range(0, valores.shape[0] - n_pasos + 1, paso):
            fin = inicio + n_pasos
            tramo_activo = activo[inicio:fin]

            # La ventana debe ser homogénea: enteramente normal o enteramente
            # bajo la condición. Si mezcla, no pertenece a ninguna clase.
            if tramo_activo.any() and not tramo_activo.all():
                descartadas += 1
                continue

            bloques.append(valores[inicio:fin])
            etiquetas.append(fault_id if tramo_activo.all() else NORMAL_ID)
            fila: dict[str, object] = {
                "session_id": session_id,
                "regime": regime,
                "session_fault_id": fault_id,
                "t_start": float(tiempos[inicio]),
                "t_end": float(tiempos[fin - 1]),
                "fault_active": bool(tramo_activo.all()),
            }
            if expresado is not None:
                tramo = expresado[inicio:fin]
                fila["n_expressed"] = int(tramo.sum())
                fila["fraction_expressed"] = float(tramo.mean())
                fila["fault_expressed"] = bool(tramo.any())
            if desviacion is not None:
                fila["deviation_max"] = float(desviacion[inicio:fin].max())
            filas_meta.append(fila)

    if not bloques:
        msg = (
            f"Ninguna ventana de {cfg.length_s} s cabe en las sesiones; "
            "revisa la duración de las sesiones o la longitud de ventana"
        )
        raise ValueError(msg)

    return WindowedData(
        x=np.stack(bloques),
        y=np.array(etiquetas, dtype=object),
        meta=pd.DataFrame(filas_meta),
        signals=SIGNAL_NAMES,
        config=cfg,
        n_discarded=descartadas,
    )
