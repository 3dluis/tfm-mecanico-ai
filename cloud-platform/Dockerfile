# cloud-platform: API complementaria en nube (simple a propósito, ADR-0006).
# Contexto de build: raíz del monorepo (necesita shared/).
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY shared ./shared
COPY cloud-platform ./cloud-platform

RUN pip install --upgrade pip \
    && pip install ./shared \
    && pip install ./cloud-platform

EXPOSE 8080
CMD ["uvicorn", "cloud_platform.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
