"""Model Registry del TFM: filesystem + JSON, sin servicio independiente (ADR-0022).

Catálogo lógico común para modelos ML, LLM y de embeddings. Cada entrada, experimento y
training run es un contrato de ``mecanico_contracts.models_registry`` serializado a JSON
en ``ai-models/registry/``. Las transiciones de estado pasan por
``validate_status_transition`` (un modelo NO llega a EDGE_APPROVED solo por métricas
offline). El registro es la fuente del ModelRouter futuro (capacidades por modelo).
"""

import hashlib
import json
from pathlib import Path

from mecanico_contracts import (
    ModelEvaluation,
    ModelExperiment,
    ModelRegistryEntry,
    ModelStatus,
    TrainingRun,
    validate_status_transition,
)

_ENTRIES = "models"
_EXPERIMENTS = "experiments"
_RUNS = "training-runs"
_EVALUATIONS = "evaluations"


def sha256_of(path: Path) -> str:
    """Checksum de un artefacto (verificación de integridad del registro)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class ModelRegistry:
    """Acceso al registro en disco. Determinista: mismo contenido ⇒ mismos bytes."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        for sub in (_ENTRIES, _EXPERIMENTS, _RUNS, _EVALUATIONS):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ persistencia
    @staticmethod
    def _write(path: Path, payload: str) -> None:
        path.write_text(payload + "\n", encoding="utf-8")

    @staticmethod
    def _dump(model: ModelRegistryEntry | ModelExperiment | TrainingRun | ModelEvaluation) -> str:
        return json.dumps(
            json.loads(model.model_dump_json()), indent=2, ensure_ascii=False, sort_keys=True
        )

    def _entry_path(self, model_id: str, version: str) -> Path:
        safe_version = version.replace(":", "_")  # ':' es ilegal en macOS Finder/Windows
        return self.root / _ENTRIES / f"{model_id}@{safe_version}.json"

    # ------------------------------------------------------------------ modelos
    def register(self, entry: ModelRegistryEntry) -> Path:
        """Alta o sobreescritura consciente de una entrada del catálogo."""
        path = self._entry_path(entry.model_id, entry.version)
        self._write(path, self._dump(entry))
        return path

    def get(self, model_id: str, version: str) -> ModelRegistryEntry:
        raw = self._entry_path(model_id, version).read_text(encoding="utf-8")
        return ModelRegistryEntry.model_validate_json(raw)

    def entries(self) -> list[ModelRegistryEntry]:
        return sorted(
            (
                ModelRegistryEntry.model_validate_json(p.read_text(encoding="utf-8"))
                for p in (self.root / _ENTRIES).glob("*.json")
            ),
            key=lambda e: (e.model_id, e.version),
        )

    def update_status(self, model_id: str, version: str, new_status: ModelStatus) -> None:
        """Transición de ciclo de vida VALIDADA (lanza ValueError si es ilegal)."""
        entry = self.get(model_id, version)
        validate_status_transition(entry.status, new_status)
        self.register(entry.model_copy(update={"status": new_status}))

    def verify_artifact(self, model_id: str, version: str, artifact: Path) -> bool:
        """True si el checksum del artefacto coincide con el registrado."""
        entry = self.get(model_id, version)
        if entry.checksum is None:
            msg = f"{model_id}@{version}: la entrada no registra checksum"
            raise ValueError(msg)
        return sha256_of(artifact) == entry.checksum

    # ------------------------------------------------------- experimentos y runs
    def save_experiment(self, exp: ModelExperiment) -> Path:
        path = self.root / _EXPERIMENTS / f"{exp.experiment_id}.json"
        self._write(path, self._dump(exp))
        return path

    def get_experiment(self, experiment_id: str) -> ModelExperiment:
        raw = (self.root / _EXPERIMENTS / f"{experiment_id}.json").read_text(encoding="utf-8")
        return ModelExperiment.model_validate_json(raw)

    def save_training_run(self, run: TrainingRun) -> Path:
        path = self.root / _RUNS / f"{run.training_run_id}.json"
        self._write(path, self._dump(run))
        return path

    def save_evaluation(self, ev: ModelEvaluation) -> Path:
        path = self.root / _EVALUATIONS / f"{ev.evaluation_id}.json"
        self._write(path, self._dump(ev))
        return path

    def evaluations(self, model_id: str | None = None) -> list[ModelEvaluation]:
        evs = [
            ModelEvaluation.model_validate_json(p.read_text(encoding="utf-8"))
            for p in (self.root / _EVALUATIONS).glob("*.json")
        ]
        if model_id is not None:
            evs = [e for e in evs if e.model_id == model_id]
        return sorted(evs, key=lambda e: e.evaluation_id)

    def training_runs(self, experiment_id: str | None = None) -> list[TrainingRun]:
        runs = [
            TrainingRun.model_validate_json(p.read_text(encoding="utf-8"))
            for p in (self.root / _RUNS).glob("*.json")
        ]
        if experiment_id is not None:
            runs = [r for r in runs if r.experiment_id == experiment_id]
        return sorted(runs, key=lambda r: r.training_run_id)

    # ---------------------------------------------------------------- integridad
    def check(self) -> list[str]:
        """Validación ligera (CI): todo JSON parsea como contrato y las referencias
        experimento↔run↔modelo existen. Devuelve la lista de problemas."""
        problems: list[str] = []
        entries = {(e.model_id, e.version) for e in self.entries()}
        run_ids = {r.training_run_id for r in self.training_runs()}
        for exp_path in (self.root / _EXPERIMENTS).glob("*.json"):
            exp = ModelExperiment.model_validate_json(exp_path.read_text(encoding="utf-8"))
            problems.extend(
                f"{exp.experiment_id}: training run inexistente {rid}"
                for rid in exp.training_run_ids
                if rid not in run_ids
            )
        for run in self.training_runs():
            if (run.model_id, run.model_version) not in entries:
                problems.append(
                    f"{run.training_run_id}: modelo {run.model_id}@{run.model_version} sin entrada"
                )
        for ev in self.evaluations():
            if (ev.model_id, ev.model_version) not in entries:
                problems.append(
                    f"{ev.evaluation_id}: modelo {ev.model_id}@{ev.model_version} sin entrada"
                )
        return problems
