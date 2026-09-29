#!/usr/bin/env python3
"""Search Console operee par l'agent, avec l'acces du proprietaire du site.

Appelle l'API Search Console (REST, documentee par Google) au nom d'un
compte de service que le proprietaire a ajoute a sa propriete. Mise en
place : references/gsc-access.md. Methode de decouverte des URL :
references/url-discovery.md.

Sous-commandes :
    sites            proprietes accessibles au compte de service
    sitemaps         sitemaps connus de Search Console (erreurs, derniere lecture)
    submit-sitemap   soumet ou re-soumet un sitemap (sitemaps.submit) -- action externe
    inspect          URL Inspection API : liste des URL non indexees, et les
                     quelques URL prioritaires a proposer a la demande manuelle
    mark-requested   note dans le fichier d'etat les URL demandees a la main
    stats            Search Analytics (clics, impressions, CTR, position)

Exemples :
    GSC_SERVICE_ACCOUNT_FILE=~/secrets/gsc.json python search_console.py sites
    python search_console.py sitemaps --site sc-domain:example.com
    python search_console.py submit-sitemap --site sc-domain:example.com \\
        --sitemap https://example.com/sitemap.xml
    python search_console.py inspect --site sc-domain:example.com \\
        --sitemap https://example.com/sitemap.xml --state gsc_state.json --out inspect.json
    python search_console.py stats --site sc-domain:example.com --days 28 --dimension page

Acces (jamais en argument, jamais affiche) :
    GSC_SERVICE_ACCOUNT_FILE  chemin du fichier JSON de la cle du compte de service
                              (pip install google-auth requests)
    GSC_ACCESS_TOKEN          ou un jeton OAuth deja obtenu (ex. gcloud), sans dependance

Quotas (https://developers.google.com/webmaster-tools/limits, maj 2025-08-28) :
URL Inspection 2 000 requetes/jour et 600/minute par propriete. Le script
s'arrete au premier refus de quota et garde ce qu'il a deja inspecte.

Codes de sortie : 0 = OK ; 1 = erreur d'API ou resultat partiel ; 2 = acces absent.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import envkeys  # noqa: E402

WEBMASTERS = "https://www.googleapis.com/webmasters/v3"
INSPECT_ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SCOPE_WRITE = "https://www.googleapis.com/auth/webmasters"  # sitemaps.submit
SCOPE_READ = "https://www.googleapis.com/auth/webmasters.readonly"
INSPECT_DAILY_QUOTA = 2000  # par propriete
INSPECT_PER_MINUTE = 600  # par propriete
RETRY_STATUSES = (500, 502, 503, 504)
USER_AGENT = "seo-geo-optimizer/2.4 (Search Console client)"


class AccessMissing(Exception):
    """Neither GSC_ACCESS_TOKEN nor a readable GSC_SERVICE_ACCOUNT_FILE."""


class ApiError(Exception):
    def __init__(self, status: int | None, message: str) -> None:
        super().__init__(f"HTTP {status} : {message}" if status else message)
        self.status = status
        self.message = message

    @property
    def quota(self) -> bool:
        return self.status == 429 or "quota" in self.message.lower()


# --------------------------------------------------------------------------- access

def access_token(write: bool = False) -> str:
    """Token from GSC_ACCESS_TOKEN, else minted from the service-account key.
    Never printed. write=True asks for the scope sitemaps.submit needs."""
    token = envkeys.secret("GSC_ACCESS_TOKEN")
    if token:
        return token
    path = envkeys.secret_file("GSC_SERVICE_ACCOUNT_FILE")
    if not path:
        raise AccessMissing("GSC_SERVICE_ACCOUNT_FILE (fichier de cle) ou GSC_ACCESS_TOKEN absent ou introuvable")
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests as google_requests
    except ImportError as e:  # pragma: no cover - depends on the machine
        raise AccessMissing("bibliotheques Google absentes : pip install google-auth requests") from e
    creds = service_account.Credentials.from_service_account_file(
        str(path), scopes=[SCOPE_WRITE if write else SCOPE_READ])
    creds.refresh(google_requests.Request())
    return creds.token


def urllib_transport(method: str, url: str, headers: dict, body: bytes | None, timeout: float = 60.0):
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# --------------------------------------------------------------------------- client

class SearchConsole:
    """Minimal REST client. `transport(method, url, headers, body)` returns
    (status, bytes); tests inject a fake one, nothing leaves the machine."""

    def __init__(self, token: str, transport=urllib_transport, sleep=time.sleep, retries: int = 3) -> None:
        self._token = token
        self._transport = transport
        self._sleep = sleep
        self._retries = retries

    def _call(self, method: str, url: str, payload: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self._token}", "User-Agent": USER_AGENT}
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        for attempt in range(self._retries + 1):
            status, raw = self._transport(method, url, headers, body)
            if status in RETRY_STATUSES and attempt < self._retries:
                self._sleep(2 ** attempt)
                continue
            break
        text = (raw or b"").decode("utf-8", errors="replace")
        if not 200 <= status < 300:
            try:
                message = json.loads(text).get("error", {}).get("message", "") or text
            except ValueError:
                message = text
            raise ApiError(status, envkeys.redact(message[:300], [self._token]))
        return json.loads(text) if text.strip() else {}

    @staticmethod
    def _q(value: str) -> str:
        return urllib.parse.quote(value, safe="")

    def sites(self) -> list[dict]:
        return self._call("GET", f"{WEBMASTERS}/sites").get("siteEntry", [])

    def sitemaps(self, site: str) -> list[dict]:
        return self._call("GET", f"{WEBMASTERS}/sites/{self._q(site)}/sitemaps").get("sitemap", [])

    def submit_sitemap(self, site: str, feed: str) -> None:
        """sitemaps.submit: PUT, empty body and response (API reference, maj 2024-07-23)."""
        self._call("PUT", f"{WEBMASTERS}/sites/{self._q(site)}/sitemaps/{self._q(feed)}")

    def inspect(self, site: str, url: str, language: str = "en-US") -> dict:
        return self._call("POST", INSPECT_ENDPOINT,
                          {"inspectionUrl": url, "siteUrl": site, "languageCode": language})

    def search_analytics(self, site: str, body: dict) -> list[dict]:
        return self._call("POST", f"{WEBMASTERS}/sites/{self._q(site)}/searchAnalytics/query", body).get("rows", [])


# --------------------------------------------------------------------------- inspection

def classify(index_status: dict) -> str:
    """Category of an indexStatusResult, from enum fields (language-independent)."""
    if index_status.get("verdict") == "PASS":
        return "indexed"
    fetch = index_status.get("pageFetchState", "")
    if index_status.get("robotsTxtState") == "DISALLOWED" or fetch == "BLOCKED_ROBOTS_TXT":
        return "blocked_robots_txt"
    if index_status.get("indexingState") in ("BLOCKED_BY_META_TAG", "BLOCKED_BY_HTTP_HEADER"):
        return "noindex"
    if fetch and fetch not in ("SUCCESSFUL", "PAGE_FETCH_STATE_UNSPECIFIED"):
        return "fetch_error"
    google, declared = index_status.get("googleCanonical"), index_status.get("userCanonical")
    if google and declared and google != declared:
        return "canonical_elsewhere"
    coverage = (index_status.get("coverageState") or "").lower()
    if "unknown" in coverage:
        return "unknown_to_google"
    if "discovered" in coverage:
        return "discovered_not_crawled"
    if "crawled" in coverage:
        return "crawled_not_indexed"
    return "other"


# Only these categories can gain from a manual "Request indexing": the others
# need a fix on the site first (robots.txt, noindex, error, canonical).
REQUESTABLE = ("unknown_to_google", "discovered_not_crawled", "crawled_not_indexed", "other")

NEXT_STEP = {
    "indexed": "indexee : rien a faire",
    "unknown_to_google": "absente de l'index connu : verifier sitemap (lastmod), lien interne depuis l'accueil ou une rubrique",
    "discovered_not_crawled": "connue, pas encore exploree : maillage interne, patience ; demande manuelle possible",
    "crawled_not_indexed": "exploree, non retenue : contenu propre et utile, doublon eventuel, pas une question de soumission",
    "blocked_robots_txt": "bloquee par robots.txt : corriger robots.txt, ne pas soumettre",
    "noindex": "noindex (meta ou en-tete) : retirer le noindex si la page doit etre indexee",
    "fetch_error": "erreur d'exploration (404, 5xx, soft 404, redirection) : corriger la reponse HTTP",
    "canonical_elsewhere": "Google retient une autre URL canonique : verifier le canonical et les doublons",
    "other": "cas non classe : ouvrir le lien d'inspection",
}


def summarize(url: str, response: dict) -> dict:
    result = response.get("inspectionResult", {})
    idx = result.get("indexStatusResult", {})
    category = classify(idx)
    return {
        "url": url,
        "category": category,
        "verdict": idx.get("verdict"),
        "coverage": idx.get("coverageState"),
        "page_fetch": idx.get("pageFetchState"),
        "indexing_state": idx.get("indexingState"),
        "robots_txt": idx.get("robotsTxtState"),
        "last_crawl": idx.get("lastCrawlTime"),
        "google_canonical": idx.get("googleCanonical"),
        "user_canonical": idx.get("userCanonical"),
        "next_step": NEXT_STEP.get(category, ""),
        "link": result.get("inspectionResultLink"),
    }


def load_state(path: Path | None) -> dict:
    if path and path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def save_state(path: Path | None, state: dict) -> None:
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _age(value: str | None, now: datetime) -> timedelta | None:
    if not value:
        return None
    try:
        return now - datetime.fromisoformat(value)
    except ValueError:
        return None


def order_urls(entries: list[tuple[str, str | None]], priority: list[str]) -> list[str]:
    """Priority URLs first (in the given order), then by lastmod, newest first."""
    known = {u for u, _ in entries}
    first = [u for u in priority if u in known]
    rest = sorted((e for e in entries if e[0] not in set(first)), key=lambda e: e[1] or "", reverse=True)
    seen: dict[str, None] = {}
    for u in first + [u for u, _ in rest]:
        seen.setdefault(u, None)
    return list(seen)


def run_inspection(client: SearchConsole, site: str, urls: list[str], state: dict, *,
                   max_inspect: int = 100, max_request: int = 10, recheck_days: int = 7,
                   request_cooldown_days: int = 7, pace: float = 0.2, now: datetime | None = None,
                   sleep=time.sleep) -> dict:
    """Inspects up to max_inspect URLs (never above the daily quota), skipping
    URLs found indexed less than recheck_days ago. Updates `state` in place."""
    now = now or datetime.now(timezone.utc)
    max_inspect = max(0, min(max_inspect, INSPECT_DAILY_QUOTA))
    pace = max(pace, 60.0 / INSPECT_PER_MINUTE)
    report = {"site": site, "candidates": len(urls), "inspected": 0, "indexed": 0,
              "skipped_recently_indexed": 0, "not_indexed": [], "to_request": [],
              "errors": [], "quota_stopped": False}
    consecutive_errors = 0
    for url in urls:
        if report["inspected"] >= max_inspect:
            break
        entry = state.setdefault(url, {})
        age = _age(entry.get("inspected_at"), now)
        if entry.get("category") == "indexed" and age is not None and age < timedelta(days=recheck_days):
            report["skipped_recently_indexed"] += 1
            report["indexed"] += 1
            continue
        try:
            summary = summarize(url, client.inspect(site, url))
        except ApiError as e:
            report["errors"].append({"url": url, "error": str(e)})
            if e.quota:
                report["quota_stopped"] = True
                break
            consecutive_errors += 1
            if consecutive_errors >= 3:
                break
            continue
        consecutive_errors = 0
        report["inspected"] += 1
        entry.update(category=summary["category"], verdict=summary["verdict"],
                     coverage=summary["coverage"], inspected_at=now.isoformat())
        if summary["category"] == "indexed":
            report["indexed"] += 1
        else:
            report["not_indexed"].append(summary)
            requested = _age(entry.get("requested_at"), now)
            recently_requested = requested is not None and requested < timedelta(days=request_cooldown_days)
            if (summary["category"] in REQUESTABLE and not recently_requested
                    and len(report["to_request"]) < max_request):
                report["to_request"].append(url)
        sleep(pace)
    report["by_category"] = {}
    for item in report["not_indexed"]:
        report["by_category"][item["category"]] = report["by_category"].get(item["category"], 0) + 1
    return report


def mark_requested(state: dict, urls: list[str], now: datetime | None = None) -> int:
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    for u in urls:
        state.setdefault(u, {})["requested_at"] = stamp
    return len(urls)


# --------------------------------------------------------------------------- CLI helpers

def urls_from_args(args) -> list[tuple[str, str | None]]:
    """(url, lastmod) from --urls FILE and/or --sitemap URL (index followed)."""
    entries: list[tuple[str, str | None]] = []
    if getattr(args, "urls", None):
        entries += [(u.strip(), None) for u in Path(args.urls).read_text(encoding="utf-8").splitlines()
                    if u.strip() and not u.startswith("#")]
    for sm in getattr(args, "sitemap", None) or []:
        import sitemaps

        origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(sm))
        found = sitemaps.discover(origin, [sm])
        entries += [(e.loc, e.lastmod) for e in found.entries]
    return entries


def _emit(data, out: str | None) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
        print(f"Ecrit : {out}")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("sites", help="proprietes accessibles")

    s = sub.add_parser("sitemaps", help="sitemaps connus de Search Console")
    s.add_argument("--site", required=True, help="ex: sc-domain:example.com ou https://example.com/")

    s = sub.add_parser("submit-sitemap", help="soumet ou re-soumet un sitemap (action externe)")
    s.add_argument("--site", required=True)
    s.add_argument("--sitemap", action="append", required=True, help="URL du sitemap (repetable)")
    s.add_argument("--dry-run", action="store_true", help="affiche ce qui serait soumis, n'appelle pas l'API")

    s = sub.add_parser("inspect", help="URL Inspection API : URL non indexees")
    s.add_argument("--site", required=True)
    s.add_argument("--sitemap", action="append", help="URL d'un sitemap a inspecter (repetable)")
    s.add_argument("--urls", help="fichier : une URL par ligne")
    s.add_argument("--priority", help="fichier : URL a inspecter en premier")
    s.add_argument("--state", help="fichier d'etat JSON (hors depot) : evite de re-inspecter")
    s.add_argument("--max-inspect", type=int, default=100, help=f"au plus N inspections (plafond {INSPECT_DAILY_QUOTA})")
    s.add_argument("--max-request", type=int, default=10,
                   help="au plus N URL proposees a la demande manuelle (Google en accepte environ 10/jour)")
    s.add_argument("--recheck-days", type=int, default=7)
    s.add_argument("--pace", type=float, default=0.2, help="secondes entre deux inspections (min 0.1)")
    s.add_argument("--out", help="ecrit le JSON ici (sinon stdout)")

    s = sub.add_parser("mark-requested", help="note les URL demandees a la main dans l'etat")
    s.add_argument("--state", required=True)
    s.add_argument("urls", nargs="+")

    s = sub.add_parser("stats", help="Search Analytics")
    s.add_argument("--site", required=True)
    s.add_argument("--days", type=int, default=28)
    s.add_argument("--dimension", choices=["page", "query", "date", "country", "device"], default="page")
    s.add_argument("--search-type", choices=["web", "discover", "googleNews", "news", "image", "video"], default="web")
    s.add_argument("--row-limit", type=int, default=25)
    s.add_argument("--path-filter", help="ex: https://example.com/ (propriete domaine avec sous-domaines)")
    s.add_argument("--out")
    return p


def main(argv: list[str] | None = None, client: SearchConsole | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "mark-requested":
        state_path = Path(args.state)
        state = load_state(state_path)
        n = mark_requested(state, args.urls)
        save_state(state_path, state)
        print(json.dumps({"marked": n}))
        return 0

    if args.command == "submit-sitemap" and args.dry_run:
        for sm in args.sitemap:
            print(f"--dry-run : soumettrait {sm} a {args.site}")
        return 0

    if client is None:
        try:
            client = SearchConsole(access_token(write=args.command == "submit-sitemap"))
        except AccessMissing as e:
            print(f"Acces Search Console absent : {e}. Voir references/gsc-access.md", file=sys.stderr)
            return 2

    try:
        if args.command == "sites":
            _emit([{"site": s.get("siteUrl"), "permission": s.get("permissionLevel")} for s in client.sites()], None)
        elif args.command == "sitemaps":
            _emit([{k: s.get(k) for k in ("path", "lastSubmitted", "lastDownloaded", "isPending",
                                          "isSitemapsIndex", "errors", "warnings")}
                   for s in client.sitemaps(args.site)], None)
        elif args.command == "submit-sitemap":
            for sm in args.sitemap:
                client.submit_sitemap(args.site, sm)
                print(f"Soumis : {sm}")
        elif args.command == "inspect":
            entries = urls_from_args(args)
            if not entries:
                print("Aucune URL : --sitemap ou --urls", file=sys.stderr)
                return 1
            priority = []
            if args.priority:
                priority = [u.strip() for u in Path(args.priority).read_text(encoding="utf-8").splitlines() if u.strip()]
            state_path = Path(args.state) if args.state else None
            state = load_state(state_path)
            report = run_inspection(client, args.site, order_urls(entries, priority), state,
                                    max_inspect=args.max_inspect, max_request=args.max_request,
                                    recheck_days=args.recheck_days, pace=args.pace)
            save_state(state_path, state)
            _emit(report, args.out)
            return 1 if report["errors"] else 0
        elif args.command == "stats":
            import gsc_report

            end = datetime.now(timezone.utc).date()
            start = end - timedelta(days=args.days)
            body = gsc_report.build_query_body(start.isoformat(), end.isoformat(), args.dimension,
                                               args.path_filter, args.row_limit, args.search_type)
            rows = client.search_analytics(args.site, body)
            _emit({"site": args.site, "start_date": start.isoformat(), "end_date": end.isoformat(),
                   "dimension": args.dimension, "search_type": args.search_type, "measured": True,
                   "rows": [{"key": r["keys"][0], "clicks": r.get("clicks", 0),
                             "impressions": r.get("impressions", 0),
                             "ctr": round(r.get("ctr", 0) * 100, 2),
                             "position": round(r.get("position", 0), 1)} for r in rows]}, args.out)
    except ApiError as e:
        hint = ""
        if e.status == 403:
            hint = (" -- le compte de service n'a pas le droit requis sur cette propriete "
                    "(references/gsc-access.md, etape 7)")
        print(f"Erreur Search Console : {e}{hint}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
