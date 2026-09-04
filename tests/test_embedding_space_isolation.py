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

    def search_lexical(self, *a: Any, **k: Any) -> list[RetrievedChunk]:
        """La rama léxica de la fusión híbrida no usa vectores: no lleva espacio."""
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

    def embed_one(self, texto: str) -> np.ndarray:
        return np.zeros(384, dtype=np.float32)


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


def test_ninguna_busqueda_vectorial_omite_el_espacio() -> None:
    """Comprobación estática sobre las rutas que buscan.

    **Esta prueba, tal como estaba escrita el 4 de septiembre de 2026, pasaba
    contra el código defectuoso**, y lo detectó una auditoría independiente. Al
    reescribirla tras la corrección perdió la mitad que localizaba el defecto: la
    inspección de los llamantes de `recuperar()`. En el código defectuoso las
    búsquedas de `retrieval_runner` **sí** pasaban el parámetro; lo que valía
    nulo era su origen.

    Se conserva la comprobación de las búsquedas y se añade la que faltaba: que
    el valor pasado **no pueda ser nulo**, es decir que no venga de un parámetro
    opcional sino del proveedor. La garantía fuerte la da `mypy --strict`; esta
    prueba cubre el caso de un módulo nuevo que la eluda.

    `search_lexical` queda fuera a propósito: no usa vectores, así que no tiene
    espacio que declarar.
    """
    omisiones: list[str] = []
    for fichero in (*LLAMANTES, RAIZ / "experiments" / "retrieval_runner.py"):
        arbol = ast.parse(fichero.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Call):
                continue
            if getattr(nodo.func, "attr", None) != "search":
                continue
            claves = {k.arg for k in nodo.keywords if k.arg}
            if "embedding_model" not in claves:
                omisiones.append(f"{fichero.name}:{nodo.lineno}")
    assert not omisiones, "búsquedas vectoriales sin espacio declarado: " + ", ".join(omisiones)


def test_el_espacio_no_puede_venir_de_un_parametro_opcional() -> None:
    """La mitad que se había perdido: de dónde sale el valor, no si se pasa.

    Es la comprobación que habría fallado contra el código defectuoso, donde el
    parámetro se pasaba y su origen era un argumento con valor nulo por defecto.
    """
    import ast
    import inspect

    from mecanico_ia_exp.experiments import retrieval_runner

    fuente = inspect.getsource(retrieval_runner.recuperar)
    arbol = ast.parse(fuente.lstrip())
    asignaciones = [
        n
        for n in ast.walk(arbol)
        if isinstance(n, ast.Assign)
        and any(getattr(d, "id", None) == "embedding_model" for d in n.targets)
    ]
    assert asignaciones, "`recuperar` no deriva el espacio: ¿de dónde sale?"
    origen = ast.unparse(asignaciones[0].value)
    assert "provider" in origen and "identity" in origen, (
        f"el espacio se deriva de {origen!r} y no del proveedor que vectoriza la consulta"
    )


def test_recuperar_no_acepta_el_espacio_como_parametro() -> None:
    """Lo deriva del proveedor, que es lo que impide que diverja.

    Un parámetro que hay que acordarse de pasar es el defecto que esto corrige:
    volver a añadirlo reabriría la puerta.
    """
    import inspect

    from mecanico_ia_exp.experiments.retrieval_runner import recuperar

    assert "embedding_model" not in inspect.signature(recuperar).parameters


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


# --- 4 · Pruebas semánticas ----------------------------------------------------
# El defecto pasó desapercibido porque la suite comprobaba **estructura** --que
# hubiera resultados, que vinieran ordenados-- y nunca que el espacio de la
# consulta y el del índice fueran el mismo. `len(resultados) > 0` se cumple
# igual comparando vectores de espacios incompatibles.


def test_la_consulta_y_el_indice_usan_el_mismo_proveedor() -> None:
    """No basta con que el modelo coincida: el proveedor lo produce."""
    proveedor = ProveedorFalso()
    espia = StoreEspia()
    from mecanico_ia_exp.experiments.retrieval_runner import recuperar

    recuperar(
        "semantic",
        store=espia,  # type: ignore[arg-type]
        provider=proveedor,  # type: ignore[arg-type]
        caso={"case_id": "T01", "fault_id": "F01_vacuum_leak", "query": "fuel trim"},
        vehicle_id="mazda-3-bk-2007",
        engine_code="Z6",
    )
    assert espia.modelos == [proveedor.identity.model]


def test_dos_modelos_de_igual_dimension_son_espacios_distintos() -> None:
    """La dimensión **no** identifica el espacio.

    Los dos modelos del índice producen vectores de 384, y el proveedor `hashing`
    también. Tres espacios incompatibles con la misma forma: nada en la aritmética
    de la búsqueda los distingue, solo su identificador.
    """
    from mecanico_ia_exp.rag.embeddings import MODELOS, HashingEmbeddingProvider

    hashing = HashingEmbeddingProvider().identity
    assert hashing.dimension == 384
    assert len({MODELOS["en"], MODELOS["multilingual"], hashing.model}) == 3, (
        "tres modelos distintos; si alguno coincidiera, el índice no podría separarlos"
    )


def test_el_identificador_del_espacio_no_es_solo_el_modelo() -> None:
    """Versionado del espacio: proveedor, modelo, dimensión y versión.

    Dos ejecuciones del mismo modelo con distinta versión de la biblioteca
    producen vectores que no son comparables entre sí. El identificador tiene que
    llevarlo todo, no solo el nombre del modelo.
    """
    from mecanico_ia_exp.rag.embeddings import get_provider

    identidad = get_provider("hashing").identity
    d = identidad.as_dict()
    for campo in ("embedding_provider", "embedding_model", "embedding_dimension"):
        assert campo in d, campo
    assert identidad.version, "sin versión, dos índices del mismo modelo son indistinguibles"


def test_buscar_en_un_espacio_no_indexado_falla_en_vez_de_devolver_vacio() -> None:
    """El riesgo del signo contrario, introducido por la propia corrección.

    Con el espacio ya obligatorio, declarar uno inexistente devolvía cero filas
    **en silencio**, y cero filas se lee como «no hay evidencia»: una abstención
    con aspecto legítimo causada por un error de configuración.

    **Ejercita el guardián real de `PgVectorStore.search`**, no una
    reimplementación en una subclase de prueba: una auditoría señaló que la
    versión anterior comprobaba el doble y no el contrato. Se sustituye solo la
    consulta de espacios indexados, que es lo que necesita la base de datos.
    """
    from mecanico_ia_exp.rag.store import PgVectorStore

    real = PgVectorStore.__new__(PgVectorStore)  # sin conexión: no hace falta
    object.__setattr__(real, "embedding_models", lambda: frozenset({"modelo-realmente-indexado"}))
    with pytest.raises(ValueError, match="no está indexado"):
        PgVectorStore.search(
            real,
            np.zeros(384, dtype=np.float32),
            vehicle_id="mazda-3-bk-2007",
            embedding_model="espacio-que-no-existe",
        )


def test_el_fragmento_pertinente_gana_al_irrelevante() -> None:
    """Relevancia, no solo estructura, **con el proveedor real del proyecto**.

    Ninguna prueba comprobaba que la recuperación ordene por pertinencia: todas
    se conformaban con que hubiera resultados. Una auditoría señaló además que la
    versión anterior de esta prueba no ejecutaba ninguna línea del proyecto.

    Usa el proveedor `hashing`, que es determinista y no descarga nada, y su
    propia métrica de similitud. Con conocimiento previo de cuál es el fragmento
    pertinente, debe quedar por encima del irrelevante.
    """
    from mecanico_ia_exp.rag.embeddings import get_provider

    proveedor = get_provider("hashing")
    consulta = "engine coolant temperature sensor circuit malfunction"
    pertinente = (
        "Engine coolant temperature sensor circuit. Measure the resistance of the "
        "coolant temperature sensor and compare with the standard value."
    )
    irrelevante = "Seat belt pretensioner deployment and airbag module replacement."

    vectores = proveedor.embed([consulta, pertinente, irrelevante])
    q, p_, i = (v / np.linalg.norm(v) for v in vectores)
    assert float(q @ p_) > float(q @ i), (
        "el fragmento pertinente no gana al irrelevante: la recuperación no ordena "
        "por proximidad semántica en este espacio"
    )
