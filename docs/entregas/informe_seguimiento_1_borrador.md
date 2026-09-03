# Informe de seguimiento 1 — borrador de contenido

**TFM · Máster Universitario en Inteligencia Artificial · Universidad Alfonso X el Sabio**
**Autor:** Luis Daniel Díaz Díaz · **Fecha del borrador:** 1 de septiembre de 2026

> ⚠ **Este borrador NO tiene formato oficial.** La sesión informativa 25-26 indica que los
> formatos oficiales de los informes de seguimiento están en el mosaico *Documentación* del
> campus. **Hay que descargarlos y volcar este contenido en ellos.** El texto de aquí es el
> contenido; el continente es del campus.
>
> **Fecha límite:** 18/09/2026 (convocatoria de noviembre) o 30/09/2026 (diciembre).
> El informe se entrega por el campus y **se comunica al director su disponibilidad**.
>
> `[AUTHOR_DECISION_REQUIRED]` — a qué convocatoria se opta.

---

## 1. Título del trabajo

**Título registrado en la propuesta (14/07/2026):** «Sistema inteligente para el diagnóstico y
mantenimiento predictivo de vehículos».

**Título propuesto tras la acotación del alcance:** `[AUTHOR_DECISION_REQUIRED]`.

El alcance efectivo del trabajo ya no es el mantenimiento predictivo, sino **el soporte
verificable y la abstención en explicaciones diagnósticas**. La normativa prevé exactamente
este caso: «El título propuesto tiene carácter orientativo y puede ser modificado. El título
definitivo deberá comunicarse tras una primera reunión con el director para consensuarlo».

Propuesta de título, a consensuar:

> *Explicación diagnóstica trazable y abstención ante evidencia insuficiente: evaluación de un
> agente con recuperación aumentada sobre telemetría OBD-II*

## 2. Pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la
> evidencia disponible no es suficiente para sostener una explicación en lugar de generar una
> hipótesis sin fundamento?

Se descompone en cuatro subpreguntas evaluables por separado, cada una con su criterio fijado
**antes** de la evaluación final:

| | Subpregunta | Se responde en |
|---|---|---|
| PI.1 | Diagnóstico a partir de telemetría OBD-II | E8 |
| PI.2 | Explicación trazable hasta su evidencia | E14, E17 |
| PI.3 | Reconocimiento de evidencia insuficiente | E16, E17 |
| PI.4 | Rechazo de evidencia parecida pero incorrecta | E17 |

La respuesta global admite tres valores —sostenida, parcialmente sostenida, no sostenida— y se
han enumerado por adelantado cuatro desenlaces que la refutarían.

## 3. Estado de avance

### 3.1 Marco teórico

Revisión con procedimiento inspirado en PRISMA, en cuatro iteraciones: ≈170 consultas, ≈1 350
registros visualizados, ≈250 candidatos evaluados en fuente primaria y **144 referencias
consolidadas**.

De ellas, **110 tienen su identificador verificado programáticamente** en Crossref y DataCite;
**ninguna resultó inexistente o rota**. Las 34 restantes carecen de identificador en el barrido
y están señaladas para localización manual.

**Limitación declarada:** el barrido se ejecutó mediante buscador web con verificación en la
página del editor. El acceso automatizado a IEEE Xplore y ScienceDirect estuvo parcialmente
bloqueado, y los candidatos no verificables **se descartaron en lugar de citarse sin
verificar**. El flujo PRISMA formal, con recuentos por base, requiere acceso institucional y
está pendiente. Las cadenas de búsqueda están preparadas para ejecutarlo.

### 3.2 Marco metodológico

Diseño experimental cerrado y documentado. El experimento central manipula **una sola
variable** —qué evidencia documental está disponible— manteniendo idénticos datos, modelo,
semillas, atribución y prompt entre condiciones:

| Condición | Corpus | Comportamiento esperado |
|---|---|---|
| Completa | evidencia correcta presente | explicar, con cada afirmación trazada |
| Parcial | evidencia incompleta | abstenerse, salvo explicación limitada declarada |
| Ausente | evidencia retirada | abstenerse |
| Con distractor | evidencia parecida pero incorrecta | rechazarla; abstenerse si no queda otra |

Dos decisiones de diseño estructurales:

1. **El modelo de lenguaje no diagnostica ni decide.** Redacta y organiza evidencia que otros
   componentes han producido.
2. **La decisión de suficiencia vive en un componente determinista, fuera del modelo.** Si la
   tomara el modelo, la respuesta a la pregunta dependería de su disposición a admitir que no
   sabe algo, que es justo lo que no puede darse por supuesto.

El conjunto de test **permanece cerrado hasta la evaluación final**, con cierre técnico: el
cargador lanza una excepción si se intenta abrir sin declaración explícita y razón escrita.

### 3.3 Trabajo experimental

Plan de veinte fases. **Cinco cerradas**, cada una con informe, criterios de aceptación y
gates de calidad de código en verde.

| Fase | Estado |
|---|---|
| E1 entorno | cerrada |
| E2 generación de datos sintéticos | cerrada |
| **E3 datos reales** | pendiente — desde ADR-003 es validación externa, no precondición de la pregunta |
| E4 análisis exploratorio | cerrada |
| E5 preprocesamiento y particionado | cerrada |
| E6 baseline | cerrada |
| E7 modelo temporal | en curso |
| E8-E20 | pendientes |

### 3.4 Resultados disponibles

**Todas las cifras son de validación.** El conjunto de test no se ha abierto.

| | Exactitud | F1 macro |
|---|---|---|
| Referencia mínima (clase mayoritaria) | 0,286 | 0,074 |
| Baseline: bosque aleatorio sobre 139 descriptores | **0,878** | **0,876** |

Tres de las seis condiciones se clasifican perfectamente (F1 = 1,000). Todos los errores van a
«sin fallo»: el modelo no inventa diagnósticos cruzados.

**Cuatro hallazgos con consecuencia directa sobre la investigación:**

1. **Existe una fuente natural de casos de abstención.** El termostato bloqueado tiene un
   límite **físico** de detección: mientras el motor no habría superado por sí mismo el techo
   de temperatura que el fallo impone, la señal averiada es idéntica a la sana. No es una
   debilidad del modelo, es un límite de la evidencia. Son casos donde la respuesta correcta
   del agente es abstenerse — exactamente el escenario que la pregunta interroga, y no
   fabricado para el experimento.

2. **Evidencia aparente que no sobrevive al escrutinio.** Con ventana de 30 s, el mejor
   descriptor para el fallo de encendido resultó ser una variante de temperatura de
   refrigerante —señal que ese fallo no toca— y su tamaño de efecto quedaba **por debajo del
   suelo de ruido** medido para esa longitud. Es el fenómeno que el trabajo investiga, en
   miniatura.

3. **La evidencia de un fallo puede residir en una señal distinta de la averiada.** La deriva
   del caudalímetro no se detecta en el caudal de aire, sino en la compensación que hace la
   centralita. Una explicación que dijese «el caudalímetro está derivado porque el caudal es
   bajo» sería **falsa**. Esto condiciona qué afirmaciones puede emitir legítimamente el agente.

4. **La confianza del modelo está mal calibrada** (infraconfiada). Como esa confianza alimenta
   el criterio de suficiencia, calibrarla deja de ser un refinamiento y pasa a ser una
   precondición.

**Resultados negativos, conservados y publicados.** El fallo de encendido se detecta solo en la
mitad de los casos. Estaba anticipado por escrito **antes** de medirlo, con su motivo
cuantificado. No se ha aumentado su severidad para mejorar la cifra: un trabajo sobre
suficiencia de evidencia necesita casos difíciles.

### 3.5 Trazabilidad y control de calidad

Se mantiene una matriz que conecta pregunta → vacío → objetivo → experimento → métrica →
resultado, con detección automática de elementos huérfanos, y un registro de trece controles de
calidad con su estado y su evidencia.

Toda decisión científica relevante queda documentada en un registro de decisiones fechado.

## 4. Porcentaje de avance estimado

| Bloque | Avance | Base de la estimación |
|---|---|---|
| Marco teórico | 75 % | capítulo redactado; PRISMA formal y tres lecturas pendientes |
| Marco metodológico | 80 % | diseño cerrado y documentado; falta redactarlo en la memoria |
| Trabajo experimental | 25 % | 5 fases cerradas de 20; el experimento central pendiente |
| Resultados y discusión | 5 % | solo baseline, en validación |
| Conclusiones | 0 % | dependen de los resultados |
| **Global** | **≈ 40 %** | |

`[AUTHOR_DECISION_REQUIRED]` — la estimación es del autor; el director la valida.

## 5. Dificultades encontradas

1. **Fuente de datos reales sin resolver.** Fue el bloqueo principal mientras la pregunta
   exigía datos reales. El 3 de septiembre de 2026 la pregunta se enmendó (ADR-003): ya no
   los exige; exige que cada dataset declare su procedencia. Los datos sintéticos, calibrados
   contra el manual del vehículo, aportan control experimental pero **ninguna validez
   externa**, que se declara como limitación. Los datos reales siguen buscándose como
   validación adicional.

2. **Reorientación del marco experimental.** El trabajo mantiene la pregunta pero ha sustituido
   su diseño experimental por otro más directo y con una condición adicional —el rechazo de
   evidencia parecida pero incorrecta— que el diseño anterior no contemplaba. El cambio está
   documentado con su justificación y su coste; el diseño anterior se conserva íntegro.

3. **Acotación del alcance respecto de la propuesta inicial.** La propuesta de julio incluía
   despliegue en hardware embarcado, aplicación móvil y plataforma en la nube. El trabajo se ha
   concentrado en la pregunta de investigación; esos tres elementos pasan a trabajo futuro.
   **Se somete a consideración del director.**

## 6. Trabajo previsto hasta el informe 2

1. Decidir el dataset de la evaluación final y, si hay fuente, incorporar datos reales como validación externa.
2. Cerrar modelo temporal, evaluación y atribución.
3. Construir el corpus documental e indexarlo.
4. Integrar el agente y la verificación de trazabilidad.
5. Completar la bibliografía y ejecutar el flujo PRISMA formal si hay acceso institucional.

## 7. Consultas al director

1. **Extensión del TFM.** Tres cifras oficiales incompatibles: 50 000-60 000 palabras (nota al
   pie de la plantilla), 31-73 páginas (recomendaciones por capítulo) y mínimo 60 páginas sin
   anexos (sesión informativa 25-26). ¿Cuál rige?
2. **Plantilla vigente.** ¿Sigue rigiendo la plantilla del curso 24-25?
3. **Estilo de citación.** La plantilla indica APA 6.ª edición. ¿Se confirma?
4. **Título definitivo** y **acotación del alcance** respecto de la propuesta aprobada.
5. **Convocatoria** a la que se opta.

---

**Nota de integridad.** Ninguna cifra de este informe procede de una estimación. Todas las
métricas están respaldadas por un registro de ejecución reproducible con su semilla,
configuración y artefactos. Lo que no se ha ejecutado se declara como no ejecutado.
