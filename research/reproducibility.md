# Reproducibilidad

Qué hace falta para reproducir cada resultado. Se rellena por experimento, **al ejecutarlo**.

## Entorno oficial verificado

| Componente | Versión | Verificado en |
|---|---|---|
| Hardware | Apple M4 Pro, 24 GB | E1 |
| Sistema | macOS 26.6.2 (Darwin 25.6.0), arm64 | E1 |
| Python | 3.11.14, gestionado por uv | E1 |
| uv | 0.10.2 — gestor oficial, sin `pip install` suelto | E1 |
| PyTorch | 2.13.0, MPS comprobado con una operación real | E1 |
| PostgreSQL | 14.15 (Homebrew), puerto 5432 | E1 |
| pgvector | 0.8.0, más `pg_trgm`, en la base `mecanico_ia_exp` | E1 |
| Docker | 29.3.1 + Compose v5.1.1 — solo portabilidad | E1 |
| Ollama | instalado — **opcional, nunca en resultados oficiales** | E1 |

Colab no interviene. Docker no es el entorno principal.

## Qué registra cada ejecución

`experiment_id` · commit · versión del dataset · versión del corpus · versión del modelo ·
modelo de embeddings · proveedor y modelo de lenguaje · versión del prompt · semilla ·
parámetros · métricas. En JSON y CSV, bajo `experiments/`.

**Ningún número llega a la memoria sin proceder de uno de esos registros.**

### Cinco registros anteriores a esta convención

`experiments/E6_baseline_synthetic_v2.json`, `E6_baseline_synthetic_v3.json`,
`E7_temporal_synthetic_v2.json`, `E7_temporal_synthetic_v3.json` y `E9_xai_synthetic_v2.json`
**no llevan cabecera de identificación**: les faltan `commit`, `executed_at`, `dirty` y
`dataset_type`. Son de antes de que la convención existiera.

**No se regeneran para arreglarlo.** Regenerar cambiaría las cifras publicadas, que es un precio
mucho más alto que el de declarar la carencia: lo que se pierde es poder anclar esas cinco
ejecuciones a un commit exacto, y eso se dice en lugar de disimularlo. A cambio, **todo registro
nuevo de PI.1 lleva la cabecera**, y además el **protocolo** del que sale, para que una cifra nueva
no se confunda con una corrección silenciosa de la anterior.

`CORRECTED 2026-10-12`.

## Estado por fase

| Fase | Reproducible | Artefactos | Semilla |
|---|---|---|---|
| E1 entorno | sí | `docs/experiments/E1_entorno.md`, `notebooks/00_environment_check.ipynb` | — |
| E2 datos sintéticos | sí | `data/raw/synthetic/synthetic_v1.parquet` + `.meta.json`; `uv run mecanico-exp generate-synthetic` | **20260901** |
| E3 datos reales | pendiente — validación externa (ADR-003), sin fuente | — | — |
| E4 análisis exploratorio | sí | `tables/E4_*.csv`, `figures/FIG-E4-*.png` | — |
| E5 preprocesamiento | sí | `synthetic_v2`; ventana 120 s; reparto por sesión; `noise_floor_max_delta` como función reutilizable | registrada |
| E6 baseline | sí | `experiments/E6_baseline.json`, `tables/E6_*.csv`, `figures/FIG-E6-*.png`; `uv run mecanico-exp train-baseline` | registrada |
| E7-E20 | `[EXPERIMENT_REQUIRED]` | — | — |

E2 verifica que dos ejecuciones con la misma semilla producen ficheros idénticos, y que dos
semillas distintas no.

## Cierre del conjunto de test

No es una convención: es un cierre técnico. `load_partition("test")` **lanza una excepción**;
abrirlo exige `allow_test=True` **y una razón por escrito**, que se imprime en la salida de la
ejecución. Tres tests comprueban el cierre, incluido que el mensaje indique usar validación.

La disciplina no se confía a la memoria de quien escribe el código: un descuido produce una
excepción, no un resultado inválido que nadie note.

## Regla de honestidad

Si no se ejecutó, no se declara ejecutado. Si el hardware no se probó, no se declara validado
—**Raspberry Pi incluida** (L-11)—. Los resultados obtenidos con Ollama no se mezclan con los
oficiales.

## Datos y artefactos excluidos del control de versiones

`data/`, `corpus/raw|processed/`, `models/`, `results/`, `figures/`, `tables/` y
`experiments/runs/` están en `.gitignore` **por diseño**: se regeneran. Se versionan los
`.gitkeep`, los manifiestos de corpus, los `.md` de datos y `results/RESULTADOS_TFM.md`.

Consecuencia: la reproducibilidad depende de que el **generador** esté versionado y sea
determinista, no de que lo esté su salida. Es correcto, y hay que decirlo en el capítulo 4.
