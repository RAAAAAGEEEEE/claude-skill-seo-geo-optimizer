# Audit framework détaillé (technique, on-page, E-E-A-T)

Revu le 2026-09-27. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).

Base SEO classique (technique/on-page/E-E-A-T), enrichie des
signaux GEO (retrieval par IA génératives). Utiliser ce fichier pour l'audit
approfondi ; [checklist.md](checklist.md) pour le pass rapide.

**Limitation outillage** : `web_fetch`/`curl` ne détectent pas le schema
injecté côté client (plugins WordPress type Yoast/RankMath/AIOSEO). Pour
vérifier un schema existant : navigateur +
`document.querySelectorAll('script[type="application/ld+json"]')`, ou le
Rich Results Test (https://search.google.com/test/rich-results). Ne jamais
conclure "pas de schema" sur la seule base d'un `curl`.

## Ordre de priorité
1. Crawlabilité & indexation (Google peut-il trouver/indexer le contenu ?)
2. Fondations techniques (le site est-il rapide et fonctionnel ?)
3. On-page (le contenu est-il optimisé ?)
4. Qualité de contenu (mérite-t-il de ranker/être cité ?)
5. Autorité & liens (a-t-il de la crédibilité ?)

## Crawlabilité & indexation
- `robots.txt` : pas de blocage involontaire, pages importantes autorisées,
  référence au sitemap. Pour les bots IA, voir [ai-crawlers.md](ai-crawlers.md).
- `sitemap.xml` : existe, accessible, uniquement des URLs canoniques et
  indexables, à jour, bien formaté.
- Architecture : pages importantes à ≤3 clics de la home, hiérarchie
  logique, pas de pages orphelines.
- Sites volumineux : URLs paramétrées maîtrisées, navigation à facettes
  gérée, pas de session ID dans l'URL.
- Indexation : comparer indexé vs attendu (`site:domaine.com` + Search
  Console), pas de noindex sur des pages importantes (meta **ou** en-tête
  `X-Robots-Tag`, détectés par `generate_report.py`), pas de chaînes de
  redirection, pas de redirection temporaire (302/307) sur une URL
  canonique, pas de soft 404 (page « aucun résultat » en 200 indexable), une
  URL inexistante répond 404/410 et **jamais 5xx**, canonicals cohérents
  (HTTP→HTTPS, www vs non-www, trailing slash).
- Contenu dans le HTML initial : les crawlers IA autres que Googlebot
  n'exécutent pas ou peu le JavaScript ; tout ce qui n'est rendu que côté
  client est invisible pour eux (Microsoft le dit pour le contenu caché :
  « AI systems may not render hidden content », 2025-10-08, ESTABLISHED).

## Vitesse & Core Web Vitals
- Bon : LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1 ; mauvais : > 4 s, > 500 ms,
  > 0,25 ; au 75e percentile, mobile et desktop séparés (ESTABLISHED,
  [Google](https://developers.google.com/search/docs/appearance/core-web-vitals),
  maj 2025-12-10). Pas de signal « page experience » unique ; la pertinence
  prime ([page experience](https://developers.google.com/search/docs/appearance/page-experience), maj 2026-09-22).
- À venir : soft navigations activées par défaut dans Chrome 151, intégration
  future aux Core Web Vitals, remontée CrUX non décidée (2026-09-02).
- Facteurs : TTFB, optimisation images, exécution JS, delivery CSS, headers
  de cache, CDN, chargement des fonts.
- Outils : PageSpeed Insights, WebPageTest, Chrome DevTools, rapport Core
  Web Vitals de Search Console.

## hreflang (sites multilingues)
Point technique souvent cassé en SEO international. Ordre de grandeur :
67 % de 374 756 domaines avec au moins une erreur (Ahrefs, 2023-08-10,
CLAIMED méthode publiée — ce chiffre compte l'absence de `x-default`, que
Google n'exige pas). Le « 75 % » souvent cité vient d'une étude SEMrush de
**2017**, pas de 2026. Trois règles non négociables :
- **Auto-référencement** : chaque page doit inclure une balise hreflang qui
  pointe vers elle-même, en plus des autres langues.
- **Réciprocité** : si la page A référence B, B doit référencer A en retour
  — sinon Google ignore la paire. Vérifié automatiquement par
  `scripts/generate_report.py` sur les pages incluses dans le même audit.
- **Codes ISO valides** : `en-GB` pas `en-uk`, `es` pas `sp`. Un code
  invalide fait ignorer la balise entièrement.
Éviter aussi : canonical qui pointe vers une autre langue (chaque version
doit se canonicaliser elle-même). `x-default` est recommandé, pas requis.
Et surtout : une URL de langue qui sert le contenu d'une autre langue
(`/en/` en français, `lang="en"`, indexable) est un doublon, pas une
traduction — la passer en 404 ou `noindex` tant qu'elle n'est pas traduite.

## Mobile & sécurité
- Responsive (pas de site m. séparé), tailles de tap targets, viewport
  configuré, pas de scroll horizontal, contenu identique desktop/mobile.
- HTTPS partout, certificat valide, pas de mixed content, redirections
  HTTP→HTTPS, HSTS en bonus.

## On-page
### Title / meta description
- Title : unique par page, descriptif, concis, mot-clé proche du début.
  La longueur « 50-60 caractères » est une convention d'outils SEO, pas une
  règle Google (qui peut réécrire le lien de titre).
- Meta description : unique, 150-160 caractères, mot-clé principal, value
  proposition claire, CTA.

### Heading structure
- Un seul H1 par page, contenant le mot-clé principal.
- Hiérarchie logique H1→H2→H3, pas de saut de niveau, pas de heading utilisé
  uniquement pour le style.

### Contenu
- Mot-clé dans les 100 premiers mots, mots-clés liés utilisés naturellement,
  profondeur suffisante, répond à l'intention de recherche, meilleur que la
  concurrence.
- Éviter : pages avec peu de contenu unique, pages tag/catégorie sans
  valeur, contenu dupliqué/quasi-dupliqué.

### Images
- Noms de fichiers descriptifs, alt text sur toutes les images (qui décrit
  l'image), fichiers compressés, formats modernes (WebP), lazy loading,
  images responsive.

### Maillage interne
- Pages importantes bien liées, anchor text descriptif, pas de lien interne
  cassé, pas de pages orphelines, pas d'anchor text sur-optimisé.

### Ciblage mot-clé
- Un mot-clé principal clair par page, alignement title/H1/URL, pas de
  cannibalisation entre pages, mapping mot-clé au niveau du site.

## E-E-A-T signals
Ce que Google en dit (pas un facteur de classement en soi, la confiance
d'abord) et le balisage d'éditeur : [eeat-news.md](eeat-news.md).
- **Experience** : expérience de première main démontrée, insights/données
  originaux, exemples et études de cas réels.
- **Expertise** : credentials auteur visibles, information précise et
  détaillée, claims correctement sourcés.
- **Authoritativeness** : reconnu dans le domaine, cité par d'autres,
  credentials industrie.
- **Trustworthiness** : information exacte, transparence sur l'activité,
  coordonnées de contact disponibles, politique de confidentialité/CGU,
  HTTPS.

## Signaux GEO (retrieval par IA génératives)
Prérequis, dans l'ordre :
1. Accès réel des crawlers ([cloudflare-ai-access.md](cloudflare-ai-access.md),
   [`../scripts/check_ai_access.py`](../scripts/check_ai_access.py)).
2. Indexation et extrait autorisé : pas de `noindex`, `nosnippet`,
   `max-snippet:0` involontaire.
3. Google : réglage Search Console « Search generative AI » sur Inclure
   (défaut) ; `Google-Extended` n'y change rien
   ([google-ai-features.md](google-ai-features.md)).

Ensuite, ce qui est établi ou soutenu (détail et sources :
[evidence.md](evidence.md)) :
- Google : l'optimisation pour l'IA « reste du SEO » ; pas de fichier, de
  balisage ou de découpage spécial (ESTABLISHED, guide maj 2026-07-10).
- Des preuves vérifiables dans le texte (chiffres, citations, sources,
  dates) : seul levier de contenu appuyé par une étude causale évaluée par
  des pairs, en cadre simulé (SUPPORTED, KDD 2024).
- Structure lisible : titres explicites, réponse directe en tête de
  section, tableaux HTML sémantiques, contenu non caché (ESTABLISHED côté
  Bing ; principe de rédaction robuste, pas une garantie).
- Fraîcheur réelle : mettre à jour le fond, pas seulement la date.
- Les moteurs IA citent beaucoup de sources tierces : la présence ailleurs
  (mentions, reprises) relève du skill `SEO`.

Les statistiques de « lift de citation » par type de schema reprises dans
les blogs SEO ne reposent sur aucune donnée primaire publiée (vérifié le
2026-09-27) : ne pas les réintroduire.

## Problèmes fréquents par type de site
### SaaS/Produit
Pages produit peu profondes, blog non intégré aux pages produit, pas de
pages comparaison/alternatives, pages features trop courtes, pas de
glossaire/contenu éducatif.

### E-commerce
Pages catégorie pauvres, descriptions produit dupliquées, schema produit
manquant, navigation à facettes créant des doublons, pages rupture de stock
mal gérées.

### Contenu/Blog
Contenu obsolète non rafraîchi, cannibalisation de mots-clés, pas de
clustering thématique, maillage interne pauvre, pages auteur manquantes.

### Commerce local
NAP incohérent, schema local manquant, Google Business Profile non optimisé,
pages de localisation manquantes, pas de contenu local. Détail sur
l'automatisation possible (API, délai d'approbation Google) :
[google-business-profile.md](google-business-profile.md).

## Format de rapport
Ne pas rédiger le rapport à la main :
[`../scripts/generate_report.py`](../scripts/generate_report.py) produit
`AUDIT_GEO.md` (lisible) + `.json` (machine-lisible), re-exécutable à
l'identique. Y ajouter ensuite, manuellement, ce que les scripts ne peuvent
pas voir ([checklist.md](checklist.md)) et l'ordre de priorité P0/P1/P2 —
qui relève du jugement, pas de la détection.

Priorisation par défaut : accès crawlers bloqué → indexation cassée
(noindex, 5xx, redirections temporaires, doublons de langue) → extrait ou
réglage IA bloquant → fondamentaux manquants (title/canonical/H1) → schema
invalide → performance → contenu/E-E-A-T → long terme.

## Outils
Tout ce dont ce skill a besoin est gratuit et automatisable via ses scripts
(voir le tableau dans [SKILL.md](../SKILL.md)) : Search Console API, CrUX
API, IndexNow, requêtes HTTP directes. Mesure des citations IA : rapport
« Generative AI performance » de Search Console (impressions, interface
seulement) et rapport « AI Performance » de Bing Webmaster Tools (citations
Copilot) — tous deux exigent la vérification du site. Les suites payantes (Screaming Frog,
Ahrefs, Semrush) apportent surtout du crawl à grande échelle et des données
de backlinks tierces — utiles au-delà de quelques centaines de pages, non
nécessaires pour l'audit couvert ici.

Compléments manuels ponctuels : Rich Results Test (rendu JS, référence pour
l'éligibilité), PageSpeed Insights (labo, quand CrUX manque de données).
