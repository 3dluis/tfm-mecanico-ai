"""Evaluación práctica de ELM327-emulator + python-OBD (Fase 1, tarea F1.3).

Comprueba empíricamente:
  E1. Arranque del emulador en proceso y obtención de un pty (transporte serie virtual).
  E2. Conexión de python-OBD al pty y handshake ELM327 (ATZ, ATE0, protocolo).
  E3. Cobertura de PIDs del subconjunto definido en docs/03 (§3.1).
  E4. Inyección dinámica de valores en caliente (mecanismo `answer` / ObdMessage).
  E5. Lectura de DTCs (modo 03).
  E6. Transporte TCP (socket) como alternativa al pty.
  E7. Latencia media de consulta por PID.

Salida: informe JSON por stdout (consumido por docs/adr/0003).
"""

from __future__ import annotations

import json
import socket
import statistics
import time
from typing import Any

RPM_INYECTADA = 2000.0
MIN_MUESTRAS_P95 = 2
RESULTS: dict[str, Any] = {}

# ----------------------------------------------------------------------------- E1
from elm import Elm  # noqa: E402

session = Elm(batch_mode=True)
session.__enter__()  # arranca el hilo del emulador (equivalente a `with Elm() as session`)
pty_port = session.get_pty()
time.sleep(1.5)
RESULTS["E1_pty"] = {"ok": pty_port is not None, "port": str(pty_port)}
RESULTS["emulator_version"] = getattr(session, "version", "desconocida")
RESULTS["scenario"] = session.scenario

# ----------------------------------------------------------------------------- E2
import obd  # noqa: E402

obd.logger.setLevel("CRITICAL")
conn = obd.OBD(pty_port, fast=False, timeout=1.0)
RESULTS["E2_conexion"] = {
    "ok": conn.is_connected(),
    "protocolo": conn.protocol_name(),
    "num_pids_soportados": len(conn.supported_commands),
}

# ----------------------------------------------------------------------------- E3
SUBSET = [
    "RPM",
    "SPEED",
    "COOLANT_TEMP",
    "ENGINE_LOAD",
    "MAF",
    "SHORT_FUEL_TRIM_1",
    "LONG_FUEL_TRIM_1",
    "O2_B1S1",
    "TIMING_ADVANCE",
    "INTAKE_TEMP",
    "THROTTLE_POS",
    "INTAKE_PRESSURE",
    "CONTROL_MODULE_VOLTAGE",
    "FUEL_LEVEL",
]
cobertura: dict[str, Any] = {}
latencias: list[float] = []
for name in SUBSET:
    cmd = getattr(obd.commands, name, None)
    if cmd is None:
        cobertura[name] = {"soportado": False, "motivo": "PID no definido en python-OBD"}
        continue
    t0 = time.perf_counter()
    rsp = conn.query(cmd, force=True)
    dt = (time.perf_counter() - t0) * 1000
    ok = rsp is not None and not rsp.is_null()
    if ok:
        latencias.append(dt)
    cobertura[name] = {
        "soportado": ok,
        "valor": str(rsp.value) if ok else None,
        "latencia_ms": round(dt, 1),
    }
RESULTS["E3_cobertura_pids"] = cobertura
RESULTS["E3_resumen"] = {
    "pids_ok": sum(1 for v in cobertura.values() if v["soportado"]),
    "pids_total": len(SUBSET),
}

# ----------------------------------------------------------------------------- E4
# Mecanismo 1: diccionario `answer` (respuesta fija por comando, en caliente).
inyeccion: dict[str, Any] = {}
try:
    rpm_antes = conn.query(obd.commands.RPM, force=True)
    # 0C = PID de RPM; valor = (A*256+B)/4 -> 0x1F40 = 8000/4 = 2000 rpm.
    # La clave del dict `answer` es el nombre de la entrada en ObdMessage ("RPM"),
    # y el formato de respuesta usa las etiquetas XML del emulador (verificado F1.3).
    session.answer["RPM"] = "<header>7E8</header><size>04</size><data>41 0C 1F 40</data>"
    time.sleep(0.3)
    rpm_despues = conn.query(obd.commands.RPM, force=True)
    del session.answer["RPM"]
    inyeccion["mecanismo_answer"] = {
        "ok": (not rpm_despues.is_null()) and rpm_despues.value.magnitude == RPM_INYECTADA,
        "antes": str(rpm_antes.value),
        "despues": str(rpm_despues.value),
    }
except Exception as exc:
    inyeccion["mecanismo_answer"] = {"ok": False, "error": repr(exc)}

# Mecanismo 2: edición de ObdMessage (plantillas con Python evaluado).
try:
    from elm import ObdMessage  # inspección de estructura

    escenarios = list(ObdMessage.keys())
    ejemplo = ObdMessage["default"].get("ELM_VERSION", {})
    inyeccion["mecanismo_obdmessage"] = {
        "ok": True,
        "escenarios_disponibles": escenarios,
        "claves_de_una_entrada": list(ejemplo.keys()),
    }
except Exception as exc:
    inyeccion["mecanismo_obdmessage"] = {"ok": False, "error": repr(exc)}
RESULTS["E4_inyeccion_dinamica"] = inyeccion

# ----------------------------------------------------------------------------- E5
try:
    dtc = conn.query(obd.commands.GET_DTC, force=True)
    RESULTS["E5_dtc"] = {"ok": dtc is not None, "valor": str(dtc.value)}
except Exception as exc:
    RESULTS["E5_dtc"] = {"ok": False, "error": repr(exc)}

# ----------------------------------------------------------------------------- E7
RESULTS["E7_latencia"] = {
    "media_ms": round(statistics.mean(latencias), 1) if latencias else None,
    "p95_ms": round(sorted(latencias)[int(0.95 * len(latencias)) - 1], 1)
    if len(latencias) >= MIN_MUESTRAS_P95
    else None,
    "muestras": len(latencias),
}

conn.close()
session.terminate()

# ----------------------------------------------------------------------------- E6
tcp: dict[str, Any] = {}
try:
    net_session = Elm(batch_mode=True, net_port=35000)
    net_session.__enter__()  # hilo
    time.sleep(1.5)
    with socket.create_connection(("127.0.0.1", 35000), timeout=3) as sk:
        sk.sendall(b"ATZ\r")
        time.sleep(0.8)
        banner = sk.recv(1024).decode(errors="replace")
        sk.sendall(b"010C\r")
        time.sleep(0.8)
        rpm_raw = banner + sk.recv(1024).decode(errors="replace")
    tcp = {
        # El eco y el banner pueden llegar repartidos entre lecturas; se evalúa el conjunto.
        "ok": "ELM327" in rpm_raw and "41 0C" in rpm_raw.replace("410C", "41 0C"),
        "banner": banner.strip()[:60],
        "respuesta_010C": rpm_raw.strip()[:80],
    }
    net_session.terminate()
except Exception as exc:
    tcp = {"ok": False, "error": repr(exc)}
RESULTS["E6_tcp"] = tcp

print(json.dumps(RESULTS, indent=2, ensure_ascii=False, default=str))
