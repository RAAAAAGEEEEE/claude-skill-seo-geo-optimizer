# Indexation — règles strictes à respecter

## La bonne méthode (par défaut, toujours)
Pour des pages web classiques : `sitemap.xml` à jour + soumission dans
Google Search Console + inspection d'URL manuelle ponctuelle pour les pages
importantes qui tardent à être crawlées. Google recrawle automatiquement via
le sitemap — c'est le mécanisme normal, il n'y a rien d'autre à construire.

## Interdictions (ne jamais faire, même si demandé sans plus de contexte)

### Google Indexing API
**Ne pas utiliser la Google Indexing API pour indexer des pages classiques.**
Cette API est réservée par Google à deux types de contenu uniquement :
`JobPosting` (offres d'emploi) et `BroadcastEvent` intégré dans une
`VideoObject` (diffusions en direct). L'utiliser pour autre chose (pages
marketing, articles de blog, pages produit) est un usage détourné des
conditions d'utilisation de l'API — le risque documenté est un flag comme
usage abusif pouvant mener à une coupure d'accès à l'API pour le compte
concerné. Si l'utilisateur demande "indexer plus vite via l'API Google" pour
un type de page hors `JobPosting`/`BroadcastEvent` : expliquer la
restriction, proposer le sitemap + Search Console à la place.

### Auto-submit hors sitemap
Ne pas coder de mécanisme qui pousse automatiquement des URLs vers Google
(ou tout moteur) en dehors du flux normal sitemap → crawl. Un script qui
"ping" Google à chaque nouvelle page, ou qui automatise des soumissions
répétées, s'apparente à du spam d'indexation et n'accélère pas
l'indexation de façon fiable — le sitemap fait déjà ce travail.

## Ce qui reste légitime et utile
- Mettre à jour `sitemap.xml` immédiatement après publication d'une page
  (voir [../scripts/generate_sitemap.py](../scripts/generate_sitemap.py)).
- Inspection d'URL manuelle dans Search Console pour une page précise qui ne
  s'indexe pas après plusieurs jours — c'est un outil de diagnostic/priorité,
  pas un mécanisme d'indexation de masse, et il reste manuel par design.
- Soumettre une URL à Brave Search (`https://search.brave.com/submit-url`)
  pour la visibilité dans le web search de Claude — voir
  [ai-crawlers.md](ai-crawlers.md#geo--soumission-brave-search). Ce n'est pas
  un équivalent de la Google Indexing API : Brave ne pénalise pas ce type de
  soumission ponctuelle, c'est son usage prévu.
