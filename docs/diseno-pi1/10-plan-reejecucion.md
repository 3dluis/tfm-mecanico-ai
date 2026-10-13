# 10. Plan de reejecución (Fase I)

**Los entregables son artefactos, no valores deseados.** Cada paso entrega un registro, una tabla o un
documento; ninguno entrega «una mejora». Si un paso produce un resultado plano o negativo, el paso está
cumplido.

## 10.1 Orden y dependencias

```
A. Correcciones documentales (E7, E2, las cuatro inconsistencias)
      │  no depende de nada; se puede hacer hoy
      ▼
B. Cambios de procedencia en el ejecutor del generador y del preprocesado
      │  depende de A solo por orden de lectura
      ▼
C. Generación de synthetic_v4 + sus cinco criterios de integridad
      │  depende de B: sin el manifiesto no se genera
      ▼
D. Reparto y subconjuntos anidados T6 ⊂ T12 ⊂ T18 ⊂ T22
      │  depende de C
      ▼
E. Protocolo simétrico implementado (partición interna, selección de época, calibración pareja)
      │  depende de D
      ▼
F. Rejilla: 6 representaciones (A1, A2, A3, A4, B, C) × 4 volúmenes × 5 réplicas = 120 celdas
      │  depende de E
      ▼
G. Análisis por fallo con el indicador de expresión
      │  depende de F, que es quien registra las predicciones por ventana
      ▼
H. Matriz de conclusiones revisada con la evidencia nueva
      │  depende de G
      ▼
I. Decisión del autor sobre qué entra en los capítulos 5 y 6
```

Los pasos A y B no tocan ningún resultado y pueden hacerse mientras se revisa el resto del paquete.

## 10.2 Recursos y duración estimada

| Paso | Cómputo | Trabajo | Nota |
|---|---|---|---|
| A | minutos | un día | lectura y escritura, más la reejecución de E6 sobre `synthetic_v2` con predicciones por ventana, que es lo que da registro a las dos cifras del termostato |
| B | ninguno | medio día | tres cambios de procedencia y sus pruebas |
| C | minutos | una hora | generación, preprocesado y los cinco criterios |
| D | minutos | una hora | reparto, subconjuntos y las tres pruebas de fuga |
| E | ninguno | un día | es el cambio con más riesgo de implementación |
| F | ~35 min | medio día | cinco variantes del bosque, que cuestan segundos cada una, y la red recurrente, que es la única cara: veinte ejecuciones de hasta 135 s. Bajo `launchd`, como la ejecución de E19 que funcionó |
| G | minutos | un día | el análisis, no el cómputo, es lo que lleva tiempo |
| H | ninguno | medio día | |

**Total estimado: entre cuatro y cinco días de trabajo y menos de una hora de cómputo.** El cómputo no
es la restricción; lo es no confundir variables, y eso se paga en cuidado, no en máquina.

## 10.3 Criterios de integridad, por paso

| Paso | Qué tiene que cumplirse para seguir |
|---|---|
| A | ninguna cifra del informe de E7 difiere de su registro; ninguna afirmación sobre el volumen sin su marca; `v3` no descrito como calibrado en ningún documento; y la reejecución de E6 **reproduce** las métricas agregadas de su registro, sin lo cual las dos cifras del termostato se retiran |
| B | la prueba de reconstrucción del manifiesto pasa: una sesión se regenera desde su `SessionSpec` y sale idéntica |
| C | los cinco criterios de `02-protocolo-synthetic-v4.md`, incluido el ralentí dentro del rango del manual y el reparto 22/7/7 |
| D | anidamiento estructural, auditoría de fuga en los cuatro puntos, estadísticos de normalización procedentes de cada subconjunto |
| E | la selección de época no toca validación en ninguna ruta del código; los dos modelos reciben el mismo reparto interno; el conjunto de prueba no se lee |
| F | las cinco semillas declaradas aparecen en los **ciento veinte** registros; ninguna celda con semilla distinta; las seis representaciones presentes en los cuatro volúmenes |
| G | el indicador de expresión se deriva del generador y no del modelo; las cifras del termostato quedan con registro |
| H | ninguna conclusión nueva sin su artefacto |

## 10.4 Criterios de parada

Se para y se informa, sin seguir al paso siguiente, si:

1. un criterio de integridad de la tabla anterior falla;
2. la generación de `synthetic_v4` no reproduce el ralentí del manual, lo que indicaría que la
   calibración no es la que se cree;
3. el protocolo simétrico cambia el resultado de `synthetic_v2` respecto de lo publicado **de forma que
   no se explique por la simetría**, porque entonces habría un defecto de implementación y no un
   hallazgo;
4. alguna orden lee la partición de prueba;
5. aparece la necesidad de un diseño 2×2 para sostener una conclusión: eso es ampliar el alcance y lo
   decide el autor, no el plan.

**No se para** porque la curva salga plana, porque la ventaja del modelo secuencial desaparezca al
corregir la asimetría, o porque el análisis por fallo refute la hipótesis del termostato. Esos tres son
resultados, y los tres son publicables.

## 10.5 Entregables

| Paso | Entregable |
|---|---|
| A | informe de E7 corregido con sus marcas; fila E2 corregida; cuatro inconsistencias resueltas o declaradas |
| B | `synthetic_v4.provenance.json` y su prueba de reconstrucción |
| C | el conjunto, su ficha, su manifiesto y el informe de los cinco criterios |
| D | la definición de los cuatro subconjuntos, con su permutación declarada, y las pruebas de fuga |
| E | el ejecutor con partición interna, y la prueba de que validación no interviene en la selección |
| F | **ciento veinte** registros con cabecera completa y predicciones por ventana; tabla resumen con medianas, rangos y diferencias apareadas, incluida la de `A2` frente a `A3`, que es la única que aísla la dinámica intraventana |
| G | el análisis por fallo separado por expresión; el artefacto que da registro a las cifras del termostato |
| H | la matriz de conclusiones con la evidencia nueva |

Ninguno de estos entregables es «que la red supere al bosque». Si eso ocurre, será un resultado; si no,
también.

## 10.6 Qué queda fuera de este plan, y sigue por delante

Las tres prioridades que el tutor puso antes de cualquier ampliación temporal: el rediseño de la
condición con distractor, el reentrenamiento del adaptador sin contaminación y las ablaciones de E18
sobre el conjunto de prueba. Este plan **no** compite con ellas; si hay que elegir, van primero.
