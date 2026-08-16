# F-PREREG — comparación de los dos pre-registros y decisión propuesta

**16 de agosto de 2026 · pasos 1 y 2 de [F-PREREG](F-PREREG_tarea.md) · el paso 7 (tag
`prereg-v1.0`) REQUIERE LA APROBACIÓN DEL AUTOR EXPLÍCITA y no se ha ejecutado.**

## 0. Lo primero: no había que descubrir nada, había que ir a buscarlo

El pre-registro alternativo **no estaba perdido**: está en la rama
`backup-alineacion-cientifica` como `docs/experiments/pre-registro-v1.md` (v1.0-rc1, 327
líneas, ~7 500 palabras) y **nunca se fusionó a `main`**. Y el propio `PROTO-CONF-001.md`
de `main` lleva desde el 13 de agosto una nota de reconciliación fechada que ya analizaba
el conflicto y **recomendaba una salida**. F-PREREG no parte de cero: parte de una
recomendación escrita hace tres días que quedó sin ejecutar.

## 1. Los dos documentos

| | `PROTO-CONF-001.md` (main) | `pre-registro-v1.md` (rama backup) |
|---|---|---|
| Estado | PRE-REGISTRADO, no ejecutado | v1.0-rc1 PROPUESTO, no ejecutado |
| Alcance | **Solo H-EVT** | **Todas las familias**: H-EVT, H-MEM, H-MAS, H-PERS, H-EXP, H-MAIN + precondición EXP-SEG-001 |
| Extensión | 122 líneas | 327 líneas |
| Aporta en exclusiva | Manifiesto `arms-freeze-v1.json` con checksums y regla de verificación sha256 previa a ejecutar | Criterio edge transversal · plan estadístico global · protocolo anti-contaminación de retirada triple · análisis de errores · amenazas a la validez · política de resultados negativos · reglas de enmienda · tabla maestra |

## 2. Diferencias que hay que resolver

| # | Punto | `PROTO-CONF-001` | `pre-registro-v1` | Resolución propuesta |
|---|---|---|---|---|
| D-1 | Diseño del confirmatorio de H-EVT | 15 sesiones, 5 episodios | **EXP-ANOM-004** sobre `obd-lab-suite-v2`, R = 10 réplicas, 40 episodios held-out, semillas 11000–20036 | **Adoptar `pre-registro-v1`**: más potencia estadística, y ninguno se ha ejecutado, así que no hay coste de cambio |
| D-2 | Cobertura de hipótesis | Solo H-EVT | Seis familias + precondición | Adoptar `pre-registro-v1` como maestro |
| D-3 | Congelación de brazos por checksum | **Presente** (`arms-freeze-v1.json`, verificación sha256) | Ausente | **Conservar de `PROTO-CONF-001`** e incorporarlo al maestro |
| D-4 | Estatus de H4 (edge) | No cubierto | **No es hipótesis**: es un *criterio transversal* que se aplica a todos los experimentos (§3.4) | Adoptar. Afecta al cronograma (ver §4) |
| D-5 | Estatus del RAG | No cubierto | **R3 es instrumental**, con métricas IR descriptivas (hit rate, MRR, nDCG) y **sin criterio de aceptación científico**. La antigua H2 sobrevive como variable *secundaria* dentro de H-EXP (X1 vs X0) | Adoptar. Afecta al cronograma (ver §4) |
| D-6 | Dependencia común | No declarada | **Todo el programa del agente (EXP-MEM-001, EXP-EXP-001, EXP-MAS-001) requiere D1**, que lo fija R2 (smoke del SLM) | Adoptar: R2 pasa a ser el desbloqueante crítico |

**Ninguna diferencia es irreconciliable y ninguna obliga a descartar trabajo ejecutado**,
porque ninguno de los dos protocolos se ha ejecutado nunca.

## 3. Decisión propuesta (requiere la aprobación del autor)

1. **`pre-registro-v1.md` se adopta como maestro**, se fusiona a `main` y se congela.
2. **`PROTO-CONF-001.md` queda superseded** en su sección de H-EVT, **conservando** de él
   el manifiesto `arms-freeze-v1.json` y la regla de verificación previa a ejecutar, que se
   incorporan al maestro. No se borra: se marca como superado, según la regla de ADRs.
3. Se crea el tag **`prereg-v1.0`**. A partir de ahí, y solo a partir de ahí, se puede
   ejecutar cualquier confirmatorio.
4. Nada de la serie EXP-ANOM-001…010-R2 se reinterpreta: sigue siendo exploratoria en su
   totalidad. `pre-registro-v1` §11 ya la trata así y fija su límite de uso.

## 4. Consecuencia para el cronograma (docs/10)

El plan que redacté antes de leer esta rama trataba H2, H3 y H4 como tres experimentos
paralelos. **El diseño pre-registrado dice otra cosa**, y prevalece:

| Lo que decía mi cronograma | Lo que dice el pre-registro |
|---|---|
| M4 «EXP-RAG-001 (H2), brazos A/B» | **R3 es instrumental**, no contrasta hipótesis. El contraste vive en **EXP-EXP-001** (X0 / X1 / X2), donde «con RAG vs sin RAG» es secundaria |
| M5 «EXP-MEM-001 (H3), definir métricas antes de ejecutar» | **EXP-MEM-001 ya está pre-registrado**: brazos M0/M1/M2, 20 secuencias, Δexactitud ≥ +0.10 abs., −50 % rel. de consolidaciones erróneas, semillas 55000 y 30040–30079. No hay que diseñarlo: hay que ejecutarlo |
| «H4 — benchmark de recursos en edge» | **Criterio transversal edge**, aplicable a todos los experimentos, no un experimento propio |
| — | **R2 (smoke del SLM) fija D1 y bloquea EXP-MEM-001, EXP-EXP-001 y EXP-MAS-001.** Está preparado desde F9 y nunca se ejecutó |

**Reordenación que se deriva:** `R2 → R3 → EXP-EXP-001 / EXP-MEM-001`, con el criterio edge
aplicado transversalmente. R2 sube a MUST y a primera posición del camino crítico: sin él no
hay nada del lado del agente.

Diseñar un `EXP-RAG-001` nuevo por mi cuenta habría creado un experimento paralelo que
contradice el pre-registro. No se hace.

## 5. Lo que queda pendiente de ti

- [ ] Aprobar la adopción de `pre-registro-v1` como maestro (§3).
- [ ] Aprobar el merge controlado de la rama (ver el informe de estado: hay mucho más que el
      pre-registro en ella).
- [ ] Aprobar la creación del tag `prereg-v1.0`.
- [ ] Confirmar la reordenación del cronograma de §4.

Hasta que apruebes, **no se ejecuta ningún confirmatorio** y el tag no se crea.
