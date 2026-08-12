# shared — mecanico_contracts

Única fuente de verdad de los contratos entre dominios (ADR-0007). Pydantic v2; exportación a
JSON Schema en `schemas/` (`make schemas`) para consumidores no-Python (Flutter).

Regla del monorepo: todo proyecto depende de `shared`; ningún proyecto importa a otro.
Versionado: `schema_version` en cada mensaje; solo cambios aditivos dentro de una versión.
