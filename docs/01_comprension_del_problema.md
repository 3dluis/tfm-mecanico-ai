# 1. Comprensión del problema

## 1.1 Contexto

Los vehículos modernos exponen información de estado a través del estándar OBD-II (On-Board Diagnostics II), obligatorio en turismos de gasolina en EE. UU. desde 1996 y en la Unión Europea (EOBD) desde 2001 (gasolina) y 2004 (diésel). OBD-II define, entre otros, los servicios de diagnóstico (SAE J1979 / ISO 15031-5), los códigos de diagnóstico de fallo o DTC (SAE J2012 / ISO 15031-6) y el conector físico (SAE J1962). Sobre esta interfaz pueden leerse parámetros en tiempo real (PID): régimen del motor, temperatura del refrigerante, ajustes de combustible (fuel trims), carga calculada, tensión de sensores de oxígeno, etc.

El diagnóstico convencional presenta tres carencias que motivan este trabajo:

1. **Reactividad.** Los DTC se generan cuando un umbral de fallo ya se ha superado; el testigo MIL se enciende cuando el problema existe, no cuando se está gestando. La degradación progresiva (p. ej., deriva de un sensor MAF, empobrecimiento gradual de mezcla) no produce códigos hasta fases avanzadas.
2. **Opacidad para el usuario.** Un DTC (p. ej., `P0171 – System Too Lean, Bank 1`) identifica un síntoma, no una causa, y su interpretación exige conocimiento experto: el mismo código puede deberse a una fuga de vacío, un MAF sucio, baja presión de combustible o una sonda lambda degradada.
3. **Conocimiento disperso y no acumulativo.** La relación entre patrones de señales y causas raíz está repartida entre manuales de taller, boletines técnicos de servicio y experiencia de mecánicos, sin que las herramientas de diagnóstico habituales acumulen ni reutilicen los casos ya resueltos.

## 1.2 Problema

**No existe, en el ámbito del diagnóstico accesible al usuario final, un sistema que combine (a) análisis continuo de series temporales OBD-II en el borde (edge), (b) detección de anomalías no supervisada capaz de señalar comportamientos degradados sin DTC asociado, (c) razonamiento explicable apoyado en documentación técnica, y (d) acumulación de experiencia diagnóstica a lo largo del tiempo.**

Los escáneres comerciales leen y borran códigos; las plataformas telemáticas de flota centralizan datos pero dependen de conectividad y reglas predefinidas; los asistentes basados exclusivamente en LLM carecen de anclaje en los datos reales del vehículo y son propensos a alucinación. El hueco que este TFM explora es la integración de estas piezas en un agente híbrido edge-cloud.

## 1.3 Pregunta de investigación

> **PI (v3, oficial desde la alineación científica v3, 2026-08-18):** ¿Puede un sistema
> inteligente híbrido identificar patrones de fallo no representados en su conocimiento
> disponible, generar hipótesis diagnósticas a partir del análisis contextual y
> longitudinal de datos OBD-II y validarlas mediante evidencia antes de incorporarlas como
> conocimiento reutilizable?

*Especificación metodológica (fuera del enunciado):* el sistema se implementa mediante aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente, modelos de lenguaje, RAG y memoria con validación, sobre una arquitectura Edge–Cloud. Los mecanismos son medios: la refutación de cualquier hipótesis parcial no invalida la PI — la responde. Historia de la PI (v1 de Fase 0; v2 «Opción B» de 12-ago) en `docs/correspondencia_nomenclatura.md` §0.

La investigación estudia la transición epistemológica «observación → contexto → anomalía → reconocimiento de conocimiento insuficiente → hipótesis → evidencia → verificación → conocimiento validado/abstención» (cadena completa y subpreguntas PI.a–PI.e en [`docs/alineacion_v3/01_nucleo_cientifico.md`](alineacion_v3/01_nucleo_cientifico.md), fuente canónica).

**Definición operacional:** un patrón de fallo está **no representado en el conocimiento disponible** cuando se cumplen simultáneamente las tres exclusiones E-DET (fuera del entrenamiento/ajuste del detector), E-RAG (fuera del corpus recuperable) y E-MEM (fuera de la memoria longitudinal) — propiedad relativa al sistema, comprobable por construcción y auditada antes de cada ejecución. Los términos «desconocido», «nuevo» o «nunca visto» no se usan como sinónimos técnicos, y no se afirmará el descubrimiento de fallos desconocidos para la ingeniería automotriz.

## 1.4 Hipótesis de trabajo

La hipótesis integradora contrasta directamente la PI; cinco subordinadas aíslan mecanismos. Formulación completa, criterios de apoyo/refutación/no-concluyente y operacionalización: núcleo científico §5.

- **H-MAIN (integradora):** bajo el protocolo held-out/open-set de exclusión triple, el sistema podrá identificar la anomalía, reconocer la insuficiencia de su conocimiento (en lugar de identificar erróneamente con confianza), generar hipótesis trazables, contrastarlas con evidencia y consolidar solo lo que satisfaga criterios de validación pre-establecidos — absteniéndose en caso contrario.
- **H-EVT:** la representación contextual por eventos mejora la detección frente a las alternativas por ventanas.
- **H-PERS:** la normalidad personalizada por vehículo reduce falsos positivos o mejora la detección.
- **H-EXP:** recuperar y contrastar evidencia mejora la exactitud factual, trazabilidad y calibración de las hipótesis frente a la generación sin evidencia o sin verificación.
- **H-MEM:** la memoria sometida a validación reduce la contaminación del conocimiento y permite reutilizar experiencias verificadas sin propagar hipótesis incorrectas (M0/M1/M2).
- **H-MAS (secundaria):** la descomposición multiagente aporta ventaja medible en alguna parte concreta de la cadena frente a alternativas más simples. **No se asume verdadera**: si el monolítico iguala, se publica como resultado.
- **Criterio transversal edge** (no es hipótesis): latencia, RAM, CPU y coste de tokens dentro del presupuesto pre-registrado; una configuración que lo viole se declara no viable aunque gane en calidad.

Correspondencia con las históricas H1–H4: `docs/correspondencia_nomenclatura.md`. Las hipótesis son falsables, sus umbrales se congelan en el pre-registro antes de ejecutar y los resultados negativos se publican con el mismo detalle.

## 1.5 Usuarios y casos de uso previstos

1. **Conductor particular:** recibe avisos tempranos y explicaciones comprensibles ("el ajuste de combustible a largo plazo lleva 3 semanas subiendo; patrón compatible con fuga de vacío; severidad media; revisar antes de 1000 km").
2. **Taller pequeño:** usa el historial y las hipótesis del agente como apoyo pre-diagnóstico.
3. **Investigación:** el sistema como banco de pruebas de agentes LLM con memoria en dispositivos de recursos limitados.

El caso 1 es el que guía el diseño del prototipo; los otros dos se declaran como contexto.
