# Procedencia documental

## Qué hay que poder reconstruir

```
consulta
  ↓
resultado de recuperación
  ↓
fragmento
  ↓
documento
  ↓
vehículo
  ↓
página / sección
  ↓
editor
  ↓
URL de origen
```

Si algún eslabón se pierde, la cita no es verificable, y una cita que no se puede
verificar no cumple su función.

## Nunca una referencia genérica

Está prohibido citar «según el manual». Una referencia debe identificar cuál:

```
Toyota · Corolla · 2020 · Repair Manual
Sección: ... · Página: ... · Fragmento: ...
Fuente: Toyota TIS
```

## El SHA-256

Cada documento obtenido lleva su huella. Es lo que permite demostrar **qué
versión documental participó en cada experimento**. Sin ella, «se usó el manual
de mantenimiento» es una afirmación no verificable: los fabricantes revisan sus
publicaciones.

Constancia registrada por descarga:

```
document_id · vehicle_id · download_url · final_url · publisher
downloaded_at · content_type · file_size · sha256 · http_status
license_or_access_notes
```

Se guarda en `corpus/vehicles/<vehicle_id>/metadata/<document_id>.json`, que **sí**
se versiona aunque el documento no.

## Idempotencia y versiones

Si la huella no cambió, no se reingiere: una versión nueva sin contenido nuevo
solo añade ruido. Con `--force` se fuerza.

Si la huella cambió, se crea una `document_version` nueva. **No se sobrescribe la
anterior en silencio**: un experimento ejecutado contra la versión previa debe
seguir siendo reconstruible.
