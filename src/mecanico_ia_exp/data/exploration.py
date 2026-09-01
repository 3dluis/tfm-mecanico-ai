"""Análisis exploratorio de las series OBD-II.

Cada función responde a una pregunta concreta sobre los datos. Ninguna produce
gráficas: el cálculo se separa del dibujo para poder comprobar el primero con
tests, que es donde puede haber un error silencioso.

E2 dejó una lección que estructura todo este módulo: dos de las cinco
condiciones de fallo son invisibles en las medias y solo aparecen en la
dispersión o en la frecuencia de eventos. Por eso la separabilidad se mide sobre
**nivel y dispersión por separado**, y no solo sobre el nivel.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from mecanico_ia_exp.obd.faults import NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES


def describe_signals(datos: pd.DataFrame) -> pd.DataFrame:
    """Estadísticos descriptivos por señal."""
    filas: list[dict[str, float | str]] = []
    for nombre in SIGNAL_NAMES:
        serie = datos[nombre]
        filas.append(
            {
                "signal": nombre,
                "n": float(serie.size),
                "missing": float(serie.isna().sum()),
                "mean": float(serie.mean()),
                "std": float(serie.std()),
                "min": float(serie.min()),
                "p25": float(serie.quantile(0.25)),
                "median": float(serie.median()),
                "p75": float(serie.quantile(0.75)),
                "max": float(serie.max()),
            }
        )
    return pd.DataFrame(filas)


def missingness(datos: pd.DataFrame) -> pd.DataFrame:
    """Proporción de valores ausentes por columna.

    En datos sintéticos es cero por construcción, y decirlo importa: los datos
    reales tendrán huecos --tramas perdidas, sensores que no responden-- y un
    pipeline que nunca los ha visto fallará al encontrarlos.
    """
    total = len(datos)
    filas = [
        {
            "column": str(col),
            "missing": float(datos[col].isna().sum()),
            "fraction": float(datos[col].isna().sum()) / total if total else 0.0,
        }
        for col in datos.columns
    ]
    return pd.DataFrame(filas)


def class_balance(datos: pd.DataFrame) -> pd.DataFrame:
    """Sesiones y muestras por condición."""
    agrupado = datos.groupby("fault_id").agg(
        sessions=("session_id", "nunique"),
        samples=("timestamp", "size"),
        active_samples=("fault_active", "sum"),
    )
    resultado = agrupado.reset_index()
    resultado["share"] = resultado["samples"] / resultado["samples"].sum()
    return resultado


def regime_balance(datos: pd.DataFrame) -> pd.DataFrame:
    """Sesiones por régimen de conducción."""
    agrupado = datos.groupby("regime").agg(
        sessions=("session_id", "nunique"), samples=("timestamp", "size")
    )
    return agrupado.reset_index()


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """Tamaño del efecto de Cliff entre dos muestras.

    Mide la probabilidad de que un valor de ``a`` supere a uno de ``b``, menos la
    contraria. Está en [-1, 1]: 0 es solape total, ±1 separación completa.

    Se prefiere a una diferencia de medias estandarizada porque no supone
    normalidad ni varianzas iguales, y aquí ninguna de las dos cosas está
    garantizada: los ajustes de combustible bajo fallo son marcadamente
    asimétricos.

    Implementación por ordenación en O(n log n); la definición ingenua es
    cuadrática y con 20 000 muestras por condición resulta impracticable.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return float("nan")

    b_ordenado = np.sort(b)
    menores = np.searchsorted(b_ordenado, a, side="left")
    menores_o_iguales = np.searchsorted(b_ordenado, a, side="right")
    mayores = b.size - menores_o_iguales
    return float((menores.sum() - mayores.sum()) / (a.size * b.size))


def interpret_delta(delta: float) -> str:
    """Etiqueta cualitativa del tamaño del efecto.

    Los cortes (0,147 / 0,33 / 0,474) son los de uso convencional para el delta
    de Cliff. Son una convención de lectura, no un resultado: se usan para
    ordenar la exposición, nunca para decidir.
    """
    magnitud = abs(delta)
    if np.isnan(delta):
        return "indefinido"
    if magnitud < 0.147:
        return "insignificante"
    if magnitud < 0.33:
        return "pequeño"
    if magnitud < 0.474:
        return "medio"
    return "grande"


@dataclass(frozen=True)
class BlockConfig:
    """Bloques para calcular dispersión.

    El ventanado definitivo se decide en E5 con evidencia. Estos bloques existen
    solo para que el análisis exploratorio pueda medir dispersión, que sobre una
    muestra suelta no está definida.
    """

    length_s: float = 60.0


def block_statistics(datos: pd.DataFrame, config: BlockConfig | None = None) -> pd.DataFrame:
    """Resume cada sesión en bloques consecutivos: media y desviación por señal.

    Los bloques no se solapan y no cruzan sesiones. Ambas cosas importan: el
    solape inflaría artificialmente el número de observaciones independientes, y
    cruzar sesiones mezclaría vehículos distintos.
    """
    cfg = config or BlockConfig()
    trozos: list[pd.DataFrame] = []
    columnas = list(SIGNAL_NAMES)

    for session_id, grupo in datos.groupby("session_id", sort=True):
        bloque = (grupo["timestamp"] // cfg.length_s).astype(int)
        agrupado = grupo.groupby(bloque)
        # Media y desviación se calculan por separado y se nombran de forma
        # explícita: agregarlas a la vez produce columnas de dos niveles que
        # después hay que aplanar, y ese aplanado es una fuente de errores
        # silenciosos en el orden de las columnas.
        medias = agrupado[columnas].mean()
        medias.columns = pd.Index([f"{c}_mean" for c in columnas])
        desviaciones = agrupado[columnas].std()
        desviaciones.columns = pd.Index([f"{c}_std" for c in columnas])

        agregado = pd.concat([medias, desviaciones], axis=1).reset_index(drop=True)
        agregado["session_id"] = session_id
        agregado["fault_id"] = grupo["fault_id"].iloc[0]
        agregado["regime"] = grupo["regime"].iloc[0]
        agregado["fault_active"] = agrupado["fault_active"].max().to_numpy()
        trozos.append(agregado)

    return pd.concat(trozos, ignore_index=True)


def separability(datos: pd.DataFrame, config: BlockConfig | None = None) -> pd.DataFrame:
    """Separabilidad de cada señal frente a la condición normal.

    Devuelve, por condición de fallo y señal, el tamaño del efecto sobre el
    **nivel** (media del bloque) y sobre la **dispersión** (desviación típica del
    bloque). Una señal puede ser inútil en nivel y decisiva en dispersión --es el
    caso de la sonda lambda ante una sonda lenta-- y mirar solo lo primero la
    daría por descartada.
    """
    bloques = block_statistics(datos, config)
    normal = bloques[bloques["fault_id"] == NORMAL_ID]
    filas: list[dict[str, float | str]] = []

    for fault_id in sorted(bloques["fault_id"].unique()):
        if fault_id == NORMAL_ID:
            continue
        con_fallo = bloques[(bloques["fault_id"] == fault_id) & bloques["fault_active"]]
        for señal in SIGNAL_NAMES:
            d_nivel = cliffs_delta(
                con_fallo[f"{señal}_mean"].to_numpy(), normal[f"{señal}_mean"].to_numpy()
            )
            d_disp = cliffs_delta(
                con_fallo[f"{señal}_std"].to_numpy(), normal[f"{señal}_std"].to_numpy()
            )
            filas.append(
                {
                    "fault_id": fault_id,
                    "signal": señal,
                    "delta_level": d_nivel,
                    "delta_dispersion": d_disp,
                    "delta_max_abs": max(abs(d_nivel), abs(d_disp)),
                    "interpretation": interpret_delta(
                        d_nivel if abs(d_nivel) >= abs(d_disp) else d_disp
                    ),
                }
            )
    return pd.DataFrame(filas)


def correlation_matrix(datos: pd.DataFrame) -> pd.DataFrame:
    """Correlación de Spearman entre señales.

    Spearman y no Pearson: varias relaciones del generador son monótonas pero no
    lineales --el régimen salta al cambiar de marcha-- y Pearson las subestima.
    """
    return datos[list(SIGNAL_NAMES)].corr(method="spearman")


def cross_correlation(x: np.ndarray, y: np.ndarray, max_lag: int = 30) -> pd.DataFrame:
    """Correlación cruzada entre dos señales para desfases de -max_lag a +max_lag.

    Un desfase distinto de cero indica que una señal se adelanta a la otra, que
    es lo que distingue una respuesta de una coincidencia.

    Convención: un desfase **positivo** significa que ``y`` va retrasada respecto
    de ``x`` --hay que adelantar ``y`` esa cantidad para alinearlas--. Se declara
    porque el signo es la mitad de la información y la convención contraria es
    igual de común.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size:
        msg = f"Las series deben tener la misma longitud: {x.size} y {y.size}"
        raise ValueError(msg)

    filas: list[dict[str, float]] = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            a, b = x[-lag:], y[: y.size + lag]
        elif lag > 0:
            a, b = x[: x.size - lag], y[lag:]
        else:
            a, b = x, y
        if a.size < 3 or a.std() == 0 or b.std() == 0:
            filas.append({"lag": float(lag), "r": float("nan")})
        else:
            filas.append({"lag": float(lag), "r": float(np.corrcoef(a, b)[0, 1])})
    return pd.DataFrame(filas)


def temporal_drift(datos: pd.DataFrame, signal: str) -> pd.DataFrame:
    """Pendiente de cada señal a lo largo de cada sesión.

    Distingue una condición estable de una que se instala progresivamente. La
    deriva del caudalímetro debería aparecer aquí y la fuga de vacío no.
    """
    filas: list[dict[str, float | str]] = []
    for session_id, grupo in datos.groupby("session_id", sort=True):
        t = grupo["timestamp"].to_numpy(dtype=float)
        v = grupo[signal].to_numpy(dtype=float)
        pendiente = float(np.polyfit(t, v, 1)[0]) if t.size > 2 else float("nan")
        filas.append(
            {
                "session_id": str(session_id),
                "fault_id": str(grupo["fault_id"].iloc[0]),
                "regime": str(grupo["regime"].iloc[0]),
                "signal": signal,
                "slope_per_s": pendiente,
            }
        )
    return pd.DataFrame(filas)


def noise_floor_max_delta(
    x: np.ndarray,
    session_ids: pd.Series,
    *,
    n_repeats: int = 30,
    seed: int = 7,
    quantile: float = 0.9,
) -> float:
    """Suelo de ruido del estadístico «mayor efecto entre muchos descriptores».

    Cuando se busca el descriptor con mayor tamaño de efecto entre cientos, el
    máximo está inflado: con suficientes comparaciones, algo destaca siempre.
    Sin una referencia, un valor moderado se confunde con evidencia.

    Este control lo cuantifica. Parte **solo de la condición normal**, la divide
    en dos mitades **por sesión** y calcula el mismo estadístico. No hay fallo de
    por medio, así que todo lo que salga es ruido. Se repite con particiones
    distintas y se devuelve el cuantil pedido.

    Un efecto observado por debajo de este suelo no es evidencia de nada.

    La partición es por sesión y no por ventana por la misma razón que el reparto
    de E5: dos ventanas de una sesión no son observaciones independientes, y
    partirlas al azar daría un suelo artificialmente bajo.
    """
    sesiones = np.array(sorted(session_ids.unique()))
    if sesiones.size < 2:
        msg = "Hacen falta al menos dos sesiones para construir un control"
        raise ValueError(msg)

    rng = np.random.default_rng(seed)
    maximos: list[float] = []
    for _ in range(n_repeats):
        orden = rng.permutation(sesiones.size)
        mitad = set(sesiones[orden[: sesiones.size // 2]].tolist())
        mascara = session_ids.isin(mitad).to_numpy(dtype=bool)
        if not mascara.any() or mascara.all():
            continue
        a, b = x[mascara], x[~mascara]
        maximos.append(max(abs(cliffs_delta(a[:, j], b[:, j])) for j in range(x.shape[1])))

    return float(np.quantile(maximos, quantile))
