# Revisión académica integral de la memoria

**Fecha:** 14 de octubre de 2026 · **Qué cubre:** la revisión científica de los capítulos 5 y 6, la
bibliografía, los anexos, la correspondencia con el repositorio, la reproducibilidad y los campos
institucionales pendientes · **Qué NO hace:** no amplía la memoria, no cambia el título, no toca la
pregunta de investigación y no ejecuta ningún experimento

## 1. Capítulos 5 y 6: los trece puntos, uno a uno

| # | Qué debe reflejarse | Dónde está | ¿Correctamente? |
|---|---|---|---|
| 1 | **E6 y E7** | cap. 5, Tabla 5.1 y Figuras 5.3 y B.1 | **sí**. Exactitud 0,878 frente a 0,286; el modelo temporal **no supera** al tabular y así se dice. Las matrices muestran que los doce errores del bosque van a «sin fallo» y que la red produce cuatro cruzados |
| 2 | **E13 y sus limitaciones** | cap. 5, Tabla 5.7 y los tres párrafos siguientes | **sí**. «Los resultados del adaptador describen su comportamiento sobre casos que pudo haber visto, **no su generalización**» |
| 3 | **Contaminación** | cap. 5, párrafo del adaptador; cap. 6, limitaciones; anexo B.1 | **sí**, y con el estatuto declarado: la tabla de anexo B.1 clasifica ese resultado como «afectado por contaminación» y dice qué no puede sostener |
| 4 | **Ablaciones E18** | cap. 5, Tabla 5.8 y Figura 5.11 | **sí**, incluida la ablación `A2` marcada **inconclusa** en la tabla, en la figura y en su pie, con la causa: la consulta, no la ablación |
| 5 | **Evaluación final E19** | cap. 5, apartado propio, Figuras 5.12 y 5.13; cap. 6, OE3, OE5 y general | **sí**. 0 de 14, 2 de 8 y 6 de 10, con denominadores, ventanas y sesiones |
| 6 | **Distractor P1** | cap. 6, OE5 y objetivo general | **parcialmente**: está en el capítulo 6 y **citado** en el 5, pero el capítulo 5 no tiene apartado propio para él. Es la entrada `N-3`, abierta |
| 7 | **L-26** | cap. 5, cierre del apartado de E19; cap. 6, limitaciones | **sí**. Siete de 35 salidas con una cifra que el verificador no produjo, y la frase que importa: **ninguna de las dos tasas cambia**, porque las produce el verificador determinista |
| 8 | **`synthetic_v1`, `v2` y `v3`** | cap. 5, Figuras 5.2 y 5.4; cap. 6, OE2; anexo A.5 | **sí**. La tabla A.5 da los tres con su medición de reconstructibilidad, y el capítulo 6 ya no dice que de `v3` salgan E6, E7 y la evaluación final |
| 9 | **`fault_active` y `fault_expressed`** | cap. 5, PI.1, Figura 5.6 | **sí**, y con la advertencia explícita de que **no está comprobado** que las cinco ventanas sin señal sean las cinco que el modelo falla |
| 10 | **Limitaciones de reproducibilidad** | cap. 6, OE2; anexo C.5 | **sí**, con las dos medidas y lo que no se distribuye |
| 11 | **Aperturas del conjunto de prueba** | cap. 5, párrafo 2; anexo B.5 | **sí**: cinco aperturas en el capítulo, y los cinco niveles con lo que consume cada uno en el anexo |
| 12 | **Resultados negativos** | cap. 5, PI.1 y ablaciones; anexo B.1 | **sí**. El modelo temporal, la ablación inconclusa y la conclusión retirada sobre el volumen, los tres con su causa |
| 13 | **Contribución metodológica complementaria** | **en ninguna parte** | **no**. Es la entrada `N-4`, pendiente de decisión del autor, y se solapa con la ausencia de un apartado de contribuciones |

### Las cuatro prohibiciones, comprobadas

| Prohibición | Comprobación | Resultado |
|---|---|---|
| No presentar resultados contaminados como evidencia independiente | el único resultado contaminado es el del adaptador, y las tres veces que aparece lleva su salvedad; el anexo B.1 lo clasifica | **cumple** |
| No presentar cero falsa confianza como garantía de riesgo cero | el capítulo 5 publica el intervalo de Wilson, dice que el límite **depende del nivel de confianza y del modelo estadístico**, y que supone una independencia entre ejecuciones que estas no tienen | **cumple** |
| No atribuir una ventaja al contexto temporal cuando cambian representación y estimador | corregido el 13-10-2026 (`A-3`): el párrafo ya no atribuye al volumen, y la Figura 5.4 muestra las dos variables que se mueven | **cumple** |
| No presentar como validada una capacidad solo implementada | PI.2 se declara «sostenida como trazabilidad, **no como soporte medido**», y el capítulo 6 repite que la coincidencia con un juicio independiente **no se ha medido** | **cumple** |

## 2. Bibliografía

Medida sobre las 39 entradas y sobre las citas de los ocho ficheros de la memoria.

| Comprobación | Resultado |
|---|---|
| Correspondencia entre citas y referencias | **completa**: ninguna entrada queda sin citar en el texto |
| Identificadores | **39 de 39** llevan DOI o identificador de arXiv |
| Duplicados | **ninguno** |
| Consistencia de estilo | APA, con sangría francesa aplicada por el estilo de la plantilla |
| Fuentes realmente utilizadas | sí: cada entrada aparece citada al menos una vez |
| Manuales técnicos y conjuntos de datos | el manual de taller del vehículo y la norma ISO 15031-5 están referenciados |
| Fuentes de los métodos experimentales | los métodos llevan su referencia: bosque aleatorio, GRU, valores de Shapley, calibración, recuperación aumentada y adaptación de bajo rango |

**Un pendiente declarado:** la entrada de la norma ISO 15031-5 lleva «[Edición pendiente de
confirmar: 2015 o posterior]». No es un error de cita: es una comprobación abierta que el texto
señala en lugar de esconder. Conviene cerrarla antes de la entrega definitiva.

## 3. Anexos

| Comprobación | Resultado |
|---|---|
| No duplican el cuerpo | comprobado uno a uno en `propuesta-anexos.md` §7. El único solape real —el anexo C con el procedimiento de reproducción del repositorio— está declarado, con la opción de sustituirlo por una referencia |
| Figuras explicadas | las dos, A.1 y B.1, con su párrafo previo, su pie de siete campos y su interpretación |
| Datos con procedencia | las trece tablas citan su fichero o su fuente documental |
| Referencias cruzadas | once correspondencias declaradas con los capítulos, en `propuesta-anexos.md` §5 |
| Extensión | 15 páginas de 123, **12,2 %**, por debajo del 20 % que la plantilla toma como referencia |
| No compensan la extensión del cuerpo | **no se usan para eso**, y la auditoría de `D-01` lo dice expresamente: los anexos no puntúan y el mínimo de la sesión informativa los excluye |

## 4. Correspondencia con los notebooks y el repositorio

| Comprobación | Resultado |
|---|---|
| Rutas citadas en los capítulos | **52 ficheros citados, los 52 existen** |
| Los siete notebooks | ejecutados y reexportados; el anexo C.2 los lista con su modalidad |
| Versiones HTML | las siete, completas, sin rutas locales y con la modalidad visible |
| Figuras | las 18 presentes a 300 ppp, todas en el registro de `scripts/figuras_memoria.py` |
| Tablas | 36 numeradas, con numeración correlativa comprobada por prueba |
| Registros experimentales | cada cifra publicada cita el registro del que sale |
| Manifiestos | `configs/manifest_e19.json` congela las cuatro huellas antes de abrir el conjunto de prueba |
| Commit de referencia | impreso en la primera celda de cada notebook ejecutado |
| Limitaciones de reproducción | anexo C.5 y `configs/datos_no_reconstruibles.json` |

## 5. Reproducibilidad

| Comprobación | Resultado |
|---|---|
| Procedimiento desde un clon limpio | validado, con todos los pasos en verde |
| `synthetic_v2` | **se reconstruye bit a bit**: 72 de 72 sesiones idénticas y las cuatro huellas coinciden con las congeladas |
| `synthetic_v1` y `synthetic_v3` | **no se reconstruyen**, medido muestra a muestra; el guion se niega con los dos |
| Censo de artefactos históricos | **0 desviaciones** |
| Lo que no se distribuye | corpus, índice documental y pesos del adaptador, declarados con la prueba que cada uno detiene |

## 6. Campos institucionales pendientes de la portada

| Campo | Estado | Qué falta |
|---|---|---|
| Título | **provisional** | el registrado. `D-06` abierta: dos opciones preparadas para el director |
| Autor | **completo** | Luis Daniel Díaz |
| Encabezado, «Apellidos, Nombre» | **completo** | Díaz, Luis Daniel |
| **Director** | **pendiente** | el nombre completo. Consta el nombre de pila por la vía de la conversación, no por un documento del repositorio, y no se completa con una suposición |
| **Fecha** | **pendiente** | depende de la convocatoria. La sesión informativa fija dos: depósito el **13 de noviembre de 2026** o el **4 de diciembre de 2026**. La decisión es del autor |
| Código de la titulación | **lo trae la plantilla** | aparece en la portada tal como la plantilla lo imprime |

Los dos pendientes se muestran **a la vista** en el documento preliminar —`[Director/a]` y
`[Fecha (mes y año)]`— para que no pasen inadvertidos. **En la versión que se entregue formalmente
no puede quedar ningún marcador visible**: se rellenan en `configs/portada-tfm.json` y se vuelve a
montar.

## 7. Lo que esta revisión deja abierto

| # | Qué | De quién depende |
|---|---|---|
| 1 | **`D-01`**, la extensión | del director. Auditoría y borrador de consulta preparados |
| 2 | **`D-06`**, el título | del director. Dos opciones con su coste |
| 3 | **Apartado de contribuciones** en el capítulo 6 | del autor: es la carencia con más consecuencia en una defensa |
| 4 | **`N-4`**, la contribución metodológica complementaria | del autor |
| 5 | **`N-3`**, el apartado de P1 en el capítulo 5 | del autor |
| 6 | **Edición de la norma ISO** en la bibliografía | comprobación documental |
| 7 | **Director y fecha** de la portada | del autor |
| 8 | **`P2`**, el reentrenamiento del adaptador | de la infraestructura. Sigue `BLOCKED — INFRASTRUCTURE` y no bloquea lo documental |
