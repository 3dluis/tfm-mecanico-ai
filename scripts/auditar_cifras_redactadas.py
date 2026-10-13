"""¿Dicen la verdad las cifras que el redactor escribe?

**Lo que motivó este guion.** Al ejecutar el rediseño de la condición con
distractor apareció una salida así:

    verificador:  "cobertura 0.00 < 0.80"
    redactor:     "cobertura 0.908 < 0.80"

La frase del redactor es internamente falsa: 0,908 no es menor que 0,80. El
número que escribió es la **confianza calibrada**, no la cobertura. Y las tres
barreras del trabajo la dejaron pasar: esquema válido, veredicto respetado, cero
citas inventadas.

**Qué audita.** Dos cosas distintas, porque fallan de maneras distintas:

1. **Las abstenciones.** Los números del campo ``missing_evidence`` del redactor
   frente a los que escribió el verificador para el mismo caso. Un número que el
   redactor dice y el verificador no es una **cifra ajena**.
2. **Las afirmaciones de las explicaciones.** Cada afirmación cita una o varias
   observaciones y escribe su valor en prosa. Se comprueba que el número del
   texto sea el de la observación citada, admitiendo cualquier redondeo de cero a
   seis decimales y los dos instantes de la ventana. Lo que no se admite es un
   número que no salga de ahí.

El segundo caso es el grave: las afirmaciones son el núcleo de la trazabilidad, y
una afirmación puede citar el identificador correcto y **corromper los dígitos**
del valor que cita.

**Por qué no es una barrera nueva.** Es una auditoría *a posteriori* sobre
registros ya escritos. La propuesta de corrección del recorrido está en
`docs/methodology/propuesta-validador-numerico.md`, se aplica de forma
prospectiva y se evalúa con un protocolo propio.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from mecanico_ia_exp.config import paths

#: Pares (registro de suficiencia, registro del agente, etiqueta).
PARES = (
    ("E15_suficiencia", "E13_agente_transformers", "modelo base, sin adaptador"),
    ("E15_suficiencia", "E13_agente_transformers-lora", "adaptador v1"),
    ("E15_suficiencia", "E13_agente_transformers-lora@slm_lora_v2", "adaptador v2, el canónico"),
    (
        "E15_suficiencia_distractor_v2",
        "E13_agente_transformers-lora@slm_lora_v2_distractor_v2_redaccion",
        "adaptador v2 sobre los casos de P1",
    ),
)

DECIMAL = re.compile(r"-?\d+\.\d+")


def _cifras(valor: Any) -> set[float]:
    texto = " ".join(valor) if isinstance(valor, list) else str(valor or "")
    return {round(float(x), 6) for x in DECIMAL.findall(texto)}


def _redondeos(valor: float) -> set[float]:
    """Todo redondeo legítimo de un valor, de cero a seis decimales."""
    return {round(valor, k) for k in range(7)}


@dataclass
class Resultado:
    etiqueta: str
    abstenciones: int = 0
    abstenciones_con_cifra_ajena: int = 0
    explicaciones: int = 0
    afirmaciones: int = 0
    afirmaciones_con_cifra_ajena: int = 0
    detalle: list[tuple[str, str, list[float]]] = field(default_factory=list)

    @property
    def total_defectuosas(self) -> int:
        return self.abstenciones_con_cifra_ajena + self.afirmaciones_con_cifra_ajena


def auditar(suficiencia: str, agente: str, etiqueta: str) -> Resultado | None:
    suf_p = paths.EXPERIMENTS / f"{suficiencia}.json"
    ag_p = paths.EXPERIMENTS / f"{agente}.json"
    if not (suf_p.is_file() and ag_p.is_file()):
        return None

    suf = json.loads(suf_p.read_text("utf-8"))
    ag = json.loads(ag_p.read_text("utf-8"))
    por_gold = {c["case_id"]: c for c in suf.get("cases", [])}
    res = Resultado(etiqueta)

    for run in ag.get("runs", []):
        caso = por_gold.get(run.get("gold_case_id"))
        if caso is None:
            continue
        salida = run.get("output") or {}
        identificador = str(run.get("gold_case_id"))

        if salida.get("decision") == "ABSTAIN":
            res.abstenciones += 1
            ajenas = _cifras(salida.get("missing_evidence")) - _cifras(
                caso["verdict"].get("missing_evidence")
            )
            if ajenas:
                res.abstenciones_con_cifra_ajena += 1
                res.detalle.append((identificador, "abstención", sorted(ajenas)))
            continue

        if salida.get("decision") != "EXPLAIN":
            continue

        res.explicaciones += 1
        observaciones = {o["observation_id"]: o for o in caso["bundle"]["observations"]}
        for afirmacion in salida.get("claims", []):
            res.afirmaciones += 1
            permitidas: set[float] = set()
            for oid in afirmacion.get("observational_evidence", []):
                observacion = observaciones.get(oid)
                if observacion is None:
                    continue
                permitidas |= _redondeos(float(observacion["value"]))
                for extremo in ("window_start_s", "window_end_s"):
                    if observacion.get(extremo) is not None:
                        permitidas |= _redondeos(float(observacion[extremo]))
            ajenas = _cifras(afirmacion.get("text")) - permitidas
            if ajenas:
                res.afirmaciones_con_cifra_ajena += 1
                res.detalle.append(
                    (identificador, f"afirmación {afirmacion.get('claim_id')}", sorted(ajenas))
                )
    return res


def main() -> int:
    resultados = [r for p in PARES if (r := auditar(*p)) is not None]

    print("AUDITORÍA DE LAS CIFRAS QUE EL REDACTOR ESCRIBE\n")
    cabecera = f"{'configuración':34} {'abstenciones':>14} {'afirmaciones':>14}"
    print(cabecera)
    print("─" * len(cabecera))
    for r in resultados:
        print(
            f"{r.etiqueta:34} "
            f"{r.abstenciones_con_cifra_ajena:>5} de {r.abstenciones:<6} "
            f"{r.afirmaciones_con_cifra_ajena:>5} de {r.afirmaciones:<6}"
        )

    print("\nDETALLE\n")
    for r in resultados:
        if not r.detalle:
            print(f"  {r.etiqueta}: sin cifras ajenas")
            continue
        print(f"  {r.etiqueta}:")
        for caso, donde, ajenas in r.detalle:
            print(f"    {caso:34} {donde:18} {ajenas}")

    total = sum(r.total_defectuosas for r in resultados)
    print()
    if total:
        print(
            f"{total} salida(s) con al menos una cifra que no sale de los datos que recibió.\n"
            "Las tres barreras —esquema, veredicto, citas— las dejan pasar: comprueban que\n"
            "el identificador citado se entregara, no que el número dicho sea cierto.\n"
            "No se corrige el recorrido sobre lo ya ejecutado: se declara (L-26), y la\n"
            "propuesta está en docs/methodology/propuesta-validador-numerico.md."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
