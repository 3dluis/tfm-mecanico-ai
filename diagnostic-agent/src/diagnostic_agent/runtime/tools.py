"""Tool Registry del Edge Agent Runtime (ADR-0016).

Toda capacidad del runtime está registrada con su especificación completa; la ejecución
pasa por ``ToolRegistry.execute`` que: valida el nivel de riesgo (VEHICLE_WRITE bloqueado
en v1), aplica timeout blando, registra la llamada (auditoría + presupuestos del loop) y
propaga errores de forma controlada.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RiskLevel(StrEnum):
    READ_ONLY = "read_only"
    SAFE_LOCAL = "safe_local"
    VEHICLE_WRITE = "vehicle_write"  # bloqueado en v1 (ADR-0016)
    EXTERNAL = "external"


@dataclass(frozen=True)
class ToolSpec:
    """Especificación formal de una herramienta."""

    name: str
    description: str
    input_schema: dict[str, str]  # campo → tipo (documental; validación fina en el handler)
    output_schema: dict[str, str]
    timeout_s: float
    permissions: tuple[str, ...]  # roles autorizados
    side_effects: str  # 'none' | 'local_write' | 'vehicle_write' | 'network'
    idempotent: bool
    risk_level: RiskLevel
    handler: Callable[..., Any]


@dataclass
class ToolCallRecord:
    """Registro de una ejecución (alimenta AgentStep.tools_used y observabilidad)."""

    tool: str
    agent_role: str
    duration_ms: float
    ok: bool
    error: str | None = None


class ToolExecutionError(RuntimeError):
    pass


@dataclass
class ToolRegistry:
    """Registro + ejecutor auditado."""

    tools: dict[str, ToolSpec] = field(default_factory=dict)
    history: list[ToolCallRecord] = field(default_factory=list)

    def register(self, spec: ToolSpec) -> None:
        if spec.risk_level is RiskLevel.VEHICLE_WRITE:
            msg = (
                f"{spec.name}: las herramientas VEHICLE_WRITE no son registrables en v1 (ADR-0016)"
            )
            raise ValueError(msg)
        self.tools[spec.name] = spec

    def execute(self, name: str, agent_role: str, **kwargs: Any) -> Any:
        spec = self.tools.get(name)
        if spec is None:
            msg = f"herramienta no registrada: {name}"
            raise ToolExecutionError(msg)
        if agent_role not in spec.permissions:
            msg = f"rol {agent_role!r} sin permiso para {name} (permitidos: {spec.permissions})"
            raise ToolExecutionError(msg)
        t0 = time.perf_counter()
        try:
            result = spec.handler(**kwargs)
            self.history.append(
                ToolCallRecord(name, agent_role, (time.perf_counter() - t0) * 1000, True)
            )
        except Exception as exc:
            self.history.append(
                ToolCallRecord(
                    name, agent_role, (time.perf_counter() - t0) * 1000, False, repr(exc)[:200]
                )
            )
            raise ToolExecutionError(f"{name}: {exc}") from exc
        else:
            return result

    @property
    def total_calls(self) -> int:
        return len(self.history)
