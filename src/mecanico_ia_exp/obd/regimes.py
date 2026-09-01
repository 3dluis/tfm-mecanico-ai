"""Regímenes de conducción.

Un régimen es una secuencia de fases, cada una con una velocidad objetivo y una
duración media. La duración real se perturba por semilla, de modo que dos
sesiones del mismo régimen no son copias la una de la otra: si lo fueran, el
modelo aprendería a reconocer la sesión en lugar del comportamiento.

Procedencia: los perfiles derivan de los del proyecto de ingeniería hermano,
ampliados aquí con los regímenes de aceleración y deceleración sostenidas que el
análisis de transitorios necesita.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Phase:
    """Tramo de un perfil de conducción."""

    name: str
    target_speed_kmh: float
    mean_duration_s: float


@dataclass(frozen=True)
class Regime:
    """Perfil completo, con la temperatura inicial de refrigerante que implica."""

    name: str
    phases: tuple[Phase, ...]
    initial_coolant_c: float | None = None
    """``None`` = motor ya caliente. Un valor = arranque desde esa temperatura."""


REGIMES: dict[str, Regime] = {
    "idle": Regime(
        name="idle",
        phases=(Phase("idle", 0.0, 120.0),),
    ),
    "urban": Regime(
        name="urban",
        phases=(
            Phase("idle", 0.0, 25.0),
            Phase("accel", 45.0, 15.0),
            Phase("cruise", 45.0, 40.0),
            Phase("decel", 0.0, 10.0),
        ),
    ),
    "highway": Regime(
        name="highway",
        phases=(
            Phase("accel", 110.0, 30.0),
            Phase("cruise", 110.0, 180.0),
            Phase("vary", 95.0, 60.0),
            Phase("cruise", 115.0, 120.0),
        ),
    ),
    "warmup": Regime(
        name="warmup",
        phases=(
            Phase("idle", 0.0, 60.0),
            Phase("accel", 40.0, 20.0),
            Phase("cruise", 40.0, 60.0),
            Phase("decel", 0.0, 12.0),
        ),
        initial_coolant_c=None,  # se sustituye por la ambiente en el motor
    ),
    "acceleration": Regime(
        name="acceleration",
        phases=(
            Phase("idle", 0.0, 8.0),
            Phase("accel", 120.0, 45.0),
            Phase("cruise", 120.0, 20.0),
        ),
    ),
    "deceleration": Regime(
        name="deceleration",
        phases=(
            Phase("cruise", 110.0, 25.0),
            Phase("decel", 0.0, 30.0),
            Phase("idle", 0.0, 20.0),
        ),
    ),
}

REGIME_NAMES: tuple[str, ...] = tuple(REGIMES)

#: El régimen de calentamiento arranca frío; los demás, con el motor en régimen.
COLD_START_REGIMES: frozenset[str] = frozenset({"warmup"})
