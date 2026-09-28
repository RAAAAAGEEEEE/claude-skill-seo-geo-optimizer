#!/usr/bin/env python3
"""Server-log analysis of search and AI crawlers, with verification against
the IP ranges the vendors publish.

What a log shows that no crawl of your own can: which crawler really came,
what it fetched, which status it got, and whether a request that *claims*
to be Googlebot or GPTBot really came from that vendor.

Per crawler (catalogue: ai_bots.py + a few engines and SEO tools):
  hits, pages vs robots.txt vs assets, status classes (2xx/3xx/4xx/5xx, 429),
  first/last seen, top paths, verified / spoofed / not verifiable hits.
Findings (each with evidence label and source, see references/automation.md):
  - 5xx or 429 served to a crawler         (ESTABLISHED, Google crawl docs)
  - robots.txt answered non-200 to crawlers (ESTABLISHED, RFC 9309 / Google)
  - user-agent claims a vendor, IP outside its published ranges
                                            (ESTABLISHED method: vendor JSON)
  - most-hit 404 paths (broken links or old URLs crawlers still request)
  - with --sitemap-urls or --site: sitemap URLs that Googlebot / bingbot /
    OAI-SearchBot never requested in the window (inferred, not a verdict).

Verification uses the vendors' JSON lists (fetched once per run, or read
from --ranges-dir for offline use). Vendors without a JSON list (Meta,
Amazon, MistralAI-Training) are reported as "non vérifiable", never as
verified. Reverse-DNS checks and Web Bot Auth signatures are not done here
(see references/automation.md).

Privacy: IP addresses are personal data. They never appear in the output:
counts only, and spoofed sources are shown as /24 (IPv4) or /48 (IPv6).

Log formats: Apache/nginx "combined" (default), or JSON lines with keys
remote_addr|ip|client_ip, time|time_local|timestamp, request|path|uri,
status, http_user_agent|user_agent. Gzip files are read directly.

Usage:
    python crawler_logs.py access.log [access.log.1.gz ...] [--site https://example.com]
        [--sitemap-urls urls.txt] [--no-verify] [--ranges-dir DIR] [--json out.json] [--md out.md]

Exit codes: 0 analysed, 1 at least one finding labelled ESTABLISHED with
blocking impact (5xx/429 to Googlebot or bingbot, robots.txt 5xx), 2 no
parsable line.
"""

from __future__ import annotations

import argparse
import gzip
import ipaddress
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ai_bots  # noqa: E402

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/2.3)"
CHECKED_ON = "2026-09-28"

_G = "https://developers.google.com/static/crawling/ipranges/"
# robots token (lower case) -> published IP range lists. All URLs fetched on
# 2026-09-28 (HTTP 200). Google announced on 2026-03-31 that the old
# /static/search/apis/ipranges/googlebot.json path will redirect: use these.
RANGES: dict[str, list[str]] = {
    "googlebot": [_G + "common-crawlers.json"],
    "googleother": [_G + "common-crawlers.json"],
    "google-inspectiontool": [_G + "common-crawlers.json"],
    "storebot-google": [_G + "common-crawlers.json"],
    "adsbot-google": [_G + "special-crawlers.json"],
    "google-agent": [_G + "user-triggered-agents.json"],
    "bingbot": ["https://www.bing.com/toolbox/bingbot.json"],
    "oai-searchbot": ["https://openai.com/searchbot.json"],
    "gptbot": ["https://openai.com/gptbot.json"],
    "chatgpt-user": ["https://openai.com/chatgpt-user.json"],
    "perplexitybot": ["https://www.perplexity.ai/perplexitybot.json"],
    "perplexity-user": ["https://www.perplexity.ai/perplexity-user.json"],
    "claudebot": ["https://claude.com/crawling/bots.json"],
    "claude-searchbot": ["https://claude.com/crawling/bots.json"],
    "claude-user": ["https://claude.com/crawling/bots.json"],
    "applebot": ["https://search.developer.apple.com/applebot.json"],
    "duckassistbot": ["https://duckduckgo.com/duckassistbot.json"],
    "ccbot": ["https://index.commoncrawl.org/ccbot.json"],
    "oai-adsbot": ["https://openai.com/adsbot.json"],
    "mistralai-user": ["https://mistral.ai/mistralai-user-ips.json"],
    "mistralai-index": ["https://mistral.ai/mistralai-index-ips.json"],
    "duckduckbot": ["https://duckduckgo.com/duckduckbot.json"],
}

# Crawlers outside ai_bots.py that matter in a log. (token, vendor, role)
EXTRA_BOTS = [
    ("GoogleOther", "Google", "engine"), ("Google-InspectionTool", "Google", "engine"),
    ("Storebot-Google", "Google", "engine"), ("AdsBot-Google", "Google", "engine"),
    ("YandexBot", "Yandex", "engine"), ("Baiduspider", "Baidu", "engine"), ("Qwantbot", "Qwant", "engine"),
    ("SeznamBot", "Seznam", "engine"), ("Bytespider", "ByteDance", "training"),
    ("AhrefsBot", "Ahrefs", "seo-tool"), ("SemrushBot", "Semrush", "seo-tool"), ("MJ12bot", "Majestic", "seo-tool"),
    ("DotBot", "Moz", "seo-tool"), ("OAI-AdsBot", "OpenAI", "other"), ("DuckDuckBot", "DuckDuckGo", "engine"),
]

CRITICAL = ("googlebot", "bingbot")  # a 5xx/429 to these slows or stops crawling of the whole site
COVERAGE_BOTS = ("Googlebot", "bingbot", "OAI-SearchBot")
ASSET_EXT = (".css", ".js", ".mjs", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico", ".woff",
             ".woff2", ".ttf", ".mp4", ".webm", ".map", ".json", ".xml", ".txt", ".pdf")

_COMBINED = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d{3}) \S+'
    r'(?: "(?P<referer>[^"]*)" "(?P<ua>[^"]*)")?')


# --------------------------------------------------------------------------- catalogue

@dataclass(frozen=True)
class Crawler:
    token: str
    vendor: str
    role: str


def catalogue() -> list[Crawler]:
    items = [Crawler(b.robots_token, b.vendor, b.role) for b in ai_bots.AI_BOTS if b.role != "token"]
    items += [Crawler(t, v, r) for t, v, r in EXTRA_BOTS]
    # Longest token first: "Googlebot" must not swallow "Google-InspectionTool", etc.
    return sorted(items, key=lambda c: -len(c.token))


_CATALOGUE = catalogue()


def identify(ua: str) -> Crawler | None:
    low = (ua or "").lower()
    for c in _CATALOGUE:
        if c.token.lower() in low:
            return c
    return None


# --------------------------------------------------------------------------- parsing

@dataclass
class Hit:
    ip: str
    time: datetime | None
    method: str
    path: str
    status: int
    ua: str


def _parse_time(value: str) -> datetime | None:
    for fmt in ("%d/%b/%Y:%H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            return datetime.strptime(value.replace("Z", "+0000"), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def _split_request(request: str) -> tuple[str, str]:
    parts = request.split()
    if len(parts) >= 2:
        return parts[0], parts[1]
    return "", request


def parse_line(line: str) -> Hit | None:
    line = line.strip()
    if not line:
        return None
    if line.startswith("{"):
        try:
            d = json.loads(line)
        except ValueError:
            return None
        ip = d.get("remote_addr") or d.get("ip") or d.get("client_ip") or ""
        req = d.get("request") or ""
        method, path = _split_request(req) if req else (d.get("method", ""), d.get("path") or d.get("uri") or "")
        try:
            status = int(d.get("status"))
        except (TypeError, ValueError):
            return None
        ts = d.get("time") or d.get("time_local") or d.get("timestamp") or ""
        return Hit(ip, _parse_time(str(ts)), method, path, status, d.get("http_user_agent") or d.get("user_agent") or "")
    m = _COMBINED.match(line)
    if not m:
        return None
    method, path = _split_request(m.group("request"))
    return Hit(m.group("ip"), _parse_time(m.group("time")), method, path, int(m.group("status")), m.group("ua") or "")


def read_lines(paths: list[str]):
    for p in paths:
        opener = gzip.open if p.endswith(".gz") else open
        with opener(p, "rt", encoding="utf-8", errors="replace") as fh:
            yield from fh


# --------------------------------------------------------------------------- IP ranges

def parse_ranges(data) -> list:
    """Every ipv4Prefix / ipv6Prefix in a vendor JSON (any nesting)."""
    out, stack = [], [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("ipv4Prefix", "ipv6Prefix") and isinstance(v, str):
                    try:
                        out.append(ipaddress.ip_network(v, strict=False))
                    except ValueError:
                        pass
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(node, list):
            stack.extend(node)
    return out


def load_ranges(tokens: set[str], ranges_dir: Path | None = None, timeout: float = 20.0) -> tuple[dict, dict]:
    """token -> list of networks, plus a status per list URL."""
    cache: dict[str, list] = {}
    status: dict[str, str] = {}
    result: dict[str, list] = {}
    for token in tokens:
        urls = RANGES.get(token)
        if not urls:
            continue
        nets = []
        for url in urls:
            if url not in cache:
                cache[url] = []
                try:
                    if ranges_dir:
                        f = ranges_dir / Path(urllib.parse.urlsplit(url).path).name
                        data = json.loads(f.read_text(encoding="utf-8"))
                    else:
                        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                        with urllib.request.urlopen(req, timeout=timeout) as r:
                            data = json.loads(r.read().decode("utf-8"))
                    cache[url] = parse_ranges(data)
                    status[url] = f"ok ({len(cache[url])} plages)"
                except (OSError, ValueError, urllib.error.URLError) as e:
                    status[url] = f"erreur : {e}"
            nets += cache[url]
        if nets:
            result[token] = nets
    return result, status


def verify(ip: str, nets: list) -> bool | None:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    return any(addr in n for n in nets if n.version == addr.version)


def mask(ip: str) -> str:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return "invalide"
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))


# --------------------------------------------------------------------------- analysis

@dataclass
class BotStats:
    vendor: str
    role: str
    hits: int = 0
    pages: int = 0
    robots_txt: int = 0
    assets: int = 0
    status: Counter = field(default_factory=Counter)
    paths: Counter = field(default_factory=Counter)
    first: datetime | None = None
    last: datetime | None = None
    verified: int = 0
    spoofed: int = 0
    unverifiable: int = 0
    spoof_sources: Counter = field(default_factory=Counter)
    robots_status: Counter = field(default_factory=Counter)


def _kind(path: str) -> str:
    p = urllib.parse.urlsplit(path).path.lower()
    if p == "/robots.txt":
        return "robots"
    if p.endswith(ASSET_EXT):
        return "asset"
    return "page"


def analyze(lines, ranges: dict | None = None) -> dict:
    bots: dict[str, BotStats] = {}
    parsed = unparsed = total_bot = 0
    not_found: Counter = Counter()
    fetched_by: dict[str, set[str]] = defaultdict(set)
    for line in lines:
        hit = parse_line(line)
        if hit is None:
            if line.strip():
                unparsed += 1
            continue
        parsed += 1
        crawler = identify(hit.ua)
        if not crawler:
            continue
        total_bot += 1
        s = bots.setdefault(crawler.token, BotStats(crawler.vendor, crawler.role))
        s.hits += 1
        kind = _kind(hit.path)
        path_only = urllib.parse.urlsplit(hit.path).path or "/"
        if kind == "robots":
            s.robots_txt += 1
            s.robots_status[hit.status] += 1
        elif kind == "asset":
            s.assets += 1
        else:
            s.pages += 1
            s.paths[path_only] += 1
            if 200 <= hit.status < 300:
                fetched_by[crawler.token].add(path_only)
        s.status[hit.status] += 1
        if hit.status == 404:
            not_found[path_only] += 1
        if hit.time:
            s.first = min(s.first, hit.time) if s.first else hit.time
            s.last = max(s.last, hit.time) if s.last else hit.time
        nets = (ranges or {}).get(crawler.token.lower())
        if ranges is None or not nets:
            s.unverifiable += 1
        else:
            ok = verify(hit.ip, nets)
            if ok:
                s.verified += 1
            elif ok is False:
                s.spoofed += 1
                s.spoof_sources[mask(hit.ip)] += 1
            else:
                s.unverifiable += 1
    return {"parsed": parsed, "unparsed": unparsed, "bot_hits": total_bot, "bots": bots,
            "not_found": not_found, "fetched_by": fetched_by}


def _status_classes(c: Counter) -> dict:
    out = Counter()
    for code, n in c.items():
        out[f"{code // 100}xx"] += n
    if c.get(429):
        out["429"] = c[429]
    return dict(sorted(out.items()))


def findings(result: dict, sitemap_paths: list[str] | None = None) -> list[dict]:
    out = []
    for token, s in result["bots"].items():
        errors = sum(n for code, n in s.status.items() if code >= 500)
        throttled = s.status.get(429, 0)
        if errors or throttled:
            blocking = token.lower() in CRITICAL
            out.append({"code": "crawler-5xx-429", "label": "ESTABLISHED", "blocking": blocking,
                        "detail": f"{token} : {errors} réponse(s) 5xx et {throttled} 429 sur {s.hits} requête(s)",
                        "source": "https://developers.google.com/crawling/docs/crawl-budget (5xx/429 ralentissent le crawl)"})
        bad_robots = {c: n for c, n in s.robots_status.items() if c != 200}
        if bad_robots:
            blocking = any(c >= 500 or c == 429 for c in bad_robots)
            out.append({"code": "robots-txt-not-200", "label": "ESTABLISHED", "blocking": blocking,
                        "detail": f"{token} : robots.txt servi en {bad_robots} (5xx/429 = tout interdit chez Google)",
                        "source": "https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec"})
        if s.spoofed:
            out.append({"code": "spoofed-crawler", "label": "ESTABLISHED", "blocking": False,
                        "detail": f"{token} : {s.spoofed} requête(s) hors des plages publiées par {s.vendor} "
                                  f"(sources : {', '.join(n for n, _ in s.spoof_sources.most_common(5))})",
                        "source": "https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests et listes JSON des fournisseurs (RANGES)"})
    if result["not_found"]:
        top = ", ".join(f"{p} ({n})" for p, n in result["not_found"].most_common(10))
        out.append({"code": "crawler-404", "label": "ESTABLISHED", "blocking": False,
                    "detail": f"404 les plus demandés par des crawlers : {top}",
                    "source": "https://developers.google.com/crawling/docs/troubleshooting/http-status-codes"})
    if sitemap_paths:
        for token in COVERAGE_BOTS:
            if token not in result["bots"]:
                continue
            seen = result["fetched_by"].get(token, set())
            missing = [p for p in sitemap_paths if p not in seen]
            if missing:
                out.append({"code": "sitemap-url-not-crawled", "label": "inféré", "blocking": False,
                            "detail": f"{token} : {len(missing)}/{len(sitemap_paths)} URL(s) du sitemap jamais "
                                      f"demandée(s) en 2xx sur la période, ex. {', '.join(missing[:5])}",
                            "source": "comparaison journal / sitemap (fenêtre du journal seulement)"})
    return out


def to_json(result: dict, fnd: list[dict], range_status: dict) -> dict:
    bots = {}
    for token, s in sorted(result["bots"].items(), key=lambda kv: -kv[1].hits):
        bots[token] = {"vendor": s.vendor, "role": s.role, "hits": s.hits, "pages": s.pages,
                       "robots_txt": s.robots_txt, "assets": s.assets, "status": _status_classes(s.status),
                       "first": s.first.isoformat() if s.first else None,
                       "last": s.last.isoformat() if s.last else None,
                       "verified": s.verified, "spoofed": s.spoofed, "unverifiable": s.unverifiable,
                       "top_paths": s.paths.most_common(10)}
    return {"tool": "crawler_logs.py", "ranges_checked_on": CHECKED_ON, "parsed_lines": result["parsed"],
            "unparsed_lines": result["unparsed"], "bot_hits": result["bot_hits"], "bots": bots,
            "range_lists": range_status, "findings": fnd}


def render_md(data: dict) -> str:
    lines = ["# Crawlers dans les journaux", "",
             f"{data['parsed_lines']} ligne(s) lue(s), {data['unparsed_lines']} non reconnue(s), "
             f"{data['bot_hits']} requête(s) de crawlers identifiés.", "",
             "| Crawler | Éditeur | Rôle | Requêtes | Pages | robots.txt | Statuts | Vérifiées | Usurpées | Non vérifiables |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for token, b in data["bots"].items():
        st = " ".join(f"{k}:{v}" for k, v in b["status"].items())
        lines.append(f"| {token} | {b['vendor']} | {b['role']} | {b['hits']} | {b['pages']} | {b['robots_txt']} | "
                     f"{st} | {b['verified']} | {b['spoofed']} | {b['unverifiable']} |")
    lines += ["", "## Constats", ""]
    if not data["findings"]:
        lines.append("Aucun.")
    for f in data["findings"]:
        lines.append(f"- **{f['code']}** [{f['label']}{', bloquant' if f['blocking'] else ''}] {f['detail']} "
                     f"(source : {f['source']})")
    lines += ["", "## Listes d'IP des fournisseurs", ""]
    lines += [f"- {u} : {s}" for u, s in data["range_lists"].items()] or ["- vérification désactivée"]
    lines += ["", "Les adresses IP ne sont jamais écrites : sources usurpées agrégées en /24 (IPv4) ou /48 (IPv6).",
              "Meta et Amazon ne publient pas de liste JSON (Amazon : pages HTML) : leurs requêtes restent « non vérifiables »."]
    return "\n".join(lines) + "\n"


def _sitemap_paths(args) -> list[str] | None:
    urls: list[str] = []
    if args.sitemap_urls:
        urls = [u.strip() for u in Path(args.sitemap_urls).read_text(encoding="utf-8").splitlines() if u.strip()]
    elif args.site:
        import robotstxt
        import sitemaps
        parts = urllib.parse.urlsplit(args.site)
        origin = f"{parts.scheme}://{parts.netloc}"
        declared = []
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{origin}/robots.txt",
                                                               headers={"User-Agent": USER_AGENT}), timeout=20) as r:
                declared = robotstxt.parse(r.read().decode("utf-8", errors="replace")).records("sitemap")
        except OSError:
            pass
        urls = sitemaps.discover(origin, declared).urls
    return [urllib.parse.urlsplit(u).path or "/" for u in urls] or None


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Crawlers de recherche et d'IA dans les journaux serveur.")
    p.add_argument("logs", nargs="+", help="Fichiers de journal (combined ou JSON lines, .gz accepté)")
    p.add_argument("--no-verify", action="store_true", help="Ne pas vérifier les IP (aucune requête réseau)")
    p.add_argument("--ranges-dir", type=Path, default=None, help="Listes JSON locales (nom de fichier = celui de l'URL)")
    p.add_argument("--site", default=None, help="Lire le sitemap du site pour la couverture de crawl")
    p.add_argument("--sitemap-urls", default=None, help="Fichier d'URLs du sitemap (une par ligne)")
    p.add_argument("--json", default=None)
    p.add_argument("--md", default=None)
    args = p.parse_args(argv)

    ranges, range_status = (None, {})
    if not args.no_verify:
        tokens = {c.token.lower() for c in _CATALOGUE}
        ranges, range_status = load_ranges(tokens, args.ranges_dir)
    result = analyze(read_lines(args.logs), ranges)
    if result["parsed"] == 0:
        print("Aucune ligne reconnue : format non pris en charge (combined ou JSON lines).")
        return 2
    fnd = findings(result, _sitemap_paths(args))
    data = to_json(result, fnd, range_status)
    md = render_md(data)
    print(md)
    if args.json:
        Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    return 1 if any(f["blocking"] for f in fnd) else 0


if __name__ == "__main__":
    sys.exit(main())
