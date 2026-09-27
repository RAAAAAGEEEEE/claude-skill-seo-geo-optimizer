#!/usr/bin/env python3
"""Extract the SEO-relevant signals of one HTML page, with the standard
library's HTML parser rather than regular expressions.

Why not regexes: attribute order varies between frameworks
(`<meta content=... name=description>` is valid), and frameworks such as
Next.js ship large inline scripts whose strings contain things that look like
tags. A regex audit reported both cases wrongly; a tokenizer does not.

Also records the redirect chain (a 307 on the home page is a finding, a
silently followed redirect is not) and the X-Robots-Tag header, since
`noindex` / `nosnippet` can live in HTTP headers as well as in the markup.

Used by generate_report.py. Stdlib only.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/2.0)"


class _SignalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.title: str | None = None
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.h1_count = 0
        self.jsonld_blocks: list[str] = []
        self.has_data_nosnippet = False
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_jsonld = False
        self._jsonld_parts: list[str] = []
        self._svg_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if "data-nosnippet" in a:
            self.has_data_nosnippet = True
        if tag == "svg":
            self._svg_depth += 1
        elif tag == "html" and self.html_lang is None:
            self.html_lang = a.get("lang") or None
        elif tag == "title" and self.title is None and self._svg_depth == 0:
            self._in_title = True
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)

    def handle_endtag(self, tag: str) -> None:
        if tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)
        elif tag == "title" and self._in_title:
            self._in_title = False
            self.title = "".join(self._title_parts).strip() or None
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld_blocks.append("".join(self._jsonld_parts))

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        elif self._in_jsonld:
            self._jsonld_parts.append(data)


@dataclass
class PageSignals:
    url: str
    final_url: str | None = None
    http_status: int | None = None
    redirects: list[tuple[int, str]] = field(default_factory=list)  # (status, target)
    x_robots_tag: str | None = None
    html_lang: str | None = None
    title: str | None = None
    description: str | None = None
    canonical: str | None = None
    robots_directives: list[str] = field(default_factory=list)  # meta robots + googlebot + header
    has_og_title: bool = False
    h1_count: int = 0
    jsonld_blocks: list[str] = field(default_factory=list)
    hreflang_links: list[tuple[str, str]] = field(default_factory=list)  # (lang, absolute href)
    has_data_nosnippet: bool = False
    error: str | None = None

    @property
    def noindex(self) -> bool:
        return any(d in ("noindex", "none") for d in self.robots_directives)

    @property
    def nosnippet(self) -> bool:
        """nosnippet or max-snippet:0 -- both keep the page out of text
        snippets and out of AI Overviews / AI Mode (Google preview controls)."""
        return any(d == "nosnippet" or d.replace(" ", "") == "max-snippet:0" for d in self.robots_directives)


class _RecordingRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        super().__init__()
        self.chain: list[tuple[int, str]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802 (stdlib signature)
        self.chain.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_VALUED_DIRECTIVES = ("max-snippet", "max-image-preview", "max-video-preview", "unavailable_after")


def _split_directives(value: str) -> list[str]:
    """Directives that apply to Google. "otherbot: noindex" (X-Robots-Tag
    form scoped to another crawler) is dropped; "googlebot: noindex" is kept."""
    out = []
    for part in value.split(","):
        part = part.strip().lower()
        if ":" in part and not part.startswith(_VALUED_DIRECTIVES):
            agent, _, rest = part.partition(":")
            if agent.strip() != "googlebot":
                continue
            part = rest.strip()
        if part:
            out.append(part)
    return out


def fetch_signals(url: str, timeout: float = 20.0, user_agent: str = USER_AGENT) -> PageSignals:
    signals = PageSignals(url=url)
    redirects = _RecordingRedirects()
    opener = urllib.request.build_opener(redirects)
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept-Language": "fr,en;q=0.8"})
    try:
        with opener.open(request, timeout=timeout) as resp:
            signals.http_status = resp.status
            signals.final_url = resp.geturl()
            signals.x_robots_tag = resp.headers.get("X-Robots-Tag")
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        signals.http_status = e.code
        signals.error = f"HTTP {e.code}"
        signals.redirects = redirects.chain
        return signals
    except Exception as e:  # DNS, TLS, timeout
        signals.error = str(e)
        return signals
    signals.redirects = redirects.chain
    parse_html(signals, html)
    return signals


def parse_html(signals: PageSignals, html: str) -> PageSignals:
    parser = _SignalParser()
    parser.feed(html)
    base = signals.final_url or signals.url

    signals.html_lang = parser.html_lang
    signals.title = parser.title
    signals.h1_count = parser.h1_count
    signals.jsonld_blocks = parser.jsonld_blocks
    signals.has_data_nosnippet = parser.has_data_nosnippet

    directives: list[str] = []
    for m in parser.meta:
        name = m.get("name", "").lower()
        prop = m.get("property", "").lower()
        if name == "description" and signals.description is None:
            signals.description = m.get("content", "").strip()
        elif name in ("robots", "googlebot"):
            directives += _split_directives(m.get("content", ""))
        if prop == "og:title":
            signals.has_og_title = True
    if signals.x_robots_tag:
        directives += _split_directives(signals.x_robots_tag)
    signals.robots_directives = directives

    for link in parser.links:
        rels = link.get("rel", "").lower().split()
        href = link.get("href", "")
        if "canonical" in rels and signals.canonical is None and href:
            signals.canonical = urljoin(base, href)
        if "alternate" in rels and link.get("hreflang") and href:
            signals.hreflang_links.append((link["hreflang"], urljoin(base, href)))
    return signals
