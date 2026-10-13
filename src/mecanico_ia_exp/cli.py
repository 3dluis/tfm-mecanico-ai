"""Interfaz de línea de comandos del laboratorio.

De momento expone la auditoría del entorno, que es lo que cierra la fase E1.
Los subcomandos de las fases siguientes se añaden aquí conforme se aprueban.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    generar.add_argument(
        "--esquema",
        choices=("vigente", "historico"),
        default="vigente",
        help=(
            "vigente incluye las columnas de expresión efectiva del fallo. historico las "
            "omite y es el esquema de synthetic_v1, v2 y v3: reconstruir uno de ellos con "
            "el esquema vigente produce un meta.parquet distinto y rompe la verificación de "
            "la congelación de E19, que lo fija por huella. Solo se admite para esos tres"
        ),
    )

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
    datos_ajuste = subparsers.add_parser(
        "training-data", help="generar el conjunto de ajuste del SLM"
    )
    datos_ajuste.add_argument(
        "--particion-ejemplos",
        choices=("train", "validation"),
        default="validation",
        help=(
            "de dónde salen los ejemplos. validation es lo que produjo slm_lora_v2 y "
            "CONTAMINA, porque E13 y E15 miden al redactor sobre validación: tres de sus "
            "cinco ventanas de evaluación eran las mismas del ajuste "
            "(docs/methodology/auditoria-contaminacion-adaptador.md). Se conserva para poder "
            "reproducir aquel conjunto. Para un adaptador nuevo, train"
        ),
    )
    ft = subparsers.add_parser("finetune-slm", help="ajustar el SLM con LoRA")
    ft.add_argument("--epochs", type=int, default=4)
    ft.add_argument(
        "--datos",
        default="",
        help=(
            "etiqueta del conjunto de ejemplos: usa "
            "data/processed/slm_finetune_prepared_<etiqueta>. Sin ella, el histórico"
        ),
    )
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
        "--goldset",
        default="",
        help=(
            "nombre de un conjunto anotado alternativo dentro de configs/. Sin él se usa el "
            "canónico, goldset_mazda3_bk.yaml, que está fijado por huella en el manifiesto de "
            "E19 y no se edita. Lo exige el rediseño de la condición con distractor (P1), que "
            "mide sobre casos nuevos en un fichero nuevo"
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
        "preprocess",
        "sufficiency",
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
        from mecanico_ia_exp.experiments.preprocess_runner import ANTERIORES_AL_MANIFIESTO

        historico = args.esquema == "historico"
        if historico and args.dataset_id not in ANTERIORES_AL_MANIFIESTO:
            print(
                f"El esquema histórico solo se admite para "
                f"{', '.join(sorted(ANTERIORES_AL_MANIFIESTO))}, que están congelados. "
                f"«{args.dataset_id}» es un conjunto nuevo y tiene que llevar las columnas "
                "de expresión efectiva del fallo.\n\nNo se escribe nada."
            )
            return 1

        datos, metadata = generate_dataset(
            specs,
            dataset_id=args.dataset_id,
            seed=args.seed,
            notes="Plan equilibrado E2.",
            con_expresion=not historico,
        )
        from mecanico_ia_exp.experiments.destinos import ArtefactoOcupadoError, exigir_libres
        from mecanico_ia_exp.obd.auditoria import (
            AuditoriaDelGeneradorError,
            exigir_auditoria_limpia,
        )
        from mecanico_ia_exp.obd.procedencia import construir, escribir, ruta_de

        # Los TRES destinos se comprueban antes de escribir el primero. Si solo
        # se comprobara el manifiesto, una regeneración habría reemplazado ya el
        # parquet y la ficha antes de fallar, y el manifiesto antiguo habría
        # quedado describiendo datos nuevos: una procedencia que miente es peor
        # que no tenerla.
        destino = paths.ensure(paths.DATA_RAW_SYNTHETIC) / f"{args.dataset_id}.parquet"
        try:
            exigir_libres(
                {
                    "datos": destino,
                    "ficha": destino.with_suffix(".meta.json"),
                    "procedencia": ruta_de(args.dataset_id),
                }
            )
        except ArtefactoOcupadoError as error:
            print(
                f"\n{error}\n"
                "Para generar un conjunto nuevo, usa otro --dataset-id. "
                "Los conjuntos existentes sostienen cifras publicadas y no se regeneran.\n"
                "\nNo se escribe nada."
            )
            return 1

        manifiesto = construir(
            specs,
            datos,
            dataset_id=args.dataset_id,
            seed=args.seed,
            con_expresion=not historico,
        )

        # La auditoría va ANTES de escribir, no después. Un conjunto que no la
        # pasa no llega a existir en disco, y así no hay forma de entrenar sobre
        # él por descuido. `synthetic_v3` se generó sin este paso, con el motor
        # sin calibrar, y nadie lo notó hasta que una conclusión publicada hubo
        # que retirarla.
        if historico:
            # Un conjunto en esquema histórico no puede pasar la comprobación de
            # expresión, porque no trae las columnas. Se informa la auditoría sin
            # bloquear, como ya hace el preprocesado con esos mismos tres
            # conjuntos, y se dice por qué en lugar de saltarla en silencio.
            from mecanico_ia_exp.obd.auditoria import auditar

            print("\nAuditoría del generador (esquema histórico, informativa):")
            for comprobacion in auditar(datos, manifiesto):
                print(f"  {comprobacion}")
            print(
                "  La comprobación 8 no se puede verificar sin las columnas de expresión: "
                "es el esquema de un conjunto congelado y se reproduce tal como era."
            )
        else:
            print("\nAuditoría del generador:")
            try:
                for comprobacion in exigir_auditoria_limpia(datos, manifiesto):
                    print(f"  {comprobacion}")
            except AuditoriaDelGeneradorError as error:
                print(f"\n{error}\n\nNo se escribe nada.")
                return 1

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

        return run_preprocess(args.dataset_id, etiqueta=args.etiqueta)

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

        return run_training_data(
            etiqueta=args.etiqueta,
            particion_de_ejemplos=args.particion_ejemplos,
        )

    if args.command == "finetune-slm":
        from mecanico_ia_exp.llm.finetune import FinetuneConfig, finetune

        sufijo_datos = f"_{args.datos}" if args.datos else ""
        destino_adaptador = paths.MODELS / args.adapter_dir
        if destino_adaptador.exists() and any(destino_adaptador.iterdir()):
            print(
                f"Ya existe models/{args.adapter_dir} y no se sobrescribe: un adaptador "
                "congelado sostiene cifras publicadas.\n\nNo se escribe nada."
            )
            return 1
        # Las huellas de la congelación se comprueban ANTES de cargar el modelo.
        # El fichero de congelación promete que «si los ficheros de ejemplos no
        # coinciden con las huellas que declara, no se ajusta»; sin esto, la
        # promesa estaba escrita y no se cumplía, y un `.jsonl` cambiado después
        # de congelar habría producido un adaptador de otros datos con apariencia
        # de seguir la configuración declarada.
        version = args.adapter_dir.split("_")[-1]
        congelacion = paths.CONFIGS / f"congelacion-adaptador-{version}.json"
        if congelacion.is_file():
            import hashlib

            congelado = json.loads(congelacion.read_text("utf-8"))

            # Las huellas no bastan: comprobarlas y después ajustar con OTRO
            # directorio de datos, o con otro número de épocas, produciría un
            # adaptador que no es el congelado con apariencia de serlo. Se ata
            # también el origen de los datos y los hiperparámetros que el fichero
            # declara.
            # Se compara el directorio que de verdad se va a usar, no la etiqueta:
            # omitir `--datos` resolvía al conjunto histórico y la comprobación
            # anterior lo dejaba pasar por estar vacía la etiqueta.
            # Comparación EXACTA del nombre de directorio. Buscarlo como
            # subcadena dejaba pasar el histórico, porque `slm_finetune_prepared`
            # está contenido en `slm_finetune_prepared_sin_contaminacion`.
            esperado = congelado["datos_de_ajuste"]["ficheros"]["preparados"]
            directorio_congelado = Path(esperado).parent.name
            directorio = f"slm_finetune_prepared{sufijo_datos}"
            if directorio != directorio_congelado:
                print(
                    f"{congelacion.name} congela los ejemplos de «{esperado}» y se ha pedido "
                    f"ajustar con «{directorio}».\n"
                    "Un adaptador entrenado con otros datos no es el experimento congelado.\n"
                    "\nNo se ajusta nada."
                )
                return 1
            epocas = int(congelado["hiperparametros"]["epochs"])
            if args.epochs != epocas:
                print(
                    f"{congelacion.name} congela {epocas} épocas y se han pedido "
                    f"{args.epochs}. El criterio de parada es parte del experimento "
                    "congelado.\n\nNo se ajusta nada."
                )
                return 1

            declaradas = congelado["datos_de_ajuste"]["huellas_sha256_16"]
            discrepantes = []
            for relativa, esperada in sorted(declaradas.items()):
                fichero = paths.DATA_PROCESSED / relativa
                if not fichero.is_file():
                    discrepantes.append(f"{relativa}: falta")
                    continue
                actual = hashlib.sha256(fichero.read_bytes()).hexdigest()[:16]
                if actual != esperada:
                    discrepantes.append(f"{relativa}: {esperada} → {actual}")
            if discrepantes:
                detalle = "\n".join(f"  - {d}" for d in discrepantes)
                print(
                    f"Los ejemplos no son los que {congelacion.name} congeló:\n{detalle}\n"
                    "Un ajuste sobre otros datos con la configuración declarada no es el "
                    "experimento congelado.\n\nNo se ajusta nada."
                )
                return 1
            print(
                f"congelación verificada: {len(declaradas)} ficheros, origen de los datos y "
                f"{epocas} épocas coinciden con {congelacion.name}"
            )

        h = finetune(
            paths.DATA_PROCESSED / f"slm_finetune_prepared{sufijo_datos}",
            destino_adaptador,
            FinetuneConfig(epochs=args.epochs),
        )
        print(f"\nadaptador guardado en models/{args.adapter_dir} · {h.seconds:.0f} s")
        return 0

    if args.command == "sufficiency":
        from mecanico_ia_exp.experiments.sufficiency_runner import (
            GOLDSET,
            run_sufficiency,
        )

        conjunto_anotado = GOLDSET
        if args.goldset:
            conjunto_anotado = paths.CONFIGS / args.goldset
            if not conjunto_anotado.is_file():
                print(f"No existe el conjunto anotado: {conjunto_anotado}")
                return 2
            if conjunto_anotado == GOLDSET:
                print("Para el canónico no hace falta --goldset.")
            else:
                print(f"conjunto anotado alternativo: {conjunto_anotado.name}")

        return run_sufficiency(
            llm=args.llm,
            oracle=args.mode == "oracle",
            adverse=args.mode == "adverse",
            policy=args.policy,
            etiqueta=args.etiqueta,
            goldset=conjunto_anotado,
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
