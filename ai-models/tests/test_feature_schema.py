"""Tests del contrato de features versionado (F13, Protocolo ML v1)."""

from ai_models.features.schema import (
    FS1,
    FS2_DRAFT,
    SCHEMAS,
    FeatureKind,
    validate_fs1_against_contract,
)
from mecanico_contracts.features import CANONICAL_PIDS, FEATURE_NAMES


def test_fs1_coincide_con_contrato_compartido() -> None:
    """La descripción fs1 debe reflejar EXACTAMENTE FEATURE_NAMES (nombre y orden)."""
    validate_fs1_against_contract()
    assert FS1.names == list(FEATURE_NAMES)
    assert len(FS1.specs) == 42


def test_fs1_specs_completas_y_sin_duplicados() -> None:
    assert len(set(FS1.names)) == len(FS1.names)
    for spec in FS1.specs:
        assert spec.description
        assert spec.windowed
        for pid in spec.source_pids:
            assert pid in CANONICAL_PIDS
    derived = [s for s in FS1.specs if s.kind is FeatureKind.DERIVED]
    assert len(derived) == 6  # 5 correlaciones + total_trim_mean


def test_fs2_es_borrador_y_no_entrenable() -> None:
    """fs2 está declarado pero NO implementado: prohibido usarlo como esquema vigente."""
    assert FS2_DRAFT.status == "draft"
    assert FS1.status == "vigente"
    # sin colisiones de nombre con fs1
    assert not set(FS2_DRAFT.names) & set(FS1.names)
    # cada candidata justifica su origen en la descripción (no exploración indiscriminada)
    assert all(s.description for s in FS2_DRAFT.specs)


def test_registro_de_esquemas() -> None:
    assert SCHEMAS["fs1"] is FS1
    assert SCHEMAS["fs2-draft"] is FS2_DRAFT
