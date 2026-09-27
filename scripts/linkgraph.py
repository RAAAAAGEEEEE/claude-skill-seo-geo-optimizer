#!/usr/bin/env python3
"""Internal-linking graph of a crawled sample: click depth, inbound links
(contextual vs navigation), orphan pages, broken links, links to redirects,
anchor quality, and a cocoon / silo view by URL directory.

What is sourced and what is not (detail: references/french-practitioners.md):
- ESTABLISHED (Google, "Link best practices", updated 2025-12-10): links must
  be <a href>; every page you care about needs a link from another page of
  the site; anchors descriptive, not "click here" / "read more"; no ideal
  number of links.
- CLAIMED (practitioners, no published data): contextual links in the body
  weigh more than menu links; depth <= 3 clicks; pages of one topic should
  link to their parent ("mother") page and to each other, and mostly stay in
  their silo; anchors varied rather than one exact phrase. Thresholds here are
  the skill's own defaults, exposed as parameters -- never presented as rules.

Input is plain dicts so the module can be tested offline:
    pages   = {final_url: {"status": int, "indexable": bool, "anchors": [...]}}
    resolve = {requested_url: final_url}   (redirects followed while crawling)
Anchors come from htmlsignals.PageSignals.anchors.

Stdlib only.
"""

from __future__ import annotations

import re
import urllib.parse
from collections import Counter, defaultdict, deque

GENERIC_ANCHORS = {
    "cliquez ici", "cliquer ici", "ici", "en savoir plus", "lire la suite", "voir plus", "plus", "suite",
    "lire plus", "découvrir", "decouvrir", "voir", "lien", "cette page", "click here", "here", "read more",
    "more", "learn more", "this page", "link",
}
_LOCALE = re.compile(r"^[a-z]{2}(-[a-z]{2})?$", re.I)


def normalize(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", p.query, ""))


def same_site(url: str, host: str) -> bool:
    p = urllib.parse.urlsplit(url)
    return p.scheme in ("http", "https") and p.netloc.lower() == host.lower()


def cluster_of(url: str) -> tuple[str, str] | None:
    """(cluster key, mother page path) from the URL directory, skipping a
    leading locale segment: /fr/robots/g1 -> ("/fr/robots", "/fr/robots").
    None for the home page and first-level pages without a directory."""
    parts = [p for p in urllib.parse.urlsplit(url).path.split("/") if p]
    prefix = []
    if parts and _LOCALE.match(parts[0]):
        prefix, parts = parts[:1], parts[1:]
    if not parts:
        return None
    key = "/" + "/".join(prefix + parts[:1])
    return key, key


def build_edges(pages: dict[str, dict], resolve: dict[str, str], host: str) -> list[dict]:
    """Internal edges between distinct pages: {source, target (final), requested, text, zone, rel}."""
    edges = []
    for source, page in pages.items():
        for a in page.get("anchors", []):
            href = a.get("href")
            if not href or not same_site(href, host):
                continue
            requested = normalize(href)
            target = normalize(resolve.get(requested, requested))
            if target == normalize(source):
                continue
            edges.append({"source": normalize(source), "target": target, "requested": requested,
                          "text": a.get("text", ""), "zone": a.get("zone", "unknown"), "rel": a.get("rel", "")})
    return edges


def click_depth(edges: list[dict], home: str) -> dict[str, int]:
    graph: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        graph[e["source"]].add(e["target"])
    home = normalize(home)
    depth = {home: 0}
    queue = deque([home])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, ()):
            if nxt not in depth:
                depth[nxt] = depth[node] + 1
                queue.append(nxt)
    return depth


def analyze(pages: dict[str, dict], resolve: dict[str, str], home: str, host: str, sitemap_urls: list[str],
            *, complete: bool, max_depth: int = 3, repeat_share: float = 0.8, repeat_min: int = 5) -> dict:
    """Metrics and raw findings of the internal-linking graph.

    `complete` = every sitemap URL was fetched: orphan detection is only
    conclusive then (a link from an unfetched page cannot be seen).
    """
    pages = {normalize(u): p for u, p in pages.items()}
    home_n = normalize(resolve.get(normalize(home), home))
    edges = build_edges(pages, {normalize(k): v for k, v in resolve.items()}, host)
    depth = click_depth(edges, home_n)

    zones = Counter(e["zone"] for e in edges)
    zone_known = sum(zones.values()) > 0 and zones.get("unknown", 0) / sum(zones.values()) < 0.5

    inbound: dict[str, set[str]] = defaultdict(set)
    inbound_main: dict[str, set[str]] = defaultdict(set)
    outbound_main: dict[str, set[str]] = defaultdict(set)
    anchors_main: dict[str, Counter] = defaultdict(Counter)
    for e in edges:
        inbound[e["target"]].add(e["source"])
        if e["zone"] == "main":
            inbound_main[e["target"]].add(e["source"])
            outbound_main[e["source"]].add(e["target"])
            anchors_main[e["target"]][e["text"].strip().lower()] += 1

    fetched_ok = {u for u, p in pages.items() if p.get("status") == 200 and p.get("indexable", True)}
    sitemap_final = {normalize(resolve.get(normalize(u), u)) for u in sitemap_urls}

    broken, to_redirect, generic, empty, nofollow = [], [], [], [], []
    for e in edges:
        status = pages.get(e["target"], {}).get("status")
        if status and status >= 400:
            broken.append({"source": e["source"], "target": e["target"], "status": status})
        if e["requested"] != e["target"]:
            to_redirect.append({"source": e["source"], "requested": e["requested"], "final": e["target"]})
        text = e["text"].strip().lower()
        if not text:
            empty.append({"source": e["source"], "target": e["target"]})
        elif text in GENERIC_ANCHORS:
            generic.append({"source": e["source"], "target": e["target"], "text": e["text"]})
        if "nofollow" in e["rel"].split():
            nofollow.append({"source": e["source"], "target": e["target"]})

    def _not_crawlable(a: dict) -> bool:
        # <a> without href, or javascript:. A "#fragment" (skip link, table of contents) is fine.
        raw = a.get("raw_href")
        return a.get("href") is None and (raw is None or raw.strip().lower().startswith("javascript:"))

    non_crawlable = {u: n for u, p in pages.items() if (n := sum(1 for a in p.get("anchors", []) if _not_crawlable(a)))}

    orphans = sorted(u for u in sitemap_final if u != home_n and not inbound.get(u))
    unreachable = sorted(u for u in fetched_ok if u not in depth)
    deep = sorted((u, depth[u]) for u in fetched_ok if depth.get(u, 0) > max_depth)

    no_ctx_in = sorted(u for u in fetched_ok if u != home_n and inbound.get(u) and not inbound_main.get(u)) \
        if zone_known else []
    no_ctx_out = sorted(u for u in fetched_ok if not outbound_main.get(u)) if zone_known else []

    repeated = []
    for target, counter in anchors_main.items():
        total = sum(counter.values())
        text, n = counter.most_common(1)[0]
        if total >= repeat_min and text and n / total >= repeat_share:
            repeated.append({"target": target, "anchor": text, "share": round(n / total, 2), "links": total})

    # Cocoon / silo view by directory.
    clusters: dict[str, dict] = {}
    for u in fetched_ok:
        c = cluster_of(u)
        if not c:
            continue
        key, mother_path = c
        info = clusters.setdefault(key, {"mother": None, "children": []})
        if urllib.parse.urlsplit(u).path.rstrip("/") == mother_path:
            info["mother"] = u
        else:
            info["children"].append(u)
    cluster_rows, no_uplink = [], []
    for key, info in sorted(clusters.items()):
        mother, children = info["mother"], sorted(info["children"])
        if not children:
            continue  # a lone page is not a silo
        ctx_out = [e for e in edges if e["zone"] == "main" and e["source"] in set(children) | {mother}]
        leaving = [e for e in ctx_out if (cluster_of(e["target"]) or ("",))[0] != key]
        up_any = [ch for ch in children if mother and any(e["source"] == ch and e["target"] == mother for e in edges)]
        up_ctx = [ch for ch in children if mother and mother in outbound_main.get(ch, set())]
        down = [ch for ch in children if mother and ch in {e["target"] for e in edges if e["source"] == mother}]
        siblings = sum(1 for e in ctx_out if e["source"] in children and e["target"] in children)
        cluster_rows.append({
            "cluster": key, "mother": mother, "children": len(children),
            "children_linking_mother": len(up_any), "children_linking_mother_in_text": len(up_ctx),
            "mother_linking_children": len(down), "sibling_links_in_text": siblings,
            "contextual_links": len(ctx_out),
            "contextual_leaving_share": round(len(leaving) / len(ctx_out), 2) if ctx_out else None,
        })
        if mother:
            no_uplink += [ch for ch in children if ch not in up_any]

    per_page = {
        u: {"depth": depth.get(u), "inlinks": len(inbound.get(u, ())), "inlinks_in_text": len(inbound_main.get(u, ())),
            "outlinks_in_text": len(outbound_main.get(u, ()))}
        for u in sorted(set(pages) | sitemap_final)
    }
    return {
        "complete": complete,
        "home": home_n,
        "edges": len(edges),
        "zones": dict(zones),
        "zone_known": zone_known,
        "max_depth": max_depth,
        "per_page": per_page,
        "orphans": orphans,
        "unreachable_from_home": unreachable,
        "deep": [{"url": u, "depth": d} for u, d in deep],
        "no_contextual_inlink": no_ctx_in,
        "no_contextual_outlink": no_ctx_out,
        "broken": broken,
        "to_redirect": to_redirect,
        "generic_anchors": generic,
        "empty_anchors": empty,
        "internal_nofollow": nofollow,
        "non_crawlable": non_crawlable,
        "repeated_anchors": repeated,
        "clusters": cluster_rows,
        "cocoon_no_uplink": sorted(no_uplink),
    }
