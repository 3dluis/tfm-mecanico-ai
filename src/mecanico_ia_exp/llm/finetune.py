"""Ajuste fino del SLM con PyTorch y PEFT sobre Apple Silicon.

**Qué se ajusta y qué no.** Se ajusta el *formato de la tarea*: cómo respetar el
veredicto, cómo anclar cada afirmación en su observación y su fragmento, cómo
cerrar el JSON, cuándo abstenerse. No se ajusta el contenido del manual, y hay
dos mecanismos que lo garantizan:

1. **El texto del manual solo aparece en el prompt**, en la respuesta de la
   herramienta, nunca en la completion (comprobado por
   ``verify_no_manual_content_in_targets`` al generar los datos).
2. **La pérdida se calcula solo sobre los tokens de la completion.** Los tokens
   del prompt se enmascaran con ``-100``. El gradiente no toca lo que el modelo
   ve del manual: aprende a responder, no a recitar.

**Por qué PyTorch y no MLX.** MLX es más rápido en Apple Silicon y solo funciona
en Apple Silicon. Un tercero con Linux y NVIDIA no podría reproducir el ajuste.
PyTorch corre en cualquier sitio, es el stack declarado del proyecto y es el
mismo con el que se entrenó el modelo temporal.

**Limitación de MPS.** No hay cuantización a 4 bits: el modelo va en bf16, unos
6 GB de pesos. Cabe en 24 GB y entrena en minutos con 55 ejemplos.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

MODELO_BASE = "Qwen/Qwen2.5-3B-Instruct"


@dataclass(frozen=True)
class FinetuneConfig:
    """Hiperparámetros del ajuste. Se registran con el adaptador."""

    base_model: str = MODELO_BASE
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj")
    """Solo las proyecciones de atención. Es lo que decide a qué atiende el
    modelo dentro del contexto --qué observación va con qué fragmento--, que es
    exactamente lo que hay que enseñar. Las capas de alimentación, donde reside
    más conocimiento factual, se dejan intactas."""

    epochs: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 4096
    seed: int = 20260901
    device: str = "mps"


@dataclass
class FinetuneHistory:
    train_loss: list[float] = field(default_factory=list)
    val_loss: list[float] = field(default_factory=list)
    n_train: int = 0
    n_valid: int = 0
    n_trainable_params: int = 0
    n_total_params: int = 0
    seconds: float = 0.0
    n_truncated: int = 0
    """Ejemplos cuyo prompt superó ``max_seq_length`` y se recortó por la
    izquierda. Se cuenta: recortar en silencio ocultaría que el modelo no vio
    parte de la evidencia."""


def _cargar_jsonl(ruta: Path) -> list[dict[str, str]]:
    return [
        json.loads(linea)
        for linea in ruta.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]


def _tokenizar(
    tok: Any, ejemplo: dict[str, str], max_len: int
) -> tuple[list[int], list[int], bool]:
    """Devuelve (input_ids, labels, truncado).

    Las etiquetas del prompt son ``-100``: PyTorch las ignora en la pérdida. Es
    la garantía de que el gradiente solo actúa sobre la completion.
    """
    prompt_ids: list[int] = tok(ejemplo["prompt"], add_special_tokens=False)["input_ids"]
    completion_ids: list[int] = tok(
        ejemplo["completion"] + tok.eos_token, add_special_tokens=False
    )["input_ids"]

    truncado = False
    exceso = len(prompt_ids) + len(completion_ids) - max_len
    if exceso > 0:
        # Se recorta el prompt por la IZQUIERDA: lo que se pierde es el sistema
        # y el principio del contexto, nunca la evidencia recuperada ni la
        # completion, que están al final.
        prompt_ids = prompt_ids[exceso:]
        truncado = True

    input_ids = prompt_ids + completion_ids
    labels = [-100] * len(prompt_ids) + completion_ids
    return input_ids, labels, truncado


def finetune(
    data_dir: Path,
    adapter_dir: Path,
    config: FinetuneConfig | None = None,
    *,
    verbose: bool = True,
) -> FinetuneHistory:
    """Ajusta el modelo y guarda el adaptador LoRA."""
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = config or FinetuneConfig()
    torch.manual_seed(cfg.seed)
    if cfg.device == "mps":
        torch.mps.manual_seed(cfg.seed)

    # Los tipos de transformers y peft son abiertos; se fijan a Any en la
    # frontera en lugar de silenciar cada llamada.
    tok: Any = AutoTokenizer.from_pretrained(cfg.base_model)
    base: Any = AutoModelForCausalLM.from_pretrained(cfg.base_model, dtype=torch.bfloat16)
    base.to(cfg.device)

    lora = LoraConfig(
        r=cfg.lora_rank,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=list(cfg.target_modules),
        task_type="CAUSAL_LM",
    )
    modelo: Any = get_peft_model(base, lora)

    historia = FinetuneHistory()
    historia.n_trainable_params = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    historia.n_total_params = sum(p.numel() for p in modelo.parameters())

    train = _cargar_jsonl(data_dir / "train.jsonl")
    valid = _cargar_jsonl(data_dir / "valid.jsonl")
    historia.n_train, historia.n_valid = len(train), len(valid)

    tokenizados: list[tuple[list[int], list[int]]] = []
    for ejemplo in train:
        ids, labels, truncado = _tokenizar(tok, ejemplo, cfg.max_seq_length)
        historia.n_truncated += int(truncado)
        tokenizados.append((ids, labels))
    validos = [_tokenizar(tok, e, cfg.max_seq_length)[:2] for e in valid]

    if verbose:
        print(
            f"parámetros entrenables: {historia.n_trainable_params:,} de "
            f"{historia.n_total_params:,} "
            f"({100 * historia.n_trainable_params / historia.n_total_params:.2f} %)"
        )
        print(
            f"ejemplos: {len(train)} train · {len(valid)} valid · {historia.n_truncated} truncados"
        )

    optimizador = torch.optim.AdamW(
        (p for p in modelo.parameters() if p.requires_grad),
        lr=cfg.learning_rate,
        weight_decay=0.0,
    )
    generador = torch.Generator().manual_seed(cfg.seed)

    def perdida_de(ids: list[int], labels: list[int]) -> torch.Tensor:
        entrada = torch.tensor([ids], device=cfg.device)
        etiquetas = torch.tensor([labels], device=cfg.device)
        salida: Any = modelo(input_ids=entrada, labels=etiquetas)
        return torch.as_tensor(salida.loss)

    def evaluar() -> float:
        modelo.eval()
        with torch.no_grad():
            total = sum(float(perdida_de(ids, labels).item()) for ids, labels in validos)
        modelo.train()
        return total / max(len(validos), 1)

    inicio = time.perf_counter()
    modelo.train()
    for epoca in range(cfg.epochs):
        orden = torch.randperm(len(tokenizados), generator=generador).tolist()
        acumulada = 0.0
        for k, indice in enumerate(orden, start=1):
            ids, labels = tokenizados[indice]
            optimizador.zero_grad()
            perdida = perdida_de(ids, labels)
            perdida.backward()  # type: ignore[no-untyped-call]
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            optimizador.step()
            acumulada += float(perdida.item())
            if verbose and k % 10 == 0:
                print(f"  época {epoca + 1} · paso {k}/{len(orden)} · pérdida {acumulada / k:.4f}")
        historia.train_loss.append(acumulada / len(orden))
        historia.val_loss.append(evaluar())
        if verbose:
            print(
                f"época {epoca + 1}/{cfg.epochs} · pérdida train {historia.train_loss[-1]:.4f} · "
                f"valid {historia.val_loss[-1]:.4f}"
            )

    historia.seconds = time.perf_counter() - inicio

    adapter_dir.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(adapter_dir))
    (adapter_dir / "finetune_config.json").write_text(
        json.dumps(
            {"config": asdict(cfg), "history": asdict(historia)}, indent=2, ensure_ascii=False
        )
        + "\n",
        encoding="utf-8",
    )
    return historia
