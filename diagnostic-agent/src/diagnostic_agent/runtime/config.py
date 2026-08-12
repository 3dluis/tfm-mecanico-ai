"""Configuración del Edge Agent Runtime: feature flags experimentales y límites duros.

Las arquitecturas A0–A6 del diseño experimental (docs/agent-runtime/12, ADR-0018) son
configuraciones de esta clase, no productos distintos.
"""

from dataclasses import dataclass, field
from typing import Any

from mecanico_contracts import EpistemicLevel, MemoryMode

GRAPH_VERSION = "rt1"


@dataclass
class StopConditions:
    """Límites duros del loop (ADR-0017). Superarlos fuerza Report con outcome honesto."""

    max_iterations: int = 4
    max_execution_time_s: float = 120.0
    max_hypotheses: int = 5
    max_tool_calls: int = 20
    max_tool_retries: int = 2
    max_llm_calls: int = 8
    minimum_evidence: int = 2  # piezas de soporte para la hipótesis top
    minimum_confidence: float = 0.6  # PROBABLE


@dataclass
class RuntimeConfig:
    """Flags de arquitectura + límites + contexto epistemológico."""

    memory_mode: MemoryMode = MemoryMode.EPISODIC
    enable_critic: bool = True
    enable_loop: bool = True  # False = una sola pasada (A1-A3)
    epistemic_level: EpistemicLevel = EpistemicLevel.SIMULATED
    stop: StopConditions = field(default_factory=StopConditions)
    model_router: dict[str, str] = field(
        default_factory=lambda: {
            "triage": "deterministic",
            "hypothesize": "heuristic",  # u 'ollama:<tag>' cuando se elija el modelo
            "critic": "deterministic-checklist",
            "report": "template",
            "retrieval": "lexical-v1",
            "anomaly": "lof-onnx",
        }
    )
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def architecture(cls, arm: str) -> "RuntimeConfig":
        """Preconfiguraciones A1–A6 (A0 no usa el runtime: baseline puro de detección)."""
        presets: dict[str, dict[str, Any]] = {
            "A1": {"memory_mode": MemoryMode.NONE, "enable_critic": False, "enable_loop": False},
            "A2": {"memory_mode": MemoryMode.NONE, "enable_critic": False, "enable_loop": False},
            "A3": {"memory_mode": MemoryMode.NONE, "enable_critic": True, "enable_loop": False},
            "A4": {"memory_mode": MemoryMode.EPISODIC, "enable_critic": True, "enable_loop": False},
            "A5": {
                "memory_mode": MemoryMode.EPISODIC_SEMANTIC,
                "enable_critic": True,
                "enable_loop": False,
            },
            "A6": {
                "memory_mode": MemoryMode.EPISODIC_SEMANTIC,
                "enable_critic": True,
                "enable_loop": True,
            },
        }
        if arm not in presets:
            msg = f"arquitectura desconocida: {arm} (válidas: {sorted(presets)})"
            raise ValueError(msg)
        return cls(**presets[arm])
