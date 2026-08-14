"""Higiene de dependencias: nada se importa sin declararse (reproducibilidad, ADR-0032).

Consume `tools/dep_inventory.py`, que es la herramienta canónica del inventario del stack
ML/XAI (docs/models/15). El test no fija versiones: comprueba invariantes.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from dep_inventory import build_inventory  # noqa: E402

#: Declaradas sin import directo que están JUSTIFICADAS (no son deuda):
#: tooling del gate, extras de fases futuras ya aprobadas y transitivas declaradas
#: explícitamente para fijar su rango. Ver docs/models/15_stack_ml_xai.md.
ALLOWED_DECLARED_UNUSED = {
    # tooling del gate de calidad (se invocan por CLI, no por import)
    "ruff",
    "mypy",
    "pytest-cov",
    "pre-commit",
    "types-pyyaml",
    "uvicorn",
    "alembic",
    # extras de la capa agéntica/LLM, aún no implementada (docs/agent-runtime)
    "chromadb",
    "sentence-transformers",
    "langchain-core",
    "ollama",
    # entorno de investigación opcional y driver de PostgreSQL (uso vía SQLAlchemy)
    "jupyterlab",
    "psycopg",
    # ONNX: se declara para fijar el rango; el import directo lo hace skl2onnx
    "onnx",
    # pandas: declarada en ai-models y sin uso real — deuda registrada en docs/models/15
    "pandas",
}


def test_no_hay_dependencias_usadas_sin_declarar() -> None:
    """Un import de terceros sin declaración rompe la reproducibilidad del entorno."""
    inv = build_inventory()
    assert inv["used_but_not_declared"] == [], (
        "dependencias importadas pero NO declaradas en ningún pyproject: "
        f"{inv['used_but_not_declared']} — declararlas antes de commitear"
    )


def test_todo_import_de_terceros_esta_en_el_lock() -> None:
    inv = build_inventory()
    assert inv["imported_not_in_lock"] == [], (
        f"importadas y ausentes de uv.lock: {inv['imported_not_in_lock']}"
    )


def test_declaradas_sin_uso_son_solo_las_justificadas() -> None:
    """Si aparece una nueva declarada-sin-uso, hay que justificarla o retirarla."""
    inv = build_inventory()
    inesperadas = sorted(set(inv["declared_but_unused"]) - ALLOWED_DECLARED_UNUSED)
    assert not inesperadas, (
        f"declaradas sin uso y sin justificar: {inesperadas} — "
        "documentar en docs/models/15_stack_ml_xai.md o retirar"
    )


def test_el_stack_cientifico_nuclear_esta_declarado_y_en_uso() -> None:
    """numpy, scikit-learn y scipy son CORE: deben estar declaradas e importadas."""
    inv = build_inventory()
    rows = {r["library"]: r for r in inv["inventory"]}
    for lib in ("numpy", "scikit-learn", "scipy"):
        assert lib in rows, f"{lib} debería estar importada en el repositorio"
        assert rows[lib]["declared"], f"{lib} importada pero no declarada"
    assert "source" in rows["numpy"]["categories"]
    assert rows["numpy"]["n_files"] > 10  # es transversal, no puntual
