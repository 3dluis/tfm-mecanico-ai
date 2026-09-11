# 16 · Capítulo 6 · contenido retirado para la primera entrega

El capítulo de conclusiones pasa a **conclusiones provisionales**. Sale de él todo lo que
adelanta resultados aún no consolidados y los códigos internos del registro de limitaciones.
Este documento **custodia literalmente** lo retirado, porque parte de ello no vive en ningún
otro punto de la memoria.

> **Aviso.** La línea base trivial y el análisis de la unidad de observación **solo existían en
> el capítulo 6**. Mientras el capítulo 5 siga congelado, desaparecen del cuerpo de la memoria.

## Lo que solo estaba aquí · debe volver con el capítulo 5

### La línea base trivial

> Una política que se abstuviera siempre, sin mirar nada, acertaría doce de esas diecisiete
> decisiones, y en las doce condiciones donde la evidencia no está completa acertaría las doce:
> exactamente las mismas que el sistema. Toda la ventaja del agente sobre esa política trivial
> está en los casos donde la evidencia sí está y hay que explicar. Dicho de otro modo,
> abstenerse bien no distingue a este sistema de uno que no mirara nada; lo que lo distingue es
> abstenerse bien **y además** explicar cuando debe, que es la mitad donde falla dos de cada
> cinco veces por confianza insuficiente del modelo especializado.

Es el hallazgo más severo del trabajo sobre sí mismo y no aparece en ningún otro capítulo.

### La unidad de observación

> Las diecisiete decisiones evaluadas proceden de **cinco ventanas de telemetría** sometidas a
> distintas variantes del corpus. No son diecisiete observaciones independientes, y ninguna
> cifra de este trabajo debería leerse como si lo fueran.

El **principio** permanece en el capítulo 4 y en la nueva sección 6.2; el **recuento** sale.

### La procedencia del resultado

> Las cifras proceden de una ejecución que la metodología etiqueta como cota superior asistida
> por oráculo, porque la selección de ventanas exige que el modelo especializado haya acertado.
> Y el criterio de suficiencia se corrigió dos veces sobre los mismos casos puntuados, después
> de observar sus fallos; las tres versiones y sus resultados se conservan, y esa secuencia
> forma parte del resultado tanto como su cifra final.

### El respeto al veredicto y las citas

> El modelo de lenguaje respeta la decisión en todas las ejecuciones cuya salida pudo evaluarse
> —nueve de nueve en la configuración desplegada, y siete de siete evaluables en las dos
> anteriores—, y no produce una sola cita inexistente, porque una barrera fuera de él lo impide.
>
> En las cuarenta y cinco ejecuciones del redactor sobre el motor de inferencia local —cinco
> configuraciones por nueve preguntas— no aparece una sola cita inexistente. Lo que **no** se ha
> calculado son las magnitudes agregadas de esa trazabilidad.

## Lo que sigue vivo en el registro interno

Las veintidós entradas `L-01` a `L-22` permanecen íntegras en `research/limitations-register.md`,
con sus campos de qué limita, por qué, evidencia, a qué afecta, consecuencia, cómo comprobarlo y
severidad. De ahí salen las seis limitaciones de alto nivel que la memoria presenta, y ahí
quedan los detalles que no van al cuerpo: los dos espacios vectoriales mezclados, el punto de
operación de 0,72 a 0,79, las trece de catorce abstenciones por cobertura, las dos ejecuciones
negativas sin reportar y las discrepancias entre informes de fase y registros.

## Versión anterior completa

Recuperable con `git show` sobre el commit anterior a esta revisión.
