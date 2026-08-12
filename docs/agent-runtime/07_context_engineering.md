# 07 — Context Engineering

[← Índice](README.md)

Nunca se envía al LLM "toda la base de datos". El contexto de cada llamada se ENSAMBLA
dinámicamente con presupuesto por sección (tokens aproximados por caracteres/4; el
presupuesto total se dimensiona al modelo activo vía ModelRouter):

| Sección | Presupuesto v1 | Prioridad | Fuente |
|---|---|---|---|
| system instructions (rol del agente) | 300 | fija | plantilla versionada (prompt_version) |
| objective | 100 | fija | estado |
| vehicle summary | 100 | alta | repositorio |
| current anomaly (features notables) | 400 | alta | estado (solo features |v|>ε, redondeadas) |
| active hypotheses (+estados) | 300 | alta | estado |
| retrieved cases (top-k, con nivel epistemológico) | 400 | media | Recall |
| retrieved documents (top-k truncados) | 900 | media | Knowledge |
| tool outputs recientes | 300 | media | working memory |
| pending questions | 100 | alta | estado |

Reglas: (1) prioridad ante desbordo — se truncan primero documentos, luego casos; nunca la
anomalía ni las hipótesis; (2) los datos numéricos entran RESUMIDOS (features de ventana,
no series crudas); (3) todo chunk/caso incluido en contexto queda registrado como
RetrievalEvent — el contexto es reconstruible ex post; (4) el ensamblado es una función
pura del estado → testeable y reproducible.
