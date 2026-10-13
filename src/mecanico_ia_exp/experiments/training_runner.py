"""Ejecución de E13b: generación del conjunto de entrenamiento del SLM.

Recorre ventanas reales de validación, ejecuta el pipeline completo sobre cada
una --atribución, recuperación, ensamblado, verificación-- y construye el ejemplo
a partir de la evidencia resultante.

Los ejemplos son, por tanto, **derivados de ejecuciones auténticas**. Ninguno se
ha escrito a mano ni generado con otro modelo.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Literal

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
    """Los tres artefactos de E13b, antes de escribir el primero.

    Los dos `.jsonl` van aquí y no solo el registro: son **los ejemplos con que
    se ajustó el adaptador**. Proteger el registro y dejar los ejemplos en una
    ruta fija los habría sobrescrito, y el registro anterior habría quedado
    apuntando a unos ficheros cuyas huellas ya no coinciden con las que declara
    --que es peor que perderlos, porque no se nota--.
    """
    sufijo = f"_{etiqueta}" if etiqueta else ""
    ejemplos = paths.DATA_PROCESSED / f"slm_finetune{sufijo}"
    return {
        "registro": paths.EXPERIMENTS / f"E13b_training_data{sufijo}.json",
        "ejemplos_train": ejemplos / "train.jsonl",
        "ejemplos_valid": ejemplos / "valid.jsonl",
    }


class ContaminacionError(RuntimeError):
    """Los ejemplos de ajuste tocan una partición sobre la que se va a medir."""


def exigir_particion_de_ajuste_limpia(ventanas: list[str], dataset_id: str) -> dict[str, int]:
    """Falla si alguna ventana de los ejemplos cae en validación o en prueba.

    **Esta comprobación nació de un defecto real.** Los ejemplos de
    `models/slm_lora_v2` se generaron desde validación, y E13 y E15 midieron la
    calidad del redactor sobre validación: tres de las cinco ventanas de
    evaluación eran **exactamente las mismas** con que se había ajustado.
    Documentado en `docs/methodology/auditoria-contaminacion-adaptador.md`.

    Se comprueba por **sesión** además de por ventana: dos ventanas de la misma
    sesión comparten la mitad de sus muestras, de modo que la disyunción por
    ventana no bastaría.

    **Y se comprueba leyendo el reparto, no las particiones.**
    `synthetic_v2_preprocess.json` registra a qué partición va cada sesión, que
    es toda la información que hace falta. Cargar la partición de prueba para
    esto habría sido una apertura del conjunto de prueba —y una apertura
    innecesaria es peor que inútil: gasta la única cosa que no se repone—.
    """
    manifiesto = paths.DATA_PROCESSED / f"{dataset_id}_preprocess.json"
    if not manifiesto.is_file():
        msg = (
            f"No está {manifiesto.name} y sin él no se puede comprobar que los ejemplos no "
            "tocan validación ni prueba. Reconstrúyalo con scripts/reconstruir_datos.sh."
        )
        raise ContaminacionError(msg)
    reparto: dict[str, str] = json.loads(manifiesto.read_text("utf-8"))["split_assignment"]

    sesiones = {v.split("@")[0] for v in ventanas}
    reservadas = {
        particion: {s for s, p in reparto.items() if p == particion}
        for particion in ("validation", "test")
    }
    problemas = {
        particion: sorted(sesiones & reservado) for particion, reservado in reservadas.items()
    }
    if any(problemas.values()):
        detalle = "\n".join(
            f"  {particion}: {len(s)} sesión(es) {s[:4]}" for particion, s in problemas.items() if s
        )
        msg = (
            "Los ejemplos de ajuste tocan particiones sobre las que se mide:\n"
            f"{detalle}\n"
            "Es la contaminación que P2 corrige. Genere los ejemplos desde la partición de "
            "entrenamiento."
        )
        raise ContaminacionError(msg)
    return {p: len(s) for p, s in reservadas.items()}


def run_training_data(
    dataset_id: str = DATASET,
    ventanas_por_condicion: int = 12,
    *,
    etiqueta: str = "",
    particion_de_ejemplos: Literal["train", "validation"] = "validation",
) -> int:
    """Construye los ejemplos con que se ajusta el redactor.

    ``particion_de_ejemplos`` decide de dónde salen. El valor por omisión,
    ``"validation"``, es el que produjo `models/slm_lora_v2` y **se conserva solo
    para poder reproducir aquel conjunto**: contamina, porque E13 y E15 miden
    sobre validación. Para un adaptador nuevo hay que pasar ``"train"``.
    """
    destinos = exigir_libres(destinos_de(etiqueta))
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    if particion_de_ejemplos == "train":
        # Los ejemplos salen de la misma partición con que se ajustó el bosque.
        # No es un problema para el redactor: su trabajo es escribir lo que se le
        # entrega, no diagnosticar. Y es la única partición disjunta por
        # construcción de las dos sobre las que se le mide.
        origen = entrenamiento
    else:
        origen = load_partition("validation", dataset_id=dataset_id)
    validacion = origen
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
        candidatas = np.flatnonzero((validacion.y == fault_id) & aciertos)
        if particion_de_ejemplos == "validation":
            # Selección HISTÓRICA, intacta: las primeras ventanas. Este modo
            # existe para reproducir el conjunto de `slm_lora_v2`, de modo que
            # mejorarlo lo rompería.
            indices = candidatas[:ventanas_por_condicion]
        else:
            # Las ventanas se reparten **entre sesiones**, no se toman las
            # primeras: tomar las primeras concentraba los ejemplos de cada
            # condición en una o dos sesiones, lo que produce ejemplos casi
            # duplicados --ventanas consecutivas comparten la mitad de sus
            # muestras-- y deja el reparto interno sin sesiones que separar.
            por_sesion: dict[str, list[int]] = {}
            for i in candidatas:
                por_sesion.setdefault(str(validacion.meta.iloc[i]["session_id"]), []).append(int(i))
            ordenados: list[int] = []
            for k in range(max((len(v) for v in por_sesion.values()), default=0)):
                for sesion in sorted(por_sesion):
                    if k < len(por_sesion[sesion]):
                        ordenados.append(por_sesion[sesion][k])
            indices = np.array(ordenados[:ventanas_por_condicion], dtype=int)
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

    # Reparto en entrenamiento y validación del ajuste, **POR SESIÓN**.
    #
    # Repartir por ventana no basta, y es un defecto que estuvo aquí: dos
    # ventanas consecutivas de la misma sesión comparten la mitad de sus
    # muestras, de modo que `F05_misfire__idle__02@240s` en entrenamiento y
    # `@300s` en validación dejaban que la pérdida de validación del ajuste
    # midiera sobre datos que el adaptador acababa de ver. Es la misma fuga que
    # el reparto del conjunto principal evita desde E5, y que aquí no se había
    # propagado.
    #
    # Las variantes de corpus de una misma ventana comparten `case_id` y la
    # ventana comparte sesión, así que agrupar por sesión las mantiene juntas.
    casos = sorted({e.case_id for e in ejemplos})
    limpio = particion_de_ejemplos == "train"

    if not limpio:
        # Reparto HISTÓRICO, por ventana. Se conserva por el mismo motivo que la
        # selección: este modo existe para reproducir el conjunto de
        # `slm_lora_v2`, y mejorarlo lo rompería.
        casos_train = set(casos[: int(len(casos) * 0.85)])
    else:
        # Por SESIÓN y **estratificado por condición**. Por ventana no basta: dos
        # ventanas consecutivas comparten la mitad de sus muestras, de modo que
        # la pérdida de validación del ajuste mediría sobre datos vistos. Y
        # cortar por orden dejaba la validación interna con una sola condición,
        # porque las últimas por orden alfabético eran las de encendido.
        por_condicion: dict[str, list[str]] = {}
        for sesion in sorted({e.case_id.split("@")[0] for e in ejemplos}):
            por_condicion.setdefault(sesion.split("__")[0], []).append(sesion)
        sesiones_valid = {lista[-1] for lista in por_condicion.values() if len(lista) > 1}
        casos_train = {e.case_id for e in ejemplos if e.case_id.split("@")[0] not in sesiones_valid}

    paths.ensure(destinos["ejemplos_train"].parent)
    # La comprobación de contaminación va **antes** de escribir un solo ejemplo.
    # Descubrir después que los ejemplos tocan la partición sobre la que se mide
    # ya sería tarde: el fichero existiría y alguien podría ajustar con él.
    if particion_de_ejemplos == "train":
        reservadas = exigir_particion_de_ajuste_limpia(
            sorted({e.case_id for e in ejemplos}), dataset_id
        )
        print(
            f"\nSin contaminación: ninguna de las {len(ejemplos)} muestras de ajuste toca "
            f"validación ({reservadas['validation']} sesiones) ni prueba "
            f"({reservadas['test']})."
        )
    else:
        print(
            "\nAVISO: los ejemplos salen de VALIDACIÓN, que es donde E13 y E15 miden al "
            "redactor. Es la contaminación documentada en "
            "docs/methodology/auditoria-contaminacion-adaptador.md. Se conserva para poder "
            "reproducir el conjunto de slm_lora_v2; para un adaptador nuevo, use "
            "--particion-ejemplos train."
        )

    # Si algo falla después de escribir los `.jsonl`, se borran. Un destino a
    # medias bloquea el reintento, porque la negativa a sobrescribir no distingue
    # «ya está hecho» de «quedó a medias», y eso ya pasó una vez.
    escritos: list[Path] = []
    try:
        for nombre, seleccion in (
            ("train", [e for e in ejemplos if e.case_id in casos_train]),
            ("valid", [e for e in ejemplos if e.case_id not in casos_train]),
        ):
            ruta = destinos[f"ejemplos_{nombre}"]
            # Se anota ANTES de escribir: si `write_text` falla a mitad, el
            # fichero existe a medias y hay que borrarlo igual. Anotarlo después
            # dejaba fuera justo el que había quedado corrupto.
            escritos.append(ruta)
            ruta.write_text("\n".join(e.to_jsonl() for e in seleccion) + "\n", encoding="utf-8")
            print(f"  {ruta.relative_to(paths.ROOT)}  {len(seleccion)} ejemplos")
    except Exception:
        for ruta in escritos:
            ruta.unlink(missing_ok=True)
        raise

    def _limpiar_todo() -> None:
        """Borra lo que esta ejecución escribió, para que el reintento sea posible.

        Incluye el registro: si falla al escribirlo, los dos `.jsonl` quedarían
        en disco sin él y la negativa a sobrescribir impediría reintentar con la
        misma etiqueta. No es hipotético, pasó al introducir el reparto por
        sesión.
        """
        for ruta in escritos:
            ruta.unlink(missing_ok=True)
        destinos["registro"].unlink(missing_ok=True)

    huellas = {
        n: hashlib.sha256(destinos[f"ejemplos_{n}"].read_bytes()).hexdigest()[:16]
        for n in ("train", "valid")
    }
    try:
        identidad = embeddings.identity
        escribir(
            destinos["registro"],
            {
                "experiment_id": "E13b_training_data",
                "n_examples": len(ejemplos),
                "n_cases": len(casos),
                "split_by": "source_session" if limpio else "source_window",
                "window_selection": "across_sessions" if limpio else "first_n",
                "split_unit_note": (
                    "por SESIÓN y estratificado por condición: dos ventanas consecutivas "
                    "comparten la mitad de sus muestras, de modo que repartir por ventana dejaba "
                    "que la pérdida de validación del ajuste midiera sobre datos vistos; y cortar "
                    "por orden dejaba la validación interna con una sola condición"
                    if limpio
                    else "por VENTANA, el reparto histórico: se conserva para poder reproducir el "
                    "conjunto de slm_lora_v2, y deja ventanas de la misma sesión a los dos lados"
                ),
                "split_seed": 20260901,
                "distribution": reparto,
                "leakage_check": "sin texto del manual en las salidas esperadas",
                "examples_partition": particion_de_ejemplos,
                "contamination_check": (
                    "ninguna sesión de los ejemplos aparece en validación ni en prueba; "
                    "comprobado antes de escribir"
                    if particion_de_ejemplos == "train"
                    else "NO SE COMPRUEBA: los ejemplos salen de validación, que es donde E13 y "
                    "E15 miden al redactor. Es la contaminación que P2 corrige "
                    "(docs/methodology/auditoria-contaminacion-adaptador.md)"
                ),
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
    except Exception:
        _limpiar_todo()
        raise
    print("\nregistro experiments/E13b_training_data.json")
    return 0
