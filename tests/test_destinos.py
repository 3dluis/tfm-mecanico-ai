"""Una ejecución nueva no puede pisar un artefacto anterior ni uno histórico.

`tables/`, `figures/`, `data/` y `models/` están fuera del control de versiones,
así que Git no puede avisar de que un artefacto histórico cambió. El censo de
huellas es la única protección posible, y este fichero comprueba que funciona en
los dos sentidos: que detecta un cambio y que no se alarma por un artefacto
nuevo.
"""

from __future__ import annotations

import json

import pytest

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.experiments import (
    ablation_runner,
    baseline_runner,
    retrieval_runner,
    temporal_runner,
    threshold_runner,
    training_runner,
    xai_runner,
)
from mecanico_ia_exp.experiments.destinos import (
    PATRONES_HISTORICOS,
    REGISTRO_HISTORICO,
    ArtefactoOcupadoError,
    HistoricoAlteradoError,
    censar,
    escribir_censo,
    exigir_historicos_intactos,
    exigir_libres,
    verificar_historicos,
)

# --------------------------------------------------------- destinos ocupados


def test_un_destino_libre_pasa(tmp_path) -> None:
    destinos = {"a": tmp_path / "a.json", "b": tmp_path / "b.csv"}
    assert exigir_libres(destinos) == destinos


def test_un_destino_ocupado_detiene_la_ejecucion(tmp_path) -> None:
    ocupado = tmp_path / "a.json"
    ocupado.write_text("{}", encoding="utf-8")
    with pytest.raises(ArtefactoOcupadoError, match="no se sobrescriben"):
        exigir_libres({"a": ocupado, "b": tmp_path / "b.csv"})


def test_se_comprueban_todos_antes_de_escribir_el_primero(tmp_path) -> None:
    """El mensaje nombra los dos ocupados, no se detiene en el primero."""
    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "b.csv").write_text("x", encoding="utf-8")
    with pytest.raises(ArtefactoOcupadoError) as error:
        exigir_libres({"a": tmp_path / "a.json", "b": tmp_path / "b.csv"})
    assert "a.json" in str(error.value)
    assert "b.csv" in str(error.value)


# ------------------------------------------------- las rutas de los ejecutores


def test_sin_etiqueta_el_baseline_conserva_los_nombres_historicos() -> None:
    destinos = baseline_runner.destinos_de("synthetic_v2")
    assert destinos["registro"].name == "E6_baseline_synthetic_v2.json"
    assert destinos["figura_confusion"].name == "FIG-E6-01_confusion_baseline.png"


def test_con_etiqueta_los_seis_artefactos_del_baseline_cambian_de_ruta() -> None:
    """El hallazgo que motivó esto: proteger solo el registro dejaba expuestas
    tres tablas y dos figuras."""
    historicos = baseline_runner.destinos_de("synthetic_v2")
    etiquetados = baseline_runner.destinos_de("synthetic_v2", "reejecucion")
    assert set(historicos) == set(etiquetados)
    for clave in historicos:
        assert historicos[clave] != etiquetados[clave], f"{clave} no cambió de ruta"


def test_el_baseline_se_niega_a_sobrescribir_el_registro_publicado() -> None:
    """Sin etiqueta, y existiendo ya el registro de E6, la ejecución no arranca.

    No entrena nada: la negativa ocurre antes, que es el punto.
    """
    if not baseline_runner.destinos_de("synthetic_v2")["registro"].exists():
        pytest.skip("el registro histórico de E6 no está en esta copia")
    with pytest.raises(ArtefactoOcupadoError):
        baseline_runner.run_baseline("synthetic_v2")


def test_con_etiqueta_el_temporal_cambia_tambien_el_normalizador() -> None:
    historicos = temporal_runner.destinos_de("synthetic_v2")
    etiquetados = temporal_runner.destinos_de("synthetic_v2", "pi1")
    assert historicos["normalizador_media"].name == "E7_standardizer_mean.npy"
    assert etiquetados["normalizador_media"] != historicos["normalizador_media"]


def test_los_ejecutores_declaran_su_protocolo() -> None:
    """Una cifra nueva no puede confundirse con una corrección silenciosa de la
    anterior: el registro dice de qué protocolo sale."""
    assert "sin_calibrar" in baseline_runner.PROTOCOLO_HISTORICO
    assert "epoca_sobre_validacion" in temporal_runner.PROTOCOLO_HISTORICO


# ------------------------------------------------------- el censo y su guardia


def test_el_censo_del_repositorio_esta_intacto() -> None:
    """La comprobación que se ejecuta después de cada modificación."""
    assert REGISTRO_HISTORICO.is_file(), "falta el censo de artefactos históricos"
    assert exigir_historicos_intactos() > 0


def test_el_censo_cubre_las_cuatro_familias_sin_control_de_versiones() -> None:
    patrones = " ".join(PATRONES_HISTORICOS)
    for familia in ("tables/", "figures/", "data/raw/synthetic/", "models/"):
        assert familia in patrones, f"{familia} no está censada y Git no la vigila"


def test_el_censo_declara_los_registros_de_los_experimentos_publicados() -> None:
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    for experimento in ("E6_baseline", "E7_temporal", "E18_ablacion", "E19_anotacion"):
        assert any(experimento in ruta for ruta in declaradas), f"{experimento} sin censar"


def test_el_censo_detecta_un_artefacto_alterado(tmp_path) -> None:
    objetivo = tmp_path / "tables"
    objetivo.mkdir()
    (objetivo / "historico.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)

    (objetivo / "historico.csv").write_text("a,b\n9,9\n", encoding="utf-8")
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert len(desviaciones) == 1
    assert "cambió" in desviaciones[0].motivo
    with pytest.raises(HistoricoAlteradoError, match="alterado"):
        exigir_historicos_intactos(censo, raiz=tmp_path)


def test_el_censo_detecta_un_artefacto_borrado(tmp_path) -> None:
    (tmp_path / "tables").mkdir()
    fichero = tmp_path / "tables" / "historico.csv"
    fichero.write_text("x\n", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)

    fichero.unlink()
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert [d.motivo for d in desviaciones] == ["falta"]


def test_un_artefacto_nuevo_no_es_una_desviacion(tmp_path) -> None:
    """Producir artefactos nuevos es lo que una ejecución nueva hace."""
    (tmp_path / "tables").mkdir()
    (tmp_path / "tables" / "historico.csv").write_text("x\n", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)

    (tmp_path / "tables" / "E6_reejecucion_por_ventana.csv").write_text("y\n", encoding="utf-8")
    assert verificar_historicos(censo, raiz=tmp_path) == []


def test_sin_censo_la_verificacion_falla_en_lugar_de_callar(tmp_path) -> None:
    desviaciones = verificar_historicos(tmp_path / "no_existe.json", raiz=tmp_path)
    assert len(desviaciones) == 1
    assert "no existe el censo" in desviaciones[0].motivo


def test_un_censo_ilegible_falla(tmp_path) -> None:
    censo = tmp_path / "censo.json"
    censo.write_text("{esto no es json", encoding="utf-8")
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert "no se puede leer" in desviaciones[0].motivo


def test_censar_no_toca_nada(tmp_path) -> None:
    (tmp_path / "tables").mkdir()
    fichero = tmp_path / "tables" / "a.csv"
    fichero.write_text("x\n", encoding="utf-8")
    antes = fichero.stat().st_mtime_ns
    censar(raiz=tmp_path)
    assert fichero.stat().st_mtime_ns == antes


def test_el_censo_usa_rutas_relativas_a_la_raiz() -> None:
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    assert all(not ruta.startswith("/") for ruta in declaradas)
    assert all((paths.ROOT / ruta).is_file() for ruta in declaradas)


# ------------------------------------------- los siete ejecutores, uno por uno

#: Cada ejecutor con su función de destinos y los argumentos que necesita. La
#: lista existe para que añadir un ejecutor sin etiqueta rompa un test.
EJECUTORES = (
    ("E6 baseline", baseline_runner.destinos_de, ("synthetic_v2",)),
    ("E7 temporal", temporal_runner.destinos_de, ("synthetic_v2",)),
    ("E9 atribución", xai_runner.destinos_de, ("synthetic_v2",)),
    ("E12 recuperación", retrieval_runner.destinos_de, ()),
    ("E15b barrido", threshold_runner.destinos_de, ()),
    ("E13b datos de ajuste", training_runner.destinos_de, ()),
    ("E18 ablación A1", ablation_runner.destinos_de, ("A1",)),
)


@pytest.mark.parametrize(("nombre", "destinos_de", "args"), EJECUTORES)
def test_toda_etiqueta_cambia_todos_los_destinos(nombre, destinos_de, args) -> None:
    """Proteger solo el registro deja expuestas las tablas y las figuras.

    Es el error que ya ocurrió dos veces: la primera con el identificador del
    conjunto, la segunda con el del experimento.
    """
    historicos = destinos_de(*args)
    etiquetados = destinos_de(*args, "una_etiqueta")
    assert set(historicos) == set(etiquetados)
    for clave in historicos:
        assert historicos[clave] != etiquetados[clave], f"{nombre}: {clave} no cambió de ruta"


@pytest.mark.parametrize(("nombre", "destinos_de", "args"), EJECUTORES)
def test_los_destinos_historicos_estan_censados(nombre, destinos_de, args) -> None:
    """Si un artefacto publicado no está en el censo, nada vigila que no cambie."""
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    for clave, ruta in destinos_de(*args).items():
        if not ruta.exists():
            continue
        relativa = str(ruta.relative_to(paths.ROOT))
        assert relativa in declaradas, f"{nombre}: {clave} existe y no está censado"


def test_las_ablaciones_sobre_prueba_exigen_etiqueta() -> None:
    """Repetir E18 sobre prueba sin etiqueta borraría la ejecución publicada."""
    with pytest.raises(ArtefactoOcupadoError, match="su propia etiqueta"):
        ablation_runner.run_ablations("synthetic_v2", particion="test", allow_test=True, reason="x")
