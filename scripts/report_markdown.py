#!/usr/bin/env python3
"""Markdown rendering of a run_audit.py JSON report (French, for the site
owner). Pure function of the JSON: re-render an old report with
    python report_markdown.py audit_20260928T090000Z.json > audit.md

Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PRIORITY_TEXT = {
    "P0": "P0 — bloquant (accès des crawlers ou du site)",
    "P1": "P1 — indexation et cohérence cassées",
    "P2": "P2 — qualité, hygiène, maillage",
}
MODULE_TEXT = {
    "ai_access": "Accès crawlers IA", "sitemaps": "Sitemaps", "crawl": "Crawl", "probes_404": "URLs inexistantes",
    "coherence": "Cohérence", "link_graph": "Maillage interne", "pagespeed": "PageSpeed Insights",
    "crux": "CrUX (terrain)", "search_console": "Search Console", "indexnow": "IndexNow",
}


def _cell(value: object) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def render(r: dict) -> str:
    s = r["summary"]
    f = s["findings"]
    date = r["finished_at"][:16].replace("T", " ")
    out = [
        f"# Audit SEO/GEO — {r.get('home') or r['site']} — {date} UTC",
        "",
        f"Généré par `{r['generator']}` ({r['requests']} requêtes HTTP). **Mesuré** = requête HTTP, CrUX, "
        "PageSpeed, Search Console ; **inféré** = lecture du HTML servi sans JavaScript. Étiquettes des règles : "
        "ESTABLISHED (doc officielle), SUPPORTED (étude indépendante), CLAIMED (praticien ou vendeur, jamais "
        "seul à l'origine d'une priorité P0/P1) — voir `references/data-hygiene.md`.",
        "",
        "## Résumé",
        f"- **P0 : {f['P0']}** · **P1 : {f['P1']}** · P2 : {f['P2']}",
        f"- {s['pages_fetched']} page(s) récupérée(s) ; {s['sitemap_urls']} URL(s) déclarée(s) dans les sitemaps ; "
        + ("toutes vérifiées." if s["crawl_complete"] else
           "**échantillon** : les pages orphelines et la profondeur sont des estimations."),
    ]
    if s.get("skipped_by_robots"):
        out.append(f"- {len(s['skipped_by_robots'])} URL(s) non visitée(s) car interdites par robots.txt.")
    if r.get("previous_report"):
        out.append(f"- Comparé au rapport précédent : `{Path(r['previous_report']).name}` (voir le fichier diff_*.md).")
    out += ["", "| Module | État | Détail |", "|---|---|---|"]
    for name, m in r["modules"].items():
        out.append(f"| {MODULE_TEXT.get(name, name)} | {m['status']} | {_cell(m['reason'])} |")

    out += ["", "## Plan de correction priorisé", ""]
    if not r["findings"]:
        out.append("Aucun constat.")
    for prio in ("P0", "P1", "P2"):
        items = [x for x in r["findings"] if x["priority"] == prio]
        if not items:
            continue
        out += [f"### {PRIORITY_TEXT[prio]} ({len(items)})", ""]
        for i, x in enumerate(items, 1):
            out.append(f"{i}. **{x['title']}** — {x['count']} occurrence(s) · {x['category']} · "
                       f"{x['label']} · {x['nature']}")
            out.append(f"   - Correctif : {x['fix']}")
            for u in x["urls"][:5]:
                out.append(f"   - {u}")
            if len(x["urls"]) > 5 or x.get("urls_truncated"):
                out.append(f"   - … et {x['count'] - min(5, len(x['urls']))} autre(s) (voir le JSON)")
            for d in x["details"][:3]:
                out.append(f"   - détail : {d}")
            out.append(f"   - Source : {x['source']}")
        out.append("")

    ai = r.get("ai_access")
    if ai:
        out += ["## Accès des crawlers (mesuré, user-agents simulés)", "",
                f"robots.txt : HTTP {ai['robots_txt']['status']} ; référence navigateur : HTTP "
                f"{ai['baseline']['http_status']}" + (f", CDN : {ai['baseline']['cdn']}" if ai["baseline"].get("cdn") else ""),
                "", "| Crawler | Rôle | robots.txt | HTTP | Verdict |", "|---|---|---|---|---|"]
        for b in ai["bots"]:
            robots_col = {True: "allow", False: "**DENY**", None: "?"}[b["robots_allows"]]
            out.append(f"| `{b['token']}` ({_cell(b['vendor'])}) | {b['role']} | {robots_col} | "
                       f"{b['http_status'] or '—'} | {b['verdict']} |")
        out += ["", "Un 403 prouve une règle par user-agent ; un 200 ne prouve pas que le vrai bot (IP du "
                "fournisseur) passe. Confirmer dans les journaux ou le tableau de bord CDN.", ""]

    sm = r.get("sitemaps") or {}
    if sm.get("read"):
        out += ["## Sitemaps (mesuré)", "", "| Fichier | HTTP | Type | URLs | Erreur |", "|---|---|---|---|---|"]
        for x in sm["read"]:
            out.append(f"| {x['url']} | {_cell(x['status'])} | {_cell(x['kind'])} | {x['count']} | {_cell(x['error'])} |")
        lm = sm.get("lastmod") or {}
        if lm:
            out.append(f"\n`lastmod` renseigné sur {lm['with_lastmod']}/{lm['total']} entrée(s).")
        out.append("")

    if r.get("probes_404"):
        out += ["## URLs inexistantes (mesuré ; attendu : 404 ou 410)", ""]
        out += [f"- {p['url']} → HTTP {p['status'] or p.get('error')}" for p in r["probes_404"]]
        out.append("")

    g = r.get("link_graph")
    if g:
        out += ["## Maillage interne (inféré)", "",
                f"{g['edges']} lien(s) interne(s) entre pages ; zones : "
                + ", ".join(f"{k} {v}" for k, v in sorted(g["zones"].items()))
                + ("" if g["zone_known"] else " — pas de `<main>`/`<nav>` : liens contextuels non distinguables"),
                f"Orphelines : {len(g['orphans'])} ; au-delà de {g['max_depth']} clics : {len(g['deep'])} ; "
                f"non atteignables depuis l'accueil : {len(g['unreachable_from_home'])} ; liens cassés : {len(g['broken'])}.",
                "", "### Cocon / silos par répertoire (heuristique CLAIMED, voir references/french-practitioners.md)", ""]
        if g["clusters"]:
            out += ["| Rubrique | Page mère | Filles | Filles → mère | dont dans le texte | Mère → filles | "
                    "Liens entre sœurs (texte) | Liens contextuels sortant de la rubrique |",
                    "|---|---|---|---|---|---|---|---|"]
            for c in g["clusters"]:
                share = "—" if c["contextual_leaving_share"] is None else f"{int(c['contextual_leaving_share'] * 100)} %"
                out.append(f"| `{c['cluster']}` | {'oui' if c['mother'] else '**absente**'} | {c['children']} | "
                           f"{c['children_linking_mother']} | {c['children_linking_mother_in_text']} | "
                           f"{c['mother_linking_children']} | {c['sibling_links_in_text']} | {share} |")
        else:
            out.append("Aucune rubrique à plusieurs niveaux dans l'échantillon.")
        out.append("")

    if r.get("pagespeed"):
        out += ["## PageSpeed Insights (mesuré)", "", "| Page | Score labo | Terrain (page) | Terrain (origine) |",
                "|---|---|---|---|"]
        for p in r["pagespeed"]:
            def fld(block):
                if not block:
                    return "aucune donnée"
                return f"{block['overall']} (" + ", ".join(f"{m['label']} {m['p75']}{m['unit']}" for m in block["metrics"]
                                                          if m["label"] in ("LCP", "INP", "CLS")) + ")"
            out.append(f"| {p['url']} | {_cell(p['performance_score'])} | {fld(p['field_page'])} | {fld(p['field_origin'])} |")
        out.append("")
    crux = r.get("crux")
    if crux:
        out += ["## Core Web Vitals — CrUX origine (mesuré)", ""]
        if crux.get("no_data"):
            out.append("Aucune donnée CrUX : trafic Chrome insuffisant, pas un problème de performance.")
        else:
            out += ["| Métrique | p75 | État |", "|---|---|---|"]
            for m in crux["metrics"]:
                v = f"{m['p75']:.2f}" if m["unit"] == "" else f"{m['p75']:.0f}{m['unit']}"
                out.append(f"| {m['label']} | {v} | {m['rating']} |")
        out.append("")
    gsc = r.get("search_console")
    if gsc:
        out += ["## Search Console (mesuré)", "",
                f"Propriété `{gsc['site']}`, {gsc['start_date']} → {gsc['end_date']} : {gsc['clicks']} clic(s), "
                f"{gsc['impressions']} impression(s), {gsc['pages_with_impressions']} page(s) avec impressions. "
                "AI Overviews / AI Mode sont inclus dans le type `web`, sans distinction dans l'API.", ""]
    ix = r.get("indexnow")
    if ix:
        out += ["## IndexNow", "",
                f"Fichier de clé à la racine : {'vérifié' if ix['key_file_ok'] else '**absent ou incorrect**'} ; "
                f"{len(ix['changed_urls'])} URL(s) nouvelle(s) ou modifiée(s) ; "
                + (f"soumises : {ix['response']}" if ix["submitted"] else "non soumises."), ""]

    out += ["## Détail par page", "",
            "| URL | HTTP | Prof. | Liens entrants (texte) | Mots | Sitemap | Constats |", "|---|---|---|---|---|---|---|"]
    for p in r["pages"]:
        inl = f"{p.get('inlinks', '—')} ({p.get('inlinks_in_text', '—')})"
        words = p["main_words"] if p.get("main_words") is not None else p.get("words")
        out.append(f"| {p['url']} | {_cell(p['http_status'])} | {_cell(p.get('depth'))} | {inl} | {_cell(words)} | "
                   f"{'oui' if p['in_sitemap'] else 'non'} | {_cell(', '.join(p['issues']) or '—')} |")
    out += ["", "## Limites de ce rapport",
            "- Pas de rendu JavaScript : contenu, liens ou JSON-LD injectés côté client sont invisibles ici.",
            "- User-agents simulés depuis cette machine : un 200 ne garantit pas l'accès du vrai crawler.",
            "- Les seuils de profondeur, de mots et d'ancres répétées sont des heuristiques du skill (CLAIMED).",
            "- Aucune mesure des citations dans ChatGPT, Claude, Perplexity ; rapports IA de Search Console et de "
            "Bing : interface seulement.", ""]
    return "\n".join(out)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("Usage: python report_markdown.py audit_<stamp>.json", file=sys.stderr)
        return 1
    print(render(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
