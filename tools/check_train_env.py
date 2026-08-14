"""Verifica que el entorno de ENTRENAMIENTO está completo antes de lanzar un experimento.

Motivación (auditoría del stack, F20): `uv sync --all-packages --locked` sin `--group
train` **desinstala torch, shap y matplotlib** y deja un entorno de entrenamiento
incompleto sin avisar. Este comprobador falla pronto y con un mensaje accionable, en
lugar de dejar que un runner muera a mitad de un experimento largo.

Uso: `make check-train-env` (los targets `experiments-*` lo invocan antes de ejecutar).
"""

from importlib.metadata import PackageNotFoundError, version

#: Paquetes del grupo `train` (root pyproject) imprescindibles para la línea ML.
REQUIRED: tuple[tuple[str, str], ...] = (
    ("torch", "autoencoders denso y recurrentes"),
    ("shap", "evaluación XAI (Adenda XAI v1)"),
    ("matplotlib", "figuras de los informes"),
)
#: Del entorno base, pero se comprueban por ser CORE de la línea experimental.
CORE: tuple[tuple[str, str], ...] = (
    ("numpy", "álgebra y ventanas"),
    ("scipy", "correlación de rango (agreement XAI)"),
    ("scikit-learn", "detectores clásicos, PCA y métricas"),
)


def main() -> int:
    missing: list[str] = []
    print("entorno de entrenamiento (docs/models/15_stack_ml_xai.md):")
    for name, purpose in (*CORE, *REQUIRED):
        try:
            print(f"  {name:14s} {version(name):<12} {purpose}")
        except PackageNotFoundError:
            print(f"  {name:14s} {'AUSENTE':<12} {purpose}")
            missing.append(name)
    if missing:
        print(
            f"\nFaltan {len(missing)} paquete(s): {', '.join(missing)}.\n"
            "Ejecuta `make install-train` (uv sync --all-packages --group train --locked).\n"
            "Un `uv sync --locked` a secas NO instala el grupo train y desinstala torch/shap/"
            "matplotlib si ya estaban."
        )
        return 1
    print("\nentorno de entrenamiento completo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
