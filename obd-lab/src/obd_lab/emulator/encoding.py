"""Codificación de valores físicos a respuestas OBD-II modo 01 (SAE J1979).

Genera las respuestas hex que el emulador ELM327 devuelve por cada PID, en el formato
de entrada del emulador: ``<header>7E8</header><size>NN</size><data>41 PP …</data>``.
"""

_PID_HEX: dict[str, str] = {
    "ENGINE_LOAD": "04",
    "COOLANT_TEMP": "05",
    "SHORT_FUEL_TRIM_1": "06",
    "LONG_FUEL_TRIM_1": "07",
    "INTAKE_PRESSURE": "0B",
    "RPM": "0C",
    "SPEED": "0D",
    "TIMING_ADVANCE": "0E",
    "INTAKE_TEMP": "0F",
    "MAF": "10",
    "THROTTLE_POS": "11",
    "O2_B1S1": "14",
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def encode_pid(pid: str, value: float) -> tuple[str, str]:
    """Devuelve (patrón_request_regex, respuesta_emulador) para un PID y valor físico."""
    code = _PID_HEX[pid]
    if pid == "RPM":
        raw = int(_clamp(value, 0, 16383.75) * 4)
        data = f"41 {code} {raw >> 8:02X} {raw & 0xFF:02X}"
    elif pid == "SPEED":
        data = f"41 {code} {int(_clamp(value, 0, 255)):02X}"
    elif pid in ("ENGINE_LOAD", "THROTTLE_POS"):
        data = f"41 {code} {int(_clamp(value, 0, 100) * 255 / 100):02X}"
    elif pid in ("COOLANT_TEMP", "INTAKE_TEMP"):
        data = f"41 {code} {int(_clamp(value, -40, 215)) + 40:02X}"
    elif pid in ("SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1"):
        data = f"41 {code} {int(_clamp(value, -100, 99.2) * 128 / 100) + 128:02X}"
    elif pid == "INTAKE_PRESSURE":
        data = f"41 {code} {int(_clamp(value, 0, 255)):02X}"
    elif pid == "TIMING_ADVANCE":
        data = f"41 {code} {int((_clamp(value, -64, 63.5) + 64) * 2):02X}"
    elif pid == "MAF":
        raw = int(_clamp(value, 0, 655.35) * 100)
        data = f"41 {code} {raw >> 8:02X} {raw & 0xFF:02X}"
    elif pid == "O2_B1S1":
        # A = tensión/0.005 V; B = 0xFF (STFT no usado en este sensor)
        data = f"41 {code} {int(_clamp(value, 0, 1.275) / 0.005):02X} FF"
    else:  # pragma: no cover
        msg = f"PID sin codificador: {pid}"
        raise KeyError(msg)
    n_bytes = len(data.split())
    request = f"^01{code}[0-9A-F]?$"
    return request, f"<header>7E8</header><size>{n_bytes:02X}</size><data>{data}</data>"


def quantize(pid: str, value: float) -> float:
    """Aplica la cuantización de la codificación J1979 (ida y vuelta encode→decode).

    Crítico para la validez experimental: las sesiones offline deben tener la MISMA
    resolución que el camino vivo (adaptador real o emulador), o los detectores se
    entrenan con una distribución que nunca verán en inferencia (hallazgo del smoke
    F3.6: las std de PIDs casi constantes difieren en un orden de magnitud).
    """
    if pid == "RPM":
        return int(_clamp(value, 0, 16383.75) * 4) / 4.0
    if pid in ("SPEED", "INTAKE_PRESSURE"):
        return float(int(_clamp(value, 0, 255)))
    if pid in ("ENGINE_LOAD", "THROTTLE_POS"):
        return int(_clamp(value, 0, 100) * 255 / 100) * 100 / 255.0
    if pid in ("COOLANT_TEMP", "INTAKE_TEMP"):
        return float(int(_clamp(value, -40, 215)))
    if pid in ("SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1"):
        return int(_clamp(value, -100, 99.2) * 128 / 100) * 100 / 128.0
    if pid == "TIMING_ADVANCE":
        return int((_clamp(value, -64, 63.5) + 64) * 2) / 2.0 - 64.0
    if pid == "MAF":
        return int(_clamp(value, 0, 655.35) * 100) / 100.0
    if pid == "O2_B1S1":
        return int(_clamp(value, 0, 1.275) / 0.005) * 0.005
    msg = f"PID sin cuantizador: {pid}"
    raise KeyError(msg)


def quantize_tick(values: dict[str, float]) -> dict[str, float]:
    """Cuantiza todos los PIDs de un tick."""
    return {pid: quantize(pid, v) for pid, v in values.items()}
