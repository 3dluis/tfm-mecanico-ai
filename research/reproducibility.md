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

## Estado por fase

| Fase | Reproducible | Artefactos | Semilla |
|---|---|---|---|
| E1 entorno | sí | `docs/experiments/E1_entorno.md`, `notebooks/00_environment_check.ipynb` | — |
| E2 datos sintéticos | sí | `data/raw/synthetic/synthetic_v1.parquet` + `.meta.json`; `uv run mecanico-exp generate-synthetic` | **20260901** |
| E3-E20 | `[EXPERIMENT_REQUIRED]` | — | — |

E2 verifica que dos ejecuciones con la misma semilla producen ficheros idénticos, y que dos
semillas distintas no.

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
