"""Ejecución de E13b: generación del conjunto de entrenamiento del SLM.

Recorre ventanas reales de validación, ejecuta el pipeline completo sobre cada
una --atribución, recuperación, ensamblado, verificación-- y construye el ejemplo
a partir de la evidencia resultante.

Los ejemplos son, por tanto, **derivados de ejecuciones auténticas**. Ninguno se
ha escrito a mano ni generado con otro modelo.
"""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import numpy as np
import yaml

from mecanico_ia_exp.abstention.sufficiency import (
    VERIFIER_VERSION,
    EvidenceVerifier,
    SufficiencyThresholds,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.experiments.destinos import exigir_libres
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.llm.training_data import (
    TrainingExample,
    build_example,
    verify_no_manual_content_in_targets,
)
from mecanico_ia_exp.models.baseline import BaselineConfig, train_baseline
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.ingest import load_vehicle
from mecanico_ia_exp.rag.store import PgVectorStore
from mecanico_ia_exp.xai.attribution import explain_cases, select_background

DATASET = "synthetic_v2"
VEHICULO = "mazda-3-bk-2007"

#: Variantes de corpus con las que se genera cada caso. Que el conjunto contenga
#: las cuatro es lo que enseña al modelo a abstenerse: si solo viera casos con
#: evidencia, aprendería que siempre se explica.
VARIANTES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("FULL", ()),
    ("ABSENT", ("__todos__",)),
    ("PARTIAL", ("__procedimientos__",)),
)


def destinos_de(etiqueta: str = "") -> dict[str, Path]:
    """El registro de E13b, antes de escribirlo."""
    sufijo = f"_{etiqueta}" if etiqueta else ""
    return {"registro": paths.EXPERIMENTS / f"E13b_training_data{sufijo}.json"}


def run_training_data(
    dataset_id: str = DATASET,
    ventanas_por_condicion: int = 12,
    *,
    etiqueta: str = "",
) -> int:
    destinos = exigir_libres(destinos_de(etiqueta))
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    perfil = load_vehicle(VEHICULO)
    gold = yaml.safe_load((paths.CONFIGS / "goldset_mazda3_bk.yaml").read_text())
    por_fallo = {c["fault_id"]: c for c in gold["cases"] if c.get("corpus_variant") is None}

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    fondo, huella = select_background(
        entrenamiento.features,
        entrenamiento.y,
        normal_label="F00_normal",
        n=100,
        seed=configuracion.seed,
    )
    umbrales = SufficiencyThresholds()
    verificador = EvidenceVerifier(umbrales)
    store = PgVectorStore()
    embeddings = get_provider("multilingual")

    from mecanico_ia_exp.experiments.retrieval_runner import DIAGNOSTICO_A_DTC, recuperar

    predicciones = np.asarray(modelo.predict(validacion.features), dtype=np.str_)
    aciertos = predicciones == validacion.y

    ejemplos: list[TrainingExample] = []
    semilla = 0

    for fault_id, caso in sorted(por_fallo.items()):
        indices = np.flatnonzero((validacion.y == fault_id) & aciertos)[:ventanas_por_condicion]
        if indices.size == 0:
            continue
        codigos = DIAGNOSTICO_A_DTC.get(fault_id, ())

        # Se explican todas las ventanas de la condición de una vez: la
        # atribución por permutación es lo caro del proceso.
        atribuciones = explain_cases(
            modelo,
            validacion.features[indices],
            feature_names=entrenamiento.feature_names,
            background=fondo,
            background_hash=huella,
            case_ids=[
                f"{validacion.meta.iloc[i]['session_id']}@{validacion.meta.iloc[i]['t_start']:.0f}s"
                for i in indices
            ],
            model_id=f"rf_{dataset_id}",
            meta=validacion.meta.iloc[indices].reset_index(drop=True),
            seed=configuracion.seed,
        )

        for atribucion in atribuciones:
            for nombre, marca in VARIANTES:
                if marca == ("__todos__",):
                    excluidos = store.chunks_for_dtc(codigos, vehicle_id=VEHICULO)
                elif marca == ("__procedimientos__",):
                    # Se retiran los procedimientos y se dejan las tablas: el
                    # corpus menciona la condición sin documentar su diagnóstico.
                    excluidos = tuple(
                        c for c in store.chunks_for_dtc(codigos, vehicle_id=VEHICULO) if ":" in c
                    )[:40]
                else:
                    excluidos = ()

                recuperados = recuperar(
                    "diagnosis-guided",
                    store=store,
                    provider=embeddings,
                    caso=caso,
                    vehicle_id=VEHICULO,
                    engine_code=perfil.engine_code or "Z6",
                    exclude_chunks=excluidos,
                )
                bundle, _ = assemble(
                    case_id=atribucion.case_id,
                    perfil=perfil,
                    atribucion=atribucion,
                    recuperados=recuperados,
                    calibrated_confidence=atribucion.confidence,
                    accepted_applicability=umbrales.accepted_applicability,
                    expected_dtc=codigos,
                )
                veredicto = verificador.verify(bundle)
                ejemplo = build_example(bundle, veredicto, corpus_variant=nombre, seed=semilla)
                semilla += 1
                if ejemplo is not None:
                    ejemplos.append(ejemplo)

    store.dispose()

    # Equilibrado entre explicar y abstenerse.
    #
    # El pipeline produce naturalmente muchas más abstenciones que explicaciones:
    # dos condiciones tienen confianza baja, y cada caso se genera además en tres
    # variantes de corpus de las que dos retiran evidencia. El reparto crudo sale
    # en torno al 80 % de abstenciones.
    #
    # Entrenar con ese reparto enseñaría a abstenerse **por costumbre**, no por
    # evidencia. Un modelo así parecería prudente y sería inútil: es uno de los
    # desenlaces adversos que el plan enumeró de antemano --abstención trivial
    # con cobertura próxima a cero--. Se equilibra a propósito.
    rng_balance = random.Random(20260901)
    explican = [e for e in ejemplos if e.decision == "EXPLAIN"]
    abstienen = [e for e in ejemplos if e.decision == "ABSTAIN"]
    objetivo = min(len(abstienen), max(len(explican), 1))
    if len(abstienen) > objetivo:
        # Se conserva la proporción entre variantes al submuestrear: quitar todas
        # las de una variante cambiaría qué aprende el modelo a distinguir.
        por_variante: dict[str, list[TrainingExample]] = {}
        for e in abstienen:
            por_variante.setdefault(e.corpus_variant, []).append(e)
        conservadas: list[TrainingExample] = []
        cuota = max(1, objetivo // max(len(por_variante), 1))
        for grupo in por_variante.values():
            rng_balance.shuffle(grupo)
            conservadas.extend(grupo[:cuota])
        abstienen = conservadas
    print(
        f"equilibrado: {len(explican)} EXPLAIN · {len(abstienen)} ABSTAIN "
        f"(crudo: {sum(1 for e in ejemplos if e.decision == 'ABSTAIN')} abstenciones)"
    )
    ejemplos = explican + abstienen
    rng_balance.shuffle(ejemplos)

    # La comprobación que sostiene el experimento: ninguna salida esperada puede
    # contener texto del manual.
    fugas = verify_no_manual_content_in_targets(ejemplos)
    print(f"ejemplos generados: {len(ejemplos)}")
    print(f"comprobación de fuga de contenido: {len(fugas)} problemas")
    if fugas:
        for f in fugas[:5]:
            print(f"  {f}")
        print("\nABORTADO: hay texto del manual en las salidas esperadas.")
        return 1

    reparto: dict[str, int] = {}
    for e in ejemplos:
        clave = f"{e.corpus_variant}/{e.decision}"
        reparto[clave] = reparto.get(clave, 0) + 1
    print("\nreparto:")
    for clave, n in sorted(reparto.items()):
        print(f"  {clave:<20} {n}")

    # Reparto en entrenamiento y validación del ajuste, POR CASO: dos variantes
    # del mismo caso comparten observaciones, y separarlas al azar filtraría
    # información entre particiones igual que ocurriría con las ventanas.
    # Partición por **ventana de origen**, que es la unidad independiente. Las
    # variantes de corpus de una misma ventana comparten `case_id` y caen juntas:
    # repartirlas entre particiones sería fuga, aunque los prompts difieran.
    casos = sorted({e.case_id for e in ejemplos})
    corte = int(len(casos) * 0.85)
    casos_train = set(casos[:corte])

    destino = paths.ensure(paths.DATA_PROCESSED / "slm_finetune")
    for nombre, seleccion in (
        ("train", [e for e in ejemplos if e.case_id in casos_train]),
        ("valid", [e for e in ejemplos if e.case_id not in casos_train]),
    ):
        ruta = destino / f"{nombre}.jsonl"
        ruta.write_text("\n".join(e.to_jsonl() for e in seleccion) + "\n", encoding="utf-8")
        print(f"  {ruta.name:<12} {len(seleccion)} ejemplos")

    huellas = {
        n: hashlib.sha256((destino / f"{n}.jsonl").read_bytes()).hexdigest()[:16]
        for n in ("train", "valid")
    }
    identidad = embeddings.identity
    escribir(
        destinos["registro"],
        {
            "experiment_id": "E13b_training_data",
            "n_examples": len(ejemplos),
            "n_cases": len(casos),
            "split_by": "source_window",
            "split_unit_note": (
                "las variantes de corpus de una misma ventana comparten case_id y "
                "caen en la misma partición"
            ),
            "split_seed": 20260901,
            "distribution": reparto,
            "leakage_check": "sin texto del manual en las salidas esperadas",
            # Linaje: sin esto no se puede decidir sobre el adaptador.
            "source_verifier_version": VERIFIER_VERSION,
            "source_case_set": sorted({e.case_id for e in ejemplos}),
            "source_embedding_space_id": (
                f"{identidad.provider}/{identidad.model}/"
                f"d{identidad.dimension}/v{identidad.version}"
            ),
            "dataset_hash": huellas,
        },
        dataset_id=dataset_id,
        dataset_type="synthetic",
        embedding_model=identidad.model,
        seed=20260901,
    )
    print("\nregistro experiments/E13b_training_data.json")
    return 0
