# diagnostic-agent

Núcleo inteligente EDGE (objetivo: Raspberry Pi 5, 8 GB).

Separación estricta (ADR-0009): `detection/` (ML matemático: features + ONNX + scoring) y
`reasoning/` (LLM: grafo LangGraph, RAG, memoria de casos) no se importan entre sí; se comunican
mediante contratos (`DetectedAnomaly`). El LLM nunca decide si hay anomalía.

API local: `/health`, `/ready` (scaffolding). Configuración: variables `MECANICO_*`
(ver `.env.example` en la raíz).
