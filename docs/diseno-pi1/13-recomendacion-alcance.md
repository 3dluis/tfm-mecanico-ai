# Recomendación sobre el alcance de PI.1: ¿hacen falta las nueve fases?

**Fecha:** 13 de octubre de 2026 · **Qué es:** una recomendación, no una decisión. El paquete de
diseño sigue aprobado tal como está y **ninguna fase se retira aquí** · **Qué la motiva:** el
encargo pide decir si las nueve fases son realmente necesarias, y entre el 12 y el 13 de octubre
han cambiado cosas que afectan a la respuesta

## 1. La recomendación, en una frase

**Ejecutar la fase A, plegar G dentro de ella, fundir H con la matriz de impacto de los capítulos 5
y 6 que ya existe, y aplazar B, C, D, E y F —es decir, `synthetic_v4` y la curva de volumen— a
trabajo futuro, declarando con precisión qué queda sin responder.**

Eso convierte «entre cuatro y cinco días de trabajo» en **uno y medio**, no deja ninguna afirmación
falsa en el texto y renuncia a una medición que, como se argumenta abajo, no responde a lo que PI.1
pregunta.

## 2. Qué ha cambiado desde que el paquete se escribió

El paquete es del 12 de octubre. En veinticuatro horas, tres cosas:

| Qué | Efecto sobre PI.1 |
|---|---|
| **La expresión efectiva del fallo quedó medida** | la fase G —comprobar qué pasa con el termostato y con el encendido— tiene ya su medición principal: en calentamiento, **32 de 45 ventanas** etiquetadas con el termostato **no contienen ninguna señal observable del fallo**, y el encendido **no expresa por completo ninguna** de sus 45 (`../methodology/expresion-efectiva-del-fallo.md` §4) |
| **La infraestructura de B, C, D y E está construida y probada** | manifiesto de procedencia, particiones internas, subconjuntos anidados, semillas pre-registradas y auditoría del generador con doce comprobaciones existen en `src/` y pasan sus pruebas. Lo que queda de esas fases **no es código: es generar el conjunto y ejecutar** |
| **`synthetic_v3` resultó además no reconstruible** | medido: 0 de 216 sesiones idénticas con el generador publicado (`L-25`). No cambia el diagnóstico de PI.1 —ya se sabía pre-calibración— y sí cambia la lectura del riesgo de crear un conjunto nuevo |

## 3. El argumento de fondo: la curva de volumen no responde a lo que PI.1 pregunta

La pregunta que el tutor fijó es **en qué tipos de fallo el contexto temporal aporta señal
diagnóstica adicional y en cuáles no**. Las fases C, D, E y F construyen una curva de volumen con
subconjuntos anidados, cinco semillas y comparación apareada entre el bosque y la red recurrente.

Eso es un buen diseño y responde a **otra** pregunta: *¿mejora el estimador recurrente al tabular
cuando hay más datos?* El propio paquete lo reconoce en su decisión 5: la comparación se enuncia
como **diferencia entre dos recorridos completos**, no como efecto del contexto temporal, porque el
diseño 2×2 que lo aislaría ampliaría el alcance del TFM y **no se propone**.

De modo que, tras cuatro o cinco días de trabajo y ciento veinte ejecuciones, PI.1 tendría una curva
bien hecha sobre la que **seguiría sin poder** atribuir la diferencia al contexto temporal. Eso no
es un defecto del diseño: es que la pregunta exige un diseño que el TFM ha decidido no abordar.

**Y lo que PI.1 sí puede responder, ya tiene respuesta.** «¿En qué fallos aporta el contexto
temporal?» se responde, para los dos fallos donde la cuestión se planteó, con la medición de
expresión:

- **El termostato** es donde la red recurrente aventajaba al bosque, 11 de 14 ventanas frente a 9.
  Y es el único fallo con ventanas **sin ninguna señal observable**: 32 de 45 en calentamiento. La
  hipótesis que eso sugiere —que la ventaja aparente del modelo temporal se concentra en ventanas
  donde no hay nada que ver, y por tanto no es una ventaja de representación— es comprobable con
  **una sola ejecución**: E6 sobre `synthetic_v2` con predicciones por ventana, que **la fase A ya
  incluye**.
- **El fallo de encendido**, con 0 de 45 ventanas plenamente expresadas, explica por sí mismo por
  qué ninguna representación lo detecta bien. No hace falta una curva de volumen para eso.

## 4. Lo que se gana aplazando, y lo que se pierde

### Lo que se gana

| | |
|---|---|
| **Tiempo** | de cuatro o cinco días a uno y medio, a dos meses de la entrega |
| **Riesgo que no se corre** | no se crea un segundo conjunto con nombre canónico dos meses antes de entregar. La validación de hoy en un clon limpio mostró que **un conjunto con el mismo nombre y otro contenido pasa las pruebas**: `meta.parquet` y el reparto reproducen aunque las señales no. Un `synthetic_v4` nuevo multiplica las ocasiones de ese error |
| **Coherencia del alcance** | el paquete advierte de sí mismo que, si los protocolos empiezan a parecer una investigación sobre qué arquitectura es superior, hay que recortarlos. Las fases C–F son la parte que más se le parece |

### Lo que se pierde, y conviene no minimizarlo

| | |
|---|---|
| **La única comparación con réplicas de todo el trabajo** | F sería la única medición con cinco semillas y comparación apareada. Todo lo demás del TFM es ejecución única, y un tribunal puede preguntar por qué. **Es el argumento más fuerte en contra de esta recomendación** |
| **La curva de volumen** | queda sin medir, y con ella la pregunta de si la desventaja del modelo temporal era de datos. Ahora mismo esa atribución está en el capítulo 5 y **está confundida**; aplazar significa **retirarla**, no dejarla |
| **La ablación de representaciones** | las cinco escalones de dinámica intraventana no se miden |

### Cómo se acota la pérdida

La pérdida de la comparación con réplicas es real y se compensa en parte: **una ejecución de E6 con
cinco semillas sobre `synthetic_v2`**, sin conjunto nuevo y sin curva, cuesta minutos y da la
dispersión del modelo de diagnóstico, que es la cifra que el capítulo 5 publica sin incertidumbre.
No es la comparación apareada de F, y responde a la objeción de la ejecución única donde más
importa: en la cifra principal de PI.1.

## 5. Las nueve fases, una a una

| Fase | Qué decide | Recomendación | Por qué |
|---|---|---|---|
| **A** · correcciones a E7 y E2 | qué corregir, con su evidencia | **EJECUTAR** | hoy el informe de E7 contradice a su propio registro y el índice describe `synthetic_v3` como calibrado cuando es anterior a la calibración. Son afirmaciones falsas en documentos publicados, y corregirlas no depende de nada |
| **B** · protocolo de `synthetic_v4` y manifiesto | cómo se genera el conjunto nuevo | **APLAZAR la generación; el manifiesto ya está hecho** | la procedencia está construida, probada y en uso. Generar `v4` es la decisión costosa, y es la que se aplaza |
| **C** · subconjuntos anidados | los cuatro volúmenes | **APLAZAR** | el código existe y pasa sus pruebas; sin `v4` no hay nada que repartir |
| **D** · protocolo de comparación simétrica | el protocolo entre los dos modelos | **CONSERVAR como diseño** | es el documento que hace interpretable cualquier comparación futura. Vale escrito aunque no se ejecute |
| **E** · réplicas y semillas | cinco semillas, apareadas | **CONSERVAR el pre-registro; sustituir por cinco semillas de E6 sobre `synthetic_v2`** | las semillas están declaradas; lo que se recomienda es gastarlas en la cifra que el capítulo publica, no en una curva |
| **F** · ablación de representación | las ciento veinte celdas | **APLAZAR** | es la fase cuya medición no responde a la pregunta de PI.1, por lo dicho en §3 |
| **G** · análisis por fallo | termostato y encendido | **PLEGAR DENTRO DE A** | su medición principal ya existe; lo que falta son las predicciones por ventana, que A ya ejecuta |
| **H** · matriz de conclusiones afectadas | qué afirmaciones caen | **FUNDIR con `../audits/matriz-impacto-cap5-cap6.md`** | esa matriz ya existe, es del 13 de octubre y cubre los dos capítulos completos, no solo lo que PI.1 toca. Mantener dos matrices es garantizar que una quede obsoleta |
| **I** · plan de reejecución | orden y dependencias | **REDUCIR al orden de A** | con cinco fases aplazadas, el plan de diez pasos sobra |

## 6. Qué habría que escribir si se acepta

No basta con no ejecutar: hay que decir qué queda sin responder, y dónde.

1. **En el capítulo 5**, retirar la atribución de la desventaja del modelo temporal al volumen de
   datos (entrada `A-3` de la matriz de impacto). Hoy esa frase compara dos generadores distintos.
2. **En el capítulo 6**, prospectiva: la curva de volumen y la ablación de representaciones quedan
   como trabajo futuro, **con su diseño ya escrito**, que es más de lo que suele dejarse. Y decir que
   el diseño 2×2 que aislaría el contexto temporal queda fuera del alcance de un TFM.
3. **En `docs/experiments/E7_modelo_temporal.md`**, el resultado de la fase A.
4. **En el informe de PI.1**, la respuesta que sí se puede dar: **el contexto temporal no aporta
   señal donde no hay señal**, y en el termostato en calentamiento, que es donde la ventaja aparente
   se concentraba, 32 de 45 ventanas etiquetadas no contienen ninguna.

## 7. Un hallazgo colateral que conviene arreglar antes

**El `README.md` de este paquete usa la formulación de la pregunta de investigación que `ADR-004`
declaró superada.** Su sección «Para qué es esto, y para qué no» enuncia la pregunta amplia
—patrones no representados, generación de hipótesis, conocimiento reutilizable— como si fuera la
vigente. Es un cuarto documento con esa contradicción, además de los tres que la matriz de impacto
de `ADR-004` inventarió el 13 de octubre, y la corrección es la misma: sustituir el enunciado por el
canónico, sin tocar nada más.

## 8. Qué decide el autor

**Lo que esta recomendación no hace:** no retira ninguna fase, no modifica el paquete de diseño, no
toca el capítulo 5 ni el 6, y no ejecuta nada.

**La decisión tiene dos partes separables**, y conviene no resolverlas juntas:

1. **Ejecutar A ahora** —con G plegada— es barato, corrige afirmaciones falsas y no depende de la
   otra decisión. Se recomienda sin reservas.
2. **Aplazar B, C, D, E y F** es la decisión de alcance, y el argumento en contra —perder la única
   comparación con réplicas del trabajo— es serio. La compensación propuesta, cinco semillas de E6
   sobre `synthetic_v2`, lo mitiga en la cifra principal y no en la comparación entre modelos.
