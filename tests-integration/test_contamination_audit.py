"""La auditoría de exclusión triple detecta contaminación real e inyectada (B0.5, F24).

Un auditor de contaminación solo sirve si FALLA cuando el conocimiento held-out se cuela
por alguna vía. Se comprueban las vías principales con violaciones inyectadas en copias, y
se fija además el hallazgo real vigente: el corpus v1 describe los mecanismos de las tres
clases held-out (violación de E-RAG que bloquea los experimentos de los pasos 5-8 hasta el
rediseño del corpus).
"""

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from contamination_audit import SPEC_PATH, load_spec, run_audit, scan_text  # noqa: E402


def test_el_estado_actual_del_repo_esta_medido() -> None:
    """Fija el estado vigente: E-DET/E-MEM/prompts limpios; E-RAG violada por corpus_v1."""
    report = run_audit()
    checks = {v["check"] for v in report["violations"]}
    assert checks == {"E-RAG/corpus"}, report["violations"]
    classes = {v["heldout_class"] for v in report["violations"]}
    assert classes == {"corr_break_rpm_maf", "load_coolant_decouple", "joint_slow_drift"}
    assert report["clean"] is False


def test_detecta_alias_en_texto() -> None:
    spec = load_spec()
    hits = scan_text("entrenado con joint_slow_drift a proposito", spec, mechanisms=False)
    assert hits and hits[0]["heldout_class"] == "joint_slow_drift"
    assert hits[0]["kind"] == "alias"


def test_detecta_mecanismo_cruzando_saltos_de_linea() -> None:
    spec = load_spec()
    text = "se observa una pérdida de correlación\nentre RPM y MAF en el sensor"
    hits = scan_text(text, spec, mechanisms=True)
    assert any(h["kind"] == "mechanism_term" for h in hits)


def test_no_da_falsos_positivos_en_texto_neutro() -> None:
    spec = load_spec()
    text = "el LTFT cruza fronteras de cuantización en sesiones largas de autovía"
    assert scan_text(text, spec, mechanisms=True) == []


def test_detecta_heldout_en_suite_de_train(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Inyección E-DET: una suite con held-out en la sección train debe ser violación."""
    import contamination_audit as ca

    bad_suite = {
        "train": [{"scenario_id": "x", "category": "known_fault", "fault": "load_coolant_decouple"}]
    }
    suites = tmp_path / "scenarios"
    suites.mkdir()
    (suites / "bad.yaml").write_text(yaml.safe_dump(bad_suite), encoding="utf-8")
    spec = load_spec()
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    spec["scan"]["scenario_suites"] = "scenarios/*.yaml"
    violations = ca.check_scenario_suites(spec)
    assert violations and violations[0]["heldout_class"] == "load_coolant_decouple"
    assert violations[0]["section"] == "train"


def test_detecta_sesion_de_train_contaminada(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    import contamination_audit as ca

    train = tmp_path / "data" / "sessions" / "train"
    train.mkdir(parents=True)
    header = {"session_id": "bad", "scenario": {"fault": "corr_break_rpm_maf"}}
    (train / "bad.jsonl").write_text(json.dumps(header) + "\n", encoding="utf-8")
    spec = load_spec()
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    spec["scan"]["session_dirs"] = ["data/sessions/train"]
    violations = ca.check_session_dirs(spec)
    assert violations and violations[0]["check"] == "E-DET/sessions"


def test_detecta_memoria_contaminada_via_export(tmp_path: Path) -> None:
    """CN5 instrumental: un export de memoria con una hipótesis held-out debe detectarse."""
    export = tmp_path / "memoria.jsonl"
    export.write_text(
        json.dumps({"case": 1, "hypothesis": "ruptura de correlación entre rpm y maf"}) + "\n",
        encoding="utf-8",
    )
    report = run_audit(memory_state=export)
    mem = [v for v in report["violations"] if v["check"] == "E-MEM/memory"]
    assert mem and mem[0]["heldout_class"] == "corr_break_rpm_maf"


def test_la_especificacion_declara_las_tres_clases_congeladas() -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    assert set(spec["heldout_classes"]) == {
        "corr_break_rpm_maf",
        "load_coolant_decouple",
        "joint_slow_drift",
    }
    assert spec["limits"]  # las fronteras de lo auditable están declaradas
