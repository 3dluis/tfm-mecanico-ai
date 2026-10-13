"""Interfaz de línea de comandos del laboratorio.

De momento expone la auditoría del entorno, que es lo que cierra la fase E1.
Los subcomandos de las fases siguientes se añaden aquí conforme se aprueban.
"""

from __future__ import annotations

import argparse
import json
import sys

from mecanico_ia_exp.abstention.sufficiency import POLITICAS, VERIFIER_VERSION
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

    subparsers.add_parser("eda", help="análisis exploratorio: figuras y tablas")
    for nombre, ayuda in (
        ("preprocess", "estudio de ventana, ventanado y reparto sin fuga"),
        ("train-baseline", "entrenar y evaluar el baseline"),
        ("train-temporal", "entrenar y evaluar el modelo temporal"),
    ):
        sub = subparsers.add_parser(nombre, help=ayuda)
        sub.add_argument("--dataset-id", default="synthetic_v2")
    train_baseline = subparsers.choices["train-baseline"]
    train_baseline.add_argument(
        "--por-ventana",
        action="store_true",
        help="guardar también la predicción de cada ventana con su sesión y su temperatura media",
    )

    subparsers.add_parser("xai", help="atribución sobre el modelo especializado")
    subparsers.add_parser("eval-retrieval", help="evaluar la recuperación")
    umbral = subparsers.add_parser(
        "threshold-sweep", help="barrido del umbral de confianza sobre validación"
    )
    umbral.add_argument("--dataset-id", default="synthetic_v2")
    subparsers.add_parser("training-data", help="generar el conjunto de ajuste del SLM")
    ft = subparsers.add_parser("finetune-slm", help="ajustar el SLM con LoRA")
    ft.add_argument("--epochs", type=int, default=4)
    ft.add_argument(
        "--adapter-dir",
        default="slm_lora",
        help="subdirectorio de models/ donde guardar el adaptador (no pisa otros)",
    )
    suf = subparsers.add_parser(
        "sufficiency", help="verificar suficiencia y, opcionalmente, redactar"
    )
    suf.add_argument(
        "--mode",
        choices=("oracle", "non-oracle", "adverse"),
        default="oracle",
        help=(
            "oracle: los códigos que acotan la búsqueda y exige el verificador salen de la "
            "etiqueta anotada (cota superior asistida por oráculo). non-oracle: salen del "
            "diagnóstico del modelo. adverse: además, ventanas que el modelo clasifica mal. "
            "Política congelada en docs/methodology/politica-evaluacion-no-oracular.md"
        ),
    )
    suf.add_argument(
        "--llm",
        default=None,
        help=(
            "proveedor de lenguaje: echo, ollama, transformers (base), "
            "transformers-lora (ajustado) o transformers-lora@<subdir de models/>. "
            "Sin él, no se redacta"
        ),
    )
    suf.add_argument(
        "--policy",
        choices=POLITICAS,
        default=VERIFIER_VERSION,
        help=(
            "versión de la política de suficiencia. v2.1 es la canónica; v2.2 lee el "
            "requisito de la puerta de códigos de la declaración del diagnóstico "
            "(docs/methodology/politica-puerta-dtc.md) y escribe sus artefactos con "
            "sufijo para no sobrescribir los registros vigentes"
        ),
    )
    abl = subparsers.add_parser("ablations", help="ablaciones E18 sobre el conjunto anotado")
    abl.add_argument("--dataset-id", default="synthetic_v2")
    abl.add_argument(
        "--ablation",
        choices=("A1", "A2", "A3", "A4", "all"),
        default="all",
        help=(
            "A1 sin atribución, A2 sin recuperación semántica, A3 sin criterio de "
            "suficiencia, A4 umbral único. Definidas en "
            "docs/methodology/preregistro-e18-ablaciones.md"
        ),
    )
    abl.add_argument(
        "--partition",
        choices=("validation", "test"),
        default="validation",
        help=(
            "sobre qué se miden las ablaciones. Repetirlas sobre el conjunto de prueba es "
            "el tercero de los pendientes del tutor, exige --open-test con --reason y "
            "constituye una apertura que hay que registrar en "
            "docs/methodology/registro-aperturas-test.md ANTES de ejecutar"
        ),
    )
    abl.add_argument(
        "--open-test",
        action="store_true",
        help=(
            "declara la apertura del conjunto de prueba. Sin esto y sin --reason, pedir "
            "la partición de prueba es un error, no un resultado"
        ),
    )
    abl.add_argument(
        "--reason",
        default="",
        help=(
            "razón por escrito de la apertura. Queda EN EL REGISTRO de cada ablación, no "
            "solo en la salida de la ejecución"
        ),
    )
    abl.add_argument(
        "--mode",
        choices=("oracle", "non-oracle"),
        default="oracle",
        help=(
            "oracle: los códigos que acotan la búsqueda y exige el verificador salen de la "
            "etiqueta anotada. non-oracle: salen del diagnóstico del modelo. Las ablaciones "
            "no tienen modo adverso: su variable es el componente retirado"
        ),
    )

    fin = subparsers.add_parser(
        "final-evaluation",
        help="E19, la evaluación final bajo las reglas congeladas",
    )
    fin.add_argument("--dataset-id", default="synthetic_v2")
    fin.add_argument(
        "--partition",
        choices=("validation", "test"),
        default="validation",
        help=(
            "sobre qué se mide. validation recorre el ejecutor sobre una partición ya "
            "conocida y escribe artefactos con sufijo: sirve para comprobarlo sin abrir "
            "nada. test es la evaluación final y exige --open-test con --reason"
        ),
    )
    fin.add_argument(
        "--open-test",
        action="store_true",
        help=(
            "declara la apertura del conjunto de prueba. Sin esto y sin --reason, pedir "
            "la partición de prueba es un error, no un resultado"
        ),
    )
    fin.add_argument(
        "--reason",
        default="",
        help="razón por escrito de la apertura; queda impresa en la salida de la ejecución",
    )
    fin.add_argument(
        "--stratum",
        choices=("operativo", "comparativo", "adverso", "all"),
        default="all",
        help=(
            "operativo es el que responde a la pregunta; comparativo y adverso son "
            "descriptivos. Definidos en docs/methodology/congelacion-anotacion-e19.md"
        ),
    )
    fin.add_argument(
        "--llm",
        default=None,
        help=(
            "proveedor de lenguaje para medir la redacción. En la evaluación final es "
            "obligatorio, porque sus métricas se publican; en un ensayo, opcional"
        ),
    )
    fin.add_argument(
        "--attempt",
        default="",
        help=(
            "identificador de una repetición sobre prueba, por ejemplo v2. Sin él, una "
            "segunda ejecución sobrescribiría la anotación sellada de la primera, que es "
            "lo que la sección 11 de las reglas congeladas prohíbe"
        ),
    )

    # La etiqueta va a TODOS los ejecutores que escriben artefactos, y en un solo
    # sitio para que añadir un subcomando sin ella se note. Sin etiqueta, el
    # ejecutor conserva los nombres históricos y se niega a sobrescribirlos; sin
    # esta opción, esos subcomandos no podrían reejecutarse desde la línea de
    # órdenes, que es peor que no protegerlos.
    for nombre in (
        "train-baseline",
        "train-temporal",
        "xai",
        "eval-retrieval",
        "threshold-sweep",
        "training-data",
        "ablations",
    ):
        subparsers.choices[nombre].add_argument(
            "--etiqueta",
            default="",
            help=(
                "identifica la ejecución y entra en el nombre de todos sus artefactos; "
                "sin ella se usan los nombres históricos y la ejecución se niega a "
                "sobrescribirlos"
            ),
        )

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
        from mecanico_ia_exp.obd.auditoria import (
            AuditoriaDelGeneradorError,
            exigir_auditoria_limpia,
        )
        from mecanico_ia_exp.obd.procedencia import construir, escribir, ruta_de

        manifiesto = construir(specs, datos, dataset_id=args.dataset_id, seed=args.seed)

        # La auditoría va ANTES de escribir, no después. Un conjunto que no la
        # pasa no llega a existir en disco, y así no hay forma de entrenar sobre
        # él por descuido. `synthetic_v3` se generó sin este paso, con el motor
        # sin calibrar, y nadie lo notó hasta que una conclusión publicada hubo
        # que retirarla.
        print("\nAuditoría del generador:")
        try:
            for comprobacion in exigir_auditoria_limpia(datos, manifiesto):
                print(f"  {comprobacion}")
        except AuditoriaDelGeneradorError as error:
            print(f"\n{error}\n\nNo se escribe nada.")
            return 1

        destino = paths.ensure(paths.DATA_RAW_SYNTHETIC) / f"{args.dataset_id}.parquet"
        datos.to_parquet(destino, index=False)
        metadata.write(destino.with_suffix(".meta.json"))
        escribir(ruta_de(args.dataset_id), manifiesto)
        print(f"\n{len(datos)} muestras en {metadata.n_sessions} sesiones -> {destino.name}")
        print(f"procedencia por sesión -> {ruta_de(args.dataset_id).name}")
        return 0

    if args.command == "eda":
        from mecanico_ia_exp.experiments.eda_runner import run_eda

        return run_eda()

    if args.command == "preprocess":
        from mecanico_ia_exp.experiments.preprocess_runner import run_preprocess

        return run_preprocess(args.dataset_id)

    if args.command == "train-baseline":
        from mecanico_ia_exp.experiments.baseline_runner import run_baseline

        return run_baseline(args.dataset_id, etiqueta=args.etiqueta, por_ventana=args.por_ventana)

    if args.command == "train-temporal":
        from mecanico_ia_exp.experiments.temporal_runner import run_temporal

        return run_temporal(args.dataset_id, etiqueta=args.etiqueta)

    if args.command == "xai":
        from mecanico_ia_exp.experiments.xai_runner import run_xai

        return run_xai(etiqueta=args.etiqueta)

    if args.command == "eval-retrieval":
        from mecanico_ia_exp.experiments.retrieval_runner import (
            run_retrieval_evaluation,
        )

        return run_retrieval_evaluation(etiqueta=args.etiqueta)

    if args.command == "threshold-sweep":
        from mecanico_ia_exp.experiments.threshold_runner import run_threshold_sweep

        return run_threshold_sweep(args.dataset_id, etiqueta=args.etiqueta)

    if args.command == "training-data":
        from mecanico_ia_exp.experiments.training_runner import run_training_data

        return run_training_data(etiqueta=args.etiqueta)

    if args.command == "finetune-slm":
        from mecanico_ia_exp.llm.finetune import FinetuneConfig, finetune

        h = finetune(
            paths.DATA_PROCESSED / "slm_finetune_prepared",
            paths.MODELS / args.adapter_dir,
            FinetuneConfig(epochs=args.epochs),
        )
        print(f"\nadaptador guardado en models/{args.adapter_dir} · {h.seconds:.0f} s")
        return 0

    if args.command == "sufficiency":
        from mecanico_ia_exp.experiments.sufficiency_runner import (
            run_sufficiency,
        )

        return run_sufficiency(
            llm=args.llm,
            oracle=args.mode == "oracle",
            adverse=args.mode == "adverse",
            policy=args.policy,
        )

    if args.command == "ablations":
        from mecanico_ia_exp.experiments.ablation_runner import run_ablations

        return run_ablations(
            args.dataset_id,
            ablation=args.ablation,
            oracle=args.mode == "oracle",
            etiqueta=args.etiqueta,
            particion=args.partition,
            allow_test=args.open_test,
            reason=args.reason,
        )

    if args.command == "final-evaluation":
        from mecanico_ia_exp.experiments.final_runner import ESTRATOS, run_final_evaluation

        return run_final_evaluation(
            args.dataset_id,
            llm=args.llm,
            particion=args.partition,
            open_test=args.open_test,
            reason=args.reason,
            estratos=ESTRATOS if args.stratum == "all" else (args.stratum,),
            intento=args.attempt,
        )

    return 2


if __name__ == "__main__":
    sys.exit(main())
