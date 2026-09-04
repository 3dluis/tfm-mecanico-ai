"""Aislamiento del espacio de embeddings: `MIXED-EMBEDDING-SPACE`.

El índice contiene dos vectores por fragmento, de dos modelos distintos. Que
convivan es deliberado; que una búsqueda no diga en cuál busca, no.

**Por qué estas pruebas se escriben así.** Ya existía una garantía documentada de
que la búsqueda filtraba, respaldada por un test que **pasaba el parámetro a
mano**. Esa prueba pasaba y el defecto estaba vivo, porque la ruta real no lo
pasaba. Aquí se comprueba la ruta real: qué llega a la capa de almacenamiento
cuando la llaman los ejecutores, no cuando la llama un test.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from mecanico_ia_exp.rag.store import RetrievedChunk

RAIZ = Path(__file__).resolve().parents[1] / "src" / "mecanico_ia_exp"

#: Los cuatro puntos desde los que se recupera en producción.
LLAMANTES = (
    RAIZ / "experiments" / "retrieval_runner.py",
    RAIZ / "experiments" / "sufficiency_runner.py",
    RAIZ / "experiments" / "training_runner.py",
)


class StoreEspia:
    """Registra con qué espacio se le pidió buscar, y devuelve algo plausible."""

    def __init__(self) -> None:
        self.modelos: list[str | None] = []

    def search(self, query_vector: Any, **kwargs: Any) -> list[RetrievedChunk]:
        self.modelos.append(kwargs.get("embedding_model"))
        return []

    def chunks_for_dtc(self, *a: Any, **k: Any) -> tuple[str, ...]:
        return ()

    def chunks_for_files(self, *a: Any, **k: Any) -> tuple[str, ...]:
        return ()


class ProveedorFalso:
    """Un proveedor con identidad, como los reales."""

    class _Id:
        provider = "sentence-transformers"
        model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        dimension = 384
        version = "1"

    identity = _Id()

    def embed(self, textos: list[str]) -> np.ndarray:
        return np.zeros((len(textos), 384), dtype=np.float32)


# --- 1 · La ruta real declara el espacio ---------------------------------------


@pytest.mark.parametrize(
    "estrategia", ["semantic", "diagnosis-guided", "hybrid", "semantic+authority"]
)
def test_toda_estrategia_declara_el_espacio_en_que_busca(estrategia: str) -> None:
    """Ninguna consulta puede llegar a la base sin decir en qué espacio busca.

    Es la prueba que faltaba: ejercita `recuperar()` como lo llaman los
    ejecutores y mira qué recibe la capa de almacenamiento.
    """
    from mecanico_ia_exp.experiments.retrieval_runner import recuperar

    espia = StoreEspia()
    recuperar(
        estrategia,
        store=espia,  # type: ignore[arg-type]
        provider=ProveedorFalso(),  # type: ignore[arg-type]
        caso={"case_id": "T01", "fault_id": "F01_vacuum_leak", "query": "fuel trim high"},
        vehicle_id="mazda-3-bk-2007",
        engine_code="Z6",
    )
    assert espia.modelos, "la estrategia no llegó a buscar"
    assert None not in espia.modelos, (
        f"{estrategia}: {espia.modelos.count(None)} de {len(espia.modelos)} búsquedas "
        "sin espacio declarado; mezclarían dos modelos en una misma ordenación"
    )


def test_el_espacio_declarado_es_el_del_proveedor_que_vectoriza_la_consulta() -> None:
    """Consulta e índice en el mismo espacio **por construcción**.

    Si el modelo se pasara como una constante escrita aparte, podría divergir del
    proveedor sin que nada lo notara.
    """
    from mecanico_ia_exp.experiments.retrieval_runner import recuperar

    espia, proveedor = StoreEspia(), ProveedorFalso()
    recuperar(
        "semantic",
        store=espia,  # type: ignore[arg-type]
        provider=proveedor,  # type: ignore[arg-type]
        caso={"case_id": "T01", "fault_id": "F01_vacuum_leak", "query": "fuel trim high"},
        vehicle_id="mazda-3-bk-2007",
        engine_code="Z6",
    )
    assert set(espia.modelos) == {proveedor.identity.model}


# --- 2 · El defecto es imposible, no improbable ---------------------------------


def test_buscar_sin_declarar_el_espacio_es_un_error() -> None:
    """`embedding_model` deja de tener valor por defecto.

    Con un parámetro opcional el defecto reaparece la próxima vez que alguien
    añada una llamada y lo olvide. Sin valor por defecto, no compila.
    """
    import inspect

    from mecanico_ia_exp.rag.store import PgVectorStore, VectorStore

    for clase in (VectorStore, PgVectorStore):
        parametro = inspect.signature(clase.search).parameters["embedding_model"]
        assert parametro.default is inspect.Parameter.empty, (
            f"{clase.__name__}.search tiene `embedding_model` opcional: "
            "una búsqueda sin espacio declarado vuelve a ser posible"
        )


def test_ningun_punto_de_llamada_omite_el_espacio() -> None:
    """Comprobación estática de las tres rutas: suficiencia, recuperación, ajuste.

    Complementa a la prueba dinámica: cubre puntos de llamada que un test podría
    no ejercitar, y falla al añadir uno nuevo que olvide el parámetro.
    """
    omisiones: list[str] = []
    for fichero in LLAMANTES:
        arbol = ast.parse(fichero.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Call):
                continue
            nombre = getattr(nodo.func, "attr", None) or getattr(nodo.func, "id", None)
            if nombre not in ("search", "recuperar"):
                continue
            claves = {k.arg for k in nodo.keywords if k.arg}
            if "embedding_model" not in claves and not any(k.arg is None for k in nodo.keywords):
                omisiones.append(f"{fichero.name}:{nodo.lineno} {nombre}()")
    assert not omisiones, "puntos de llamada sin espacio declarado: " + ", ".join(omisiones)


# --- 3 · Efecto observable del defecto -----------------------------------------


def test_un_indice_con_dos_modelos_duplica_cada_fragmento() -> None:
    """Reproduce el efecto: sin filtro, cada fragmento compite dos veces.

    Es lo que se observa en los artefactos congelados: 24 de 150 posiciones del
    resultado vigente están ocupadas por un fragmento ya presente.
    """
    indice = [
        {"chunk_id": "ch1", "embedding_model": "A", "score": 0.9},
        {"chunk_id": "ch1", "embedding_model": "B", "score": 0.4},
        {"chunk_id": "ch2", "embedding_model": "A", "score": 0.7},
        {"chunk_id": "ch2", "embedding_model": "B", "score": 0.6},
    ]
    sin_filtro = sorted(indice, key=lambda r: -r["score"])[:3]
    assert len({r["chunk_id"] for r in sin_filtro}) < len(sin_filtro), (
        "sin declarar el espacio, un fragmento ocupa dos posiciones del resultado"
    )
    con_filtro = sorted(
        (r for r in indice if r["embedding_model"] == "A"), key=lambda r: -r["score"]
    )
    assert len({r["chunk_id"] for r in con_filtro}) == len(con_filtro)
