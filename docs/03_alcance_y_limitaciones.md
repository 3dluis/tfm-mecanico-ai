# 3. Alcance y limitaciones

## 3.1 Dentro del alcance

**Datos y dominio**
- Protocolo OBD-II estándar (SAE J1979): PIDs del modo 01 (datos en tiempo real), modo 03 (DTC almacenados) y modo 09 (información del vehículo). Subconjunto de 10–20 PIDs relevantes para motor de gasolina (RPM, carga, temperatura refrigerante, MAF/MAP, fuel trims corto/largo plazo, sensores O2, avance de encendido, velocidad, tensión de batería, temperatura de admisión).
- Series temporales generadas por el emulador ELM327 con escenarios de conducción y fallos inyectados; datasets públicos de OBD-II como complemento para validación de la detección de anomalías (previa verificación de disponibilidad y licencia, véase `06_investigacion_y_datasets.md`).

**Plataforma**
- Entorno edge emulado: contenedor Docker `linux/arm64` (vía QEMU/binfmt) para validar compatibilidad binaria, y contenedor con límites de CPU/RAM (`--cpus`, `--memory`) equivalentes a Raspberry Pi 5 8 GB para las mediciones de rendimiento.
- Emulador OBD-II por software (categoría ELM327-emulator) conectado por puerto serie virtual (pty) o TCP. La capa de transporte del módulo de adquisición será intercambiable (`serial | tcp | bluetooth-rfcomm`), de modo que el paso a un adaptador Bluetooth real sea un cambio de configuración, no de código.

**Inteligencia**
- Detección de anomalías no supervisada (mínimo dos técnicas comparadas) sobre ventanas deslizantes de PIDs.
- LLM local pequeño (rango 1–4 B parámetros cuantizado, servido con Ollama) para el agente; se permite un LLM mayor vía API cloud como *baseline* de comparación, siempre etiquetado como componente cloud del sistema híbrido.
- RAG con base vectorial local (ChromaDB) y embeddings de sentence-transformers multilingües compactos.
- Memoria de casos persistente (episódica) con recuperación por similitud.
- Agente LangGraph con herramientas: lectura de telemetría, consulta DTC, búsqueda RAG, búsqueda en memoria, registro de caso.

**Interfaz**
- API REST FastAPI con documentación OpenAPI.
- Interfaz mínima de visualización (web simple o Flutter reducido según cronograma).

## 3.2 Fuera del alcance (exclusiones explícitas)

1. Lectura de buses propietarios del fabricante (UDS/ISO 14229, CAN raw más allá de OBD-II estándar).
2. Actuación sobre el vehículo (escritura, borrado de DTC en vehículo real, control de actuadores).
3. Vehículos eléctricos e híbridos (los PIDs relevantes difieren sustancialmente).
4. Certificación o uso en producción; el sistema es un prototipo de investigación y así se declarará ante el usuario final ("no sustituye el diagnóstico profesional").
5. Entrenamiento o fine-tuning de LLM; solo inferencia con modelos preentrenados.
6. Multiusuario, autenticación avanzada y seguridad de nivel producción en la API.
7. App móvil completa con distribución (queda como OS1).

## 3.3 Limitaciones (declaradas, no eliminables en este TFM)

**L1 — Validación sobre datos emulados/sintéticos.** La principal limitación metodológica: los fallos se inyectan según modelos de fallo definidos por el autor a partir de los trabajos revisados y de documentación técnica, no se observan en vehículos reales. Las conclusiones sobre detección "temprana" son válidas dentro del entorno emulado; su transferencia a vehículos reales queda como trabajo futuro. Esta limitación se mitigará parcialmente validando la capa de detección también sobre al menos un dataset público con datos reales.

**L2 — Rendimiento medido en emulación.** QEMU no reproduce fielmente el rendimiento de la CPU ARM real (suele ser más lento en emulación de instrucciones y no modela la microarquitectura del Cortex-A76). Las mediciones se harán en contenedor con límites de recursos y se reportarán como *cota aproximada*, declarando el método. Si se consigue una Raspberry Pi física antes de la entrega, se repetirán las mediciones clave.

**L3 — Bluetooth no emulado.** No se validará la pila Bluetooth real (emparejamiento, RFCOMM, pérdidas de conexión). Se valida la lógica de adquisición sobre transporte serie/TCP y se documenta el diseño para BT.

**L4 — Corpus RAG restringido.** Los manuales de taller de fabricantes están protegidos por derechos de autor; el corpus se limitará a documentación de licencia compatible (descripciones estándar de DTC, material técnico libre, documentación generada). La calidad del RAG está acotada por este corpus y se declarará.

**L5 — Evaluación de explicaciones parcialmente subjetiva.** La calidad de una explicación diagnóstica no tiene métrica objetiva única. Se usará rúbrica definida a priori y, si se emplea LLM-as-judge, se declararán sus sesgos conocidos y se contrastará una muestra manualmente.

**L6 — Tamaño del LLM local.** Los modelos de 1–4 B cuantizados tienen capacidades de razonamiento limitadas; parte del diseño (salidas estructuradas, descomposición del razonamiento en nodos del grafo, RAG) existe precisamente para compensarlo. Aun así, habrá casos que un modelo mayor resolvería y el local no; el experimento comparativo edge vs. cloud lo cuantificará.

**L7 — Plazo.** Con entrega en septiembre de 2026, el margen para iteraciones experimentales es de una sola pasada completa más correcciones. No hay holgura para rehacer experimentos de gran escala.

## 3.4 Supuestos

- S1: El emulador ELM327 elegido cubre los PIDs del subconjunto definido o permite extenderlos (verificación en la Fase 1).
- S2: Existe al menos un dataset público de OBD-II con datos reales utilizables para validar la detección (verificación en la Fase 1; candidatos listados en `06`).
- S3: Un modelo de 1–4 B cuantizado alcanza calidad mínima de generación estructurada en español o inglés técnico (verificación temprana en la Fase 2; si falla, el plan B es usar el LLM cloud como generador y degradar el rol del LLM local a clasificación/plantillas, documentando el hallazgo como resultado).
