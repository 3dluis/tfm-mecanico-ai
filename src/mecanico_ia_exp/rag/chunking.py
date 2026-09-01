"""Troceado estructural con procedencia.

Trocear por número de caracteres es rápido y destruye lo único que hace citable a
un fragmento. Un procedimiento diagnóstico partido a mitad de su condición de
detección produce dos fragmentos que, por separado, no sostienen nada.

Aquí la estructura del manual **forma parte de la procedencia**: capítulo,
sección, subsección y página viajan con el texto. Un fragmento sabe de dónde
salió, y por eso una afirmación que lo cite se puede comprobar.

Regla que no se rompe: **un fragmento no cruza páginas no contiguas**. El rango
``page_start``-``page_end`` siempre corresponde al texto que contiene.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from mecanico_ia_exp.rag.loaders import LoadedDocument

CHUNKING_VERSION = "1.0.0"

#: Tamaño objetivo en caracteres. No es un corte duro: solo se parte en una
#: frontera estructural o, en su defecto, al final de una frase.
TAMANO_OBJETIVO = 1200
TAMANO_MAXIMO = 2000
TAMANO_MINIMO = 120

#: Códigos de diagnóstico OBD-II. La letra indica el sistema y los cuatro
#: caracteres restantes son hexadecimales: B104F y P0102 son ambos válidos.
PATRON_DTC = re.compile(r"\b([PBCU][0-2][0-9A-F]{3})\b")

#: Motores a los que un procedimiento del manual declara aplicar, en su cabecera.
PATRON_MOTORES = re.compile(r"\[([A-Z0-9]{2}(?:\s*,\s*[A-Z0-9]{2})*)\]")

#: Marcadores estructurales del manual de taller. Abren un fragmento nuevo.
MARCADORES = (
    "DETECTION CONDITION",
    "Diagnostic procedure",
    "DIAGNOSTIC PROCEDURE",
    "Diagnostic support note",
    "POSSIBLE CAUSE",
    "INSPECTION PROCEDURE",
    "SYMPTOM TROUBLESHOOTING",
    "PURPOSE",
    "PREPARATION",
    "PROCEDURE",
    "SPECIFICATION",
    "CAUTION",
    "WARNING",
    "NOTE",
)
_PATRON_MARCADOR = re.compile(r"(?=(?:" + "|".join(re.escape(m) for m in MARCADORES) + r"))")


class VehicleSystem(StrEnum):
    """Sistema del vehículo al que se refiere un fragmento."""

    ENGINE = "ENGINE"
    FUEL = "FUEL"
    AIR_INTAKE = "AIR_INTAKE"
    IGNITION = "IGNITION"
    COOLING = "COOLING"
    EMISSIONS = "EMISSIONS"
    TRANSMISSION = "TRANSMISSION"
    ELECTRICAL = "ELECTRICAL"
    OBD = "OBD"
    OTHER = "OTHER"


class Classification(StrEnum):
    """Cómo se obtuvo la clasificación de sistema.

    Se registra porque no vale lo mismo: una clasificación derivada de palabras
    clave es una conjetura útil, no un dato del manual, y quien lea el fragmento
    debe poder distinguirlo.
    """

    EXPLICIT = "explicit"
    """Consta en la estructura del documento."""

    DERIVED = "derived"
    """Deducida de términos del texto."""

    UNKNOWN = "unknown"
    """No hay base para clasificar."""


#: Términos por sistema. Deliberadamente específicos: "sensor" o "valve" a secas
#: clasificarían medio manual en cualquier categoría.
TERMINOS: dict[VehicleSystem, tuple[str, ...]] = {
    VehicleSystem.COOLING: ("thermostat", "coolant", "radiator", "ect sensor", "cooling fan"),
    VehicleSystem.AIR_INTAKE: (
        "maf sensor",
        "mass airflow",
        "intake air",
        "throttle valve",
        "air cleaner",
        "intake manifold",
        "iat sensor",
    ),
    VehicleSystem.FUEL: (
        "fuel injector",
        "fuel pump",
        "fuel trim",
        "fuel pressure",
        "fuel line",
        "purge valve",
    ),
    VehicleSystem.IGNITION: (
        "ignition coil",
        "spark plug",
        "ignition timing",
        "misfire",
        "knock sensor",
    ),
    VehicleSystem.EMISSIONS: (
        "ho2s",
        "o2 sensor",
        "catalytic",
        "evap",
        "egr",
        "oxygen sensor",
        "emission",
    ),
    VehicleSystem.OBD: (
        "dtc",
        "malfunction indicator",
        "pcm monitor",
        "on - board diagnostic",
        "freeze frame",
        "readiness",
    ),
    VehicleSystem.TRANSMISSION: (
        "transaxle",
        "transmission",
        "clutch",
        "gear shift",
        "selector lever",
    ),
    VehicleSystem.ELECTRICAL: (
        "wiring harness",
        "connector",
        "circuit",
        "battery",
        "ground point",
        "relay",
    ),
    VehicleSystem.ENGINE: (
        "cylinder head",
        "camshaft",
        "crankshaft",
        "timing chain",
        "valve clearance",
        "engine mount",
    ),
}


@dataclass(frozen=True)
class Chunk:
    """Fragmento con toda su procedencia."""

    chunk_id: str
    document_id: str
    version_id: str
    vehicle_id: str
    ordinal: int
    text: str
    content_hash: str

    language: str = "en"
    """Idioma del fragmento. Lo hereda del documento; no se adivina."""

    chapter: str | None = None
    section: str | None = None
    subsection: str | None = None
    page_start: int | None = None
    page_end: int | None = None

    dtc_codes: tuple[str, ...] = ()
    vehicle_system: VehicleSystem = VehicleSystem.OTHER
    system_classification: Classification = Classification.UNKNOWN
    engine_codes: tuple[str, ...] = ()
    source_file: str | None = None
    n_tokens: int = 0

    def provenance(self) -> str:
        """Cita legible. Nunca 'según el manual' a secas."""
        partes = [self.document_id]
        if self.chapter:
            partes.append(f"capítulo {self.chapter}")
        if self.section:
            partes.append(f"sección «{self.section}»")
        if self.page_start is not None:
            pagina = (
                f"página {self.page_start}"
                if self.page_start == self.page_end
                else f"páginas {self.page_start}-{self.page_end}"
            )
            partes.append(pagina)
        if self.source_file:
            partes.append(self.source_file)
        return " · ".join(partes)


@dataclass
class ChunkingConfig:
    """Parámetros del troceado. Se registran con la ingesta."""

    target_size: int = TAMANO_OBJETIVO
    max_size: int = TAMANO_MAXIMO
    min_size: int = TAMANO_MINIMO
    version: str = CHUNKING_VERSION
    extra: dict[str, str] = field(default_factory=dict)


def extract_dtc_codes(texto: str) -> tuple[str, ...]:
    """Códigos DTC presentes en el texto, sin inventar ninguno.

    Solo se devuelven códigos que aparecen literalmente. No se infieren
    asociaciones entre un síntoma y un código: eso sería fabricar la evidencia
    que el experimento pretende verificar.
    """
    return tuple(sorted(set(PATRON_DTC.findall(texto))))


def extract_engine_codes(texto: str) -> tuple[str, ...]:
    """Motores que el fragmento declara cubrir, de la forma ``[ZJ, Z6]``.

    Importa porque un procedimiento de otro motor no aplica al vehículo aunque
    coincidan marca, modelo y año.
    """
    codigos: set[str] = set()
    for grupo in PATRON_MOTORES.findall(texto):
        for codigo in grupo.split(","):
            limpio = codigo.strip()
            if re.fullmatch(r"[A-Z]{1,2}[0-9]?", limpio) or limpio in {"LF", "Z6", "ZJ", "L3"}:
                codigos.add(limpio)
    return tuple(sorted(codigos))


def classify_system(texto: str) -> tuple[VehicleSystem, Classification]:
    """Sistema del vehículo, con la forma en que se obtuvo."""
    minuscula = texto.lower()
    puntuaciones = {
        sistema: sum(minuscula.count(t) for t in terminos) for sistema, terminos in TERMINOS.items()
    }
    mejor = max(puntuaciones, key=lambda s: puntuaciones[s])
    if puntuaciones[mejor] == 0:
        return VehicleSystem.OTHER, Classification.UNKNOWN
    return mejor, Classification.DERIVED


def _titulo_de(documento: LoadedDocument) -> str:
    """Título de la sección: la primera línea con aspecto de encabezado."""
    for pagina in documento.pages:
        for linea in pagina.text.split("\n"):
            limpia = linea.strip()
            if len(limpia) < 4:
                continue
            # Los encabezados del manual van en mayúsculas y sin punto final.
            sin_codigo = re.sub(r"\b[A-Z]\d[A-Z]\d{9,}\b", "", limpia).strip()
            if sin_codigo and sin_codigo == sin_codigo.upper() and len(sin_codigo) < 90:
                return sin_codigo.rstrip(" .")
            return limpia[:90].rstrip(" .")
    return ""


def _partir_pagina(texto: str, config: ChunkingConfig) -> list[str]:
    """Parte el texto de una página en trozos por frontera estructural."""
    if len(texto) <= config.max_size:
        return [texto] if texto.strip() else []

    piezas = [p for p in _PATRON_MARCADOR.split(texto) if p.strip()]
    if len(piezas) == 1:
        # Sin marcadores: se parte por frases, nunca a mitad de palabra.
        piezas = re.split(r"(?<=[.:;])\s+", texto)

    trozos: list[str] = []
    actual = ""
    for pieza in piezas:
        if actual and len(actual) + len(pieza) > config.target_size:
            trozos.append(actual.strip())
            actual = pieza
        else:
            actual = f"{actual} {pieza}".strip() if actual else pieza
        while len(actual) > config.max_size:
            corte = actual.rfind(" ", 0, config.max_size)
            corte = corte if corte > config.min_size else config.max_size
            trozos.append(actual[:corte].strip())
            actual = actual[corte:].strip()
    if actual.strip():
        trozos.append(actual.strip())
    return [t for t in trozos if len(t) >= config.min_size or not trozos]


def chunk_document(
    documento: LoadedDocument,
    *,
    document_id: str,
    version_id: str,
    vehicle_id: str,
    chapter: str | None = None,
    language: str = "en",
    config: ChunkingConfig | None = None,
    relative_to: Path | None = None,
) -> list[Chunk]:
    """Trocea un documento conservando su procedencia."""
    cfg = config or ChunkingConfig()
    seccion = _titulo_de(documento)
    ruta = (
        str(documento.source_file.relative_to(relative_to))
        if relative_to and relative_to in documento.source_file.parents
        else documento.source_file.name
    )

    fragmentos: list[Chunk] = []
    ordinal = 0
    for pagina in documento.pages:
        if not pagina.text.strip():
            continue
        for trozo in _partir_pagina(pagina.text, cfg):
            sistema, clasificacion = classify_system(trozo)
            huella = hashlib.sha256(trozo.encode("utf-8")).hexdigest()
            fragmentos.append(
                Chunk(
                    chunk_id=f"{version_id}:{ordinal:05d}",
                    document_id=document_id,
                    version_id=version_id,
                    vehicle_id=vehicle_id,
                    ordinal=ordinal,
                    text=trozo,
                    content_hash=huella,
                    language=language,
                    chapter=chapter,
                    section=seccion or None,
                    subsection=None,
                    # Un fragmento nace dentro de una página y no la abandona:
                    # así el rango citado siempre corresponde a su contenido.
                    page_start=pagina.number,
                    page_end=pagina.number,
                    dtc_codes=extract_dtc_codes(trozo),
                    vehicle_system=sistema,
                    system_classification=clasificacion,
                    engine_codes=extract_engine_codes(trozo),
                    source_file=ruta,
                    n_tokens=len(trozo.split()),
                )
            )
            ordinal += 1
    return fragmentos
