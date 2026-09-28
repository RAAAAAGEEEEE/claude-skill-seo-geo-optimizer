# Glossaire / lexique : quand il aide, comment le construire

Revu le 2026-09-28. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
Script : [`../scripts/glossary_check.py`](../scripts/glossary_check.py).

## Verdict

| Question | Réponse | Niveau |
|---|---|---|
| Un glossaire aide-t-il le SEO ? | Oui, **sous conditions**. Aucune doc Google ne vise les glossaires. Les règles générales s'appliquent : contenu utile et original, un lien vers chaque page importante, ancres descriptives. | ESTABLISHED (règles générales) ; « le glossaire gagne en soi » : CLAIMED |
| Aide-t-il à être cité par les IA ? | **Non démontré.** Aucune étude indépendante ne le mesure. La plus grande étude publique par type de contenu n'a même pas de catégorie glossaire. Les chiffres « 3 à 5 fois plus cités » circulent sans méthode. | CLAIMED, invérifiable |
| Le balisage `DefinedTerm` sert-il ? | Vocabulaire stable de schema.org, mais **aucun rich result Google** et aucun effet mesuré sur les citations. Facultatif. | ESTABLISHED (absence de la galerie) |

Pourquoi le skill le propose quand même : un site de référence ou un SaaS
emploie un vocabulaire que ses visiteurs cherchent (« qu'est-ce que… »).
Définir chaque terme une fois, à une adresse stable, puis y lier les
premières mentions, c'est du maillage descriptif (ESTABLISHED) et une page
utile, pas une astuce « pour l'IA ».

## Sources

| Affirmation | Étiquette | Source (date) |
|---|---|---|
| `DefinedTerm` et `DefinedTermSet` sont dans le core de schema.org (pas en pending). Propriétés : `termCode`, `inDefinedTermSet`, `hasDefinedTerm` | ESTABLISHED | [DefinedTerm](https://schema.org/DefinedTerm), [DefinedTermSet](https://schema.org/DefinedTermSet) (v30.1, 2026-09-16) |
| Galerie Google : 25 fonctionnalités, ni DefinedTerm ni « glossary » ni « definition » | ESTABLISHED | [search gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery) (maj 2026-06-15) |
| Ne pas baliser un contenu invisible ; le balisage représente la page | ESTABLISHED | [structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) (maj 2026-07-10) |
| Pas de schema spécial pour les fonctions IA ; ne pas recycler ce que d'autres ont déjà dit (« commodity content ») | ESTABLISHED | [guide IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) (maj 2026-07-10) |
| Google n'indexe généralement pas les fragments d'URL : `#terme` n'est pas une page à part | ESTABLISHED | [URL structure](https://developers.google.com/search/docs/crawling-indexing/url-structure) (maj 2025-12-10) |
| Ancres descriptives et concises ; chaque page importante reçoit au moins un lien | ESTABLISHED | [link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) (maj 2025-12-10) |
| Générer beaucoup de pages sans valeur ajoutée, par IA ou par assemblage, relève du *scaled content abuse* ; pages quasi identiques sur des variantes : *doorways* | ESTABLISHED | [spam policies](https://developers.google.com/search/docs/essentials/spam-policies) (maj 2026-08-28) ; [contenu IA](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) (maj 2025-12-10) |
| Canonical réservé aux doublons ; une vraie page de définition n'est pas un doublon du hub | ESTABLISHED | [canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) (maj 2026-07-10) |
| Glossaire multilingue : hreflang réciproque par terme | ESTABLISHED | [versions localisées](https://developers.google.com/search/docs/specialty/international/localized-versions) (maj 2026-09-21) |
| 47,3 % des requêtes « définition » déclenchent un AI Overview, contre 20,5 % en moyenne (146 M de SERP, US desktop) | CLAIMED, méthode publiée | [Ahrefs](https://ahrefs.com/blog/ai-overview-triggers/) (2025-11-10) |
| Avec un résumé IA, 8 % de clic sur un résultat contre 15 % sans : une définition nue risque le zéro clic | SUPPORTED | [Pew](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/) (2025-07-22) |
| 1,06 M de citations IA classées en 11 types : aucune catégorie glossaire | CLAIMED, méthode partielle | [Wix / Peec AI](https://www.wix.com/studio/ai-search-lab/research/content-types-most-cited-by-llms) (2026-03-23) |
| Reprendre Wikipedia impose attribution et CC BY-SA 4.0 | ESTABLISHED | [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content) (consulté 2026-09-28) |
| ISO interdit la copie de ses normes, y compris ISO 8373:2021 (vocabulaire de la robotique, en révision) | ESTABLISHED | [ISO copyright](https://www.iso.org/copyright.html) ; [ISO 8373](https://www.iso.org/standard/75539.html) (consultés 2026-09-28) |

**Sites de référence observés** (HTML brut lu le 2026-09-28) : Ahrefs, MDN,
Moz, Investopedia, CNIL, JDN, Larousse. Modèle dominant : un **hub** avec une
définition courte et un lien, plus **une URL par terme** qui a sa propre
intention. **Aucun** n'utilise `DefinedTerm`. Leur visibilité n'a pas été
mesurée : ce sont des exemples de structure, pas des preuves d'efficacité.

## Recette (ce que le skill propose)

1. **Partir des données du site** : les termes que le site emploie déjà.
   `glossary_check.py suggest` relève les sigles et les `<abbr>`/`<dfn>`
   présents sur plusieurs pages. Tri humain obligatoire.
2. **Hub** `/lexique` (ou `/glossaire`) en HTML statique : une définition de
   1 à 2 phrases et une ancre (`id`) par terme.
3. **Une URL par terme** seulement si le terme a une intention de recherche
   propre **et** un contenu propre (contexte, distinctions, exemples,
   données maison, sources). Sinon, l'ancre sur le hub suffit : un `#terme`
   n'est pas indexé à part (ESTABLISHED). Seuils de longueur : CLAIMED,
   jamais imposés.
4. **Définitions originales**, rédigées ou relues par un humain, avec date et
   auteur. Pas de génération en masse, pas de copie ISO. Wikipedia seulement
   sous CC BY-SA, et cela reste du contenu banal (ESTABLISHED).
5. **Maillage** : lier la **première** mention d'un terme dans un article vers
   sa définition, et de la définition vers les pages approfondies. Pas
   d'auto-lien sur chaque occurrence ; varier les ancres (principe
   ESTABLISHED ; « une fois par page » : CLAIMED). Un lien de menu vers le
   hub ne compte pas comme lien vers la définition.
   `glossary_check.py audit --site` liste ces occasions ; il **n'insère
   rien**.
6. **Page trop mince** : l'enrichir, ou la fusionner dans le hub avec une 301.
   Pas de canonical vers le hub (ce n'est pas un doublon).
7. **Balisage facultatif** : `DefinedTermSet` sur le hub, un `DefinedTerm` par
   terme, **généré depuis les mêmes données que le HTML**
   (`glossary_check.py build`). Propriétés : `@id`, `name`, `description`
   (identique au texte visible), `url`, `inDefinedTermSet`, `termCode`,
   `alternateName`, `sameAs` (Wikidata). Sur une page terme, `WebPage` ou
   `Article` avec `mainEntity` vers le `DefinedTerm`, plus `BreadcrumbList`
   (choix de modélisation, CLAIMED).
8. **Multilingue** : hreflang réciproque terme par terme.
9. **Mesurer** dans Search Console (requêtes « définition », « qu'est-ce
   que ») avant de généraliser.

## Contrôles automatiques (`glossary_check.py`)

| Constat | Étiquette | Bloquant |
|---|---|---|
| Terme du JSON-LD absent du texte visible (`jsonld-term-not-visible`) | ESTABLISHED | oui |
| `url`/`@id` en `#fragment` sans `id` correspondant (`term-anchor-missing`) | ESTABLISHED | oui |
| Terme sans définition, en double, ou ancre en collision (`build`) | ESTABLISHED | oui |
| Définition de moins de 12 mots (`definition-short`) | CLAIMED, heuristique | non |
| Terme ni ancré ni doté d'une URL (`term-not-addressable`) | CLAIMED | non |
| Mention d'un terme sans lien vers sa définition (occasions de maillage) | ESTABLISHED (principe) | non : suggestion |
| Terme jamais cité ailleurs sur le site | inféré | non |

## Risques à dire au propriétaire

- Des centaines de définitions générées ou compilées : *scaled content
  abuse*. Des pages de termes quasi identiques : *doorways*.
- Requêtes de définition très exposées aux AI Overviews : le glossaire peut
  gagner en visibilité et perdre en clics.
- Un glossaire n'apporte rien si les articles ne le lient pas : c'est le
  maillage qui fait sa valeur.

## Non vérifié

Cloudflare Learning Center (403 au bot), glossaire Semrush (URL
introuvable), aide Bing sur `DefinedTerm` (rendue en JavaScript), études
MADX, LLM Pulse et Hendricks.AI citées par des blogs (introuvables).
