# Tres tipos de fallo experimental (F19) — extensión del Protocolo ML v1

**Estado: VIGENTE · 2026-08-14 · extiende el [Protocolo Experimental ML v1](protocolo_ml_v1.md)
sin modificarlo · motivado por EXP-ANOM-007/008/009 y verificado por AUDIT-DATA-001**

Cuatro iteraciones consecutivas de la línea ML atribuyeron un mismo resultado negativo
(«el detector no detecta») a causas distintas y sucesivamente refutadas: volumen de
datos, capacidad del modelo, regularización, representación de features y memoria
temporal. La auditoría F19 mostró que dos de esos resultados no eran del modelo. De ahí
esta regla: **antes de atribuir un resultado negativo, hay que decidir de qué tipo es.**

## 1. Los tres tipos

| Tipo | Definición | Cómo se demuestra |
|---|---|---|
| **model failure** | El fenómeno ES distinguible del normal con medios sencillos, y el detector no lo detecta. | Separabilidad sin modelos (AUC pareada y poblacional) claramente > azar mientras el recall del detector es bajo. |
| **dataset coverage failure** | Un comportamiento **normal** presente en evaluación falta o es raro en entrenamiento; el modelo lo marca por no haberlo visto. | Matriz de cobertura con el comportamiento ABSENT/RARE en train y presente en test + brazo control que lo cubre y corrige el FPR. |
| **anomaly construction failure** | El fenómeno **no es distinguible por construcción**: la inyección queda por debajo del ruido operativo o del paso de cuantización del sensor. | Separabilidad sin modelos ≈ azar, o `|Δ| < paso de cuantización`, o ground truth que no sobrevive al pipeline. |

Los tres son resultados legítimos y publicables. Confundirlos es lo que no es admisible:
un `recall = 0.00` sobre una anomalía indistinguible **no mide** la capacidad del
detector, y un FPR alto causado por un hueco de cobertura **no mide** la calidad del
modelo.

## 2. Orden de comprobación obligatorio

Ante cualquier resultado negativo de detección, en este orden:

1. **¿Es distinguible?** Separabilidad sin modelos entrenados (`ai_models.audit.detectability`):
   AUC pareada (mismo escenario y semilla) y AUC poblacional (frente a la normalidad de
   train), esta última **con control SHAM** para descartar que la separabilidad venga del
   escenario y no de la inyección.
2. **¿Sobrevive la inyección al pipeline?** Traza generación → cuantización J1979 →
   snapshot → matriz → ventana → features. Si el efecto desaparece en algún eslabón, el
   problema es de construcción o de preprocesado, no del modelo.
3. **¿Coincide el ground truth con lo que realmente cambia?** Si el GT declara señales que
   la inyección no toca (u omite señales que sí toca), las métricas de atribución de ese
   fallo no son interpretables tal cual.
4. **¿Está el comportamiento normal implicado representado en train?** Matriz de
   cobertura por régimen, estado térmico, carga, trims y transiciones de cuantización.
5. **Solo entonces**, atribuir a modelo o arquitectura.

## 3. Consecuencia sobre las métricas

- Un recall de una anomalía clasificada `INDISTINGUISHABLE` o `INVALID_BY_CONSTRUCTION`
  se reporta **con su clasificación al lado** y no se agrega a las medias globales sin
  declararlo.
- Un FPR asociado a un hueco de cobertura documentado se reporta como tal.
- Las métricas históricas **no se reescriben**: se añade contexto (ver la tabla de
  reinterpretación del informe F19).

## 4. Instrumentación de referencia

`ai_models.audit.detectability` (métricas y umbrales congelados),
`ai-models/experiments/e9_anomaly_audit.py` (auditoría ejecutable),
`ai-models/configs/audit-data-001.yaml` (protocolo congelado antes de medir).
