#!/usr/bin/env python3
"""Catalog of search and AI crawlers: robots.txt token, role, user-agent.

Single source of truth for check_ai_access.py and generate_sitemap.py. The
human-readable version, with sources and evidence labels, is
references/ai-crawlers.md -- update both together.

Roles:
- engine   : classic search engine crawler whose index also feeds AI answers
             (Googlebot -> AI Overviews / AI Mode, bingbot -> Copilot).
- search   : crawler that builds an AI assistant's search index (citations).
- user     : fetcher triggered by a user's request. Several vendors document
             that these may ignore robots.txt (see `robots_note`).
- training : crawler whose data trains models. Blocking it does not remove a
             site from the vendor's search answers.
- token    : robots.txt control token only. No request ever carries it as a
             user-agent, so an HTTP test with it is meaningless.

`ua` is the documented user-agent string when the vendor publishes one
(`ua_documented=True`); otherwise a string built around the token, which is
what CDN/WAF rules match on. Where the vendor writes a Chrome version as
W.X.Y.Z, a current-looking version is filled in. Checked 2026-09-27 against
the vendors' pages.
"""

from __future__ import annotations

from dataclasses import dataclass

CHECKED_ON = "2026-09-27"


@dataclass(frozen=True)
class Bot:
    vendor: str
    robots_token: str
    role: str
    ua: str | None
    ua_documented: bool
    doc: str
    robots_note: str = ""


def _generic(token: str, version: str = "1.0", info_url: str = "") -> str:
    suffix = f"; +{info_url}" if info_url else ""
    return f"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; {token}/{version}{suffix})"


_MISTRAL = "https://docs.mistral.ai/robots"


AI_BOTS: list[Bot] = [
    # OpenAI -- https://developers.openai.com/api/docs/bots
    Bot("OpenAI", "OAI-SearchBot", "search",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.4; +https://openai.com/searchbot",
        True, "https://developers.openai.com/api/docs/bots", "changement pris en compte en ~24 h"),
    Bot("OpenAI", "ChatGPT-User", "user",
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
        True, "https://developers.openai.com/api/docs/bots", "robots.txt pas garanti (requete de l'utilisateur)"),
    Bot("OpenAI", "GPTBot", "training",
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.4; +https://openai.com/gptbot",
        True, "https://developers.openai.com/api/docs/bots"),
    # Anthropic -- https://support.claude.com/en/articles/8896518 (UA strings not published)
    Bot("Anthropic", "Claude-SearchBot", "search", _generic("Claude-SearchBot"), False,
        "https://support.claude.com/en/articles/8896518"),
    Bot("Anthropic", "Claude-User", "user", _generic("Claude-User"), False,
        "https://support.claude.com/en/articles/8896518", "respecte robots.txt (doc Anthropic)"),
    Bot("Anthropic", "ClaudeBot", "training", _generic("ClaudeBot"), False,
        "https://support.claude.com/en/articles/8896518"),
    # Perplexity -- https://docs.perplexity.ai/guides/bots
    Bot("Perplexity", "PerplexityBot", "search",
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
        True, "https://docs.perplexity.ai/guides/bots"),
    Bot("Perplexity", "Perplexity-User", "user",
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)",
        True, "https://docs.perplexity.ai/guides/bots", "ignore generalement robots.txt (doc Perplexity)"),
    # Google -- https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers
    Bot("Google", "Googlebot", "engine",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        True, "https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers",
        "alimente Search, AI Overviews et AI Mode"),
    Bot("Google", "Google-Agent", "user",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko; compatible; Google-Agent; "
        "+https://developers.google.com/crawling/docs/crawlers-fetchers/google-agent) Chrome/140.0.0.0 Safari/537.36",
        True, "https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers",
        "ignore generalement robots.txt (fetcher declenche par l'utilisateur)"),
    Bot("Google", "Google-Extended", "token", None, True,
        "https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers",
        "jeton seul : entrainement Gemini + grounding Gemini Apps/Vertex AI ; sans effet sur Search ni AI Overviews"),
    # Microsoft -- bingbot grounds Copilot
    Bot("Microsoft", "bingbot", "engine",
        "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) "
        "Chrome/140.0.0.0 Safari/537.36",
        True, "https://blogs.bing.com/webmaster/april-2022/Announcing-user-agent-change-for-Bing-crawler-bingbot",
        "alimente Bing et le grounding de Copilot ; controle IA via NOCACHE/NOARCHIVE"),
    # Apple -- https://support.apple.com/en-us/119829
    Bot("Apple", "Applebot", "engine",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)",
        True, "https://support.apple.com/en-us/119829", "suit les regles Googlebot si Applebot n'est pas nomme"),
    Bot("Apple", "Applebot-Extended", "token", None, True, "https://support.apple.com/en-us/119829",
        "jeton seul : entrainement des modeles Apple ; ne crawle pas"),
    # Mistral -- https://docs.mistral.ai/robots
    Bot("Mistral", "MistralAI-Index", "search", _generic("MistralAI-Index", info_url=_MISTRAL),
        True, "https://docs.mistral.ai/robots"),
    Bot("Mistral", "MistralAI-User", "user", _generic("MistralAI-User", info_url=_MISTRAL),
        True, "https://docs.mistral.ai/robots", "respecte robots.txt (doc Mistral)"),
    Bot("Mistral", "MistralAI-Training", "training", _generic("MistralAI-Training", info_url=_MISTRAL),
        True, "https://docs.mistral.ai/robots"),
    # Meta -- https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/
    Bot("Meta", "meta-webindexer", "search",
        "meta-webindexer/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/web-crawlers)",
        True, "https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/"),
    Bot("Meta", "meta-externalfetcher", "user",
        "meta-externalfetcher/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/web-crawlers)",
        True, "https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/", "peut ignorer robots.txt"),
    Bot("Meta", "meta-externalagent", "training",
        "meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/web-crawlers)",
        True, "https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/", "entrainement et indexation"),
    # Amazon -- https://developer.amazon.com/amazonbot
    Bot("Amazon", "Amzn-SearchBot", "search", _generic("Amzn-SearchBot", "0.1"), False, "https://developer.amazon.com/amazonbot"),
    Bot("Amazon", "Amzn-User", "user", _generic("Amzn-User", "0.1"), False, "https://developer.amazon.com/amazonbot",
        "peut ne pas suivre toutes les directives"),
    Bot("Amazon", "Amazonbot", "training", _generic("Amazonbot", "0.1"), False, "https://developer.amazon.com/amazonbot",
        "peut servir a entrainer des modeles Amazon ; ignore Crawl-delay"),
    # DuckDuckGo, Common Crawl
    Bot("DuckDuckGo", "DuckAssistBot", "search", "DuckAssistBot/1.2; (+http://duckduckgo.com/duckassistbot.html)",
        True, "https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot", "blocage effectif sous 72 h"),
    Bot("Common Crawl", "CCBot", "training", "CCBot/2.0 (https://commoncrawl.org/faq/)", True,
        "https://commoncrawl.org/ccbot", "corpus ouvert, massivement reutilise pour l'entrainement"),
]

CITATION_ROLES = ("engine", "search", "user")


def by_token(token: str) -> Bot | None:
    token = token.lower()
    return next((b for b in AI_BOTS if b.robots_token.lower() == token), None)
