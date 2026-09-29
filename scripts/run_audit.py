#!/usr/bin/env python3
"""Audit SEO/GEO complet et sans intervention d'un site : une commande, un
rapport date (Markdown + JSON) avec un plan de correction priorise, et le
diff avec le rapport precedent.

Etapes (chacune notee ran / skipped / error dans le rapport) :
  1. accueil (HTTP, redirections) et robots.txt (RFC 9309) ;
  2. acces reel des crawlers de recherche et d'IA (check_ai_access.py) ;
  3. sitemaps (robots.txt, index, gzip) et coherence lastmod ;
  4. crawl d'un echantillon : accueil + URLs du sitemap + liens internes,
     dans la limite de --max-pages, en respectant robots.txt ;
  5. par page : HTTP, noindex/nosnippet, title, description, canonical, H1,
     lang, JSON-LD valide (validate_schema.py) ;
  6. URLs inexistantes sondees par rubrique (404 attendu, jamais 5xx ni 200) ;
  7. coherence sitemap / canonical / hreflang / noindex / langue ;
  8. maillage interne : profondeur, orphelines, liens casses, ancres, cocon
     par repertoire (linkgraph.py) ;
  9. optionnels, uniquement si l'acces est fourni par l'environnement :
     PageSpeed Insights (PAGESPEED_API_KEY), CrUX (CRUX_API_KEY, sinon
     PAGESPEED_API_KEY), Search Console (GSC_SERVICE_ACCOUNT_FILE + --gsc-site
     ou GSC_SITE), IndexNow (cle dans la variable nommee par
     --indexnow-key-env, INDEXNOW_KEY par defaut).

Correctifs surs, sans toucher au site ni a la production :
  - <stamp>_sitemap.proposed.xml : URLs verifiees 200, indexables, auto-
    canoniques, lastmod repris du sitemap existant (jamais invente) ;
  - <stamp>_indexnow_urls.txt : URLs nouvelles ou modifiees depuis le
    rapport precedent ;
  - soumission IndexNow de ces URLs SEULEMENT avec --indexnow-submit (action
    externe : les URLs sont partagees avec tous les moteurs participants).
Les corrections de code du site restent dans la procedure PLAN -> FIX ->
VERIFY de SKILL.md.

Secrets : lus dans l'environnement ou un chemin de fichier, jamais en
argument, jamais ecrits dans le rapport (redaction finale du JSON et du
Markdown).

Usage :
    python run_audit.py --site https://example.com
    python run_audit.py --site https://example.com --max-pages 100 --out-dir ~/seo-reports
    PAGESPEED_API_KEY=... GSC_SERVICE_ACCOUNT_FILE=~/secrets/gsc.json \\
        python run_audit.py --site https://example.com --gsc-site sc-domain:example.com

Sortie : <out-dir>/<hote>/audit_<AAAAMMJJTHHMMSSZ>.md|.json (+ diff_*.md).
Code de sortie : 0 aucun P0, 1 au moins un P0, 2 accueil injoignable (non
concluant). Stdlib uniquement, sauf Search Console (pip install google-auth
requests).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import random
import sys
import time
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_ai_access  # noqa: E402
import envkeys  # noqa: E402
import linkgraph  # noqa: E402
import robotstxt  # noqa: E402
import sitemaps as sitemaps_mod  # noqa: E402
from audit_rules import RULES, finding_id, hreflang_checks, page_checks  # noqa: E402
from htmlsignals import USER_AGENT, PageSignals, fetch_signals  # noqa: E402
from validate_schema import validate_blocks  # noqa: E402

VERSION = "2.3.0"
AUDIT_TOKEN = "seo-geo-optimizer-audit"
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".ico", ".zip", ".gz", ".xml",
            ".json", ".txt", ".csv", ".mp4", ".webm", ".mp3", ".css", ".js", ".woff", ".woff2")
CITATION_ROLES = ("search", "user", "engine")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
MAX_URLS_KEPT = 50  # per finding in the JSON; the count stays exact


# --------------------------------------------------------------------------- helpers

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def is_page_candidate(url: str, host: str, include_query: bool) -> bool:
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https") or p.netloc.lower() != host.lower():
        return False
    if p.query and not include_query:
        return False
    return not p.path.lower().endswith(SKIP_EXT)


def stratified_sample(urls: list[str], budget: int) -> list[str]:
    """Round-robin across URL directories so one big section cannot eat the budget."""
    if len(urls) <= budget:
        return list(urls)
    groups: dict[str, list[str]] = defaultdict(list)
    for u in urls:
        parts = [x for x in urllib.parse.urlsplit(u).path.split("/") if x]
        groups["/".join(parts[:2])].append(u)
    out: list[str] = []
    keys = sorted(groups)
    while len(out) < budget:
        progressed = False
        for k in keys:
            if groups[k] and len(out) < budget:
                out.append(groups[k].pop(0))
                progressed = True
        if not progressed:
            break
    return out


class Findings:
    """Aggregates findings by rule code (one entry per code, URLs listed)."""

    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def add(self, code: str, url: str | None = None, detail: str | None = None, nature: str = "inféré") -> None:
        rule = RULES[code]
        item = self.items.setdefault(code, {
            "id": finding_id(code), "code": code, "priority": rule.priority, "category": rule.category,
            "title": rule.title, "label": rule.label, "source": rule.source, "fix": rule.fix,
            "nature": nature, "urls": [], "details": [], "count": 0,
        })
        if nature == "mesuré":
            item["nature"] = "mesuré"
        if detail and detail not in item["details"]:
            item["details"].append(detail)
        if url and url in item["urls"]:
            return  # same URL again: one occurrence, extra detail kept
        item["count"] += 1
        if url:
            item["urls"].append(url)

    def sorted(self) -> list[dict]:
        out = []
        for item in self.items.values():
            item = dict(item)
            item["urls"] = sorted(item["urls"])
            item["urls_truncated"] = max(0, len(item["urls"]) - MAX_URLS_KEPT)
            item["urls"] = item["urls"][:MAX_URLS_KEPT]
            item["details"] = item["details"][:MAX_URLS_KEPT]
            out.append(item)
        return sorted(out, key=lambda f: (PRIORITY_ORDER[f["priority"]], f["category"], -f["count"], f["code"]))


# --------------------------------------------------------------------------- audit

class Audit:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.site = args.site.rstrip("/") + "/" if urllib.parse.urlsplit(args.site).path in ("", "/") else args.site
        self.findings = Findings()
        self.modules: dict[str, dict] = {}
        self.pages: dict[str, PageSignals] = {}  # key: normalized final URL (or requested URL on error)
        self.schema: dict[str, list[dict]] = {}
        self.resolve: dict[str, str] = {}  # normalized requested -> normalized final
        self.requests = 0
        self.secrets: list[str | None] = []
        self.report: dict = {}

    # -- plumbing
    def module(self, name: str, status: str, reason: str = "", **extra) -> None:
        self.modules[name] = {"status": status, "reason": reason, **extra}

    def log(self, msg: str) -> None:
        print(envkeys.redact(msg, self.secrets), flush=True)

    def fetch(self, url: str) -> PageSignals:
        if self.requests:
            time.sleep(self.args.delay)
        self.requests += 1
        return fetch_signals(url, timeout=self.args.timeout)

    def crawl_page(self, url: str) -> PageSignals:
        requested = linkgraph.normalize(url)
        if requested in self.resolve:
            return self.pages[self.resolve[requested]]
        s = self.fetch(url)
        final = linkgraph.normalize(s.final_url or url)
        self.resolve[requested] = final
        if final not in self.pages:
            self.pages[final] = s
            self.schema[final] = validate_blocks(s.jsonld_blocks, label=final) if s.jsonld_blocks else []
        return self.pages[final]

    # -- steps
    def run(self) -> int:
        a = self.args
        started = now_utc()
        self.pagespeed_key = envkeys.secret("PAGESPEED_API_KEY")
        self.crux_key = envkeys.secret("CRUX_API_KEY") or self.pagespeed_key
        self.indexnow_key = envkeys.secret(a.indexnow_key_env)
        self.gsc_file = envkeys.secret_file("GSC_SERVICE_ACCOUNT_FILE")
        self.gsc_site = a.gsc_site or envkeys.secret("GSC_SITE")
        self.secrets = [self.pagespeed_key, self.crux_key, self.indexnow_key]

        self.log(f"[1/9] Accueil {self.site}")
        home = self.crawl_page(self.site)
        self.home = linkgraph.normalize(home.final_url or self.site)
        self.host = urllib.parse.urlsplit(self.home).netloc
        self.origin = f"{urllib.parse.urlsplit(self.home).scheme}://{self.host}"
        home_ok = home.http_status == 200
        if not home_ok:
            self.findings.add("home-unreachable", self.site, f"HTTP {home.http_status or home.error}", "mesuré")

        self.log("[1/9] robots.txt")
        self.robots_status, self.robots, robots_err = check_ai_access.fetch_robots(self.origin)
        self.requests += 1
        fallback = robotstxt.verdict_for_status(self.robots_status)
        if fallback == "disallow-all":
            self.findings.add("robots-unreadable", f"{self.origin}/robots.txt",
                              f"HTTP {self.robots_status or robots_err}", "mesuré")

        if home_ok:
            self.step_ai_access()
        else:
            self.module("ai_access", "skipped", "accueil hors 200 : verdicts non attribuables")
        self.step_sitemaps()
        if home_ok:
            self.step_crawl()
            self.step_probes()
            self.step_coherence()
            self.step_links()
        else:
            for m in ("crawl", "probes_404", "coherence", "link_graph"):
                self.module(m, "skipped", "accueil hors 200")
        self.step_pagespeed(home_ok)
        self.step_crux()
        self.step_gsc()
        previous = self.previous_report()
        self.step_indexnow(previous)
        self.build_report(started, previous)
        return self.write_outputs(previous)

    def robots_allows(self, token: str, url: str) -> bool:
        fallback = robotstxt.verdict_for_status(self.robots_status)
        if fallback == "allow-all" or (fallback is None and self.robots is None):
            return True
        if fallback == "disallow-all":
            return False
        p = urllib.parse.urlsplit(url)
        return robotstxt.is_allowed(self.robots, token, (p.path or "/") + (f"?{p.query}" if p.query else ""))

    def step_ai_access(self) -> None:
        if self.args.no_ai_access:
            self.module("ai_access", "skipped", "--no-ai-access")
            self.ai_access = None
            return
        self.log("[2/9] Acces des crawlers de recherche et d'IA")
        self.ai_access = check_ai_access.check_site(self.home)
        self.requests += len(self.ai_access["bots"]) + 2
        blocked = [b for b in self.ai_access["bots"]
                   if b["role"] in CITATION_ROLES and b["verdict"] in ("blocked-upstream", "blocked-by-robots")]
        for b in blocked:
            self.findings.add("crawler-blocked", None, f"{b['token']} ({b['vendor']}, {b['role']}) : {b['verdict']}",
                              "mesuré")
        self.module("ai_access", "ran", f"{len(self.ai_access['bots'])} crawlers, {len(blocked)} bloqué(s)")

    def step_sitemaps(self) -> None:
        self.log("[3/9] Sitemaps")
        declared = self.robots.records("sitemap") if self.robots else []
        self.sitemaps = sitemaps_mod.discover(getattr(self, "origin", self.site.rstrip("/")), declared,
                                              timeout=self.args.timeout)
        self.requests += len(self.sitemaps.read)
        if not self.sitemaps.entries:
            self.findings.add("sitemap-missing", None, "; ".join(f"{r['url']} -> {r['error'] or r['kind']}"
                                                                for r in self.sitemaps.read), "mesuré")
        host = getattr(self, "host", urllib.parse.urlsplit(self.site).netloc)
        for u in sitemaps_mod.foreign_entries(self.sitemaps, host):
            self.findings.add("sitemap-foreign-host", u, nature="mesuré")
        lm = sitemaps_mod.lastmod_findings(self.sitemaps)
        if lm["uniform"]:
            self.findings.add("sitemap-lastmod-uniform", None,
                              f"{lm['with_lastmod']} URL(s) datées du {lm['uniform_value']}", "mesuré")
        for u in lm["future"]:
            self.findings.add("sitemap-lastmod-future", u, nature="mesuré")
        for u in self.sitemaps.urls:
            if urllib.parse.urlsplit(u).netloc.lower() == host.lower() and not self.robots_allows("Googlebot", u):
                self.findings.add("googlebot-disallowed", u, nature="mesuré")
        self.lastmod_stats = lm
        self.module("sitemaps", "ran", f"{len(self.sitemaps.read)} fichier(s), {len(self.sitemaps.urls)} URL(s)")

    def step_crawl(self) -> None:
        a = self.args
        self.log(f"[4/9] Crawl (max {a.max_pages} pages, {a.delay}s entre requetes)")
        sitemap_urls = [u for u in self.sitemaps.urls if is_page_candidate(u, self.host, True)]
        self.skipped_by_robots: list[str] = []
        budget = a.max_pages - 1
        queue = stratified_sample(sitemap_urls, budget)
        self.sitemap_sampled = len(queue) < len(sitemap_urls)
        seen = {linkgraph.normalize(u) for u in queue} | {self.home}
        i = 0
        frontier: list[str] = []
        # Sitemap URLs first (coverage of what the site declares), then links found on the way.
        pending = queue
        for anchor in self.pages[self.home].anchors:
            href = anchor.get("href")
            if href and is_page_candidate(href, self.host, a.include_query) and linkgraph.normalize(href) not in seen:
                seen.add(linkgraph.normalize(href))
                frontier.append(href)
        while len(self.pages) < a.max_pages and (i < len(pending) or frontier):
            if i < len(pending):
                url = pending[i]
                i += 1
            else:
                url = frontier.pop(0)
            if not self.robots_allows(AUDIT_TOKEN, url):
                self.skipped_by_robots.append(url)
                continue
            page = self.crawl_page(url)
            for anchor in page.anchors:
                href = anchor.get("href")
                if not href or not is_page_candidate(href, self.host, a.include_query):
                    continue
                n = linkgraph.normalize(href)
                if n not in seen:
                    seen.add(n)
                    frontier.append(href)
        fetched_sitemap = sum(1 for u in sitemap_urls if linkgraph.normalize(u) in self.resolve)
        self.crawl_complete = fetched_sitemap == len(sitemap_urls)
        self.discovered_not_fetched = len(frontier)
        sitemap_final = {self.resolve.get(linkgraph.normalize(u), linkgraph.normalize(u)) for u in sitemap_urls}
        for key, s in self.pages.items():
            for c in page_checks(s, self.schema.get(key, [])):
                if c["kind"] != "issue":
                    continue
                code = c["code"]
                if code == "noindex" and key != self.home:
                    if key in sitemap_final:
                        continue  # reported as sitemap-noindex (coherence step)
                    code = "noindex-linked"  # often deliberate (empty listing, utility page)
                self.findings.add(code, key, c["message"])
        self.module("crawl", "ran", f"{len(self.pages)} page(s) récupérée(s), {fetched_sitemap}/{len(sitemap_urls)} "
                    f"URL(s) du sitemap, {len(frontier)} lien(s) découvert(s) non visité(s)",
                    complete=self.crawl_complete)

    def step_probes(self) -> None:
        self.log("[6/9] URLs inexistantes (404 attendu)")
        # Probe below the root and below every HTML page of one or two path segments:
        # dynamic routes (/fr/robots/<slug>) live under listing pages, and an unknown
        # slug there must give 404, not 500 (a case found on a real site on 2026-09-27).
        inbound: dict[str, int] = defaultdict(int)
        for s in self.pages.values():
            for a in s.anchors:
                if a.get("href"):
                    inbound[linkgraph.normalize(a["href"])] += 1
        prefixes = set()
        for key, s in self.pages.items():
            if not (s.http_status == 200 and s.is_html):
                continue
            parts = [x for x in urllib.parse.urlsplit(key).path.split("/") if x]
            for depth in (1, 2):
                if len(parts) >= depth:
                    prefixes.add("/" + "/".join(parts[:depth]))
        ranked = sorted(prefixes, key=lambda p: (-inbound.get(linkgraph.normalize(self.origin + p), 0), p))
        chosen = [""] + ranked[: self.args.probes - 1]
        self.probes = []
        for prefix in chosen:
            url = f"{self.origin}{prefix}/seo-audit-404-{random.getrandbits(32):08x}"
            s = self.fetch(url)
            self.probes.append({"url": url, "status": s.http_status, "error": s.error if s.http_status is None else None})
            if s.http_status and s.http_status >= 500:
                self.findings.add("unknown-url-5xx", url, f"HTTP {s.http_status}", "mesuré")
            elif s.http_status == 200:
                self.findings.add("unknown-url-200", url, "HTTP 200", "mesuré")
        self.module("probes_404", "ran", f"{len(self.probes)} URL(s) sondée(s)")

    def _page(self, url: str) -> PageSignals | None:
        n = linkgraph.normalize(url)
        return self.pages.get(self.resolve.get(n, n))

    def _indexable(self, s: PageSignals) -> bool:
        return s.http_status == 200 and s.is_html and not s.noindex

    def step_coherence(self) -> None:
        self.log("[7/9] Coherence sitemap / canonical / hreflang / langue")
        # Fetch a few canonical and hreflang targets that the crawl did not reach.
        extra = 0
        for s in list(self.pages.values()):
            targets = ([s.canonical] if s.canonical else []) + [h for _l, h in s.hreflang_links]
            for t in targets:
                if extra >= self.args.extra_targets or not is_page_candidate(t, self.host, True):
                    continue
                if linkgraph.normalize(t) not in self.resolve:
                    self.crawl_page(t)
                    extra += 1

        sitemap_set = {linkgraph.normalize(u) for u in self.sitemaps.urls}
        for u in self.sitemaps.urls:
            n = linkgraph.normalize(u)
            if n not in self.resolve:
                continue
            s = self.pages[self.resolve[n]]
            if s.http_status != 200 or self.resolve[n] != n:
                self.findings.add("sitemap-non-200", u, f"HTTP {s.http_status}"
                                  + (f" -> {self.resolve[n]}" if self.resolve[n] != n else ""), "mesuré")
            elif s.noindex:
                self.findings.add("sitemap-noindex", u, nature="mesuré")
            elif s.canonical and linkgraph.normalize(s.canonical) != n:
                self.findings.add("sitemap-canonical-elsewhere", u, f"canonical -> {s.canonical}")

        for key, s in self.pages.items():
            if not self._indexable(s):
                continue
            if s.canonical and linkgraph.normalize(s.canonical) != key:
                target = self._page(s.canonical)
                if target is not None:
                    tkey = linkgraph.normalize(target.final_url or target.url)
                    if not self._indexable(target) or tkey != linkgraph.normalize(s.canonical):
                        self.findings.add("canonical-to-bad-target", key, f"canonical -> {s.canonical} "
                                          f"(HTTP {target.http_status}{', noindex' if target.noindex else ''})")
            if sitemap_set and key not in sitemap_set and (not s.canonical or linkgraph.normalize(s.canonical) == key):
                if not any(self.resolve.get(u) == key for u in sitemap_set):
                    self.findings.add("not-in-sitemap", key)
            words = s.main_word_count if s.main_word_count is not None else s.word_count
            if words < self.args.thin_words:
                self.findings.add("thin-page", key, f"{words} mot(s)")

        # hreflang: reciprocity, targets, declared language vs page language.
        signals = [s for s in self.pages.values() if s.http_status == 200]
        for c in hreflang_checks(signals):
            self.findings.add(c["code"], c["url"], c["message"])
        for s in signals:
            for lang, href in s.hreflang_links:
                if lang.lower() == "x-default":
                    continue
                target = self._page(href)
                if target is None:
                    continue
                if not self._indexable(target):
                    self.findings.add("hreflang-bad-target", href, f"HTTP {target.http_status}"
                                      f"{', noindex' if target.noindex else ''} (déclaré par {s.final_url})")
                elif target.html_lang and target.html_lang.split("-")[0].lower() != lang.split("-")[0].lower():
                    self.findings.add("hreflang-lang-mismatch", href,
                                      f"hreflang={lang} mais <html lang={target.html_lang}>")

        # Duplicates between indexable pages.
        for attr, code in (("title", "title-duplicate"), ("description", "description-duplicate")):
            groups: dict[str, list[str]] = defaultdict(list)
            for key, s in self.pages.items():
                value = getattr(s, attr)
                if value and self._indexable(s) and not (s.canonical and linkgraph.normalize(s.canonical) != key):
                    groups[value.strip()].append(key)
            for value, urls in groups.items():
                if len(urls) > 1:
                    for u in urls:
                        self.findings.add(code, u, f"« {value[:80]} » ({len(urls)} pages)")
        self.module("coherence", "ran", f"{extra} cible(s) canonical/hreflang supplémentaire(s) récupérée(s)")

    def step_links(self) -> None:
        self.log("[8/9] Maillage interne et cocon")
        pages = {k: {"status": s.http_status, "indexable": self._indexable(s), "anchors": s.anchors}
                 for k, s in self.pages.items()}
        sitemap_same_host = [u for u in self.sitemaps.urls if is_page_candidate(u, self.host, True)]
        g = linkgraph.analyze(pages, self.resolve, self.home, self.host, sitemap_same_host,
                              complete=self.crawl_complete, max_depth=self.args.max_depth)
        self.graph = g
        suffix = "" if g["complete"] else " (échantillon : liens depuis les pages non visitées invisibles)"
        for u in g["orphans"]:
            if u in self.pages and self._indexable(self.pages[u]):
                self.findings.add("orphan-page", u, "aucun lien entrant depuis les pages visitées" + suffix)
        for b in g["broken"]:
            self.findings.add("broken-internal-link", b["target"], f"HTTP {b['status']} depuis {b['source']}", "mesuré")
        for r in g["to_redirect"]:
            self.findings.add("link-to-redirect", r["requested"], f"{r['requested']} -> {r['final']} (depuis {r['source']})")
        for u, n in g["non_crawlable"].items():
            self.findings.add("non-crawlable-link", u, f"{n} lien(s)")
        for e in g["empty_anchors"]:
            self.findings.add("empty-anchor", e["source"], f"vers {e['target']}")
        for e in g["generic_anchors"]:
            self.findings.add("generic-anchor", e["source"], f"« {e['text']} » vers {e['target']}")
        for e in g["internal_nofollow"]:
            self.findings.add("internal-nofollow", e["source"], f"vers {e['target']}")
        for d in g["deep"]:
            self.findings.add("deep-page", d["url"], f"profondeur {d['depth']}")
        for u in g["unreachable_from_home"]:
            if u not in g["orphans"]:  # an orphan is already reported as such
                self.findings.add("deep-page", u, "non atteignable depuis l'accueil par les liens des pages visitées")
        for u in g["no_contextual_inlink"]:
            self.findings.add("no-contextual-inlink", u)
        for u in g["no_contextual_outlink"]:
            if u != g["home"]:
                self.findings.add("no-contextual-outlink", u)
        for r in g["repeated_anchors"]:
            self.findings.add("anchor-repeated", r["target"], f"« {r['anchor']} » = {int(r['share'] * 100)} % "
                              f"de {r['links']} liens")
        for u in g["cocoon_no_uplink"]:
            self.findings.add("cocoon-no-uplink", u)
        note = "" if g["zone_known"] else " ; pas de <main>/<nav> : contrôles contextuels désactivés"
        self.module("link_graph", "ran", f"{g['edges']} lien(s) interne(s), {len(g['clusters'])} rubrique(s){note}")

    def step_pagespeed(self, home_ok: bool) -> None:
        self.psi = []
        if not self.pagespeed_key:
            self.module("pagespeed", "skipped", "PAGESPEED_API_KEY absente")
            return
        if not home_ok:
            self.module("pagespeed", "skipped", "accueil hors 200")
            return
        import pagespeed

        self.log("[9/9] PageSpeed Insights")
        targets = [self.home] + [u for u in self.sitemaps.urls if linkgraph.normalize(u) != self.home]
        errors = []
        for url in targets[: self.args.psi_pages]:
            try:
                r = pagespeed.extract(pagespeed.run(url, self.pagespeed_key, self.args.psi_strategy))
            except RuntimeError as e:
                errors.append(str(e))
                continue
            self.psi.append(r)
            if r["performance_score"] is not None and r["performance_score"] < 50:
                self.findings.add("lab-performance-low", url, f"score {r['performance_score']}", "mesuré")
            field = r["field_page"] or r["field_origin"]
            for m in (field or {}).get("metrics", []):
                if m["label"] not in ("LCP", "INP", "CLS"):
                    continue
                code = {"MAUVAIS": "cwv-poor", "A AMELIORER": "cwv-needs-improvement"}.get(m["rating"])
                if code:
                    scope = "page" if r["field_page"] else "origine"
                    self.findings.add(code, url, f"{m['label']} p75 = {m['p75']}{m['unit']} ({scope}, terrain)", "mesuré")
        status = "ran" if self.psi else "error"
        self.module("pagespeed", status, f"{len(self.psi)} page(s) mesurée(s)" + (f" ; {errors[0]}" if errors else ""))

    def step_crux(self) -> None:
        self.crux = None
        if not self.crux_key:
            self.module("crux", "skipped", "CRUX_API_KEY et PAGESPEED_API_KEY absentes")
            return
        import crux_report

        captured = io.StringIO()  # crux_report prints the raw API error body; keep it out of the logs
        try:
            with contextlib.redirect_stderr(captured):
                record = crux_report.query_crux(self.crux_key, {"origin": getattr(self, "origin", self.site)}, None)
        except Exception as e:  # noqa: BLE001 -- recorded, redacted, never fatal
            try:
                detail = json.loads(captured.getvalue().split(":", 1)[1])["error"]["message"]
            except (ValueError, KeyError, IndexError, TypeError):
                detail = ""
            self.module("crux", "error", envkeys.redact(f"{e} {detail}".strip(), self.secrets))
            return
        if record is None:
            self.crux = {"no_data": True}
            self.module("crux", "ran", "aucune donnée terrain (trafic insuffisant, pas un problème de performance)")
            return
        metrics = crux_report.extract(record)
        self.crux = {"metrics": metrics}
        for m in metrics:
            code = {"MAUVAIS": "cwv-poor", "A AMELIORER": "cwv-needs-improvement"}.get(m["rating"])
            if code and m["label"] in ("LCP", "INP", "CLS"):
                self.findings.add(code, None, f"{m['label']} p75 = {m['p75']}{m['unit']} (origine, CrUX)", "mesuré")
        self.module("crux", "ran", f"{len(metrics)} métrique(s)")

    def step_gsc(self) -> None:
        self.gsc = None
        if not (self.gsc_file and self.gsc_site):
            if os.environ.get("GSC_SERVICE_ACCOUNT_FILE") and not self.gsc_file:
                reason = "GSC_SERVICE_ACCOUNT_FILE pointe vers un fichier introuvable"
            elif not self.gsc_file:
                reason = "GSC_SERVICE_ACCOUNT_FILE absente"
            else:
                reason = "propriété absente (--gsc-site ou GSC_SITE)"
            self.module("search_console", "skipped", reason)
            return
        try:
            import gsc_report
        except ImportError as e:
            self.module("search_console", "skipped", f"dépendance manquante ({e.name}) : pip install google-auth requests")
            return
        try:
            token = gsc_report.get_access_token(self.gsc_file)
            end = now_utc().date()
            start = end - timedelta(days=self.args.gsc_days)
            rows = gsc_report.query_search_analytics(token, self.gsc_site, start.isoformat(), end.isoformat(),
                                                     dimension="page", path_filter=self.origin + "/", row_limit=5000)
        except Exception as e:  # noqa: BLE001
            self.module("search_console", "error", envkeys.redact(f"{type(e).__name__}: {e}", self.secrets)[:300])
            return
        seen = {linkgraph.normalize(r["key"]) for r in rows}
        for u in self.sitemaps.urls:
            s = self._page(u)
            if s is not None and self._indexable(s) and linkgraph.normalize(s.final_url or u) not in seen:
                self.findings.add("gsc-no-impressions", u, nature="mesuré")
        self.gsc = {"site": self.gsc_site, "start_date": start.isoformat(), "end_date": end.isoformat(),
                    "pages_with_impressions": len(rows), "clicks": sum(r["clicks"] for r in rows),
                    "impressions": sum(r["impressions"] for r in rows),
                    "top": sorted(rows, key=lambda r: -r["clicks"])[:20]}
        self.module("search_console", "ran", f"{len(rows)} page(s) avec impressions")

    def previous_report(self) -> dict | None:
        if self.args.no_diff:
            return None
        folder = self.out_folder()
        files = sorted(folder.glob("audit_*.json")) if folder.exists() else []
        if not files:
            return None
        try:
            return json.loads(files[-1].read_text(encoding="utf-8")) | {"_path": str(files[-1])}
        except (OSError, json.JSONDecodeError):
            return None

    def changed_urls(self, previous: dict | None) -> list[str]:
        """Indexable sitemap URLs that are new or whose lastmod changed since the previous run.
        Empty on the first run: without a reference, "new" would mean the whole sitemap."""
        if previous is None:
            return []
        before = {e["loc"]: e.get("lastmod") for e in (previous or {}).get("sitemaps", {}).get("entries", [])}
        out = []
        for e in self.sitemaps.entries:
            s = self._page(e.loc)
            if s is None or not self._indexable(s):
                continue
            if e.loc not in before or (e.lastmod and e.lastmod != before[e.loc]):
                out.append(e.loc)
        return sorted(set(out))

    def step_indexnow(self, previous: dict | None) -> None:
        self.indexnow = None
        if not self.indexnow_key:
            self.module("indexnow", "skipped", f"variable {self.args.indexnow_key_env} absente")
            return
        import indexnow_submit

        if not indexnow_submit.KEY_RE.match(self.indexnow_key):
            self.findings.add("indexnow-key-invalid", None, "format de clé invalide (8-128 caractères a-z A-Z 0-9 -)")
            self.module("indexnow", "error", "format de clé invalide")
            return
        ok, info = indexnow_submit.verify_key_file(self.host, self.indexnow_key, None)
        self.requests += 1
        if not ok:
            self.findings.add("indexnow-key-invalid", None, envkeys.redact(info, self.secrets), "mesuré")
        urls = self.changed_urls(previous)
        self.indexnow = {"key_file_ok": ok, "changed_urls": urls, "baseline": previous is None,
                         "submitted": False, "response": None}
        if self.args.indexnow_submit and ok and urls and previous is not None:
            status, body = indexnow_submit.submit(self.host, self.indexnow_key, info, urls[:10_000])
            self.indexnow.update(submitted=status in (200, 202), response=f"HTTP {status} {indexnow_submit.interpret_status(status)}")
            self.module("indexnow", "ran", f"{len(urls)} URL(s) soumise(s) : HTTP {status}")
        else:
            why = ("premier rapport : il sert de référence pour les suivants" if previous is None
                   else "--indexnow-submit absent" if not self.args.indexnow_submit
                   else "clé non vérifiée" if not ok else "aucune URL nouvelle ou modifiée")
            self.module("indexnow", "ran", f"clé {'OK' if ok else 'KO'}, {len(urls)} URL(s) candidate(s), non soumis : {why}")

    # -- output
    def out_folder(self) -> Path:
        host = getattr(self, "host", urllib.parse.urlsplit(self.site).netloc) or "site"
        return Path(self.args.out_dir).expanduser() / host.replace(":", "_")

    def build_report(self, started: datetime, previous: dict | None) -> None:
        findings = self.findings.sorted()
        g = getattr(self, "graph", None)
        pages = []
        in_sitemap = {self.resolve.get(linkgraph.normalize(u), linkgraph.normalize(u)) for u in self.sitemaps.urls}
        for key, s in sorted(self.pages.items()):
            per = (g or {}).get("per_page", {}).get(key, {})
            pages.append({
                "url": key, "requested": s.url, "http_status": s.http_status, "redirects": s.redirects,
                "title": s.title, "description": s.description, "canonical": s.canonical, "html_lang": s.html_lang,
                "noindex": s.noindex, "nosnippet": s.nosnippet, "h1_count": s.h1_count,
                "hreflang_links": s.hreflang_links, "words": s.word_count, "main_words": s.main_word_count,
                "in_sitemap": key in in_sitemap,
                "schema_types": sorted({t for r in self.schema.get(key, []) for t in r["types"]}),
                "issues": [c["code"] for c in page_checks(s, self.schema.get(key, [])) if c["kind"] == "issue"],
                "error": s.error, **per,
            })
        counts = {p: sum(1 for f in findings if f["priority"] == p) for p in ("P0", "P1", "P2")}
        self.report = {
            "schema_version": 1,
            "generator": f"seo-geo-optimizer/scripts/run_audit.py {VERSION}",
            "site": self.site,
            "home": getattr(self, "home", None),
            "started_at": started.isoformat(),
            "finished_at": now_utc().isoformat(),
            "options": {"max_pages": self.args.max_pages, "delay": self.args.delay, "max_depth": self.args.max_depth,
                        "thin_words": self.args.thin_words, "include_query": self.args.include_query,
                        "user_agent": USER_AGENT,
                        "credentials_present": {"PAGESPEED_API_KEY": bool(self.pagespeed_key),
                                                "CRUX_API_KEY": bool(envkeys.secret("CRUX_API_KEY")),
                                                "GSC_SERVICE_ACCOUNT_FILE": bool(self.gsc_file),
                                                self.args.indexnow_key_env: bool(self.indexnow_key)}},
            "requests": self.requests,
            "modules": self.modules,
            "summary": {"findings": counts, "pages_fetched": len(self.pages),
                        "sitemap_urls": len(self.sitemaps.urls), "crawl_complete": getattr(self, "crawl_complete", False),
                        "sitemap_sampled": getattr(self, "sitemap_sampled", False),
                        "skipped_by_robots": getattr(self, "skipped_by_robots", [])},
            "findings": findings,
            "robots_txt": {"status": self.robots_status, "sitemaps": self.robots.records("sitemap") if self.robots else []},
            "ai_access": getattr(self, "ai_access", None),
            "sitemaps": {"read": self.sitemaps.read, "lastmod": getattr(self, "lastmod_stats", None),
                         "entries": [{"loc": e.loc, "lastmod": e.lastmod} for e in self.sitemaps.entries]},
            "probes_404": getattr(self, "probes", []),
            "link_graph": {k: v for k, v in (g or {}).items() if k != "per_page"} if g else None,
            "pagespeed": self.psi,
            "crux": self.crux,
            "search_console": self.gsc,
            "indexnow": self.indexnow,
            "pages": pages,
            "previous_report": (previous or {}).get("_path"),
        }

    def write_outputs(self, previous: dict | None) -> int:
        import report_markdown
        import diff_reports

        folder = self.out_folder()
        folder.mkdir(parents=True, exist_ok=True)
        stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
        report = envkeys.redact_obj(self.report, self.secrets)
        json_path = folder / f"audit_{stamp}.json"
        md_path = folder / f"audit_{stamp}.md"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(envkeys.redact(report_markdown.render(report), self.secrets), encoding="utf-8")
        written = [md_path, json_path]

        proposed = self.proposed_sitemap()
        if proposed:
            path = folder / f"audit_{stamp}_sitemap.proposed.xml"
            path.write_text(proposed, encoding="utf-8")
            written.append(path)
        if self.indexnow and self.indexnow["changed_urls"]:
            path = folder / f"audit_{stamp}_indexnow_urls.txt"
            path.write_text("\n".join(self.indexnow["changed_urls"]) + "\n", encoding="utf-8")
            written.append(path)
        new_p0 = []
        if previous is not None:
            diff = diff_reports.diff(previous, report)
            path = folder / f"diff_{stamp}.md"
            path.write_text(diff_reports.render(diff), encoding="utf-8")
            written.append(path)
            new_p0 = [f for f in diff["new"] if f["priority"] == "P0"]

        c = report["summary"]["findings"]
        self.log("")
        self.log(f"Resultat : P0={c['P0']} P1={c['P1']} P2={c['P2']} ; {report['summary']['pages_fetched']} page(s), "
                 f"{report['requests']} requete(s)")
        for f in report["findings"][:12]:
            self.log(f"  {f['priority']} {f['title']} ({f['count']}) [{f['label']}, {f['nature']}]")
        for name, m in report["modules"].items():
            self.log(f"  module {name}: {m['status']}" + (f" -- {m['reason']}" if m["reason"] else ""))
        for p in written:
            self.log(f"Ecrit : {p}")
        if new_p0:
            self.log(f"NOUVEAU P0 depuis le rapport precedent : {', '.join(f['title'] for f in new_p0)}")
        if self.pages.get(getattr(self, "home", ""), None) is None or self.pages[self.home].http_status != 200:
            return 2
        return 1 if c["P0"] else 0

    def proposed_sitemap(self) -> str | None:
        codes = {"sitemap-non-200", "sitemap-noindex", "sitemap-canonical-elsewhere", "not-in-sitemap",
                 "sitemap-lastmod-uniform", "sitemap-lastmod-future", "sitemap-foreign-host"}
        if not codes & set(self.findings.items) or not self.crawl_complete_or_small():
            return None
        entries, seen = [], set()
        for key, s in sorted(self.pages.items()):
            if not self._indexable(s) or key in seen:
                continue
            if s.canonical and linkgraph.normalize(s.canonical) != key:
                continue
            if urllib.parse.urlsplit(key).netloc != self.host:
                continue
            seen.add(key)
            lastmod = self.sitemaps.lastmod_of(key) or next(
                (e.lastmod for e in self.sitemaps.entries if self.resolve.get(linkgraph.normalize(e.loc)) == key), None)
            if "sitemap-lastmod-uniform" in self.findings.items:
                lastmod = None  # a generation date is not a modification date
            entries.append((s.final_url or key, lastmod))
        return sitemaps_mod.build_proposed_sitemap(entries) if entries else None

    def crawl_complete_or_small(self) -> bool:
        # Only propose a replacement sitemap when every declared URL was checked.
        return bool(getattr(self, "crawl_complete", False))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--site", required=True, help="URL de l'accueil, ex: https://example.com")
    p.add_argument("--out-dir", default="seo-reports", help="Dossier des rapports (defaut : ./seo-reports)")
    p.add_argument("--max-pages", type=int, default=60, help="Pages HTML recuperees au plus (defaut 60)")
    p.add_argument("--delay", type=float, default=0.5, help="Secondes entre deux requetes (defaut 0.5)")
    p.add_argument("--timeout", type=float, default=20.0)
    p.add_argument("--include-query", action="store_true", help="Suivre aussi les URLs a parametres")
    p.add_argument("--max-depth", type=int, default=3, help="Profondeur de clic signalee au-dela (heuristique, defaut 3)")
    p.add_argument("--thin-words", type=int, default=60, help="Mots sous lesquels une page est 'quasi vide' (heuristique)")
    p.add_argument("--probes", type=int, default=20, help="URLs inexistantes sondees au plus (defaut 20)")
    p.add_argument("--extra-targets", type=int, default=15, help="Cibles canonical/hreflang hors crawl a verifier")
    p.add_argument("--no-ai-access", action="store_true", help="Ne pas tester les crawlers IA")
    p.add_argument("--psi-pages", type=int, default=3, help="Pages mesurees par PageSpeed Insights (si cle)")
    p.add_argument("--psi-strategy", choices=["mobile", "desktop"], default="mobile")
    p.add_argument("--gsc-site", default=None, help="Propriete Search Console, ex: sc-domain:example.com (ou GSC_SITE)")
    p.add_argument("--gsc-days", type=int, default=28)
    p.add_argument("--indexnow-key-env", default="INDEXNOW_KEY",
                   help="Nom de la variable d'environnement qui contient la cle IndexNow de CE site")
    p.add_argument("--indexnow-submit", action="store_true",
                   help="Soumettre a IndexNow les URLs nouvelles/modifiees (action externe, a approuver)")
    p.add_argument("--no-diff", action="store_true", help="Ne pas comparer au rapport precedent")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    if not urllib.parse.urlsplit(args.site).scheme.startswith("http"):
        print("--site doit commencer par http:// ou https://", file=sys.stderr)
        return 2
    return Audit(args).run()


if __name__ == "__main__":
    sys.exit(main())
