# Mecánico IA — comandos canónicos del monorepo.
COMPOSE := docker compose

.PHONY: install schemas lint type test check \
        dev research cloud edge full down \
        arm64-build eval-emulator

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

lint:
	ruff check shared obd-lab ai-models diagnostic-agent cloud-platform tools
	ruff format --check shared obd-lab ai-models diagnostic-agent cloud-platform tools

type:
	mypy

test:
	pytest

check: lint type test schemas
	git diff --quiet shared/schemas || (echo "ERROR: esquemas desactualizados; commitea shared/schemas" && exit 1)

# ------------------------------------------------------------ perfiles docker
dev:  ## núcleo edge: emulador + agente + ollama
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

experiments: generate-suite  ## reproduce el experimento E1 de baselines
	python ai-models/experiments/e1_baselines.py --sessions data/sessions

llm-smoke:  ## smoke comparativo de SLMs (requiere Ollama con los modelos descargados)
	python tools/llm_smoke.py
