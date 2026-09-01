# Entorno oficial — macOS Apple Silicon

Entorno de referencia del TFM. Los resultados oficiales se producen aquí.

## Requisitos

- macOS sobre Apple Silicon (verificado en M4 Pro, macOS 26.6).
- [uv](https://docs.astral.sh/uv/). Si no está: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- PostgreSQL 14 o superior con `pgvector`. Ver [postgres-local.md](postgres-local.md).

No hace falta instalar Python a mano: uv resuelve e instala 3.11.

## Instalación

```bash
cd mecanico-ia-exp
uv sync --all-extras
```

Los extras separan lo pesado de lo esencial:

| Extra | Contiene | Cuándo |
|---|---|---|
| (ninguno) | configuración, pandas, SQLAlchemy, pgvector, Alembic | siempre |
| `ml` | PyTorch, scikit-learn, SHAP | fases E6-E9 |
| `nb` | JupyterLab, matplotlib, seaborn | análisis y figuras |
| `llm` | httpx, tenacity | fases E13 en adelante |

Para un entorno mínimo, `uv sync` sin extras basta para ejecutar la auditoría y
los tests de configuración.

## Configuración

```bash
cp .env.example .env
```

En una instalación de PostgreSQL por Homebrew, el usuario del sistema suele ser
superusuario y no necesita contraseña: basta con `DATABASE_USER` a tu usuario y
`DATABASE_PASSWORD` vacío. El fichero `.env` no se versiona.

## Verificación

```bash
uv run mecanico-exp doctor
```

Salida esperada en el entorno oficial:

```
[OK ] python: 3.11.14 (…/.venv/bin/python3)
[OK ] plataforma: Darwin 25.6.0 / arm64
[OK ] torch: torch 2.13.0 — dispositivo mps
[OK ] postgresql: PostgreSQL 14.15 (Homebrew)
[OK ] pgvector: instalada 0.8.0
```

`uv run mecanico-exp doctor --no-db` omite las comprobaciones de base de datos;
`--json` emite el informe en JSON para adjuntarlo al registro de un experimento.

## Apple Silicon y MPS

El laboratorio no asume CUDA en ningún punto y no incorpora dependencias que
exijan NVIDIA. El dispositivo se resuelve así:

```python
from mecanico_ia_exp.config.environment import resolve_device

resolve_device()  # "mps" o "cpu"
```

Cuando una operación de PyTorch o de SHAP no esté implementada en MPS, se
ejecuta en CPU **y se deja constancia**: el registro del experimento anota el
dispositivo realmente usado en cada etapa. Un fallback silencioso convertiría dos
resultados no comparables en aparentemente comparables.

## Gates de calidad

```bash
uv run ruff check .
uv run ruff format --check src tests
uv run mypy src
uv run pytest
```

Una fase no se considera cerrada con un gate en rojo.

## Análisis

```bash
uv run python -m ipykernel install --user --name mecanico-ia-exp \
  --display-name "Python 3 (mecanico-ia-exp)"
uv run jupyter lab
```

Los notebooks importan de `src/mecanico_ia_exp/`. No contienen lógica científica
que no exista también en el paquete.
