"""Contrato de salida del agente.

El modelo de lenguaje **redacta y organiza**; no decide si hay evidencia
suficiente ni inventa de dónde sale. Su salida se valida contra este esquema, y
cada referencia se comprueba después contra lo que realmente se recuperó.

Dos formas posibles, y ninguna más:

- ``EXPLAIN`` con afirmaciones, cada una con sus referencias.
- ``ABSTAIN`` con el motivo y qué evidencia faltó.

Que la abstención sea una **forma válida del esquema** y no un error de
generación es deliberado: si el modelo solo pudiera producir explicaciones,
abstenerse le exigiría desobedecer el formato.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Decision(StrEnum):
    EXPLAIN = "EXPLAIN"
    ABSTAIN = "ABSTAIN"


class AbstainReason(StrEnum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_APPLICABLE_DOCUMENTATION = "NO_APPLICABLE_DOCUMENTATION"
    CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"
    LOW_MODEL_CONFIDENCE = "LOW_MODEL_CONFIDENCE"


class GeneratedClaim(BaseModel):
    """Una afirmación con las referencias que el modelo dice que la sostienen.

    Que las cite no significa que existan: eso se comprueba aparte, contra el
    conjunto realmente recuperado. Es la comprobación que impide que una cita
    inventada pase por buena.
    """

    claim_id: str = Field(pattern=r"^C\d{2}$")
    text: str = Field(min_length=10, max_length=600)
    observational_evidence: list[str] = Field(default_factory=list)
    documentary_evidence: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def _sin_lenguaje_causal_no_sostenido(cls, valor: str) -> str:
        """Rechaza afirmaciones que declaran causa demostrada.

        La cadena OBD-II → modelo → atribución sostiene **observaciones**, no
        causas. «Los ajustes están desplazados» es lo que la evidencia permite;
        «hay una fuga de vacío» sería atribuir causalidad a una atribución, y E9
        dejó por escrito que eso no se hace.

        No se corrige el texto: se rechaza, para que el fallo se vea.
        """
        prohibidas = (
            "está causado por",
            "la causa es",
            "se debe a que",
            "demuestra que",
            "prueba que",
            "is caused by",
            "proves that",
        )
        minuscula = valor.lower()
        for frase in prohibidas:
            if frase in minuscula:
                msg = (
                    f"la afirmación declara causa demostrada ({frase!r}); "
                    "la evidencia disponible sostiene observaciones, no causas"
                )
                raise ValueError(msg)
        return valor


class ExplainOutput(BaseModel):
    """El agente explica."""

    decision: Decision = Decision.EXPLAIN
    diagnosis: str = Field(min_length=3, max_length=200)
    confidence: float = Field(ge=0.0, le=1.0)
    claims: list[GeneratedClaim] = Field(min_length=1)
    limitations: list[str] = Field(default_factory=list)

    @field_validator("claims")
    @classmethod
    def _identificadores_unicos(cls, valor: list[GeneratedClaim]) -> list[GeneratedClaim]:
        ids = [c.claim_id for c in valor]
        if len(set(ids)) != len(ids):
            msg = "hay identificadores de afirmación repetidos"
            raise ValueError(msg)
        return valor


class AbstainOutput(BaseModel):
    """El agente se abstiene. **No es un error**: es una salida correcta."""

    decision: Decision = Decision.ABSTAIN
    reason: AbstainReason
    missing_evidence: list[str] = Field(default_factory=list)
    notes: str = ""


AgentOutput = ExplainOutput | AbstainOutput


class FakeCitationError(ValueError):
    """El modelo citó una referencia que no estaba en lo recuperado."""


def verify_citations(
    salida: AgentOutput,
    *,
    available_chunks: set[str],
    available_observations: set[str],
) -> list[str]:
    """Comprueba que toda referencia existe en lo que se le entregó al modelo.

    Es la barrera contra la cita inventada. Un modelo puede producir un
    identificador con la forma correcta que no corresponde a nada: se parece a
    una cita, resuelve a la nada, y sin esta comprobación pasaría por buena.

    Devuelve las referencias inexistentes. Vacío significa que todas resuelven.
    """
    if isinstance(salida, AbstainOutput):
        return []

    inventadas: list[str] = []
    for claim in salida.claims:
        for ref in claim.documentary_evidence:
            if ref not in available_chunks:
                inventadas.append(f"{claim.claim_id} cita el fragmento inexistente {ref}")
        for ref in claim.observational_evidence:
            if ref not in available_observations:
                inventadas.append(f"{claim.claim_id} cita la observación inexistente {ref}")
    return inventadas
