"""Auditoría ejecutable de la exclusión triple E-DET / E-RAG / E-MEM (B0.5, F24).

Convierte la matriz de contaminación del núcleo científico (alineación v3 §9) en
comprobaciones ejecutables: verifica que ninguna clase held-out haya entrado por el lado
de entrenamiento/conocimiento — suites y sesiones de train/validation, registro de
corridas de entrenamiento, corpus RAG, plantillas de prompt y semillas de memoria — y
emite un informe JSON con la evidencia exacta (fichero, línea, término) de cada hallazgo.

La especificación de qué buscar y dónde es DECLARATIVA y se congela con el pre-registro:
``ai-models/configs/heldout-exclusions.yaml``. Un held-out en el lado de evaluación no es
contaminación (whitelist documentada en esa misma especificación).

Salidas: exit 0 = sin violaciones · exit 1 = violaciones (el run confirmatorio queda
inválido, NO CONCLUYENTE) · el informe se escribe siempre.

Uso:
    python tools/contamination_audit.py [--report out.json] [--memory-state export.jsonl]
"""

import argparse
import glob
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "ai-models" / "configs" / "heldout-exclusions.yaml"
DEFAULT_REPORT = REPO_ROOT / "ai-models" / "experiments" / "contamination_audit.json"


def _norm(text: str) -> str:
    """Espacios normalizados (los términos de mecanismo pueden cruzar saltos de línea)."""
    return re.sub(r"\s+", " ", text)


def _readable(path: Path) -> str:
    """Contenido del fichero con los escapes JSON resueltos cuando aplica.

    Un export JSON con ``ensure_ascii`` (p. ej. ``correlaci\\u00f3n``) ocultaría un término
    de mecanismo al escaneo textual — vector de evasión real. Para .json/.jsonl se
    re-serializa cada documento sin escapes; si el parseo falla, se escanea el texto tal
    cual (nunca se escanea menos por un fichero corrupto).
    """
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix not in {".json", ".jsonl"}:
        return raw
    decoded: list[str] = []
    try:
        if path.suffix == ".jsonl":
            for line in raw.splitlines():
                if line.strip():
                    decoded.append(json.dumps(json.loads(line), ensure_ascii=False))
        else:
            decoded.append(json.dumps(json.loads(raw), ensure_ascii=False))
    except (json.JSONDecodeError, ValueError):
        return raw
    return raw + "\n" + "\n".join(decoded)


def load_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    spec: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    for cls in spec["heldout_classes"].values():
        cls["_patterns"] = [re.compile(t, re.IGNORECASE) for t in cls.get("mechanism_terms", [])]
        cls["_aliases"] = [re.compile(re.escape(a), re.IGNORECASE) for a in cls["aliases"]]
    return spec


def _line_of(raw: str, span_start: int) -> int:
    return raw.count("\n", 0, span_start) + 1


def scan_text(raw: str, spec: dict[str, Any], *, mechanisms: bool) -> list[dict[str, Any]]:
    """Busca alias (siempre) y términos de mecanismo (si procede) en un texto."""
    hits: list[dict[str, Any]] = []
    flat = _norm(raw)
    for name, cls in spec["heldout_classes"].items():
        for rx in cls["_aliases"]:
            for m in rx.finditer(raw):
                hits.append(
                    {
                        "heldout_class": name,
                        "kind": "alias",
                        "match": m.group(0),
                        "line": _line_of(raw, m.start()),
                    }
                )
        if mechanisms:
            for rx in cls["_patterns"]:
                for m in rx.finditer(flat):
                    hits.append(
                        {
                            "heldout_class": name,
                            "kind": "mechanism_term",
                            "match": m.group(0)[:120],
                            "line": None,  # el match es sobre texto normalizado
                        }
                    )
    return hits


# --------------------------------------------------------------------- comprobaciones
def check_scenario_suites(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """E-DET (a): held-out prohibido en secciones train/validation de las suites."""
    violations: list[dict[str, Any]] = []
    keys = set(spec["scan"]["train_section_keys"])
    heldout = {a for c in spec["heldout_classes"].values() for a in c["aliases"]}
    for path in sorted(glob.glob(str(REPO_ROOT / spec["scan"]["scenario_suites"]))):
        try:
            doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:  # pragma: no cover - suite corrupta
            violations.append({"check": "E-DET/suites", "file": path, "error": str(exc)})
            continue
        if not isinstance(doc, dict):
            continue
        for section, entries in doc.items():
            if section not in keys or not isinstance(entries, list):
                continue
            for entry in entries:
                fault = entry.get("fault") if isinstance(entry, dict) else None
                if fault in heldout:
                    violations.append(
                        {
                            "check": "E-DET/suites",
                            "file": str(Path(path).relative_to(REPO_ROOT)),
                            "section": section,
                            "scenario_id": str(entry.get("scenario_id")),
                            "heldout_class": fault,
                        }
                    )
    return violations


def check_session_dirs(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """E-DET (b): ninguna sesión materializada de train/validation con fallo held-out."""
    violations = []
    heldout = {a for c in spec["heldout_classes"].values() for a in c["aliases"]}
    directories: list[Path] = []
    for rel in spec["scan"]["session_dirs"]:
        if any(ch in rel for ch in "*?["):
            directories.extend(Path(d) for d in sorted(glob.glob(str(REPO_ROOT / rel))))
        else:
            directories.append(REPO_ROOT / rel)
    for directory in directories:
        if not directory.is_dir():
            continue
        for session in sorted(directory.glob("*.jsonl")):
            with session.open(encoding="utf-8") as fh:
                header = json.loads(fh.readline())
            fault = (header.get("scenario") or {}).get("fault")
            if fault in heldout:
                violations.append(
                    {
                        "check": "E-DET/sessions",
                        "file": str(session.relative_to(REPO_ROOT)),
                        "heldout_class": fault,
                    }
                )
    return violations


def check_training_runs(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """E-DET (c): el registro de corridas de entrenamiento no referencia held-out."""
    violations = []
    for path in sorted(glob.glob(str(REPO_ROOT / spec["scan"]["training_runs"]))):
        raw = _readable(Path(path))
        for hit in scan_text(raw, spec, mechanisms=False):
            violations.append(
                {
                    "check": "E-DET/training-runs",
                    "file": str(Path(path).relative_to(REPO_ROOT)),
                    **hit,
                }
            )
    return violations


def check_corpus(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """E-RAG: el corpus recuperable no describe clases held-out (alias NI mecanismo)."""
    violations = []
    for path in sorted(glob.glob(str(REPO_ROOT / spec["scan"]["corpus"]))):
        raw = Path(path).read_text(encoding="utf-8")
        for hit in scan_text(raw, spec, mechanisms=True):
            violations.append(
                {"check": "E-RAG/corpus", "file": str(Path(path).relative_to(REPO_ROOT)), **hit}
            )
    return violations


def check_prompts(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Prompts: las plantillas que ve el LLM no mencionan clases held-out."""
    violations = []
    for rel in spec["scan"]["prompt_sources"]:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        for hit in scan_text(raw, spec, mechanisms=True):
            violations.append({"check": "prompts", "file": rel, **hit})
    return violations


def check_memory(spec: dict[str, Any], memory_state: Path | None) -> list[dict[str, Any]]:
    """E-MEM: semillas de memoria versionadas + export opcional del estado vivo."""
    violations = []
    paths = [Path(p) for p in glob.glob(str(REPO_ROOT / spec["scan"]["memory_seeds"]))]
    if memory_state is not None:
        paths.append(memory_state)
    for path in paths:
        if not path.is_file():
            continue
        raw = _readable(path)
        for hit in scan_text(raw, spec, mechanisms=True):
            violations.append({"check": "E-MEM/memory", "file": str(path), **hit})
    return violations


def run_audit(memory_state: Path | None = None, spec_path: Path = SPEC_PATH) -> dict[str, Any]:
    spec = load_spec(spec_path)
    violations = (
        check_scenario_suites(spec)
        + check_session_dirs(spec)
        + check_training_runs(spec)
        + check_corpus(spec)
        + check_prompts(spec)
        + check_memory(spec, memory_state)
    )
    return {
        "audited_at": datetime.now(tz=UTC).isoformat(),
        "spec": str(spec_path.relative_to(REPO_ROOT))
        if spec_path.is_absolute()
        else str(spec_path),
        "heldout_classes": sorted(spec["heldout_classes"]),
        "checks_run": [
            "E-DET/suites",
            "E-DET/sessions",
            "E-DET/training-runs",
            "E-RAG/corpus",
            "prompts",
            "E-MEM/memory",
        ],
        "memory_state_provided": memory_state is not None,
        "evaluation_side_whitelist": spec.get("evaluation_side", []),
        "declared_limits": spec.get("limits", ""),
        "n_violations": len(violations),
        "clean": not violations,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--memory-state", type=Path, default=None)
    args = parser.parse_args()
    report = run_audit(args.memory_state)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    for v in report["violations"]:
        loc = f":{v['line']}" if v.get("line") else ""
        detail = v.get("kind", v.get("section", ""))
        evidence = v.get("match", v.get("scenario_id", ""))
        print(
            f"  ✗ [{v['check']}] {v['file']}{loc} → {v.get('heldout_class')} ({detail}: {evidence})"
        )
    print(
        f"exclusión triple {'VERIFICADA' if report['clean'] else 'VIOLADA'} · "
        f"{report['n_violations']} hallazgos → {args.report.name}"
    )
    return 0 if report["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
