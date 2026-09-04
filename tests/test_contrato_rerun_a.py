"""Contrato de RERUN-A: una sola variable.

La afirmación entera del experimento —«lo único que cambia es el aislamiento del
espacio vectorial»— descansa en configuración, no en aritmética. Estas pruebas la
fijan: si alguien mueve una de esas piezas, falla aquí y no en la interpretación
de un resultado seis pasos más tarde.

Pre-registro: `docs/methodology/preregistro-rerun-a.md`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


# --- El verificador canónico -------------------------------------------------


def test_la_politica_canonica_es_v2_1() -> None:
    """v2.2 está implementada y **sin medir**: introducirla ahora cambiaría dos
    variables en la misma ejecución y la atribución causal se perdería."""
    from mecanico_ia_exp.abstention.sufficiency import POLITICAS, VERIFIER_VERSION

    assert VERIFIER_VERSION == "v2.1", (
        "RERUN-A exige v2.1. v2.2 se mide en RERUN-B, sobre recuperación ya canónica"
    )
    assert VERIFIER_VERSION in POLITICAS


def test_bajo_v2_1_la_puerta_de_codigos_se_comporta_como_su_artefacto() -> None:
    """El requisito explícito es lo único que v2.2 añade.

    Con v2.1 activo, un fragmento sin códigos esperados no puede recibir los
    motivos que v2.2 introdujo: si los recibiera, el artefacto congelado de v2.1
    dejaría de ser reproducible.
    """
    from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
    from mecanico_ia_exp.evidence.support import DtcRequirement, check_support

    fragmento = DocumentaryEvidence(
        chunk_id="ch",
        document_id="doc",
        vehicle_id="v",
        text=(
            "B1234 throttle position sensor.\nTurn the ignition switch off. Measure the "
            "resistance. Is the resistance within specification?\nYes Go to the next step."
        ),
        score=0.5,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=("B1234",),
        section="DTC B1234 [ZJ, Z6]",
    )
    resultado = check_support(
        Claim("C01", "t", ()),
        fragmento,
        signal="throttle_position",
        expected_dtc=("B1234",),
        requisito=DtcRequirement.DTC_REQUIRED,
    )
    assert resultado.supports
    assert resultado.dtc_requirement == DtcRequirement.DTC_REQUIRED.value


def test_el_umbral_y_la_semilla_no_se_mueven() -> None:
    """Las constantes que el pre-registro declara controladas."""
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    u = SufficiencyThresholds()
    assert u.min_confidence == 0.79
    assert u.min_claim_coverage == 0.8
    assert u.accepted_applicability == frozenset({"EXACT_MATCH"})


# --- El conjunto de recuperación ---------------------------------------------


def test_el_conjunto_de_recuperacion_es_el_original_de_seis() -> None:
    """Reejecutar sobre los diecisiete cambiaría **dos** variables.

    El conjunto anotado creció después de aquella ejecución. La ampliación es un
    experimento distinto, con otra pregunta y otro identificador.
    """
    from mecanico_ia_exp.experiments.retrieval_runner import CONJUNTO_E12_ORIGINAL

    assert len(CONJUNTO_E12_ORIGINAL) == 6
    artefacto = json.loads(
        (RAIZ / "experiments" / "E12_retrieval.json").read_text(encoding="utf-8")
    )
    del_artefacto = tuple(c["case_id"] for c in artefacto["strategies"][0]["cases"])
    assert del_artefacto == CONJUNTO_E12_ORIGINAL, (
        "el conjunto declarado no coincide con el del artefacto que se quiere replicar"
    )


# --- Las líneas base como control de integridad ------------------------------


def test_las_lineas_base_invariantes_estan_declaradas_como_vector() -> None:
    """Su valor no puede depender del número de condiciones.

    Expresadas como razones sobre las ejecuciones totales, retirar una condición
    las cambia **por construcción** y la regla de parada saltaría sin que nada
    fuera mal.
    """
    texto = (RAIZ / "docs" / "methodology" / "preregistro-rerun-a.md").read_text(encoding="utf-8")
    assert "B = [" in texto, "las invariantes deben declararse como vector ordenado"
    assert "por (fallo, condición)" in texto or "por fallo y condición" in texto


@pytest.mark.parametrize("retirado", ["p = 0,008", "p = 0.008"])
def test_el_valor_p_retirado_no_reaparece(retirado: str) -> None:
    """`RETRACTED_INVALID_INFERENCE`: no debe poder volver desde ningún documento
    vivo. Se permite únicamente donde se declara su retirada."""
    permitidos = {
        "preregistro-rerun-a.md",
        "08_decisiones_autor_20260904.md",
        "estados-provisionales.md",
    }
    ofensores = []
    for f in (RAIZ / "docs").rglob("*.md"):
        if f.name in permitidos or "revision" in f.parts:
            continue
        if retirado in f.read_text(encoding="utf-8"):
            ofensores.append(str(f.relative_to(RAIZ)))
    assert not ofensores, f"el valor p retirado reaparece en: {ofensores}"
