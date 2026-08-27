# 1. Comprensión del problema

## 1.1 Contexto

Los vehículos modernos exponen información de estado a través del estándar OBD-II (On-Board Diagnostics II), obligatorio en turismos de gasolina en EE. UU. desde 1996 y en la Unión Europea (EOBD) desde 2001 (gasolina) y 2004 (diésel). OBD-II define, entre otros, los servicios de diagnóstico (SAE J1979 / ISO 15031-5), los códigos de diagnóstico de fallo o DTC (SAE J2012 / ISO 15031-6) y el conector físico (SAE J1962). Sobre esta interfaz pueden leerse parámetros en tiempo real (PID): régimen del motor, temperatura del refrigerante, ajustes de combustible (fuel trims), carga calculada, tensión de sensores de oxígeno, etc.

El diagnóstico convencional presenta tres carencias que motivan este trabajo:

1. **Reactividad.** Los DTC se generan cuando un umbral de fallo ya se ha superado; el testigo MIL se enciende cuando el problema existe, no cuando se está gestando. La degradación progresiva (p. ej., deriva de un sensor MAF, empobrecimiento gradual de mezcla) no produce códigos hasta fases avanzadas.
2. **Opacidad para el usuario.** Un DTC (p. ej., `P0171 – System Too Lean, Bank 1`) identifica un síntoma, no una causa, y su interpretación exige conocimiento experto: el mismo código puede deberse a una fuga de vacío, un MAF sucio, baja presión de combustible o una sonda lambda degradada.
3. **Conocimiento disperso y no acumulativo.** La relación entre patrones de señales y causas raíz está repartida entre manuales de taller, boletines técnicos de servicio y experiencia de mecánicos, sin que las herramientas de diagnóstico habituales acumulen ni reutilicen los casos ya resueltos.

## 1.2 Problema

**Las herramientas de diagnóstico accesibles al usuario final no explican sus conclusiones de forma verificable, y los asistentes basados en modelos de lenguaje producen explicaciones fluidas cuya relación con la evidencia disponible no puede comprobarse ni tiene por qué existir.**

Los escáneres comerciales leen y borran códigos sin justificar nada. Las plataformas telemáticas de flota centralizan datos pero aplican reglas predefinidas. Los asistentes basados exclusivamente en modelos de lenguaje carecen de anclaje en los datos reales del vehículo y en la documentación técnica: pueden producir una explicación plausible tanto cuando la documentación la respalda como cuando no existe documentación alguna sobre el caso, y nada en la salida permite distinguir ambas situaciones. Ese es el problema que este TFM aborda: no la ausencia de explicación, sino la **imposibilidad de comprobar si una explicación está sostenida**, y la ausencia de un comportamiento definido cuando no lo está.

Dos consecuencias delimitan el trabajo:

1. Una explicación diagnóstica solo es defendible si cada afirmación puede rastrearse hasta una evidencia concreta —un fragmento del corpus técnico o una comprobación sobre la telemetría—, y esa correspondencia debe **verificarse**, no declararse.
2. Cuando la evidencia disponible no sostiene ninguna explicación, la salida correcta no es una hipótesis plausible: es declarar la insuficiencia. Un sistema que completa los huecos transmite al usuario una confianza injustificada, y es más peligroso que uno que no responde.

## 1.3 Pregunta de investigación

> **PI (v4, oficial desde el 27-ago-2026):** ¿Puede un agente con RAG explicar el
> diagnóstico de un vehículo a partir de datos OBD-II reales, rastreando cada explicación
> hasta su evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente
> para sostener una explicación en lugar de generar una hipótesis sin fundamento?

*Especificación metodológica (fuera del enunciado):* el sistema se implementa mediante un agente sobre un grafo explícito, recuperación documental sobre un corpus con manifiesto, un modelo de lenguaje pequeño ejecutado localmente, un verificador determinista y una política de abstención, sobre la arquitectura Edge–Cloud construida en las fases anteriores. Los mecanismos son medios: la refutación de una hipótesis parcial no invalida la PI, la responde.

La investigación estudia la cadena «observar → contextualizar → diagnosticar → recuperar evidencia → verificar el soporte → explicación trazable o abstención», con las subpreguntas PI.a–PI.f detalladas en la fuente canónica [`docs/alineacion_v4/01_nucleo_cientifico.md`](alineacion_v4/01_nucleo_cientifico.md).

**Historia de la PI.** Esta formulación sustituye a la PI v3 (18-ago-2026), centrada en identificar patrones no representados, generar hipótesis, validarlas e incorporarlas como conocimiento reutilizable. El cambio, acordado con el tutor, acota el alcance a un tramo ejecutable dentro del plazo del TFM y conserva todo el trabajo previo. La evolución completa v1 → v4 y su justificación están en [`docs/alineacion_v4/04_historial_pi.md`](alineacion_v4/04_historial_pi.md); lo que sale del alcance experimental, en [`05_fuera_de_alcance.md`](alineacion_v4/05_fuera_de_alcance.md).

**Definiciones operativas.** El trabajo distingue con un único significado **dato**, **evidencia**, **diagnóstico**, **explicación**, **afirmación**, **hipótesis** (objeto interno del proceso, nunca un resultado) y **abstención** (salida correcta, no fallo). Tabla completa en el núcleo científico §2. La condición de **evidencia insuficiente** no se simula: se construye retirando del corpus recuperable, con manifiesto y checksum verificados, los documentos que describen el mecanismo evaluado.

## 1.4 Hipótesis de trabajo

La hipótesis integradora contrasta directamente la PI; cuatro subordinadas aíslan mecanismos. Formulación completa, criterios de apoyo/refutación/no-concluyente y umbrales: núcleo científico §5 y [`03_diseno_experimental.md`](alineacion_v4/03_diseno_experimental.md) §4.

- **H-MAIN (integradora):** con la cobertura del corpus controlada experimentalmente, el agente podrá producir una explicación correcta cuando la evidencia esté disponible, mantener cada afirmación relevante rastreable hasta una evidencia concreta, no introducir afirmaciones sin soporte y declarar evidencia insuficiente cuando el corpus no la contenga. Co-primarias Q1–Q5.
- **H-GRD (soporte):** recuperar evidencia y verificar el soporte de cada afirmación reduce las afirmaciones no sustentadas frente a generar la explicación sin evidencia o sin verificarla.
- **H-TRC (trazabilidad):** la correspondencia afirmación→evidencia→dato que produce el sistema es efectiva —las referencias resuelven y su contenido sostiene la afirmación— por encima de una atribución posicional trivial.
- **H-ABS (abstención):** ante evidencia deliberadamente retirada del corpus el sistema declara insuficiencia en lugar de explicar, con una tasa de falsa abstención acotada cuando la evidencia sí está.
- **H-SEL (exactitud selectiva):** la abstención mejora la exactitud sobre los casos no abstenidos sin reducir la cobertura por debajo del mínimo pre-registrado.
- **Criterio transversal edge** (no es hipótesis): latencia, RAM y coste de tokens dentro del presupuesto pre-registrado; una configuración que lo viole se declara no viable aunque gane en calidad.

**Hipótesis retiradas del contraste principal**, con su diseño conservado y sin ejecutar: H-MEM (memoria validada) y H-MAS (multiagente) pasan a trabajo futuro; H-EVT y H-PERS pasan a línea instrumental sobre la calidad del contexto diagnóstico y no condicionan la respuesta a la PI. Correspondencia con las históricas H1–H4 y con la nomenclatura v3: `docs/correspondencia_nomenclatura.md` y núcleo científico §11.

Las hipótesis son falsables, sus umbrales se congelan mediante la enmienda ENM-001 del pre-registro antes de ejecutar, y los resultados negativos se publican con el mismo detalle.

## 1.5 Usuarios y casos de uso previstos

1. **Conductor particular:** recibe avisos tempranos y explicaciones comprensibles ("el ajuste de combustible a largo plazo lleva 3 semanas subiendo; patrón compatible con fuga de vacío; severidad media; revisar antes de 1000 km").
2. **Taller pequeño:** usa el historial y las hipótesis del agente como apoyo pre-diagnóstico.
3. **Investigación:** el sistema como banco de pruebas de agentes LLM con memoria en dispositivos de recursos limitados.

El caso 1 es el que guía el diseño del prototipo; los otros dos se declaran como contexto.
