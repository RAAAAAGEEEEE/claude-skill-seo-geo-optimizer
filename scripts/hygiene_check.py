#!/usr/bin/env python3
"""Hygiene checks that need no account: hostile bots and fake traffic,
and the "helpful content" signals Google documents for a small site.

Three subcommands, each printing findings with an evidence label and a
source (rules: references/bot-traffic-hygiene.md and
references/helpful-content-small-site.md):

  probes  --site URL
      Public GET requests to the audited site only. (a) scanner paths
      (/.env, /.git/config, /wp-login.php...): a closed connection (nginx
      `return 444`) or 404 is fine, a 200 is a finding; (b) link-preview and
      search robots (WhatsApp, facebookexternalhit, Googlebot, OAI-SearchBot,
      ClaudeBot...) must still get the home page: a 403, 429, 503 or a
      Cloudflare challenge (`cf-mitigated: challenge`) is a finding. The
      user-agent is simulated from your machine: a 200 does not prove the real
      robot passes (see references/cloudflare-ai-access.md).

  logs    access.log [...] [--internal-ip IP ...] [--cf-ranges FILE | --no-fetch]
      Reads nginx/Apache logs (same formats as crawler_logs.py). Measures the
      share of scanner lines, of internal traffic, of headless browsers, and
      of lines whose "client" is a Cloudflare address (= real_ip missing).
      Counts only: no IP address is ever written.

  content --site URL [--max-pages N] [--group-min N]
      Reads the sitemap, samples pages, and reports: pages without a visible
      byline, groups of near-duplicate pages under the same URL pattern
      (city/trade pages), pages with a thin unique text, and bursts of new
      sitemap dates. A heuristic: it lists, the owner decides.

Exit codes: 0 no blocking finding, 1 at least one P1 finding, 2 nothing could
be measured (site unreachable, no parsable line).

Stdlib only.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import crawler_logs  # noqa: E402
import sitemaps  # noqa: E402

CF_IPS = ("https://www.cloudflare.com/ips-v4", "https://www.cloudflare.com/ips-v6")
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

SCANNER_PATHS = ("/.env", "/.git/config", "/.ssh/id_rsa", "/wp-login.php", "/wp-admin/", "/phpmyadmin/",
                 "/xmlrpc.php", "/cgi-bin/")
SCANNER_RE = re.compile(r"(?i)(/\.env|/\.git(/|$)|/\.ssh|\.php(\?|$)|/wp-(admin|includes|content|login)|"
                        r"/phpmyadmin|/cgi-bin)")

# Preview and search robots that must keep reading the home page.
PREVIEW_UAS = {
    "WhatsApp": "WhatsApp/2.23.20.0 A",
    "facebookexternalhit": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "OAI-SearchBot": "Mozilla/5.0 (compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)",
    "ClaudeBot": "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
}

# --- evidence labels (see references/data-hygiene.md) ---------------------------
SRC_NGINX_444 = "https://nginx.org/en/docs/http/ngx_http_rewrite_module.html"
SRC_CF_REALIP = "https://developers.cloudflare.com/support/troubleshooting/restoring-visitor-ips/restoring-original-visitor-ips/"
SRC_CF_BFM = "https://developers.cloudflare.com/bots/get-started/bot-fight-mode/"
SRC_G_HELPFUL = "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
SRC_G_SPAM = "https://developers.google.com/search/docs/essentials/spam-policies"


def finding(code, priority, label, message, source, kind="mesuré"):
    return {"code": code, "priority": priority, "label": label, "message": message, "source": source, "kind": kind}


# --------------------------------------------------------------------------- HTTP

def _request(url: str, ua: str, timeout: float = 15.0):
    """(status, headers, body_text, error). error='closed' for a connection
    closed without a response (nginx 444) or reset."""
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read(300_000).decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read(20_000).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
        return e.code, dict(e.headers), body, None
    except (ConnectionError, TimeoutError) as e:
        return None, {}, "", "closed" if isinstance(e, ConnectionError) else "timeout"
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        closed = any(k in reason for k in ("RemoteDisconnected", "Connection reset", "Connection aborted",
                                           "BadStatusLine", "Remote end closed"))
        return None, {}, "", "closed" if closed else reason
    except Exception as e:  # noqa: BLE001
        text = str(e)
        closed = any(k in text for k in ("RemoteDisconnected", "Remote end closed", "BadStatusLine"))
        return None, {}, "", "closed" if closed else text


def is_challenge(status, headers, body) -> bool:
    h = {k.lower(): v for k, v in (headers or {}).items()}
    if h.get("cf-mitigated", "").lower() == "challenge":
        return True
    return status in (403, 429, 503) and ("just a moment" in body.lower() or "cf-chl" in body.lower())


# --------------------------------------------------------------------------- probes

def run_probes(site: str, request=_request, pause: float = 0.3) -> dict:
    origin = site.rstrip("/")
    out = {"scanner": [], "preview": [], "findings": []}
    st, _, _, err = request(origin + "/", BROWSER_UA)
    if st != 200:
        out["reachable"] = False
        out["error"] = err or f"HTTP {st}"
        return out
    out["reachable"] = True
    soft: list[str] = []
    for path in SCANNER_PATHS:
        st, headers, body, err = request(origin + path, BROWSER_UA)
        verdict = "closed" if err == "closed" else ("served" if st == 200 else f"http-{st}" if st else f"error:{err}")
        out["scanner"].append({"path": path, "status": st, "verdict": verdict})
        if st == 200:
            out["findings"].append(finding(
                "scanner-path-served", "P1", "ESTABLISHED",
                f"{path} répond 200 : vérifier qu'il ne s'agit pas d'un vrai fichier exposé (secret, dépôt). "
                "Un 200 HTML identique à l'accueil est un repli d'application, à couper quand même.",
                SRC_NGINX_444))
        elif st in (403, 404, 301, 302, 308):
            soft.append(f"{path}={st}")
        time.sleep(pause)
    if soft:
        out["findings"].append(finding(
            "scanner-path-not-444", "P2", "SUPPORTED",
            f"{len(soft)} chemin(s) de scanner répondent par une page ({', '.join(soft)}) : correct pour le "
            "visiteur, mais `return 444` ferme la connexion sans réponse et allège le journal (un scanner n'est "
            "pas un visiteur). Garder /.well-known/ ouvert.", SRC_NGINX_444, "inféré"))
    for name, ua in PREVIEW_UAS.items():
        st, headers, body, err = request(origin + "/", ua)
        verdict = "ok" if st == 200 else ("challenge" if is_challenge(st, headers, body) else (
            f"http-{st}" if st else f"error:{err}"))
        out["preview"].append({"robot": name, "status": st, "verdict": verdict})
        if verdict != "ok":
            out["findings"].append(finding(
                "preview-robot-refused", "P1", "ESTABLISHED",
                f"« {name} » simulé reçoit {verdict} sur l'accueil : un robot d'aperçu ou de recherche refusé "
                "perd le lien enrichi ou la citation. Regarder la règle 444 par agent, la limite de débit, "
                "Bot Fight Mode (non contournable par règle WAF) ou « Block AI bots ».",
                SRC_CF_BFM))
        time.sleep(pause)
    return out


# --------------------------------------------------------------------------- logs

def load_cf_ranges(path: str | None, fetch: bool) -> list:
    nets, sources = [], []
    if path:
        sources = [Path(path).read_text(encoding="utf-8")]
    elif fetch:
        for url in CF_IPS:
            st, _, body, _ = _request(url, "seo-geo-optimizer-audit/2.6")
            if st == 200:
                sources.append(body)
    for text in sources:
        for line in text.split():
            try:
                nets.append(ipaddress.ip_network(line.strip(), strict=False))
            except ValueError:
                pass
    return nets


def analyze_logs(lines, internal_ips=(), cf_nets=(), headless_re=re.compile(r"(?i)headlesschrome|phantomjs|puppeteer")) -> dict:
    total = scanner = internal = headless = cf = blocked444 = limited429 = 0
    scanner_ips: set[str] = set()
    internal_set = set(internal_ips)
    bot_decl = Counter()
    for raw in lines:
        hit = crawler_logs.parse_line(raw)
        if hit is None:
            continue
        total += 1
        if SCANNER_RE.search(hit.path):
            scanner += 1
            scanner_ips.add(hit.ip)
        if hit.ip in internal_set:
            internal += 1
        if headless_re.search(hit.ua):
            headless += 1
        if hit.status == 444:
            blocked444 += 1
        if hit.status == 429:
            limited429 += 1
        if cf_nets:
            try:
                ip = ipaddress.ip_address(hit.ip)
                if any(ip in n for n in cf_nets):
                    cf += 1
            except ValueError:
                pass
        c = crawler_logs.identify(hit.ua)
        if c:
            bot_decl[c.token] += 1
    return {"lines": total, "scanner": scanner, "scanner_distinct_sources": len(scanner_ips), "internal": internal,
            "headless": headless, "cloudflare_as_client": cf, "status_444": blocked444, "status_429": limited429,
            "declared_bots": sum(bot_decl.values()), "cf_ranges_loaded": bool(cf_nets),
            "internal_ips_given": bool(internal_set)}


def log_findings(r: dict) -> list[dict]:
    n = r["lines"] or 1
    out = []
    if r["cf_ranges_loaded"] and r["cloudflare_as_client"] / n > 0.01:
        out.append(finding(
            "real-ip-missing", "P1", "ESTABLISHED",
            f"{r['cloudflare_as_client']} ligne(s) sur {r['lines']} ({r['cloudflare_as_client'] * 100 // n} %) ont une "
            "adresse Cloudflare pour client : `set_real_ip_from` (plages Cloudflare) + `real_ip_header CF-Connecting-IP` "
            "manquent. Sans elles, limit_req, fail2ban et les statistiques voient Cloudflare, pas le visiteur.",
            SRC_CF_REALIP))
    if not r["cf_ranges_loaded"]:
        out.append(finding("cf-ranges-not-loaded", "P2", "ESTABLISHED",
                           "Plages Cloudflare non chargées (--no-fetch ou téléchargement impossible) : contrôle "
                           "real_ip non fait. Si le site n'est pas derrière Cloudflare, ce contrôle est sans objet.",
                           SRC_CF_REALIP, "inféré"))
    if r["scanner"] / n > 0.03:
        out.append(finding(
            "scanner-noise", "P2", "SUPPORTED",
            f"{r['scanner'] * 100 // n} % des lignes visent des chemins de scanners "
            f"({r['scanner_distinct_sources']} sources distinctes) : `return 444` sur ces chemins, et ne pas "
            "les compter comme visites. Une liste d'adresses ajoute peu, les scanners changent d'adresse.",
            SRC_NGINX_444))
    if r["internal_ips_given"] and r["internal"] / n > 0.05:
        out.append(finding(
            "internal-traffic", "P1", "ESTABLISHED",
            f"{r['internal'] * 100 // n} % des lignes viennent d'adresses internes déclarées : exclure du journal "
            "de statistiques (second access_log conditionnel) ou de l'outil de comptage, sinon l'audience est fausse.",
            "mesure locale du journal fourni"))
    if not r["internal_ips_given"]:
        out.append(finding("internal-ip-not-given", "P2", "ESTABLISHED",
                           "Aucune adresse interne fournie (--internal-ip) : part du trafic interne non mesurée "
                           "(serveur lui-même, surveillances, VPN).", "mesure locale", "inféré"))
    if r["headless"] / n > 0.03:
        out.append(finding(
            "headless-traffic", "P2", "SUPPORTED",
            f"{r['headless'] * 100 // n} % des lignes portent un navigateur sans tête : à compter à part "
            "(ce peut être votre propre surveillance).", "mesure locale du journal fourni"))
    return out


# --------------------------------------------------------------------------- content

class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.zone = []
        self.text: list[str] = []
        self.byline = False
        self.ld: list[str] = []
        self._ld = False
        self.date = False
        self.title = ""
        self._title = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag in ("script", "style", "noscript"):
            if tag == "script" and "ld+json" in a.get("type", ""):
                self._ld = True
            self.skip += 1
        if tag in ("nav", "header", "footer", "aside"):
            self.zone.append(tag)
        if tag == "title":
            self._title = True
        cls = (a.get("class", "") + " " + a.get("itemprop", "") + " " + a.get("rel", "")).lower()
        if tag == "meta" and a.get("name", "").lower() == "author" and a.get("content", "").strip():
            self.byline = True
        if re.search(r"\b(author|byline|auteur)\b", cls) or a.get("rel", "").lower() == "author":
            self.byline = True
        if tag == "time" and a.get("datetime"):
            self.date = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
            self._ld = False
        if tag in ("nav", "header", "footer", "aside") and tag in self.zone:
            self.zone.remove(tag)
        if tag == "title":
            self._title = False

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._ld:
            self.ld.append(data)
            return
        if self.skip or self.zone:
            return
        self.text.append(data)


def parse_content(html: str) -> dict:
    p = _Page()
    try:
        p.feed(html)
        p.close()
    except Exception:  # noqa: BLE001
        pass
    words = re.findall(r"[\wÀ-ÿ'-]+", " ".join(p.text).lower())
    ld_author = False
    for chunk in p.ld:
        try:
            data = json.loads(chunk)
        except ValueError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if node.get("author"):
                    ld_author = True
                stack += [v for v in node.values() if isinstance(v, (dict, list))]
            elif isinstance(node, list):
                stack += node
    return {"words": words, "byline": p.byline or ld_author, "date": p.date, "title": p.title.strip()}


def shingles(words: list[str], k: int = 5) -> set:
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def similarity(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _pattern(url: str) -> str:
    """Group key: path with the last segment replaced (… /services/plombier-lyon -> /services/*)."""
    parts = [s for s in urllib.parse.urlparse(url).path.split("/") if s]
    return "/" + "/".join(parts[:-1] + ["*"]) if len(parts) >= 2 else "/"


def analyze_content(pages: dict[str, dict], lastmods: dict[str, str | None], group_min: int = 5,
                    dup_threshold: float = 0.6) -> list[dict]:
    out = []
    content = {u: p for u, p in pages.items() if len(p["words"]) >= 50}
    groups: dict[str, list[str]] = defaultdict(list)
    for u in pages:
        groups[_pattern(u)].append(u)
    # near duplicates inside a group of sibling pages (city/trade pages)
    for pat, urls in groups.items():
        if len(urls) < group_min:
            continue
        sh = {u: shingles(pages[u]["words"]) for u in urls}
        dup_pairs, flagged = 0, set()
        for i, a in enumerate(urls):
            for b in urls[i + 1:]:
                if similarity(sh[a], sh[b]) >= dup_threshold:
                    dup_pairs += 1
                    flagged.update((a, b))
        if flagged:
            out.append(finding(
                "near-duplicate-pages", "P2", "ESTABLISHED",
                f"{len(flagged)} page(s) sur {len(urls)} sous {pat} se ressemblent à {int(dup_threshold * 100)} % ou "
                "plus (seuil du skill ; hors menus et pied de page) : pages ville/métier au gabarit identique. Google nomme "
                "ce motif (pages ciblant des villes qui mènent au même contenu, pages quasi identiques) "
                "dans les doorways et le contenu de masse. Regrouper, enrichir avec du contenu propre "
                "(exemples réels, prix, zone, photos) ou passer en noindex.",
                SRC_G_SPAM, "inféré"))
    thin = [u for u, p in pages.items() if len(p["words"]) < 150]
    if thin:
        out.append(finding("thin-pages", "P2", "CLAIMED",
                           f"{len(thin)} page(s) sur {len(pages)} avec moins de 150 mots de contenu propre "
                           "(seuil du skill, pas de Google, qui n'a pas de nombre de mots préféré) : une page courte "
                           "peut suffire si elle répond complètement. À relire, pas à gonfler.",
                           SRC_G_HELPFUL, "inféré"))
    articles = [u for u, p in content.items() if len(p["words"]) >= 300]
    no_byline = [u for u in articles if not pages[u]["byline"]]
    if articles and no_byline:
        out.append(finding("no-byline", "P2", "ESTABLISHED",
                           f"{len(no_byline)} page(s) de fond sur {len(articles)} sans auteur visible : Google "
                           "demande « Do pages carry a byline, where one might be expected? » et un lien vers "
                           "une page auteur. Ajouter un vrai nom (jamais un profil inventé).",
                           SRC_G_HELPFUL, "inféré"))
    dated = [u for u in lastmods if lastmods[u]]
    if len(dated) >= 10:
        per_day = Counter(lastmods[u][:10] for u in dated)
        day, n = per_day.most_common(1)[0]
        if n >= 10 and n / len(dated) > 0.5:
            out.append(finding("publication-burst", "P2", "ESTABLISHED",
                               f"{n} URL ont la même date {day} ({n * 100 // len(dated)} % du sitemap) : soit une "
                               "génération en masse, soit un lastmod de génération. Google déconseille d'ajouter "
                               "ou retirer beaucoup de contenu pour paraître « frais » ; étaler et ne dater que "
                               "les vraies modifications.", SRC_G_HELPFUL, "inféré"))
    return out


def run_content(site: str, max_pages: int, group_min: int, fetch=sitemaps._get) -> dict:
    origin = site.rstrip("/")
    st, _, _, err = _request(origin + "/", BROWSER_UA)
    if st != 200:
        return {"reachable": False, "error": err or f"HTTP {st}", "findings": []}
    robots = []
    s, body, _ = fetch(origin + "/robots.txt", 20.0)
    if s == 200 and body:
        robots = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body.decode("utf-8", "replace"))
    sm = sitemaps.discover(origin, robots, fetch=fetch)
    urls = sm.urls
    if not urls:
        return {"reachable": True, "pages": 0, "findings": [finding(
            "no-sitemap-urls", "P2", "ESTABLISHED", "Aucune URL lisible dans le sitemap : contrôle du contenu non fait.",
            SRC_G_HELPFUL, "inféré")]}
    # sample evenly across the list so every URL pattern is seen
    step = max(1, len(urls) // max_pages)
    sample = urls[::step][:max_pages]
    pages = {}
    for u in sample:
        st, headers, body, err = _request(u, BROWSER_UA)
        if st == 200 and body:
            pages[u] = parse_content(body)
        time.sleep(0.2)
    lastmods = {u: sm.lastmod_of(u) for u in urls}
    return {"reachable": True, "pages": len(pages), "sitemap_urls": len(urls),
            "findings": analyze_content(pages, lastmods, group_min)}


# --------------------------------------------------------------------------- CLI

def _print(findings: list[dict]) -> int:
    code = 0
    for f in findings:
        print(f"  {f['priority']} {f['message']} [{f['label']}, {f['kind']}] {f['source']}")
        if f["priority"] in ("P0", "P1"):
            code = 1
    if not findings:
        print("  aucun constat")
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("probes")
    p1.add_argument("--site", required=True)
    p1.add_argument("--json")
    p2 = sub.add_parser("logs")
    p2.add_argument("files", nargs="+")
    p2.add_argument("--internal-ip", action="append", default=[])
    p2.add_argument("--cf-ranges")
    p2.add_argument("--no-fetch", action="store_true")
    p2.add_argument("--json")
    p3 = sub.add_parser("content")
    p3.add_argument("--site", required=True)
    p3.add_argument("--max-pages", type=int, default=40)
    p3.add_argument("--group-min", type=int, default=5)
    p3.add_argument("--json")
    a = ap.parse_args(argv)

    if a.cmd == "probes":
        r = run_probes(a.site)
        if not r.get("reachable"):
            print(f"accueil injoignable ou hors 200 ({r.get('error')}) : rien à conclure", file=sys.stderr)
            return 2
        print("Scanners : " + ", ".join(f"{x['path']}={x['verdict']}" for x in r["scanner"]))
        print("Robots d'aperçu et de recherche : " + ", ".join(f"{x['robot']}={x['verdict']}" for x in r["preview"]))
        findings = r["findings"]
        data = r
    elif a.cmd == "logs":
        nets = load_cf_ranges(a.cf_ranges, not a.no_fetch)
        r = analyze_logs(crawler_logs.read_lines(a.files), a.internal_ip, nets)
        if not r["lines"]:
            print("aucune ligne exploitable", file=sys.stderr)
            return 2
        print("Mesures (comptes seulement) : " + ", ".join(f"{k}={v}" for k, v in r.items() if isinstance(v, int)))
        findings = log_findings(r)
        data = {**r, "findings": findings}
    else:
        r = run_content(a.site, a.max_pages, a.group_min)
        if not r.get("reachable"):
            print(f"accueil injoignable ou hors 200 ({r.get('error')}) : rien à conclure", file=sys.stderr)
            return 2
        print(f"{r.get('pages', 0)} page(s) lue(s) sur {r.get('sitemap_urls', 0)} URL du sitemap")
        findings = r["findings"]
        data = r
    code = _print(findings)
    if getattr(a, "json", None):
        Path(a.json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
