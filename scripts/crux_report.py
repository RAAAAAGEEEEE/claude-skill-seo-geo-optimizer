#!/usr/bin/env python3
"""Core Web Vitals REELS (donnees terrain) via l'API Chrome UX Report (CrUX).

Difference essentielle avec Lighthouse/PageSpeed en mode labo : CrUX rapporte
ce que les vrais utilisateurs Chrome ont mesure sur les 28 derniers jours, pas
une simulation. C'est de la donnee MESUREE au sens de
references/data-hygiene.md -- a privilegier sur toute estimation.

Limite : un site a faible trafic peut ne pas avoir assez de donnees CrUX
(reponse 404 de l'API). Ce n'est pas une erreur du script : cela signifie
"pas assez d'utilisateurs reels pour produire une mesure fiable", et il faut
alors se rabattre sur du labo (PageSpeed/Lighthouse) en le disant clairement.

Cle API gratuite (une fois) :
1. https://console.cloud.google.com/apis/library/chromeuxreport.googleapis.com
   -> Activer l'API "Chrome UX Report API"
2. https://console.cloud.google.com/apis/credentials -> Creer une cle API
3. Aucun quota facture ; limite de debit generreuse pour un usage d'audit.

Usage:
    python crux_report.py --key <API_KEY> --origin https://example.com
    python crux_report.py --key <API_KEY> --url https://example.com/page --form-factor PHONE
    python crux_report.py --key <API_KEY> --origin https://example.com --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"

# Seuils officiels Google (verifies 2026-07) : "good" / "needs improvement" / "poor"
THRESHOLDS = {
    "largest_contentful_paint": (2500, 4000, "ms", "LCP"),
    "interaction_to_next_paint": (200, 500, "ms", "INP"),
    "cumulative_layout_shift": (0.10, 0.25, "", "CLS"),
    "first_contentful_paint": (1800, 3000, "ms", "FCP"),
    "experimental_time_to_first_byte": (800, 1800, "ms", "TTFB"),
}


def query_crux(api_key: str, target: dict, form_factor: str | None) -> dict | None:
    payload = dict(target)
    if form_factor:
        payload["formFactor"] = form_factor
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{ENDPOINT}?key={api_key}", data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 404:
            return None  # pas assez de donnees terrain, cas normal
        print(f"Erreur API {e.code}: {body[:400]}", file=sys.stderr)
        raise


def rate(metric_key: str, p75: float) -> str:
    if metric_key not in THRESHOLDS:
        return "?"
    good, poor, _unit, _label = THRESHOLDS[metric_key]
    if p75 <= good:
        return "BON"
    if p75 <= poor:
        return "A AMELIORER"
    return "MAUVAIS"


def extract(record: dict) -> list[dict]:
    out = []
    for key, metric in record.get("record", {}).get("metrics", {}).items():
        p75 = metric.get("percentiles", {}).get("p75")
        if p75 is None:
            continue
        p75_num = float(p75)
        _g, _p, unit, label = THRESHOLDS.get(key, (0, 0, "", key))
        out.append({
            "metric": key,
            "label": label,
            "p75": p75_num,
            "unit": unit,
            "rating": rate(key, p75_num),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--origin", help="Origine entiere, ex: https://example.com")
    group.add_argument("--url", help="URL de page precise")
    parser.add_argument("--key", required=True, help="Cle API Google (Chrome UX Report API)")
    parser.add_argument("--form-factor", choices=["PHONE", "DESKTOP", "TABLET"], default=None,
                        help="Par defaut : toutes plateformes confondues")
    parser.add_argument("--json", dest="json_out", default=None)
    args = parser.parse_args()

    target = {"origin": args.origin} if args.origin else {"url": args.url}
    label = args.origin or args.url

    record = query_crux(args.key, target, args.form_factor)
    if record is None:
        print(f"{label} : aucune donnee CrUX disponible.")
        print("Cela signifie un trafic Chrome reel insuffisant sur les 28 derniers jours,")
        print("pas un probleme de performance. Se rabattre sur une mesure labo")
        print("(PageSpeed Insights / Lighthouse) et le signaler comme telle dans le rapport.")
        return 0

    metrics = extract(record)
    ff = args.form_factor or "toutes plateformes"
    print(f"CrUX -- {label} ({ff}, 28 derniers jours, donnee terrain reelle)")
    print(f"{'Metrique':10s} {'p75':>10s}  Etat")
    print("-" * 36)
    for m in metrics:
        value = f"{m['p75']:.2f}" if m["unit"] == "" else f"{m['p75']:.0f}{m['unit']}"
        print(f"{m['label']:10s} {value:>10s}  {m['rating']}")

    failing = [m["label"] for m in metrics if m["rating"] == "MAUVAIS"]
    if failing:
        print(f"\n{len(failing)} metrique(s) en zone MAUVAIS : {', '.join(failing)}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump({"target": label, "form_factor": ff, "metrics": metrics, "measured": True},
                      f, indent=2, ensure_ascii=False)
        print(f"JSON ecrit : {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
