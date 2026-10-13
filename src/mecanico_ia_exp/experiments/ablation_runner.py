"""Ejecución de E18: ablaciones del sistema de decisión.

Pre-registro vinculante: `docs/methodology/preregistro-e18-ablaciones.md`, congelado
antes de cualquier medición. Cada ablación cambia **exactamente un** elemento
respecto de la configuración canónica --verificador v2.1, umbral 0,79, recuperación
guiada por el diagnóstico, observaciones por atribución-- y todo lo demás se toma
del mismo preparativo que E15: mismo conjunto, mismo modelo, misma calibración,
mismo fondo de atribución, misma semilla.

Por eso este módulo no construye casi nada propio: reutiliza las piezas que
`sufficiency_runner` expone. Si duplicara el preparativo, una diferencia entre la
ablación y la configuración canónica podría venir de ahí, y la ablación dejaría de
aislar la pieza que retira.

Las ablaciones **no redactan**: se ejecutan sin proveedor de lenguaje, porque lo
que miden es la decisión y la evidencia, no la redacción.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd

from mecanico_ia_exp.abstention.sufficiency import (
    VERIFIER_VERSION,
    Decision,
    EvidenceVerifier,
    Reason,
    Sufficiency,
    SufficiencyThresholds,
    SufficiencyVerdict,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.evidence.model import EvidenceBundle
from mecanico_ia_exp.experiments.destinos import ArtefactoOcupadoError, exigir_libres
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.experiments.retrieval_runner import (
    DIAGNOSTICO_A_DTC,
    PROFUNDIDAD,
    TOP_K,
    recuperar,
    reordenar_por_autoridad,
)
from mecanico_ia_exp.experiments.sufficiency_runner import (
    DATASET,
    GOLDSET,
    POLITICA_EVALUACION,
    VEHICULO,
    CasoVerificado,
    Contexto,
    atribucion_de,
    case_id_de,
    confianza_calibrada_de,
    fragmentos_excluidos,
    preparar,
    requisito_dtc,
    seleccionar_ventana,
)
from mecanico_ia_exp.rag.embeddings import EmbeddingProvider, get_provider
from mecanico_ia_exp.rag.store import PgVectorStore, RetrievedChunk
from mecanico_ia_exp.xai.attribution import (
    CaseAttribution,
    Direccion,
    SignalAttribution,
    split_feature_name,
)

#: Las cuatro ablaciones, con el nombre que les da el pre-registro. El orden es el
#: del documento y no se reordena: los informes se leen contra esa tabla.
ABLACIONES: dict[str, str] = {
    "A1": "sin atribución",
    "A2": "sin recuperación semántica",
    "A3": "sin criterio de suficiencia",
    "A4": "umbral único",
}

#: Qué se cambia, operativamente, en cada ablación. Va al registro porque un
#: identificador no dice qué se midió, y el lector del artefacto no tiene por qué
#: tener el pre-registro delante.
CAMBIO_OPERATIVO: dict[str, str] = {
    "A1": (
        "las tres observaciones se eligen por |z| del descriptor frente a la media y "
        "desviación de la clase F00_normal en entrenamiento, no por importancia de Shapley"
    ),
    "A2": (
        "la consulta no se vectoriza: recuperación léxica sobre el texto completo con los "
        "mismos filtros de vehículo, motor y códigos de avería y la misma profundidad"
    ),
    "A3": (
        "se retira el criterio compuesto: EXPLAIN si hay al menos un fragmento aplicable, "
        "ABSTAIN si no hay ninguno"
    ),
    "A4": (
        "la decisión se toma solo con la confianza calibrada frente al umbral, ignorando "
        "cobertura, número de fragmentos y de fuentes y contradicciones"
    ),
}

PREREGISTRO = "docs/methodology/preregistro-e18-ablaciones.md"

#: Clase sin fallo contra la que A1 tipifica los descriptores. Es la misma que
#: define el fondo de la atribución canónica: la ablación cambia el criterio de
#: selección, no la referencia de normalidad.
CLASE_SIN_FALLO = "F00_normal"

#: Función explicada por el sustituto de A1. Se declara como ablación en el propio
#: campo: un artefacto de A1 no puede parecer una atribución SHAP.
FUNCION_EXPLICADA_A1 = "ablacion_A1[desviacion_tipificada_vs_F00_normal]"

#: Umbral relativo por debajo del cual una contribución se considera neutra. Es el
#: mismo criterio del 2 % de la atribución canónica, para que la regla que descarta
#: observaciones neutras se comporte igual en las dos rutas.
UMBRAL_NEUTRO = 0.02


# ---------------------------------------------------------------------------
# A1: observaciones por desviación tipificada
# ---------------------------------------------------------------------------


def estadisticos_sin_fallo(
    x_train: npt.NDArray[np.float64],
    y_train: npt.NDArray[np.str_],
    *,
    normal_label: str = CLASE_SIN_FALLO,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Media y desviación de cada descriptor en la clase sin fallo de entrenamiento.

    **Solo entrenamiento.** Si la referencia incluyera validación, la selección de
    observaciones llevaría información de la partición sobre la que se mide, y la
    ablación compararía dos cosas distintas en lugar de un criterio contra otro.
    """
    normales = np.flatnonzero(y_train == normal_label)
    if normales.size == 0:
        msg = f"No hay muestras de la clase {normal_label!r} en entrenamiento"
        raise ValueError(msg)
    muestras = np.asarray(x_train[normales], dtype=np.float64)
    return muestras.mean(axis=0), muestras.std(axis=0)


def desviaciones_tipificadas(
    x_caso: npt.NDArray[np.float64],
    media: npt.NDArray[np.float64],
    desviacion: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Desviación tipificada de cada descriptor del caso frente a la clase sin fallo.

    Un descriptor constante en la clase sin fallo tiene desviación cero y su
    cociente no está definido. Se le asigna z = 0 en lugar de infinito: un
    descriptor que no varía en la normalidad no distingue nada, y dejar que un
    infinito lo coloque primero sería un artefacto aritmético, no una observación.
    """
    z = np.zeros_like(media, dtype=np.float64)
    utiles = desviacion > 0.0
    z[utiles] = (np.asarray(x_caso, dtype=np.float64)[utiles] - media[utiles]) / desviacion[utiles]
    return z


def atribucion_por_desviacion(
    *,
    x_caso: npt.NDArray[np.float64],
    media: npt.NDArray[np.float64],
    desviacion: npt.NDArray[np.float64],
    feature_names: tuple[str, ...],
    case_id: str,
    model_id: str,
    predicted_class: str,
    confidence: float,
    session_id: str | None = None,
    window_start_s: float | None = None,
    window_end_s: float | None = None,
    seed: int = 0,
) -> CaseAttribution:
    """Sustituto de la atribución para A1, con la **misma estructura**.

    Se devuelve un `CaseAttribution` y no una estructura nueva para no tocar
    `assemble`: el resto del recorrido debe ser idéntico, y cualquier cambio en el
    ensamblado introduciría una segunda variable en una ablación que solo puede
    manipular una.

    El campo `importance` lleva la desviación tipificada con su signo, de modo que
    `CaseAttribution.top` --que ordena por valor absoluto-- selecciona exactamente
    los descriptores de mayor |z|. `explained_function` declara que esto es una
    ablación y no una atribución de Shapley.
    """
    z = desviaciones_tipificadas(x_caso, media, desviacion)
    umbral = float(np.abs(z).max()) * UMBRAL_NEUTRO
    atribuciones: list[SignalAttribution] = []
    for j, nombre in enumerate(feature_names):
        senal, estadistico = split_feature_name(nombre)
        valor_z = float(z[j])
        direccion: Direccion = (
            "neutral" if abs(valor_z) < umbral else ("increases" if valor_z > 0 else "decreases")
        )
        atribuciones.append(
            SignalAttribution(
                feature=nombre,
                signal=senal,
                statistic=estadistico,
                importance=valor_z,
                direction=direccion,
                value=float(x_caso[j]),
            )
        )
    # Huella de la referencia frente a la que se tipificó. Cumple el papel que el
    # hash del fondo cumple en la atribución canónica: identificar contra qué se
    # comparó, sin lo cual la observación no es reproducible.
    huella = hashlib.sha256(media.tobytes() + desviacion.tobytes()).hexdigest()[:16]
    return CaseAttribution(
        explanation_id=f"{model_id}:{case_id}",
        case_id=case_id,
        model_id=model_id,
        explained_function=FUNCION_EXPLICADA_A1,
        predicted_class=predicted_class,
        confidence=confidence,
        attributions=tuple(atribuciones),
        session_id=session_id,
        window_start_s=window_start_s,
        window_end_s=window_end_s,
        background_hash=huella,
        explainer="ablacion_A1:z_score_vs_F00_normal",
        seed=seed,
    )


# ---------------------------------------------------------------------------
# A2: recuperación léxica
# ---------------------------------------------------------------------------


class AlmacenLexico(Protocol):
    """Lo único que A2 necesita de un almacén: búsqueda de texto completo.

    Se declara como protocolo para que la ruta léxica se pueda probar con un
    doble, sin base de datos: la regla que esta ablación implementa --filtros y
    reordenación-- no necesita PostgreSQL para ser correcta o incorrecta.
    """

    def search_lexical(
        self,
        query_text: str,
        *,
        vehicle_id: str,
        top_k: int = 10,
        engine_codes: tuple[str, ...] | None = None,
        language: str = "en",
    ) -> list[RetrievedChunk]: ...


def recuperar_lexico(
    *,
    store: AlmacenLexico,
    caso: Mapping[str, Any],
    vehicle_id: str,
    engine_code: str,
    dtc_codes: tuple[str, ...],
    top_k: int = TOP_K,
    exclude_chunks: tuple[str, ...] = (),
    language: str = "en",
    apply_engine_filter: bool = True,
    depth: int = PROFUNDIDAD,
) -> list[RetrievedChunk]:
    """Ruta de A2: la consulta **no se vectoriza**.

    Vive aquí y no en `retrieval_runner.recuperar` a propósito: `ESTRATEGIAS` y el
    comportamiento de esa función definen E12, que ya está medido y publicado.
    Añadir una estrategia allí cambiaría el conjunto de estrategias comparadas en
    un experimento cerrado.

    Se conservan los demás filtros de la estrategia guiada --vehículo, motor cuando
    corresponde, códigos de avería del diagnóstico-- y la misma profundidad y
    `top_k`, porque la única variable que la ablación manipula es la similitud
    semántica. El filtro de códigos se aplica después de recuperar, porque la
    búsqueda de texto completo no lo admite como predicado; el efecto es el mismo
    que el del predicado de la ruta semántica.
    """
    clave = "query" if language == "en" else f"query_{language}"
    consulta = " ".join(str(caso.get(clave) or caso["query"]).split())
    motores: tuple[str, ...] | None = (
        ((engine_code, "ZJ") if engine_code == "Z6" else (engine_code,))
        if apply_engine_filter
        else None
    )
    crudos = store.search_lexical(
        consulta,
        vehicle_id=vehicle_id,
        top_k=depth,
        engine_codes=motores,
        language=language,
    )
    retirados = set(exclude_chunks)
    candidatos = [r for r in crudos if r.chunk_id not in retirados]
    if dtc_codes:
        # Sin códigos declarados para el diagnóstico no se filtra: es el
        # equivalente léxico de la degradación que la estrategia guiada aplica
        # cuando el mapa no documenta la condición.
        pedidos = set(dtc_codes)
        candidatos = [r for r in candidatos if pedidos & set(r.dtc_codes)]
    return reordenar_por_autoridad(candidatos, top_k)


# ---------------------------------------------------------------------------
# A3 y A4: reglas de decisión degradadas
# ---------------------------------------------------------------------------


def decision_a3(fragmentos_aplicables: int) -> tuple[Decision, list[Reason]]:
    """A3: explicar si existe algún fragmento aplicable, abstenerse si no hay ninguno.

    No se comprueba si el fragmento sostiene lo afirmado, que es justo la pieza que
    esta ablación retira.
    """
    if fragmentos_aplicables >= 1:
        return Decision.EXPLAIN, []
    return Decision.ABSTAIN, [Reason.NO_DOCUMENTARY_EVIDENCE]


def decision_a4(confianza: float, *, min_confidence: float) -> tuple[Decision, list[Reason]]:
    """A4: explicar si la confianza calibrada alcanza el umbral, y nada más.

    Se ignoran cobertura, número de fragmentos, número de fuentes y
    contradicciones: es una puerta de confianza sola, que es lo que la ablación
    contrasta contra el criterio compuesto.
    """
    if confianza >= min_confidence:
        return Decision.EXPLAIN, []
    return Decision.ABSTAIN, [Reason.LOW_CONFIDENCE]


def veredicto_de_ablacion(
    ablacion: str,
    *,
    bundle: EvidenceBundle,
    canonico: SufficiencyVerdict,
    umbrales: SufficiencyThresholds,
) -> SufficiencyVerdict:
    """Veredicto de la ablación, reutilizando las señales del verificador canónico.

    `A1` y `A2` no cambian la regla de decisión --cambian la evidencia que le
    llega--, así que devuelven el veredicto del verificador tal cual. `A3` y `A4`
    conservan las mismas señales medidas y sustituyen solo la regla: así la
    comparación entre ablación y configuración canónica se lee sobre las mismas
    cifras y la diferencia es atribuible a la regla.
    """
    if ablacion in ("A1", "A2"):
        return canonico
    if ablacion == "A3":
        decision, motivos = decision_a3(int(canonico.signals["n_documents_applicable"]))
        faltante = [] if decision is Decision.EXPLAIN else ["ningún fragmento documental aplicable"]
    elif ablacion == "A4":
        decision, motivos = decision_a4(bundle.confidence, min_confidence=umbrales.min_confidence)
        faltante = (
            []
            if decision is Decision.EXPLAIN
            else [f"confianza {bundle.confidence:.3f} < {umbrales.min_confidence:.2f}"]
        )
    else:
        msg = f"ablación desconocida: {ablacion!r}; declaradas {tuple(ABLACIONES)}"
        raise ValueError(msg)
    return SufficiencyVerdict(
        case_id=canonico.case_id,
        sufficiency=(
            Sufficiency.SUPPORTED
            if decision is Decision.EXPLAIN
            else Sufficiency.INSUFFICIENT_EVIDENCE
        ),
        decision=decision,
        reasons=motivos,
        signals=dict(canonico.signals),
        missing_evidence=faltante,
    )


# ---------------------------------------------------------------------------
# Resumen: las dos tasas y la cobertura, con sus denominadores
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Tasa:
    """Un recuento con su denominador y sus ventanas independientes.

    La tasa nunca viaja sola. Los diecisiete casos proceden de cinco ventanas de
    telemetría, de modo que una proporción sin su número de ventanas sugeriría una
    independencia que el conjunto no tiene.
    """

    numerador: int
    denominador: int
    ventanas: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "numerator": self.numerador,
            "denominator": self.denominador,
            "n_independent_windows": self.ventanas,
            "rate": None if self.denominador == 0 else round(self.numerador / self.denominador, 4),
        }


def _tasa(casos: Sequence[CasoVerificado], decision: Decision) -> Tasa:
    """Cuántos de estos casos terminaron en la decisión indicada."""
    return Tasa(
        numerador=sum(1 for c in casos if c.verdict.decision is decision),
        denominador=len(casos),
        ventanas=len({c.case_id for c in casos}),
    )


def resumen_abstencion(casos: Sequence[CasoVerificado]) -> dict[str, Any]:
    """Falsa confianza, abstención innecesaria y cobertura, contadas como en M5.

    Definiciones de `docs/memoria/cap4_marco_metodologico.md` (M5):

    - falsa confianza: explica / casos que **debían abstenerse**;
    - abstención innecesaria: se abstiene / casos que **debían explicar**.

    El denominador de la falsa confianza se publica dos veces, y no por prudencia
    decorativa: las tres filas de la condición con distractor **y filtro de motor**
    no añaden ningún distractor que la condición parcial no tuviera, de modo que el
    capítulo 5 las cuenta aparte. Presentar solo el denominador grande daría una
    tasa más favorable por casos que no discriminan.

    Las dos tasas no se combinan en una sola cifra: una compromete a quien actúa
    sobre el vehículo y la otra solo cuesta cobertura.
    """
    debian_abstenerse = [c for c in casos if c.expected_action == "ABSTAIN"]
    sin_distractor_con_filtro = [c for c in debian_abstenerse if c.corpus_variant != "DISTRACTOR"]
    debian_explicar = [c for c in casos if c.expected_action == "EXPLAIN"]
    evidencia_completa = [c for c in casos if c.corpus_variant == "FULL"]

    falsa_confianza = _tasa(sin_distractor_con_filtro, Decision.EXPLAIN).to_dict()
    falsa_confianza["including_distractor_with_filter"] = _tasa(
        debian_abstenerse, Decision.EXPLAIN
    ).to_dict()
    return {
        "metric_definition": "docs/memoria/cap4_marco_metodologico.md, M5",
        "n_cases": len(casos),
        "false_confidence": falsa_confianza,
        "unnecessary_abstention": _tasa(debian_explicar, Decision.ABSTAIN).to_dict(),
        "coverage_full_evidence": _tasa(evidencia_completa, Decision.EXPLAIN).to_dict(),
        "decisions": {c.gold["case_id"]: c.verdict.decision.value for c in casos},
    }


# ---------------------------------------------------------------------------
# Recorrido de una ablación
# ---------------------------------------------------------------------------


def fila_de(caso: CasoVerificado, *, grados: frozenset[str]) -> dict[str, Any]:
    """Una fila por caso: lo que el pre-registro exige registrar, y nada más.

    Incluye los `chunk_id` que llegaron al verificador porque sin ellos no se
    puede decir si una diferencia con la configuración canónica viene de la
    evidencia o de la decisión, que es la pregunta de `A1` y `A2`.
    """
    señales = caso.verdict.signals
    aplicables = caso.bundle.applicable_documents(grados)
    return {
        "case_id": caso.gold["case_id"],
        "window_case_id": caso.case_id,
        "fault_id": caso.gold["fault_id"],
        "condition": caso.corpus_variant,
        "diagnosis_used": caso.diagnosis_used,
        "dtc_requirement": caso.dtc_requirement,
        "calibrated_confidence": señales["confidence"],
        "n_documents_applicable": señales["n_documents_applicable"],
        "claim_coverage": señales["claim_coverage"],
        "expected_action": caso.expected_action,
        "decision": caso.verdict.decision.value,
        "correct": caso.correcto,
        "sufficiency": caso.verdict.sufficiency.value,
        "reasons": "; ".join(r.value for r in caso.verdict.reasons),
        "chunk_ids_to_verifier": ";".join(d.chunk_id for d in caso.bundle.documents),
        "applicable_chunk_ids": ";".join(d.chunk_id for d in aplicables),
    }


def ejecutar_ablacion(
    ablacion: str,
    ctx: Contexto,
    *,
    store: PgVectorStore,
    provider: EmbeddingProvider | None,
    umbrales: SufficiencyThresholds,
    oracle: bool = True,
) -> list[CasoVerificado]:
    """Recorre el conjunto anotado con una ablación activa.

    Todo lo que no es la pieza ablacionada se toma del contexto compartido con
    E15. La política del verificador es la canónica en las cuatro: una ablación que
    además cambiara de política manipularía dos variables.
    """
    if ablacion not in ABLACIONES:
        msg = f"ablación desconocida: {ablacion!r}; declaradas {tuple(ABLACIONES)}"
        raise ValueError(msg)
    verificador = EvidenceVerifier(umbrales)
    media: npt.NDArray[np.float64] | None = None
    desviacion: npt.NDArray[np.float64] | None = None
    if ablacion == "A1":
        media, desviacion = estadisticos_sin_fallo(ctx.entrenamiento.features, ctx.entrenamiento.y)

    verificados: list[CasoVerificado] = []
    for caso in ctx.casos_gold:
        # GROUND TRUTH. A partir de aquí solo puede usarse para puntuar.
        fault_id = str(caso["fault_id"])
        i = seleccionar_ventana(caso, ctx, adverse=False)
        if i is None:
            continue
        case_id = case_id_de(ctx.evaluacion, i)

        if ablacion == "A1" and media is not None and desviacion is not None:
            prob = np.asarray(
                ctx.modelo.predict_proba(ctx.evaluacion.features[i : i + 1]), dtype=np.float64
            )[0]
            indice = int(prob.argmax())
            fila_meta = ctx.evaluacion.meta.iloc[i]
            atribucion = atribucion_por_desviacion(
                x_caso=np.asarray(ctx.evaluacion.features[i], dtype=np.float64),
                media=media,
                desviacion=desviacion,
                feature_names=ctx.entrenamiento.feature_names,
                case_id=case_id,
                model_id=f"rf_{ctx.dataset_id}",
                predicted_class=str(ctx.modelo.classes_[indice]),
                confidence=float(prob[indice]),
                session_id=str(fila_meta["session_id"]),
                window_start_s=float(fila_meta["t_start"]),
                window_end_s=float(fila_meta["t_end"]),
                seed=ctx.configuracion.seed,
            )
        else:
            atribucion = atribucion_de(ctx, i, case_id)

        predicha = str(atribucion.predicted_class)
        confianza_calibrada = confianza_calibrada_de(ctx, i, predicha)
        excluidos = fragmentos_excluidos(store, caso)

        # MODEL PREDICTION frente a GROUND TRUTH: en modo no oracular todo lo que
        # sigue sale del diagnóstico del modelo, que es lo único que el sistema
        # posee cuando se ejecuta de verdad.
        diagnostico = fault_id if oracle else predicha
        codigos_esperados = DIAGNOSTICO_A_DTC.get(diagnostico, ())
        aplicar_filtro_motor = bool(caso.get("apply_engine_filter", True))

        if ablacion == "A2":
            recuperados = recuperar_lexico(
                store=store,
                caso=caso,
                vehicle_id=VEHICULO,
                engine_code=ctx.perfil.engine_code or "Z6",
                dtc_codes=codigos_esperados,
                exclude_chunks=excluidos,
                apply_engine_filter=aplicar_filtro_motor,
            )
        else:
            if provider is None:  # pragma: no cover - lo garantiza el ejecutor
                msg = "la ruta semántica necesita un proveedor de embeddings"
                raise ValueError(msg)
            caso_consulta = caso if oracle else {**caso, "fault_id": predicha}
            recuperados = recuperar(
                "diagnosis-guided",
                store=store,
                provider=provider,
                caso=caso_consulta,
                vehicle_id=VEHICULO,
                engine_code=ctx.perfil.engine_code or "Z6",
                exclude_chunks=excluidos,
                apply_engine_filter=aplicar_filtro_motor,
            )

        requisito = requisito_dtc(diagnostico, VERIFIER_VERSION)
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
        canonico = verificador.verify(bundle)
        veredicto = veredicto_de_ablacion(
            ablacion, bundle=bundle, canonico=canonico, umbrales=umbrales
        )
        verificados.append(
            CasoVerificado(
                gold=caso,
                case_id=case_id,
                bundle=bundle,
                verdict=veredicto,
                support_checks=list(comprobaciones),
                diagnosis_used=diagnostico,
                dtc_requirement=requisito.value,
            )
        )
    return verificados


def documento_ablacion(
    ablacion: str,
    *,
    modo: str,
    oracle: bool,
    dataset_id: str,
    umbrales: SufficiencyThresholds,
    calibracion: dict[str, Any],
    casos: list[CasoVerificado],
    embedding_space_id: str | None,
) -> dict[str, Any]:
    """Contenido del registro de una ablación, sin la cabecera de identificación.

    Se construye aparte del recorrido para que su forma sea comprobable sin
    ejecutar el experimento.
    """
    grados = umbrales.accepted_applicability
    return {
        "experiment_id": f"E18_ablation_{ablacion}",
        "ablation_id": ablacion,
        "ablation": ABLACIONES[ablacion],
        "operational_change": CAMBIO_OPERATIVO[ablacion],
        "preregistration": PREREGISTRO,
        "mode": modo,
        "oracle_channels_open": {
            "O1_window_selection_requires_correct_prediction": True,
            "O2_retrieval_scoped_by_annotated_label": oracle,
            "O3_support_dtc_from_annotated_label": oracle,
        },
        "evaluation_policy": POLITICA_EVALUACION,
        "dataset_id": dataset_id,
        "vehicle_id": VEHICULO,
        "verifier_version": VERIFIER_VERSION,
        "retrieval": {
            # A2 no vectoriza la consulta: declararle un espacio de embeddings
            # afirmaría algo que no ocurrió.
            "route": "lexical_full_text" if ablacion == "A2" else "diagnosis-guided",
            "query_vectorized": ablacion != "A2",
            "embedding_space_id": None if ablacion == "A2" else embedding_space_id,
            "top_k": TOP_K,
            "depth": PROFUNDIDAD,
        },
        "thresholds": umbrales.to_dict(),
        "calibration": calibracion,
        "summary": resumen_abstencion(casos),
        "cases": [
            {
                **fila_de(c, grados=grados),
                "bundle": c.bundle.to_dict(),
                "verdict": c.verdict.to_dict(),
                # Rastro de por qué cada cita se aceptó o se descartó.
                "support_checks": [s.to_dict() for s in c.support_checks],
            }
            for c in casos
        ],
    }


def destinos_de(ablacion: str, etiqueta: str = "") -> dict[str, Path]:
    """Los dos artefactos de una ablación, antes de escribir el primero."""
    sufijo = f"_{etiqueta}" if etiqueta else ""
    return {
        "registro": paths.EXPERIMENTS / f"E18_ablacion_{ablacion}{sufijo}.json",
        "tabla": paths.TABLES / f"E18_ablacion_{ablacion}{sufijo}.csv",
    }


def run_ablations(
    dataset_id: str = DATASET,
    *,
    ablation: str = "all",
    oracle: bool = True,
    etiqueta: str = "",
    particion: Literal["train", "validation", "test"] = "validation",
    allow_test: bool = False,
    reason: str = "",
) -> int:
    """Ejecuta una ablación o las cuatro, cada una con su registro y su tabla.

    No se pasa proveedor de lenguaje: el pre-registro declara que las ablaciones
    no redactan.

    ``etiqueta`` entra en el nombre de los dos artefactos de cada ablación. Sin
    ella se conservan los nombres de la ejecución publicada del 1 de octubre y
    la ejecución **se niega a escribir** si ya existen.

    ``particion`` permite repetir las ablaciones sobre el conjunto de **prueba**,
    que es el tercero de los pendientes del tutor. Hacerlo exige ``allow_test``
    y una ``reason`` escrita, y constituye una **apertura del conjunto de
    prueba** que hay que registrar en
    ``docs/methodology/registro-aperturas-test.md``: el ejecutor no puede
    obligar a escribir ese registro, pero sí exige la razón y la deja en el
    artefacto.
    """
    if ablation != "all" and ablation not in ABLACIONES:
        msg = f"ablación desconocida: {ablation!r}; declaradas {(*ABLACIONES, 'all')}"
        raise ValueError(msg)
    seleccionadas = tuple(ABLACIONES) if ablation == "all" else (ablation,)

    if particion != "validation" and not etiqueta:
        msg = (
            f"una ejecución sobre {particion!r} necesita su propia etiqueta: sin ella "
            "sobrescribiría los artefactos de la ejecución publicada sobre validación"
        )
        raise ArtefactoOcupadoError(msg)
    for ablacion in seleccionadas:
        exigir_libres(destinos_de(ablacion, etiqueta))

    ctx = preparar(dataset_id, particion=particion, allow_test=allow_test, reason=reason)
    umbrales = SufficiencyThresholds()
    store = PgVectorStore()
    # El proveedor se construye solo si alguna ablación recorre la ruta semántica:
    # cargar el modelo de embeddings para medir A2 sola sería tiempo gastado en una
    # pieza que esa ablación precisamente no usa.
    provider = get_provider("multilingual") if any(a != "A2" for a in seleccionadas) else None
    espacio = (
        None
        if provider is None
        else (
            f"{provider.identity.provider}/{provider.identity.model}/"
            f"d{provider.identity.dimension}/v{provider.identity.version}"
        )
    )
    modo = "oracle" if oracle else "non_oracle"
    paths.ensure(paths.TABLES)
    paths.ensure(paths.EXPERIMENTS)

    for ablacion in seleccionadas:
        print(f"\n=== E18 {ablacion}: {ABLACIONES[ablacion]} · modo {modo} ===")
        casos = ejecutar_ablacion(
            ablacion,
            ctx,
            store=store,
            provider=provider,
            umbrales=umbrales,
            oracle=oracle,
        )
        filas = [fila_de(c, grados=umbrales.accepted_applicability) for c in casos]
        cab = (
            f"{'caso':<38}{'esperado':>10}{'decidido':>10}{'':>3}"
            f"{'conf':>7}{'docs':>6}{'cob.':>7}  motivos"
        )
        print(cab)
        print("-" * len(cab))
        for c in casos:
            s = c.verdict.signals
            motivos = ", ".join(r.value.replace("_", " ").lower() for r in c.verdict.reasons)
            print(
                f"{c.gold['case_id']!s:<38}{c.expected_action:>10}"
                f"{c.verdict.decision.value:>10}{'OK' if c.correcto else '!!':>3}"
                f"{s['confidence']:>7.3f}{s['n_documents_applicable']:>6}"
                f"{s['claim_coverage']:>7.2f}  {motivos[:44]}"
            )
        resumen = resumen_abstencion(casos)
        fc = resumen["false_confidence"]
        ai = resumen["unnecessary_abstention"]
        cob = resumen["coverage_full_evidence"]
        print(
            f"\n  falsa confianza        {fc['numerator']}/{fc['denominator']}"
            f" sobre {fc['n_independent_windows']} ventanas"
            f" ({fc['including_distractor_with_filter']['numerator']}"
            f"/{fc['including_distractor_with_filter']['denominator']}"
            " con la condición con distractor y filtro)"
            f"\n  abstención innecesaria {ai['numerator']}/{ai['denominator']}"
            f" sobre {ai['n_independent_windows']} ventanas"
            f"\n  cobertura (evidencia completa) {cob['numerator']}/{cob['denominator']}"
        )

        destinos = destinos_de(ablacion, etiqueta)
        pd.DataFrame(filas).to_csv(destinos["tabla"], index=False)
        escribir(
            destinos["registro"],
            documento_ablacion(
                ablacion,
                modo=modo,
                oracle=oracle,
                dataset_id=dataset_id,
                umbrales=umbrales,
                calibracion=ctx.calibracion,
                casos=casos,
                embedding_space_id=espacio,
            ),
            seed=ctx.configuracion.seed,
            dataset_id=dataset_id,
            dataset_type="synthetic",
            embedding_model=None
            if ablacion == "A2" or provider is None
            else provider.identity.model,
            goldset=GOLDSET.name,
        )
        print(f"  tabla    E18_ablacion_{ablacion}.csv")
        print(f"  registro experiments/E18_ablacion_{ablacion}.json")

    store.dispose()
    return 0
