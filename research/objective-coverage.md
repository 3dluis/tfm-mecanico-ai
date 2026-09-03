# Cobertura por objetivo

**Marco canónico** (ADR-001) · 1 de septiembre de 2026, 15:00.

Los objetivos son los de `mecanico-ia/docs/memoria/02_objetivos.md` (borrador v1). **Dos de
ellos describen el marco legacy** y deben reformularse: ver `traceability-matrix.md` §5.

| Objetivo | Fases | Métricas | Resultado | Capítulo | Estado |
|---|---|---|---|---|---|
| **OE-M1** — revisar críticamente el estado del conocimiento | (documental) | — | 144 referencias verificadas | 3 | **PASS_WITH_OBSERVATIONS** — falta cubrir la pertinencia de la evidencia (I-03) y el PRISMA formal |
| **OE-M2** — entorno reproducible de telemetría y corpus con variantes congeladas | E1 ✅, E2 ✅, E3 (validación externa, pendiente), E4 ✅, E5 ✅, E10 ✅ | — | 5 fases cerradas de 6 | 4 | **PASS_WITH_OBSERVATIONS** — desde ADR-003 E3 no bloquea; queda como validación externa sin fuente |
| **OE-M3** ⚠ — implementar y comparar técnicas **no supervisadas** de detección, evaluando explicabilidad | **E6 ✅**, E7, E8, E9 | M1 | baseline en validación: F1 macro 0,876 | 4, 5 | **FAIL de coherencia** — el marco canónico usa modelo supervisado. Reformular |
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
- Fases cerradas: **5** de 20

## Lectura

Ningún objetivo está cumplido, pero **OE-M3 ya tiene su primera cifra**: el baseline de E6
fija el umbral (F1 macro 0,876) contra el que se medirá el modelo temporal.

**OE-M2 está a una sola decisión (E3) de completarse.** Cuatro de sus seis fases están
cerradas; la que falta es la que bloquea el proyecto entero.

Y dos de los cinco objetivos hay que reescribirlos antes de que signifiquen algo. **OE-M3 es
el más urgente**: describe detección no supervisada, y lo que E6 acaba de cerrar es un bosque
aleatorio supervisado.
