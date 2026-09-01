"""Verificación del soporte: ¿el fragmento citado sostiene lo afirmado?

**Citar no es sostener.** Una afirmación puede llevar una referencia que existe,
resuelve y pertenece al vehículo correcto, y aun así no decir nada sobre lo que
se afirma. Es el fallo más difícil de ver a simple vista, porque el texto
resultante parece impecable, y es el que la pregunta de investigación interroga.

La comprobación es **determinista**: no interviene ningún modelo de lenguaje. Se
apoya en que el manual nombra cada señal con un vocabulario acotado, así que
comprobar si un fragmento habla de una señal es una operación decidible.

Lo que esta verificación NO hace: juzgar si el contenido del fragmento implica
lógicamente la afirmación. Eso exigiría una interpretación que este componente no
puede hacer de forma verificable. Se limita a lo comprobable --que el fragmento
trate de la señal, que sea de tipo diagnóstico, que porte el código pertinente--
y deja constancia de sus límites en lugar de fingir que decide más.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.rag.manifest import DocumentType

#: Vocabulario con que el manual nombra cada señal. Sale de leer el corpus, no
#: de suponerlo: son los términos que aparecen en los procedimientos.
TERMINOS_SENAL: dict[str, tuple[str, ...]] = {
    "stft_bank1": ("short term fuel trim", "stft", "short-term fuel trim", "fuel trim"),
    "ltft_bank1": ("long term fuel trim", "ltft", "long-term fuel trim", "fuel trim"),
    "maf": ("maf", "mass air flow", "mass airflow", "air flow sensor"),
    "map": (
        "map sensor",
        "manifold absolute pressure",
        "intake manifold pressure",
        "manifold pressure",
    ),
    "coolant_temperature": ("coolant temperature", "ect", "engine coolant"),
    "intake_air_temperature": ("intake air temperature", "iat"),
    "oxygen_sensor": ("ho2s", "oxygen sensor", "o2 sensor", "heated oxygen"),
    "rpm": ("engine speed", "rpm", "revolution"),
    "vehicle_speed": ("vehicle speed", "vss", "speed sensor"),
    "engine_load": ("engine load", "calculated load", "load value"),
    "throttle_position": ("throttle position", "tp sensor", "throttle valve"),
    "ignition_timing": ("ignition timing", "spark advance", "timing advance"),
}

#: Tipos de documento que pueden sostener un diagnóstico. Una descripción de
#: funcionamiento explica cómo trabaja un componente; no sostiene que esté
#: averiado.
TIPOS_DIAGNOSTICOS: frozenset[str] = frozenset(
    {
        DocumentType.REPAIR_MANUAL.value,
        DocumentType.WORKSHOP_MANUAL.value,
        DocumentType.DIAGNOSTIC_MANUAL.value,
        DocumentType.DTC_DOCUMENTATION.value,
        DocumentType.TECHNICAL_SERVICE_BULLETIN.value,
    }
)

#: Secciones del manual que son procedimiento diagnóstico y no descripción.
_PATRON_DIAGNOSTICO = re.compile(
    r"\b(DTC\s+[PBCU]\d|DETECTION CONDITION|DIAGNOSTIC PROCEDURE|"
    r"Diagnostic procedure|INSPECTION|TROUBLESHOOTING|POSSIBLE CAUSE)\b"
)


@dataclass(frozen=True)
class SupportCheck:
    """Resultado de comprobar si un fragmento sostiene una afirmación."""

    claim_id: str
    chunk_id: str
    mentions_signal: bool
    is_diagnostic: bool
    carries_expected_dtc: bool | None
    """``None`` cuando la condición no tiene DTC esperado que comprobar."""

    supports: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "chunk_id": self.chunk_id,
            "mentions_signal": self.mentions_signal,
            "is_diagnostic": self.is_diagnostic,
            "carries_expected_dtc": self.carries_expected_dtc,
            "supports": self.supports,
            "reason": self.reason,
        }


def mentions_signal(texto: str, senal: str) -> bool:
    """¿El fragmento habla de esta señal?

    La señal puede llegar como pareja de correlación --``rpm+maf``--, en cuyo
    caso basta con que el fragmento mencione cualquiera de las dos.
    """
    minuscula = texto.lower()
    for parte in senal.split("+"):
        for termino in TERMINOS_SENAL.get(parte, (parte.replace("_", " "),)):
            if termino in minuscula:
                return True
    return False


def is_diagnostic_content(evidencia: DocumentaryEvidence) -> bool:
    """¿Es contenido diagnóstico y no una descripción de funcionamiento?

    E12 lo midió: para una consulta sobre síntomas de la sonda, la recuperación
    devuelve arriba «HEATED OXYGEN SENSOR (HO2S) FUNCTION». Ese documento explica
    cómo funciona el sensor y no sostiene que esté averiado.
    """
    if evidencia.document_type not in TIPOS_DIAGNOSTICOS:
        return False
    if evidencia.dtc_codes:
        return True
    contexto = f"{evidencia.section or ''} {evidencia.text[:600]}"
    return bool(_PATRON_DIAGNOSTICO.search(contexto))


def check_support(
    claim: Claim,
    evidencia: DocumentaryEvidence,
    *,
    signal: str,
    expected_dtc: tuple[str, ...] = (),
) -> SupportCheck:
    """Comprueba si un fragmento concreto sostiene una afirmación concreta."""
    menciona = mentions_signal(evidencia.text, signal)
    diagnostico = is_diagnostic_content(evidencia)
    lleva_dtc: bool | None = None
    if expected_dtc:
        lleva_dtc = bool(set(evidencia.dtc_codes) & set(expected_dtc))

    if not menciona:
        return SupportCheck(
            claim.claim_id,
            evidencia.chunk_id,
            menciona,
            diagnostico,
            lleva_dtc,
            False,
            f"el fragmento no menciona la señal {signal}",
        )
    if not diagnostico:
        return SupportCheck(
            claim.claim_id,
            evidencia.chunk_id,
            menciona,
            diagnostico,
            lleva_dtc,
            False,
            "el fragmento describe el componente pero no es contenido diagnóstico",
        )
    if lleva_dtc is False:
        return SupportCheck(
            claim.claim_id,
            evidencia.chunk_id,
            menciona,
            diagnostico,
            lleva_dtc,
            False,
            f"el fragmento no porta ninguno de los códigos esperados {list(expected_dtc)}",
        )
    return SupportCheck(
        claim.claim_id,
        evidencia.chunk_id,
        menciona,
        diagnostico,
        lleva_dtc,
        True,
        "menciona la señal en contenido diagnóstico del vehículo",
    )
