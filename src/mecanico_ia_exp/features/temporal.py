"""Descriptores temporales por ventana.

E4 dejó dos requisitos que este módulo cumple.

**No basta con medias.** Dos de las cinco condiciones no aparecen en el nivel:
la sonda lenta vive en la dispersión y en la frecuencia de conmutación, y el
fallo de encendido en episodios de uno a tres segundos que un promedio disuelve.
Por eso hay extremos, saltos y conteos de eventos, no solo momentos.

**Una pendiente sobre la señal cruda es sobre todo régimen de conducción.** Se
mantiene porque dentro de una ventana corta el perfil varía menos que a lo largo
de una sesión, pero se sabe lo que mide y no se le atribuye más.

El orden de los descriptores es **estable y explícito**. Un orden que dependa de
la iteración de un diccionario convierte un modelo guardado en irrecuperable en
cuanto cambie la versión de Python.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from mecanico_ia_exp.obd.signals import SIGNAL_NAMES

#: Las operaciones de numpy pierden el tipo bajo comprobación estricta; se
#: reafirma en un solo sitio en lugar de silenciar el aviso en cada retorno.
Vector = npt.NDArray[np.float64]


def _f64(valores: object) -> Vector:
    return np.asarray(valores, dtype=np.float64)


#: Estadísticos univariantes, en orden fijo.
ESTADISTICOS: tuple[str, ...] = (
    "mean",
    "std",
    "min",
    "max",
    "range",
    "slope",
    "delta_min",
    "delta_max",
    "n_events",
    "autocorr1",
    "crossings",
)

#: Parejas cuya correlación dentro de la ventana aporta información multivariable.
#: Salen de las relaciones que el motor implementa y que E2 verificó.
PAREJAS: tuple[tuple[str, str], ...] = (
    ("rpm", "maf"),
    ("engine_load", "maf"),
    ("rpm", "vehicle_speed"),
    ("throttle_position", "engine_load"),
    ("engine_load", "coolant_temperature"),
    ("stft_bank1", "ltft_bank1"),
)

#: Cociente entre el caudal medido y el que corresponde al producto régimen x carga.
#:
#: Es un descriptor **informado por la física**: si el caudalímetro subestima, el
#: cociente baja aunque el caudal absoluto siga pareciendo normal. Responde
#: directamente al hallazgo de E4 --la deriva no se ve en el caudal-- y se declara
#: como tal.
#:
#: [VERIFY_ON_REAL_DATA] La constante de proporcionalidad depende del motor. En
#: datos reales habría que comprobar que el cociente sigue siendo estable en
#: condiciones normales antes de usarlo como evidencia.
RATIO_NAME = "maf_over_rpm_load"

FEATURE_NAMES: tuple[str, ...] = (
    tuple(f"{s}_{e}" for s in SIGNAL_NAMES for e in ESTADISTICOS)
    + tuple(f"corr_{a}_{b}" for a, b in PAREJAS)
    + (RATIO_NAME,)
)

_EPS = 1e-9


def _autocorr1(x: Vector) -> Vector:
    """Autocorrelación de retardo 1, por ventana. Mide cuánta inercia tiene la
    señal: una sonda amortiguada la tiene alta, una señal ruidosa baja."""
    a = x[:, :-1]
    b = x[:, 1:]
    a_c = a - a.mean(axis=1, keepdims=True)
    b_c = b - b.mean(axis=1, keepdims=True)
    num = (a_c * b_c).sum(axis=1)
    den = np.sqrt((a_c**2).sum(axis=1) * (b_c**2).sum(axis=1)) + _EPS
    return _f64(num / den)


def _crossings(x: Vector) -> Vector:
    """Cruces por la mediana de la ventana.

    Cuenta con qué frecuencia oscila la señal, independientemente de su
    amplitud. Es el descriptor que distingue una sonda sana de una lenta.
    """
    mediana = np.median(x, axis=1, keepdims=True)
    signos = np.sign(x - mediana)
    return _f64((np.diff(signos, axis=1) != 0).sum(axis=1))


def _n_events(diferencias: Vector) -> Vector:
    """Saltos que se apartan más de tres desviaciones de lo habitual en la ventana.

    Umbral relativo a la propia ventana y no absoluto: un umbral fijo en rpm
    contaría como evento cualquier aceleración en autovía. Así se cuentan
    excursiones anómalas *para ese tramo*, que es lo que un episodio de fallo de
    encendido produce.
    """
    media = diferencias.mean(axis=1, keepdims=True)
    desviacion = diferencias.std(axis=1, keepdims=True) + _EPS
    z = np.abs(diferencias - media) / desviacion
    return _f64((z > 3.0).sum(axis=1))


def _slope(x: Vector) -> Vector:
    """Pendiente de un ajuste lineal, por ventana.

    Se calcula en forma cerrada para las n ventanas a la vez: ajustar una por
    una con polyfit multiplica por cien el tiempo sin cambiar el resultado.
    """
    n = x.shape[1]
    t = np.arange(n, dtype=np.float64)
    t_c = t - t.mean()
    x_c = x - x.mean(axis=1, keepdims=True)
    return _f64((x_c * t_c).sum(axis=1) / ((t_c**2).sum() + _EPS))


def extract_features(x: Vector, signals: tuple[str, ...] = SIGNAL_NAMES) -> Vector:
    """Descriptores de cada ventana.

    Entrada ``(n_ventanas, n_pasos, n_señales)``; salida
    ``(n_ventanas, len(FEATURE_NAMES))`` en el orden de ``FEATURE_NAMES``.
    """
    if x.ndim != 3:
        msg = f"Se esperaban tres dimensiones (ventanas, pasos, señales), no {x.shape}"
        raise ValueError(msg)
    if x.shape[2] != len(signals):
        msg = f"{x.shape[2]} señales en los datos y {len(signals)} declaradas"
        raise ValueError(msg)
    if x.shape[1] < 3:
        msg = f"Una ventana de {x.shape[1]} pasos no admite pendiente ni autocorrelación"
        raise ValueError(msg)

    indice = {nombre: i for i, nombre in enumerate(signals)}
    columnas: list[Vector] = []

    for nombre in signals:
        serie = _f64(x[:, :, indice[nombre]])
        diferencias = _f64(np.diff(serie, axis=1))
        minimo = serie.min(axis=1)
        maximo = serie.max(axis=1)
        # El orden debe coincidir con ESTADISTICOS.
        columnas.extend(
            [
                serie.mean(axis=1),
                serie.std(axis=1),
                minimo,
                maximo,
                maximo - minimo,
                _slope(serie),
                diferencias.min(axis=1),
                diferencias.max(axis=1),
                _n_events(diferencias),
                _autocorr1(serie),
                _crossings(serie),
            ]
        )

    for a, b in PAREJAS:
        sa = _f64(x[:, :, indice[a]])
        sb = _f64(x[:, :, indice[b]])
        a_c = sa - sa.mean(axis=1, keepdims=True)
        b_c = sb - sb.mean(axis=1, keepdims=True)
        num = (a_c * b_c).sum(axis=1)
        den = np.sqrt((a_c**2).sum(axis=1) * (b_c**2).sum(axis=1)) + _EPS
        columnas.append(_f64(num / den))

    rpm = _f64(x[:, :, indice["rpm"]])
    carga = _f64(x[:, :, indice["engine_load"]])
    maf = _f64(x[:, :, indice["maf"]])
    columnas.append(_f64((maf / (rpm * carga + _EPS)).mean(axis=1)))

    matriz = np.column_stack(columnas)
    if matriz.shape[1] != len(FEATURE_NAMES):
        msg = f"Se produjeron {matriz.shape[1]} descriptores y se declaran {len(FEATURE_NAMES)}"
        raise ValueError(msg)
    return _f64(matriz)
