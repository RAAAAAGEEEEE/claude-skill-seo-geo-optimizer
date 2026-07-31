#!/usr/bin/env python3
"""Soumet des URLs via le protocole IndexNow (Bing, Yandex, Naver, Seznam, Yep).

IndexNow est le SEUL mecanisme de soumission directe legitime et automatisable
couvert par ce skill. Ne pas confondre avec la Google Indexing API, dont
l'usage est restreint a JobPosting/BroadcastEvent et interdit ici (voir
references/indexing-rules.md). Google ne participe pas a IndexNow -- pour
Google, seul le sitemap + Search Console font foi.

Mise en place (une fois par site) :
1. Generer une cle : chaine hexadecimale de 8 a 128 caracteres.
   python -c "import uuid; print(uuid.uuid4().hex)"
2. Publier un fichier <cle>.txt a la racine du site, contenant uniquement
   la cle en texte brut. Ex : https://example.com/a1b2c3....txt
3. Verifier qu'il est accessible publiquement (le script le fait avant tout
   envoi et refuse de soumettre sinon).

Usage:
    # verifie la cle sans rien soumettre
    python indexnow_submit.py --host example.com --key <cle> --dry-run --urls urls.txt

    # soumission reelle
    python indexnow_submit.py --host example.com --key <cle> --urls urls.txt

Gratuit, sans quota documente, sans authentification autre que la cle.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS_PER_REQUEST = 10_000  # limite du protocole
USER_AGENT = "seo-geo-optimizer/1.0 (+IndexNow client)"


def verify_key_file(host: str, key: str, key_location: str | None) -> tuple[bool, str]:
    """Verifie que le fichier de cle est publiquement accessible et correct."""
    url = key_location or f"https://{host}/{key}.txt"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace").strip()
    except urllib.error.HTTPError as e:
        return False, f"{url} -> HTTP {e.code} (le fichier de cle doit etre public)"
    except Exception as e:
        return False, f"{url} -> {e}"

    if body != key:
        return False, f"{url} existe mais son contenu ne correspond pas a la cle fournie"
    return True, url


def submit(host: str, key: str, key_location: str, urls: list[str]) -> tuple[int, str]:
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def interpret_status(code: int) -> str:
    return {
        200: "OK -- URLs soumises",
        202: "Accepte -- cle en cours de validation par le moteur",
        400: "Requete invalide (format)",
        403: "Cle refusee -- le fichier de cle n'est pas valide cote moteur",
        422: "URLs invalides (ne correspondent pas au host, ou schema incorrect)",
        429: "Trop de requetes -- ralentir",
    }.get(code, f"Code inattendu {code}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", required=True, help="Domaine sans schema, ex: example.com")
    parser.add_argument("--key", required=True, help="Cle IndexNow (hex, 8-128 caracteres)")
    parser.add_argument("--key-location", default=None, help="URL du fichier de cle si non standard")
    parser.add_argument("--urls", required=True, type=Path, help="Fichier: une URL par ligne")
    parser.add_argument("--dry-run", action="store_true", help="Verifie la cle et les URLs, ne soumet rien")
    args = parser.parse_args()

    if not (8 <= len(args.key) <= 128) or not all(c in "0123456789abcdefABCDEF-" for c in args.key):
        print("Cle invalide : attendu 8 a 128 caracteres hexadecimaux.", file=sys.stderr)
        return 1

    urls = [u.strip() for u in args.urls.read_text(encoding="utf-8").splitlines() if u.strip()]
    if not urls:
        print("Aucune URL a soumettre.", file=sys.stderr)
        return 1
    if len(urls) > MAX_URLS_PER_REQUEST:
        print(f"{len(urls)} URLs > limite de {MAX_URLS_PER_REQUEST} par requete.", file=sys.stderr)
        return 1

    # Toutes les URLs doivent appartenir au host declare (regle du protocole).
    foreign = [u for u in urls if urllib.parse.urlparse(u).netloc != args.host]
    if foreign:
        print(f"{len(foreign)} URL(s) hors du host '{args.host}', ex: {foreign[0]}", file=sys.stderr)
        return 1

    ok, key_info = verify_key_file(args.host, args.key, args.key_location)
    if not ok:
        print(f"Verification de la cle ECHOUEE : {key_info}", file=sys.stderr)
        print("Publier le fichier de cle avant toute soumission.", file=sys.stderr)
        return 1
    print(f"Cle verifiee : {key_info}")
    print(f"{len(urls)} URL(s) pretes.")

    if args.dry_run:
        print("--dry-run : rien n'a ete soumis.")
        for u in urls[:10]:
            print(f"  {u}")
        if len(urls) > 10:
            print(f"  ... et {len(urls) - 10} autre(s)")
        return 0

    status, body = submit(args.host, args.key, key_info, urls)
    print(f"HTTP {status} -- {interpret_status(status)}")
    if body.strip():
        print(body[:500])
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
