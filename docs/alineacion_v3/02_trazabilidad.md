# Alineación científica v3 — Trazabilidad y reinterpretación de la evidencia

**2026-08-18 · Entregables 8 y 11.** Matriz de trazabilidad completa, reinterpretación de
los 14 experimentos ejecutados sin reescribir ninguna métrica, y matriz de cobertura del
Estado del Arte reformada por pasos de la cadena.

## 1. Matriz de trazabilidad PI → V\* → S → OE → H → experimento → métricas → estado

| PI (parte) | V\*/S | OE | Hipótesis | Experimento(s) | Métricas primarias | Resultado / estado | Contribución candidata |
|---|---|---|---|---|---|---|---|
| PI.a detección contextual | S1 | OE-C2 | H-EVT | EXP-ANOM-004 (confirmatorio E0–E4, **no ejecutado**); pilotos 002/003 | FPR condicionado a recall; recall de episodios held-out | pendiente de `prereg-v1.0` | (posible) C-EVT |
| PI.a personalización | S1 | OE-C2 | H-PERS | EXP-PERS (no diseñado en detalle; brazo E4) | ΔF1/ΔFPR por vehículo; arranque en frío | pendiente | — |
| PI.a (precondición: ¿el detector puede?) | S1/S6 | OE-C2 | H1→precondición (HX-ML-1…5) | EXP-ANOM-001…010-R2 + AUDIT-DATA-001 | F1/FPR por ventana y episodio | **cerrada** (H1 SUPPORTED; F22) | evidencia instrumental + hallazgo metodológico de cobertura efectiva |
| PI.b reconocimiento de insuficiencia | S6/S2 | OE-C1, OE-C4 | H-MAIN (P2, P3) | EXP-MAIN-001 (no ejecutado) | tasa «no cubierto» correcta; identificación confiada errónea; AURC | pendiente; bloqueado por R2 (SLM) | C1 |
| PI.c hipótesis + evidencia + verificación | S2/S3 | OE-C3 | H-EXP; H-MAS (arquitectura) | EXP-EXP-001, EXP-MAS-001 (A0–A6) (no ejecutados) | exactitud factual; falsos respaldos/rechazos; coste | pendientes; bloqueados por R2 | C2 |
| PI.d consolidación validada | S4 | OE-C4 | H-MEM | EXP-MEM-001 (M0/M1/M2) (no ejecutado) | contaminación; propagación; utilidad posterior | pendiente; bloqueado por R2 | C3 |
| PI end-to-end | V\* | OE-C4 | H-MAIN completa | EXP-MAIN-001 + controles CN1–CN9 | P1–P5 | pendiente | C1+C2+C3 |
| transversal | S5 | (instrumental) | H-MAS secundaria + criterio edge | A0–A6; mediciones por etapa | latencia/RAM/tokens | parcial (benchs de infraestructura); RAM bloqueada por corrección del instrumento | — |

Regla de lectura: si un elemento no puede conectarse a una fila de esta matriz, no
pertenece al núcleo científico (es artefacto o ingeniería).

## 2. Reinterpretación de los experimentos ejecutados (nada se renumera ni se borra)

Los 14 estudios ejecutados pertenecen TODOS a los pasos 1–3 de la cadena (observar,
contextualizar, detectar) más la validez del banco (S6). Ninguno toca los pasos 4–8:
esa mitad de la cadena está **sin evidencia propia**, y así debe decirlo la memoria.

| Experimento (fase) | Qué evalúa (cadena) | Qué hipótesis actual informa | Evidencia que aporta | Estado tras v3 |
|---|---|---|---|---|
| EXP-ANOM-001 (F3) | paso 3 — baselines | precondición de H-EVT | LOF equilibrio detección/FP; z-score/IForest rechazados | **válido**; baseline congelado (arms-freeze-v1) |
| EXP-ANOM-002 (F8) | pasos 2–3 — ventana vs evento | piloto de H-EVT | eventos solos < ventanas; señal complementaria relacional | **válido como piloto**; nunca confirmación de H-EVT |
| EXP-ANOM-003 (F9) | paso 3 — causa del FPR de eventos | piloto de H-EVT | insuficiencia de normalidad; scoring robusto rechazado | **válido**; motiva la ampliación de train del confirmatorio |
| PROTO-CONF-001/EXP-ANOM-004 | pasos 2–3 confirmatorio | H-EVT | (no ejecutado; protocolo congelado) | intacto |
| EXP-ANOM-005 (F13) | instrumental — paridad del camino wide | (integridad) | paridad exacta; ancla 0.163197 | **válido**; control de integridad P4 de toda la serie |
| EXP-ANOM-006 (F14) | paso 3 — AE vs LOF | precondición | AE denegado (FPR 3×) | **válido (negativo)** |
| EXP-ANOM-007 (F16) | paso 3 + XAI | precondición; D3 XAI | causa = features absolutas de trim; AR@K ≫ azar | **válido**; primera evidencia XAI (ADOPT) |
| EXP-ANOM-008 (F17) | paso 3 — representación fs2-lite | precondición | KEEP fs1; causa refinada al evento LTFT cuantizado | **válido (negativo)** |
| EXP-ANOM-009 (F18) | paso 3 — temporales | HX-ML-3 (refutada) | LSTM/GRU peores; brazo control revela techo de cobertura | **válido (negativo mayor)** |
| AUDIT-DATA-001 (F19) | S6 — validez del banco | (metodológica) | 7/8 anomalías separables sin modelos ⇒ recall 0.000 = fallo de modelo; taxonomía de fallos experimentales | **válido**; fundamento del orden de comprobación |
| F20 (benchmark v2) | S6 — cobertura | (metodológica) | expansión dirigida por mecanismo; RNG separado | **válido con corrección**: su «huecos cerrados» era cobertura declarada |
| EXP-ANOM-010 (F21) | paso 3 + S6 | HX-ML-4 (refutada) | cobertura declarada ≠ cobertura efectiva | **válido (negativo mayor)**; hallazgo metodológico reutilizable |
| EXP-ANOM-010-R2 (F22) | paso 3 + S6 | HX-ML-5 (SUPPORTED) | con cobertura efectiva verificada, FPR 0.0086 sin tocar el modelo; AE = CANDIDATE FOR PROMOTION (no adopción) | **válido**; cierra H1 exploratoria |
| R2 (LLM smoke) | pasos 5–7 (instrumento) | D1 del pre-registro | (no ejecutado) | **bloqueante** del programa agéntico |

Lecturas nuevas que la estructura v3 añade (sin tocar cifras):

1. **La serie completa 001…010-R2 es un estudio de S1 sobre el paso 3**, cuya conclusión
   es doble: (a) el detector clásico congelado sigue siendo el instrumento por defecto;
   (b) el techo de los detectores densos era la *cobertura efectiva de la normalidad*
   medida en el espacio que consume el modelo — un resultado sobre los **datos y su
   instrumentación**, no sobre arquitecturas.
2. **Los cuatro negativos mayores (F14, F17, F18, F21) son evidencia de disciplina de
   abstención** aplicada a nosotros mismos: ejemplifican la regla «la afirmación nunca
   supera la evidencia» que el sistema deberá aplicar en los pasos 4–8. La memoria los
   presenta como capital metodológico, no como fracasos.
3. **F19–F22 fundan la variante «cobertura declarada ≠ cobertura efectiva»** que la
   metodología incorpora al diseño de todo banco futuro (criterio bloqueante en el freeze).
4. **Nada de lo ejecutado responde PI.b–PI.d.** Toda afirmación sobre hipótesis,
   verificación o memoria en la memoria del TFM debe citar únicamente diseño, no
   resultados — hasta que el backlog (03) se ejecute.

## 3. Matriz de cobertura del Estado del Arte (reformada por pasos de la cadena)

Codificación: ✔ cubre · ◐ parcial · «·» no tratado. Columnas = pasos/capacidades de la
cadena. (Sustituye a la matriz por componentes tecnológicos; los 15 antecedentes son los
mismos, verificados en el corpus.)

| # | Trabajo | Detección | Contexto | Longitudinal | Hipótesis | Evidencia | Verificación | Memoria validada | Open-set | Consolidación |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Mahale et al. 2025 | ◐ | · | · | ✔ | ✔ (RAG) | ◐ | · | · | · |
| 2 | Lin & Miao 2025 | · | · | · | ✔ | ◐ | ◐ | ◐ | · | · |
| 3 | CADD — Chen et al. 2024 | ✔ | ✔ | ◐ | · | · | ✔ (detección) | · | ◐ | · |
| 4 | DDAS — Murphey et al. 2003 | ✔ | ◐ | ◐ | ◐ | · | · | ✔ (casos) | · | ◐ |
| 5 | SAGE — Kang et al. 2026 [preprint] | ◐ | · | · | ✔ | ◐ | ◐ | · | · | · |
| 6 | MA-RCA — Fu et al. 2025 | ◐ | · | · | ✔ | ✔ | ✔ | ✔ | · | ◐ |
| 7 | Giannoulidis et al. 2024 | ✔ | ◐ | ✔ | · | · | · | ◐ | ◐ | · |
| 8 | Cherdo et al. 2023 | ✔ | ◐ | · | · | · | · | · | ◐ | · |
| 9 | PARAM — Harbola & Purwar 2025 [preprint] | ◐ | · | · | ✔ | ✔ | ◐ | ◐ | · | · |
| 10 | Park et al. 2025 | · | · | · | ✔ | ✔ | ◐ | · | · | · |
| 11 | HDSO — Shang & Yang 2026 [preprint] | · | · | ◐ | ✔ | ◐ | ✔ | ✔ | · | ✔ (habilidades) |
| 12 | FaultExplainer — Khan et al. 2024 [preprint] | ✔ | · | · | ✔ | ◐ | · | · | · | · |
| 13 | RAAD-LLM — Russell-Gilbert et al. 2025 [preprint] | ✔ | ◐ | · | ✔ | ✔ | · | · | · | · |
| 14 | Das et al. 2025 | ◐ | · | · | ✔ | · | · | · | · | · |
| 15 | DriveAgent — Hou et al. 2025 [preprint] | ◐ | ◐ | · | ✔ | · | ◐ | · | · | · |

Lectura honesta de la matriz (obligatoria en la memoria):

- **Pasos individuales**: bien cubiertos — detección (3, 7, 8, 12, 13), hipótesis con LLM
  (1, 5, 6, 9–15), evidencia por RAG (1, 6, 9, 10, 13).
- **Combinaciones parciales**: MA-RCA y HDSO cubren la sub-cadena
  hipótesis→evidencia→verificación→memoria, **fuera del dominio vehicular y sin telemetría
  física ni open-set**; HDSO consolida con validación, pero sobre habilidades en benchmark.
  CADD une detección+contexto con validación de la detección, sin diagnóstico posterior.
  Son los antecedentes que más obligan a la prudencia de V\* y se citan como tales.
- **Cadena completa (detección→…→consolidación con open-set)**: ninguno de los 15 la
  recorre con evaluación conjunta. Esta es la única afirmación de ausencia que la matriz
  sostiene, y se formula siempre como «en los trabajos revisados no se identificó…».
- La columna Open-set casi vacía justifica que el reconocimiento de insuficiencia (paso 4)
  sea la bisagra menos estudiada — y el foco de PI.b.

## 4. Estructura argumental A–E del Estado del Arte (guía de reescritura)

| Bloque | Pregunta | Contenido (secciones actuales que lo alimentan) |
|---|---|---|
| A. Qué sabemos | capacidades suficientemente estudiadas | detección no supervisada (§4), eventos/segmentación (§5), RAG técnico (§8.2), edge (§11) |
| B. Qué sabemos parcialmente | mecanismos que resuelven partes | LLM diagnóstico sin verificación (§8), multiagente (§9), memoria de agentes (§10), personalización (§6) |
| C. Qué sigue sin resolverse | V\* | §14 reescrito + matriz §3 |
| D. Por qué importa | consecuencias de saltar de anomalía a diagnóstico sin cadena verificable | Mahale (fluidez ≠ exactitud), contradicciones (§13), coste de la memoria contaminada |
| E. Qué necesita estudiar este TFM | la transición anomalía no cubierta → hipótesis → evidencia → verificación → conocimiento/abstención | posicionamiento (§15) reescrito sobre PI v3 |

Cada familia de trabajos debe indicar: qué parte de la cadena cubre · qué parte no ·
qué evidencia aporta · qué limitaciones · cómo contribuye a justificar V\*.
