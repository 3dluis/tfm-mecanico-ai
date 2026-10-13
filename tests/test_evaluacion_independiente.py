"""La regla de selección del conjunto de evaluación independiente, comprobable.

Un conjunto «congelado» que nadie puede reejecutar es una lista de nombres. Lo
que lo hace congelado es que la regla que lo produjo se puede volver a aplicar y
dar exactamente lo mismo, y que la exclusión que lo justifica se pueda verificar
en lugar de creer.

**Dónde se puede comprobar qué.** Las entradas de la regla —las ventanas que vio
el adaptador, las de la evaluación de E15, las sesiones de ajuste— están
registradas en la congelación, de modo que la selección se verifica en cualquier
clon, sin ningún fichero no distribuido. Lo que **no** se puede comprobar en un
clon es que esas entradas correspondan de verdad a `synthetic_v3`: ese conjunto
no es reconstruible —es pre-calibración— y esa comprobación lleva el marcador
``artefactos``.
"""

from __future__ import annotations

import hashlib
import json

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


def _huella(ventanas: list[str]) -> str:
    return hashlib.sha256(json.dumps(sorted(ventanas), sort_keys=True).encode()).hexdigest()[:16]


# ----------------------------------------------- lo que se comprueba en un clon


def test_la_congelacion_declara_lo_que_no_permite_afirmar() -> None:
    cfg = _congelacion()
    assert cfg["ventanas"], "sin ventanas no hay conjunto"
    assert len(cfg["lo_que_este_conjunto_no_permite_afirmar"]) >= 3
    assert len(cfg["condiciones_de_invalidez"]) >= 3
    assert "no es reconstruible" in cfg["limite_de_la_verificacion_en_un_clon"]


def test_la_huella_de_la_seleccion_corresponde_a_las_quince_ventanas() -> None:
    """Si alguien edita la lista sin recalcular la huella, esto lo ve."""
    cfg = _congelacion()
    ventanas = [v["ventana"] for v in cfg["ventanas"]]
    assert _huella(ventanas) == cfg["huella_de_la_seleccion_sha256_16"]


def test_una_ventana_por_sesion_para_que_no_solapen_muestras() -> None:
    sesiones = [v["sesion"] for v in _congelacion()["ventanas"]]
    assert len(sesiones) == len(set(sesiones))


def test_ninguna_ventana_elegida_estaba_entre_las_excluidas() -> None:
    """La exclusión, contra las entradas registradas: sin datos en disco."""
    cfg = _congelacion()
    excluidas = set(cfg["entradas_de_la_regla"]["sesiones_excluidas_en_total"])
    for v in cfg["ventanas"]:
        assert v["sesion"] not in excluidas, f"{v['sesion']} está entre las vistas"


def test_las_entradas_registradas_son_las_que_dice_la_auditoria() -> None:
    """43 ventanas de ajuste y 5 de evaluación: las cifras de la auditoría."""
    e = _congelacion()["entradas_de_la_regla"]
    assert len(e["ventanas_de_ajuste_de_slm_lora_v2"]) == 43
    assert len(e["ventanas_de_evaluacion_de_E15"]) == 5
    solape = set(e["ventanas_de_ajuste_de_slm_lora_v2"]) & set(e["ventanas_de_evaluacion_de_E15"])
    assert len(solape) == 3, f"la auditoría midió 3 ventanas contaminadas, aquí salen {len(solape)}"


def test_las_quince_cubren_las_cinco_clases_de_fallo() -> None:
    clases = {v["clase"] for v in _congelacion()["ventanas"]}
    assert len(clases) == 5
    assert all(v["fallo_activo"] for v in _congelacion()["ventanas"])


# ------------------------- lo que solo se comprueba donde están los artefactos


@pytest.mark.artefactos
def test_las_entradas_registradas_coinciden_con_los_ficheros_del_autor() -> None:
    """Que la congelación no se haya separado de los ficheros de los que salió."""
    e = _congelacion()["entradas_de_la_regla"]
    en_disco = sorted(
        {
            json.loads(linea)["case_id"]
            for nombre in ("train", "valid")
            for linea in (AJUSTE_V2 / f"{nombre}.jsonl").read_text("utf-8").splitlines()
            if linea.strip()
        }
    )
    assert en_disco == e["ventanas_de_ajuste_de_slm_lora_v2"]

    e15 = json.loads(E15.read_text("utf-8"))
    assert (
        sorted({c["bundle"]["case_id"] for c in e15["cases"]}) == e["ventanas_de_evaluacion_de_E15"]
    )

    reparto = json.loads(PRE_V2.read_text("utf-8"))["split_assignment"]
    assert (
        sorted({s for s, p in reparto.items() if p == "train"})
        == e["sesiones_de_train_de_synthetic_v2"]
    )


@pytest.mark.artefactos
def test_la_regla_reproduce_la_seleccion_sobre_synthetic_v3() -> None:
    """Se vuelve a aplicar la regla escrita y tiene que dar las mismas 15."""
    import pandas as pd

    cfg = _congelacion()
    excluidas = set(cfg["entradas_de_la_regla"]["sesiones_excluidas_en_total"])
    meta = pd.read_parquet(META_V3)
    libre = meta[(meta.partition == "validation") & (~meta.session_id.isin(excluidas))].copy()
    libre["ventana"] = libre.session_id + "@" + libre.t_start.astype(int).astype(str) + "s"

    obtenidas = []
    for clase in sorted(c for c in libre.label.unique() if c != "F00_normal"):
        for sesion in sorted(libre[libre.label == clase].session_id.unique())[:3]:
            cand = libre[(libre.session_id == sesion) & libre.fault_active].sort_values("t_start")
            obtenidas.append(cand.iloc[0].ventana)

    esperada = cfg["huella_de_la_seleccion_sha256_16"]
    assert _huella(obtenidas) == esperada, (
        f"la regla ya no reproduce la selección congelada: {_huella(obtenidas)} ≠ {esperada}. "
        "O cambió el reparto, o cambió la regla, o cambió el conjunto."
    )


@pytest.mark.artefactos
def test_validacion_de_synthetic_v2_no_ofrece_ninguna_ventana_de_fallo_libre() -> None:
    """La razón medida por la que el conjunto no sale de synthetic_v2.

    Si esta prueba empezara a fallar, la justificación escrita en la congelación
    habría dejado de ser cierta y habría que reescribirla.
    """
    import pandas as pd

    cfg = _congelacion()
    excluidas = set(cfg["entradas_de_la_regla"]["sesiones_excluidas_en_total"])
    meta = pd.read_parquet(META_V2)
    libre = meta[(meta.partition == "validation") & (~meta.session_id.isin(excluidas))]
    clases_de_fallo = {c for c in libre.label.unique() if c != "F00_normal"}
    assert not clases_de_fallo, (
        f"ahora sí hay ventanas de fallo libres en validación de synthetic_v2: {clases_de_fallo}"
    )
