# 9. Arquitectura del monorepo multi-dominio (v1)

**Fecha:** 2026-08-12 · **Sustituye parcialmente a:** docs/05 (que sigue vigente en lo conceptual)
**Origen:** ajuste de plan solicitado por el autor: desarrollo y investigación en paralelo,
Docker desde el inicio, cinco dominios + contratos compartidos.

---

## 9.1 Evaluación de la arquitectura propuesta

La propuesta de cinco dominios es correcta y madura. Sus tres aciertos principales:

1. **Separar `ai-models` (entrenamiento) de `diagnostic-agent` (inferencia)** materializa el
   desacoplamiento entrenamiento/inferencia que la literatura de edge ML recomienda y que ya
   estaba implícito en docs/05: el edge nunca entrena, solo ejecuta artefactos exportados.
2. **Elevar `obd-lab` a dominio propio** convierte el generador de escenarios en un artefacto
   independiente, instalable y citable — condición necesaria para que sea contribución técnica
   de la investigación (C4 de docs/06). Un laboratorio separado también permite usarlo contra
   un futuro vehículo real como *grabador* (mismo contrato, fuente distinta).
3. **Contratos compartidos** eliminan el acoplamiento punto a punto: cada dominio depende de
   `shared`, nunca de otro dominio.

Riesgos de la propuesta, con su tratamiento:

- **R-arq1. Amplitud vs. plazo.** Cinco dominios invitan a repartir esfuerzo uniformemente;
  el cronograma no lo permite. Tratamiento: los cinco se *estructuran* ahora (coste ~1 día),
  pero la implementación funcional sigue el orden del roadmap: obd-lab → diagnostic-agent →
  ai-models → cloud-platform (mínimo) → mobile-app (si hay tiempo, OS1). El scaffolding de
  mobile-app y cloud-platform queda listo para no bloquear, no para desarrollarse ya.
- **R-arq2. Sobre-ingeniería de la nube.** Mitigado por decisión explícita: FastAPI + PostgreSQL
  + docker compose, sin Kubernetes, sin colas, sin microservicios (ADR-0006). La "distribución
  de modelos" es un endpoint de descarga con manifiesto, no un sistema MLOps.
- **R-arq3. Contratos en dos lenguajes (Python/Dart).** Mitigado con una única fuente de verdad
  (Pydantic v2) y exportación automática a JSON Schema, desde donde Flutter genera sus modelos.
  Nunca se escriben contratos a mano dos veces (ADR-0007).

## 9.2 Componentes faltantes identificados (y su tratamiento)

| Falta | Por qué importa | Tratamiento |
|---|---|---|
| **Versionado de contratos** | Edge, cloud y móvil evolucionan a ritmos distintos | Campo `schema_version` en todos los mensajes; carpeta `shared/schemas/` versionada en git |
| **Identidad de dispositivo** | La sincronización y la memoria necesitan saber *qué vehículo/dispositivo* | Contratos `device_id`/`vehicle_id` desde el día 1; provisión simple por archivo de config en el TFM |
| **Manifiesto de modelo** | "Mover un modelo a la RPi" sin metadatos (versión, métricas, hash, ventana, features) es ingobernable | Contrato `ModelManifest` + convención de empaquetado (§9.7) |
| **Observabilidad mínima** | H4 exige medir latencia/memoria; sin logs estructurados no hay análisis de errores | Logging estructurado (JSON) común vía `shared`; métricas de tiempo por nodo del agente en las trazas |
| **Protocolo de sincronización definido** | "Sincronización Edge-Cloud" es ambigua | Patrón *outbox* en el edge: cola local de eventos → push idempotente por lotes cuando hay red; last-write-wins con marca temporal; sin sincronización bidireccional compleja en el TFM |
| **Descubrimiento del edge por el móvil** | "Comunicarse directamente con la Raspberry Pi" | v1: IP configurada manualmente en la app; mejora futura: mDNS. Documentado, no implementado |
| **Semillas y reproducibilidad transversal** | Los experimentos cruzan obd-lab ↔ ai-models ↔ agent | `RunConfig` con semilla en contratos de obd-lab; toda sesión generada registra su config |
| **Seguridad mínima** | API expuestas | Token estático en edge (LAN), API key en cloud; TLS delegado al despliegue. Declarado como fuera de alcance endurecerlo |

## 9.3 Mejoras propuestas (aceptadas en este diseño)

1. **obd-lab como "grabador/reproductor" universal:** además de emular, define el formato de
   *sesión grabada* (JSONL de OBDReading). Reproducir un dataset real (HCRL) y un escenario
   sintético produce el mismo artefacto → los consumidores no distinguen la fuente. Esto
   refuerza la defensa contra la circularidad (RI1) y hace el laboratorio citable por terceros.
2. **El agente consume modelos, no librerías de ML:** `diagnostic-agent` solo conoce ONNX Runtime
   y el `ModelManifest`; scikit-learn/PyTorch viven únicamente en `ai-models`. Esto reduce la
   imagen edge y hace real el desacoplamiento.
3. **Separación estricta ML/LLM reflejada en paquetes:** en `diagnostic-agent`, `detection/`
   (matemático: scoring, features, ONNX) y `reasoning/` (LLM: grafo, RAG, memoria) no se
   importan entre sí; se comunican por contratos (`DetectedAnomaly` entra al agente como dato).
   El LLM jamás decide si hay anomalía; explica y diagnostica anomalías ya detectadas.
4. **`experiments/` vive en `ai-models`** (es investigación), pero los escenarios que usa se
   declaran en `obd-lab/scenarios/` y los resultados finales se copian a `docs/` para la memoria.

## 9.4 Dependencias entre proyectos

```
                +----------- shared (contratos) -----------+
                |        |          |           |          |
            obd-lab  ai-models  diagnostic-  cloud-     mobile-app
                        |          agent      platform   (vía JSON Schema)
                        |            |           |
   (artefactos ONNX + manifest) ----->           |
                                     | <--- distribución de modelos (pull)
                                     +---------> sincronización (push outbox)
```

Reglas: (1) todo dominio depende solo de `shared`; (2) los artefactos (modelos, sesiones
grabadas, corpus) cruzan dominios por el sistema de archivos o por API, nunca por import;
(3) `mobile-app` no importa Python: consume JSON Schemas generados desde `shared`.

## 9.5 Estructura completa del monorepo

```
mecanico-ia/
├── Makefile                      # comandos canónicos (dev, research, edge, cloud, full, check…)
├── docker-compose.yml            # raíz: 5 perfiles, servicios de todos los dominios
├── .env.example
├── pyproject.toml                # raíz: SOLO tooling compartido (ruff, mypy, pytest) — sin código
├── docs/                         # planificación, ADRs, estado del arte, informes, diagramas
├── shared/                       # ÚNICA dependencia común
│   ├── pyproject.toml            #   paquete: mecanico_contracts
│   ├── src/mecanico_contracts/   #   Pydantic v2: mensajes, enums, versionado
│   ├── schemas/                  #   JSON Schema exportados (fuente para Flutter)
│   └── tests/
├── obd-lab/                      # laboratorio de simulación OBD-II
│   ├── pyproject.toml            #   paquete: obd_lab (CLI: obd-lab)
│   ├── src/obd_lab/
│   │   ├── emulator/             #   integración ELM327-emulator (pty/TCP), escenario "mecanico"
│   │   ├── scenarios/            #   perfiles de conducción + modelos de fallo parametrizados
│   │   ├── injection/            #   inyección de fallos en caliente
│   │   ├── replay/               #   reproducción de datasets reales (HCRL…) y sesiones grabadas
│   │   └── recording/            #   formato de sesión (JSONL de OBDReading) + writer
│   ├── scenarios/                #   escenarios declarativos (YAML) versionados
│   └── tests/
├── ai-models/                    # investigación y entrenamiento (NUNCA corre en edge)
│   ├── pyproject.toml            #   paquete: ai_models
│   ├── src/ai_models/
│   │   ├── data/                 #   carga de sesiones obd-lab y datasets públicos
│   │   ├── preprocessing/        #   limpieza, resampling, ventanas
│   │   ├── features/             #   feature engineering (compartir definición con manifest)
│   │   ├── anomaly/              #   IForest, autoencoder, baseline; entrenamiento y selección
│   │   ├── clustering/           #   agrupación de patrones (apoyo a memoria/casos)
│   │   ├── evaluation/           #   métricas (F1 por eventos sin PA), comparación
│   │   └── export/               #   exportación ONNX + cuantización + ModelManifest
│   ├── notebooks/
│   ├── experiments/              #   h1_…h4_ reproducibles por semilla
│   └── models/                   #   (gitignored) artefactos producidos
├── diagnostic-agent/             # núcleo inteligente EDGE
│   ├── pyproject.toml            #   paquete: diagnostic_agent
│   ├── src/diagnostic_agent/
│   │   ├── acquisition/          #   cliente OBD + TransportLayer (serial|tcp|bt) [de Fase 1]
│   │   ├── telemetry/            #   normalización, buffer, ventanas
│   │   ├── detection/            #   ML: features runtime + inferencia ONNX + scoring  ─┐
│   │   ├── reasoning/            #   LLM: grafo LangGraph, RAG, memoria, hipótesis      │ separación
│   │   │   ├── graph/            #   triage→recall→retrieve→hypothesize→verify→report   │ estricta
│   │   │   ├── rag/              #   Chroma + embeddings                                │ ML / LLM
│   │   │   ├── memory/           #   casos episódicos + evolución                      ─┘
│   │   │   └── llm/              #   cliente Ollama/cloud tras una interfaz
│   │   ├── storage/              #   SQLite: telemetría, eventos, diagnósticos, casos, outbox
│   │   ├── sync/                 #   outbox → cloud (push idempotente)
│   │   ├── models_runtime/       #   carga de ModelManifest + ONNX Runtime
│   │   └── api/                  #   FastAPI local (LAN) + UI mínima
│   └── tests/
├── cloud-platform/               # nube complementaria (simple a propósito)
│   ├── pyproject.toml            #   paquete: cloud_platform
│   ├── src/cloud_platform/
│   │   ├── auth/                 #   API keys / tokens simples
│   │   ├── registry/             #   usuarios, vehículos, dispositivos
│   │   ├── telemetry/            #   histórico (ingesta desde outbox edge)
│   │   ├── diagnostics/          #   diagnósticos sincronizados
│   │   ├── knowledge/            #   conocimiento documental (corpus compartible)
│   │   ├── model_registry/       #   manifiestos + artefactos + endpoint de distribución
│   │   └── api/                  #   FastAPI
│   ├── migrations/
│   └── tests/
├── mobile-app/                   # Flutter (offline-first; edge directo + cloud complementaria)
│   ├── README.md                 #   arquitectura y decisión de datos (v1: solo scaffolding)
│   └── (flutter create pospuesto a su fase)
└── tools/                        # utilidades transversales (eval_emulator.py de Fase 1…)
```

## 9.6 Servicios: qué corre dónde

| Servicio | Edge (RPi) | Cloud | Dev (Mac/Docker) |
|---|---|---|---|
| Emulador/lab OBD | — (vehículo real) | — | ✅ obd-lab |
| Adquisición + detección ML + agente + RAG + memoria + SQLite + API local | ✅ | — | ✅ (contenedor `agent`) |
| Ollama (LLM local) | ✅ | opcional (baseline mayor) | ✅ |
| Vector store (Chroma embebido) | ✅ dentro del agente | — | ✅ |
| API cloud + PostgreSQL + model registry + conocimiento | — | ✅ | ✅ (perfil cloud/full) |
| Entrenamiento / notebooks / experimentos | ❌ nunca | opcional | ✅ (perfil research) |
| App móvil | — | — | dispositivo/simulador (fuera de compose) |

## 9.7 Ciclo de vida de un modelo: del entrenamiento a la Raspberry Pi

1. **Generación de datos** (`obd-lab`): escenarios YAML → sesiones JSONL (semilla fija) + datasets reales reproducidos al mismo formato.
2. **Entrenamiento** (`ai-models`, Mac/cloud): preprocesado → features (definición serializada) → entrenamiento IForest/AE → evaluación con protocolo E3 (F1 por eventos, held-out).
3. **Exportación** (`ai-models/export`): modelo → ONNX (+ cuantización INT8 si AE) → empaquetado `model-<nombre>-<semver>/` con `manifest.json` (`ModelManifest`: versión, tipo, hash sha256, features esperadas, ventana, umbral, métricas de validación, semilla, fecha).
4. **Publicación**: `POST /models` al model registry de `cloud-platform` (o copia local en dev).
5. **Distribución**: el edge consulta `GET /models/latest?type=anomaly` y descarga si el manifiesto es más nuevo y compatible (`schema_version`); verificación de hash. En dev: volumen compartido.
6. **Carga en runtime** (`diagnostic-agent/models_runtime`): valida manifiesto contra las features que produce `detection/`; si no coinciden, rechaza y mantiene el modelo anterior (rollback trivial: el anterior no se borra).
7. **LLM aparte:** los LLM no siguen este ciclo; se referencian por tag de Ollama en configuración. El registry solo gobierna modelos matemáticos.

## 9.8 Estrategia Docker

Un único `docker-compose.yml` raíz con **perfiles** (los servicios declaran a qué perfiles pertenecen); imágenes por dominio en `<dominio>/Dockerfile`; base común documentada (python:3.11-slim multi-arch).

| Perfil | Servicios | Uso |
|---|---|---|
| `dev` | obd-lab (emulador TCP) + agent + ollama | desarrollo diario del núcleo |
| `research` | jupyter (ai-models) + volúmenes de datos | experimentación/entrenamiento |
| `cloud` | cloud-api + postgres | desarrollo de la nube |
| `edge` | agent + ollama (objetivo arm64, límites RPi 5) | validación edge |
| `full` | todos los anteriores | integración extremo a extremo |

Reglas: la matriz de recursos del ADR-0002 sigue vigente (límites 4 vCPU/8 GB en `edge`);
builds arm64 vía `docker buildx --platform linux/arm64` sobre los mismos Dockerfiles;
sin Kubernetes ni orquestación adicional (ADR-0006).

## 9.9 Contratos principales (resumen; fuente en `shared/`)

`OBDReading` (lectura puntual de PID), `VehicleTelemetry` (ventana de lecturas normalizadas),
`DetectedAnomaly` (ventana + score + PIDs implicados + detector/versión), `DTCRecord`,
`DiagnosticHypothesis` (causa candidata + evidencia + confianza), `DiagnosticResult`
(hipótesis ganadora + explicación + severidad + trazabilidad), `MaintenanceRecommendation`,
`AgentEvent` (traza de nodo del grafo), `CaseRecord` (memoria de casos), `ModelManifest`,
`RecordedSession`/`ScenarioSpec` (obd-lab), `SyncEnvelope` (outbox). Todos con
`schema_version`; exportados a JSON Schema para Flutter.

## 9.10 Correspondencia con el trabajo de Fase 1

Nada se tira: `src/mecanico_ia/vehicle_sim` → `obd-lab`; `acquisition/storage/rag/memory/agent/api`
→ `diagnostic-agent`; `anomaly` se divide (entrenamiento → `ai-models`, inferencia →
`diagnostic-agent/detection`); `tools/eval_emulator.py` → `tools/`. La migración se hace con
`git mv` preservando historial. docs/05 y docs/08 quedan como diseño conceptual de referencia;
este documento y los ADR 0006–0009 son la materialización.
