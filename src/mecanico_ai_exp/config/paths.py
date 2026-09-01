"""Rutas del laboratorio, ancladas a la raíz del repositorio.

Ningún módulo compone rutas a mano: todas salen de aquí, para que un notebook
ejecutado desde ``notebooks/`` y un test ejecutado desde la raíz escriban en el
mismo sitio.
"""

from pathlib import Path

# src/mecanico_ai_exp/config/paths.py -> raíz del repositorio
ROOT = Path(__file__).resolve().parents[3]

DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
DATA_RAW_SYNTHETIC = DATA_RAW / "synthetic"
DATA_RAW_REAL = DATA_RAW / "real"
DATA_INTERIM = DATA / "interim"
DATA_PROCESSED = DATA / "processed"

CORPUS = ROOT / "corpus"
CORPUS_RAW = CORPUS / "raw"
CORPUS_PROCESSED = CORPUS / "processed"
CORPUS_MANIFESTS = CORPUS / "manifests"

MODELS = ROOT / "models"
EXPERIMENTS = ROOT / "experiments"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
CONFIGS = ROOT / "configs"
MIGRATIONS = ROOT / "migrations"
DOCS = ROOT / "docs"


def ensure(path: Path) -> Path:
    """Crea el directorio si falta y lo devuelve, para encadenar en una expresión."""
    path.mkdir(parents=True, exist_ok=True)
    return path
