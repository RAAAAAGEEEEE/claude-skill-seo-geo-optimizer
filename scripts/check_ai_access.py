#!/usr/bin/env python3
"""Verifie qu'un site est REELLEMENT accessible aux crawlers IA.

Deux couches distinctes, souvent confondues :
1. `robots.txt` autorise-t-il le bot ? (declaratif, ce que le site dit)
2. Le serveur/CDN sert-il vraiment la page a ce bot ? (reel, ce qui se passe)

Un site peut avoir un robots.txt parfaitement permissif ET renvoyer 403 aux
bots IA parce que le CDN (Cloudflare, Akamai, Fastly...) les bloque en amont.
Ce script detecte ce cas -- invisible avec un simple `curl` classique.

Contexte 2026 : Cloudflare bascule les nouveaux sites et les plans gratuits
vers un blocage par defaut des crawlers d'entrainement/agents IA a partir du
15 septembre 2026 (voir references/cloudflare-ai-access.md). Un site qui
depend de la visibilite dans les moteurs generatifs doit verifier son etat
reel, pas seulement son robots.txt.

Usage:
    python check_ai_access.py https://example.com [--json out.json]

Aucune authentification requise. Fait 1 requete par bot teste (~12 requetes).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict

# User-agents reels des principaux crawlers IA, groupes par fonction.
# "search" = utilise au moment de la requete pour citer une source (impact
# direct sur la visibilite GEO). "training" = alimente le modele (impact
# indirect, long terme).
AI_BOTS = [
    ("OAI-SearchBot", "search", "OpenAI / ChatGPT Search"),
    ("ChatGPT-User", "search", "OpenAI / navigation utilisateur ChatGPT"),
    ("GPTBot", "training", "OpenAI / entrainement"),
    ("Claude-SearchBot", "search", "Anthropic / recherche"),
    ("Claude-User", "search", "Anthropic / navigation utilisateur"),
    ("ClaudeBot", "training", "Anthropic / entrainement"),
    ("PerplexityBot", "search", "Perplexity / index"),
    ("Perplexity-User", "search", "Perplexity / navigation utilisateur"),
    ("Google-Extended", "training", "Google / Gemini + AI Overviews (grounding)"),
    ("Applebot-Extended", "training", "Apple Intelligence"),
    ("Googlebot", "search", "Google Search classique (reference de controle)"),
    ("Bingbot", "search", "Bing + partenaires (reference de controle)"),
]

TIMEOUT = 20.0


@dataclass
class BotResult:
    user_agent: str
    role: str
    label: str
    robots_allows: bool | None  # None = robots.txt illisible
    http_status: int | None
    served: bool
    note: str = ""


def fetch(url: str, user_agent: str) -> tuple[int | None, str | None, str]:
    """Retourne (status_code, body, error). Ne leve jamais."""
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as e:
        return e.code, None, f"HTTP {e.code}"
    except Exception as e:  # DNS, TLS, timeout...
        return None, None, str(e)


def parse_robots(robots_txt: str) -> dict[str, list[tuple[str, str]]]:
    """Parse minimaliste : {user_agent_lower: [(directive, path), ...]}.

    Suffisant pour un diagnostic Allow/Disallow simple. Ne gere pas les
    subtilites de priorite par longueur de pattern du protocole complet --
    en cas de robots.txt complexe, verifier manuellement.
    """
    rules: dict[str, list[tuple[str, str]]] = {}
    current_agents: list[str] = []
    for raw_line in robots_txt.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()
        if field == "user-agent":
            current_agents.append(value.lower())
            rules.setdefault(value.lower(), [])
        elif field in ("allow", "disallow"):
            for agent in current_agents or ["*"]:
                rules.setdefault(agent, []).append((field, value))
        else:
            current_agents = []
    return rules


def robots_allows_path(rules: dict[str, list[tuple[str, str]]], user_agent: str, path: str = "/") -> bool:
    """Applique les regles du groupe le plus specifique (le bot, sinon '*')."""
    group = rules.get(user_agent.lower())
    if group is None:
        group = rules.get("*", [])

    best_match: tuple[int, bool] | None = None  # (longueur du pattern, autorise)
    for directive, pattern in group:
        if pattern == "":
            # "Disallow:" vide = tout autoriser
            candidate = (0, True) if directive == "disallow" else (0, True)
        elif path.startswith(pattern.rstrip("*")):
            candidate = (len(pattern), directive == "allow")
        else:
            continue
        if best_match is None or candidate[0] > best_match[0]:
            best_match = candidate

    return True if best_match is None else best_match[1]


def check_site(base_url: str) -> dict:
    parsed = urllib.parse.urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{origin}/robots.txt"

    robots_status, robots_body, robots_err = fetch(robots_url, "Mozilla/5.0 (seo-geo-optimizer)")
    rules = parse_robots(robots_body) if robots_body else {}
    robots_readable = bool(robots_body)

    results: list[BotResult] = []
    for ua, role, label in AI_BOTS:
        allowed = robots_allows_path(rules, ua) if robots_readable else None
        status, _body, err = fetch(base_url, ua)
        served = status == 200
        note = ""
        if allowed and not served:
            note = "BLOQUE EN AMONT (CDN/pare-feu) malgre un robots.txt permissif"
        elif allowed is False and served:
            note = "robots.txt interdit mais le serveur repond quand meme (les bots respectueux s'abstiendront)"
        elif err and not served:
            note = err
        results.append(
            BotResult(
                user_agent=ua, role=role, label=label,
                robots_allows=allowed, http_status=status, served=served, note=note,
            )
        )

    return {
        "url": base_url,
        "robots_txt": {
            "url": robots_url,
            "status": robots_status,
            "readable": robots_readable,
            "error": robots_err or None,
        },
        "bots": [asdict(r) for r in results],
    }


def print_report(data: dict) -> int:
    print(f"Cible : {data['url']}")
    r = data["robots_txt"]
    print(f"robots.txt : HTTP {r['status']} ({'lisible' if r['readable'] else 'ILLISIBLE'})")
    print()
    print(f"{'Bot':22s} {'Role':9s} {'robots':8s} {'HTTP':6s} {'Servi'}")
    print("-" * 62)

    blocked_search = []
    silent_blocks = []
    for b in data["bots"]:
        robots_txt_col = {True: "allow", False: "DENY", None: "?"}[b["robots_allows"]]
        status_col = str(b["http_status"]) if b["http_status"] else "err"
        print(f"{b['user_agent']:22s} {b['role']:9s} {robots_txt_col:8s} {status_col:6s} {'oui' if b['served'] else 'NON'}")
        if b["note"]:
            print(f"  -> {b['note']}")
        if b["role"] == "search" and not b["served"]:
            blocked_search.append(b["user_agent"])
        if b["robots_allows"] and not b["served"]:
            silent_blocks.append(b["user_agent"])

    print()
    if silent_blocks:
        print(f"ALERTE : {len(silent_blocks)} bot(s) autorise(s) par robots.txt mais bloque(s) en amont :")
        print(f"  {', '.join(silent_blocks)}")
        print("  Cause probable : regle CDN/WAF (Cloudflare, Akamai...) devant le serveur.")
        print("  Voir references/cloudflare-ai-access.md")
    if blocked_search:
        print(f"IMPACT GEO : {len(blocked_search)} bot(s) de RECHERCHE inaccessible(s) -- "
              f"le site ne peut pas etre cite par ces moteurs : {', '.join(blocked_search)}")
    if not silent_blocks and not blocked_search:
        print("Aucun blocage detecte : tous les crawlers IA testes accedent au site.")

    return 1 if (silent_blocks or blocked_search) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="URL a tester, ex: https://example.com")
    parser.add_argument("--json", dest="json_out", default=None, help="Ecrit le resultat brut en JSON")
    args = parser.parse_args()

    data = check_site(args.url)
    exit_code = print_report(data)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nJSON ecrit : {args.json_out}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
