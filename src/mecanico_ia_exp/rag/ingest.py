"""Ingesta del corpus documental de un vehículo.

    uv run python -m mecanico_ia_exp.rag.ingest \\
      --vehicle toyota-corolla-2020 \\
      --manifest corpus/vehicles/toyota-corolla-2020/manifest.yaml

Encadena: validar manifiesto → descargar lo público autorizado → verificar
huella → registrar procedencia → emitir informe.

La ingesta **no se detiene ante un documento que falta**. Lo registra y sigue.
Un corpus incompleto es un hecho del experimento, y ocultarlo tras un error
impediría distinguir «no había evidencia» de «no se pudo ejecutar».
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.rag.document_downloader import (
    MISSING_LICENSED_DOCUMENT,
    DownloadFailure,
    DownloadRecord,
    missing_document_notice,
    try_download,
)
from mecanico_ia_exp.rag.manifest import AccessType, DocumentManifest
from mecanico_ia_exp.rag.vehicle import VehicleProfile

CORPUS_VEHICLES = paths.CORPUS / "vehicles"


@dataclass
class IngestionReport:
    """Resultado de una ingesta, con lo que entró y lo que faltó."""

    vehicle_id: str
    corpus_version: str
    manifest_hash: str
    started_at: datetime
    documents_registered: int = 0
    documents_downloaded: int = 0
    documents_skipped: int = 0
    documents_failed: int = 0
    chunks_created: int = 0
    embeddings_created: int = 0
    downloads: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    missing_licensed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicle_id": self.vehicle_id,
            "corpus_version": self.corpus_version,
            "manifest_hash": self.manifest_hash,
            "started_at": self.started_at.isoformat(),
            "documents_registered": self.documents_registered,
            "documents_downloaded": self.documents_downloaded,
            "documents_skipped": self.documents_skipped,
            "documents_failed": self.documents_failed,
            "chunks_created": self.chunks_created,
            "embeddings_created": self.embeddings_created,
            "downloads": self.downloads,
            "failures": self.failures,
            "missing_licensed": self.missing_licensed,
        }

    def __str__(self) -> str:
        return (
            f"vehículo {self.vehicle_id} · corpus {self.corpus_version}\n"
            f"  registrados {self.documents_registered} · "
            f"descargados {self.documents_downloaded} · "
            f"omitidos {self.documents_skipped} · "
            f"fallidos {self.documents_failed}\n"
            f"  fragmentos {self.chunks_created} · embeddings {self.embeddings_created}"
        )


def manifest_hash(path: Path) -> str:
    """Huella del manifiesto: identifica qué lista documental produjo un corpus."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_vehicle(vehicle_id: str, base: Path | None = None) -> VehicleProfile:
    """Carga el perfil declarado del vehículo."""
    import yaml

    raiz = base or CORPUS_VEHICLES
    ruta = raiz / vehicle_id / "vehicle.yaml"
    if not ruta.is_file():
        msg = f"No existe el perfil {ruta}. Registra el vehículo antes de ingerir."
        raise FileNotFoundError(msg)
    return VehicleProfile.model_validate(yaml.safe_load(ruta.read_text(encoding="utf-8")))


def run_ingestion(
    vehicle_id: str,
    manifest_path: Path,
    *,
    base: Path | None = None,
    force: bool = False,
) -> IngestionReport:
    """Ejecuta la ingesta documental y devuelve su informe."""
    raiz = (base or CORPUS_VEHICLES) / vehicle_id
    manifiesto = DocumentManifest.load(manifest_path)
    perfil = load_vehicle(vehicle_id, base)

    if manifiesto.vehicle_id != perfil.vehicle_id:
        msg = (
            f"El manifiesto declara {manifiesto.vehicle_id!r} y el perfil "
            f"{perfil.vehicle_id!r}. No se ingiere documentación cruzada."
        )
        raise ValueError(msg)

    informe = IngestionReport(
        vehicle_id=vehicle_id,
        corpus_version=manifiesto.corpus_version,
        manifest_hash=manifest_hash(manifest_path),
        started_at=datetime.now(UTC),
        documents_registered=len(manifiesto.documents),
    )

    for documento in manifiesto.documents:
        if not documento.active:
            informe.documents_skipped += 1
            continue

        if documento.access_type is not AccessType.PUBLIC or not documento.download:
            informe.documents_skipped += 1
            if documento.access_type in (AccessType.SUBSCRIPTION, AccessType.LICENSED):
                informe.missing_licensed.append(documento.document_id)
                print(missing_document_notice(documento))
                print()
            continue

        destino = raiz / "raw" / f"{documento.document_id}.pdf"
        resultado = try_download(documento, destino, force=force)

        if isinstance(resultado, DownloadRecord):
            informe.documents_downloaded += 1
            informe.downloads.append(resultado.to_dict())
            (raiz / "metadata").mkdir(parents=True, exist_ok=True)
            (raiz / "metadata" / f"{documento.document_id}.json").write_text(
                json.dumps(resultado.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"descargado  {documento.document_id}  sha256 {resultado.sha256[:16]}…")
        elif isinstance(resultado, DownloadFailure):
            informe.documents_failed += 1
            informe.failures.append(resultado.to_dict())
            print(
                f"FALLO       {documento.document_id}: {resultado.reason}\n"
                f"            {resultado.download_url}\n"
                "            No se sustituye por ninguna otra fuente."
            )

    return informe


def write_report(informe: IngestionReport) -> Path:
    """Guarda el informe con marca temporal, sin pisar los anteriores."""
    directorio = paths.ensure(paths.RESULTS / "rag_ingestion")
    marca = informe.started_at.strftime("%Y%m%dT%H%M%SZ")
    destino = directorio / f"{informe.vehicle_id}_{marca}.json"
    destino.write_text(
        json.dumps(informe.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return destino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mecanico_ia_exp.rag.ingest", description=__doc__)
    parser.add_argument("--vehicle", required=True, help="vehicle_id a ingerir")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--force", action="store_true", help="reingerir aunque la huella no haya cambiado"
    )
    args = parser.parse_args(argv)

    informe = run_ingestion(args.vehicle, args.manifest, force=args.force)
    print(f"\n{informe}")
    destino = write_report(informe)
    print(f"informe {destino.relative_to(paths.ROOT)}")

    if informe.missing_licensed:
        print(
            f"\n{MISSING_LICENSED_DOCUMENT}: "
            f"{', '.join(informe.missing_licensed)}\n"
            "El corpus está incompleto y así queda registrado. Ninguna fuente de "
            "menor autoridad los sustituye."
        )
    return 0 if informe.documents_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
