# ai-models: entorno de investigación/entrenamiento (JupyterLab).
# Contexto de build: raíz del monorepo (necesita shared/). NUNCA se despliega en edge.
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /work

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY shared ./shared
COPY ai-models ./ai-models

RUN pip install --upgrade pip \
    && pip install ./shared \
    && pip install "./ai-models[export,research]"

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--NotebookApp.token=''", "--notebook-dir=/work/ai-models/notebooks"]
