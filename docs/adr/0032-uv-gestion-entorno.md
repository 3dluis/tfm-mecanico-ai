# ADR-0032 — uv como gestor de entorno y dependencias del monorepo

**Estado:** Aceptada (decisión del autor, F13 · 2026-08-13)
**Relacionada con:** ADR-0003 (emulador ELM327), ADR-0006 (monorepo y tooling raíz),
ADR-0030 (PostgreSQL + pgvector edge), ADR-0031 (línea experimental ML)

## Contexto

El entorno de desarrollo se montaba con `pip install -e` por paquete (Makefile + CI),
sin lockfile: dos máquinas (o dos fechas) resolvían versiones distintas, lo que es
incompatible con la exigencia de reproducibilidad del TFM (§13 del Protocolo ML v1:
`library_versions` debe ser reconstruible). Además, al congelar el entorno afloró un
hueco real: `diagnostic-agent` usaba `psycopg`, `pgvector` y `alembic` (oficiales desde
ADR-0030) sin declararlos como dependencias — se instalaban ad hoc.

## Decisión

1. **uv gestiona el entorno del monorepo** mediante un *workspace*: el `pyproject.toml`
   raíz (virtual, sin `[project]`) declara los 5 miembros; cada miembro referencia
   `mecanico-contracts` (y entre sí donde aplique) vía `[tool.uv.sources]
   { workspace = true }`.
2. **`uv.lock` se committea** y es la única fuente de versiones: `make install` =
   `uv sync --all-packages --locked` (falla si el lock está desactualizado — mismo
   espíritu que el gate de esquemas). `.python-version` fija CPython 3.11.
3. **El grupo `dev` raíz** reúne todo lo que exige `make check`: ruff, mypy, pytest(+cov),
   pre-commit, types-PyYAML, los extras de miembros necesarios para el gate
   (`ai-models[export]`, `diagnostic-agent[detection]`) y el subconjunto ligero de tipado
   del runtime agéntico (langgraph, langchain-core) — sin arrastrar el extra `reasoning`
   completo (chromadb/sentence-transformers/ollama) al entorno de gate.
4. **Los comandos del Makefile corren vía `uv run`** (usan `.venv` del workspace sin
   activación manual); los nombres `make …` no cambian. CI usa `astral-sh/setup-uv` con
   caché + `uv sync --locked`.
5. **El emulador ELM327 queda FUERA del lock** (ADR-0003 exige `setuptools<81` +
   `--no-build-isolation`, incompatible con la resolución universal): se instala con
   `make install-emulator` (uv pip) y sus tests siguen saltándose si no está presente.
   CI lo instala igual que antes.
6. **Se corrigen dependencias no declaradas** de `diagnostic-agent`: `psycopg[binary]`,
   `pgvector`, `alembic` pasan a dependencias principales (ADR-0030).
7. **Docker no cambia en esta decisión**: los Dockerfiles siguen con pip; migrarlos a
   `uv sync --locked` es una mejora candidata separada (afecta a las imágenes edge/cloud
   y debe medirse en ARM64).

## Alternativas consideradas

- *Seguir con pip + requirements congelados a mano:* frágil (5 paquetes editable +
  extras), sin resolución universal multi-plataforma (Mac de desarrollo vs contenedor
  x86 vs RPi ARM64) y sin verificación `--locked` en CI.
- *Poetry / PDM:* cubrirían el lockfile, pero uv añade workspaces nativos para monorepo,
  es órdenes de magnitud más rápido y no introduce formato de lock propio por paquete.
- *conda/mamba:* sobredimensionado; ninguna dependencia exige binarios fuera de PyPI.

## Consecuencias

- Reproducibilidad: mismas versiones en Mac, sandbox y CI (`uv.lock`, 256 paquetes
  resueltos); el campo `library_versions` de los experimentos queda anclado al lock del
  commit correspondiente.
- Los flujos documentados cambian una sola línea: `python3 -m venv … && make install` →
  `make install` (uv crea `.venv` él mismo). Quien prefiera pip puede seguir usándolo
  (los `pyproject.toml` de los miembros siguen siendo estándar), pero el camino soportado
  y verificado es uv.
- Un warning de deprecación UPSTREAM (fastapi/testclient sobre starlette moderna) se
  silencia con un filtro DOCUMENTADO y específico en la config de pytest — no es un
  warning propio ni un ignore genérico.
- Pendiente declarado: migrar Dockerfiles a uv y validar en ARM64/RPi5 (junto a A2/A3).
