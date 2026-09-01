# Calibración de los datos sintéticos contra el manual de taller

Fecha: 1 de septiembre de 2026 · Vehículo: Mazda 3 BK 2007, motor **Z6 1,6 L MTX**

## Qué se hizo y qué no

**Se hizo:** anclar cada constante del generador OBD-II a un valor del manual de
taller del vehículo, con su cita literal y el fichero del que sale.

**No se hizo:** convertir los datos en reales. Siguen siendo sintéticos. La
calibración hace que sus parámetros dejen de ser arbitrarios y pasen a estar
documentados; no los convierte en una medición. La pregunta de investigación
habla de datos OBD-II **reales**, y eso exige registros de un vehículo real.

Esta limitación va en la memoria como tal, no como nota al pie.

## Por qué hacía falta

El generador anterior era coherente consigo mismo y **no correspondía a ningún
vehículo**. Sus constantes eran invenciones plausibles. Medido contra la
especificación de Mazda, los cuatro parámetros comprobables quedaban fuera:

| Parámetro | Generador | Especificación Mazda | Desviación |
|---|---|---|---|
| Ralentí | 776–851 rpm | 640–740 rpm | **+15 %** |
| Refrigerante máximo | 88,5 °C | 80–84 °C de apertura | por encima del rango |
| Caudal máximo | 91,8 g/s | 74 g/s (límite del 1,6 L) | **+24 %** |
| Avance en ralentí | 15,0 BTDC° | 9–11 BTDC° | **+40 %** |

## Elección del motor

**Z6, 1,6 L, transmisión manual.** No es cosmético.

Los procedimientos del manual son **específicos de motor**: sus identificadores
llevan `[ZJ, Z6]` o `[LF]`. La cobertura es LF 507 ficheros, ZJ/Z6 486, comunes
90. Los DTC que corresponden a las condiciones de este experimento están
documentados para `[ZJ, Z6]`, y el régimen de ralentí que el manual especifica es
también de Z6 y ZJ.

Anclar el generador a un motor y las citas a otro produciría evidencia
inaplicable al propio dato: exactamente lo que el validador de aplicabilidad
existe para impedir. Y lo impide de hecho: un documento declarado `[LF]` frente a
este perfil da `PARTIAL_MATCH`, y **no** cuenta como evidencia fuerte.

## Hallazgos, uno por constante

### 1 · Ralentí: 820 → 690 rpm

> «Idle speed ATX Z6: 700 - 800 rpm MTX ZJ: 690 - 790 rpm Z6: 640 - 740 rpm»
> — `srvc/B3E011002000W01.pdf`

El valor de 820 rpm no salía de ningún sitio. Se toma el punto medio del rango
documentado para Z6 con transmisión manual. Además se bajó el recorte inferior
de 650 a 620 rpm: el anterior habría truncado valores legítimos, porque el manual
documenta ralentí desde 640.

Resultado medido: **646–721 rpm**, dentro de 640–740.

### 2 · Termostato: 88 → 82 °C

> «Thermostat Type Wax, bottom-bypass. Opening temperature (°C) 80 - 84.
> Full-open temperature (°C) 95 / 97» — `srvc/B3E010002000T03.pdf`

Los 88 °C anteriores quedaban por encima del rango de apertura inicial. Se toma
el punto medio de 80–84.

Resultado medido: regulación en **82,5 °C**.

### 3 · Avance de encendido: base 12 → 7,7

> «Ignition timing (test mode on) (BTDC°) 9 - 11» — `srvc/B3E011002000W01.pdf`

La base se resolvió hacia atrás para que el avance en ralentí caiga dentro del
rango, dados el régimen y la carga de ralentí ya calibrados.

Resultado medido: **10,0 BTDC°**.

### 4 · Caudal de aire: el hallazgo que obligó a cambiar el modelo

Este es el más instructivo, porque la primera corrección **rompió algo**.

El modelo anterior era proporcionalidad pura: `maf = k · rpm · carga`. Reescalar
`k` para ajustar el máximo dejó el ralentí en 1,2 g/s, por debajo incluso del
suelo artificial de 1,5 g/s que el propio generador imponía. El ruido pasó a
dominar y la correlación entre el caudal y el producto régimen×carga se hundió de
0,881 a **0,569**: un test que llevaba desde E2 en verde empezó a fallar.

El fallo era correcto. Un caudalímetro real **no** es proporcional puro: hay un
caudal de base con el motor en ralentí. Y el manual lo dice:

> «MAF (Mass airflow) g/s · Ignition switch ON: approx. 0 g/s ·
> **Idle (after warm up): approx. 2.5 g/s**» — `srvc/B3E014018880W14.pdf`

El modelo pasa a `maf = desplazamiento + k · rpm · carga`, con los dos extremos
anclados:

- **inferior**, documentado: 2,5 g/s en ralentí;
- **superior**, deducido: 74 g/s, por cálculo volumétrico del Z6 de 1,6 L —
  `1,6 L × (5200/2 rev/min) × 0,9 de rendimiento volumétrico × 1,184 g/L / 60 s`.

El extremo superior **no** sale del manual y se declara como deducción. Los
59,5 g/s que aparecen en `srvc/B3E010200100W08.pdf` **no son un máximo**: son un
umbral para identificar operación a carga alta dentro de la detección del DTC del
sensor de mariposa. Superarlos a plena carga es correcto, y confundir un umbral
de diagnóstico con un límite físico habría vuelto a descalibrar el modelo.

Resultado medido: ralentí **2,47–2,59 g/s** en todos los regímenes; pico
**74,2 g/s**.

### 5 · Una incoherencia propia, detectada y corregida

Tras el segundo ajuste, el pico quedó en 91,4 g/s: un valor de motor **2.0 L**,
mientras el ralentí estaba anclado al **1,6 L**. Se estaban mezclando dos
motores en el mismo generador. La corrección fue fijar explícitamente el motor
Z6 y recalcular el límite superior para esa cilindrada.

Queda anotado porque es el tipo de error que no da la cara: cada valor por
separado era defendible, y solo su combinación resultaba imposible.

## Efecto sobre la correlación en ralentí

Con el modelo corregido, la correlación entre el caudal y el producto
régimen×carga es de 0,999–1,000 en todos los regímenes de conducción, y de
**0,638 en ralentí puro**.

No es un defecto. En ralentí el producto régimen×carga varía unas 5 veces entre
su mínimo y su máximo, frente a las 100–170 de la conducción; con tan poco
recorrido, el ruido del sensor domina. **Un caudalímetro real se comporta igual.**

Es el mismo fenómeno que E4 y E5 encontraron repetidamente: una relación real
puede quedar enmascarada cuando el rango dinámico es pequeño. El test se dividió
en dos, uno para conducción y otro para ralentí, y ambos comprueban lo que
físicamente cabe esperar.

## Respaldo documental de las condiciones de fallo

E2 dejó las cinco fichas de fallo con `source = [EVIDENCE_REQUIRED]`. Cuatro
quedan resueltas con DTC documentados del propio manual:

| Condición | DTC | Título en el manual | Fichero |
|---|---|---|---|
| F02 deriva de caudalímetro | P0101, P0102 | MAF sensor circuit range/performance; low input | `B3E010200102T02`, `B3E010200100W01` |
| F03 termostato bloqueado | P0125 | Insufficient coolant temperature for closed loop fuel control | `B3E010200100W11` |
| F04 sonda lenta | P0133 | Front HO2S circuit slow response | `B3E010200100W13` |
| F05 fallo de encendido | P0300, P0301–P0304 | Random misfire / Cylinder No.N misfire detected | `B3E010200102T02` |

La condición de detección de **P0133** merece atención: el manual dice que la
centralita vigila «the inversion cycle period, lean-to-rich response time and
rich-to-lean response time». Es **exactamente** la firma que E4 midió por su
cuenta: la separabilidad de F04 está en la dispersión y en la frecuencia de
conmutación de la sonda, no en su nivel medio. La medición independiente y la
documentación del fabricante coinciden.

### Uno sigue sin respaldo

**F01, fuga de vacío.** Se apoyaba en un DTC de mezcla pobre tipo P0171, que
**no aparece en ninguno de los 2 580 ficheros de servicio** del manual. Queda
`[EVIDENCE_REQUIRED]`.

No se le asigna un código por parecido. Las opciones son localizar el código que
Mazda usa para el BK en esa condición, o reformular la condición sobre un DTC que
sí esté documentado. Mientras tanto, F01 no puede sostener una explicación
apoyada en el manual, aunque el modelo la clasifique perfectamente.

Es un caso limpio para el experimento: una condición **detectable por el modelo y
sin respaldo documental** es precisamente donde la abstención debe activarse.

## Efecto sobre los resultados

La calibración cambió los niveles absolutos de las señales. **No cambió la
estructura discriminativa:**

| Métrica | Antes | Después |
|---|---|---|
| Baseline, F1 macro | 0,876 | **0,879** |
| Temporal, F1 macro | 0,822 | **0,823** |
| F03, exhaustividad | 0,643 | 0,643 |
| F05, exhaustividad | 0,500 | 0,500 |

Las conclusiones de E4 a E7 sobreviven. Es una comprobación de robustez que no se
buscaba y que conviene tener: los hallazgos no dependían de las constantes
inventadas.

## Trazabilidad

Cada constante lleva en `src/mecanico_ia_exp/obd/engine.py` el fichero del manual
del que sale. El detalle completo con las citas está en
`configs/calibracion_mazda3_bk.yaml`, que distingue explícitamente entre valores
**documentados** y valores **deducidos**.

Ocho tests comprueban que el generador sigue dentro de la especificación:
ralentí, caudal en ralentí, avance de encendido, regulación del termostato,
correlación en conducción y correlación en ralentí.
