#!/usr/bin/env python3
"""Confiance et hygiene du site (ajout 2.8.0) : HTTPS, en-tetes de securite,
security.txt, identite de l'organisation (sameAs, contact), coherence
sitemap lastmod / date de la page.

Ces controles NE SONT PAS des facteurs de classement (Google : seuls les Core
Web Vitals comptent parmi les aspects "page experience", maj non datee de la page).
Ils sont P2 au plus : HTTPS est un indicateur positif de qualite (web.dev
enable-https), le reste protege le site ou aide la desambiguisation de
l'entite. Stdlib uniquement, lecture seule.

Usage : python trust_check.py --site https://exemple.fr
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

UA = "seo-geo-optimizer-audit/2.8 (+lecture seule)"


def _request(url: str, timeout: float = 15.0, follow: bool = True):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener(*([] if follow else [NoRedirect()]))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, ""
    except Exception as e:  # DNS, TLS, timeout
        return None, {}, str(e)


def check_headers(origin: str, request=_request) -> list[tuple[str, str | None, str]]:
    """(code, url, detail). Rien si le site repond mal : on ne conclut pas."""
    out = []
    host = origin.split("://", 1)[1]
    st, hdr, _ = request(origin + "/")
    if st != 200:
        return out
    if origin.startswith("https://"):
        st80, h80, _ = request("http://" + host + "/", follow=False)
        loc = h80.get("location", "")
        if st80 == 200:
            out.append(("http-no-redirect", "http://" + host + "/", "la version http repond 200 sans rediriger"))
        elif st80 in (301, 302, 307, 308) and not loc.startswith("https://"):
            out.append(("http-no-redirect", "http://" + host + "/", f"redirige vers {loc[:80]}"))
        if "strict-transport-security" not in hdr:
            out.append(("hsts-missing", origin + "/", "en-tete Strict-Transport-Security absent"))
        else:
            m = re.search(r"max-age=(\d+)", hdr["strict-transport-security"], re.I)
            if not m or int(m.group(1)) < 15552000:
                out.append(("hsts-missing", origin + "/", "max-age absent ou inferieur a 180 jours"))
    miss = [h for h in ("x-content-type-options", "referrer-policy") if h not in hdr]
    if miss:
        out.append(("security-headers-missing", origin + "/", "absents : " + ", ".join(miss)))
    return out


def check_security_txt(origin: str, request=_request, today: date | None = None):
    today = today or datetime.now(timezone.utc).date()
    st, _, body = request(origin + "/.well-known/security.txt")
    if st != 200 or "contact:" not in body.lower():
        return [("security-txt-missing", origin + "/.well-known/security.txt", f"HTTP {st}" if st else "injoignable")]
    m = re.search(r"^expires:\s*(\S+)", body, re.I | re.M)
    if not m:
        return [("security-txt-expired", origin + "/.well-known/security.txt", "champ Expires absent (obligatoire, RFC 9116)")]
    try:
        exp = datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).date()
    except ValueError:
        return [("security-txt-expired", origin + "/.well-known/security.txt", f"Expires illisible : {m.group(1)}")]
    if exp < today:
        return [("security-txt-expired", origin + "/.well-known/security.txt", f"expire le {exp}")]
    return []


def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def jsonld_nodes(blocks: list[str]) -> list[dict]:
    nodes = []
    for b in blocks:
        try:
            nodes += [n for n in _walk(json.loads(b)) if isinstance(n, dict)]
        except ValueError:
            pass
    return nodes


def check_identity(home_jsonld: list[str], home_html_has_contact: bool | None = None):
    """sameAs et contact sur l'entite Organization / LocalBusiness de l'accueil."""
    out = []
    orgs = [n for n in jsonld_nodes(home_jsonld)
            if any(t in str(n.get("@type", "")) for t in ("Organization", "LocalBusiness", "Corporation"))]
    if not orgs:
        return out  # pas d'entite : deja couvert par les regles de schema
    if not any(n.get("sameAs") for n in orgs):
        out.append(("org-sameas-missing", None, "aucun sameAs sur l'Organization de l'accueil"))
    if not any(n.get("email") or n.get("telephone") or n.get("contactPoint") for n in orgs):
        out.append(("org-contact-missing", None, "ni email, ni telephone, ni contactPoint dans le schema"))
    return out


def _d(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return None


def page_modified_date(jsonld: list[str], meta: list[dict]) -> date | None:
    for n in jsonld_nodes(jsonld):
        if n.get("dateModified") and _d(str(n["dateModified"])):
            return _d(str(n["dateModified"]))
    for m in meta:
        if m.get("property") == "article:modified_time" and _d(m.get("content", "")):
            return _d(m["content"])
    return None


def check_lastmod_vs_page(pairs: list[tuple[str, str, date | None]], tolerance_days: int = 2):
    """pairs : (url, lastmod du sitemap, date de modification annoncee par la page).
    Ne juge que les pages qui annoncent une date : sinon 'non mesurable'."""
    bad = []
    for url, lm, pd in pairs:
        d = _d(lm)
        if d and pd and abs((d - pd).days) > tolerance_days:
            bad.append((url, f"sitemap {d} / page {pd}"))
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", required=True)
    a = ap.parse_args(argv)
    origin = a.site.rstrip("/")
    res = check_headers(origin) + check_security_txt(origin)
    st, _, html = _request(origin + "/")
    if st == 200:
        blocks = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I)
        res += check_identity(blocks)
    print(json.dumps([{"code": c, "url": u, "detail": d} for c, u, d in res], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
