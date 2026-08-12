# 07 — EventContext, EventBaseline y baseline por vehículo

[← Índice](README.md) · ADR: [0021](../adr/0021-deteccion-anomalias-contextual.md)

## EventContext (la clave de comparabilidad)

Dos eventos solo se comparan si su contexto es equivalente. `context_signature` v1 =
discretización estable de: event_type · rango de velocidad (bins de 20 km/h sobre
start_speed→end_speed) · estado térmico (cold/warming/warm) · rango de carga · duración
(bins log). Extensible con: contexto de vía (GPS), transmisión, configuración del vehículo.
La firma es una cadena canónica (p. ej. `ACCELERATION|40-80|warm|load2|d4-8s`) — indexable
en SQLite.

## EventBaseline

Comportamiento normal ACUMULADO de UN VEHÍCULO para UN contexto:

`baseline_id · vehicle_id · event_type · context_signature · sample_count ·
feature_distribution (media/desv/percentiles p5-p95 por feature) · centroid · first_seen ·
last_updated · version · confidence` (campos conceptuales; formato físico v1 = JSON por
feature; se re-evalúa si el volumen lo exige — requisito 20).

Actualización incremental (media/var online tipo Welford + reservas de percentiles);
`confidence` crece con sample_count y decae si el patrón de actualización se rompe. El
baseline ES memoria evolutiva de normalidad (complemento del LearnedPattern, que captura
anormalidad recurrente): vehicle-specific learning del requisito 19.

## Trips y sesiones

TRIP se modela como `VehicleEvent(event_type=TRIP)` contenedor (decisión: reutilizar la
entidad — evita tabla paralela y la jerarquía ya existe; evaluada la entidad propia y
descartada por duplicación). Relación TelemetrySession↔Trip: N:M libre — una sesión puede
contener varios trips (captura larga) y un trip puede cruzar sesiones (reconexión); el trip
referencia session_id de inicio y fin vía sus eventos hijo. Nunca se asume 1:1.
