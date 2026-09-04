"""Cabecera de identificación de los registros de experimento.

Un registro sin identificación no es un artefacto: es un fichero. Sin commit ni
fecha, dos ejecuciones distintas del mismo experimento son indistinguibles desde
el propio registro, y una sobrescritura es invisible.

Eso ocurrió: los informes de tres fases publicaban cifras de ejecuciones que un
commit posterior había sustituido, y el defecto solo se detectó comparando el
historial de Git con el árbol de trabajo. La regla estaba escrita en tres
documentos del proyecto y ninguno de los quince registros la cumplía.

Este módulo la hace obligatoria en el punto donde se escribe el registro, que es
el único sitio donde una regla de este tipo se cumple sola.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _git(*args: str) -> str | None:
    """Devuelve la salida de un comando de Git, o ``None`` fuera de un repositorio."""
    try:
        salida = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return salida.stdout.strip() if salida.returncode == 0 else None


def cabecera(
    experiment_id: str,
    *,
    seed: int | None = None,
    dataset_id: str | None = None,
    dataset_type: str | None = None,
    corpus_version: str | None = None,
    embedding_model: str | None = None,
    model: str | None = None,
    prompt_version: str | None = None,
    goldset: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construye la cabecera con que se identifica una ejecución.

    ``commit`` y ``dirty`` proceden de Git. Un registro escrito con el árbol
    sucio no es reproducible desde el commit que declara, y por eso el campo se
    escribe en lugar de omitirse: es preferible un registro que declare su propia
    debilidad a uno que la esconda.

    Los campos que no aplican al experimento se omiten; los que aplican y no se
    conocen se escriben como ``None``, que es una afirmación distinta de no
    estar.
    """
    commit = _git("rev-parse", "HEAD")
    estado = _git("status", "--porcelain")
    datos: dict[str, Any] = {
        "experiment_id": experiment_id,
        "commit": commit,
        "dirty": None if estado is None else bool(estado.strip()),
        "executed_at": datetime.now(UTC).isoformat(),
    }
    opcionales = {
        "seed": seed,
        "dataset_id": dataset_id,
        "dataset_type": dataset_type,
        "corpus_version": corpus_version,
        "embedding_model": embedding_model,
        "model": model,
        "prompt_version": prompt_version,
        "goldset": goldset,
    }
    datos.update({k: v for k, v in opcionales.items() if v is not None})
    if extra:
        datos.update(extra)
    return datos


#: Campos que todo registro debe llevar. Se comprueba en los tests.
CAMPOS_OBLIGATORIOS: frozenset[str] = frozenset({"experiment_id", "commit", "dirty", "executed_at"})


def escribir(destino: Path, contenido: dict[str, Any], **kwargs: Any) -> Path:
    """Escribe un registro con su cabecera delante.

    La cabecera va primero en el fichero por una razón práctica: quien lo abre
    ve antes de qué ejecución habla que qué obtuvo.
    """
    experiment_id = str(contenido.get("experiment_id", destino.stem))
    documento = cabecera(experiment_id, **kwargs)
    documento.update({k: v for k, v in contenido.items() if k != "experiment_id"})
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(documento, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destino
