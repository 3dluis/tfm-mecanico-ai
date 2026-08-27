# 12 — Diseño experimental de arquitecturas (A0–A6)

> **⚠ Fuera del alcance experimental del TFM (ADR-0036, 27-ago-2026).** Tras la
> acotación de la pregunta de investigación a explicación diagnóstica trazable y
> abstención ante evidencia insuficiente, la ablación de arquitecturas agénticas no forma parte de la validación
> experimental de este trabajo. **El diseño y el código se conservan** y siguen siendo
> correctos; simplemente no se evalúan. Catálogo completo y justificación:
> [`docs/alineacion_v4/05_fuera_de_alcance.md`](../../alineacion_v4/05_fuera_de_alcance.md).

> **Nota F8:** las etiquetas A0–A6 designan ARQUITECTURAS DE AGENTE (esta página). La
> comparación de detección window/event/both (R1+E1) usa la dimensión `anomaly_mode`
> (AM-W/AM-E/AM-WE) y se cerró SIN LLM antes de los experimentos de agentes — resultado
> en [models/comparisons/anomaly_window_vs_event_v1.md](../models/comparisons/anomaly_window_vs_event_v1.md).
> Decisión F8: la entrada por defecto del sistema agéntico sigue siendo LOF-ventana; los
> eventos entran como evidencia complementaria (no como detector sustituto).

[← Índice](README.md) · ADR: [0018](../adr/0018-diseno-experimental-arquitecturas.md)

## Arquitecturas comparadas (por FEATURE FLAGS, no productos distintos)

Una única base de código; `RuntimeConfig` habilita/deshabilita componentes:

| Arq. | Descripción | Flags |
|---|---|---|
| A0 | ML baseline (sin LLM/agente): detección + regla de mapeo directo a causa | detector only |
| A1 | LLM + RAG (una pasada, sin grafo) | hypothesizer+retriever, sin verify/loop |
| A2 | Single Agent + RAG (= grafo lineal g1 de F4) | grafo lineal, memory_mode=none |
| A3 | Multi-Agent + RAG | runtime, recall/critic OFF, loop OFF |
| A4 | A3 + memoria episódica | recall ON (episodic) |
| A5 | A4 + memoria evolutiva | recall ON (episodic+semantic) |
| A6 | Full runtime + loop engineering | critic ON, loop ON, re-planificación |

## Métricas (todas computables desde la BD; doc 11)

Precisión diagnóstica top-1/top-k contra ground truth de obd-lab (DiagnosticFeedback) ·
recall de la causa correcta · false diagnosis rate (afirmar causa incorrecta con
PROBABLE/CONFIRMED) · unsupported claims (hipótesis sin evidencia de soporte) · evidence
coverage · nº de iteraciones y tool calls · tiempo de diagnóstico · tokens · CPU/RAM ·
energía (solo RPi física, opcional).

## Protocolo

Mismo lote de casos (suite de obd-lab ampliada: conocidos con semillas nuevas + held-out),
mismas semillas, mismo modelo por brazo (mapa del router fijado), una arquitectura por
pasada. Los brazos con LLM se ejecutan además con el HeuristicHypothesizer como control
(aísla la contribución del LLM de la de la arquitectura).

## Hipótesis experimental adicional (análisis del encargo §21)

**Encaja como hipótesis secundaria H5 sin cambiar la pregunta principal** — de hecho la
descompone: la PI pregunta si el agente híbrido puede descubrir y explicar patrones no
documentados; H5 pregunta QUÉ COMPONENTES de la arquitectura contribuyen a ello.

> **H5:** La incorporación de memoria episódica, memoria evolutiva y ciclos iterativos de
> verificación (A4–A6) mejora la capacidad de identificar y explicar fallos previamente no
> observados — medida como precisión top-1/top-k, unsupported claims y evidence coverage
> sobre los escenarios held-out — respecto a un agente sin memoria y de ejecución única (A1–A2).

Es falsable, usa la infraestructura ya construida (memory_mode + flags + ground truth) y
subsume H3 (efecto de la memoria) como su componente A4-vs-A2/A3. Recomendación: presentarla
al tutor junto con la redefinición operativa ya pendiente de validación.
