#!/usr/bin/env python3
"""Genere sitemap.xml (+ robots.txt optionnel) pour un site ou un
deploiement multi-sites, sans dependance a un schema de base de donnees
particulier.

Usage:
    python generate_sitemap.py pages.json --domain https://example.com \
        --out sitemap.xml [--extra-urls extra.json] [--write-robots]

Format de pages.json (liste d'objets, "url" relative au domaine ou absolue) :
    [
      {"url": "/", "changefreq": "weekly", "priority": "1.0"},
      {"url": "/tarifs.html", "changefreq": "monthly", "priority": "0.8"}
    ]

--extra-urls pointe vers un fichier JSON de meme forme, genere par
n'importe quelle source externe (export CSV->JSON d'une DB de sites clients,
liste de sous-domaines, etc.) -- ce script ne lit jamais une DB directement,
pour rester reutilisable sur n'importe quel projet.

Champs optionnels par entree : "lastmod" (sinon: date du jour). Si "url" ne
commence pas par http, elle est prefixee par --domain.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CHANGEFREQ = "monthly"
DEFAULT_PRIORITY = "0.5"

AI_BOTS_ALLOW = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Perplexity-User",
    "Google-Extended", "Applebot-Extended",
]


def load_pages(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path}: attendu une liste JSON d'objets {{url, changefreq, priority}}")
    return data


def normalize_url(url: str, domain: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return domain.rstrip("/") + "/" + url.lstrip("/")


def build_sitemap(pages: list[dict], domain: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen = set()
    for page in pages:
        url = normalize_url(page["url"], domain)
        if url in seen:
            continue
        seen.add(url)
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{page.get('lastmod', today)}</lastmod>")
        lines.append(f"    <changefreq>{page.get('changefreq', DEFAULT_CHANGEFREQ)}</changefreq>")
        lines.append(f"    <priority>{page.get('priority', DEFAULT_PRIORITY)}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)


def build_robots(domain: str) -> str:
    lines = ["User-agent: *", "Allow: /", ""]
    lines.append("# Bots IA autorises explicitement (entrainement + recherche/citation)")
    for bot in AI_BOTS_ALLOW:
        lines.append(f"User-agent: {bot}")
        lines.append("Allow: /")
        lines.append("")
    lines.append(f"Sitemap: {domain.rstrip('/')}/sitemap.xml")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages_file", type=Path, help="JSON: liste des pages statiques du site")
    parser.add_argument("--domain", required=True, help="Domaine racine, ex: https://example.com")
    parser.add_argument("--out", type=Path, default=Path("sitemap.xml"), help="Fichier sitemap de sortie")
    parser.add_argument("--extra-urls", type=Path, default=None, help="JSON additionnel (multi-sites) au meme format")
    parser.add_argument("--write-robots", action="store_true", help="Ecrit aussi robots.txt a cote de --out")
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

    sitemap_xml = build_sitemap(pages, args.domain)
    args.out.write_text(sitemap_xml, encoding="utf-8")
    print(f"Sitemap ecrit : {args.out} ({len(pages)} URL(s))")

    if args.write_robots:
        robots_path = args.out.parent / "robots.txt"
        robots_path.write_text(build_robots(args.domain), encoding="utf-8")
        print(f"Robots.txt ecrit : {robots_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
