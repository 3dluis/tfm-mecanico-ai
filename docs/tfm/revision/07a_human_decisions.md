# 07a · Decisiones humanas

**Fecha:** 3 de septiembre de 2026 · **Ninguna decisión está tomada.** Este documento las
enuncia, ofrece opciones, propone una recomendación razonada y declara su impacto. La
recomendación no es una decisión: el autor decide, y donde se indica, con el director.

**Clasificación:**

- `PUEDE_DECIDIRSE_AHORA` — depende solo de evidencia ya disponible.
- `DEBE_DECIDIR_EL_INVESTIGADOR` — decisión científica del autor; no requiere al director.
- `DEBE_VALIDARSE_CON_TUTOR` — afecta a lo aprobado, a la normativa o al alcance
  comprometido; no puede resolverse sin el director.

---

| ID | Decisión | Opciones | Recomendación | Impacto | ¿Necesita tutor? |
|---|---|---|---|---|---|
| **D-01** | **Extensión y formato del TFM.** Tres cifras oficiales incompatibles: 50 000–60 000 palabras (nota al pie de la plantilla), 31–73 páginas (recomendaciones por capítulo) y mínimo 60 páginas sin anexos (sesión informativa del curso, con «no apto» aparejado). Hoy: 12 550 palabras ≈ 31 páginas | (a) Regirse por el mínimo de 60 páginas del curso vigente; (b) regirse por las 50 000 palabras de la plantilla; (c) pedir al director que fije la cifra por escrito | **(c), y mientras tanto planificar contra (a).** La proyección honesta con el contenido que falta da 60–78 páginas, que cumple (a) sin relleno. Alcanzar (b) exigiría duplicar el contenido y no hay materia para hacerlo sin rellenar | Condiciona el cronograma completo y el plan de redacción del grupo 5 | **Sí** · `DEBE_VALIDARSE_CON_TUTOR` |
| **D-02** | **Ejecución canónica de E5, E6, E7 y E12.** Los informes publican ejecuciones anteriores a la recalibración del generador; los registros vigentes dan otras cifras | (a) Declarar canónicos los registros vigentes y regenerar informes y capítulos; (b) restaurar las ejecuciones antiguas bajo identificador propio y citarlas; (c) mezcla: vigentes para E6, E7 y E12; restaurar E5 | **(a).** Es la única que deja el documento verificable contra el árbol. Las lecturas cualitativas se mantienen en los cuatro casos; cambian magnitudes | Desbloquea P-01 y P-04. Cambia cifras publicadas en `cap4`, `cap5`, la matriz y tres informes de fase | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-03** | **Estatuto del oráculo del código de avería.** La consulta de recuperación y la verificación de soporte consumen la etiqueta anotada | (a) Conservarlo y etiquetarlo como cota superior asistida por oráculo; (b) sustituirlo por la predicción del modelo y reejecutar E12; (c) ambas: conservar la cota y añadir la medición no oracular | **(c) si hay tiempo, (a) si no.** El experimento actual mide algo real y valioso sobre el mecanismo de recuperación; lo que no puede es presentarse como rendimiento extremo a extremo. La versión no oracular comparte implementación con D-08 | Sin (a) al menos, el claim de recuperación de PI.2 no se sostiene como está escrito | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-04** | **Alcance de PI.3 y PI.4.** Las cuatro condiciones se evalúan sobre un solo fallo | (a) Acotar las conclusiones al caso evaluado; (b) ampliar el conjunto anotado a tres fallos más con las cuatro condiciones y dos ventanas por fallo; (c) acotar ahora y ampliar si el calendario lo permite | **(c).** Acotar es barato y honesto, y deja el documento defendible desde hoy; ampliar después solo mejora. Ampliar sin acotar deja la afirmación descubierta mientras tanto | Es la corrección de mayor efecto en defensa y la más barata en su versión (a) | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-05** | **Umbral de suficiencia.** No hay registro del barrido ni criterio fechado | (a) Declararlo definido heurísticamente y retirar «calibrados, no elegidos»; (b) registrar el barrido como artefacto con criterio fechado y mantener la palabra; (c) declararlo elección de política del sistema | **(a) ahora, (b) si se quiere sostener la palabra.** Está verificado que las nueve decisiones son idénticas para cualquier umbral en (0,5999, 0,9078]: el resultado no depende del umbral, solo la frase | Afecta a una frase de `cap5` y al informe de la fase. Ningún resultado cambia | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-06** | **Objetivos, título y Anexo A.** Los objetivos del capítulo 2 están reformulados frente a los aprobados en julio; tres marcadores de consenso abiertos; el título registrado ya no describe el alcance | (a) Llevar al director la reformulación y el título nuevo; (b) mantener los aprobados y declarar la desviación; (c) mantener los aprobados en el cuerpo y la reformulación en anexo | **(a).** El propio proyecto ya redactó las tres opciones de reformulación con su coste; la normativa prevé expresamente que el título se consense tras la primera reunión | Bloquea el gate de objetivos y el capítulo 2. Es lo único que impide cerrar la coherencia entre pregunta, objetivos y conclusiones | **Sí** · `DEBE_VALIDARSE_CON_TUTOR` |
| **D-07** | **Bibliografía: versión de las normas y metadatos.** La plantilla dice 6.ª edición; la sesión informativa menciona otro estilo. Dos referencias del vacío con metadatos incompletos y una no localizada | (a) 6.ª edición, completar las dos, consultar las actas de la tercera o retirarla; (b) 7.ª edición si el director lo indica, lo que además resuelve un hallazgo menor; (c) preguntar y avanzar con (a) | **(c).** Los metadatos se completan igual en ambos casos; la versión solo cambia el formato y un hallazgo | Afecta al gate de referencias, que la normativa vincula al «no apto» | **Sí** para la versión · `PUEDE_DECIDIRSE_AHORA` para los metadatos |
| **D-08** | **Escenario adverso: diagnóstico incorrecto.** Hoy solo se evalúan ventanas bien clasificadas | (a) Declarar la condición como limitación y no ejecutar; (b) ejecutar el experimento adverso con criterio de éxito fijado antes; (c) declarar ahora y ejecutar en la evaluación final | **(c).** Es el experimento que un tribunal pedirá y el que hace falsable la parte más difícil de la pregunta. Comparte implementación con D-03(b). Riesgo declarado: es plausible que el sistema falle, y eso sería un resultado publicable | Alto valor científico. Sin él, toda conclusión queda condicionada a un diagnóstico correcto | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-09** | **La métrica de distancia entre completitud y soporte.** Es invariante por construcción | (a) Retirarla de resultados y declararla propiedad del diseño; (b) añadir un brazo en que el modelo genere sus propias citas, para que la distancia pueda ser distinta de cero; (c) implementar M4 y ejecutar la fase de trazabilidad pendiente | **(a) ahora, (b) como trabajo futuro.** (b) es un experimento nuevo de valor alto: mediría lo que la métrica pretende medir. (c) sin (b) volvería a dar cero | Afecta a cómo se presenta PI.2, no a que la trazabilidad funcione | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-10** | **Procedencia del corpus.** El enlace de origen apunta al portal oficial del fabricante, que no es el canal por el que se adquirió el ejemplar | (a) Corregir el enlace para que describa el canal real y mover el portal a un campo de editor; (b) readquirir el manual por el canal oficial antes del depósito y actualizar la huella; (c) (a) ahora y (b) si es viable | **(c).** (a) es obligatorio y cuesta minutos; (b) mejora la posición pero depende de disponibilidad y de coste | Afecta a la cadena de procedencia de toda cita y a la limitación correspondiente | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-11** | **Métricas de rendimiento y pre-registro.** El grupo de métricas de coste no tiene subpregunta asignada; el pre-registro del marco vigente no está congelado | (a) Declarar el grupo descriptivo y congelar el pre-registro antes de la evaluación final; (b) convertir el coste en criterio con umbral; (c) dejar ambos abiertos | **(a).** Convertir el coste en criterio exigiría medir sobre la plataforma que el trabajo ya declaró fuera de alcance. Congelar el pre-registro antes de abrir el test es lo que separa una predicción de una descripción | Afecta al gate de metodología y a la credibilidad de la evaluación final | No · `DEBE_DECIDIR_EL_INVESTIGADOR` |
| **D-12** | **Convocatoria y declaración del uso de herramientas de asistencia automatizada.** El primer informe de seguimiento vence el 18 o el 30 de septiembre; el proyecto registra por escrito las herramientas empleadas | (a) Declararlo en la memoria en el apartado que el director indique; (b) preguntar primero si la titulación lo exige y en qué forma; (c) no declararlo | **(b) y después (a).** La política de la titulación no consta en los documentos disponibles y no se inventa. Si existe obligación, se cumple; si no existe, declararlo sigue siendo defendible y coherente con el resto del trabajo. **(c) no se recomienda** | Afecta al depósito y a la integridad académica | **Sí** · `DEBE_VALIDARSE_CON_TUTOR` |

---

## Resumen por clasificación

| Clasificación | Decisiones |
|---|---|
| `PUEDE_DECIDIRSE_AHORA` | D-07 (parte de metadatos) |
| `DEBE_DECIDIR_EL_INVESTIGADOR` | D-02, D-03, D-04, D-05, D-08, D-09, D-10, D-11 |
| `DEBE_VALIDARSE_CON_TUTOR` | D-01, D-06, D-07 (versión de normas), D-12 |

## Lo que puede avanzar sin esperar al director

Ocho decisiones son del investigador y no dependen del tutor. Con ellas se puede ejecutar
íntegro el **grupo 1** (integridad del instrumento) y buena parte de los grupos 2 y 3. Lo que
queda condicionado a la reunión con el director es la extensión (D-01), los objetivos y el
título (D-06), la versión de las normas de cita (D-07) y la declaración de uso de herramientas
(D-12); ninguna de esas cuatro bloquea las correcciones técnicas.

**La pregunta de investigación no está en esta tabla y no se toca.** Permanece bloqueada.
