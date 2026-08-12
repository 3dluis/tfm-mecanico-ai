# Comparación — Window vs Event vs Both v1 (EXP-ANOM-002, F8)

**Fuente:** `ai-models/experiments/e2_summary.json` + `e2_results.csv` +
`e2_per_scenario.csv` + `e2_event_quality.csv` (runner `e2_window_vs_event.py`, config
`configs/exp-anom-002.yaml`, git del run registrado en runs.jsonl y en el registro).

## 1. Pregunta experimental (PI.5/H6)

¿La segmentación de telemetría mediante eventos vehiculares mejora la capacidad de
detectar anomalías — especialmente las multivariables y temporales — respecto al
análisis basado únicamente en ventanas temporales arbitrarias?

**Hipótesis previa (pre-registrada en event-intelligence/11):** los eventos aportan
contexto que reduce falsas alarmas por mezcla de regímenes y mejora la localización de
anomalías relacionales; la combinación debería dominar en recall.

## 2. Nomenclatura

El plan de esta iteración etiquetó los brazos "A2/A3/A6"; como A0–A6 ya designan
**arquitecturas de agente** (ADR-0018), se conserva la nomenclatura registrada y los
brazos usan la dimensión `anomaly_mode`:

| Etiqueta del plan | Brazo | Contenido |
|---|---|---|
| "A2" | **AM-W** | ventanas 60/30 + LOF k=10 (config E1 exacta) |
| "A3" | **AM-E** | eventos `ed:1` + baseline-z por (event_type, context_signature) |
| — | **AM-E-NOCTX** | ablación: ídem SIN contexto (solo event_type) |
| "A6" | **AM-WE** | OR por tick de AM-W y AM-E (sin umbral nuevo) |

## 3. Protocolo (equidad por construcción)

Mismos datos que EXP-ANOM-001: suite v1 (21 sesiones), split `suite-v1-split-1`, mismas
semillas, held-out intocable. **Marco común por tick**: cada brazo marca los ticks que
cubren sus detecciones; GT = intervalo real del fallo. Umbrales al 1 % FPR objetivo
fijados SOLO con train: LOF por cuantil de train (reproduce exactamente el de E1:
0.1632 ✓); eventos por cuantil leave-one-session-out sobre train normal (evita el sesgo
in-sample). Ningún brazo recibe información extra; el detector de eventos jamás ve
etiquetas. Sin LLM.

## 4. Resultados globales (marco por tick)

| Brazo | Split | P | R | F1 | FPR | Episodios | Held-out | Retardo medio |
|---|---|---|---|---|---|---|---|---|
| **AM-W** | val | 0.96 | 0.69 | **0.80** | **0.030** | 5/5 | — | 84 s |
| **AM-W** | test | 0.89 | 0.54 | **0.67** | **0.067** | 4/6 | 2/4 | 15 s |
| AM-E | val | 0.64 | 0.38 | 0.48 | 0.229 | 3/5 | — | 53 s |
| AM-E | test | 0.76 | 0.47 | 0.58 | 0.149 | 4/6 | 2/4 | 177 s |
| AM-E-NOCTX | val | 0.79 | 0.38 | 0.51 | 0.104 | 3/5 | — | 404 s |
| AM-E-NOCTX | test | 0.73 | 0.40 | 0.52 | 0.149 | 3/6 | 1/4 | 19 s |
| AM-WE | val | 0.74 | **0.69** | 0.71 | 0.257 | **5/5** | — | 84 s |
| AM-WE | test | 0.77 | **0.63** | 0.69 | 0.189 | 4/6 | 2/4 | **4.2 s** |

## 5. Análisis

**5.1 El brazo de eventos NO sustituye a LOF-ventana.** Con el protocolo honesto (1 %
FPR objetivo, umbral train-only), AM-E queda por debajo en F1 y muy por encima en FPR.
**Este resultado se documenta como válido**: la hipótesis "evento reemplaza a ventana"
no se sostiene en las condiciones actuales.

**5.2 …pero la causa dominante del FPR es diagnóstica, no conceptual.** El FPR de AM-E
se concentra en normales de AUTOVÍA (0.41–0.52 por tick) mientras urbano queda casi
limpio (0.02–0.19). Dos mecanismos identificados: (a) solo hay 2 sesiones normales de
train por perfil → la varianza ENTRE sesiones (deriva aleatoria del LTFT del simulador)
domina los baselines; (b) en el marco por tick, un solo evento CONSTANT_SPEED falso de
autovía marca cientos de ticks — el coste por FP de un evento largo es estructuralmente
mayor que el de una ventana de 60 s.

**5.3 Señal complementaria real en el held-out relacional.** En `t-corrbreak-u`
(desacoplo RPM/MAF urbano, held-out): AM-E localiza R=0.73 con retardo 17 s frente a
R=0.25 y 30 s de AM-W. Es exactamente el tipo de anomalía relacional que motiva la PI —
la comparación por contexto la hace visible donde LOF apenas la delimita. En cambio en
autovía (`t-corrbreak-h`) ocurre lo contrario (AM-W R=1.0; AM-E R=0.08): la señal vive
en regímenes que el brazo de eventos cubre mal con los baselines actuales.

**5.4 La combinación mejora recall y retardo, con coste en FPR.** AM-WE: recall test
0.54→0.63, retardo medio 15→4.2 s, y en `t-corrbreak-u` R=0.79. FPR sube 0.067→0.189
(heredado de AM-E en autovía). Sin arreglo del FPR de autovía, la unión no es aceptable
para producción, pero demuestra complementariedad.

**5.5 Ablación: el context_signature aporta.** AM-E vs AM-E-NOCTX (mismo algoritmo,
features, regla de umbral; solo cambia el agrupamiento): F1 test 0.58 vs 0.52, held-out
2/4 vs 1/4, y en validación el sin-contexto degrada el retardo (404 s). Diferencias
pequeñas en valor absoluto (leer como direccionales), consistentes con la hipótesis
contextual y con CADD.

**5.6 Fallos que ningún brazo detecta.** `t-coolfreeze` y `t-jointdrift` siguen sin
detectarse por NINGÚN brazo (igual que en E1) — el techo actual no lo pone la
representación sino la sensibilidad de los detectores a derivas lentas conjuntas.
`v-thermo` y `v-misfire` los pierde AM-E (contextos fríos con pocos baselines; la firma
del misfire es de alta frecuencia y las medias por evento la diluyen) pero los cubre
AM-W → otra evidencia de complementariedad.

**5.7 Cobertura y coste.** AM-E puntúa el 87.7 % de los eventos (111/902 sin baseline
aplicable — contextos fríos/raros; honestidad: no se flaggean). Coste computacional del
brazo de eventos: **inferior** al de ventanas (features 0.15 s vs 0.52 s por suite;
modelo 38 KB vs 142 KB; 9 ms vs 28 ms por sesión de 30 min; 20 vs 42 features). La capa
Event Intelligence NO es cara: RSS pico del experimento completo 213 MB.

**5.8 Calidad del detector de eventos en la suite** (vs GT, IoU≥0.5, media val+test):
F1 por tipo 0.71–1.00, onset 0–9 ticks, duration error 4–19 ticks (detalle en
`e2_event_quality.csv`) — consistente con el slice F6 sobre perfiles nuevos (highway,
cold_start, idle).

## 6. Baseline global vs por-vehículo

**No evaluable en esta iteración**: la suite v1 simula UN único vehículo, de modo que
"baseline específico del vehículo" y "baseline global" coinciden. Se documenta la
limitación sin forzar conclusiones (requeriría ≥2 perfiles de vehículo independientes en
obd-lab — candidato a EXP-ANOM-003).

## 7. Limitaciones

Datos 100 % sintéticos; 6 episodios de test (diferencias de 1–2 episodios NO son
concluyentes — todas las lecturas por episodio son direccionales); train normal pequeño
(6 sesiones, 2 por perfil) que penaliza específicamente al brazo de eventos; el marco
por tick — elegido por equidad — amplifica el coste de los FP de eventos largos (una
métrica por-evento daría otra lectura del FPR y se añadirá en la v2 de esta comparación);
un solo vehículo (§6); umbral de eventos LOSO con solo 6 sesiones (cuantil inestable).

## 8. Decisión

1. **LOF k=10 (ventanas) SIGUE siendo el modelo por defecto** — sin cambio de selección,
   sin supersession de ADR (la conclusión de EXP-ANOM-001 se mantiene).
2. `event-baseline-z` permanece **CANDIDATE**: valor demostrado como señal COMPLEMENTARIA
   (localización del held-out relacional urbano, retardo) — no como sustituto.
3. La combinación se registra como `anom-combined-we@0.1.0` (EXPERIMENTAL): prometedora
   en recall/retardo, no aceptable sin resolver el FPR de autovía.
4. **No se afirma que Event Intelligence "mejore la detección" en general**: mejora la
   localización de UNA anomalía relacional y el retardo de la unión; empeora FPR. Ambas
   caras quedan documentadas.
5. Mejora prioritaria identificada (para aprobación, NO ejecutada): ampliar el train
   normal por contexto (más semillas normales; barato y no toca held-out) + métrica
   complementaria por-evento → EXP-ANOM-003.
