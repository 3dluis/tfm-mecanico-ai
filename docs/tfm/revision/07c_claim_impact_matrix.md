# 07c · Matriz de impacto sobre las afirmaciones

**Fecha:** 3 de septiembre de 2026 · Qué afirmación del documento cambia con cada corrección,
en qué dirección, y qué fortaleza verificada podría verse afectada. **Nada se ha modificado.**

Las tres columnas de estado usan la clasificación del verificador de evidencia:
`SUPPORTED` · `PARTIALLY_SUPPORTED` · `UNSUPPORTED` · `CONTRADICTED` · `UNVERIFIABLE`.

---

## 1. Afirmaciones que cambian de estado al corregir

| Afirmación (abreviada) | Dónde | Estado hoy | Problema | Estado tras corregir | Dirección del cambio |
|---|---|---|---|---|---|
| «Las cuatro subpreguntas quedan sostenidas» | `cap5:203-205` | `PARTIALLY_SUPPORTED` | P-03, P-02, P-08 | `SUPPORTED` **con alcance declarado** | Se estrecha: pasa a «sobre el caso evaluado, con diagnóstico correcto y códigos anotados» |
| «Toda afirmación admitida es trazable hasta una observación y un fragmento» | `cap5:207`, `cap4` | `PARTIALLY_SUPPORTED` (condicional) | P-02, P-06A, P-08 | `SUPPORTED` condicionado | Se declara la condición; la cobertura se recalcula con textos corregidos |
| «La distancia entre completitud y soporte es cero» | `cap5:208` | `UNVERIFIABLE` | P-05 | **retirada de resultados** | Deja de ser un resultado y pasa a propiedad del diseño |
| «La decisión cambia al retirar la evidencia» | `cap5`, `cap6`, resumen | `SUPPORTED` con n = 1 fallo | P-03 | `SUPPORTED` con n declarado | Se explicita el tamaño; no se debilita el hallazgo |
| «La evidencia parecida no se acepta» | `cap5`, matriz | `SUPPORTED` en lo evaluado | P-03 | `SUPPORTED` con n declarado | Igual |
| «El modelo temporal no supera al tabular» | `cap5:52-62`, `cap3`, `cap6`, L-15 | `CONTRADICTED` por el registro propio | P-04, P-06C | `SUPPORTED` como inconcluso | **Cambia de signo la lectura**: con más datos el orden se invierte; ninguna diferencia se ha establecido con réplicas |
| «El fallo de encendido se detecta en la mitad de los casos» | `cap5`, L-15 | `CONTRADICTED` en el conjunto mayor | P-04 | acotada al conjunto pequeño | Se declara que con el triple de sesiones sube a 0,91 |
| «La recuperación guiada encuentra el procedimiento siempre» | `cap5:82-92` | `PARTIALLY_SUPPORTED` | P-01 nº 2, P-02 | `SUPPORTED` como cota superior asistida por oráculo | Cifras regeneradas desde el registro; etiqueta nueva |
| «El idioma de la consulta importa» | `cap5:94-105` | `UNVERIFIABLE` | P-01 nº 3 | `SUPPORTED` si `RX-03` lo reproduce; **retirada** si no | Puede desaparecer del documento |
| «Su confianza calibrada significa lo que aparenta» | `cap5:64-71, 204-206` | `PARTIALLY_SUPPORTED` | P-01 nº 4, P-07 | `SUPPORTED` con verbo más débil | Pasa a «reduce el error de calibración», con registro |
| «Los umbrales están calibrados, no elegidos» | `cap5:123-125`, informe de fase | `UNSUPPORTED` | P-07 | **reformulada**: «definido heurísticamente» | Se retira la palabra; el resultado no cambia |
| «Respeta el veredicto 9 de 9» | `cap5:172-176` | `PARTIALLY_SUPPORTED` | P-06B | `SUPPORTED` con denominador real | El denominador baja en dos configuraciones |
| Recuentos de trazabilidad: 18 / 12 / 0,667 | `matriz:67-73` | `CONTRADICTED` por el registro | P-01 nº 5 | `SUPPORTED` con 27 / 15 / 0,556 | **Empeora la cifra publicada**; se corrige igualmente |
| Suelo de ruido y ejemplo de la ventana | `cap4:95-108` | `CONTRADICTED` por el registro | P-01 nº 1, P-06C | `SUPPORTED` regenerado | Cambian las cuatro cifras y el descriptor del ejemplo |
| Afirmación de novedad sobre la cuarta subpregunta | `cap1:54-57` | `CONTRADICTED` por el registro propio | P-13, P-10 | `SUPPORTED` en su forma estrecha | Se estrecha y se cita |
| «Existen trabajos sobre robustez a documentos irrelevantes» | `cap3:213-218` | `UNSUPPORTED` (sin cita) | P-10 | `SUPPORTED` con cuatro referencias | Se incorporan fuentes ya verificadas |
| «Las discrepancias informe ↔ registro son dos: E6 y E7» | `cap5:7-8`, `cap6:100-101` | `CONTRADICTED` | P-01 | corregida a cuatro o más | Se amplía el recuento propio |

**Ninguna corrección mejora artificialmente una cifra.** Tres de ellas la empeoran: los
recuentos de trazabilidad, el denominador del respeto al veredicto y el suelo de ruido. Se
corrigen igual.

---

## 2. Afirmaciones que **no** cambian

Estas se han verificado contra el artefacto y sobreviven a todas las correcciones previstas.
Forman el núcleo de lo que el trabajo puede defender.

| Afirmación | Evidencia que la sostiene |
|---|---|
| El agente explica con evidencia y se abstiene sin ella, sobre el mismo caso y con la misma confianza calibrada | `experiments/E15_suficiencia.json`: C05 a C09 comparten caso, ventana y confianza 0,9078; solo cambia el corpus |
| El sistema responde a la **pertinencia** y no a la presencia | En las condiciones parcial y con distractor hay cuatro documentos aplicables delante y la cobertura es 0,00 |
| La verificación de soporte discrimina **sin** el oráculo | C07: rechaza las doce comprobaciones por falta de mención de la señal, aunque los fragmentos llevan el código esperado |
| Cero citas inexistentes | 63 ejecuciones verificadas contra el contexto entregado; la barrera se comprueba fuera del modelo |
| El diagnóstico supera con mucho a la referencia mínima | 0,8788 frente a 0,0741 de F1 macro, verificado en el registro |
| La recuperación semántica pura no encuentra el procedimiento y la guiada sí | 0,000 frente a 1,000 de tasa de acierto en el registro vigente; el salto sobrevive a la corrección de cifras |
| Los datos son sintéticos y no se presentan como reales | Declarado en resumen, capítulos 1, 4, 5 y 6 y en la matriz |
| La partición no tiene fuga temporal | Reparto por sesión, con auditor que se prueba provocando la fuga |
| El conjunto de test está cerrado | Cierre por código; ningún ejecutor lo abre; verificado en las seis auditorías |
| La decisión de abstención vive fuera del modelo de lenguaje | Verificador determinista; el modelo redacta lo ya decidido |

---

## 3. Fortalezas en riesgo por cada corrección

De las 65 fortalezas verificadas, estas son las que cada corrección podría dañar si se ejecuta
sin cuidado, y cómo se protege cada una.

| Corrección | Fortaleza en riesgo | Cómo se protege |
|---|---|---|
| **P-06A** plantilla de afirmaciones | «Las afirmaciones no atribuyen causa»; el validador rechaza frases causales | El cambio toca el sentido de la magnitud, no la prohibición causal. El test de frases causales se conserva y se ejecuta antes y después |
| **P-06A** | «Una afirmación por observación, con sus fragmentos» (la forma que el ajuste del modelo consiguió) | El cambio afecta al texto de la afirmación, no a la estructura. Se comprueba que la estructura se mantiene en la reejecución del agente |
| **P-06B** respeto al veredicto | «Cero citas inexistentes» | Son métricas independientes; la corrección no toca la barrera de citas |
| **P-01** regeneración de tablas | «Trece resultados negativos conservados» | Se regeneran también los negativos. Ninguno se retira. Comprobación explícita antes de publicar |
| **P-01** | «Una afirmación falsa tachada en cuatro informes en lugar de borrada» | El histórico no se reescribe: las cifras antiguas se marcan, no se borran |
| **P-03** opción B, acotar | «Los desenlaces que refutarían la pregunta están enumerados de antemano» | Acotar el alcance no toca esa lista, que es lo que hace falsable el trabajo |
| **P-03** opción A, ampliar | «El conjunto anotado se fijó antes de ejecutar» | Los casos nuevos se anotan **antes** de ejecutarlos, con su acción esperada, igual que los actuales |
| **P-05** retirar la distancia | «Doble trazabilidad verificada a nivel de afirmación» | La doble trazabilidad se sostiene con la cobertura, que no es invariante, y con los paquetes de evidencia |
| **P-07** retirar «calibrados» | «Los umbrales se fijaron solo con validación» | Esa fortaleza es cierta y se conserva: el test nunca se usó. Lo que se retira es la palabra «calibrado», no la disciplina de partición |
| **P-02** declarar el oráculo | «La recuperación guiada resuelve lo que la semántica no» | El hallazgo sobrevive: con la etiqueta declarada sigue diciendo que en documentación técnica lo que une consulta y procedimiento es un identificador exacto |
| **P-04** publicar el resultado vigente | «El resultado negativo del modelo temporal se conservó y se publicó» | La fortaleza se mantiene y se refuerza: el proyecto además detectó y registró su propia corrección. Lo que falla es que no llegó a la memoria |
| **P-09** fuente única | «La matriz de trazabilidad no tiene experimentos huérfanos» | La vista generada debe conservar la cobertura inversa; se comprueba en el gate |
| **P-12** ampliar capítulos | «Ninguna afirmación de significación estadística»; «cero adjetivación vacía» | El texto nuevo pasa por las mismas reglas de redacción; la auditoría de autenticidad se ejecuta después, en su fase |
| **P-11** procedencia | «La procedencia dudosa del corpus está documentada con precisión» | La corrección la hace **más** precisa: separa editor de canal en lugar de ocultar nada |

---

## 4. Riesgo residual después de corregir

Aun ejecutando todo el plan, quedan tres cosas que no se resuelven con correcciones
documentales, y conviene que consten desde ahora.

| Riesgo | Por qué persiste | Cómo se declara |
|---|---|---|
| **Validez externa nula** | Los datos son sintéticos; ninguna corrección los convierte en reales | Ya está declarado como la primera limitación, en cinco documentos |
| **Tamaño de la evidencia** | Aunque se amplíe el conjunto anotado, seguirán siendo pocos casos para afirmar propiedades generales | Se declara el n junto a cada tasa; las conclusiones hablan de mecanismo, no de rendimiento poblacional |
| **La cadena diagnóstico → consulta** | Si no se ejecutan los experimentos nuevos, el sistema no se ha medido de extremo a extremo | Se declara como condición de toda conclusión y como el primer trabajo pendiente |

Después de corregir, el trabajo responde a la pregunta de investigación **en su parte más
difícil** —el sistema distingue tener evidencia de tener evidencia pertinente, y se abstiene
cuando no la tiene— sobre una base declarada y estrecha. Eso es defendible. Lo que no sería
defendible es lo que hay hoy: la misma conclusión sin la base declarada.
