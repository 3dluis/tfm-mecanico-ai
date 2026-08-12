# ADR-0003 — Estrategia de emulación OBD-II: ELM327-emulator + escenario propio

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 1

## Contexto

Sin vehículo ni adaptador físico, todo el desarrollo y la experimentación dependen de emular un dispositivo ELM327 con datos realistas y fallos inyectables (componente C1, riesgo R3). Se evaluaron alternativas de forma práctica en el sandbox de desarrollo el 2026-08-12; la evidencia cruda está en `docs/fase1/evidencia_emulador.json` y el script en `tools/eval_emulator.py`.

## Evaluación empírica de ELM327-emulator (v3.0.5, Ircama)

| Prueba | Resultado |
|---|---|
| E1 Arranque en proceso + pty (serie virtual) | ✅ `/dev/pts/N`; python-OBD conecta como si fuera un adaptador USB/BT-serie |
| E2 Handshake ELM327 completo con python-OBD | ✅ Protocolo ISO 15765-4 (CAN 11/500), 66 PIDs anunciados en escenario `default` |
| E3 Cobertura del subconjunto de 14 PIDs (docs/03 §3.1) | ⚠️ 9/14 en escenarios de serie; faltan fuel trims, O2_B1S1, TIMING_ADVANCE, FUEL_LEVEL como respuestas dinámicas |
| E4 Inyección dinámica en caliente | ✅ Dos mecanismos verificados: dict `answer` (respuesta puntual, p. ej. RPM→2000) y edición de `ObdMessage` + `set_sorted_obd_msg()` (p. ej. COOLANT_TEMP→100 °C) |
| E5 Lectura de DTCs (modo 03) | ✅ Responde (lista vacía en escenarios de serie; los DTC se definirán por escenario) |
| E6 Transporte TCP (`Elm(net_port=...)`) | ✅ Servidor en :35000; imprescindible para Docker (los pty no cruzan contenedores) |
| E7 Latencia por consulta | ✅ media 0,7 ms, p95 0,8 ms — sobra margen para muestreo a 1 Hz |
| Extra | El escenario `car` trae 244 entradas (incluye SHORT/LONG_FUEL_TRIM_1, TIMING_ADVANCE, O2, y DTCs por PID); las entradas soportan respuestas fijas, listas rotatorias y **lambdas Python** (`ResponseFooter`), es decir, valores computables en función del tiempo/estado |

Restricción de empaquetado: su `setup.py` usa `pkg_resources` → instalar con `setuptools<81` y `--no-build-isolation` (documentado en ADR-0001).

## Decisión

**Adoptar ELM327-emulator como capa de protocolo, gobernado por un escenario propio (`mecanico`) generado programáticamente por nuestro componente `vehicle_sim`.** El generador de escenarios construye el dict de entradas (uno por PID del subconjunto, con `ResponseFooter` dinámicos alimentados por el modelo de conducción/fallo) y lo inyecta vía `ObdMessage` + `set_sorted_obd_msg()`. Fallos y DTCs se activan en caliente con los mecanismos E4. Transportes: pty en desarrollo local, TCP dentro de Docker — exactamente las dos implementaciones previstas de `TransportLayer` (ADR-0004).

Con esto, la carencia E3 desaparece (los PIDs los define nuestro escenario) y el emulador queda reducido a lo que hace bien: el protocolo ELM327/ISO-TP fiel.

## Alternativas consideradas

- *OBDSim (obdgpslogger):* C, sin mantenimiento reciente aparente, integración Python pobre; descartado sin evaluación profunda por coste/beneficio.
- *Generador propio hablando ELM327 crudo:* control total, pero reimplementar el manejo AT/ISO-TP que el emulador ya resuelve es esfuerzo sin valor investigador; queda como **contingencia R3** si el emulador impone límites inesperados (el contrato `TransportLayer` lo permite sin tocar el resto).
- *Mock a nivel de API de python-OBD (sin protocolo):* barato, pero elimina la fidelidad de protocolo y debilita la validez del prototipo edge; se usará solo en tests unitarios.

## Consecuencias

- `vehicle_sim` tiene interfaz clara: produce escenarios (dict) y comandos de inyección de fallo; el emulador es un detalle sustituible.
- Los perfiles de conducción y modelos de fallo (IN-8) pasan a ser el trabajo central de la Fase 2 (T1).
- Los tests de integración usan pty (marcador `emulator`); CI los ejecuta en Linux sin hardware.
