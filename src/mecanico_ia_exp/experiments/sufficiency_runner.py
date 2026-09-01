"""Ejecución de E15: verificación de suficiencia sobre los casos anotados.

Sin modelo de lenguaje. El verificador es determinista por diseño, y esta fase
comprueba precisamente eso: que la decisión de explicar o abstenerse se puede
tomar y auditar sin que intervenga un generador de texto.

Los umbrales se calibran **solo con validación**. El test sigue cerrado.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
import yaml

from mecanico_ia_exp.abstention.sufficiency import (
    EvidenceVerifier,
    SufficiencyThresholds,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import expected_calibration_error
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.models.baseline import BaselineConfig, train_baseline
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.ingest import load_vehicle
from mecanico_ia_exp.rag.store import PgVectorStore
from mecanico_ia_exp.xai.attribution import explain_cases, select_background

DATASET = "synthetic_v2"
VEHICULO = "mazda-3-bk-2007"
GOLDSET = paths.CONFIGS / "goldset_mazda3_bk.yaml"


def _calibrar(entrenamiento: Any, validacion: Any, configuracion: BaselineConfig) -> Any:
    """Calibra la confianza del modelo con validación cruzada sobre entrenamiento.

    E6 midió que el bosque está infraconfiado: confianza media 0,738 frente a
    0,878 de acierto. Un umbral sobre esa confianza cruda haría que el criterio
    se abstuviera de más, y parecería prudencia cuando sería mala medición.

    La calibración se ajusta **sobre entrenamiento**, con validación cruzada
    interna, para no gastar validación en dos cosas: aquí se calibra y después se
    fijan los umbrales.
    """
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import RandomForestClassifier

    base = RandomForestClassifier(
        n_estimators=configuracion.n_estimators,
        min_samples_leaf=configuracion.min_samples_leaf,
        class_weight=configuracion.class_weight,
        random_state=configuracion.seed,
        n_jobs=configuracion.n_jobs,
    )
    calibrado = CalibratedClassifierCV(base, method="isotonic", cv=5)
    calibrado.fit(entrenamiento.features, entrenamiento.y)
    return calibrado


def run_sufficiency(dataset_id: str = DATASET) -> int:
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    perfil = load_vehicle(VEHICULO)
    gold = yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))
    casos_gold = list(gold["cases"])

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    calibrado = _calibrar(entrenamiento, validacion, configuracion)

    # Efecto de la calibración, medido sobre validación.
    for nombre, m in (("sin calibrar", modelo), ("calibrado", calibrado)):
        prob = np.asarray(m.predict_proba(validacion.features), dtype=np.float64)
        pred = np.asarray(m.predict(validacion.features), dtype=np.str_)
        conf = prob.max(axis=1)
        aciertos = (pred == validacion.y).astype(bool)
        print(
            f"{nombre:<14} ECE {expected_calibration_error(conf, aciertos):.3f} · "
            f"confianza media {conf.mean():.3f} · acierto {aciertos.mean():.3f} · "
            f"sesgo {conf.mean() - aciertos.mean():+.3f}"
        )

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
    provider = get_provider("multilingual")

    from mecanico_ia_exp.experiments.retrieval_runner import recuperar

    predicciones = np.asarray(modelo.predict(validacion.features), dtype=np.str_)
    aciertos = predicciones == validacion.y

    print(f"\numbrales: {json.dumps(umbrales.to_dict(), ensure_ascii=False)}\n")
    filas: list[dict[str, Any]] = []
    veredictos: list[Any] = []

    for caso in casos_gold:
        fault_id = str(caso["fault_id"])
        indices = np.flatnonzero((validacion.y == fault_id) & aciertos)
        if indices.size == 0:
            print(f"{caso['case_id']}: sin casos correctamente clasificados")
            continue
        i = int(indices[0])
        case_id = (
            f"{validacion.meta.iloc[i]['session_id']}@{validacion.meta.iloc[i]['t_start']:.0f}s"
        )

        atribucion = explain_cases(
            modelo,
            validacion.features[i : i + 1],
            feature_names=entrenamiento.feature_names,
            background=fondo,
            background_hash=huella,
            case_ids=[case_id],
            model_id=f"rf_{dataset_id}",
            meta=validacion.meta.iloc[[i]].reset_index(drop=True),
            seed=configuracion.seed,
        )[0]

        prob_cal = np.asarray(calibrado.predict_proba(validacion.features[i : i + 1]))[0]
        clases_cal = list(calibrado.classes_)
        confianza_calibrada = float(prob_cal[clases_cal.index(atribucion.predicted_class)])

        # La condición ABSENT retira del índice la evidencia que sostenía la
        # explicación. Todo lo demás --datos, modelo, atribución, consulta-- es
        # idéntico al caso con evidencia: si el agente decidiera igual, no
        # estaría usando la evidencia.
        excluidos = store.chunks_for_dtc(
            tuple(caso.get("exclude_dtc") or ()), vehicle_id=VEHICULO
        ) + store.chunks_for_files(tuple(caso.get("exclude_files") or ()), vehicle_id=VEHICULO)
        recuperados = recuperar(
            "diagnosis-guided",
            store=store,
            provider=provider,
            caso=caso,
            vehicle_id=VEHICULO,
            engine_code=perfil.engine_code or "Z6",
            exclude_chunks=excluidos,
        )

        # Los DTC que documentan esta condición: si el fragmento citado no
        # porta ninguno, no está hablando de este fallo.
        from mecanico_ia_exp.experiments.retrieval_runner import DIAGNOSTICO_A_DTC

        bundle, comprobaciones = assemble(
            case_id=case_id,
            perfil=perfil,
            atribucion=atribucion,
            recuperados=recuperados,
            calibrated_confidence=confianza_calibrada,
            accepted_applicability=umbrales.accepted_applicability,
            expected_dtc=DIAGNOSTICO_A_DTC.get(fault_id, ()),
        )
        veredicto = verificador.verify(bundle)
        veredictos.append((caso, bundle, veredicto, comprobaciones))

        esperado = str(caso["expected_action"])
        correcto = veredicto.decision.value == esperado
        filas.append(
            {
                "case_id_gold": caso["case_id"],
                "fault_id": fault_id,
                "case_id": case_id,
                "corpus_variant": caso.get("corpus_variant", "FULL"),
                "n_excluded_chunks": len(excluidos),
                "expected_action": esperado,
                "decision": veredicto.decision.value,
                "correct": correcto,
                "sufficiency": veredicto.sufficiency.value,
                "reasons": "; ".join(r.value for r in veredicto.reasons),
                **{k: v for k, v in veredicto.signals.items() if k != "contradictions"},
            }
        )

    print(
        f"{'caso':<38}{'esperado':>10}{'decidido':>10}{'':>3}"
        f"{'conf':>7}{'docs':>6}{'cob.':>7}  motivos"
    )
    print("-" * 118)
    for caso, _bundle, v, _comp in veredictos:
        esperado = str(caso["expected_action"])
        marca = "OK" if v.decision.value == esperado else "!!"
        s = v.signals
        motivos = ", ".join(r.value.replace("_", " ").lower() for r in v.reasons)
        print(
            f"{caso['case_id']!s:<38}{esperado:>10}{v.decision.value:>10}{marca:>3}"
            f"{s['confidence']:>7.3f}{s['n_documents_applicable']:>6}"
            f"{s['claim_coverage']:>7.2f}  {motivos[:44]}"
        )

    aciertos_decision = sum(
        1 for c, _b, v, _cc in veredictos if v.decision.value == str(c["expected_action"])
    )
    print(f"\ndecisiones correctas: {aciertos_decision}/{len(veredictos)}")

    tablas = paths.ensure(paths.TABLES)
    pd.DataFrame(filas).to_csv(tablas / "E15_suficiencia.csv", index=False)
    experimentos = paths.ensure(paths.EXPERIMENTS)
    (experimentos / "E15_suficiencia.json").write_text(
        json.dumps(
            {
                "experiment_id": "E15_sufficiency",
                "dataset_id": dataset_id,
                "vehicle_id": VEHICULO,
                "thresholds": umbrales.to_dict(),
                "calibration": "isotonic, cv=5 sobre entrenamiento",
                "cases": [
                    {
                        "case_id": c["case_id"],
                        "fault_id": c["fault_id"],
                        "corpus_variant": c.get("corpus_variant", "FULL"),
                        "bundle": b.to_dict(),
                        "verdict": v.to_dict(),
                        # Rastro de por qué cada cita se aceptó o se descartó.
                        # Sin él la decisión no sería auditable.
                        "support_checks": [c.to_dict() for c in comp],
                    }
                    for c, b, v, comp in veredictos
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print("tabla   E15_suficiencia.csv")
    print("registro experiments/E15_suficiencia.json")
    store.dispose()
    return 0
