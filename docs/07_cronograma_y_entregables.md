# 7. Cronograma por fases y entregables

## 7.1 Marco temporal

Inicio: 13 de agosto de 2026. Entrega: septiembre de 2026 (fecha exacta pendiente de confirmación por el autor; el plan asume disponibilidad de la memoria completa el **18 de septiembre** y una semana final de margen). Son **~6 semanas**: el cronograma es agresivo por necesidad y la escritura de la memoria es **transversal desde la semana 1**, no una fase final.

⚠️ Regla de gestión: cada fase termina con revisión y aprobación del autor. Si un hito semanal se retrasa más de 2 días, se ejecuta el siguiente recorte de la lista de §7.3 en lugar de comprimir las fases posteriores.

## 7.2 Fases

### Fase 1 — Fundamentos y entorno (13–19 ago, semana 1)
| Actividad | Resultado verificable |
|---|---|
| Repositorio Git + estructura + CI mínima + convenciones | Repo operativo con `docs/` versionado |
| Estado del arte: IN-1, IN-2, IN-5, IN-7, IN-8 (primer barrido); IN-6 verificación de datasets | Fichas de lectura + decisión de datasets + especificación de los 5 escenarios de fallo |
| Entorno Docker dual (arm64 + x86 limitado) con Ollama y emulador ELM327 evaluado | `docker compose up` funcional; veredicto sobre R3 (¿emulador suficiente o generador propio?) |
| Smoke test de LLM candidatos (JSON estructurado) | Veredicto temprano sobre R4/S3 |
| **Memoria:** esqueleto en plantilla UAX + capítulo de introducción borrador | Índice completo + intro v0 |

**Hito H1 (19 ago): entorno reproducible + plan experimental aprobado.**

### Fase 2 — Datos y detección (20 ago – 2 sep, semanas 2–3)
| Actividad | Resultado verificable |
|---|---|
| Generador de escenarios + inyección de fallos (C1) con semillas | 5+ escenarios normales y de fallo reproducibles |
| Adquisición (C2) + persistencia (C3) | Sesiones almacenadas; pérdida < 1 % |
| Detección: baseline z-score + Isolation Forest + autoencoder ONNX (OE4) | Comparativa F1/AUC/latencia/memoria sobre escenarios held-out |
| Corpus RAG + indexación + métricas de recuperación (OE5) | Índice construido; hit-rate sobre consultas de prueba |
| **Memoria:** estado del arte redactado; capítulo de metodología v0 | Capítulos 2 y 3 borrador |

**Hito H2 (2 sep): pipeline datos→detección evaluado; RAG operativo.**

### Fase 3 — Agente, memoria de casos e interfaz (3–9 sep, semana 4)
| Actividad | Resultado verificable |
|---|---|
| Agente LangGraph completo (C6) con trazas persistidas | Diagnóstico de extremo a extremo sobre escenario de fallo |
| Memoria de casos (C5b) integrada | Casos escritos y recuperados por similitud |
| API REST (C7) + UI web mínima (C8) | Demo navegable de un caso completo |
| **Memoria:** capítulo de diseño/implementación v0 | Capítulo 4 borrador |

**Hito H3 (9 sep): sistema completo funcional en el entorno emulado.**

### Fase 4 — Evaluación experimental (10–16 sep, semana 5)
| Actividad | Resultado verificable |
|---|---|
| Experimentos H1 (detección, held-out), H2 (RAG A/B), H3 (memoria antes/después), H4 (recursos en perfil RPi) | CSVs de resultados versionados + tablas y figuras |
| Comparativa LLM local vs. cloud (mismo agente) | Tabla de compromiso calidad/latencia/coste |
| Análisis de errores y amenazas a la validez | Sección de discusión v0 |
| **Memoria:** capítulo de resultados y discusión | Capítulos 5 y 6 borrador |

**Hito H4 (16 sep): todas las hipótesis evaluadas con datos.**

### Fase 5 — Cierre (17 sep – entrega, semana 6)
| Actividad | Resultado verificable |
|---|---|
| Memoria completa: revisión integral, conclusiones, trabajo futuro, formato UAX | Documento final |
| Limpieza del repositorio + README + guía de reproducción | Repo entregable |
| Preparación de la defensa (guion + demo grabada de respaldo) | Presentación v0 |

**Hito H5: entrega.**

## 7.3 Lista de recortes preacordada (en orden de ejecución si falta tiempo)

1. Flutter (OS1) → la UI queda como web mínima. *(ya recortado por defecto)*
2. Sincronización cloud (OS2) → exportación manual de memoria. *(ya recortado por defecto)*
3. Recuperación híbrida BM25+denso → solo densa.
4. Autoencoder ONNX → comparativa queda en baseline + Isolation Forest (se pierde profundidad en OE4, no la validez).
5. Comparativa de 3 LLM locales → 1 LLM local elegido por smoke test + baseline cloud.
6. UI web → solo API + notebook de demostración.
7. **Línea roja infranqueable:** detección + agente con RAG + memoria + evaluación H1–H3 + memoria del TFM. Si esto peligra, la conversación es con el tutor, no con el cronograma.

## 7.4 Lista de entregables

**Documentales**
- E1. Memoria del TFM (plantilla UAX).
- E2. Este conjunto de documentos de planificación (`docs/`), actualizado al cierre.
- E3. Plan y protocolo experimental (escenarios de fallo, rúbrica de explicaciones, semillas, held-out) publicado a priori en el repo.
- E4. Presentación de defensa + demo grabada de respaldo.

**Software**
- E5. Repositorio Git con: módulos C1–C8, tests, CI mínima, docker-compose dual (arm64/x86-limitado), README con guía de reproducción paso a paso.
- E6. Emulador/generador de escenarios de fallo parametrizable (contribución C4).

**Datos y resultados**
- E7. Dataset sintético generado (sesiones normales y con fallo) con semillas y scripts de regeneración.
- E8. Resultados experimentales en bruto (CSV) + notebooks de análisis y figuras.
- E9. Corpus RAG empaquetado con manifiesto de licencias.
