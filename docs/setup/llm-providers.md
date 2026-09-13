# Proveedores de modelo de lenguaje

## Principio

La lógica científica no depende del proveedor. El modelo de lenguaje se sustituye
cambiando variables de entorno, sin tocar una línea del pipeline.

Esto no es una comodidad de ingeniería: es una condición del experimento. Si el
resultado cambiara de forma sustantiva al cambiar de proveedor, eso sería un
hallazgo a reportar, y solo se puede detectar si el intercambio es trivial.

## Abstracción

```python
class LLMProvider(Protocol):
    def complete(self, prompt: str, *, schema: type[BaseModel]) -> LLMResponse: ...
```

Toda llamada registra lo que la hace reproducible:

| Campo | Para qué |
|---|---|
| `provider` | quién respondió |
| `model` | identificador exacto del modelo |
| `temperature` | 0.0 en los experimentos oficiales |
| `max_tokens` | límite de la respuesta |
| `prompt_version` | versión del prompt; cambiarlo invalida la comparación |
| `endpoint_type` | remoto por API, local o determinista |
| `experiment_id` | ejecución a la que pertenece |

## Proveedores implementados

| Valor de `LLM_PROVIDER` | Uso |
|---|---|
| `echo` | determinista, sin red. Por defecto. Tests y CI |
| `ollama` | modelo local vía HTTP; solo portabilidad |
| `transformers` | modelo local con `transformers` (Qwen2.5-3B-Instruct por defecto), en MPS |
| `transformers-lora` | el anterior con el adaptador LoRA de `models/slm_lora`; `transformers-lora@<subdir>` elige otro adaptador (`mecanico-exp sufficiency --llm transformers-lora@slm_lora_v2`) |

Un proveedor remoto por API con la interfaz de chat habitual estaba previsto en el diseño
(`docs/plan_experimental_macbook.md`), pero **no se implementó**: ningún resultado del
laboratorio procede de un proveedor remoto. Hasta el 13-09-2026 el tipo de configuración
admitía los valores `openai_compatible` y `anthropic` sin implementación detrás; se corrigió
para que la configuración documente solo lo que existe.

`echo` es el valor por defecto deliberadamente: un checkout recién clonado no
llama a ninguna red hasta que alguien lo configura para hacerlo.

## Configuración

```dotenv
LLM_PROVIDER=transformers-lora
LLM_MODEL=
LLM_BASE_URL=
LLM_API_KEY=
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2048
```

Las claves viven en `.env`, que no se versiona, y nunca en el código, en los
notebooks ni en los registros de experimento.

## Lo que el modelo recibe

Diagnóstico del modelo especializado, su confianza, evidencia observacional,
atribución, fragmentos recuperados con sus puntuaciones y la decisión de
suficiencia ya tomada.

## Lo que el modelo puede y no puede hacer

**Puede:** explicar, organizar la evidencia, relacionar observaciones y producir
lenguaje natural legible.

**No puede:** inventar valores OBD-II, inventar referencias, inventar
puntuaciones, crear evidencia que no exista, ni aportar su conocimiento
paramétrico como si fuera una fuente.

Esto no se confía a la buena voluntad del prompt. La salida se valida contra un
esquema, cada referencia se resuelve contra el corpus real, y una referencia que
no resuelve invalida la afirmación que la invoca.
