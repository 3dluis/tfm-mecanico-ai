"""Proveedores de modelo de lenguaje.

La lógica científica no depende del proveedor. Se cambia con una variable de
entorno y nada más se toca. No es comodidad: si el resultado cambiara de forma
sustantiva al cambiar de proveedor, sería un hallazgo, y solo se detecta si el
intercambio es trivial.

**El modelo elegido es local.** Un SLM sobre Apple Silicon, sin clave de API y
sin red tras la primera descarga. Eso hace el experimento reproducible por un
tercero sin darse de alta en ningún sitio, que es lo que la portabilidad del TFM
exige.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

PROMPT_VERSION = "p1"


@dataclass(frozen=True)
class LLMIdentity:
    """Lo que identifica una generación. Se registra con cada llamada."""

    provider: str
    model: str
    temperature: float
    max_tokens: int
    prompt_version: str
    endpoint_type: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "llm_provider": self.provider,
            "llm_model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "prompt_version": self.prompt_version,
            "endpoint_type": self.endpoint_type,
        }


@dataclass
class LLMResponse:
    """Respuesta cruda, antes de validar contra el esquema."""

    text: str
    identity: LLMIdentity
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    finish_reason: str = ""
    latency_s: float = 0.0

    def as_json(self) -> dict[str, Any]:
        """Extrae el objeto JSON de la respuesta.

        Un modelo pequeño envuelve el JSON en texto o en vallas de código con
        frecuencia. Se extrae el primer objeto equilibrado en lugar de exigir que
        la respuesta sea JSON puro: rechazarla por el envoltorio mediría la
        obediencia al formato y no la calidad del razonamiento.
        """
        texto = self.text.strip()
        inicio = texto.find("{")
        if inicio == -1:
            msg = "la respuesta no contiene ningún objeto JSON"
            raise ValueError(msg)
        profundidad = 0
        for i, caracter in enumerate(texto[inicio:], start=inicio):
            if caracter == "{":
                profundidad += 1
            elif caracter == "}":
                profundidad -= 1
                if profundidad == 0:
                    return dict(json.loads(texto[inicio : i + 1]))
        msg = "el objeto JSON de la respuesta está incompleto"
        raise ValueError(msg)


class LLMProvider(ABC):
    """Contrato del proveedor."""

    @property
    @abstractmethod
    def identity(self) -> LLMIdentity: ...

    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Genera una respuesta a partir de la conversación."""


class EchoProvider(LLMProvider):
    """Proveedor determinista, sin red.

    No genera lenguaje: construye la salida a partir de la evidencia que se le
    entrega, siguiendo el esquema. Sirve para tres cosas: que los tests corran
    sin modelo, que la integración continua no dependa de una descarga, y como
    **referencia inferior** del experimento --lo que se obtiene sin capacidad de
    redacción alguna--.

    Si el modelo de lenguaje no supera a esto en las métricas de trazabilidad, no
    está aportando nada que no aporte una plantilla.
    """

    @property
    def identity(self) -> LLMIdentity:
        return LLMIdentity(
            provider="echo",
            model="deterministic-template",
            temperature=0.0,
            max_tokens=0,
            prompt_version=PROMPT_VERSION,
            endpoint_type="local",
        )

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        # La plantilla lee el último mensaje de herramienta: es donde viaja la
        # evidencia recuperada.
        evidencia: list[dict[str, Any]] = []
        for m in reversed(messages):
            if m.get("role") == "tool":
                try:
                    evidencia = json.loads(m.get("content", "[]"))
                except json.JSONDecodeError:
                    evidencia = []
                break

        if not evidencia:
            salida: dict[str, Any] = {
                "decision": "ABSTAIN",
                "reason": "NO_APPLICABLE_DOCUMENTATION",
                "missing_evidence": ["no se recuperó ningún fragmento aplicable"],
                "notes": "plantilla determinista",
            }
        else:
            salida = {
                "decision": "EXPLAIN",
                "diagnosis": "condición compatible con la evidencia recuperada",
                "confidence": 0.5,
                "claims": [
                    {
                        "claim_id": "C01",
                        "text": (
                            "La evidencia recuperada describe la condición "
                            "observada en las señales del vehículo."
                        ),
                        "observational_evidence": ["OBS001"],
                        "documentary_evidence": [evidencia[0]["chunk_id"]],
                    }
                ],
                "limitations": ["salida generada por plantilla, sin razonamiento"],
            }
        return LLMResponse(
            text=json.dumps(salida, ensure_ascii=False),
            identity=self.identity,
            finish_reason="stop",
        )


class OllamaProvider(LLMProvider):
    """SLM local a través de Ollama.

    **No descarga modelos.** Si el modelo no está presente, falla con
    instrucciones para obtenerlo. Descargar varios gigabytes como efecto lateral
    de ejecutar un experimento no es aceptable.
    """

    def __init__(
        self,
        model: str = "qwen2.5:3b-instruct-q4_K_M",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout_s: float = 180.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout_s

    @property
    def identity(self) -> LLMIdentity:
        return LLMIdentity(
            provider="ollama",
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            prompt_version=PROMPT_VERSION,
            endpoint_type="local",
        )

    def available(self) -> bool:
        """¿Está el servicio en marcha y el modelo presente?"""
        import httpx

        try:
            r = httpx.get(f"{self._base_url}/api/tags", timeout=5.0)
            r.raise_for_status()
            modelos = {m["name"] for m in r.json().get("models", [])}
        except Exception:
            return False
        return self._model in modelos

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        import time

        import httpx

        cuerpo: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self._temperature,
                "num_predict": self._max_tokens,
                # Semilla fija: dos ejecuciones del mismo caso deben dar la misma
                # respuesta, o las métricas de trazabilidad no serían
                # reproducibles.
                "seed": 20260901,
            },
        }
        if tools:
            cuerpo["tools"] = tools
        if json_schema:
            cuerpo["format"] = json_schema

        inicio = time.perf_counter()
        try:
            respuesta = httpx.post(f"{self._base_url}/api/chat", json=cuerpo, timeout=self._timeout)
            respuesta.raise_for_status()
        except httpx.HTTPError as error:
            msg = (
                f"Ollama no respondió en {self._base_url}: {error}. "
                f"Arranca el servicio y comprueba que el modelo {self._model!r} "
                "está descargado: `ollama pull " + self._model + "`"
            )
            raise RuntimeError(msg) from error

        datos = respuesta.json()
        mensaje = datos.get("message", {})
        return LLMResponse(
            text=mensaje.get("content", ""),
            identity=self.identity,
            tool_calls=mensaje.get("tool_calls", []),
            finish_reason=datos.get("done_reason", ""),
            latency_s=time.perf_counter() - inicio,
        )


def get_llm(nombre: str = "echo", **kwargs: Any) -> LLMProvider:
    """Selecciona proveedor por nombre.

    Por defecto ``echo``: un checkout recién clonado no necesita ningún modelo
    para pasar los tests.
    """
    if nombre == "echo":
        return EchoProvider()
    if nombre == "ollama":
        return OllamaProvider(**kwargs)
    if nombre == "transformers":
        return TransformersProvider(**kwargs)
    adaptador = adapter_dir_from_name(nombre)
    if adaptador is not None:
        return TransformersProvider(adapter_dir=adaptador, **kwargs)
    msg = f"Proveedor de LLM desconocido: {nombre!r}"
    raise ValueError(msg)


def adapter_dir_from_name(nombre: str) -> str | None:
    """``transformers-lora`` -> ``models/slm_lora``; ``transformers-lora@X`` -> ``models/X``.

    Varias iteraciones del ajuste tienen que poder medirse una contra otra sin
    que la última pise a la anterior.
    """
    if nombre == "transformers-lora":
        return "models/slm_lora"
    if nombre.startswith("transformers-lora@"):
        sub = nombre.split("@", 1)[1].strip("/")
        if not sub or "/" in sub or sub.startswith("."):
            msg = f"Nombre de adaptador no válido: {sub!r}"
            raise ValueError(msg)
        return f"models/{sub}"
    return None


class TransformersProvider(LLMProvider):
    """SLM local por PyTorch, con o sin adaptador LoRA.

    Es la vía de inferencia del modelo **ajustado**: Ollama no puede servir un
    adaptador PEFT, así que el modelo ajustado se ejecuta con el mismo stack con
    el que se entrenó. Con ``adapter_dir=None`` sirve el modelo base, lo que
    permite medir antes y después con exactamente el mismo código de inferencia
    --si se comparara Ollama contra transformers, parte de la diferencia sería
    del motor y no del ajuste--.

    Generación determinista: sin muestreo, semilla fija. Dos ejecuciones del
    mismo caso deben dar la misma respuesta.
    """

    def __init__(
        self,
        base_model: str = "Qwen/Qwen2.5-3B-Instruct",
        revision: str | None = None,
        adapter_dir: str | None = None,
        max_tokens: int = 1024,
        device: str | None = None,
    ) -> None:
        self._base_model = base_model
        self._revision = revision
        self._adapter_dir = adapter_dir
        self._max_tokens = max_tokens
        self._device = device
        self._modelo: Any = None
        self._tok: Any = None

    def _cargar(self) -> None:
        if self._modelo is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if self._device is None:
            self._device = "mps" if torch.backends.mps.is_available() else "cpu"
        extra = {"revision": self._revision} if self._revision else {}
        self._tok = AutoTokenizer.from_pretrained(self._base_model, **extra)
        modelo: Any = AutoModelForCausalLM.from_pretrained(
            self._base_model, dtype=torch.bfloat16, **extra
        )
        if self._adapter_dir:
            from peft import PeftModel

            modelo = PeftModel.from_pretrained(modelo, self._adapter_dir)
            # Fusionar el adaptador en los pesos evita el sobrecoste de la doble
            # proyección en cada token durante la generación.
            modelo = modelo.merge_and_unload()
        modelo.to(self._device)
        modelo.eval()
        self._modelo = modelo

    @property
    def identity(self) -> LLMIdentity:
        etiqueta = self._base_model + (f"+lora:{self._adapter_dir}" if self._adapter_dir else "")
        return LLMIdentity(
            provider="transformers",
            model=etiqueta,
            temperature=0.0,
            max_tokens=self._max_tokens,
            prompt_version=PROMPT_VERSION,
            endpoint_type="local",
        )

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        import time

        import torch

        self._cargar()
        # Se renderiza con la MISMA plantilla que se usó en el ajuste, para que lo
        # que ve al inferir sea lo que vio al entrenar.
        prompt = self._tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        entrada = self._tok(prompt, return_tensors="pt").to(self._device)

        torch.manual_seed(20260901)
        inicio = time.perf_counter()
        with torch.no_grad():
            salida = self._modelo.generate(
                **entrada,
                max_new_tokens=self._max_tokens,
                do_sample=False,
                pad_token_id=self._tok.eos_token_id,
            )
        latencia = time.perf_counter() - inicio
        nuevos = salida[0, entrada["input_ids"].shape[1] :]
        texto = self._tok.decode(nuevos, skip_special_tokens=True)
        return LLMResponse(
            text=texto,
            identity=self.identity,
            finish_reason="stop" if nuevos.shape[0] < self._max_tokens else "length",
            latency_s=latencia,
        )
