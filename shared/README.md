# shared — mecanico_contracts

Única fuente de verdad de los contratos entre dominios (ADR-0007) y del **modelo de datos
v2** (ADR-0012/0013): telemetría trazable, diagnóstico estructurado, memoria en tres
niveles, provenance, agente y RAG. Documentación navegable:
[docs/data-architecture/](../docs/data-architecture/README.md).

Generación automática (no-divergencia): `make schemas` (JSON Schema, 31 entidades),
`make data-docs` (diccionario de datos + ejemplos). CI verifica que estén al día.

Módulos: `models.py` (mensajes núcleo) · `data_model.py` (modelo de datos v2) ·
`enums.py`/`data_enums.py` · `features.py` (definición canónica de features: contrato
entrenamiento↔inferencia) · `session_io.py` (formato común de sesión) ·
`export_schemas.py`/`gen_data_dictionary.py` (generadores).

Regla del monorepo: todo proyecto depende de `shared`; ningún proyecto importa a otro
(la capa `tests-integration/` en la raíz es el único punto que compone varios proyectos).
Versionado: `SCHEMA_VERSION` global (v2) + [CHANGELOG](CHANGELOG.md); política en
[docs/data-architecture/07](../docs/data-architecture/07_provenance_versionado.md).
