"""Construcción y congelación del corpus C-A y de sus variantes de disponibilidad (R3).

Ensambla el corpus recuperable a partir de las dos capas declaradas en
``diagnostic-agent/knowledge/corpus_v2/sources.yaml`` —extractos externos con revisión
fijada y documentos propios de procedimiento— los trocea de forma determinista y emite:

* ``build/corpus-CA.yaml``          corpus completo (Escenario A)
* ``build/corpus-CB-<mecanismo>.yaml``   evidencia ausente (Escenario B)
* ``build/corpus-CBp-<mecanismo>.yaml``  evidencia parcial (Escenario B duro)
* ``ai-models/configs/corpus-v2-freeze.json``  manifiesto con el hash de cada variante

Las variantes construidas NO se versionan (``build/`` está en .gitignore): son
regenerables de forma determinista y el manifiesto con sus hashes es el ancla, misma
política que ``data/`` y que los bancos sintéticos.

Las variantes se construyen retirando los documentos declarados en ``mechanisms.yaml`` y
**reponiendo chunks de la reserva** hasta igualar el recuento de C-A: si la exclusión
redujese el tamaño del corpus, el sistema podría abstenerse por esa señal superficial y no
por la evidencia (amenaza a la validez nº 5 del diseño experimental).

Todo es determinista: mismo árbol de fuentes, mismos hashes. Library-first (ADR-0035):
troceado y hashing con biblioteca estándar; los contratos los pone ``mecanico_contracts``.

Uso:
    python tools/build_corpus.py                 # construye todo y escribe el manifiesto
    python tools/build_corpus.py --verify        # comprueba que lo construido no ha cambiado
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "diagnostic-agent" / "knowledge" / "corpus_v2"
BUILD_DIR = CORPUS_DIR / "build"
FREEZE_PATH = REPO_ROOT / "ai-models" / "configs" / "corpus-v2-freeze.json"

#: Secciones de los extractos externos que no son contenido técnico y se descartan.
_DROP_SECTIONS = {
    "references",
    "external links",
    "see also",
    "further reading",
    "notes",
    "bibliography",
    "sources",
    "véase también",
    "referencias",
    "enlaces externos",
    "bibliografía",
    "notas",
}


def _sentences(paragraph: str) -> list[str]:
    """Corte por frases suficiente para el solape (no se parte una frase en dos chunks)."""
    parts = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [p.strip() for p in parts if p.strip()]


def _clean_external(raw: str) -> list[str]:
    """Extrae los párrafos de contenido, descartando cabeceras y secciones no técnicas."""
    paragraphs: list[str] = []
    skipping = False
    for block in raw.split("\n"):
        line = block.strip()
        if not line:
            continue
        header = re.fullmatch(r"=+\s*(.+?)\s*=+", line)
        if header:
            skipping = header.group(1).strip().lower() in _DROP_SECTIONS
            continue
        if skipping:
            continue
        paragraphs.append(line)
    return paragraphs


def chunk_paragraphs(paragraphs: list[str], cfg: dict[str, int]) -> list[str]:
    """Agrupa párrafos en chunks de ``target_words`` sin partir frases, con solape."""
    target, minimum, overlap = cfg["target_words"], cfg["min_words"], cfg["overlap_sentences"]
    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for paragraph in paragraphs:
        for sentence in _sentences(paragraph):
            current.append(sentence)
            count += len(sentence.split())
            if count >= target:
                chunks.append(" ".join(current))
                current = current[-overlap:] if overlap else []
                count = sum(len(s.split()) for s in current)
    if current and count >= minimum:
        chunks.append(" ".join(current))
    elif current and chunks:
        chunks[-1] = chunks[-1] + " " + " ".join(current)
    elif current:
        chunks.append(" ".join(current))
    return chunks


def _doc_entry(
    document_id: str,
    title: str,
    source: str,
    license_: str,
    version: str,
    metadata: dict[str, str],
    chunks: list[str],
) -> dict[str, Any]:
    checksum = hashlib.sha256("\n".join(chunks).encode("utf-8")).hexdigest()
    return {
        "document_id": document_id,
        "title": title,
        "source": source,
        "license": license_,
        "version": version,
        "checksum": checksum,
        "metadata": metadata,
        "chunks": [{"seq": i, "text": text} for i, text in enumerate(chunks)],
    }


def build_documents(spec: dict[str, Any], provenance: dict[str, Any]) -> list[dict[str, Any]]:
    """Todos los documentos disponibles: capa externa (incluida la reserva) y capa propia."""
    cfg = spec["chunking"]
    documents: list[dict[str, Any]] = []

    declared = list(spec["external"]["articles"]) + list(
        spec.get("reserve", {}).get("articles", [])
    )
    for article in declared:
        key = article["key"]
        path = CORPUS_DIR / "external" / f"{key}.txt"
        if not path.exists() or key not in provenance:
            continue
        prov = provenance[key]
        chunks = chunk_paragraphs(_clean_external(path.read_text(encoding="utf-8")), cfg)
        documents.append(
            _doc_entry(
                document_id=f"ext-{key}",
                title=prov["resolved_title"],
                source=f"{prov['url']} (oldid={prov['revid']}, {prov['revision_timestamp'][:10]})",
                license_=prov["license"],
                version=str(prov["revid"]),
                metadata={
                    "layer": "externa",
                    "topic": article["topic"],
                    "component": article["component"],
                    "lang": article["lang"],
                    "reserve": "true" if key.startswith("rsv-") else "false",
                },
                chunks=chunks,
            )
        )

    for path in sorted((CORPUS_DIR / "own").glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        for doc in payload["documents"]:
            chunks = chunk_paragraphs([doc["text"].strip()], cfg)
            documents.append(
                _doc_entry(
                    document_id=doc["id"],
                    title=doc["title"],
                    source="Mecánico IA (obra propia del proyecto)",
                    license_="CC-BY-4.0",
                    version=spec["version"],
                    metadata={"layer": "propia", **{k: str(v) for k, v in doc["metadata"].items()}},
                    chunks=chunks,
                )
            )
    return documents


def _count_chunks(documents: list[dict[str, Any]]) -> int:
    return sum(len(d["chunks"]) for d in documents)


def _write_variant(name: str, note: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    """Escribe una variante y devuelve su entrada de manifiesto."""
    payload = {
        "corpus_id": name,
        "note": note,
        "documents": documents,
    }
    path = BUILD_DIR / f"{name}.yaml"
    text = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=100)
    path.write_text(text, encoding="utf-8")
    return {
        "file": str(path.relative_to(REPO_ROOT)),
        "documents": len(documents),
        "chunks": _count_chunks(documents),
        "words": sum(len(c["text"].split()) for d in documents for c in d["chunks"]),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def build_all() -> dict[str, Any]:
    spec = yaml.safe_load((CORPUS_DIR / "sources.yaml").read_text(encoding="utf-8"))
    mech_spec = yaml.safe_load((CORPUS_DIR / "mechanisms.yaml").read_text(encoding="utf-8"))
    provenance = json.loads((CORPUS_DIR / "external" / "provenance.json").read_text("utf-8"))
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    everything = build_documents(spec, provenance)
    by_id = {d["document_id"]: d for d in everything}
    reserve = [d for d in everything if d["metadata"].get("reserve") == "true"]
    core = [d for d in everything if d["metadata"].get("reserve") != "true"]

    manifest: dict[str, Any] = {
        "version": spec["version"],
        "chunking": spec["chunking"],
        "note": (
            "C-A es el corpus completo del Escenario A. Las variantes C-B y C-B' retiran "
            "documentos por mecanismo y reponen chunks de la reserva para igualar el "
            "recuento, de modo que la exclusión no sea detectable por el tamaño."
        ),
        "variants": {},
    }
    manifest["variants"]["corpus-CA"] = _write_variant(
        "corpus-CA", "Escenario A — evidencia suficiente (corpus completo)", core
    )
    target_chunks = _count_chunks(core)

    for mechanism, rule in sorted(mech_spec["mechanisms"].items()):
        causal = set(rule["causal"])
        component = set(rule["componente"])
        for label, removed in (("CB", causal | component), ("CBp", causal)):
            kept = [d for d in core if d["document_id"] not in removed]
            missing = target_chunks - _count_chunks(kept)
            filler: list[dict[str, Any]] = []
            for document in reserve:
                if missing <= 0:
                    break
                take = min(len(document["chunks"]), missing)
                filler.append({**document, "chunks": document["chunks"][:take]})
                missing -= take
            note = (
                "Escenario B — evidencia ausente"
                if label == "CB"
                else "Escenario B duro — evidencia parcial no concluyente"
            )
            entry = _write_variant(
                f"corpus-{label}-{mechanism}",
                f"{note} · mecanismo excluido: {rule['label']}",
                kept + filler,
            )
            entry["mechanism"] = mechanism
            entry["removed_documents"] = sorted(d for d in removed if d in by_id)
            entry["filler_documents"] = [d["document_id"] for d in filler]
            manifest["variants"][f"corpus-{label}-{mechanism}"] = entry

    # Evidencia de referencia por mecanismo (métricas M3/M4/M6). Se deriva de la misma
    # declaración que construye las variantes: es pertinente exactamente aquello cuya
    # retirada produce el Escenario B. Queda congelada aquí, ANTES de ejecutar.
    manifest["evidence_reference"] = {
        "note": (
            "chunk_id pertinentes por mecanismo, derivados de mechanisms.yaml (causal + "
            "componente). Congelados antes de ejecutar. PENDIENTE de validación del autor "
            "como evaluador humano antes de EXP-RET-001."
        ),
        "validated_by_author": False,
        "by_mechanism": {
            mechanism: sorted(
                f"{document_id}#{chunk['seq']}"
                for document_id in (set(rule["causal"]) | set(rule["componente"]))
                if document_id in by_id
                for chunk in by_id[document_id]["chunks"]
            )
            for mechanism, rule in sorted(mech_spec["mechanisms"].items())
        },
    }

    FREEZE_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def verify() -> tuple[bool, list[str]]:
    """Recomprueba que cada variante en disco conserva el hash del manifiesto."""
    if not FREEZE_PATH.exists():
        return False, ["no existe el manifiesto; ejecuta la construcción primero"]
    manifest = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    problems: list[str] = []
    for name, entry in manifest["variants"].items():
        path = REPO_ROOT / entry["file"]
        if not path.exists():
            problems.append(f"{name}: falta {entry['file']}")
            continue
        digest = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        if digest != entry["sha256"]:
            problems.append(f"{name}: sha256 {digest[:12]}… ≠ {entry['sha256'][:12]}…")
    return not problems, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verifica los hashes congelados")
    args = parser.parse_args()

    if args.verify:
        ok, problems = verify()
        print("corpus VERIFICADO" if ok else "corpus ALTERADO:\n  " + "\n  ".join(problems))
        return 0 if ok else 1

    manifest = build_all()
    base = manifest["variants"]["corpus-CA"]
    print(
        f"C-A: {base['documents']} documentos · {base['chunks']} chunks · {base['words']} palabras"
    )
    print(f"variantes: {len(manifest['variants']) - 1}")
    for name, entry in manifest["variants"].items():
        if name == "corpus-CA":
            continue
        print(
            f"  {name:34s} {entry['chunks']:4d} chunks "
            f"(−{len(entry['removed_documents'])} docs, +{len(entry['filler_documents'])} relleno)"
        )
    print(f"\nmanifiesto: {FREEZE_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
