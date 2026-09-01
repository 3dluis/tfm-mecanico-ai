"""Perfil del vehículo y validación de aplicabilidad documental.

La pregunta de investigación exige rastrear cada explicación hasta su evidencia.
Una evidencia documental que pertenece a **otro vehículo** no sostiene nada,
aunque su texto sea semánticamente parecido. Este módulo es el que impide esa
confusión.

Un mismo modelo y año puede llevar motores, transmisiones, mercados y
configuraciones de emisiones distintos. «Toyota Corolla 2020» por sí solo no
selecciona un procedimiento de taller.

**Los campos desconocidos permanecen a ``None``.** Nunca se infieren. Un
``engine_code`` inventado convertiría el validador en un generador de falsos
emparejamientos exactos.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Applicability(StrEnum):
    """Grado de correspondencia entre un documento y un vehículo."""

    EXACT_MATCH = "EXACT_MATCH"
    """Coinciden todos los campos comparables y ninguno queda sin comprobar."""

    COMPATIBLE = "COMPATIBLE"
    """Coinciden los campos comprobables; el resto no está declarado en ambos."""

    PARTIAL_MATCH = "PARTIAL_MATCH"
    """Coincide la identidad básica pero difiere algún campo secundario."""

    UNKNOWN = "UNKNOWN"
    """No hay información suficiente para decidir. **No es evidencia válida.**"""

    INCOMPATIBLE = "INCOMPATIBLE"
    """Algún campo identificador difiere. El documento no aplica."""


#: Grados que pueden sostener evidencia sin una justificación explícita adicional.
#: ``COMPATIBLE`` se admite solo bajo política declarada; ``UNKNOWN`` nunca.
GRADOS_FUERTES: frozenset[Applicability] = frozenset({Applicability.EXACT_MATCH})


class VehicleProfile(BaseModel):
    """Identidad técnica de un vehículo.

    Lo que no se sabe se deja en ``None``. El validador trata un ``None`` como
    «sin comprobar», nunca como «coincide».
    """

    vehicle_id: str
    manufacturer: str
    model: str
    model_year: int
    generation: str | None = None
    market: str | None = None
    engine_code: str | None = None
    engine_displacement: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    vin_prefix: str | None = None
    obd_protocol: str | None = None
    notes: str = ""

    #: Campos que identifican al vehículo. Una diferencia en cualquiera de ellos
    #: hace el documento inaplicable.
    IDENTIDAD: tuple[str, ...] = Field(
        default=("manufacturer", "model", "model_year"), exclude=True
    )

    #: Campos que refinan la aplicabilidad dentro de un mismo modelo y año.
    REFINAMIENTO: tuple[str, ...] = Field(
        default=("generation", "market", "engine_code", "transmission"), exclude=True
    )


def _normalizar(valor: object) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip().lower()
    return texto or None


class VehicleApplicabilityValidator:
    """Decide si un documento puede constituir evidencia para un vehículo.

    La comparación es deliberadamente conservadora. Ante la duda devuelve
    ``UNKNOWN``, que **no** es evidencia válida: es mejor abstenerse que sostener
    una explicación sobre documentación de otro coche.
    """

    def __init__(self, vehicle: VehicleProfile) -> None:
        self.vehicle = vehicle

    def validate(self, documento: VehicleProfile) -> Applicability:
        """Compara el vehículo del experimento con el que declara el documento."""
        # Identidad: una diferencia declarada en ambos lados es descalificatoria.
        comprobados = 0
        for campo in self.vehicle.IDENTIDAD:
            propio = _normalizar(getattr(self.vehicle, campo))
            ajeno = _normalizar(getattr(documento, campo))
            if propio is None or ajeno is None:
                continue
            comprobados += 1
            if propio != ajeno:
                return Applicability.INCOMPATIBLE

        if comprobados < len(self.vehicle.IDENTIDAD):
            # Falta parte de la identidad: no se puede afirmar que aplique.
            return Applicability.UNKNOWN

        # Refinamiento: fabricante, modelo y año coinciden. Ahora importa si el
        # documento es para este motor, mercado y transmisión concretos.
        refinados = 0
        for campo in self.vehicle.REFINAMIENTO:
            propio = _normalizar(getattr(self.vehicle, campo))
            ajeno = _normalizar(getattr(documento, campo))
            if propio is None or ajeno is None:
                continue
            refinados += 1
            if propio != ajeno:
                return Applicability.PARTIAL_MATCH

        if refinados == 0:
            # Nada que refinar por ambos lados: coincide lo básico y no consta
            # que difiera nada más. No es coincidencia exacta demostrada.
            return Applicability.COMPATIBLE

        return Applicability.EXACT_MATCH

    def is_strong_evidence(
        self, documento: VehicleProfile, *, allow_compatible: bool = False
    ) -> bool:
        """¿Puede este documento sostener evidencia por sí solo?

        ``allow_compatible`` es la política explícitamente justificada que el
        experimento puede declarar. Por defecto está desactivada: sin ella, solo
        una coincidencia exacta basta.
        """
        grado = self.validate(documento)
        if grado in GRADOS_FUERTES:
            return True
        return allow_compatible and grado is Applicability.COMPATIBLE
