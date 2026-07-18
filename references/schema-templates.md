# Templates JSON-LD (paste-ready)

Variables entre `{{ }}` à remplacer par les vraies données au moment de la
génération. Ne jamais inventer une valeur manquante — utiliser `null` ou
demander la donnée à l'utilisateur plutôt que de la halluciner.

Toujours valider le bloc généré avec `scripts/validate_schema.py` ou le
Rich Results Test (https://search.google.com/test/rich-results) avant de
considérer la tâche terminée.

## LocalBusiness (choisir le sous-type : Restaurant, Bakery, HairSalon...)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "{{Restaurant|Bakery|HairSalon|LocalBusiness}}",
  "name": "{{nom}}",
  "image": "{{url_image}}",
  "@id": "{{url_site}}",
  "url": "{{url_site}}",
  "telephone": "{{tel}}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{{rue}}",
    "addressLocality": "{{ville}}",
    "postalCode": "{{cp}}",
    "addressCountry": "FR"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": "{{lat}}", "longitude": "{{lng}}" },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "opens": "{{h_ouv}}", "closes": "{{h_ferm}}"
  }],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{note}}", "reviewCount": "{{nb_avis}}"
  }
}
</script>
```

## Organization + sameAs (domaine racine)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{{marque}}",
  "url": "{{url_racine}}",
  "logo": "{{url_logo}}",
  "sameAs": ["{{lien_linkedin}}","{{lien_x}}","{{lien_wikidata_si_dispo}}"]
}
</script>
```

## FAQPage
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "{{question}}",
    "acceptedAnswer": { "@type": "Answer", "text": "{{réponse}}" }
  }]
}
</script>
```

## Product
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{nom_produit}}",
  "image": ["{{url_image}}"],
  "description": "{{description}}",
  "sku": "{{sku}}",
  "brand": { "@type": "Brand", "name": "{{marque}}" },
  "offers": {
    "@type": "Offer",
    "url": "{{url_produit}}",
    "priceCurrency": "EUR",
    "price": "{{prix}}",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{note}}", "reviewCount": "{{nb_avis}}"
  }
}
</script>
```

## Article + author (E-E-A-T)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{titre}}",
  "image": ["{{url_image}}"],
  "datePublished": "{{date_publication}}",
  "dateModified": "{{date_modification}}",
  "author": {
    "@type": "Person",
    "name": "{{nom_auteur}}",
    "url": "{{url_page_auteur}}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{{marque}}",
    "logo": { "@type": "ImageObject", "url": "{{url_logo}}" }
  }
}
</script>
```

## HowTo
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{{titre_tutoriel}}",
  "step": [
    { "@type": "HowToStep", "name": "{{étape_1}}", "text": "{{détail_1}}" },
    { "@type": "HowToStep", "name": "{{étape_2}}", "text": "{{détail_2}}" }
  ]
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
