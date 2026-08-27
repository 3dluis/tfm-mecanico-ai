# Línea C — Agentes LLM, memoria, RAG, LLM-as-judge y "patrones no documentados"

> **⚠ Nota de vigencia (2026-08-27, alineación v4).** Esta línea se divide. Sus fichas de
> **RAG, agentes y evaluación con juez** siguen siendo centrales y alimentan la línea D
> ([`linea_d_trazabilidad_fidelidad_abstencion.md`](linea_d_trazabilidad_fidelidad_abstencion.md)),
> que cubre fidelidad, atribución de evidencia, incertidumbre y abstención. Sus fichas de
> **memoria de agentes, consolidación validada y «patrones no documentados»** pasan de
> centrales a **antecedente y trabajo futuro**
> ([`docs/alineacion_v4/05_fuera_de_alcance.md`](../alineacion_v4/05_fuera_de_alcance.md)):
> se conservan y se citan, pero ya no sostienen el vacío del TFM.

> Fichas de trabajo del primer barrido (Fase 1, 2026-08-12). Referencias verificadas en la fecha
> del barrido; releer texto completo antes de citar en la memoria.

## Agentes LLM y memoria

| # | Referencia (verificada) | Aporte para el TFM |
|---|---|---|
| C1 | Yao et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) | Patrón base pensamiento→acción→observación; reduce alucinación vs CoT puro. Cita obligada para el diseño del agente. |
| C2 | Schick et al. (2023). *Toolformer.* NeurIPS 2023. [arXiv:2302.04761](https://arxiv.org/abs/2302.04761) | Tool-use aprendido por fine-tuning; nuestro contraste: herramientas orquestadas, no aprendidas (defendible en edge por coste). |
| C3 | Shinn et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS 2023. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | Memoria episódica de reflexiones entre episodios sin actualizar pesos → antecedente directo de nuestra memoria evolutiva. |
| C4 | Wang et al. (2024). *A Survey on LLM based Autonomous Agents.* Front. Comput. Sci. 18(6). [arXiv:2308.11432](https://arxiv.org/abs/2308.11432) | Framework perfil-memoria-planificación-acción; vocabulario taxonómico. |
| C5 | Xi et al. (2023). *The Rise and Potential of LLM Based Agents.* [arXiv:2309.07864](https://arxiv.org/abs/2309.07864) | Survey panorámico complementario. |
| C6 | Packer et al. (2023). *MemGPT: Towards LLMs as Operating Systems.* [arXiv:2310.08560](https://arxiv.org/abs/2310.08560) | Jerarquía de memoria paginada para contextos pequeños — crítico con SLM cuantizado en edge. |
| C7 | Park et al. (2023). *Generative Agents.* UIST 2023. [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) | Pipeline observación→recuperación (recencia+relevancia+importancia)→reflexión: patrón para destilar casos en reglas diagnósticas. |
| C8 | Zhang et al. (2024). *A Survey on the Memory Mechanism of LLM based Agents.* [arXiv:2404.13501](https://arxiv.org/abs/2404.13501) | Survey vertebrador del capítulo de memoria (operaciones: escritura/gestión/lectura; métricas). |
| C9 | Xu et al. (2025). *A-MEM: Agentic Memory for LLM Agents.* NeurIPS 2025. [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) | El más cercano a "memoria evolutiva" (notas enlazadas que evolucionan). **Diferenciarse explícitamente de él** en la memoria. |

## RAG y evaluación

| # | Referencia | Aporte |
|---|---|---|
| C10 | Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 2020. [arXiv:2005.11401](https://arxiv.org/abs/2005.11401) | Fundacional; argumento de conocimiento actualizable sin reentrenar. |
| C11 | Gao et al. (2023/24). *RAG for LLMs: A Survey.* [arXiv:2312.10997](https://arxiv.org/abs/2312.10997) | Taxonomía Naive/Advanced/Modular para situar nuestro pipeline. |
| C12 | Shuster et al. (2021). *Retrieval Augmentation Reduces Hallucination in Conversation.* Findings EMNLP 2021. [arXiv:2104.07567](https://arxiv.org/abs/2104.07567) | Evidencia empírica RAG↓alucinación. |
| C13 | Béchard & Marquez Ayala (2024). *Reducing hallucination in structured outputs via RAG.* NAACL 2024 Industry. [arXiv:2404.08189](https://arxiv.org/abs/2404.08189) | Caso industrial con salidas estructuradas y **modelos pequeños + buen recuperador** — nuestro caso exacto. |
| C14 | Thakur et al. (2021). *BEIR.* NeurIPS 2021 D&B. [arXiv:2104.08663](https://arxiv.org/abs/2104.08663) | Precedente metodológico de métricas IR (nDCG@k, recall@k, MRR); robustez de BM25 fuera de dominio. |
| C15 | Es et al. (2024). *RAGAs.* EACL 2024 Demos. [ACL](https://aclanthology.org/2024.eacl-demo.16/) · [arXiv:2309.15217](https://arxiv.org/abs/2309.15217) | Framework de evaluación RAG; **es LLM-as-judge encubierto** → complementar con métricas objetivas. |

## LLM-as-judge y limitaciones

- **C16. Zheng et al. (2023).** *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS 2023 D&B. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685). Legitima el método (>80 % acuerdo con humanos) y documenta sus sesgos: posición, verbosidad, auto-mejora, razonamiento débil.
- **C17. Wang et al. (2024).** *Large Language Models are not Fair Evaluators.* ACL 2024. [ACL](https://aclanthology.org/2024.acl-long.511/) · [arXiv:2305.17926](https://arxiv.org/abs/2305.17926). El ranking se manipula alterando el orden de respuestas; propone calibraciones (BPC/MEC + human-in-the-loop). → Aleatorizar posiciones, no juzgar con el mismo modelo generador, validar submuestra manualmente.

## Operativización de "patrones no documentados" en la literatura

- **C18. Feng & Zhao (2021).** *Fault Description Based Attribute Transfer for Zero-Sample Industrial Fault Diagnosis.* IEEE TII 17(3):1852–1862. [IEEE](https://ieeexplore.ieee.org/document/9072621/). Protocolo de **clases held-out** con descripción semántica a priori (zero-shot sobre Tennessee Eastman).
- **C19. Lundgren & Jung (2022).** *Data-driven fault diagnosis analysis and open-set classification of time-series data.* Control Engineering Practice 121. [arXiv:2009.04756](https://arxiv.org/abs/2009.04756). **Dominio automotriz real (motor Volvo, fugas de admisión y fallos de sensor):** "fallo desconocido" = rechazado por todos los clasificadores one-class de las clases conocidas (open-set). La referencia más valiosa para nuestro protocolo.
- **C20. Pang et al. (2021).** *Deep Learning for Anomaly Detection: A Review.* ACM CSUR 54(2). [arXiv:2007.02500](https://arxiv.org/abs/2007.02500). Marco general: "lo nunca visto" = novelty detection sobre distribución de lo normal, evaluado con AUC sobre anomalías excluidas del entrenamiento.

**Patrón transversal:** nadie evalúa "descubrir patrones nuevos" en sentido absoluto; siempre se reduce a (i) clases held-out con semántica previa, (ii) rechazo open-set, o (iii) scoring de desviación de lo normal. **Nuestra redefinición operativa (docs/01 §1.3) queda alineada con la práctica estándar y es defendible ante el tribunal** — y puede reforzarse añadiendo el protocolo held-out sobre el corpus RAG/memoria (retirar clases de fallo del corpus y medir si el agente las señala como no cubiertas).

## Implicaciones de diseño para nuestro agente

1. Declarar el agente como ReAct con grafo explícito (LangGraph) y herramientas orquestadas (no aprendidas).
2. Memoria evolutiva = composición citable: episódica tipo Reflexion + recuperación ponderada tipo Generative Agents + evolución de notas tipo A-MEM (diferenciándonos: dominio técnico anclado en telemetría, edge, SLM).
3. Cadena argumental RAG: C10→C11→C12→C13 (el caso de C13 —modelo pequeño + recuperador— es el nuestro).
4. Evaluación en dos capas: recuperación con métricas IR objetivas; generación con rúbrica + juez LLM calibrado (C16/C17) y submuestra validada por el autor.
5. H2/H3 ganan un experimento extra barato y potente: **protocolo held-out de clases de fallo en corpus y memoria** (C18/C19), que operativiza directamente la pregunta de investigación principal.
