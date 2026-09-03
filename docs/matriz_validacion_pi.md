# Matriz de validación de la pregunta de investigación

Última actualización: 3 de septiembre de 2026 · Datos: `synthetic_v2` (`dataset_type: synthetic`, calibrado contra el manual; ADR-003) ·
Corpus: manual de taller Mazda 3 BK, 6 158 fragmentos

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de
> datos OBD-II, rastreando cada explicación hasta su evidencia de
> origen, y reconocer cuándo la evidencia disponible no es suficiente para
> sostener una explicación en lugar de generar una hipótesis sin fundamento?

---

## Procedencia de los datos, y lo que condiciona

**Los datos son sintéticos** (`dataset_type: synthetic`), generados por un modelo
paramétrico calibrado contra el manual del Mazda 3 BK. La calibración documenta
sus parámetros; **no los convierte en una medición**.

Desde el 3 de septiembre de 2026 (ADR-003) la pregunta de investigación no exige
que los datos sean reales: exige que cada resultado declare sobre qué datos se
obtuvo. Esta matriz responde, por tanto, a la pregunta tal como está formulada,
**sobre el dataset declarado**. Lo que un resultado sobre sintéticos sostiene es el
comportamiento del agente ante los mecanismos de fallo representados; no
sostiene comportamiento equivalente en un vehículo real, y esa validez externa se
declara como limitación (L-01), no se presume.

Cada fila indica cuánto depende el resultado del realismo del dato. Las que
dependen menos son las que menos cambiarían con datos reales; las que dependen
más son las que habría que repetir sobre ellos.

---

## Estado por subpregunta

| PI | Métrica | Criterio | **Resultado medido** | Decisión |
|---|---|---|---|---|
| **PI.1** Diagnóstico | F1 macro sobre validación | Supera a la clase mayoritaria con margen amplio y la confianza está calibrada | **0,879** frente a 0,074 · ECE 0,144 → **0,085** tras calibrar | **Sostenida sobre datos sintéticos** |
| **PI.2** Trazabilidad | `claim support rate`, `citation completeness` | Toda afirmación admitida se ancla en observación y documento verificados | Tras corregir el mapeo diagnóstico→DTC, **cobertura 1,00 en las cinco condiciones con evidencia** | **Sostenida** |
| **PI.3** Reconocimiento de insuficiencia | Decisión EXPLAIN/ABSTAIN | La decisión cambia al retirar la evidencia | **EXPLAIN → ABSTAIN** con datos, modelo, atribución y confianza idénticos · 4 de 6 decisiones correctas | **Sostenida** |
| **PI.4** Rechazo de evidencia engañosa | Distractores aceptados | El procedimiento de otro motor no se acepta como evidencia | Semántica pura: **1 distractor por encima del correcto**. Con filtro: 0. **Sin filtro de motor**, el validador lo degrada a `PARTIAL_MATCH` y el agente se abstiene igual | **Sostenida, con dos líneas de defensa** |

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

**Estaba parcialmente sostenida, y se corrigió la causa.** Un tercio de las
afirmaciones se quedaba sin cita porque el mapeo diagnóstico→DTC describía mal
una condición: para la deriva del caudalímetro se buscaban solo los códigos del
sensor --que documentan la tensión de su circuito-- y no los de mezcla --que
documentan los ajustes de combustible desviados, que es lo que el modelo
observa--.

Con el mapeo corregido, **la cobertura es 1,00 en las cinco condiciones con
evidencia disponible**.

El verificador **sigue rechazando** la mayoría de las citas candidatas, y eso es
la pieza funcionando: rechaza tablas de códigos que mencionan el fallo sin
documentar cómo se comprueba, y procedimientos del motor equivocado.

**Depende poco de la condición sintética.** La desalineación entre lo que el
modelo mira y lo que el manual documenta es una propiedad del manual y del
problema, no de los datos.

---

## PI.3 · Reconocimiento de insuficiencia · **el resultado central**

Las **cuatro condiciones** sobre el mismo caso, con confianza idéntica 0,908:

| Condición | Docs aplicables | Cobertura | Decisión |
|---|---|---|---|
| **FULL** evidencia presente | 5 | 1,00 | **EXPLAIN** |
| **ABSENT** evidencia retirada | 0 | 0,00 | **ABSTAIN** |
| **PARTIAL** solo tablas de códigos | 4 | 0,00 | **ABSTAIN** |
| **DISTRACTOR** procedimiento de otro motor | 4 | 0,00 | **ABSTAIN** |

Mismos datos OBD-II. Mismo modelo. Misma atribución. **Misma confianza.** Lo
único que cambia es que se retiran del índice los 70 fragmentos que portan los
códigos que documentan esa condición.

La decisión cambia **porque cambió la evidencia**, no porque cambiara la certeza
del modelo. Es la pregunta de investigación reducida a su mínima expresión.

Decisiones correctas: **7 de 9**. Las dos discrepancias se dejan registradas sin
ajustar umbrales:

- **Fallo de encendido:** confianza calibrada 0,462. El conjunto anotado dice
  EXPLAIN porque *existe documento*; el criterio dice ABSTAIN porque *el modelo
  no es fiable ahí*. Probablemente la etiqueta esperada está mal puesta.
- **Deriva del caudalímetro:** confianza calibrada 0,600, por debajo del umbral
  de 0,80. Su cobertura documental es ahora 1,00, tras corregir el mapeo.

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

**Sostenida sobre `synthetic_v2` (`dataset_type: synthetic`, calibrado contra el
manual). Sin validación externa en vehículo real (L-01).**

Las cuatro subpreguntas se cumplen con los datos disponibles:

- **PI.1** el modelo diagnostica muy por encima del azar y su confianza está
  calibrada;
- **PI.2** toda afirmación admitida se ancla en observación y documento
  verificados, tras corregir el mapeo diagnóstico→DTC;
- **PI.3** la decisión cambia limpiamente entre las cuatro condiciones de
  disponibilidad de evidencia, con la confianza del modelo constante;
- **PI.4** el procedimiento del motor equivocado se rechaza, y por dos vías
  independientes.

**Lo que esto NO significa.** Los datos usados son sintéticos, y la pregunta se
responde sobre ellos. Lo mostrado es que **el mecanismo funciona**: que
retirar evidencia cambia la decisión, que una cita que no sostiene se rechaza y
que un documento de otro motor no cuenta. Queda por demostrar que sigue
funcionando cuando el dato de entrada tiene el ruido, el solapamiento entre
condiciones y los fallos concurrentes de un vehículo real.

El resultado que más se sostendría con datos reales es **PI.4**, que es
puramente documental. El que más cambiaría es **PI.1**.

---

## Lo que falta para ampliar la validez de la respuesta

| Requisito | Estado |
|---|---|
| Datos OBD-II reales del Mazda 3 BK con motor Z6, como validación externa (ya no precondición de la PI; ADR-003) | **Pendiente — decisión del autor** |
| Proveedor de modelo de lenguaje | **Pendiente — decisión del autor** |
| Umbrales de suficiencia calibrados sobre validación | Pendiente |
| Mapeo diagnóstico→DTC corregido para la deriva del caudalímetro | Pendiente |
| Condiciones PARTIAL y DISTRACTOR extendidas a todos los casos | Pendiente |

El primero es el que ampliaría la validez externa. Los demás afinarían un
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
