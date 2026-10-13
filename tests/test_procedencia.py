"""El manifiesto de procedencia tiene que permitir regenerar la sesión.

Un manifiesto que no lo permita no documenta nada, por completo que parezca.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from mecanico_ia_exp.obd.procedencia import (
    CALIBRACION_NO_LEIDA,
    FUENTES_DEL_GENERADOR,
    ProcedenciaIncompletaError,
    construir,
    escribir,
    huellas_del_generador,
    reconstruir,
)
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import (
    SessionSpec,
    build_balanced_specs,
    generate_dataset,
    generate_session,
)


@pytest.fixture(scope="module")
def conjunto() -> tuple[list[SessionSpec], object, dict]:
    specs = [
        SessionSpec(
            session_id=s.session_id,
            regime=s.regime,
            duration_s=120.0,
            seed=s.seed,
            fault_id=s.fault_id,
            fault_onset_s=0.0 if s.fault_onset_s == 0.0 else 24.0,
            ambient_temp_c=s.ambient_temp_c,
        )
        for s in build_balanced_specs(seed=20260901, sessions_per_fault=2)
    ]
    datos, _ = generate_dataset(specs, dataset_id="procedencia_test", seed=20260901)
    manifiesto = construir(specs, datos, dataset_id="procedencia_test", seed=20260901)
    return specs, datos, manifiesto


# ------------------------------------------------------------------- huellas


def test_la_huella_cubre_las_fuentes_del_generador() -> None:
    huellas = huellas_del_generador()
    assert set(huellas) == set(FUENTES_DEL_GENERADOR)
    assert all(len(h) == 16 for h in huellas.values())


def test_el_motor_esta_entre_las_fuentes() -> None:
    """El YAML documenta las constantes; `engine.py` las contiene.

    La huella que de verdad fija el fenómeno es la del módulo, porque es el que
    se lee. El YAML va también, para detectar que los dos se separen.
    """
    assert "src/mecanico_ia_exp/obd/engine.py" in FUENTES_DEL_GENERADOR
    assert CALIBRACION_NO_LEIDA in FUENTES_DEL_GENERADOR


def test_una_fuente_que_falta_es_un_error(tmp_path) -> None:
    with pytest.raises(ProcedenciaIncompletaError, match="Falta una fuente"):
        huellas_del_generador(raiz=tmp_path)


# -------------------------------------------------------------- el manifiesto


def test_el_manifiesto_ficha_todas_las_sesiones(conjunto) -> None:
    specs, _, manifiesto = conjunto
    assert manifiesto["n_sessions"] == len(specs)
    assert {f["session_id"] for f in manifiesto["sessions"]} == {s.session_id for s in specs}


def test_el_manifiesto_guarda_lo_que_la_ficha_antigua_perdia(conjunto) -> None:
    _, _, manifiesto = conjunto
    ficha = manifiesto["sessions"][0]
    for campo in ("seed", "duration_s", "ambient_temp_c", "fault_onset_s", "fault_params"):
        assert campo in ficha, f"falta {campo}, que la ficha por conjunto no registraba"


def test_el_manifiesto_declara_que_la_version_no_identifica(conjunto) -> None:
    _, _, manifiesto = conjunto
    assert "synthetic_v2" in manifiesto["generator"]["declared_version_no_identifica"]


def test_el_manifiesto_guarda_los_parametros_de_expresion(conjunto) -> None:
    _, _, manifiesto = conjunto
    expresion = manifiesto["expression"]
    assert expresion["ratio_declarado"] > 0
    assert set(expresion["umbral_por_senal"]) == set(SIGNAL_NAMES)


def test_una_especificacion_sin_datos_se_rechaza(conjunto) -> None:
    specs, datos, _ = conjunto
    huerfana = SessionSpec(session_id="no_generada", regime="idle", duration_s=60.0, seed=1)
    with pytest.raises(ProcedenciaIncompletaError, match="sin datos generados"):
        construir([*specs, huerfana], datos, dataset_id="x", seed=1)


# ---------------------------------------------------------- la reconstrucción


def test_la_sesion_se_regenera_identica_desde_su_ficha(conjunto) -> None:
    """La comprobación que da sentido al fichero."""
    _, datos, manifiesto = conjunto
    for ficha in manifiesto["sessions"]:
        session_id = ficha["session_id"]
        spec = reconstruir(manifiesto, session_id)
        regenerada = generate_session(spec)
        original = datos[datos["session_id"] == session_id].sort_values("timestamp")
        assert np.array_equal(
            original[list(SIGNAL_NAMES)].to_numpy(), regenerada[list(SIGNAL_NAMES)].to_numpy()
        ), f"{session_id} no se regenera igual"


def test_la_expresion_tambien_se_regenera_igual(conjunto) -> None:
    _, datos, manifiesto = conjunto
    session_id = manifiesto["sessions"][-1]["session_id"]
    regenerada = generate_session(reconstruir(manifiesto, session_id))
    original = datos[datos["session_id"] == session_id].sort_values("timestamp")
    assert np.array_equal(
        original["fault_expressed"].to_numpy(), regenerada["fault_expressed"].to_numpy()
    )


def test_pedir_una_sesion_que_no_esta_falla(conjunto) -> None:
    _, _, manifiesto = conjunto
    with pytest.raises(ProcedenciaIncompletaError, match="no contiene"):
        reconstruir(manifiesto, "inexistente")


# --------------------------------------------------------------- la escritura


def test_escribir_no_sobrescribe(tmp_path, conjunto) -> None:
    """Un manifiesto sobrescrito es procedencia perdida sin aviso."""
    _, _, manifiesto = conjunto
    destino = tmp_path / "m.json"
    escribir(destino, manifiesto)
    assert json.loads(destino.read_text("utf-8"))["dataset_id"] == "procedencia_test"
    with pytest.raises(FileExistsError, match="no se sobrescribe"):
        escribir(destino, manifiesto)
