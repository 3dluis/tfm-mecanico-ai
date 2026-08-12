"""Runner del pipeline inicial del edge (iteración F3, ADR-0011).

    adquisición → normalización → almacenamiento local → features → detección

El razonamiento LLM queda deliberadamente FUERA del camino crítico en esta iteración:
las anomalías se persisten y quedan listas para que el agente (fase siguiente) las
consuma como ``DetectedAnomaly``.
"""

import logging
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from diagnostic_agent.acquisition.client import AcquisitionClient
from diagnostic_agent.acquisition.transport import TransportConfig
from diagnostic_agent.detection.detector import OnnxDetector, make_anomaly
from diagnostic_agent.storage.db import AnomalyRow, EdgeStore, ReadingRow
from diagnostic_agent.telemetry.windows import WindowBuilder
from mecanico_contracts import DetectedAnomaly
from mecanico_contracts.features import feature_vector

logger = logging.getLogger(__name__)


def run_pipeline(
    transport: TransportConfig,
    model_package: Path,
    db_path: str | Path,
    duration_s: float,
    sample_rate_hz: float = 1.0,
    vehicle_id: str = "veh-local",
    device_id: str = "dev-local",
    warmup_windows: int = 2,
) -> dict[str, object]:
    """Ejecuta el pipeline durante ``duration_s`` y devuelve un resumen medible."""
    detector = OnnxDetector(model_package)
    manifest = detector.manifest
    store = EdgeStore(db_path)
    windows = WindowBuilder(size=manifest.window_size, stride=manifest.window_stride)

    session_id = str(uuid.uuid4())
    store.start_session(session_id, vehicle_id, device_id, datetime.now(tz=UTC), sample_rate_hz)

    client = AcquisitionClient(transport, vehicle_id, device_id)
    if not client.connect():
        msg = f"sin conexión OBD via {transport.portstr}"
        raise ConnectionError(msg)

    anomalies: list[DetectedAnomaly] = []
    ticks = 0
    expected = int(duration_s * sample_rate_hz)
    missing_readings = 0
    scoring_ms: list[float] = []

    try:
        for readings in client.stream(sample_rate_hz, max_ticks=expected):
            ticks += 1
            missing_readings += max(0, len(client.pids) - len(readings))
            store.add_readings(session_id, readings)
            window = windows.push_tick(readings)
            if window is None:
                continue
            # Gating de calentamiento: las primeras ventanas del viaje contienen el
            # transitorio térmico/de arranque (cola del 1% del umbral) y producirían
            # falsas alarmas sistemáticas. Los monitores OBD reales también exigen
            # condiciones estables antes de evaluar (documentado en ADR-0011).
            if windows._emitted <= warmup_windows:
                continue
            t0 = time.perf_counter()
            vec = feature_vector(window)
            score, contrib = detector.score(vec)
            scoring_ms.append((time.perf_counter() - t0) * 1000)
            if score > manifest.decision_threshold:
                anomaly = make_anomaly(
                    detector.kind,
                    score,
                    manifest.decision_threshold,
                    contrib,
                    vec,
                    vehicle_id,
                    window_id=f"{session_id}:{ticks}",
                    model_name=manifest.name,
                    model_version=manifest.version,
                )
                store.add_anomaly(session_id, anomaly)
                anomalies.append(anomaly)
                logger.info(
                    "ANOMALÍA t=%ss score=%.4f (thr=%.4f) PIDs=%s",
                    ticks,
                    score,
                    manifest.decision_threshold,
                    anomaly.involved_pids,
                )
    finally:
        client.close()

    total_readings = store.count(ReadingRow)
    return {
        "session_id": session_id,
        "ticks": ticks,
        "readings_stored": total_readings,
        "reading_loss_pct": round(100 * missing_readings / (ticks * len(client.pids)), 2),
        "windows_scored": len(scoring_ms),
        "anomalies": len(anomalies),
        "anomalies_stored": store.count(AnomalyRow),
        "anomaly_ticks": [a.window_id.split(":")[1] for a in anomalies],
        "mean_scoring_ms": round(sum(scoring_ms) / len(scoring_ms), 2) if scoring_ms else None,
        "model": f"{manifest.name}-{manifest.version}",
    }
