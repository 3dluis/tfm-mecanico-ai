# 05 · Verificación de cuatro referencias contra fuente primaria

**Fecha:** 10 de septiembre de 2026 · **Origen:** cuarta petición del director, «verificar
personalmente 3-4 referencias al azar de tu bibliografía (accede a la fuente primaria y
confirma que dice lo que citas)».

## Procedimiento de selección, reproducible

Población: las **21 referencias citadas en el cuerpo** de la memoria, no la lista maestra
completa. Estratos por frente teórico, definidos por palabra clave del título. Semilla
**20260910**, la fecha del encargo. Selección sin reemplazo entre estratos, en orden fijo, de
modo que la muestra se reproduce ejecutando el mismo procedimiento.

La muestra **no es cómoda**: dos de las cuatro arrastraban metadatos incompletos marcados
`[VERIFY_SOURCE]`, y una resultó no sostener lo que se le atribuía.

## Resultados

| Ref | Afirmación en la memoria | Fuente primaria | Sección | Evidencia encontrada | Veredicto |
|---|---|---|---|---|---|
| **REF-049** Hossain et al. (2024) | «los conjuntos públicos de telemetría OBD-II con fallos etiquetados son escasos y, cuando existen, rara vez vienen acompañados de la documentación de taller del vehículo» — `cap3:64` | *Computer Modeling in Engineering & Sciences*, 141(2), 951–996. DOI 10.32604/cmes.2024.056022 | §1 y §5.2, «Insufficient Availability of Labeled Data» | «One of the limitations of using real-world data is the absence or incomplete nature of labeling, as annotating a vast quantity of data is a time-intensive task that necessitates specialized expertise» | **PARCIALMENTE SOPORTADA** |
| **REF-044** Haque, Zabin y Uddin (2025) | «Los valores de Shapley… **los** combinan con selección de descriptores y ensamblado para clasificar fallos en motores de vehículo eléctrico» — `cap3:118` | *Machines*, 13(4), 314. DOI 10.3390/machines13040314 | resumen | «**Local Interpretable Model-Agnostic Explanations (LIME)** were used to improve transparency and gain an understanding of decisions made through the Soft Voting Classifier» | **NO SOPORTADA** |
| **REF-016** Béchard y Ayala (2024) | «La recuperación de información puede reducirlo, pero no lo elimina por sí sola» — `cap1:17` | NAACL 2024, Industry Track. arXiv:2404.08189 | resumen | «our proposed system significantly **reduces** hallucinations in the output» | **PARCIALMENTE SOPORTADA** |
| **REF-106** Shuster et al. (2021) | misma afirmación que la anterior — `cap1:17` | *Findings of the ACL: EMNLP 2021*, 3784–3803. DOI 10.18653/v1/2021.findings-emnlp.320 | resumen | «substantially **reduce** the well-known problem of knowledge hallucination in state-of-the-art chatbots» | **PARCIALMENTE SOPORTADA** |

## El fallo, y por qué importa

**REF-044 no usa valores de Shapley: usa LIME.** Son dos métodos de atribución distintos, y la
memoria lo citaba como ejemplo del predominio del primero. El resumen del artículo no menciona
Shapley ni SHAP en ningún punto.

El error es de interpretación, no de existencia: el artículo existe, está correctamente
identificado y **sí pertenece al frente de explicabilidad**. Lo que no sostiene es la
afirmación concreta que se le colgaba.

**No se ha sustituido la referencia por otra que encajara.** Se corrige la afirmación para que
diga lo que la fuente dice. Sustituirla habría hecho desaparecer el fallo sin resolverlo, y
habría perdido un ejemplo válido de que la atribución en este dominio no se hace solo con
Shapley.

## Las tres parciales

En los tres casos la fuente sostiene **reducción** de la alucinación o **escasez de datos
etiquetados**, y la memoria daba un paso más:

- REF-049 documenta que los datos reales están sin etiquetar o mal etiquetados. **No dice nada
  sobre documentación de taller**, que era una observación propia de este trabajo presentada
  como si viniera de la revisión.
- REF-016 y REF-106 miden reducción. Que la recuperación **no elimine** la alucinación es una
  inferencia razonable de «reduce», pero ninguno de los dos lo afirma, y la memoria lo
  presentaba como resultado de ambos.

En los tres casos se ha acotado la afirmación a lo que la fuente sostiene, y lo que es
observación del autor se atribuye al autor.

## Metadatos corregidos

| Ref | Antes | Después |
|---|---|---|
| REF-049 | «AI-driven vehicle fault diagnosis: A review», autores incompletos, sin identificador | título completo, tres autores, páginas 951–996, DOI |
| REF-044 | sin publicación | *Machines*, 13(4), 314, DOI |
| REF-016 | «*arXiv*» | NAACL 2024, Industry Track, con el arXiv como preimpresión |
| REF-106 | autores incompletos, sin identificador | cinco autores, páginas 3784–3803, DOI |

Cuatro marcas `[VERIFY_SOURCE]` menos. Quedan cuatro en la bibliografía, y **no se continúa
con ellas**: el director pidió una muestra, y ampliarla ahora impediría leer el resultado de la
muestra como lo que es.

## Lectura del ejercicio

Una de cuatro no sostenía lo que se le atribuía. Sobre 21 referencias citadas, una muestra de
cuatro no permite estimar cuántas más están en la misma situación, pero sí basta para concluir
que **el control era necesario** y que conviene repetirlo sobre el resto antes del depósito.
