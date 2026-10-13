"""Auditoría del generador: doce comprobaciones antes de entrenar nada.

`synthetic_v3` se generó con el motor sin calibrar y nadie lo notó hasta que una
auditoría posterior comparó el ralentí con el manual. El coste de no haberlo
comprobado el día de la generación fue una conclusión publicada --«el volumen
era la limitación»-- que confundía volumen con calibración del fenómeno y hubo
que retirar.

Estas doce comprobaciones existen para que eso se detecte **antes** de que un
modelo toque el conjunto. Ninguna es sofisticada; la tercera habría bastado.

## Fallo cerrado, y qué significa aquí

Una comprobación que el conjunto no permite realizar --porque le faltan las
columnas de expresión, o porque no hay manifiesto-- se marca `NO_VERIFICABLE` y
**cuenta como fallo**. La alternativa, saltarla, produce un informe en verde que
no dice nada.

Dos de las doce se marcan `INFORMATIVA` a propósito: la expresión efectiva de
los fallos y la variabilidad entre sesiones **se miden y se publican, no se
aprueban**. Un termostato que solo se expresa en una quinta parte de sus
muestras no es un defecto del conjunto: es el fenómeno, y la decisión de qué
hacer con esas ventanas es del protocolo, no de esta auditoría. El usuario pidió
explícitamente que no se eliminen sin más.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from mecanico_ia_exp.obd.engine import _IDLE_RPM, _THERMOSTAT_C
from mecanico_ia_exp.obd.expresion import RATIO_DECLARADO
from mecanico_ia_exp.obd.faults import NORMAL_ID
from mecanico_ia_exp.obd.signals import COLUMNAS_DE_EXPRESION, SIGNAL_NAMES, SIGNALS_BY_NAME

PASS = "PASS"
FALLA = "FALLA"
NO_VERIFICABLE = "NO_VERIFICABLE"
INFORMATIVA = "INFORMATIVA"

#: Ralentí documentado del Z6 con transmisión manual, del manual de taller
#: (`configs/calibracion_mazda3_bk.yaml`, srvc/B3E011002000W01.pdf).
RALENTI_DOCUMENTADO = (640.0, 740.0)

#: Apertura del termostato documentada: 80-84 °C (srvc/B3E010002000T03.pdf).
TERMOSTATO_DOCUMENTADO = (80.0, 84.0)


class AuditoriaDelGeneradorError(RuntimeError):
    """El conjunto generado no pasa la auditoría y no se usa para entrenar."""


@dataclass(frozen=True)
class Comprobacion:
    """Una comprobación con su estado y el detalle que la justifica."""

    numero: int
    nombre: str
    estado: str
    detalle: str

    @property
    def bloquea(self) -> bool:
        """Las informativas no bloquean; las no verificables sí."""
        return self.estado in (FALLA, NO_VERIFICABLE)

    def __str__(self) -> str:
        return f"[{self.estado:14s}] {self.numero:2d}. {self.nombre} — {self.detalle}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": self.numero,
            "check": self.nombre,
            "status": self.estado,
            "detail": self.detalle,
        }


# ------------------------------------------------------------------ las doce


def _c1_coherencia_fisica(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    fuera: list[str] = []
    for nombre in SIGNAL_NAMES:
        spec = SIGNALS_BY_NAME[nombre]
        serie = datos[nombre]
        n = int(((serie < spec.minimum) | (serie > spec.maximum)).sum())
        if n:
            fuera.append(f"{nombre} ({n})")
    if fuera:
        return Comprobacion(1, "coherencia física", FALLA, f"fuera de rango: {', '.join(fuera)}")
    return Comprobacion(
        1, "coherencia física", PASS, f"las {len(SIGNAL_NAMES)} señales dentro de su rango"
    )


def _c2_rangos_documentados(
    datos: pd.DataFrame, _manifiesto: dict[str, Any] | None
) -> Comprobacion:
    """El ralentí sin fallo dentro del rango del manual.

    Es la comprobación que habría detectado el problema de `v3` el día que se
    generó. Se mide sobre las muestras **sin fallo** con el vehículo parado, que
    es la condición en que el manual define el ralentí.
    """
    sanas = datos[datos["fault_id"] == NORMAL_ID]
    ralenti = sanas.loc[sanas["vehicle_speed"] < 2.0, "rpm"]
    if ralenti.empty:
        return Comprobacion(
            2, "rangos documentados", NO_VERIFICABLE, "ninguna muestra sana con el vehículo parado"
        )
    bajo, alto = RALENTI_DOCUMENTADO
    mediana = float(ralenti.median())
    p5, p95 = (float(x) for x in ralenti.quantile([0.05, 0.95]))
    detalle = (
        f"ralentí sano: mediana {mediana:.1f}, p5 {p5:.1f}, p95 {p95:.1f} rpm "
        f"(manual {bajo:.0f}-{alto:.0f}; constante del motor {_IDLE_RPM:.1f})"
    )
    if not bajo <= mediana <= alto:
        return Comprobacion(2, "rangos documentados", FALLA, detalle)
    techo = float(sanas["coolant_temperature"].max())
    if techo > TERMOSTATO_DOCUMENTADO[1] + 5.0:
        return Comprobacion(
            2,
            "rangos documentados",
            FALLA,
            f"{detalle}; refrigerante sano hasta {techo:.1f} °C, por encima del termostato "
            f"documentado ({_THERMOSTAT_C:.1f})",
        )
    return Comprobacion(2, "rangos documentados", PASS, detalle)


#: Relaciones que el motor construye a propósito y cuyo signo tiene que
#: aparecer: sin ellas el conjunto no tendría estructura que aprender.
RELACIONES_ESPERADAS: tuple[tuple[str, str, float], ...] = (
    ("rpm", "maf", 0.5),
    ("engine_load", "map", 0.5),
    ("vehicle_speed", "rpm", 0.5),
    ("engine_load", "throttle_position", 0.5),
)


def _c3_relaciones(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    sanas = datos[datos["fault_id"] == NORMAL_ID]
    if len(sanas) < 100:
        return Comprobacion(3, "relaciones entre señales", NO_VERIFICABLE, "muy pocas sanas")
    flojas: list[str] = []
    medidas: list[str] = []
    for a, b, minimo in RELACIONES_ESPERADAS:
        r = float(sanas[a].corr(sanas[b]))
        medidas.append(f"{a}~{b} {r:+.2f}")
        if not np.isfinite(r) or r < minimo:
            flojas.append(f"{a}~{b} {r:+.2f} < {minimo}")
    if flojas:
        return Comprobacion(3, "relaciones entre señales", FALLA, "; ".join(flojas))
    return Comprobacion(3, "relaciones entre señales", PASS, "; ".join(medidas))


def _c4_continuidad(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    problemas: list[str] = []
    for session_id, grupo in datos.groupby("session_id", sort=True):
        t = grupo["timestamp"].to_numpy(dtype=float)
        if not np.all(np.diff(t) > 0):
            problemas.append(f"{session_id}: tiempo no creciente")
            continue
        pasos = np.diff(t)
        if pasos.size and not np.allclose(pasos, pasos[0]):
            problemas.append(f"{session_id}: paso irregular")
    if problemas:
        return Comprobacion(4, "continuidad temporal", FALLA, "; ".join(problemas[:3]))
    return Comprobacion(
        4,
        "continuidad temporal",
        PASS,
        f"{datos['session_id'].nunique()} sesiones con tiempo creciente y paso constante",
    )


def _c5_frecuencia(datos: pd.DataFrame, manifiesto: dict[str, Any] | None) -> Comprobacion:
    pasos = {
        float(np.diff(g["timestamp"].to_numpy(dtype=float))[0])
        for _, g in datos.groupby("session_id", sort=True)
        if len(g) > 1
    }
    if len(pasos) != 1:
        return Comprobacion(
            5, "frecuencia de muestreo", FALLA, f"{len(pasos)} pasos distintos: {sorted(pasos)[:4]}"
        )
    observada = 1.0 / pasos.pop()
    if manifiesto is None:
        return Comprobacion(
            5, "frecuencia de muestreo", NO_VERIFICABLE, f"observada {observada} Hz, sin manifiesto"
        )
    declarada = float(manifiesto["sampling_rate_hz"])
    if abs(observada - declarada) > 1e-9:
        return Comprobacion(
            5,
            "frecuencia de muestreo",
            FALLA,
            f"declarada {declarada} Hz, observada {observada} Hz",
        )
    return Comprobacion(5, "frecuencia de muestreo", PASS, f"{observada} Hz, igual a la declarada")


def _c6_calentamiento(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    """En calentamiento sin fallo el refrigerante tiene que subir.

    Es la premisa de la que depende todo el análisis del termostato: si en una
    sesión sana de calentamiento la temperatura no sube, el fallo no tiene nada
    que impedir y la condición no es observable por motivos del generador.
    """
    sanas = datos[(datos["fault_id"] == NORMAL_ID) & (datos["regime"] == "warmup")]
    if sanas.empty:
        return Comprobacion(
            6,
            "evolución en calentamiento",
            NO_VERIFICABLE,
            "sin sesiones sanas de calentamiento",
        )
    subidas: list[float] = []
    for _, grupo in sanas.groupby("session_id", sort=True):
        serie = grupo.sort_values("timestamp")["coolant_temperature"].to_numpy(dtype=float)
        subidas.append(float(serie[-1] - serie[0]))
    menor = min(subidas)
    detalle = (
        f"{len(subidas)} sesiones sanas de calentamiento; subida de {menor:+.1f} a "
        f"{max(subidas):+.1f} °C"
    )
    if menor <= 0.0:
        return Comprobacion(6, "evolución en calentamiento", FALLA, detalle)
    return Comprobacion(6, "evolución en calentamiento", PASS, detalle)


def _c7_variabilidad(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    """Dos sesiones de la misma condición y régimen no pueden ser iguales.

    Si lo fueran, la semilla por sesión no estaría entrando y el conjunto
    tendría menos información de la que su número de sesiones sugiere.
    """
    iguales: list[str] = []
    resumenes: dict[tuple[str, str], list[tuple[str, tuple[float, ...]]]] = {}
    for session_id, grupo in datos.groupby("session_id", sort=True):
        clave = (str(grupo["fault_id"].iloc[0]), str(grupo["regime"].iloc[0]))
        firma = tuple(round(float(grupo[s].mean()), 9) for s in SIGNAL_NAMES)
        resumenes.setdefault(clave, []).append((str(session_id), firma))
    for clave, lista in resumenes.items():
        firmas = [f for _, f in lista]
        if len(set(firmas)) != len(firmas):
            iguales.append(f"{clave[0]}/{clave[1]}")
    if iguales:
        return Comprobacion(
            7, "variabilidad entre sesiones", FALLA, f"sesiones idénticas en: {', '.join(iguales)}"
        )
    grupos = len(resumenes)
    return Comprobacion(
        7,
        "variabilidad entre sesiones",
        INFORMATIVA,
        f"ninguna sesión repetida en {grupos} grupos condición/régimen; "
        f"{datos['session_id'].nunique()} sesiones distintas",
    )


def _c8_expresion(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    """Qué fracción de las muestras activas alteró de verdad la trayectoria.

    **Se mide y se publica; no se aprueba.** Una condición que se exprese poco no
    es un defecto: es el fenómeno. Lo que sería un defecto es tratar la etiqueta
    como prueba de que el fallo se manifestó, y para impedirlo basta tener la
    cifra delante.
    """
    faltan = [c for c in COLUMNAS_DE_EXPRESION if c not in datos.columns]
    if faltan:
        return Comprobacion(
            8, "expresión efectiva de los fallos", NO_VERIFICABLE, f"faltan las columnas {faltan}"
        )
    sanas_expresadas = int(datos.loc[datos["fault_id"] == NORMAL_ID, "fault_expressed"].sum())
    if sanas_expresadas:
        return Comprobacion(
            8,
            "expresión efectiva de los fallos",
            FALLA,
            f"{sanas_expresadas} muestras sanas marcadas como expresadas",
        )
    inactivas = int(datos.loc[~datos["fault_active"], "fault_expressed"].sum())
    if inactivas:
        return Comprobacion(
            8,
            "expresión efectiva de los fallos",
            FALLA,
            f"{inactivas} muestras con el fallo inactivo marcadas como expresadas",
        )
    activas = datos[datos["fault_active"]]
    if activas.empty:
        return Comprobacion(
            8, "expresión efectiva de los fallos", NO_VERIFICABLE, "ninguna muestra activa"
        )
    por_fallo = activas.groupby("fault_id")["fault_expressed"].agg(["sum", "size"])
    partes = [
        f"{str(fid).split('_', 1)[0]} {int(fila['sum'])}/{int(fila['size'])}"
        f" ({fila['sum'] / fila['size']:.0%})"
        for fid, fila in por_fallo.iterrows()
    ]
    return Comprobacion(
        8, "expresión efectiva de los fallos", INFORMATIVA, "expresadas: " + ", ".join(partes)
    )


def _c9_sin_delator(datos: pd.DataFrame, _manifiesto: dict[str, Any] | None) -> Comprobacion:
    """Ninguna señal, por sí sola y con un umbral, debe separar perfectamente.

    Una señal delatora convertiría el problema en trivial y la comparación entre
    representaciones en un artefacto del generador. Se busca el peor caso: para
    cada señal y cada condición, la mejor regla de un solo umbral.
    """
    etiquetas = datos["fault_id"].to_numpy()
    condiciones = [c for c in np.unique(etiquetas) if c != NORMAL_ID]
    if not condiciones:
        return Comprobacion(9, "sin señal delatora", NO_VERIFICABLE, "no hay condiciones de fallo")
    delatoras: list[str] = []
    for nombre in SIGNAL_NAMES:
        valores = datos[nombre].to_numpy(dtype=float)
        for condicion in condiciones:
            es = etiquetas == condicion
            dentro, fuera = valores[es], valores[~es]
            if dentro.size == 0 or fuera.size == 0:
                continue
            # Un umbral que separe perfectamente existe si y solo si los rangos
            # de las dos clases son disjuntos. Comprobarlo cuesta dos extremos.
            if dentro.min() > fuera.max() or dentro.max() < fuera.min():
                delatoras.append(f"{nombre} separa {condicion}")
    if delatoras:
        return Comprobacion(
            9,
            "sin señal delatora",
            FALLA,
            f"{len(delatoras)} señal(es) delatora(s) con un solo umbral: {delatoras[:3]}",
        )
    return Comprobacion(
        9,
        "sin señal delatora",
        PASS,
        f"ninguna de las {len(SIGNAL_NAMES)} señales separa por sí sola ninguna de las "
        f"{len(condiciones)} condiciones",
    )


def _c10_independencia(datos: pd.DataFrame, manifiesto: dict[str, Any] | None) -> Comprobacion:
    """Ninguna sesión puede aparecer dos veces.

    El reparto entre particiones se audita aparte, con `audit_split`; lo que
    aquí se comprueba es la premisa de la que ese reparto depende: que la sesión
    sea de verdad la unidad, es decir que su identificador sea único y que todas
    sus muestras lleven la misma condición y el mismo régimen.
    """
    mezcladas: list[str] = []
    for session_id, grupo in datos.groupby("session_id", sort=True):
        if grupo["fault_id"].nunique() != 1 or grupo["regime"].nunique() != 1:
            mezcladas.append(str(session_id))
    if mezcladas:
        return Comprobacion(
            10,
            "independencia por sesión",
            FALLA,
            f"{len(mezcladas)} sesión(es) con más de una condición o régimen: {mezcladas[:3]}",
        )
    n = datos["session_id"].nunique()
    if manifiesto is not None and int(manifiesto["n_sessions"]) != n:
        return Comprobacion(
            10,
            "independencia por sesión",
            FALLA,
            f"el manifiesto declara {manifiesto['n_sessions']} sesiones y hay {n}",
        )
    return Comprobacion(
        10, "independencia por sesión", PASS, f"{n} sesiones, cada una de una sola condición"
    )


def _c11_procedencia(datos: pd.DataFrame, manifiesto: dict[str, Any] | None) -> Comprobacion:
    if manifiesto is None:
        return Comprobacion(11, "procedencia por sesión", NO_VERIFICABLE, "sin manifiesto")
    fichadas = {str(f["session_id"]) for f in manifiesto["sessions"]}
    presentes = {str(s) for s in datos["session_id"].unique()}
    if faltan := presentes - fichadas:
        return Comprobacion(
            11,
            "procedencia por sesión",
            FALLA,
            f"{len(faltan)} sesión(es) sin ficha: {sorted(faltan)[:3]}",
        )
    if sobran := fichadas - presentes:
        return Comprobacion(
            11,
            "procedencia por sesión",
            FALLA,
            f"{len(sobran)} ficha(s) sin datos: {sorted(sobran)[:3]}",
        )
    huellas = manifiesto["generator"].get("source_fingerprints_16") or {}
    if not huellas:
        return Comprobacion(
            11, "procedencia por sesión", FALLA, "el manifiesto no lleva huellas del generador"
        )
    return Comprobacion(
        11,
        "procedencia por sesión",
        PASS,
        f"{len(fichadas)} fichas con semilla y parámetros, y {len(huellas)} huellas del generador",
    )


def _c12_reproducibilidad(datos: pd.DataFrame, manifiesto: dict[str, Any] | None) -> Comprobacion:
    """Regenera una sesión **con fallo** desde su ficha y la compara entera.

    Es la comprobación que da sentido al manifiesto: si de la ficha no sale la
    misma serie, el fichero no documenta la procedencia aunque lo diga su
    nombre.

    Dos decisiones que no son obvias:

    * Se regenera **una sesión con fallo**, no la primera por orden. En un plan
      equilibrado la primera por orden es una sesión sana, y una sesión sana no
      ejercita nada de lo que puede estar mal: su expresión es cero por
      construcción y sus parámetros de fallo están vacíos.
    * Se comparan también las **columnas de expresión**. Comparar solo las doce
      señales dejaría pasar una anotación de expresión incorrecta con los
      valores intactos, y la comprobación 8 no la detectaría porque es
      informativa y no aprobatoria.

    Dentro de las sesiones con fallo se toma la **primera por orden**, para que
    el resultado de la auditoría sea él mismo reproducible.
    """
    if manifiesto is None:
        return Comprobacion(12, "reproducibilidad exacta", NO_VERIFICABLE, "sin manifiesto")
    from mecanico_ia_exp.obd.procedencia import reconstruir
    from mecanico_ia_exp.obd.synthetic import generate_session

    con_fallo = sorted(
        str(f["session_id"]) for f in manifiesto["sessions"] if f["fault_id"] != NORMAL_ID
    )
    if not con_fallo:
        return Comprobacion(
            12,
            "reproducibilidad exacta",
            NO_VERIFICABLE,
            "el manifiesto no tiene sesiones con fallo",
        )
    session_id = con_fallo[0]
    spec = reconstruir(manifiesto, session_id)
    ratio = float(manifiesto.get("expression", {}).get("ratio_declarado", RATIO_DECLARADO))
    regenerada = generate_session(spec, ratio_expresion=ratio)
    original = datos[datos["session_id"] == session_id].sort_values("timestamp")
    if len(original) != len(regenerada):
        return Comprobacion(
            12,
            "reproducibilidad exacta",
            FALLA,
            f"{session_id}: {len(original)} muestras guardadas y {len(regenerada)} regeneradas",
        )
    a = original[list(SIGNAL_NAMES)].to_numpy(dtype=float)
    b = regenerada[list(SIGNAL_NAMES)].to_numpy(dtype=float)
    if not np.array_equal(a, b):
        return Comprobacion(
            12,
            "reproducibilidad exacta",
            FALLA,
            f"{session_id}: la serie regenerada difiere, máximo {np.abs(a - b).max():.3g}",
        )

    columnas_expresion = [c for c in COLUMNAS_DE_EXPRESION if c in original.columns]
    if not columnas_expresion:
        return Comprobacion(
            12,
            "reproducibilidad exacta",
            NO_VERIFICABLE,
            f"{session_id}: las doce señales coinciden, pero el conjunto no trae las "
            "columnas de expresión y no se pueden comparar",
        )
    discrepantes = [
        columna
        for columna in columnas_expresion
        if not np.array_equal(original[columna].to_numpy(), regenerada[columna].to_numpy())
    ]
    if discrepantes:
        return Comprobacion(
            12,
            "reproducibilidad exacta",
            FALLA,
            f"{session_id}: las señales coinciden pero la anotación de expresión no: "
            f"{discrepantes}",
        )
    return Comprobacion(
        12,
        "reproducibilidad exacta",
        PASS,
        f"{session_id} ({spec.fault_id}) regenerada desde su ficha: idéntica bit a bit en "
        f"{len(original)} muestras, señales y expresión",
    )


COMPROBACIONES: tuple[Callable[[pd.DataFrame, dict[str, Any] | None], Comprobacion], ...] = (
    _c1_coherencia_fisica,
    _c2_rangos_documentados,
    _c3_relaciones,
    _c4_continuidad,
    _c5_frecuencia,
    _c6_calentamiento,
    _c7_variabilidad,
    _c8_expresion,
    _c9_sin_delator,
    _c10_independencia,
    _c11_procedencia,
    _c12_reproducibilidad,
)


def auditar(datos: pd.DataFrame, manifiesto: dict[str, Any] | None = None) -> list[Comprobacion]:
    """Pasa las doce comprobaciones y devuelve todas, también las que pasan."""
    return [comprobacion(datos, manifiesto) for comprobacion in COMPROBACIONES]


def exigir_auditoria_limpia(
    datos: pd.DataFrame, manifiesto: dict[str, Any] | None = None
) -> list[Comprobacion]:
    """Se detiene si alguna comprobación falla o no se puede verificar."""
    informe = auditar(datos, manifiesto)
    bloquean = [c for c in informe if c.bloquea]
    if bloquean:
        listado = "\n".join(f"  {c}" for c in bloquean)
        msg = f"{len(bloquean)} de {len(informe)} comprobaciones del generador no pasan:\n{listado}"
        raise AuditoriaDelGeneradorError(msg)
    return informe
