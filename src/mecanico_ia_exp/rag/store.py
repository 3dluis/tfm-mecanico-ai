"""Almacén vectorial sobre PostgreSQL con pgvector.

**El vehículo es un parámetro obligatorio de la búsqueda, no un filtro
opcional.** No existe forma de llamar a ``search`` sin decir de qué vehículo se
busca evidencia. Es deliberado: un filtro que se puede omitir se omite, y
entonces documentación de otro coche aparece como evidencia por parecerse.

Cada recuperación queda registrada con su consulta, sus parámetros y lo que
devolvió. Sin ese registro, «el sistema recuperó este fragmento» no es
comprobable después, y la trazabilidad que la pregunta de investigación exige se
quedaría en una afirmación.
"""

from __future__ import annotations

import hashlib
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

import numpy as np
import numpy.typing as npt
import sqlalchemy as sa

from mecanico_ia_exp.config.settings import get_settings
from mecanico_ia_exp.rag.chunking import Chunk
from mecanico_ia_exp.rag.embeddings import EmbeddingIdentity
from mecanico_ia_exp.rag.manifest import DocumentEntry
from mecanico_ia_exp.rag.vehicle import VehicleProfile

ESQUEMA = "rag"

#: Configuración de búsqueda de texto completo por idioma. Buscar texto español
#: con la configuración inglesa lematiza mal --no reconoce «ralentí» ni
#: «combustible» como raíces-- y la búsqueda léxica pierde justo lo que aporta.
CONFIG_FTS: dict[str, str] = {"en": "english", "es": "spanish"}


@dataclass(frozen=True)
class RetrievedChunk:
    """Un fragmento recuperado, con todo lo necesario para citarlo."""

    chunk_id: str
    document_id: str
    vehicle_id: str
    text: str
    score: float
    rank: int
    chapter: str | None
    section: str | None
    page_start: int | None
    page_end: int | None
    dtc_codes: tuple[str, ...]
    vehicle_system: str | None
    engine_codes: tuple[str, ...]
    source_file: str | None
    language: str = "en"
    document_title: str | None = None
    publisher: str | None = None
    source_url: str | None = None
    authority_level: str | None = None
    document_type: str | None = None

    def provenance(self) -> str:
        """Cita completa. Nunca «según el manual» sin decir cuál."""
        partes: list[str] = []
        if self.publisher:
            partes.append(self.publisher)
        if self.document_title:
            partes.append(self.document_title)
        if self.section:
            partes.append(f"sección «{self.section}»")
        if self.page_start is not None:
            partes.append(
                f"página {self.page_start}"
                if self.page_start == self.page_end
                else f"páginas {self.page_start}-{self.page_end}"
            )
        partes.append(f"fragmento {self.chunk_id}")
        if self.source_url:
            partes.append(self.source_url)
        return " · ".join(partes)


class VectorStore(ABC):
    """Contrato del almacén. La lógica científica no depende de la implementación."""

    @abstractmethod
    def search(
        self,
        query_vector: npt.NDArray[np.float32],
        *,
        vehicle_id: str,
        top_k: int = 10,
        document_types: tuple[str, ...] | None = None,
        engine_codes: tuple[str, ...] | None = None,
        dtc_codes: tuple[str, ...] | None = None,
        exclude_documents: tuple[str, ...] = (),
        exclude_chunks: tuple[str, ...] = (),
        embedding_model: str,
    ) -> list[RetrievedChunk]:
        """Busca fragmentos **del vehículo indicado**.

        ``exclude_documents`` y ``exclude_chunks`` construyen las variantes del
        corpus del experimento central: retirar evidencia es una operación
        explícita y auditable, nunca un efecto lateral.
        """


class PgVectorStore(VectorStore):
    """Implementación sobre PostgreSQL + pgvector."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().database.url
        self._engine = sa.create_engine(self._url, future=True)

    def dispose(self) -> None:
        self._engine.dispose()

    # ------------------------------------------------------------- registro

    def register_vehicle(self, perfil: VehicleProfile) -> None:
        with self._engine.begin() as cx:
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.vehicle (
                        vehicle_id, manufacturer, model, model_year, generation,
                        market, engine_code, engine_displacement, fuel_type,
                        transmission, obd_protocol, notes)
                    VALUES (:vehicle_id, :manufacturer, :model, :model_year, :generation,
                            :market, :engine_code, :engine_displacement, :fuel_type,
                            :transmission, :obd_protocol, :notes)
                    ON CONFLICT (vehicle_id) DO UPDATE SET
                        manufacturer = EXCLUDED.manufacturer,
                        model = EXCLUDED.model,
                        model_year = EXCLUDED.model_year,
                        generation = EXCLUDED.generation,
                        market = EXCLUDED.market,
                        engine_code = EXCLUDED.engine_code,
                        engine_displacement = EXCLUDED.engine_displacement,
                        fuel_type = EXCLUDED.fuel_type,
                        transmission = EXCLUDED.transmission,
                        obd_protocol = EXCLUDED.obd_protocol,
                        notes = EXCLUDED.notes
                """),
                {
                    "vehicle_id": perfil.vehicle_id,
                    "manufacturer": perfil.manufacturer,
                    "model": perfil.model,
                    "model_year": perfil.model_year,
                    "generation": perfil.generation,
                    "market": perfil.market,
                    "engine_code": perfil.engine_code,
                    "engine_displacement": perfil.engine_displacement,
                    "fuel_type": perfil.fuel_type,
                    "transmission": perfil.transmission,
                    "obd_protocol": perfil.obd_protocol,
                    "notes": perfil.notes,
                },
            )

    def register_document(self, entrada: DocumentEntry) -> None:
        with self._engine.begin() as cx:
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.document (
                        document_id, vehicle_id, document_type, title, publisher,
                        acquisition_source, acquisition_channel, source_url,
                        authority_level, access_type, language, model_year_start,
                        model_year_end, engine_codes, market, redistributable,
                        verified, verification_notes, active)
                    VALUES (:document_id, :vehicle_id, :document_type, :title, :publisher,
                            :acquisition_source, :acquisition_channel, :source_url,
                            :authority_level, :access_type, :language, :model_year_start,
                            :model_year_end, :engine_codes, :market, :redistributable,
                            :verified, :verification_notes, :active)
                    ON CONFLICT (document_id) DO UPDATE SET
                        verified = EXCLUDED.verified,
                        verification_notes = EXCLUDED.verification_notes,
                        active = EXCLUDED.active
                """),
                {
                    "document_id": entrada.document_id,
                    "vehicle_id": entrada.vehicle_id,
                    "document_type": entrada.document_type.value,
                    "title": entrada.title,
                    "publisher": entrada.publisher,
                    "acquisition_source": entrada.acquisition_source,
                    "acquisition_channel": (
                        entrada.acquisition_channel.value if entrada.acquisition_channel else None
                    ),
                    "source_url": entrada.source_url,
                    "authority_level": entrada.authority_level.value,
                    "access_type": entrada.access_type.value,
                    "language": entrada.language,
                    "model_year_start": entrada.model_year_start,
                    "model_year_end": entrada.model_year_end,
                    "engine_codes": list(entrada.engine_codes),
                    "market": entrada.market,
                    "redistributable": entrada.redistributable,
                    "verified": entrada.verified,
                    "verification_notes": entrada.verification_notes,
                    "active": entrada.active,
                },
            )

    def register_version(
        self,
        *,
        version_id: str,
        document_id: str,
        sha256: str,
        revision: str | None = None,
        file_size: int | None = None,
        local_file: str | None = None,
    ) -> str:
        """Registra una versión documental. Si la huella ya existe, la reutiliza.

        Nunca se sobrescribe una versión anterior: un experimento ejecutado
        contra ella debe seguir siendo reconstruible.
        """
        with self._engine.begin() as cx:
            existente = cx.execute(
                sa.text(
                    f"SELECT version_id FROM {ESQUEMA}.document_version "
                    "WHERE document_id = :d AND sha256 = :s"
                ),
                {"d": document_id, "s": sha256},
            ).scalar_one_or_none()
            if existente:
                return str(existente)
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.document_version (
                        version_id, document_id, sha256, retrieved_at, revision,
                        file_size, local_file, active)
                    VALUES (:v, :d, :s, :t, :r, :f, :l, true)
                """),
                {
                    "v": version_id,
                    "d": document_id,
                    "s": sha256,
                    "t": datetime.now(UTC),
                    "r": revision,
                    "f": file_size,
                    "l": local_file,
                },
            )
        return version_id

    def store_chunks(self, fragmentos: list[Chunk]) -> int:
        if not fragmentos:
            return 0
        filas = [
            {
                "chunk_id": c.chunk_id,
                "version_id": c.version_id,
                "document_id": c.document_id,
                "vehicle_id": c.vehicle_id,
                "ordinal": c.ordinal,
                "text": c.text,
                "content_hash": c.content_hash,
                "chapter": c.chapter,
                "section": c.section,
                "subsection": c.subsection,
                "page_start": c.page_start,
                "page_end": c.page_end,
                "dtc_codes": list(c.dtc_codes),
                "vehicle_system": c.vehicle_system.value,
                "system_classification": c.system_classification.value,
                "engine_codes": list(c.engine_codes),
                "source_file": c.source_file,
                "n_tokens": c.n_tokens,
                "language": c.language,
            }
            for c in fragmentos
        ]
        with self._engine.begin() as cx:
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.document_chunk (
                        chunk_id, version_id, document_id, vehicle_id, ordinal, text,
                        content_hash, chapter, section, subsection, page_start, page_end,
                        dtc_codes, vehicle_system, system_classification, engine_codes,
                        source_file, n_tokens, language)
                    VALUES (:chunk_id, :version_id, :document_id, :vehicle_id, :ordinal,
                            :text, :content_hash, :chapter, :section, :subsection,
                            :page_start, :page_end, :dtc_codes, :vehicle_system,
                            :system_classification, :engine_codes, :source_file, :n_tokens,
                            :language)
                    ON CONFLICT (chunk_id) DO NOTHING
                """),
                filas,
            )
        return len(filas)

    def store_embeddings(
        self,
        fragmentos: list[Chunk],
        vectores: npt.NDArray[np.float32],
        identidad: EmbeddingIdentity,
        *,
        ingestion_run_id: str | None = None,
    ) -> int:
        if not fragmentos:
            return 0
        if vectores.shape[0] != len(fragmentos):
            msg = f"{len(fragmentos)} fragmentos y {vectores.shape[0]} vectores"
            raise ValueError(msg)
        if vectores.shape[1] != identidad.dimension:
            msg = (
                f"El proveedor declara {identidad.dimension} dimensiones y produjo "
                f"{vectores.shape[1]}"
            )
            raise ValueError(msg)

        ahora = datetime.now(UTC)
        filas = [
            {
                "embedding_id": f"{c.chunk_id}:{identidad.model}",
                "chunk_id": c.chunk_id,
                "vehicle_id": c.vehicle_id,
                "document_id": c.document_id,
                "provider": identidad.provider,
                "model": identidad.model,
                "dimension": identidad.dimension,
                "version": identidad.version,
                "created_at": ahora,
                "run": ingestion_run_id,
                "vector": "[" + ",".join(f"{v:.6f}" for v in vectores[i]) + "]",
            }
            for i, c in enumerate(fragmentos)
        ]
        with self._engine.begin() as cx:
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.embedding (
                        embedding_id, chunk_id, vehicle_id, document_id,
                        embedding_provider, embedding_model, embedding_dimension,
                        embedding_version, created_at, ingestion_run_id, vector)
                    VALUES (:embedding_id, :chunk_id, :vehicle_id, :document_id,
                            :provider, :model, :dimension, :version, :created_at,
                            :run, CAST(:vector AS vector))
                    ON CONFLICT (chunk_id, embedding_model) DO NOTHING
                """),
                filas,
            )
        return len(filas)

    # ----------------------------------------------------------- búsqueda

    @lru_cache(maxsize=1)  # noqa: B019
    def embedding_models(self) -> frozenset[str]:
        """Espacios vectoriales realmente indexados, en todo el índice.

        Un índice puede contener varios a propósito, para compararlos. Saber
        cuáles hay es lo que permite rechazar una búsqueda en un espacio que no
        existe en lugar de devolver cero filas en silencio.

        **Alcance deliberado: el índice entero, no un vehículo.** Que un vehículo
        concreto no tenga fragmentos es un resultado legítimo --devuelve vacío--;
        que el espacio no exista en ninguna parte es un error de configuración.
        Confundirlos convertiría el blindaje en un fallo espurio.
        """
        with self._engine.connect() as conexion:
            filas = conexion.execute(sa.text("SELECT DISTINCT embedding_model FROM rag.embedding"))
            return frozenset(str(f[0]) for f in filas)

    def corpus_counts(self, *, vehicle_id: str, identidad: EmbeddingIdentity) -> dict[str, int]:
        """Fragmentos, ficheros de origen y vectores indexados de un vehículo.

        Existe para una comprobación que no puede hacerse de otra manera: un índice
        **incompleto** no da error, da menos evidencia, y menos evidencia se cuenta
        como una abstención legítima. La evaluación final compara estos recuentos
        con los congelados antes de medir, porque la sección 11 del documento de
        congelación trata un índice incompleto como motivo de invalidez.

        Los vectores se acotan por el vehículo **en las dos tablas**, porque la
        búsqueda filtra por el del vector y las comprobaciones filtraban por el del
        fragmento: el esquema no obliga a que coincidan, y si no coincidieran la
        búsqueda recuperaría menos evidencia de la que esta comprobación da por
        completa. Menos evidencia se cuenta como una abstención legítima.

        Los vectores se cuentan por la identidad **completa** del espacio y no por
        el nombre del modelo: el proveedor incluye el dispositivo, y un índice con
        vectores producidos en CPU bajo el mismo nombre de modelo pasaría un filtro
        por nombre mientras la consulta se vectoriza en otro espacio. Es la forma
        que tendría de reaparecer `MIXED-EMBEDDING-SPACE`.
        """
        with self._engine.connect() as cx:
            fragmentos, ficheros = cx.execute(
                sa.text(
                    f"SELECT count(*), count(DISTINCT source_file) "
                    f"FROM {ESQUEMA}.document_chunk WHERE vehicle_id = :v"
                ),
                {"v": vehicle_id},
            ).one()
            vectores = cx.execute(
                sa.text(
                    f"SELECT count(*) FROM {ESQUEMA}.embedding e "
                    f"JOIN {ESQUEMA}.document_chunk c ON c.chunk_id = e.chunk_id "
                    "WHERE e.vehicle_id = :v AND c.vehicle_id = :v "
                    "AND e.embedding_provider = :p "
                    "AND e.embedding_model = :m AND e.embedding_dimension = :d "
                    "AND e.embedding_version = :r"
                ),
                {
                    "v": vehicle_id,
                    "p": identidad.provider,
                    "m": identidad.model,
                    "d": identidad.dimension,
                    "r": identidad.version,
                },
            ).scalar_one()
        return {
            "n_chunks": int(fragmentos),
            "n_source_files": int(ficheros),
            "n_vectors_in_space": int(vectores),
        }

    def corpus_fingerprint(self, *, vehicle_id: str) -> str:
        """Huella del **contenido indexado** de un vehículo, fila a fila y entera.

        Los recuentos no detectan una sustitución: cambiar el texto de un fragmento,
        o un código por el que la recuperación filtra, o el encabezado de sección por
        el que el verificador decide si un fragmento es un procedimiento, deja el
        número de filas igual y cambia lo que el sistema encuentra y lo que acepta
        como soporte. Y un índice que devuelve menos evidencia no da error: produce
        abstenciones que parecen legítimas.

        Por eso la huella no elige campos. Se construye sobre la **fila completa**
        de cada fragmento y la de su documento, serializadas por la propia base de
        datos, en orden de `chunk_id`. Elegir campos obliga a acertar la lista, y la
        lista crece: el texto, el fichero, los códigos de avería y de motor, el tipo
        de documento y el nivel de autoridad para la reordenación, la sección para la
        clasificación del fragmento, el identificador de documento para el recuento
        de fuentes distintas. Incluirlo todo convierte un acierto en una propiedad.

        Una migración del esquema cambia la huella, y debe cambiarla: es un cambio
        visible del substrato sobre el que se mide.
        """
        huella = hashlib.sha256()
        with self._engine.connect() as cx:
            filas = cx.execute(
                sa.text(
                    "SELECT c.chunk_id, row_to_json(c)::text, row_to_json(d)::text "
                    f"FROM {ESQUEMA}.document_chunk c "
                    f"JOIN {ESQUEMA}.document d ON d.document_id = c.document_id "
                    "WHERE c.vehicle_id = :v ORDER BY c.chunk_id"
                ),
                {"v": vehicle_id},
            ).all()
        for chunk_id, fragmento, documento in filas:
            huella.update(f"{chunk_id}|{fragmento}|{documento}\n".encode())
        return huella.hexdigest()[:16]

    def vectors_fingerprint(self, *, vehicle_id: str, identidad: EmbeddingIdentity) -> str:
        """Huella de los **vectores** indexados del espacio declarado.

        Es la última pieza que decidía el resultado y no estaba cubierta: la
        búsqueda ordena por distancia al vector, de modo que sustituir un vector
        --dejando intactos el fragmento, sus metadatos y la identidad del espacio--
        cambia qué evidencia se recupera y, con ella, las tasas de abstención, sin
        que ningún recuento ni la huella del contenido se muevan.

        El vector se lee como texto para que la huella no dependa de cómo el
        controlador materialice el tipo.
        """
        huella = hashlib.sha256()
        with self._engine.connect() as cx:
            filas = cx.execute(
                sa.text(
                    "SELECT e.chunk_id, e.vector::text "
                    f"FROM {ESQUEMA}.embedding e "
                    f"JOIN {ESQUEMA}.document_chunk c ON c.chunk_id = e.chunk_id "
                    "WHERE e.vehicle_id = :v AND c.vehicle_id = :v "
                    "AND e.embedding_provider = :p "
                    "AND e.embedding_model = :m AND e.embedding_dimension = :d "
                    "AND e.embedding_version = :r ORDER BY e.chunk_id"
                ),
                {
                    "v": vehicle_id,
                    "p": identidad.provider,
                    "m": identidad.model,
                    "d": identidad.dimension,
                    "r": identidad.version,
                },
            ).all()
        for chunk_id, vector in filas:
            huella.update(f"{chunk_id}|{vector}\n".encode())
        return huella.hexdigest()[:16]

    def spaces_for_model(
        self, *, embedding_model: str, vehicle_id: str
    ) -> tuple[tuple[str, int, str], ...]:
        """Espacios indexados que comparten un nombre de modelo.

        La búsqueda acota por `embedding_model`, que es lo que RERUN-A impuso para
        no mezclar dos modelos en una misma ordenación. Pero la identidad de un
        espacio es más que el nombre: incluye el proveedor con su dispositivo, la
        dimensión y la versión. Si dos espacios compartieran nombre, acotar por
        nombre dejaría de identificar uno solo y la ordenación volvería a mezclar.

        Saberlo permite exigir, antes de medir, que el nombre identifique un único
        espacio; mientras lo haga, acotar por nombre y acotar por identidad son la
        misma cosa.

        Se acota al vehículo evaluado, como los demás recuentos: la búsqueda filtra
        por vehículo, de modo que los vectores de otro no pueden mezclarse en esta
        evaluación y exigir que todo el índice tuviera un solo espacio por nombre
        habría bloqueado la ejecución por un motivo falso.
        """
        with self._engine.connect() as cx:
            filas = cx.execute(
                sa.text(
                    "SELECT DISTINCT e.embedding_provider, e.embedding_dimension, "
                    f"e.embedding_version FROM {ESQUEMA}.embedding e "
                    f"JOIN {ESQUEMA}.document_chunk c ON c.chunk_id = e.chunk_id "
                    "WHERE e.embedding_model = :m AND e.vehicle_id = :v AND c.vehicle_id = :v "
                    "ORDER BY e.embedding_provider, e.embedding_dimension, e.embedding_version"
                ),
                {"m": embedding_model, "v": vehicle_id},
            ).all()
        return tuple((str(p), int(d), str(v)) for p, d, v in filas)

    def vehicle_id_mismatches(self, *, vehicle_id: str) -> int:
        """Vectores cuyo vehículo no es el del fragmento al que apuntan.

        La búsqueda filtra por el vehículo **del vector** y las comprobaciones del
        índice exigen que los dos coincidan. Mientras no haya desajustes, las dos
        cosas son equivalentes; si los hubiera, la búsqueda podría recuperar un
        vector que ninguna comprobación miró. El esquema no lo impide, así que se
        cuenta.
        """
        with self._engine.connect() as cx:
            return int(
                cx.execute(
                    sa.text(
                        f"SELECT count(*) FROM {ESQUEMA}.embedding e "
                        f"JOIN {ESQUEMA}.document_chunk c ON c.chunk_id = e.chunk_id "
                        "WHERE (e.vehicle_id = :v OR c.vehicle_id = :v) "
                        "AND e.vehicle_id <> c.vehicle_id"
                    ),
                    {"v": vehicle_id},
                ).scalar_one()
            )

    def search(
        self,
        query_vector: npt.NDArray[np.float32],
        *,
        vehicle_id: str,
        top_k: int = 10,
        document_types: tuple[str, ...] | None = None,
        engine_codes: tuple[str, ...] | None = None,
        dtc_codes: tuple[str, ...] | None = None,
        exclude_documents: tuple[str, ...] = (),
        exclude_chunks: tuple[str, ...] = (),
        embedding_model: str,
    ) -> list[RetrievedChunk]:
        # Un espacio que no existe en el índice devolvería cero filas, y cero
        # filas se confunde con «no hay evidencia»: una abstención con aspecto
        # legítimo por un error de configuración. Se comprueba y se declara.
        if embedding_model not in self.embedding_models():
            raise ValueError(
                f"el espacio {embedding_model!r} no está indexado; buscar en él "
                "devolvería cero resultados, indistinguibles de la ausencia de "
                "evidencia. Espacios disponibles: "
                f"{sorted(self.embedding_models())}"
            )
        vector = "[" + ",".join(f"{v:.6f}" for v in np.asarray(query_vector).ravel()) + "]"
        # El modelo de embeddings acota la búsqueda. Un índice puede contener
        # vectores de varios modelos --conviven a propósito, para poder
        # compararlos-- y mezclarlos en una misma consulta compararía puntos de
        # espacios distintos: los resultados serían ruido con aspecto de orden.
        #
        # Hasta el 4 de septiembre de 2026 este razonamiento estaba escrito aquí
        # y la línea siguiente hacía el filtro **opcional**, con el parámetro a
        # nulo por defecto. Ninguno de los tres ejecutores lo pasaba, así que
        # cada consulta ordenó 12 316 vectores de dos espacios a la vez. El
        # parámetro es ahora obligatorio: `MIXED-EMBEDDING-SPACE`,
        # `docs/methodology/politica-espacio-de-embeddings.md`.
        condiciones = [
            "e.vehicle_id = :vehicle_id",
            "e.embedding_model = :embedding_model",
        ]
        parametros: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "vector": vector,
            "top_k": top_k,
            "embedding_model": embedding_model,
        }
        if document_types:
            condiciones.append("d.document_type = ANY(:document_types)")
            parametros["document_types"] = list(document_types)
        if engine_codes:
            # Un fragmento sin motores declarados no se descarta: puede ser
            # información general del vehículo. Se descarta el que declara
            # motores y ninguno coincide.
            condiciones.append(
                "(cardinality(c.engine_codes) = 0 OR c.engine_codes && :engine_codes)"
            )
            parametros["engine_codes"] = list(engine_codes)
        if dtc_codes:
            condiciones.append("c.dtc_codes && :dtc_codes")
            parametros["dtc_codes"] = list(dtc_codes)
        if exclude_documents:
            condiciones.append("NOT (c.document_id = ANY(:exclude_documents))")
            parametros["exclude_documents"] = list(exclude_documents)
        if exclude_chunks:
            condiciones.append("NOT (c.chunk_id = ANY(:exclude_chunks))")
            parametros["exclude_chunks"] = list(exclude_chunks)

        consulta = sa.text(f"""
            SELECT c.chunk_id, c.document_id, c.vehicle_id, c.text,
                   1 - (e.vector <=> CAST(:vector AS vector)) AS score,
                   c.chapter, c.section, c.page_start, c.page_end, c.dtc_codes,
                   c.vehicle_system, c.engine_codes, c.source_file, c.language,
                   d.title, d.publisher, d.source_url, d.authority_level, d.document_type
            FROM {ESQUEMA}.embedding e
            JOIN {ESQUEMA}.document_chunk c ON c.chunk_id = e.chunk_id
            JOIN {ESQUEMA}.document d ON d.document_id = c.document_id
            WHERE {" AND ".join(condiciones)}
            ORDER BY e.vector <=> CAST(:vector AS vector)
            LIMIT :top_k
        """)
        with self._engine.connect() as cx:
            filas = cx.execute(consulta, parametros).mappings().all()

        return [
            RetrievedChunk(
                chunk_id=f["chunk_id"],
                document_id=f["document_id"],
                vehicle_id=f["vehicle_id"],
                text=f["text"],
                score=float(f["score"]),
                rank=i + 1,
                chapter=f["chapter"],
                section=f["section"],
                page_start=f["page_start"],
                page_end=f["page_end"],
                dtc_codes=tuple(f["dtc_codes"] or ()),
                vehicle_system=f["vehicle_system"],
                engine_codes=tuple(f["engine_codes"] or ()),
                source_file=f["source_file"],
                language=f["language"],
                document_title=f["title"],
                publisher=f["publisher"],
                source_url=f["source_url"],
                authority_level=f["authority_level"],
                document_type=f["document_type"],
            )
            for i, f in enumerate(filas)
        ]

    def chunks_for_files(self, ficheros: tuple[str, ...], *, vehicle_id: str) -> tuple[str, ...]:
        """Identificadores de los fragmentos que provienen de estos ficheros.

        Sirve para construir la condición ABSENT del experimento: se retira del
        índice la evidencia que sostenía una explicación, se repite el caso con
        todo lo demás idéntico y se observa si el agente cambia de decisión.

        La exclusión es **explícita y auditable**: queda registrada en la
        recuperación como lista de fragmentos retirados, no como un efecto
        lateral de haber filtrado por otra cosa.
        """
        if not ficheros:
            return ()
        with self._engine.connect() as cx:
            filas = (
                cx.execute(
                    sa.text(
                        f"SELECT chunk_id FROM {ESQUEMA}.document_chunk "
                        "WHERE vehicle_id = :v AND source_file = ANY(:f)"
                    ),
                    {"v": vehicle_id, "f": list(ficheros)},
                )
                .scalars()
                .all()
            )
        return tuple(str(f) for f in filas)

    def chunks_for_dtc(self, codigos: tuple[str, ...], *, vehicle_id: str) -> tuple[str, ...]:
        """Fragmentos que portan alguno de estos códigos de diagnóstico.

        Es la forma correcta de construir la condición ABSENT. Retirar solo el
        fichero del procedimiento principal deja fuera las tablas de códigos, la
        lógica de detección y los procedimientos vecinos que mencionan el mismo
        código: la evidencia seguiría ahí y la condición no sería ABSENT.

        Se comprobó: excluyendo los cuatro ficheros del procedimiento de P2187,
        el sistema seguía recuperando evidencia suficiente desde los
        procedimientos de P2096, P2195 y P2196, que portan el mismo código.
        """
        if not codigos:
            return ()
        with self._engine.connect() as cx:
            filas = (
                cx.execute(
                    sa.text(
                        f"SELECT chunk_id FROM {ESQUEMA}.document_chunk "
                        "WHERE vehicle_id = :v AND dtc_codes && :c"
                    ),
                    {"v": vehicle_id, "c": list(codigos)},
                )
                .scalars()
                .all()
            )
        return tuple(str(f) for f in filas)

    def log_retrieval(
        self,
        *,
        vehicle_id: str,
        query_text: str,
        resultados: list[RetrievedChunk],
        identidad: EmbeddingIdentity,
        top_k: int,
        filters: dict[str, Any] | None = None,
        corpus_variant: str | None = None,
        experiment_id: str | None = None,
        query_language: str = "en",
    ) -> str:
        """Registra una recuperación y devuelve su identificador."""
        import json

        run_id = str(uuid.uuid4())
        with self._engine.begin() as cx:
            cx.execute(
                sa.text(f"""
                    INSERT INTO {ESQUEMA}.retrieval_run (
                        run_id, vehicle_id, query_text, executed_at, embedding_provider,
                        embedding_model, top_k, filters, corpus_variant, experiment_id,
                        query_language)
                    VALUES (:r, :v, :q, :t, :p, :m, :k, :f, :cv, :e, :ql)
                """),
                {
                    "r": run_id,
                    "v": vehicle_id,
                    "q": query_text,
                    "t": datetime.now(UTC),
                    "p": identidad.provider,
                    "m": identidad.model,
                    "k": top_k,
                    "f": json.dumps(filters or {}, ensure_ascii=False),
                    "cv": corpus_variant,
                    "e": experiment_id,
                    "ql": query_language,
                },
            )
            if resultados:
                cx.execute(
                    sa.text(f"""
                        INSERT INTO {ESQUEMA}.retrieval_result (
                            result_id, run_id, chunk_id, rank, score,
                            authority_level, evidence_rank)
                        VALUES (:i, :r, :c, :k, :s, :a, :er)
                    """),
                    [
                        {
                            "i": f"{run_id}:{r.rank}",
                            "r": run_id,
                            "c": r.chunk_id,
                            "k": r.rank,
                            "s": r.score,
                            "a": r.authority_level,
                            "er": None,
                        }
                        for r in resultados
                    ],
                )
        return run_id

    # ------------------------------------------------------ búsqueda léxica

    def search_lexical(
        self,
        query_text: str,
        *,
        vehicle_id: str,
        top_k: int = 10,
        engine_codes: tuple[str, ...] | None = None,
        language: str = "en",
    ) -> list[RetrievedChunk]:
        """Búsqueda de texto completo de PostgreSQL, con el mismo filtro de vehículo.

        Complementa a la semántica donde esta es débil: códigos como P0133,
        referencias de pieza y terminología exacta. Un embedding coloca «P0133» y
        «P0134» prácticamente en el mismo sitio; la coincidencia exacta no.
        """
        configuracion = CONFIG_FTS.get(language, "simple")
        condiciones = [
            "c.vehicle_id = :vehicle_id",
            f"to_tsvector('{configuracion}', c.text) @@ plainto_tsquery('{configuracion}', :q)",
            # Solo se buscan fragmentos del idioma de la consulta: la búsqueda
            # léxica no cruza idiomas, y fingir que sí devolvería coincidencias
            # por accidente ortográfico.
            "c.language = :language",
        ]
        parametros: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "q": query_text,
            "top_k": top_k,
            "language": language,
        }
        if engine_codes:
            condiciones.append(
                "(cardinality(c.engine_codes) = 0 OR c.engine_codes && :engine_codes)"
            )
            parametros["engine_codes"] = list(engine_codes)

        consulta = sa.text(f"""
            SELECT c.chunk_id, c.document_id, c.vehicle_id, c.text,
                   ts_rank(to_tsvector('{configuracion}', c.text),
                           plainto_tsquery('{configuracion}', :q)) AS score,
                   c.chapter, c.section, c.page_start, c.page_end, c.dtc_codes,
                   c.vehicle_system, c.engine_codes, c.source_file, c.language,
                   d.title, d.publisher, d.source_url, d.authority_level, d.document_type
            FROM {ESQUEMA}.document_chunk c
            JOIN {ESQUEMA}.document d ON d.document_id = c.document_id
            WHERE {" AND ".join(condiciones)}
            ORDER BY score DESC
            LIMIT :top_k
        """)
        with self._engine.connect() as cx:
            filas = cx.execute(consulta, parametros).mappings().all()

        return [
            RetrievedChunk(
                chunk_id=f["chunk_id"],
                document_id=f["document_id"],
                vehicle_id=f["vehicle_id"],
                text=f["text"],
                score=float(f["score"]),
                rank=i + 1,
                chapter=f["chapter"],
                section=f["section"],
                page_start=f["page_start"],
                page_end=f["page_end"],
                dtc_codes=tuple(f["dtc_codes"] or ()),
                vehicle_system=f["vehicle_system"],
                engine_codes=tuple(f["engine_codes"] or ()),
                source_file=f["source_file"],
                language=f["language"],
                document_title=f["title"],
                publisher=f["publisher"],
                source_url=f["source_url"],
                authority_level=f["authority_level"],
                document_type=f["document_type"],
            )
            for i, f in enumerate(filas)
        ]


def reciprocal_rank_fusion(
    listas: list[list[RetrievedChunk]], *, k: int = 60, top_k: int = 10
) -> list[RetrievedChunk]:
    """Fusiona varias listas ordenadas por la suma de rangos recíprocos.

    Se elige frente a sumar puntuaciones porque las escalas no son comparables:
    la distancia coseno vive en [0, 1] y ``ts_rank`` no tiene cota superior fija.
    Sumar ambas daría a la léxica un peso arbitrario que dependería del corpus.

    La constante ``k`` amortigua las primeras posiciones para que un único primer
    puesto no domine la fusión.

    **La fusión decide el orden, no la puntuación.** Cada fragmento conserva su
    mejor puntuación de origen. El peso de la fusión vive en una escala propia
    --en torno a 1/60-- que no es comparable con una similitud coseno, y
    sustituir una por otra rompe cualquier criterio posterior que compare
    puntuaciones entre estrategias. Ocurrió: el verificador de suficiencia
    rechazaba por «poco apoyo documental» un caso cuyas puntuaciones eran
    0,016 simplemente por venir de una fusión.
    """
    puntos: dict[str, float] = {}
    fragmentos: dict[str, RetrievedChunk] = {}
    mejor_original: dict[str, float] = {}
    for lista in listas:
        for posicion, fragmento in enumerate(lista, start=1):
            puntos[fragmento.chunk_id] = puntos.get(fragmento.chunk_id, 0.0) + 1.0 / (k + posicion)
            fragmentos.setdefault(fragmento.chunk_id, fragmento)
            mejor_original[fragmento.chunk_id] = max(
                mejor_original.get(fragmento.chunk_id, 0.0), fragmento.score
            )

    ordenados = sorted(puntos.items(), key=lambda par: par[1], reverse=True)[:top_k]
    salida: list[RetrievedChunk] = []
    for posicion, (chunk_id, _peso) in enumerate(ordenados, start=1):
        base = fragmentos[chunk_id]
        salida.append(
            RetrievedChunk(**{**base.__dict__, "rank": posicion, "score": mejor_original[chunk_id]})
        )
    return salida
