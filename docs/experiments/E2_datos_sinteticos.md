# E2 — Datos sintéticos

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**

## Objetivo

Un generador reproducible de señales OBD-II plausibles, con relaciones entre
variables, regímenes de conducción y condiciones de fallo con verdad de
referencia explícita.

## Qué aporta y qué no

Aporta **control experimental**: se conoce exactamente qué ocurre en cada
instante, y se puede manipular. Sin eso no hay forma de comprobar si una
explicación se corresponde con la realidad.

No aporta validez externa. El modelo es paramétrico y **no está calibrado contra
datos reales**. No sustituye a E3, y ninguna conclusión sobre datos reales puede
apoyarse en estos datos. Se hace constar porque la pregunta de investigación
habla de datos reales.

> **Nota del 3 de septiembre de 2026 (ADR-003).** La pregunta de investigación ya no exige datos reales; exige declarar la procedencia, y la de este conjunto es `synthetic`. La ausencia de validez externa sigue siendo cierta y sigue siendo la limitación L-01.

## Componentes

| Módulo | Contenido | Procedencia |
|---|---|---|
| `obd/signals.py` | 12 señales con unidad y rango físico | REUSE — catálogo de PIDs del proyecto de ingeniería, reexpresado |
| `obd/regimes.py` | 6 regímenes de conducción | ADAPT — perfiles del proyecto hermano, más aceleración y deceleración sostenidas |
| `obd/engine.py` | Motor de simulación paso a paso | ADAPT |
| `obd/faults.py` | 5 fallos con ficha completa | ADAPT |
| `obd/synthetic.py` | Sesiones, dataset y plan equilibrado | NEW |
| `data/metadata.py` | Ficha de procedencia | NEW |

**Presión de combustible descartada.** Figuraba en la lista inicial de señales.
El modelo disponible no la produce y añadirla exigiría inventar una dinámica sin
respaldo. Se descarta por el criterio de usar únicamente señales justificables.

## Dataset generado

`data/raw/synthetic/synthetic_v1.parquet` — semilla 20260901.

| | |
|---|---|
| Muestras | 21 600 |
| Sesiones | 36 |
| Duración total | 6,0 h a 1 Hz |
| Condiciones | 6 (normal + 5 fallos), 6 sesiones cada una |
| Instantes con fallo activo | 2 880 por condición de fallo (el fallo entra al 20 % de la sesión) |

Reparto por régimen: urbano 12, autovía 12, ralentí 6, calentamiento 6. El
desequilibrio es un artefacto del reparto cíclico de 6 sesiones entre 4
regímenes. **Las clases sí están perfectamente equilibradas**, que es lo que
afecta a las métricas; el reparto por régimen se anota para tenerlo en cuenta al
interpretar E4.

## Hallazgo 1 — la relación régimen↔caudal es conjunta, no marginal

Un test inicial exigía correlación marginal alta entre régimen y caudal de aire.
Falló, y el generador tenía razón:

| Régimen | r(régimen, caudal) | r(régimen × carga, caudal) |
|---|---|---|
| ralentí | 0,067 | 0,881 |
| urbano | 0,476 | 1,000 |
| autovía | **−0,213** | 1,000 |
| aceleración | 0,152 | 1,000 |

El caudal depende del **producto** régimen × carga. La correlación marginal es
baja, y en autovía negativa: a velocidad de crucero constante ambas señales
apenas varían y domina el ruido. Un vehículo real se comporta igual.

Consecuencia para E9: **una correlación marginal baja no implica ausencia de
relación**. Una señal puede ser determinante sin destacar en un diagrama
bivariante. Al interpretar la atribución hay que tenerlo presente, o se
descartarán como irrelevantes señales que sí lo son.

El test se corrigió para comprobar la relación que el motor implementa
realmente, no la que se había supuesto.

## Hallazgo 2 — dos de los cinco fallos son invisibles en las medias

Medias sobre los instantes con fallo activo:

| Condición | stft | ltft | maf | refrigerante |
|---|---|---|---|---|
| normal | 0,06 | 0,01 | 21,74 | 81,4 |
| fuga de vacío | 4,36 | 2,94 | 21,25 | 82,2 |
| deriva de caudalímetro | 6,81 | 5,15 | 18,87 | 83,4 |
| termostato bloqueado | −0,02 | −0,00 | 21,76 | **69,2** |
| sonda lenta | −0,08 | 0,09 | 20,99 | 83,8 |
| fallo de encendido | 0,03 | −0,05 | 21,29 | 83,3 |

Tres fallos tienen firma clara en medias. Los otros dos no, porque su firma es
temporal:

**Sonda lenta.** La desviación típica de la sonda cae de 0,250 a **0,033**: la
oscilación se amortigua casi por completo. Invisible en la media, evidente en la
varianza.

**Fallo de encendido.** Aislando su efecto con la misma semilla con y sin fallo:
**5,7 %** de instantes alterados, caída media de **−218 rpm** (máxima −337) y
salto de carga de **+6,9 %**. La inyección funciona. Pero en el agregado queda
diluida: la desviación típica de la variación de régimen sube solo de 115,4 a
117,1 frente a la condición normal, porque los episodios son una fracción pequeña
de la sesión y el ruido de fondo del régimen los enmascara parcialmente.

Consecuencia para E5: los descriptores por ventana **no pueden limitarse a
medias**. Hacen falta varianza, conteo de eventos y extremos, o dos de las cinco
condiciones serán indetectables por construcción.

Consecuencia para E6-E8: **no se da por supuesto que el fallo de encendido sea
aprendible** con estos parámetros. Es una pregunta empírica. Si resulta que no lo
es, se reportará como tal y no se subirá su severidad para forzar un resultado
favorable.

## Verdad de referencia

Cada muestra lleva `fault_id` (condición de la sesión) y `fault_active` (si el
fallo actuaba en ese instante). El fallo entra al 20 % de la sesión, de modo que
cada sesión contiene la transición y no solo el estado final.

La **sesión** es la unidad de generación y será la unidad de reparto en E5.
Coinciden a propósito: repartir ventanas de una misma sesión entre entrenamiento
y test filtraría información entre particiones.

## Tests

`tests/test_synthetic_obd.py` — 31 casos:

- reproducibilidad por semilla, y no reproducibilidad entre semillas distintas;
- ninguna señal fuera de rango físico, con y sin fallo, en los cinco fallos;
- las relaciones declaradas se observan en los datos;
- calentamiento efectivo en arranque en frío;
- el fallo no actúa antes de su instante de inicio;
- cada fallo altera al menos una de las señales que su ficha declara;
- procedencia registrada y persistente.

El penúltimo es el que impide que una ficha mienta: si un fallo declarara señales
que no toca, toda explicación construida sobre esa ficha sería falsa.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `ruff format --check` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 25 ficheros |
| `pytest` | 47 casos en verde |

## Respaldo documental pendiente

Las cinco fichas de fallo llevan `source = [EVIDENCE_REQUIRED]`. Ninguna firma
tiene todavía respaldo documental verificado. Se resuelve en E10, al construir el
corpus. Un fallo cuya firma no llegue a tener respaldo **no podrá sostener una
explicación**, y eso será un resultado, no un defecto.

## Artefactos

- `data/raw/synthetic/synthetic_v1.parquet` y su `.meta.json`
- `uv run mecanico-exp generate-synthetic` — regeneración reproducible
- `src/mecanico_ia_exp/obd/`, `src/mecanico_ia_exp/data/metadata.py`

## Siguiente

E3 queda **bloqueada**: requiere decidir la fuente de datos OBD-II reales.
Se continúa por E4 (análisis exploratorio temporal) sobre los datos sintéticos.


> **Nota del 3 de septiembre de 2026 (ADR-003).** E3 deja de ser precondición de la PI y pasa a validación externa, pendiente de fuente.