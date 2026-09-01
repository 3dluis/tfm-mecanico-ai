"""Metadata y procedencia de los conjuntos de datos.

Un dataset sin procedencia no es utilizable en un experimento: no se puede decir
de dónde salió, con qué semilla, ni si mezcla datos sintéticos con reales. Este
módulo obliga a declararlo.

La separación entre sintético y real no es una etiqueta administrativa. Los
sintéticos sirven para control experimental; los reales, para validar. Mezclarlos
sin conservar la marca haría imposible saber sobre qué se está midiendo, y
convertiría cualquier conclusión sobre datos reales en una afirmación sin
respaldo.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

DatasetType = Literal["synthetic", "real"]


class DatasetMetadata(BaseModel):
    """Ficha de procedencia de un conjunto de datos."""

    dataset_id: str
    dataset_type: DatasetType
    source: str
    """De dónde salió: el generador y su versión, o la fuente real concreta."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: str
    sampling_rate_hz: float
    vehicle_or_simulator: str
    notes: str = ""

    # Detalle que hace la generación reproducible y el reparto auditable.
    seed: int | None = None
    n_sessions: int = 0
    n_samples: int = 0
    signals: tuple[str, ...] = ()
    fault_ids: tuple[str, ...] = ()
    session_ids: tuple[str, ...] = ()

    def write(self, path: Path) -> Path:
        """Guarda la ficha junto al dataset."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return path

    @classmethod
    def read(cls, path: Path) -> DatasetMetadata:
        """Recupera una ficha guardada."""
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))
