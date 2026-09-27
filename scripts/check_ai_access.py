#!/usr/bin/env python3
"""Verifie qu'une page est REELLEMENT accessible aux crawlers de recherche
et d'IA, en separant deux couches souvent confondues :

1. robots.txt autorise-t-il le crawler ? (declaratif, RFC 9309 applique
   strictement : groupes, plus long motif, jokers -- voir robotstxt.py)
2. Le serveur/CDN sert-il la page a une requete portant son user-agent ?
   (mesure, comparee a une requete navigateur de reference)

Verdicts par crawler :
- ok                 : robots autorise, page servie (200).
- blocked-by-robots  : robots.txt l'interdit (intention declaree).
- blocked-upstream   : robots autorise, mais 401/403/429/503 alors que la
                       reference navigateur recoit 200 -> regle CDN/WAF par
                       user-agent (cas Cloudflare, voir references/).
- robots-deny-served : robots interdit mais le serveur repond 200 (normal :
                       robots.txt n'est pas un controle d'acces).
- token-only         : jeton robots.txt sans user-agent propre
                       (Google-Extended, Applebot-Extended) : seul robots.txt
                       compte, aucun test HTTP n'a de sens.
- inconclusive       : la reference navigateur echoue elle-meme, ou erreur
                       reseau : on ne peut rien attribuer au crawler.

Limite a garder en tete : la requete part de cette machine, pas des IP du
fournisseur. Un CDN qui verifie les bots par IP (Cloudflare "verified bots")
peut traiter differemment le vrai crawler. Un 403 ici prouve une regle par
user-agent ; un 200 ne prouve pas que le vrai bot passe. Confirmer dans les
journaux serveur ou le tableau de bord du CDN.

Usage:
    python check_ai_access.py https://example.com/page [--json out.json] [--roles search,user,engine]

Code de sortie : 0 aucun blocage, 1 blocage detecte, 2 non concluant.
Aucune authentification. ~25 requetes (1 robots.txt, 1 reference, 1 par
crawler dote d'un user-agent). Catalogue : ai_bots.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import robotstxt  # noqa: E402
from ai_bots import AI_BOTS, CHECKED_ON, CITATION_ROLES  # noqa: E402

TIMEOUT = 20.0
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/140.0.0.0 Safari/537.36")
BLOCK_CODES = {401, 403, 406, 429, 451, 503}


@dataclass
class Probe:
    status: int | None
    error: str | None
    cdn: str | None
    mitigated: str | None


@dataclass
class BotResult:
    vendor: str
    token: str
    role: str
    robots_allows: bool | None
    http_status: int | None
    verdict: str
    note: str
    ua_documented: bool


def _detect_cdn(headers) -> str | None:
    server = (headers.get("Server") or "").lower()
    if "cloudflare" in server or headers.get("CF-RAY"):
        return "cloudflare"
    if headers.get("X-Served-By") and "cache" in (headers.get("X-Served-By") or "").lower():
        return "fastly"
    if "akamai" in server or headers.get("X-Akamai-Transformed"):
        return "akamai"
    if headers.get("X-Amz-Cf-Id"):
        return "cloudfront"
    return None


def probe(url: str, user_agent: str) -> Probe:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read(2048)
            return Probe(resp.status, None, _detect_cdn(resp.headers), resp.headers.get("cf-mitigated"))
    except urllib.error.HTTPError as e:
        return Probe(e.code, f"HTTP {e.code}", _detect_cdn(e.headers), e.headers.get("cf-mitigated"))
    except Exception as e:  # DNS, TLS, timeout
        return Probe(None, str(e), None, None)


def fetch_robots(origin: str) -> tuple[int | None, robotstxt.RobotsTxt | None, str | None]:
    url = f"{origin}/robots.txt"
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, robotstxt.parse(resp.read().decode("utf-8", errors="replace")), None
    except urllib.error.HTTPError as e:
        return e.code, None, f"HTTP {e.code}"
    except Exception as e:
        return None, None, str(e)


def _robots_verdict(robots_status: int | None, robots: robotstxt.RobotsTxt | None, token: str, path: str) -> bool | None:
    fallback = robotstxt.verdict_for_status(robots_status)
    if fallback == "allow-all":
        return True
    if fallback == "disallow-all":
        return False
    return robotstxt.is_allowed(robots, token, path) if robots else None


def check_site(url: str, roles: tuple[str, ...] | None = None, pause: float = 0.2) -> dict:
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")

    robots_status, robots, robots_err = fetch_robots(origin)
    baseline = probe(url, BROWSER_UA)
    baseline_ok = baseline.status == 200

    results: list[BotResult] = []
    for bot in AI_BOTS:
        if roles and bot.role not in roles:
            continue
        allowed = _robots_verdict(robots_status, robots, bot.robots_token, path)
        if bot.ua is None:
            results.append(BotResult(bot.vendor, bot.robots_token, bot.role, allowed, None, "token-only",
                                     bot.robots_note, bot.ua_documented))
            continue
        p = probe(url, bot.ua)
        time.sleep(pause)
        if p.status is None or not baseline_ok:
            verdict = "inconclusive"
            note = p.error or f"reference navigateur en echec (HTTP {baseline.status})"
        elif allowed is False:
            verdict = "robots-deny-served" if p.status == 200 else "blocked-by-robots"
            note = bot.robots_note
        elif p.status == 200:
            verdict, note = "ok", bot.robots_note
        elif p.status in BLOCK_CODES:
            verdict = "blocked-upstream"
            note = f"HTTP {p.status} pour ce user-agent, 200 pour un navigateur"
            if p.mitigated:
                note += f" (cf-mitigated: {p.mitigated})"
        else:
            verdict, note = "inconclusive", f"HTTP {p.status}"
        results.append(BotResult(bot.vendor, bot.robots_token, bot.role, allowed, p.status, verdict, note,
                                 bot.ua_documented))

    return {
        "url": url,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "catalog_checked_on": CHECKED_ON,
        "robots_txt": {
            "url": f"{origin}/robots.txt",
            "status": robots_status,
            "error": robots_err,
            "fallback": robotstxt.verdict_for_status(robots_status),
            "sitemaps": robots.records("sitemap") if robots else [],
            "license": robots.records("license") if robots else [],
            "content_signal": robots.records("content-signal") if robots else [],
            "content_usage": robots.records("content-usage") if robots else [],
        },
        "baseline": {"user_agent": BROWSER_UA, "http_status": baseline.status, "error": baseline.error, "cdn": baseline.cdn},
        "bots": [asdict(r) for r in results],
    }


def print_report(data: dict) -> int:
    r = data["robots_txt"]
    print(f"Cible : {data['url']}  ({data['checked_at'][:19]}Z, catalogue du {data['catalog_checked_on']})")
    print(f"robots.txt : HTTP {r['status']}"
          + (f" -> traite comme '{r['fallback']}' (RFC 9309)" if r["fallback"] else ""))
    for key, label in (("sitemaps", "Sitemap"), ("license", "License (RSL)"),
                       ("content_signal", "Content-Signal"), ("content_usage", "Content-Usage (aipref)")):
        for value in r[key]:
            print(f"  {label}: {value}")
    b = data["baseline"]
    print(f"Reference navigateur : HTTP {b['http_status'] or 'erreur'}" + (f", CDN : {b['cdn']}" if b["cdn"] else ""))
    print()
    print(f"{'Crawler':22s} {'Fournisseur':12s} {'Role':9s} {'robots':7s} {'HTTP':5s} Verdict")
    print("-" * 78)
    for bot in data["bots"]:
        robots_col = {True: "allow", False: "DENY", None: "?"}[bot["robots_allows"]]
        print(f"{bot['token']:22s} {bot['vendor']:12s} {bot['role']:9s} {robots_col:7s} "
              f"{str(bot['http_status'] or '-'):5s} {bot['verdict']}")
        if bot["note"]:
            print(f"  -> {bot['note']}")

    if data["baseline"]["http_status"] != 200:
        print()
        print(f"NON CONCLUANT : la page ne repond pas 200 a un navigateur (HTTP {b['http_status'] or 'erreur'}). "
              "Aucun verdict par crawler n'est attribuable ; relancer quand le site repond.")
        return 2

    upstream = [x["token"] for x in data["bots"] if x["verdict"] == "blocked-upstream"]
    citation_blocked = [x["token"] for x in data["bots"]
                        if x["role"] in CITATION_ROLES and x["verdict"] in ("blocked-upstream", "blocked-by-robots")]
    print()
    if upstream:
        print(f"ALERTE : {len(upstream)} crawler(s) autorise(s) par robots.txt mais refuse(s) par le serveur/CDN : "
              f"{', '.join(upstream)}")
        print("  Regle par user-agent probable (CDN/WAF). Voir references/cloudflare-ai-access.md.")
    if citation_blocked:
        print(f"IMPACT : {len(citation_blocked)} crawler(s) de recherche/citation bloque(s) : {', '.join(citation_blocked)}")
    if not upstream and not citation_blocked:
        print("Aucun blocage detecte sur les crawlers de recherche/citation (user-agents simules).")
    print("Rappel : test depuis cette machine, pas depuis les IP des fournisseurs ; confirmer dans les logs/CDN.")
    return 1 if (upstream or citation_blocked) else 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="Page a tester, ex: https://example.com/fr/produit")
    parser.add_argument("--json", dest="json_out", default=None, help="Ecrit le resultat brut en JSON")
    parser.add_argument("--roles", default=None,
                        help="Filtre de roles, ex: search,user,engine (defaut : tous)")
    args = parser.parse_args()

    roles = tuple(x.strip() for x in args.roles.split(",")) if args.roles else None
    data = check_site(args.url, roles=roles)
    exit_code = print_report(data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON ecrit : {args.json_out}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
