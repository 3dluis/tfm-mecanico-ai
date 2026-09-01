# Cobertura por objetivo

**Marco canónico** (ADR-001) · 1 de septiembre de 2026.

Los objetivos son los de `mecanico-ia/docs/memoria/02_objetivos.md` (borrador v1). **Dos de
ellos describen el marco legacy** y deben reformularse: ver `traceability-matrix.md` §5.

| Objetivo | Fases | Métricas | Resultado | Capítulo | Estado |
|---|---|---|---|---|---|
| **OE-M1** — revisar críticamente el estado del conocimiento | (documental) | — | 144 referencias verificadas | 3 | **PASS_WITH_OBSERVATIONS** — falta cubrir la pertinencia de la evidencia (I-03) y el PRISMA formal |
| **OE-M2** — entorno reproducible de telemetría y corpus con variantes congeladas | E1 ✅, E2 ✅, E3 ⛔, E4, E5, E10 | — | E1 y E2 cerradas | 4 | **BLOCKED** — E3 sin fuente de datos |
| **OE-M3** ⚠ — implementar y comparar técnicas **no supervisadas** de detección, evaluando explicabilidad | E6, E7, E8, E9 | M1 | ninguno | 4, 5 | **FAIL de coherencia** — el marco canónico usa modelo supervisado. Reformular |
| **OE-M4** — implementar el agente que recupera, explica con afirmaciones referenciadas, verifica y decide | E11, E12, E13, E14, E15, E16 | M2, M4, M5 | ninguno | 4, 5 | **PENDING** |
| **OE-M5** ⚠ — evaluar el agente bajo **dos escenarios**, y documentar el trabajo | E17, E18, E19, E20 | M1-M6 | ninguno | 5, 6 | **FAIL de coherencia** — son cuatro condiciones. Reformular |

## Objetivos secundarios

| ID | Enunciado | Estado |
|---|---|---|
| OS1 | Aplicación móvil que consuma la interfaz de consulta | fuera del compromiso de cumplimiento; `FUTURE` en el plan canónico |
| OS2 | Sincronización con plataforma en la nube | ídem |

Ambos fueron recortados de forma preacordada al planificar. Su ausencia no afecta a los
objetivos específicos — pero sí a la correspondencia con la propuesta aprobada (L-13).

## Huérfanos

- Objetivos sin fase asignada: **0**
- Fases sin objetivo: **0**
- Objetivos que describen otro marco: **2** (OE-M3, OE-M5)
- Objetivos cumplidos: **0** de 5

## Lectura

Ningún objetivo está cumplido. **OE-M1 y OE-M2 son los únicos que pueden avanzar hoy**: el
primero es documental, el segundo está a una decisión (E3) de desbloquearse. Los otros tres
dependen de datos que aún no existen.

Y dos de los cinco hay que reescribirlos antes de que signifiquen algo.
