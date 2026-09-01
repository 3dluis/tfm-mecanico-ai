# Corpus documental por vehículo

## La regla

> El corpus RAG está condicionado por el vehículo objeto de análisis. La
> similitud semántica con documentación correspondiente a otro vehículo **no
> constituye evidencia suficiente**.

Un manual de un Corolla 2019 puede parecerse muchísimo al de un Corolla 2020.
Puede describir el mismo sistema con las mismas palabras. Y puede indicar un
valor distinto en el único punto que importa para el diagnóstico.

Por eso el vehículo no es un filtro que se aplica al final: es una condición de
admisibilidad que viaja con cada fragmento.

## Estructura

```
corpus/vehicles/<vehicle_id>/
├── vehicle.yaml     perfil técnico declarado
├── manifest.yaml    lista blanca de documentos y fuentes
├── raw/             documentos tal como se obtuvieron (no se versionan)
├── processed/       texto extraído
├── chunks/          fragmentos con su procedencia
└── metadata/        constancia de descarga: huella, fecha, URL final
```

`vehicle.yaml` y `manifest.yaml` **sí** se versionan; los documentos **no**. El
repositorio registra que un documento existe, de dónde sale y con qué huella, sin
redistribuirlo.

## Vehículo piloto

`toyota-corolla-2020` inicializa la arquitectura. **Es un piloto documental, no
el vehículo del experimento.**

Si el vehículo real del que se obtengan los datos OBD-II resulta ser otro, su
documentación no sustenta esos diagnósticos. El procedimiento es: registrar el
vehículo real, localizar su documentación, crear un `vehicle_id` nuevo, generar
un corpus separado, regenerar los embeddings y repetir las pruebas.

Nunca se mezcla documentación de vehículos distintos como si fuera equivalente.

## Campos desconocidos

Lo que no se sabe queda en `null` y no se infiere. Un `engine_code` inventado
convertiría el validador de aplicabilidad en un generador de coincidencias
exactas falsas: exactamente lo contrario de lo que debe hacer.

El Corolla 2020 se ofreció con más de una motorización. Hasta conocer el motor
concreto, el perfil no puede producir `EXACT_MATCH` frente a un documento
específico de motor, **y eso es correcto**.

## Estado del corpus piloto

| Documento | Tipo | Acceso | Estado |
|---|---|---|---|
| Repair Manual | REPAIR_MANUAL | suscripción (TIS) | `MISSING_LICENSED_DOCUMENT` |
| Warranty & Maintenance Guide | WARRANTY_MAINTENANCE_GUIDE | público | descarga rechazada por el servidor (403) |
| Owner's Manual | OWNERS_MANUAL | público, portal interactivo | sin URL directa estable |

El corpus está **vacío de contenido**. Se declara así en lugar de rellenarlo con
fuentes de menor autoridad. Ver [ingestion.md](ingestion.md).
