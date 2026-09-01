"""Interfaz de línea de comandos del laboratorio.

De momento expone la auditoría del entorno, que es lo que cierra la fase E1.
Los subcomandos de las fases siguientes se añaden aquí conforme se aprueban.
"""

from __future__ import annotations

import argparse
import json
import sys

from mecanico_ia_exp.config.environment import audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mecanico-exp", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="auditar el entorno de ejecución")
    doctor.add_argument(
        "--no-db", action="store_true", help="omitir las comprobaciones de PostgreSQL"
    )
    doctor.add_argument("--json", action="store_true", help="emitir el informe en JSON")

    args = parser.parse_args(argv)

    if args.command == "doctor":
        report = audit(include_database=not args.no_db)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(report)
        return 0 if report.ok else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
