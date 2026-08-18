# Alineación científica v3 — Backlog experimental para responder H-MAIN

**2026-08-18 · Entregable 12.** Qué falta ejecutar, en qué orden y con qué bloqueantes,
para que H-MAIN pueda responderse. Nada de esta lista es confirmatorio hasta el tag
`prereg-v1.0`; el orden respeta las dependencias reales, no la conveniencia.

## 0. Bloqueantes previos (sin experimento nuevo)

| # | Bloqueante | Por qué bloquea | Estado |
|---|---|---|---|
| B0.1 | **R2 — smoke del SLM** (preparado desde F9, nunca ejecutado) | fija el parámetro diferido D1 (modelo de lenguaje) del pre-registro; sin él no hay generador de hipótesis ni juez | pendiente en el Mac (requiere ollama local) |
| B0.2 | Corrección de `peak_rss_mb()` (F22: infla ×1024 fuera de Linux) | el criterio edge de RAM no es verificable con un instrumento que mide mal | decidido en F-PREREG §2.5; cambio de código mínimo |
| B0.3 | Enmienda de cobertura efectiva al dataset confirmatorio `suite-v2` (F-PREREG §2.2) | sin ella, ~1/3 de las réplicas nacerían con cobertura efectiva nula en la dimensión que domina el FPR | especificada; falta materializar la suite |
| B0.4 | Congelación del pre-registro (`prereg-v1.0`) con PI v3, H-MAIN v3, §11 completada | frontera exploratorio/confirmatorio | tras aprobar esta alineación |
| B0.5 | Matriz de contaminación ejecutable (verificador de E-DET/E-RAG/E-MEM previo a cada run) | H-MAIN es ininterpretable sin exclusión verificada | diseño en núcleo §9; herramienta pendiente (ligera) |

## 1. Experimentos pendientes, por paso de la cadena

| Orden | Experimento | Cadena | Hipótesis | Diseño (resumen) | Depende de |
|---|---|---|---|---|---|
| 1 | **EXP-SEG-001** — calidad de segmentación de eventos | 2 | precondición de H-EVT | segmentador vs GT del emulador; P/R/F1, IoU, error inicio/fin; en train+validation | B0.3, B0.4 |
| 2 | **EXP-ANOM-004** — E0–E4 confirmatorio | 2–3 | **H-EVT** | 5 brazos × 10 réplicas; Wilcoxon pareado; co-primarias FPR/recall held-out | EXP-SEG-001 |
| 3 | **EXP-PERS-001** — global vs individual vs jerárquico | 2–3 | **H-PERS** | brazo E4 extendido; ≥2 perfiles de vehículo; curva de arranque en frío | EXP-ANOM-004 |
| 4 | **EXP-COV-001** — reconocimiento de cobertura | 4 | H-MAIN (P2/P3 aislada) | el sistema declara cubierto/no-cubierto sobre casos conocidos + held-out; AURC, calibración; **sin LLM aún** (score + reglas) como baseline del paso 4 | B0.3 |
| 5 | **EXP-EXP-001** — LLM vs +RAG vs +RAG+verificación | 5–7 | **H-EXP** | 3 brazos + control heurístico; exactitud factual con juez calibrado + submuestra manual; corpus con manifiesto | B0.1, B0.4 |
| 6 | **EXP-MAS-001** — ablación A0–A6 | 5–7 | **H-MAS** | monolítico → runtime completo, mismo SLM; estratificación por dificultad | EXP-EXP-001 |
| 7 | **EXP-MEM-001** — M0 / M1 / M2 | 8 | **H-MEM** | secuencias de casos repetidos/variantes + escenarios de contaminación (CN5/CN6); tasa de contaminación, propagación, utilidad | EXP-EXP-001 |
| 8 | **EXP-MAIN-001** — cadena completa held-out/open-set | 4–8 | **H-MAIN** | protocolo de 15 pasos (núcleo §8.1) con P1–P5; controles CN1–CN9; referencias: sistema con conocimiento (cota sup.), supervisado (cota inf.), hipótesis plantilla (control) | todos los anteriores |
| 9 | **Validaciones externas** | — | validez externa | HCRL (¿el LTFT real cruza cuantización a esta frecuencia?) · ARM64/RPi5 (A2/A3) · confirmatorio del AE (CANDIDATE FOR PROMOTION) | independientes; ninguna bloquea H-MAIN pero acotan las conclusiones |

## 2. Controles negativos (transversales a 4–8)

CN1–CN9 del núcleo §8.3 se materializan como escenarios del banco (los CN1/CN2 ya tienen
base: las normales largas de v3; CN5/CN6 son estados sembrados en memoria; CN3 es un
documento distractor con manifiesto). Cada experimento de los pasos 4–8 declara qué CN
incluye; EXP-MAIN-001 los incluye todos.

## 3. Riesgos de calendario (entrega septiembre 2026)

- La cadena 5–8 depende íntegramente de B0.1 (R2). **Es el camino crítico.**
- Si el calendario obliga a recortar, el orden de sacrificio pre-declarado es:
  EXP-PERS-001 → EXP-MAS-001 (H-MAS ya es secundaria) → reducción de n en EXP-MEM-001,
  **nunca** EXP-MAIN-001 ni sus controles: sin ellos la PI queda sin contraste y el TFM
  solo podría defender la mitad detectora de la cadena más el diseño.
- Escenario mínimo defendible: EXP-SEG + EXP-ANOM-004 + EXP-COV + EXP-EXP + EXP-MEM
  (n reducido) + EXP-MAIN — con delimitaciones honestas sobre lo no ejecutado.
