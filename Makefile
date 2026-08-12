.PHONY: install lint type test check dev arm64-build eval-emulator

install:
	pip install --upgrade pip "setuptools<81" wheel
	pip install -e ".[sim,anomaly,dev]" --no-build-isolation
	pre-commit install

lint:
	ruff check src tests && ruff format --check src tests

type:
	mypy

test:
	pytest --cov

check: lint type test

dev:
	docker compose -f docker/compose.yml --profile dev up --build

arm64-build:
	docker buildx build --platform linux/arm64 -f docker/edge.Dockerfile -t mecanico-ia:arm64 .

eval-emulator:
	python tools/eval_emulator.py
