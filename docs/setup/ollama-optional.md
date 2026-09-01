# Ollama — soporte opcional de portabilidad

## Qué papel tiene, y cuál no

Ollama permite que un tercero ejecute el pipeline completo con un modelo de
lenguaje local, sin dar de alta una cuenta ni gastar en llamadas a una API. Ese
es todo su papel: **portabilidad**.

Ollama **no** es el modelo oficial de experimentación. En concreto:

- no se ejecuta durante los experimentos oficiales;
- sus resultados no se mezclan con los oficiales, ni en tablas ni en figuras;
- no es un requisito de instalación;
- el laboratorio no descarga modelos automáticamente en ningún momento.

Un resultado producido con Ollama se etiqueta como tal en el registro del
experimento y se reporta por separado.

## Uso

Con Ollama instalado en el sistema, o mediante el perfil de contenedor:

```bash
docker compose --profile ollama up -d
```

Descarga del modelo, **de forma explícita y manual**:

```bash
ollama pull llama3.1:8b
```

Configuración:

```dotenv
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.0
```

## Qué esperar

Un modelo local pequeño produce salida estructurada con menos fiabilidad que un
modelo remoto grande: es más probable que incumpla el esquema y que necesite
reintentos. Eso afecta a la tasa de salidas válidas, no a la validez del diseño:
la decisión de explicar o abstenerse la toma un componente determinista fuera del
modelo de lenguaje, y las referencias se verifican contra el corpus real
independientemente de quién haya redactado el texto.

Dicho de otro modo: cambiar de modelo cambia la calidad de la redacción, no las
reglas de la evidencia.
