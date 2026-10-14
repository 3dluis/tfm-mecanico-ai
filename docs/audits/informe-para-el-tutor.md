# Estado del TFM — informe breve para la revisión del director

**Fecha:** 14 de octubre de 2026 · **Documento que acompaña:** `entregables/memoria.docx` y
`entregables/memoria.pdf`, **133 páginas**, generados desde el mismo commit, que el propio documento
imprime en su segunda página · **Estado: BORRADOR PARA REVISIÓN**

## Dónde está el trabajo

La memoria responde a la pregunta acotada que `ADR-004` fijó como canónica el 12 de septiembre:
si un agente con recuperación aumentada puede explicar un diagnóstico vehicular obtenido de datos
OBD-II, rastrear cada afirmación hasta su evidencia, y reconocer cuándo esa evidencia no basta.

Los veinte experimentos del plan están ejecutados salvo uno. La evaluación final sobre el conjunto
de prueba se midió el 12 de octubre y sus cifras están incorporadas. Los capítulos 1 a 6 están
escritos, con dieciséis figuras y treinta y siete tablas, y tres anexos.

## Los resultados principales, en cinco líneas

1. **El diagnóstico funciona en las condiciones evaluadas**: exactitud 0,878 frente a 0,286 de la
   referencia mínima, con la confianza calibrada. El modelo temporal no superó al tabular.
2. **Tener documentación aplicable no equivale a tener soporte.** Con cinco, seis y siete fragmentos
   del vehículo y del código correctos delante, la cobertura de afirmaciones es cero.
3. **El sistema se abstiene cuando debe**: sobre el conjunto de prueba, ninguna de las catorce
   ejecuciones que debían terminar en abstención terminó en explicación, y dos de las ocho que
   debían explicar se abstuvieron.
4. **Lo que sostiene ese comportamiento es el criterio de suficiencia, no la explicabilidad**: las
   ablaciones muestran que retirar la atribución no cambia ninguna decisión, y que sustituir el
   criterio por una puerta de confianza lleva la falsa confianza de cero a nueve sobre nueve.
5. **Una decisión correcta no garantiza una explicación correcta**: siete de las treinta y cinco
   salidas del modelo de lenguaje contienen una cifra que el verificador no produjo, sin que ninguna
   de las dos tasas cambie.

## Las limitaciones que condicionan todo lo anterior

Un vehículo, telemetría sintética y un catálogo cerrado de cinco fallos. Pocas unidades
independientes: entre tres y ocho ventanas según la métrica, de modo que el intervalo del cero de
falsa confianza llega al 21,5 %. El criterio se revisó dos veces sobre los mismos casos con que se
mide, y el modelo de lenguaje se ajustó con ventanas que incluyen las de tres de los casos
evaluados. Dos de los tres conjuntos sintéticos no se reconstruyen con el generador publicado; el
que sostiene las cifras publicadas sí, bit a bit.

## Lo que está pendiente de su orientación

| | Qué | Por qué no lo decido yo |
|---|---|---|
| **1** | **La extensión aplicable**. Los documentos oficiales dan tres cifras incompatibles | ninguno deroga a los otros |
| **2** | **El título**. El registrado promete mantenimiento predictivo, que el trabajo no hace | la sesión informativa pide consensuarlo |
| **3** | **El alcance**. La pregunta se acotó en septiembre; dos capacidades quedaron como líneas futuras | confirmar que la memoria se sostenga sobre esa versión, o completar alguna |

## Lo que está pendiente y no depende de usted

El reentrenamiento del adaptador del modelo de lenguaje está detenido por memoria insuficiente:
necesita más de 17 GB por paso y la máquina disponible tiene 24 en total. Está declarado como
limitación y no impide cerrar la memoria. El nombre del director y la fecha de convocatoria faltan
en la portada, y el documento los muestra a la vista a propósito.

## Cómo comprobar lo que el documento afirma

El repositorio acompaña a la memoria. Cinco órdenes desde un clon reconstruyen el conjunto de datos
y ejecutan las pruebas; siete notebooks con su versión en HTML permiten leer los experimentos sin
instalar nada; y cada cifra de los capítulos cita el registro del que sale. El anexo C lo detalla, y
declara también lo que no se puede reproducir y por qué.
