#!/usr/bin/env python3
"""PageSpeed Insights API v5: Lighthouse lab metrics plus the CrUX field data
that PSI embeds (page and origin), for one URL.

Lab (Lighthouse) = simulated, one run, indicative. Field (loadingExperience)
= real Chrome users, 28 days, p75 -- the data Core Web Vitals are judged on
(references/audit-framework.md). The report keeps them apart.

Key: environment variable PAGESPEED_API_KEY (Google Cloud API key with the
"PageSpeed Insights API" enabled). The key travels as ?key= (the documented
method); it is never printed, and errors are redacted.
Doc: https://developers.google.com/speed/docs/insights/v5/get-started

Usage:
    PAGESPEED_API_KEY=... python pagespeed.py https://example.com/ [--strategy mobile|desktop] [--json out.json]

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import envkeys  # noqa: E402

ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
ENV_KEY = "PAGESPEED_API_KEY"

# PSI field metric ids -> (label, unit, divisor). CLS is reported x100 by PSI.
FIELD_METRICS = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", "ms", 1),
    "INTERACTION_TO_NEXT_PAINT": ("INP", "ms", 1),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", "", 100),
    "FIRST_CONTENTFUL_PAINT_MS": ("FCP (diagnostic)", "ms", 1),
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": ("TTFB (diagnostic)", "ms", 1),
}
LAB_AUDITS = {
    "largest-contentful-paint": ("LCP (labo)", "ms"),
    "cumulative-layout-shift": ("CLS (labo)", ""),
    "total-blocking-time": ("TBT (labo)", "ms"),
    "first-contentful-paint": ("FCP (labo)", "ms"),
    "server-response-time": ("TTFB (labo)", "ms"),
}
CATEGORY_RATING = {"FAST": "BON", "AVERAGE": "A AMELIORER", "SLOW": "MAUVAIS"}


def run(url: str, key: str, strategy: str = "mobile", timeout: float = 90.0) -> dict:
    query = urllib.parse.urlencode({"url": url, "strategy": strategy, "category": "performance", "key": key})
    req = urllib.request.Request(f"{ENDPOINT}?{query}", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(body)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = " ".join(body.split())[:200]
        raise RuntimeError(envkeys.redact(f"PSI HTTP {e.code}: {message}", [key])) from None
    except Exception as e:  # timeout, DNS
        raise RuntimeError(envkeys.redact(f"PSI: {e}", [key])) from None


def _field(block: dict | None) -> dict | None:
    if not block or not block.get("metrics"):
        return None
    out = []
    for metric_id, (label, unit, divisor) in FIELD_METRICS.items():
        m = block["metrics"].get(metric_id)
        if not m or m.get("percentile") is None:
            continue
        out.append({"metric": metric_id, "label": label, "p75": m["percentile"] / divisor, "unit": unit,
                    "rating": CATEGORY_RATING.get(m.get("category", ""), "?")})
    return {"overall": CATEGORY_RATING.get(block.get("overall_category", ""), "?"), "metrics": out}


def extract(data: dict) -> dict:
    lh = data.get("lighthouseResult", {})
    score = lh.get("categories", {}).get("performance", {}).get("score")
    lab = []
    for audit_id, (label, unit) in LAB_AUDITS.items():
        a = lh.get("audits", {}).get(audit_id)
        if a and a.get("numericValue") is not None:
            lab.append({"metric": audit_id, "label": label, "value": a["numericValue"], "unit": unit})
    return {
        "url": data.get("id") or lh.get("finalUrl"),
        "strategy": (lh.get("configSettings") or {}).get("formFactor"),
        "performance_score": round(score * 100) if score is not None else None,
        "lab": lab,
        "field_page": _field(data.get("loadingExperience")),
        "field_origin": _field(data.get("originLoadingExperience")),
        "lighthouse_version": lh.get("lighthouseVersion"),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    parser.add_argument("--json", dest="json_out", default=None)
    args = parser.parse_args()
    key = envkeys.secret(ENV_KEY)
    if not key:
        print(f"Variable d'environnement {ENV_KEY} absente : rien a mesurer.", file=sys.stderr)
        return 2
    try:
        result = extract(run(args.url, key, args.strategy))
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(f"PSI {args.strategy} -- {result['url']} : score performance {result['performance_score']}")
    for m in result["lab"]:
        print(f"  {m['label']:18s} {m['value']:.2f}{m['unit']}")
    for name in ("field_page", "field_origin"):
        block = result[name]
        print(f"  {name}: " + ("aucune donnee terrain" if not block else block["overall"]))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
