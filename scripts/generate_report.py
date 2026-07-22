#!/usr/bin/env python3
"""Assemble un rapport SEO/GEO final unique : audit technique (par URL) +
validation schema + donnees mesurees Search Console (si credentials fournis).

Produit deux fichiers : un Markdown lisible (style AUDIT_GEO.md) et un JSON
machine-lisible (pour un futur dashboard -- voir la lacune identifiee dans
ARCHITECTURE.md de seo-geo-optimizer : aucun script ne produisait de sortie
structuree jusqu'ici).

Usage minimal (technique + schema seulement) :
    python generate_report.py --urls urls.txt --out-prefix rapport

Avec Search Console (donnee mesuree en plus des inferences HTML) :
    python generate_report.py --urls urls.txt --out-prefix rapport \
        --gsc-service-account creds.json --gsc-site sc-domain:example.com \
        --gsc-path-filter https://example.com/

Necessite : pip install requests (+ google-auth si --gsc-service-account utilise)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_schema import extract_blocks_from_text, validate_blocks  # noqa: E402

TITLE_RE = re.compile(r"<title>([^<]*)</title>", re.IGNORECASE)
DESC_RE = re.compile(r'name=["\']description["\'][^>]*content=["\']([^"\']*)', re.IGNORECASE)
CANONICAL_RE = re.compile(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']*)', re.IGNORECASE)
OG_TITLE_RE = re.compile(r'property=["\']og:title["\']', re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>", re.IGNORECASE)


@dataclass
class PageAudit:
    url: str
    http_status: int | None = None
    title: str | None = None
    has_description: bool = False
    has_canonical: bool = False
    has_og: bool = False
    h1_count: int = 0
    schema_results: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def issues(self) -> list[str]:
        problems = []
        if self.http_status and self.http_status != 200:
            problems.append(f"HTTP {self.http_status} (attendu 200)")
        if not self.title:
            problems.append("title manquant")
        if not self.has_description:
            problems.append("meta description manquante")
        if not self.has_canonical:
            problems.append("canonical manquant")
        if self.h1_count == 0:
            problems.append("aucun H1")
        elif self.h1_count > 1:
            problems.append(f"{self.h1_count} H1 (attendu 1)")
        for r in self.schema_results:
            if not r["valid"]:
                problems.append(f"schema invalide ({r['block']}): {r['error']}")
        return problems


USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/1.0)"


def audit_url(url: str, timeout: float = 20.0) -> PageAudit:
    audit = PageAudit(url=url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            audit.http_status = resp.status
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        audit.http_status = e.code
        audit.error = f"HTTP {e.code}"
        return audit
    except Exception as e:
        audit.error = str(e)
        return audit

    title_match = TITLE_RE.search(html)
    audit.title = title_match.group(1).strip() if title_match else None
    audit.has_description = bool(DESC_RE.search(html))
    audit.has_canonical = bool(CANONICAL_RE.search(html))
    audit.has_og = bool(OG_TITLE_RE.search(html))
    audit.h1_count = len(H1_RE.findall(html))

    blocks = extract_blocks_from_text(html)
    audit.schema_results = validate_blocks(blocks, label=url)

    return audit


def build_markdown(audits: list[PageAudit], gsc_data: dict | None) -> str:
    lines = [
        f"# Rapport SEO/GEO consolidé — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "Généré par `scripts/generate_report.py` (seo-geo-optimizer). "
        "Sections techniques : inférées depuis le HTML public. "
        "Section Search Console (si présente) : donnée mesurée réelle, voir `references/data-hygiene.md`.",
        "",
        "## Résumé",
        f"- {len(audits)} URL(s) auditée(s)",
        f"- {sum(1 for a in audits if not a.issues)} sans problème détecté",
        f"- {sum(1 for a in audits if a.issues)} avec au moins un problème",
        "",
        "## Détail par page",
    ]
    for a in audits:
        lines.append(f"\n### {a.url}")
        if a.error:
            lines.append(f"- **Erreur** : {a.error}")
            continue
        if not a.issues:
            lines.append("- Aucun problème détecté (title/description/canonical/H1/schema OK).")
        else:
            for issue in a.issues:
                lines.append(f"- **{issue}**")
        if a.schema_results:
            types = [t for r in a.schema_results for t in r["types"]]
            if types:
                lines.append(f"- Schema présent : {', '.join(types)}")

    if gsc_data:
        lines.append("\n## Search Console (donnée mesurée)")
        lines.append(
            f"Période : {gsc_data['start_date']} → {gsc_data['end_date']} "
            f"(propriété `{gsc_data['site']}`{', filtré sur ' + gsc_data['path_filter'] if gsc_data.get('path_filter') else ''})"
        )
        lines.append("")
        lines.append("| Page/requête | Clics | Impressions | CTR | Position |")
        lines.append("|---|---|---|---|---|")
        for row in gsc_data["rows"]:
            lines.append(f"| {row['key']} | {row['clicks']} | {row['impressions']} | {row['ctr']}% | {row['position']} |")
        zero_impression_urls = [a.url for a in audits if not any(r["key"] == a.url for r in gsc_data["rows"])]
        if zero_impression_urls:
            lines.append(
                f"\n**{len(zero_impression_urls)} page(s) auditée(s) sans aucune impression Search Console "
                f"sur cette période** : {', '.join(zero_impression_urls)} — normal si récentes, à re-vérifier plus tard."
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--urls", required=True, type=Path, help="Fichier avec une URL par ligne")
    parser.add_argument("--out-prefix", required=True, type=Path, help="Prefixe de sortie (ecrit <prefix>.md et <prefix>.json)")
    parser.add_argument("--gsc-service-account", type=Path, default=None)
    parser.add_argument("--gsc-site", default=None)
    parser.add_argument("--gsc-path-filter", default=None)
    parser.add_argument("--gsc-days", type=int, default=28)
    args = parser.parse_args()

    urls = [u.strip() for u in args.urls.read_text(encoding="utf-8").splitlines() if u.strip()]
    print(f"Audit de {len(urls)} URL(s)...")
    audits = [audit_url(u) for u in urls]

    gsc_data = None
    if args.gsc_service_account and args.gsc_site:
        print("Requete Search Console...")
        import gsc_report

        token = gsc_report.get_access_token(args.gsc_service_account)
        from datetime import timedelta

        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=args.gsc_days)
        rows = gsc_report.query_search_analytics(
            token, args.gsc_site, start.isoformat(), end.isoformat(),
            dimension="page", path_filter=args.gsc_path_filter, row_limit=100,
        )
        gsc_data = {
            "site": args.gsc_site,
            "path_filter": args.gsc_path_filter,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "rows": rows,
        }

    markdown = build_markdown(audits, gsc_data)
    md_path = args.out_prefix.with_suffix(".md")
    md_path.write_text(markdown, encoding="utf-8")

    json_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pages": [
            {
                "url": a.url, "http_status": a.http_status, "title": a.title,
                "has_description": a.has_description, "has_canonical": a.has_canonical,
                "has_og": a.has_og, "h1_count": a.h1_count,
                "schema_results": a.schema_results, "issues": a.issues, "error": a.error,
            }
            for a in audits
        ],
        "search_console": gsc_data,
    }
    json_path = args.out_prefix.with_suffix(".json")
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Ecrit : {md_path}")
    print(f"Ecrit : {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
