# Matriz de impacto: ADR-004 frente a los notebooks y la documentación

**Fecha:** 13 de octubre de 2026 · **Qué resuelve:** la contradicción `JURY-CRT-001`, detectada por
el tribunal simulado · **Decisión del autor:** mantener la pregunta acotada de `ADR-004`; la amplia
pasa a línea de investigación futura · **Estado de este documento:** se elabora **antes** de
modificar ningún documento científico, como exige el encargo

## 1. La contradicción, delimitada

`ADR-004`, de 12 de septiembre de 2026, aceptada y decidida por la dirección del TFM, fija la
pregunta canónica:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

Y declara superada la formulación amplia de agosto de 2026, tras auditar sus cinco términos: uno
tenía evidencia y dos no tenían implementación ni fase en el plan de veinte.

**Tres documentos la contradicen**, los tres escritos el 12 y 13 de octubre de 2026 al preparar la
entrega de notebooks. Ninguno es anterior a `ADR-004`: la contradicción se introdujo después, al
tomar como enunciado principal una formulación que la decisión ya había retirado.

## 2. Inventario completo, documento a documento

Buscado en todo el repositorio por las dos formulaciones.

### 2.1 Documentos que usan la formulación **superada** como vigente

| Documento | Dónde | Qué dice | Acción |
|---|---|---|---|
| `notebooks/00_introduccion.ipynb` | §1, cita en bloque | la amplia, presentada como «la pregunta de investigación» | **sustituir** por la canónica |
| ídem | §1, párrafo siguiente | «La pregunta tiene cuatro verbos: identificar, generar, validar e incorporar» | **reescribir**: los verbos de la canónica son explicar, rastrear y reconocer |
| `docs/notebooks/html/00_introduccion.html` | derivado | ídem | **regenerar** del notebook corregido |
| `docs/notebook-traceability.md` | encabezado «La pregunta principal» | la amplia | **sustituir** por la canónica |

### 2.2 Documentos que **mencionan** la amplia correctamente, como superada

No se tocan: documentan la historia de la decisión, que es lo que hay que conservar.

| Documento | Papel |
|---|---|
| `research/decisions/ADR-004-pregunta-de-investigacion-canonica.md` | **la decisión misma** |
| `docs/audits/full_memory_review/11_BLOCKERS_AND_DECISIONS.md` | registra el conflicto `SD-01` que `ADR-004` resolvió |
| `docs/audits/scope_change/DIFERENCIAL-v2.0-a-acotada-20260915.md` | el diferencial entre las dos formulaciones |

### 2.3 Documentos que ya usan la **canónica**

No requieren cambio. Son la mayoría, y por eso la contradicción es acotada y no sistémica.

`README.md` · `docs/memoria/cap1_introduccion.md` · `docs/matriz_validacion_pi.md` ·
`docs/tfm-traceability.md` · `docs/plan_experimental_macbook.md` ·
`docs/methodology/estados-provisionales.md` · `docs/tfm/cambio_pi_eliminacion_datos_reales.md` ·
`docs/tfm/revision/00_baseline.md` · `docs/tfm/revision/07_correction_plan.md` ·
`docs/audits/tutor_observations/06-alignment-matrix.md`

## 3. Lo que **no** cambia, y es la parte tranquilizadora

**Las cuatro subpreguntas son las mismas en los dos sitios.** Se ha comparado una a una:

| | En `docs/matriz_validacion_pi.md` (canónica) | En `00_introduccion.ipynb` |
|---|---|---|
| **PI.1** | diagnóstico: F1 macro frente a la clase mayoritaria, con confianza calibrable | «que el diagnóstico a partir de OBD-II supere a la clase mayoritaria con margen amplio y que su confianza se pueda calibrar» |
| **PI.2** | trazabilidad: toda afirmación anclada en observación y documento verificados | «que toda afirmación se ancle en una observación o un fragmento identificable» |
| **PI.3** | reconocimiento de insuficiencia: la decisión cambia al retirar la evidencia | «que el sistema reconozca cuándo no sabe: al retirar la evidencia, pasa de explicar a abstenerse» |
| **PI.4** | rechazo de evidencia engañosa | «que rechace evidencia no pertinente» |

**Consecuencia:** ningún experimento, ninguna métrica, ningún resultado y ninguna conclusión cambia
de sentido. Lo que cambia es el enunciado que los encabeza, que hoy promete más de lo que las cuatro
subpreguntas evalúan.

Y las cuatro subpreguntas **sí** son lo que la pregunta canónica pide: explicar (PI.1 y PI.2),
rastrear hasta la evidencia (PI.2) y reconocer la insuficiencia (PI.3 y PI.4). El encaje es directo.

## 4. Qué pasa con los componentes de la formulación amplia

La decisión del autor es conservarlos, no eliminarlos, y clasificarlos como **capacidades
complementarias o exploratorias**. Inventario de lo que existe y dónde queda:

| Componente de la formulación amplia | Qué hay construido | Clasificación |
|---|---|---|
| **Detección de anomalías** | E6 y E7: bosque y GRU sobre ventanas, con sus registros y cifras | **necesario** para PI.1: es el diagnóstico |
| **Análisis longitudinal** | E4 y E5 —ventanado, estudio de duración—, E7, y el diseño de PI.1 en `docs/diseno-pi1/` | **necesario** para PI.1 en su parte medida; **exploratorio** en lo que el diseño de PI.1 aún no ha ejecutado |
| **Generación de hipótesis** | E9: la atribución produce las observaciones que sostienen la hipótesis diagnóstica | **necesario** para PI.2 |
| **Identificación de patrones no representados** | **nada**: no tiene experimento ni fase en el plan de veinte | **línea futura**, sin evidencia |
| **Incorporación como conocimiento reutilizable** (memoria evolutiva) | **nada**: ídem | **línea futura**, sin evidencia |

**Nada se elimina.** Los tres primeros ya están al servicio de la pregunta canónica y así se nombran.
Los dos últimos no tienen nada que eliminar, porque nunca se construyeron; pasan a trabajo futuro,
que es exactamente lo que `ADR-004` concluyó al auditarlos.

## 5. Trazabilidad que hay que preservar al corregir

Cada cambio debe mantener la cadena intacta:

```
pregunta canónica (ADR-004)
  → cuatro subpreguntas (matriz de validación)      · SIN CAMBIO
    → objetivos específicos (cap. 2)                 · SIN CAMBIO
      → experimentos E1–E19 (plan e informes)        · SIN CAMBIO
        → métricas (matriz de validación)            · SIN CAMBIO
          → resultados (registros en experiments/)   · SIN CAMBIO
            → conclusiones (cap. 6)                  · SIN CAMBIO
```

**Solo cambia el enunciado de la primera línea en tres documentos.** Nada aguas abajo depende del
enunciado amplio, porque los notebooks ya trazaban contra las cuatro subpreguntas canónicas.

## 6. Riesgo de la corrección, y cómo se acota

| Riesgo | Acotación |
|---|---|
| Que al cambiar el enunciado se altere alguna afirmación sobre resultados | ninguna cifra, tabla ni figura se toca; el cambio es de texto en tres sitios, y el gate de notebooks comprueba después que las cifras siguen saliendo de sus artefactos |
| Que se pierda la historia de la decisión | no se toca `ADR-004` ni los dos documentos de auditoría que registran el conflicto; **este documento se conserva** como registro del cambio |
| Que la línea futura quede escondida | se declara explícitamente en el notebook de introducción, en el apartado de lo que queda abierto, y con la razón: dos de sus términos no tienen experimento |
| Que el HTML quede desincronizado | se regenera desde el notebook y el gate lo comprueba |

## 7. Qué se hace, en orden

1. Este documento, **antes** de tocar nada. ✓
2. `00_introduccion.ipynb`: sustituir el enunciado y reescribir el párrafo de los verbos; añadir la
   formulación amplia como línea futura, con su estado de evidencia.
3. `docs/notebook-traceability.md`: sustituir el encabezado.
4. Regenerar el HTML de los cinco notebooks.
5. Gate completo y verificación del censo.
6. Dejar escrito en el informe del tribunal que `JURY-CRT-001` queda resuelto, con su fecha.

**Lo que no se hace:** modificar `ADR-004`, eliminar experimentos o resultados, reescribir
conclusiones, ni presentar la ampliación como decidida. La propuesta formal de ampliación, si llega,
será posterior y tendrá que sostenerse en resultados verificables.
