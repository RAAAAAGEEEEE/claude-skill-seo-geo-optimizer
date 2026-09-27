#!/usr/bin/env python3
"""Validate schema.org JSON-LD blocks against Google Search's documented
requirements, from an HTML file, a .json file or a URL.

Usage:
    python validate_schema.py <file.html|file.json|https://...> [...]

Three levels:
- ERROR   : invalid JSON, template placeholder left in, or a property that
            Google lists as *required* for the rich result is missing.
- WARNING : markup that is valid schema.org but earns nothing in Google
            (deprecated rich result, self-serving review stars), or a null
            value.
- OK      : nothing found.

Requirement tables follow Google Search Central's structured data pages
(checked 2026-09, see references/schema-templates.md for sources). A type
without a Google rich result (e.g. WebAPI) is not an error: it can still help
entity understanding, it just has no Google requirement to check.

Not a substitute for the Rich Results Test
(https://search.google.com/test/rich-results), which also renders JavaScript
and remains the reference for eligibility.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

# Google-required properties, per rich-result feature. "a|b" = one of.
REQUIRED: dict[str, list[str]] = {
    "Article": [],  # Google: no required property, all recommended
    "BreadcrumbList": ["itemListElement"],
    "ListItem": ["position"],
    "Dataset": ["name", "description"],
    "Event": ["name", "startDate", "location"],
    "JobPosting": ["title", "description", "datePosted", "hiringOrganization", "jobLocation|applicantLocationRequirements"],
    "LocalBusiness": ["name", "address"],
    "Organization": [],  # Google: no required property
    "Product": ["name", "offers|review|aggregateRating"],
    "Offer": ["price|priceSpecification"],
    "AggregateRating": ["ratingValue", "ratingCount|reviewCount"],
    "Review": ["author", "reviewRating"],
    "Recipe": ["name", "image"],
    "VideoObject": ["name", "thumbnailUrl", "uploadDate"],
    "FAQPage": ["mainEntity"],
    "QAPage": ["mainEntity"],
    "Question": ["name"],
    "ProfilePage": ["mainEntity"],
    "DiscussionForumPosting": ["author", "datePublished"],
    "SoftwareApplication": ["name", "offers", "aggregateRating|review"],
    "WebSite": ["name", "url"],
    "ImageObject": [],
}

# Subtypes checked with their parent's rules.
PARENT: dict[str, str] = {
    **{t: "Article" for t in (
        "NewsArticle", "BlogPosting", "ReportageNewsArticle", "AnalysisNewsArticle",
        "OpinionNewsArticle", "ReviewNewsArticle", "BackgroundNewsArticle", "TechArticle",
        "ScholarlyArticle", "SatiricalArticle", "LiveBlogPosting", "SocialMediaPosting",
    )},
    **{t: "LocalBusiness" for t in (
        "Restaurant", "Bakery", "CafeOrCoffeeShop", "BarOrPub", "FoodEstablishment", "HairSalon",
        "BeautySalon", "HealthAndBeautyBusiness", "Store", "ProfessionalService", "LegalService",
        "Attorney", "Dentist", "MedicalBusiness", "Physician", "AutoRepair", "AutomotiveBusiness",
        "LodgingBusiness", "Hotel", "HomeAndConstructionBusiness", "Electrician", "Plumber",
        "RealEstateAgent", "TravelAgency", "FinancialService", "SportsActivityLocation",
        "EntertainmentBusiness", "ChildCare", "DryCleaningOrLaundry", "EmploymentAgency",
    )},
    **{t: "Organization" for t in (
        "NewsMediaOrganization", "Corporation", "EducationalOrganization", "NGO", "OnlineStore",
        "OnlineBusiness", "GovernmentOrganization", "MedicalOrganization", "ResearchOrganization",
    )},
    **{t: "SoftwareApplication" for t in ("MobileApplication", "WebApplication", "VideoGame")},
    "ProductGroup": "Product",
    "AggregateOffer": "Offer",
}

# Valid schema.org, but no Google Search rich result any more (or a narrower
# use than people assume). Source: developers.google.com/search/updates,
# checked 2026-09-27. Keeping the markup is harmless; selling it as a Google
# gain is not.
NO_GOOGLE_RICH_RESULT: dict[str, str] = {
    "FAQPage": "rich result FAQ supprime pour tous les sites le 07/05/2026 (doc retiree le 15/06/2026)",
    "HowTo": "rich result HowTo retire le 13/09/2023",
    "ClaimReview": "retire de Google Search (annonce du 12/06/2025) ; reste lu par Fact Check Explorer",
    "SpecialAnnouncement": "rich result retire (effectif le 31/07/2025)",
    "EstimatedSalary": "rich result retire (annonce du 12/06/2025, doc retiree le 09/09/2025)",
    "Occupation": "rich result Estimated salary retire (09/09/2025)",
    "Vehicle": "rich result Vehicle listing retire (09/09/2025)",
    "Car": "rich result Vehicle listing retire (09/09/2025)",
    "Quiz": "rich result Practice problem retire (05/11/2025)",
    "Dataset": "sert uniquement a Dataset Search, pas a Google Search (05/11/2025)",
    "Course": "Course info retire (09/09/2025) ; seul le carrousel Course list reste documente",
}

SELF_SERVING_REVIEW_HOSTS = {"LocalBusiness", "Organization"}

JSONLD_BLOCK_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]*\}\}")


def extract_blocks_from_text(text: str, is_json: bool = False) -> list[str]:
    if is_json:
        return [text]
    return JSONLD_BLOCK_RE.findall(text)


def _types(node: dict) -> list[str]:
    t = node.get("@type")
    if isinstance(t, list):
        return [x for x in t if isinstance(x, str)]
    return [t] if isinstance(t, str) else []


def _rule_type(t: str) -> str:
    return PARENT.get(t, t)


def _missing(node: dict, spec: str) -> bool:
    return not any(node.get(alt) not in (None, "", []) for alt in spec.split("|"))


def _walk(node: dict, path: str, errors: list[str], warnings: list[str], found: list[str], nested_in: str | None) -> None:
    for t in _types(node):
        found.append(t)
        rule = _rule_type(t)
        for spec in REQUIRED.get(rule, []):
            if rule == "ListItem" and spec == "position" and nested_in != "BreadcrumbList":
                continue
            if _missing(node, spec):
                errors.append(f"{path}: {t} - propriété requise par Google manquante : {spec.replace('|', ' ou ')}")
        if t in NO_GOOGLE_RICH_RESULT or rule in NO_GOOGLE_RICH_RESULT:
            warnings.append(f"{path}: {t} - {NO_GOOGLE_RICH_RESULT.get(t) or NO_GOOGLE_RICH_RESULT[rule]}")
        if rule in SELF_SERVING_REVIEW_HOSTS and ("aggregateRating" in node or "review" in node):
            warnings.append(
                f"{path}: {t} - avis/notes sur sa propre entreprise (self-serving) : Google n'affiche pas "
                "d'étoiles pour LocalBusiness/Organization notés par eux-mêmes"
            )

    parent_type = _rule_type(_types(node)[0]) if _types(node) else nested_in
    for key, value in node.items():
        child_path = f"{path}.{key}"
        if value is None:
            warnings.append(f"{child_path}: valeur null (omettre la propriété plutôt que la déclarer vide)")
        elif isinstance(value, dict):
            _walk(value, child_path, errors, warnings, found, parent_type)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    _walk(item, f"{child_path}[{i}]", errors, warnings, found, parent_type)


def validate_blocks(blocks: list[str], label: str) -> list[dict]:
    """Validate raw JSON-LD strings. Returns one dict per block:
    {block, valid, error, warnings, types}. Reused by generate_report.py."""
    results = []
    for i, raw in enumerate(blocks):
        block_id = f"{label}#block{i}"
        errors: list[str] = []
        warnings: list[str] = []
        found: list[str] = []
        placeholders = PLACEHOLDER_RE.findall(raw)
        if placeholders:
            errors.append(f"{block_id}: gabarit non rempli {placeholders[:3]}")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            results.append({"block": block_id, "valid": False, "error": f"JSON invalide : {e}", "warnings": [], "types": []})
            continue

        roots = data if isinstance(data, list) else [data]
        for root in roots:
            if not isinstance(root, dict):
                continue
            context = str(root.get("@context", ""))
            if "schema.org" not in context:
                warnings.append(f"{block_id}: @context absent ou différent de https://schema.org")
            nodes = root.get("@graph") if isinstance(root.get("@graph"), list) else [root]
            for j, node in enumerate(nodes):
                if isinstance(node, dict):
                    _walk(node, f"{block_id}" + (f".@graph[{j}]" if node is not root else ""), errors, warnings, found, None)

        results.append({
            "block": block_id,
            "valid": not errors,
            "error": "; ".join(errors) if errors else None,
            "warnings": warnings,
            "types": sorted(set(found)),
        })
    return results


def _load(arg: str) -> tuple[str, list[str]]:
    if arg.startswith(("http://", "https://")):
        req = urllib.request.Request(arg, headers={"User-Agent": "Mozilla/5.0 (compatible; seo-geo-optimizer/2.0)"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return arg, extract_blocks_from_text(resp.read().decode("utf-8", errors="replace"))
    path = Path(arg)
    text = path.read_text(encoding="utf-8", errors="replace")
    return str(path), extract_blocks_from_text(text, is_json=path.suffix == ".json")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    total_ok = total_ko = total_warn = 0
    for arg in sys.argv[1:]:
        try:
            label, blocks = _load(arg)
        except (OSError, ValueError) as e:
            print(f"{arg}: illisible ({e})")
            total_ko += 1
            continue
        if not blocks:
            print(f"{label}: aucun bloc JSON-LD trouvé (si le site injecte le schema en JavaScript, "
                  "utiliser le Rich Results Test)")
            continue
        for r in validate_blocks(blocks, label):
            status = "OK       " if r["valid"] else "INVALIDE "
            print(f"  {status} {r['block']} ({', '.join(r['types']) or 'aucun @type'})")
            if r["error"]:
                for err in r["error"].split("; "):
                    print(f"      ERREUR  {err}")
            for w in r["warnings"]:
                print(f"      ALERTE  {w}")
            total_ok += r["valid"]
            total_ko += not r["valid"]
            total_warn += len(r["warnings"])

    print(f"\n{total_ok} bloc(s) valide(s), {total_ko} invalide(s)/en erreur, {total_warn} alerte(s)")
    return 1 if total_ko else 0


if __name__ == "__main__":
    sys.exit(main())
