# El valor científico de la fase F, y si cabe un conjunto mínimo de réplicas

**Fecha:** 13 de octubre de 2026 · **Qué pide el encargo:** evaluar el valor científico de la fase F
**antes** de descartarla, y decir si hay un conjunto mínimo de réplicas posible **sin reabrir
conjuntos de prueba ni ampliar el alcance** · **Qué NO hace este documento:** ejecutar nada. **La
fase F no se ha ejecutado**, y la propuesta de réplicas es una propuesta

## 1. La respuesta, en dos frases

**La fase F tiene valor metodológico real y no responde a ninguna afirmación que el TFM necesite
sostener.** Pero sí cabe un conjunto mínimo de réplicas, mucho más barato, que ataca la limitación de
frente: **cinco réplicas de E6 sobre `synthetic_v2`**, sin conjunto nuevo, sin tocar la partición de
prueba y sin salir del experimento que ya existe.

## 2. Qué daría la fase F, exactamente

Ciento veinte celdas: cuatro volúmenes anidados × cinco semillas × dos modelos, más la escalera de
ablación de representaciones.

| Lo que F produciría | Para qué sirve en este TFM |
|---|---|
| Una **curva de volumen** con cuatro puntos y dispersión por semilla | responde a «¿mejora el estimador recurrente con más datos?», que **no es ninguna de las cuatro subpreguntas** |
| Una **comparación apareada** entre bosque y red recurrente, con cinco semillas | sería la **única medición con réplicas de todo el trabajo**, y eso tiene valor por sí mismo |
| Cinco escalones de **ablación de la dinámica intraventana** | lo más cercano a aislar qué aporta el contexto temporal, **sin llegar a aislarlo** |
| Dispersión de F1 macro en cada celda | la cifra que el capítulo 5 publica sin incertidumbre |

### Lo que F no daría, y es lo que decide

**No permitiría atribuir ninguna diferencia al contexto temporal.** Lo dice el propio paquete en su
decisión 5: la comparación se enuncia como **diferencia entre dos recorridos completos**, no como
efecto del contexto temporal, porque el diseño 2×2 que lo aislaría **amplía el alcance del TFM** y no
se propone. Después de cuatro o cinco días de trabajo y ciento veinte ejecuciones, la pregunta de PI.1
seguiría sin responderse por esa vía.

**Y la pregunta que PI.1 sí tenía que responder ya está respondida**, con una medición que no costó
ninguna ejecución nueva: el rendimiento por clase del bosque se ordena igual que la **expresión
efectiva del fallo**. Las tres condiciones plenamente expresadas se aciertan por completo; las dos que
falla son las dos con un problema de expresión —el termostato con cinco ventanas sin ninguna señal, el
encendido sin ninguna ventana plenamente expresada—. Está en
[`14-cierre-alcance-reducido.md`](14-cierre-alcance-reducido.md) §2.

### El coste real, que no es el cómputo

| Concepto | Coste |
|---|---|
| Cómputo de F | ~35 minutos |
| Trabajo de F | medio día |
| **Las fases de las que F depende** | B —generar `synthetic_v4`—, C y E: **tres días más** |
| **El riesgo que B introduce** | un **tercer conjunto** con nombre canónico a dos meses de la entrega. La validación en un clon limpio del 13 de octubre midió que un conjunto con el mismo nombre y otro contenido **pasa las pruebas**, porque el ventanado y el reparto reproducen aunque las señales no |

**F cuesta cuatro días y un conjunto nuevo, no treinta y cinco minutos.** Esa es la cifra que hay que
poner en la balanza.

## 3. Veredicto sobre F

| | |
|---|---|
| **Valor para la pregunta canónica** | **ninguno directo.** PI.1 exige que el diagnóstico supere a la clase mayoritaria con confianza calibrable, y E6 lo establece: F1 macro 0,8788 frente a 0,0741 |
| **Valor metodológico** | **real.** Sería la única comparación apareada con réplicas del trabajo |
| **Valor como respuesta a la objeción «todo es ejecución única»** | **parcial**, y hay una forma más barata de obtenerlo (§4) |
| **Riesgo** | alto: depende de generar un conjunto nuevo dos meses antes de entregar |
| **Recomendación** | **no ejecutar.** Conservar su diseño como trabajo futuro, que es más de lo que suele dejarse: el protocolo está escrito y pre-registrado |

**Lo que se perdería, dicho sin suavizarlo:** la curva de volumen y la escalera de ablación quedan sin
medir, y con ellas la pregunta de si la desventaja del modelo temporal era de datos. Aplazar esa
pregunta significa **retirar** la afirmación que hoy la responde en el capítulo 5, no dejarla: está en
la entrada `A-3` de la matriz de impacto, y la fase A ya marcó el hallazgo como `SUPERSEDED`.

## 4. El conjunto mínimo de réplicas que sí cabe

### 4.1 Qué se propone

**Cinco réplicas de E6 —el bosque— sobre `synthetic_v2`**, con las cinco semillas ya pre-registradas
en `configs/semillas_pi1.json`: `20260901`, `20261901`, `20262901`, `20263901`, `20264901`. La primera
es la de la ejecución publicada, de modo que una de las cinco **reproduce** la cifra vigente y sirve de
control.

| Condición | Cumple |
|---|---|
| **No reabre ningún conjunto de prueba** | E6 mide sobre **validación**. La partición de prueba no se toca, no se carga y no se nombra |
| **No amplía el alcance** | es el mismo experimento, el mismo conjunto, la misma métrica y la misma partición. Lo único que cambia es la semilla del estimador |
| **No necesita conjunto nuevo** | `synthetic_v2` existe y se reconstruye bit a bit con sus huellas congeladas verificadas |
| **No sobrescribe nada** | el ejecutor exige `--etiqueta` y **se niega a escribir** sobre los nombres históricos |
| **Coste** | el ajuste del bosque tarda segundos. Cinco réplicas: **minutos** |

### 4.2 Qué mediría, y qué NO mediría

**Lo que mediría:** la dispersión de F1 macro, de la exactitud y del error de calibración **entre
semillas del estimador**. Es la incertidumbre que el capítulo 5 publica hoy sin ninguna: «el error de
calibración se calcula con diez intervalos sobre 98 ventanas y **se publica sin incertidumbre**».

**Lo que NO mediría, y es la salvedad que hay que escribir junto a cualquier cifra que salga de
ahí.** Lo declara ya el propio pre-registro de las semillas:

> «las cinco réplicas comparten las **mismas** sesiones de validación y de prueba, de modo que no son
> cinco muestras independientes: su dispersión mide **variabilidad de ajuste**, no variabilidad de
> evaluación, y el intervalo que se lea de ellas **subestima la incertidumbre total**.»

Con doce sesiones de validación y dos por condición, la variabilidad que domina es la del **reparto**,
y para medirla haría falta repartir de otra manera —lo que cambiaría el conjunto— o conseguir más
sesiones. Cinco semillas del bosque no la tocan.

### 4.3 Lo que no se propone, y por qué

**Cinco réplicas de E7 —la red recurrente— no se recomiendan como comparación.** `temporal_runner`
pasa la partición de **validación** a `train_temporal` para seleccionar la época:

```python
entrenado = train_temporal(entrenamiento.x, entrenamiento.y,
                           validacion.x, validacion.y, ...)
```

Esa es exactamente la asimetría que la auditoría de PI.1 identificó como una de las tres cosas que
invalidaban la comparación: el bosque no selecciona nada en validación y la red sí. **Ejecutar cinco
semillas con esa asimetría la replicaría cinco veces**, y el resultado seguiría sin ser interpretable
como comparación entre modelos. Corregirlo es la fase E —tres particiones internas y selección de
época fuera de validación—, que queda aplazada.

Dos conductas posibles, y se recomienda la primera:

| | |
|---|---|
| **Recomendado** | ejecutar las réplicas **solo de E6**, y presentar su dispersión como lo que es: la del modelo de diagnóstico vigente, que es el que el sistema usa |
| Alternativa | ejecutar también las de E7, **declarando** que describen la dispersión de un procedimiento con selección de época en validación y que **no se usan para comparar** con el bosque. Añade una cifra y un párrafo de salvedades; el beneficio es dudoso |

### 4.4 Lo que haría falta para ejecutarlo

Nada que no exista, y por eso la propuesta es barata:

```bash
for s in 20260901 20261901 20262901 20263901 20264901; do
  uv run mecanico-exp train-baseline --dataset-id synthetic_v2 \
    --etiqueta replica_$s          # la semilla entra por la configuración
done
```

**Falta una pieza pequeña:** `BaselineConfig.seed` existe y el ejecutor **no expone la semilla por
línea de órdenes**. Hacen falta dos líneas —un `--semilla` que llegue a la configuración— y eso es
una modificación del ejecutor, no del experimento: con la semilla por defecto, el comportamiento no
cambia. **No se ha escrito**, porque el encargo pide evaluar y no ejecutar.

### 4.5 El criterio, si se autoriza

Conviene fijarlo antes, no después:

| | |
|---|---|
| **Qué se publica** | mediana y rango de F1 macro, exactitud y error de calibración sobre las cinco réplicas, y las cinco cifras individuales |
| **Qué no se publica** | ningún intervalo de confianza. Cinco réplicas que comparten las sesiones de evaluación no lo sostienen |
| **Control de integridad** | la réplica con semilla `20260901` tiene que **reproducir** el registro publicado. Si no lo hace, hay algo que no es la semilla, y se para |
| **Qué resultado se publica** | el que salga. Si la dispersión es grande, la cifra de 0,8788 queda relativizada y eso **se dice**: es información sobre la fragilidad del resultado, no un fallo del trabajo |
| **Qué no se hace** | elegir la mejor de las cinco, ni sustituir la cifra publicada por la mediana. La publicada se conserva con su registro; la dispersión se añade |

## 5. Resumen para la decisión del autor

| Opción | Coste | Qué resuelve | Riesgo |
|---|---|---|---|
| **Ejecutar F** | 4–5 días + un conjunto nuevo | la curva de volumen y la ablación de representaciones; la única comparación apareada del trabajo | alto: tercer conjunto canónico a dos meses de entregar |
| **Réplicas mínimas de E6** | dos líneas de código y minutos de cómputo | la incertidumbre de la cifra principal de PI.1, que hoy se publica sin ninguna | bajo: mismo conjunto, misma partición, sin tocar la prueba |
| **Ninguna de las dos** | cero | nada | la limitación de la ejecución única queda declarada y sin atenuar |

**Recomendación:** la segunda. No cierra la objeción de la ejecución única —nada que comparta las
sesiones de evaluación la cierra—, y la convierte de «no hay ninguna réplica» en «hay cinco, y miden
la variabilidad de ajuste y no la de evaluación», que es una posición defendible y verdadera.
