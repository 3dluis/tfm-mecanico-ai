# 5. Protocolo comparable entre bosque aleatorio y red recurrente (Fase D)

**El problema que resuelve.** Hoy la comparación está sesgada a favor del modelo temporal y el propio
informe de E7 lo declara: «la GRU restaura la época con mejor F1 macro **de validación** y la cifra que
se reporta es la F1 macro sobre esa misma validación: es el máximo de entre sesenta y setenta y cuatro
evaluaciones sobre el conjunto que se publica. El bosque no selecciona nada sobre validación».

Dicho sin tecnicismos: a la red se le dejan setenta y cuatro intentos y se publica el mejor, medido en
el mismo examen con el que se eligió. Al bosque, uno. Y aun así la red pierde en el conjunto oficial,
lo que hace que **ese resultado negativo sea conservador**; pero su ventaja de 0,0125 en el conjunto
grande es menor que el sesgo plausible, y por eso es inconclusa.

## 5.1 Las tres particiones y para qué sirve cada una

| Partición | Para qué | Quién la ve |
|---|---|---|
| **Interno de ajuste** | ajustar los parámetros del modelo | los dos modelos |
| **Interno de desarrollo** | **seleccionar la época** y, si se tocaran, los hiperparámetros | los dos modelos |
| **Interno de calibración** | ajustar el calibrador isotónico | los dos modelos |
| **Validación** | medir y comparar | solo para medir, **nunca para seleccionar** |
| **Prueba** | no se usa en PI.1 | nadie |

Las tres internas salen de las sesiones de entrenamiento de cada punto de la curva, repartidas **por
sesión** y estratificadas por condición, en proporciones **4/6, 1/6 y 1/6**: por condición, el resto va a
ajuste y desarrollo y calibración reciben al menos una sesión cada una. En los cuatro puntos sale 4/1/1,
8/2/2, 12/3/3 y 14/4/4 sesiones por condición.

**El cambio central:** la época del modelo temporal se selecciona sobre el **interno de desarrollo** y
la cifra se reporta sobre validación, que ya no interviene en ninguna decisión.

**Y la calibración tiene su propia partición, que es lo que hace el protocolo de verdad simétrico.** La
tentación es calibrar sobre el interno de desarrollo, que ya existe y no cuesta nada; pero ahí la época
de la red **se eligió** mirando esa partición, de modo que sus predicciones están sesgadas a favor en
ella. El bosque no tiene paso de selección equivalente, así que calibrar los dos sobre desarrollo
volvería a dar ventaja a uno. Con una tercera partición disjunta, ninguno de los dos ha visto esos datos
para decidir nada.

Con `T6` eso deja cuatro sesiones de ajuste, una de desarrollo y una de calibración por condición, que es
poco y hay que decirlo: en el punto más pequeño tanto la selección de época como la calibración serán
ruidosas. Es una propiedad del punto, no un defecto del protocolo, y se lee mirando la tendencia a lo
largo de los cuatro puntos y no el valor de uno.

**Y el conjunto de prueba no se usa para seleccionar nada, en ningún punto de este protocolo.** PI.1 se
responde sobre validación. La partición de prueba de `synthetic_v4` existe porque el reparto la crea, y
se queda cerrada.

## 5.2 Simetría, punto por punto

| | Bosque aleatorio | Red recurrente |
|---|---|---|
| Representación | 139 descriptores de ventana | secuencia de 120 × 12 |
| Ajuste | sobre el interno de ajuste | sobre el interno de ajuste |
| Selección de época | no aplica | **sobre el interno de desarrollo** |
| Hiperparámetros | los congelados de `BaselineConfig`; si se tocaran, sobre el interno de desarrollo | los congelados de la configuración de E7; igual condición |
| Calibración | isotónica **sobre las predicciones del interno de calibración** | la misma técnica y los mismos datos para los dos, sin validación cruzada, y sobre una partición que ninguno usó para seleccionar nada |
| Métrica que se publica | sobre **validación** | sobre **validación** |
| Semilla | la de la réplica | la misma de la réplica, apareada |

La calibración merece dos notas.

La primera, que hoy el bosque se calibra y la red no, y aun así la red sale mejor calibrada en los dos
conjuntos: ECE 0,1317 frente a 0,1439 en `v2`, y 0,0163 frente a 0,0801 en `v3`. Calibrar las dos con la
misma técnica y sobre los mismos datos convierte esa observación en comparable; hoy no lo es.

La segunda es cómo se calibra, y la respuesta cambió al calcular su coste.

El código actual usa `CalibratedClassifierCV(..., cv=5)`, que forma sus pliegues **por muestra**, es decir
por ventana: ventanas solapadas de una misma sesión caen a la vez en el pliegue que ajusta el modelo y en
el que ajusta el calibrador, lo que rompe el control por sesión que el resto del protocolo mantiene. La
corrección evidente sería agrupar los pliegues por sesión. Pero aplicarla a la red recurrente significa
**cinco ajustes más por celda** para obtener predicciones fuera de pliegue, y con veinte celdas de red
eso convierte media hora de cómputo en varias horas.

**La solución que se adopta: una partición interna de calibración propia**, disjunta del ajuste y del
desarrollo, repartida por sesión. El calibrador se ajusta sobre las predicciones que el modelo ya produce
en ella: **cero ajustes adicionales** para los dos modelos, el mismo procedimiento con los mismos datos
para ambos, y —a diferencia de calibrar sobre desarrollo— sobre datos que ninguno de los dos usó para
elegir época ni hiperparámetros.

**Su límite, declarado:** la isotónica sobre una partición pequeña es ruidosa. En el punto `T6` el interno
de calibración tiene una sesión por condición. Es una propiedad del punto, no del procedimiento, y se
lee en la tendencia de los cuatro puntos.

**Y sobre lo ya publicado:** el reparto por ventana afecta a los experimentos que ajustan el calibrador,
que son E15 y E19 (`threshold_runner.py` y `sufficiency_runner.py`, ambos
`CalibratedClassifierCV(method="isotonic", cv=5)`). **E6 no está entre ellos**: `baseline_runner.py`
ajusta un bosque sin calibrar y calcula su error de calibración sobre `predict_proba` en crudo, de modo
que su ECE de 0,1439 es el del modelo sin calibrar y no arrastra esta limitación —lo que también quiere
decir que la comparación de ECE entre E6 y E7 no es una comparación entre dos calibradores. Sobre E15 y
E19 el reparto **no** invalida ninguna cifra: el error de calibración se reporta sobre validación o sobre
prueba, ajenas a esos pliegues, así que el número es honesto. Lo que queda es un calibrador peor ajustado
de lo que podría estar. Va a limitaciones, no a correcciones: E19 está cerrada y su código no se toca.

## 5.3 Métricas que se publican

Las mismas para los dos, sobre validación: exactitud, F1 macro, F1 ponderado, exactitud equilibrada y
**métricas por clase**, que son las que responden a la pregunta del tutor; y error de calibración
esperado con diez tramos, confianza media, acierto y sesgo, antes y después de calibrar.

Con cinco semillas, cada cifra se resume como mediana y rango entre réplicas, y las diferencias entre
modelos se calculan **apareadas por semilla**. Ver `06-plan-replicas.md`.

## 5.4 Lo que este protocolo sigue sin aislar, y hay que decirlo donde se publique

**La comparación cambia la representación y el estimador a la vez.** Bosque sobre descriptores frente a
red recurrente sobre series: una diferencia por clase podría venir del sesgo inductivo de la red, de su
regularización o de su capacidad, y no de que la secuencia contenga más información diagnóstica.

Aislarlo exigiría un diseño 2×2 —los dos estimadores sobre las dos representaciones— y **no se
propone**: ampliaría el alcance del TFM, que no es decidir qué arquitectura es mejor. Lo que se propone
es enunciar el resultado por lo que es: **una diferencia entre dos recorridos completos**,
representación y modelo juntos, que es lo que el trabajo compara y lo que un taller elegiría.

La ablación `A` frente a `B` de `07-ablacion-representacion.md` **sí** aísla la representación, porque
mantiene el estimador. Es el único eslabón limpio de la cadena, y por eso importa.

## 5.5 Criterio de parada

Se para si la prueba de fuga de la normalización falla, si la selección de época toca validación o el
interno de calibración en algún punto del código, si las tres particiones internas comparten alguna
sesión, o si los dos modelos no reciben el mismo reparto interno. Se para también si
cualquier orden de este protocolo lee la partición de prueba.

No se para por el signo de la diferencia.
