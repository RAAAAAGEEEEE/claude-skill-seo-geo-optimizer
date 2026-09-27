#!/usr/bin/env python3
"""Rapport SEO/GEO consolide : audit technique par URL (parseur HTML reel),
reciprocite hreflang, validation schema, acces reel des crawlers IA, Core Web
Vitals terrain et Search Console -- tout ce qui est mesurable, en une commande.

Produit deux fichiers : <prefix>.md (lisible) et <prefix>.json (machine).

Usage minimal (technique + schema + hreflang, aucun acces requis) :
    python generate_report.py --urls urls.txt --out-prefix rapport

Complet (acces crawlers IA + CrUX via la variable CRUX_API_KEY + Search Console) :
    python generate_report.py --urls urls.txt --out-prefix rapport \
        --check-ai-access \
        --gsc-service-account creds.json --gsc-site sc-domain:example.com \
        --gsc-path-filter https://example.com/

Chaque section indique sa nature : "inferee" (lecture du HTML public) ou
"mesuree" (requete HTTP reelle, CrUX, Search Console) -- cf.
references/data-hygiene.md.

Stdlib uniquement, sauf --gsc-service-account (pip install google-auth requests).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from htmlsignals import PageSignals, fetch_signals  # noqa: E402
from audit_rules import hreflang_checks, page_checks  # noqa: E402
from validate_schema import validate_blocks  # noqa: E402

CITATION_ROLES = ("search", "user", "engine")


@dataclass
class PageAudit:
    signals: PageSignals
    schema_results: list[dict] = field(default_factory=list)

    @property
    def url(self) -> str:
        return self.signals.url

    @property
    def checks(self) -> list[dict]:
        return page_checks(self.signals, self.schema_results)

    @property
    def issues(self) -> list[str]:
        return [c["message"] for c in self.checks if c["kind"] == "issue"]

    @property
    def notes(self) -> list[str]:
        return [c["message"] for c in self.checks if c["kind"] == "note"]


def audit_url(url: str) -> PageAudit:
    signals = fetch_signals(url)
    audit = PageAudit(signals=signals)
    if signals.jsonld_blocks:
        audit.schema_results = validate_blocks(signals.jsonld_blocks, label=url)
    return audit


def check_hreflang_reciprocity(audits: list[PageAudit]) -> list[str]:
    """Self-reference, x-default and return links (rules: audit_rules.py)."""
    return [c["message"] for c in hreflang_checks([a.signals for a in audits])]


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def build_markdown(audits: list[PageAudit], gsc_data: dict | None, ai_access: dict | None, crux_data: dict | None) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Rapport SEO/GEO consolidé — {today}",
        "",
        "Généré par `scripts/generate_report.py` (seo-geo-optimizer). Technique et schema : "
        "**inférés** du HTML public servi sans JavaScript. Accès crawlers, CrUX, Search Console : "
        "**mesurés** (voir `references/data-hygiene.md`).",
        "",
        "## Résumé",
        f"- {len(audits)} URL(s) auditée(s), {sum(1 for a in audits if not a.issues)} sans problème détecté",
    ]

    if ai_access:
        blocked = [b for b in ai_access["bots"] if b["role"] in CITATION_ROLES and b["verdict"] in ("blocked-upstream", "blocked-by-robots")]
        if blocked:
            lines.append(
                f"- **P0 — {len(blocked)} crawler(s) de recherche/citation bloqué(s)** : "
                + ", ".join(f"`{b['token']}`" for b in blocked)
            )
        else:
            lines.append("- Accès des crawlers de recherche/citation : aucun blocage détecté (UA simulés)")
        lines += ["", "## Accès des crawlers IA (mesuré, user-agents simulés)", ""]
        base = ai_access.get("baseline", {})
        lines.append(f"Référence navigateur : HTTP {base.get('http_status') or 'erreur'}"
                     + (f", CDN détecté : {base['cdn']}" if base.get("cdn") else ""))
        lines += ["", "| Crawler | Rôle | robots.txt | HTTP | Verdict |", "|---|---|---|---|---|"]
        for b in ai_access["bots"]:
            robots_col = {True: "allow", False: "**DENY**", None: "?"}[b["robots_allows"]]
            lines.append(
                f"| `{b['token']}` ({_cell(b['vendor'])}) | {b['role']} | {robots_col} | "
                f"{b['http_status'] or '—'} | {b['verdict']} |"
            )
        lines += [
            "",
            "Une requête avec un user-agent simulé ne vient pas des IP du fournisseur : un 403 indique une règle "
            "par user-agent (CDN/WAF), un 200 ne garantit pas que le vrai bot passe. Confirmer dans les journaux "
            "serveur ou le tableau de bord CDN. Voir `references/cloudflare-ai-access.md`.",
        ]

    if crux_data:
        lines += ["", "## Core Web Vitals — terrain (CrUX, mesuré)", ""]
        if crux_data.get("no_data"):
            lines.append("Aucune donnée CrUX : trafic Chrome réel insuffisant sur 28 jours. Ce n'est **pas** un "
                         "problème de performance ; se rabattre sur une mesure labo et l'étiqueter comme telle.")
        else:
            lines += ["| Métrique | p75 | État |", "|---|---|---|"]
            for m in crux_data.get("metrics", []):
                value = f"{m['p75']:.2f}" if m["unit"] == "" else f"{m['p75']:.0f}{m['unit']}"
                lines.append(f"| {m['label']} | {value} | {m['rating']} |")

    hreflang_problems = check_hreflang_reciprocity(audits)
    if any(a.signals.hreflang_links for a in audits):
        lines += ["", "## hreflang (inféré)"]
        if hreflang_problems:
            lines += [f"- {p}" for p in hreflang_problems]
        else:
            lines.append("Auto-référence et liens retour OK sur les paires vérifiables dans ce périmètre.")

    lines += ["", "## Détail par page (inféré)"]
    for a in audits:
        s = a.signals
        lines.append(f"\n### {a.url}")
        if s.redirects:
            chain = " → ".join(f"{code} {target}" for code, target in s.redirects)
            lines.append(f"- Redirections : {chain}")
        if a.issues:
            lines += [f"- **{issue}**" for issue in a.issues]
        else:
            lines.append("- Aucun problème détecté (HTTP, indexabilité, title, description, canonical, H1, lang, schema).")
        lines += [f"- {n}" for n in a.notes]
        types = sorted({t for r in a.schema_results for t in r["types"]})
        if types:
            lines.append(f"- Schema : {', '.join(types)}")

    if gsc_data:
        lines += ["", "## Search Console (mesuré)"]
        lines.append(
            f"Période : {gsc_data['start_date']} → {gsc_data['end_date']}, type `{gsc_data.get('search_type', 'web')}` "
            f"(propriété `{gsc_data['site']}`"
            f"{', filtré sur ' + gsc_data['path_filter'] if gsc_data.get('path_filter') else ''}). "
            "AI Overviews et AI Mode sont comptés dans le type `web` ; le rapport « Generative AI performance » "
            "(impressions seulement) n'existe que dans l'interface Search Console, pas dans l'API "
            "(voir references/google-ai-features.md)."
        )
        lines += ["", "| Page | Clics | Impressions | CTR | Position |", "|---|---|---|---|---|"]
        for row in gsc_data["rows"]:
            lines.append(f"| {_cell(row['key'])} | {row['clicks']} | {row['impressions']} | {row['ctr']}% | {row['position']} |")
        seen = {r["key"] for r in gsc_data["rows"]}
        missing = [a.url for a in audits if a.url not in seen and (a.signals.final_url or "") not in seen]
        if missing:
            lines.append(f"\n**{len(missing)} page(s) auditée(s) sans impression sur la période** : "
                         f"{', '.join(missing)} — normal si récentes, sinon vérifier l'indexation.")
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--urls", required=True, type=Path, help="Fichier avec une URL par ligne")
    parser.add_argument("--out-prefix", required=True, type=Path, help="Ecrit <prefix>.md et <prefix>.json")
    parser.add_argument("--gsc-service-account", type=Path, default=None)
    parser.add_argument("--gsc-site", default=None)
    parser.add_argument("--gsc-path-filter", default=None)
    parser.add_argument("--gsc-days", type=int, default=28)
    parser.add_argument("--check-ai-access", action="store_true",
                        help="Teste l'acces reel des crawlers IA sur la 1re URL")
    parser.add_argument("--crux-key", default=None,
                        help="Deprecie (visible dans la liste des processus) : preferer la variable CRUX_API_KEY")
    args = parser.parse_args()

    urls = [u.strip() for u in args.urls.read_text(encoding="utf-8").splitlines() if u.strip() and not u.startswith("#")]
    if not urls:
        print("Aucune URL.", file=sys.stderr)
        return 1
    first = urllib.parse.urlparse(urls[0])
    origin = f"{first.scheme}://{first.netloc}"

    ai_access = None
    if args.check_ai_access:
        print(f"Acces des crawlers IA sur {urls[0]}...")
        import check_ai_access

        ai_access = check_ai_access.check_site(urls[0])

    crux_key = args.crux_key or os.environ.get("CRUX_API_KEY") or None
    crux_data = None
    if crux_key:
        print(f"CrUX sur {origin}...")
        import crux_report

        record = crux_report.query_crux(crux_key, {"origin": origin}, None)
        crux_data = {"no_data": True} if record is None else {"metrics": crux_report.extract(record)}

    print(f"Audit de {len(urls)} URL(s)...")
    audits = [audit_url(u) for u in urls]

    gsc_data = None
    if args.gsc_service_account and args.gsc_site:
        print("Search Console...")
        import gsc_report

        token = gsc_report.get_access_token(args.gsc_service_account)
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=args.gsc_days)
        rows = gsc_report.query_search_analytics(
            token, args.gsc_site, start.isoformat(), end.isoformat(),
            dimension="page", path_filter=args.gsc_path_filter, row_limit=250,
        )
        gsc_data = {"site": args.gsc_site, "path_filter": args.gsc_path_filter, "search_type": "web",
                    "start_date": start.isoformat(), "end_date": end.isoformat(), "rows": rows}

    md_path = args.out_prefix.with_suffix(".md")
    md_path.write_text(build_markdown(audits, gsc_data, ai_access, crux_data), encoding="utf-8")

    json_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "seo-geo-optimizer/scripts/generate_report.py",
        "pages": [
            {
                "url": a.url, "final_url": a.signals.final_url, "http_status": a.signals.http_status,
                "redirects": a.signals.redirects, "title": a.signals.title, "description": a.signals.description,
                "canonical": a.signals.canonical, "html_lang": a.signals.html_lang,
                "robots_directives": a.signals.robots_directives, "noindex": a.signals.noindex,
                "nosnippet": a.signals.nosnippet, "h1_count": a.signals.h1_count,
                "has_og_title": a.signals.has_og_title, "hreflang_links": a.signals.hreflang_links,
                "schema_results": a.schema_results, "issues": a.issues, "notes": a.notes,
                "error": a.signals.error, "nature": "inferred",
            }
            for a in audits
        ],
        "hreflang_problems": check_hreflang_reciprocity(audits),
        "ai_access": ai_access,
        "core_web_vitals": crux_data,
        "search_console": gsc_data,
    }
    json_path = args.out_prefix.with_suffix(".json")
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Ecrit : {md_path}")
    print(f"Ecrit : {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
