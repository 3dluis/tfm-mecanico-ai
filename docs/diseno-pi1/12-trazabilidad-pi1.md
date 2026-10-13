# 12. Trazabilidad de PI.1

## 12.1 Dónde encaja PI.1 en la pregunta del TFM

La pregunta de investigación pregunta si un sistema híbrido puede identificar patrones de fallo no
representados en su conocimiento disponible, generar hipótesis diagnósticas desde el análisis contextual
y longitudinal de datos OBD-II, y validarlas mediante evidencia antes de incorporarlas como
conocimiento reutilizable.

PI.1 cubre **una** pieza: la calidad y los límites de la hipótesis diagnóstica que el sistema genera a
partir de la telemetría, y qué información diagnóstica aporta cada representación de esa telemetría. No
cubre la validación documental, que es PI.2 y PI.3, ni el rechazo de evidencia engañosa, que es PI.4.

**Lo que PI.1 no es:** un estudio sobre qué arquitectura de aprendizaje automático es superior. La
comparación entre el bosque y la red recurrente sirve para entender qué aporta cada representación y
dónde falla, no para coronar una. El objeto de evaluación sigue siendo el sistema completo, y E19 acaba
de medirlo.

## 12.2 La cadena

```
PI.1  ¿en qué tipos de fallo el contexto temporal aporta señal diagnóstica adicional?
  │
  ├── OE3  diagnosticar desde ventanas de telemetría y caracterizar la confianza
  │
  ├── representación del estado y de la ventana
  │     ├── A  nivel medio de ventana ......... bosque ... (por diseñar)
  │     ├── B  139 descriptores ............... bosque ... E6
  │     └── C  secuencia 120 × 12 ............. BiGRU .... E7
  │
  ├── comparación agregada ........ E6 frente a E7, NEGATIVA en v2, INCONCLUSA en v3
  ├── comparación por fallo ........ patrón observado, pendiente de réplicas y de expresión
  ├── control del volumen .......... CONFUNDIDO hoy; curva T6-T22 por diseñar
  └── interpretación .............. acotada: diferencia entre dos recorridos, no efecto temporal
```

## 12.3 Matriz: pregunta → experimento → métrica → artefacto → estado

| Pieza de PI.1 | Experimento | Métrica | Artefacto | Estado |
|---|---|---|---|---|
| El diagnóstico supera al azar y su confianza se puede calibrar | E6, E19 | F1 macro, ECE | `E6_baseline_synthetic_v2.json`, `E19_evaluacion_final_v3.json` | **sostenido** sobre validación y sobre prueba |
| Separabilidad por señal y por vía | E4 | delta de Cliff | `tables/E4_*.csv` | sostenido; sin JSON |
| La representación secuencial supera a la tabular | E7 | F1 macro | `E7_temporal_synthetic_v2.json` | **NEGATIVO** en el conjunto oficial |
| …y lo hace con más volumen | E7 sobre `v3` | F1 macro | `E7_temporal_synthetic_v3.json` | **INCONCLUSO y confundido**: el conjunto es pre-calibración |
| El contexto temporal aporta en el termostato | E7 por clase | F1 y exhaustividad del termostato | matrices de confusión de E6 y E7 | **patrón observado, no demostrado**: falta saber si la ventaja está en ventanas con el fallo expresado |
| Cuánto aporta la **dinámica intraventana** | escalón **`A2` frente a `A3`** de la escalera de ablaciones, con el estimador fijo | F1 por clase | por diseñar, Fase F | **por medir**; es el **único** eslabón que la aísla. `A` frente a `B` sin escalones añade 127 descriptores mezclados y no sirve para esta atribución |
| El volumen limitaba la comparación | curva T6-T22 | F1 macro y por clase frente a sesiones de entrenamiento | por diseñar, Fase C | **por medir** |
| La ventaja sobrevive a la simetría y a la semilla | protocolo simétrico, cinco réplicas | diferencias apareadas | por diseñar, Fases D y E | **por medir** |
| Dónde ocurre la diferencia en el termostato y en el encendido | análisis por expresión | exhaustividad con el fallo expresado y sin expresar | por diseñar, Fase G | **por medir** |

## 12.4 Qué documento sostiene cada decisión del paquete

| Decisión | Documento |
|---|---|
| Corregir E7 y E2 sin borrar la afirmación anterior | `01` |
| Generar `synthetic_v4` sin adoptarlo como canónico | `02` |
| Poder responder con qué configuración se generó cada sesión | `03` |
| Medir el volumen con validación fija y subconjuntos anidados | `04` |
| Quitar la asimetría de la selección de época | `05` |
| Cinco semillas declaradas antes de ejecutar | `06` |
| Llamar a `A` por su nombre y decir qué comparación aísla qué | `07` |
| Comprobar el termostato en lugar de asumirlo | `08` |
| Qué conclusiones del capítulo 5 caen, se matizan o resisten | `09` |
| En qué orden, a qué coste y con qué criterios de parada | `10` |
| Qué puede salir mal y qué lo detectaría | `11` |

## 12.5 Lo que PI.1 podrá afirmar cuando esto se ejecute, y lo que no

**Podrá afirmar:** si la dinámica intraventana aporta sobre el nivel y la dispersión, con el estimador
fijo, que es el escalón `A2` frente a `A3`; cómo
cambian los dos recorridos al aumentar las sesiones de entrenamiento, con todo lo demás fijo; si las
diferencias por fallo sobreviven al cambio de semilla; y si la ventaja del recorrido secuencial en el
termostato ocurre en ventanas donde el fallo está expresado.

**No podrá afirmar:** que el contexto temporal, como tal, aporte o no aporte, porque la comparación entre
descriptores y secuencia cambia también el estimador. Para eso haría falta un diseño 2×2 que este
trabajo no incluye, y decirlo es más útil que insinuar lo contrario.
