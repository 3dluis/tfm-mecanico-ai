"""Descarga de la capa externa del corpus C-A con revisión fijada (R3, PI v4).

Obtiene el extracto en texto plano de cada artículo declarado en
``diagnostic-agent/knowledge/corpus_v2/sources.yaml`` y lo versiona en
``corpus_v2/external/<key>.txt`` junto con su procedencia (URL, licencia, ``revid`` y
marca temporal de la revisión). **Fijar la revisión es lo que hace el corpus
reproducible**: aunque el artículo cambie, el texto usado en el experimento es el del
``revid`` registrado.

Library-first (ADR-0035): sólo biblioteca estándar más ``yaml``; aquí no hay más que
orquestación de red y escritura de procedencia.

Uso:
    python tools/fetch_corpus_sources.py            # descarga lo que falte
    python tools/fetch_corpus_sources.py --refresh  # vuelve a descargar todo
"""

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "diagnostic-agent" / "knowledge" / "corpus_v2"
SPEC_PATH = CORPUS_DIR / "sources.yaml"
EXTERNAL_DIR = CORPUS_DIR / "external"
PROVENANCE_PATH = EXTERNAL_DIR / "provenance.json"

#: Pausa entre peticiones. La API devuelve 429 con ráfagas; el respeto del ritmo es
#: requisito de su política de uso, no una cortesía.
THROTTLE_S = 2.0


def fetch_article(lang: str, title: str, user_agent: str) -> dict[str, Any]:
    """Extracto en texto plano más la procedencia de la revisión concreta."""
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "extracts|revisions",
            "rvprop": "ids|timestamp",
            "explaintext": 1,
            "format": "json",
            "titles": title,
            "redirects": 1,
        }
    )
    url = f"https://{lang}.wikipedia.org/w/api.php?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    page = next(iter(payload["query"]["pages"].values()))
    if "missing" in page:
        raise LookupError(f"{lang}:{title} no existe")
    revision = page["revisions"][0]
    return {
        "resolved_title": page["title"],
        "text": page.get("extract", "") or "",
        "revid": revision["revid"],
        "revision_timestamp": revision["timestamp"],
        "url": (
            f"https://{lang}.wikipedia.org/wiki/"
            f"{urllib.parse.quote(page['title'].replace(' ', '_'))}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="vuelve a descargar todo")
    args = parser.parse_args()

    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    external = spec["external"]
    user_agent = external["user_agent"]
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    provenance: dict[str, Any] = {}
    if PROVENANCE_PATH.exists() and not args.refresh:
        provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

    failures: list[str] = []
    articles = list(external["articles"]) + list(spec.get("reserve", {}).get("articles", []))
    for article in articles:
        key = article["key"]
        target = EXTERNAL_DIR / f"{key}.txt"
        if target.exists() and key in provenance and not args.refresh:
            print(f"  = {key:18s} ya descargado (rev {provenance[key]['revid']})")
            continue
        try:
            fetched = fetch_article(article["lang"], article["title"], user_agent)
        except Exception as exc:
            failures.append(f"{key}: {exc}")
            print(f"  ! {key:18s} ERROR {exc}")
            time.sleep(THROTTLE_S)
            continue
        target.write_text(fetched["text"], encoding="utf-8")
        provenance[key] = {
            "lang": article["lang"],
            "requested_title": article["title"],
            "resolved_title": fetched["resolved_title"],
            "url": fetched["url"],
            "revid": fetched["revid"],
            "revision_timestamp": fetched["revision_timestamp"],
            "license": external["license"],
            "words": len(fetched["text"].split()),
            "topic": article["topic"],
            "component": article["component"],
        }
        print(f"  + {key:18s} {provenance[key]['words']:6d} pal.  rev={fetched['revid']}")
        time.sleep(THROTTLE_S)

    PROVENANCE_PATH.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    total = sum(entry["words"] for entry in provenance.values())
    print(
        f"\n{len(provenance)} artículos · {total} palabras · procedencia en {PROVENANCE_PATH.name}"
    )
    if failures:
        print("FALLOS:\n  " + "\n  ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
