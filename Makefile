# Mecánico IA — comandos canónicos del monorepo.
COMPOSE := docker compose

.PHONY: install schemas lint type test check \
        dev research cloud edge full down \
        arm64-build eval-emulator \
        db-up db-upgrade db-revision db-psql pg-bench pg-vector-bench test-pg

# ------------------------------------------------------------- entorno local
install:  ## instala todos los proyectos en editable + tooling (venv activo)
	pip install --upgrade pip "setuptools<81" wheel
	pip install -e ./shared
	pip install --no-build-isolation "ELM327-emulator>=3.0.5"
	pip install -e "./obd-lab[dev]"
	pip install -e "./ai-models[dev]"
	pip install -e "./diagnostic-agent[detection,dev]"
	pip install -e "./cloud-platform[dev]"
	pip install ruff mypy pytest pytest-cov pre-commit
	pre-commit install

schemas:  ## regenera los JSON Schema desde los contratos (ADR-0007)
	python -m mecanico_contracts.export_schemas shared/schemas

data-docs: schemas  ## regenera diccionario de datos + ejemplos desde los contratos (ADR-0012)
	python -m mecanico_contracts.gen_data_dictionary docs/data-architecture/02_diccionario_datos.md
	python tools/gen_data_examples.py

lint:
	ruff check shared obd-lab ai-models diagnostic-agent cloud-platform tools
	ruff format --check shared obd-lab ai-models diagnostic-agent cloud-platform tools

type:
	mypy

test:
	pytest

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
	python tools/eval_emulator.py

# ------------------------------------------------------------------ laboratorio
generate-suite:  ## genera las sesiones de la suite v1 en data/sessions
	python -m obd_lab.cli generate --suite obd-lab/scenarios/suite_v1.yaml --out data/sessions

registry:  ## reconstruye el Model Registry desde F3+F8+F9+F10 (determinista)
	cd ai-models && python experiments/register_f3.py && python experiments/register_e2.py && python experiments/register_e3.py && python experiments/register_f10.py

experiments: generate-suite  ## reproduce el experimento E1 de baselines
	python ai-models/experiments/e1_baselines.py --sessions data/sessions

llm-smoke-deep:  ## smoke PROFUNDO del candidato R2 (Qwen2.5-3B-Instruct Q4_K_M; requiere Ollama)
	python tools/llm_smoke_deep.py

llm-bench:  ## benchmark agent-diagnostics v1 (tras superar el smoke; requiere Ollama)
	python tools/bench_agent_diagnostics.py --model qwen2.5:3b-instruct-q4_K_M

llm-smoke:  ## smoke comparativo de SLMs (requiere Ollama con los modelos descargados)
	python tools/llm_smoke.py

# ------------------------------------- persistencia edge: PostgreSQL + pgvector (ADR-0030)
MECANICO_DB_URL ?= postgresql+psycopg://mecanico:mecanico@localhost:15432/mecanico_edge

db-up:  ## levanta solo PostgreSQL+pgvector del edge
	$(COMPOSE) --profile edge-postgres up -d edge-postgres

db-upgrade:  ## aplica las migraciones Alembic (mecanismo OFICIAL de esquema)
	cd diagnostic-agent && MECANICO_DB_URL=$(MECANICO_DB_URL) alembic upgrade head

db-revision:  ## nueva revisión con autogenerado (revisar SIEMPRE el diff antes de commitear)
	cd diagnostic-agent && MECANICO_DB_URL=$(MECANICO_DB_URL) alembic revision --autogenerate -m "$(m)"

db-psql:  ## consola psql contra el edge
	psql "$(subst +psycopg,,$(MECANICO_DB_URL))"

test-pg:  ## tests de integración REALES contra PostgreSQL (se saltan si no hay BD)
	MECANICO_TEST_DB_URL=$(MECANICO_DB_URL) pytest tests-integration/test_pg_edge_e2e.py -q

pg-bench:  ## dimensionamiento: 1h/8h/24h de snapshots en PostgreSQL (WAL, disco, RAM, CPU)
	MECANICO_DB_URL=$(MECANICO_DB_URL) python tools/pg_edge_benchmark.py

pg-vector-bench:  ## baseline del RAG local: top-K sobre chunks/casos/patrones
	MECANICO_DB_URL=$(MECANICO_DB_URL) python tools/pg_vector_benchmark.py
