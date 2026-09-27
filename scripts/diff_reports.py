#!/usr/bin/env python3
"""Compare two run_audit.py JSON reports of the same site: findings that
appeared, disappeared or changed scope, and the evolution of the key
figures (pages, orphans, Core Web Vitals, Search Console).

Usage:
    python diff_reports.py OLD.json NEW.json [--out diff.md]
    python diff_reports.py --dir seo-reports/example.com [--out diff.md]   # two latest reports

Exit code: 0, or 1 if a P0 finding appeared (usable as an alert in cron).
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _by_id(report: dict) -> dict[str, dict]:
    return {f["id"]: f for f in report.get("findings", [])}


def _metrics(report: dict) -> dict[str, float | int | None]:
    s = report.get("summary", {})
    g = report.get("link_graph") or {}
    out: dict[str, float | int | None] = {
        "P0": s.get("findings", {}).get("P0"), "P1": s.get("findings", {}).get("P1"),
        "P2": s.get("findings", {}).get("P2"), "pages récupérées": s.get("pages_fetched"),
        "URLs du sitemap": s.get("sitemap_urls"), "liens internes": g.get("edges"),
        "pages orphelines": len(g.get("orphans", [])) if g else None,
        "liens cassés": len(g.get("broken", [])) if g else None,
    }
    for p in report.get("pagespeed") or []:
        if p.get("url") == report.get("home") or len(report.get("pagespeed")) == 1:
            out["score PSI accueil (labo)"] = p.get("performance_score")
    crux = report.get("crux") or {}
    for m in crux.get("metrics", []):
        if m["label"] in ("LCP", "INP", "CLS"):
            out[f"CrUX {m['label']} p75"] = m["p75"]
    gsc = report.get("search_console") or {}
    if gsc:
        out["GSC clics"] = gsc.get("clicks")
        out["GSC impressions"] = gsc.get("impressions")
    return out


def diff(old: dict, new: dict) -> dict:
    a, b = _by_id(old), _by_id(new)
    changed = []
    for fid in sorted(set(a) & set(b)):
        before, after = set(a[fid]["urls"]), set(b[fid]["urls"])
        if before != after or a[fid]["count"] != b[fid]["count"]:
            changed.append({"finding": b[fid], "count_before": a[fid]["count"], "count_after": b[fid]["count"],
                            "urls_added": sorted(after - before), "urls_removed": sorted(before - after)})
    m_old, m_new = _metrics(old), _metrics(new)
    metrics = [{"name": k, "before": m_old.get(k), "after": m_new.get(k)}
               for k in list(dict.fromkeys(list(m_old) + list(m_new)))]
    return {
        "site": new.get("home") or new.get("site"),
        "old_at": old.get("finished_at"), "new_at": new.get("finished_at"),
        "new": [b[i] for i in sorted(set(b) - set(a))],
        "resolved": [a[i] for i in sorted(set(a) - set(b))],
        "changed": changed,
        "metrics": metrics,
    }


def render(d: dict) -> str:
    order = {"P0": 0, "P1": 1, "P2": 2}
    out = [f"# Évolution SEO/GEO — {d['site']}", "", f"Du {(d['old_at'] or '?')[:16]} au {(d['new_at'] or '?')[:16]} (UTC).", ""]
    out += ["## Chiffres", "", "| Indicateur | Avant | Après |", "|---|---|---|"]
    for m in d["metrics"]:
        if m["before"] is None and m["after"] is None:
            continue
        out.append(f"| {m['name']} | {m['before'] if m['before'] is not None else '—'} | "
                   f"{m['after'] if m['after'] is not None else '—'} |")
    for title, items in (("Nouveaux constats", d["new"]), ("Constats résolus", d["resolved"])):
        out += ["", f"## {title} ({len(items)})"]
        for f in sorted(items, key=lambda x: (order[x["priority"]], x["code"])):
            out.append(f"- {f['priority']} **{f['title']}** ({f['count']}) — {', '.join(f['urls'][:3]) or '—'}")
    out += ["", f"## Constats dont le périmètre a changé ({len(d['changed'])})"]
    for c in sorted(d["changed"], key=lambda x: (order[x["finding"]["priority"]], x["finding"]["code"])):
        f = c["finding"]
        out.append(f"- {f['priority']} **{f['title']}** : {c['count_before']} → {c['count_after']}")
        for u in c["urls_added"][:5]:
            out.append(f"  - + {u}")
        for u in c["urls_removed"][:5]:
            out.append(f"  - − {u}")
    return "\n".join(out) + "\n"


def latest_two(folder: Path) -> tuple[Path, Path]:
    files = sorted(folder.glob("audit_*.json"))
    if len(files) < 2:
        raise SystemExit(f"Moins de deux rapports audit_*.json dans {folder}")
    return files[-2], files[-1]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("reports", nargs="*", type=Path, help="OLD.json NEW.json")
    p.add_argument("--dir", type=Path, default=None, help="Dossier d'un site : compare les deux derniers rapports")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    if args.dir:
        old_path, new_path = latest_two(args.dir)
    elif len(args.reports) == 2:
        old_path, new_path = args.reports
    else:
        p.error("donner OLD.json NEW.json, ou --dir")
    d = diff(json.loads(old_path.read_text(encoding="utf-8")), json.loads(new_path.read_text(encoding="utf-8")))
    text = render(d)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"Ecrit : {args.out}")
    else:
        print(text)
    return 1 if any(f["priority"] == "P0" for f in d["new"]) else 0


if __name__ == "__main__":
    sys.exit(main())
