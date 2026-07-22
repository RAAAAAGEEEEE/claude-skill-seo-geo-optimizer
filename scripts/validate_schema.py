#!/usr/bin/env python3
"""Valide les blocs JSON-LD schema.org d'un fichier HTML ou d'un fichier .json.

Usage:
    python validate_schema.py <fichier.html|fichier.json> [...]

Vérifie uniquement la présence des champs requis par type schema.org
(sous-ensemble courant : LocalBusiness, Organization, FAQPage, Product,
Article, HowTo, BreadcrumbList). Ne remplace pas le Rich Results Test
(https://search.google.com/test/rich-results), qui reste la référence pour
l'éligibilité aux rich results Google.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = {
    "LocalBusiness": ["name", "address"],
    "Organization": ["name", "url"],
    "FAQPage": ["mainEntity"],
    "Product": ["name", "offers"],
    "Article": ["headline", "author", "datePublished"],
    "HowTo": ["name", "step"],
    "BreadcrumbList": ["itemListElement"],
    "Question": ["name", "acceptedAnswer"],
    "Offer": ["price", "priceCurrency"],
}

JSONLD_BLOCK_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def extract_blocks_from_text(text: str, is_json: bool = False) -> list[str]:
    if is_json:
        return [text]
    return JSONLD_BLOCK_RE.findall(text)


def extract_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return extract_blocks_from_text(text, is_json=path.suffix == ".json")


def validate_blocks(blocks: list[str], label: str) -> list[dict]:
    """Reutilisable par d'autres scripts (ex. generate_report.py) : valide une
    liste de blocs JSON-LD bruts (deja extraits), retourne un resultat structure
    par bloc plutot que d'imprimer sur stdout.
    """
    results = []
    for i, raw in enumerate(blocks):
        block_id = f"{label}#block{i}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            results.append({"block": block_id, "valid": False, "error": f"JSON invalide: {e}", "types": []})
            continue

        nodes = data if isinstance(data, list) else [data]
        errors: list[str] = []
        for node in nodes:
            if isinstance(node, dict):
                validate_node(node, block_id, errors)
        types = [resolve_type(n) for n in nodes if isinstance(n, dict) and resolve_type(n)]
        results.append({"block": block_id, "valid": not errors, "error": "; ".join(errors) if errors else None, "types": types})
    return results


def resolve_type(node: dict) -> str | None:
    t = node.get("@type")
    if isinstance(t, list):
        return t[0] if t else None
    return t


def validate_node(node: dict, path: str, errors: list[str]) -> None:
    node_type = resolve_type(node)
    if node_type and node_type in REQUIRED_FIELDS:
        for field in REQUIRED_FIELDS[node_type]:
            if field not in node:
                errors.append(f"{path}: type '{node_type}' - champ requis manquant: '{field}'")
    for key, value in node.items():
        if isinstance(value, dict):
            validate_node(value, f"{path}.{key}", errors)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    validate_node(item, f"{path}.{key}[{i}]", errors)


def validate_file(path: Path) -> tuple[int, int]:
    blocks = extract_blocks(path)
    if not blocks:
        print(f"{path}: aucun bloc JSON-LD trouvé")
        return 0, 0

    ok, ko = 0, 0
    for i, raw in enumerate(blocks):
        block_path = f"{path}#block{i}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"{block_path}: JSON invalide — {e}")
            ko += 1
            continue

        nodes = data if isinstance(data, list) else [data]
        errors: list[str] = []
        for node in nodes:
            if isinstance(node, dict):
                validate_node(node, block_path, errors)

        if errors:
            for err in errors:
                print(f"  INVALIDE  {err}")
            ko += 1
        else:
            node_types = [resolve_type(n) for n in nodes if isinstance(n, dict)]
            print(f"  OK        {block_path} ({', '.join(t for t in node_types if t)})")
            ok += 1

    return ok, ko


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    total_ok, total_ko = 0, 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"{path}: fichier introuvable")
            total_ko += 1
            continue
        ok, ko = validate_file(path)
        total_ok += ok
        total_ko += ko

    print(f"\n{total_ok} bloc(s) valide(s), {total_ko} invalide(s)/en erreur")
    return 1 if total_ko else 0


if __name__ == "__main__":
    sys.exit(main())
