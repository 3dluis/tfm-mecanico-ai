"""Las rutas se resuelven contra la raíz del repositorio, no contra el cwd."""

from __future__ import annotations

from mecanico_ai_exp.config import paths


def test_root_contiene_el_paquete() -> None:
    assert (paths.ROOT / "src" / "mecanico_ai_exp" / "__init__.py").is_file()


def test_root_contiene_pyproject() -> None:
    assert (paths.ROOT / "pyproject.toml").is_file()


def test_directorios_declarados_estan_bajo_root() -> None:
    for directorio in (
        paths.DATA_RAW_SYNTHETIC,
        paths.DATA_RAW_REAL,
        paths.CORPUS_MANIFESTS,
        paths.RESULTS,
        paths.FIGURES,
        paths.TABLES,
    ):
        assert paths.ROOT in directorio.parents


def test_ensure_es_idempotente(tmp_path: object) -> None:
    from pathlib import Path

    destino = Path(str(tmp_path)) / "a" / "b"
    assert paths.ensure(destino).is_dir()
    assert paths.ensure(destino).is_dir()
