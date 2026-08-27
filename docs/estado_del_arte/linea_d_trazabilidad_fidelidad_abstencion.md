# Línea D — Fidelidad, atribución de evidencia, incertidumbre y abstención

**Abierta el 2026-08-27 con la alineación científica v4.** Es la línea de análisis que
sostiene directamente la PI v4 y que la revisión anterior no cubría: las líneas A
(OBD-II/ML y datasets), B (anomalías y modelos pequeños en el borde) y C (agentes, RAG y
memoria) se abrieron bajo una pregunta centrada en el descubrimiento y en la memoria, y la
atribución verificable de evidencia y la abstención quedaron fuera de su alcance.

**Estado: pendiente de ejecución.** Este documento fija el protocolo de búsqueda y los
criterios; las fichas de las referencias se incorporarán al completarlo. No se listan aquí
referencias sin verificar en fuente primaria: la regla del proyecto es no inventar citas.

---

## 1. Pregunta que responde la línea

> ¿Qué se sabe sobre verificar que lo que un sistema generativo afirma está sostenido por
> la evidencia que ha recuperado, y sobre qué debe hacer cuando no lo está?

Aporta a las dimensiones **D1** (trazabilidad verificable) y **D2** (comportamiento ante
evidencia insuficiente) del vacío V4\*
(`capitulo2_estado_del_arte.md` §2.15, `docs/alineacion_v4/01_nucleo_cientifico.md` §3).

## 2. Preguntas de revisión nuevas

- **RQ18** — ¿Cómo se mide que una explicación generada está sostenida por la evidencia
  recuperada, y con qué validez son esas medidas? *(groundedness, faithfulness)*
- **RQ19** — ¿Cómo se genera y se evalúa una atribución de evidencia verificable —que la
  cita exista, resuelva y sostenga la afirmación—, y con qué separación entre corrección y
  completitud? *(citation attribution, provenance)*
- **RQ20** — ¿Qué marcos existen para que un sistema decida no responder, y cómo se evalúa
  esa decisión? *(uncertainty, selective prediction, abstention, risk-coverage)*
- **RQ21** — ¿Qué evidencia hay sobre la reducción efectiva de afirmaciones no sustentadas
  mediante recuperación en dominios técnicos, y qué factores la determinan?
  *(hallucination mitigation)*
- **RQ22** — ¿Se ha aplicado algo de lo anterior a explicaciones ancladas simultáneamente en
  documentación y en telemetría física?

## 3. Subtemas y términos de búsqueda

| Subtema | Términos (inglés) | Términos (español) |
|---|---|---|
| Soporte y fidelidad | `groundedness`, `faithfulness`, `factual consistency`, `RAG evaluation`, `answer attribution` | fidelidad, consistencia factual, evaluación de RAG |
| Atribución y procedencia | `citation attribution`, `attributable to identified sources`, `provenance`, `evidence attribution`, `verifiable generation` | atribución de citas, procedencia, generación verificable |
| Incertidumbre y abstención | `selective prediction`, `abstention`, `learning to defer`, `reject option`, `risk-coverage curve`, `AURC`, `calibration`, `conformal prediction` | predicción selectiva, abstención, opción de rechazo, calibración |
| Mitigación de alucinación | `hallucination mitigation`, `unsupported claims`, `claim verification`, `retrieval-grounded generation` | mitigación de alucinaciones, afirmaciones no sustentadas |
| Aplicación técnica/industrial | `technical support RAG`, `maintenance question answering`, `industrial diagnostics LLM evaluation` | RAG en soporte técnico, diagnóstico industrial |
| Cruce con el dominio | `vehicle diagnostics RAG`, `OBD-II LLM explanation`, `automotive fault explanation` | diagnóstico vehicular con RAG, explicación de averías |

Cruces obligatorios: cada término de las tres primeras filas × `{vehicle, automotive,
OBD-II, telemetry, predictive maintenance}`. El objetivo del cruce es **refutar** D1 y D2,
no confirmarlos.

## 4. Criterios de inclusión y exclusión

**Inclusión.** Publicaciones 2021–2026 (o anteriores si fundacionales, marcadas como tales);
estudios que propongan o evalúen medidas de soporte, atribución, incertidumbre o abstención
en sistemas generativos con recuperación; o que trasladen predicción selectiva a esos
sistemas; metodología verificable; verificación en fuente primaria en la fecha del barrido.

**Exclusión.** Material comercial; ausencia de metodología; trabajos de alucinación
puramente descriptivos sin medida propuesta; alineación y seguridad de modelos sin relación
con el soporte por evidencia; duplicados; imposibilidad de verificación en fuente primaria.

**Marcado.** Los preprints se marcan siempre como tales y se usan como indicador de
tendencia, no como evidencia consolidada, conforme a §2.2.2 del capítulo 2.

## 5. Búsqueda adversarial obligatoria

Antes de dar por cerrada la línea, se ejecuta una búsqueda cuyo objetivo declarado es
**refutar V4\***: encontrar un trabajo que evalúe conjuntamente diagnóstico sobre telemetría
vehicular real, explicación con RAG, trazabilidad verificada hasta la evidencia y
comportamiento ante evidencia insuficiente. Si aparece, se incorpora como antecedente y
V4\* se reformula (§2.15.3). Candidatos de partida para vigilancia: derivados de Mahale et
al. (2025), RAAD-LLM y sus continuaciones, y trabajos de *selective RAG* aplicados a
mantenimiento.

## 6. Relación con las líneas existentes

- **Línea A** (OBD-II, ML, datasets): se conserva íntegra como línea principal.
- **Línea B** (anomalías y modelos pequeños en el borde): se conserva como antecedente
  instrumental del contexto diagnóstico y del criterio edge.
- **Línea C** (agentes, RAG y memoria): su parte de **RAG y agentes** alimenta esta línea;
  su parte de **memoria y consolidación** pasa a antecedente y a trabajo futuro
  (`docs/alineacion_v4/05_fuera_de_alcance.md`).
