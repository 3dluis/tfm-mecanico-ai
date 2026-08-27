# 10. Cronograma rebalanceado hasta la entrega (desde F22)

**Fecha de emisión:** 16 de agosto de 2026 · **Revisado el 27 de agosto de 2026** ·
**Sustituye operativamente a** `docs/07` §7.2, que se conserva como registro del plan
original.

> **⚠ Revisión del 27-ago-2026 (ADR-0036).** La acotación de la pregunta de investigación
> **simplifica este cronograma**: de tres experimentos agénticos encadenados (EXP-EXP-001,
> EXP-MEM-001, EXP-MAS-001) se pasa a dos (**EXP-RET-001** y **EXP-EVID-001**), y el
> contraste principal deja de depender de la memoria. Cambios en las tareas MUST:
>
> | Antes | Ahora |
> |---|---|
> | **M4** — corpus e índice RAG con métricas descriptivas | **M4** — corpus en **tres variantes** C-A / C-B / C-B′ con manifiesto, checksum y evidencia de referencia por caso (parámetro diferido **D4**), más **EXP-RET-001**: la recuperación deja de ser instrumental y **contrasta H-GRD** |
> | **M5** — EXP-MEM-001 (M0/M1/M2) | **Retirada del alcance.** Diseño conservado sin ejecutar (`alineacion_v4/05_fuera_de_alcance.md` §1) |
> | **M5b** — EXP-EXP-001 (X0/X1/X2) | **M5** — **EXP-EVID-001**: absorbe EXP-EXP-001 y EXP-COV-001; 3 brazos B1/B2/B3 × 2 escenarios × 40 casos; contrasta H-MAIN, H-GRD, H-TRC, H-ABS y H-SEL |
>
> **M2b (R2, fijar el modelo de lenguaje) sigue siendo el camino crítico** y ahora comparte
> ese lugar con **M4**, que pasa a ser bloqueante. El orden de sacrificio pre-declarado, si
> el calendario aprieta: validaciones externas → variante C-B′ → brazo B1 → EXP-SEG-001;
> **nunca** el Escenario B ni el brazo B3. Plan experimental vigente:
> [`03_diseno_experimental.md`](alineacion_v4/03_diseno_experimental.md) §5.

## 10.1 Punto de partida real

| | |
|---|---|
| Fases técnicas cerradas | F1–F22 |
| H1 (detección) | exploratorio **`SUPPORTED`** — línea **congelada** tras F22 |
| H2 (RAG) · H3 (memoria) · H4 (edge) | **sin ejecutar** — bajo la PI v4: H-GRD/H-TRC/H-ABS/H-SEL sin ejecutar; H-MEM fuera de alcance; el criterio edge sigue vigente |
| Memoria del TFM | esqueleto creado en F22; 0 palabras **en `main`** — pero ver la corrección de §10.1.1 |
| Pre-registro | **sin congelar** ⇒ nada confirmatorio es posible todavía |
| API del prototipo | solo `/health` y `/ready` |
| Días hasta el 18 de septiembre | **33** |

El desequilibrio que este cronograma corrige: 22 fases dedicadas casi por completo a H1,
frente a 0 en H2/H3/H4.

### 10.1.1 Corrección: hay ~61 000 palabras de material científico fuera de `main`

La primera versión de este cronograma decía «0 páginas de memoria». **Era cierto para `main`
y engañoso para el proyecto.** La rama `backup-alineacion-cientifica`, nunca fusionada,
contiene:

| Documento | Palabras | Qué es |
|---|---|---|
| `estado_del_arte/estado_del_arte_y_metodologia_tutor.md` | 15 391 | Estado del arte + metodología, formato de entrega a tutor |
| `estado_del_arte/capitulo2_estado_del_arte.md` | 10 814 | **Capítulo de estado del arte redactado** (Entrega 4, 2026-08-12), ≈153 referencias verificadas en fuente primaria, metodología tipo PRISMA, búsqueda adversarial, vacíos V1–V7, matriz de trazabilidad, RQ1–RQ17 |
| `estado_del_arte/entrega1/2/3_revision_sistematica.md` | 20 566 | Las tres iteraciones de revisión sistemática |
| `experiments/pre-registro-v1.md` | 7 464 | **El pre-registro global** (ver F-PREREG) |
| `auditoria_alineacion_investigacion.md` · `propuesta_alineacion_final.md` · `afirmaciones_novedad.md` · `resumen_ejecutivo_estado_del_arte.md` | 6 978 | Auditoría de alineación y afirmaciones de novedad |

**Consecuencia directa:** el Cap. 3 (Marco Teórico) de la memoria **no se escribe desde
cero**; se adapta desde `capitulo2_estado_del_arte.md`. Y **S5 (merge controlado de la rama)
deja de ser SHOULD y pasa a MUST, en primera posición**: escribir el Cap. 3 partiendo de
cero teniendo 10 814 palabras sin fusionar sería tirar el trabajo a la basura.

El capítulo declara sus propios pendientes antes del depósito, que hay que respetar: flujo
PRISMA formal con acceso institucional, lectura a texto completo de tres trabajos y búsqueda
adversarial de vigilancia inmediatamente antes de depositar.

## 10.2 Principio de alcance (vigente desde ahora)

> Una tarea nueva debe contribuir **directamente** a una hipótesis, a un objetivo del TFM, a
> la reproducibilidad o a la entrega final. Si no cumple una de las cuatro, se pospone.

Y la regla de avance documental: **cada experimento relevante actualiza la memoria o deja el
bloque preparado.** La memoria pasa a ser entregable continuo, no fase final.

## 10.3 Clasificación del trabajo restante

### MUST HAVE — sin esto no hay TFM defendible

| ID | Tarea | Depende de | Salida verificable |
|---|---|---|---|
| **M0** | **Merge controlado de `backup-alineacion-cientifica`** (era S5) | — | Paquete científico en `main` sin sobrescribir nada más reciente (§10.1.1) |
| M1 | **Memoria: capítulos 1, 2 y 3** | **M0** | Texto redactado; Cap. 3 **se adapta** de `capitulo2_estado_del_arte.md`, no se escribe de cero |
| M2 | **F-PREREG** — reconciliar y congelar `prereg-v1.0` | M0 | Tag `prereg-v1.0`; comparación y decisión ya redactadas |
| **M2b** | **R2 — smoke del SLM (fija D1)** | — | **Desbloquea EXP-MEM-001, EXP-EXP-001 y EXP-MAS-001**; preparado desde F9 y nunca ejecutado |
| M3 | **Corpus técnico defendible para RAG** | auditoría (hecha) | Corpus con `source`, licencia, versión, hash y chunking; `CORPUS_MANIFEST.md` |
| M4 | **R3 — corpus e índice RAG con métricas IR descriptivas** | M3, M2b | Hit rate, MRR, nDCG. **Instrumental**: no contrasta hipótesis (ver F-PREREG §4) |
| M5 | **EXP-MEM-001** — brazos M0/M1/M2, **ya pre-registrado** | M2, M2b | Δexactitud ≥ +0.10 abs.; −50 % rel. consolidaciones erróneas. **No hay que diseñarlo: hay que ejecutarlo** |
| **M5b** | **EXP-EXP-001** — X0 / X1 / X2 | M4, M2b | Aquí vive el contraste «con RAG vs sin RAG», como variable secundaria |
| M6 | **API mínima del prototipo** | modelo de datos (hecho) | Endpoints del flujo científico, sin CRUD administrativo |
| M7 | **Memoria: capítulos 4, 5 y 6** | M1, M4, M5 | Texto redactado con cifras trazables a artefactos |
| M8 | **Guía de reproducción + limpieza del repositorio** | — | Un tercero levanta el sistema y reproduce un experimento |
| M9 | **Presentación de defensa + demo grabada** | M6 | Guion + vídeo de respaldo |

### SHOULD HAVE — mejora sustancialmente la defensa

| ID | Tarea | Depende de | Riesgo si falta |
|---|---|---|---|
| S1 | **A2/A3 — validación ARM64/RPi5** | hardware disponible | Sin ella, toda afirmación edge queda como `ARM64 pending` |
| S2 | **Criterio edge transversal medido** — no es un experimento propio: `pre-registro-v1` §3.4 lo aplica a *todos* | S1 | El presupuesto edge queda sin verificar |
| S3 | **HCRL — descarga, auditoría y replay** | — | Validez externa nula; el hallazgo del LTFT queda como propiedad del emulador |
| S4 | **Serie confirmatoria mínima** | M2 | Todo el trabajo permanece exploratorio |
| ~~S5~~ | ~~Merge controlado de `backup-alineacion-cientifica`~~ | — | **Promovido a M0**: es prerrequisito de la memoria (§10.1.1) |
| S7 | **Corregir `peak_rss_mb()` fuera de Linux** | — | Cifras de memoria erróneas ×1024 en H4 |

### OPTIONAL — solo si sobra tiempo tras MUST + SHOULD

| ID | Tarea | Nota |
|---|---|---|
| O1 | UI web ligera | Solo si aporta a la demo; **no reactivar Flutter** |
| O2 | Brazo C de H2: RAG + reranking | Únicamente si el baseline lo justifica |
| O3 | Ablation volumen vs cobertura (cierra el confound de F22) | Científicamente valiosa; no imprescindible para defender |
| O4 | D3 — evaluación XAI sobre `ae_v3` | D3 **congelado sin evaluar** por decisión del 16-08-2026; queda aquí por si sobra tiempo |

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
| **S1 · 16-22 ago** | **M0 (merge)** → M2 (F-PREREG) · **M2b (R2, fija D1)** · M3 (corpus) · S7 | **M1**: Cap. 1, 2 y 3 (Cap. 3 adaptado, no de cero) | Paquete científico en `main` · `prereg-v1.0` congelado · **D1 fijado** |
| **S2 · 23-29 ago** | **M4 (R3)** · M6 (API mínima) | Cap. 4 completo | Índice RAG con métricas descriptivas |
| **S3 · 30 ago-5 sep** | **M5 (EXP-MEM-001)** · **M5b (EXP-EXP-001)** · S3 (HCRL si llega) | Cap. 5 §2.1-2.3 | H-MEM y H-EXP respondidas |
| **S4 · 6-12 sep** | S1/S2 (edge) · S4 (confirmatorios) | Cap. 5 §2.4 y §3; Cap. 6 | Criterio edge medido o declarado pendiente |
| **S5 · 13-18 sep** | M8 (reproducibilidad) · M9 (demo) | Revisión integral · resumen/abstract | **Memoria completa** |
| **S6 · 19 sep-entrega** | Margen | Correcciones del tutor | Entrega |

## 10.5 Dependencias

```
F22 (hecho)
     │
     ↓
 M0 merge de la rama científica ───────┬──────────────┐
     │                                 │              │
     ↓                                 ↓              ↓
 M1 Cap.1-3 (Cap.3 adaptado)      M2 F-PREREG   M2b R2 → fija D1
     │                                 │              │
     │                                 ↓              ├────────────┐
     │                          S4 confirmatorios     │            │
     │                                 │              ↓            ↓
 M3 corpus ──────────────────────────────────▶  M4 R3 ──▶ M5b EXP-EXP-001
     │                                 │              │            │
     │                                 │         M5 EXP-MEM-001 ───┤
     │                                 │              │            │
 S1 A2/A3 ──▶ S2 criterio edge         │              │            │
     │                                 │              │            │
 M6 API ─────────────────────▶  M7 Cap.4-6  ◀─────────┴────────────┘
                                       │
                                       ↓
                              M8 reproducibilidad
                                       ↓
                                M9 defensa · ENTREGA
```

Camino crítico: **M0 → M1 / M2b → M4 → M5·M5b → M7 → M8 → M9**.

Dos cambios importantes respecto a la primera versión: **M0 (el merge) encabeza todo**,
porque de él dependen tanto la memoria como el pre-registro; y **M2b (R2) entra en el camino
crítico**, porque el pre-registro global condiciona EXP-MEM-001, EXP-EXP-001 y EXP-MAS-001 a
que D1 esté fijado, y R2 lleva preparado sin ejecutar desde F9.

Todo lo que dependa de hardware (S1, S2) o de terceros (S3) sigue **fuera** del camino
crítico a propósito: el TFM no puede quedar bloqueado esperando una Raspberry Pi.

## 10.6 Decisiones abiertas que condicionan este cronograma

1. **Extensión de la memoria — ABIERTA, y es la que más condiciona este plan.** La plantilla
   exige 50 000–60 000 palabras y a la vez recomienda 31–73 páginas por capítulo
   (≈ 12 000–29 000 palabras): un factor de 2 a 4 de diferencia. **Hay que preguntar al
   tutor.** Mientras tanto se planifica en modo contingencia: se redacta primero el núcleo
   defendible (≈ 25 000 palabras) y cada capítulo marca qué apartados se ampliarían si el
   tutor confirma las 50 000. Si se confirman, hay que recortar antes en §10.3 —
   previsiblemente O1-O4 completos y probablemente S2 y S4.
3. ~~**D3 (XAI).**~~ **RESUELTA** (16-08-2026): D3 se congela **sin evaluar**, dejando
   constancia expresa de que su precondición se cumplió y no se aprovechó, para que no se
   lea como que se evaluó y salió mal.
4. **Tutor — ABIERTA.** No consta asignado en la documentación del proyecto. Es un
   bloqueante administrativo con plazo, no técnico, y de él depende también la decisión 1.

