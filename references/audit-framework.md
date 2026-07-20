# Audit framework détaillé (technique, on-page, E-E-A-T)

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
  Console), pas de noindex sur des pages importantes, pas de chaînes de
  redirection, pas de soft 404, canonicals cohérents (HTTP→HTTPS, www vs
  non-www, trailing slash).

## Vitesse & Core Web Vitals
- LCP < 2.5s, INP < 200ms, CLS < 0.1 (seuils Google actuels).
- Facteurs : TTFB, optimisation images, exécution JS, delivery CSS, headers
  de cache, CDN, chargement des fonts.
- Outils : PageSpeed Insights, WebPageTest, Chrome DevTools, rapport Core
  Web Vitals de Search Console.

## Mobile & sécurité
- Responsive (pas de site m. séparé), tailles de tap targets, viewport
  configuré, pas de scroll horizontal, contenu identique desktop/mobile.
- HTTPS partout, certificat valide, pas de mixed content, redirections
  HTTP→HTTPS, HSTS en bonus.

## On-page
### Title / meta description
- Title : unique par page, mot-clé proche du début, 50-60 caractères,
  accrocheur. Pas de nom de marque en fin (déjà affiché par le SERP).
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
Sources détaillées et chiffres exacts : voir [ai-crawlers.md](ai-crawlers.md)
et la section "Signaux GEO" de [SKILL.md](../SKILL.md).
- Les IA lisent souvent des passages isolément (chunking) : réponse directe
  en tête de section, contexte ensuite — ~44% des citations LLM proviennent
  du premier tiers d'une page (nohacks.co, 2026).
- Ranker sur Google ≠ être cité par une IA : seulement ~38% des citations IA
  viennent du top 10 organique — deux systèmes de retrieval distincts.
- Citer des sources tierces, inclure des statistiques et des citations
  directes augmente la probabilité de citation par les moteurs génératifs
  (étude Princeton/Georgia Tech/IIT Delhi, KDD 2024, Aggarwal et al. — lift
  jusqu'à 40% selon la méthode).
- 3+ types de schema sur une page : probabilité de citation LLM ~13 points
  plus élevée (corrélation observée, pas une garantie).

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
pages de localisation manquantes, pas de contenu local.

## Format de rapport d'audit
**Résumé exécutif** : état de santé global, top 3-5 problèmes prioritaires,
quick wins identifiés.

**Par section** (technique, on-page, contenu) et par problème :
- **Problème** : ce qui ne va pas
- **Impact** : SEO/GEO, Élevé/Moyen/Faible
- **Preuve** : comment le problème a été trouvé
- **Correction** : recommandation précise
- **Priorité** : P0/P1/P2

**Plan d'action priorisé** : corrections critiques (bloquent
indexation/ranking) → améliorations à fort impact → quick wins → recommandations
long terme.

## Outils
**Gratuits** : Search Console, PageSpeed Insights, Bing Webmaster Tools,
Rich Results Test, Mobile-Friendly Test, Schema Validator.
**Payants (si disponibles)** : Screaming Frog, Ahrefs/Semrush, Sitebulb,
ContentKing.
