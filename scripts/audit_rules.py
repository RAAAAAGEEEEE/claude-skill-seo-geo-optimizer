#!/usr/bin/env python3
"""Single catalogue of the audit rules: code, priority, evidence label,
source, fix hint -- and the per-page checks that produce them.

Used by generate_report.py (per-page issues, unchanged wording) and by
run_audit.py (prioritized fix list, diffs between runs). A rule lives here
once; the reports only format it.

Priorities follow the order of SKILL.md: access -> indexing and snippet ->
content in the HTML -> evidence -> markup -> performance.
- P0 : the site, or a crawler that cites, cannot read the pages.
- P1 : indexing or coherence broken on real pages (5xx, noindex in the
       sitemap, canonical/hreflang contradictions, broken links, orphans).
- P2 : quality and hygiene (duplicates, anchors, depth, cocoon structure).

Labels: ESTABLISHED (primary documentation), SUPPORTED (independent study
with data), CLAIMED (practitioner or vendor) -- references/data-hygiene.md.
A CLAIMED rule never gets P0/P1 on its own.

Stdlib only.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

G = "https://developers.google.com/search/docs"


@dataclass(frozen=True)
class Rule:
    priority: str
    category: str
    title: str
    label: str
    source: str
    fix: str


RULES: dict[str, Rule] = {
    # --- Access -------------------------------------------------------------
    "home-unreachable": Rule("P0", "acces", "Page d'accueil inaccessible ou hors 200", "ESTABLISHED",
                             f"{G}/crawling-indexing/http-network-errors",
                             "Rétablir une réponse 200 sur l'accueil avant tout autre chantier."),
    "robots-unreadable": Rule("P0", "acces", "robots.txt en 5xx/429 ou injoignable : tout est interdit aux crawlers",
                              "ESTABLISHED", "https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec",
                              "Servir robots.txt en 200 (ou 404 si aucune règle)."),
    "crawler-blocked": Rule("P0", "acces", "Crawler de recherche/citation bloqué (robots.txt ou CDN)", "ESTABLISHED",
                            "references/ai-crawlers.md",
                            "Décision produit : ouvrir le crawler dans robots.txt ou la règle CDN/WAF "
                            "(references/cloudflare-ai-access.md). Ne pas trancher seul."),
    "googlebot-disallowed": Rule("P0", "acces", "URL du sitemap interdite à Googlebot par robots.txt", "ESTABLISHED",
                                 "https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec",
                                 "Retirer l'URL du sitemap ou lever la règle Disallow."),
    # --- Indexing / HTTP ----------------------------------------------------
    "http-5xx": Rule("P1", "indexation", "Erreur serveur 5xx", "ESTABLISHED",
                     f"{G}/crawling-indexing/http-network-errors",
                     "Corriger l'erreur ; une URL inconnue doit répondre 404/410, jamais 5xx."),
    "http-not-200": Rule("P1", "indexation", "Page auditée hors 200", "ESTABLISHED",
                         f"{G}/crawling-indexing/http-network-errors",
                         "Normal seulement si l'URL ne doit pas exister : alors la retirer des liens et du sitemap."),
    "unreachable": Rule("P1", "indexation", "Page inaccessible (DNS, TLS, délai)", "ESTABLISHED",
                        f"{G}/crawling-indexing/http-network-errors", "Vérifier le serveur et le certificat."),
    "unknown-url-5xx": Rule("P1", "indexation", "URL inexistante qui répond 5xx", "ESTABLISHED",
                            f"{G}/crawling-indexing/http-network-errors",
                            "Renvoyer 404 (notFound) sur une ressource inconnue au lieu de lever une erreur."),
    "unknown-url-200": Rule("P1", "indexation", "URL inexistante qui répond 200 (soft 404)", "ESTABLISHED",
                            f"{G}/crawling-indexing/http-network-errors#soft-404-errors",
                            "Répondre 404/410 sur une URL inconnue."),
    "redirect-temporary": Rule("P1", "indexation", "Redirection temporaire (302/303/307)", "ESTABLISHED",
                               f"{G}/crawling-indexing/301-redirects",
                               "Utiliser 301/308 si le déplacement est définitif."),
    "noindex": Rule("P1", "indexation", "noindex (meta ou X-Robots-Tag)", "ESTABLISHED",
                    f"{G}/crawling-indexing/block-indexing",
                    "Retirer noindex si la page doit être trouvée (elle est alors aussi absente des AI Overviews)."),
    "noindex-linked": Rule("P2", "indexation", "Page en noindex liée en interne : vérifier que c'est voulu", "ESTABLISHED",
                           f"{G}/crawling-indexing/block-indexing",
                           "Voulu pour une page vide ou utilitaire ; sinon retirer noindex et l'ajouter au sitemap."),
    "nosnippet": Rule("P1", "indexation", "nosnippet ou max-snippet:0 : pas d'extrait ni d'usage dans AI Overviews/AI Mode",
                      "ESTABLISHED", f"{G}/appearance/ai-features", "Retirer la directive si ce n'est pas voulu."),
    # --- Sitemap / canonical / hreflang coherence ---------------------------
    "sitemap-missing": Rule("P1", "coherence", "Aucun sitemap trouvé (robots.txt ni /sitemap.xml)", "ESTABLISHED",
                            f"{G}/crawling-indexing/sitemaps/build-sitemap",
                            "Publier un sitemap et le déclarer dans robots.txt (scripts/generate_sitemap.py)."),
    "sitemap-non-200": Rule("P1", "coherence", "URL du sitemap hors 200 ou redirigée", "ESTABLISHED",
                            f"{G}/crawling-indexing/sitemaps/build-sitemap",
                            "Ne lister que des URLs canoniques qui répondent 200 (voir le sitemap proposé)."),
    "sitemap-noindex": Rule("P1", "coherence", "URL du sitemap en noindex", "ESTABLISHED",
                            f"{G}/crawling-indexing/sitemaps/build-sitemap",
                            "Retirer du sitemap ou lever le noindex : les deux signaux se contredisent."),
    "sitemap-canonical-elsewhere": Rule("P1", "coherence", "URL du sitemap qui se canonicalise vers une autre URL",
                                        "ESTABLISHED", f"{G}/crawling-indexing/consolidate-duplicate-urls",
                                        "Lister l'URL canonique dans le sitemap, pas la variante."),
    "sitemap-foreign-host": Rule("P2", "coherence", "URL du sitemap sur un autre hôte", "ESTABLISHED",
                                 f"{G}/crawling-indexing/sitemaps/build-sitemap",
                                 "Un sitemap ne couvre que son hôte, sauf vérification croisée dans Search Console."),
    "sitemap-lastmod-uniform": Rule("P2", "coherence", "lastmod identique sur toutes les URLs (date de génération ?)",
                                    "ESTABLISHED", f"{G}/crawling-indexing/sitemaps/build-sitemap",
                                    "N'écrire lastmod que s'il reflète une vraie modification significative."),
    "sitemap-lastmod-future": Rule("P2", "coherence", "lastmod dans le futur", "ESTABLISHED",
                                   f"{G}/crawling-indexing/sitemaps/build-sitemap", "Corriger la date."),
    "not-in-sitemap": Rule("P2", "coherence", "Page indexable liée en interne mais absente du sitemap", "ESTABLISHED",
                           f"{G}/crawling-indexing/sitemaps/overview",
                           "L'ajouter au sitemap si elle doit être trouvée, sinon la passer en noindex."),
    "canonical-missing": Rule("P1", "coherence", "canonical manquant", "ESTABLISHED",
                              f"{G}/crawling-indexing/consolidate-duplicate-urls",
                              "Ajouter <link rel=canonical> auto-référent sur chaque page indexable."),
    "canonical-to-bad-target": Rule("P1", "coherence", "canonical vers une URL non indexable (hors 200, redirigée ou noindex)",
                                    "ESTABLISHED", f"{G}/crawling-indexing/consolidate-duplicate-urls",
                                    "Pointer le canonical vers une URL 200 indexable."),
    "hreflang-error": Rule("P1", "coherence", "hreflang incohérent (auto-référence ou lien retour manquant)",
                           "ESTABLISHED", f"{G}/specialty/international/localized-versions",
                           "Chaque version liste toutes les versions, elle-même comprise, et réciproquement."),
    "hreflang-bad-target": Rule("P1", "coherence", "hreflang vers une URL hors 200 ou noindex", "ESTABLISHED",
                                f"{G}/specialty/international/localized-versions",
                                "Ne déclarer que des versions 200 indexables."),
    "hreflang-lang-mismatch": Rule("P1", "coherence", "Langue déclarée (hreflang) ≠ langue de la page (lang)",
                                   "ESTABLISHED", f"{G}/specialty/international/localized-versions",
                                   "Une URL de langue qui sert une autre langue est un doublon : 404 ou noindex "
                                   "tant qu'elle n'est pas traduite."),
    "hreflang-no-x-default": Rule("P2", "coherence", "Pas de x-default (recommandé, pas obligatoire)", "ESTABLISHED",
                                  f"{G}/specialty/international/localized-versions",
                                  "Ajouter x-default vers la page de choix de langue ou la langue par défaut."),
    # --- On-page ------------------------------------------------------------
    "title-missing": Rule("P1", "on-page", "title manquant", "ESTABLISHED", f"{G}/appearance/title-link",
                          "Ajouter un <title> unique et descriptif."),
    "description-missing": Rule("P2", "on-page", "meta description manquante", "ESTABLISHED", f"{G}/appearance/snippet",
                                "Ajouter une description propre à la page (Google peut la réécrire)."),
    "title-duplicate": Rule("P2", "on-page", "title dupliqué entre pages", "ESTABLISHED", f"{G}/appearance/title-link",
                            "Donner à chaque page un title propre."),
    "description-duplicate": Rule("P2", "on-page", "meta description dupliquée entre pages", "ESTABLISHED",
                                  f"{G}/appearance/snippet", "Rédiger une description propre à chaque page."),
    "h1-missing": Rule("P2", "on-page", "aucun H1", "CLAIMED", f"{G}/fundamentals/seo-starter-guide",
                       "Convention d'outils : Google n'exige pas de H1 ; un titre principal visible aide le lecteur."),
    "h1-multiple": Rule("P2", "on-page", "plusieurs H1", "CLAIMED", f"{G}/fundamentals/seo-starter-guide",
                        "Convention d'outils, pas une exigence Google ; ne corriger que si la hiérarchie est confuse."),
    "lang-missing": Rule("P2", "on-page", "attribut lang absent sur <html>", "ESTABLISHED",
                         f"{G}/specialty/international/managing-multi-regional-sites",
                         "Google ignore lang (il lit le contenu) ; Bing et l'accessibilité l'utilisent : l'ajouter."),
    "thin-page": Rule("P2", "contenu", "Page indexable quasi vide (risque de soft 404)", "ESTABLISHED",
                      f"{G}/crawling-indexing/http-network-errors#soft-404-errors",
                      "noindex tant que la page est vide, ou la remplir. Seuil de mots : heuristique du skill."),
    "schema-invalid": Rule("P1", "schema", "JSON-LD invalide ou propriété requise manquante", "ESTABLISHED",
                           f"{G}/appearance/structured-data/sd-policies",
                           "Corriger le bloc puis relancer validate_schema.py."),
    # --- Internal linking ---------------------------------------------------
    "broken-internal-link": Rule("P1", "maillage", "Lien interne vers une URL en erreur (4xx/5xx)", "ESTABLISHED",
                                 f"{G}/crawling-indexing/links-crawlable",
                                 "Corriger ou retirer le lien."),
    "orphan-page": Rule("P1", "maillage", "Page du sitemap sans aucun lien interne entrant (orpheline)", "ESTABLISHED",
                        f"{G}/crawling-indexing/links-crawlable",
                        "La lier depuis au moins une page pertinente (idéalement un lien contextuel)."),
    "link-to-redirect": Rule("P2", "maillage", "Lien interne vers une URL qui redirige", "ESTABLISHED",
                             f"{G}/crawling-indexing/301-redirects",
                             "Pointer directement vers l'URL finale."),
    "non-crawlable-link": Rule("P2", "maillage", "<a> sans href exploitable (javascript:, absent)", "ESTABLISHED",
                               f"{G}/crawling-indexing/links-crawlable",
                               "Utiliser <a href=\"/chemin\"> pour tout lien de navigation."),
    "empty-anchor": Rule("P2", "maillage", "Lien interne sans texte d'ancre (ni alt d'image)", "ESTABLISHED",
                         f"{G}/crawling-indexing/links-crawlable",
                         "Donner un texte d'ancre descriptif (ou un alt à l'image liée)."),
    "generic-anchor": Rule("P2", "maillage", "Ancre générique (« cliquez ici », « en savoir plus »)", "ESTABLISHED",
                           f"{G}/crawling-indexing/links-crawlable",
                           "Décrire la page cible dans l'ancre."),
    "deep-page": Rule("P2", "maillage", "Page à plus de 3 clics de l'accueil", "CLAIMED",
                      "references/french-practitioners.md",
                      "Seuil de convention (non documenté par Google) : rapprocher les pages importantes."),
    "no-contextual-inlink": Rule("P2", "maillage", "Page liée uniquement depuis la navigation (aucun lien contextuel entrant)",
                                 "CLAIMED", "references/french-practitioners.md",
                                 "Ajouter un lien depuis le corps d'une page du même sujet (méthode du cocon)."),
    "no-contextual-outlink": Rule("P2", "maillage", "Page sans lien contextuel sortant", "CLAIMED",
                                  "references/french-practitioners.md",
                                  "Lier dans le texte vers la page mère et les pages sœurs pertinentes."),
    "cocoon-no-uplink": Rule("P2", "maillage", "Page fille sans lien vers sa page mère (cocon)", "CLAIMED",
                             "references/french-practitioners.md",
                             "Ajouter un lien contextuel montant vers la page mère de la rubrique."),
    "anchor-repeated": Rule("P2", "maillage", "Même ancre exacte pour presque tous les liens contextuels vers une page",
                            "CLAIMED", "references/french-practitioners.md",
                            "Varier les ancres (termes proches, entités) sans bourrage de mots-clés."),
    "internal-nofollow": Rule("P2", "maillage", "Lien interne en nofollow", "ESTABLISHED",
                              f"{G}/crawling-indexing/qualify-outbound-links",
                              "nofollow qualifie les liens sortants ; pour une page interne à ne pas explorer, Google "
                              "renvoie à robots.txt (disallow). Sinon, laisser le lien suivi."),
    # --- Performance / measurement -----------------------------------------
    "cwv-poor": Rule("P1", "performance", "Core Web Vital en zone mauvaise (p75)", "ESTABLISHED",
                     "https://web.dev/articles/vitals", "Traiter la métrique en cause (LCP, INP ou CLS)."),
    "cwv-needs-improvement": Rule("P2", "performance", "Core Web Vital à améliorer (p75)", "ESTABLISHED",
                                  "https://web.dev/articles/vitals", "Traiter la métrique en cause."),
    "lab-performance-low": Rule("P2", "performance", "Score Lighthouse performance < 50 (labo, mobile)", "ESTABLISHED",
                                "https://developers.google.com/speed/docs/insights/v5/about",
                                "Mesure labo : indicative, la donnée terrain (CrUX) prime."),
    "gsc-no-impressions": Rule("P2", "mesure", "Page du sitemap sans impression Search Console sur la période",
                               "ESTABLISHED", "https://support.google.com/webmasters/answer/7576553",
                               "Normal si récente ; sinon inspecter l'URL (indexation)."),
    "indexnow-key-invalid": Rule("P2", "indexation", "Clé IndexNow non publiée à la racine ou incorrecte", "ESTABLISHED",
                                 "https://www.indexnow.org/documentation",
                                 "Publier /<clé>.txt à la racine, contenant uniquement la clé."),
}


def finding_id(code: str, scope: str = "") -> str:
    """Stable identifier across runs: same code + same scope = same finding."""
    return hashlib.sha1(f"{code}|{scope}".encode("utf-8")).hexdigest()[:12]


def page_checks(signals, schema_results: list[dict]) -> list[dict]:
    """Per-page checks. Each item: {code, kind: issue|note, message}.

    `message` keeps the historical wording of generate_report.py.
    """
    s = signals
    out: list[dict] = []

    def add(code: str, message: str, kind: str = "issue") -> None:
        out.append({"code": code, "kind": kind, "message": message})

    if s.error and s.http_status is None:
        add("unreachable", f"inaccessible : {s.error}")
        return out
    if s.http_status and s.http_status >= 500:
        add("http-5xx", f"HTTP {s.http_status} : erreur serveur (une URL inconnue doit repondre 404/410, "
                        "jamais 5xx ; des 5xx repetes ralentissent le crawl)")
    elif s.http_status and s.http_status != 200:
        add("http-not-200", f"HTTP {s.http_status} (normal seulement si l'URL ne doit pas exister)")
    for code, target in s.redirects:
        if code in (302, 303, 307):
            add("redirect-temporary",
                f"redirection temporaire {code} vers {target} : utiliser 301/308 si le deplacement est definitif")
    if s.noindex:
        add("noindex", "noindex (meta robots ou X-Robots-Tag) : page exclue de Google, donc des AI Overviews/AI Mode")
    if s.nosnippet:
        add("nosnippet", "nosnippet ou max-snippet:0 : pas d'extrait ni d'usage dans AI Overviews/AI Mode")
    if s.http_status == 200 and s.is_html:
        if not s.title:
            add("title-missing", "title manquant")
        if not s.description:
            add("description-missing", "meta description manquante")
        if not s.canonical:
            add("canonical-missing", "canonical manquant")
        if s.h1_count == 0:
            add("h1-missing", "aucun H1")
        elif s.h1_count > 1:
            add("h1-multiple", f"{s.h1_count} H1 (un seul attendu)")
        if not s.html_lang:
            add("lang-missing", "attribut lang absent sur <html>")
    for r in schema_results:
        if not r["valid"]:
            add("schema-invalid", f"schema invalide ({r['block']}) : {r['error']}")

    final = s.final_url or s.url
    if s.canonical and s.canonical.rstrip("/") != final.rstrip("/"):
        add("canonical-elsewhere", f"canonical vers une autre URL : {s.canonical}", "note")
    if s.has_data_nosnippet:
        add("data-nosnippet", "data-nosnippet present : ces passages sont exclus des extraits et des AI Overviews", "note")
    for r in schema_results:
        for w in r.get("warnings", []):
            add("schema-warning", f"schema : {w}", "note")
    return out


def hreflang_checks(signals_list) -> list[dict]:
    """Self-reference, x-default and return links between the audited pages.

    Only pairs where both pages are in this run can be checked; targets outside
    the run are skipped, not reported as errors. Items: {code, url, message}.
    """
    out: list[dict] = []
    by_url = {s.final_url or s.url: s for s in signals_list}
    for s in signals_list:
        links = s.hreflang_links
        if not links:
            continue
        me = s.final_url or s.url
        if not any(href == me for _lang, href in links):
            out.append({"code": "hreflang-error", "url": me, "message": f"{me} : pas de balise hreflang vers elle-meme"})
        if not any(lang.lower() == "x-default" for lang, _href in links):
            out.append({"code": "hreflang-no-x-default", "url": me,
                        "message": f"{me} : pas de x-default (recommande, pas obligatoire)"})
        for lang, href in links:
            if href == me or href not in by_url:
                continue
            back = by_url[href].hreflang_links
            if not any(back_href == me for _l, back_href in back):
                out.append({"code": "hreflang-error", "url": me,
                            "message": f"{me} reference {href} (hreflang={lang}) sans lien retour"})
    return out
