# Mecánico IA — Resumen ejecutivo del plan de proyecto

**Proyecto:** Sistema Inteligente Híbrido Edge-Cloud para Diagnóstico y Mantenimiento Predictivo Vehicular mediante OBD-II
**Autor:** Luis Daniel Díaz
**Documento:** Fase 0 — Base del proyecto (versión 0.1, 12 de agosto de 2026)
**Estado:** Borrador de planificación; **la estructura científica vigente es la alineación v4 (27-ago-2026)**

---

> **⚠ Núcleo científico vigente (2026-08-27, ADR-0036).** Los documentos de planificación
> `00`–`10` se conservan como registro del plan. La estructura científica del TFM es la de
> [`docs/alineacion_v4/`](alineacion_v4/01_nucleo_cientifico.md):
>
> - **Pregunta de investigación (PI v4):** ¿puede un agente con RAG explicar el diagnóstico
>   de un vehículo a partir de datos OBD-II reales, rastreando cada explicación hasta su
>   evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente para
>   sostener una explicación en lugar de generar una hipótesis sin fundamento?
> - **Cadena:** observar → contextualizar → diagnosticar → recuperar evidencia → verificar
>   el soporte → explicación trazable **o** abstención declarada.
> - **Fuera del alcance experimental:** memoria evolutiva, consolidación de conocimiento,
>   descubrimiento de fallos no representados, aprendizaje autónomo y comparación de
>   arquitecturas multiagente. Se conservan diseño y código
>   ([`05_fuera_de_alcance.md`](alineacion_v4/05_fuera_de_alcance.md)).
> - **Historia del cambio:** [`04_historial_pi.md`](alineacion_v4/04_historial_pi.md).
> - **Auditoría del impacto:** [`00_auditoria_impacto.md`](alineacion_v4/00_auditoria_impacto.md).

## 1. Propósito de este conjunto de documentos

Este directorio (`docs/`) constituye la base de planificación del TFM. Cubre los 18 puntos solicitados en el arranque del proyecto, organizados en ocho documentos:

| Documento | Contenido | Puntos cubiertos |
|---|---|---|
| `00_resumen_ejecutivo.md` | Visión general, decisiones clave y advertencias de alcance | — |
| `01_comprension_del_problema.md` | Comprensión del problema y pregunta de investigación | 1 |
| `02_objetivos.md` | Objetivos generales y específicos | 2 |
| `03_alcance_y_limitaciones.md` | Alcance, exclusiones y limitaciones | 3, 4 |
| `04_riesgos.md` | Riesgos técnicos y riesgos de investigación | 5, 13 |
| `05_arquitectura.md` | Arquitectura de alto nivel, componentes y tecnologías | 6, 7, 8 |
| `06_investigacion_y_datasets.md` | Investigaciones necesarias, datasets, contribuciones, publicaciones, innovación, investigación vs. ingeniería | 11, 12, 14, 15, 16, 17 |
| `07_cronograma_y_entregables.md` | Cronograma por fases y lista de entregables | 9, 10 |
| `08_roadmap_tecnico.md` | Roadmap técnico del prototipo | 18 |

## 2. Decisiones de contexto ya tomadas (confirmadas por el autor)

1. **Plazo de entrega: septiembre de 2026.** A fecha de este documento quedan aproximadamente 5–6 semanas de trabajo efectivo. Esta es la restricción dominante de todo el plan.
2. **Entorno de desarrollo 100 % emulado.** No hay hardware físico disponible: la Raspberry Pi se emulará mediante contenedores Docker (con imagen ARM64 para validar compatibilidad y límites de recursos para aproximar el rendimiento), y el adaptador OBD-II se sustituirá por un emulador de ELM327 por software. La conexión Bluetooth se abstraerá en una capa de transporte configurable (serie virtual / TCP), dado que emular Bluetooth real dentro de Docker no es viable de forma fiable.
3. **Documentación de trabajo en Markdown**, versionada con Git, con volcado posterior a la plantilla UAX para la memoria final.

## 3. Advertencia principal de alcance

⚠️ **El alcance descrito en la propuesta original no es realizable íntegramente en 5–6 semanas.** El plan que sigue divide el sistema en un **núcleo indispensable** (captura OBD-II emulada → detección de anomalías → agente LangGraph con RAG → diagnóstico explicable → memoria de casos) y **extensiones prescindibles** (aplicación móvil completa, sincronización cloud avanzada, despliegue en hardware real). El detalle está en `03_alcance_y_limitaciones.md` y el orden de recortes en `07_cronograma_y_entregables.md`.

La pregunta de investigación se mantiene, pero su validación experimental se acota a **patrones de fallo inyectados sintéticamente y datasets públicos**, no a fallos reales en vehículo físico. Esta acotación debe declararse explícitamente en la memoria como limitación metodológica.

## 4. Dependencias pendientes del autor

1. **Propuesta temática aprobada:** los archivos de la carpeta TFM (incluida `Propuesta temática TFM - Luis Daniel Díaz.pdf` y la plantilla UAX) están como marcadores de iCloud sin descargar y no he podido leerlos. Es necesario abrirlos una vez en Finder (o activar "Descargar ahora") para que pueda alinear este plan con la propuesta ya presentada y con los requisitos formales de la plantilla.
2. **Fecha exacta de entrega y de defensa** dentro de septiembre, para calibrar la última semana del cronograma.
3. **Aprobación de este plan** antes de iniciar la Fase 1 (estado del arte y preparación del entorno).

## 5. Método de trabajo acordado

Al final de cada fase: resumen de resultados, dudas y riesgos detectados, propuestas de mejora, y **parada hasta aprobación explícita del autor**. Ninguna fase avanza automáticamente.
