"""Exporta los contratos a JSON Schema (``shared/schemas/``) para consumidores no-Python.

Uso: ``python -m mecanico_contracts.export_schemas [directorio_salida]``
(o ``make schemas`` desde la raíz del monorepo). Ver ADR-0007.
"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel

import mecanico_contracts as mc

EXPORTABLE: list[type[BaseModel]] = [
    mc.OBDReading,
    mc.VehicleTelemetry,
    mc.DTCRecord,
    mc.DetectedAnomaly,
    mc.DiagnosticHypothesis,
    mc.DiagnosticResult,
    mc.MaintenanceRecommendation,
    mc.AgentEvent,
    mc.CaseRecord,
    mc.ModelManifest,
    mc.ScenarioSpec,
    mc.RecordedSession,
    mc.SyncEnvelope,
    mc.TelemetrySession,
    mc.TelemetryPoint,
    mc.TelemetryWindow,
    mc.FeatureVector,
    mc.ModelInference,
    mc.DiagnosticCase,
    mc.DiagnosticEvidence,
    mc.ProvenanceRecord,
    mc.CaseMemory,
    mc.LearnedPattern,
    mc.PatternRelation,
    mc.DiagnosticFeedback,
    mc.MaintenanceEvent,
    mc.AgentRun,
    mc.AgentStep,
    mc.RetrievalEvent,
    mc.KnowledgeDocument,
    mc.KnowledgeChunk,
    mc.VehicleEvent,
    mc.EventFeatureVector,
    mc.EventBaseline,
    mc.TrainingRun,
    mc.ModelExperiment,
    mc.ModelEvaluation,
    mc.ModelRegistryEntry,
    mc.ModelDeployment,
    mc.HardwareValidation,
]


def export_all(out_dir: Path) -> list[Path]:
    """Escribe un ``<Modelo>.schema.json`` por contrato y devuelve las rutas."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for model in EXPORTABLE:
        path = out_dir / f"{model.__name__}.schema.json"
        path.write_text(
            json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[2] / "schemas"
    files = export_all(target)
    print(f"{len(files)} esquemas exportados a {target}")
