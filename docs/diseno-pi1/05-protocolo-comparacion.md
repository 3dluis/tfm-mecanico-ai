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
| **Entrenamiento**, dividido en interno de ajuste e interno de desarrollo | ajustar parámetros, **seleccionar la época**, elegir hiperparámetros, ajustar la calibración | los dos modelos |
| **Validación** | medir y comparar | solo para medir, **nunca para seleccionar** |
| **Prueba** | no se usa en PI.1 | nadie |

**El cambio central:** la época del modelo temporal se selecciona sobre una **partición interna de
desarrollo**, obtenida del propio subconjunto de entrenamiento y repartida **por sesión**, y la cifra se
reporta después sobre validación, que ya no interviene en ninguna decisión.

El reparto interno propuesto: de las sesiones de entrenamiento de cada punto de la curva, **cinco
sextos a ajuste y un sexto a desarrollo**, estratificado por condición y por sesión. Con `T6` eso deja
cinco sesiones de ajuste y una de desarrollo por condición, que es poco y hay que decirlo: en el punto
más pequeño la selección de época será ruidosa, y esa es una propiedad del punto, no un defecto del
protocolo.

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
| Calibración | isotónica, validación cruzada interna **sobre el interno de ajuste** | la misma técnica, sobre el mismo interno de ajuste, para que la calibración no sea una ventaja de uno |
| Métrica que se publica | sobre **validación** | sobre **validación** |
| Semilla | la de la réplica | la misma de la réplica, apareada |

La calibración merece una nota. Hoy el bosque se calibra y la red no, y aun así la red sale mejor
calibrada en los dos conjuntos: ECE 0,1317 frente a 0,1439 en `v2`, y 0,0163 frente a 0,0801 en `v3`.
Calibrar las dos con la misma técnica y sobre los mismos datos convierte esa observación en comparable;
hoy no lo es.

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

Se para si la prueba de fuga de la normalización falla, si la selección de época toca validación en
algún punto del código, o si los dos modelos no reciben el mismo reparto interno. Se para también si
cualquier orden de este protocolo lee la partición de prueba.

No se para por el signo de la diferencia.
