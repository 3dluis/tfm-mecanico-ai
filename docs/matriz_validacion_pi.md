# Matriz de validación de la pregunta de investigación

Última actualización: 1 de septiembre de 2026 · Datos: `synthetic_v2` ·
Corpus: manual de taller Mazda 3 BK, 6 158 fragmentos

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de
> datos OBD-II **reales**, rastreando cada explicación hasta su evidencia de
> origen, y reconocer cuándo la evidencia disponible no es suficiente para
> sostener una explicación en lugar de generar una hipótesis sin fundamento?

---

## Advertencia que condiciona toda la matriz

**Los datos no son reales.** Son sintéticos, generados por un modelo paramétrico
calibrado contra el manual del Mazda 3 BK. La calibración documenta sus
parámetros; **no los convierte en una medición**.

La pregunta, tal como está formulada, **no puede responderse todavía**. Lo que
esta matriz responde es su versión condicional:

> *Con datos OBD-II sintéticos calibrados contra la documentación del vehículo,
> ¿puede el agente explicar rastreando la evidencia y abstenerse cuando no la
> hay?*

Cada fila indica qué parte del resultado depende de esa condición. Las que
dependen menos son las que menos cambiarían con datos reales; las que dependen
más son las que habría que rehacer.

---

## Estado por subpregunta

| PI | Métrica | Criterio | **Resultado medido** | Decisión |
|---|---|---|---|---|
| **PI.1** Diagnóstico | F1 macro sobre validación | Supera claramente a la clase mayoritaria y la confianza está calibrada | **0,879** frente a 0,074 · ECE 0,144 → **0,085** tras calibrar | **Sostenida sobre datos sintéticos** |
| **PI.2** Trazabilidad | `claim support rate`, `citation completeness` | Toda afirmación admitida se ancla en observación y documento verificados | 18 afirmaciones · 18 con observación · **12 sostenidas (0,667)** · 51 comprobaciones de soporte, **21 aceptadas (41 %)** | **Parcialmente sostenida** |
| **PI.3** Reconocimiento de insuficiencia | Decisión EXPLAIN/ABSTAIN | La decisión cambia al retirar la evidencia | **EXPLAIN → ABSTAIN** con datos, modelo, atribución y confianza idénticos · 4 de 6 decisiones correctas | **Sostenida** |
| **PI.4** Rechazo de evidencia engañosa | Distractores aceptados | El procedimiento de otro motor no se acepta como evidencia | Semántica pura: **1 distractor, y por encima del correcto**. Con filtro de aplicabilidad: **0** | **Sostenida** |

---

## PI.1 · Diagnóstico

| | |
|---|---|
| Modelo | Bosque aleatorio sobre 139 descriptores |
| F1 macro (validación) | **0,879** |
| Referencia mínima | 0,074 |
| Calibración | ECE 0,144 → **0,085**; sesgo −0,140 → +0,009 |

**Depende mucho de la condición sintética.** El generador produce condiciones
limpias y equilibradas. Un vehículo real tendría solapamiento entre condiciones,
fallos concurrentes y ruido de adquisición.

**Límite encontrado que sí trasladaría:** el termostato bloqueado es
**físicamente indetectable** mientras el motor no habría superado su techo de
71 °C. Las ventanas que el modelo falla tienen 54,3 °C de media; las que acierta,
70,7. Ningún clasificador distingue dos señales idénticas, y eso ocurre igual en
un coche real.

---

## PI.2 · Trazabilidad · **la más débil**

| | |
|---|---|
| Afirmaciones generadas | 18 |
| Con evidencia observacional | 18 (1,000) |
| Con cita documental **verificada** | 12 (**0,667**) |
| Comprobaciones de soporte ejecutadas | 51 |
| Comprobaciones **aceptadas** | 21 (**41 %**) |

La cadena de procedencia se reconstruye por completo. Desde cualquier resultado:

```
consulta → retrieval_run → fragmento → documento → vehículo
→ sección y página → editor → URL de origen
```

**Por qué solo parcialmente sostenida:** un tercio de las afirmaciones no
consigue cita que las sostenga, y el verificador **rechaza el 59 % de las citas
candidatas**. Eso no es un fallo: es la pieza funcionando. Pero significa que el
sistema, tal como está, no puede sostener documentalmente todo lo que observa.

El caso que lo explica: el modelo detecta la deriva del caudalímetro **por los
ajustes de combustible**, y el procedimiento del manual para ese DTC habla de **la
tensión del circuito del sensor**. Observación y documentación describen el mismo
fallo por vías distintas, y la verificación de soporte lo rechaza correctamente.

**Depende poco de la condición sintética.** La desalineación entre lo que el
modelo mira y lo que el manual documenta es una propiedad del manual y del
problema, no de los datos.

---

## PI.3 · Reconocimiento de insuficiencia · **el resultado central**

| Caso | Confianza | Docs aplicables | Cobertura | Decisión |
|---|---|---|---|---|
| Evidencia presente | 0,908 | 4 | 1,00 | **EXPLAIN** |
| Evidencia retirada | **0,908** | **0** | **0,00** | **ABSTAIN** |

Mismos datos OBD-II. Mismo modelo. Misma atribución. **Misma confianza.** Lo
único que cambia es que se retiran del índice los 70 fragmentos que portan los
códigos que documentan esa condición.

La decisión cambia **porque cambió la evidencia**, no porque cambiara la certeza
del modelo. Es la pregunta de investigación reducida a su mínima expresión.

Decisiones correctas: **4 de 6**. Las dos discrepancias se dejan registradas sin
ajustar umbrales:

- **Fallo de encendido:** confianza calibrada 0,462. El conjunto anotado dice
  EXPLAIN porque *existe documento*; el criterio dice ABSTAIN porque *el modelo
  no es fiable ahí*. Probablemente la etiqueta esperada está mal puesta.
- **Deriva del caudalímetro:** cobertura 0,00 por la desalineación descrita en
  PI.2.

**Depende poco de la condición sintética.** El mecanismo --retirar evidencia y
observar el cambio de decisión-- opera sobre el corpus, que es documentación real
del fabricante.

**La decisión la toma un componente determinista, sin modelo de lenguaje.** Si la
tomara el LLM, la respuesta dependería de su disposición a admitir que no sabe
algo.

---

## PI.4 · Rechazo de evidencia engañosa

El distractor no hubo que fabricarlo: cada DTC tiene en el corpus **dos**
procedimientos, `[ZJ, Z6]` y `[LF]`. Mismo código, contenido casi idéntico, motor
inaplicable al vehículo.

| Estrategia | Distractores recuperados | **Por encima del correcto** |
|---|---|---|
| Semántica pura | **1** | **1** |
| Con filtro de aplicabilidad | 0 | 0 |

**La similitud semántica sí acepta el procedimiento del motor equivocado, y lo
coloca por delante del aplicable.** El filtro de aplicabilidad lo elimina.

Y el validador discrimina en el caso general: un documento `[ZJ, Z6]` frente a
este perfil da `EXACT_MATCH`; uno `[LF]` da `PARTIAL_MATCH` y **no cuenta como
evidencia fuerte**.

**No depende de la condición sintética.** Es puramente documental.

---

## Hallazgo transversal que no estaba previsto

La recuperación semántica **nunca** encuentra el procedimiento correcto en los
diez primeros: Hit@10 = 0,00. Guiarla con el diagnóstico del modelo la lleva a
**1,00**.

| Estrategia | Hit@10 | MRR | nDCG |
|---|---|---|---|
| semántica | 0,00 | 0,000 | 0,000 |
| + filtro de motor | 0,20 | 0,040 | 0,149 |
| + jerarquía de autoridad | 0,40 | 0,107 | 0,468 |
| híbrida | 0,40 | 0,107 | 0,468 |
| **guiada por el diagnóstico** | **1,00** | 0,467 | 0,642 |

Esto **valida una decisión de arquitectura** que se había tomado por otras
razones: que el LLM no diagnostique sobre OBD-II crudo. Si lo hiciera, no habría
diagnóstico previo que guiara la recuperación, y el sistema se quedaría con la
estrategia que puntúa cero.

---

## Veredicto

**Parcialmente sostenida, y condicionada a datos sintéticos.**

- PI.1 y PI.3 se cumplen sobre los datos disponibles.
- PI.4 se cumple y no depende de que los datos sean sintéticos.
- **PI.2 se cumple solo en parte**: dos tercios de las afirmaciones consiguen
  cita verificada.

Según los criterios fijados de antemano, «parcialmente sostenida» corresponde a
cumplir PI.1 y fallar PI.3 o PI.4. Aquí ocurre lo contrario: **falla parcialmente
PI.2**, que era una de las dos que sostienen el trabajo.

**No se reinterpreta como éxito.** El resultado es que el sistema abstiene
correctamente y traza correctamente lo que traza, **pero no consigue respaldo
documental para todo lo que observa**. Es un resultado honesto y publicable, y
apunta a dónde seguir: alinear el mapeo entre lo que el modelo mira y lo que el
manual documenta.

---

## Lo que falta para responder a la pregunta como está formulada

| Requisito | Estado |
|---|---|
| Datos OBD-II **reales** del Mazda 3 BK con motor Z6 | **Pendiente — decisión del autor** |
| Proveedor de modelo de lenguaje | **Pendiente — decisión del autor** |
| Umbrales de suficiencia calibrados sobre validación | Pendiente |
| Mapeo diagnóstico→DTC corregido para la deriva del caudalímetro | Pendiente |
| Condiciones PARTIAL y DISTRACTOR extendidas a todos los casos | Pendiente |

El primero es el que bloquea la pregunta literal. Los demás afinarían un
resultado que ya existe.

---

## Desenlaces que se enumeraron de antemano, y cuáles ocurrieron

| Desenlace previsto | ¿Ocurrió? |
|---|---|
| La tasa de abstención es indistinguible con y sin evidencia | **No.** La decisión cambia limpiamente |
| Las referencias existen y resuelven pero no sostienen lo afirmado | **Parcialmente.** El verificador rechaza el 59 % de las citas candidatas, y eso es lo que impide que ocurra |
| El distractor se acepta como soporte | **Sí, con similitud pura.** El filtro de aplicabilidad lo evita |
| El agente se abstiene también con evidencia, con cobertura próxima a cero | **No.** Explica en 3 de 5 casos con evidencia |
| El modelo especializado no supera al baseline trivial | **No.** 0,879 frente a 0,074 |

Que dos de los cinco desenlaces adversos se hayan materializado --y se reporten--
es señal de que el experimento podía fallar, que era la condición que se puso al
diseñarlo.
