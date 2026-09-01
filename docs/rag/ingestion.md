# Ingesta documental

```bash
uv run python -m mecanico_ia_exp.rag.ingest \
  --vehicle toyota-corolla-2020 \
  --manifest corpus/vehicles/toyota-corolla-2020/manifest.yaml
```

Encadena: validar manifiesto → descargar lo público autorizado → verificar huella
→ registrar procedencia → emitir informe.

## El descargador no es un rastreador

Solo obtiene URLs declaradas en el manifiesto con `download: true` **y**
`access_type: public`. No sigue enlaces, no descubre recursos, no descarga nada
que no esté previsto de antemano.

Lo que no hace, y no hará:

- saltar la autenticación de ningún portal;
- automatizar la descarga de documentación por suscripción;
- almacenar credenciales, cookies o sesiones;
- evadir restricciones de descarga.

Un documento por suscripción declarado con `download: true` **se rechaza al
cargar el manifiesto**, no al ejecutarlo: el error aparece al declarar la
intención.

## Documentos ausentes

Un documento declarado y no disponible aparece como `MISSING_LICENSED_DOCUMENT`,
con instrucciones para obtenerlo legítimamente de su fabricante.

**Nunca se sustituye por una fuente de menor autoridad.** Un manual de taller
ausente deja un hueco declarado, no un blog en su lugar.

## Un fallo no detiene la ingesta

Se registra y se continúa. Un corpus incompleto es un hecho del experimento;
ocultarlo tras una excepción impediría distinguir «no había evidencia» de «no se
pudo ejecutar».

## Informe

`results/rag_ingestion/<vehicle_id>_<marca temporal>.json`:

```
documents_registered · documents_downloaded · documents_skipped
documents_failed · chunks_created · embeddings_created
vehicle_id · corpus_version · manifest_hash
downloads[] · failures[] · missing_licensed[]
```

`manifest_hash` identifica qué lista documental produjo ese corpus.

## Estado del piloto — 1 de septiembre de 2026

```
registrados 3 · descargados 0 · omitidos 2 · fallidos 1
```

- **Repair Manual**: `MISSING_LICENSED_DOCUMENT`. Requiere suscripción a Toyota
  TIS. Es la evidencia de rango 1, la más autorizada, y no está.
- **Warranty & Maintenance Guide**: la URL declarada como pública devuelve **403
  AccessDenied desde Amazon S3**. La raíz del bucket también. No es un bloqueo de
  agentes automatizados sino una política de acceso del almacenamiento: ninguna
  manipulación de cabeceras lo cambiaría, y falsear un navegador para sortearlo
  sería precisamente lo que este proyecto no hace.
- **Owner's Manual**: portal interactivo, sin PDF de URL directa estable.

El corpus está vacío de contenido y así queda registrado.

## Licencias

Los binarios de `raw/`, `processed/` y `chunks/` están excluidos del control de
versiones. `metadata/`, `vehicle.yaml` y `manifest.yaml` se versionan: el
proyecto registra que un documento existe sin redistribuirlo.

Quien clone el repositorio puede descargar los documentos públicos permitidos;
los protegidos aparecen como ausentes con instrucciones para obtenerlos.
