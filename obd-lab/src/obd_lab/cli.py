"""CLI del laboratorio OBD-II.

Comandos:
    obd-lab generate --suite <suite.yaml> --out <dir>   Genera todas las sesiones de la suite
    obd-lab list-faults                                  Catálogo de fallos disponible
"""

import argparse
import sys
from pathlib import Path

from obd_lab import __version__
from obd_lab.injection.faults import CATALOG


def _cmd_generate(suite_path: Path, out_dir: Path) -> int:
    from obd_lab.generate import write_session
    from obd_lab.scenarios.loader import load_suite

    suite = load_suite(suite_path)
    total = 0
    for split, specs in suite.items():
        split_dir = out_dir / split
        for spec in specs:
            path = write_session(spec, split_dir)
            print(f"[{split}] {spec.scenario_id} -> {path}")
            total += 1
    print(f"{total} sesiones generadas en {out_dir}")
    return 0


def _cmd_list_faults() -> int:
    for name, f in CATALOG.items():
        print(f"{name:22s} [{f.category:11s}] {f.description} :: firma: {f.expected_signature}")
    return 0


def main() -> int:
    """Punto de entrada de ``obd-lab``."""
    parser = argparse.ArgumentParser(prog="obd-lab", description=f"obd-lab {__version__}")
    sub = parser.add_subparsers(dest="cmd")
    gen = sub.add_parser("generate", help="Genera las sesiones de una suite YAML")
    gen.add_argument("--suite", type=Path, required=True)
    gen.add_argument("--out", type=Path, required=True)
    sub.add_parser("list-faults", help="Muestra el catálogo de fallos")

    args = parser.parse_args()
    if args.cmd == "generate":
        return _cmd_generate(args.suite, args.out)
    if args.cmd == "list-faults":
        return _cmd_list_faults()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
