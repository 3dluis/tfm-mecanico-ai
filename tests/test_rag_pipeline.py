"""Cargadores, troceado, embeddings y almacén vectorial.

Los tests marcados ``db`` necesitan PostgreSQL con pgvector y el corpus ingerido.
El resto corre sin red ni base de datos.
"""

from __future__ import annotations

from itertools import pairwise

import numpy as np
import pytest

from mecanico_ia_exp.rag.chunking import (
    ChunkingConfig,
    Classification,
    VehicleSystem,
    chunk_document,
    classify_system,
    extract_dtc_codes,
    extract_engine_codes,
)
from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider, get_provider
from mecanico_ia_exp.rag.loaders import (
    LoadedDocument,
    LoadedPage,
    UnsupportedFormatError,
    load_document,
)

#: Espacio vectorial en que buscan estas pruebas. Declararlo es obligatorio
#: desde `MIXED-EMBEDDING-SPACE`: el índice contiene dos modelos y una búsqueda
#: sin espacio los mezclaba en una misma ordenación.
#:
#: Estas pruebas comprueban **propiedades estructurales** de la búsqueda --orden,
#: filtros por vehículo y motor, exclusiones-- y no relevancia semántica, así que
#: su vector de consulta puede venir de otro proveedor. Lo que no puede es dejar
#: el espacio del índice sin declarar.
ESPACIO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

VEHICULO = "mazda-3-bk-2007"


# ------------------------------------------------------------- cargadores


def test_html_loader(tmp_path) -> None:
    ruta = tmp_path / "d.html"
    ruta.write_text(
        "<html><head><title>Manual</title><style>p{color:red}</style></head>"
        "<body><script>var x=1</script><p>Thermostat opening 80 C</p></body></html>",
        encoding="utf-8",
    )
    doc = load_document(ruta)
    assert doc.title == "Manual"
    assert "Thermostat opening 80 C" in doc.text
    # Guiones de estilo y scripts no son contenido: si acaban en el texto,
    # contaminan los fragmentos y aparecen en las citas.
    assert "color:red" not in doc.text
    assert "var x" not in doc.text
    assert doc.paginated is False


def test_text_loader_toma_el_titulo_del_encabezado(tmp_path) -> None:
    ruta = tmp_path / "d.md"
    ruta.write_text("# Procedimiento\n\nTexto del cuerpo.", encoding="utf-8")
    doc = load_document(ruta)
    assert doc.title == "Procedimiento"
    assert doc.paginated is False


def test_un_formato_sin_cargador_falla_con_mensaje_util(tmp_path) -> None:
    ruta = tmp_path / "d.xyz"
    ruta.write_text("x", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError, match="Admitidos"):
        load_document(ruta)


def test_un_formato_sin_paginacion_lo_declara(tmp_path) -> None:
    """Inventar números de página haría las citas irrastreables."""
    ruta = tmp_path / "d.txt"
    ruta.write_text("contenido", encoding="utf-8")
    doc = load_document(ruta)
    assert doc.paginated is False
    assert doc.n_pages == 1


# ---------------------------------------------------------------- metadata


def test_dtc_metadata() -> None:
    """Los códigos se extraen literalmente; no se infieren asociaciones."""
    texto = "DTC P0133 Front HO2S circuit slow response. See also B104F and U0100."
    assert extract_dtc_codes(texto) == ("B104F", "P0133", "U0100")


def test_no_se_inventan_dtc_donde_no_los_hay() -> None:
    """Un síntoma descrito sin código no genera código."""
    texto = "The oxygen sensor responds slowly and the mixture runs lean."
    assert extract_dtc_codes(texto) == ()


def test_un_codigo_malformado_no_se_admite() -> None:
    assert extract_dtc_codes("P017 and PX0171 and 0171") == ()


def test_los_motores_declarados_se_extraen_de_la_cabecera() -> None:
    assert extract_engine_codes("DTC P0133 [ZJ, Z6] B3E010200100W13") == ("Z6", "ZJ")
    assert extract_engine_codes("PROCEDURE [LF]") == ("LF",)


def test_la_clasificacion_de_sistema_declara_como_se_obtuvo() -> None:
    """Una clasificación derivada de palabras clave es una conjetura útil, no un
    dato del manual, y quien lea el fragmento debe poder distinguirlo."""
    sistema, como = classify_system("Thermostat opening temperature and coolant flow")
    assert sistema is VehicleSystem.COOLING
    assert como is Classification.DERIVED

    sistema, como = classify_system("xxxx yyyy zzzz")
    assert sistema is VehicleSystem.OTHER
    assert como is Classification.UNKNOWN


# ----------------------------------------------------------------- troceado


def _documento(paginas: list[str]) -> LoadedDocument:
    from pathlib import Path

    return LoadedDocument(
        source_file=Path("srvc/B3E010200100W13.pdf"),
        pages=[LoadedPage(number=i + 1, text=t) for i, t in enumerate(paginas)],
        paginated=True,
    )


def test_chunk_provenance() -> None:
    """Cada fragmento sabe de dónde salió, y su cita lo dice."""
    doc = _documento(["DTC P0133 [ZJ, Z6]\nDETECTION CONDITION\nThe PCM monitors..."])
    fragmentos = chunk_document(
        doc, document_id="manual", version_id="v1", vehicle_id=VEHICULO, chapter="srvc"
    )
    assert fragmentos
    c = fragmentos[0]
    assert c.document_id == "manual"
    assert c.version_id == "v1"
    assert c.vehicle_id == VEHICULO
    assert c.chapter == "srvc"
    assert c.section == "DTC P0133 [ZJ, Z6]"
    assert c.dtc_codes == ("P0133",)
    assert c.engine_codes == ("Z6", "ZJ")
    assert c.content_hash
    cita = c.provenance()
    assert "manual" in cita and "página 1" in cita and "srvc" in cita


def test_page_provenance() -> None:
    """El rango de páginas corresponde siempre al texto del fragmento.

    Un fragmento nace dentro de una página y no la abandona. Si cruzara páginas
    sin registrarlo, la cita señalaría un sitio donde el texto no está.
    """
    doc = _documento(["Primera página " * 40, "Segunda página " * 40, "Tercera " * 40])
    fragmentos = chunk_document(doc, document_id="m", version_id="v1", vehicle_id=VEHICULO)
    assert fragmentos
    for c in fragmentos:
        assert c.page_start == c.page_end
        assert 1 <= c.page_start <= 3
        esperado = doc.pages[c.page_start - 1].text
        assert c.text.split()[0] in esperado

    assert {c.page_start for c in fragmentos} == {1, 2, 3}


def test_una_pagina_vacia_no_produce_fragmentos() -> None:
    doc = _documento(["Contenido real aquí", "   ", ""])
    fragmentos = chunk_document(doc, document_id="m", version_id="v1", vehicle_id=VEHICULO)
    assert {c.page_start for c in fragmentos} == {1}


def test_los_identificadores_de_fragmento_son_unicos() -> None:
    doc = _documento(["Texto largo. " * 200, "Otro texto. " * 200])
    fragmentos = chunk_document(
        doc,
        document_id="m",
        version_id="v1",
        vehicle_id=VEHICULO,
        config=ChunkingConfig(target_size=300, max_size=500),
    )
    identificadores = [c.chunk_id for c in fragmentos]
    assert len(identificadores) == len(set(identificadores))


def test_el_troceado_respeta_el_tamano_maximo() -> None:
    doc = _documento(["palabra " * 3000])
    fragmentos = chunk_document(
        doc,
        document_id="m",
        version_id="v1",
        vehicle_id=VEHICULO,
        config=ChunkingConfig(target_size=400, max_size=600),
    )
    assert fragmentos
    assert all(len(c.text) <= 600 for c in fragmentos)


# --------------------------------------------------------------- embeddings


def test_el_proveedor_de_hashing_es_determinista() -> None:
    """Los tests no pueden depender de descargar un modelo ni de la red."""
    p = HashingEmbeddingProvider()
    a = p.embed(["DTC P0133 front HO2S slow response"])
    b = p.embed(["DTC P0133 front HO2S slow response"])
    assert np.array_equal(a, b)


def test_los_vectores_salen_normalizados() -> None:
    """Con norma 1, la distancia coseno equivale al producto escalar y las
    puntuaciones son comparables entre consultas."""
    p = HashingEmbeddingProvider()
    v = p.embed(["texto uno", "texto dos distinto"])
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-5)


def test_textos_distintos_producen_vectores_distintos() -> None:
    p = HashingEmbeddingProvider()
    v = p.embed(["thermostat opening temperature", "misfire cylinder detection"])
    assert not np.allclose(v[0], v[1])


def test_la_identidad_del_espacio_vectorial_se_declara() -> None:
    """Dos corpus indexados con modelos distintos no son comparables."""
    identidad = HashingEmbeddingProvider(dimension=384).identity
    datos = identidad.as_dict()
    assert datos["embedding_dimension"] == 384
    assert set(datos) == {
        "embedding_provider",
        "embedding_model",
        "embedding_dimension",
        "embedding_version",
    }


def test_un_proveedor_desconocido_se_rechaza() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        get_provider("inexistente")


def test_el_proveedor_por_defecto_no_toca_la_red() -> None:
    """Un checkout recién clonado no descarga modelos hasta que se le pide."""
    assert isinstance(get_provider(), HashingEmbeddingProvider)


# ------------------------------------------------------- almacén (requiere BD)


@pytest.fixture(scope="module")
def store():
    pytest.importorskip("sqlalchemy")
    from mecanico_ia_exp.rag.store import PgVectorStore

    s = PgVectorStore()
    yield s
    s.dispose()


@pytest.mark.db
def test_pgvector_extension(store) -> None:
    import sqlalchemy as sa

    with store._engine.connect() as cx:
        version = cx.execute(
            sa.text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        ).scalar_one_or_none()
    assert version is not None, "la extensión vector no está instalada"


@pytest.mark.db
def test_embedding_storage(store) -> None:
    """Cada embedding conserva el modelo con el que se generó.

    Varios modelos conviven en el índice **a propósito**: es lo que permite
    compararlos sobre el mismo corpus sin reindexar dos bases. Lo que no puede
    ocurrir es que una consulta los mezcle, y de eso se encarga el filtro por
    modelo en la búsqueda.

    Sí deben compartir dimensión: el esquema declara ``vector(384)`` y un modelo
    de otra dimensión no cabría, lo que obliga a que el cambio sea una migración
    explícita en lugar de un efecto colateral.
    """
    import sqlalchemy as sa

    with store._engine.connect() as cx:
        fila = (
            cx.execute(
                sa.text("""
                SELECT count(*) AS n, count(DISTINCT embedding_model) AS modelos,
                       count(DISTINCT embedding_dimension) AS dimensiones,
                       min(embedding_dimension) AS dim
                FROM rag.embedding WHERE vehicle_id = :v
            """),
                {"v": VEHICULO},
            )
            .mappings()
            .one()
        )
    assert fila["n"] > 0, "no hay embeddings ingeridos"
    assert fila["dimensiones"] == 1, "conviven dimensiones distintas en el mismo esquema"
    assert fila["dim"] == 384


@pytest.mark.db
def test_vector_search(store) -> None:
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("oxygen sensor slow response")
    res = store.search(v, vehicle_id=VEHICULO, top_k=5, embedding_model=ESPACIO)
    assert res
    assert [r.rank for r in res] == list(range(1, len(res) + 1))
    # Las puntuaciones llegan ordenadas de mayor a menor.
    assert all(a.score >= b.score for a, b in pairwise(res))


@pytest.mark.db
def test_no_cross_vehicle_retrieval(store) -> None:
    """Buscar evidencia de otro vehículo no devuelve nada de este.

    El vehículo es parámetro obligatorio de search: no existe la búsqueda global
    que permitiría que documentación de otro coche apareciera como evidencia.
    """
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("oxygen sensor slow response")
    assert (
        store.search(v, vehicle_id="vehiculo-inexistente", top_k=10, embedding_model=ESPACIO) == []
    )

    propios = store.search(v, vehicle_id=VEHICULO, top_k=10, embedding_model=ESPACIO)
    assert propios
    assert all(r.vehicle_id == VEHICULO for r in propios)


@pytest.mark.db
def test_vehicle_metadata_filter(store) -> None:
    """Un procedimiento de otro motor no debe pasar el filtro."""
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("engine inspection procedure")
    filtrados = store.search(
        v, vehicle_id=VEHICULO, top_k=100, engine_codes=("Z6", "ZJ"), embedding_model=ESPACIO
    )
    ajenos = [
        r
        for r in filtrados
        if r.engine_codes and "Z6" not in r.engine_codes and "ZJ" not in r.engine_codes
    ]
    assert not ajenos, f"{len(ajenos)} fragmentos de otro motor pasaron el filtro"


@pytest.mark.db
def test_el_filtro_por_dtc_devuelve_solo_fragmentos_con_ese_codigo(store) -> None:
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("slow response")
    res = store.search(
        v, vehicle_id=VEHICULO, top_k=10, dtc_codes=("P0133",), embedding_model=ESPACIO
    )
    assert res, "el corpus debería contener el procedimiento de P0133"
    assert all("P0133" in r.dtc_codes for r in res)


@pytest.mark.db
def test_la_exclusion_de_documentos_construye_las_variantes_del_corpus(store) -> None:
    """Retirar evidencia es explícito y auditable, nunca un efecto lateral."""
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("oxygen sensor")
    completo = store.search(v, vehicle_id=VEHICULO, top_k=5, embedding_model=ESPACIO)
    assert completo
    excluidos = tuple({r.chunk_id for r in completo})
    reducido = store.search(
        v, vehicle_id=VEHICULO, top_k=5, exclude_chunks=excluidos, embedding_model=ESPACIO
    )
    assert not ({r.chunk_id for r in reducido} & set(excluidos))


@pytest.mark.db
def test_retrieval_logging(store) -> None:
    """Sin registro, «el sistema recuperó este fragmento» no es comprobable."""
    import sqlalchemy as sa

    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    proveedor = HashingEmbeddingProvider()
    v = proveedor.embed_one("thermostat")
    res = store.search(v, vehicle_id=VEHICULO, top_k=3, embedding_model=ESPACIO)
    run_id = store.log_retrieval(
        vehicle_id=VEHICULO,
        query_text="thermostat",
        resultados=res,
        identidad=proveedor.identity,
        top_k=3,
        experiment_id="test",
    )
    with store._engine.connect() as cx:
        run = (
            cx.execute(
                sa.text(
                    "SELECT query_text, top_k, embedding_model FROM rag.retrieval_run "
                    "WHERE run_id = :r"
                ),
                {"r": run_id},
            )
            .mappings()
            .one()
        )
        n = cx.execute(
            sa.text("SELECT count(*) FROM rag.retrieval_result WHERE run_id = :r"),
            {"r": run_id},
        ).scalar_one()
    assert run["query_text"] == "thermostat"
    assert run["top_k"] == 3
    assert run["embedding_model"] == proveedor.identity.model
    assert n == len(res)


@pytest.mark.db
def test_document_versioning_no_duplica_una_huella_conocida(store) -> None:
    """Reingerir contenido idéntico no crea una versión nueva."""
    import sqlalchemy as sa

    with store._engine.connect() as cx:
        filas = cx.execute(
            sa.text(
                "SELECT sha256, count(*) AS n FROM rag.document_version "
                "GROUP BY sha256 HAVING count(*) > 1"
            )
        ).all()
    assert not filas, "hay huellas duplicadas en el historial de versiones"


@pytest.mark.db
def test_chunk_provenance_completa_en_la_base(store) -> None:
    """El gate de la fase: desde un resultado se reconstruye toda la cadena."""
    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("HO2S inspection")
    res = store.search(v, vehicle_id=VEHICULO, top_k=1, embedding_model=ESPACIO)
    assert res
    r = res[0]
    assert r.chunk_id and r.document_id and r.vehicle_id
    assert r.page_start is not None
    assert r.section
    assert r.publisher
    assert r.source_url
    assert r.authority_level
    assert r.source_file
    cita = r.provenance()
    for esperado in (r.publisher, "página", r.chunk_id, r.source_url):
        assert esperado in cita


# ------------------------------------------------------------------ idioma


def test_el_fragmento_hereda_el_idioma_del_documento() -> None:
    """El idioma se declara en el manifiesto; no se detecta ni se adivina."""
    doc = _documento(["Thermostat opening temperature 80 - 84 C"])
    fragmentos = chunk_document(
        doc, document_id="m", version_id="v1", vehicle_id=VEHICULO, language="es"
    )
    assert fragmentos
    assert all(c.language == "es" for c in fragmentos)


def test_el_idioma_por_defecto_es_ingles() -> None:
    doc = _documento(["Some content"])
    fragmentos = chunk_document(doc, document_id="m", version_id="v1", vehicle_id=VEHICULO)
    assert fragmentos[0].language == "en"


def test_cada_idioma_tiene_su_configuracion_de_busqueda_textual() -> None:
    """Buscar texto español con la configuración inglesa lematiza mal."""
    from mecanico_ia_exp.rag.store import CONFIG_FTS

    assert CONFIG_FTS["en"] == "english"
    assert CONFIG_FTS["es"] == "spanish"


def test_el_modelo_por_defecto_es_multilingue() -> None:
    """Medido: el monolingüe encuentra 1 de 5 con consultas en español."""
    from mecanico_ia_exp.rag.embeddings import MODELOS, SentenceTransformerProvider

    assert "multilingual" in SentenceTransformerProvider()._model_name
    assert set(MODELOS) == {"en", "multilingual"}


@pytest.mark.db
def test_la_busqueda_lexica_no_cruza_idiomas(store) -> None:
    """El corpus es solo inglés: una búsqueda léxica en español debe devolver
    cero, no coincidencias por accidente ortográfico."""
    en = store.search_lexical("fuel trim idle", vehicle_id=VEHICULO, top_k=5, language="en")
    es = store.search_lexical(
        "ajuste de combustible ralentí", vehicle_id=VEHICULO, top_k=5, language="es"
    )
    assert en, "la búsqueda léxica en inglés debería encontrar algo"
    assert not es, "no hay documentos en español; devolver algo sería un accidente"


@pytest.mark.db
def test_la_busqueda_vectorial_no_mezcla_espacios_de_modelos_distintos(store) -> None:
    """Dos modelos conviven en el índice a propósito, para poder compararlos.
    Mezclarlos en una consulta compararía puntos de espacios distintos."""
    import sqlalchemy as sa

    with store._engine.connect() as cx:
        modelos = (
            cx.execute(sa.text("SELECT DISTINCT embedding_model FROM rag.embedding"))
            .scalars()
            .all()
        )
    assert len(modelos) >= 2, "se esperaban al menos dos modelos indexados"

    from mecanico_ia_exp.rag.embeddings import HashingEmbeddingProvider

    v = HashingEmbeddingProvider().embed_one("thermostat")
    for modelo in modelos:
        res = store.search(v, vehicle_id=VEHICULO, top_k=5, embedding_model=str(modelo))
        assert res
