# Propuestas de reformulación de objetivos

**1 de septiembre de 2026.** Cierra GATE-03, que es el único `FAIL` que queda.

**Esto son propuestas, no decisiones.** Cada bloque ofrece alternativas con su coste y su
consecuencia. `[AUTHOR_DECISION_REQUIRED]` en los tres casos.

**Restricciones que toda propuesta respeta:** infinitivo · verificable al terminar · sin
deseos futuros · vocabulario del marco canónico (E1-E20, M1-M6, FULL/PARTIAL/ABSENT/DISTRACTOR)
· entre 4 y 6 objetivos específicos.

---

## 1. Objetivo general — dos problemas

### Enunciado actual

> **Diseñar y evaluar** experimentalmente un agente basado en recuperación aumentada por
> evidencia que explique diagnósticos vehiculares obtenidos a partir de datos OBD-II reales,
> manteniendo una correspondencia verificable entre cada afirmación de la explicación y la
> evidencia que la sostiene, y que se abstenga de explicar cuando la evidencia disponible
> resulte insuficiente, **bajo las restricciones de cómputo propias de una plataforma
> embarcada**.

**Problema 1.** Dos verbos; la plantilla pide uno.
**Problema 2.** La cláusula final ya no describe el trabajo: M6 se mide sobre un MacBook M4
Pro y el despliegue embarcado es `FUTURE`. Mantenerla sería declarar algo no verificado.

### Opción A — verbo terminal, el diseño baja a objetivo específico *(recomendada)*

> **Evaluar** experimentalmente un agente de recuperación aumentada por evidencia, diseñado a
> tal efecto, en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos
> OBD-II manteniendo una correspondencia verificable entre cada afirmación y la evidencia que
> la sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no
> pertinente.

Un verbo. El diseño queda absorbido como subordinada y sigue cubierto por OE-M4. Añade «o no
pertinente», que incorpora PI.4 —hoy el objetivo general no la menciona—. Retira la cláusula
embarcada.

**Coste:** el diseño del artefacto deja de aparecer en el objetivo general. Es correcto: en
esta investigación el artefacto es el medio, no el fin.

### Opción B — verbo que contiene a ambos

> **Validar** experimentalmente un agente de recuperación aumentada por evidencia que explique
> diagnósticos vehiculares […]

«Validar» implica haber construido. Más compacto, algo menos transparente.

### Opción C — mantener dos verbos y declararlo

Conservar el enunciado y declarar al director la desviación consciente respecto de la regla
«solo un verbo», con su motivo.

**Coste:** un tribunal puede señalarlo. **Ventaja:** ninguna, salvo no tocar el texto.

### Sobre «datos OBD-II reales»

Las tres opciones escriben «datos OBD-II» sin «reales», **a la espera de E3**. Si E3 se
resuelve con datos reales, se repone la palabra. Si no, el objetivo general no debe prometer
lo que el trabajo no hará. Ver L-01.

**Resuelto el 3 de septiembre de 2026 (ADR-003):** la PI ya no lleva «reales». El objetivo
general escribe «datos OBD-II» de forma definitiva, no a la espera de E3.

---

## 2. OE-M3 — describe un marco que ya no se usa

### Enunciado actual

> Implementar y comparar **técnicas no supervisadas de detección de anomalías** bajo un
> protocolo experimental publicado con anterioridad a su ejecución, evaluando también la
> explicabilidad de las detecciones, de modo que el sistema disponga de un contexto diagnóstico
> verificable y caracterizado.

**El marco canónico no usa detección no supervisada.** Usa un baseline tabular (E6, bosque
aleatorio, ya cerrado) y un modelo temporal supervisado (E7), con atribución (E9). La parte de
explicabilidad sí sobrevive.

### Opción A — reflejar lo que se hace *(recomendada)*

> **Construir y evaluar** un modelo de diagnóstico sobre ventanas de telemetría, contrastado
> frente a una referencia mínima y a un baseline tabular, con su confianza calibrada y con
> atribución de descriptores, de modo que el sistema disponga de un contexto diagnóstico
> verificable y caracterizado.

Cubre E5-E9. Nombra explícitamente la **calibración**, que E6 demostró que no es un detalle
—ECE 0,140, modelo infraconfiado— sino una precondición del criterio de suficiencia (L-14).
«Contrastado frente a una referencia mínima» recoge lo que E6 ya hizo: la clase mayoritaria da
F1 macro 0,074 frente a 0,876 del baseline.

### Opción B — más corta

> **Desarrollar** un modelo de diagnóstico calibrado sobre telemetría OBD-II, con atribución de
> descriptores, que produzca un contexto diagnóstico verificable.

Pierde el contraste contra baseline, que es precisamente lo que da valor al resultado.

### Nota

La expresión «bajo un protocolo experimental publicado con anterioridad a su ejecución» del
enunciado actual **conviene conservarla en alguna forma**: describe una práctica real del
proyecto y es de las cosas que un tribunal valora. Puede ir en OE-M5 o en el capítulo 4.

---

## 3. OE-M5 — dos escenarios donde hay cuatro condiciones

### Enunciado actual

> Evaluar el agente frente a las hipótesis declaradas, **bajo dos escenarios** de
> disponibilidad de evidencia controlada, midiendo exactitud diagnóstica, **soporte y fidelidad
> de la explicación**, corrección y completitud de la trazabilidad y calidad de la abstención, y
> documentar el trabajo conforme a la normativa de la titulación, incluyendo de forma explícita
> los resultados negativos y las limitaciones de validez.

**Tres problemas.** Son cuatro condiciones, no dos escenarios. «Soporte y fidelidad» es
vocabulario legacy. Y E18 (ablaciones) y E20 (demostración) no están cubiertas.

### Opción A — reflejar el diseño canónico *(recomendada)*

> **Evaluar** el agente frente a las hipótesis declaradas bajo **cuatro condiciones de
> disponibilidad y pertinencia de la evidencia** —completa, parcial, ausente y con
> distractor—, midiendo exactitud diagnóstica, calidad de la recuperación, trazabilidad de las
> afirmaciones y calidad de la abstención con su cobertura, aislando la contribución de cada
> componente mediante ablaciones, y documentar el trabajo conforme a la normativa de la
> titulación, incluidos de forma explícita los resultados negativos y las limitaciones de
> validez.

Cubre E17, E18, E19 y E20. Vocabulario canónico. «Con su cobertura» es deliberado: corrección y
cobertura de la abstención solo significan algo juntas. Mantiene el compromiso de publicar
resultados negativos, que el proyecto ya cumple y conviene no perder.

### Opción B — separar la documentación

Dividir en dos objetivos: uno de evaluación experimental y otro de documentación. Subiría a
seis objetivos específicos, dentro del límite de la plantilla.

**A favor:** cada uno queda más nítido. **En contra:** la documentación no es un objetivo de
investigación, y un tribunal podría leerlo como relleno.

---

## 4. Consecuencia sobre la cobertura

Con las opciones A, la cobertura queda:

| Objetivo | Fases | Estado tras la reformulación |
|---|---|---|
| OE-M1 revisión del conocimiento | documental | sin cambios |
| OE-M2 entorno y corpus | E1 ✅ E2 ✅ **E3 ⛔** E4 ✅ E5 ✅ E10 | sin cambios |
| **OE-M3 modelo de diagnóstico calibrado** | E5 ✅ **E6 ✅** E7 E8 E9 | **coherente** |
| OE-M4 agente que recupera, explica, verifica y decide | E11-E16 | sin cambios |
| **OE-M5 evaluación bajo cuatro condiciones** | E17 E18 E19 E20 | **coherente** |

Cinco objetivos. Ninguna fase huérfana. **GATE-03 pasaría a `PASS`.**

## 5. Qué NO cambian estas propuestas

- El **enunciado de la pregunta de investigación**. Intacto.
- El **número de objetivos**: siguen siendo cinco.
- La **trazabilidad hacia los 13 objetivos de la propuesta aprobada**, que va al Anexo A.
- El compromiso de **publicar los resultados negativos**.

## 6. Trabajo pendiente si se aceptan

1. Actualizar `docs/memoria/02_objetivos.md` (repositorio legacy — **leerlo antes de tocarlo**).
2. Regenerar `objective-coverage.md` y `traceability-matrix.md`.
3. Reevaluar GATE-03.
4. Llevar el cambio a la reunión con el director, junto con el título definitivo.
