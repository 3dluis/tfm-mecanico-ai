"""Política de suficiencia v2: el papel del fragmento.

Cada test corresponde a una condición de `docs/methodology/politica-suficiencia-v2.md`.
Los fragmentos de prueba están escritos con la forma del manual real —un
procedimiento con pasos y bifurcaciones, una tabla que enumera códigos, una
descripción de lógica de detección— pero **no reproducen ningún caso del
conjunto anotado**: la política debe funcionar sobre cualquier fragmento.

**Única edición posterior a la congelación de v2**, 4 de septiembre de 2026: la
señal de los fixtures pasó de `throttle_position` a `throttle_position`. Ninguna
aserción cambió. El motivo es un hallazgo, no una limpieza: `throttle_position` no
está en el diccionario de vocabulario del verificador, y estos tests pasaban
gracias a que una señal sin correspondencia caía a una comparación literal del
identificador. Al hacer explícita esa ausencia con
`SIGNAL_MAPPING_UNAVAILABLE`, las tres pruebas que exigían soporte dejaron de
pasar. Es decir: **la demostración de generalidad de v2 se apoyaba en el
comportamiento silencioso que ahora se elimina.** Se registra en
`docs/methodology/limitacion-vocabulario-senales.md`.
"""

from __future__ import annotations

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.evidence.support import ChunkRole, check_support, classify_chunk

CLAIM = Claim(claim_id="C01", text="El descriptor throttle_position (mean) toma el valor 3,2.")


def _fragmento(texto: str, seccion: str, dtc: tuple[str, ...]) -> DocumentaryEvidence:
    return DocumentaryEvidence(
        chunk_id="ch",
        document_id="doc",
        vehicle_id="v",
        text=texto,
        score=0.5,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=dtc,
    )


PROCEDIMIENTO = _fragmento(
    "Diagnostic procedure. Turn the ignition switch off. Disconnect the throttle position "
    "sensor connector. Measure the voltage at terminal A. Is the voltage within "
    "specification?\nYes Go to the next step.\nNo Repair or replace the harness.",
    "DTC P9911 [ZJ, Z6]",
    ("P9911",),
)
TABLA = _fragmento(
    "P9901 throttle position sensor circuit low\nP9902 throttle position sensor circuit high\n"
    "P9911 throttle position sensor performance\nP9912 brake fluid level",
    "DTC TABLE [ZJ, Z6]",
    ("P9901", "P9902", "P9911", "P9912"),
)
REFERENCIA = _fragmento(
    "P9911 throttle position sensor performance. The PCM monitors the throttle position sensor "
    "signal while the vehicle is moving. If the signal remains out of range, the PCM "
    "determines that there is a malfunction.",
    "DTC DETECTION LOGIC AND CONDITIONS [ZJ, Z6]",
    ("P9911",),
)


def test_dtc_table_not_sufficient_by_itself() -> None:
    """Una tabla porta el código y nombra la señal, y no sostiene nada.

    Es el hallazgo que motivó esta política: en v1 pasaba las tres
    comprobaciones y se contaba como soporte.
    """
    assert classify_chunk(TABLA) is ChunkRole.CODE_DEFINITION_OR_TABLE
    r = check_support(CLAIM, TABLA, signal="throttle_position", expected_dtc=("P9911",))
    assert r.mentions_signal and r.carries_expected_dtc
    assert not r.supports
    assert "no es un procedimiento" in r.reason


def test_signal_mention_not_sufficient_by_itself() -> None:
    """Nombrar la señal en contenido técnico tampoco basta: la lógica de
    detección dice qué vigila la centralita, no cómo se comprueba."""
    assert classify_chunk(REFERENCIA) is ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE
    r = check_support(CLAIM, REFERENCIA, signal="throttle_position", expected_dtc=("P9911",))
    assert r.mentions_signal and r.carries_expected_dtc
    assert not r.supports


def test_procedure_can_support_claim() -> None:
    """Y un procedimiento sí: la política no abstiene siempre."""
    assert classify_chunk(PROCEDIMIENTO) is ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
    r = check_support(CLAIM, PROCEDIMIENTO, signal="throttle_position", expected_dtc=("P9911",))
    assert r.supports


def test_partial_reference_requires_abstention_when_procedure_missing() -> None:
    """La condición de evidencia parcial: quedan tabla y referencia, falta el
    procedimiento. Ninguna afirmación puede quedar sostenida."""
    from mecanico_ia_exp.evidence.assembly import build_claims
    from mecanico_ia_exp.evidence.model import Observation

    obs = Observation(
        observation_id="OBS001",
        signal="throttle_position",
        statistic="mean",
        value=3.2,
        direction="increases",
        importance=0.1,
    )
    claims, _ = build_claims(
        [obs],
        [TABLA, REFERENCIA],
        accepted_applicability=frozenset({"EXACT_MATCH"}),
        expected_dtc=("P9911",),
    )
    assert claims[0].support_status.value != "SUPPORTED"
    assert claims[0].chunk_ids == ()


def test_wrong_engine_procedure_rejected() -> None:
    """El filtro de aplicabilidad no se toca y sigue funcionando: un
    procedimiento del motor incorrecto no entra entre los aplicables."""
    from mecanico_ia_exp.evidence.assembly import build_claims
    from mecanico_ia_exp.evidence.model import Observation

    otro_motor = DocumentaryEvidence(
        chunk_id="ch-lf",
        document_id="doc",
        vehicle_id="v",
        text=PROCEDIMIENTO.text,
        score=0.9,
        applicability="PARTIAL_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=("P9911",),
    )
    obs = Observation("OBS001", "throttle_position", "mean", 3.2, "increases", 0.1)
    claims, comprobaciones = build_claims(
        [obs],
        [otro_motor],
        accepted_applicability=frozenset({"EXACT_MATCH"}),
        expected_dtc=("P9911",),
    )
    assert comprobaciones == [], "un fragmento no aplicable no llega a comprobarse"
    assert claims[0].chunk_ids == ()


def test_absent_evidence_abstains() -> None:
    """Sin ningún documento, ninguna afirmación queda sostenida."""
    from mecanico_ia_exp.evidence.assembly import build_claims
    from mecanico_ia_exp.evidence.model import Observation

    obs = Observation("OBS001", "throttle_position", "mean", 3.2, "increases", 0.1)
    claims, _ = build_claims(
        [obs], [], accepted_applicability=frozenset({"EXACT_MATCH"}), expected_dtc=("P9911",)
    )
    assert claims[0].chunk_ids == ()
    assert claims[0].support_status.value != "SUPPORTED"


def test_el_procedimiento_se_examina_antes_que_la_tabla() -> None:
    """Segunda cara del hallazgo: en v1 las dos plazas de cita las podía ocupar
    una tabla bien puntuada y el procedimiento no llegaba a examinarse."""
    from mecanico_ia_exp.evidence.assembly import build_claims
    from mecanico_ia_exp.evidence.model import Observation

    tabla_bien_puntuada = DocumentaryEvidence(
        chunk_id="ch-tabla",
        document_id="doc",
        vehicle_id="v",
        text=TABLA.text,
        score=0.99,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=TABLA.dtc_codes,
    )
    procedimiento_mal_puntuado = DocumentaryEvidence(
        chunk_id="ch-proc",
        document_id="doc",
        vehicle_id="v",
        text=PROCEDIMIENTO.text,
        score=0.11,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=("P9911",),
    )
    obs = Observation("OBS001", "throttle_position", "mean", 3.2, "increases", 0.1)
    claims, comprobaciones = build_claims(
        [obs],
        [tabla_bien_puntuada, procedimiento_mal_puntuado],
        accepted_applicability=frozenset({"EXACT_MATCH"}),
        expected_dtc=("P9911",),
    )
    assert comprobaciones[0].chunk_id == "ch-proc", "el procedimiento se examina primero"
    assert claims[0].chunk_ids == ("ch-proc",)


def test_la_clasificacion_no_depende_de_ninguna_senal_concreta() -> None:
    """La política debe aplicarse a cualquier fragmento del corpus.

    Si la clasificación cambiara al sustituir la señal por otra, sería una regla
    escrita para los casos evaluados y no un criterio.
    """
    for senal in ("throttle position", "steering angle", "turbocharger boost"):
        proc = _fragmento(
            PROCEDIMIENTO.text.replace("throttle position", senal),
            "DTC P9911 [ZJ, Z6]",
            ("P9911",),
        )
        tabla = _fragmento(
            TABLA.text.replace("throttle position", senal), "DTC TABLE [ZJ, Z6]", TABLA.dtc_codes
        )
        assert classify_chunk(proc) is ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
        assert classify_chunk(tabla) is ChunkRole.CODE_DEFINITION_OR_TABLE
