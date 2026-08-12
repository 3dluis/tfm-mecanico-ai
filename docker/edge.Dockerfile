# Imagen del nodo edge de Mecánico IA.
# Multiplataforma: linux/amd64 (desarrollo) y linux/arm64 (validación RPi — ADR-0002).
FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema mínimas (compilación de ruedas ausentes en arm64).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

# ELM327-emulator usa pkg_resources en setup.py: requiere setuptools<81 (ver ADR-0003).
RUN pip install --upgrade pip "setuptools<81" wheel \
    && pip install -e ".[sim,anomaly]" --no-build-isolation

COPY tools ./tools
COPY tests ./tests

CMD ["python", "-c", "import mecanico_ia; print('mecanico-ia edge listo:', mecanico_ia.__version__)"]
