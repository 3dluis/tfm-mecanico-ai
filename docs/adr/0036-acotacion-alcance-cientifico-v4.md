# ADR-0036 — Acotación del alcance científico: explicación trazable y abstención

**Estado:** Aceptada (F26 · 2026-08-27, acordada con el tutor)
**Sustituye en su ámbito a:** la estructura científica de
[`docs/alineacion_v3/01_nucleo_cientifico.md`](../alineacion_v3/01_nucleo_cientifico.md)
(se conserva como documento histórico)
**Relacionada con:** ADR-0013 (memoria de tres niveles), ADR-0014 (agente v1), ADR-0015
(runtime multiagente), ADR-0018 (diseño experimental de arquitecturas), ADR-0022
(gobernanza de modelos), pre-registro `prereg-v1.0` (enmienda ENM-001)

## Contexto

La pregunta de investigación vigente hasta el 27-ago-2026 (PI v3) comprometía al trabajo con
una cadena de ocho pasos: observar, contextualizar, detectar, reconocer insuficiencia,
hipotetizar, recuperar y contrastar evidencia, verificar y consolidar conocimiento
validado. Contrastarla exigía seis familias de hipótesis (H-MAIN, H-EVT, H-PERS, H-EXP,
H-MEM, H-MAS) y ocho experimentos encadenados.

La propia auditoría interna del proyecto lo declaraba sin ambigüedad: *«nada de lo
ejecutado responde PI.b–PI.d»* (`alineacion_v3/02_trazabilidad.md` §2). Los catorce
estudios ejecutados entre F3 y F22 pertenecen todos a los pasos 1–3. A seis semanas de la
entrega, la mitad de la cadena carecía de evidencia propia y dependía de un bloqueante no
resuelto (R2, la elección del modelo de lenguaje local).

Tres opciones estaban sobre la mesa:

1. **Mantener la PI v3 y ejecutar la cadena completa.** Requiere EXP-SEG, EXP-ANOM-004,
   EXP-PERS, EXP-COV, EXP-EXP, EXP-MAS, EXP-MEM y EXP-MAIN, con dependencias en serie desde
   R2. El orden de sacrificio pre-declarado ya reconocía que no cabía completo. Riesgo alto
   de llegar a la entrega con la hipótesis principal no contrastada.
2. **Mantener la PI v3 y reportar solo la mitad detectora más el diseño del resto.** Deja la
   pregunta de investigación sin contraste experimental, que es el defecto que un tribunal
   señala con más facilidad.
3. **Acotar la PI a un tramo enteramente ejecutable, conservando todo el trabajo previo
   como instrumento.** Reduce el compromiso a lo que puede demostrarse y convierte la
   evidencia ya producida en la base instrumental del nuevo contraste.

## Decisión

**Se adopta la opción 3.** La pregunta de investigación pasa a ser:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II
> reales, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la
> evidencia disponible no es suficiente para sostener una explicación en lugar de generar
> una hipótesis sin fundamento?

Consecuencias vinculantes:

1. **El flujo científico principal** del sistema es: vehículo → OBD-II → procesamiento y
   contexto → diagnóstico → RAG → recuperación de evidencia → verificador → *¿evidencia
   suficiente?* → explicación diagnóstica trazable **o** abstención declarada.
2. **Los detectores de anomalías y el runtime multiagente son subsistemas auxiliares.**
   Siguen existiendo, siguen siendo necesarios (producen el contexto diagnóstico) y
   conservan toda su evidencia, pero dejan de dominar la narrativa científica.
3. **La memoria evolutiva, la consolidación de conocimiento, el descubrimiento de fallos no
   representados y el aprendizaje autónomo salen del alcance experimental.** No se elimina
   su código, sus contratos ni sus ADR: se documentan como no evaluados en
   `docs/alineacion_v4/05_fuera_de_alcance.md`. Los nodos `recall` y `memorize` del grafo
   se desactivan por configuración en los experimentos de la PI v4.
4. **La exclusión E-RAG cambia de papel.** Deja de ser una restricción que el corpus debía
   cumplir y pasa a ser la variable independiente principal: retirar del corpus, con
   manifiesto y checksum, los documentos que describen el mecanismo evaluado es lo que
   construye la condición de evidencia insuficiente. E-DET se conserva. E-MEM sale del
   protocolo.
5. **El pre-registro congelado no se reescribe.** El cambio entra por la enmienda ENM-001,
   fechada y no retroactiva, conforme a `pre-registro-v1.md` §2.1 y §13. No es retroactiva
   porque no se ha ejecutado ningún experimento confirmatorio.
6. **La palabra «descubrimiento» deja de usarse como contribución.** Los términos
   *dato*, *evidencia*, *diagnóstico*, *explicación*, *afirmación*, *hipótesis* y
   *abstención* tienen definición operativa única (núcleo científico v4 §2).
7. **La historia de la PI se documenta, no se oculta** (`04_historial_pi.md`).

## Alternativas descartadas

- **Conservar H-MAS o H-MEM como hipótesis secundarias del TFM.** Descartado: aunque
  fuesen baratas de enunciar, obligan a mantener experimentos que no responden a la PI v4 y
  reintroducen la dispersión que motiva este ADR. Pasan a trabajo futuro completas.
- **Eliminar el código de memoria y del runtime multiagente.** Descartado: es código
  funcional, cubierto por tests y referenciado por contratos y migraciones; eliminarlo
  generaría trabajo sin beneficio y rompería la trazabilidad de las fases anteriores.
- **Reescribir los documentos históricos bajo la nueva nomenclatura.** Descartado por la
  regla del repositorio: los documentos cerrados conservan su redacción y se leen por
  tablas de correspondencia.

## Consecuencias

**Positivas.** El contraste de la PI se reduce de ocho experimentos a tres, dos de ellos
ejecutables en una sola sesión de cómputo tras resolver R2 y R3. Las métricas centrales de
trazabilidad (corrección y completitud de citación, profundidad de traza) son
**deterministas** y no dependen de un juez de lenguaje, lo que aumenta la objetividad
respecto al diseño anterior. El hallazgo negativo de F24 (el corpus describía los
mecanismos held-out) se convierte en el punto de partida del diseño.

**Negativas y riesgos.** Se renuncia a una contribución potencialmente más ambiciosa. La
construcción del corpus en sus tres variantes (R3) pasa a ser bloqueante y no estaba en el
camino crítico. El corpus es obra propia, lo que limita la validez externa y debe
declararse. R2 sigue siendo el camino crítico.

**Neutras.** Los bancos congelados (`suite_v2`, `cases_v2`), la auditoría de contaminación,
la persistencia PostgreSQL+pgvector, el emulador y los contratos compartidos se reutilizan
sin modificación.
