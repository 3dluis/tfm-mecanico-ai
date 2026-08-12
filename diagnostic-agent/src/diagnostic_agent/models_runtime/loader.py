"""Carga segura de paquetes de modelo en el edge (ADR-0009).

Un paquete es un directorio ``model-<nombre>-<semver>/`` con ``manifest.json``
(contrato ``ModelManifest``) + el artefacto. La carga valida: hash sha256, formato,
y compatibilidad de features con la definición canónica local.
"""

import hashlib
import json
from pathlib import Path

from mecanico_contracts import ModelManifest
from mecanico_contracts.features import FEATURE_NAMES


class ModelPackageError(RuntimeError):
    """El paquete de modelo es inválido o incompatible con este runtime."""


def load_manifest(package_dir: Path) -> ModelManifest:
    """Lee y valida el manifiesto de un paquete."""
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.exists():
        msg = f"paquete sin manifest.json: {package_dir}"
        raise ModelPackageError(msg)
    return ModelManifest.model_validate(json.loads(manifest_path.read_text(encoding="utf-8")))


def verify_package(package_dir: Path) -> ModelManifest:
    """Valida hash y compatibilidad; devuelve el manifiesto listo para cargar."""
    manifest = load_manifest(package_dir)
    artifact = package_dir / manifest.artifact_filename
    if not artifact.exists():
        msg = f"artefacto ausente: {artifact}"
        raise ModelPackageError(msg)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != manifest.artifact_sha256:
        msg = (
            f"sha256 no coincide para {artifact.name}: "
            f"manifiesto={manifest.artifact_sha256[:12]}… real={digest[:12]}…"
        )
        raise ModelPackageError(msg)
    if manifest.expected_features != FEATURE_NAMES:
        msg = (
            "features incompatibles con el runtime local: el manifiesto declara "
            f"{len(manifest.expected_features)} y el runtime produce {len(FEATURE_NAMES)} "
            "(o el orden difiere). Se conserva el modelo anterior (rollback, ADR-0009)."
        )
        raise ModelPackageError(msg)
    if manifest.artifact_format != "onnx":
        msg = f"formato no soportado por este runtime: {manifest.artifact_format}"
        raise ModelPackageError(msg)
    return manifest
