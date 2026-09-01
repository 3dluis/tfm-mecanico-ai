#!/usr/bin/env bash
# Crea la base de datos del laboratorio y aplica las migraciones.
#
# Es deliberadamente conservador: si la base ya existe no la toca, y no altera
# ninguna otra base del servidor. No requiere superusuario más allá del permiso
# para crear una base de datos.
set -euo pipefail

cd "$(dirname "$0")/.."

[ -f .env ] && set -a && . ./.env && set +a

HOST="${DATABASE_HOST:-localhost}"
PORT="${DATABASE_PORT:-5432}"
NAME="${DATABASE_NAME:-mecanico_ai_exp}"
USER_ARG=""
[ -n "${DATABASE_USER:-}" ] && USER_ARG="-U ${DATABASE_USER}"

echo "Servidor: ${HOST}:${PORT}   Base objetivo: ${NAME}"

# shellcheck disable=SC2086
EXISTE=$(psql -h "$HOST" -p "$PORT" $USER_ARG -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname = '${NAME}'")

if [ "$EXISTE" = "1" ]; then
  echo "La base '${NAME}' ya existe; no se recrea."
else
  # shellcheck disable=SC2086
  psql -h "$HOST" -p "$PORT" $USER_ARG -d postgres -c "CREATE DATABASE \"${NAME}\""
  echo "Base '${NAME}' creada."
fi

echo "Aplicando migraciones..."
uv run alembic upgrade head

# shellcheck disable=SC2086
psql -h "$HOST" -p "$PORT" $USER_ARG -d "$NAME" -c \
  "SELECT extname, extversion FROM pg_extension ORDER BY extname"

echo "Base de datos lista."
