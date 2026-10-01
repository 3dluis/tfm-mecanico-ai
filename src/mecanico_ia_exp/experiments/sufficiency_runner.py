"""Ejecución de E15: verificación de suficiencia sobre los casos anotados.

Sin modelo de lenguaje. El verificador es determinista por diseño, y esta fase
comprueba precisamente eso: que la decisión de explicar o abstenerse se puede
tomar y auditar sin que intervenga un generador de texto.

Los umbrales se calibran **solo con validación**. El test sigue cerrado.

El módulo expone además las piezas del recorrido --preparativo, selección de
ventana, atribución, requisito de la puerta de códigos, nombre del artefacto--
porque las ablaciones de E18 tienen que recorrer **el mismo** camino cambiando una
sola pieza. Si cada ejecutor construyera su propio preparativo, una diferencia
entre la ablación y la configuración canónica podría venir del preparativo y la
atribución causal se perdería.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd
import yaml

from mecanico_ia_exp.abstention.sufficiency import (
    POLITICAS,
    VERIFIER_VERSION,
    EvidenceVerifier,
    SufficiencyThresholds,
    SufficiencyVerdict,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import Dataset, load_partition
from mecanico_ia_exp.evaluation.metrics import expected_calibration_error
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.evidence.model import EvidenceBundle
from mecanico_ia_exp.evidence.support import DtcRequirement, SupportCheck, dtc_requirement
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.experiments.retrieval_runner import DIAGNOSTICO_A_DTC, recuperar
from mecanico_ia_exp.llm.agent import PROMPT_VERSION, AgentRun
from mecanico_ia_exp.models.baseline import BaselineConfig, train_baseline
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.ingest import load_vehicle
from mecanico_ia_exp.rag.store import PgVectorStore
from mecanico_ia_exp.rag.vehicle import VehicleProfile
from mecanico_ia_exp.xai.attribution import CaseAttribution, explain_cases, select_background

DATASET = "synthetic_v2"
VEHICULO = "mazda-3-bk-2007"
GOLDSET = paths.CONFIGS / "goldset_mazda3_bk.yaml"

#: Política de evaluación congelada. Se escribe en el registro para que el
#: artefacto diga bajo qué reglas se midió y no haya que deducirlo del commit.
POLITICA_EVALUACION = "docs/methodology/politica-evaluacion-no-oracular.md"


def validar_politica(policy: str) -> str:
    """Comprueba que la política del verificador es una de las declaradas.

    Se valida en el borde --al entrar en el ejecutor-- y no al usarla: una
    política mal escrita produciría un artefacto con el nombre canónico y el
    comportamiento de otra versión, que es exactamente la confusión que el campo
    `verifier_version` del registro existe para evitar.
    """
    if policy not in POLITICAS:
        msg = f"política de suficiencia desconocida: {policy!r}; declaradas {POLITICAS}"
        raise ValueError(msg)
    return policy


def modo_de(*, oracle: bool, adverse: bool) -> str:
    """Nombre del modo de evaluación, tal como va al registro."""
    return "adverse" if adverse else ("oracle" if oracle else "non_oracle")


def sufijo_artefacto(modo: str, policy: str = VERIFIER_VERSION) -> str:
    """Sufijo del nombre de los artefactos de una ejecución.

    Una política no canónica **nunca** puede escribir sobre los registros
    vigentes: `E15_suficiencia.json` es el de v2.1 en modo oracular y el capítulo
    5 cita esa cifra. Sin este sufijo, medir v2.2 (RERUN-B) borraría el artefacto
    con el que hay que compararla, y la comparación dejaría de ser posible desde
    los ficheros.
    """
    sufijo = "" if modo == "oracle" else f"_{modo}"
    if validar_politica(policy) != VERIFIER_VERSION:
        sufijo += f"_{policy.replace('.', '_')}"
    return sufijo


def requisito_dtc(diagnostico: str, policy: str = VERIFIER_VERSION) -> DtcRequirement:
    """Requisito de la puerta de códigos para un diagnóstico, según la política.

    Bajo la política canónica v2.1 la puerta se comporta como en su artefacto
    congelado: `DTC_REQUIRED` siempre. El requisito explícito, leído de cómo esté
    **declarado** el diagnóstico en el mapa de códigos, es lo único que v2.2
    añade (`docs/methodology/politica-puerta-dtc.md`).
    """
    if validar_politica(policy) == "v2.2":
        return dtc_requirement(diagnostico, DIAGNOSTICO_A_DTC)
    return DtcRequirement.DTC_REQUIRED


def calibrar(entrenamiento: Dataset, validacion: Dataset, configuracion: BaselineConfig) -> Any:
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


@dataclass(frozen=True)
class Contexto:
    """Preparativo compartido por E15 y por las ablaciones de E18.

    Lleva el modelo, su calibración y el fondo de atribución ya construidos: son
    las piezas que el pre-registro de E18 declara **intactas**, y compartir el
    objeto es la forma de que ninguna ablación las reconstruya por su cuenta.
    """

    dataset_id: str
    entrenamiento: Dataset
    validacion: Dataset
    perfil: VehicleProfile
    casos_gold: list[dict[str, Any]]
    configuracion: BaselineConfig
    modelo: Any
    calibrado: Any
    fondo: npt.NDArray[np.float64]
    fondo_hash: str
    calibracion: dict[str, Any]
    aciertos: npt.NDArray[np.bool_]


def preparar(dataset_id: str = DATASET) -> Contexto:
    """Carga particiones y conjunto anotado, entrena el bosque y lo calibra.

    El efecto de la calibración se **registra**, no solo se imprime: la cifra
    sostiene la mitad del criterio de PI.1 y una transcripción de consola no es
    un artefacto verificable.
    """
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    perfil = load_vehicle(VEHICULO)
    gold = yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))
    casos_gold = list(gold["cases"])

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    calibrado = calibrar(entrenamiento, validacion, configuracion)

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
        aciertos_m = (pred == validacion.y).astype(bool)
        ece = float(expected_calibration_error(conf, aciertos_m))
        calibracion[clave] = {
            "ece": round(ece, 6),
            "mean_confidence": round(float(conf.mean()), 6),
            "accuracy": round(float(aciertos_m.mean()), 6),
            "bias": round(float(conf.mean() - aciertos_m.mean()), 6),
        }
        print(
            f"{nombre:<14} ECE {ece:.3f} · "
            f"confianza media {conf.mean():.3f} · acierto {aciertos_m.mean():.3f} · "
            f"sesgo {conf.mean() - aciertos_m.mean():+.3f}"
        )

    fondo, huella = select_background(
        entrenamiento.features,
        entrenamiento.y,
        normal_label="F00_normal",
        n=100,
        seed=configuracion.seed,
    )

    predicciones = np.asarray(modelo.predict(validacion.features), dtype=np.str_)
    return Contexto(
        dataset_id=dataset_id,
        entrenamiento=entrenamiento,
        validacion=validacion,
        perfil=perfil,
        casos_gold=casos_gold,
        configuracion=configuracion,
        modelo=modelo,
        calibrado=calibrado,
        fondo=fondo,
        fondo_hash=huella,
        calibracion=calibracion,
        aciertos=np.asarray(predicciones == validacion.y, dtype=bool),
    )


def seleccionar_ventana(caso: Mapping[str, Any], ctx: Contexto, *, adverse: bool) -> int | None:
    """Índice de la ventana de validación con que se ejecuta un caso anotado.

    En el modo adverso se buscan ventanas de esta condición que el modelo
    clasifica **mal**: es el escenario que el modo vigente excluye por
    construcción, y donde se comprueba si una explicación trazable puede
    respaldar un diagnóstico falso.

    Devuelve ``None`` cuando la condición no tiene ninguna ventana del tipo
    pedido, que es un hecho del conjunto y no un error.
    """
    fault_id = str(caso["fault_id"])
    seleccion = (ctx.validacion.y == fault_id) & (~ctx.aciertos if adverse else ctx.aciertos)
    indices = np.flatnonzero(seleccion)
    if indices.size == 0:
        cual = "mal clasificados" if adverse else "correctamente clasificados"
        print(f"{caso['case_id']}: sin casos {cual}")
        return None
    if adverse:
        # Regla A-1 de `politica-evaluacion-no-oracular-enmienda-01.md`: entre
        # los errores del modelo se elige el **más confiado**, que es el único
        # que supera la puerta de confianza y llega al verificador. Elegir el
        # primero por índice escogía el caso menos adverso disponible.
        confianzas = np.asarray(ctx.calibrado.predict_proba(ctx.validacion.features[indices])).max(
            axis=1
        )
        return int(indices[int(np.argmax(confianzas))])
    return int(indices[0])


def case_id_de(validacion: Dataset, i: int) -> str:
    """Identificador de la ventana: sesión y segundo de inicio."""
    return f"{validacion.meta.iloc[i]['session_id']}@{validacion.meta.iloc[i]['t_start']:.0f}s"


def atribucion_de(ctx: Contexto, i: int, case_id: str) -> CaseAttribution:
    """Atribución SHAP de la ventana, con el fondo y la semilla del contexto."""
    return explain_cases(
        ctx.modelo,
        ctx.validacion.features[i : i + 1],
        feature_names=ctx.entrenamiento.feature_names,
        background=ctx.fondo,
        background_hash=ctx.fondo_hash,
        case_ids=[case_id],
        model_id=f"rf_{ctx.dataset_id}",
        meta=ctx.validacion.meta.iloc[[i]].reset_index(drop=True),
        seed=ctx.configuracion.seed,
    )[0]


def confianza_calibrada_de(ctx: Contexto, i: int, clase: str) -> float:
    """Confianza calibrada que el modelo asigna a la clase indicada."""
    prob_cal = np.asarray(ctx.calibrado.predict_proba(ctx.validacion.features[i : i + 1]))[0]
    clases_cal = list(ctx.calibrado.classes_)
    return float(prob_cal[clases_cal.index(clase)])


def fragmentos_excluidos(
    store: PgVectorStore, caso: Mapping[str, Any], *, vehicle_id: str = VEHICULO
) -> tuple[str, ...]:
    """Fragmentos que la condición de evidencia retira del índice.

    La condición ABSENT retira del índice la evidencia que sostenía la
    explicación. Todo lo demás --datos, modelo, atribución, consulta-- es
    idéntico al caso con evidencia: si el agente decidiera igual, no estaría
    usando la evidencia.
    """
    return store.chunks_for_dtc(
        tuple(caso.get("exclude_dtc") or ()), vehicle_id=vehicle_id
    ) + store.chunks_for_files(tuple(caso.get("exclude_files") or ()), vehicle_id=vehicle_id)


@dataclass
class CasoVerificado:
    """Un caso anotado recorrido de punta a punta, con su rastro completo."""

    gold: dict[str, Any]
    case_id: str
    bundle: EvidenceBundle
    verdict: SufficiencyVerdict
    support_checks: list[SupportCheck] = field(default_factory=list)
    diagnosis_used: str = ""
    dtc_requirement: str = DtcRequirement.DTC_REQUIRED.value
    agente: AgentRun | None = None

    @property
    def expected_action(self) -> str:
        return str(self.gold["expected_action"])

    @property
    def corpus_variant(self) -> str:
        return str(self.gold.get("corpus_variant", "FULL"))

    @property
    def correcto(self) -> bool:
        return self.verdict.decision.value == self.expected_action


def documento_suficiencia(
    *,
    modo: str,
    oracle: bool,
    adverse: bool,
    dataset_id: str,
    policy: str,
    umbrales: SufficiencyThresholds,
    calibracion: dict[str, Any],
    casos: list[CasoVerificado],
) -> dict[str, Any]:
    """Contenido del registro de E15, sin la cabecera de identificación.

    Se construye aparte del recorrido para que su forma sea comprobable sin
    ejecutar el experimento: un test con casos de juguete puede verificar que el
    documento sigue llevando los mismos campos que el artefacto vigente.
    """
    return {
        "experiment_id": f"E15_sufficiency{'' if modo == 'oracle' else f'_{modo}'}",
        "mode": modo,
        "oracle_channels_open": {
            # Los tres canales de `docs/methodology/politica-evaluacion-no-oracular.md`.
            "O1_window_selection_requires_correct_prediction": not adverse,
            "O2_retrieval_scoped_by_annotated_label": oracle,
            "O3_support_dtc_from_annotated_label": oracle,
        },
        "evaluation_policy": POLITICA_EVALUACION,
        "dataset_id": dataset_id,
        "vehicle_id": VEHICULO,
        "verifier_version": policy,
        "thresholds": umbrales.to_dict(),
        "calibration": calibracion,
        "cases": [
            {
                "case_id": c.gold["case_id"],
                "fault_id": c.gold["fault_id"],
                "diagnosis_used": c.diagnosis_used,
                "dtc_requirement": c.dtc_requirement,
                "corpus_variant": c.corpus_variant,
                "bundle": c.bundle.to_dict(),
                "verdict": c.verdict.to_dict(),
                # Rastro de por qué cada cita se aceptó o se descartó.
                # Sin él la decisión no sería auditable.
                "support_checks": [s.to_dict() for s in c.support_checks],
            }
            for c in casos
        ],
    }


def run_sufficiency(
    dataset_id: str = DATASET,
    llm: str | None = None,
    *,
    oracle: bool = True,
    adverse: bool = False,
    policy: str = VERIFIER_VERSION,
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

    `policy` elige la versión de la política de suficiencia. Con una política no
    canónica los artefactos llevan sufijo: una ejecución de RERUN-B no puede
    sobrescribir los registros que el capítulo 5 cita.
    """
    validar_politica(policy)
    ctx = preparar(dataset_id)

    umbrales = SufficiencyThresholds()
    verificador = EvidenceVerifier(umbrales)
    store = PgVectorStore()
    provider = get_provider("multilingual")

    print(f"\numbrales: {json.dumps(umbrales.to_dict(), ensure_ascii=False)}\n")
    filas: list[dict[str, Any]] = []
    verificados: list[CasoVerificado] = []

    for caso in ctx.casos_gold:
        # GROUND TRUTH. A partir de aquí solo puede usarse para puntuar.
        fault_id = str(caso["fault_id"])
        i = seleccionar_ventana(caso, ctx, adverse=adverse)
        if i is None:
            continue
        case_id = case_id_de(ctx.validacion, i)

        atribucion = atribucion_de(ctx, i, case_id)
        confianza_calibrada = confianza_calibrada_de(ctx, i, str(atribucion.predicted_class))

        excluidos = fragmentos_excluidos(store, caso)
        # RAG QUERY INPUT. El texto de consulta es el del caso, que describe
        # síntomas; lo que cambia entre modos es qué códigos acotan la búsqueda.
        caso_consulta = caso if oracle else {**caso, "fault_id": str(atribucion.predicted_class)}
        recuperados = recuperar(
            "diagnosis-guided",
            store=store,
            provider=provider,
            caso=caso_consulta,
            vehicle_id=VEHICULO,
            engine_code=ctx.perfil.engine_code or "Z6",
            exclude_chunks=excluidos,
            apply_engine_filter=bool(caso.get("apply_engine_filter", True)),
        )

        # MODEL PREDICTION frente a GROUND TRUTH. En modo no oracular todo lo que
        # sigue se deriva del diagnóstico del modelo, que es lo único que el
        # sistema posee cuando se ejecuta de verdad.
        diagnostico = fault_id if oracle else str(atribucion.predicted_class)
        # Los DTC que documentan la condición **diagnosticada**: si el fragmento
        # citado no porta ninguno, no está hablando de ese fallo.
        codigos_esperados = DIAGNOSTICO_A_DTC.get(diagnostico, ())
        requisito = requisito_dtc(diagnostico, policy)

        bundle, comprobaciones = assemble(
            case_id=case_id,
            perfil=ctx.perfil,
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

        verificados.append(
            CasoVerificado(
                gold=caso,
                case_id=case_id,
                bundle=bundle,
                verdict=veredicto,
                support_checks=list(comprobaciones),
                diagnosis_used=diagnostico,
                dtc_requirement=requisito.value,
                agente=ejecucion,
            )
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
    for c in verificados:
        v = c.verdict
        marca = "OK" if c.correcto else "!!"
        s = v.signals
        motivos = ", ".join(r.value.replace("_", " ").lower() for r in v.reasons)
        print(
            f"{c.gold['case_id']!s:<38}{c.expected_action:>10}{v.decision.value:>10}{marca:>3}"
            f"{s['confidence']:>7.3f}{s['n_documents_applicable']:>6}"
            f"{s['claim_coverage']:>7.2f}  {motivos[:44]}"
        )

    aciertos_decision = sum(1 for c in verificados if c.correcto)
    print(f"\ndecisiones correctas: {aciertos_decision}/{len(verificados)}")

    modo = modo_de(oracle=oracle, adverse=adverse)
    sufijo = sufijo_artefacto(modo, policy)
    tablas = paths.ensure(paths.TABLES)
    pd.DataFrame(filas).to_csv(tablas / f"E15_suficiencia{sufijo}.csv", index=False)
    experimentos = paths.ensure(paths.EXPERIMENTS)
    escribir(
        experimentos / f"E15_suficiencia{sufijo}.json",
        documento_suficiencia(
            modo=modo,
            oracle=oracle,
            adverse=adverse,
            dataset_id=dataset_id,
            policy=policy,
            umbrales=umbrales,
            calibracion=ctx.calibracion,
            casos=verificados,
        ),
        seed=ctx.configuracion.seed,
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
        for c in verificados:
            e = c.agente
            if e is None:
                continue
            agentes.append(e)
            forma = e.output.decision.value if e.output else "—"
            # Sin salida no hay veredicto que juzgar: se marca, no se cuenta.
            respeta = "—" if e.respected_verdict is None else "sí" if e.respected_verdict else "NO"
            print(
                f"{c.gold['case_id']!s:<38}{c.verdict.decision.value:>10}{forma:>10}"
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
            # El registro del agente lleva el mismo sufijo que el del verificador:
            # una redacción producida bajo otra política no es la misma ejecución.
            sufijo_agente = "" if policy == VERIFIER_VERSION else f"_{policy.replace('.', '_')}"
            escribir(
                experimentos / f"E13_agente_{llm}{sufijo_agente}.json",
                {
                    "experiment_id": "E13_agent",
                    "llm": llm,
                    "llm_provider": llm.split("-")[0] if "-" in llm else llm,
                    "identity": agentes[0].raw.identity.as_dict() if agentes[0].raw else None,
                    # El agente consume los paquetes de evidencia de esta misma
                    # ejecución: sin declarar de qué recuperación salen, su
                    # resultado no es rastreable hasta el índice.
                    "retrieval_run_id": f"{modo}@{policy}",
                    "verifier_version": policy,
                    "embedding_space_id": (
                        f"{provider.identity.provider}/{provider.identity.model}/"
                        f"d{provider.identity.dimension}/v{provider.identity.version}"
                    ),
                    "runs": [a.to_dict() for a in agentes],
                },
                seed=ctx.configuracion.seed,
                dataset_id=dataset_id,
                dataset_type="synthetic",
                model=llm,
                prompt_version=PROMPT_VERSION,
                embedding_model=provider.identity.model,
                goldset=GOLDSET.name,
            )
            print(f"\nregistro experiments/E13_agente_{llm}{sufijo_agente}.json")

    print(f"tabla   E15_suficiencia{sufijo}.csv")
    print(f"registro experiments/E15_suficiencia{sufijo}.json")
    store.dispose()
    return 0
