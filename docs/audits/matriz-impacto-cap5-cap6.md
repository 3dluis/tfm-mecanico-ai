# Matriz de impacto sobre los capítulos 5 y 6

**Fecha:** 13 de octubre de 2026 · **Qué es:** el inventario de lo que los hallazgos del 12 y 13 de
octubre tocan en el texto de los capítulos de resultados y conclusiones · **Qué NO es:** una
reescritura. **No se ha modificado ni una línea de los dos capítulos.** Aquí solo se dice qué habría
que corregir, con qué evidencia y con qué prioridad, para que la decisión y la redacción sean del
autor · **Por qué existe:** el encargo pide preparar la matriz **antes** de tocar los documentos
científicos

## 1. Resumen: qué queda afectado

Veintidós entradas, repartidas en tres clases. El recuento es el de esta matriz, no una medición
sobre el texto: no se ha contado cuántas afirmaciones tienen los dos capítulos en total, y por eso
no se da ninguna proporción.

| Clase | Cuántas | Qué son |
|---|---|---|
| **Falsas hoy** | **6** | dicen algo que ya no es cierto. Dos están en el primer párrafo de su capítulo |
| **Incompletas o excesivas** | **10** | la cifra es correcta y lo que se afirma con ella va más allá, o le falta una salvedad |
| **Ausentes** | **6** | contenido que los capítulos no contemplan y que hace falta |

**Lo tranquilizador, y conviene decirlo primero:** ninguna cifra de los dos capítulos resulta
incorrecta. Las tablas 5.1 a 5.8 siguen diciendo lo que midieron sus registros. Lo que cambia es
**lo que se puede afirmar con ellas** y, en seis casos, una afirmación de estado que el tiempo ha
dejado atrás.

**Lo que no es tranquilizador:** tres afirmaciones del capítulo 5 y tres del 6 son **falsas hoy**, y
una de cada capítulo aparece en su primer párrafo, que es lo primero que un tribunal lee.

## 2. Las seis que son falsas hoy — **CORREGIDAS el 13-10-2026**

> **Estado.** Las seis se corrigieron el mismo día, en dos pasos: la propuesta con las cinco
> columnas exigidas está en [`correccion-cap5-cap6-paso-a.md`](correccion-cap5-cap6-paso-a.md) y la
> aplicación conserva en cada caso lo que el capítulo decía, dentro de una nota fechada. Ninguna
> cifra se modificó. `tests/test_memoria_afirmaciones.py` comprueba que ninguna de las seis frases
> vuelva al texto como afirmación.

Estas no admiten matiz: dicen algo que ya no es cierto.

| # | Dónde | Qué dice | Por qué es falso | Evidencia |
|---|---|---|---|---|
| **F-1** | cap. 5, párrafo 2 | «el conjunto de prueba **permanece cerrado y no se ha consultado**» | se abrió **cinco veces**: tres intentos de E19, la comprobación P3 y una accidental. En cuatro hubo exposición de etiquetas y de predicciones | `docs/methodology/registro-aperturas-test.md`, cinco niveles de apertura |
| **F-2** | cap. 6, párrafo 1 | «la evaluación final sobre el conjunto de prueba, **que sigue cerrado**» | ídem | ídem |
| **F-3** | cap. 6, OE2 | «el conjunto de prueba **está cerrado por construcción**» | el cierre **técnico** sigue en el código —`allow_test=True` más razón escrita— y eso es cierto; que el conjunto esté cerrado, no | `src/mecanico_ia_exp/data/dataset.py:77` y el registro de aperturas |
| **F-4** | cap. 5, §PI.3/PI.4 | «**la condición con distractor y filtro no añade** en ninguno de los tres fallos un distractor que la parcial no tuviera» y su causa atribuida al filtro de motor | la causa **no era el filtro**: `C12` y `C16` tenían **exactamente la misma configuración** que `C11` y `C15`, y el único campo que difería no lo lee el recorrido de suficiencia | `docs/methodology/protocolo-distractor-v2.md` §1 |
| **F-5** | cap. 6, obj. general | «el rediseño de la condición con distractor **queda como trabajo posterior**; mientras no se haga, **PI.4 seguirá sin poder interpretarse**» | **se hizo el 13-10-2026.** 6/6 abstenciones, las seis por insuficiencia de la evidencia y ninguna por confianza baja | `docs/experiments/P1_distractor_v2.md` |
| **F-6** | cap. 5, párrafo 1 y cap. 6, párrafo 1 | «Son resultados parciales: **la evaluación final sobre el conjunto de prueba queda pendiente**» | E19 se ejecutó el 12-10-2026 y está medida | `e19-medido`, `experiments/E19_evaluacion_final_v3.json` |

## 3. Las que no son falsas pero prometen más de lo que la evidencia sostiene

| # | Dónde | Qué dice | Qué hay que añadir o acotar | Evidencia |
|---|---|---|---|---|
| **A-1** | cap. 5, Tabla 5.7 y su discusión | «el conjunto con que se ajustaron los adaptadores no registró las ventanas de origen, pero los valores permiten identificarlas: **las dos primeras sirven a diez de las diecisiete ejecuciones**» | la cifra medida es **11 de 17**, no 10, y el mecanismo es más simple y peor de lo que el párrafo sugiere: los ejemplos se generaban **desde la partición de validación**, que es donde se mide al redactor. No hace falta identificar ventanas por sus valores: están en el fichero de ejemplos | `docs/methodology/auditoria-contaminacion-adaptador.md` §2 |
| **A-2** | cap. 5, Tabla 5.7, fila del adaptador v2 | «17/17 válidas · 17/17 respeta el veredicto · 0 citas inexistentes» | las cifras **no cambian**, y hay que añadir que **3 de esas 17 salidas contienen una cifra que el verificador no produjo**, dos de ellas en una frase internamente falsa. Las tres barreras las dejan pasar | `L-26`, `scripts/auditar_cifras_redactadas.py` |
| **A-3** | cap. 5, §PI.1, y cap. 6, OE3 | «Con un conjunto tres veces mayor… el orden se invierte por un margen de 0,012… **la desventaja del modelo temporal se atribuye al volumen de datos**» | el conjunto tres veces mayor es `synthetic_v3`, que es **pre-calibración**: la comparación cruza dos generadores distintos y la atribución al volumen está **confundida**. Ya estaba detectado; sigue en el texto | `docs/auditoria-pi1-contexto-temporal.md`, `L-25` |
| **A-4** | cap. 6, OE2 | «el entorno experimental reproducible **se cumplió parcialmente**… el generador es determinista» | cierto, y con un límite que falta: **`synthetic_v3` no es reconstruible** con el generador publicado, y de él salen E6, E7 y la evaluación final. Medido: 0 de 216 sesiones idénticas. Lo que agrava el caso es que el ventanado y el reparto **sí** reproducen, de modo que una reconstrucción ingenua pasa las pruebas midiendo otras señales | `L-25`, `configs/datos_no_reconstruibles.json` |
| **A-5** | cap. 6, OE4 | «El modelo de lenguaje **no cita nada que no se le haya entregado**» | cierto y **incompleto**: no cita identificadores que no recibió, **y puede escribir un número que nadie le dio**. La trazabilidad verificada cubre las citas, no las cifras | `L-26` |
| **A-6** | cap. 6, limitaciones, párrafo del índice documental | «el adaptador sigue entrenado sobre ejemplos generados antes de la corrección… **y no se ha reentrenado**» | hay que añadir **por qué** sigue sin reentrenarse: el reentrenamiento se diseñó, se preparó, se congeló y **se detuvo cuatro veces por memoria insuficiente**, con la causa medida —25,4 GB de huella física en una máquina de 24, el 97 % en el asignador de Metal— | `docs/experiments/incidencia-p2-02.md` |
| **A-7** | cap. 5, Tabla 5.5, filas `C12`, `C13`, `C16`, `C17` | las filas se publican con sus decisiones | las de `C12` y `C16` **no son condiciones independientes**: su configuración era idéntica a la parcial. La nota al pie ya las separa del recuento; lo que hay que corregir es **la razón** que da, que culpa al filtro de motor | `protocolo-distractor-v2.md` §1 |
| **A-8** | cap. 5, §PI.3/PI.4, y cap. 6, OE5 | «la protección procede en dos fallos de la aplicabilidad y en el tercero del vocabulario de la señal» | P1 añade una medición **más fuerte** y conviene incorporarla: con el distractor clasificado **`EXACT_MATCH`** —del motor correcto y con el código del fallo—, el filtro y el validador de aplicabilidad **no actúan**, y lo que rechaza es la **verificación de soporte**. 1 de 5, 3 de 7 y 1 de 6 documentos aplicables eran distractores | `P1_distractor_v2.md` §3 |
| **A-9** | cap. 5, §PI.2, trazabilidad | «las 51 afirmaciones conservan la observación que las origina… la proporción de afirmaciones con cita cuya cita las sostiene es de 12 sobre 12, **pero esa igualdad es una propiedad del procedimiento y no una medición**» | el párrafo es correcto y prudente. Lo que hay que añadir: `L-26` muestra que la propiedad se refiere a **identificadores**; el texto redactado puede contener una cifra falsa sin que ninguna comprobación lo note | `L-26` |
| **A-10** | cap. 6, limitaciones | «El criterio de suficiencia se revisó dos veces sobre los mismos casos…» | correcto. Falta la contaminación análoga del **redactor**, que es de otra clase: no es que el criterio se ajustara sobre los casos, es que el adaptador **se entrenó con las ventanas en que se le midió** | `L-23` |

## 4. Lo que hay que **añadir** porque no existe en el texto

No es corrección: es contenido nuevo que los capítulos no contemplan.

| # | Qué añadir | Dónde | Por qué |
|---|---|---|---|
| **N-1** | **El resultado de E19** y sus cifras | cap. 5, apartado nuevo; cap. 6, en los objetivos y en el general | es la evaluación final y el texto la da por pendiente |
| **N-2** | **La distinción `fault_active` / `fault_expressed`** y su efecto en la lectura de los errores | cap. 5, §PI.1, junto al análisis descriptivo; cap. 6, limitaciones | una condición puede estar asignada a una sesión **sin alteración observable** en todas sus ventanas. Medido el 12-10-2026 sobre sesiones generadas para esa medición: en el termostato con régimen de calentamiento, **32 de 45 ventanas etiquetadas con el fallo no contienen ninguna señal observable de él**, y el fallo de encendido **no expresa por completo ninguna** de sus 45 (`docs/methodology/expresion-efectiva-del-fallo.md` §4). Eso cambia cómo se leen los falsos negativos del termostato y del encendido, que el capítulo atribuye hoy a un «límite físico de detección» sin cuantificarlo |
| **N-3** | **El resultado de P1** | cap. 5, §PI.4; cap. 6, OE5 y general | PI.4 pasa de «sin respuesta interpretable» a tener una medición con `n = 3` |
| **N-4** | **La contribución metodológica complementaria**, si el autor la acepta | cap. 6, contribuciones | con el enunciado acotado de `contribucion-metodologica-congelacion.md` §10.2 y sus dos tablas de evidencia juntas |
| **N-5** | **El conjunto de evaluación independiente del redactor**, congelado y sin ejecutar | cap. 6, prospectiva | está decidido cómo se medirá, y decirlo vale aunque no se haya medido |
| **N-6** | **Las cinco aperturas y sus niveles** | cap. 5, nota metodológica; cap. 6, limitaciones | sustituye a F-1, F-2 y F-3, y es lo que el tribunal preguntará |

## 5. Qué NO hay que tocar

Para que la corrección no se desborde, conviene fijar también el límite.

| Qué | Por qué no se toca |
|---|---|
| Las tablas 5.1 a 5.8 | ninguna cifra es incorrecta. Cada una dice lo que midió su registro, y los registros no han cambiado |
| Las conclusiones de los objetivos OE1 a OE5 | su **sentido** no cambia con ninguno de los hallazgos. Cambian las salvedades, no los veredictos |
| La calificación «parcialmente sostenida» de la pregunta | sigue siendo la que la evidencia permite. P1 la refuerza en PI.4 y `L-26` la debilita en PI.2: no hay razón para moverla en ninguna dirección |
| El capítulo 3 y el capítulo 4 | ningún hallazgo del 12 y 13 de octubre los toca |
| La prospectiva | se amplía con N-5, no se reescribe |

## 6. Orden recomendado, y qué decide el autor

1. **Primero las seis falsas** (F-1…F-6). Son afirmaciones de estado, la corrección es de hecho y no de interpretación, y dos están en el primer párrafo de su capítulo.
2. **Después N-1**, el resultado de E19, porque F-6 lo exige: no se puede decir que la evaluación final está hecha sin decir qué midió.
3. **Después A-1, A-2, A-6 y A-10**, el bloque de la contaminación del redactor, que son cuatro párrafos del mismo asunto en dos capítulos.
4. **Después A-3 y A-4**, el bloque de `synthetic_v3`.
5. **Después N-3 y A-7, A-8**, el bloque del distractor.
6. **Después A-5, A-9 y N-2**, el bloque de la trazabilidad y la expresión del fallo.
7. **Al final N-4 y N-5**, que son decisiones del autor y no correcciones.

**Lo que decide el autor y este documento no:** si la contribución metodológica entra (N-4); cómo se redacta la nota de las aperturas (N-6), que admite una versión breve en el capítulo 5 y otra desarrollada en el 6; y si la distinción `fault_expressed` entra en el capítulo 5 como parte del análisis descriptivo o solo en limitaciones (N-2).

**Lo que este documento no hace, por instrucción:** no reescribe conclusiones, no modifica cifras, no retira resultados y no toca los dos capítulos.
