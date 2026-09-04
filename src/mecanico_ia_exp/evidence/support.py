"""Verificación del soporte: ¿el fragmento citado sostiene lo afirmado?

**Citar no es sostener.** Una afirmación puede llevar una referencia que existe,
resuelve y pertenece al vehículo correcto, y aun así no decir nada sobre lo que
se afirma. Es el fallo más difícil de ver a simple vista, porque el texto
resultante parece impecable, y es el que la pregunta de investigación interroga.

La comprobación es **determinista**: no interviene ningún modelo de lenguaje. Se
apoya en que el manual nombra cada señal con un vocabulario acotado, así que
comprobar si un fragmento habla de una señal es una operación decidible.

Lo que esta verificación NO hace: juzgar si el contenido del fragmento implica
lógicamente la afirmación. Eso exigiría una interpretación que este componente no
puede hacer de forma verificable. Se limita a lo comprobable --que el fragmento
trate de la señal, que sea de tipo diagnóstico, que porte el código pertinente--
y deja constancia de sus límites en lugar de fingir que decide más.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.rag.manifest import DocumentType

#: Vocabulario con que el manual nombra cada señal. Sale de leer el corpus, no
#: de suponerlo: son los términos que aparecen en los procedimientos.
TERMINOS_SENAL: dict[str, tuple[str, ...]] = {
    "stft_bank1": ("short term fuel trim", "stft", "short-term fuel trim", "fuel trim"),
    "ltft_bank1": ("long term fuel trim", "ltft", "long-term fuel trim", "fuel trim"),
    "maf": ("maf", "mass air flow", "mass airflow", "air flow sensor"),
    "map": (
        "map sensor",
        "manifold absolute pressure",
        "intake manifold pressure",
        "manifold pressure",
    ),
    "coolant_temperature": ("coolant temperature", "ect", "engine coolant"),
    "intake_air_temperature": ("intake air temperature", "iat"),
    "oxygen_sensor": ("ho2s", "oxygen sensor", "o2 sensor", "heated oxygen"),
    "rpm": ("engine speed", "rpm", "revolution"),
    "vehicle_speed": ("vehicle speed", "vss", "speed sensor"),
    "engine_load": ("engine load", "calculated load", "load value"),
    "throttle_position": ("throttle position", "tp sensor", "throttle valve"),
    "ignition_timing": ("ignition timing", "spark advance", "timing advance"),
}

#: Estado de la correspondencia entre el identificador de una señal y el
#: vocabulario del manual. Se declara explícitamente porque **no saber traducir
#: una señal no es lo mismo que no encontrar evidencia sobre ella**, y sin esta
#: distinción las dos cosas producían la misma salida: ninguna cita.
MAPEADA = "MAPPED"
SIN_CORRESPONDENCIA = "SIGNAL_MAPPING_UNAVAILABLE"


def signal_mapping(senal: str) -> str:
    """¿Sabe el verificador con qué palabras nombra el manual esta señal?

    `TERMINOS_SENAL` está construido a mano leyendo el corpus, y cubre las doce
    señales del conjunto experimental. Para cualquier otra, el verificador no
    tiene vocabulario: puede intentar una coincidencia literal del identificador,
    pero un fallo de esa coincidencia **no es prueba de que el manual calle sobre
    la señal**, sino de que el instrumento no sabe buscarla.

    Devuelve `SIGNAL_MAPPING_UNAVAILABLE` en ese caso, y el llamante decide. Es
    una limitación declarada del instrumento, no un defecto oculto: ampliar el
    diccionario automáticamente introduciría una variable experimental nueva.
    """
    return MAPEADA if all(p in TERMINOS_SENAL for p in senal.split("+")) else SIN_CORRESPONDENCIA


#: Tipos de documento que pueden sostener un diagnóstico. Una descripción de
#: funcionamiento explica cómo trabaja un componente; no sostiene que esté
#: averiado.
TIPOS_DIAGNOSTICOS: frozenset[str] = frozenset(
    {
        DocumentType.REPAIR_MANUAL.value,
        DocumentType.WORKSHOP_MANUAL.value,
        DocumentType.DIAGNOSTIC_MANUAL.value,
        DocumentType.DTC_DOCUMENTATION.value,
        DocumentType.TECHNICAL_SERVICE_BULLETIN.value,
    }
)

#: Secciones del manual que son procedimiento diagnóstico y no descripción.
_PATRON_DIAGNOSTICO = re.compile(
    r"\b(DTC\s+[PBCU]\d|DETECTION CONDITION|DIAGNOSTIC PROCEDURE|"
    r"Diagnostic procedure|INSPECTION|TROUBLESHOOTING|POSSIBLE CAUSE)\b"
)

# --------------------------------------------------------------------------
# Papel del fragmento (política v2, `docs/methodology/politica-suficiencia-v2.md`)
#
# La unidad de decisión era el documento y tiene que ser el fragmento: todo el
# corpus es un manual de taller, así que el tipo de documento no discrimina, y
# llevar un código de avería no prueba que el fragmento diagnostique --las tablas
# llevan decenas--. Ninguno de los rasgos de abajo nombra una señal, un código ni
# una condición de fallo: se aplican igual a un fragmento sobre frenos.


class ChunkRole(StrEnum):
    """Qué hace el fragmento, no de qué fichero viene."""

    PROCEDURAL_DIAGNOSTIC_EVIDENCE = "PROCEDURAL_DIAGNOSTIC_EVIDENCE"
    """Pasos de inspección y criterios de decisión: dice cómo se comprueba."""

    SUPPORTING_DIAGNOSTIC_REFERENCE = "SUPPORTING_DIAGNOSTIC_REFERENCE"
    """Lógica de detección o especificaciones: dice qué vigila la centralita."""

    CODE_DEFINITION_OR_TABLE = "CODE_DEFINITION_OR_TABLE"
    """Enumera códigos. Dice que existen, no cómo se diagnostican."""

    UNCLASSIFIED = "UNCLASSIFIED"
    """No encaja. Se trata como incapaz de sostener: la ausencia de prueba no es
    prueba."""


#: Acciones que solo aparecen en un procedimiento: alguien tiene que hacer algo.
_PASOS_INSPECCION = re.compile(
    r"\b(inspect|measure|disconnect|reconnect|remove|install|replace|repair|"
    r"turn the ignition|connect the|check for|verify)\b",
    re.IGNORECASE,
)

#: Marcas de decisión: el procedimiento bifurca según lo observado.
_CRITERIOS_DECISION = re.compile(
    r"(\bgo to the next step\b|\bgo to step\b|\bIs the\b.{0,80}\?|\bAre the\b.{0,80}\?|"
    r"^\s*(yes|no)\b|\bspecification\b|\bstandard value\b)",
    re.IGNORECASE | re.MULTILINE,
)

#: Marcas de lógica de detección: describe qué vigila el sistema, sin decir cómo
#: se comprueba desde fuera.
_LOGICA_DETECCION = re.compile(
    r"(\bthe PCM (monitors|determines|detects)\b|\bdetection condition\b|"
    r"\bmonitoring condition\b)",
    re.IGNORECASE,
)

#: Encabezados que anuncian un listado.
_ENCABEZADO_TABLA = re.compile(
    r"(\bDTC TABLE\b|\bSELF\s*-?\s*TEST\b|\bDETECTION LOGIC AND CONDITIONS\b|"
    r"\bLIST\b|\bINDEX\b)",
    re.IGNORECASE,
)

#: Encabezado de procedimiento: nombra un único código como asunto. Es el título
#: con que el manual encabeza cada procedimiento diagnóstico: 272 secciones así,
#: con 921 fragmentos, en el corpus del vehículo.
_ENCABEZADO_PROCEDIMIENTO = re.compile(r"^\s*DTC\s+[PBCU]\d{4}\b", re.IGNORECASE)

#: Encabezado de listado, a nivel de sección (v2.1). Se define aparte de
#: `_ENCABEZADO_TABLA`, que sigue sirviendo a la clasificación por fragmento de v2
#: sin cambios: aquel patrón mezclaba listados con lógica de detección, y la regla
#: documentada para v2.1 las separa, porque una tabla y una condición de detección
#: son cosas distintas del manual. Ninguna de las dos sostiene, así que la
#: separación no cambia ninguna decisión: cambia el papel que se registra.
_SECCION_TABLA = re.compile(
    r"(\bDTC TABLE\b|\bSELF\s*-?\s*TEST\b|\bLIST\b|\bINDEX\b)", re.IGNORECASE
)

#: Encabezado de material de referencia: habla del código con contenido técnico
#: pero no dice cómo se comprueba nada desde fuera.
_ENCABEZADO_REFERENCIA = re.compile(
    r"(DETECTION LOGIC|DETECTION CONDITIONS?|TEST MODE|SPECIFICATIONS?|"
    r"\bFUNCTION\b|DESCRIPTION|MONITORING)",
    re.IGNORECASE,
)

#: A partir de cuántos códigos distintos un fragmento se comporta como listado.
#: En este manual un procedimiento trata uno, a veces una familia pequeña; de
#: 6 105 fragmentos, 657 portan uno y 71 portan dos, y la cola llega a más de
#: cuarenta. **Nunca decide solo**: siempre se combina con las marcas de arriba.
MAX_CODIGOS_PROCEDIMIENTO = 3


def classify_section(section: str | None) -> ChunkRole | None:
    """Papel declarado por el encabezado de sección (política v2.1).

    La sección es la unidad semántica del manual: un procedimiento diagnóstico es
    una sección titulada por el código que diagnostica, y el troceado la parte en
    varios fragmentos. Clasificar cada fragmento en aislamiento hacía que las
    partes de un mismo procedimiento recibieran papeles distintos, que es medir
    una decisión del sistema de recuperación como si fuera una propiedad del
    documento.

    Devuelve ``None`` cuando el encabezado no declara nada; entonces decide la
    clasificación por rasgos del fragmento, que es la de v2.
    """
    if not section:
        return None
    if _ENCABEZADO_PROCEDIMIENTO.search(section):
        return ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
    if _SECCION_TABLA.search(section):
        return ChunkRole.CODE_DEFINITION_OR_TABLE
    if _ENCABEZADO_REFERENCIA.search(section):
        return ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE
    return None


def classify_chunk(evidencia: DocumentaryEvidence) -> ChunkRole:
    """Clasifica el fragmento por lo que hace.

    Dos pasos: primero el encabezado de sección, que es la taxonomía del propio
    manual; si no declara nada, los rasgos del fragmento. Todas las reglas son
    generales: ninguna menciona una señal, un código ni un fallo concretos.
    """
    por_seccion = classify_section(evidencia.section)
    if por_seccion is not None:
        return por_seccion

    encabezado = evidencia.section or ""
    cuerpo = f"{encabezado}\n{evidencia.text}"
    n_dtc = len(set(evidencia.dtc_codes))
    es_listado = n_dtc >= MAX_CODIGOS_PROCEDIMIENTO or bool(_ENCABEZADO_TABLA.search(encabezado))
    encabeza_procedimiento = bool(_ENCABEZADO_PROCEDIMIENTO.search(encabezado))

    tiene_pasos = bool(_PASOS_INSPECCION.search(cuerpo))
    tiene_decision = bool(_CRITERIOS_DECISION.search(cuerpo))
    if tiene_pasos and tiene_decision and (not es_listado or encabeza_procedimiento):
        return ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
    if _LOGICA_DETECCION.search(cuerpo):
        return ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE
    if es_listado:
        return ChunkRole.CODE_DEFINITION_OR_TABLE
    return ChunkRole.UNCLASSIFIED


#: Papeles que pueden sostener una afirmación por sí solos. Solo uno.
PAPELES_QUE_SOSTIENEN: frozenset[str] = frozenset({ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE.value})


def role_priority(evidencia: DocumentaryEvidence) -> int:
    """Orden de examen: por papel antes que por puntuación de recuperación.

    En v1 los candidatos se examinaban por puntuación y el bucle se detenía tras
    aceptar dos: una tabla bien puntuada podía ocupar las dos plazas y el
    procedimiento correcto no llegaba a examinarse. Eso era un artefacto de la
    implementación, no una decisión de diseño.
    """
    orden = {
        ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE: 0,
        ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE: 1,
        ChunkRole.CODE_DEFINITION_OR_TABLE: 2,
        ChunkRole.UNCLASSIFIED: 3,
    }
    return orden[classify_chunk(evidencia)]


@dataclass(frozen=True)
class SupportCheck:
    """Resultado de comprobar si un fragmento sostiene una afirmación."""

    claim_id: str
    chunk_id: str
    mentions_signal: bool
    is_diagnostic: bool
    carries_expected_dtc: bool | None
    """``None`` cuando la condición no tiene DTC esperado que comprobar."""

    supports: bool
    reason: str
    chunk_role: str = ChunkRole.UNCLASSIFIED.value
    #: `MAPPED` o `SIGNAL_MAPPING_UNAVAILABLE`. Distingue «no hay evidencia» de
    #: «el verificador no sabe traducir esta señal al vocabulario del manual».
    signal_mapping: str = MAPEADA
    """Papel del fragmento. Solo el procedimiento sostiene por sí solo."""

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "chunk_id": self.chunk_id,
            "mentions_signal": self.mentions_signal,
            "is_diagnostic": self.is_diagnostic,
            "carries_expected_dtc": self.carries_expected_dtc,
            "chunk_role": self.chunk_role,
            "signal_mapping": self.signal_mapping,
            "supports": self.supports,
            "reason": self.reason,
        }


def mentions_signal(texto: str, senal: str) -> bool:
    """¿El fragmento habla de esta señal?

    La señal puede llegar como pareja de correlación --``rpm+maf``--, en cuyo
    caso basta con que el fragmento mencione cualquiera de las dos.
    """
    minuscula = texto.lower()
    for parte in senal.split("+"):
        for termino in TERMINOS_SENAL.get(parte, (parte.replace("_", " "),)):
            if termino in minuscula:
                return True
    return False


def is_diagnostic_content(evidencia: DocumentaryEvidence) -> bool:
    """¿Es contenido diagnóstico y no una descripción de funcionamiento?

    E12 lo midió: para una consulta sobre síntomas de la sonda, la recuperación
    devuelve arriba «HEATED OXYGEN SENSOR (HO2S) FUNCTION». Ese documento explica
    cómo funciona el sensor y no sostiene que esté averiado.
    """
    if evidencia.document_type not in TIPOS_DIAGNOSTICOS:
        return False
    if evidencia.dtc_codes:
        return True
    contexto = f"{evidencia.section or ''} {evidencia.text[:600]}"
    return bool(_PATRON_DIAGNOSTICO.search(contexto))


def check_support(
    claim: Claim,
    evidencia: DocumentaryEvidence,
    *,
    signal: str,
    expected_dtc: tuple[str, ...] = (),
) -> SupportCheck:
    """Comprueba si un fragmento concreto sostiene una afirmación concreta.

    Cuatro condiciones, todas necesarias: que el fragmento **mencione la señal**,
    que sea **contenido diagnóstico**, que **porte el código esperado** y que su
    **papel** sea el de procedimiento.

    La cuarta es la que añade la política v2. Sin ella, una tabla que enumera
    códigos y nombra la señal pasaba las tres primeras y sostenía una afirmación
    que no sostiene: `docs/experiments/hallazgo-lexical-support-confound.md`.
    """
    correspondencia = signal_mapping(signal)
    menciona = mentions_signal(evidencia.text, signal)
    diagnostico = is_diagnostic_content(evidencia)
    papel = classify_chunk(evidencia).value
    lleva_dtc: bool | None = None
    if expected_dtc:
        lleva_dtc = bool(set(evidencia.dtc_codes) & set(expected_dtc))

    def resultado(sostiene: bool, motivo: str) -> SupportCheck:
        return SupportCheck(
            claim.claim_id,
            evidencia.chunk_id,
            menciona,
            diagnostico,
            lleva_dtc,
            sostiene,
            motivo,
            papel,
            correspondencia,
        )

    if correspondencia == SIN_CORRESPONDENCIA:
        # No se degrada a «no menciona la señal». El verificador no sabe con qué
        # palabras buscar, y decirlo es distinto de decir que no hay nada.
        return resultado(
            False,
            f"{SIN_CORRESPONDENCIA}: el verificador no tiene vocabulario del manual "
            f"para la señal {signal}; la ausencia de cita no es prueba de ausencia "
            "de evidencia",
        )
    if not menciona:
        return resultado(False, f"el fragmento no menciona la señal {signal}")
    if not diagnostico:
        return resultado(
            False, "el fragmento describe el componente pero no es contenido diagnóstico"
        )
    if lleva_dtc is False:
        return resultado(
            False, f"el fragmento no porta ninguno de los códigos esperados {list(expected_dtc)}"
        )
    if papel not in PAPELES_QUE_SOSTIENEN:
        return resultado(
            False,
            f"el fragmento porta el código y nombra la señal, pero su papel es {papel}: "
            "no es un procedimiento diagnóstico y no sostiene por sí solo",
        )
    return resultado(
        True, "procedimiento diagnóstico del vehículo que menciona la señal y porta el código"
    )
