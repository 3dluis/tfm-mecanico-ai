"""Corpus documental por vehículo: perfil, manifiesto, aplicabilidad y descarga.

La pregunta de investigación exige rastrear cada explicación hasta su evidencia.
Una evidencia que pertenece a otro vehículo no sostiene nada por muy parecido que
sea su texto. Estos tests protegen esa frontera.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import pytest
import yaml

from mecanico_ia_exp.rag.document_downloader import (
    DownloadFailure,
    DownloadNotAllowedError,
    ensure_downloadable,
    missing_document_notice,
    sha256_of,
    try_download,
)
from mecanico_ia_exp.rag.ingest import load_vehicle, manifest_hash, run_ingestion
from mecanico_ia_exp.rag.manifest import (
    AccessType,
    AuthorityLevel,
    DocumentEntry,
    DocumentManifest,
    DocumentType,
)
from mecanico_ia_exp.rag.vehicle import (
    Applicability,
    VehicleApplicabilityValidator,
    VehicleProfile,
)

RAIZ_CORPUS = Path("corpus/vehicles")
PILOTO = "toyota-corolla-2020"


# --------------------------------------------------------- perfil de vehículo


def test_vehicle_profile() -> None:
    """El perfil piloto se carga y declara lo que sabe."""
    perfil = load_vehicle(PILOTO, RAIZ_CORPUS)
    assert perfil.vehicle_id == PILOTO
    assert perfil.manufacturer == "Toyota"
    assert perfil.model == "Corolla"
    assert perfil.model_year == 2020
    assert perfil.market == "North America"


def test_los_campos_desconocidos_quedan_en_nulo() -> None:
    """Un engine_code inventado convertiría el validador en un generador de
    coincidencias exactas falsas."""
    perfil = load_vehicle(PILOTO, RAIZ_CORPUS)
    assert perfil.engine_code is None
    assert perfil.transmission is None
    assert perfil.vin_prefix is None
    assert perfil.obd_protocol is None


# ------------------------------------------------------------- aplicabilidad


def _perfil(**cambios: object) -> VehicleProfile:
    base: dict[str, object] = {
        "vehicle_id": "v",
        "manufacturer": "Toyota",
        "model": "Corolla",
        "model_year": 2020,
    }
    base.update(cambios)
    return VehicleProfile.model_validate(base)


def test_vehicle_applicability() -> None:
    """Coincidencia exacta cuando coinciden identidad y refinamiento."""
    vehiculo = _perfil(market="North America", engine_code="2ZR-FAE")
    documento = _perfil(market="North America", engine_code="2ZR-FAE")
    validador = VehicleApplicabilityValidator(vehiculo)
    assert validador.validate(documento) is Applicability.EXACT_MATCH
    assert validador.is_strong_evidence(documento)


def test_otro_modelo_es_incompatible() -> None:
    validador = VehicleApplicabilityValidator(_perfil())
    assert validador.validate(_perfil(model="Camry")) is Applicability.INCOMPATIBLE


def test_otro_año_es_incompatible() -> None:
    validador = VehicleApplicabilityValidator(_perfil())
    assert validador.validate(_perfil(model_year=2019)) is Applicability.INCOMPATIBLE


def test_otro_fabricante_es_incompatible() -> None:
    validador = VehicleApplicabilityValidator(_perfil())
    assert validador.validate(_perfil(manufacturer="Honda")) is Applicability.INCOMPATIBLE


def test_otro_motor_del_mismo_modelo_es_coincidencia_parcial() -> None:
    """Un mismo modelo y año puede llevar motores distintos; un procedimiento de
    otro motor no es evidencia fuerte."""
    vehiculo = _perfil(engine_code="2ZR-FAE")
    documento = _perfil(engine_code="M20A-FKS")
    validador = VehicleApplicabilityValidator(vehiculo)
    assert validador.validate(documento) is Applicability.PARTIAL_MATCH
    assert not validador.is_strong_evidence(documento)


def test_sin_identidad_completa_el_resultado_es_desconocido() -> None:
    vehiculo = VehicleProfile(
        vehicle_id="v", manufacturer="Toyota", model="Corolla", model_year=2020
    )
    documento = VehicleProfile(
        vehicle_id="d", manufacturer="Toyota", model="Corolla", model_year=2020
    )
    documento.model_year = 2020
    sin_modelo = documento.model_copy(update={"model": None})
    assert VehicleApplicabilityValidator(vehiculo).validate(sin_modelo) is Applicability.UNKNOWN


def test_lo_desconocido_nunca_es_evidencia_valida() -> None:
    """UNKNOWN no debe convertirse silenciosamente en evidencia."""
    vehiculo = _perfil()
    sin_modelo = _perfil().model_copy(update={"model": None})
    validador = VehicleApplicabilityValidator(vehiculo)
    assert not validador.is_strong_evidence(sin_modelo)
    assert not validador.is_strong_evidence(sin_modelo, allow_compatible=True)


def test_lo_compatible_solo_vale_bajo_politica_declarada() -> None:
    vehiculo = _perfil()
    documento = _perfil()
    validador = VehicleApplicabilityValidator(vehiculo)
    assert validador.validate(documento) is Applicability.COMPATIBLE
    assert not validador.is_strong_evidence(documento)
    assert validador.is_strong_evidence(documento, allow_compatible=True)


# ---------------------------------------------------------------- manifiesto


def test_manifest_validation() -> None:
    """El manifiesto piloto carga, y sus documentos pertenecen a su vehículo."""
    manifiesto = DocumentManifest.load(RAIZ_CORPUS / PILOTO / "manifest.yaml")
    assert manifiesto.vehicle_id == PILOTO
    assert all(d.vehicle_id == PILOTO for d in manifiesto.documents)
    assert {s.source_id for s in manifiesto.sources} >= {"toyota-tis"}


def test_el_manifiesto_rechaza_documentacion_de_otro_vehiculo() -> None:
    """Nunca se mezcla documentación de vehículos distintos como equivalente."""
    ajeno = DocumentEntry(
        document_id="d1",
        vehicle_id="honda-civic-2020",
        document_type=DocumentType.REPAIR_MANUAL,
        title="t",
        publisher="Honda",
        source_url="https://example.invalid/",
        access_type=AccessType.PUBLIC,
        authority_level=AuthorityLevel.A,
    )
    with pytest.raises(ValueError, match="otro vehículo"):
        DocumentManifest(vehicle_id=PILOTO, documents=[ajeno])


def test_duplicate_document() -> None:
    """Dos entradas con el mismo identificador harían ambigua la procedencia."""
    entrada = DocumentEntry(
        document_id="repetido",
        vehicle_id=PILOTO,
        document_type=DocumentType.OWNERS_MANUAL,
        title="t",
        publisher="Toyota",
        source_url="https://example.invalid/",
        access_type=AccessType.PUBLIC,
        authority_level=AuthorityLevel.A,
    )
    with pytest.raises(ValueError, match="repetidos"):
        DocumentManifest(vehicle_id=PILOTO, documents=[entrada, entrada])


def test_un_documento_por_suscripcion_no_puede_declararse_descargable() -> None:
    """El error aparece al declarar la intención, no al ejecutarla."""
    with pytest.raises(ValueError, match="no admite descarga automática"):
        DocumentEntry(
            document_id="d",
            vehicle_id=PILOTO,
            document_type=DocumentType.REPAIR_MANUAL,
            title="t",
            publisher="Toyota",
            source_url="https://techinfo.toyota.com/",
            access_type=AccessType.SUBSCRIPTION,
            authority_level=AuthorityLevel.A,
            download=True,
        )


def test_la_jerarquia_de_evidencia_pone_el_manual_de_taller_por_delante() -> None:
    """La autoridad no la determina la similitud con la consulta."""
    manifiesto = DocumentManifest.load(RAIZ_CORPUS / PILOTO / "manifest.yaml")
    taller = manifiesto.by_id("toyota-corolla-2020-repair-manual")
    mantenimiento = manifiesto.by_id("toyota-corolla-2020-warranty-maintenance")
    propietario = manifiesto.by_id("toyota-corolla-2020-owners-manual")
    assert taller.evidence_rank < propietario.evidence_rank < mantenimiento.evidence_rank


# ------------------------------------------------------------------ descarga


def test_private_document_not_downloaded() -> None:
    """El manual de taller bajo suscripción nunca entra en la lista de descarga."""
    manifiesto = DocumentManifest.load(RAIZ_CORPUS / PILOTO / "manifest.yaml")
    descargables = {d.document_id for d in manifiesto.downloadable()}
    assert "toyota-corolla-2020-repair-manual" not in descargables

    taller = manifiesto.by_id("toyota-corolla-2020-repair-manual")
    with pytest.raises(DownloadNotAllowedError, match="No se automatiza"):
        ensure_downloadable(taller)


def test_el_aviso_de_documento_ausente_indica_como_obtenerlo() -> None:
    """Nunca se sustituye por una fuente de menor autoridad."""
    manifiesto = DocumentManifest.load(RAIZ_CORPUS / PILOTO / "manifest.yaml")
    aviso = missing_document_notice(manifiesto.by_id("toyota-corolla-2020-repair-manual"))
    assert "MISSING_LICENSED_DOCUMENT" in aviso
    assert "Toyota TIS" in aviso
    assert "menor autoridad" in aviso


def test_document_checksum(tmp_path: Path) -> None:
    """El SHA-256 es lo que permite demostrar qué versión participó en cada
    experimento."""
    fichero = tmp_path / "d.pdf"
    contenido = b"%PDF-1.7 contenido de prueba"
    fichero.write_bytes(contenido)
    assert sha256_of(fichero) == hashlib.sha256(contenido).hexdigest()


def test_una_diferencia_de_un_byte_cambia_la_huella(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"contenido")
    b.write_bytes(b"contenidos")
    assert sha256_of(a) != sha256_of(b)


def test_public_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Una descarga pública produce constancia completa de procedencia.

    No se toca la red: se sustituye el cliente HTTP para que el test sea
    determinista y no dependa de la disponibilidad de un servidor ajeno.
    """
    contenido = b"%PDF-1.7 guia de mantenimiento"

    class RespuestaFalsa:
        status_code = 200
        content = contenido
        headers: ClassVar[dict[str, str]] = {"content-type": "application/pdf"}
        url = "https://example.invalid/final.pdf"

        def raise_for_status(self) -> None:
            return None

    class ClienteFalso:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self) -> ClienteFalso:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def get(self, _url: str) -> RespuestaFalsa:
            return RespuestaFalsa()

    import httpx

    monkeypatch.setattr(httpx, "Client", ClienteFalso)

    entrada = DocumentEntry(
        document_id="publico",
        vehicle_id=PILOTO,
        document_type=DocumentType.WARRANTY_MAINTENANCE_GUIDE,
        title="Guía",
        publisher="Toyota",
        source_url="https://example.invalid/d.pdf",
        access_type=AccessType.PUBLIC,
        authority_level=AuthorityLevel.A,
        download=True,
    )
    destino = tmp_path / "publico.pdf"
    resultado = try_download(entrada, destino)

    assert not isinstance(resultado, DownloadFailure)
    assert destino.is_file()
    assert resultado.sha256 == hashlib.sha256(contenido).hexdigest()
    assert resultado.http_status == 200
    assert resultado.publisher == "Toyota"
    assert resultado.vehicle_id == PILOTO
    assert resultado.final_url == "https://example.invalid/final.pdf"
    assert resultado.file_size == len(contenido)


def test_un_fallo_de_descarga_se_registra_y_no_detiene_la_ingesta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Que una URL declarada pública devuelva 403 es información sobre el corpus.
    Sustituirla por otra fuente convertiría esa información en silencio."""
    import httpx

    class ClienteQueFalla:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self) -> ClienteQueFalla:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def get(self, url: str) -> object:
            peticion = httpx.Request("GET", url)
            respuesta = httpx.Response(403, request=peticion)
            raise httpx.HTTPStatusError("403", request=peticion, response=respuesta)

    monkeypatch.setattr(httpx, "Client", ClienteQueFalla)

    entrada = DocumentEntry(
        document_id="falla",
        vehicle_id=PILOTO,
        document_type=DocumentType.WARRANTY_MAINTENANCE_GUIDE,
        title="Guía",
        publisher="Toyota",
        source_url="https://example.invalid/d.pdf",
        access_type=AccessType.PUBLIC,
        authority_level=AuthorityLevel.A,
        download=True,
    )
    resultado = try_download(entrada, tmp_path / "falla.pdf")
    assert isinstance(resultado, DownloadFailure)
    assert resultado.http_status == 403
    assert not (tmp_path / "falla.pdf").exists()


def test_document_versioning(tmp_path: Path) -> None:
    """Si la huella no cambió, no se reingiere: una versión nueva sin contenido
    nuevo solo añadiría ruido al historial."""
    contenido = b"%PDF-1.7 estable"
    destino = tmp_path / "estable.pdf"
    destino.write_bytes(contenido)
    huella = hashlib.sha256(contenido).hexdigest()

    entrada = DocumentEntry(
        document_id="estable",
        vehicle_id=PILOTO,
        document_type=DocumentType.WARRANTY_MAINTENANCE_GUIDE,
        title="Guía",
        publisher="Toyota",
        source_url="https://example.invalid/d.pdf",
        access_type=AccessType.PUBLIC,
        authority_level=AuthorityLevel.A,
        download=True,
        sha256=huella,
        downloaded_at=datetime.now(UTC),
    )
    resultado = try_download(entrada, destino)
    assert not isinstance(resultado, DownloadFailure)
    assert resultado.http_status == 304
    assert resultado.sha256 == huella


# ------------------------------------------------------------------ ingesta


def test_la_huella_del_manifiesto_identifica_la_lista_documental() -> None:
    ruta = RAIZ_CORPUS / PILOTO / "manifest.yaml"
    assert manifest_hash(ruta) == hashlib.sha256(ruta.read_bytes()).hexdigest()


def test_la_ingesta_no_admite_perfil_y_manifiesto_de_vehiculos_distintos(
    tmp_path: Path,
) -> None:
    (tmp_path / "otro").mkdir()
    (tmp_path / "otro" / "vehicle.yaml").write_text(
        yaml.safe_dump(
            {
                "vehicle_id": "otro",
                "manufacturer": "Honda",
                "model": "Civic",
                "model_year": 2020,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="documentación cruzada"):
        run_ingestion("otro", RAIZ_CORPUS / PILOTO / "manifest.yaml", base=tmp_path)
