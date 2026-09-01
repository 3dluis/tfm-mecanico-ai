# E3 — candidatos de datos OBD-II reales

**1 de septiembre de 2026.** E3 es el **bloqueo de mayor impacto del proyecto**: la pregunta de
investigación se formula sobre datos OBD-II **reales** y hoy solo hay sintéticos, que no
aportan validez externa (L-01).

**Esto es un informe de candidatos, no una decisión.** `[AUTHOR_DECISION_REQUIRED]`.

## El criterio que ningún candidato puede incumplir

Antes de comparar candidatos hay que fijar qué hace que un dataset sirva **a este trabajo en
concreto**, y no a un trabajo de detección de anomalías cualquiera.

El modelo de evidencia exige que una afirmación se rastree así:

```
claim → observation → signal → time window → value/pattern
```

**«Signal» tiene que ser una señal con nombre.** «El ajuste de combustible a largo plazo se
mantiene en +2,9 %» es una afirmación verificable. «La tercera componente principal vale 1,7»
no lo es: no puede sostener una explicación diagnóstica ni ser comprobada por un lector.

> **Criterio eliminatorio: el dataset debe publicar las señales originales con su nombre y su
> unidad.** Un dataset transformado —PCA, embeddings, señales anonimizadas— **rompe la rama
> observacional del modelo de evidencia**, y con ella PI.2 y la mitad de M4.

Criterios secundarios: etiquetas de fallo con verdad de referencia · frecuencia de muestreo
conocida · procedencia y licencia declaradas · señales que solapen con el catálogo del
proyecto.

---

## Candidato 1 — EngineAD

**Referencia:** ya está en la bibliografía del proyecto como **REF-048**.
**DOI:** [10.5683/SP3/TX13P1](https://doi.org/10.5683/SP3/TX13P1) (Borealis) ·
preprint arXiv:2603.25955 · **licencia CC BY-NC 4.0** *(el preprint indica CC BY 4.0:
`[VERIFY_SOURCE]` la discrepancia)*.

| Aspecto | Valoración |
|---|---|
| Realidad de los datos | **Excelente.** Flota de **25 vehículos comerciales**, **seis meses** de telemetría continua de alta resolución |
| Etiquetado | **Excelente.** Anotaciones de expertos que distinguen estado normal de **indicadores tempranos de fallo de motor** |
| Procedencia y licencia | Declaradas, con DOI y repositorio institucional |
| **Señales con nombre** | ⚠ **BLOQUEANTE POR VERIFICAR.** El resumen declara que los datos se distribuyen preprocesados en «segmentos de 300 instantes de **8 componentes principales**». **No consta el número ni el nombre de las señales originales** |

### La pregunta que decide

**¿Publica EngineAD las señales originales, o solo las componentes principales?**

Si solo publica componentes principales, **el dataset es inservible para este TFM** por muy
bueno que sea: no se puede construir evidencia observacional trazable sobre una componente
principal. Serviría para detectar anomalías; no para explicarlas con evidencia verificable, que
es lo que el trabajo investiga.

**Verificación pendiente**, en este orden: (1) descargar el registro de Borealis y mirar qué
ficheros contiene; (2) leer el artículo completo, sección de datos; (3) si solo hay
componentes, escribir a los autores.

`[VERIFY_SOURCE]` · **Coste de comprobarlo: una tarde. Coste de no comprobarlo: descubrirlo en
E9.**

### Segundo caveat

Son **vehículos comerciales** con fallos incipientes de motor anotados por expertos. Los cinco
mecanismos que el proyecto simula —fuga de vacío, deriva de caudalímetro, termostato bloqueado,
sonda lenta, fallo de encendido— **pueden no estar representados como tales**. Si el
etiquetado es binario normal/anómalo, PI.1 cambia de naturaleza: pasa de clasificación
multiclase de mecanismos a detección binaria, y con ella cambian M1 y buena parte del diseño.

---

## Candidato 2 — Conjuntos citados en la propuesta aprobada

La propuesta entregada a la universidad el 14/07/2026 lista dos conjuntos:

| # | Entrada de la propuesta | Estado |
|---|---|---|
| 10 | *OBD-II & CAN-Based Driving Behavior Dataset* | `[VERIFY_SOURCE]` — sin identificador ni URL verificada |
| 11 | *OBD-II datasets* | `[VERIFY_SOURCE]` — entrada genérica, sin identificar |

**Ventaja institucional:** figuran en un documento oficial ya entregado. Usarlos no exige
justificar un cambio de fuente.

**Caveat de fondo:** un conjunto de **comportamiento de conducción** etiqueta maniobras y estilo
de conducción, **no fallos mecánicos**. Si es así, no sirve para PI.1 tal como está formulada,
por mucho que sea OBD-II real.

`[AUTHOR_DECISION_REQUIRED]` — identificar exactamente a qué conjuntos se refieren esas dos
entradas. Son del propio autor y no constan en el corpus de 144 referencias.

---

## Candidato 3 — Conjuntos abiertos de flota

Localizados en la búsqueda del 1 de septiembre, **sin verificar**:

| Fuente | Contenido declarado | Limitación previsible |
|---|---|---|
| Conjunto abierto de dispositivo OBD propietario | ≈30 vehículos, ≈4 meses | **Sin etiquetas de fallo** |
| Conjunto académico de diez señales OBD-II | refrigerante, MAP, RPM, velocidad, temperatura de admisión | **Sin etiquetas de fallo** |

`[VERIFY_SOURCE]` en ambos.

**Sin etiquetas de fallo, un conjunto no responde PI.1**, pero **sí puede servir para otra cosa
valiosa**: calibrar el generador sintético contra distribuciones reales. Eso convertiría L-01
de «sin validez externa» a «validez externa parcial, con el generador calibrado contra datos
reales» — que es una limitación mucho más defendible.

---

## Candidato 4 — Datos propios

Adquisición con adaptador OBD-II sobre vehículo propio, tal como preveía la propuesta original.

**A favor:** control total, señales con nombre garantizadas, procedencia trivial.
**En contra:** sin fallos reales que inyectar; provocar fallos en un vehículo real está fuera de
alcance y de presupuesto. Sirve para la condición normal y para la demostración final, no para
el banco de evaluación.

---

## Recomendación de procedimiento

**No elegir todavía.** Ejecutar en este orden, que ordena las comprobaciones por lo que cuesta
descubrirlas tarde:

1. **Verificar si EngineAD publica señales con nombre.** Es la comprobación más barata y la que
   más decide. Si las publica, es el mejor candidato con diferencia.
2. **Identificar los dos conjuntos de la propuesta aprobada** y comprobar si etiquetan fallos
   mecánicos o comportamiento de conducción.
3. **Si ninguno tiene etiquetas de mecanismo de fallo**, plantear la vía mixta: datos reales
   para calibrar el generador y para la demostración, sintéticos para el banco de evaluación,
   **con la limitación declarada en el enunciado de la pregunta y no escondida en el capítulo
   6**.
4. **Registrar la decisión como ADR-003**, con las opciones descartadas y su motivo.

## Consecuencia sobre la pregunta de investigación

Si al final no hay datos reales con fallos etiquetados, **la PI debe reformularse antes de
seguir**, no después. Decir «datos OBD-II reales» y evaluar sobre sintéticos sería la clase de
afirmación sin respaldo que este trabajo se dedica a detectar en otros sistemas.

Formulación alternativa, si se llega a ese punto:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo **a partir de telemetría
> OBD-II**, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la
> evidencia disponible no es suficiente […]?

Y declarar en el capítulo 4, sin rodeos, sobre qué datos se ejecutó y qué validez externa
tiene el resultado.
