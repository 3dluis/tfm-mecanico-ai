# 11. Riesgos metodológicos

Cada riesgo con lo que lo detectaría. Un riesgo sin detector es una esperanza.

## 11.1 Fugas de información

| # | Riesgo | Qué lo detecta |
|---|---|---|
| 1 | **Normalización desde el conjunto grande.** Si los estadísticos por señal se calculan sobre las 22 sesiones y se entrena con 6, el punto pequeño usa información de las dieciséis que no le tocan y la curva sale más plana de lo que es | Una prueba que construya un subconjunto desplazado y compruebe que no queda centrado, como la que E7 ya tiene para entrenamiento → validación |
| 2 | **Calibración desde el entrenamiento completo.** El mismo problema por otra vía | Comprobar que el objeto calibrado se ajustó con el número de ventanas del punto |
| 3 | **Subconjuntos por ventana en lugar de por sesión.** Dos ventanas consecutivas comparten la mitad de sus muestras | `audit_masks` sobre las máscaras reales de cada punto, no sobre el reparto |
| 3b | **Pliegues de calibración por ventana.** `CalibratedClassifierCV(..., cv=5)` reparte por muestra, de modo que ventanas solapadas de una sesión caen en el pliegue que ajusta el modelo y en el que ajusta el calibrador. El código actual lo hace así | Calibrar sobre la **partición interna de calibración**, repartida por sesión y disjunta del ajuste **y del desarrollo**: sin validación cruzada y sin ajustes adicionales. Sobre lo ya publicado no invalida cifras —el ECE se reporta sobre datos ajenos a esos pliegues— y va a limitaciones |
| 3c | **Calibración ruidosa en el punto pequeño.** La isotónica sobre una partición interna con una sesión por condición es inestable | Se declara con la cifra del punto `T6` en lugar de ocultarla; y la tendencia de la calibración se lee a lo largo de los cuatro puntos, no en uno |
| 3d | **Calibrar sobre la partición donde se eligió la época.** Las predicciones de la red en el interno de desarrollo están sesgadas a su favor, porque la época se eligió mirándolas; el bosque no tiene ese paso, así que calibrar ahí reintroduce la asimetría que esta fase corrige | Tercera partición interna, de calibración, disjunta de ajuste y desarrollo; y la comprobación de que las tres no comparten ninguna sesión |
| 4 | **Selección de época sobre la validación que se reporta.** Es el defecto que esta fase viene a corregir; reintroducirlo sería lo más fácil del mundo | Una prueba que falle si la ruta de selección recibe la partición de validación |
| 5 | **Lectura de la partición de prueba.** El cargador ya la cierra con excepción y razón escrita | El cierre técnico existente, y que ninguna orden de este plan pase `allow_test` |

## 11.2 Confusores

| # | Riesgo | Qué lo detecta o lo acota |
|---|---|---|
| 6 | **Representación y estimador cambian juntos** en `B` frente a `C`. Es estructural y no se elimina sin un diseño 2×2 | Se declara donde se publique, y se apoya la conclusión sobre representación en `A` frente a `B`, que sí la aísla |
| 7 | **Volumen y realización.** Cambiar el número de sesiones cambia qué sesiones hay | Subconjuntos anidados dentro de un único conjunto, con validación fija |
| 8 | **Volumen y calibración del generador**, que es el confusor que invalidó la conclusión anterior | `synthetic_v4` generado con una sola versión del generador, con las huellas de su código en el manifiesto |
| 9 | **Régimen y volumen.** Si `v4` llevara además una distribución distinta de regímenes, la curva volvería a estar confundida | La variación dirigida del calentamiento queda fuera de `v4` y, si se hace, será un conjunto aparte |

## 11.3 Sobreajuste y sobreinterpretación

| # | Riesgo | Qué lo detecta o lo acota |
|---|---|---|
| 10 | **Sobreajuste a las pocas sesiones de calentamiento.** El conjunto oficial tiene siete ventanas de termostato en calentamiento en entrenamiento; una red con diecinueve mil parámetros puede memorizarlas | El análisis por expresión del fallo: si la ventaja está en ventanas sin señal, es ajuste y no información |
| 11 | **Elegir la semilla después.** Cinco semillas declaradas en el paquete, comprobadas en los registros | La prueba que compara las semillas de los ciento veinte registros con las declaradas |
| 12 | **Leer una diferencia de dos ventanas como un efecto.** Catorce ventanas de dos sesiones no son catorce observaciones | Diferencias apareadas por semilla, mediana y recuento de signos; y la unidad de independencia declarada en cada tabla |
| 13 | **Extrapolar la curva.** Si sube en `T22`, la tentación es decir «hace falta más volumen» | Enunciar «el volumen seguía limitando en el rango explorado», que es lo que cuatro puntos sostienen |
| 14 | **Convertir PI.1 en un estudio de arquitecturas.** El riesgo de alcance, y el más probable de todos | El propio `README.md` del paquete lo declara; si los protocolos crecen hacia el 2×2 o hacia arquitecturas nuevas, hay que recortarlos |

## 11.4 Procedencia e integridad

| # | Riesgo | Qué lo detecta |
|---|---|---|
| 15 | **Una versión declarada que no distingue dos fenómenos.** Ya pasó: `GENERATOR_VERSION = 1.0.0` en `v2` y en `v3` | Huellas del código fuente del generador en el manifiesto, no una constante |
| 16 | **Regenerar un conjunto histórico para «arreglarlo»**, perdiendo la evidencia del resultado anterior | `v2` y `v3` no se regeneran; `v3` queda etiquetado como pre-calibración y sin renombrar |
| 17 | **Sobrescribir registros.** El nombre fijo ya sobrescribió los registros oficiales una vez, en E7 | Identificador de conjunto, de punto, de representación y de réplica en el nombre de cada registro |
| 18 | **Cifras sin registro.** Las dos del termostato llevan abiertas desde la auditoría de evidencia | El paso 4 de la Fase G las cierra, o se retiran |
| 19 | **Romper la cadena congelada de E19** al adoptar `v4` | `v4` no es canónico; `synthetic_v2` sigue siendo el conjunto oficial y la cadena de E19 no se toca |

## 11.5 Métricas mal interpretadas

| # | Riesgo | Qué lo acota |
|---|---|---|
| 20 | **Comparar F1 macro cuando tres clases están en 1,0000** y no hay margen. La media esconde dónde está el movimiento | Se publica siempre por clase, y la lectura se hace por clase |
| 21 | **Leer la calibración como ventaja** cuando uno de los dos modelos la selecciona sobre el conjunto que reporta | El protocolo simétrico calibra los dos igual y sobre los mismos datos |
| 22 | **Confundir ausencia deliberada de evidencia con fallo del recuperador**, que es el error que E19 ya tuvo que acotar | Las métricas de recuperación se leen por condición de evidencia, nunca agregadas |
| 23 | **Tomar la exhaustividad agregada del termostato como medida de detección** cuando una parte de sus ventanas no contiene el fallo | La separación por expresión; sin ella, la cifra agregada no significa lo que parece |

## 11.6 El riesgo que no tiene detector

Que todo esto consuma el tiempo que la memoria necesita. El TFM se defiende en diciembre, el informe de
seguimiento es el 6 de noviembre, y por delante de PI.1 están el rediseño del distractor, el
reentrenamiento del adaptador y las ablaciones sobre prueba. **Este paquete está diseñado para poder
ejecutarse en cinco días o para no ejecutarse en absoluto**, dejando en su lugar las correcciones
documentales de la Fase A, que son media jornada y resuelven los dos defectos que de verdad ensucian el
trabajo. Si hay que elegir, esa es la elección.
