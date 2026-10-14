# Borrador de consulta al director

**Fecha:** 13 de octubre de 2026 · **Estado: BORRADOR. No se ha enviado.** Queda a la espera de la
aprobación del autor · **Qué consulta:** las tres cuestiones que no pueden resolverse sin el director: `D-01` extensión,
`D-06` título y si procede revisar `ADR-004`, que acotó la pregunta de investigación

---

**Asunto:** Memoria del TFM — tres consultas antes de pasarte la versión para revisión

Hola David:

Espero que estés bien. Estoy cerrando la versión de la memoria que me gustaría pasarte para que la
revises, y hay tres cosas que prefiero consultarte antes que decidir por mi cuenta.

La primera es la extensión. He encontrado indicaciones distintas en los documentos oficiales: la
plantilla lleva una nota al pie que habla de un mínimo de 50 000 palabras, mientras que las
recomendaciones de extensión por capítulo de esa misma plantilla suman entre 31 y 73 páginas, y la
sesión informativa del curso indica un mínimo orientativo de 60 páginas sin contar anexos. La
memoria está ahora en 105 páginas de capítulos, sin anexos ni bibliografía, con unas 39 000 palabras
en total. Cumple la cifra de la sesión informativa con margen, pero no llega a la de la nota al pie.
¿Cuál debería tomar como referencia? Lo pregunto porque alcanzar las 50 000 palabras supondría
añadir alrededor de un 30 % de texto, y con el trabajo experimental que hay hecho no veo cómo
hacerlo sin repetir explicaciones.

La segunda es el título. El registrado es «Sistema inteligente para el diagnóstico y mantenimiento
predictivo de vehículos», de la propuesta de julio. El alcance acabó siendo más estrecho: el trabajo
evalúa el diagnóstico a partir de datos OBD-II, la trazabilidad entre cada afirmación de la
explicación y la evidencia que la sostiene, y la decisión de abstenerse cuando esa evidencia no
basta. No hay mantenimiento predictivo: el sistema diagnostica una condición presente, no anticipa
fallos futuros. Me preocupa que el tribunal lea el título y espere algo que no va a encontrar. ¿Te
parece que lo mantenga como está registrado, o prefieres que lo ajustemos? Si lo segundo, te
propongo algo del estilo de «Diagnóstico vehicular explicable a partir de datos OBD-II: trazabilidad
de la evidencia y abstención ante evidencia insuficiente», aunque me adapto a lo que veas.

Y la tercera tiene que ver con el alcance, y va unida a la anterior. Al revisar la evidencia caso
por caso para cerrar la memoria he puesto por escrito qué capacidades llegamos a evaluar y cuáles
no. Dos de las que planteaba la formulación inicial de la pregunta —identificar fallos que el modelo
no tiene representados, e incorporar las hipótesis validadas como conocimiento que se reutilice
después— quedaron fuera en septiembre, cuando acotamos la pregunta precisamente porque no tenían
implementación ni fase en el plan. El trabajo está alineado con esa versión acotada y responde a
ella. Antes de darla por buena quería confirmarlo contigo: ¿te parece bien que la memoria se
sostenga sobre el alcance acotado, con esas dos capacidades como líneas futuras, o preferirías que
intentara completar alguna experimentalmente? Tengo el diseño de las dos preparado desde entonces;
la primera costaría alrededor de una semana de trabajo y la segunda bastante más, y las dos pueden
terminar sin resultado concluyente, así que no me parecía sensato empezarlas sin preguntártelo.

Te agradezco mucho la orientación de estos meses y el tiempo que le dedicas a revisar el trabajo; me
ha servido especialmente para ordenar la parte experimental y para decidir qué se podía afirmar con
lo que teníamos medido. En cuanto me confirmes estos puntos te paso la memoria completa.

Un saludo,
Luis Daniel Díaz

---

## Notas para el autor, que NO van en el correo

- **Longitud**: 480 palabras. Tres preguntas, cada una con el dato que necesita y nada más.
- **Lo que la tercera pregunta hace y conviene no deshacer al editarla.** Presenta el recorte como
  **una decisión ya tomada que se confirma**, no como un problema que se descubre ahora. Es lo que
  ocurrió: `ADR-004`, de 12 de septiembre, lo decidió la dirección por escrito. Plantearlo como un
  hallazgo nuevo daría a entender que el trabajo se ha quedado corto, y no es eso.
- **Lo que deliberadamente no dice**: que la rúbrica oficial no puntúa la extensión. Es un argumento
  fuerte y su sitio es la respuesta, no la pregunta. Tampoco dice que la alternativa B «ya está
  hecha», porque sonaría a que la consulta es retórica.
- **Lo que sí dice, y es deliberado**: que los dos diseños están preparados y cuánto costarían. Si
  David quiere completarlos, la conversación empieza con el coste encima de la mesa.
- **Si la respuesta llega**: anotarla con fecha en
  `.claude/skills/uax-tfm-ai-researcher/references/uax/conflictos-uax.md` y actualizar `D-01`,
  `D-06` y, si procede, abrir un `ADR-005`.
