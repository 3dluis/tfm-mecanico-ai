"""Los requisitos `D-1` y `D-2` del rediseño del distractor, antes de ver veredictos.

**Por qué este guion existe aparte del experimento.** La política pre-registrada
de la condición con distractor exige comprobar que el distractor **llega** al
verificador (`D-1`) y que el conjunto recuperado **difiere** del de la condición
parcial (`D-2`) *antes* de mirar ninguna decisión. Si se comprobaran después, el
rediseño se estaría validando con el resultado a la vista, que es justo lo que
invalidó la versión anterior de esta condición.

De modo que aquí **solo se recupera**. No se instancia el verificador, no se monta
ningún paquete de evidencia, no se llama a ningún modelo de lenguaje y no se
escribe ningún artefacto de experimento. Lo único que sale es si los dos
requisitos se cumplen, y el guion devuelve distinto de cero si alguno falla.

`D-3` --plausibilidad semántica-- y `D-4` --la razón de insuficiencia declarada de
antemano-- son requisitos de texto, no de medición: están en el protocolo y en el
propio conjunto anotado, y este guion comprueba que **estén escritos**, no que
sean ciertos; eso lo juzga quien lo lea.
"""

from __future__ import annotations

from typing import Any

import yaml

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.experiments.retrieval_runner import recuperar
from mecanico_ia_exp.rag.embeddings import get_provider
from mecanico_ia_exp.rag.ingest import load_vehicle
from mecanico_ia_exp.rag.store import PgVectorStore

CONJUNTO = paths.CONFIGS / "goldset_mazda3_bk_distractor_v2.yaml"
VEHICULO = "mazda-3-bk-2007"

#: Pares (parcial, distractor) que el mecanismo del protocolo compara.
PARES = (
    ("P01_vacuum_leak_partial_v2", "D01_vacuum_leak_distractor_v2"),
    ("P02_thermostat_partial_v2", "D02_thermostat_distractor_v2"),
    ("P03_o2_partial_v2", "D03_o2_distractor_v2"),
)


def _excluidos(store: PgVectorStore, caso: dict[str, Any]) -> tuple[str, ...]:
    return store.chunks_for_dtc(
        tuple(caso.get("exclude_dtc") or ()), vehicle_id=VEHICULO
    ) + store.chunks_for_files(tuple(caso.get("exclude_files") or ()), vehicle_id=VEHICULO)


def main() -> int:
    casos = {c["case_id"]: c for c in yaml.safe_load(CONJUNTO.read_text("utf-8"))["cases"]}
    perfil = load_vehicle(VEHICULO)
    store = PgVectorStore()
    provider = get_provider("multilingual")
    motor = perfil.engine_code or "Z6"

    print(f"conjunto anotado: {CONJUNTO.name}")
    print(f"espacio vectorial: {provider.identity.model}")
    print(f"motor del vehículo: {motor}\n")

    problemas: list[str] = []

    for id_parcial, id_distractor in PARES:
        parcial, distractor = casos[id_parcial], casos[id_distractor]
        print(f"=== {id_distractor}  frente a  {id_parcial}")

        recuperado: dict[str, list[Any]] = {}
        for etiqueta, caso in (("parcial", parcial), ("distractor", distractor)):
            recuperado[etiqueta] = recuperar(
                "diagnosis-guided",
                store=store,
                provider=provider,
                caso=caso,
                vehicle_id=VEHICULO,
                engine_code=motor,
                exclude_chunks=_excluidos(store, caso),
                apply_engine_filter=bool(caso.get("apply_engine_filter", True)),
            )

        ids = {k: {c.chunk_id for c in v} for k, v in recuperado.items()}
        ficheros = {k: {c.source_file for c in v if c.source_file} for k, v in recuperado.items()}

        # D-1: al menos un fragmento de un fichero distractor llega al verificador.
        declarados = {str(f) for f in (distractor.get("distractor_files") or ())}
        llegan = {f for f in ficheros["distractor"] if f in declarados}
        d1 = bool(llegan)
        print(f"  D-1  ¿llega el distractor? {'SÍ' if d1 else 'NO'}")
        for f in sorted(declarados):
            n = sum(1 for c in recuperado["distractor"] if c.source_file == f)
            print(f"         {f}: {n} fragmento(s)")
        if not d1:
            problemas.append(f"{id_distractor}: D-1 falla, ningún distractor llega")

        # D-2: la diferencia simétrica de identificadores no es vacía.
        dif = ids["parcial"] ^ ids["distractor"]
        d2 = bool(dif)
        print(
            f"  D-2  parcial {len(ids['parcial'])} · distractor {len(ids['distractor'])} · "
            f"diferencia simétrica {len(dif)} -> {'OK' if d2 else 'FALLA'}"
        )
        solo_d = sorted(
            {c.source_file for c in recuperado["distractor"] if c.chunk_id in dif if c.source_file}
        )
        solo_p = sorted(
            {c.source_file for c in recuperado["parcial"] if c.chunk_id in dif if c.source_file}
        )
        print(f"         solo en distractor: {solo_d}")
        print(f"         solo en parcial:    {solo_p}")
        if not d2:
            problemas.append(f"{id_distractor}: D-2 falla, los conjuntos recuperados coinciden")

        # D-3 y D-4: declarados por escrito, antes de medir.
        if not str(distractor.get("justificacion") or "").strip():
            problemas.append(f"{id_distractor}: D-3 sin justificación escrita")
        razon = str(distractor.get("distractor_reason") or "")
        if "alcance" not in razon:
            problemas.append(f"{id_distractor}: D-4 sin razón de insuficiencia declarada")
        print(f"  D-3  justificación escrita: {'sí' if distractor.get('justificacion') else 'NO'}")
        print(f"  D-4  razón declarada: {razon[:60]}…\n")

    if problemas:
        print("NO SE PUEDE EJECUTAR. Requisitos incumplidos:")
        for p in problemas:
            print(f"  · {p}")
        print(
            "\nLa política pre-registrada ya decidió qué hacer en este caso: eliminar la "
            "condición del experimento principal y pasarla a limitación y trabajo futuro."
        )
        return 1

    print("Los cuatro requisitos se cumplen en los tres pares. La ejecución puede seguir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
