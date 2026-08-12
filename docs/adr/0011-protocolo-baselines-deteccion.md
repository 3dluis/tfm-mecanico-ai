# ADR-0011 — Protocolo de evaluación y resultados de los baselines de detección

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 3

## Contexto

El plan exige empezar por baselines simples y explicables (reglas estadísticas, z-score robusto,
IForest, LOF, OC-SVM) y solo escalar a modelos temporales si aportan mejora demostrable. La
evaluación debe ser inmune a las trampas documentadas del área (benchmarks defectuosos, point
adjustment) y al riesgo de circularidad RI1.

## Protocolo (fijado a priori; implementado en `ai_models.evaluation.protocol`)

1. **Splits con semántica:** `train` = solo normal (el experimento aborta si contiene fallos);
   `validation` = normales + fallos conocidos (comparación y selección de hiperparámetros);
   `test` = normales + held-out + conocidos con semilla nueva (una sola evaluación final).
2. **Umbral solo con train:** cuantil (1−FPR objetivo, FPR=1 %) de los scores de ventanas
   normales de entrenamiento. Nunca se ajusta con validación ni test.
3. **Métricas point-wise SIN point-adjustment** (Kim et al., AAAI 2022) + **métricas por
   episodio** (episodio detectado si alguna ventana del intervalo de fallo supera el umbral;
   retardo hasta la primera detección) + FP-rate sobre ventanas normales.
4. **Registro reproducible** de cada run (`experiments/runs.jsonl`): suite, git sha, modelo,
   parámetros, semilla, umbral, métricas por split y por categoría, latencia de inferencia por
   ventana y pico de RSS.

## Resultados de la iteración (suite v1 cuantizada, semilla 42, FPR objetivo 1 %)

| Modelo | val F1 | test F1 | FPR test | Recall conocidos | Recall held-out (ventana) | Episodios | Retardo medio | ms/ventana |
|---|---|---|---|---|---|---|---|---|
| z-score robusto (max, mediana/MAD) | 0,53 | 0,44 | 0,103 | — | 0,00 | — | — | 0,001 |
| Isolation Forest (300 árboles) | 0,02 | 0,00 | 0,017 | 0,00 | 0,00 | 0/6 | — | 0,10 |
| **LOF (k=10, novelty)** | **0,77** | **0,65** | **0,035** | **0,99** | 0,26 | 4/6 | 30 s | 0,01 |
| OC-SVM (ν=0,01, γ=0,005) | 0,82 | 0,68 | 0,086 | 0,99 | 0,35 | **6/6** | 200 s | 0,004 |

Selección de hiperparámetros: barrido SOLO sobre validación (k∈{10,25,40,60};
γ∈{scale,0,05…0,005}; max_samples IF∈{64,128,256}).

## Lecturas de los resultados (hallazgos, para la memoria)

1. **El máximo |z| univariante y el IForest fracasan estructuralmente** ante normalidad
   multimodal (ralentí/urbano/autovía/arranque frío conviven en train): coherente con la
   conclusión de "no hay ganador universal" (Schmidl, VLDB 2022) y con la naturaleza *local*
   del problema — LOF (densidad local) es el que mejor la maneja.
2. **Los fallos conocidos son casi triviales a nivel de ventana (recall 0,99)**; el reto real
   son las anomalías held-out relacionales, exactamente como anticipaba la PI. A nivel de
   EPISODIO los held-out sí se detectan (LOF 4/6, OC-SVM 6/6): la señal existe pero es
   intermitente por ventana → margen para features temporales más ricas, no necesariamente
   para modelos más complejos.
3. **Compromiso LOF vs OC-SVM:** LOF domina en FPR (3,5 % vs 8,6 %); OC-SVM en cobertura de
   episodios. Ambos exportan a ONNX con paridad numérica exacta (máx |Δ| < 1e-6) y laten <2 ms
   por ventana en el runtime del edge → H4 holgada en la parte ML.
4. El pipeline vivo añade dos medidas de robustez metodológica surgidas de fallos reales
   observados: **cuantización J1979 en el offline** (ADR-0010 §4) y **gating de calentamiento**
   (las primeras 2 ventanas del viaje no se puntúan; los monitores OBD reales también exigen
   condiciones estables).

## Decisiones

- **Modelo por defecto del edge en la siguiente iteración: LOF k=10** (mejor F1/FPR); OC-SVM se
  conserva como segundo paquete versionado para el estudio comparativo del agente.
- Los autoencoders/modelos temporales SOLO se abordarán si superan a LOF en held-out con FPR ≤
  LOF (criterio de mejora demostrable exigido por el autor).
- Próxima mejora de features candidata (barata y dirigida por el análisis de errores):
  estadísticos de ventana multiescala y correlaciones retardadas (lag-1) para las anomalías
  temporales.

## Amenazas a la validez registradas

Los fallos y sus magnitudes los define el autor (RI1; mitigado con held-out estricto + semillas
nuevas en test, pero no eliminado); un único "vehículo" sintético; resultados sobre 21 sesiones
(~10,5 h simuladas) — suficiente para comparar baselines, no para afirmaciones fuertes de
generalización. La validación con normalidad real (HCRL) sigue pendiente.
