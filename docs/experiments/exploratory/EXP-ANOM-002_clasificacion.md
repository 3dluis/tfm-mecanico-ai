# EXP-ANOM-002 — Clasificación: PILOT / EXPLORATORY (decisión del autor, F10)

**No es un experimento confirmatorio pre-registrado.** Sus resultados valen como
evidencia exploratoria y como base de diseño del protocolo definitivo
([PROTO-CONF-001](../preregistered/PROTO-CONF-001.md)); en la memoria del TFM se
presentará como experimento que ayudó a identificar problemas, comprender la
distribución y diseñar el protocolo — nunca como si hubiese sido pre-registrado.

## Inventario de decisiones (transparencia metodológica)

**Existían ANTES de ejecutar** (en la instrucción del autor del plan F8 y en el
protocolo heredado ADR-0011, previas a ver dato alguno de este experimento):
la pregunta (window vs event vs both), los brazos y su equidad (mismos datos/splits/
seeds/reglas), el marco común de evaluación, la regla de umbrales (train-only; LOSO
para eventos), la inviolabilidad del held-out, las métricas (P/R/F1/FPR/episodios/
held-out + IoU de eventos + costes), los desgloses por escenario, y la instrucción de
no afirmar mejora sin relevancia práctica.

**Tomadas DURANTE el análisis** (elecciones de implementación, previas a ver métricas
finales pero no pre-registradas formalmente): el marco por tick como unidad común (y su
efecto amplificador sobre FP de eventos largos), la política de eventos sin baseline
(no flaggear + reportar cobertura), el criterio de solape del 50 % para etiquetar
ventanas, la corrección del emparejamiento evento↔EFV (bug detectado en la primera
ejecución, corregido antes de leer resultados como definitivos).

**Consecuencia de resultados OBSERVADOS** (post-hoc; motivo principal de la
clasificación exploratoria): el diagnóstico del FPR concentrado en autovía, la
identificación de la deriva LTFT entre sesiones como causa candidata, y la propuesta de
EXP-ANOM-003 (ampliar normalidad + métricas event-level).

## Estado en el registro

`ai-models/registry/experiments/EXP-ANOM-002.json` → `study_type: "exploratory"`.
Informe: [anomaly_window_vs_event_v1](../../models/comparisons/anomaly_window_vs_event_v1.md).
