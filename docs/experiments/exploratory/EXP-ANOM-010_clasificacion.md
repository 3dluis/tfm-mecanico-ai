# EXP-ANOM-010 — Clasificación: EXPLORATORY (F21)

**Decisión del autor (aprobación de F21):** exploratorio bajo el Protocolo ML v1 + Adenda
XAI v1. Ninguna semilla reservada; arms-freeze-v1 intacto; el test histórico no se toca.
**Validez declarada: entorno emulado/sintético** — HCRL y ARM64/RPi5 siguen pendientes.

## Inventario de decisiones

**Existían ANTES de ejecutar (commit `ac7b353`, previo al run):**

- **HX-ML-4** enunciada de forma falsable con su criterio de refutación
  (`configs/exp-anom-010.yaml` + pre-especificación en prosa).
- **Criterios numéricos de D1** (PROMOTE_CANDIDATE / PARTIAL / REJECT) con los umbrales
  exactos, incluida la comparación contra el LOF congelado (0.6448).
- **Cuatro predicciones falsables**, una de ellas **negativa** (P3: la cobertura NO
  arreglará las anomalías lentas) y una de **integridad** (P4: el LOF congelado debe
  reproducir F18 exactamente, o se detiene el experimento).
- **Banco congelado por hash** antes de ejecutar (`synthetic-benchmark-v2`,
  `e2cdb79f96239b26…`); el runner aborta si los datos no coinciden.
- **Regla de parada** en dos ramas: (a) deriva de pipeline ⇒ no se interpretan los brazos;
  (b) D1 = REJECT ⇒ informe de causa, sin añadir capacidad, arquitecturas ni datos.
- Composición de brazos con **cambio único** entre `ae_v11` y `ae_v2`: los datos de train.

**Tomadas DURANTE la ejecución (ninguna afecta al ajuste ni a los criterios):**

- Contenido del informe de causa: qué se mide para diagnosticar (features dominantes del
  error, distancias a cada conjunto normal en unidades estandarizadas comunes, cobertura
  de nivel de LTFT por ventana y sonda Monte Carlo del mecanismo). La *obligación* de
  emitirlo estaba pre-especificada; su contenido concreto se decidió al escribirlo.
- Semilla **572** (bloque exploratorio 401-599, no gastada) para la sonda Monte Carlo del
  mecanismo. Queda registrada como gastada.
- Uso del cuantizador real del proyecto (`obd_lab.emulator.encoding.quantize`) en la sonda
  en lugar de una reimplementación con `round` — corrección de un error propio detectado
  al comparar la sonda con las sesiones reales (regla library-first, ADR-0035).

**Nada de esto se decidió después de ver métricas:** los criterios de D1 se aplicaron tal
como estaban escritos, incluido el hecho de que `ae_v2` cumple los dos criterios de F1 y
falla los dos de FPR ⇒ REJECT.

## Errores propios declarados

- Primera versión del informe de causa: calculaba el umbral de los falsos positivos con el
  train equivocado (v1.1 en vez del train del propio brazo). Detectado y corregido antes
  de fijar resultados; las cifras publicadas provienen de la versión corregida.
- Primera versión de la sonda del mecanismo: usaba `round` como cuantizador, lo que
  sobreestimaba la probabilidad de cruce (0.30-0.54 frente a 0.05-0.26 reales). Corregido
  usando el cuantizador del proyecto. La conclusión cualitativa no cambia; la cuantitativa
  sí, y por eso se rehízo la ejecución completa.

## Clasificación del resultado

`dataset coverage failure`, variante **cobertura declarada ≠ cobertura efectiva** (nueva,
incorporada a [tipos de fallo experimental](../tipos_de_fallo_experimental.md)).
No es fallo de modelo ni de construcción de anomalías.
