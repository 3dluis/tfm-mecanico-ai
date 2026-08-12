# Estado del arte — Síntesis del primer barrido (v0)

**Fase 1 · 2026-08-12.** Tres líneas de búsqueda (A: OBD-II/ML y datasets; B: detección de
anomalías y SLM en edge; C: agentes LLM, RAG, memoria y evaluación). 35+ referencias
verificadas en venue en la fecha del barrido. Este documento se convertirá en el capítulo 2
de la memoria; las fichas completas están en `linea_a…`, `linea_b…`, `linea_c….md`.

## Hallazgos que cambian (o confirman) decisiones del proyecto

**H-EA1. No existe dataset público de OBD-II con fallos mecánicos reales etiquetados** (Línea A).
Los datasets disponibles cubren conducción normal (HCRL Driving, 51 señales a 1 Hz; X-CANIDS,
688 señales decodificadas; AEGIS, CC BY 4.0) o anomalías de *ciberataque* inyectadas, no fallos
mecánicos. Consecuencias: (a) la inyección sintética de fallos es la práctica del área, no un
atajo — se citará como tal; (b) nuestro banco de fallos reproducible (contribución C4 de
docs/06) cubre una carencia real del área y sube de prioridad; (c) el supuesto S2 de docs/03 se
reformula: el dataset público se usará para **modelar normalidad realista**, no para validar
detección de fallos. → Actualizar docs/03 y docs/06 al abrir Fase 2.

**H-EA2. El hueco de investigación queda confirmado y acotado con precisión** (Líneas A y C).
Los dos trabajos más cercanos son Mahale et al. 2025 (OBD-II→XGBoost→RAG→GPT-4o, sin edge, sin
streaming, sin memoria; reporta alta fluidez pero baja exactitud factual) y Lin & Miao 2025
(KG+RAG sobre diálogos de taller, sin telemetría). Ningún trabajo peer-reviewed integra agente
LLM + telemetría OBD-II en vivo + edge + memoria de casos con evaluación extremo a extremo.

**H-EA3. La comparación "clásico vs deep" en detección es la pregunta correcta** (Línea B).
La evaluación masiva de Schmidl et al. (VLDB 2022; 71 algoritmos) muestra que los métodos
clásicos son competitivos a mucho menor coste. Emparejar Isolation Forest contra un autoencoder
tipo USAD (ONNX/INT8) es defendible y científicamente interesante en edge. Además, la crítica de
Wu & Keogh (TKDE) a los benchmarks y la de Kim et al. (AAAI 2022) al *point adjustment* fijan
nuestro protocolo: datos propios + fallos held-out + F1 por eventos sin PA, publicado a priori.

**H-EA4. El "punto dulce" de SLM en RPi 5 está en 1.5–3B** (Línea B).
Evidencia formal (arXiv 2511.07425): ~3B → 2–5 t/s; ≤1.5B → 5–15 t/s en RPi 5. Un diagnóstico
de ~300 tokens tardaría ~1–2,5 min con un 3B: aceptable para nuestro caso de uso no interactivo
(docs/01 H4), justo para conversación. Candidatos ratificados: Qwen2.5 3B, Llama 3.2 3B/1B,
Gemma 2 2B; Phi-3.5-mini como cota superior. Decisión final con smoke test propio (Fase 2).

**H-EA5. La redefinición operativa de "patrones no documentados" está alineada con la práctica
del área** (Línea C). La literatura lo operativiza siempre como held-out/open-set/novelty
(Feng & Zhao TII 2021; Lundgren & Jung CEP 2022 — este último en motor real de automóvil; Pang
et al. CSUR 2021). Refuerzo propuesto para H2/H3: retirar clases de fallo del corpus RAG y de la
memoria y medir si el agente las señala como no cubiertas (rechazo open-set) — experimento
barato que responde directamente a la pregunta de investigación.

**H-EA6. La memoria evolutiva tiene genealogía citable y un competidor del que diferenciarse**
(Línea C): Reflexion (episódica), Generative Agents (recuperación ponderada + reflexión),
MemGPT (paginación de contexto — relevante con SLM), y A-MEM (NeurIPS 2025, notas que
evolucionan). Nuestra diferenciación: dominio técnico anclado en telemetría verificable, edge,
SLM, y evaluación cuantitativa del efecto de la memoria (H3).

**H-EA7. Evaluación de explicaciones:** RAGAS es utilizable pero es LLM-as-judge encubierto;
Zheng et al. y Wang et al. (ACL 2024) obligan a calibrar: aleatorizar posiciones, juez ≠
generador, submuestra validada manualmente. Ya previsto en RI4; ahora con citas.

## Cobertura y pendientes del barrido

Cubierto: IN-1 (parcial: falta profundizar en series OBD específicas), IN-2 ✓, IN-3 ✓, IN-4 ✓,
IN-5 ✓, IN-6 ✓ (decisión de datasets tomada), IN-9 ✓. Pendiente para Fase 2: IN-7 (estándares
SAE/ISO citables desde fuentes accesibles), IN-8 (modelos de fallo con firma en PIDs — crítico
para diseñar los 5 escenarios con fundamento) y lectura completa de los 6–8 trabajos que se
citarán con más peso.
