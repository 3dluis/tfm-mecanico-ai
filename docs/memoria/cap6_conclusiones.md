# Capítulo 6: Conclusiones

## Conclusiones sobre la pregunta de investigación

`[Borrador sobre datos sintéticos (dataset_type: synthetic); se reescribe con E19.]`

La pregunta preguntaba si un agente con recuperación aumentada puede explicar un diagnóstico rastreando cada afirmación hasta su evidencia y abstenerse cuando la evidencia no basta. La respuesta que este trabajo puede dar hoy está acotada a la procedencia de sus datos y tiene dos partes.

La primera es que **sí puede, con un alcance que conviene delimitar antes de enunciarlo**. La separación entre quien diagnostica, quien decide y quien redacta no es un detalle de ingeniería: es lo que hace medible la pregunta. Con esa separación, sobre la misma ventana y con todo idéntico salvo el índice documental, el agente explica cuando la evidencia está y se abstiene cuando se retira. El modelo de lenguaje respeta la decisión en todas las ejecuciones cuya salida pudo evaluarse —nueve de nueve en la configuración desplegada, y siete de siete evaluables en las dos anteriores—, y no produce una sola cita inexistente, porque una barrera fuera de él lo impide.

Cuatro precisiones acompañan a esa afirmación, y sin ellas resultaría más fuerte de lo que la evidencia permite.

La primera es de **unidad**. Las diecisiete decisiones evaluadas proceden de **cinco ventanas de telemetría** sometidas a distintas variantes del corpus. No son diecisiete observaciones independientes, y ninguna cifra de este trabajo debería leerse como si lo fueran.

La segunda es de **comparación**. Una política que se abstuviera siempre, sin mirar nada, acertaría doce de esas diecisiete decisiones, y en las doce condiciones donde la evidencia no está completa acertaría las doce: exactamente las mismas que el sistema. Toda la ventaja del agente sobre esa política trivial está en los casos donde la evidencia sí está y hay que explicar. Dicho de otro modo, abstenerse bien no distingue a este sistema de uno que no mirara nada; lo que lo distingue es abstenerse bien **y además** explicar cuando debe, que es la mitad donde falla dos de cada cinco veces por confianza insuficiente del modelo especializado.

La tercera afecta a la **mitad de la pregunta que habla de trazabilidad**. Cada comprobación de soporte queda registrada por separado —qué afirmación, qué fragmento, si lo sostiene y por qué—, de modo que la cadena es auditable caso a caso, y en las cuarenta y cinco ejecuciones del redactor sobre el motor de inferencia local —cinco configuraciones por nueve preguntas— no aparece una sola cita inexistente. Lo que **no** se ha calculado son las magnitudes agregadas de esa trazabilidad: la proporción de afirmaciones con cita y la proporción cuya cita las sostiene existen como comprobaciones individuales en el registro, y no como cifra publicada. Mientras eso siga así, la trazabilidad se sostiene como propiedad verificable de cada caso, no como resultado agregado.

La cuarta es de **procedencia del resultado**. Las cifras proceden de una ejecución que la metodología etiqueta como cota superior asistida por oráculo, porque la selección de ventanas exige que el modelo especializado haya acertado. Y el criterio de suficiencia se corrigió dos veces sobre los mismos casos puntuados, después de observar sus fallos; las tres versiones y sus resultados se conservan, y esa secuencia forma parte del resultado tanto como su cifra final.

La segunda es que **la respuesta vale para datos sintéticos calibrados contra la documentación del vehículo y no está validada en un vehículo real**. La pregunta no exige datos reales; exige declarar la procedencia, y esta memoria la declara en cada cifra. La calibración documenta cada constante del generador con su página del manual; eso hace los datos verosímiles en lo que el manual permite comprobar, y en nada más. Un tribunal, y el propio autor, debe leer cada cifra del capítulo 5 con esa procedencia delante.

## Limitaciones

Se ordenan por severidad. Ninguna es ceremonial: cada una procede de un resultado, de un documento de método o de una norma, y dice qué limita, a qué afecta y cómo se comprobaría.

**Crítica.**

- **Los datos sintéticos no tienen validez externa** (L-01). Todos los experimentos se han ejecutado sobre datos generados, y así consta en cada cifra; la pregunta no exige datos reales, pero un resultado sobre sintéticos no demuestra comportamiento equivalente en un vehículo real. Afecta sobre todo a PI.1 y, en cuanto a generalización, a las demás. Solo la validación externa con datos reales lo resolvería.

**Altas.**

- **Dos de los cinco fallos son invisibles en las medias** (L-02) y uno de ellos, el fallo de encendido, se detecta en la mitad de los casos (L-15). El resultado se anticipó por escrito y no se corrigió aumentando la severidad del fallo.
- **Las fichas de fallo del generador no tienen respaldo documental completo** (L-03): la calibración ancla las constantes al manual, pero el mecanismo de cada fallo es una simplificación declarada.
- **Dos términos del objetivo general no están instrumentados** (L-21, L-22). El objetivo general compromete la identificación de patrones de fallo no representados en el conocimiento disponible y la incorporación de las hipótesis validadas como conocimiento reutilizable. El modelo de diagnóstico es un clasificador supervisado de conjunto cerrado, de modo que reconocer una clase aprendida no es identificar un patrón no representado; y ningún componente incorpora una hipótesis validada ni la recupera después. No son resultados negativos: son capacidades que el diseño no llegó a instrumentar, y el trabajo no puede por tanto afirmar ni negar nada sobre ellas. El ciclo que la pregunta define se cierra en su tramo central —contraste con evidencia y decisión entre explicar y abstenerse— y no de extremo a extremo.
- **Los resultados describen un solo vehículo** (L-19). Todo el trabajo se apoya en un Mazda 3 BK de 2007 con motor Z6 y en su manual de taller, elección justificada en el capítulo 4. Esa decisión garantiza por construcción la coherencia entre telemetría, códigos de avería y procedimientos documentales, que es exactamente lo que no puede darse por supuesto en otro vehículo: otro fabricante puede usar códigos distintos para la misma condición, estructurar sus procedimientos de otra forma o no publicar un manual accesible. Los resultados no se generalizan a otros modelos, a otras generaciones del mismo modelo ni a los otros dos motores documentados en el corpus, y comprobarlo exigiría repetir el trabajo sobre un vehículo con documentación equivalente.
- **Dos ejecuciones con resultado negativo no llegaron al capítulo de resultados** (L-18). El experimento de suficiencia se ejecutó también en una variante que retira el conocimiento de la etiqueta anotada y en un escenario adverso donde el modelo especializado se equivoca. La primera reproduce la ejecución de referencia decisión a decisión, lo que acota de dónde viene el auxilio del oráculo; la segunda contiene evidencia de comportamiento ante un diagnóstico incorrecto. Ambas están registradas en el repositorio y ninguna se reporta en el capítulo 5. Como el quinto objetivo se compromete expresamente a documentar los resultados negativos, la omisión se declara aquí y se corrige cuando ese capítulo deje de estar congelado.
- **Toda cifra de recuperación está pendiente de reejecución** (L-20). Se detectó que el índice documental contiene dos representaciones vectoriales de cada fragmento, procedentes de dos modelos distintos, y que ninguna búsqueda declaraba en cuál de los dos buscaba. Las consultas ordenaron por proximidad sobre dos espacios semánticos a la vez, y la procedencia de cada fragmento recuperado es indeterminada. El defecto está corregido en el código y la reejecución canónica sigue pendiente de sus auditorías. Afecta a las cuatro tablas del capítulo 5 que dependen de la recuperación, a los datos de ajuste del redactor y, por tanto, a lo que puede concluirse sobre las dos subpreguntas que exigen evidencia documental. Mientras esa reejecución no termine, las cifras de recuperación de esta memoria son **reproducibles pero no canónicas**.
- **La atribución no es causalidad** (L-06). El sistema no lo afirma en ningún punto, y el esquema de salida rechaza afirmaciones causales; la limitación es de interpretación por parte del lector.
- **Se abandonó un pre-registro congelado** (L-07) al sustituir el marco experimental anterior por el canónico. El cambio está fechado y justificado, y el diseño anterior se conserva íntegro; los umbrales del marco vigente se fijaron sobre validación, pero el pre-registro formal del marco canónico no se ha congelado todavía.
- **El barrido bibliográfico no es un flujo PRISMA formal** (L-08): el acceso a dos bases estuvo parcialmente bloqueado y los recuentos por base están pendientes.
- **La novedad sobre la cuarta subpregunta es más estrecha de lo que parecía** (L-10): existe literatura sobre robustez de la recuperación a documentos irrelevantes; lo no encontrado es su medición sobre documentación técnica del mismo fabricante y otro motor.
- **El coste de cómputo se mide sobre un ordenador de sobremesa** (L-11), no sobre la plataforma embarcada que la propuesta inicial contemplaba.
- **El alcance ejecutado es más estrecho que el aprobado** (L-13): despliegue embarcado, aplicación móvil y plataforma en la nube han pasado a prospectiva. La constancia formal de esta acotación ante la dirección está pendiente.
- **La confianza del modelo estaba mal calibrada** (L-14), y aunque se corrigió, la corrección se ajustó sobre entrenamiento con validación cruzada y no se ha comprobado sobre test.

**Medias.**

- Una correlación marginal baja entre señal y fallo no implica ausencia de relación (L-05).
- Tres trabajos relevantes están pendientes de lectura a texto completo (L-09).
- No se ha medido la fiabilidad de un juez basado en modelo de lenguaje, y por eso ninguna métrica que responda a una subpregunta lo usa (L-12).
- El descriptor informado por la física, la compensación del caudalímetro en las correcciones de combustible, no está validado con datos reales (L-16).

**Bajas.**

- El reparto por régimen de conducción está desequilibrado (L-04).
- **Todas las cifras disponibles son de validación** (L-17); el test sigue cerrado y las cifras finales pueden diferir.

**Añadidas por la fase E13, pendientes de incorporar al registro.**

- Nueve casos anotados: una diferencia de una unidad no separa nada, y la lectura debe ser caso a caso.
- El ajuste del modelo de lenguaje recortó 28 de 55 prompts de entrenamiento por límite de memoria, y la validación del ajuste tiene siete ejemplos.
- La abstención por cobertura, que es la del experimento central, tiene un solo ejemplo entre 26 en los datos de ajuste; funciona porque el prompt contiene el motivo, no porque el modelo lo haya aprendido.
- Las plantillas de afirmación describen la dirección de la contribución y no el signo del valor, lo que produce frases correctas como atribución y confusas como lectura.
- Dos informes de fase dan cifras distintas de sus registros (E6 y E7); se citan los registros y la discrepancia está por explicar.

## Prospectiva

Lo primero, y lo que más ampliaría la validez de las conclusiones, es **incorporar datos OBD-II reales** como validación externa, del vehículo de estudio o de uno cuya documentación de taller esté disponible con el mismo nivel de detalle. El laboratorio está preparado para ello: el generador sintético se sustituye por un cargador, el reparto por sesión y el estudio de ventana se repiten, y todo lo demás, modelo, atribución, corpus, verificador y agente, se ejecuta sin cambios. Las once referencias de la propuesta aprobada pendientes de incorporar incluyen dos conjuntos de datos OBD-II candidatos.

Después, en el orden en que el plan las prevé: las **ablaciones** de E18, que atribuyen el resultado a cada componente cambiando uno a la vez; la **evaluación final** de E19 con apertura declarada del test y congelación previa del pre-registro del marco canónico; y la **demostración** de E20, que escenifica el experimento central sobre un caso del dataset de evaluación final.

Tres líneas quedan fuera de este trabajo y se dejan enunciadas. El **despliegue en una plataforma embarcada**, con la medición de M6 como criterio y no como descriptiva. La **extensión a más vehículos**, donde el validador de aplicabilidad y las variantes de corpus tendrían que probarse entre fabricantes y no solo entre motores. Y la **anotación de casos con afirmaciones admisibles y evidencia mínima**, prevista en el diseño y no ejecutada, que permitiría medir no solo si el agente cita bien sino si dice todo lo que la evidencia permite decir y nada más.

## Consideraciones finales

`[Se redactan con E19. Borrador de la idea que deben transmitir:]`

Este trabajo empezó con una pregunta sobre modelos de lenguaje y terminó siendo, sobre todo, un trabajo sobre evidencia: qué es tenerla, cómo se comprueba que una referencia la sostiene y qué hace un sistema cuando no la tiene. La mayoría de los errores que el proyecto cometió y corrigió fueron variantes de la misma confusión que estudia, tener una referencia sin tener soporte, y se detectaron mirando cifras que no cuadraban. Si el sistema construido tiene un mérito, es que esa confusión no puede producirse en silencio dentro de él: cada afirmación lleva su observación y su página, cada cita se comprueba antes de escribirse, y cuando no hay con qué sostener una explicación, el sistema lo dice.
