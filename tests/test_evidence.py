"""Regresión de los defectos de instrumento del modelo de evidencia.

Cada test de este fichero corresponde a un defecto encontrado y corregido, no a
una hipótesis: el caso que reproducen estaba en un registro de ejecución.
"""

from __future__ import annotations

from mecanico_ia_exp.evidence.assembly import build_claims
from mecanico_ia_exp.evidence.model import DocumentaryEvidence, Observation

# ------------------- regresión de los defectos de instrumento (P-06, P-11)


def test_la_afirmacion_no_contradice_el_signo_del_valor_que_cita() -> None:
    """Un descriptor con valor negativo no puede describirse como «por encima».

    La primera plantilla deducía el sentido del signo SHAP (`direction`) y a
    continuación imprimía `value`, que puede tener el signo contrario. En el
    registro había un caso real: valor -1,496 descrito como situado «por encima
    de lo esperable», y contado como afirmación sostenida.
    """
    obs = Observation(
        observation_id="OBS001",
        signal="coolant_temperature",
        statistic="delta_min",
        value=-1.496284,
        direction="increases",
        importance=0.04,
        session_id="s1",
        window_start_s=120.0,
        window_end_s=239.0,
    )
    claims, _ = build_claims([obs], [], accepted_applicability=frozenset({"EXACT_MATCH"}))
    texto = claims[0].text
    assert "-1,496" in texto.replace(".", ",") or "-1.496" in texto
    assert "por encima" not in texto
    assert "por debajo" not in texto
    # Lo que sí debe decir: que el descriptor contribuye a la predicción.
    assert "contribuyen a la predicción" in texto


def test_la_afirmacion_declara_la_contribucion_en_su_sentido() -> None:
    """El signo de la atribución sigue informándose: se separa, no se pierde."""
    base = dict(
        observation_id="OBS001",
        signal="stft_bank1",
        statistic="mean",
        value=7.077,
        importance=0.04,
        session_id="s1",
        window_start_s=120.0,
        window_end_s=239.0,
    )
    sube, _ = build_claims(
        [Observation(direction="increases", **base)], [], accepted_applicability=frozenset()
    )
    baja, _ = build_claims(
        [Observation(direction="decreases", **base)], [], accepted_applicability=frozenset()
    )
    assert "al alza" in sube[0].text
    assert "a la baja" in baja[0].text


def test_la_evidencia_documental_serializa_el_fichero_de_origen() -> None:
    """Sin él, la cadena de procedencia se corta en el documento."""
    doc = DocumentaryEvidence(
        chunk_id="ch1",
        document_id="doc",
        vehicle_id="v",
        text="t",
        score=0.5,
        applicability="EXACT_MATCH",
        source_file="srvc/B3E011002000W01.pdf",
    )
    assert doc.to_dict()["source_file"] == "srvc/B3E011002000W01.pdf"
