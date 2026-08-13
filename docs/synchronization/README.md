# Sincronización Edge ↔ Cloud

**Regla fundamental (ADR-0030): Edge y Cloud son bases de datos INDEPENDIENTES.** Ambas son
PostgreSQL + pgvector, y precisamente por eso conviene decirlo explícito: **nunca** se
sincronizan por replicación física (ni streaming, ni logical replication como mecanismo
principal). El protocolo es **lógico**:

```
Edge PostgreSQL → sync.outbox (misma transacción) → API/Sync → Cloud PostgreSQL
```

## Por qué lógico y no replicación

1. **Desacoplamiento de esquemas:** cada extremo puede evolucionar su físico mientras respete
   los contratos (`schema_version` viaja en cada sobre).
2. **Offline real:** el edge opera sin red y el outbox acumula; al reconectar, entrega.
3. **Auditoría:** cada sobre lleva id, checksum, prioridad, intentos y provenance — se puede
   explicar qué se envió, cuándo y por qué.
4. **Responsabilidades distintas:** el edge opera; la nube consolida. Replicar tal cual
   impondría el modelo operativo del edge a la nube.

## Atomicidad negocio + outbox

El sobre se escribe en la **misma transacción** que el cambio que lo origina
(`EdgeStore.add_with_outbox` / `EdgeStore.transaction`). No puede quedar un diagnóstico sin su
sobre ni un sobre sin su diagnóstico. La entrega posterior es **idempotente** por
`envelope_id` (upsert por id global en la nube).

## Niveles (qué se sincroniza)

| Nivel | Contenido | Política |
|---|---|---|
| **CRITICAL** | anomalías · casos · hipótesis · evidencia · provenance · memoria episódica · patrones | siempre, prioridad alta |
| **SUMMARY** | eventos · features de evento · agregados | por defecto |
| **OPTIONAL** | snapshots completos · telemetría cruda | solo bajo configuración explícita |

Los snapshots **no** se sincronizan todos por defecto: a 1 Hz son ~107 MB/día por vehículo y
casi nunca aportan a la nube más que su resumen.

## Detalle

Política completa (prioridades, reintentos, conflictos, cuarentena, retención por clase de
dato): [data-architecture/09](../data-architecture/09_retencion_sincronizacion.md).
Ownership de cada dato: [data-architecture/08](../data-architecture/08_edge_cloud_ownership.md).
Plataforma y transaccionalidad: [data-architecture/13](../data-architecture/13_postgresql_pgvector_edge.md).
