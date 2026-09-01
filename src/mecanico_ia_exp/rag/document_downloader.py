"""Descargador controlado de documentación.

**No es un rastreador.** Solo obtiene URLs que aparecen en el manifiesto con
``download: true`` y acceso público. No sigue enlaces, no descubre recursos y no
descarga nada que no esté declarado de antemano.

Lo que este módulo no hace, y no hará:

- saltar autenticación de ningún portal;
- automatizar la descarga de documentación por suscripción;
- almacenar credenciales, cookies o sesiones;
- evadir restricciones de descarga.

Un manual de taller bajo suscripción se obtiene por su canal legítimo y se copia
a mano al directorio del vehículo. El manifiesto registra que existe y **cómo
conseguirlo**, sin intentar conseguirlo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from mecanico_ia_exp.rag.manifest import AccessType, DocumentEntry

#: Marca de un documento declarado pero ausente por requerir acceso legítimo.
MISSING_LICENSED_DOCUMENT = "MISSING_LICENSED_DOCUMENT"

#: Tamaño máximo admitido. Un manual entero cabe holgadamente; el límite existe
#: para que un error de URL no llene el disco.
LIMITE_BYTES = 512 * 1024 * 1024


@dataclass(frozen=True)
class DownloadRecord:
    """Constancia de una descarga: qué se obtuvo exactamente y cuándo.

    El SHA-256 es lo que permite demostrar **qué versión documental participó en
    cada experimento**. Sin él, «se usó el manual de mantenimiento» es una
    afirmación no verificable.
    """

    document_id: str
    vehicle_id: str
    download_url: str
    final_url: str
    publisher: str
    downloaded_at: datetime
    content_type: str
    file_size: int
    sha256: str
    http_status: int
    local_file: str
    license_or_access_notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "vehicle_id": self.vehicle_id,
            "download_url": self.download_url,
            "final_url": self.final_url,
            "publisher": self.publisher,
            "downloaded_at": self.downloaded_at.isoformat(),
            "content_type": self.content_type,
            "file_size": self.file_size,
            "sha256": self.sha256,
            "http_status": self.http_status,
            "local_file": self.local_file,
            "license_or_access_notes": self.license_or_access_notes,
        }


class DownloadNotAllowedError(RuntimeError):
    """Se ha intentado descargar un documento que el manifiesto no autoriza."""


@dataclass(frozen=True)
class DownloadFailure:
    """Constancia de una descarga que no se pudo completar.

    Un fallo se registra; no se soluciona buscando el documento en otro sitio.
    Que una URL declarada como pública devuelva 403 es información sobre el
    estado real del corpus, y sustituirla por una fuente cualquiera convertiría
    esa información en silencio.
    """

    document_id: str
    vehicle_id: str
    download_url: str
    http_status: int | None
    reason: str
    attempted_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "vehicle_id": self.vehicle_id,
            "download_url": self.download_url,
            "http_status": self.http_status,
            "reason": self.reason,
            "attempted_at": self.attempted_at.isoformat(),
        }


def sha256_of(path: Path) -> str:
    """Huella del fichero, leído por bloques para no cargarlo entero en memoria."""
    digestor = hashlib.sha256()
    with path.open("rb") as fichero:
        for bloque in iter(lambda: fichero.read(1024 * 1024), b""):
            digestor.update(bloque)
    return digestor.hexdigest()


def ensure_downloadable(entry: DocumentEntry) -> None:
    """Comprueba que el manifiesto autoriza la descarga. Si no, explica por qué."""
    if not entry.active:
        msg = f"{entry.document_id}: marcado como inactivo en el manifiesto"
        raise DownloadNotAllowedError(msg)
    if entry.access_type is not AccessType.PUBLIC:
        msg = (
            f"{entry.document_id}: acceso {entry.access_type.value!r}. "
            "Este documento se obtiene por su canal legítimo y se copia a mano. "
            "No se automatiza su descarga ni se evade su control de acceso."
        )
        raise DownloadNotAllowedError(msg)
    if not entry.download:
        msg = f"{entry.document_id}: el manifiesto declara download: false"
        raise DownloadNotAllowedError(msg)


def try_download(
    entry: DocumentEntry, destino: Path, *, force: bool = False, timeout: float = 60.0
) -> DownloadRecord | DownloadFailure:
    """Intenta descargar y devuelve el resultado, con éxito o con fallo.

    No propaga la excepción: la ingesta de un corpus con varios documentos debe
    poder terminar y reportar qué faltó, en lugar de detenerse en el primero.
    """
    import httpx

    try:
        return download_document(entry, destino, force=force, timeout=timeout)
    except httpx.HTTPStatusError as error:
        return DownloadFailure(
            document_id=entry.document_id,
            vehicle_id=entry.vehicle_id,
            download_url=entry.source_url,
            http_status=error.response.status_code,
            reason=f"{error.response.status_code} {error.response.reason_phrase}",
            attempted_at=datetime.now(UTC),
        )
    except (httpx.RequestError, DownloadNotAllowedError) as error:
        return DownloadFailure(
            document_id=entry.document_id,
            vehicle_id=entry.vehicle_id,
            download_url=entry.source_url,
            http_status=None,
            reason=f"{type(error).__name__}: {error}",
            attempted_at=datetime.now(UTC),
        )


def download_document(
    entry: DocumentEntry, destino: Path, *, force: bool = False, timeout: float = 60.0
) -> DownloadRecord:
    """Descarga un documento público declarado en el manifiesto.

    Si ya existe localmente y su huella coincide con la registrada, no se vuelve
    a descargar salvo ``force``: reingerir un documento idéntico solo produciría
    una versión nueva sin contenido nuevo.
    """
    import httpx

    ensure_downloadable(entry)
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.is_file() and entry.sha256 and not force:
        actual = sha256_of(destino)
        if actual == entry.sha256:
            return DownloadRecord(
                document_id=entry.document_id,
                vehicle_id=entry.vehicle_id,
                download_url=entry.source_url,
                final_url=entry.source_url,
                publisher=entry.publisher,
                downloaded_at=entry.downloaded_at or datetime.now(UTC),
                content_type="",
                file_size=destino.stat().st_size,
                sha256=actual,
                http_status=304,
                local_file=str(destino),
                license_or_access_notes="ya presente con la huella registrada",
            )

    with httpx.Client(follow_redirects=True, timeout=timeout) as cliente:
        respuesta = cliente.get(entry.source_url)
        respuesta.raise_for_status()
        contenido = respuesta.content

    if len(contenido) > LIMITE_BYTES:
        msg = f"{entry.document_id}: {len(contenido)} bytes supera el límite admitido"
        raise DownloadNotAllowedError(msg)

    destino.write_bytes(contenido)
    return DownloadRecord(
        document_id=entry.document_id,
        vehicle_id=entry.vehicle_id,
        download_url=entry.source_url,
        final_url=str(respuesta.url),
        publisher=entry.publisher,
        downloaded_at=datetime.now(UTC),
        content_type=respuesta.headers.get("content-type", ""),
        file_size=len(contenido),
        sha256=sha256_of(destino),
        http_status=respuesta.status_code,
        local_file=str(destino),
        license_or_access_notes=(
            "público desde infraestructura oficial del fabricante"
            if entry.redistributable
            else "público; no se redistribuye desde este repositorio"
        ),
    )


def missing_document_notice(entry: DocumentEntry) -> str:
    """Aviso para un documento declarado y ausente, con cómo obtenerlo.

    Nunca se sustituye por una fuente de menor autoridad. Un manual de taller
    ausente deja un hueco declarado, no un blog en su lugar.
    """
    return (
        f"{MISSING_LICENSED_DOCUMENT}: {entry.document_id}\n"
        f"  título   : {entry.title}\n"
        f"  editor   : {entry.publisher}\n"
        f"  acceso   : {entry.access_type.value}\n"
        f"  portal   : {entry.source_portal or entry.source_url}\n"
        f"  autoridad: nivel {entry.authority_level.value}\n"
        "  Obténgalo legítimamente por ese canal y colóquelo en el directorio "
        "del vehículo. No se sustituye por una fuente de menor autoridad."
    )
