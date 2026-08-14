"""Inventario reproducible de dependencias reales del monorepo (F20-aud).

Responde con evidencia, no por suposición: qué se **declara** en los manifiestos, qué se
**importa** de verdad en el código y dónde (paquete de origen, tests, experimentos,
herramientas), y qué versión está **congelada en `uv.lock`**.

Detecta los dos desajustes que rompen la reproducibilidad:

- ``USED_BUT_NOT_DECLARED``: se importa pero ningún manifiesto la declara.
- ``DECLARED_BUT_UNUSED``: se declara y no aparece en ningún import.

Sin dependencias nuevas: solo `ast`, `tomllib` y la librería estándar. Se ejecuta con
``uv run python tools/dep_inventory.py`` (``--json`` para volcado máquina) y lo consume el
test ``tests-integration/test_dependency_inventory.py``.
"""

import argparse
import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("shared", "obd-lab", "ai-models", "diagnostic-agent", "cloud-platform")
#: Rutas analizadas y la categoría de uso que representan.
SCAN_ROOTS: tuple[tuple[str, str], ...] = (
    ("src", "source"),
    ("tests", "tests"),
    ("experiments", "experiments"),
    ("notebooks", "notebooks"),
)
EXTRA_ROOTS: tuple[tuple[Path, str], ...] = (
    (REPO_ROOT / "tools", "tools"),
    (REPO_ROOT / "tests-integration", "tests"),
)

#: Módulo importado → distribución que lo provee (solo donde el nombre NO coincide).
IMPORT_TO_DIST: dict[str, str] = {
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "torch": "torch",
    "umap": "umap-learn",
    "dotenv": "python-dotenv",
    "skl2onnx": "skl2onnx",
    "onnxruntime": "onnxruntime",
    "PIL": "pillow",
    "psycopg": "psycopg",
    "langchain_core": "langchain-core",
    "sentence_transformers": "sentence-transformers",
    "pydantic_settings": "pydantic-settings",
    "elm": "elm327-emulator",
    "mecanico_contracts": "mecanico-contracts",
    "ai_models": "ai-models",
    "obd_lab": "obd-lab",
    "diagnostic_agent": "diagnostic-agent",
    "cloud_platform": "cloud-platform",
}
#: Paquetes propios del workspace (no son dependencias de terceros).
WORKSPACE_DISTS = {
    "mecanico-contracts",
    "ai-models",
    "obd-lab",
    "diagnostic-agent",
    "cloud-platform",
}


def _stdlib() -> set[str]:
    return set(sys.stdlib_module_names)


@dataclass
class Usage:
    """Dónde y cómo se usa una distribución."""

    dist: str
    categories: set[str] = field(default_factory=set)
    files: list[str] = field(default_factory=list)
    modules: set[str] = field(default_factory=set)


def top_level_imports(path: Path) -> set[str]:
    """Módulos de primer nivel importados en un fichero Python (incluye imports diferidos)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):  # pragma: no cover - ficheros no parseables
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


def _local_modules(roots: list[tuple[Path, str]]) -> set[str]:
    """Módulos hermanos importados por ruta (runners de experimentos, utilidades locales).

    No son dependencias de terceros: viven en el propio repositorio y se importan porque
    los runners añaden su directorio al ``sys.path``.
    """
    names: set[str] = set()
    for root, _cat in roots:
        if root.exists():
            names.update(p.stem for p in root.glob("*.py"))
    return names


def scan_imports() -> dict[str, Usage]:
    """Recorre todas las rutas relevantes y agrupa los imports por distribución."""
    std = _stdlib()
    usages: dict[str, Usage] = {}
    roots: list[tuple[Path, str]] = [
        (REPO_ROOT / member / sub, cat) for member in MEMBERS for sub, cat in SCAN_ROOTS
    ]
    roots.extend(EXTRA_ROOTS)
    local = _local_modules(roots)
    for root, category in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if ".venv" in path.parts or "__pycache__" in path.parts:
                continue
            for module in top_level_imports(path):
                if module in std or module.startswith("_") or module in local:
                    continue
                dist = IMPORT_TO_DIST.get(module, module).lower()
                u = usages.setdefault(dist, Usage(dist=dist))
                u.categories.add(category)
                u.modules.add(module)
                u.files.append(str(path.relative_to(REPO_ROOT)))
    return usages


def declared_dependencies() -> dict[str, list[str]]:
    """Distribución declarada → lista de orígenes (manifiesto y sección)."""
    out: dict[str, list[str]] = defaultdict(list)

    def _add(spec: str, origin: str) -> None:
        name = (
            spec.split(";", maxsplit=1)[0]
            .split("[", maxsplit=1)[0]
            .split(">=", maxsplit=1)[0]
            .split("==", maxsplit=1)[0]
            .split("<", maxsplit=1)[0]
            .split("~=", maxsplit=1)[0]
            .strip()
            .lower()
        )
        if name:
            out[name].append(origin)

    for rel in ["pyproject.toml", *[f"{m}/pyproject.toml" for m in MEMBERS]]:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        for spec in project.get("dependencies", []):
            _add(spec, f"{rel}:dependencies")
        for extra, specs in project.get("optional-dependencies", {}).items():
            for spec in specs:
                _add(spec, f"{rel}:optional[{extra}]")
        for group, specs in data.get("dependency-groups", {}).items():
            for spec in specs:
                _add(spec, f"{rel}:group[{group}]")
    return dict(out)


def locked_versions() -> dict[str, list[str]]:
    """Versiones presentes en uv.lock por paquete.

    OJO: el lock es universal y puede contener VARIAS versiones del mismo paquete,
    seleccionadas por marcadores de entorno (versión de Python, plataforma). Por eso la
    versión del lock NO basta para documentar qué corrió: se acompaña de la instalada.
    """
    lock = REPO_ROOT / "uv.lock"
    if not lock.exists():
        return {}
    data = tomllib.loads(lock.read_text(encoding="utf-8"))
    out: dict[str, list[str]] = defaultdict(list)
    for pkg in data.get("package", []):
        out[pkg["name"].lower()].append(pkg.get("version", ""))
    return {k: sorted(set(v)) for k, v in out.items()}


def installed_versions(names: list[str]) -> dict[str, str]:
    """Versión REALMENTE instalada en el entorno activo (fuente autoritativa de lo ejecutado)."""
    from importlib.metadata import PackageNotFoundError, version

    out: dict[str, str] = {}
    for name in names:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = ""
    return out


def build_inventory() -> dict[str, Any]:
    usages = scan_imports()
    declared = declared_dependencies()
    versions = locked_versions()
    third_party = {d: u for d, u in usages.items() if d not in WORKSPACE_DISTS}
    installed = installed_versions(sorted(third_party))
    used_not_declared = sorted(d for d in third_party if d not in declared and d in versions)
    unknown = sorted(d for d in third_party if d not in declared and d not in versions)
    declared_unused = sorted(d for d in declared if d not in usages and d not in WORKSPACE_DISTS)
    rows = []
    for dist in sorted(third_party):
        u = third_party[dist]
        rows.append(
            {
                "library": dist,
                "installed_version": installed.get(dist, ""),
                "locked_versions": versions.get(dist, []),
                "declared_in": sorted(set(declared.get(dist, []))),
                "declared": dist in declared,
                "categories": sorted(u.categories),
                "modules": sorted(u.modules),
                "n_files": len(set(u.files)),
                "example_files": sorted(set(u.files))[:5],
            }
        )
    return {
        "python_requires": ">=3.11 (`.python-version` = 3.11)",
        "package_manager": "uv (ADR-0032), uv.lock committeado",
        "n_third_party_imported": len(third_party),
        "inventory": rows,
        "used_but_not_declared": used_not_declared,
        "imported_not_in_lock": unknown,
        "declared_but_unused": declared_unused,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="volcado JSON completo")
    args = parser.parse_args()
    inv = build_inventory()
    if args.json:
        print(json.dumps(inv, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    print(f"python: {inv['python_requires']}  ·  gestor: {inv['package_manager']}")
    print(f"terceros importados: {inv['n_third_party_imported']}\n")
    print(f"{'librería':<20}{'instalada':<14}{'lock':<22}{'decl':<6}{'fich':<6}categorías")
    for row in inv["inventory"]:
        lock = ",".join(row["locked_versions"])
        print(
            f"{row['library']:<20}{row['installed_version'] or '(no inst.)':<14}{lock:<22}"
            f"{'sí' if row['declared'] else 'NO':<6}{row['n_files']:<6}"
            f"{','.join(row['categories'])}"
        )
    print(f"\nUSED_BUT_NOT_DECLARED: {inv['used_but_not_declared'] or '(ninguna)'}")
    print(f"DECLARED_BUT_UNUSED:   {inv['declared_but_unused'] or '(ninguna)'}")
    print(f"importadas fuera del lock: {inv['imported_not_in_lock'] or '(ninguna)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
