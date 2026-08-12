# obd-lab: laboratorio de simulación OBD-II (emulador ELM327 por TCP).
# Contexto de build: raíz del monorepo (necesita shared/).
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY shared ./shared
COPY obd-lab ./obd-lab

# ELM327-emulator usa pkg_resources: setuptools<81 + --no-build-isolation (ADR-0003)
RUN pip install --upgrade pip "setuptools<81" wheel \
    && pip install ./shared \
    && pip install --no-build-isolation "ELM327-emulator>=3.0.5" \
    && pip install ./obd-lab

EXPOSE 35000
# Servidor ELM327 por TCP con el escenario 'car' (el escenario propio 'mecanico'
# lo inyectará obd_lab en fases siguientes).
CMD ["python", "-m", "elm", "-n", "35000", "-s", "car"]
