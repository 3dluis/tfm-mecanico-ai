# 06 — Memoria del agente: tres niveles y evolución

[← Índice](README.md) · ADR: [0013](../adr/0013-memoria-tres-niveles.md) · Diagrama: [diagnostic-memory-flow.mmd](diagrams/diagnostic-memory-flow.mmd)

## Nivel 1 — Working memory (efímera)

Estado del grafo durante una ejecución: anomalía actual, contexto, hipótesis en curso,
evidencias recuperadas. NO se persiste como tal; su traza sí, como `AgentRun` + `AgentStep`
(+`RetrievalEvent`), con entradas/salidas ESTRUCTURADAS por nodo — nunca chain-of-thought ni
razonamiento libre del modelo. `AgentRun.memory_mode` registra qué memoria estaba habilitada
(variable del experimento H3).

## Nivel 2 — Memoria episódica (CaseMemory)

Experiencias diagnósticas recuperables por similitud: firma numérica de síntomas
(`symptom_signature`, coseno), texto sintomático (embedding en la iteración RAG), DTCs,
detector, perfil de vehículo, firma temporal. **Cada caso lleva `EpistemicLevel`**
(SIMULATED/SYNTHETIC/PUBLIC_DATASET/REAL_UNVALIDATED/HUMAN_VALIDATED) y la recuperación
pondera similitud × peso epistemológico (0,5 … 1,0): un escenario simulado jamás adquiere
automáticamente el peso de un caso real confirmado.

## Nivel 3 — Memoria semántica/evolutiva (LearnedPattern)

Patrones consolidados que emergen de múltiples casos: firma de telemetría (centroide),
firma temporal, métricas afectadas, DTCs y modos de fallo relacionados, casos a favor Y en
contra, nº de sesiones independientes y de vehículos distintos, `confidence`,
`novelty_score` (distancia a lo documentado — el candidato operativo a "patrón no
documentado" de la PI), `validation_level` y estado:

```
CANDIDATE → EMERGING → VALIDATED
    ↓           ↓
 REJECTED   SUPERSEDED → RETIRED
```

`PatternRelation` (SIMILAR_TO, CONTRADICTS, SUPERSEDES, SPECIALIZATION_OF,
GENERALIZATION_OF, CO_OCCURS_WITH, PRECEDES) forma un grafo ligero sobre SQL — sin graph-DB
mientras el volumen no lo justifique.

## Proceso de evolución (diseñado; promoción NO automática en esta fase)

```
Experiencia diagnóstica → CaseMemory → análisis de similitud
   ├─ ¿patrón conocido? SÍ → actualización de evidencia (supporting/contradicting, touch last_seen)
   └─ NO → LearnedPattern CANDIDATE (única transición implementada)
                → acumulación de casos → consolidación (EMERGING: umbrales de nº de sesiones
                  independientes/vehículos + ausencia de contradicciones dominantes)
                → validación → VALIDATED
```

**Implementado hoy:** registro de CANDIDATE desde el nodo `memorize` cuando un episodio no
casa con nada documentado; acumulación de soporte (`touch`, supporting_cases);
contradicciones y versionado en el modelo. **Deliberadamente NO implementado** (requiere
aprobación): promoción automática EMERGING/VALIDATED y fusión de candidatos — los umbrales
de consolidación son ellos mismos objeto de investigación.

## Experimento de memoria evolutiva (preparado desde ya)

`AgentRun.memory_mode ∈ {none, episodic, episodic_semantic}` permite el diseño:

| Métrica | Fuente |
|---|---|
| Precisión diagnóstica / ranking de la causa correcta | DiagnosticFeedback (ground truth obd-lab) vs hipótesis rank |
| Recall de la causa correcta en top-k | ídem |
| Calidad de explicación | rúbrica + evidencias por caso |
| Nº de hipótesis innecesarias | hipótesis CONTRADICTED por caso |
| Tiempo hasta diagnóstico / tokens | AgentRun.latency_ms, tokens_in/out |
| Recuperación relevante | RetrievalEvent vs casos realmente útiles (usados en hipótesis ganadora) |

El mismo lote de anomalías se ejecuta 3 veces (un modo cada vez) con semillas y versiones
fijadas; todo lo necesario ya se persiste.
