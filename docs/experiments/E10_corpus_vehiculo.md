# E10 — Corpus documental por vehículo

Fecha: 1 de septiembre de 2026 · Estado: **infraestructura cerrada, corpus vacío**

Sustituye al plan original de E10, que preveía reutilizar el corpus genérico del
proyecto de ingeniería. La documentación pasa a estar condicionada por el
vehículo concreto.

## Qué se construyó

| Componente | Fichero |
|---|---|
| `VehicleProfile` y `VehicleApplicabilityValidator` | `rag/vehicle.py` |
| `DocumentManifest`, `DocumentEntry`, `SourceEntry`, jerarquía de evidencia | `rag/manifest.py` |
| `DocumentDownloader`, SHA-256, `DownloadRecord`, `DownloadFailure` | `rag/document_downloader.py` |
| Ingesta e informe | `rag/ingest.py` |
| Estructura y manifiesto del piloto | `corpus/vehicles/toyota-corolla-2020/` |
| Documentación | `docs/rag/` (6 ficheros) |

## Resultado de la ingesta

```
registrados 3 · descargados 0 · omitidos 2 · fallidos 1
```

**El corpus está vacío de contenido.** Ninguno de los tres documentos declarados
pudo incorporarse:

| Documento | Rango | Estado |
|---|---|---|
| Repair Manual | 1 | `MISSING_LICENSED_DOCUMENT` — requiere suscripción a Toyota TIS |
| Warranty & Maintenance Guide | 6 | **403 AccessDenied** desde Amazon S3 |
| Owner's Manual | 5 | Portal interactivo, sin PDF de URL directa |

### Sobre el 403

La URL que el encargo daba por públicamente descargable devuelve
`AccessDenied` de Amazon S3, y la raíz del bucket también. **No es un bloqueo de
agentes automatizados**: es una política de acceso del almacenamiento. Ninguna
manipulación de cabeceras lo cambiaría.

No se intentó falsear un navegador para sortearlo. Un 403 devuelto por el
operador es una decisión de acceso, y evadirla es lo que el encargo prohíbe
expresamente. El fallo se registra con su código y su URL, y **no se sustituye
por ninguna otra fuente**.

## Dos bloqueos que impiden avanzar al LLM

**1. No hay documentos.** Sin corpus no hay evidencia documental, y sin ella no
se pueden construir las condiciones FULL, PARTIAL, ABSENT ni DISTRACTOR.

**2. No hay datos OBD-II del vehículo piloto.** Todos los datos actuales son
sintéticos: los genera un modelo paramétrico que no corresponde a ningún vehículo
real. Su identidad no puede casar legítimamente con documentación de un Corolla,
y el validador lo rechaza correctamente.

Los dos son independientes. La condición FULL necesita **ambas cosas del mismo
vehículo**: documentación aplicable y datos OBD-II reales.

Este segundo bloqueo es el mismo de E3, ahora con una consecuencia más concreta:
elegir el vehículo real no es solo elegir una fuente de datos, es elegir de qué
vehículo habrá que conseguir el manual de taller.

## Decisiones de diseño

**`UNKNOWN` nunca es evidencia válida.** Es la decisión más importante del
validador. Significa que no se puede afirmar que el documento aplique; tratarlo
como válido convertiría la ignorancia en respaldo.

**Los campos desconocidos quedan en `null`.** Un `engine_code` inventado
convertiría el validador en un generador de coincidencias exactas falsas. El
Corolla 2020 tuvo más de una motorización: hasta conocer cuál, el perfil no puede
producir `EXACT_MATCH` frente a un documento específico de motor, y eso es
correcto.

**La descarga se rechaza al declararla, no al ejecutarla.** Un documento por
suscripción con `download: true` falla al cargar el manifiesto.

**Un fallo no detiene la ingesta.** Se registra y se sigue. Un corpus incompleto
es un hecho del experimento; ocultarlo tras una excepción impediría distinguir
«no había evidencia» de «no se pudo ejecutar».

**Los binarios no se versionan.** `raw/`, `processed/` y `chunks/` están
excluidos; `metadata/`, `vehicle.yaml` y `manifest.yaml` sí se versionan. El
proyecto registra que un documento existe, con su huella, sin redistribuirlo.

## Tests

`tests/test_vehicle_corpus.py` — 24 casos. Los que sostienen la fase:

- `test_vehicle_applicability` y sus variantes: otro modelo, otro año, otro
  fabricante y **otro motor del mismo modelo** producen el grado correcto;
- `test_lo_desconocido_nunca_es_evidencia_valida`;
- `test_private_document_not_downloaded`: el manual de taller no entra en la
  lista de descarga y `ensure_downloadable` lo rechaza;
- `test_un_documento_por_suscripcion_no_puede_declararse_descargable`;
- `test_el_manifiesto_rechaza_documentacion_de_otro_vehiculo`;
- `test_document_checksum` y `test_document_versioning`;
- `test_un_fallo_de_descarga_se_registra_y_no_detiene_la_ingesta`.

Las descargas de prueba no tocan la red: se sustituye el cliente HTTP para que
los tests sean deterministas.

## Pendiente

Extracción, troceado estructural, embeddings e indexación en pgvector. La
maquinaria se puede construir y probar con un documento de prueba, pero **el
corpus real espera a que haya un documento real**.

Tests todavía no escritos por depender de ello: `test_chunk_provenance`,
`test_page_provenance`, `test_vehicle_filter`, `test_pgvector_ingestion`.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 46 ficheros |
| `pytest` | 150 casos en verde |
