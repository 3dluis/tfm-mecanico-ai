# diagnostic-agent: núcleo edge (multi-arch: amd64 dev / arm64 Raspberry Pi).
# Contexto de build: raíz del monorepo (necesita shared/).
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY shared ./shared
COPY diagnostic-agent ./diagnostic-agent

# Scaffolding Fase 2: base + detection. El extra 'reasoning' (LangGraph/Chroma/
# sentence-transformers) se añade cuando se implemente el agente para no inflar
# la imagen antes de tiempo.
RUN pip install --upgrade pip \
    && pip install ./shared \
    && pip install "./diagnostic-agent[detection]"

RUN mkdir -p /app/data
EXPOSE 8000
CMD ["uvicorn", "diagnostic_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
