"""CLI del laboratorio OBD-II (scaffolding: solo versión; comandos en fases siguientes)."""

import sys

from obd_lab import __version__


def main() -> int:
    """Punto de entrada de ``obd-lab``."""
    print(f"obd-lab {__version__} — laboratorio de simulación OBD-II (Mecánico IA)")
    print("Comandos (próximas fases): run, inject, replay, record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
