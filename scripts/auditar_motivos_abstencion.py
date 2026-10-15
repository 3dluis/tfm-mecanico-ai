"""¿Dice el redactor el motivo que el verificador registró?

**Por qué hace falta, habiendo ya `auditar_cifras_redactadas.py`.** Aquel guion
compara el conjunto de números del campo ``missing_evidence`` del redactor con el
conjunto de números del verificador, **agrupando todos los motivos del caso**. Esa
agrupación tiene un punto ciego: si el redactor cita mal el umbral de la confianza
y escribe 0,80 donde se aplicó 0,79, pero el caso tiene además un motivo de
cobertura cuyo umbral sí es 0,80, el 0,80 aparece en el conjunto del verificador y
la discrepancia no se detecta. Ocurre en `C04_misfire`, en dos estratos.

**Qué hace este guion.** Alinea **motivo con motivo** por su etiqueta —confianza,
cobertura, fragmentos aplicables— y compara los números dentro de cada pareja. Eso
permite clasificar la discrepancia en lugar de solo contarla:

``UMBRAL_ERRONEO``
    el valor medido coincide y el umbral citado no es el que se aplicó.
``VALOR_SIN_ORIGEN``
    el valor escrito no procede del motivo homólogo del verificador.
``MOTIVO_OMITIDO``
    el verificador registró un motivo que el redactor no escribe.
``MOTIVO_SIN_CIFRAS``
    el redactor añade una frase sin números que el verificador no escribió.

**Qué no hace.** No corrige ninguna salida, no reejecuta nada y no cambia ninguna
tasa: `T_FC` y `T_AI` las produce el verificador determinista, que no usa modelo de
lenguaje. Es una lectura más fina de registros ya publicados, y su resultado amplía
la limitación `L-26`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Literal

from mecanico_ia_exp.config import paths

DECIMAL = re.compile(r"-?\d+\.\d+")

#: Etiqueta canónica de cada familia de motivos, por el término que la encabeza.
ETIQUETAS = ("confianza", "cobertura", "fragmentos")

Clase = Literal[
    "UMBRAL_ERRONEO",
    "VALOR_SIN_ORIGEN",
    "MOTIVO_OMITIDO",
    "MOTIVO_SIN_CIFRAS",
]


def _etiqueta(motivo: str) -> str:
    """La familia a la que pertenece un motivo, o su texto si no lleva ninguna."""
    for nombre in ETIQUETAS:
        if nombre in motivo:
            return nombre
    return "sin etiqueta"


def _cifras(motivo: str) -> list[float]:
    return [round(float(x), 6) for x in DECIMAL.findall(motivo)]


@dataclass(frozen=True)
class Discrepancia:
    caso: str
    etiqueta: str
    clase: Clase
    verificador: str
    redactor: str


@dataclass
class Recuento:
    abstenciones: int = 0
    con_discrepancia_numerica: int = 0
    con_discrepancia_de_cualquier_tipo: int = 0
    discrepancias: list[Discrepancia] = field(default_factory=list)


def _comparar(caso: str, del_verificador: list[str], del_redactor: list[str]) -> list[Discrepancia]:
    """Las discrepancias entre los motivos de un caso, alineados por etiqueta."""
    por_etiqueta_v = {_etiqueta(m): m for m in del_verificador}
    por_etiqueta_r = {_etiqueta(m): m for m in del_redactor}
    hallazgos: list[Discrepancia] = []

    for etiqueta, motivo_v in por_etiqueta_v.items():
        motivo_r = por_etiqueta_r.get(etiqueta)
        if motivo_r is None:
            hallazgos.append(Discrepancia(caso, etiqueta, "MOTIVO_OMITIDO", motivo_v, ""))
            continue
        cifras_v, cifras_r = _cifras(motivo_v), _cifras(motivo_r)
        if cifras_v == cifras_r:
            continue
        # El primer número de un motivo es el valor medido; el segundo, el umbral.
        mismo_valor = bool(cifras_v) and bool(cifras_r) and cifras_v[0] == cifras_r[0]
        clase: Clase = "UMBRAL_ERRONEO" if mismo_valor else "VALOR_SIN_ORIGEN"
        hallazgos.append(Discrepancia(caso, etiqueta, clase, motivo_v, motivo_r))

    for etiqueta, motivo_r in por_etiqueta_r.items():
        if etiqueta not in por_etiqueta_v and not _cifras(motivo_r):
            hallazgos.append(Discrepancia(caso, etiqueta, "MOTIVO_SIN_CIFRAS", "", motivo_r))

    return hallazgos


def auditar(nombre: str = "E19_evaluacion_final_v3") -> Recuento:
    archivo = paths.EXPERIMENTS / f"{nombre}.json"
    registro = json.loads(archivo.read_text("utf-8"))
    recuento = Recuento()

    for estrato, contenido in registro.get("strata", {}).items():
        por_ventana = {c["bundle"]["case_id"]: c for c in contenido.get("cases", [])}
        for run in contenido.get("writing", {}).get("runs", []):
            caso = por_ventana.get(run.get("case_id"))
            salida = run.get("output") or {}
            if caso is None or salida.get("decision") != "ABSTAIN":
                continue
            recuento.abstenciones += 1
            hallazgos = _comparar(
                f"{estrato}/{run.get('gold_case_id')}",
                list(caso["verdict"].get("missing_evidence") or []),
                list(salida.get("missing_evidence") or []),
            )
            if not hallazgos:
                continue
            recuento.con_discrepancia_de_cualquier_tipo += 1
            if any(h.clase in ("UMBRAL_ERRONEO", "VALOR_SIN_ORIGEN") for h in hallazgos):
                recuento.con_discrepancia_numerica += 1
            recuento.discrepancias.extend(hallazgos)

    return recuento


def main() -> int:
    recuento = auditar()
    print("MOTIVOS DE ABSTENCIÓN DE LA EVALUACIÓN FINAL, ALINEADOS MOTIVO CON MOTIVO\n")
    numericas = recuento.con_discrepancia_numerica
    cualquiera = recuento.con_discrepancia_de_cualquier_tipo
    print(f"  abstenciones evaluadas                        {recuento.abstenciones}")
    print(f"  con alguna discrepancia numérica              {numericas}")
    print(f"  con discrepancia de cualquier tipo            {cualquiera}")

    por_clase: dict[str, int] = {}
    for h in recuento.discrepancias:
        por_clase[h.clase] = por_clase.get(h.clase, 0) + 1
    print("\nPOR CLASE\n")
    for clase in ("VALOR_SIN_ORIGEN", "UMBRAL_ERRONEO", "MOTIVO_OMITIDO", "MOTIVO_SIN_CIFRAS"):
        print(f"  {clase:<20} {por_clase.get(clase, 0)}")

    print("\nDETALLE DE LAS DISCREPANCIAS NUMÉRICAS\n")
    for h in recuento.discrepancias:
        if h.clase not in ("UMBRAL_ERRONEO", "VALOR_SIN_ORIGEN"):
            continue
        print(f"  {h.caso:<34} {h.clase}")
        print(f"      verificador: {h.verificador}")
        print(f"      redactor   : {h.redactor}")

    print(
        "\nNinguna decisión cambia por esto: la toma el verificador determinista.\n"
        "El defecto está en el motivo escrito. Se declara en L-26."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
