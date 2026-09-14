# Reproducibilidad

Estado: **borrador** (13-09-2026). Reúne en un solo sitio lo que ya está disperso en
`research/reproducibility.md` (entorno verificado en E1), `docs/EXPERIMENTO_PASO_A_PASO.md`
(secuencia de comandos), `pyproject.toml` / `uv.lock` (versiones) y los registros de
`experiments/`. Ningún valor de esta página se ha medido de nuevo: todos tienen fuente.

## Entorno verificado (E1, `research/reproducibility.md`)

| Componente | Valor |
|---|---|
| Hardware | Apple M4 Pro, 24 GB |
| Sistema | macOS 26.6.2 (Darwin 25.6.0), arm64 |
| Python | 3.11.14 (`.python-version` = 3.11; `pyproject.toml` `>=3.11,<3.12`) |
| uv | 0.10.2 |
| PostgreSQL / pgvector | 14.15 (Homebrew) / 0.8.0, más `pg_trgm` |
| Acelerador | MPS (PyTorch). CUDA no se contempla (`config/environment.py:93-99`) |
| Docker | 29.3.1 + Compose v5.1.1, solo para portabilidad (`compose.yaml`: `pgvector/pgvector:pg16` en el puerto 5433) |

Los registros JSON **no** graban plataforma, versión de Python ni hostname; solo
`device: "mps"` en E7. Es una carencia conocida (ver riesgos).

## Versiones fijadas en `uv.lock`

| Paquete | Versión | Paquete | Versión |
|---|---|---|---|
| numpy | 2.4.6 | torch | 2.13.0 |
| scipy | 1.17.1 | shap | 0.51.0 |
| pandas | 3.0.5 | transformers | 5.16.1 |
| scikit-learn | 1.9.0 | peft | 0.20.0 |
| sqlalchemy | 2.0.52 | sentence-transformers | 6.0.1 |
| alembic | 1.19.1 | psycopg (binary) | 3.3.5 |
| pydantic / pydantic-settings | 2.13.5 / 2.15.0 | pgvector | 0.5.0 |
| pyarrow | 25.0.1 | matplotlib / seaborn | 3.11.1 / 0.13.2 |
| ruff / mypy / pytest | 0.16.5 / 2.3.1 / 9.1.1 | nbformat | 5.11.1 |

No hay SDK de ningún proveedor LLM: la comunicación es HTTP con `httpx` 0.28.1
(`pyproject.toml:45-48`). `uv.lock` está en sincronía con `pyproject.toml` (mismo commit
`a6057fd`; `requires-dist` idéntico).

## Modelos

| Modelo | Identificador | Dónde se fija |
|---|---|---|
| Embeddings (canónico) | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones | `src/mecanico_ia_exp/rag/embeddings.py:186-190`; `migrations/versions/0003_embeddings.py` |
| Embeddings (inglés) | `sentence-transformers/all-MiniLM-L6-v2`, 384 d | ídem |
| SLM base | `Qwen/Qwen2.5-3B-Instruct` | `src/mecanico_ia_exp/llm/finetune.py:40` |
| Adaptadores LoRA | `models/slm_lora`, `models/slm_lora_v2`: r = 16, α = 32, dropout 0,05, `q/k/v/o_proj`, 4 épocas, lr 2e-4, seq 3072, bf16, MPS; 7 372 800 parámetros entrenables | `models/slm_lora*/{adapter_config.json,finetune_config.json}` (versionados); pesos `adapter_model.safetensors` (28 MB cada uno) **no versionados** |
| Ollama (opcional, fuera de resultados oficiales) | `qwen2.5:3b-instruct-q4_K_M` | `llm/provider.py:183-184` |

La descarga del modelo base de Hugging Face ocurre de forma implícita en
`AutoModelForCausalLM.from_pretrained`; no hay comando de descarga documentado.

## Semillas

Semilla global **20260901** (`config/settings.py:65`, `cli.py:31`, `models/baseline.py:30`,
`models/temporal.py:50`, `data/splits.py:37`, `llm/finetune.py:60`, `rag/embeddings.py:80`,
`xai/attribution.py`); `torch.manual_seed` + `torch.mps.manual_seed` + `np.random.seed` en
`models/training.py:78-81`. Semillas locales distintas: `obd/engine.py:115` (42),
`data/exploration.py:283` (7), `llm/training_data.py:165` (0), `xai/attribution.py:90` (0).
No se fija `PYTHONHASHSEED` ni `torch.use_deterministic_algorithms`.

## Datos

- Telemetría: **sintética**, generada por `uv run mecanico-exp generate-synthetic` con la
  semilla anterior; no se versiona, se regenera (`.gitignore:29-34`). E2 comprobó que dos
  ejecuciones con la misma semilla producen ficheros idénticos.
- Corpus: manual de taller del Mazda 3 BK 2007 (3 055 PDF, 238 MB), `access_type: licensed`,
  `redistributable: false`, `verified: false` (`corpus/vehicles/mazda-3-bk-2007/manifest.yaml`).
  Entra por un **enlace simbólico** a una ruta de la máquina del autor
  (`corpus/vehicles/mazda-3-bk-2007/raw/user-provided/workshop-manual`). Huellas: 6 158
  fragmentos con `content_hash`; estado congelado en `configs/manifest_rerun_a.json`.
- Conjunto anotado: `configs/goldset_mazda3_bk.yaml` (versionado).

## Identificadores de commit anteriores al 13-09-2026

El historial de `main` se normalizó el 13-09-2026 (retirada de trailers automáticos en 69
mensajes). Los SHA anteriores a esa fecha que aparecen en el campo `commit` de los registros
JSON, en `configs/manifest_rerun_a.json` y en documentos de método no se han editado: se
resuelven con la tabla de `docs/git-sha-mapping.md` o directamente contra la rama de archivo
`backup/pre-history-cleanup-20260913-1815`, que conserva el historial original de forma
permanente (`git show <sha-antiguo>` funciona mientras exista esa rama). Los registros de
RERUN-A (13/14-09) citan ya SHA del historial normalizado.

## Muestra de datos y scripts

`data/samples/synthetic_sample.parquet` (18 sesiones, 1,3 MB) permite ejecutar el flujo
`preprocess → train-baseline` sin regenerar nada (`data/README.md`). `scripts/reproduce_baseline.sh`
y `scripts/reproduce_main_results.sh` encadenan los comandos de abajo y muestran el `diff` con
los registros versionados.

## Ruta mínima para el tribunal

Sin PostgreSQL ni manual de taller se reproduce el bloque de telemetría (E2 → E9):

```
uv sync --all-extras
uv run mecanico-exp doctor --no-db
uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 --sessions-per-fault 12
uv run mecanico-exp eda
uv run mecanico-exp preprocess --dataset-id synthetic_v2
uv run mecanico-exp train-baseline --dataset-id synthetic_v2     # → experiments/E6_baseline_synthetic_v2.json, FIG-E6-01
uv run mecanico-exp train-temporal --dataset-id synthetic_v2     # → experiments/E7_temporal_synthetic_v2.json, FIG-E7-01/02
uv run mecanico-exp xai                                          # → experiments/E9_xai_synthetic_v2.json
uv run mecanico-exp threshold-sweep --dataset-id synthetic_v2    # → experiments/E15b_barrido_umbral.json
```

Con PostgreSQL + pgvector y el manual disponible, continúa con `bash scripts/init_db.sh`,
`uv run python scripts/ingest_mazda.py multilingual`, `uv run mecanico-exp eval-retrieval`
y `uv run mecanico-exp sufficiency [--mode oracle|non-oracle|adverse] [--llm …]`
(`docs/EXPERIMENTO_PASO_A_PASO.md:428-446`).

Gate de calidad: `uv run ruff check . && uv run mypy src && uv run pytest`.

Nota sobre `uv sync --frozen`: `uv.lock` está en sincronía con `pyproject.toml`, así que
`uv sync --frozen --all-extras` es equivalente y más estricto; el proyecto documenta
`--all-extras` sin `--frozen`.

## Riesgos para la reproducibilidad (ordenados por gravedad)

1. **El corpus no es redistribuible y entra por un symlink absoluto** a la máquina del autor.
   Un tercero no puede ejecutar E11–E15 sin conseguir el manual por su cuenta; el manifiesto
   además declara procedencia no verificada.
2. **El adaptador LoRA no es canónico**: se entrenó sobre un conjunto generado con
   recuperación de procedencia indeterminada (`MIXED-EMBEDDING-SPACE`). RERUN-A (13/14-09)
   fijó registros canónicos para E12, E15, E13b y E13, con decisiones idénticas; el
   reentrenamiento del adaptador sigue pendiente (`docs/experiments/resultado-rerun-a.md`).
3. **Los pesos LoRA no están versionados** (28 MB × 2); se regeneran con `finetune-slm`
   (~75 min). Las tablas y figuras usadas en la memoria sí están, desde el 13-09, en
   `artifacts/` con su procedencia (`artifacts/README.md`).
4. **Sin CI ni pre-commit**: los gates dependen de ejecución manual.
5. **Registros sin huella de máquina** y **sin `commit`/`executed_at` en siete JSON** (E6, E7,
   E9, E13b, E13 echo/ollama/esquema_v1).
6. **Determinismo en MPS** apoyado solo en semillas; no se garantiza bit-exactitud.
7. `.env.example` fija `EMBEDDING_DIM=768` cuando la dimensión real es 384, y documenta
   variables que el código no lee.
8. Los tests marcados `db` y `llm` requieren servicios externos; sin ellos la suite no se
   ejecuta completa.
