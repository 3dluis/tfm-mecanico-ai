# Mecánico IA — comandos canónicos del monorepo.
# Entorno gestionado por uv (ADR-0032): `make install` = uv sync desde uv.lock; todos los
# comandos python/tooling corren vía `uv run` (usa .venv del workspace, sin activar nada).
COMPOSE := docker compose
RUN := uv run

.PHONY: install install-emulator schemas lint type test check \
        dev research cloud edge full down \
        arm64-build eval-emulator \
        db-up db-upgrade db-revision db-psql pg-bench pg-vector-bench test-pg

# ------------------------------------------------------------- entorno local
install:  ## crea/sincroniza .venv desde uv.lock (miembros editable + grupo dev)
	uv sync --all-packages --locked
	$(RUN) pre-commit install

install-emulator:  ## emulador ELM327 (fuera del lock: setuptools<81 + no-build-isolation, ADR-0003)
	uv pip install "setuptools<81" wheel
	uv pip install --no-build-isolation "ELM327-emulator>=3.0.5"

schemas:  ## regenera los JSON Schema desde los contratos (ADR-0007)
	$(RUN) python -m mecanico_contracts.export_schemas shared/schemas

data-docs: schemas  ## regenera diccionario de datos + ejemplos desde los contratos (ADR-0012)
	$(RUN) python -m mecanico_contracts.gen_data_dictionary docs/data-architecture/02_diccionario_datos.md
	$(RUN) python tools/gen_data_examples.py

lint:
	$(RUN) ruff check shared obd-lab ai-models diagnostic-agent cloud-platform tools
	$(RUN) ruff format --check shared obd-lab ai-models diagnostic-agent cloud-platform tools

type:
	$(RUN) mypy

test:
	$(RUN) pytest

check: lint type test data-docs
	git diff --quiet shared/schemas docs/data-architecture || (echo "ERROR: schemas/diccionario desactualizados; commitea los regenerados" && exit 1)

# ------------------------------------------------------------ perfiles docker
dev:  ## núcleo edge: PostgreSQL+pgvector + emulador + agente + ollama (sin cloud)
	$(COMPOSE) --profile dev up --build

research:  ## jupyter para ai-models
	$(COMPOSE) --profile research up --build

cloud:  ## api cloud + postgres
	$(COMPOSE) --profile cloud up --build

edge:  ## agente con límites de recursos RPi 5 (ADR-0002)
	$(COMPOSE) --profile edge up --build

full:  ## todo (integración extremo a extremo)
	$(COMPOSE) --profile full up --build

down:
	$(COMPOSE) --profile full down

# ------------------------------------------------------------------- utilidades
arm64-build:  ## valida compatibilidad ARM64 de la imagen edge (ADR-0002)
	docker buildx build --platform linux/arm64 -f diagnostic-agent/Dockerfile -t mecanico-agent:arm64 .

eval-emulator:  ## evaluación práctica del emulador (Fase 1)
	$(RUN) python tools/eval_emulator.py

# ------------------------------------------------------------------ laboratorio
generate-suite:  ## genera las sesiones de la suite v1 en data/sessions
	$(RUN) python -m obd_lab.cli generate --suite obd-lab/scenarios/suite_v1.yaml --out data/sessions

registry:  ## reconstruye el Model Registry desde F3+F8+F9+F10+F13 (determinista)
	cd ai-models && $(RUN) python experiments/register_f3.py && $(RUN) python experiments/register_e2.py && $(RUN) python experiments/register_e3.py && $(RUN) python experiments/register_f10.py && $(RUN) python experiments/register_f13.py

experiments: generate-suite  ## reproduce el experimento E1 de baselines
	$(RUN) python ai-models/experiments/e1_baselines.py --sessions data/sessions

experiments-wide: generate-suite  ## reproduce el experimento E4 (F13): paridad del camino wide
	$(RUN) python ai-models/experiments/e4_wide_parity.py --sessions data/sessions

llm-smoke-deep:  ## smoke PROFUNDO del candidato R2 (Qwen2.5-3B-Instruct Q4_K_M; requiere Ollama)
	$(RUN) python tools/llm_smoke_deep.py

llm-bench:  ## benchmark agent-diagnostics v1 (tras superar el smoke; requiere Ollama)
	$(RUN) python tools/bench_agent_diagnostics.py --model qwen2.5:3b-instruct-q4_K_M

llm-smoke:  ## smoke comparativo de SLMs (requiere Ollama con los modelos descargados)
	$(RUN) python tools/llm_smoke.py

# ------------------------------------- persistencia edge: PostgreSQL + pgvector (ADR-0030)
MECANICO_DB_URL ?= postgresql+psycopg://mecanico:mecanico@localhost:15432/mecanico_edge

db-up:  ## levanta solo PostgreSQL+pgvector del edge
	$(COMPOSE) --profile edge-postgres up -d edge-postgres

db-upgrade:  ## aplica las migraciones Alembic (mecanismo OFICIAL de esquema)
	cd diagnostic-agent && MECANICO_DB_URL=$(MECANICO_DB_URL) $(RUN) alembic upgrade head

db-revision:  ## nueva revisión con autogenerado (revisar SIEMPRE el diff antes de commitear)
	cd diagnostic-agent && MECANICO_DB_URL=$(MECANICO_DB_URL) $(RUN) alembic revision --autogenerate -m "$(m)"

db-psql:  ## consola psql contra el edge
	psql "$(subst +psycopg,,$(MECANICO_DB_URL))"

test-pg:  ## tests de integración REALES contra PostgreSQL (se saltan si no hay BD)
	MECANICO_TEST_DB_URL=$(MECANICO_DB_URL) $(RUN) pytest tests-integration/test_pg_edge_e2e.py -q

pg-bench:  ## dimensionamiento: 1h/8h/24h de snapshots en PostgreSQL (WAL, disco, RAM, CPU)
	MECANICO_DB_URL=$(MECANICO_DB_URL) $(RUN) python tools/pg_edge_benchmark.py

pg-vector-bench:  ## baseline del RAG local: top-K sobre chunks/casos/patrones
	MECANICO_DB_URL=$(MECANICO_DB_URL) $(RUN) python tools/pg_vector_benchmark.py
