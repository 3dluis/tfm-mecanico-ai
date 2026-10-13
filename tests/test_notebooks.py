"""Validación automática de los notebooks que se entregan como evidencia.

Un notebook que se entrega al tribunal es un documento **y** un programa. Como
documento tiene que poder leerse sin ejecutarlo; como programa tiene que
ejecutarse desde un kernel limpio en una máquina que no es la del autor. Este
fichero comprueba las dos cosas, y una tercera que es la que de verdad importa:
que **las cifras del notebook coincidan con los artefactos** de los que dicen
salir.

## Qué se comprueba, y por qué cada cosa

* **Integridad y estructura.** Que el JSON es un notebook válido y que lleva las
  sesiones obligatorias. Un notebook sin sección de limitaciones no es un
  documento científico, por bien que ejecute.
* **Portabilidad.** Ni rutas absolutas, ni directorios personales, ni secretos.
  Un notebook con `/Users/alguien/` funciona en una máquina y en ninguna otra.
* **Protección de lo congelado.** Que ninguna celda escriba en `experiments/`,
  `tables/`, `figures/` o `data/`, y que el censo de artefactos históricos siga
  intacto después de ejecutarlos.
* **Ejecución desde cero.** Con kernel limpio y uno por uno. Un notebook que
  solo funciona porque antes se ejecutó otro no es reproducible, y el tribunal
  los abrirá en el orden que quiera.
* **Coherencia con los artefactos.** Que las cifras que el notebook enseña sean
  las de los registros. Es lo que separa un documento de evidencia de una
  presentación.

Los que ejecutan de verdad están marcados `notebook`: tardan minutos y se dejan
fuera del ciclo rápido con `-m "not notebook"`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import nbformat
import pytest

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.experiments.destinos import verificar_historicos

NOTEBOOKS = paths.ROOT / "notebooks"

#: Los notebooks de la primera entrega: escritos completos y ejecutables sin
#: servicios externos. Los heredados siguen en el directorio y se comprueban
#: solo en lo estructural, porque son plantillas pendientes de desarrollar.
ENTREGADOS: tuple[str, ...] = (
    "00_introduccion.ipynb",
    "01_exploracion_obd.ipynb",
    "02_comparacion_modelos.ipynb",
    "03_analisis_e19.ipynb",
    "04_explicabilidad.ipynb",
    "05_suficiencia_y_abstencion.ipynb",
)

#: Secciones que todo notebook entregado tiene que llevar. No se exige la
#: numeración exacta --cada experimento ordena a su manera-- sino que el
#: contenido esté.
SECCIONES_OBLIGATORIAS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("identificación del experimento", ("**Experimento", "**Experimentos")),
    ("pregunta de investigación", ("Pregunta de investigación", "pregunta de investigación")),
    ("objetivo", ("Objetivo", "objetivo")),
    ("datos", ("Conjunto", "conjunto")),
    ("metodología", ("Metodología", "metodología", "Fundamento", "Preparación del entorno")),
    ("resultados", ("Resultado", "resultado")),
    ("interpretación", ("Qué podemos interpretar", "Qué podemos interpretar")),
    ("limitaciones", ("Qué no podemos afirmar", "Limitaciones", "limitaciones")),
    ("resultados negativos", ("negativ",)),
    ("reproducibilidad", ("Reproducibilidad", "reproducibilidad")),
    ("referencias y trazabilidad", ("Referencias", "trazabilidad")),
    ("conclusiones", ("Conclusiones", "conclusiones")),
)

#: Lo que delata un notebook atado a una máquina concreta.
PATRONES_LOCALES: tuple[tuple[str, str], ...] = (
    (r"/Users/[A-Za-z0-9_.-]+", "ruta de un directorio personal de macOS"),
    (r"/home/[A-Za-z0-9_.-]+", "ruta de un directorio personal de Linux"),
    (r"[A-Z]:\\\\", "ruta absoluta de Windows"),
    (r"/private/tmp/", "ruta temporal de la máquina del autor"),
    (r"localhost:\d{4}", "servicio local con puerto fijo"),
)

#: Lo que delata una credencial. Se busca el patrón, no el valor: encontrar uno
#: de verdad sería ya tarde.
PATRONES_SECRETO: tuple[tuple[str, str], ...] = (
    (r"(?i)\b(api[_-]?key|secret|passwd|password|token)\s*=\s*['\"][^'\"]{8,}", "credencial"),
    (r"sk-[A-Za-z0-9]{20,}", "clave de API"),
    (r"postgres(ql)?://[^\\s'\"]*:[^\\s'\"@]+@", "cadena de conexión con contraseña"),
)

#: Directorios donde ningún notebook puede escribir.
PROHIBIDO_ESCRIBIR: tuple[str, ...] = (
    "paths.EXPERIMENTS",
    "paths.TABLES",
    "paths.FIGURES",
    "paths.DATA_RAW",
    "paths.DATA_PROCESSED",
    "paths.MODELS",
)


def _cargar(nombre: str) -> nbformat.NotebookNode:
    return nbformat.read(NOTEBOOKS / nombre, as_version=4)


def _texto(nb: nbformat.NotebookNode, tipo: str) -> str:
    return "\n".join("".join(c["source"]) for c in nb.cells if c["cell_type"] == tipo)


# ------------------------------------------------------------- lo estructural


def test_estan_los_cuatro_notebooks_de_la_entrega() -> None:
    faltan = [n for n in ENTREGADOS if not (NOTEBOOKS / n).is_file()]
    assert not faltan, f"faltan notebooks de la entrega: {faltan}"


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_el_json_es_un_notebook_valido(nombre: str) -> None:
    nbformat.validate(_cargar(nombre))


@pytest.mark.parametrize("nombre", sorted(p.name for p in NOTEBOOKS.glob("*.ipynb")))
def test_todo_notebook_del_repositorio_es_json_valido(nombre: str) -> None:
    """También los heredados: un JSON roto rompe Jupyter al abrirlo."""
    nbformat.validate(nbformat.read(NOTEBOOKS / nombre, as_version=4))


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_lleva_todas_las_secciones_obligatorias(nombre: str) -> None:
    texto = _texto(_cargar(nombre), "markdown")
    faltan = [
        seccion
        for seccion, marcas in SECCIONES_OBLIGATORIAS
        if not any(marca in texto for marca in marcas)
    ]
    assert not faltan, f"{nombre} no cubre: {faltan}"


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_declara_su_modalidad(nombre: str) -> None:
    """Las cuatro modalidades no son intercambiables y hay que decir cuál es."""
    assert "declarar_modalidad" in _texto(_cargar(nombre), "code"), (
        f"{nombre} no declara si reproduce, reanaliza, visualiza evidencia o ilustra"
    )


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_todo_grafico_lleva_su_interpretacion(nombre: str) -> None:
    """Un gráfico sin las tres lecturas es un adorno.

    Se cuentan las llamadas a ``exportar`` --toda figura del notebook pasa por
    ahí-- y se exige al menos tantos bloques de interpretación como figuras.
    """
    nb = _cargar(nombre)
    figuras = _texto(nb, "code").count("soporte.exportar(")
    if not figuras:
        pytest.skip("este notebook no produce figuras")
    markdown = _texto(nb, "markdown")
    for apartado in ("**Qué muestra", "**Qué podemos interpretar", "**Qué no podemos afirmar"):
        encontrados = markdown.count(apartado)
        assert encontrados >= figuras, (
            f"{nombre}: {figuras} figura(s) y solo {encontrados} «{apartado}»"
        )


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_no_se_entrega_con_salidas_guardadas(nombre: str) -> None:
    """Las salidas de la máquina del autor pasarían por las del lector."""
    con_salida = [
        i
        for i, c in enumerate(_cargar(nombre).cells)
        if c["cell_type"] == "code" and c.get("outputs")
    ]
    assert not con_salida, f"{nombre} trae salidas guardadas en las celdas {con_salida}"


# ------------------------------------------------------------- portabilidad


@pytest.mark.parametrize("nombre", sorted(p.name for p in NOTEBOOKS.glob("*.ipynb")))
def test_sin_rutas_locales(nombre: str) -> None:
    contenido = (NOTEBOOKS / nombre).read_text("utf-8")
    encontrados = [
        f"{descripcion}: {m.group(0)}"
        for patron, descripcion in PATRONES_LOCALES
        for m in re.finditer(patron, contenido)
    ]
    assert not encontrados, f"{nombre} no es portable: {encontrados[:4]}"


@pytest.mark.parametrize("nombre", sorted(p.name for p in NOTEBOOKS.glob("*.ipynb")))
def test_sin_secretos(nombre: str) -> None:
    contenido = (NOTEBOOKS / nombre).read_text("utf-8")
    encontrados = [
        descripcion for patron, descripcion in PATRONES_SECRETO if re.search(patron, contenido)
    ]
    assert not encontrados, f"{nombre} parece contener {encontrados}"


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_la_raiz_se_resuelve_sin_ruta_absoluta(nombre: str) -> None:
    codigo = _texto(_cargar(nombre), "code")
    assert "Path.cwd()" in codigo, f"{nombre} no ancla la raíz de forma relativa"


# ------------------------------------------------ protección de lo congelado


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_ningun_notebook_escribe_donde_viven_los_artefactos(nombre: str) -> None:
    """La garantía no es la buena intención: es que la ruta de salida sea otra."""
    codigo = _texto(_cargar(nombre), "code")
    escrituras = re.findall(
        r"(?:to_csv|to_parquet|write_text|write_bytes|savefig|np\.save)\(", codigo
    )
    if not escrituras:
        return
    for prohibido in PROHIBIDO_ESCRIBIR:
        assert prohibido not in codigo, (
            f"{nombre} menciona {prohibido} y escribe: podría pisar un artefacto histórico"
        )


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_no_reejecuta_experimentos_congelados(nombre: str) -> None:
    """E19 se midió una vez. Ningún notebook puede volver a medirla."""
    codigo = _texto(_cargar(nombre), "code")
    for prohibida in ("run_final_evaluation", "ejecutar_e19", "allow_test=True"):
        assert prohibida not in codigo, f"{nombre} invoca {prohibida}"


def test_los_artefactos_historicos_siguen_intactos() -> None:
    """Se ejecuta después de los notebooks en el mismo lote: si alguno tocó un
    artefacto congelado, el censo lo delata."""
    desviaciones = verificar_historicos()
    assert not desviaciones, f"artefactos alterados: {[str(d) for d in desviaciones][:5]}"


# ----------------------------------------- coherencia entre cifras y artefactos


def test_las_cifras_de_e19_del_notebook_salen_de_su_artefacto() -> None:
    """0/14, 2/8 y 6/10 tienen que poder recalcularse desde la tabla congelada.

    Es la comprobación que convierte el notebook en evidencia: si la tabla
    cambiara, esto fallaría antes de que nadie citara una cifra obsoleta.
    """
    import pandas as pd

    tabla = pd.read_csv(paths.ROOT / "artifacts" / "tables" / "E19_evaluacion_final_v3.csv")
    operativo = tabla[tabla.stratum == "operativo"]

    abstenerse = operativo[operativo.expected_decision == "ABSTAIN"]
    explicar = operativo[operativo.expected_decision == "EXPLAIN"]
    completa = operativo[operativo.corpus_variant == "FULL"]

    assert len(abstenerse) == 14
    assert len(explicar) == 8
    assert len(completa) == 10
    assert len(abstenerse[abstenerse.decision == "EXPLAIN"]) == 0, "falsa confianza"
    assert len(explicar[explicar.decision == "ABSTAIN"]) == 2, "abstención innecesaria"
    assert len(completa[completa.decision == "EXPLAIN"]) == 6, "cobertura"
    assert operativo.window_id.nunique() == 10
    assert operativo.session_id.nunique() == 10


def test_las_cifras_de_e6_y_e7_siguen_siendo_las_citadas() -> None:
    """Los notebooks las leen del registro, pero el texto cita algunas.

    Si un registro cambiara, el texto quedaría obsoleto en silencio. Esto lo
    impide.
    """
    e6 = json.loads((paths.EXPERIMENTS / "E6_baseline_synthetic_v2.json").read_text("utf-8"))
    e7 = json.loads((paths.EXPERIMENTS / "E7_temporal_synthetic_v2.json").read_text("utf-8"))
    assert e6["metrics"]["macro_f1"] == pytest.approx(0.8788, abs=1e-4)
    assert e7["metrics"]["macro_f1"] == pytest.approx(0.8230, abs=1e-4)
    assert e6["majority_baseline"]["macro_f1"] == pytest.approx(0.0741, abs=1e-4)

    texto = "\n".join(
        "".join(c["source"])
        for n in ENTREGADOS
        for c in _cargar(n).cells
        if c["cell_type"] == "markdown"
    )
    for cifra in ("0,8788", "0,8230", "0,0741"):
        assert cifra in texto, f"la cifra {cifra} dejó de citarse: revisar el texto"


def test_los_artefactos_que_los_notebooks_leen_existen() -> None:
    """Un notebook que pide una tabla que no se versiona falla en el tribunal."""
    necesarios = [
        paths.ROOT / "data" / "samples" / "synthetic_sample.parquet",
        paths.ROOT / "artifacts" / "tables" / "E19_evaluacion_final_v3.csv",
        paths.ROOT / "artifacts" / "tables" / "E5_estudio_ventana.csv",
        paths.ROOT / "artifacts" / "tables" / "E5_reparto.csv",
        paths.ROOT / "artifacts" / "figures" / "FIG-E4-01_series_normal_vs_fallo.png",
        paths.EXPERIMENTS / "E19_anotacion_v3.json",
    ]
    faltan = [str(p.relative_to(paths.ROOT)) for p in necesarios if not p.is_file()]
    assert not faltan, f"los notebooks leen artefactos que no están versionados: {faltan}"


# --------------------------------------------------- ejecución desde un kernel limpio


@pytest.mark.notebook
@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_se_ejecuta_entero_desde_un_kernel_limpio(nombre: str, tmp_path: Path) -> None:
    """Uno por uno, con kernel propio y sin estado de ningún otro.

    Que un notebook dependa de variables definidas en otro es el modo más común
    de que funcione en la máquina del autor y falle en la del tribunal, que los
    abrirá en el orden que quiera.
    """
    from nbclient import NotebookClient

    nb = _cargar(nombre)
    cliente = NotebookClient(
        nb,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOKS)}},
    )
    cliente.execute()

    errores = [
        (i, s.get("ename"), s.get("evalue"))
        for i, c in enumerate(nb.cells)
        if c["cell_type"] == "code"
        for s in c.get("outputs", [])
        if s.get("output_type") == "error"
    ]
    assert not errores, f"{nombre} falló: {errores[:2]}"


@pytest.mark.parametrize("nombre", ENTREGADOS)
def test_la_raiz_se_encuentra_desde_cualquier_directorio(nombre: str, tmp_path: Path) -> None:
    """El tribunal abrirá Jupyter donde quiera, no necesariamente en la raíz.

    El preámbulo anterior suponía dos únicos casos --la raíz o `notebooks/`-- y
    en cualquier otro directorio el import fallaba.
    """
    import subprocess
    import sys

    preambulo = next(
        "".join(c["source"])
        for c in _cargar(nombre).cells
        if c["cell_type"] == "code" and "_raiz_del_repositorio" in "".join(c["source"])
    )
    for desde in (paths.ROOT, NOTEBOOKS, paths.ROOT / "docs" / "diseno-pi1", paths.ROOT / "src"):
        resultado = subprocess.run(
            [sys.executable, "-c", preambulo],
            cwd=desde,
            capture_output=True,
            text=True,
            check=False,
        )
        assert resultado.returncode == 0, f"{nombre} desde {desde}: {resultado.stderr[-300:]}"
        assert "python" in resultado.stdout


@pytest.mark.parametrize("nombre", sorted(p.name for p in NOTEBOOKS.glob("*.ipynb")))
def test_ningun_notebook_lee_de_un_directorio_que_un_clon_no_trae(nombre: str) -> None:
    """`tables/` y `figures/` están fuera de Git: un clon no los tiene.

    Leer de ahí hace que el notebook funcione en la máquina del autor y falle en
    la del tribunal, que es el modo de fallo que toda esta entrega existe para
    evitar. `artifacts/` es la copia versionada.
    """
    codigo = _texto(_cargar(nombre), "code")
    for prohibido in ("paths.TABLES", "paths.FIGURES", "paths.DATA_RAW_SYNTHETIC"):
        assert prohibido not in codigo, (
            f"{nombre} lee de {prohibido}, que un clon recién hecho no trae; "
            "usa artifacts/ o soporte.tabla()/soporte.figura()"
        )
