# Diseño de los dos experimentos que faltan para alcanzar la pregunta

Pre-registro. Se escribe **antes** de ejecutar nada y fija los criterios de aceptación antes de
conocer ningún resultado. Cubre los dos términos de la pregunta de investigación que el plan de
veinte fases no contemplaba.

`PI_STATUS = LOCKED` — el plan experimental alcanza a la pregunta, no al revés.

---

# Gate 1 · `UNREPRESENTED_PATTERN_VALIDATION`

**Qué hay que demostrar:** que el sistema distingue un patrón de fallo que **no está
representado** en su conocimiento disponible de uno que sí lo está, y que esa distinción no es
un artefacto del bajo rendimiento del clasificador.

## El problema que hay que resolver

Hoy el detector se entrena sobre las mismas seis clases que el generador produce y la
recuperación se guía por un diccionario que asocia esas mismas clases a sus códigos de avería.
Reconocer una clase aprendida no demuestra nada sobre patrones no representados, y la partición
de test cierra casos, no clases.

Hay además un problema de identificabilidad ya descrito en el marco teórico: un patrón no
representado y un patrón mal observado **producen la misma señal externa**, confianza calibrada
baja. Sin un control que los separe, cualquier resultado sería ambiguo.

## Diseño propuesto · exclusión de una clase

Se retira una clase de fallo, `F04_o2_lag`, de **tres** sitios a la vez:

1. las particiones de entrenamiento y validación del detector;
2. el diccionario `DIAGNOSTICO_A_DTC` que guía la recuperación;
3. los ejemplos de ajuste del redactor.

La clase se conserva en el generador, de modo que puedan producirse sesiones con ese fallo. El
corpus documental **sí conserva** su procedimiento: así el conocimiento ausente queda localizado
en el detector y en la guía de recuperación, no en la evidencia.

### Cuatro brazos

| Brazo | Clase presentada | En el entrenamiento | En el corpus | Qué aísla |
|---|---|---|---|---|
| A · representado | `F01_vacuum_leak` | sí | sí | comportamiento de referencia |
| B · no representado, documentado | `F04_o2_lag` | **no** | sí | el conocimiento ausente es del modelo |
| C · no representado, no documentado | `F04_o2_lag` | **no** | **no** | ausencia simultánea en modelo y evidencia |
| D · control de observabilidad | `F01_vacuum_leak` en ventanas de 10 s | sí | sí | patrón representado pero **mal observado** |

El brazo D es el que da valor al experimento: si B y D se comportan igual, el sistema no
distingue desconocimiento de mala observación, y el resultado es negativo aunque las cifras
parezcan buenas.

### Qué hay que implementar

- Una partición `leave_one_class_out` en `splits.py`, con la clase excluida declarada en el
  registro de la ejecución.
- Un mecanismo de detección fuera de distribución. El más barato defendible es umbralizar la
  confianza calibrada máxima, fijando el umbral **sobre validación y sin ver la clase
  excluida**; se apoya en la clasificación selectiva de Geifman y El-Yaniv (2017, MET-09), ya
  citada en el marco teórico.
- Un motivo de abstención nuevo, `PATTERN_NOT_REPRESENTED`, distinto de
  `LOW_MODEL_CONFIDENCE`, para que la salida diga **por qué** se abstiene.
- Un control del conocimiento paramétrico del modelo de lenguaje: preguntarle por la clase
  excluida **sin evidencia recuperada** y registrar si la nombra. Si la conoce de memoria, el
  brazo C no mide lo que pretende.

### Criterio de aceptación, fijado antes de ejecutar

**Se sostiene si**, en el brazo B, el sistema se abstiene con motivo `PATTERN_NOT_REPRESENTED`
en una proporción de casos mayor que en el brazo D con una diferencia que no se explique por el
azar, y en el brazo A explica con normalidad.

**Se refuta si** B y D son indistinguibles, o si el brazo A se degrada al introducir el
mecanismo, lo que significaría haber comprado la detección a costa de la utilidad.

**Queda no concluyente si** el control del conocimiento paramétrico revela que el modelo de
lenguaje nombra la clase excluida sin evidencia.

---

# Gate 2 · `REUSABLE_KNOWLEDGE_VALIDATION`

**Qué hay que demostrar:** que una hipótesis que supera la validación se incorpora y se recupera
después, que una que no la supera **no** se incorpora, y que lo incorporado no se convierte en
evidencia de sí mismo.

## El riesgo que hay que evitar antes de diseñar nada

Una memoria de hipótesis validadas introduce circularidad: si lo almacenado puede satisfacer el
criterio de suficiencia, una hipótesis acabaría sosteniéndose sobre su propia validación
anterior, y el sistema podría explicar sin evidencia documental alguna. Es exactamente el fallo
que el resto del diseño existe para impedir.

**Regla de diseño, previa a la implementación:** lo incorporado se recupera como **antecedente**
—un diagnóstico previo con su procedencia—, nunca como evidencia documental que cuente para la
cobertura de afirmaciones. La suficiencia sigue exigiendo documentación del manual.

## Diseño propuesto

Un almacén de hipótesis validadas donde cada registro guarda el caso, el diagnóstico, las
afirmaciones, las citas que las sostuvieron, el veredicto, la versión del corpus y el
identificador de la ejecución.

**Vía positiva.** Un caso que termina en `EXPLAIN` con suficiencia satisfecha deja su registro.

**Vía negativa.** Un caso que termina en `ABSTAIN`, por cualquiera de los motivos, **no deja
registro**. Es la mitad del gate que la pregunta exige y la que más fácilmente se olvida medir.

**Recuperación posterior.** Un caso equivalente presentado más tarde encuentra el antecedente y
lo incorpora a su contexto como tal, sin que cuente para la suficiencia.

**Invalidación.** Si la versión del corpus cambia de modo que alguna cita del registro deja de
ser aplicable, el registro se marca invalidado y deja de recuperarse. Sin esto, la memoria
conserva conocimiento cuya evidencia ya no existe.

### Cuatro medidas

| Medida | Qué cuenta | Valor exigido |
|---|---|---|
| Admisión | hipótesis validadas que quedan incorporadas | todas |
| **Rechazo** | hipótesis abstenidas que quedan incorporadas | **ninguna** |
| Recuperación | casos equivalentes que recuperan su antecedente | todos |
| No contaminación | casos en que un antecedente satisface por sí solo la suficiencia | **ninguno** |

### Criterio de aceptación, fijado antes de ejecutar

**Se sostiene si** el rechazo y la no contaminación son exactos —cero en ambos— y la admisión y
la recuperación funcionan sobre el conjunto de casos evaluado.

**Se refuta si** una sola hipótesis abstenida entra en la memoria, o si un antecedente permite
explicar un caso sin documentación aplicable.

Las dos medidas que deben dar cero son las que importan. Una memoria que incorpora bien y
recupera bien, pero que admite una hipótesis no validada, es peor que no tener memoria.

---

# Consecuencias para la memoria

Ambos gates están **diseñados y no ejecutados**. Los objetivos específicos del capítulo 2 los
declaran como compromiso; el capítulo 4 declara que no tienen fase asignada. Ninguno de los dos
puede darse por cumplido sin ejecutar el experimento correspondiente y publicar su resultado,
sea cual sea.

Las limitaciones `L-21` y `L-22` se mantienen abiertas y pasan a citar este pre-registro como la
vía de cierre.
