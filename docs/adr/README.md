# Índice de ADRs

| # | Título | Fase | Estado |
|---|---|---|---|
| [0001](0001-estructura-y-stack-del-repositorio.md) | Estructura del repositorio y stack de calidad | 1 | Aceptada (evolucionada por 0006) |
| [0002](0002-emulacion-dual-raspberry-pi.md) | Emulación dual de la Raspberry Pi | 1 | Aceptada |
| [0003](0003-emulacion-obd2-elm327.md) | Emulación OBD-II: ELM327-emulator + escenario propio | 1 | Aceptada |
| [0004](0004-capa-de-transporte-plugable.md) | Capa de transporte plugable | 1 | Aceptada |
| [0005](0005-alcance-validacion-docker-en-sandbox.md) | Alcance de la validación Docker en sandbox | 1 | Aceptada |
| [0006](0006-monorepo-multidominio.md) | Monorepo multi-dominio, nube simple | 2 | Aceptada |
| [0007](0007-contratos-compartidos.md) | Contratos compartidos Pydantic→JSON Schema | 2 | Aceptada |
| [0008](0008-perfiles-docker.md) | Compose único con perfiles | 2 | Aceptada |
| [0009](0009-ciclo-de-vida-modelos.md) | Ciclo de vida de modelos ONNX+manifiesto | 2 | Aceptada |
| [0010](0010-generador-de-escenarios.md) | Generador de escenarios (3 categorías, cuantización) | 3 | Aceptada |
| [0011](0011-protocolo-baselines-deteccion.md) | Protocolo y resultados de baselines | 3 | Aceptada |
| [0012](0012-arquitectura-de-datos.md) | Arquitectura de datos: clases, trazabilidad, provenance | 4 | Aceptada |
| [0013](0013-memoria-tres-niveles.md) | Memoria en 3 niveles, pesos epistemológicos | 4 | Aceptada |
| [0014](0014-agente-v1.md) | Agente v1 LangGraph, responsabilidades estrictas | 4 | Aceptada (= arquitectura A2) |
| [0015](0015-edge-agent-runtime-multiagente.md) | Edge Agent Runtime multiagente, agentes lógicos, local-first | 5 | Aceptada |
| [0016](0016-tool-registry-y-seguridad.md) | Tool Registry y read-only sobre vehículo | 5 | Aceptada |
| [0017](0017-loop-y-context-engineering.md) | Loop engineering con límites + context engineering | 5 | Aceptada |
| [0018](0018-diseno-experimental-arquitecturas.md) | Diseño experimental A0–A6 con feature flags | 5 | Aceptada |
| [0019](0019-event-intelligence-layer.md) | Capa Vehicle Event Intelligence | 6 | Aceptada |
| [0020](0020-incorporacion-imu.md) | Incorporación de IMU (ICM-20948 ref.; simulada primero) | 6 | Aceptada (SHOULD) |
| [0021](0021-deteccion-anomalias-contextual.md) | Anomalías contextuales y EventBaseline | 6 | Aceptada |
| [0022](0022-gobernanza-de-modelos.md) | Gobernanza de modelos: registry, cards, manifest, ciclo de vida | 7 | Aceptada |
| [0023](0023-estrategia-llm-local.md) | Estrategia LLM: local cuantizado, escalera de adaptación, benchmark propio | 7 | Aceptada |
| [0024](0024-embeddings-y-experimentos.md) | Embeddings evaluados aparte; configs declarativas; selección multicriterio | 7 | Aceptada |
| [0025](0025-representacion-canonica-wide.md) | Representación canónica horizontal (VehicleTelemetrySnapshot) | 11 | Aceptada |
| [0026](0026-alineacion-temporal-snapshots.md) | Alineación temporal `sync:v1` (1 Hz validado; 5 Hz candidato) | 11 | Aceptada |
| [0027](0027-nulos-y-pids-no-soportados.md) | NULL ≠ 0: PIDs no soportados y calidad por señal | 11 | Aceptada |
| [0028](0028-particionamiento-snapshots.md) | Particionamiento mensual de snapshots (candidato, no activado) | 11 | Aceptada |
| [0029](0029-evaluacion-postgresql-pgvector-edge.md) | Evaluación PostgreSQL+pgvector en Edge → HYBRID (REJECT edge · ACCEPT cloud) | 11 | **Superada por [0030](0030-postgresql-pgvector-edge.md)** (se conserva con sus mediciones) |
| [0030](0030-postgresql-pgvector-edge.md) | **PostgreSQL + pgvector = plataforma oficial de persistencia del Edge** (schemas lógicos, particionado, Alembic, SQLite→legacy) | 12 | Aceptada |
| [0031](0031-linea-experimental-ml-wide.md) | Línea experimental ML sobre representación wide: snapshot = entrada canónica de ML (paridad EXP-ANOM-005), Protocolo ML v1, reactivación exploratoria de AE/temporales, familia EXP-PAT-*, semillas 401–599 | 13 | Aceptada |
