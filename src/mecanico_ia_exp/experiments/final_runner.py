"""Ejecución de E19, la evaluación final, bajo las reglas congeladas.

El recorrido es el de E15: misma recuperación, mismo ensamblado de evidencia,
mismo verificador. Lo que este módulo añade es todo lo que la congelación exige y
que E15 no necesitaba, porque E15 medía sobre una partición que ya se había
mirado:

1. la partición es un parámetro, y el conjunto de prueba sigue cerrado;
2. la ventana de cada caso se elige con una regla determinista que **no consulta
   al modelo** en el estrato que responde a la pregunta;
3. los casos se generan desde el conjunto elegible congelado;
4. las reglas se **cargan** del manifiesto, no se repiten aquí;
5. la anotación se escribe y se sella **antes** de verificar nada;
6. las huellas de lo congelado se comprueban antes de tocar una partición;
7. los denominadores de las dos tasas se fijan con la anotación, antes de que el
   agente redacte una sola frase;
8. las tasas y la cobertura se calculan después, contra esa anotación;
9. cada tasa viaja con sus ejecuciones, sus ventanas y sus sesiones distintas;
10. cualquier elemento congelado que no pueda verificarse **detiene** la
    ejecución.

Reglas: `docs/methodology/congelacion-anotacion-e19.md`. Estado congelado:
`configs/manifest_e19.json`. Ninguna de las dos cosas se reescribe desde aquí.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd

from mecanico_ia_exp.abstention.sufficiency import (
    Decision,
    EvidenceVerifier,
    SufficiencyThresholds,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import Particion
from mecanico_ia_exp.evaluation.metrics import evaluate_classification
from mecanico_ia_exp.evidence.assembly import assemble
from mecanico_ia_exp.experiments.congelacion import (
    cargar_anclaje,
    cargar_manifiesto,
    casos_elegibles,
    verificar,
)
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.experiments.retrieval_runner import DIAGNOSTICO_A_DTC, recuperar
from mecanico_ia_exp.experiments.sufficiency_runner import (
    DATASET,
    GOLDSET,
    VEHICULO,
    CasoVerificado,
    Contexto,
    atribucion_de,
    confianza_calibrada_de,
    fragmentos_excluidos,
    preparar,
    requisito_dtc,
    validar_politica,
)
from mecanico_ia_exp.models.baseline import train_majority_baseline
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.store import PgVectorStore

#: El estrato que responde a la pregunta. Los otros dos son descriptivos.
ESTRATO_PRIMARIO = "operativo"
ESTRATOS = ("operativo", "comparativo", "adverso")

#: Lo que es cada artefacto, escrito **dentro** del artefacto.
ES_EVALUACION_FINAL = "EVALUACION_FINAL"
ES_ENSAYO = "ENSAYO_DEL_EJECUTOR"

EXPLICA = Decision.EXPLAIN.value
ABSTIENE = Decision.ABSTAIN.value


def condicion_del_artefacto(particion: str) -> dict[str, str]:
    """Qué es este artefacto, dicho dentro de él y no solo en su nombre.

    Un recorrido sobre validación bajo las reglas de E19 sirve para auditar el
    ejecutor antes de abrir nada, pero no es un resultado de la evaluación final.
    El sufijo del nombre lo distingue; esto lo dice también quien lea el JSON sin
    mirar de dónde salió, que es como se leen los registros seis meses después.
    """
    if particion == "test":
        return {
            "status": ES_EVALUACION_FINAL,
            "note": "medicion sobre el conjunto de prueba bajo las reglas congeladas de E19",
        }
    return {
        "status": ES_ENSAYO,
        "note": (
            f"ensayo del ejecutor sobre la particion {particion}: NO es un resultado de "
            "E19 y la memoria no lo cita. Existe para auditar el recorrido antes de "
            "abrir el conjunto de prueba"
        ),
    }


def sufijo_de(particion: str) -> str:
    """Sufijo de los artefactos de una ejecución.

    Solo la evaluación final escribe sin sufijo. Un recorrido de prueba sobre
    validación **no puede** sobrescribir el registro de E19: si pudiera, bastaría
    un ensayo para borrar la única medición que el conjunto de prueba admite.
    """
    return "" if particion == "test" else f"_{particion}"


class AperturaNoDeclaradaError(RuntimeError):
    """Se ha pedido medir sobre prueba sin la declaración formal de apertura."""


class AnotacionIncoherenteError(RuntimeError):
    """Los denominadores de las tasas no son los que la anotación fijó."""


# ---------------------------------------------------------------------------
# Ventanas: selección determinista
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Ventana:
    """Una ventana de la partición, identificada como en el resto del laboratorio."""

    indice: int
    session_id: str
    t_start: float

    @property
    def case_id(self) -> str:
        return f"{self.session_id}@{self.t_start:.0f}s"

    def to_dict(self) -> dict[str, Any]:
        return {"window_id": self.case_id, "session_id": self.session_id, "t_start": self.t_start}


def _ventana(meta: pd.DataFrame, i: int) -> Ventana:
    fila = meta.iloc[i]
    return Ventana(
        indice=int(i), session_id=str(fila["session_id"]), t_start=float(fila["t_start"])
    )


def orden_canonico(meta: pd.DataFrame, indices: Sequence[int]) -> list[int]:
    """Los índices dados, ordenados por `session_id` y después por `t_start`.

    El orden es total --los dos campos identifican la ventana-- y por tanto no
    hay empates que resolver. Es la única fuente de orden de este módulo: elegir
    «la primera» significa siempre la primera aquí.
    """
    claves = [
        (str(meta.iloc[i]["session_id"]), float(meta.iloc[i]["t_start"]), int(i)) for i in indices
    ]
    return [i for _, _, i in sorted(claves)]


def ventanas_operativas(
    meta: pd.DataFrame, y: npt.NDArray[np.str_], fault_id: str
) -> list[Ventana]:
    """Regla primaria: la primera ventana **de la condición** en cada sesión.

    No consulta al modelo, de modo que el canal de oráculo `O-1` queda cerrado:
    se evalúa el sistema sobre ventanas elegidas por su posición, que es lo que
    ocurriría en funcionamiento. Y toma una sola ventana por sesión, de modo que
    entre las elegidas no hay solape: con ventana de 120 s y paso de 60 s, dos
    ventanas consecutivas comparten la mitad de sus muestras.

    «La primera de la condición» y no «la primera de la sesión»: en una sesión con
    avería las primeras ventanas están etiquetadas como funcionamiento normal,
    porque el fallo se inyecta tras un calentamiento, y una ventana sin el fallo no
    puede explicarse con la documentación de ese fallo. La regla congelada lo dice
    así desde la precisión del 1 de octubre de 2026, anterior a toda medición.
    """
    indices = orden_canonico(meta, np.flatnonzero(y == fault_id).tolist())
    vistas: dict[str, Ventana] = {}
    for i in indices:
        ventana = _ventana(meta, i)
        vistas.setdefault(ventana.session_id, ventana)
    return [vistas[s] for s in sorted(vistas)]


def ventana_comparativa(
    meta: pd.DataFrame, y: npt.NDArray[np.str_], aciertos: npt.NDArray[np.bool_], fault_id: str
) -> Ventana | None:
    """Regla de validación: la primera ventana que el modelo clasifica bien.

    Es un canal de oráculo abierto por definición, y por eso este estrato es
    descriptivo: existe para que una diferencia entre prueba y validación no
    confunda el efecto de la partición con el de haber cambiado la regla.
    """
    candidatas = np.flatnonzero((y == fault_id) & aciertos).tolist()
    if not candidatas:
        return None
    return _ventana(meta, orden_canonico(meta, candidatas)[0])


def ventana_adversa(
    meta: pd.DataFrame,
    y: npt.NDArray[np.str_],
    aciertos: npt.NDArray[np.bool_],
    confianzas: npt.NDArray[np.float64],
    fault_id: str,
) -> Ventana | None:
    """Regla `A-1`: entre los errores del modelo, el de mayor confianza.

    Elegir el primero por índice escogía el error menos adverso disponible: el
    que no supera la puerta de confianza y por tanto nunca llega al verificador.
    El desempate es el orden canónico, para que la regla sea determinista también
    cuando dos errores empatan en confianza.
    """
    candidatas = np.flatnonzero((y == fault_id) & ~aciertos).tolist()
    if not candidatas:
        return None
    ordenadas = orden_canonico(meta, candidatas)
    # `min` devuelve el primero de los mínimos en orden de iteración, y la
    # iteración es la canónica: entre errores que empatan en confianza gana el
    # de menor `session_id` y, a igualdad, el de menor `t_start`.
    mejor = min(ordenadas, key=lambda i: -float(confianzas[i]))
    return _ventana(meta, mejor)


# ---------------------------------------------------------------------------
# La decisión esperada, con sus tres únicas entradas
# ---------------------------------------------------------------------------


def decision_esperada(*, label: str, predicted_class: str, corpus_variant: str) -> str:
    """`EXPLAIN` solo si hay evidencia admisible **y** el diagnóstico es correcto.

    Las tres entradas son las únicas que la congelación permite: la etiqueta
    verdadera, la clase predicha por el recorrido evaluado --el argumento máximo
    del bosque sin calibrar-- y la condición de evidencia del caso. Ninguna
    salida del verificador interviene: si la anotación se derivara del veredicto,
    de la cobertura o de las comprobaciones de soporte, se estaría midiendo la
    política contra sí misma.

    La condición de evidencia decide la primera mitad: solo la variante con
    evidencia completa deja en el índice el procedimiento diagnóstico que el
    manual publica para la condición. La segunda mitad es la que hace que el
    estrato adverso espere abstención incluso con evidencia completa: si el
    diagnóstico es incorrecto, no hay evidencia admisible para la afirmación que
    el sistema iba a hacer, por mucho que el manual documente bien otra cosa.
    """
    hay_evidencia_admisible = corpus_variant == "FULL"
    diagnostico_correcto = predicted_class == label
    return EXPLICA if hay_evidencia_admisible and diagnostico_correcto else ABSTIENE


@dataclass(frozen=True)
class CasoFinal:
    """Una ejecución anotada: un caso del conjunto sobre una ventana concreta."""

    gold: Mapping[str, Any]
    estrato: str
    ventana: Ventana
    label: str
    predicted_class: str
    expected_decision: str

    @property
    def case_id_gold(self) -> str:
        return str(self.gold["case_id"])

    @property
    def fault_id(self) -> str:
        return str(self.gold["fault_id"])

    @property
    def corpus_variant(self) -> str:
        return str(self.gold.get("corpus_variant", "FULL"))

    @property
    def ejecucion_id(self) -> str:
        """Identificador único de la ejecución.

        Hace falta porque varias condiciones de evidencia del mismo fallo se
        ejecutan sobre la **misma** ventana --es el experimento central-- y el
        identificador de ventana solo no las distinguiría.
        """
        return f"{self.case_id_gold}@{self.ventana.case_id}"

    @property
    def prediction_correct(self) -> bool:
        return self.predicted_class == self.label

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.ejecucion_id,
            "case_id_gold": self.case_id_gold,
            "stratum": self.estrato,
            "fault_id": self.fault_id,
            "corpus_variant": self.corpus_variant,
            **self.ventana.to_dict(),
            "label": self.label,
            "predicted_class": self.predicted_class,
            "prediction_correct": self.prediction_correct,
            "expected_decision": self.expected_decision,
        }


def casos_del_estrato(
    estrato: str,
    *,
    elegibles: Mapping[str, str],
    casos_gold: Mapping[str, Mapping[str, Any]],
    meta: pd.DataFrame,
    y: npt.NDArray[np.str_],
    predicciones: npt.NDArray[np.str_],
    aciertos: npt.NDArray[np.bool_],
    confianzas: npt.NDArray[np.float64],
) -> tuple[list[CasoFinal], list[dict[str, str]]]:
    """Las ejecuciones de un estrato, y las que no son evaluables.

    Un caso sin ventana del tipo que su estrato pide no se sustituye por otra: se
    declara **no evaluable por ausencia de ventanas**, que es un hecho de la
    partición, y no entra en ningún numerador ni denominador.
    """
    if estrato not in ESTRATOS:
        msg = f"estrato desconocido: {estrato!r}; declarados {ESTRATOS}"
        raise ValueError(msg)

    casos: list[CasoFinal] = []
    no_evaluables: list[dict[str, str]] = []
    for case_id in sorted(elegibles):
        gold = casos_gold[case_id]
        variante = elegibles[case_id]
        fault_id = str(gold["fault_id"])

        if estrato == "adverso" and variante != "FULL":
            continue

        if estrato == "operativo":
            ventanas = ventanas_operativas(meta, y, fault_id)
        elif estrato == "comparativo":
            una = ventana_comparativa(meta, y, aciertos, fault_id)
            ventanas = [una] if una is not None else []
        else:
            una = ventana_adversa(meta, y, aciertos, confianzas, fault_id)
            ventanas = [una] if una is not None else []

        if not ventanas:
            no_evaluables.append(
                {
                    "case_id_gold": case_id,
                    "stratum": estrato,
                    "reason": "no evaluable por ausencia de ventanas del tipo que la regla pide",
                }
            )
            continue

        for ventana in ventanas:
            label = str(y[ventana.indice])
            predicha = str(predicciones[ventana.indice])
            casos.append(
                CasoFinal(
                    gold=gold,
                    estrato=estrato,
                    ventana=ventana,
                    label=label,
                    predicted_class=predicha,
                    expected_decision=decision_esperada(
                        label=label, predicted_class=predicha, corpus_variant=variante
                    ),
                )
            )
    return casos, no_evaluables


# ---------------------------------------------------------------------------
# Recuentos, denominadores y tasas
# ---------------------------------------------------------------------------


def recuento(casos: Sequence[CasoFinal]) -> dict[str, int]:
    """Ejecuciones, ventanas distintas y sesiones distintas.

    Las tres cifras viajan juntas en todo este módulo. Varias ejecuciones pueden
    compartir ventana, y varias ventanas, sesión: una proporción sin estos
    recuentos sugeriría una independencia que el conjunto no tiene.
    """
    return {
        "n_runs": len(casos),
        "n_windows": len({c.ventana.case_id for c in casos}),
        "n_sessions": len({c.ventana.session_id for c in casos}),
    }


def denominadores(casos: Sequence[CasoFinal]) -> dict[str, Any]:
    """Los denominadores de las dos tasas, fijados **antes** de medir nada.

    Cuántas ejecuciones debían explicar y cuántas abstenerse no es una decisión
    que pueda tomarse después de ver las decisiones del sistema. Queda aquí, en
    la anotación, y el ejecutor comprueba al final que las tasas se calcularon
    sobre estos mismos números.
    """
    return {
        "total": recuento(casos),
        "expected_explain": recuento([c for c in casos if c.expected_decision == EXPLICA]),
        "expected_abstain": recuento([c for c in casos if c.expected_decision == ABSTIENE]),
        "full_evidence": recuento([c for c in casos if c.corpus_variant == "FULL"]),
    }


@dataclass(frozen=True)
class Tasa:
    """Un recuento con su denominador, sus ventanas y sus sesiones."""

    numerador: int
    denominador: int
    ventanas: int
    sesiones: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "numerator": self.numerador,
            "denominator": self.denominador,
            "n_independent_windows": self.ventanas,
            "n_independent_sessions": self.sesiones,
            "rate": None if self.denominador == 0 else round(self.numerador / self.denominador, 4),
        }


def _tasa(pares: Sequence[tuple[CasoFinal, str]], decision: str) -> Tasa:
    cuenta = recuento([c for c, _ in pares])
    return Tasa(
        numerador=sum(1 for _, d in pares if d == decision),
        denominador=len(pares),
        ventanas=cuenta["n_windows"],
        sesiones=cuenta["n_sessions"],
    )


def tasas(pares: Sequence[tuple[CasoFinal, str]]) -> dict[str, Any]:
    """Falsa confianza, abstención innecesaria y cobertura, contadas como en M5.

    - falsa confianza: explica / ejecuciones que **debían abstenerse**;
    - abstención innecesaria: se abstiene / ejecuciones que **debían explicar**.

    Las dos no se combinan en una sola cifra: explicar sin soporte entrega al
    mecánico un procedimiento que el manual no respalda, y abstenerse de más le
    devuelve un «no lo sé» que no le sirve pero no le engaña.
    """
    debian_abstenerse = [p for p in pares if p[0].expected_decision == ABSTIENE]
    debian_explicar = [p for p in pares if p[0].expected_decision == EXPLICA]
    evidencia_completa = [p for p in pares if p[0].corpus_variant == "FULL"]
    return {
        "metric_definition": "docs/memoria/cap4_marco_metodologico.md, M5",
        "false_confidence": _tasa(debian_abstenerse, EXPLICA).to_dict(),
        "unnecessary_abstention": _tasa(debian_explicar, ABSTIENE).to_dict(),
        "coverage_full_evidence": _tasa(evidencia_completa, EXPLICA).to_dict(),
    }


def politicas_de_referencia(
    pares: Sequence[tuple[CasoFinal, str]],
    confianzas: Mapping[str, float],
    *,
    min_confidence: float,
) -> dict[str, Any]:
    """Las dos políticas triviales, recalculadas sobre **estas** ejecuciones.

    Sin ellas una tasa no dice nada: abstenerse siempre da falsa confianza cero,
    y explicar cuando el modelo confía es la puerta de confianza sola, que es lo
    que el criterio compuesto tiene que mejorar.
    """
    siempre = [(c, ABSTIENE) for c, _ in pares]
    confia = [
        (c, EXPLICA if confianzas[c.ejecucion_id] >= min_confidence else ABSTIENE) for c, _ in pares
    ]
    return {
        "abstain_always": tasas(siempre),
        "explain_if_model_is_confident": {
            "min_confidence": min_confidence,
            **tasas(confia),
        },
    }


# ---------------------------------------------------------------------------
# El artefacto de anotación, sellado antes de medir
# ---------------------------------------------------------------------------


def documento_anotacion(
    *,
    particion: str,
    dataset_id: str,
    policy: str,
    manifiesto: Mapping[str, Any],
    anclaje: Mapping[str, Any],
    verificacion: Mapping[str, Any],
    casos: Sequence[CasoFinal],
    no_evaluables: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """La anotación completa, con sus denominadores y sus entradas declaradas."""
    por_estrato = {e: [c for c in casos if c.estrato == e] for e in ESTRATOS}
    return {
        "experiment_id": "E19_anotacion",
        **condicion_del_artefacto(particion),
        "partition": particion,
        "dataset_id": dataset_id,
        "verifier_version": policy,
        "frozen_rules": {
            "file": manifiesto["frozen_rules"]["file"],
            "anchor_file": manifiesto["anchor_file"],
            "frozen_at_commit": anclaje["frozen_at_commit"],
            "files": dict(anclaje["files"]),
        },
        "freeze_verification": dict(verificacion),
        "expected_decision_rule": dict(manifiesto["expected_decision"]),
        "primary_stratum": ESTRATO_PRIMARIO,
        "strata": {
            estrato: {
                "answers_pi": estrato == ESTRATO_PRIMARIO,
                "denominators": denominadores(filas),
                "runs": [c.to_dict() for c in filas],
            }
            for estrato, filas in por_estrato.items()
        },
        "non_evaluable": [dict(n) for n in no_evaluables],
    }


def sellar_anotacion(documento: Mapping[str, Any], *, sufijo: str = "") -> tuple[Path, str]:
    """Escribe la anotación y devuelve su ruta y su huella.

    La huella es lo que convierte «la anotación no se ajustó a los resultados» en
    una afirmación comprobable y no en una cuestión de palabra: se calcula aquí,
    antes de que el verificador haya visto un solo caso, y el registro de la
    ejecución la cita.
    """
    destino = paths.ensure(paths.EXPERIMENTS) / f"E19_anotacion{sufijo}.json"
    escribir(
        destino,
        dict(documento),
        seed=20260901,
        dataset_id=str(documento["dataset_id"]),
        dataset_type="synthetic",
        goldset=GOLDSET.name,
    )
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# El recorrido
# ---------------------------------------------------------------------------


def metricas_de_diagnostico(ctx: Contexto, particion: str) -> dict[str, Any]:
    """Diagnóstico y calibración sobre la partición, frente a la clase mayoritaria.

    La referencia es la clase mayoritaria **de esta partición**, no la de
    validación: comparar con la referencia de otra partición mezclaría dos cosas.
    """
    clases = tuple(sorted(set(ctx.entrenamiento.y.tolist())))
    mayoritaria = train_majority_baseline(ctx.entrenamiento.y)
    y = ctx.evaluacion.y

    probabilidades = np.asarray(ctx.modelo.predict_proba(ctx.evaluacion.features), dtype=np.float64)
    orden = [list(ctx.modelo.classes_).index(c) for c in clases]
    predicciones = np.asarray(ctx.modelo.predict(ctx.evaluacion.features), dtype=np.str_)

    informe = evaluate_classification(
        y,
        predicciones,
        partition=particion,
        probabilities=probabilidades[:, orden],
        class_order=clases,
    )
    trivial = evaluate_classification(
        y,
        np.full(y.shape, mayoritaria, dtype=y.dtype),
        partition=particion,
        class_order=clases,
    )
    return {
        "partition": particion,
        "majority_class": mayoritaria,
        "majority_baseline": trivial.to_dict(),
        "forest": informe.to_dict(),
        "calibration": ctx.calibracion,
    }


def ejecutar_caso(
    caso: CasoFinal,
    *,
    ctx: Contexto,
    store: PgVectorStore,
    provider: Any,
    verificador: EvidenceVerifier,
    umbrales: SufficiencyThresholds,
    policy: str,
    llm: str | None,
) -> tuple[CasoVerificado, float]:
    """Un caso de punta a punta, por el mismo camino que E15.

    Los canales de oráculo `O-2` y `O-3` quedan cerrados: la recuperación y el
    requisito de la puerta de códigos se derivan de la **clase predicha**, nunca
    de la etiqueta. En el estrato operativo hay ventanas que el modelo puede
    clasificar mal, y derivar la búsqueda de la etiqueta ocultaría precisamente
    el comportamiento que se quiere medir.
    """
    i = caso.ventana.indice
    atribucion = atribucion_de(ctx, i, caso.ventana.case_id)
    diagnostico = str(atribucion.predicted_class)
    confianza = confianza_calibrada_de(ctx, i, diagnostico)

    recuperados = recuperar(
        "diagnosis-guided",
        store=store,
        provider=provider,
        caso={**dict(caso.gold), "fault_id": diagnostico},
        vehicle_id=VEHICULO,
        engine_code=ctx.perfil.engine_code or "Z6",
        exclude_chunks=fragmentos_excluidos(store, caso.gold),
        apply_engine_filter=bool(caso.gold.get("apply_engine_filter", True)),
    )
    requisito = requisito_dtc(diagnostico, policy)
    bundle, comprobaciones = assemble(
        case_id=caso.ventana.case_id,
        perfil=ctx.perfil,
        atribucion=atribucion,
        recuperados=recuperados,
        calibrated_confidence=confianza,
        accepted_applicability=umbrales.accepted_applicability,
        expected_dtc=DIAGNOSTICO_A_DTC.get(diagnostico, ()),
        dtc_requirement=requisito,
    )
    veredicto = verificador.verify(bundle)

    ejecucion = None
    if llm:
        from mecanico_ia_exp.llm.agent import run_agent
        from mecanico_ia_exp.llm.provider import get_llm

        ejecucion = run_agent(get_llm(llm), bundle, veredicto)
        ejecucion.gold_case_id = caso.case_id_gold

    return (
        CasoVerificado(
            gold=dict(caso.gold),
            case_id=caso.ventana.case_id,
            bundle=bundle,
            verdict=veredicto,
            support_checks=list(comprobaciones),
            diagnosis_used=diagnostico,
            dtc_requirement=requisito.value,
            agente=ejecucion,
        ),
        confianza,
    )


def comparar_con_lo_declarado(
    manifiesto: Mapping[str, Any], casos: Sequence[CasoFinal]
) -> dict[str, Any]:
    """Recuentos observados del estrato primario frente a los declarados.

    Las cifras congeladas --veintidós ejecuciones, diez ventanas, diez sesiones--
    son una expectativa sobre la partición, no una regla del método, y por eso una
    discrepancia **no** detiene la ejecución: podría ser un hecho del conjunto, por
    ejemplo una sesión sin ninguna ventana de su condición. Lo que no puede es
    absorberse en silencio, así que se registra y se avisa.
    """
    declarado = manifiesto["window_selection"]["primary_stratum"]
    observado = recuento(casos)
    esperado = {
        "n_runs": int(declarado["n_runs"]),
        "n_windows": int(declarado["n_windows"]),
        "n_sessions": int(declarado["n_sessions"]),
    }
    return {"declared": esperado, "observed": observado, "matches": esperado == observado}


def comprobar_denominadores(
    anotados: Mapping[str, Any], casos: Sequence[CasoFinal], estrato: str
) -> None:
    """Fallo cerrado: las tasas se calculan sobre los denominadores anotados.

    Si al final de la ejecución los recuentos no son los que la anotación fijó,
    algo cambió entre anotar y medir --un caso perdido, una ventana sustituida--
    y la medición deja de ser interpretable. No se corrige: se detiene.
    """
    esperados = anotados["strata"][estrato]["denominators"]
    obtenidos = denominadores(casos)
    if esperados != obtenidos:
        msg = (
            f"los denominadores del estrato {estrato} no son los anotados.\n"
            f"  anotados:  {json.dumps(esperados, sort_keys=True)}\n"
            f"  obtenidos: {json.dumps(obtenidos, sort_keys=True)}\n"
            "La anotación es el referente contra el que se mide: la ejecución se detiene."
        )
        raise AnotacionIncoherenteError(msg)


def fila_de(caso: CasoFinal, verificado: CasoVerificado) -> dict[str, Any]:
    """Una fila por ejecución, con lo que la congelación manda publicar."""
    v = verificado.verdict
    return {
        **caso.to_dict(),
        "diagnosis_used": verificado.diagnosis_used,
        "dtc_requirement": verificado.dtc_requirement,
        "decision": v.decision.value,
        "correct": v.decision.value == caso.expected_decision,
        "sufficiency": v.sufficiency.value,
        "reasons": "; ".join(r.value for r in v.reasons),
        **{k: val for k, val in v.signals.items() if k != "contradictions"},
    }


def documento_final(
    *,
    particion: str,
    dataset_id: str,
    policy: str,
    umbrales: SufficiencyThresholds,
    anotacion: Mapping[str, Any],
    ruta_anotacion: Path,
    huella_anotacion: str,
    verificacion: Mapping[str, Any],
    diagnostico: Mapping[str, Any],
    cotejo: Mapping[str, Any],
    por_estrato: Mapping[str, list[tuple[CasoFinal, CasoVerificado]]],
    confianzas: Mapping[str, float],
) -> dict[str, Any]:
    """El registro de E19, construido aparte para poder comprobar su forma."""
    bloques: dict[str, Any] = {}
    for estrato, pares in por_estrato.items():
        decisiones = [(c, v.verdict.decision.value) for c, v in pares]
        bloques[estrato] = {
            "answers_pi": estrato == ESTRATO_PRIMARIO,
            "denominators": anotacion["strata"][estrato]["denominators"],
            "rates": tasas(decisiones),
            "reference_policies": politicas_de_referencia(
                decisiones, confianzas, min_confidence=umbrales.min_confidence
            ),
            "cases": [
                {
                    "run_id": c.ejecucion_id,
                    "expected_decision": c.expected_decision,
                    "diagnosis_used": v.diagnosis_used,
                    "dtc_requirement": v.dtc_requirement,
                    "bundle": v.bundle.to_dict(),
                    "verdict": v.verdict.to_dict(),
                    "support_checks": [s.to_dict() for s in v.support_checks],
                }
                for c, v in pares
            ],
        }
    return {
        "experiment_id": "E19_final_evaluation",
        **condicion_del_artefacto(particion),
        "partition": particion,
        "dataset_id": dataset_id,
        "vehicle_id": VEHICULO,
        "verifier_version": policy,
        "thresholds": umbrales.to_dict(),
        "oracle_channels_open": {
            "O1_window_selection_requires_correct_prediction": {
                "operativo": False,
                "comparativo": True,
                "adverso": "invertido",
            },
            "O2_retrieval_scoped_by_annotated_label": False,
            "O3_support_dtc_from_annotated_label": False,
        },
        "annotation": {
            "file": ruta_anotacion.name,
            "sha256_16": huella_anotacion,
            "written_before_any_measurement": True,
        },
        "freeze_verification": dict(verificacion),
        "declared_vs_observed": dict(cotejo),
        "diagnosis": dict(diagnostico),
        "strata": bloques,
        "non_evaluable": anotacion["non_evaluable"],
    }


def run_final_evaluation(
    dataset_id: str = DATASET,
    llm: str | None = None,
    *,
    particion: Particion = "test",
    open_test: bool = False,
    reason: str = "",
    estratos: Sequence[str] = ESTRATOS,
    policy: str | None = None,
) -> int:
    """Ejecuta E19 sobre la partición indicada, bajo las reglas congeladas.

    Con `particion="validation"` se recorre todo el camino sobre una partición ya
    conocida: sirve para comprobar el ejecutor sin abrir nada, y sus artefactos
    llevan sufijo para que no puedan confundirse con los de la evaluación final.

    Con `particion="test"` exige `open_test` y una razón por escrito. La razón es
    la declaración formal de apertura, y el cargador la imprime en la salida de
    la ejecución.
    """
    verificacion = verificar().exigir()
    print(verificacion, "\n")
    anclaje = cargar_anclaje()
    manifiesto = cargar_manifiesto(anclaje)
    policy = validar_politica(policy or str(manifiesto["canonical_policy"]["verifier_version"]))

    if particion == "test" and (not open_test or not reason.strip()):
        msg = (
            "E19 mide sobre el conjunto de prueba, que está cerrado. Hace falta la "
            "declaración formal de apertura: `open_test=True` y una razón por "
            "escrito que quede en la salida de la ejecución. Para probar el "
            "ejecutor sin abrir nada, usa particion='validation'."
        )
        raise AperturaNoDeclaradaError(msg)

    desconocidos = [e for e in estratos if e not in ESTRATOS]
    if desconocidos:
        msg = f"estratos desconocidos: {desconocidos}; declarados {ESTRATOS}"
        raise ValueError(msg)

    import yaml

    gold = yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))
    casos_gold = {str(c["case_id"]): c for c in gold["cases"]}
    elegibles = casos_elegibles(manifiesto)

    ctx = preparar(dataset_id, particion=particion, allow_test=open_test, reason=reason)
    meta = ctx.evaluacion.meta
    predicciones = np.asarray(ctx.modelo.predict(ctx.evaluacion.features), dtype=np.str_)
    confianzas_ventana = np.asarray(
        ctx.calibrado.predict_proba(ctx.evaluacion.features), dtype=np.float64
    ).max(axis=1)

    casos: list[CasoFinal] = []
    no_evaluables: list[dict[str, str]] = []
    for estrato in estratos:
        del_estrato, sin_ventana = casos_del_estrato(
            estrato,
            elegibles=elegibles,
            casos_gold=casos_gold,
            meta=meta,
            y=ctx.evaluacion.y,
            predicciones=predicciones,
            aciertos=ctx.aciertos,
            confianzas=confianzas_ventana,
        )
        casos.extend(del_estrato)
        no_evaluables.extend(sin_ventana)

    sufijo = sufijo_de(particion)
    anotacion = documento_anotacion(
        particion=particion,
        dataset_id=dataset_id,
        policy=policy,
        manifiesto=manifiesto,
        anclaje=anclaje,
        verificacion=verificacion.to_dict(),
        casos=casos,
        no_evaluables=no_evaluables,
    )
    ruta_anotacion, huella_anotacion = sellar_anotacion(anotacion, sufijo=sufijo)
    print(f"anotación sellada en {ruta_anotacion.name}, huella {huella_anotacion}")
    for estrato in estratos:
        cuentas = anotacion["strata"][estrato]["denominators"]
        print(
            f"  {estrato:<12} ejecuciones {cuentas['total']['n_runs']:>3} · "
            f"ventanas {cuentas['total']['n_windows']:>3} · "
            f"sesiones {cuentas['total']['n_sessions']:>3} · "
            f"deben explicar {cuentas['expected_explain']['n_runs']:>3} · "
            f"deben abstenerse {cuentas['expected_abstain']['n_runs']:>3}"
        )
    if no_evaluables:
        print(f"  no evaluables: {len(no_evaluables)}")

    cotejo = comparar_con_lo_declarado(
        manifiesto, [c for c in casos if c.estrato == ESTRATO_PRIMARIO]
    )
    if ESTRATO_PRIMARIO in estratos and not cotejo["matches"]:
        print(
            "\nAVISO: el estrato primario no da los recuentos declarados en el "
            f"manifiesto.\n  declarado: {json.dumps(cotejo['declared'], sort_keys=True)}"
            f"\n  observado: {json.dumps(cotejo['observed'], sort_keys=True)}\n"
            "  No detiene la ejecución --puede ser un hecho de la partición-- pero queda "
            "en el registro y hay que declararlo con las cifras."
        )

    umbrales = SufficiencyThresholds()
    verificador = EvidenceVerifier(umbrales)
    store = PgVectorStore()
    provider = get_provider("multilingual")

    por_estrato: dict[str, list[tuple[CasoFinal, CasoVerificado]]] = {e: [] for e in estratos}
    confianzas: dict[str, float] = {}
    filas: list[dict[str, Any]] = []
    try:
        for caso in casos:
            verificado, confianza = ejecutar_caso(
                caso,
                ctx=ctx,
                store=store,
                provider=provider,
                verificador=verificador,
                umbrales=umbrales,
                policy=policy,
                llm=llm,
            )
            por_estrato[caso.estrato].append((caso, verificado))
            confianzas[caso.ejecucion_id] = confianza
            filas.append(fila_de(caso, verificado))
    finally:
        store.dispose()

    for estrato in estratos:
        comprobar_denominadores(anotacion, [c for c, _ in por_estrato[estrato]], estrato)

    print(f"\n{'ejecución':<52}{'esperado':>10}{'decidido':>10}{'':>3}{'conf':>7}{'cob.':>7}")
    print("-" * 89)
    for fila in filas:
        marca = "OK" if fila["correct"] else "!!"
        print(
            f"{fila['run_id']!s:<52}{fila['expected_decision']:>10}{fila['decision']:>10}"
            f"{marca:>3}{fila['confidence']:>7.3f}{fila['claim_coverage']:>7.2f}"
        )

    diagnostico = metricas_de_diagnostico(ctx, particion)
    print(
        f"\ndiagnóstico sobre {particion}: F1 macro "
        f"{diagnostico['forest']['macro_f1']:.3f} frente a "
        f"{diagnostico['majority_baseline']['macro_f1']:.3f} de la clase mayoritaria"
    )
    for estrato in estratos:
        bloque = tasas([(c, v.verdict.decision.value) for c, v in por_estrato[estrato]])
        marca = "PRIMARIO" if estrato == ESTRATO_PRIMARIO else "descriptivo"
        print(f"\n{estrato} ({marca})")
        for nombre, clave in (
            ("falsa confianza    ", "false_confidence"),
            ("abstención innec.  ", "unnecessary_abstention"),
            ("cobertura completa ", "coverage_full_evidence"),
        ):
            t = bloque[clave]
            tasa = "—" if t["rate"] is None else f"{t['rate']:.4f}"
            print(
                f"  {nombre} {t['numerator']:>3}/{t['denominator']:<3} = {tasa:<8}"
                f"({t['n_independent_windows']} ventanas, "
                f"{t['n_independent_sessions']} sesiones)"
            )

    tablas = paths.ensure(paths.TABLES)
    pd.DataFrame(filas).to_csv(tablas / f"E19_evaluacion_final{sufijo}.csv", index=False)
    destino = paths.ensure(paths.EXPERIMENTS) / f"E19_evaluacion_final{sufijo}.json"
    escribir(
        destino,
        documento_final(
            particion=particion,
            dataset_id=dataset_id,
            policy=policy,
            umbrales=umbrales,
            anotacion=anotacion,
            ruta_anotacion=ruta_anotacion,
            huella_anotacion=huella_anotacion,
            verificacion=verificacion.to_dict(),
            diagnostico=diagnostico,
            cotejo=cotejo,
            por_estrato=por_estrato,
            confianzas=confianzas,
        ),
        seed=ctx.configuracion.seed,
        dataset_id=dataset_id,
        dataset_type="synthetic",
        embedding_model=provider.identity.model,
        model=llm,
        goldset=GOLDSET.name,
    )
    print(f"\nregistro experiments/{destino.name}")
    print(f"tabla    E19_evaluacion_final{sufijo}.csv")
    return 0
