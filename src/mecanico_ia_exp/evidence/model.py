"""Modelo de evidencia: observacional, documental y su enlace con las afirmaciones.

Dos clases de evidencia, y ninguna basta sola.

**Observacional.** Procede del vehículo: una señal, en una ventana temporal
concreta, con un valor o un patrón concreto. La produce la cadena
OBD-II → ventanado → descriptores → modelo → atribución.

**Documental.** Procede del corpus: un fragmento con su documento, sección,
página y editor. La produce la recuperación.

La observacional dice **qué se ve en este vehículo**; la documental dice **qué
significa eso**. Una explicación que solo tenga la primera describe sin
interpretar; una que solo tenga la segunda interpreta sin mirar el coche.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EvidenceKind(StrEnum):
    OBSERVATIONAL = "observational"
    DOCUMENTARY = "documentary"


class SupportStatus(StrEnum):
    """Estado de soporte de una afirmación."""

    SUPPORTED = "SUPPORTED"
    """Tiene evidencia y esa evidencia la sostiene."""

    UNSUPPORTED = "UNSUPPORTED"
    """No tiene evidencia que la sostenga."""

    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    """Tiene una de las dos clases de evidencia, no ambas."""

    CONTRADICTED = "CONTRADICTED"
    """La evidencia disponible se opone a lo afirmado."""


@dataclass(frozen=True)
class Observation:
    """Evidencia observacional: una señal, una ventana, un patrón.

    ``observation_id`` es lo que una afirmación cita. Sin él, «los ajustes de
    combustible están elevados» no se puede comprobar contra el dato.
    """

    observation_id: str
    signal: str
    statistic: str
    value: float
    direction: str
    importance: float
    session_id: str | None = None
    window_start_s: float | None = None
    window_end_s: float | None = None
    source: str = "xai"

    def trace(self) -> str:
        """Traza hasta el dato: señal, ventana, valor."""
        ventana = (
            f"ventana {self.window_start_s:.0f}-{self.window_end_s:.0f} s"
            if self.window_start_s is not None and self.window_end_s is not None
            else "ventana no declarada"
        )
        sesion = f"sesión {self.session_id}" if self.session_id else "sesión no declarada"
        return (
            f"{self.observation_id}: {self.signal}.{self.statistic} = {self.value:.4g} "
            f"({self.direction}) · {sesion} · {ventana}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "kind": EvidenceKind.OBSERVATIONAL.value,
            "signal": self.signal,
            "statistic": self.statistic,
            "value": round(self.value, 6),
            "direction": self.direction,
            "importance": round(self.importance, 6),
            "session_id": self.session_id,
            "window_start_s": self.window_start_s,
            "window_end_s": self.window_end_s,
        }


@dataclass(frozen=True)
class DocumentaryEvidence:
    """Evidencia documental: un fragmento con su procedencia completa."""

    chunk_id: str
    document_id: str
    vehicle_id: str
    text: str
    score: float
    applicability: str
    """Grado devuelto por el validador de aplicabilidad al vehículo."""

    authority_level: str | None = None
    document_type: str | None = None
    publisher: str | None = None
    section: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    source_url: str | None = None
    source_file: str | None = None
    dtc_codes: tuple[str, ...] = ()
    engine_codes: tuple[str, ...] = ()

    def trace(self) -> str:
        """Cita completa. Nunca «según el manual» sin decir cuál."""
        partes = [p for p in (self.publisher, self.document_id, self.section) if p]
        if self.page_start is not None:
            partes.append(f"página {self.page_start}")
        partes.append(self.chunk_id)
        if self.source_url:
            partes.append(self.source_url)
        return " · ".join(partes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "kind": EvidenceKind.DOCUMENTARY.value,
            "document_id": self.document_id,
            "vehicle_id": self.vehicle_id,
            "score": round(self.score, 6),
            "applicability": self.applicability,
            "authority_level": self.authority_level,
            "document_type": self.document_type,
            "publisher": self.publisher,
            "section": self.section,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "source_url": self.source_url,
            "dtc_codes": list(self.dtc_codes),
        }


@dataclass
class Claim:
    """Una afirmación atómica con la evidencia que la cita."""

    claim_id: str
    text: str
    observation_ids: tuple[str, ...] = ()
    chunk_ids: tuple[str, ...] = ()
    support_status: SupportStatus = SupportStatus.UNSUPPORTED
    notes: str = ""

    @property
    def has_observational(self) -> bool:
        return bool(self.observation_ids)

    @property
    def has_documentary(self) -> bool:
        return bool(self.chunk_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "observational_evidence": list(self.observation_ids),
            "documentary_evidence": list(self.chunk_ids),
            "support_status": self.support_status.value,
            "notes": self.notes,
        }


@dataclass
class EvidenceBundle:
    """Toda la evidencia reunida para un caso, antes de decidir.

    Es lo que el verificador de suficiencia examina y lo que, si se decide
    explicar, recibe el modelo de lenguaje. El modelo no añade evidencia: la
    redacta.
    """

    case_id: str
    vehicle_id: str
    predicted_class: str
    model_confidence: float
    calibrated_confidence: float | None = None
    observations: list[Observation] = field(default_factory=list)
    documents: list[DocumentaryEvidence] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        """Confianza a usar en el criterio: la calibrada si existe.

        E6 midió que el bosque está infraconfiado --confianza media 0,738 frente
        a 0,878 de acierto--. Un umbral sobre la confianza cruda se abstendría de
        más, así que el criterio usa la calibrada cuando está disponible.
        """
        return (
            self.calibrated_confidence
            if self.calibrated_confidence is not None
            else self.model_confidence
        )

    def applicable_documents(self, grados: frozenset[str]) -> list[DocumentaryEvidence]:
        """Fragmentos cuyo grado de aplicabilidad admite el criterio."""
        return [d for d in self.documents if d.applicability in grados]

    def distinct_sources(self, grados: frozenset[str]) -> set[str]:
        """Documentos distintos entre los aplicables.

        Cinco fragmentos de un mismo documento no son cinco apoyos
        independientes: son el mismo apoyo troceado.
        """
        return {d.document_id for d in self.applicable_documents(grados)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "vehicle_id": self.vehicle_id,
            "predicted_class": self.predicted_class,
            "model_confidence": round(self.model_confidence, 4),
            "calibrated_confidence": (
                round(self.calibrated_confidence, 4)
                if self.calibrated_confidence is not None
                else None
            ),
            "observations": [o.to_dict() for o in self.observations],
            "documents": [d.to_dict() for d in self.documents],
            "claims": [c.to_dict() for c in self.claims],
        }
