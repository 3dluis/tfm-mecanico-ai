"""Emulador ELM327 en vivo alimentado por el generador de escenarios (ADR-0010).

Levanta ELM327-emulator (pty o TCP), registra el escenario ``mecanico`` (entradas propias
para los 12 PIDs canónicos sobre la base de los escenarios de serie) y un hilo alimentador
que avanza el ``SignalEngine`` en tiempo real — con el fallo del ``ScenarioSpec`` aplicado
en su ventana — publicando cada tick las respuestas codificadas vía ``session.answer``.
"""

import threading
import time

from mecanico_contracts import ScenarioSpec
from mecanico_contracts.features import CANONICAL_PIDS
from obd_lab.emulator.encoding import encode_pid
from obd_lab.generate import iter_ticks


class LiveEmulator:
    """Ciclo de vida del emulador en vivo para un escenario dado."""

    def __init__(self, spec: ScenarioSpec, net_port: int | None = None) -> None:
        self.spec = spec
        self.net_port = net_port
        self._session = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    # ------------------------------------------------------------------ setup
    def start(self) -> str:
        """Arranca emulador + alimentador; devuelve el puerto (pty o host TCP)."""
        from elm import Elm  # import tardío: dependencia del extra [emulator]

        session = Elm(batch_mode=True, net_port=self.net_port)
        self._session = session
        session.__enter__()
        port = f"127.0.0.1:{self.net_port}" if self.net_port else session.get_pty()
        time.sleep(1.0)

        # Escenario 'mecanico': el emulador SIEMPRE re-mezcla 'default'+'AT'+escenario y
        # resuelve colisiones de Request por la clave 'Priority' (menor = gana; por
        # defecto 10). Nuestras entradas llevan Priority=1 para ganar a las de serie —
        # hallazgo del smoke F3.6: sin esto, las entradas 'default' ensombrecen las
        # nuestras y el emulador responde valores estáticos de fábrica.
        base = dict(session.ObdMessage["car"])
        for pid in CANONICAL_PIDS:
            request, response = encode_pid(pid, 0.0)
            base[f"MEC_{pid}"] = {
                "Descr": f"Mecanico IA {pid}",
                "Header": "7E0",
                "Priority": 1,
                "Request": request,
                "Response": response,
            }
        session.ObdMessage["mecanico"] = base
        session.set_sorted_obd_msg("mecanico")

        self._thread = threading.Thread(target=self._feed, daemon=True)
        self._thread.start()
        return str(port)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
        if self._session is not None:
            self._session.terminate()

    # ------------------------------------------------------------------- feed
    def _feed(self) -> None:
        session = self._session
        assert session is not None  # start() siempre lo inicializa antes del hilo
        period = 1.0 / self.spec.sample_rate_hz
        for values in iter_ticks(self.spec):
            if self._stop.is_set():
                return
            t0 = time.perf_counter()
            for pid in CANONICAL_PIDS:
                _, response = encode_pid(pid, values[pid])
                session.answer[f"MEC_{pid}"] = response
            elapsed = time.perf_counter() - t0
            if elapsed < period:
                self._stop.wait(period - elapsed)
