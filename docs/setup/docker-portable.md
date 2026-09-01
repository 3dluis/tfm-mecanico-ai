# Modo portable — PostgreSQL en contenedor

Docker **no es el entorno principal** del TFM. Este modo existe para que un
tercero pueda reproducir el experimento sin instalar PostgreSQL ni compilar
`pgvector`.

El pipeline científico es idéntico en ambos modos. Lo único que cambia es dónde
vive la base de datos y de dónde sale el modelo de lenguaje.

## Levantar la base

```bash
docker compose up -d postgres
```

Usa la imagen `pgvector/pgvector:pg16`, que trae la extensión incorporada. El
puerto publicado en el anfitrión es **5433**, no 5432, para no colisionar con una
instalación local.

## Configuración

```dotenv
DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_NAME=mecanico_ia_exp
DATABASE_USER=mecanico
DATABASE_PASSWORD=mecanico
```

Las credenciales del contenedor son de desarrollo y están a la vista en
`compose.yaml`: el contenedor no se expone fuera de la máquina.

## Puesta en marcha

```bash
uv sync --all-extras
uv run alembic upgrade head
uv run mecanico-exp doctor
```

La base ya existe (la crea el propio contenedor), así que basta con aplicar las
migraciones; no hace falta `scripts/init_db.sh`.

## Ciclo de vida

```bash
docker compose ps                 # estado
docker compose logs -f postgres   # registro
docker compose stop postgres      # parar, conservando datos
docker compose down               # parar y eliminar el contenedor
docker compose down -v            # además, borrar el volumen de datos
```

`down -v` destruye el corpus indexado. Es irreversible.

## Ollama opcional

```bash
docker compose --profile ollama up -d
```

El perfil mantiene el servicio fuera del arranque por defecto: sin `--profile
ollama`, `docker compose up -d` no lo levanta. Ver
[ollama-optional.md](ollama-optional.md).

## Diferencias que hay que declarar

La versión de PostgreSQL difiere entre modos: 14 en la instalación local del
autor, 16 en la imagen del contenedor. No afecta a la semántica de `pgvector`
para lo que el laboratorio hace, pero el registro del experimento anota la
versión real del servidor empleado, y cualquier comparación entre ejecuciones lo
tiene en cuenta.
