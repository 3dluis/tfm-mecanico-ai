"""El freeze de un banco sintético detecta cualquier alteración (F21).

Un manifiesto de congelación solo sirve si FALLA cuando los datos cambian. Estos tests
comprueban las tres formas de romperlo: contenido alterado, sesión perdida y sesión
añadida sin declarar.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from freeze_benchmark import freeze, partition_manifest, verify  # noqa: E402

from mecanico_contracts import ScenarioSpec  # noqa: E402
from obd_lab.generate import write_session  # noqa: E402


@pytest.fixture(scope="module")
def sessions(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Dos sesiones normales cortas y deterministas."""
    out = tmp_path_factory.mktemp("freeze") / "train"
    for seed in (571, 572):
        write_session(
            ScenarioSpec(
                scenario_id=f"frz-{seed}",
                description="normal corto para el test de freeze",
                category="normal",
                driving_profile="urban",
                duration_s=60.0,
                seed=seed,
            ),
            out,
        )
    return out


def _manifest(sessions: Path, tmp_path: Path) -> Path:
    manifest = freeze("test-bench", {"train": sessions})
    path = tmp_path / "freeze.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return path


def test_freeze_verifica_datos_intactos(sessions: Path, tmp_path: Path) -> None:
    ok, problems = verify(_manifest(sessions, tmp_path))
    assert ok, problems


def test_freeze_es_determinista(sessions: Path) -> None:
    first = partition_manifest("train", sessions)
    second = partition_manifest("train", sessions)
    assert first["aggregate_sha256"] == second["aggregate_sha256"]


def test_freeze_detecta_contenido_alterado(sessions: Path, tmp_path: Path) -> None:
    path = _manifest(sessions, tmp_path)
    target = sorted(sessions.glob("*.jsonl"))[0]
    original = target.read_text(encoding="utf-8")
    target.write_text(original + '{"pid":"RPM","value":0.0}\n', encoding="utf-8")
    try:
        ok, problems = verify(path)
        assert not ok
        assert any("hash distinto" in p for p in problems)
    finally:
        target.write_text(original, encoding="utf-8")


def test_freeze_detecta_sesion_perdida(sessions: Path, tmp_path: Path) -> None:
    path = _manifest(sessions, tmp_path)
    target = sorted(sessions.glob("*.jsonl"))[0]
    content = target.read_bytes()
    target.unlink()
    try:
        ok, problems = verify(path)
        assert not ok
        assert any("falta" in p for p in problems)
    finally:
        target.write_bytes(content)


def test_freeze_detecta_sesion_no_declarada(sessions: Path, tmp_path: Path) -> None:
    path = _manifest(sessions, tmp_path)
    intruder = sessions / "intrusa.jsonl"
    intruder.write_bytes(sorted(sessions.glob("*.jsonl"))[0].read_bytes())
    try:
        ok, problems = verify(path)
        assert not ok
        assert any("NO declarada" in p for p in problems)
    finally:
        intruder.unlink()


def test_freeze_del_banco_v2_esta_verificado() -> None:
    """El manifiesto commiteado describe el banco realmente usado por EXP-ANOM-010."""
    manifest = json.loads(
        (REPO_ROOT / "ai-models" / "configs" / "benchmark-v2-freeze.json").read_text(
            encoding="utf-8"
        )
    )
    parts = {p["name"]: p for p in manifest["partitions"]}
    assert manifest["frozen"] is True
    assert parts["train_v11"]["n_sessions"] == 22
    assert parts["expansion_v2"]["n_sessions"] == 12
    assert parts["test_historico"]["n_sessions"] == 8
    # el train es solo normalidad; los fallos viven únicamente en el test histórico
    assert parts["train_v11"]["faults"] == []
    assert parts["expansion_v2"]["faults"] == []
    assert parts["test_historico"]["faults"]
    # la expansión usa exactamente las semillas declaradas en F20
    assert parts["expansion_v2"]["seeds"] == list(range(530, 542))
