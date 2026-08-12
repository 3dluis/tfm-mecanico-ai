# ai-models

Investigación, experimentación, entrenamiento, evaluación, comparación y exportación de modelos.
**Nunca se ejecuta en el edge** (ADR-0009): el edge consume artefactos ONNX + manifiesto.

Estructura: data/ · preprocessing/ · features/ · anomaly/ · clustering/ · evaluation/ · export/ ·
notebooks/ · experiments/ (uno por hipótesis H1–H4, reproducibles por semilla).

Protocolo de evaluación: F1 por eventos sin point-adjustment, escenarios held-out
(ver docs/estado_del_arte/linea_b y docs/04 RI1).
