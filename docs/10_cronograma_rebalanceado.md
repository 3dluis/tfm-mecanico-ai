# 10. Cronograma rebalanceado hasta la entrega (desde F22)

**Fecha de emisión:** 16 de agosto de 2026 · **Sustituye operativamente a** `docs/07`
§7.2, que se conserva como registro del plan original · **Estado:** propuesta, pendiente de
la aprobación del autor.

## 10.1 Punto de partida real

| | |
|---|---|
| Fases técnicas cerradas | F1–F22 |
| H1 (detección) | exploratorio **`SUPPORTED`** — línea **congelada** tras F22 |
| H2 (RAG) · H3 (memoria) · H4 (edge) | **sin ejecutar** |
| Memoria del TFM | esqueleto creado en F22; **0 palabras redactadas** |
| Pre-registro | **sin congelar** ⇒ nada confirmatorio es posible todavía |
| API del prototipo | solo `/health` y `/ready` |
| Días hasta el 18 de septiembre | **33** |

El desequilibrio que este cronograma corrige: 22 fases dedicadas casi por completo a H1,
frente a 0 en H2/H3/H4 y 0 páginas de memoria.

## 10.2 Principio de alcance (vigente desde ahora)

> Una tarea nueva debe contribuir **directamente** a una hipótesis, a un objetivo del TFM, a
> la reproducibilidad o a la entrega final. Si no cumple una de las cuatro, se pospone.

Y la regla de avance documental: **cada experimento relevante actualiza la memoria o deja el
bloque preparado.** La memoria pasa a ser entregable continuo, no fase final.

## 10.3 Clasificación del trabajo restante

### MUST HAVE — sin esto no hay TFM defendible

| ID | Tarea | Depende de | Salida verificable |
|---|---|---|---|
| M1 | **Memoria: capítulos 1, 2 y 3** | esqueleto (hecho) | Texto redactado; Cap. 3 sale del estado del arte ya escrito |
| M2 | **F-PREREG** — reconciliar y congelar `prereg-v1.0` | — | Tag `prereg-v1.0` + tabla de decisiones |
| M3 | **Corpus técnico defendible para RAG** | — | Corpus con `source`, licencia, versión, hash y chunking registrados |
| M4 | **EXP-RAG-001 (H2)** — brazos A/B | M3 | Hit@K, Recall@K, MRR, nDCG@K con librerías maduras |
| M5 | **EXP-MEM-001 (H3)** — brazos con/sin memoria longitudinal | agente v1 (hecho) | Métricas definidas **antes** de ejecutar |
| M6 | **API mínima del prototipo** | modelo de datos (hecho) | Endpoints del flujo científico, sin CRUD administrativo |
| M7 | **Memoria: capítulos 4, 5 y 6** | M1, M4, M5 | Texto redactado con cifras trazables a artefactos |
| M8 | **Guía de reproducción + limpieza del repositorio** | — | Un tercero levanta el sistema y reproduce un experimento |
| M9 | **Presentación de defensa + demo grabada** | M6 | Guion + vídeo de respaldo |

### SHOULD HAVE — mejora sustancialmente la defensa

| ID | Tarea | Depende de | Riesgo si falta |
|---|---|---|---|
| S1 | **A2/A3 — validación ARM64/RPi5** | hardware disponible | Sin ella, toda afirmación edge queda como `ARM64 pending` |
| S2 | **H4 — benchmark de recursos en edge** | S1 | H4 sin datos; se declara no evaluada |
| S3 | **HCRL — descarga, auditoría y replay** | — | Validez externa nula; el hallazgo del LTFT queda como propiedad del emulador |
| S4 | **Serie confirmatoria mínima** | M2 | Todo el trabajo permanece exploratorio |
| S5 | **Merge controlado de `backup-alineacion-cientifica`** | M2 | Documentos científicos siguen fuera de `main` |
| S7 | **Corregir `peak_rss_mb()` fuera de Linux** | — | Cifras de memoria erróneas ×1024 en H4 |

### OPTIONAL — solo si sobra tiempo tras MUST + SHOULD

| ID | Tarea | Nota |
|---|---|---|
| O1 | UI web ligera | Solo si aporta a la demo; **no reactivar Flutter** |
| O2 | Brazo C de H2: RAG + reranking | Únicamente si el baseline lo justifica |
| O3 | Ablation volumen vs cobertura (cierra el confound de F22) | Científicamente valiosa; no imprescindible para defender |
| O4 | D3 — evaluación XAI sobre `ae_v3` | Su condición se ha disparado por primera vez (ver §10.6) |

### CUT IF NEEDED — orden de sacrificio preacordado

1. O1 (UI web) → la API y un cliente/notebook bastan para la demo.
2. O2 (reranking).
3. O3 (ablation de volumen) → se declara como limitación, que ya está escrita.
4. O4 (XAI sobre `ae_v3`) → D3 se congela sin evaluar, documentando por qué.
5. S4 (confirmatorios) → **todo el TFM se presenta como exploratorio**, que es defendible si
   se declara con rigor, pero pierde fuerza.
6. S3 (HCRL) → se declara la ausencia de validez externa como limitación central.
7. **Línea roja infranqueable:** memoria completa + H2 + H3 + API mínima + reproducibilidad.
   Si esto peligra, la conversación es con el tutor, no con el cronograma.

## 10.4 Calendario propuesto

Trabajo en paralelo desde el primer día: **memoria y experimentos avanzan a la vez**, que es
justamente lo que no ocurrió en F1–F22.

| Semana | Experimentos / sistema | Memoria | Hitos |
|---|---|---|---|
| **S1 · 16-22 ago** | M2 (F-PREREG) · M3 (corpus RAG) · S7 · preparar S1/A2-A3 | **M1**: Cap. 1, 2 y 3 | `prereg-v1.0` congelado · corpus registrado |
| **S2 · 23-29 ago** | **M4 (EXP-RAG-001)** · M6 (API mínima) | Cap. 4 completo; Cap. 5 §2.2 con H2 | H2 respondida |
| **S3 · 30 ago-5 sep** | **M5 (EXP-MEM-001)** · S3 (HCRL si llega) | Cap. 5 §2.1 y §2.3 | H3 respondida |
| **S4 · 6-12 sep** | S1/S2 (edge) · S4 (confirmatorios) | Cap. 5 §2.4 y §3; Cap. 6 | H4 respondida o declarada pendiente |
| **S5 · 13-18 sep** | M8 (reproducibilidad) · M9 (demo) | Revisión integral · resumen/abstract | **Memoria completa** |
| **S6 · 19 sep-entrega** | Margen | Correcciones del tutor | Entrega |

## 10.5 Dependencias

```
                 ┌─────────────────────────────────────────┐
F22 (hecho) ─────┤                                         │
                 ↓                                         ↓
            M1 Cap.1-3 ──────────────┐              M2 F-PREREG
                 │                   │                     │
   M3 corpus ────┤                   │                     ↓
       │         │                   │              S4 confirmatorios
       ↓         │                   │                     │
   M4 H2 (RAG) ──┤                   │                     │
       │         │                   │                     │
   M5 H3 (mem.) ─┤                   │                     │
       │         │                   │                     │
  S1 A2/A3 ──▶ S2 H4 ────────────────┤                     │
       │                             ↓                     ↓
   M6 API ───────────────────▶  M7 Cap.4-6  ◀──────────────┘
                                     │
                                     ↓
                            M8 reproducibilidad
                                     ↓
                              M9 defensa · ENTREGA
```

Camino crítico: **M1 → M4/M5 → M7 → M8 → M9**. Todo lo que dependa de hardware (S1, S2) o de
terceros (S3) está fuera del camino crítico **a propósito**: el TFM no puede quedar
bloqueado esperando una Raspberry Pi.

## 10.6 Decisiones abiertas que condicionan este cronograma

1. **Extensión de la memoria.** La plantilla exige 50 000–60 000 palabras y a la vez
   recomienda 31–73 páginas por capítulo (≈ 12 000–29 000 palabras). Un factor de 2 a 4 de
   diferencia. **Hay que preguntar al tutor**: con 50 000 palabras, la escritura es la
   actividad dominante de las cinco semanas y hay que recortar antes en la lista de §10.3.
3. **D3 (XAI).** Su condición —`D1 = PROMOTE_CANDIDATE`— se ha cumplido por primera vez en
   F22. Evaluarlo es trabajo nuevo; congelarlo sin evaluar desaprovecha la única ocasión.
4. **Tutor.** No consta asignado en la documentación del proyecto. Es un bloqueante
   administrativo con plazo, no técnico.

