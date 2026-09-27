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

Since 2.1.0 it also records every `<a>` element (resolved href, anchor text,
rel, and the page zone it sits in) and a visible word count, which the
internal-linking analysis (linkgraph.py) needs. Zone of a link:
- "main"        : inside <main> / <article> (or role=main) and not inside a
                  <nav>/<aside> -- a contextual link in the body text;
- "boilerplate" : inside <nav>, <aside>, or a <header>/<footer> that is not
                  part of the main content (and the equivalent ARIA roles);
- "unknown"     : no such landmark encloses the link.

Used by generate_report.py and run_audit.py. Stdlib only.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/2.1)"

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source",
         "track", "wbr"}
_LANDMARK_TAGS = {"nav": "nav", "aside": "aside", "header": "header", "footer": "footer", "main": "main",
                  "article": "main"}
_LANDMARK_ROLES = {"navigation": "nav", "complementary": "aside", "banner": "header", "contentinfo": "footer",
                   "main": "main"}
_NO_TEXT = {"script", "style", "noscript", "template"}


def zone_of(landmarks: list[str]) -> str:
    """Zone of an element from the landmarks that enclose it."""
    if not landmarks:
        return "unknown"
    if "nav" in landmarks or "aside" in landmarks:
        return "boilerplate"
    if "main" in landmarks:
        return "main"  # a header/footer inside an article is part of the content
    return "boilerplate"  # page-level header/footer


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
        # Open-element stack: (tag, landmark or None). Void elements are never pushed.
        self._stack: list[tuple[str, str | None]] = []
        self._skip_text = 0
        self._anchor: dict | None = None
        self.anchors: list[dict] = []
        self.words_total = 0
        self.words_main = 0
        self.has_main_landmark = False

    def _landmarks(self) -> list[str]:
        return [lm for _tag, lm in self._stack if lm]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if "data-nosnippet" in a:
            self.has_data_nosnippet = True
        if tag not in _VOID:
            landmark = _LANDMARK_TAGS.get(tag) or _LANDMARK_ROLES.get(a.get("role", "").strip().lower())
            if landmark == "main":
                self.has_main_landmark = True
            self._stack.append((tag, landmark))
        if tag in _NO_TEXT:
            self._skip_text += 1
        if tag == "a":
            if self._anchor is not None:  # unclosed <a>: close the previous one
                self._close_anchor()
            href = dict(attrs).get("href")  # None when the attribute is absent
            self._anchor = {"href": href, "rel": a.get("rel", "").lower(), "text": [],
                            "label": a.get("aria-label", "") or a.get("title", ""),
                            "zone": zone_of(self._landmarks())}
        elif tag == "img" and self._anchor is not None and a.get("alt"):
            self._anchor["text"].append(a["alt"])
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
        if tag not in _VOID:
            self._pop(tag)
        if tag in _NO_TEXT:
            self._skip_text = max(0, self._skip_text - 1)
        if tag == "a" and self._anchor is not None:
            self._close_anchor()
        if tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)

    def _pop(self, tag: str) -> None:
        """Close `tag` and anything left open inside it; ignore a stray end tag."""
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                return

    def _close_anchor(self) -> None:
        a = self._anchor
        self._anchor = None
        if a is None:
            return
        text = " ".join(" ".join(a["text"]).split())
        self.anchors.append({"href": a["href"], "rel": a["rel"], "zone": a["zone"],
                             "text": text or " ".join(a["label"].split())})

    def handle_endtag(self, tag: str) -> None:
        if tag not in _VOID:
            self._pop(tag)
        if tag in _NO_TEXT:
            self._skip_text = max(0, self._skip_text - 1)
        if tag == "a" and self._anchor is not None:
            self._close_anchor()
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
        elif self._skip_text == 0 and self._svg_depth == 0:
            n = len(data.split())
            if n:
                self.words_total += n
                if zone_of(self._landmarks()) == "main":
                    self.words_main += n
                if self._anchor is not None:
                    self._anchor["text"].append(data)

    def close(self) -> None:
        super().close()
        if self._anchor is not None:
            self._close_anchor()


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
    # {"href": absolute URL without fragment, or None if not crawlable, "raw_href", "text", "rel", "zone"}
    anchors: list[dict] = field(default_factory=list)
    word_count: int = 0  # visible words on the page (scripts, styles excluded)
    main_word_count: int | None = None  # words inside <main>/<article>; None without such a landmark
    content_type: str | None = None
    error: str | None = None

    @property
    def noindex(self) -> bool:
        return any(d in ("noindex", "none") for d in self.robots_directives)

    @property
    def nosnippet(self) -> bool:
        """nosnippet or max-snippet:0 -- both keep the page out of text
        snippets and out of AI Overviews / AI Mode (Google preview controls)."""
        return any(d == "nosnippet" or d.replace(" ", "") == "max-snippet:0" for d in self.robots_directives)

    @property
    def is_html(self) -> bool:
        return self.content_type is None or "html" in self.content_type.lower()


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


MAX_HTML_BYTES = 5 * 1024 * 1024  # Googlebot reads the first 2 MB of an HTML file; keep a margin


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
            signals.content_type = resp.headers.get("Content-Type")
            signals.redirects = redirects.chain
            if not signals.is_html:
                return signals  # PDF, image, feed...: nothing to parse
            html = resp.read(MAX_HTML_BYTES).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        signals.http_status = e.code
        signals.error = f"HTTP {e.code}"
        signals.redirects = redirects.chain
        return signals
    except Exception as e:  # DNS, TLS, timeout
        signals.error = str(e)
        return signals
    parse_html(signals, html)
    return signals


def parse_html(signals: PageSignals, html: str) -> PageSignals:
    parser = _SignalParser()
    parser.feed(html)
    parser.close()
    base = signals.final_url or signals.url

    signals.html_lang = parser.html_lang
    signals.title = parser.title
    signals.h1_count = parser.h1_count
    signals.jsonld_blocks = parser.jsonld_blocks
    signals.has_data_nosnippet = parser.has_data_nosnippet
    signals.word_count = parser.words_total
    signals.main_word_count = parser.words_main if parser.has_main_landmark else None

    signals.anchors = []
    for a in parser.anchors:
        raw = a["href"]
        href = (raw or "").strip()
        # Google follows <a href> only; javascript: and bare fragments are not links to a page.
        crawlable = raw is not None and bool(href) and not href.lower().startswith(("javascript:", "#"))
        signals.anchors.append({
            "href": urljoin(base, href).split("#", 1)[0] if crawlable else None,
            "raw_href": raw,
            "text": a["text"],
            "rel": a["rel"],
            "zone": a["zone"],
        })

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
