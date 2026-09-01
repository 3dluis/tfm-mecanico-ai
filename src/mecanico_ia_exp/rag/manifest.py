"""Manifiesto documental: qué documentos existen, de dónde salen y qué autoridad tienen.

El manifiesto es la lista blanca. El descargador **solo** acepta URLs que
aparezcan aquí con ``download: true``: no hay rastreo, no hay descubrimiento
automático de enlaces, no hay excepciones.

La autoridad de una fuente no la determina su parecido con la consulta. Un manual
de taller del fabricante y una respuesta de foro pueden ser igual de similares a
una pregunta, y no valen lo mismo. El nivel de autoridad se declara en el
manifiesto y viaja con cada fragmento hasta la explicación final.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class AuthorityLevel(StrEnum):
    """Nivel de autoridad de la fuente."""

    A = "A"
    """Fabricante u OEM. Prioridad máxima."""

    B = "B"
    """Organismos oficiales y documentación regulatoria."""

    C = "C"
    """Documentación técnica secundaria contrastada. Requiere justificación."""


class AcquisitionChannel(StrEnum):
    """Por dónde llegó el documento, que no es lo mismo que quién lo publicó.

    Un manual de taller de Mazda descargado de un agregador sigue teniendo a
    Mazda como editor original, pero su canal de adquisición es un repositorio
    secundario. Esa distinción determina si su procedencia es verificable y si
    su redistribución está permitida: confundir ambas cosas convierte a un
    intermediario en autoridad.
    """

    OEM_OFFICIAL = "OEM_OFFICIAL"
    """Portal oficial del fabricante. Procedencia verificable."""

    REGULATORY = "REGULATORY"
    """Base pública de un organismo oficial."""

    SECONDARY_REPOSITORY = "SECONDARY_REPOSITORY"
    """Agregador de terceros. Procedencia y licencia por verificar."""

    USER_PROVIDED = "USER_PROVIDED"
    """Aportado por el autor desde una copia obtenida legítimamente."""


class DocumentType(StrEnum):
    """Tipo de documento, que determina su lugar en la jerarquía de evidencia."""

    REPAIR_MANUAL = "REPAIR_MANUAL"
    WORKSHOP_MANUAL = "WORKSHOP_MANUAL"
    ENGINE_MANUAL = "ENGINE_MANUAL"
    DIAGNOSTIC_MANUAL = "DIAGNOSTIC_MANUAL"
    DTC_DOCUMENTATION = "DTC_DOCUMENTATION"
    TECHNICAL_SERVICE_BULLETIN = "TECHNICAL_SERVICE_BULLETIN"
    ELECTRICAL_WIRING_DIAGRAM = "ELECTRICAL_WIRING_DIAGRAM"
    TECHNICAL_TRAINING = "TECHNICAL_TRAINING"
    OWNERS_MANUAL = "OWNERS_MANUAL"
    WARRANTY_MAINTENANCE_GUIDE = "WARRANTY_MAINTENANCE_GUIDE"
    NEW_CAR_FEATURES = "NEW_CAR_FEATURES"
    REGULATORY = "REGULATORY"
    SECONDARY_TECHNICAL = "SECONDARY_TECHNICAL"


#: Jerarquía de evidencia. Un número menor manda sobre uno mayor,
#: **independientemente de la puntuación de similitud**.
JERARQUIA_EVIDENCIA: dict[DocumentType, int] = {
    DocumentType.REPAIR_MANUAL: 1,
    DocumentType.WORKSHOP_MANUAL: 1,
    DocumentType.DIAGNOSTIC_MANUAL: 1,
    DocumentType.ENGINE_MANUAL: 2,
    DocumentType.DTC_DOCUMENTATION: 2,
    DocumentType.TECHNICAL_SERVICE_BULLETIN: 2,
    DocumentType.ELECTRICAL_WIRING_DIAGRAM: 3,
    DocumentType.TECHNICAL_TRAINING: 4,
    DocumentType.OWNERS_MANUAL: 5,
    DocumentType.WARRANTY_MAINTENANCE_GUIDE: 6,
    DocumentType.NEW_CAR_FEATURES: 6,
    DocumentType.REGULATORY: 7,
    DocumentType.SECONDARY_TECHNICAL: 8,
}


class AccessType(StrEnum):
    """Cómo se obtiene el documento."""

    PUBLIC = "public"
    """Accesible públicamente desde infraestructura oficial. Descargable."""

    SUBSCRIPTION = "subscription"
    """Requiere suscripción legítima. **Nunca se descarga automáticamente.**"""

    LICENSED = "licensed"
    """Obtenido con licencia. Existe localmente y no se redistribuye."""


class DocumentEntry(BaseModel):
    """Una entrada del manifiesto."""

    document_id: str
    vehicle_id: str
    document_type: DocumentType
    title: str
    publisher: str
    """Editor original. Quien produjo el documento, no quien lo sirve."""

    source_url: str
    access_type: AccessType
    authority_level: AuthorityLevel
    language: str = "en"

    download: bool = False
    """Solo se descarga si es ``True`` **y** el acceso es público."""

    redistributable: bool = False
    """Si es ``False``, el binario no entra en el repositorio."""

    acquisition_source: str | None = None
    """De dónde se obtuvo la copia. Puede no coincidir con el editor."""

    acquisition_channel: AcquisitionChannel | None = None

    manufacturer: str | None = None
    model: str | None = None
    model_year: int | None = None
    market: str | None = None
    engine_code: str | None = None
    engine_codes: list[str] = Field(default_factory=list)
    """Motores que el documento declara cubrir. Vacío = no consta."""

    generation: str | None = None
    model_year_start: int | None = None
    model_year_end: int | None = None
    """Un manual suele cubrir un rango de años, no uno solo."""

    publication_date: str | None = None
    revision: str | None = None
    source_portal: str | None = None

    verified: bool = False
    """¿Se ha inspeccionado el contenido para confirmar lo que declara?

    Un documento sin verificar **no puede sostener evidencia científica**. El
    nombre del fichero no es prueba de nada: hay que abrirlo y comprobar editor,
    modelo, rango de años, revisión y cobertura diagnóstica.
    """

    verification_notes: str = ""

    local_file: str | None = None
    sha256: str | None = None
    downloaded_at: datetime | None = None
    active: bool = True
    notes: str = ""

    @field_validator("download")
    @classmethod
    def _solo_publico_se_descarga(cls, valor: bool, info: Any) -> bool:
        """Un documento por suscripción nunca lleva ``download: true``.

        Se rechaza en la carga del manifiesto y no en el descargador: así el
        error aparece al declarar la intención, no al ejecutarla.
        """
        acceso = info.data.get("access_type")
        if valor and acceso is not None and acceso is not AccessType.PUBLIC:
            msg = (
                f"Acceso {acceso!r} no admite descarga automática. "
                "Los documentos por suscripción o licencia se obtienen "
                "legítimamente por su canal y se copian a mano."
            )
            raise ValueError(msg)
        return valor

    @property
    def evidence_rank(self) -> int:
        """Puesto en la jerarquía de evidencia. Menor es más autorizado."""
        return JERARQUIA_EVIDENCIA[self.document_type]


class SourceEntry(BaseModel):
    """Un portal o sistema del que proceden documentos."""

    source_id: str
    publisher: str
    source_type: str
    authority_level: AuthorityLevel
    access_type: AccessType
    url: str
    description: str = ""


class DocumentManifest(BaseModel):
    """Manifiesto completo de un vehículo."""

    vehicle_id: str
    corpus_version: str = "1.0.0"
    sources: list[SourceEntry] = Field(default_factory=list)
    documents: list[DocumentEntry] = Field(default_factory=list)

    @field_validator("documents")
    @classmethod
    def _identificadores_unicos(cls, valor: list[DocumentEntry]) -> list[DocumentEntry]:
        identificadores = [d.document_id for d in valor]
        repetidos = {i for i in identificadores if identificadores.count(i) > 1}
        if repetidos:
            msg = f"Identificadores de documento repetidos: {sorted(repetidos)}"
            raise ValueError(msg)
        return valor

    def model_post_init(self, _context: object) -> None:
        """Todo documento debe pertenecer al vehículo del manifiesto."""
        ajenos = [d.document_id for d in self.documents if d.vehicle_id != self.vehicle_id]
        if ajenos:
            msg = (
                f"El manifiesto de {self.vehicle_id!r} contiene documentos de otro "
                f"vehículo: {ajenos}. Nunca se mezcla documentación de vehículos "
                "distintos como si fuera equivalente."
            )
            raise ValueError(msg)

    @classmethod
    def load(cls, path: Path) -> DocumentManifest:
        """Carga y valida un manifiesto en YAML."""
        datos = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls.model_validate(datos)

    def downloadable(self) -> list[DocumentEntry]:
        """Documentos que el descargador puede tratar de obtener."""
        return [
            d
            for d in self.documents
            if d.active and d.download and d.access_type is AccessType.PUBLIC
        ]

    def by_id(self, document_id: str) -> DocumentEntry:
        for documento in self.documents:
            if documento.document_id == document_id:
                return documento
        msg = f"El manifiesto no contiene el documento {document_id!r}"
        raise KeyError(msg)
