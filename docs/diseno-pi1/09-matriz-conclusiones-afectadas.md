# 9. Matriz de conclusiones afectadas (Fase H)

**No se modifica el capítulo 5 todavía.** Esta matriz dice qué habría que cambiar y con qué evidencia,
para que el autor decida.

## 9.1 Capítulo 5

| # | Afirmación | Dónde | Estado | Qué hacer |
|---|---|---|---|---|
| 1 | Dos de los cinco fallos no son visibles en las medias; el termostato tiene un límite físico de detección mientras el motor no habría superado la temperatura del techo | `cap5:13` | **Válida** | Nada. El análisis por fallo la reforzará con un artefacto que entonces no existía |
| 2 | Tabla comparativa de los dos modelos con sus cifras de `synthetic_v2` | `cap5:27` | **Válida** | Nada: cita el registro vigente, no el informe obsoleto |
| 3 | «El modelo temporal no supera al tabular… por clase acierta dos ventanas más en el termostato bloqueado, 11 de 14 frente a 9 de 14, sobre dos sesiones y una sola semilla» | `cap5:33` | **Válida con matiz** | Añadir que las catorce ventanas proceden de **dos sesiones** y se solapan a mitad, de modo que no son catorce observaciones; y que no está comprobado si las dos de ventaja contienen señal del fallo |
| 4 | «Con un conjunto tres veces mayor… el orden se invierte… de modo que la desventaja del modelo temporal se atribuye al volumen de datos y no se toma como resultado sobre la arquitectura» | `cap5:33` | **Invalidada** | La comparación cambia volumen **y** calibración del generador. Retirar la atribución al volumen o condicionarla explícitamente, y remitir a la curva de `04-subconjuntos-anidados.md` como la vía para responderlo |
| 5 | «Todos los errores del bosque van a la condición sin fallo: el modelo no produce diagnósticos cruzados» | `cap5:33` | **Válida, y acotada donde está** | Está correctamente limitada al bosque sobre el conjunto oficial. Añadir, al lado, que el modelo secuencial **sí** produce diagnósticos cruzados en los dos conjuntos y el bosque sobre `v3` produce siete falsas alarmas |
| 6 | El fallo de encendido se detecta en 7 de 14 ventanas, anticipado por escrito y sin aumentar la severidad | `cap5:35` | **Válida** | Nada |
| 7 | La atribución se comporta de forma desigual y en el encendido mezcla señales no declaradas | `cap5:50` | **Válida** | Nada |
| 8 | «PI.1 queda sostenida en su forma actual y no en la original… la formulación original pedía que un modelo temporal superase a la línea base… y eso no ocurrió» | `cap5:249` | **Válida** | Nada. Es exactamente la redacción que la evidencia sostiene |
| 9 | Resultados de suficiencia, trazabilidad y redacción sobre validación | `cap5` §§ siguientes | **Válidas**, y ahora acompañadas de las de prueba | Incorporar E19 **cuando el autor lo autorice**, separando primario de descriptivos |

## 9.2 Capítulo 6

| # | Afirmación | Dónde | Estado | Qué hacer |
|---|---|---|---|---|
| 10 | «Con este volumen de datos el modelo temporal no aportó ventaja sobre el tabular, y la formulación original de la subpregunta, que la pedía, no se cumplió» | `cap6:11` | **Válida con matiz** | «Con este volumen» sugiere que con más volumen sí: eso es lo que la evidencia no sostiene. Reformular como «en las condiciones evaluadas» |
| 11 | «Falta la evaluación sobre el conjunto de prueba» | `cap6:11` | **Obsoleta** | Ya existe. Actualizar cuando se incorpore E19 |

## 9.3 Otros documentos

| Documento | Estado | Qué hacer |
|---|---|---|
| `docs/experiments/E7_modelo_temporal.md` | cifras obsoletas y dos conclusiones sobre el volumen | Fase A |
| `docs/experiment-index.md`, fila E2 | procedencia de `v3` incorrecta | Fase A |
| `research/traceability-matrix.md` | conserva el enunciado original de PI.1 | Fase A, `TRAZ-PI1-01` |
| `docs/matriz_validacion_pi.md` | dos cifras del termostato sin registro | Fase A y paso 4 de la Fase G |
| `docs/limitations.md` | no declara la asimetría de selección, la ausencia de réplicas ni el confusor | Añadir las tres |
| `JURY_GUIDE.md` | no señala dónde se lee este resultado negativo | Añadir, porque es uno de los más defendibles del trabajo |

## 9.4 Lo que necesita evidencia nueva antes de poder afirmarse

1. Si el volumen limitaba la comparación. **Vía:** curva de `T6` a `T22` con validación fija.
2. Si el contexto temporal aporta en el termostato. **Vía:** análisis por expresión del fallo.
3. Si la ventaja del modelo secuencial sobrevive a la simetría de protocolo y al cambio de semilla.
   **Vía:** protocolo simétrico y cinco réplicas apareadas.
4. Cuánto aporta la dinámica dentro de la ventana frente al nivel. **Vía:** `A` frente a `B`, el único
   eslabón que aísla la representación.
