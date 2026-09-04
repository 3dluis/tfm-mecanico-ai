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
    VERIFIER_VERSION,
    EvidenceVerifier,
    SufficiencyThresholds,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import expected_calibration_error
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.llm.agent import PROMPT_VERSION
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


def run_sufficiency(
    dataset_id: str = DATASET,
    llm: str | None = None,
    *,
    oracle: bool = True,
    adverse: bool = False,
) -> int:
    """Ejecuta el experimento de suficiencia sobre el conjunto anotado.

    Los tres modos están definidos y congelados en
    `docs/methodology/politica-evaluacion-no-oracular.md`.

    - `oracle=True`: modo vigente. Los códigos que acotan la búsqueda y los que
      exige el verificador se derivan de la **etiqueta anotada**. Es una **cota
      superior asistida por oráculo**, no una estimación del comportamiento.
    - `oracle=False`: se derivan del **diagnóstico del modelo**, que es lo único
      que el sistema posee en ejecución.
    - `adverse=True`: además, se seleccionan ventanas que el modelo **clasifica
      mal**. El sistema busca evidencia para un diagnóstico incorrecto.

    En los tres modos la etiqueta y la decisión anotada se usan **solo para
    puntuar**, nunca para recuperar ni para verificar.
    """
    """Verifica la suficiencia y, si se pide un proveedor, redacta con él."""
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    perfil = load_vehicle(VEHICULO)
    gold = yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))
    casos_gold = list(gold["cases"])

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    calibrado = _calibrar(entrenamiento, validacion, configuracion)

    # Efecto de la calibración, medido sobre validación. Se **registra**, no solo
    # se imprime: la cifra sostiene la mitad del criterio de PI.1 y una
    # transcripción de consola no es un artefacto verificable.
    calibracion: dict[str, Any] = {
        "method": "isotonic, cv=5 sobre entrenamiento",
        "partition": "validation",
        "n_windows": len(validacion.y),
        "n_bins": 10,
    }
    for clave, nombre, m in (
        ("uncalibrated", "sin calibrar", modelo),
        ("calibrated", "calibrado", calibrado),
    ):
        prob = np.asarray(m.predict_proba(validacion.features), dtype=np.float64)
        pred = np.asarray(m.predict(validacion.features), dtype=validacion.y.dtype)
        conf = prob.max(axis=1)
        aciertos = (pred == validacion.y).astype(bool)
        ece = float(expected_calibration_error(conf, aciertos))
        calibracion[clave] = {
            "ece": round(ece, 6),
            "mean_confidence": round(float(conf.mean()), 6),
            "accuracy": round(float(aciertos.mean()), 6),
            "bias": round(float(conf.mean() - aciertos.mean()), 6),
        }
        print(
            f"{nombre:<14} ECE {ece:.3f} · "
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
        # GROUND TRUTH. A partir de aquí solo puede usarse para puntuar.
        fault_id = str(caso["fault_id"])
        # En el modo adverso se buscan ventanas de esta condición que el modelo
        # clasifica **mal**: es el escenario que el modo vigente excluye por
        # construcción, y donde se comprueba si una explicación trazable puede
        # respaldar un diagnóstico falso.
        seleccion = (validacion.y == fault_id) & (~aciertos if adverse else aciertos)
        indices = np.flatnonzero(seleccion)
        if indices.size == 0:
            cual = "mal clasificados" if adverse else "correctamente clasificados"
            print(f"{caso['case_id']}: sin casos {cual}")
            continue
        if adverse:
            # Regla A-1 de `politica-evaluacion-no-oracular-enmienda-01.md`: entre
            # los errores del modelo se elige el **más confiado**, que es el único
            # que supera la puerta de confianza y llega al verificador. Elegir el
            # primero por índice escogía el caso menos adverso disponible.
            confianzas = np.asarray(calibrado.predict_proba(validacion.features[indices])).max(
                axis=1
            )
            i = int(indices[int(np.argmax(confianzas))])
        else:
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
        # RAG QUERY INPUT. El texto de consulta es el del caso, que describe
        # síntomas; lo que cambia entre modos es qué códigos acotan la búsqueda.
        caso_consulta = caso if oracle else {**caso, "fault_id": str(atribucion.predicted_class)}
        recuperados = recuperar(
            "diagnosis-guided",
            store=store,
            provider=provider,
            caso=caso_consulta,
            vehicle_id=VEHICULO,
            engine_code=perfil.engine_code or "Z6",
            exclude_chunks=excluidos,
            apply_engine_filter=bool(caso.get("apply_engine_filter", True)),
        )

        # Los DTC que documentan la condición **diagnosticada**: si el fragmento
        # citado no porta ninguno, no está hablando de ese fallo.
        from mecanico_ia_exp.evidence.support import DtcRequirement, dtc_requirement
        from mecanico_ia_exp.experiments.retrieval_runner import DIAGNOSTICO_A_DTC

        # MODEL PREDICTION frente a GROUND TRUTH. En modo no oracular todo lo que
        # sigue se deriva del diagnóstico del modelo, que es lo único que el
        # sistema posee cuando se ejecuta de verdad.
        diagnostico = fault_id if oracle else str(atribucion.predicted_class)
        codigos_esperados = DIAGNOSTICO_A_DTC.get(diagnostico, ())
        # El requisito de la puerta de códigos sale de cómo esté **declarado** el
        # diagnóstico, no de su nombre: `docs/methodology/politica-puerta-dtc.md`.
        # Bajo la política canónica v2.1 la puerta se comporta como en su
        # artefacto congelado: `DTC_REQUIRED` siempre. El requisito explícito es
        # lo único que v2.2 añade, y se activa solo cuando esa es la política.
        requisito = (
            dtc_requirement(diagnostico, DIAGNOSTICO_A_DTC)
            if VERIFIER_VERSION == "v2.2"
            else DtcRequirement.DTC_REQUIRED
        )

        bundle, comprobaciones = assemble(
            case_id=case_id,
            perfil=perfil,
            atribucion=atribucion,
            recuperados=recuperados,
            calibrated_confidence=confianza_calibrada,
            accepted_applicability=umbrales.accepted_applicability,
            expected_dtc=codigos_esperados,
            dtc_requirement=requisito,
        )
        veredicto = verificador.verify(bundle)

        ejecucion = None
        if llm:
            from mecanico_ia_exp.llm.agent import run_agent
            from mecanico_ia_exp.llm.provider import get_llm

            ejecucion = run_agent(get_llm(llm), bundle, veredicto)
            ejecucion.gold_case_id = str(caso["case_id"])

        veredictos.append(
            (caso, bundle, veredicto, comprobaciones, ejecucion, diagnostico, requisito.value)
        )

        esperado = str(caso["expected_action"])
        correcto = veredicto.decision.value == esperado
        filas.append(
            {
                "case_id_gold": caso["case_id"],
                "fault_id": fault_id,
                "predicted_class": str(atribucion.predicted_class),
                "prediction_correct": str(atribucion.predicted_class) == fault_id,
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
    for caso, _bundle, v, _comp, _e, _d, _r in veredictos:
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
        1
        for c, _b, v, _cc, _e, _d, _r in veredictos
        if v.decision.value == str(c["expected_action"])
    )
    print(f"\ndecisiones correctas: {aciertos_decision}/{len(veredictos)}")

    modo = "adverse" if adverse else ("oracle" if oracle else "non_oracle")
    sufijo = "" if modo == "oracle" else f"_{modo}"
    tablas = paths.ensure(paths.TABLES)
    pd.DataFrame(filas).to_csv(tablas / f"E15_suficiencia{sufijo}.csv", index=False)
    experimentos = paths.ensure(paths.EXPERIMENTS)
    escribir(
        experimentos / f"E15_suficiencia{sufijo}.json",
        {
            "experiment_id": f"E15_sufficiency{sufijo}",
            "mode": modo,
            "oracle_channels_open": {
                # Los tres canales de `docs/methodology/politica-evaluacion-no-oracular.md`.
                "O1_window_selection_requires_correct_prediction": not adverse,
                "O2_retrieval_scoped_by_annotated_label": oracle,
                "O3_support_dtc_from_annotated_label": oracle,
            },
            "evaluation_policy": "docs/methodology/politica-evaluacion-no-oracular.md",
            "dataset_id": dataset_id,
            "vehicle_id": VEHICULO,
            "verifier_version": VERIFIER_VERSION,
            "thresholds": umbrales.to_dict(),
            "calibration": calibracion,
            "cases": [
                {
                    "case_id": c["case_id"],
                    "fault_id": c["fault_id"],
                    "diagnosis_used": d,
                    "dtc_requirement": r,
                    "corpus_variant": c.get("corpus_variant", "FULL"),
                    "bundle": b.to_dict(),
                    "verdict": v.to_dict(),
                    # Rastro de por qué cada cita se aceptó o se descartó.
                    # Sin él la decisión no sería auditable.
                    "support_checks": [c.to_dict() for c in comp],
                }
                for c, b, v, comp, _e, d, r in veredictos
            ],
        },
        seed=configuracion.seed,
        dataset_id=dataset_id,
        dataset_type="synthetic",
        embedding_model=provider.identity.model,
        goldset=GOLDSET.name,
    )
    if llm:
        print("\n=== redacción con el modelo de lenguaje ===")
        cab = (
            f"{'caso':<38}{'veredicto':>10}{'redactó':>10}{'respeta':>9}"
            f"{'citas falsas':>14}{'esquema':>9}{'seg':>7}"
        )
        print(cab)
        print("-" * len(cab))
        agentes = []
        for caso, _b, v, _c, e, _d, _r in veredictos:
            if e is None:
                continue
            agentes.append(e)
            forma = e.output.decision.value if e.output else "—"
            # Sin salida no hay veredicto que juzgar: se marca, no se cuenta.
            respeta = "—" if e.respected_verdict is None else "sí" if e.respected_verdict else "NO"
            print(
                f"{caso['case_id']!s:<38}{v.decision.value:>10}{forma:>10}"
                f"{respeta:>9}"
                f"{len(e.fake_citations):>14}"
                f"{('ok' if not e.schema_error else 'FALLA'):>9}"
                f"{(e.raw.latency_s if e.raw else 0):>7.1f}"
            )
        if agentes:
            n = len(agentes)
            print(
                f"\n  salidas válidas    {sum(1 for a in agentes if a.valid)}/{n}"
                f"\n  respetan veredicto {sum(1 for a in agentes if a.respected_verdict)}"
                f"/{sum(1 for a in agentes if a.respected_verdict is not None)}"
                " (sobre salidas evaluables)"
                f"\n  citas inventadas   {sum(len(a.fake_citations) for a in agentes)}"
                f"\n  fallos de esquema  {sum(1 for a in agentes if a.schema_error)}"
            )
            escribir(
                experimentos / f"E13_agente_{llm}.json",
                {
                    "experiment_id": "E13_agent",
                    "llm": llm,
                    "identity": agentes[0].raw.identity.as_dict() if agentes[0].raw else None,
                    "runs": [a.to_dict() for a in agentes],
                },
                seed=configuracion.seed,
                dataset_id=dataset_id,
                dataset_type="synthetic",
                model=llm,
                prompt_version=PROMPT_VERSION,
                goldset=GOLDSET.name,
            )
            print(f"\nregistro experiments/E13_agente_{llm}.json")

    print(f"tabla   E15_suficiencia{sufijo}.csv")
    print(f"registro experiments/E15_suficiencia{sufijo}.json")
    store.dispose()
    return 0
