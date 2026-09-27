#!/usr/bin/env python3
"""Tire un rapport Search Console reel via un compte de service GCP.

Donnee MESUREE (pas une inference depuis le HTML public) -- voir
references/data-hygiene.md. Reutilisable sur n'importe quel site : le
compte de service doit juste etre ajoute comme utilisateur (Proprietaire ou
Utilisateur complet) sur la propriete Search Console visee.

Usage:
    python gsc_report.py --service-account creds.json --site sc-domain:example.com \
        [--path-filter https://example.com/] [--days 28] [--dimension query|page] \
        [--out report.json]

Prerequis compte de service (a faire une fois par site, dans Google Cloud Console) :
1. Creer un projet GCP (ou reutiliser un existant) + activer l'API
   "Google Search Console API".
2. IAM & Admin > Comptes de service > Creer un compte de service.
3. Creer une cle JSON pour ce compte (Cles > Ajouter une cle > JSON).
4. Dans Search Console (search.google.com/search-console) : Parametres >
   Utilisateurs et autorisations > Ajouter un utilisateur > coller l'email
   du compte de service (ex: xxx@projet.iam.gserviceaccount.com). L'API
   demande un droit de lecture : "Restreint" devrait suffire (inference depuis
   la table des permissions, non ecrit par Google) ; "Complet" en cas de doute.
5. Stocker le fichier JSON hors du repo git (secrets/, jamais commite).

Necessite : pip install google-auth requests
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from google.oauth2 import service_account
import google.auth.transport.requests as google_requests

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API_BASE = "https://www.googleapis.com/webmasters/v3"


def get_access_token(service_account_path: Path) -> str:
    creds = service_account.Credentials.from_service_account_file(str(service_account_path), scopes=SCOPES)
    creds.refresh(google_requests.Request())
    return creds.token


def list_accessible_sites(token: str) -> list[dict]:
    resp = requests.get(f"{API_BASE}/sites", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json().get("siteEntry", [])


SEARCH_TYPES = ("web", "discover", "googleNews", "news", "image", "video")


def build_query_body(start_date: str, end_date: str, dimension: str, path_filter: str | None,
                     row_limit: int, search_type: str = "web", data_state: str = "final") -> dict:
    """Request body for searchAnalytics.query. `type` replaces the deprecated
    `searchType` (API reference, last updated 2026-08-11)."""
    if search_type not in SEARCH_TYPES:
        raise ValueError(f"type inconnu : {search_type}")
    body: dict = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": [dimension],
        "rowLimit": min(row_limit, 25_000),
        "type": search_type,
        "dataState": data_state,
    }
    if path_filter:
        body["dimensionFilterGroups"] = [
            {"filters": [{"dimension": "page", "operator": "contains", "expression": path_filter}]}
        ]
    return body


def query_search_analytics(
    token: str,
    site_url: str,
    start_date: str,
    end_date: str,
    dimension: str = "page",
    path_filter: str | None = None,
    row_limit: int = 25,
    search_type: str = "web",
    data_state: str = "final",
) -> list[dict]:
    body = build_query_body(start_date, end_date, dimension, path_filter, row_limit, search_type, data_state)
    from urllib.parse import quote

    resp = requests.post(
        f"{API_BASE}/sites/{quote(site_url, safe='')}/searchAnalytics/query",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body,
    )
    resp.raise_for_status()
    rows = resp.json().get("rows", [])
    return [
        {
            "key": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"] * 100, 2),
            "position": round(r["position"], 1),
        }
        for r in rows
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--service-account", required=True, type=Path)
    parser.add_argument("--site", required=True, help="ex: sc-domain:example.com ou https://example.com/")
    parser.add_argument("--path-filter", default=None, help="ex: https://example.com/ pour exclure les sous-domaines")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--dimension", choices=["query", "page"], default="page")
    parser.add_argument("--row-limit", type=int, default=25)
    parser.add_argument("--search-type", choices=SEARCH_TYPES, default="web")
    parser.add_argument("--data-state", choices=["final", "all"], default="final",
                        help="all = inclut les donnees fraiches non consolidees")
    parser.add_argument("--out", type=Path, default=None, help="Ecrit le resultat en JSON ici (sinon stdout)")
    args = parser.parse_args()

    if not args.service_account.exists():
        print(f"Introuvable : {args.service_account}", file=sys.stderr)
        return 1

    token = get_access_token(args.service_account)

    sites = list_accessible_sites(token)
    if not any(s["siteUrl"] == args.site for s in sites):
        print(
            f"ATTENTION : le compte de service n'a pas d'acces confirme a '{args.site}'. "
            f"Proprietes accessibles : {[s['siteUrl'] for s in sites]}",
            file=sys.stderr,
        )

    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=args.days)

    rows = query_search_analytics(
        token, args.site, start.isoformat(), end.isoformat(),
        dimension=args.dimension, path_filter=args.path_filter, row_limit=args.row_limit,
        search_type=args.search_type, data_state=args.data_state,
    )

    result = {
        "site": args.site,
        "path_filter": args.path_filter,
        "dimension": args.dimension,
        "search_type": args.search_type,
        "data_state": args.data_state,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "rows": rows,
        "measured": True,  # cf. data-hygiene.md : donnee mesuree, pas generee
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(output, encoding="utf-8")
        print(f"Rapport ecrit : {args.out} ({len(rows)} ligne(s))")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
