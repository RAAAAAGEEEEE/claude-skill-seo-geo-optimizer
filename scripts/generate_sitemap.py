#!/usr/bin/env python3
"""Genere sitemap.xml (+ robots.txt optionnel) pour un site ou un
deploiement multi-sites, sans dependance a un schema de base de donnees
particulier.

Usage:
    python generate_sitemap.py pages.json --domain https://example.com \
        --out sitemap.xml [--extra-urls extra.json] \
        [--write-robots --ai-policy open|search-only]

Format de pages.json (liste d'objets, "url" relative au domaine ou absolue) :
    [
      {"url": "/", "lastmod": "2026-09-20"},
      {"url": "/tarifs.html"}
    ]

Regles appliquees (Google Search Central, "Build and submit a sitemap") :
- `lastmod` n'est ecrit que s'il est fourni. Google l'utilise seulement s'il
  est "consistently and verifiably accurate" : dater toutes les pages du jour
  de generation (ancien comportement de ce script) apprend a Google a ignorer
  le champ pour tout le site.
- `changefreq` et `priority` sont ignores par Google ; ils ne sont ecrits que
  s'ils sont fournis explicitement (Bing et d'autres peuvent les lire).
- Les URLs sont echappees en XML (& < > " ').
- 50 000 URLs ou 50 Mo max par fichier : au-dela, decouper et faire un index.

--extra-urls pointe vers un fichier JSON de meme forme, genere par
n'importe quelle source externe (export d'une DB, liste de sous-domaines...)
-- ce script ne lit jamais une DB directement.

--ai-policy (avec --write-robots) :
- open        : tous les crawlers IA autorises explicitement (defaut).
- search-only : crawlers d'entrainement interdits, crawlers de recherche et
                fetchers declenches par l'utilisateur autorises. Liste et roles :
                scripts/ai_bots.py, references/ai-crawlers.md.
C'est une decision produit : ne pas la trancher a la place du proprietaire.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).parent))
from ai_bots import AI_BOTS  # noqa: E402

MAX_URLS_PER_FILE = 50_000
_ENTITIES = {'"': "&quot;", "'": "&apos;"}


def _xml(value: str) -> str:
    return escape(value, _ENTITIES)


def load_pages(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path}: attendu une liste JSON d'objets {{url, lastmod?}}")
    return data


def normalize_url(url: str, domain: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return domain.rstrip("/") + "/" + url.lstrip("/")


def build_sitemap(pages: list[dict], domain: str) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen: set[str] = set()
    for page in pages:
        url = normalize_url(page["url"], domain)
        if url in seen:
            continue
        seen.add(url)
        lines.append("  <url>")
        lines.append(f"    <loc>{_xml(url)}</loc>")
        for optional in ("lastmod", "changefreq", "priority"):
            if page.get(optional):
                lines.append(f"    <{optional}>{_xml(str(page[optional]))}</{optional}>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots(domain: str, ai_policy: str = "open") -> str:
    lines = ["User-agent: *", "Allow: /", ""]
    crawlers = [b for b in AI_BOTS if b.robots_token and b.robots_token.lower() not in ("googlebot", "bingbot")]
    if ai_policy == "search-only":
        lines.append("# Politique 'search-only' : pas d'entrainement, citation autorisee.")
        blocked = [b for b in crawlers if b.role in ("training", "token")]
        allowed = [b for b in crawlers if b.role not in ("training", "token")]
    else:
        lines.append("# Politique 'open' : crawlers IA autorises explicitement.")
        blocked, allowed = [], crawlers
    if blocked:
        for bot in blocked:
            lines.append(f"User-agent: {bot.robots_token}")
        lines += ["Disallow: /", ""]
    for bot in allowed:
        lines.append(f"User-agent: {bot.robots_token}")
    lines += ["Allow: /", ""]
    lines.append(f"Sitemap: {domain.rstrip('/')}/sitemap.xml")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages_file", type=Path, help="JSON: liste des pages du site")
    parser.add_argument("--domain", required=True, help="Domaine racine, ex: https://example.com")
    parser.add_argument("--out", type=Path, default=Path("sitemap.xml"), help="Fichier sitemap de sortie")
    parser.add_argument("--extra-urls", type=Path, default=None, help="JSON additionnel (multi-sites) au meme format")
    parser.add_argument("--write-robots", action="store_true", help="Ecrit aussi robots.txt a cote de --out")
    parser.add_argument("--ai-policy", choices=["open", "search-only"], default="open",
                        help="Politique crawlers IA du robots.txt genere (decision produit)")
    args = parser.parse_args()

    if not args.pages_file.exists():
        print(f"Introuvable : {args.pages_file}", file=sys.stderr)
        return 1

    pages = load_pages(args.pages_file)
    if args.extra_urls:
        if not args.extra_urls.exists():
            print(f"Introuvable : {args.extra_urls}", file=sys.stderr)
            return 1
        pages += load_pages(args.extra_urls)

    if len(pages) > MAX_URLS_PER_FILE:
        print(f"{len(pages)} URLs > {MAX_URLS_PER_FILE} par fichier : decouper en plusieurs sitemaps + index.",
              file=sys.stderr)
        return 1

    without_lastmod = sum(1 for p in pages if not p.get("lastmod"))
    args.out.write_text(build_sitemap(pages, args.domain), encoding="utf-8")
    print(f"Sitemap ecrit : {args.out} ({len(pages)} URL(s), {without_lastmod} sans lastmod -- "
          "normal si la date reelle de modification est inconnue)")

    if args.write_robots:
        robots_path = args.out.parent / "robots.txt"
        robots_path.write_text(build_robots(args.domain, args.ai_policy), encoding="utf-8")
        print(f"Robots.txt ecrit : {robots_path} (politique IA : {args.ai_policy})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
