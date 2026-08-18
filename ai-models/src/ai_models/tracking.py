"""Registro reproducible de experimentos (requisito del plan de investigación).

Cada run se anexa a ``experiments/runs.jsonl`` con: dataset/sesiones, escenario/suite,
versión del código (git sha), modelo y versión, parámetros, semilla, métricas, tiempo
de inferencia y consumo aproximado de recursos.
"""

import json
import platform
import resource
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def git_sha(repo_root: Path) -> str:
    """SHA corto del commit actual (o 'sin-git' si no aplica)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "sin-git"


def peak_rss_mb() -> float:
    """Pico de RSS del proceso en MB (vía ``resource``).

    ``ru_maxrss`` está en **KB en Linux** y en **BYTES en macOS/BSD** (hallazgo F22:
    la versión anterior asumía KB siempre e inflaba ×1024 las medidas hechas en macOS).
    Corregido como requisito previo del criterio edge del pre-registro (F-PREREG §2.5).
    """
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    divisor = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return round(raw / divisor, 1)


def record_run(runs_file: Path, run: dict[str, Any]) -> None:
    """Anexa un registro de run con metadatos de entorno."""
    run = {
        "recorded_at": datetime.now(tz=UTC).isoformat(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        **run,
    }
    runs_file.parent.mkdir(parents=True, exist_ok=True)
    with runs_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(run, ensure_ascii=False, default=str) + "\n")
