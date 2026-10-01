"""Ejecución de E12: evaluación de la recuperación sobre el conjunto anotado.

Compara cuatro estrategias sobre las mismas consultas y la misma verdad de
referencia. La pregunta que responde la puso E11: cuánto aporta el filtrado por
metadata y la jerarquía de autoridad sobre la similitud desnuda.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.evaluation.retrieval import (
    RetrievalMetrics,
    StrategyReport,
    evaluate_case,
)
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.rag.embeddings import EmbeddingProvider, get_provider
from mecanico_ia_exp.rag.manifest import JERARQUIA_EVIDENCIA, DocumentType
from mecanico_ia_exp.rag.store import PgVectorStore, RetrievedChunk, reciprocal_rank_fusion

GOLDSET = paths.CONFIGS / "goldset_mazda3_bk.yaml"
TOP_K = 10

#: Profundidad de recuperación antes de filtrar o reordenar. Se recupera de más y
#: se recorta después: filtrar sobre top-10 dejaría al filtro sin nada que hacer.
PROFUNDIDAD = 60

ESTRATEGIAS = (
    "semantic",
    "semantic+engine",
    "semantic+authority",
    "hybrid",
    "diagnosis-guided",
)

#: Correspondencia entre la condición que predice el modelo especializado y el
#: DTC cuyo procedimiento documenta esa condición. Sale de la calibración
#: (configs/calibracion_mazda3_bk.yaml), donde cada pareja lleva su cita.
#:
#: Una condición sin DTC conocido degrada a la mejor estrategia ciega en lugar
#: de devolver nada.
DIAGNOSTICO_A_DTC: dict[str, tuple[str, ...]] = {
    # Declaración explícita, con lista vacía: **no existe un código de avería para
    # la ausencia de avería**. Es un hecho del dominio, y declararlo aquí es lo que
    # permite a `dtc_requirement` distinguir «esta condición no se documenta con
    # códigos» de «nadie ha declarado sus códigos». Sin esta línea, las dos cosas
    # eran la misma lista vacía. Ver `docs/methodology/politica-puerta-dtc.md`.
    "F00_normal": (),
    # Mazda NO usa los códigos genéricos P0171/P0172 para la mezcla: usa la
    # familia P2177/P2178/P2187/P2188. P2187 es "Fuel system too lean at idle" y
    # su condición de detección vigila los ajustes de combustible en ralentí,
    # que es la firma de una fuga de vacío.
    "F01_vacuum_leak": ("P2187", "P2177"),
    # Una deriva del caudalímetro deja DOS rastros documentales, y hasta E15 solo
    # se buscaba uno. Los códigos del sensor --P0101, P0102-- documentan la
    # tensión de su circuito; los de mezcla --P2177, P2178-- documentan los
    # ajustes de combustible desviados, que es lo que el modelo realmente observa
    # (E9: `maf` no contribuye nada a la detección).
    #
    # Buscar solo los del sensor dejaba las afirmaciones sobre ajustes de
    # combustible sin evidencia que las sostuviera, y la cobertura de ese caso
    # caía a cero. No es ajustar para acertar: es corregir un mapeo que
    # describía mal la condición.
    #
    # P2177/P2178 son "off idle" y P2187/P2188 "at idle". La fuga de vacío es
    # peor en ralentí; la deriva del caudalímetro afecta a todos los regímenes.
    "F02_maf_drift": ("P0101", "P0102", "P2177", "P2178"),
    "F03_thermostat_stuck": ("P0125",),
    "F04_o2_lag": ("P0133",),
    "F05_misfire": ("P0300", "P0301", "P0302", "P0303", "P0304"),
}


def reordenar_por_autoridad(resultados: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
    """Ordena por jerarquía de evidencia y, dentro de cada nivel, por similitud.

    La autoridad manda sobre la puntuación del vector: un procedimiento de taller
    y una descripción de funcionamiento pueden parecerse igual a una consulta y
    no valen lo mismo como evidencia.
    """

    def clave(r: RetrievedChunk) -> tuple[int, int, float]:
        try:
            rango = JERARQUIA_EVIDENCIA[DocumentType(r.document_type or "")]
        except (ValueError, KeyError):
            rango = 99
        # Un fragmento que porta un DTC es más específico que uno que no: la
        # sección «DTC P0133» sostiene un diagnóstico y «HO2S FUNCTION» lo
        # describe. Sin este desempate, la jerarquía por tipo de documento no
        # distingue dentro de un mismo manual.
        con_dtc = 0 if r.dtc_codes else 1
        return (rango, con_dtc, -r.score)

    return [
        RetrievedChunk(**{**r.__dict__, "rank": i + 1})
        for i, r in enumerate(sorted(resultados, key=clave)[:top_k])
    ]


def recuperar(
    estrategia: str,
    *,
    store: PgVectorStore,
    provider: EmbeddingProvider,
    caso: dict[str, Any],
    vehicle_id: str,
    engine_code: str,
    top_k: int = TOP_K,
    exclude_chunks: tuple[str, ...] = (),
    language: str = "en",
    apply_engine_filter: bool = True,
    dtc_map: dict[str, tuple[str, ...]] | None = None,
) -> list[RetrievedChunk]:
    """Ejecuta una estrategia de recuperación sobre un caso.

    El espacio vectorial **no es un parámetro**: se deriva del proveedor que
    vectoriza la consulta. Consulta e índice quedan en el mismo espacio por
    construcción, y no hay nada que un llamante pueda olvidar.

    Antes era un parámetro opcional y ninguno de los tres ejecutores lo pasaba:
    `docs/methodology/politica-espacio-de-embeddings.md`.
    """
    embedding_model = provider.identity.model
    # La consulta en el idioma pedido. El corpus es solo inglés, así que una
    # consulta en español es recuperación translingüe: el caso realista, porque
    # el TFM se escribe en español y el manual del fabricante está en inglés.
    clave = "query" if language == "en" else f"query_{language}"
    consulta = " ".join(str(caso.get(clave) or caso["query"]).split())
    vector = provider.embed_one(consulta)
    # El filtro de motor se puede desactivar a propósito para medir qué hace el
    # verificador cuando un procedimiento de otro motor le llega. Con el filtro
    # puesto nunca llega, lo que es correcto en producción y deja sin probar
    # la última línea de defensa.
    motores: tuple[str, ...] | None = (
        ((engine_code, "ZJ") if engine_code == "Z6" else (engine_code,))
        if apply_engine_filter
        else None
    )

    if estrategia == "semantic":
        return store.search(
            vector,
            vehicle_id=vehicle_id,
            top_k=top_k,
            exclude_chunks=exclude_chunks,
            embedding_model=embedding_model,
        )

    if estrategia == "semantic+engine":
        return store.search(
            vector,
            vehicle_id=vehicle_id,
            top_k=top_k,
            engine_codes=motores,
            exclude_chunks=exclude_chunks,
            embedding_model=embedding_model,
        )

    if estrategia == "semantic+authority":
        amplio = store.search(
            vector,
            vehicle_id=vehicle_id,
            top_k=PROFUNDIDAD,
            engine_codes=motores,
            exclude_chunks=exclude_chunks,
            embedding_model=embedding_model,
        )
        return reordenar_por_autoridad(amplio, top_k)

    if estrategia == "diagnosis-guided":
        # La estrategia que el pipeline realmente puede ejecutar: el modelo
        # especializado ya ha emitido un diagnóstico, y la ficha de esa condición
        # nombra los DTC que la documentan. Se usa esa información --que el
        # sistema posee en ese punto-- para acotar la búsqueda.
        #
        # No es hacer trampa con la respuesta: es la arquitectura que la
        # pregunta de investigación describe, donde el modelo diagnostica y el
        # RAG busca evidencia PARA ese diagnóstico.
        codigos = (dtc_map or DIAGNOSTICO_A_DTC).get(str(caso.get("fault_id", "")))
        if not codigos:
            # Sin DTC conocido para la condición, se degrada a la mejor
            # estrategia ciega en lugar de devolver nada.
            return recuperar(
                "hybrid",
                store=store,
                provider=provider,
                caso=caso,
                vehicle_id=vehicle_id,
                engine_code=engine_code,
                top_k=top_k,
                exclude_chunks=exclude_chunks,
                language=language,
                dtc_map=dtc_map,
                # Se propaga: al degradar se perdía y la condición declarada
                # «sin filtro» corría **con** el filtro puesto. Es el mismo
                # patrón que `MIXED-EMBEDDING-SPACE`, un nivel más abajo.
                apply_engine_filter=apply_engine_filter,
            )
        acotado = store.search(
            vector,
            vehicle_id=vehicle_id,
            top_k=PROFUNDIDAD,
            engine_codes=motores,
            dtc_codes=codigos,
            exclude_chunks=exclude_chunks,
            embedding_model=embedding_model,
        )
        return reordenar_por_autoridad(acotado, top_k)

    if estrategia == "hybrid":
        semantica = store.search(
            vector,
            vehicle_id=vehicle_id,
            top_k=PROFUNDIDAD,
            engine_codes=motores,
            exclude_chunks=exclude_chunks,
            embedding_model=embedding_model,
        )
        lexica = [
            r
            for r in store.search_lexical(
                consulta,
                vehicle_id=vehicle_id,
                top_k=PROFUNDIDAD,
                engine_codes=motores,
                language=language,
            )
            if r.chunk_id not in set(exclude_chunks)
        ]
        fusion = reciprocal_rank_fusion([semantica, lexica], top_k=PROFUNDIDAD)
        return reordenar_por_autoridad(fusion, top_k)

    msg = f"Estrategia desconocida: {estrategia!r}"
    raise ValueError(msg)


#: Los seis casos con que se ejecutó E12 la primera vez, leídos de su propio
#: artefacto. El conjunto anotado creció después a diecisiete: reejecutar sobre
#: los diecisiete cambiaría **dos** variables a la vez --el espacio de embeddings
#: y el conjunto-- y el contraste dejaría de ser atribuible.
#:
#: La ampliación es un experimento **distinto**, con su propio identificador y su
#: propio pre-registro: responde a si el comportamiento se mantiene al ampliar la
#: cobertura, que no es la misma pregunta.
CONJUNTO_E12_ORIGINAL: tuple[str, ...] = (
    "C01_maf_drift",
    "C02_thermostat_stuck",
    "C03_o2_slow_response",
    "C04_misfire",
    "C05_vacuum_leak",
    "C06_vacuum_leak_evidencia_retirada",
)


#: Configuración versionada del mapa de códigos con que se produjo el artefacto
#: original. **No se edita el mapa vigente hasta que coincida**: el mapa actual
#: pertenece al estado posterior del proyecto y se usa en `E12-EXTENDED`. Aquí se
#: carga el congelado, con su huella, para que `RERUN-A` manipule una variable.
MAPA_LEGACY = Path(__file__).resolve().parents[3] / "configs" / "e12_legacy_dtc_map.json"


def cargar_mapa_legacy() -> tuple[dict[str, tuple[str, ...]], str]:
    """Mapa congelado de E12 y su huella, para que ambos vayan al registro."""
    doc = json.loads(MAPA_LEGACY.read_text(encoding="utf-8"))
    return {k: tuple(v) for k, v in doc["map"].items()}, str(doc["map_sha256_16"])


def _huella(texto: str) -> str:
    """Huella del conjunto de casos, para que quede en el registro."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def run_retrieval_evaluation(
    goldset_path: Path = GOLDSET,
    *,
    case_set: tuple[str, ...] = CONJUNTO_E12_ORIGINAL,
    dtc_map: dict[str, tuple[str, ...]] | None = None,
) -> int:
    """Evalúa todas las estrategias y guarda los resultados.

    Por omisión usa el conjunto de seis casos del E12 original. Pasar otro
    conjunto convierte la ejecución en un experimento distinto y debe declararse
    como tal.
    """
    gold = yaml.safe_load(goldset_path.read_text(encoding="utf-8"))
    vehicle_id = gold["vehicle_id"]
    engine_code = gold["engine_code"]
    por_id = {c["case_id"]: c for c in gold["cases"]}
    faltan = [c for c in case_set if c not in por_id]
    if faltan:
        msg = f"casos ausentes del conjunto anotado: {faltan}"
        raise ValueError(msg)
    casos = [por_id[c] for c in case_set]

    # El mapa congelado por omisión: `RERUN-A` reproduce el estado del artefacto.
    mapa, mapa_hash = cargar_mapa_legacy()
    if dtc_map is not None:
        mapa, mapa_hash = dtc_map, _huella(repr(sorted(dtc_map.items())))

    store = PgVectorStore()
    provider = get_provider("multilingual")
    identidad = provider.identity
    espacio = f"{identidad.provider}/{identidad.model}/d{identidad.dimension}/v{identidad.version}"
    recuperado_por_caso: list[dict[str, Any]] = []
    print(f"conjunto anotado: {len(casos)} casos · vehículo {vehicle_id} motor {engine_code}")
    print(f"embeddings: {identidad.model}\n")

    informes: list[StrategyReport] = []
    detalle: list[dict[str, Any]] = []

    for estrategia in ESTRATEGIAS:
        informe = StrategyReport(strategy=estrategia, k=TOP_K)
        for caso in casos:
            resultados = recuperar(
                estrategia,
                store=store,
                provider=provider,
                caso=caso,
                vehicle_id=vehicle_id,
                engine_code=engine_code,
                dtc_map=mapa,
            )
            ficheros = [r.source_file or "" for r in resultados]
            metricas: RetrievalMetrics = evaluate_case(
                case_id=str(caso["case_id"]),
                retrieved_files=ficheros,
                relevant_files=set(caso["relevant_files"] or []),
                supporting_files=set(caso.get("supporting_files") or []),
                distractor_files=set(caso.get("distractor_files") or []),
                k=TOP_K,
            )
            informe.cases.append(metricas)
            store.log_retrieval(
                vehicle_id=vehicle_id,
                query_text=" ".join(str(caso["query"]).split()),
                resultados=resultados,
                identidad=identidad,
                top_k=TOP_K,
                filters={"strategy": estrategia},
                corpus_variant="FULL",
                experiment_id="E12_retrieval",
            )
            # Qué fragmentos estuvieron delante del verificador, en qué orden y
            # en qué espacio. Sin esto, reconstruirlo después exige la tabla de
            # registro de la base, que no está versionada: el criterio de
            # verificación de este experimento no sería comprobable.
            recuperado_por_caso.append(
                {
                    "case_id": str(caso["case_id"]),
                    "retrieval_strategy": estrategia,
                    "embedding_space_id": espacio,
                    "top_k": TOP_K,
                    "filters": {
                        "vehicle_id": vehicle_id,
                        "engine_code": engine_code,
                        "corpus_variant": "FULL",
                    },
                    "results": [
                        {
                            "rank": r.rank,
                            "chunk_id": r.chunk_id,
                            "document_id": r.document_id,
                            "source_file": r.source_file,
                            "score": round(float(r.score), 6),
                            "section": getattr(r, "section", None),
                        }
                        for r in resultados
                    ],
                }
            )
            detalle.append({"strategy": estrategia, **metricas.to_dict()})
        informes.append(informe)

    cabecera = (
        f"{'estrategia':<20}{'P@10':>8}{'R@10':>8}{'MRR':>8}{'Hit':>7}"
        f"{'nDCG':>8}{'distr.':>9}{'distr>rel':>11}"
    )
    print(cabecera)
    print("-" * len(cabecera))
    for informe in informes:
        print(
            f"{informe.strategy:<20}{informe.mean_precision:>8.3f}"
            f"{informe.mean_recall:>8.3f}{informe.mrr:>8.3f}"
            f"{informe.hit_rate:>7.2f}{informe.mean_ndcg:>8.3f}"
            f"{informe.distractors_total:>9d}{informe.distractor_above_relevant:>11d}"
        )

    print("\nposición del primer documento relevante, por caso:")
    print(f"  {'caso':<32}" + "".join(f"{e:>20}" for e in ESTRATEGIAS))
    for i, caso in enumerate(casos):
        fila = f"  {caso['case_id']:<32}"
        for informe in informes:
            rango = informe.cases[i].first_relevant_rank
            fila += f"{(str(rango) if rango else '—'):>20}"
        print(fila)

    tablas = paths.ensure(paths.TABLES)
    import pandas as pd

    pd.DataFrame(detalle).to_csv(tablas / "E12_retrieval_por_caso.csv", index=False)
    pd.DataFrame([i.to_dict() for i in informes]).drop(columns=["cases"]).to_csv(
        tablas / "E12_retrieval_por_estrategia.csv", index=False
    )

    experimentos = paths.ensure(paths.EXPERIMENTS)
    escribir(
        experimentos / "E12_retrieval.json",
        {
            "experiment_id": "E12_retrieval",
            "vehicle_id": vehicle_id,
            "engine_code": engine_code,
            "case_set_id": "E12_ORIGINAL_6" if case_set == CONJUNTO_E12_ORIGINAL else "CUSTOM",
            "case_set": list(case_set),
            "case_set_hash": _huella("|".join(case_set)),
            "dtc_map_id": "E12_LEGACY_DTC_MAP" if dtc_map is None else "CUSTOM",
            "dtc_map_hash": mapa_hash,
            "goldset_hash": _huella(goldset_path.read_text(encoding="utf-8")),
            "top_k": TOP_K,
            "retrieval_depth": PROFUNDIDAD,
            "embedding": identidad.as_dict(),
            "embedding_space_id": espacio,
            "strategies": [i.to_dict() for i in informes],
            "retrieved": recuperado_por_caso,
        },
        goldset=str(goldset_path.name),
        embedding_model=identidad.model,
    )
    print("\ntabla   E12_retrieval_por_caso.csv, E12_retrieval_por_estrategia.csv")
    print("registro experiments/E12_retrieval.json")
    store.dispose()
    return 0
