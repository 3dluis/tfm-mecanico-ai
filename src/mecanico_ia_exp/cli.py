"""Interfaz de línea de comandos del laboratorio.

De momento expone la auditoría del entorno, que es lo que cierra la fase E1.
Los subcomandos de las fases siguientes se añaden aquí conforme se aprueban.
"""

from __future__ import annotations

import argparse
import json
import sys

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.config.environment import audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mecanico-exp", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="auditar el entorno de ejecución")
    doctor.add_argument(
        "--no-db", action="store_true", help="omitir las comprobaciones de PostgreSQL"
    )
    doctor.add_argument("--json", action="store_true", help="emitir el informe en JSON")

    generar = subparsers.add_parser(
        "generate-synthetic", help="generar el conjunto de datos sintético"
    )
    generar.add_argument("--dataset-id", default="synthetic_v1")
    generar.add_argument("--seed", type=int, default=20260901)
    generar.add_argument("--sessions-per-fault", type=int, default=6)
    generar.add_argument("--duration-s", type=float, default=600.0)

    args = parser.parse_args(argv)

    if args.command == "doctor":
        report = audit(include_database=not args.no_db)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(report)
        return 0 if report.ok else 1

    if args.command == "generate-synthetic":
        from mecanico_ia_exp.obd.synthetic import build_balanced_specs, generate_dataset

        specs = build_balanced_specs(
            seed=args.seed,
            sessions_per_fault=args.sessions_per_fault,
            duration_s=args.duration_s,
        )
        datos, metadata = generate_dataset(
            specs, dataset_id=args.dataset_id, seed=args.seed, notes="Plan equilibrado E2."
        )
        destino = paths.ensure(paths.DATA_RAW_SYNTHETIC) / f"{args.dataset_id}.parquet"
        datos.to_parquet(destino, index=False)
        metadata.write(destino.with_suffix(".meta.json"))
        print(f"{len(datos)} muestras en {metadata.n_sessions} sesiones -> {destino.name}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
