"""Auditoría del entorno de ejecución.

Comprueba, sin modificar nada, que la máquina reúne lo que el laboratorio
necesita: intérprete, acelerador, base de datos y extensión vectorial. Es lo
primero que se ejecuta en una máquina nueva y lo que abre el notebook 00.

El fallback a CPU cuando MPS no está disponible se reporta explícitamente: un
resultado obtenido en CPU y otro en MPS no son intercambiables sin decirlo.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Check:
    """Resultado de una comprobación individual."""

    name: str
    ok: bool
    detail: str

    def __str__(self) -> str:
        return f"[{'OK ' if self.ok else 'FALLA'}] {self.name}: {self.detail}"


@dataclass
class EnvironmentReport:
    """Conjunto de comprobaciones con veredicto agregado."""

    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append(Check(name=name, ok=ok, detail=detail))

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in self.checks],
        }

    def __str__(self) -> str:
        return "\n".join(str(check) for check in self.checks)


def check_python() -> Check:
    version = sys.version_info
    ok = (version.major, version.minor) == (3, 11)
    return Check(
        name="python",
        ok=ok,
        detail=f"{platform.python_version()} ({sys.executable})"
        + ("" if ok else " — se espera 3.11"),
    )


def check_platform() -> Check:
    machine = platform.machine()
    ok = platform.system() == "Darwin" and machine == "arm64"
    detail = f"{platform.system()} {platform.release()} / {machine}"
    if not ok:
        detail += " — el entorno oficial es macOS Apple Silicon; otras plataformas son portables"
    return Check(name="plataforma", ok=ok, detail=detail)


def check_torch_device() -> Check:
    """Determina el dispositivo de cómputo. La ausencia de MPS no es un fallo:
    es una condición del entorno que debe quedar registrada en el experimento."""
    try:
        import torch
    except ImportError:
        return Check(
            name="torch",
            ok=False,
            detail="no instalado — `uv sync --extra ml`",
        )

    if torch.backends.mps.is_available():
        detail = f"torch {torch.__version__} — dispositivo mps"
    elif torch.backends.mps.is_built():
        detail = f"torch {torch.__version__} — mps compilado pero no disponible; se usará cpu"
    else:
        detail = f"torch {torch.__version__} — sin mps; se usará cpu"
    return Check(name="torch", ok=True, detail=detail)


def resolve_device() -> str:
    """Dispositivo de cómputo efectivo. Nunca asume CUDA."""
    try:
        import torch
    except ImportError:
        return "cpu"
    return "mps" if torch.backends.mps.is_available() else "cpu"


def check_database() -> Check:
    """Conectividad con PostgreSQL. Solo lee; no crea ni altera nada."""
    from mecanico_ia_exp.config.settings import get_settings

    settings = get_settings().database
    try:
        import sqlalchemy as sa

        engine = sa.create_engine(settings.url, connect_args={"connect_timeout": 5})
        with engine.connect() as connection:
            version = connection.execute(sa.text("select version()")).scalar_one()
        engine.dispose()
    # Cualquier fallo de conexión es información, no una excepción a propagar.
    except Exception as error:
        return Check(
            name="postgresql",
            ok=False,
            detail=f"sin conexión a {settings.host}:{settings.port}/{settings.name}: {error}",
        )
    return Check(name="postgresql", ok=True, detail=str(version).split(" on ")[0])


def check_pgvector() -> Check:
    """Disponibilidad de la extensión vectorial, instalada o instalable."""
    from mecanico_ia_exp.config.settings import get_settings

    settings = get_settings().database
    try:
        import sqlalchemy as sa

        engine = sa.create_engine(settings.url, connect_args={"connect_timeout": 5})
        with engine.connect() as connection:
            row = connection.execute(
                sa.text(
                    "select default_version, installed_version "
                    "from pg_available_extensions where name = 'vector'"
                )
            ).one_or_none()
        engine.dispose()
    except Exception as error:
        return Check(name="pgvector", ok=False, detail=f"no verificable: {error}")

    if row is None:
        return Check(
            name="pgvector",
            ok=False,
            detail="extensión 'vector' no disponible en este servidor",
        )
    available, installed = row
    estado = f"instalada {installed}" if installed else f"disponible {available}, sin instalar"
    return Check(name="pgvector", ok=True, detail=estado)


def audit(include_database: bool = True) -> EnvironmentReport:
    """Ejecuta la auditoría completa del entorno."""
    report = EnvironmentReport()
    report.checks.extend([check_python(), check_platform(), check_torch_device()])
    if include_database:
        db = check_database()
        report.checks.append(db)
        if db.ok:
            report.checks.append(check_pgvector())
    return report
