"""Ensamblado de la evidencia de un caso, sin modelo de lenguaje.

Las afirmaciones se construyen **de forma determinista** a partir de la evidencia
disponible. El modelo de lenguaje, cuando entre, solo las redactará: no crea
afirmaciones ni decide qué las sostiene.

Esa separación es lo que hace verificable la trazabilidad. Si el LLM generase las
afirmaciones y sus citas a la vez, comprobar que una cita sostiene lo afirmado
exigiría releer todo lo que escribió; construyéndolas aquí, el enlace entre
afirmación y evidencia existe antes de que haya texto.
"""

from __future__ import annotations

from mecanico_ia_exp.evidence.model import (
    Claim,
    DocumentaryEvidence,
    EvidenceBundle,
    Observation,
    SupportStatus,
)
from mecanico_ia_exp.evidence.support import SupportCheck, check_support
from mecanico_ia_exp.rag.store import RetrievedChunk
from mecanico_ia_exp.rag.vehicle import (
    Applicability,
    VehicleApplicabilityValidator,
    VehicleProfile,
)
from mecanico_ia_exp.xai.attribution import CaseAttribution

#: Cuántas señales atribuidas se convierten en observación. Más allá de las
#: principales, la atribución es ruido de fondo y convertirlo en evidencia
#: inflaría artificialmente el recuento.
MAX_OBSERVACIONES = 5


def observations_from_attribution(
    atribucion: CaseAttribution, *, max_observaciones: int = MAX_OBSERVACIONES
) -> list[Observation]:
    """Convierte la atribución en observaciones citables.

    Se descartan las contribuciones neutras: una señal cuya aportación es
    indistinguible de cero no observa nada, y admitirla como evidencia sería
    contar ruido.
    """
    observaciones: list[Observation] = []
    for i, atr in enumerate(atribucion.top(max_observaciones * 2), start=1):
        if atr.direction == "neutral":
            continue
        observaciones.append(
            Observation(
                observation_id=f"OBS{i:03d}",
                signal=atr.signal,
                statistic=atr.statistic,
                value=atr.value,
                direction=atr.direction,
                importance=atr.importance,
                session_id=atribucion.session_id,
                window_start_s=atribucion.window_start_s,
                window_end_s=atribucion.window_end_s,
            )
        )
        if len(observaciones) >= max_observaciones:
            break
    return observaciones


def documentary_from_retrieval(
    resultados: list[RetrievedChunk], perfil: VehicleProfile
) -> list[DocumentaryEvidence]:
    """Convierte los fragmentos recuperados en evidencia documental **con su
    grado de aplicabilidad ya evaluado**.

    La aplicabilidad se calcula aquí y no en el verificador para que viaje con la
    evidencia: un fragmento que llega hasta la explicación debe llevar consigo si
    aplica a este vehículo o no.
    """
    validador = VehicleApplicabilityValidator(perfil)
    salida: list[DocumentaryEvidence] = []
    for r in resultados:
        # El fragmento declara sus motores; lo demás lo hereda del documento, que
        # ya se validó al ingerirlo contra este vehículo.
        declarado = VehicleProfile(
            vehicle_id=r.vehicle_id,
            manufacturer=perfil.manufacturer,
            model=perfil.model,
            model_year=perfil.model_year,
            generation=perfil.generation,
            market=perfil.market,
            transmission=perfil.transmission,
            engine_code=(
                perfil.engine_code
                if perfil.engine_code and perfil.engine_code in r.engine_codes
                else (r.engine_codes[0] if r.engine_codes else None)
            ),
        )
        grado = validador.validate(declarado)
        # Un fragmento sin motor declarado no es incompatible: es información
        # general del vehículo. Se marca COMPATIBLE, no EXACT_MATCH.
        if not r.engine_codes and grado is Applicability.EXACT_MATCH:
            grado = Applicability.COMPATIBLE

        salida.append(
            DocumentaryEvidence(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                vehicle_id=r.vehicle_id,
                text=r.text,
                score=r.score,
                applicability=grado.value,
                authority_level=r.authority_level,
                document_type=r.document_type,
                publisher=r.publisher,
                section=r.section,
                page_start=r.page_start,
                page_end=r.page_end,
                source_url=r.source_url,
                source_file=r.source_file,
                dtc_codes=r.dtc_codes,
                engine_codes=r.engine_codes,
            )
        )
    return salida


def build_claims(
    observaciones: list[Observation],
    documentos: list[DocumentaryEvidence],
    *,
    accepted_applicability: frozenset[str],
    expected_dtc: tuple[str, ...] = (),
    max_claims: int = 3,
) -> tuple[list[Claim], list[SupportCheck]]:
    """Construye afirmaciones y **comprueba que la evidencia citada las sostiene**.

    Enlazar no basta. Una afirmación puede citar un fragmento aplicable, con
    buena puntuación y del vehículo correcto, que no diga nada sobre lo afirmado.
    Por eso cada candidato pasa por ``check_support`` antes de aceptarse como
    cita, y las comprobaciones se devuelven para poder auditarlas.

    Una afirmación se marca ``SUPPORTED`` solo si tiene **ambas** clases de
    evidencia y la documental supera la verificación. Con observación pero sin
    documento que la sostenga queda ``PARTIALLY_SUPPORTED``: describe sin
    interpretar.

    **Invariante que esto impone, y que no es un resultado.** Una afirmación
    recibe cita solo si la comprobación la acepta, y se marca sostenida si y solo
    si tiene cita. La distancia entre «proporción de afirmaciones con cita» y
    «proporción de afirmaciones cuya cita las sostiene» es, por tanto, cero por
    construcción, y no puede tomar otro valor mientras las afirmaciones las
    construya este módulo. Sirve como comprobación de implementación; presentarla
    como hallazgo experimental sería presentar una propiedad del código como una
    propiedad del sistema. Ver ``docs/methodology/metrics.md``.

    El texto es una plantilla neutra que enuncia lo observado **sin afirmar
    causa**. Decir «el ajuste está desplazado» es lo que la observación sostiene;
    decir «hay una fuga» sería atribuir causalidad a una atribución, que E9 dejó
    prohibido.

    **Dos hechos distintos, dos frases distintas.** ``value`` es el valor del
    descriptor en la ventana; ``direction`` es el signo de su contribución a la
    predicción del modelo. La primera versión de esta plantilla los mezclaba: de
    ``direction == "increases"`` deducía «la señal se sitúa por encima de lo
    esperable» y a continuación imprimía un ``value`` que podía ser negativo. Un
    descriptor con valor -1,496 aparecía descrito como situado «por encima», y esa
    afirmación se contabilizaba como sostenida.

    El error no era de redacción sino de tipo: afirmar que una señal está alta
    exige un valor de referencia que el sistema no tiene, mientras que el signo
    SHAP solo dice hacia dónde empuja el descriptor la salida del modelo. Decir lo
    segundo con las palabras de lo primero es exactamente la confusión entre
    atribución y estado del vehículo que `evidence-model.md` prohíbe.
    """
    aplicables = [d for d in documentos if d.applicability in accepted_applicability]
    claims: list[Claim] = []
    comprobaciones: list[SupportCheck] = []

    for i, obs in enumerate(observaciones[:max_claims], start=1):
        # Hecho observacional: el valor medido. Sin juicio sobre si es alto o bajo.
        texto = f"El descriptor {obs.signal} ({obs.statistic}) toma el valor {obs.value:.4g}"
        if obs.window_start_s is not None and obs.window_end_s is not None:
            texto += (
                f" entre los segundos {obs.window_start_s:.0f} y "
                f"{obs.window_end_s:.0f} de la sesión"
            )
        else:
            texto += " en la ventana observada"
        # Hecho sobre el modelo: hacia dónde empuja este descriptor su salida.
        aporte = "al alza" if obs.direction == "increases" else "a la baja"
        texto += (
            f", y es uno de los descriptores que más contribuyen a la predicción "
            f"del modelo, {aporte}."
        )

        claim = Claim(claim_id=f"C{i:02d}", text=texto, observation_ids=(obs.observation_id,))

        sostienen: list[str] = []
        for candidato in aplicables:
            comprobacion = check_support(
                claim, candidato, signal=obs.signal, expected_dtc=expected_dtc
            )
            comprobaciones.append(comprobacion)
            if comprobacion.supports:
                sostienen.append(candidato.chunk_id)
            if len(sostienen) >= 2:
                break

        claim.chunk_ids = tuple(sostienen)
        if sostienen:
            claim.support_status = SupportStatus.SUPPORTED
        else:
            claim.support_status = SupportStatus.PARTIALLY_SUPPORTED
            claim.notes = (
                "ningún fragmento aplicable sostiene esta afirmación: existen "
                "citas posibles, pero ninguna habla de la señal en contenido "
                "diagnóstico"
            )
        claims.append(claim)

    return claims, comprobaciones


def assemble(
    *,
    case_id: str,
    perfil: VehicleProfile,
    atribucion: CaseAttribution,
    recuperados: list[RetrievedChunk],
    calibrated_confidence: float | None = None,
    accepted_applicability: frozenset[str],
    expected_dtc: tuple[str, ...] = (),
) -> tuple[EvidenceBundle, list[SupportCheck]]:
    """Reúne toda la evidencia de un caso y verifica que la sostiene.

    Devuelve también las comprobaciones de soporte: son el rastro de por qué una
    cita se aceptó o se descartó, y sin ellas la decisión no sería auditable.
    """
    observaciones = observations_from_attribution(atribucion)
    documentos = documentary_from_retrieval(recuperados, perfil)
    claims, comprobaciones = build_claims(
        observaciones,
        documentos,
        accepted_applicability=accepted_applicability,
        expected_dtc=expected_dtc,
    )
    bundle = EvidenceBundle(
        case_id=case_id,
        vehicle_id=perfil.vehicle_id,
        predicted_class=atribucion.predicted_class,
        model_confidence=atribucion.confidence,
        calibrated_confidence=calibrated_confidence,
        observations=observaciones,
        documents=documentos,
        claims=claims,
    )
    return bundle, comprobaciones
