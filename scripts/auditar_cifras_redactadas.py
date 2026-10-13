"""¿Dicen la verdad las cifras que el redactor escribe?

**Lo que motivó este guion.** Al ejecutar el rediseño de la condición con
distractor apareció una salida así:

    verificador:  "cobertura 0.00 < 0.80"
    redactor:     "cobertura 0.908 < 0.80"

La frase del redactor es internamente falsa: 0,908 no es menor que 0,80. El
número que escribió es la **confianza calibrada**, no la cobertura. Y las tres
barreras del trabajo la dejaron pasar: esquema válido, veredicto respetado, cero
citas inventadas.

**Qué comprueba este guion y qué no.** Extrae los números decimales del campo
``missing_evidence`` que escribe el redactor y los compara con los que escribió
el verificador para el mismo caso. Un número que el redactor dice y el
verificador no es una **cifra alterada**. No juzga la prosa ni el estilo: solo si
las cifras de la justificación son las que el criterio determinista produjo.

**Por qué no es una barrera nueva.** Es una auditoría *a posteriori* sobre
registros ya escritos. Añadir una comprobación al recorrido después de ver estos
resultados sería cambiar el sistema a la vista del resultado; eso queda como
recomendación, no como código en el camino de ejecución.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mecanico_ia_exp.config import paths

#: Pares (registro de suficiencia, registro del agente) que se auditan.
PARES = (
    ("E15_suficiencia.json", "E13_agente_transformers-lora@slm_lora_v2.json"),
    ("E15_suficiencia.json", "E13_agente_transformers.json"),
    ("E15_suficiencia.json", "E13_agente_transformers-lora.json"),
    (
        "E15_suficiencia_distractor_v2.json",
        "E13_agente_transformers-lora@slm_lora_v2_distractor_v2_redaccion.json",
    ),
)

DECIMAL = re.compile(r"\d+\.\d+")


def _cifras(valor: Any) -> set[str]:
    texto = " ".join(valor) if isinstance(valor, list) else str(valor or "")
    # 0.60 y 0.600 son la misma cifra escrita de dos maneras; eso no es alterarla.
    return {str(float(x)) for x in DECIMAL.findall(texto)}


def auditar(suf_nombre: str, ag_nombre: str) -> list[tuple[str, list[str], list[str]]]:
    suf_p, ag_p = paths.EXPERIMENTS / suf_nombre, paths.EXPERIMENTS / ag_nombre
    if not (suf_p.is_file() and ag_p.is_file()):
        return []
    suf = json.loads(suf_p.read_text("utf-8"))
    ag = json.loads(ag_p.read_text("utf-8"))
    por_gold = {c["case_id"]: c for c in suf.get("cases", [])}
    por_ventana = {c["bundle"]["case_id"]: c for c in suf.get("cases", [])}

    alteradas = []
    for run in ag.get("runs", []):
        caso = por_gold.get(run.get("gold_case_id")) or por_ventana.get(run.get("case_id"))
        if caso is None:
            continue
        del_verificador = _cifras(caso["verdict"].get("missing_evidence"))
        del_redactor = _cifras((run.get("output") or {}).get("missing_evidence"))
        extra = del_redactor - del_verificador
        if extra:
            alteradas.append(
                (
                    str(run.get("gold_case_id") or run.get("case_id")),
                    sorted(del_verificador),
                    sorted(del_redactor),
                )
            )
    return alteradas


def main() -> int:
    total = 0
    for suf_nombre, ag_nombre in PARES:
        alteradas = auditar(suf_nombre, ag_nombre)
        n = len((json.loads((paths.EXPERIMENTS / ag_nombre).read_text("utf-8"))).get("runs", []))
        marca = "CIFRAS ALTERADAS" if alteradas else "sin alteraciones"
        print(f"{Path(ag_nombre).stem[:58]:58} {n:3} casos · {marca}")
        for caso, esperadas, dichas in alteradas:
            print(f"    {caso:34} verificador {esperadas} -> redactor {dichas}")
        total += len(alteradas)

    print()
    if total:
        print(
            f"{total} caso(s) con una cifra que el verificador no escribió.\n"
            "Las tres barreras del trabajo —esquema, veredicto, citas— los dejan pasar: "
            "comprueban que el identificador citado existiera, no que el número dicho sea cierto.\n"
            "No se corrige el recorrido: se declara (L-26)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
