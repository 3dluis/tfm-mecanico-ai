# Artefactos: figuras, tablas y métricas con procedencia

Copias versionadas de los artefactos que **se usan en la memoria o sostienen una cifra de
ella**. Los runners siguen escribiendo en `figures/`, `tables/` y `experiments/` (rutas que
`.gitignore` excluye salvo los registros JSON); este directorio no cambia ese flujo, solo fija
qué versión de cada artefacto se entregó y de dónde salió. No hay figuras decorativas: cada
fichero se traza a experimento → configuración → script → registro de métricas → commit.

El commit indicado es el que introdujo el registro JSON o el informe de la fase en el
historial normalizado (`docs/git-sha-mapping.md`); la fecha es la de generación del fichero
en disco.

## Figuras (`artifacts/figures/`)

| Fichero | Experimento | Dataset / configuración | Script que la genera | Registro de métricas | Generada | Commit |
|---|---|---|---|---|---|---|
| `FIG-E4-01_series_normal_vs_fallo.png` … `FIG-E4-06_balance.png` (6) | E4 análisis exploratorio | `synthetic_v1`, bloques de 60 s, delta de Cliff | `src/mecanico_ia_exp/experiments/eda_runner.py` (`mecanico-exp eda`) | sin JSON; tablas `E4_*.csv` | 2026-09-01 14:11 | `057bd3a` (E4) |
| `FIG-E5-01_estudio_ventana.png`, `FIG-E5-02_particiones.png` | E5 ventanado y reparto | `synthetic_v2`, ventana 120 s, reparto por sesión | `preprocess_runner.py` (`mecanico-exp preprocess --dataset-id synthetic_v2`) | tablas `E5_*.csv` | 2026-09-01 15:43 | `a8e9f6c` (E5) |
| `FIG-E6-01_confusion_baseline.png`, `FIG-E6-02_limite_evidencia_f03.png` | E6 línea base | `synthetic_v2`, bosque aleatorio 400 árboles, semilla 20260901 | `baseline_runner.py` (`mecanico-exp train-baseline --dataset-id synthetic_v2`) | `experiments/E6_baseline_synthetic_v2.json` | 2026-09-01 15:44 | `770ce70` / `27b9f8d` |
| `FIG-E7-01_confusion_temporal.png`, `FIG-E7-02_entrenamiento.png` | E7 modelo temporal | `synthetic_v2`, GRU bidireccional, MPS, semilla 20260901 | `temporal_runner.py` (`mecanico-exp train-temporal --dataset-id synthetic_v2`) | `experiments/E7_temporal_synthetic_v2.json` | 2026-09-01 15:45 | `27b9f8d` |

Las figuras de E6 y E7 se escriben sin sufijo de dataset; las copiadas corresponden a la
ejecución sobre `synthetic_v2` (la posterior a la de `synthetic_v3`, por hora de generación).
La memoria no incluye figuras (`docs/audits/full_memory_review/14_TABLES_FIGURES_INVENTORY.md`);
estas son las que documentan los informes de fase y las que un revisor puede regenerar con
`scripts/reproduce_baseline.sh`.

## Tablas (`artifacts/tables/`)

| Fichero | Experimento | Generada por | Registro | Usada en |
|---|---|---|---|---|
| `E4_ausencias.csv`, `E4_balance_condicion.csv`, `E4_balance_regimen.csv`, `E4_descriptivos.csv`, `E4_separabilidad.csv` | E4 | `eda_runner.py` | — | `docs/experiments/E4_eda_temporal.md`; cap. 5 §Análisis descriptivo |
| `E5_estudio_ventana.csv`, `E5_reparto.csv` | E5 | `preprocess_runner.py` | — | `docs/experiments/E5_preprocesamiento.md`; cap. 4 Tabla 4.2 |
| `E6_baseline_confusion_synthetic_v2.csv`, `E6_baseline_importancias_synthetic_v2.csv`, `E6_baseline_por_clase_synthetic_v2.csv` | E6 | `baseline_runner.py` | `E6_baseline_synthetic_v2.json` | cap. 5 §PI.1 |
| `E7_temporal_confusion_synthetic_v2.csv`, `E7_temporal_por_clase_synthetic_v2.csv` | E7 | `temporal_runner.py` | `E7_temporal_synthetic_v2.json` | cap. 5 §PI.1 |
| `E9_atribuciones_synthetic_v2.csv`, `E9_resumen_synthetic_v2.csv` | E9 | `xai_runner.py` | `E9_xai_synthetic_v2.json` | `docs/experiments/E9_atribucion.md` |
| `E12_retrieval_por_caso.csv`, `E12_retrieval_por_estrategia.csv` | E12 (**RERUN-A, 13-09-2026**, recuperación canónica) | `retrieval_runner.py` | `E12_retrieval.json` (commit `e93dda9`) | cap. 5 §PI.2 |
| `E15_suficiencia.csv`, `E15_suficiencia_non_oracle.csv` | E15 (**RERUN-A, 13-09-2026**) | `sufficiency_runner.py` | `E15_suficiencia.json`, `E15_suficiencia_non_oracle.json` | cap. 5 §PI.3 y PI.4 |
| `E15b_barrido_umbral.csv` | E15b | `threshold_runner.py` | `E15b_barrido_umbral.json` (commit `35d2360`) | `docs/methodology/criterio-umbral-enmienda-01.md` |

Las tablas de E12 y E15 anteriores a RERUN-A no se versionaron en su día; sus valores caso a
caso están íntegros en los registros de `experiments/pre_mixed_embedding_fix/`.

## Métricas (`artifacts/metrics/`)

| Fichero | Contenido |
|---|---|
| `rerun_a_comparison.json` | Comparación antes/después de RERUN-A según el pre-registro: métricas de recuperación por estrategia y caso, M5 duplicados, vector de decisiones y motivos, señales, conjuntos de fragmentos por caso, líneas base invariantes, diagnóstico D-1/D-2 del distractor, linaje de E13b. Generada el 13-09-2026 a partir de los registros; interpretación en `docs/experiments/resultado-rerun-a.md` |

Los registros de métricas propiamente dichos viven en `experiments/*.json` y no se duplican aquí.

## Informes (`artifacts/reports/`)

Los informes de fase están en `docs/experiments/` y las auditorías en `docs/tfm/revision/` y
`docs/audits/`; este directorio queda como punto de entrada y contiene solo este índice.
