# E1 — Entorno
Fecha: 1 de septiembre de 2026 · Estado: **cerrada**

## Objetivo
Dejar la máquina y el repositorio en un estado verificable, y producir el plan
experimental antes de escribir código científico.

## Qué se hizo
- Auditoría del entorno existente, en modo lectura.

- Creación del repositorio `mecanico-ia-exp`, separado e independiente.

- Configuración de uv con Python 3.11 y extras por área.

- Configuración tipada por variables de entorno, con `.env.example`.

- Auditoría automatizada del entorno, expuesta como CLI y como notebook.

- Creación de la base de datos del laboratorio y de sus extensiones.

- Alembic operativo, con la primera migración aplicada.

- Los diecisiete notebooks, con su estructura documental obligatoria.

- Documentación de instalación, metodología, plan y matriz de validación.

## Entorno verificado
| Componente | Resultado |
| --- | --- |
| Hardware | Apple M4 Pro, 24 GB |
| Sistema | macOS 26.6.2 · Darwin 25.6.0 · arm64 |
| Python | 3.11.14, gestionado por uv 0.10.2 |
| PyTorch | 2.13.0 · MPS compilado y disponible |
| MPS | comprobado con una multiplicación de matrices 512×512 en dispositivo `mps` |
| PostgreSQL | 14.15 (Homebrew), servicio activo en 5432 |
| pgvector | 0.8.0, instalada en `mecanico_ia_exp` |
| Docker | 29.3.1 · Compose v5.1.1 (solo portabilidad) |
| Ollama | instalado (opcional, no oficial) |

La verificación de MPS es una operación real ejecutada en el dispositivo, no una
consulta de disponibilidad: `torch.backends.mps.is_available()` puede devolver
cierto en configuraciones donde una operación posterior falla.

## Base de datos
La instalación de PostgreSQL ya existía y sirve a otras bases del autor
(`mgrid`, `portal_bcrd`, `visitordb`, `vmgrid`, `vmgridbk`,
`norla_migrate_test`). Ninguna ha sido consultada en su contenido, alterada ni
eliminada.

Se creó exclusivamente la base `mecanico_ia_exp` y se habilitaron en ella
`vector` 0.8.0 y `pg_trgm` 1.6, mediante `scripts/init_db.sh` y la migración
`0001_extensiones_base`.

Nota sobre `pgvector`: la fórmula de Homebrew instalada declara soporte para
PostgreSQL 17 y 18, pero existe un `vector.so` compilado para 14 en
`/opt/homebrew/lib/postgresql@14/`, y el servidor lo carga correctamente. Queda
anotado porque una reinstalación de la fórmula podría no regenerarlo;
`docs/setup/postgres-local.md` recoge cómo recompilarlo.

## Comprobaciones
```
$ uv run mecanico-exp doctor
[OK ] python: 3.11.14
[OK ] plataforma: Darwin 25.6.0 / arm64
[OK ] torch: torch 2.13.0 — dispositivo mps
[OK ] postgresql: PostgreSQL 14.15 (Homebrew)
[OK ] pgvector: instalada 0.8.0

```
| Gate | Resultado |
| --- | --- |
| `ruff check .` | sin incidencias |
| `ruff format --check src tests` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 19 ficheros |
| `pytest` | 16 casos, todos en verde |
| `notebooks/00_environment_check.ipynb` | ejecutado de principio a fin |

## Artefactos
- Repositorio `mecanico-ia-exp`, con historial propio.

- `docs/plan_experimental_macbook.md` — plan por fases y clasificación de
componentes.

- `docs/matriz_validacion_pi.md` — subpreguntas, criterios y desenlaces de
refutación.

- `docs/setup/`, `docs/methodology/`.

- `notebooks/00_environment_check.ipynb`, ejecutado.

- Base `mecanico_ia_exp` con `vector` y `pg_trgm`.

## Nota sobre el nombre
El laboratorio se creó inicialmente como `mecanico-ai-exp` y se renombró a
`mecanico-ia-exp` el mismo día, para alinearlo con el proyecto de ingeniería
`mecanico-ia`. El cambio se aplicó de forma completa —directorio, paquete
Python, nombre del proyecto, base de datos, servicios de `compose.yaml` y kernel
de Jupyter— porque una corrección parcial habría reproducido la incoherencia un
nivel más abajo.

La base de datos se renombró con `ALTER DATABASE`, conservando sus extensiones y
el sello de Alembic; no se recreó. El proyecto de ingeniería no se tocó: conserva
su nombre, su historial y su configuración.

## Qué queda abierto
Las cinco decisiones de la sección 7 del plan: fuente de datos OBD-II reales,
arquitectura del modelo temporal, proveedor LLM oficial, modelo de embeddings y
su dimensión, y conjunto definitivo de fallos.

Ninguna bloquea E2.

## Siguiente fase
E2 — datos sintéticos. Pendiente de aprobación.