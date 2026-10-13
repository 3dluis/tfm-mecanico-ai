"""Una ejecución nueva no puede pisar un artefacto anterior ni uno histórico.

`tables/`, `figures/`, `data/` y `models/` están fuera del control de versiones,
así que Git no puede avisar de que un artefacto histórico cambió. El censo de
huellas es la única protección posible, y este fichero comprueba que funciona en
los dos sentidos: que detecta un cambio y que no se alarma por un artefacto
nuevo.
"""

from __future__ import annotations

import json
from pathlib import Path

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
    ausentes_por_no_versionarse,
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


def test_el_censo_detecta_un_artefacto_versionado_borrado(tmp_path) -> None:
    """Que falte uno que viaja con el repositorio es otra cosa: algo lo borró."""
    _repositorio_de_prueba(tmp_path)
    (tmp_path / "experiments").mkdir()
    fichero = tmp_path / "experiments" / "E0_registro.json"
    fichero.write_text("{}", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)
    assert (
        json.loads(censo.read_text("utf-8"))["huellas_sha256"]["experiments/E0_registro.json"][
            "versionado"
        ]
        is True
    )

    fichero.unlink()
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert len(desviaciones) == 1
    assert "Git lo lleva" in desviaciones[0].motivo


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
    """Relativas, y presentes **las versionadas**.

    Exigir que estén todas haría fallar este test en un clon recién hecho, que
    es justamente el escenario en que tiene que pasar: las no versionadas
    faltan ahí por diseño.
    """
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    assert all(not ruta.startswith("/") for ruta in declaradas)
    faltan = [
        ruta
        for ruta, entrada in declaradas.items()
        if entrada["versionado"] and not (paths.ROOT / ruta).is_file()
    ]
    assert not faltan, f"artefactos versionados que no están: {faltan}"


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


# --------------------------------------- la etiqueta llega desde la línea de órdenes

#: Todo subcomando que escriba artefactos tiene que aceptar `--etiqueta`. Sin
#: ella el ejecutor se niega a sobrescribir, de modo que un subcomando sin la
#: opción sería un subcomando imposible de reejecutar.
SUBCOMANDOS_QUE_ESCRIBEN = (
    "train-baseline",
    "train-temporal",
    "xai",
    "eval-retrieval",
    "threshold-sweep",
    "training-data",
    "ablations",
)


@pytest.mark.parametrize("subcomando", SUBCOMANDOS_QUE_ESCRIBEN)
def test_el_subcomando_acepta_etiqueta(subcomando: str, capsys) -> None:
    from mecanico_ia_exp.cli import main

    with pytest.raises(SystemExit):
        main([subcomando, "--help"])
    assert "--etiqueta" in capsys.readouterr().out, (
        f"«{subcomando}» escribe artefactos y no se puede etiquetar desde la línea de órdenes: "
        "con los artefactos publicados en su sitio, no habría forma de reejecutarlo"
    )


def test_los_ejemplos_de_ajuste_tambien_llevan_etiqueta() -> None:
    """Proteger el registro de E13b y dejar los .jsonl en ruta fija sería peor que
    no protegerlo: el registro anterior quedaría apuntando a unos ejemplos cuyas
    huellas ya no son las que declara, y eso no se nota."""
    historicos = training_runner.destinos_de()
    etiquetados = training_runner.destinos_de("sin_contaminacion")
    assert set(historicos) == {"registro", "ejemplos_train", "ejemplos_valid"}
    for clave in historicos:
        assert historicos[clave] != etiquetados[clave], f"{clave} no cambió de ruta"


# ------------------------------------------- el censo no absorbe un cambio en silencio


def test_el_censo_se_niega_a_absorber_un_cambio(tmp_path) -> None:
    """Es el modo en que una vigilancia deja de vigilar sin que nadie lo note.

    Si un artefacto censado cambia y después se reescribe el censo para añadir
    otro, la huella alterada pasa a ser la esperada y la verificación posterior
    lo da por intacto.
    """
    (tmp_path / "tables").mkdir()
    vigilado = tmp_path / "tables" / "historico.csv"
    vigilado.write_text("a\n", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)

    vigilado.write_text("ALTERADO\n", encoding="utf-8")
    (tmp_path / "tables" / "nuevo.csv").write_text("b\n", encoding="utf-8")

    with pytest.raises(HistoricoAlteradoError, match="No se reescribe el censo"):
        escribir_censo(censo, raiz=tmp_path)

    # Y la verificación sigue delatándolo: el censo no se tocó.
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert len(desviaciones) == 1
    assert desviaciones[0].motivo.startswith("cambió")


def test_un_cambio_deliberado_se_acepta_pidiendolo(tmp_path) -> None:
    """El caso legítimo existe y tiene que ser explícito, no el camino por omisión."""
    (tmp_path / "tables").mkdir()
    vigilado = tmp_path / "tables" / "historico.csv"
    vigilado.write_text("a\n", encoding="utf-8")
    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)

    vigilado.write_text("cambiado a propósito\n", encoding="utf-8")
    escribir_censo(censo, raiz=tmp_path, aceptar_cambios=True)

    assert verificar_historicos(censo, raiz=tmp_path) == []
    assert json.loads(censo.read_text("utf-8"))["cambios_aceptados_a_proposito"] is True


def test_las_ablaciones_sobre_prueba_son_alcanzables_desde_la_linea_de_ordenes(capsys) -> None:
    """P3 --repetir E18 sobre prueba-- es un pendiente del tutor.

    Si solo se pudiera hacer llamando a Python, el ejecutor estaría protegido y
    el pendiente, inalcanzable por la vía documentada.
    """
    from mecanico_ia_exp.cli import main

    with pytest.raises(SystemExit):
        main(["ablations", "--help"])
    ayuda = capsys.readouterr().out
    for opcion in ("--partition", "--open-test", "--reason", "--etiqueta"):
        assert opcion in ayuda, f"«ablations» no expone {opcion}"


def test_el_registro_de_una_ablacion_guarda_la_particion_y_el_motivo() -> None:
    """Un registro que no dice por qué se abrió prueba no documenta la apertura."""
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    documento = ablation_runner.documento_ablacion(
        "A1",
        modo="oracle",
        oracle=True,
        dataset_id="synthetic_v2",
        umbrales=SufficiencyThresholds(),
        calibracion={},
        casos=[],
        embedding_space_id=None,
        particion="test",
        motivo_de_apertura="P3: ablaciones sobre prueba, pendiente del tutor",
    )
    assert documento["partition"] == "test"
    assert "P3" in documento["test_opening_reason"]


def test_sobre_validacion_no_se_inventa_un_motivo_de_apertura() -> None:
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    documento = ablation_runner.documento_ablacion(
        "A1",
        modo="oracle",
        oracle=True,
        dataset_id="synthetic_v2",
        umbrales=SufficiencyThresholds(),
        calibracion={},
        casos=[],
        embedding_space_id=None,
    )
    assert documento["partition"] == "validation"
    assert documento["test_opening_reason"] is None


def _repositorio_de_prueba(raiz: Path) -> None:
    """Un repositorio mínimo con `tables/` ignorado, como el de verdad.

    Hace falta porque la clasificación la decide `.gitignore`: sin repositorio
    no hay nada que preguntar, y el escenario dejaría de parecerse al real.
    """
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=raiz, check=True)
    (raiz / ".gitignore").write_text("tables/\nfigures/\n", encoding="utf-8")


def test_un_clon_sin_los_ficheros_ignorados_no_da_falsas_alarmas(tmp_path) -> None:
    """Es la comprobación que importa para el tribunal.

    `tables/`, `figures/` y `data/` están en `.gitignore`: un clon recién hecho
    no los tiene. Si su ausencia contara como desviación, la verificación
    fallaría en la máquina de quien evalúa sin que nada estuviera mal, y una
    alarma que salta siempre deja de mirarse.
    """
    _repositorio_de_prueba(tmp_path)
    (tmp_path / "tables").mkdir()
    (tmp_path / "experiments").mkdir()
    no_versionado = tmp_path / "tables" / "E0_salida.csv"
    no_versionado.write_text("a\n", encoding="utf-8")
    versionado = tmp_path / "experiments" / "E0_registro.json"
    versionado.write_text("{}", encoding="utf-8")

    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)
    declaradas = json.loads(censo.read_text("utf-8"))["huellas_sha256"]
    assert declaradas["experiments/E0_registro.json"]["versionado"] is True
    assert declaradas["tables/E0_salida.csv"]["versionado"] is False

    no_versionado.unlink()
    assert verificar_historicos(censo, raiz=tmp_path) == []
    assert ausentes_por_no_versionarse(censo, raiz=tmp_path) == ["tables/E0_salida.csv"]

    versionado.unlink()
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert len(desviaciones) == 1
    assert "Git lo lleva" in desviaciones[0].motivo


def test_el_censo_distingue_lo_que_git_lleva_de_lo_que_no() -> None:
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    versionados = {r for r, e in declaradas.items() if e["versionado"]}
    sin_versionar = set(declaradas) - versionados
    assert versionados, "ningún artefacto censado consta como versionado"
    assert sin_versionar, "ninguno sin versionar: el censo perdería su motivo de existir"
    # Los versionados son exactamente los que un clon trae: los registros, las
    # copias de artifacts/, los manifiestos y los dos ficheros de configuración
    # del adaptador. Lo demás --tables/, figures/, data/-- vive fuera de Git y
    # es la razón por la que este censo existe.
    prefijos = {r.split("/")[0] for r in versionados}
    assert prefijos <= {"experiments", "artifacts", "configs", "models"}, prefijos
    assert {r.split("/")[0] for r in sin_versionar} >= {"tables", "figures"}


def test_ampliar_el_censo_desde_un_clon_no_borra_las_huellas_que_faltan(tmp_path) -> None:
    """Es el modo más silencioso de perder la protección.

    En un clon no están los artefactos no versionados. Si al ampliar el censo se
    reescribiera con solo lo presente, sus huellas desaparecerían y el censo
    saldría más corto sin que nada fallara.
    """
    _repositorio_de_prueba(tmp_path)
    (tmp_path / "tables").mkdir()
    (tmp_path / "experiments").mkdir()
    fuera_de_git = tmp_path / "tables" / "historico.csv"
    fuera_de_git.write_text("a\n", encoding="utf-8")
    (tmp_path / "experiments" / "E0_registro.json").write_text("{}", encoding="utf-8")

    censo = tmp_path / "censo.json"
    escribir_censo(censo, raiz=tmp_path)
    antes = json.loads(censo.read_text("utf-8"))["huellas_sha256"]
    huella_original = antes["tables/historico.csv"]["sha256"]

    # El clon: el fichero ignorado no está, y se añade uno nuevo.
    fuera_de_git.unlink()
    (tmp_path / "experiments" / "E1_registro.json").write_text("{}", encoding="utf-8")
    escribir_censo(censo, raiz=tmp_path)

    despues = json.loads(censo.read_text("utf-8"))["huellas_sha256"]
    assert "experiments/E1_registro.json" in despues, "no se añadió el artefacto nuevo"
    assert "tables/historico.csv" in despues, "se perdió la huella del que no está"
    assert despues["tables/historico.csv"]["sha256"] == huella_original

    # Y si vuelve alterado, se detecta igual que antes.
    fuera_de_git.write_text("ALTERADO\n", encoding="utf-8")
    desviaciones = verificar_historicos(censo, raiz=tmp_path)
    assert len(desviaciones) == 1
    assert desviaciones[0].motivo.startswith("cambió")


def test_el_preprocesado_tambien_lleva_el_conjunto_en_el_nombre() -> None:
    """INC-E5-01: era el único ejecutor que quedaba con rutas fijas.

    Se le pasó por alto porque E5 no produce registro JSON y no aparecía en la
    búsqueda de lo que escribe en `experiments/`. La búsqueda correcta no era
    «qué escribe un registro» sino «qué escribe en una ruta fija».
    """
    from mecanico_ia_exp.experiments import preprocess_runner

    uno = preprocess_runner.destinos_de("synthetic_v2")
    otro = preprocess_runner.destinos_de("synthetic_v4")
    assert set(uno) == set(otro)
    for clave in uno:
        assert uno[clave] != otro[clave], f"{clave} no distingue el conjunto"
    # Y ninguno pisa los artefactos publicados de E5, que van sin sufijo.
    nombres = {ruta.name for ruta in uno.values()}
    assert "E5_estudio_ventana.csv" not in nombres
    assert "E5_reparto.csv" not in nombres
    assert "FIG-E5-01_estudio_ventana.png" not in nombres


def test_generar_sobre_un_conjunto_existente_no_toca_nada(tmp_path, monkeypatch, capsys) -> None:
    """Y falla ANTES de escribir el parquet, no después.

    Si solo se comprobara el manifiesto, una regeneración habría reemplazado ya
    los datos antes de fallar y el manifiesto antiguo habría quedado describiendo
    datos nuevos. Una procedencia que miente es peor que no tenerla.
    """
    from mecanico_ia_exp.cli import main

    crudo = tmp_path / "raw"
    crudo.mkdir()
    datos = crudo / "ya_existe.parquet"
    datos.write_bytes(b"contenido original")
    antes = datos.read_bytes()

    monkeypatch.setattr(paths, "DATA_RAW_SYNTHETIC", crudo)
    codigo = main(["generate-synthetic", "--dataset-id", "ya_existe", "--sessions-per-fault", "4"])
    assert codigo == 1
    assert datos.read_bytes() == antes, "el parquet existente se tocó"
    assert "No se escribe nada" in capsys.readouterr().out


def test_el_conjunto_oficial_no_se_puede_regenerar_por_descuido() -> None:
    """`synthetic_v2` sostiene las cifras de E6, E7, E9, E15 y E19."""
    from mecanico_ia_exp.cli import main

    if not (paths.DATA_RAW_SYNTHETIC / "synthetic_v2.parquet").is_file():
        pytest.skip("este clon no trae synthetic_v2")
    assert main(["generate-synthetic", "--dataset-id", "synthetic_v2"]) == 1


def test_los_guiones_de_reproduccion_usan_etiqueta() -> None:
    """Comparar con `git diff` exigía sobrescribir el registro publicado.

    Es decir, destruir el resultado para comprobar que se reproduce. Los guiones
    escriben ahora con etiqueta y comparan los dos ficheros.
    """
    for nombre in ("reproduce_baseline.sh", "reproduce_main_results.sh"):
        guion = (paths.ROOT / "scripts" / nombre).read_text("utf-8")
        assert "--etiqueta" in guion, f"{nombre} no etiqueta sus ejecuciones"
        assert "comparar_registro.py" in guion, f"{nombre} no compara con el publicado"


def test_el_comparador_ignora_lo_que_cambia_en_toda_reejecucion(tmp_path) -> None:
    import subprocess
    import sys

    base = {"commit": "aaa", "executed_at": "2026-01-01", "metrics": {"macro_f1": 0.8788}}
    otro = {"commit": "bbb", "executed_at": "2026-02-02", "metrics": {"macro_f1": 0.8788}}
    uno, dos = tmp_path / "a.json", tmp_path / "b.json"
    uno.write_text(json.dumps(base), encoding="utf-8")
    dos.write_text(json.dumps(otro), encoding="utf-8")

    resultado = subprocess.run(
        [sys.executable, str(paths.ROOT / "scripts" / "comparar_registro.py"), str(uno), str(dos)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stdout
    assert "REPRODUCIDO" in resultado.stdout

    # Un campo nuevo en el reproducido no es una diferencia: el esquema crece.
    dos.write_text(json.dumps({**otro, "protocolo": "E6_v1"}), encoding="utf-8")
    resultado = subprocess.run(
        [sys.executable, str(paths.ROOT / "scripts" / "comparar_registro.py"), str(uno), str(dos)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stdout
    assert "crecido el esquema" in resultado.stdout

    dos.write_text(json.dumps({**otro, "metrics": {"macro_f1": 0.5}}), encoding="utf-8")
    resultado = subprocess.run(
        [sys.executable, str(paths.ROOT / "scripts" / "comparar_registro.py"), str(uno), str(dos)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 1
    assert "DIFIERE metrics.macro_f1" in resultado.stdout


def test_las_reejecuciones_de_suficiencia_tambien_se_etiquetan() -> None:
    """E15 y E13 escribían en rutas fijas por modo: una reproducción las pisaba."""
    from mecanico_ia_exp.experiments.sufficiency_runner import sufijo_artefacto

    for modo in ("oracle", "non_oracle", "adverse"):
        sin = sufijo_artefacto(modo)
        con = sufijo_artefacto(modo, etiqueta="reproduccion")
        assert con != sin, f"el modo {modo} no distingue la ejecución"
        assert con.endswith("_reproduccion")


def test_el_registro_publicado_del_agente_conserva_su_nombre() -> None:
    """`E13_agente_<llm>.json` es el que cita el capítulo: no puede cambiar."""
    from mecanico_ia_exp.experiments.sufficiency_runner import destinos_de

    publicado = destinos_de("oracle", llm="transformers-lora@slm_lora_v2")
    assert publicado["registro"].name == "E15_suficiencia.json"
    assert publicado["agente"].name == "E13_agente_transformers-lora@slm_lora_v2.json"


def test_el_modo_distingue_el_registro_del_agente() -> None:
    """Una redacción no oracular parte de otra evidencia y puede decidir distinto.

    Sin el modo en el nombre, la segunda ejecución sobrescribía a la primera en
    silencio aunque sus decisiones difirieran.
    """
    from mecanico_ia_exp.experiments.sufficiency_runner import destinos_de

    llm = "transformers-lora@slm_lora_v2"
    oracular = destinos_de("oracle", llm=llm)["agente"]
    no_oracular = destinos_de("non_oracle", llm=llm)["agente"]
    assert oracular != no_oracular
    assert "non_oracle" in no_oracular.name


def test_la_ficha_del_conjunto_no_se_censa_porque_lleva_marca_de_tiempo() -> None:
    """`created_at` cambia en toda reconstrucción legítima.

    Censarla daría una alarma cada vez que alguien reconstruye el conjunto, y
    una alarma que salta siempre deja de mirarse. Lo que se vigila es el
    parquet, que sí es reproducible bit a bit.
    """
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    fichas = [r for r in declaradas if r.endswith(".meta.json") and "data/raw" in r]
    assert not fichas, f"censadas fichas con marca de tiempo: {fichas}"
    parquets = [r for r in declaradas if r.endswith(".parquet") and "data/raw" in r]
    assert parquets, "el parquet sí tiene que estar censado: es el dato"


def test_los_dos_incidentes_de_artefactos_siguen_documentados() -> None:
    """No se borran del historial aunque estén resueltos.

    Los dos los causó el trabajo sobre el repositorio y los detectó el censo. Un
    repositorio que se entrega como evidencia no esconde sus propios errores.
    """
    for nombre, marca in (
        ("incidencia-artefactos-e5.md", "INC-E5-01"),
        ("incidencia-artefactos-e15.md", "INC-E15-01"),
    ):
        documento = paths.DOCS / "experiments" / nombre
        assert documento.is_file(), f"falta {nombre}"
        texto = documento.read_text("utf-8")
        assert marca in texto
        assert "no se declara" in texto.lower() or "no restaurada" in texto.lower()


def test_el_procedimiento_de_reconstruccion_esta_documentado() -> None:
    """Una prueba que necesita recursos externos tiene que decir cómo obtenerlos."""
    documento = paths.DOCS / "reproducir-desde-cero.md"
    assert documento.is_file()
    texto = documento.read_text("utf-8")
    for pieza in ("reconstruir_datos.sh", "esquema historico", "no se puede reproducir"):
        assert pieza in texto, f"el procedimiento no explica «{pieza}»"
    for guion in ("scripts/reconstruir_datos.sh", "scripts/verificar_reconstruccion.py"):
        assert (paths.ROOT / guion).is_file(), f"falta {guion}"


def test_un_artefacto_recien_creado_cuenta_como_versionado(tmp_path) -> None:
    """Antes de confirmarse, Git todavía no lo sigue; pero `.gitignore` no lo
    excluye, de modo que viajará con el repositorio.

    Preguntar por el índice lo habría marcado como no versionado y el censo
    habría aceptado su desaparición en silencio. Es lo que pasó con los cuatro
    registros de P3: el censo se construyó antes del commit.
    """
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("tables/\n", encoding="utf-8")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "tables").mkdir()
    # Ninguno de los dos está confirmado todavía.
    (tmp_path / "experiments" / "E0_nuevo.json").write_text("{}", encoding="utf-8")
    (tmp_path / "tables" / "E0_nueva.csv").write_text("x\n", encoding="utf-8")

    censo = censar(("experiments/*.json", "tables/*.csv"), raiz=tmp_path)
    assert censo["experiments/E0_nuevo.json"]["versionado"] is True
    assert censo["tables/E0_nueva.csv"]["versionado"] is False


def test_los_registros_de_p3_estan_censados_como_versionados() -> None:
    declaradas = json.loads(REGISTRO_HISTORICO.read_text("utf-8"))["huellas_sha256"]
    for ablacion in ("A1", "A2", "A3", "A4"):
        clave = f"experiments/E18_ablacion_{ablacion}_prueba.json"
        assert clave in declaradas, f"{clave} sin censar"
        assert declaradas[clave]["versionado"] is True, f"{clave} marcado como no versionado"


def test_la_comprobacion_de_contaminacion_no_abre_el_conjunto_de_prueba() -> None:
    """Una apertura innecesaria gasta lo único que no se repone.

    La primera versión cargaba la partición de prueba para leer identificadores
    de sesión que ya estaban en el manifiesto del preprocesado. Quedó registrada
    como la quinta apertura y se corrigió en el acto.
    """
    fuente = (
        paths.ROOT / "src" / "mecanico_ia_exp" / "experiments" / "training_runner.py"
    ).read_text("utf-8")
    inicio = fuente.index("def exigir_particion_de_ajuste_limpia(")
    cuerpo = fuente[inicio : fuente.index("def run_training_data(")]
    assert "load_partition" not in cuerpo, (
        "la comprobación de contaminación carga una partición; el reparto está en "
        "<dataset>_preprocess.json y no hace falta abrir nada"
    )
    assert "split_assignment" in cuerpo


def test_los_ejemplos_de_ajuste_declaran_su_particion() -> None:
    """Un conjunto de ajuste que no dice de dónde salen sus ejemplos no permite
    saber si contamina."""
    import json as _json

    registro = paths.EXPERIMENTS / "E13b_training_data_sin_contaminacion.json"
    if not registro.is_file():
        pytest.skip("P2 todavía no ha generado el conjunto sin contaminación")
    d = _json.loads(registro.read_text("utf-8"))
    assert d["examples_partition"] == "train"
    assert "ninguna sesión" in d["contamination_check"]


# ------------------------------------- la congelacion del adaptador ata los datos


def _finetune(*args: str, capsys) -> tuple[int, str]:
    from mecanico_ia_exp.cli import main

    codigo = main(["finetune-slm", *args])
    return codigo, capsys.readouterr().out


def test_ajustar_con_otros_datos_se_niega(capsys) -> None:
    """Comprobar las huellas y después ajustar con otro directorio produciría un
    adaptador que no es el congelado con apariencia de serlo."""
    codigo, salida = _finetune("--adapter-dir", "slm_lora_v3", "--epochs", "4", capsys=capsys)
    assert codigo == 1
    assert "No se ajusta nada" in salida
    assert "otros datos" in salida


def test_ajustar_con_otro_numero_de_epocas_se_niega(capsys) -> None:
    """El criterio de parada es parte del experimento congelado."""
    codigo, salida = _finetune(
        "--datos",
        "sin_contaminacion",
        "--adapter-dir",
        "slm_lora_v3",
        "--epochs",
        "1",
        capsys=capsys,
    )
    assert codigo == 1
    assert "congela 4 épocas" in salida


def test_no_se_sobrescribe_un_adaptador_existente(capsys) -> None:
    codigo, salida = _finetune("--adapter-dir", "slm_lora_v2", capsys=capsys)
    assert codigo == 1
    assert "no se sobrescribe" in salida


def test_la_congelacion_declara_lo_que_el_codigo_comprueba() -> None:
    """Una promesa escrita y no implementada es peor que no escribirla."""
    congelacion = json.loads((paths.CONFIGS / "congelacion-adaptador-v3.json").read_text("utf-8"))
    assert congelacion["datos_de_ajuste"]["huellas_sha256_16"]
    assert congelacion["hiperparametros"]["epochs"]
    assert "preparados" in congelacion["datos_de_ajuste"]["ficheros"]
    fuente = (paths.ROOT / "src" / "mecanico_ia_exp" / "cli.py").read_text("utf-8")
    for pieza in ("huellas_sha256_16", "hiperparametros", "directorio_congelado"):
        assert pieza in fuente, f"la congelación declara «{pieza}» y el código no lo comprueba"


# ------------------------------- las tres categorias de prueba, comprobables


def test_cada_prueba_cae_en_una_sola_categoria() -> None:
    """Una prueba sin categoría falla en silencio en un clon.

    El riesgo concreto: añadir una prueba que necesite el conjunto y olvidar el
    marcador. En esta máquina pasaría; en la del tribunal, no, y parecería que el
    repositorio está roto.
    """
    import subprocess

    marcadores = ("conjunto", "notebook", "db", "llm", "slow")
    sin = " and ".join(f"not {m}" for m in marcadores)

    def cuenta(expresion: str) -> int:
        salida = subprocess.run(
            ["uv", "run", "pytest", "--collect-only", "-q", "-m", expresion],
            capture_output=True,
            text=True,
            cwd=paths.ROOT,
            check=False,
        ).stdout
        return sum(
            int(linea.rsplit(":", 1)[-1].strip())
            for linea in salida.splitlines()
            if ".py:" in linea and linea.rsplit(":", 1)[-1].strip().isdigit()
        )

    inmediatas = cuenta(sin)
    preparacion = cuenta("conjunto or notebook")
    externas = cuenta("db or llm or slow")
    todas = cuenta("")
    assert inmediatas + preparacion + externas == todas, (
        f"{todas - inmediatas - preparacion - externas} prueba(s) en más de una categoría o "
        "en ninguna"
    )


def test_el_guion_de_estado_de_pruebas_existe_y_declara_las_tres() -> None:
    guion = paths.ROOT / "scripts" / "estado_pruebas.py"
    assert guion.is_file()
    texto = guion.read_text("utf-8")
    for categoria in ("inmediatas", "con preparación", "con recursos externos"):
        assert categoria in texto
    # Y no declara satisfactoria una categoría que no ha ejecutado.
    assert "no se han ejecutado" in texto
