"""La regla de selección del conjunto de evaluación independiente, comprobable.

Un conjunto «congelado» que nadie puede reejecutar es una lista de nombres. Lo
que lo hace congelado es que la regla que lo produjo se puede volver a aplicar y
dar exactamente lo mismo, y que la exclusión que lo justifica se pueda verificar
en lugar de creer.
"""

from __future__ import annotations

import hashlib
import json

import pandas as pd
import pytest

from mecanico_ia_exp.config import paths

CONGELACION = paths.ROOT / "configs" / "evaluacion-independiente-redactor.json"
META_V3 = paths.ROOT / "data" / "processed" / "synthetic_v3_meta.parquet"
META_V2 = paths.ROOT / "data" / "processed" / "synthetic_v2_meta.parquet"
PRE_V2 = paths.ROOT / "data" / "processed" / "synthetic_v2_preprocess.json"
AJUSTE_V2 = paths.ROOT / "data" / "processed" / "slm_finetune"
E15 = paths.ROOT / "experiments" / "E15_suficiencia.json"


def _congelacion() -> dict:
    return json.loads(CONGELACION.read_text("utf-8"))


def _sesiones_excluidas() -> set[str]:
    vistas = {
        json.loads(linea)["case_id"].split("@")[0]
        for nombre in ("train", "valid")
        for linea in (AJUSTE_V2 / f"{nombre}.jsonl").read_text("utf-8").splitlines()
        if linea.strip()
    }
    e15 = json.loads(E15.read_text("utf-8"))
    de_e15 = {c["bundle"]["case_id"].split("@")[0] for c in e15["cases"]}
    reparto = json.loads(PRE_V2.read_text("utf-8"))["split_assignment"]
    de_train_v2 = {s for s, p in reparto.items() if p == "train"}
    return vistas | de_e15 | de_train_v2


def test_la_congelacion_existe_y_declara_lo_que_no_permite_afirmar() -> None:
    cfg = _congelacion()
    assert cfg["ventanas"], "sin ventanas no hay conjunto"
    assert len(cfg["lo_que_este_conjunto_no_permite_afirmar"]) >= 3
    assert len(cfg["condiciones_de_invalidez"]) >= 3


@pytest.mark.conjunto
def test_la_regla_de_seleccion_reproduce_la_huella_congelada() -> None:
    """Se vuelve a aplicar la regla escrita y tiene que dar las mismas 15."""
    cfg = _congelacion()
    meta = pd.read_parquet(META_V3)
    excluidas = _sesiones_excluidas()
    libre = meta[(meta.partition == "validation") & (~meta.session_id.isin(excluidas))].copy()
    libre["ventana"] = libre.session_id + "@" + libre.t_start.astype(int).astype(str) + "s"

    obtenidas = []
    for clase in sorted(c for c in libre.label.unique() if c != "F00_normal"):
        for sesion in sorted(libre[libre.label == clase].session_id.unique())[:3]:
            cand = libre[(libre.session_id == sesion) & libre.fault_active].sort_values("t_start")
            obtenidas.append(cand.iloc[0].ventana)

    huella = hashlib.sha256(json.dumps(sorted(obtenidas), sort_keys=True).encode()).hexdigest()
    esperada = cfg["huella_de_la_seleccion_sha256_16"]
    assert huella[:16] == esperada, (
        f"la regla ya no reproduce la selección congelada: {huella[:16]} ≠ {esperada}. "
        "O cambió el reparto, o cambió la regla, o cambió el conjunto."
    )
    assert sorted(obtenidas) == sorted(v["ventana"] for v in cfg["ventanas"])


@pytest.mark.conjunto
def test_ninguna_ventana_congelada_fue_vista_en_ajuste_ni_en_e15() -> None:
    cfg = _congelacion()
    excluidas = _sesiones_excluidas()
    for v in cfg["ventanas"]:
        assert v["sesion"] not in excluidas, f"{v['sesion']} está entre las vistas"


@pytest.mark.conjunto
def test_una_ventana_por_sesion_para_que_no_solapen_muestras() -> None:
    cfg = _congelacion()
    sesiones = [v["sesion"] for v in cfg["ventanas"]]
    assert len(sesiones) == len(set(sesiones))


@pytest.mark.conjunto
def test_validacion_de_synthetic_v2_no_ofrece_ninguna_ventana_de_fallo_libre() -> None:
    """La razón medida por la que el conjunto no sale de synthetic_v2.

    Si esta prueba empezara a fallar, la justificación escrita en la congelación
    habría dejado de ser cierta y habría que reescribirla.
    """
    meta = pd.read_parquet(META_V2)
    excluidas = _sesiones_excluidas()
    libre = meta[(meta.partition == "validation") & (~meta.session_id.isin(excluidas))]
    clases_de_fallo = {c for c in libre.label.unique() if c != "F00_normal"}
    assert not clases_de_fallo, (
        f"ahora sí hay ventanas de fallo libres en validación de synthetic_v2: {clases_de_fallo}"
    )
