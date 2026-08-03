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

## hreflang (sites multilingues)
Le point technique le plus souvent cassé en SEO international : **75% des
sites ciblant plusieurs langues ont une erreur d'implémentation hreflang**
(étude 2026), qui fragmente le classement entre versions au lieu de les
consolider. Trois règles non négociables :
- **Auto-référencement** : chaque page doit inclure une balise hreflang qui
  pointe vers elle-même, en plus des autres langues.
- **Réciprocité** : si la page A référence B, B doit référencer A en retour
  — sinon Google ignore la paire. Vérifié automatiquement par
  `scripts/generate_report.py` sur les pages incluses dans le même audit.
- **Codes ISO valides** : `en-GB` pas `en-uk`, `es` pas `sp`. Un code
  invalide fait ignorer la balise entièrement.
Éviter aussi : canonical qui pointe vers une autre langue (chaque version
doit se canonicaliser elle-même), absence de x-default pour le
sélecteur de langue par défaut.

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
Prérequis absolu, à vérifier avant tout le reste : les crawlers IA
accèdent-ils réellement au site ? Voir
[cloudflare-ai-access.md](cloudflare-ai-access.md) et
[`../scripts/check_ai_access.py`](../scripts/check_ai_access.py).

Ce qui est établi et sourçable :
- **Position officielle de Google** (guide « AI features », mis à jour le
  15 juin 2026) : *« There are no additional requirements to appear in AI
  Overviews or AI Mode, nor other special optimizations necessary »* et
  *« You don't need to create new machine readable files, AI text files, or
  markup »*. Autrement dit : côté Google, les fondamentaux SEO **sont** la
  stratégie GEO. Se méfier de toute recommandation qui prétend l'inverse.
- **Le contexte a changé, pas la méthode** : le taux de recherches Google
  sans clic atteint ~65% en 2026, ~93% en AI Mode, et les AI Overviews
  apparaissent sur une part importante des requêtes. Conséquence pratique :
  l'objectif se déplace du clic vers la **citation**, ce qui renforce
  l'intérêt d'un contenu factuel, daté et attribuable — mais ne crée pas de
  levier technique nouveau côté Google.
- **Structure pour le chunking** : les moteurs génératifs récupèrent des
  passages isolément. Une section qui commence par sa réponse est
  réutilisable telle quelle ; une section qui commence par un préambule ne
  l'est pas. C'est un principe de rédaction robuste, indépendant des
  chiffres marketing du moment.

Les statistiques de « lift de citation » par type de schema, largement
reprises dans les blogs SEO 2026, ne sont pas issues de recherche primaire
vérifiable et ont été **retirées volontairement** de ce skill plutôt que
conservées sans preuve (cf. [data-hygiene.md](data-hygiene.md)). Ne pas les
réintroduire dans un audit sans source primaire.

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

Priorisation par défaut : accès crawlers bloqué → indexation cassée →
fondamentaux manquants (title/canonical/H1) → schema invalide → performance →
contenu/E-E-A-T → long terme.

## Outils
Tout ce dont ce skill a besoin est gratuit et automatisable via ses scripts
(voir le tableau dans [SKILL.md](../SKILL.md)) : Search Console API, CrUX
API, IndexNow, requêtes HTTP directes. Les suites payantes (Screaming Frog,
Ahrefs, Semrush) apportent surtout du crawl à grande échelle et des données
de backlinks tierces — utiles au-delà de quelques centaines de pages, non
nécessaires pour l'audit couvert ici.

Compléments manuels ponctuels : Rich Results Test (rendu JS, référence pour
l'éligibilité), PageSpeed Insights (labo, quand CrUX manque de données).
