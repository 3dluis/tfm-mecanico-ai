# PostgreSQL local

## Situación en la máquina del autor

La auditoría del 1 de septiembre de 2026 encontró una instalación previa:

| | |
|---|---|
| Versión | PostgreSQL 14.15 (Homebrew), `aarch64-apple-darwin24` |
| Servicio | `postgresql@14`, activo, puerto 5432 |
| Datos | `/opt/homebrew/var/postgresql@14` |
| Usuario | `ldiaz`, superusuario |
| pgvector | 0.8.0, `vector.so` presente en `/opt/homebrew/lib/postgresql@14/` |

Esa instalación da servicio a otras bases del autor. El laboratorio **no la
sustituye ni la reconfigura**: crea únicamente su propia base de datos.

## Qué crea el laboratorio, y qué no

Crea: la base `mecanico_ai_exp`, las extensiones `vector` y `pg_trgm` dentro de
ella, y los objetos de su esquema mediante migraciones.

No hace: instalar otro servidor, tocar otras bases, eliminar esquemas, alterar
roles ni asumir permisos de superusuario más allá de crear una base de datos.

## Inicialización

```bash
bash scripts/init_db.sh
```

El script lee `.env`, comprueba si la base existe —si existe, no la recrea—,
aplica `alembic upgrade head` y lista las extensiones resultantes.

Resultado esperado:

```
 extname | extversion
---------+------------
 pg_trgm | 1.6
 plpgsql | 1.0
 vector  | 0.8.0
```

## Si pgvector no estuviera disponible

La fórmula de Homebrew compila `pgvector` contra las versiones recientes de
PostgreSQL. Para una instalación en 14:

```bash
brew install pgvector          # comprobar primero si ya está
psql -d postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector'"
```

Si la extensión no aparece, se compila contra el `pg_config` de la versión en
uso:

```bash
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config
make install PG_CONFIG=/opt/homebrew/opt/postgresql@14/bin/pg_config
```

Comprobación sin efectos persistentes:

```bash
psql -d postgres -c "LOAD 'vector'"
```

Alternativa sin compilar nada: el modo portable con contenedor, en
[docker-portable.md](docker-portable.md).

## Reiniciar el laboratorio desde cero

```bash
dropdb mecanico_ai_exp && bash scripts/init_db.sh
```

`dropdb` afecta solo a la base del laboratorio. Antes de ejecutarlo conviene
confirmar el nombre: es una operación irreversible.
