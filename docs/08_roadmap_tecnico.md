# 8. Roadmap técnico del prototipo

> **Actualización F20:** ingeniería de datos y de benchmark, sin reentrenar modelos.
> (1) **RNG separado** (ADR-0034): `vehicle_behavior_seed` y `anomaly_injection_seed`, de
> modo que los contrafactuales son exactos por construcción y v1 se preserva byte a byte.
> (2) **Synthetic Benchmark v2**: expansión de cobertura DIRIGIDA por los huecos medidos
> en F19 y derivada del mecanismo (el cruce de cuantización del LTFT exige duración, no
> más sesiones) — los cuatro huecos se cierran; v1 y el test histórico intactos.
> (3) **Ground truth verificable**: declara exactamente los PIDs que la inyección altera.
> (4) **ADR-0035 library-first** como regla permanente, `pandas` retirado y entorno de
> entrenamiento explícito (`make install-train`, `make check-train-env`). Siguiente:
> congelar el benchmark v2 y abrir la **réplica** (LOF + AE denso + temporal si procede).
>
> **Actualización F19:** la auditoría AUDIT-DATA-001 cierra la duda abierta en F18: **las
> anomalías sintéticas SÍ son distinguibles** (7/8 DETECTABLE o WEAKLY sin usar
> detectores), así que los ceros de recall en anomalías lentas son limitación de los
> detectores y no del banco. Lo que sí falla es la **cobertura de normalidad** (4 huecos,
> con el cruce de cuantización del LTFT ausente en train v1.0) y tres **ground truths**
> de atribución. Decisiones: A = INSUFFICIENT · B = PARTIAL · C = BOTH. La línea ML
> continúa en **F20 — Normal Coverage Expansion + Synthetic Benchmark v2** (cobertura
> definida a priori, corrección de GT, escenarios con fallos cortos para recuperar
> TAR@K); los modelos se replican DESPUÉS. Regla nueva del protocolo: clasificar todo
> resultado negativo como `model failure` / `dataset coverage failure` /
> `anomaly construction failure` antes de atribuirlo.
>
> **Actualización F18:** EXP-ANOM-009 **refuta HX-ML-3** (los AE recurrentes son peores
> que los estáticos y que LOF) y, con su brazo control, **demuestra cuál era el techo
> real de toda la serie EXP-ANOM-006/007/008/009: la cobertura de normalidad**. El FPR
> de la familia AE proviene íntegramente de un evento discreto legítimo y raro — la
> transición de cuantización del LTFT — que apenas aparecía en train; al cubrirlo, el
> mismo AE denso pasa de FPR 0.129 a 0.022 y supera a LOF en F1. La línea ML deja por
> tanto de buscar arquitecturas y pasa a **(1) replicar esa cobertura de forma
> independiente del diagnóstico** (primera adopción posible de un AE) y **(2) auditar la
> inyección de anomalías lentas**, que ningún modelo de la serie detecta. Secuenciales
> profundos: REJECTED; TCN/Transformer NO se abren (regla de parada). Las dependencias
> externas (A2/A3, HCRL, freeze del pre-registro) siguen vigentes — y HCRL gana una
> pregunta concreta: ¿existe el patrón de cuantización fuera del emulador?
>
> **Actualización F17:** la ablation EXP-ANOM-008 cierra la vía de features estáticas
> (fs2-lite = KEEP fs1; causa refinada: evento de adaptación del LTFT cuantizado, raro
> en train — contexto temporal) → la línea ML continúa en **EXP-ANOM-009 (modelos
> temporales, LSTM/GRU-AE, HX-ML-3)**. Quedan registradas como **tareas de dependencia
> EXTERNAS, separadas de los experimentos y en el lado del autor** (su ausencia NO
> bloquea la fase exploratoria, pero mantiene la validez declarada en «entorno
> emulado/sintético», sin validez externa): **A2/A3** — validación ARM64/Raspberry Pi 5
> (nada se declara validado en edge hasta ejecutarla); **HCRL** — descarga y replay del
> dataset real (primera evidencia fuera del simulador; re-examen de la sonda de
> cuantización y del fingerprint sintético); **pre-registro** — reconciliación y freeze
> de prereg-v1.0 (condición previa a CUALQUIER experimento confirmatorio, regla F10).
>
> **Actualización F15:** **XAI transversal** ([Adenda XAI v1](experiments/protocolo_ml_v1_adenda_xai.md),
> ADR-0033): la explicabilidad pasa de producirse a EVALUARSE en cada experimento de la
> línea ML (métricas de atribución contra el ground truth de inyección, estabilidad,
> agreement, decisiones D1/D2/D3). Progresión de la línea: F13 (fundación wide) →
> EXP-ANOM-006 (AE + severidad; D1 REJECT / D2·D3 needs-more-evidence) → EXP-ANOM-007
> (AE + train v1.1 **+ evaluación XAI completa**) → representación candidata →
> EXP-PAT-* (descubrimiento + pattern-level XAI: qué variables y momentos caracterizan
> cada patrón candidato) → RAG + memoria → hipótesis del agente (capa b) → validación.
> La atribución temporal feature×tiempo queda contemplada para el nivel secuencial (T3).

> **Actualización F13:** se abre la **línea experimental ML sobre la representación wide**
> ([Protocolo ML v1](experiments/protocolo_ml_v1.md), ADR-0031): el
> `VehicleTelemetrySnapshot` queda validado como entrada canónica de ML por paridad exacta
> con el pipeline de F3 (EXP-ANOM-005), y T3 se extiende con una progresión exploratoria
> por niveles — AE denso (EXP-ANOM-006) → LSTM/GRU-AE (EXP-ANOM-007, condicionado) →
> embeddings + HDBSCAN para descubrimiento de patrones (EXP-PAT-001/002) — manteniendo la
> condición de adopción de ADR-0011 (superar a LOF en held-out con FPR ≤) y el presupuesto
> edge como criterio de viabilidad. T8 hereda las hipótesis HX-ML-* como banco
> exploratorio; los confirmatorios siguen bloqueados hasta congelar el pre-registro.

> **Actualización F5:** T5–T7 evolucionan al **Edge Agent Runtime multiagente**
> ([docs/agent-runtime/](agent-runtime/README.md), ADR-0015…0018). Prioridades MUST/SHOULD/
> COULD y plan incremental: [informe F5](fase5/informe_impacto_runtime.md). T8 adopta el
> diseño experimental A0–A6 (agent-runtime/12). El resto (T0–T4, T9) permanece vigente.

> **Actualización F6:** se añade la capa **Event Intelligence**
> ([docs/event-intelligence/](event-intelligence/README.md), ADR-0019…0021): eventos
> vehiculares como unidad formal de análisis, baselines por contexto y anomalías
> contextuales (`anomaly_scope=EVENT`) que COEXISTEN con el pipeline de ventanas de F3.
> El experimento ventana-vs-evento entra en T8 como dimensión `anomaly_mode`
> (event-intelligence/11). Detalle: [informe F6](fase6/informe_event_intelligence.md).

> **Actualización F7:** estrategia formal de **gobernanza de modelos**
> ([docs/models/](models/README.md), ADR-0022…0024): registry + model cards + ciclo de
> vida + benchmark LLM interno + reproducibilidad. Los resultados F3 quedan importados
> al registro sin recalcular; T2/T6/T8 heredan el protocolo de evaluación y el
> versionado en 4 ejes. Detalle: [informe F7](fase7/informe_estrategia_modelos.md).

> **Actualización F10:** transición a validación científica: EXP-ANOM-001/002/003
> clasificados EXPLORATORY; protocolo confirmatorio de H-EVT **pre-registrado y
> congelado** ([PROTO-CONF-001](experiments/preregistered/PROTO-CONF-001.md)) con brazos
> checksumados (arms-freeze-v1) y datos confirmatorios ocultos (suite_conf_v1, seeds
> 901-925); arquitectura de detección dual documentada
> ([deteccion-dual](diagrams/deteccion-dual.mmd)): LOF primario + eventos complementario
> + fusión OR auditable configurable. Nomenclatura vigente: familias H-*
> ([correspondencia](correspondencia_nomenclatura.md)).

Secuencia de construcción con dependencias, criterios de "hecho" y orden pensado para que **siempre exista un sistema demostrable de extremo a extremo**, que se enriquece en cada paso (enfoque de esqueleto andante).

## 8.1 Estructura de repositorio propuesta

```
mecanico-ia/
├── docs/                      # esta planificación + ADRs + protocolo experimental
│   └── adr/                   # Architecture Decision Records (D1, D2, ...)
├── docker/
│   ├── compose.yml            # perfiles: dev (x86 limitado) / arm64 / experiments
│   └── edge.Dockerfile
├── src/mecanico_ia/
│   ├── vehicle_sim/           # C1: generador de escenarios + integración emulador ELM327
│   ├── acquisition/           # C2: cliente OBD + TransportLayer (serial|tcp|bt)
│   ├── storage/               # C3: modelos SQLAlchemy, repositorios, migraciones
│   ├── anomaly/               # C4: features de ventana, detectores, evaluación
│   ├── rag/                   # C5a: ingesta, chunking, índice, retriever
│   ├── memory/                # C5b: memoria de casos episódica
│   ├── agent/                 # C6: grafo LangGraph, nodos, herramientas, esquemas
│   ├── api/                   # C7: FastAPI, routers, UI estática mínima
│   └── config.py              # configuración tipada (pydantic-settings)
├── experiments/               # scripts reproducibles por hipótesis (h1_*, h2_*, ...)
├── data/                      # (gitignored) telemetría; corpus/ con manifiesto de licencias
├── tests/
└── pyproject.toml             # deps fijadas; ruff + mypy + pytest
```

## 8.2 Etapas técnicas

**T0 — Andamiaje (Fase 1).** Repo, pyproject, calidad (ruff/mypy/pytest/pre-commit), CI, compose con perfiles. *Hecho cuando:* CI verde en commit inicial; `docker compose --profile dev up` arranca.

**T1 — Vehículo emulado (Fase 1–2).** Evaluación del emulador ELM327 (¿expone los PIDs del subconjunto? ¿acepta valores dinámicos inyectados?). Generador de escenarios: modelo simple de dinámica de señales (perfiles de conducción por fases: ralentí/urbano/carretera, con ruido realista y correlaciones básicas entre PIDs) + capa de inyección de fallos que perturba señales según los modelos de fallo de IN-8. *Decisión R3 al final de la semana 1.* *Hecho cuando:* un script reproduce por semilla una sesión normal y una con fallo, visibles vía cliente OBD.

**T2 — Adquisición + persistencia (Fase 2).** `TransportLayer` (serial pty / tcp), sondeo asíncrono configurable, validación de rangos, escritura por lotes a SQLite. *Hecho cuando:* sesión de 30 min emulada persistida con < 1 % de pérdidas y esquema documentado.

**T3 — Detección (Fase 2).** Extracción de features por ventana deslizante (estadísticos por PID + derivadas + correlaciones seleccionadas); baseline z-score robusto; Isolation Forest; autoencoder (si sobrevive al recorte 4) exportado a ONNX. Entrenamiento solo con sesiones normales; evaluación sobre escenarios held-out. *Hecho cuando:* tabla comparativa F1/AUC/latencia/RAM generada por script.

**T4 — RAG (Fase 2).** Ingesta del corpus con manifiesto de licencias, chunking, embeddings, ChromaDB persistente, retriever con filtrado por metadatos (tipo de documento, sistema del vehículo). Set de consultas de evaluación. *Hecho cuando:* hit-rate/MRR medidos y fragmentos inspeccionados.

**T5 — Agente (Fase 3).** Esquemas Pydantic de estado y salida; nodos `triage → recall → retrieve → hypothesize → verify → report → memorize`; herramientas tipadas; trazas persistidas en SQLite; validación estructural con reintento acotado; configuración dual de LLM (Ollama local / API cloud) tras una misma interfaz. *Hecho cuando:* sobre el escenario "fuga de vacío", el agente produce diagnóstico estructurado citando la evidencia (PIDs y fragmentos RAG usados).

**T6 — Memoria de casos (Fase 3).** Esquema de caso (firma de anomalía + embedding + diagnóstico + desenlace); escritura al cerrar diagnóstico; recuperación por similitud en `recall`; política simple de consolidación (contador de refuerzo). *Hecho cuando:* la segunda ejecución de un escenario repetido recupera el caso de la primera y la traza lo muestra.

**T7 — API + UI (Fase 3).** Routers de telemetría/anomalías/diagnósticos/casos; SSE o polling para estado en vivo; página web mínima (estado del vehículo, alertas, diagnóstico legible con evidencia desplegable). *Hecho cuando:* demo de extremo a extremo navegable en el navegador.

**T8 — Banco experimental (Fase 4).** Scripts `experiments/h{1..4}_*.py` que ejecutan cada hipótesis de principio a fin con semillas y vuelcan CSV + figuras. Perfilado de recursos (memoria pico, latencia por etapa) en el perfil RPi. *Hecho cuando:* `make experiments` regenera todos los resultados de la memoria.

**T9 — Endurecimiento y reproducibilidad (Fase 5).** README de reproducción, imagen arm64 verificada, limpieza, demo grabada. *Hecho cuando:* una persona ajena puede levantar el sistema y reproducir un experimento siguiendo solo el README.

## 8.3 Dependencias entre etapas

```
T0 ─▶ T1 ─▶ T2 ─▶ T3 ─────────────┐
        │                          ├─▶ T5 ─▶ T6 ─▶ T7 ─▶ T8 ─▶ T9
        └─────────▶ T4 ────────────┘
```
T4 (RAG) es paralelizable con T2–T3. T5 no arranca sin T3 y T4 mínimos, pero puede empezar con un detector provisional (baseline z-score) si T3 se retrasa — otra ventaja del esqueleto andante.

## 8.4 Prácticas transversales

- **ADRs:** cada decisión arquitectónica relevante (D1–D6 y las que surjan) se registra en `docs/adr/` con contexto, opciones y justificación; se vuelcan luego a la memoria.
- **Reproducibilidad:** toda aleatoriedad con semilla; versiones fijadas; datos regenerables por script.
- **Protocolo experimental publicado a priori** (E3) antes de ejecutar los experimentos de la Fase 4, para blindar RI1/RI4.
- **Trazabilidad requisito→código→experimento→sección de la memoria:** tabla mantenida en `docs/` desde la Fase 2.
