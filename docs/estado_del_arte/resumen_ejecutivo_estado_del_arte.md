# Estado del Arte — Resumen ejecutivo para revisión del tutor

**TFM:** Sistema inteligente híbrido Edge–Cloud para diagnóstico y mantenimiento predictivo de vehículos con OBD-II y Raspberry Pi · Universidad Alfonso X el Sabio · 2026-08-12
**Base:** capítulo 2 completo (`capitulo2_estado_del_arte.md`), corpus ≈153 referencias verificadas en fuente primaria (entregas 1–4 en `docs/estado_del_arte/`).

**Pregunta principal:** ¿Puede un agente inteligente híbrido (LLM + aprendizaje no supervisado + memoria evolutiva + RAG) descubrir y explicar patrones de fallo vehicular previamente no documentados a partir de datos OBD-II?

**Cadena que la operacionaliza:** evento → anomalía contextual → patrón candidato → hipótesis → verificación → conocimiento. Un "patrón no documentado" exige recurrencia, ausencia de correspondencia documental y validación posterior; nunca se equipara a un outlier estadístico.

## Matriz ejecutiva

| RQ | Evidencia clave del estado del arte | Vacío | Contribución | Experimento → métrica principal |
|---|---|---|---|---|
| RQ principal | "Nuevo" se operacionaliza siempre como held-out/open-set (Feng & Zhao; Lundgren & Jung); nadie integra recurrencia + contraste documental + validación | V1 (integración) | C-INT (arquitectónica) | End-to-end con fallos held-out + held-out de conocimiento → F1 por eventos, rechazo open-set |
| RQ3, RQ17 — ¿anomalías sin etiquetas? ¿eventos vs continuo? | Contextual ≫ global, cuantificado en 3 fuentes; en vehículo real el baseline global se degrada a FPR>90 % al mezclar regímenes (CADD, RAID 2024); **nadie compara por-evento vs continuo en salud vehicular** | **V7 (central)** | **C-EVT (metodológica + experimental)** | **E0–E4** (punto / ventana / régimen / evento / evento+vehículo) → P, R, F1, FPR, retardo, F1 por evento, recursos edge |
| RQ17 — calidad de segmentación | El segmentador limita al sistema (Aboah 2023); descubrimiento no supervisado débil (F1 0,47, Kreutz) | V7 | C-EVT | Evaluación propia de segmentación contra ground truth del emulador → P/R/F1 por tipo, error inicio/fin, IoU |
| RQ9, RQ10 — ¿memoria longitudinal? ¿anomalías→conocimiento? | Consolidación validada existe solo sobre *skills* en benchmark (HDSO 2026 [preprint]; DS-Agent ICML'24); defensas de memoria filtran en recuperación, no en consolidación (MINJA, AgentPoison); memoria indexada por evento+unidad+edge: sin instancia | V2 | **C-MEM (candidata a científica)** | Ablación memoria on/off + escenarios de propagación → mejora con memoria, consolidaciones erróneas evitadas |
| RQ16 — ¿multiagente > monolítico? | Ablaciones pro (−48 % sin especialistas, SAGE; memoria y verificador = mayor valor, MA-RCA) y contra (coordinación = 1ª fuente de fallo, MAST; ventaja se disipa con LLM fuertes, Gao) | V6 (reformulado con genealogía MAS: DDAS 2003, HoloMAS 2007) | C-INT | **A0–A6** (monolítico → +tools → +especialistas → +critic → +memoria → +eventos) → exactitud, evidencias, alucinaciones, latencia, tokens, finalización |
| RQ5 — ¿explicar causa, no solo decisión? | SHAP/LIME explican la decisión; hipótesis causal por LLM existe sin verificación (FaultExplainer); verificación estructural existe sin lenguaje (Mohammadi 2025) | V4 | C-EXP (metodológica) | Evaluación de explicaciones en dos capas (juez calibrado + validación manual) → exactitud factual, trazabilidad |
| RQ13 — ¿generalizar entre vehículos? | Personalización > global bajo no-IID (+3–5 pts, Almansour); calibración por entidad no transfiere (Mercedes); F1 0,21–0,93 según vehículo (EngineAD); patrón maduro = jerárquico (Chesterman) | V3 | C-PERS (experimental) | Global vs individual vs jerárquico por evento → ΔF1/ΔFPR, coste de arranque en frío |
| RQ12 — ¿edge viable? | Cada pieza demostrada (E2USD en MCU; SLM 3B a 2–5 t/s en RPi 5); sistema end-to-end ausente (Bala; ECoLAD) | V5 | C-INT / C-EXP | Medición end-to-end en perfil RPi → latencia por etapa, RAM, t/s |
| RQ6–RQ8 — LLM, RAG, agentes | LLM pierde como detector frente a ML clásico (Das 2025) → LLM solo razona; RAG automotriz es industrial (BMW) y solo recupera; agentes en mantenimiento existen (Park, Lee, PARAM), ninguno vehicular con telemetría viva | V1, V6 | C-INT | Incluido en A0–A6 y end-to-end |
| RQ1, RQ2, RQ11, RQ14, RQ15 | Respuestas consolidadas en §2.18 del capítulo | — | — | — |

## Vacío integrador (formulación defendible)

En la literatura analizada no se identificó ninguna propuesta que integre, en un único sistema evaluado end-to-end: (i) telemetría OBD-II en streaming; (ii) segmentación en eventos operativos con normalidad por tipo de evento y baseline por vehículo; (iii) detección no supervisada contextual en edge; (iv) multiagente LLM bajo restricciones edge con RAG, historial, hipótesis y verificación; (v) memoria longitudinal con ciclo de estados de evidencia y consolidación solo tras validación. Los antecedentes cubren a lo sumo tres de los cinco ejes.

## Estado y pendientes obligatorios antes del depósito

1. **PRISMA formal** con números exactos por base (Scopus/WoS/IEEE; sintaxis lista) — hasta entonces, los recuentos declarados son del barrido preliminar por web.
2. **Texto completo** de Takara (ESWA 2025), Min (EAAI 2024) y Onsu (IoT 2025) antes de fijar V1–V7 como definitivos.
3. **Vigilancia adversarial pre-depósito** sobre HDSO, SAGE, DriveAgent, RAAD-LLM, ECoLAD/STREAM-VAE y derivados (literatura 2025–2026).
4. **Niveles de novedad diferenciados** por contribución (ver `afirmaciones_novedad.md`): C-MEM candidata a científica; C-EVT metodológica+experimental; C-INT arquitectónica; C-EXP metodológica; C-PERS experimental.
