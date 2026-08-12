# cloud-platform

Plataforma complementaria en nube — deliberadamente simple (ADR-0006): FastAPI + PostgreSQL.
Sin Kubernetes, sin colas, sin microservicios.

Responsabilidades: autenticación simple, usuarios/vehículos/dispositivos, telemetría histórica,
diagnósticos sincronizados (outbox del edge), conocimiento documental, model registry y
distribución de modelos (ADR-0009).

La nube es COMPLEMENTARIA: el edge funciona 100% sin conectividad.
