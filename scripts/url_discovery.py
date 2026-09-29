#!/usr/bin/env python3
"""Decouverte automatique des nouvelles URL d'un site, sans navigateur.

A lancer a chaque publication (hook de deploiement) ou une fois par jour
(tache planifiee). Methode et sources : references/url-discovery.md.

Ce que fait un passage :
1. lit robots.txt : le sitemap y est-il declare (ligne Sitemap:) ?
2. lit le(s) sitemap(s) et compare au passage precedent : URL nouvelles,
   modifiees (lastmod change) et retirees ; controle que lastmod est exploitable ;
3. controle le maillage : chaque nouvelle URL est-elle liee depuis l'accueil
   (ou depuis une page --hub-page) ?
4. flux Atom/RSS (--feed, ou detectes dans l'accueil) : hub WebSub declare ?
5. avec --submit et s'il y a du nouveau :
   - re-soumet le(s) sitemap(s) via l'API Search Console (sitemaps.submit) ;
   - notifie le hub WebSub de chaque flux (POST hub.mode=publish, hub.url=<flux>) ;
   - envoie les URL nouvelles, modifiees et retirees a IndexNow ;
6. avec --inspect N : URL Inspection API sur N URL au plus (nouvelles d'abord),
   liste des URL non indexees et des quelques URL a proposer a la demande
   manuelle (bonus optionnel, navigateur de l'utilisateur).

Sans --submit, rien n'est envoye a un tiers (lecture seule : GET vers le site,
lectures Search Console). --submit est une action externe : a n'activer
qu'avec l'accord du proprietaire, y compris dans une tache planifiee.

Acces (variables d'environnement, jamais en argument) : GSC_SERVICE_ACCOUNT_FILE
ou GSC_ACCESS_TOKEN (Search Console), INDEXNOW_KEY (ou --indexnow-key-env).
Absents : l'etape correspondante est "skipped", jamais "OK".

Usage :
    python url_discovery.py --site https://example.com --gsc-site sc-domain:example.com
    python url_discovery.py --site https://example.com --gsc-site sc-domain:example.com \\
        --feed https://example.com/feed.xml --submit --inspect 200

Sortie : <out-dir>/<hote>/discovery_<AAAAMMJJTHHMMSSZ>.json et .md ; etat dans
<out-dir>/<hote>/discovery_state.json (URL vues, URL en attente d'annonce,
etat d'inspection). Codes : 0 = OK ; 1 = une action ou un controle bloquant a
echoue ; 2 = site injoignable.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import envkeys  # noqa: E402
import robotstxt  # noqa: E402
import search_console  # noqa: E402
import sitemaps  # noqa: E402

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-discovery/2.4)"
DEFAULT_HUB = "https://pubsubhubbub.appspot.com/"
FEED_TYPES = ("application/rss+xml", "application/atom+xml", "application/feed+json")


# --------------------------------------------------------------------------- HTTP

def http_get(url: str, timeout: float = 20.0) -> tuple[int | None, bytes | None, dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(10 * 1024 * 1024), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, None, dict(e.headers or {})
    except Exception:  # DNS, TLS, timeout
        return None, None, {}


def http_post_form(url: str, fields: list[tuple[str, str]], timeout: float = 20.0) -> tuple[int | None, str]:
    data = urllib.parse.urlencode(fields).encode("ascii")
    try:
        req = urllib.request.Request(url, data=data, method="POST", headers={
            "User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(2000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000).decode("utf-8", errors="replace")
    except Exception as e:
        return None, str(e)


# --------------------------------------------------------------------------- parsing

class _HomeParser(HTMLParser):
    """Feed <link rel=alternate> and <a href> of a page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.feeds: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "link" and "alternate" in a.get("rel", "").lower().split() \
                and a.get("type", "").lower() in FEED_TYPES and a.get("href"):
            self.feeds.append(a["href"])
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])


def parse_page(html: str, base: str) -> tuple[list[str], set[str]]:
    """(feed URLs, normalized absolute link targets) of an HTML page."""
    p = _HomeParser()
    p.feed(html)
    feeds = [urllib.parse.urljoin(base, f) for f in p.feeds]
    links = {normalize(urllib.parse.urljoin(base, h)) for h in p.links
             if not h.strip().lower().startswith(("javascript:", "mailto:", "tel:", "#"))}
    return feeds, links


def normalize(url: str) -> str:
    """Fragment dropped; '/x/' and '/x' compared as the same page."""
    u = urllib.parse.urlparse(url)._replace(fragment="")
    path = u.path.rstrip("/") or "/"
    return urllib.parse.urlunparse(u._replace(path=path, netloc=u.netloc.lower()))


def feed_hubs(body: bytes, headers: dict) -> dict:
    """WebSub facts of a feed: format, declared hubs (XML link rel=hub or HTTP
    Link header), self URL."""
    info = {"format": None, "hubs": [], "self": None, "error": None}
    for value in [v for k, v in headers.items() if k.lower() == "link"]:
        for part in value.split(","):
            if 'rel="hub"' in part or "rel=hub" in part:
                info["hubs"].append(part.split(";")[0].strip(" <>"))
            if 'rel="self"' in part or "rel=self" in part:
                info["self"] = part.split(";")[0].strip(" <>")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        if body.lstrip()[:1] == b"{":
            info["format"] = "json"
        else:
            info["error"] = f"flux illisible : {e}"
        return info
    tag = root.tag.rsplit("}", 1)[-1].lower()
    info["format"] = {"feed": "atom", "rss": "rss", "rdf": "rss"}.get(tag, tag)
    for el in root.iter():
        if el.tag.rsplit("}", 1)[-1] != "link":
            continue
        rel, href = el.get("rel", ""), el.get("href", "")
        if rel == "hub" and href:
            info["hubs"].append(href)
        elif rel == "self" and href and not info["self"]:
            info["self"] = href
    info["hubs"] = list(dict.fromkeys(info["hubs"]))
    return info


def diff_entries(previous: dict[str, str | None] | None, current: dict[str, str | None]) -> dict:
    """New, modified (lastmod changed) and removed URLs. previous None = first run."""
    if previous is None:
        return {"baseline": True, "new": [], "modified": [], "removed": []}
    return {
        "baseline": False,
        "new": sorted(u for u in current if u not in previous),
        "modified": sorted(u for u in current if u in previous and current[u] and current[u] != previous[u]),
        "removed": sorted(u for u in previous if u not in current),
    }


# --------------------------------------------------------------------------- run

class Discovery:
    def __init__(self, args, get=http_get, post=http_post_form, gsc_client=None, now=None, sleep=time.sleep) -> None:
        self.args = args
        self.sleep = sleep
        self.get = get
        self.post = post
        self.gsc = gsc_client
        self.now = now or datetime.now(timezone.utc)
        self.site = args.site.rstrip("/")
        self.host = urllib.parse.urlparse(self.site).netloc
        self.indexnow_key = envkeys.secret(args.indexnow_key_env)
        self.secrets = [self.indexnow_key]
        self.steps: dict[str, dict] = {}
        self.findings: list[dict] = []
        self.failed = False

    def step(self, name: str, status: str, detail: str, **data) -> None:
        self.steps[name] = {"status": status, "detail": envkeys.redact(detail, self.secrets), **data}

    def finding(self, level: str, message: str, urls: list[str] | None = None) -> None:
        self.findings.append({"level": level, "message": message, "urls": urls or []})
        if level == "P0":
            self.failed = True

    # ----------------------------------------------------------------------- steps

    def run(self, state: dict) -> dict:
        status, body, _ = self.get(self.site + "/")
        if body is None:
            self.step("home", "error", f"accueil injoignable (HTTP {status})")
            return self.result(state, unreachable=True)
        home_feeds, home_links = parse_page(body.decode("utf-8", errors="replace"), self.site + "/")
        self.step("home", "ran", f"{len(home_links)} lien(s), {len(home_feeds)} flux declare(s)")

        declared = self.check_robots()
        current = self.read_sitemaps(declared)
        changes = self.compute_changes(state, current)
        self.check_linking(changes, home_links)
        feeds = self.check_feeds(home_feeds)
        announce = changes["pending"]
        self.submit_sitemaps(declared, bool(announce))
        self.ping_websub(feeds, bool(announce))
        self.indexnow(announce)
        self.inspect(state, current, changes)
        if self.args.submit and announce and not any(
                s.get("status") == "error" for k, s in self.steps.items() if k in ("search_console", "websub", "indexnow")):
            state["pending"] = []  # announced everywhere it could be
        return self.result(state)

    def check_robots(self) -> list[str]:
        status, body, _ = self.get(self.site + "/robots.txt")
        if status != 200 or body is None:
            self.step("robots", "ran", f"robots.txt HTTP {status}")
            self.finding("P1", f"robots.txt non servi en 200 (HTTP {status}) : le sitemap n'y est pas declare")
            return []
        declared = robotstxt.parse(body.decode("utf-8", errors="replace")).records("sitemap")
        self.step("robots", "ran", f"{len(declared)} ligne(s) Sitemap:", sitemaps=declared)
        if not declared:
            self.finding("P1", "Aucune ligne « Sitemap: » dans robots.txt (Google la lit a chaque passage sur robots.txt)")
        return declared

    def read_sitemaps(self, declared: list[str]) -> dict[str, str | None]:
        def fetch(url, timeout):
            status, body, _ = self.get(url)
            return status, body, None if body is not None else f"HTTP {status}"

        found = sitemaps.discover(self.site, declared, fetch=fetch)
        current = {e.loc: e.lastmod for e in found.entries}
        lm = sitemaps.lastmod_findings(found, self.now)
        self.step("sitemaps", "ran" if current else "error",
                  f"{len(found.read)} sitemap(s) lu(s), {len(current)} URL(s), {lm['with_lastmod']} avec lastmod",
                  read=[{k: r[k] for k in ("url", "status", "count", "error")} for r in found.read])
        if not current:
            self.finding("P0", "Aucun sitemap lisible : Google et IndexNow n'ont rien a decouvrir")
        elif lm["with_lastmod"] < len(current):
            self.finding("P2", f"{len(current) - lm['with_lastmod']} URL(s) sans lastmod : la modification ne peut pas etre signalee")
        if lm["uniform"]:
            self.finding("P1", f"lastmod identique partout ({lm['uniform_value']}) : date de generation, pas de modification ; Google finit par l'ignorer")
        if lm["future"]:
            self.finding("P1", "lastmod dans le futur", lm["future"][:20])
        self.sitemap_files = [r["url"] for r in found.read if r["kind"] and r["url"] in declared] or \
            [r["url"] for r in found.read if r["kind"] == "index"] or [r["url"] for r in found.read if r["kind"]][:1]
        return current

    def compute_changes(self, state: dict, current: dict[str, str | None]) -> dict:
        previous = state.get("sitemap")
        if self.args.urls:
            forced = [u.strip() for u in Path(self.args.urls).read_text(encoding="utf-8").splitlines() if u.strip()]
            changes = {"baseline": False, "new": forced, "modified": [], "removed": []}
        else:
            changes = diff_entries(previous, current)
        if current:
            state["sitemap"] = current
        pending = list(dict.fromkeys(state.get("pending", []) + changes["new"] + changes["modified"] + changes["removed"]))
        state["pending"] = pending
        changes["pending"] = pending
        self.changes = changes
        detail = ("premier passage : etat de reference enregistre, rien a annoncer" if changes["baseline"] else
                  f"{len(changes['new'])} nouvelle(s), {len(changes['modified'])} modifiee(s), "
                  f"{len(changes['removed'])} retiree(s) ; {len(pending)} en attente d'annonce")
        self.step("changes", "ran", detail)
        return changes

    def check_linking(self, changes: dict, home_links: set[str]) -> None:
        targets = set(home_links)
        for hub in self.args.hub_page or []:
            status, body, _ = self.get(hub)
            if body is not None:
                targets |= parse_page(body.decode("utf-8", errors="replace"), hub)[1]
        new = [u for u in changes["new"] if normalize(u) != normalize(self.site + "/")]
        orphans = [u for u in new if normalize(u) not in targets]
        self.step("linking", "ran", f"{len(new) - len(orphans)}/{len(new)} nouvelle(s) URL liee(s) depuis l'accueil"
                  + (" ou les pages --hub-page" if self.args.hub_page else ""), not_linked=orphans)
        if orphans:
            self.finding("P1", "Nouvelle(s) page(s) sans lien depuis l'accueil ni une page de rubrique fournie : "
                               "ajouter un lien <a href> (bloc « derniers articles », rubrique)", orphans[:50])

    def check_feeds(self, home_feeds: list[str]) -> list[dict]:
        urls = list(dict.fromkeys((self.args.feed or []) + home_feeds))
        feeds = []
        for url in urls:
            status, body, headers = self.get(url)
            if body is None:
                feeds.append({"url": url, "status": status, "hubs": [], "error": f"HTTP {status}"})
                self.finding("P1", f"Flux declare mais injoignable (HTTP {status})", [url])
                continue
            info = feed_hubs(body, headers)
            feeds.append({"url": url, "status": status, **info})
        no_hub = [f["url"] for f in feeds if not f.get("hubs") and f.get("format") in ("atom", "rss")]
        if no_hub:
            self.finding("P2", "Flux sans hub WebSub : ajouter <link rel=\"hub\" href=\"" + DEFAULT_HUB
                         + "\"/> (Atom) ou <atom:link rel=\"hub\" .../> (RSS), plus rel=\"self\"", no_hub)
        self.step("feeds", "ran" if urls else "skipped",
                  f"{len(urls)} flux, {sum(1 for f in feeds if f.get('hubs'))} avec hub" if urls
                  else "aucun flux (--feed, ou <link rel=alternate> dans l'accueil)", feeds=feeds)
        return feeds

    def submit_sitemaps(self, declared: list[str], changed: bool) -> None:
        if not self.args.gsc_site:
            self.step("search_console", "skipped", "propriete absente (--gsc-site ou GSC_SITE)")
            return
        if self.gsc is None:
            try:
                self.gsc = search_console.SearchConsole(search_console.access_token(write=self.args.submit))
            except search_console.AccessMissing as e:
                self.step("search_console", "skipped", str(e))
                return
            except Exception as e:  # token refresh failed (key revoked, clock...)
                self.step("search_console", "error", f"jeton : {type(e).__name__}")
                self.failed = True
                return
        try:
            known = {s.get("path"): s for s in self.gsc.sitemaps(self.args.gsc_site)}
        except search_console.ApiError as e:
            self.step("search_console", "error", f"sitemaps.list : {e}")
            self.failed = True
            return
        files = self.sitemap_files or declared
        missing = [f for f in files if f not in known]
        with_errors = [p for p, s in known.items() if int(s.get("errors") or 0) > 0]
        if missing:
            self.finding("P1", "Sitemap non soumis dans Search Console", missing)
        if with_errors:
            self.finding("P1", "Sitemap signale en erreur par Search Console", with_errors)
        to_submit = files if (changed or missing) else []
        if not self.args.submit:
            self.step("search_console", "ran", f"{len(known)} sitemap(s) connus ; "
                      f"{len(to_submit)} a (re)soumettre, non soumis : --submit absent",
                      known=[{k: s.get(k) for k in ("path", "lastSubmitted", "lastDownloaded", "errors", "warnings")}
                             for s in known.values()], would_submit=to_submit)
            return
        done, errors = [], []
        for f in to_submit:
            try:
                self.gsc.submit_sitemap(self.args.gsc_site, f)
                done.append(f)
            except search_console.ApiError as e:
                errors.append(f"{f} : {e}")
        self.step("search_console", "error" if errors else "ran",
                  f"{len(done)} sitemap(s) soumis" + (f", {len(errors)} echec(s)" if errors else "")
                  + ("" if to_submit else " (rien de nouveau)"), submitted=done, errors=errors)
        if errors:
            self.failed = True

    def ping_websub(self, feeds: list[dict], changed: bool) -> None:
        with_hub = [f for f in feeds if f.get("hubs")]
        if not with_hub:
            self.step("websub", "skipped", "aucun flux avec hub declare")
            return
        if not (self.args.submit and changed):
            self.step("websub", "ran", "non notifie : " + ("--submit absent" if not self.args.submit else "rien de nouveau"),
                      would_ping=[f["url"] for f in with_hub])
            return
        results, errors = [], []
        for f in with_hub:
            topic = f.get("self") or f["url"]
            for hub in f["hubs"]:
                status, text = self.post(hub, [("hub.mode", "publish"), ("hub.url", topic)])
                ok = status is not None and 200 <= status < 300
                results.append({"hub": hub, "feed": topic, "status": status})
                if not ok:
                    errors.append(f"{hub} -> HTTP {status} {text[:120]}")
        self.step("websub", "error" if errors else "ran", f"{len(results)} notification(s), {len(errors)} echec(s)",
                  results=results, errors=errors)
        if errors:
            self.failed = True

    def indexnow(self, urls: list[str]) -> None:
        if not self.indexnow_key:
            self.step("indexnow", "skipped", f"variable {self.args.indexnow_key_env} absente")
            return
        import indexnow_submit

        if not indexnow_submit.KEY_RE.match(self.indexnow_key):
            self.step("indexnow", "error", "format de cle invalide (8-128 caracteres a-z A-Z 0-9 -)")
            self.failed = True
            return
        own = [u for u in urls if urllib.parse.urlparse(u).netloc == self.host]
        if not self.args.submit or not own:
            self.step("indexnow", "ran", f"{len(own)} URL(s) candidate(s), non soumis : "
                      + ("--submit absent" if not self.args.submit else "rien de nouveau"))
            return
        ok, info = indexnow_submit.verify_key_file(self.host, self.indexnow_key, None)
        if not ok:
            self.step("indexnow", "error", f"fichier de cle : {info}")
            self.failed = True
            return
        status, _ = indexnow_submit.submit(self.host, self.indexnow_key, info, own[:indexnow_submit.MAX_URLS_PER_REQUEST])
        good = status in (200, 202)
        self.step("indexnow", "ran" if good else "error",
                  f"{len(own)} URL(s) : HTTP {status} {indexnow_submit.interpret_status(status)}")
        if not good:
            self.failed = True

    def inspect(self, state: dict, current: dict[str, str | None], changes: dict) -> None:
        if self.args.inspect <= 0:
            self.step("inspection", "skipped", "--inspect 0")
            return
        if self.gsc is None or not self.args.gsc_site:
            self.step("inspection", "skipped", "acces Search Console absent")
            return
        fresh = changes["new"] + changes["modified"]
        order = search_console.order_urls(list(current.items()), fresh + (self.args.priority or []))
        report = search_console.run_inspection(
            self.gsc, self.args.gsc_site, order, state.setdefault("inspection", {}),
            max_inspect=self.args.inspect, max_request=self.args.max_request, sleep=self.sleep)
        self.inspection = report
        self.step("inspection", "error" if report["errors"] and not report["inspected"] else "ran",
                  f"{report['inspected']} inspectee(s), {report['indexed']} indexee(s), "
                  f"{len(report['not_indexed'])} non indexee(s)"
                  + (" ; quota atteint" if report["quota_stopped"] else ""))

    # ----------------------------------------------------------------------- output

    def result(self, state: dict, unreachable: bool = False) -> dict:
        state["last_run"] = self.now.isoformat()
        return {
            "site": self.site,
            "generated_at": self.now.isoformat(),
            "submit": bool(self.args.submit),
            "unreachable": unreachable,
            "steps": self.steps,
            "changes": getattr(self, "changes", None),
            "findings": self.findings,
            "inspection": getattr(self, "inspection", None),
            "failed": self.failed,
        }


def render_markdown(r: dict) -> str:
    out = [f"# Decouverte des URL -- {r['site']}", "",
           f"Passage du {r['generated_at']} ; envois : {'oui (--submit)' if r['submit'] else 'non (lecture seule)'}", "",
           "## Etapes", "", "| Etape | Statut | Detail |", "|---|---|---|"]
    for name, s in r["steps"].items():
        out.append(f"| {name} | {s['status']} | {s['detail']} |")
    if r["findings"]:
        out += ["", "## Constats", ""]
        for f in sorted(r["findings"], key=lambda x: x["level"]):
            out.append(f"- **{f['level']}** {f['message']}" + (f" ({len(f['urls'])})" if f["urls"] else ""))
            out += [f"  - {u}" for u in f["urls"][:10]]
    ch = r.get("changes") or {}
    if ch.get("pending"):
        out += ["", "## URL a annoncer", ""] + [f"- {u}" for u in ch["pending"][:50]]
    ins = r.get("inspection")
    if ins:
        out += ["", "## Non indexees (URL Inspection API)", "",
                f"{ins['inspected']} inspectee(s), {ins['indexed']} indexee(s). Par categorie : "
                + (", ".join(f"{k} {v}" for k, v in sorted(ins["by_category"].items())) or "aucune"), ""]
        out += [f"- {x['url']} -- {x['category']} : {x['next_step']}" for x in ins["not_indexed"][:50]]
        if ins["to_request"]:
            out += ["", "Proposees a la demande manuelle (bonus, navigateur, ~10/jour) :", ""]
            out += [f"- {u}" for u in ins["to_request"]]
    return "\n".join(out) + "\n"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--site", required=True, help="URL de l'accueil, ex: https://example.com")
    p.add_argument("--gsc-site", default=envkeys.secret("GSC_SITE"),
                   help="propriete Search Console (sc-domain:example.com ou https://example.com/) ; defaut GSC_SITE")
    p.add_argument("--feed", action="append", help="URL d'un flux Atom/RSS (repetable) ; sinon detection dans l'accueil")
    p.add_argument("--hub-page", action="append", help="page de rubrique qui doit lier les nouveautes (repetable)")
    p.add_argument("--urls", help="fichier : URL publiees a annoncer (remplace la detection par le sitemap)")
    p.add_argument("--priority", action="append", help="URL a inspecter en premier (repetable)")
    p.add_argument("--submit", action="store_true", help="envoie : sitemap (API), WebSub, IndexNow -- action externe")
    p.add_argument("--inspect", type=int, default=0, help="inspecte au plus N URL (0 = non ; plafond 2000/jour)")
    p.add_argument("--max-request", type=int, default=10, help="URL proposees a la demande manuelle (defaut 10)")
    p.add_argument("--indexnow-key-env", default="INDEXNOW_KEY")
    p.add_argument("--out-dir", default="seo-reports")
    return p.parse_args(argv)


def main(argv=None, **inject) -> int:
    args = parse_args(argv)
    disc = Discovery(args, **inject)
    folder = Path(args.out_dir) / disc.host.replace(":", "_")
    state_path = folder / "discovery_state.json"
    state = search_console.load_state(state_path)
    result = disc.run(state)
    result = envkeys.redact_obj(result, disc.secrets)
    stamp = disc.now.strftime("%Y%m%dT%H%M%SZ")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"discovery_{stamp}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / f"discovery_{stamp}.md").write_text(render_markdown(result), encoding="utf-8")
    search_console.save_state(state_path, state)
    for name, s in result["steps"].items():
        print(f"  {name}: {s['status']} -- {s['detail']}")
    for f in sorted(result["findings"], key=lambda x: x["level"]):
        print(f"  {f['level']} {f['message']}" + (f" ({len(f['urls'])})" if f["urls"] else ""))
    print(f"Rapport : {folder / f'discovery_{stamp}.md'}")
    if result["unreachable"]:
        return 2
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
