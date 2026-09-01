"""Proveedores de embeddings.

El almacén vectorial no se acopla a un proveedor concreto: se le pasa uno que
cumpla ``EmbeddingProvider`` y nada más cambia. Eso importa porque el modelo de
embeddings **forma parte de la identidad del corpus**: dos corpus indexados con
modelos distintos no son comparables, y cambiar de modelo obliga a reindexar.

Por eso cada ejecución registra proveedor, modelo, dimensión y versión.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import pairwise

import numpy as np
import numpy.typing as npt

Matriz = npt.NDArray[np.float32]


@dataclass(frozen=True)
class EmbeddingIdentity:
    """Lo que identifica un espacio vectorial. Va con cada ejecución."""

    provider: str
    model: str
    dimension: int
    version: str

    def as_dict(self) -> dict[str, str | int]:
        return {
            "embedding_provider": self.provider,
            "embedding_model": self.model,
            "embedding_dimension": self.dimension,
            "embedding_version": self.version,
        }


class EmbeddingProvider(ABC):
    """Convierte textos en vectores."""

    @property
    @abstractmethod
    def identity(self) -> EmbeddingIdentity: ...

    @abstractmethod
    def embed(self, textos: list[str]) -> Matriz:
        """Devuelve ``(len(textos), dimension)`` con vectores normalizados.

        Se normalizan a norma 1 para que la distancia coseno de pgvector sea
        equivalente al producto escalar y las puntuaciones sean comparables entre
        consultas.
        """

    def embed_one(self, texto: str) -> Matriz:
        return np.asarray(self.embed([texto])[0], dtype=np.float32)


def _normalizar_filas(matriz: Matriz) -> Matriz:
    normas = np.linalg.norm(matriz, axis=1, keepdims=True)
    normas[normas == 0.0] = 1.0
    return np.asarray(matriz / normas, dtype=np.float32)


class HashingEmbeddingProvider(EmbeddingProvider):
    """Embeddings deterministas por hashing de n-gramas de palabras.

    No aprende nada y no captura sinonimia. Existe para dos cosas: que los tests
    corran sin red ni modelos descargados, y que haya una referencia inferior
    contra la que comparar un modelo aprendido. Si el modelo aprendido no supera
    a esto, no está aportando semántica.

    Es determinista por construcción: el mismo texto produce siempre el mismo
    vector, en cualquier máquina.
    """

    def __init__(self, dimension: int = 384, seed: int = 20260901) -> None:
        self._dimension = dimension
        self._seed = seed

    @property
    def identity(self) -> EmbeddingIdentity:
        return EmbeddingIdentity(
            provider="hashing",
            model=f"ngram-hash-{self._dimension}",
            dimension=self._dimension,
            version="1.0.0",
        )

    def embed(self, textos: list[str]) -> Matriz:
        salida = np.zeros((len(textos), self._dimension), dtype=np.float32)
        for i, texto in enumerate(textos):
            palabras = texto.lower().split()
            # Unigramas y bigramas: los bigramas recogen algo de orden, que en
            # terminología técnica distingue "fuel trim" de "trim fuel".
            terminos = palabras + [f"{a}_{b}" for a, b in pairwise(palabras)]
            for termino in terminos:
                digest = hashlib.blake2b(
                    termino.encode("utf-8"), digest_size=8, key=str(self._seed).encode()
                ).digest()
                indice = int.from_bytes(digest[:4], "big") % self._dimension
                signo = 1.0 if digest[4] % 2 == 0 else -1.0
                salida[i, indice] += signo
        return _normalizar_filas(salida)


class SentenceTransformerProvider(EmbeddingProvider):
    """Embeddings locales con sentence-transformers.

    El modelo por defecto es **multilingüe**. La razón está medida: con el modelo
    monolingüe inglés, una consulta en español encuentra el documento relevante
    en 1 de 5 casos dentro de los 500 primeros resultados, con posición mediana
    376. Con el multilingüe, 4 de 5 y mediana 54 --el mismo nivel que en inglés--.

    El corpus del vehículo está en inglés y el trabajo se escribe en español, así
    que la recuperación translingüe es el caso normal, no la excepción.

    Sin clave de API y sin red tras la primera descarga del modelo. Usa MPS
    cuando está disponible; el dispositivo se registra porque un resultado en CPU
    y otro en MPS no son necesariamente idénticos bit a bit.

    El modelo **no** se descarga solo al importar: se carga la primera vez que se
    piden vectores, para que importar el módulo no dispare tráfico de red.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: str | None = None,
        batch_size: int = 64,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._batch_size = batch_size
        self._modelo: object | None = None
        self._dimension: int | None = None

    def _cargar(self) -> object:
        if self._modelo is None:
            from sentence_transformers import SentenceTransformer

            if self._device is None:
                import torch

                self._device = "mps" if torch.backends.mps.is_available() else "cpu"
            modelo = SentenceTransformer(self._model_name, device=self._device)
            # El nombre del método cambió entre versiones; se prueban ambos en
            # lugar de fijar una versión concreta de la librería.
            obtener = getattr(
                modelo, "get_embedding_dimension", modelo.get_sentence_embedding_dimension
            )
            dimension = obtener()
            if dimension is None:
                msg = f"El modelo {self._model_name!r} no declara su dimensión"
                raise RuntimeError(msg)
            self._dimension = int(dimension)
            self._modelo = modelo
        return self._modelo

    @property
    def identity(self) -> EmbeddingIdentity:
        self._cargar()
        assert self._dimension is not None
        return EmbeddingIdentity(
            provider=f"sentence-transformers[{self._device}]",
            model=self._model_name,
            dimension=self._dimension,
            version="1.0.0",
        )

    def embed(self, textos: list[str]) -> Matriz:
        modelo = self._cargar()
        vectores = modelo.encode(  # type: ignore[attr-defined]
            textos,
            batch_size=self._batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectores, dtype=np.float32)


#: Modelos disponibles. Ambos de 384 dimensiones a propósito: se pueden comparar
#: sobre el mismo esquema, sin migrar y sin reindexar por partida doble.
MODELOS: dict[str, str] = {
    "en": "sentence-transformers/all-MiniLM-L6-v2",
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
}


def get_provider(nombre: str = "hashing", **kwargs: object) -> EmbeddingProvider:
    """Selecciona un proveedor por nombre.

    Por defecto ``hashing``: un checkout recién clonado no descarga modelos ni
    toca la red hasta que alguien lo pide explícitamente.
    """
    if nombre == "hashing":
        return HashingEmbeddingProvider(**kwargs)  # type: ignore[arg-type]
    if nombre in ("sentence-transformers", "st"):
        return SentenceTransformerProvider(**kwargs)  # type: ignore[arg-type]
    if nombre in ("multilingual", "ml"):
        # Un modelo monolingüe coloca una consulta en español en una región del
        # espacio que no corresponde a su traducción. Seguiría devolviendo
        # resultados, y serían casualidad.
        return SentenceTransformerProvider(
            model_name=MODELOS["multilingual"],
            **kwargs,  # type: ignore[arg-type]
        )
    msg = f"Proveedor de embeddings desconocido: {nombre!r}"
    raise ValueError(msg)
