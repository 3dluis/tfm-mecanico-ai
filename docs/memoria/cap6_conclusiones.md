# Capítulo 6: Conclusiones

> Estado: **limitaciones y prospectiva redactadas**; las conclusiones y las consideraciones
> finales dependen de E19 y se dejan como borrador condicionado. Fuente de las limitaciones:
> `research/limitations-register.md`, 17 entradas, todas procedentes de un informe de fase o
> un documento de método.

## Conclusiones sobre la pregunta de investigación

`[Borrador sobre datos sintéticos (dataset_type: synthetic); se reescribe con E19.]`

La pregunta preguntaba si un agente con recuperación aumentada puede explicar un diagnóstico
rastreando cada afirmación hasta su evidencia y abstenerse cuando la evidencia no basta. La
respuesta que este trabajo puede dar hoy está acotada a la procedencia de sus datos y tiene
dos partes.

La primera es que **sí puede, cuando el agente está construido para que la decisión no
dependa del modelo de lenguaje**. La separación entre quien diagnostica, quien decide y quien
redacta no es un detalle de ingeniería: es lo que hace medible la pregunta. Con esa
separación, sobre el mismo caso y con todo idéntico salvo el índice, el agente explica cuando
la evidencia está, se abstiene cuando se retira, y se abstiene también cuando lo que queda es
parecido pero no sostiene lo afirmado. El modelo de lenguaje respeta la decisión en todos los
casos y no produce una sola cita inexistente, porque una barrera fuera de él lo impide.

La segunda es que **la respuesta vale para datos sintéticos calibrados contra la
documentación del vehículo y no está validada en un vehículo real**. La pregunta no exige
datos reales; exige declarar la procedencia, y esta memoria la declara en cada cifra. La
calibración documenta cada constante del generador con su página del manual; eso hace los
datos verosímiles en lo que el manual permite comprobar, y en nada más. Un tribunal, y el
propio autor, debe leer cada cifra del capítulo 5 con esa procedencia delante.

## Limitaciones

Se ordenan por severidad. Ninguna es ceremonial: cada una procede de un resultado, de un
documento de método o de una norma, y dice qué limita, a qué afecta y cómo se comprobaría.

**Crítica.**

- **Los datos sintéticos no tienen validez externa** (L-01). Todos los experimentos se han
  ejecutado sobre datos generados, y así se declara en cada cifra; la pregunta no exige datos
  reales, pero un resultado sobre sintéticos no demuestra comportamiento equivalente en un
  vehículo real. Afecta sobre todo a PI.1 y, en cuanto a generalización, a las demás. Solo la
  validación externa con datos reales lo resolvería.

**Altas.**

- **Dos de los cinco fallos son invisibles en las medias** (L-02) y uno de ellos, el fallo de
  encendido, se detecta en la mitad de los casos (L-15). El resultado se anticipó por
  escrito y no se corrigió aumentando la severidad del fallo.
- **Las fichas de fallo del generador no tienen respaldo documental completo** (L-03): la
  calibración ancla las constantes al manual, pero el mecanismo de cada fallo es una
  simplificación declarada.
- **La atribución no es causalidad** (L-06). El sistema no lo afirma en ningún punto, y el
  esquema de salida rechaza afirmaciones causales; la limitación es de interpretación por
  parte del lector.
- **Se abandonó un pre-registro congelado** (L-07) al sustituir el marco experimental
  anterior por el canónico. El cambio está fechado y justificado, y el diseño anterior se
  conserva íntegro; los umbrales del marco vigente se fijaron sobre validación, pero el
  pre-registro formal del marco canónico no se ha congelado todavía.
- **El barrido bibliográfico no es un flujo PRISMA formal** (L-08): el acceso a dos bases
  estuvo parcialmente bloqueado y los recuentos por base están pendientes.
- **La novedad sobre la cuarta subpregunta es más estrecha de lo que parecía** (L-10): existe
  literatura sobre robustez de la recuperación a documentos irrelevantes; lo no encontrado es
  su medición sobre documentación técnica del mismo fabricante y otro motor.
- **El coste de cómputo se mide sobre un ordenador de sobremesa** (L-11), no sobre la
  plataforma embarcada que la propuesta inicial contemplaba.
- **El alcance ejecutado es más estrecho que el aprobado** (L-13): despliegue embarcado,
  aplicación móvil y plataforma en la nube han pasado a prospectiva. La constancia formal de
  esta acotación ante la dirección está pendiente.
- **La confianza del modelo estaba mal calibrada** (L-14), y aunque se corrigió, la
  corrección se ajustó sobre entrenamiento con validación cruzada y no se ha comprobado sobre
  test.

**Medias.**

- Una correlación marginal baja entre señal y fallo no implica ausencia de relación (L-05).
- Tres trabajos relevantes están pendientes de lectura a texto completo (L-09).
- No se ha medido la fiabilidad de un juez basado en modelo de lenguaje, y por eso ninguna
  métrica que responda a una subpregunta lo usa (L-12).
- El descriptor informado por la física, la compensación del caudalímetro en las
  correcciones de combustible, no está validado con datos reales (L-16).

**Bajas.**

- El reparto por régimen de conducción está desequilibrado (L-04).
- **Todas las cifras disponibles son de validación** (L-17); el test sigue cerrado y las
  cifras finales pueden diferir.

**Añadidas por la fase E13, pendientes de incorporar al registro.**

- Nueve casos anotados: una diferencia de una unidad no separa nada, y la lectura debe ser
  caso a caso.
- El ajuste del modelo de lenguaje recortó 28 de 55 prompts de entrenamiento por límite de
  memoria, y la validación del ajuste tiene siete ejemplos.
- La abstención por cobertura, que es la del experimento central, tiene un solo ejemplo
  entre 26 en los datos de ajuste; funciona porque el prompt contiene el motivo, no porque el
  modelo lo haya aprendido.
- Las plantillas de afirmación describen la dirección de la contribución y no el signo del
  valor, lo que produce frases correctas como atribución y confusas como lectura.
- Dos informes de fase dan cifras distintas de sus registros (E6 y E7); se citan los
  registros y la discrepancia está por explicar.

## Prospectiva

Lo primero, y lo que más ampliaría la validez de las conclusiones, es **incorporar datos
OBD-II reales** como validación externa, del vehículo de estudio o de uno cuya documentación de taller esté disponible
con el mismo nivel de detalle. El laboratorio está preparado para ello: el generador
sintético se sustituye por un cargador, el reparto por sesión y el estudio de ventana se
repiten, y todo lo demás, modelo, atribución, corpus, verificador y agente, se ejecuta sin
cambios. Las once referencias de la propuesta aprobada pendientes de incorporar incluyen dos
conjuntos de datos OBD-II candidatos.

Después, en el orden en que el plan las prevé: las **ablaciones** de E18, que atribuyen el
resultado a cada componente cambiando uno a la vez; la **evaluación final** de E19 con
apertura declarada del test y congelación previa del pre-registro del marco canónico; y la
**demostración** de E20, que escenifica el experimento central sobre un caso del dataset de evaluación final.

Tres líneas quedan fuera de este trabajo y se dejan enunciadas. El **despliegue en una
plataforma embarcada**, con la medición de M6 como criterio y no como descriptiva. La
**extensión a más vehículos**, donde el validador de aplicabilidad y las variantes de corpus
tendrían que probarse entre fabricantes y no solo entre motores. Y la **anotación de casos
con afirmaciones admisibles y evidencia mínima**, prevista en el diseño y no ejecutada, que
permitiría medir no solo si el agente cita bien sino si dice todo lo que la evidencia
permite decir y nada más.

## Consideraciones finales

`[Se redactan con E19. Borrador de la idea que deben transmitir:]`

Este trabajo empezó con una pregunta sobre modelos de lenguaje y terminó siendo, sobre todo,
un trabajo sobre evidencia: qué es tenerla, cómo se comprueba que una referencia la sostiene
y qué hace un sistema cuando no la tiene. La mayoría de los errores que el proyecto cometió y
corrigió fueron variantes de la misma confusión que estudia, tener una referencia sin tener
soporte, y se detectaron mirando cifras que no cuadraban. Si el sistema construido tiene un
mérito, es que esa confusión no puede producirse en silencio dentro de él: cada afirmación
lleva su observación y su página, cada cita se comprueba antes de escribirse, y cuando no hay
con qué sostener una explicación, el sistema lo dice.
