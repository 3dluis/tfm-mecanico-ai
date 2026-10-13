# Guía de revisión para el tribunal

Recorrido de 10–15 minutos. Cada afirmación remite a un fichero del repositorio. El lenguaje
es el de la memoria: lo que la evidencia indica, con su alcance.

## 1. Qué se investiga

Si un agente con recuperación aumentada puede explicar el diagnóstico de un vehículo a partir
de telemetría OBD-II de modo que **cada afirmación se pueda seguir hasta su evidencia** (una
observación o un fragmento del manual de taller) y **abstenerse** cuando esa evidencia no basta
(`docs/memoria/cap1_introduccion.md:25-28`). La decisión de explicar o abstenerse no la toma el
modelo de lenguaje: la toma un verificador determinista que examina la evidencia
(`docs/methodology/abstention-policy.md`, `src/mecanico_ia_exp/abstention/sufficiency.py`).

## 2. Qué aporta, en la medida en que la evidencia lo sostiene

- Un **verificador de suficiencia** con política escrita antes de implementarse y tres
  versiones congeladas, ninguna sobrescrita: v1 9/17 → v2 14/17 → v2.1 15/17
  (`docs/methodology/politica-suficiencia-v2*.md`, `experiments/E15_suficiencia_verifier_v*.json`).
- **Citas comprobadas contra el índice**: con el adaptador LoRA, 0 citas inventadas en 9 de 9
  casos (`experiments/E13_agente_transformers-lora@slm_lora_v2.json`).
- Evaluación **no oracular y adversa** con predicción declarada antes de medir
  (`docs/methodology/politica-evaluacion-no-oracular.md`), y una **reejecución pre-registrada**
  tras descubrir un defecto metodológico (`docs/methodology/preregistro-rerun-a.md`,
  `docs/experiments/resultado-rerun-a.md`).
- Un registro sistemático de lo que **no** funcionó (§5).

Lo que el trabajo **no** afirma: validez sobre datos reales (E3 no ejecutado), más de un
vehículo, resultados de test (todo es validación), ni inferencia confirmatoria sobre los
distractores (ningún valor p).

## 3. Dónde está la evidencia

| Evidencia | Ubicación |
|---|---|
| Pregunta de investigación | `docs/memoria/cap1_introduccion.md:25-28`; `research/decisions/ADR-004-pregunta-de-investigacion-canonica.md` |
| Objetivos | `docs/memoria/cap2_objetivos.md` |
| Hipótesis y criterios de refutación | `research/traceability-matrix.md` §2; `docs/memoria/cap4_marco_metodologico.md` Tabla 4.6 |
| Diseño experimental | `docs/methodology/experimental-design.md`; `docs/memoria/cap4_marco_metodologico.md` §Diseño |
| Dataset (definición y calibración) | `docs/experiments/E2_datos_sinteticos.md`; `docs/methodology/calibracion-datos-sinteticos.md`; `configs/calibracion_mazda3_bk.yaml`; muestra en `data/samples/` |
| Corpus y vehículo | `corpus/vehicles/mazda-3-bk-2007/{vehicle,manifest}.yaml`; `docs/rag/vehicle-corpus.md` |
| Línea base | `experiments/E6_baseline_synthetic_v2.json`; `docs/experiments/E6_baseline.md` |
| Experimentos principales | `experiments/E15_suficiencia.json` (oracular), `E15_suficiencia_non_oracle.json`, `E15_suficiencia_adverse.json`, `E13_agente_transformers-lora@slm_lora_v2.json`, `E12_retrieval.json` |
| Resultados negativos e inconclusos | `docs/experiment-index.md` §Resultados negativos; `docs/experiments/hallazgo-*.md`; `docs/experiments/E7_modelo_temporal.md` |
| Métricas (definición) | `docs/methodology/metrics.md` |
| Figuras y tablas usadas en la memoria | `artifacts/figures/`, `artifacts/tables/`, con procedencia en `artifacts/README.md` |
| Reproducibilidad | `docs/reproducibility.md`; `scripts/reproduce_baseline.sh`; `scripts/reproduce_main_results.sh` |
| Decisiones | `research/decisions/ADR-001…004`; `docs/tfm/revision/08_decisiones_autor_20260904.md` |
| Limitaciones | `docs/limitations.md`; `research/limitations-register.md` |
| Historial de trabajo | `git log`; `docs/git-history-report.md`; `docs/git-sha-mapping.md` |

## 4. Experimentos clave

**E6 · Línea base de diagnóstico.** Objetivo: referencia contra la que medir cualquier modelo.
Entradas: 392 ventanas de entrenamiento y 98 de validación de `synthetic_v2`, 139 descriptores.
Método: bosque aleatorio de 400 árboles con pesos por clase, semilla 20260901. Resultado:
macro-F1 0,879, ECE 0,144 (clase mayoritaria: 0,074). Interpretación: el problema sintético es
separable; la confianza está mal calibrada (L-14) y se calibra por isotónica antes de usarla en
el verificador. Ficheros: `experiments/E6_baseline_synthetic_v2.json`,
`docs/experiments/E6_baseline.md`, `artifacts/figures/FIG-E6-01_confusion_baseline.png`.

**E7 · Modelo temporal (negativo / inconcluso).** Objetivo: comprobar si una GRU supera a E6.
Criterio declarado: «si no la supera, su complejidad no está justificada». Resultado: 0,823
frente a 0,879 en `synthetic_v2`; en `synthetic_v3` gana por 0,0125, margen que el informe
declara inconcluso. Interpretación: la hipótesis PI.1, tal como está escrita («supera de forma
clara»), no se sostiene. Ficheros: `experiments/E7_temporal_synthetic_v{2,3}.json`,
`docs/experiments/E7_modelo_temporal.md`.

**E12 · Recuperación sobre el manual.** Objetivo: medir cuánto aporta filtrar por vehículo,
motor y autoridad. Entradas: 6 casos anotados (`configs/goldset_mazda3_bk.yaml`), 6 158
fragmentos del manual. Resultado: similitud pura hit-rate 0,00; guiada por el diagnóstico 1,00,
MRR 0,467 (5 casos puntuados, 1 excluido). Interpretación: el resultado se obtuvo el 1-09 con
un índice que mezclaba dos espacios de embeddings; se reejecutó el 13-09 con el espacio
declarado y las cifras son iguales (nDCG 0,642 → 0,653). El registro canónico es el del 13-09.
Ficheros: `experiments/E12_retrieval.json`, `experiments/pre_mixed_embedding_fix/E12_retrieval.json`,
`docs/experiments/resultado-rerun-a.md`.

**E15 · Explicar o abstenerse.** Objetivo: decidir EXPLAIN/ABSTAIN con un verificador
determinista bajo evidencia completa, parcial, ausente y con distractor. Método: verificador
v2.1, umbral de confianza 0,79 (fijado por criterio pre-escrito en E15b), 17 casos. Resultado:
15/17; abstiene 3/3 con evidencia ausente y 3/3 con parcial; falla C01 y C04 (evidencia
completa). Sin canales de oráculo, idéntico. Reejecutado el 13-09 con recuperación canónica:
idéntico. Interpretación: cota superior asistida por oráculo; la condición distractor resulta
redundante con la parcial en dos de tres fallos, así que PI.4 queda bajo diagnóstico. Ficheros:
`experiments/E15_suficiencia*.json`, `docs/experiments/resultado-verificador-v2-1.md`,
`docs/experiments/resultado-no-oracular-y-adverso.md`, `docs/experiments/resultado-rerun-a.md`.

**E13 · Redactor con citas comprobadas.** Objetivo: que el SLM redacte explicaciones válidas,
respete el veredicto del verificador y no invente citas. Criterio declarado: «después ≥ antes en
válidas, cero citas inventadas, veredicto no peor». Método: Qwen2.5-3B-Instruct con LoRA
(r = 16, 4 épocas, 62 ejemplos sin texto del manual), 9 casos. Resultado: 9/9 válidas, 9/9
veredicto respetado, 0 citas inventadas; el modelo base, 7/9 válidas. Interpretación: el ajuste
resolvió el formato, no el diagnóstico; el adaptador se entrenó sobre un conjunto de
procedencia indeterminada y no se ha reentrenado. Ficheros: `experiments/E13_agente_*.json`,
`docs/experiments/E13_agente_slm.md`, `models/slm_lora_v2/finetune_config.json`.

**RERUN-A · ¿Era inocuo el defecto?** Objetivo: comprobar si la mezcla de espacios de
embeddings alteraba evidencia y decisiones. Diseño pre-registrado antes de medir, sin
expectativa direccional. Resultado: los conjuntos recuperados crecen en 10 de 17 casos; las 17
decisiones son idénticas; las líneas base invariantes se reproducen. Interpretación (fijada de
antemano): sin efecto detectable con este instrumento; no es una validación del verificador.
Ficheros: `docs/methodology/preregistro-rerun-a.md`, `configs/manifest_rerun_a.json`,
`docs/experiments/resultado-rerun-a.md`, `artifacts/metrics/rerun_a_comparison.json`.

## 5. Resultados negativos e inconclusos

No se han retirado. El índice los marca como NEGATIVE, INCONCLUSIVE o SUPERSEDED, y la
evolución de un caso de EXPLICA a ABSTIENE (o al revés) entre versiones del verificador se
conserva como evidencia (`docs/experiment-index.md` §Resultados negativos). Los tres que más
pesan: E7 no supera a la línea base; la puerta de códigos de avería se omitía en silencio
(`docs/experiments/hallazgo-puerta-dtc-ausente.md`); el índice mezclaba dos espacios de
embeddings (`docs/methodology/politica-espacio-de-embeddings.md`).

## 6. Cómo reproducir el resultado principal

Sin base de datos ni manual (bloque de telemetría, minutos en Apple Silicon):

```
uv sync --all-extras
uv run mecanico-exp doctor --no-db
bash scripts/reproduce_baseline.sh
uv run pytest
```

Con PostgreSQL + pgvector y el manual de taller (`data/README.md`):

```
bash scripts/init_db.sh
uv run python scripts/ingest_mazda.py multilingual
bash scripts/reproduce_main_results.sh
```

## 7. Si quiere ejecutarlo

Seis pasos desde un clon, comprobados clonando el repositorio:
[`docs/reproducir-desde-cero.md`](docs/reproducir-desde-cero.md). Lo esencial: los conjuntos no se
distribuyen porque el generador los reconstruye **bit a bit**, y el guion de reconstrucción
contrasta sus huellas contra las que se congelaron antes de abrir el conjunto de prueba. Si alguna
difiere, falla.

Lo que **no** se puede reproducir —el corpus del manual, los pesos del adaptador, una reejecución de
E19— está declarado ahí con su motivo, y lo que se entrega en su lugar.

## 8. Si prefiere leerlo en vez de ejecutarlo

Cuatro notebooks explican los experimentos cerrados con sus gráficos, su interpretación y sus
limitaciones. Hay copia en HTML: se abren en cualquier navegador, sin instalar nada.

| Documento | Qué responde |
|---|---|
| [`00_introduccion`](docs/notebooks/html/00_introduccion.html) | el recorrido entero, de la señal OBD-II a la decisión de explicar o callar, y qué quedó demostrado |
| [`01_exploracion_obd`](docs/notebooks/html/01_exploracion_obd.html) | qué hay en los datos, incluido el caso en que la etiqueta dice «fallo» y la señal no lo contiene |
| [`02_comparacion_modelos`](docs/notebooks/html/02_comparacion_modelos.html) | por qué el modelo temporal no superó a la línea base, y por qué la explicación que se dio quedó retirada |
| [`03_analisis_e19`](docs/notebooks/html/03_analisis_e19.html) | la única medición sobre el conjunto de prueba, con sus numeradores y denominadores |

Cada uno dice al principio qué hace con la evidencia: si la reproduce, la reanaliza, la muestra tal
como quedó congelada o solo ilustra un concepto. Y cada gráfico lleva tres lecturas: qué muestra,
qué permite interpretar y **qué no permite afirmar**.

## 9. Si solo dispone de cinco minutos

1. Pregunta de investigación: `docs/memoria/cap1_introduccion.md` (líneas 25–28) y `README.md` §2.
2. Arquitectura: `README.md` §4 y `docs/methodology/experimental-design.md`.
3. Experimento baseline: `experiments/E6_baseline_synthetic_v2.json` y `docs/experiments/E6_baseline.md`.
4. Experimento principal: `experiments/E15_suficiencia.json` (clave `frozen`) y `docs/experiments/resultado-rerun-a.md`.
5. Resultados negativos: `docs/experiment-index.md` §Resultados negativos.
6. Figuras principales: `artifacts/figures/` (`FIG-E6-01`, `FIG-E7-01`, `FIG-E5-01`) con `artifacts/README.md`.
7. Matriz de trazabilidad: `docs/tfm-traceability.md`.
8. Reproducción: `docs/reproducibility.md` y `scripts/reproduce_baseline.sh`.
9. Si prefiere no ejecutar nada: `docs/notebooks/html/00_introduccion.html`, que recorre todo con sus figuras y sus limitaciones.
