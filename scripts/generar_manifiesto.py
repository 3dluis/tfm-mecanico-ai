"""Escribe `MANIFEST.json`: el inventario del paquete, con sus huellas.

**Para qué sirve.** Para que quien reciba el ZIP pueda comprobar que lo que
tiene es lo que se entregó, y para que lo que **no** viaja esté dicho con su
motivo en lugar de faltar en silencio. Un paquete que calla una exclusión obliga
a descubrirla al intentar usarla.

Se genera, no se escribe a mano: una lista de huellas mantenida a mano deja de
coincidir con los ficheros en cuanto algo cambia, y entonces estorba.

    uv run python scripts/generar_manifiesto.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

#: Qué se censa. Patrones y no una lista, para que no se quede corto.
#: En esta copia **no hay** `memoria/`: el documento académico se entrega por su
#: propio cauce y sus versiones viven en el historial. Los dos patrones que lo
#: censaban se retiran para que el inventario no busque lo que no está.
PATRONES: tuple[str, ...] = (
    "notebooks/*.ipynb",
    "artifacts/tables/*.csv",
    "artifacts/metrics/*.json",
    "artifacts/figures/memoria/*.png",
    "artifacts/figures/*.png",
    "artifacts/contrafactual/*",
    "experiments/*.json",
    "configs/*.json",
    "data/samples/*",
    "data/processed/synthetic_v2_*",
    "data/raw/synthetic/*.parquet",
    "pyproject.toml",
    "uv.lock",
)


def _huella(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as flujo:
        for bloque in iter(lambda: flujo.read(1 << 20), b""):
            digest.update(bloque)
    return digest.hexdigest()


def _git(*args: str) -> str:
    try:
        salida = subprocess.run(
            ["git", "-C", str(RAIZ), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return salida.stdout.strip()


def manifiesto() -> dict[str, object]:
    huellas: dict[str, str] = {}
    for patron in PATRONES:
        for fichero in sorted(RAIZ.glob(patron)):
            if fichero.is_file():
                huellas[str(fichero.relative_to(RAIZ))] = _huella(fichero)

    fechas = _git("log", "--reverse", "--format=%ad", "--date=short").splitlines()
    return {
        "que_es": (
            "Paquete academico autonomo del TFM: memoria, notebooks ejecutables, codigo, "
            "artefactos experimentales e historial Git completo."
        ),
        "estado": "BORRADOR PARA REVISION DEL TUTOR",
        "generado_el": datetime.now(UTC).isoformat(timespec="seconds"),
        "git": {
            "commit": _git("rev-parse", "HEAD"),
            "rama": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "commits": _git("rev-list", "--count", "HEAD"),
            "primer_commit": _git("rev-list", "--max-parents=0", "HEAD"),
            "primera_fecha": fechas[0] if fechas else "",
            "ultima_fecha": _git("log", "-1", "--format=%ad", "--date=short"),
            "ramas": len(_git("branch", "--format=%(refname:short)").splitlines()),
            "sha_identicos_al_repositorio_de_trabajo": (
                "si: el repositorio se construyo por clonacion, sin reescritura de historial"
            ),
        },
        "modalidades": {
            "DEMO": {
                "que_permite": [
                    "explorar las senales OBD-II y sus series temporales",
                    "regenerar las figuras del documento desde los registros congelados",
                    "consultar metricas, matrices de confusion y atribuciones",
                    "analizar la evaluacion final E19 y sus abstenciones",
                    "leer los resultados negativos y las limitaciones",
                ],
                "necesita": "CPU, Python 3.11 o superior, e internet UNA vez para instalar",
                "no_necesita": [
                    "GPU",
                    "PostgreSQL ni pgvector",
                    "servicios externos ni credenciales",
                    "internet durante la ejecucion",
                ],
            },
            "FULL": {
                "que_permite": "reejecutar las fases que dependen de recursos no redistribuibles",
                "necesita": [
                    "el manual de taller del fabricante, que no se redistribuye",
                    "los adaptadores LoRA (28 MB cada uno), que no viajan en el paquete",
                    "PostgreSQL con pgvector para el indice documental",
                    "GPU para el ajuste del redactor",
                ],
                "advertencia": (
                    "FULL NO es autonomo: exige recursos externos que este paquete no incluye."
                ),
            },
        },
        "datos": {
            "synthetic_v2": {
                "estado": "canonico y RECONSTRUIBLE bit a bit",
                "sesiones": 72,
                "de_el_salen": "E5, E6, E7, E9, E15, E18 y la evaluacion final E19",
                "incluido": "si, crudo y procesado",
            },
            "synthetic_v1": {
                "estado": "NO reconstruible: es anterior a la calibracion del generador",
                "sesiones": 36,
                "de_el_salen": "E4, el analisis exploratorio",
                "incluido": "si, como artefacto historico",
            },
            "synthetic_v3": {
                "estado": "NO reconstruible: anterior a la calibracion del generador",
                "sesiones": 216,
                "de_el_salen": "la comparacion de volumen de E6 y E7",
                "incluido": (
                    "NO: son 15 MB y ningun analisis del paquete lee sus senales crudas. "
                    "Viaja su metadata. Su ausencia es permanente, porque no se puede regenerar."
                ),
            },
            "contrafactual_T2": {
                "estado": "artefacto DERIVADO para analisis visual",
                "incluido": "si, en artifacts/contrafactual/, separado de los conjuntos congelados",
                "advertencia": (
                    "no entra en entrenamiento, validacion ni prueba, y no modifica ninguna metrica"
                ),
            },
        },
        "modelos": {
            "random_forest_E6": "no se distribuye el binario; su registro fija metricas y semilla",
            "bigru_E7": "no se distribuye el binario; viajan los estandarizadores y el registro",
            "adaptadores_lora": (
                "NO incluidos: 28 MB cada uno y derivados de un modelo base con licencia propia. "
                "Viajan adapter_config.json y finetune_config.json, que hacen auditable el ajuste."
            ),
            "embeddings": (
                "NO incluidos: el indice vectorial se construye del manual del fabricante, "
                "que no se redistribuye. El manifiesto del corpus si viaja."
            ),
        },
        "exclusiones_declaradas": [
            "manual de taller del fabricante: licencia que no permite redistribucion",
            "indice documental y embeddings: se construyen del manual",
            "adaptadores LoRA: tamano y licencia del modelo base",
            "synthetic_v3 crudo: 15 MB que ningun analisis del paquete necesita",
            "modelos entrenados: se regeneran desde los registros y las semillas",
        ],
        "huellas_sha256": huellas,
        "ficheros_censados": len(huellas),
    }


def main() -> int:
    datos = manifiesto()
    destino = RAIZ / "MANIFEST.json"
    destino.write_text(json.dumps(datos, indent=2, ensure_ascii=True) + "\n", "utf-8")
    print(f"{destino.name}: {datos['ficheros_censados']} ficheros censados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
