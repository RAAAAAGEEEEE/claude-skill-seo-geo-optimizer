# Données structurées : statut Google et gabarits JSON-LD

Revu le 2026-09-28. Statuts **ESTABLISHED** d'après la
[galerie Google](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)
(maj 2026-06-15) et le [journal des mises à jour](https://developers.google.com/search/updates).

Règles :
- JSON-LD uniquement ; le balisage doit décrire ce qui est **visible** sur la
  page.
- Variables `{{ }}` à remplacer par de vraies données. Ne jamais inventer une
  valeur : omettre la propriété ou demander la donnée. `null` est une erreur,
  pas une absence.
- Valider avant de clore : `python scripts/validate_schema.py <fichier|URL>`
  puis le [Rich Results Test](https://search.google.com/test/rich-results)
  (seul à rendre le JavaScript).
- Google : aucun schema « spécial IA », et un ajout de JSON-LD n'a pas montré
  d'effet sur les citations (voir [evidence.md](evidence.md)). Le balisage sert
  aux rich results et à la désambiguïsation d'entité.

## Statut par type

| Type | Rich result Google au 2026-09-27 | Verdict |
|---|---|---|
| `Organization` (+ `logo`, `sameAs`) | Logo, panneau d'entité ; aucune propriété requise | Page d'accueil, toujours |
| `WebSite` (`name`, `alternateName`) | **Nom du site** dans les résultats (la sitelinks search box a disparu le 2024-11-21) | Page d'accueil, toujours |
| `Article` / `NewsArticle` / `BlogPosting` | Oui ; aucune propriété requise ; `author.url` ou `sameAs` recommandés | Tout contenu éditorial |
| `BreadcrumbList` | Oui, **desktop seulement** depuis le 2025-01-23 | Pages internes |
| `Product` | Snippet (page sans achat) : `name` + un de `offers`/`review`/`aggregateRating`. Merchant listing (achat possible) : prix, devise, disponibilité | E-commerce ; fiches produit sans prix : pas de rich result, balisage d'entité seulement |
| `LocalBusiness` (sous-type précis) | Oui ; `name` + `address` requis | Commerce local |
| `Event`, `JobPosting`, `VideoObject`, `Recipe`, `QAPage`, `DiscussionForumPosting`, `ProfilePage` | Oui | Selon le site |
| `Review` / `AggregateRating` | Oui, **sauf** avis sur sa propre entreprise (LocalBusiness/Organization) ; avis faux ou incités non déclarés interdits (2026-07-24) | Jamais d'étoiles auto-attribuées |
| `Dataset` | **Dataset Search uniquement**, plus Google Search (2025-11-05) | Utile pour un site de données, sans effet SERP |
| `FAQPage` | **Supprimé pour tous le 2026-05-07**, doc retirée le 2026-06-15 | Laisser si présent (sans effet négatif), ne plus en ajouter comme gain Google |
| `HowTo` | Retiré le 2023-09-13 | Idem |
| `ClaimReview`, `SpecialAnnouncement`, `EstimatedSalary`, Course info, Vehicle listing, Learning video, Practice problem | Retirés (2025) ; ClaimReview reste lu par Fact Check Explorer | Ne pas vendre comme gain SERP |
| `Speakable` | Bêta, US anglais, Google Home | Hors sujet en France |
| `DefinedTermSet` / `DefinedTerm` | **Aucun** rich result (absent de la galerie) ; vocabulaire stable de schema.org | Facultatif sur un glossaire, généré depuis les mêmes données que le HTML ([glossary.md](glossary.md)) |

Google et Bing restent libres d'utiliser tout schema.org valide pour
comprendre une page ; « pas de rich result » ne veut pas dire « nuisible ».
Supprimer un balisage retiré n'est pas nécessaire (Google, 2023-08-08).

## Organization (page d'accueil)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "{{url_racine}}/#organization",
  "name": "{{marque}}",
  "url": "{{url_racine}}",
  "logo": "{{url_logo_carre_min_112px}}",
  "sameAs": ["{{profil_officiel_1}}", "{{element_wikidata_si_existe}}"]
}
</script>
```

## WebSite (nom du site, page d'accueil du domaine)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{{nom_du_site}}",
  "alternateName": "{{variante_courte}}",
  "url": "{{url_racine}}/"
}
</script>
```

## LocalBusiness (choisir le sous-type : Restaurant, Bakery, HairSalon...)
Pas d'`aggregateRating` ici : des notes que l'entreprise s'attribue ne
donnent pas d'étoiles et violent les consignes si elles sont sollicitées.
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "{{Restaurant|Bakery|HairSalon|LocalBusiness}}",
  "@id": "{{url_site}}/#business",
  "name": "{{nom}}",
  "url": "{{url_site}}",
  "image": "{{url_image}}",
  "telephone": "{{tel}}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{{rue}}",
    "addressLocality": "{{ville}}",
    "postalCode": "{{cp}}",
    "addressCountry": "FR"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": {{lat}}, "longitude": {{lng}} },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "{{h_ouv}}", "closes": "{{h_ferm}}"
  }]
}
</script>
```

## NewsArticle / Article (auteur désambiguïsé)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{{titre}}",
  "image": ["{{url_image_16x9_min_1200px}}"],
  "datePublished": "{{date_publication_iso8601}}",
  "dateModified": "{{date_modification_iso8601}}",
  "author": {
    "@type": "Person",
    "name": "{{nom_auteur}}",
    "url": "{{url_page_auteur}}"
  },
  "publisher": { "@id": "{{url_racine}}/#organization" }
}
</script>
```

## Product (snippet : page d'information, pas d'achat)
Si la page vend le produit, suivre les exigences merchant listing
(prix, devise, disponibilité, et idéalement politique de retour et de
livraison au niveau Organization).
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{nom_produit}}",
  "image": ["{{url_image}}"],
  "description": "{{description}}",
  "brand": { "@type": "Brand", "name": "{{marque}}" },
  "offers": {
    "@type": "Offer",
    "url": "{{url_page_vendeur}}",
    "price": "{{prix}}",
    "priceCurrency": "EUR",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

## BreadcrumbList
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "{{accueil}}", "item": "{{url_accueil}}" },
    { "@type": "ListItem", "position": 2, "name": "{{page_courante}}", "item": "{{url_page_courante}}" }
  ]
}
</script>
```

## DefinedTermSet (glossaire, facultatif)
Ne pas l'écrire à la main : `python scripts/glossary_check.py build --terms
termes.csv --set-name "Lexique" --set-url {{url_du_lexique}}` produit ce
bloc **et** le `<dl>` visible depuis les mêmes lignes, et refuse une ligne
sans définition.
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DefinedTermSet",
  "@id": "{{url_du_lexique}}#lexique",
  "name": "{{nom_du_lexique}}",
  "url": "{{url_du_lexique}}",
  "hasDefinedTerm": [{
    "@type": "DefinedTerm",
    "@id": "{{url_du_lexique}}#{{ancre}}",
    "name": "{{terme}}",
    "description": "{{definition_identique_au_texte_visible}}",
    "url": "{{url_du_lexique}}#{{ancre}}",
    "inDefinedTermSet": { "@id": "{{url_du_lexique}}#lexique" }
  }]
}
</script>
```
