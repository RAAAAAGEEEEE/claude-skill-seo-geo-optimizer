#!/usr/bin/env python3
"""Discover and read a site's XML sitemaps (sitemap index, gzip, the
`Sitemap:` lines of robots.txt, /sitemap.xml as a fallback).

Returns every <url> entry with its <lastmod>, and the facts an audit needs:
which sitemaps were read, which failed, entries on a foreign host, lastmod
values that are all identical (a generation date, not a modification date)
or in the future. Rules: Google Search Central, "Build and submit a sitemap"
(updated 2026-07-08) -- see references/indexing-rules.md.

Stdlib only. GET requests to the audited site only.
"""

from __future__ import annotations

import gzip
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/2.1)"
MAX_SITEMAPS = 50
MAX_BYTES = 50 * 1024 * 1024  # protocol limit: 50 MB uncompressed per file


@dataclass
class SitemapEntry:
    loc: str
    lastmod: str | None
    sitemap: str


@dataclass
class SitemapSet:
    declared_in_robots: list[str] = field(default_factory=list)
    read: list[dict] = field(default_factory=list)  # {url, status, kind, count, error}
    entries: list[SitemapEntry] = field(default_factory=list)

    @property
    def urls(self) -> list[str]:
        seen: dict[str, None] = {}
        for e in self.entries:
            seen.setdefault(e.loc, None)
        return list(seen)

    def lastmod_of(self, url: str) -> str | None:
        for e in self.entries:
            if e.loc == url and e.lastmod:
                return e.lastmod
        return None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_sitemap_xml(data: bytes) -> tuple[str, list[tuple[str, str | None]]]:
    """Returns (kind, [(loc, lastmod)]) where kind is 'index' or 'urlset'.
    Namespace-agnostic. Raises ValueError on unreadable XML."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise ValueError(f"XML illisible : {e}") from e
    kind = "index" if _local(root.tag) == "sitemapindex" else "urlset"
    child_tag = "sitemap" if kind == "index" else "url"
    out: list[tuple[str, str | None]] = []
    for node in root:
        if _local(node.tag) != child_tag:
            continue
        loc = lastmod = None
        for sub in node:
            name = _local(sub.tag)
            if name == "loc" and sub.text:
                loc = sub.text.strip()
            elif name == "lastmod" and sub.text:
                lastmod = sub.text.strip()
        if loc:
            out.append((loc, lastmod))
    return kind, out


def _get(url: str, timeout: float) -> tuple[int | None, bytes | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(MAX_BYTES), None
    except urllib.error.HTTPError as e:
        return e.code, None, f"HTTP {e.code}"
    except Exception as e:  # DNS, TLS, timeout
        return None, None, str(e)


def discover(origin: str, robots_sitemaps: list[str], timeout: float = 20.0, fetch=_get) -> SitemapSet:
    """Reads robots.txt-declared sitemaps, else /sitemap.xml; follows indexes."""
    result = SitemapSet(declared_in_robots=list(robots_sitemaps))
    queue = list(robots_sitemaps) or [f"{origin}/sitemap.xml"]
    seen: set[str] = set()
    while queue and len(seen) < MAX_SITEMAPS:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        status, body, error = fetch(url, timeout)
        record = {"url": url, "status": status, "kind": None, "count": 0, "error": error}
        result.read.append(record)
        if body is None:
            continue
        try:
            kind, items = parse_sitemap_xml(body)
        except (ValueError, OSError) as e:
            record["error"] = str(e)
            continue
        record["kind"], record["count"] = kind, len(items)
        if kind == "index":
            queue += [loc for loc, _ in items]
        else:
            result.entries += [SitemapEntry(loc, lastmod, url) for loc, lastmod in items]
    return result


def _parse_date(value: str) -> datetime | None:
    v = value.strip().replace("Z", "+00:00")
    for candidate in (v, v[:10]):
        try:
            d = datetime.fromisoformat(candidate)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def lastmod_findings(sitemaps: SitemapSet, now: datetime | None = None) -> dict:
    """{uniform: bool, uniform_value, future: [urls], with_lastmod, total}."""
    now = now or datetime.now(timezone.utc)
    values = [e.lastmod for e in sitemaps.entries if e.lastmod]
    days = {v[:10] for v in values}
    future = [e.loc for e in sitemaps.entries
              if e.lastmod and (d := _parse_date(e.lastmod)) and (d - now).days >= 1]
    return {
        "total": len(sitemaps.entries),
        "with_lastmod": len(values),
        # Uniform only means something with enough URLs.
        "uniform": len(values) >= 5 and len(days) == 1,
        "uniform_value": next(iter(days)) if len(days) == 1 else None,
        "future": future,
    }


def foreign_entries(sitemaps: SitemapSet, host: str) -> list[str]:
    return [u for u in sitemaps.urls if urllib.parse.urlparse(u).netloc.lower() != host.lower()]


def build_proposed_sitemap(entries: list[tuple[str, str | None]]) -> str:
    """Minimal urlset for the URLs verified indexable; lastmod only when known."""
    from xml.sax.saxutils import escape

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in entries:
        lines.append(f"  <url><loc>{escape(loc)}</loc>" + (f"<lastmod>{escape(lastmod)}</lastmod>" if lastmod else "")
                     + "</url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"
