#!/usr/bin/env python3
"""Glossary / lexicon automation: build, audit, and link a site's glossary.

Three sub-commands, stdlib only:

  build    Terms file (CSV or JSON, the site's own data) -> an HTML <dl>
           fragment and the matching DefinedTermSet JSON-LD. Both come from
           the same rows, so the markup always describes visible text
           (Google's structured-data guidelines). Rows with no definition,
           duplicates, or very short definitions are reported, never filled
           in. Nothing is invented.

  audit    A live glossary page (one page with anchors, or a hub linking to
           one page per term, the latter with --term-links REGEX):
             - terms found (DefinedTerm JSON-LD, <dfn>, <dt>, headings with id);
             - JSON-LD terms whose name is not visible on the page;
             - DefinedTerm url / @id fragments that point to no id on the page;
             - duplicate terms, very short definitions (heuristic);
           and, with --site, a crawl of the sitemap (robots.txt respected):
             - pages that mention a term in their body text but have no link
               to its definition (internal-linking opportunities, first
               mention only -- suggestions, never inserted automatically);
             - terms mentioned nowhere else on the site.

  suggest  Crawl a site and list candidate terms: acronyms and <abbr>/<dfn>
           texts used on several pages, minus those already in the glossary.

Evidence (see references/glossary.md): markup must match visible content
(ESTABLISHED, Google); descriptive internal links (ESTABLISHED, Google);
DefinedTerm gives no Google rich result (ESTABLISHED, absent from the gallery);
thresholds such as "definition under 12 words" are heuristics (CLAIMED).

Usage:
    python glossary_check.py build --terms terms.csv --set-name "Lexique" \\
        --set-url https://example.com/fr/lexique --lang fr --out-dir out/
    python glossary_check.py audit --url https://example.com/fr/lexique \\
        [--term-links '/fr/lexique/'] [--site https://example.com --max-pages 40] [--json out.json]
    python glossary_check.py suggest --site https://example.com [--glossary URL]

Terms file columns (CSV header or JSON keys): term (required), definition
(required), slug, url, same_as (| separated), code, alternate_names (| sep.).

Exit codes: 0 ok, 1 findings that break a rule labelled ESTABLISHED
(invisible markup, broken anchor, missing definition), 2 page unreachable.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import robotstxt  # noqa: E402
import sitemaps as sitemaps_mod  # noqa: E402

USER_AGENT = "Mozilla/5.0 (compatible; seo-geo-optimizer-audit/2.3)"
AUDIT_TOKEN = "seo-geo-optimizer-audit"
MIN_DEF_WORDS = 12  # heuristic (CLAIMED): below this a definition rarely stands on its own
MAX_BYTES = 5 * 1024 * 1024

# Tokens that look like acronyms but are not domain vocabulary.
ACRONYM_STOP = {"FR", "EN", "DE", "ES", "IT", "UE", "EU", "USA", "UK", "OK", "PDF", "HTML", "CSS", "URL", "FAQ",
                "RSS", "API", "CEO", "TV", "SAS", "SARL", "TVA", "CGU", "CGV", "RGPD", "GDPR", "HT", "TTC",
                "NB", "PS", "AM", "PM", "ID", "QR", "SEO", "JSON", "XML", "HTTP", "HTTPS", "WWW", "CTA",
                "CC", "BY", "SA", "NC", "ND"}  # Creative Commons licence tokens


# --------------------------------------------------------------------------- text helpers

def norm(text: str) -> str:
    """Lowercase, accents stripped, spaces collapsed: for comparisons only."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", norm(text)).strip("-") or "terme"


def words(text: str) -> int:
    return len(re.findall(r"\w+", text))


def term_pattern(term: str) -> re.Pattern[str]:
    """Whole-word, case- and accent-insensitive match on normalised text,
    with an optional plural s/x."""
    t = re.escape(norm(term))
    return re.compile(rf"(?<!\w){t}(?:s|x)?(?!\w)")


# --------------------------------------------------------------------------- build

@dataclass
class Term:
    term: str
    definition: str
    slug: str = ""
    url: str = ""
    same_as: list[str] = field(default_factory=list)
    code: str = ""
    alternate_names: list[str] = field(default_factory=list)


def _split(value) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in str(value or "").split("|") if v.strip()]


def load_terms(path: Path) -> list[Term]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        rows = json.loads(text)
        if isinstance(rows, dict):
            rows = rows.get("terms", [])
    else:
        rows = list(csv.DictReader(text.splitlines()))
    out = []
    for r in rows:
        r = {str(k).strip().lower(): v for k, v in r.items() if k is not None}
        out.append(Term(term=str(r.get("term") or "").strip(), definition=str(r.get("definition") or "").strip(),
                        slug=str(r.get("slug") or "").strip(), url=str(r.get("url") or "").strip(),
                        same_as=_split(r.get("same_as")), code=str(r.get("code") or "").strip(),
                        alternate_names=_split(r.get("alternate_names"))))
    return out


def check_terms(terms: list[Term], min_words: int = MIN_DEF_WORDS) -> list[dict]:
    issues = []
    seen: dict[str, str] = {}
    slugs: dict[str, str] = {}
    for t in terms:
        if not t.term:
            issues.append({"code": "term-missing-name", "label": "ESTABLISHED", "blocking": True,
                           "detail": f"ligne sans terme (définition : {t.definition[:40]!r})"})
            continue
        if not t.definition:
            issues.append({"code": "term-missing-definition", "label": "ESTABLISHED", "blocking": True,
                           "detail": f"{t.term} : aucune définition (ne rien générer à la place)"})
        elif words(t.definition) < min_words:
            issues.append({"code": "definition-short", "label": "CLAIMED", "blocking": False,
                           "detail": f"{t.term} : {words(t.definition)} mot(s) (< {min_words}, heuristique)"})
        key = norm(t.term)
        if key in seen:
            issues.append({"code": "term-duplicate", "label": "ESTABLISHED", "blocking": True,
                           "detail": f"{t.term} : en double (déjà « {seen[key]} »)"})
        seen.setdefault(key, t.term)
        slug = t.slug or slugify(t.term)
        if slug in slugs and slugs[slug] != key:
            issues.append({"code": "slug-collision", "label": "ESTABLISHED", "blocking": True,
                           "detail": f"{t.term} : ancre #{slug} déjà prise par « {slugs[slug]} »"})
        slugs.setdefault(slug, key)
    return issues


def usable(terms: list[Term]) -> list[Term]:
    """Rows that can be published: a name and a definition, first occurrence
    of each term and of each anchor only (check_terms reports the rest)."""
    seen, slugs, out = set(), set(), []
    for t in terms:
        key, slug = norm(t.term), t.slug or slugify(t.term)
        if t.term and t.definition and key not in seen and slug not in slugs:
            seen.add(key)
            slugs.add(slug)
            out.append(t)
    return out


def term_url(t: Term, set_url: str) -> str:
    return t.url or f"{set_url}#{t.slug or slugify(t.term)}"


def build_jsonld(terms: list[Term], set_name: str, set_url: str, lang: str | None = None,
                 description: str | None = None) -> dict:
    set_id = f"{set_url}#lexique"
    items = []
    for t in usable(terms):
        node = {"@type": "DefinedTerm", "@id": term_url(t, set_url), "name": t.term, "description": t.definition,
                "url": term_url(t, set_url), "inDefinedTermSet": {"@id": set_id}}
        if t.code:
            node["termCode"] = t.code
        if t.alternate_names:
            node["alternateName"] = t.alternate_names
        if t.same_as:
            node["sameAs"] = t.same_as
        items.append(node)
    data = {"@context": "https://schema.org", "@type": "DefinedTermSet", "@id": set_id, "name": set_name,
            "url": set_url, "hasDefinedTerm": items}
    if lang:
        data["inLanguage"] = lang
    if description:
        data["description"] = description
    return data


def build_html(terms: list[Term], set_url: str) -> str:
    """<dl> fragment: one <dt id> per term, the term wrapped in <dfn>. Terms
    with their own page get a link to it."""
    lines = ['<dl class="glossary">']
    for t in sorted(usable(terms), key=lambda x: norm(x.term)):
        slug = t.slug or slugify(t.term)
        label = f"<dfn>{html.escape(t.term, quote=False)}</dfn>"
        if t.url and not t.url.startswith(f"{set_url}#"):
            label = f'<a href="{html.escape(t.url)}">{label}</a>'
        lines.append(f'  <dt id="{html.escape(slug)}">{label}</dt>')
        lines.append(f"  <dd>{html.escape(t.definition, quote=False)}</dd>")
    lines.append("</dl>")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- page parsing

_BOILER = {"nav", "header", "footer", "aside"}
_SKIP = {"script", "style", "noscript", "template", "svg"}
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track",
         "wbr"}


class _GlossaryParser(HTMLParser):
    """Body text (split main vs whole), ids, links with fragments, glossary
    markers (<dfn>, <dt>, <abbr>, headings with id) and JSON-LD blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict]] = []
        self.ids: set[str] = set()
        self.links: list[dict] = []
        self.main_text: list[str] = []
        self.body_text: list[str] = []
        self.has_main = False
        self.markers: list[dict] = []  # {"kind", "text", "id"}
        self.abbrs: list[str] = []
        self.jsonld: list[str] = []
        self._capture: list[dict] = []  # open markers being filled
        self._link: dict | None = None
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []

    def _inside(self, names: set[str]) -> bool:
        return any(tag in names for tag, _ in self.stack)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "script" and "ld+json" in a.get("type", "").lower():
            self._in_jsonld, self._jsonld_buf = True, []
        if tag in ("main", "article") or a.get("role") == "main":
            self.has_main = True
        if tag == "a" and "href" in a:
            self._link = {"href": a["href"], "text": []}
        if tag in ("dfn", "dt", "abbr") or (tag in ("h2", "h3", "h4") and a.get("id")):
            self._capture.append({"kind": tag, "text": [], "id": a.get("id") or "", "depth": len(self.stack),
                                  "title": a.get("title", "")})
        if tag not in _VOID:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append("".join(self._jsonld_buf))
        if tag == "a" and self._link is not None:
            self.links.append({"href": self._link["href"], "text": " ".join("".join(self._link["text"]).split())})
            self._link = None
        for i in range(len(self._capture) - 1, -1, -1):
            if self._capture[i]["kind"] == tag:
                m = self._capture.pop(i)
                text = " ".join("".join(m["text"]).split())
                if text:
                    if m["kind"] == "abbr":
                        self.abbrs.append(text)
                    else:
                        self.markers.append({"kind": m["kind"], "text": text, "id": m["id"]})
                break
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf.append(data)
            return
        if self._inside(_SKIP):
            return
        for m in self._capture:
            m["text"].append(data)
        if self._link is not None:
            self._link["text"].append(data)
        in_main = self._inside({"main", "article"}) or any(a.get("role") == "main" for _, a in self.stack)
        if in_main and not self._inside({"nav", "aside"}):
            self.main_text.append(data)
        if not self._inside(_BOILER):
            self.body_text.append(data)


@dataclass
class Page:
    url: str
    status: int | None = None
    final_url: str | None = None
    error: str | None = None
    parser: _GlossaryParser | None = None

    @property
    def text(self) -> str:
        """Body text used for mentions: <main>/<article> if present, else the
        body outside nav/header/footer/aside."""
        if not self.parser:
            return ""
        parts = self.parser.main_text if self.parser.has_main else self.parser.body_text
        return " ".join(" ".join(parts).split())

    def link_targets(self) -> set[str]:
        """Absolute link targets, with and without fragment."""
        base = self.final_url or self.url
        out = set()
        for link in (self.parser.links if self.parser else []):
            href = link["href"].strip()
            if not href or href.lower().startswith(("javascript:", "mailto:", "tel:")):
                continue
            absolute = urllib.parse.urljoin(base, href)
            out.add(absolute)
            out.add(urllib.parse.urldefrag(absolute)[0])
        return out


def parse_page(url: str, markup: str, status: int | None = 200, final_url: str | None = None) -> Page:
    p = _GlossaryParser()
    p.feed(markup)
    p.close()
    return Page(url=url, status=status, final_url=final_url or url, parser=p)


def fetch_page(url: str, timeout: float = 20.0) -> Page:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            if "html" not in ctype.lower():
                return Page(url=url, status=r.status, final_url=r.geturl(), error=f"non HTML ({ctype})")
            body = r.read(MAX_BYTES).decode("utf-8", errors="replace")
            return parse_page(url, body, r.status, r.geturl())
    except urllib.error.HTTPError as e:
        return Page(url=url, status=e.code, error=f"HTTP {e.code}")
    except Exception as e:  # DNS, TLS, timeout
        return Page(url=url, error=str(e))


# --------------------------------------------------------------------------- glossary extraction

def _jsonld_nodes(blocks: list[str]):
    for raw in blocks:
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                yield node
                stack.extend(v for v in node.values() if isinstance(v, (dict, list)))


def _types(node: dict) -> list[str]:
    t = node.get("@type", [])
    return [t] if isinstance(t, str) else [x for x in t if isinstance(x, str)]


def extract_terms(page: Page, term_links: str | None = None) -> list[dict]:
    """Terms of a glossary page. JSON-LD DefinedTerm first; visible markers
    (<dfn>, <dt>, headings with id) complete the list. With `term_links`
    (regex on the absolute link URL), a hub that links to one page per term
    also yields its terms: link text = term, link target = definition URL."""
    terms: dict[str, dict] = {}
    base = page.final_url or page.url
    if term_links and page.parser:
        rx = re.compile(term_links)
        for link in page.parser.links:
            target = urllib.parse.urljoin(base, link["href"].strip())
            key = norm(link["text"])
            if rx.search(target) and 2 <= len(key) <= 80:
                terms.setdefault(key, {"term": link["text"], "source": "hub-link", "definition": "",
                                       "url": urllib.parse.urldefrag(target)[0], "anchor": ""})
    for node in _jsonld_nodes(page.parser.jsonld if page.parser else []):
        if "DefinedTerm" not in _types(node) or not isinstance(node.get("name"), str):
            continue
        name = node["name"].strip()
        target = node.get("url") or node.get("@id") or ""
        terms.setdefault(norm(name), {"term": name, "source": "jsonld", "definition": str(node.get("description") or ""),
                                      "url": urllib.parse.urljoin(base, target) if target else "",
                                      "anchor": ""})
    markers = page.parser.markers if page.parser else []
    if terms or any(m["kind"] in ("dfn", "dt") for m in markers):
        markers = [m for m in markers if m["kind"] in ("dfn", "dt")]  # headings only as a fallback
    for m in markers:
        key = norm(m["text"])
        if len(key) < 2 or len(key) > 80:
            continue
        entry = terms.setdefault(key, {"term": m["text"], "source": m["kind"], "definition": "", "url": "",
                                       "anchor": ""})
        if m["id"] and not entry["anchor"]:
            entry["anchor"] = m["id"]
        entry.setdefault("visible_kinds", []).append(m["kind"])
    for entry in terms.values():
        if not entry["url"] and entry["anchor"]:
            entry["url"] = f"{urllib.parse.urldefrag(base)[0]}#{entry['anchor']}"
    return list(terms.values())


def audit_glossary_page(page: Page, min_words: int = MIN_DEF_WORDS, term_links: str | None = None) -> dict:
    terms = extract_terms(page, term_links)
    visible = norm(" ".join(" ".join(page.parser.body_text).split())) if page.parser else ""
    base = urllib.parse.urldefrag(page.final_url or page.url)[0]
    issues = []
    for t in terms:
        if t["source"] == "jsonld":
            if not term_pattern(t["term"]).search(visible):
                issues.append({"code": "jsonld-term-not-visible", "label": "ESTABLISHED", "blocking": True,
                               "detail": f"{t['term']} : dans le JSON-LD mais absent du texte visible"})
            if t["definition"] and words(t["definition"]) < min_words:
                issues.append({"code": "definition-short", "label": "CLAIMED", "blocking": False,
                               "detail": f"{t['term']} : {words(t['definition'])} mot(s) (heuristique)"})
            if not t["definition"]:
                issues.append({"code": "jsonld-term-no-description", "label": "CLAIMED", "blocking": False,
                               "detail": f"{t['term']} : DefinedTerm sans description"})
        target, frag = urllib.parse.urldefrag(t["url"]) if t["url"] else ("", "")
        if frag and target == base and frag not in (page.parser.ids if page.parser else set()):
            issues.append({"code": "term-anchor-missing", "label": "ESTABLISHED", "blocking": True,
                           "detail": f"{t['term']} : #{frag} ne correspond à aucun id de la page"})
        if not t["url"]:
            issues.append({"code": "term-not-addressable", "label": "CLAIMED", "blocking": False,
                           "detail": f"{t['term']} : ni id ni URL propre, impossible de lier la définition"})
    jsonld_count = sum(1 for t in terms if t["source"] == "jsonld")
    return {"url": page.url, "status": page.status, "terms": terms, "term_count": len(terms),
            "jsonld_terms": jsonld_count, "issues": issues}


def mention_opportunities(terms: list[dict], pages: list[Page], glossary_url: str) -> dict:
    """Pages whose body text mentions a term with no link to its definition
    (the term's anchor or its own URL). One entry per (term, page)."""
    glossary_base = urllib.parse.urldefrag(glossary_url)[0]
    per_term: dict[str, list[str]] = defaultdict(list)
    mentioned: Counter = Counter()
    patterns = {t["term"]: term_pattern(t["term"]) for t in terms}
    for page in pages:
        if not page.parser or urllib.parse.urldefrag(page.final_url or page.url)[0] == glossary_base:
            continue
        text = norm(page.text)
        targets = page.link_targets()
        for t in terms:
            if not patterns[t["term"]].search(text):
                continue
            mentioned[t["term"]] += 1
            # A link to the hub alone (menu, footer) is not a link to this definition. Terms
            # with no address of their own can only be reached through the hub.
            linked = t["url"] in targets if t["url"] else glossary_base in targets
            if not linked:
                per_term[t["term"]].append(page.url)
    never = sorted(t["term"] for t in terms if mentioned[t["term"]] == 0)
    opportunities = sorted(({"term": k, "pages": v, "count": len(v)} for k, v in per_term.items()),
                           key=lambda x: (-x["count"], x["term"]))
    return {"pages_scanned": sum(1 for p in pages if p.parser), "opportunities": opportunities,
            "terms_never_mentioned": never}


# --------------------------------------------------------------------------- suggest

_ACRO = re.compile(r"(?<![\w-])([A-Za-z][A-Za-z0-9-]{1,7})(?![\w-])")


def acronyms(text: str) -> set[str]:
    out = set()
    for tok in _ACRO.findall(text):
        letters = [c for c in tok if c.isalpha()]
        upper = sum(1 for c in letters if c.isupper())
        if upper >= 2 and upper * 2 >= len(letters) and tok.upper() not in ACRONYM_STOP and not tok.isdigit():
            out.add(tok)
    return out


def suggest_terms(pages: list[Page], known: set[str] | None = None, min_pages: int = 2, limit: int = 40) -> list[dict]:
    known = {norm(k) for k in (known or set())}
    df: Counter = Counter()
    where: dict[str, list[str]] = defaultdict(list)
    kind: dict[str, str] = {}
    for page in pages:
        if not page.parser:
            continue
        found: dict[str, str] = {}
        for tok in acronyms(page.text):
            found.setdefault(tok, "sigle")
        for tok in page.parser.abbrs:
            found[tok] = "abbr"
        for m in page.parser.markers:
            if m["kind"] == "dfn":
                found[m["text"]] = "dfn"
        for tok, k in found.items():
            df[tok] += 1
            kind.setdefault(tok, k)
            if len(where[tok]) < 5:
                where[tok].append(page.url)
    out = [{"term": t, "pages": n, "kind": kind[t], "examples": where[t]}
           for t, n in df.items() if n >= min_pages and norm(t) not in known]
    return sorted(out, key=lambda x: (-x["pages"], x["term"]))[:limit]


# --------------------------------------------------------------------------- crawl (sitemap sample)

def site_pages(site: str, max_pages: int, delay: float, timeout: float) -> tuple[list[Page], dict]:
    """Home + sitemap URLs (robots.txt respected), up to max_pages."""
    parts = urllib.parse.urlsplit(site)
    origin = f"{parts.scheme}://{parts.netloc}"
    robots = None
    try:
        req = urllib.request.Request(f"{origin}/robots.txt", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            robots = robotstxt.parse(r.read(robotstxt.MAX_BYTES).decode("utf-8", errors="replace"))
    except Exception:
        robots = None  # 4xx or unreachable: no restriction assumed, as RFC 9309 for 4xx
    declared = robots.records("sitemap") if robots else []
    sm = sitemaps_mod.discover(origin, declared, timeout=timeout)
    urls = [site] + [u for u in sm.urls if urllib.parse.urlsplit(u).netloc == parts.netloc]
    seen, pages, skipped = set(), [], 0
    for u in urls:
        if len(pages) >= max_pages:
            break
        if u in seen:
            continue
        seen.add(u)
        path = urllib.parse.urlsplit(u).path or "/"
        if robots and not robotstxt.is_allowed(robots, AUDIT_TOKEN, path):
            skipped += 1
            continue
        pages.append(fetch_page(u, timeout))
        time.sleep(delay)
    return pages, {"sitemap_urls": len(sm.urls), "fetched": len(pages), "skipped_by_robots": skipped,
                   "complete": len(pages) + skipped >= len(set(urls))}


# --------------------------------------------------------------------------- CLI

def _print_issues(issues: list[dict]) -> None:
    for i in issues:
        print(f"  [{i['label']}{', bloquant' if i['blocking'] else ''}] {i['code']} -- {i['detail']}")


def cmd_build(a) -> int:
    terms = load_terms(Path(a.terms))
    issues = check_terms(terms, a.min_words)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = build_jsonld(terms, a.set_name, a.set_url, a.lang, a.description)
    (out / "glossary.jsonld").write_text(
        '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>\n",
        encoding="utf-8")
    (out / "glossary.html").write_text(build_html(terms, a.set_url), encoding="utf-8")
    print(f"{len(data['hasDefinedTerm'])} terme(s) écrits dans {out / 'glossary.html'} et {out / 'glossary.jsonld'}")
    _print_issues(issues)
    return 1 if any(i["blocking"] for i in issues) else 0


def cmd_audit(a) -> int:
    page = fetch_page(a.url, a.timeout)
    if not page.parser:
        print(f"Glossaire injoignable : {a.url} ({page.error or page.status})")
        return 2
    result = audit_glossary_page(page, a.min_words, a.term_links)
    print(f"Glossaire {a.url} : HTTP {page.status}, {result['term_count']} terme(s), "
          f"{result['jsonld_terms']} en JSON-LD DefinedTerm")
    _print_issues(result["issues"])
    if a.site:
        pages, crawl = site_pages(a.site, a.max_pages, a.delay, a.timeout)
        result["crawl"] = crawl
        result["linking"] = mention_opportunities(result["terms"], pages, a.url)
        lk = result["linking"]
        print(f"Maillage : {lk['pages_scanned']} page(s) lue(s) ({crawl['sitemap_urls']} URL(s) au sitemap, "
              f"crawl {'complet' if crawl['complete'] else 'partiel'})")
        for o in lk["opportunities"][:25]:
            print(f"  « {o['term']} » cité sans lien vers sa définition sur {o['count']} page(s) : "
                  + ", ".join(o["pages"][:3]))
        if lk["terms_never_mentioned"]:
            print(f"  Termes jamais cités ailleurs ({len(lk['terms_never_mentioned'])}) : "
                  + ", ".join(lk["terms_never_mentioned"][:20]))
    if a.json:
        Path(a.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if any(i["blocking"] for i in result["issues"]) else 0


def cmd_suggest(a) -> int:
    pages, crawl = site_pages(a.site, a.max_pages, a.delay, a.timeout)
    known: set[str] = set()
    if a.glossary:
        g = fetch_page(a.glossary, a.timeout)
        if g.parser:
            known = {t["term"] for t in extract_terms(g, a.term_links)}
    cands = suggest_terms(pages, known, a.min_pages)
    print(f"{crawl['fetched']} page(s) lue(s) ; {len(cands)} candidat(s) présent(s) sur >= {a.min_pages} pages "
          "(heuristique : sigles, <abbr>, <dfn> ; à trier à la main)")
    for c in cands:
        print(f"  {c['term']:<16} {c['pages']:>3} page(s)  [{c['kind']}]  ex. {c['examples'][0]}")
    if a.json:
        Path(a.json).write_text(json.dumps({"crawl": crawl, "candidates": cands}, ensure_ascii=False, indent=2),
                                encoding="utf-8")
    return 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Fichier de termes -> <dl> HTML + JSON-LD DefinedTermSet")
    b.add_argument("--terms", required=True)
    b.add_argument("--set-name", required=True)
    b.add_argument("--set-url", required=True, help="URL publique de la page du glossaire")
    b.add_argument("--lang", default=None)
    b.add_argument("--description", default=None)
    b.add_argument("--out-dir", default="glossary-out")
    b.add_argument("--min-words", type=int, default=MIN_DEF_WORDS)
    for name, help_ in (("audit", "Audit d'une page de glossaire (+ maillage avec --site)"),
                        ("suggest", "Termes candidats relevés sur le site")):
        s = sub.add_parser(name, help=help_)
        if name == "audit":
            s.add_argument("--url", required=True)
            s.add_argument("--site", default=None)
        else:
            s.add_argument("--site", required=True)
            s.add_argument("--glossary", default=None)
            s.add_argument("--min-pages", type=int, default=2)
        s.add_argument("--term-links", default=None,
                       help="Regex sur l'URL des liens du hub qui mènent à une page par terme, ex. '/definition/'")
        s.add_argument("--max-pages", type=int, default=40)
        s.add_argument("--delay", type=float, default=0.5)
        s.add_argument("--timeout", type=float, default=20.0)
        s.add_argument("--min-words", type=int, default=MIN_DEF_WORDS)
        s.add_argument("--json", default=None, help="Écrire le résultat complet en JSON")
    return p.parse_args(argv)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
    a = parse_args(argv)
    return {"build": cmd_build, "audit": cmd_audit, "suggest": cmd_suggest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
