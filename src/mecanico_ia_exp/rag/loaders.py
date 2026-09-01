"""Cargadores de documentos hacia un modelo intermedio común.

Todos los formatos convergen en ``LoadedDocument``, que conserva el texto **por
páginas**. Aplanar las páginas en una sola cadena ahorraría trabajo y destruiría
la trazabilidad: sin número de página no hay cita verificable, y una cita que no
se puede comprobar no cumple su función.

Cuando un formato no tiene paginación --HTML, texto, Markdown-- se registra una
sola página y se hace constar, en lugar de inventar una numeración.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LoadedPage:
    """Una página con su número de origen."""

    number: int
    """1-indexado, como lo cita un lector humano."""

    text: str


@dataclass
class LoadedDocument:
    """Documento cargado, listo para trocear."""

    source_file: Path
    pages: list[LoadedPage]
    paginated: bool
    """``False`` cuando el formato no tiene páginas y se registró una sola."""

    title: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return "\n".join(p.text for p in self.pages)

    @property
    def n_pages(self) -> int:
        return len(self.pages)

    def __bool__(self) -> bool:
        return any(p.text.strip() for p in self.pages)


class DocumentLoader(ABC):
    """Interfaz común. Un formato nuevo implementa esto y nada más cambia."""

    extensions: tuple[str, ...] = ()

    def handles(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    @abstractmethod
    def load(self, path: Path) -> LoadedDocument: ...


def _normalizar(texto: str) -> str:
    """Colapsa espacios sin unir palabras que estaban separadas por saltos.

    Los PDF del manual llegan con guiones de separación y espacios erráticos
    --"HO2S heater" aparece como "HO2S  heater", "bottom - bypass" con espacios
    alrededor del guion--. Se limpia lo evidente y se deja el resto: alterar más
    el texto haría que las citas no coincidieran con el original.
    """
    texto = texto.replace("­", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


class PdfDocumentLoader(DocumentLoader):
    """PDF, página a página."""

    extensions = (".pdf",)

    def load(self, path: Path) -> LoadedDocument:
        from pypdf import PdfReader

        lector = PdfReader(str(path))
        paginas = [
            LoadedPage(number=i + 1, text=_normalizar(pagina.extract_text() or ""))
            for i, pagina in enumerate(lector.pages)
        ]
        bruto = dict(lector.metadata or {})
        metadata = {str(k).lstrip("/"): str(v) for k, v in bruto.items()}
        return LoadedDocument(
            source_file=path,
            pages=paginas,
            paginated=True,
            title=metadata.get("Title", ""),
            metadata=metadata,
        )


class HtmlDocumentLoader(DocumentLoader):
    """HTML. Sin paginación: se registra una sola página y se declara."""

    extensions = (".html", ".htm")

    def load(self, path: Path) -> LoadedDocument:
        crudo = path.read_text(encoding="utf-8", errors="replace")
        titulo = ""
        encontrado = re.search(r"<title[^>]*>(.*?)</title>", crudo, re.I | re.S)
        if encontrado:
            titulo = _normalizar(encontrado.group(1))
        # Se eliminan bloques que no son contenido antes de quitar etiquetas: si
        # no, el texto de scripts y estilos acabaría en los fragmentos.
        sin_ruido = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", crudo, flags=re.I | re.S)
        texto = _normalizar(re.sub(r"<[^>]+>", " ", sin_ruido))
        return LoadedDocument(
            source_file=path,
            pages=[LoadedPage(number=1, text=texto)],
            paginated=False,
            title=titulo,
        )


class TextDocumentLoader(DocumentLoader):
    """Texto plano y Markdown."""

    extensions = (".txt", ".md", ".markdown")

    def load(self, path: Path) -> LoadedDocument:
        texto = _normalizar(path.read_text(encoding="utf-8", errors="replace"))
        titulo = ""
        primera = texto.lstrip().split("\n", 1)[0] if texto.strip() else ""
        if primera.startswith("#"):
            titulo = primera.lstrip("#").strip()
        return LoadedDocument(
            source_file=path,
            pages=[LoadedPage(number=1, text=texto)],
            paginated=False,
            title=titulo,
        )


LOADERS: tuple[DocumentLoader, ...] = (
    PdfDocumentLoader(),
    HtmlDocumentLoader(),
    TextDocumentLoader(),
)


class UnsupportedFormatError(ValueError):
    """No hay cargador para esta extensión."""


def load_document(path: Path) -> LoadedDocument:
    """Carga un documento eligiendo el cargador por su extensión."""
    for cargador in LOADERS:
        if cargador.handles(path):
            return cargador.load(path)
    admitidas = sorted({e for c in LOADERS for e in c.extensions})
    msg = f"Sin cargador para {path.suffix!r}. Admitidos: {admitidas}"
    raise UnsupportedFormatError(msg)
