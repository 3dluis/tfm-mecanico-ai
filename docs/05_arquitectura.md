# 5. Arquitectura de alto nivel, componentes y tecnologías

## 5.1 Visión general

Arquitectura híbrida edge-cloud con **autonomía total del edge** como principio rector: todo el ciclo captura → detección → diagnóstico → memoria funciona sin conectividad; la nube añade capacidades (LLM mayor como *baseline*/escalado, respaldo de la memoria) pero nunca es requisito.

```
┌─────────────────────────── EDGE (Raspberry Pi / contenedor emulado) ───────────────────────────┐
│                                                                                                 │
│  Vehículo emulado                 Núcleo de diagnóstico                    Servicio             │
│ ┌────────────────┐   PIDs   ┌──────────────────────────────┐        ┌──────────────────┐        │
│ │ Emulador       │────────▶│ 1. Adquisición (python-OBD)   │        │ 6. API REST      │        │
│ │ ELM327         │  serie/  │    capa transporte plugable  │        │    (FastAPI)     │        │
│ │ + escenarios   │  TCP     ├──────────────────────────────┤        └────────┬─────────┘        │
│ │ de fallo       │          │ 2. Persistencia (SQLite)     │◀────────────────┘                  │
│ └────────────────┘          │    telemetría + casos        │        ┌──────────────────┐        │
│                             ├──────────────────────────────┤        │ 7. UI mínima     │        │
│                             │ 3. Detección de anomalías    │        │ (web / Flutter)  │        │
│                             │    (ventanas, no supervisado)│        └──────────────────┘        │
│                             ├──────────────────────────────┤                                    │
│                             │ 4. Agente LangGraph          │   ┌────────────────────────┐       │
│                             │    + LLM local (Ollama)      │──▶│ 5a. RAG (pgvector,     │       │
│                             │    + verificación de soporte │   │  corpus con manifiesto)│       │
│                             │    + política de abstención  │──▶│ 5b. Memoria de casos   │       │
│                             └───────────────┬──────────────┘   │  (fuera de alcance)    │       │
│                                             ▼                  └────────────────────────┘       │
│                            ¿evidencia suficiente? sí → explicación trazable                     │
│                                                   no → abstención declarada                     │
└───────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                        │ opcional, asíncrono
┌───────────────────────────────────────▼─────────────────────────────────────────────────────────┐
│ CLOUD (opcional): LLM mayor (baseline comparativo) · respaldo/exportación de memoria de casos    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Componentes principales

**C1 — Emulador de vehículo.** Emulador ELM327 por software más un *generador de escenarios* propio que define perfiles de conducción (arranque en frío, urbano, carretera) y modelos de fallo parametrizados (deriva de MAF, fuga de vacío→fuel trims positivos, termostato atascado→refrigerante que no alcanza temperatura, sonda O2 lenta, fallo de encendido intermitente). Cada escenario es reproducible por semilla. *Este componente es también instrumento experimental: la definición de los modelos de fallo se documenta y justifica con los trabajos técnicos revisados.*

**C2 — Adquisición.** Cliente OBD-II (python-OBD) con capa de transporte plugable (`serial | tcp | bluetooth-rfcomm`), sondeo de PIDs a frecuencia configurable (nominal 1 Hz), validación de rangos y cola de escritura a persistencia.

**C3 — Persistencia.** SQLite en el edge: tablas de sesiones, muestras de telemetría, eventos/DTC, diagnósticos emitidos y casos de la memoria. Esquema versionado con migraciones simples.

**C4 — Detección de anomalías.** Ventanas deslizantes multivariante; candidatas a comparar: Isolation Forest y autoencoder ligero (ONNX para inferencia); baseline estadístico (z-score robusto por PID) como referencia mínima. Produce *eventos de anomalía* con los PIDs implicados y la desviación.

**C5a — RAG.** Corpus técnico de licencia compatible → chunking → embeddings (sentence-transformers multilingüe compacto) → ChromaDB local. Recuperación híbrida si el tiempo lo permite (denso + BM25).

**C5b — Memoria evolutiva de casos.** *(Fuera del alcance experimental, ADR-0036: se conserva funcional y documentada, pero no se evalúa; ver `docs/alineacion_v4/05_fuera_de_alcance.md`.)* Registro estructurado de cada diagnóstico: síntomas (vector de características de la anomalía + embedding textual), hipótesis, diagnóstico final, retroalimentación si existe. Recuperación por similitud al iniciar un diagnóstico nuevo; el agente decide si el caso pasado aplica. Es una memoria episódica con consolidación simple (casos repetidos elevan la confianza del patrón).

**C6 — Agente de diagnóstico (LangGraph).** Grafo explícito con nodos: `triage` (¿anomalía + DTC? ¿solo anomalía?) → `recall` (memoria de casos; desactivable) → `retrieve` (RAG sobre el corpus con manifiesto) → `hypothesize` (generación de la explicación candidata con LLM) → `verify` (contraste determinista contra las features de la ventana) → **`decide`** (descomposición de la explicación en afirmaciones atómicas, verificación del soporte de cada una contra la evidencia recuperada, y decisión de suficiencia) → `report` (explicación diagnóstica trazable **o** abstención declarada indicando qué evidencia faltó) → `memorize` (escritura en memoria; fuera del alcance experimental y desactivable). El estado del grafo y las trazas se persisten para explicabilidad y para la evaluación.

**El nodo `decide` es el núcleo científico del sistema** (ADR-0036). Una afirmación se considera sostenida cuando su referencia resuelve a un fragmento realmente recuperado cuyo contenido la respalda, o a una feature existente del vector de la ventana; y una explicación se emite solo cuando alcanza el umbral de soporte **y** el verificador confirma la firma en la telemetría —doble anclaje documental y telemétrico—. En caso contrario el sistema se abstiene. La abstención es una salida correcta, no un fallo. Los tres brazos del experimento central se obtienen configurando este nodo y la recuperación: sin RAG (B1), con RAG y sin verificación ni abstención (B2), y completo (B3).

**C7 — API REST (FastAPI).** Endpoints: estado actual, telemetría, eventos de anomalía, diagnósticos, casos de memoria, disparo manual de diagnóstico. OpenAPI autogenerado.

**C8 — UI mínima.** Prioridad: web simple servida por FastAPI (estado, alertas, diagnóstico legible). Flutter solo como OS1.

**C9 — Servicios cloud (opcional).** Endpoint de LLM mayor para el experimento comparativo H4/L6 y exportación de memoria. Sin sincronización compleja en el alcance core.

## 5.3 Decisiones de arquitectura clave (con justificación)

**D1 — Emulación dual de la Raspberry Pi.** (a) Imagen `linux/arm64` construida con buildx/QEMU: valida que todas las dependencias tienen ruedas ARM64 y que el software *funciona* en la arquitectura destino. (b) Contenedor nativo x86 con `--cpus=4 --memory=8g` (perfil RPi 5): usado para desarrollo y para mediciones de rendimiento *aproximadas*, porque QEMU degrada el rendimiento de forma no representativa. Ambos perfiles en el mismo `docker-compose`. Justificación: separar *compatibilidad* (a) de *rendimiento* (b) es la única forma metodológicamente honesta de emular sin hardware; la limitación se declara (L2).

**D2 — Bluetooth abstraído, no emulado.** Emular RFCOMM dentro de Docker exige BlueZ + hardware o mocks frágiles; el valor experimental es casi nulo porque python-OBD trata el adaptador como puerto serie en cualquier caso. Se define la interfaz `TransportLayer` y se implementan `serial` (pty del emulador) y `tcp`; `bluetooth-rfcomm` queda especificada y sin implementar. Justificación: mismo contrato de E/S, riesgo eliminado, honestidad metodológica (L3).

**D3 — SQLite y no PostgreSQL en el edge.** Un solo escritor, footprint mínimo, cero administración, fiabilidad probada en dispositivos embebidos. PostgreSQL solo aportaría concurrencia y tipos avanzados que este caso no necesita. Si el proyecto escalara a flota multiusuario (fuera de alcance), la capa de persistencia está aislada tras un repositorio para permitir el cambio.

**D4 — ChromaDB como base vectorial inicial.** API simple, persistencia local en disco, integración directa con LangChain. FAISS es la alternativa si el overhead de Chroma resulta medible en el perfil de recursos (R6); la elección definitiva se toma con datos en la Fase 2 y se documenta como micro-benchmark en la memoria.

**D5 — LangGraph y no cadena LangChain plana.** El diagnóstico requiere control de flujo condicional (¿hay DTC?, ¿hay caso similar?, ¿la hipótesis se verifica?), reintentos y estado persistente. Un grafo explícito además *es* el artefacto de explicabilidad: cada nodo deja traza. Justificación adicional: alinea con el objetivo académico de explicar el razonamiento, no solo el resultado.

**D6 — LLM local pequeño + validación estructural.** Candidatos iniciales: Qwen2.5 3B, Gemma 2 2B, Phi-3.5-mini (cuantizados Q4 en Ollama), a confirmar con un *smoke test* de generación estructurada en la Fase 2 (las versiones concretas disponibles se verificarán entonces). Toda salida del LLM pasa por esquema Pydantic con reintento acotado. Justificación: L6 y R4.

## 5.4 Stack tecnológico recomendado

| Capa | Tecnología | Justificación breve |
|---|---|---|
| Lenguaje | Python 3.11+ | Ecosistema IA; tipado gradual con mypy |
| Emulación vehículo | ELM327-emulator (a validar) + generador propio | R3: el generador propio es el respaldo |
| Cliente OBD | python-OBD | Estándar de facto, maneja ELM327 |
| Edge runtime | Docker + compose; perfiles arm64 y x86-limitado | D1 |
| Detección | scikit-learn (IForest), PyTorch→ONNX (autoencoder), numpy | Coste computacional bajo, inferencia ONNX en ARM |
| LLM local | Ollama + modelo 1–4 B cuantizado | D6 |
| Agente | LangGraph (+ LangChain solo donde aporte) | D5 |
| Embeddings | sentence-transformers compacto multilingüe | Corpus en español/inglés |
| Vector store | ChromaDB (FAISS como alternativa medida) | D4 |
| BD | SQLite (+ SQLAlchemy) | D3 |
| API | FastAPI + Pydantic v2 | OpenAPI gratis, validación |
| UI | HTML/JS mínimo servido por FastAPI; Flutter = OS1 | R1 |
| Calidad | pytest, ruff, mypy, pre-commit, GitHub Actions mínimo | R5, R7 |
| Experimentos | Notebooks + scripts reproducibles con semillas; resultados en CSV versionados | RI1 |

**Descartes justificados:** LlamaIndex (solapa con LangChain/Chroma, dos frameworks RAG duplican superficie de fallo); PostgreSQL (D3); TinyLlama como candidato principal (generación estructurada previsiblemente insuficiente frente a los 2–3 B modernos; puede incluirse en el benchmark como punto bajo de la curva capacidad/recursos).
