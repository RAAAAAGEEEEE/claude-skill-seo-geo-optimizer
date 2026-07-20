---
name: seo-geo-optimizer
description: >
  Audite et implémente directement les optimisations SEO classique (Google) et
  GEO (référencement génératif : citations par ChatGPT, Claude, Perplexity,
  Google AI Overviews) sur un site/codebase. À utiliser quand l'utilisateur veut
  auditer puis corriger un site (schema JSON-LD, meta, structure de contenu,
  E-E-A-T, robots.txt/llms.txt pour crawlers IA). Couvre sites vitrines, SaaS,
  e-commerce et commerces locaux. Ne pas confondre avec le skill `SEO` (moteur
  autonome de prospection/digital PR/outreach via `/SEO`) : ce skill-ci audite
  et modifie le code du site courant, il ne fait ni prospection ni outreach.
---

# SEO / GEO Optimizer

## Principe directeur
Le SEO 2026 se joue sur deux fronts simultanés : ranker sur Google (10 liens
bleus) ET être cité par les IA (2 à 7 sources par réponse générative). On
optimise toujours les deux, avec priorité par ROI mesuré, pas par intuition.
On commence toujours par un audit, jamais par du code aveugle.

## Ce skill vs les autres skills SEO du système
- **Ce skill (`seo-geo-optimizer`)** : audit + implémentation directe dans le
  repo courant (schema, meta, structure, robots.txt/llms.txt, E-E-A-T).
- **`SEO`** (`/SEO`) : moteur autonome multi-phases pour la prospection, le
  digital PR, les backlinks éditoriaux et l'outreach. Ne touche pas au code.
  Utiliser `/SEO` pour la partie acquisition/citation externe, ce skill-ci
  pour la partie technique/on-site.
- Si les deux sont pertinents sur un même projet : lancer ce skill d'abord
  (le site doit être solide avant de chercher des citations externes), puis
  `/SEO` pour la prospection.

## Workflow obligatoire
1. **Explorer** le repo : stack, où vivent templates/pages, `robots.txt`,
   `sitemap.xml`, système de build, head/meta, schema existant.
2. **Auditer** avant toute modification → produire `AUDIT_GEO.md` (voir
   [references/checklist.md](references/checklist.md) pour le pass rapide,
   [references/audit-framework.md](references/audit-framework.md) pour le
   détail technique/on-page/E-E-A-T).
3. **Attendre le GO** de l'utilisateur avant de coder — l'audit priorise en
   P0/P1/P2, mais ne modifie rien seul.
4. **Modifier par lots**, montrer chaque diff, valider un par un.
5. Toute décision à impact produit (ex. sous-domaines vs sous-répertoires,
   suppression d'URLs, blocage de crawlers IA) → documenter le pour/contre,
   NE PAS trancher seul.

## Les leviers, par ordre de ROI

### 1. Schema JSON-LD valide
- JSON-LD uniquement (format préféré Google/Bing/ChatGPT/Claude, cf.
  [references/ai-crawlers.md](references/ai-crawlers.md)).
- Schema **déployé** ≠ schema **valide**. Un bloc JSON-LD avec des champs
  requis manquants n'apporte aucun bénéfice : toujours valider avec
  `scripts/validate_schema.py` ou le Rich Results Test avant de considérer
  la tâche terminée.
- Les pages avec 3+ types de schema montrent une probabilité de citation LLM
  ~13 points plus élevée (source : nohacks.co, 2026). Google Search Central
  rappelle que le schema n'est pas une exigence pour l'éligibilité aux AI
  Overviews — il sert d'abord aux rich results ; le lift en citation IA est
  une corrélation observée, pas une garantie contractuelle. Ne jamais
  présenter ces chiffres comme une garantie de résultat.
- Types à prioriser : `FAQPage`, `Product`, `HowTo`, `Article`+`author`,
  `Organization`+`sameAs`, `LocalBusiness`, `BreadcrumbList`.
- Templates prêts à coller : [references/schema-templates.md](references/schema-templates.md).

### 2. Structure de contenu pour le retrieval IA
- Les IA génératives lisent souvent des passages isolément (chunking) : 44%
  des citations LLM proviennent des ~30% premiers du texte de la page.
  Réponse directe / TL;DR en tête de section, contexte ensuite.
- Un seul H1, hiérarchie H2/H3 logique. FAQ en vrai balisage Q→R (pas du
  texte plat) — cf. [references/audit-framework.md](references/audit-framework.md#heading-structure).
- Seulement ~38% des citations IA viennent du top 10 organique Google : bien
  ranker sur Google ne garantit pas d'être cité par une IA générative — ce
  sont deux systèmes de retrieval distincts, à optimiser séparément.

### 3. E-E-A-T (Experience, Expertise, Authoritativeness, Trust)
Détail complet : [references/audit-framework.md](references/audit-framework.md#e-e-a-t-signals).
Indispensables : page À-propos réelle, mentions légales, bio auteur/équipe,
cohérence NAP (Name/Address/Phone) partout pour le local.

### 4. Accessibilité aux crawlers IA
- `robots.txt` : décision explicite (pas par défaut/oubli) sur GPTBot,
  ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot, etc. — distinguer
  bots d'entraînement et bots de recherche/citation. Détail et exemple de
  configuration : [references/ai-crawlers.md](references/ai-crawlers.md).
- Créer `llms.txt` (description du site + pages clés). **`llms.txt` n'est pas
  un mécanisme de contrôle d'accès** — seul `robots.txt` en est un. Ne jamais
  présenter `llms.txt` comme un moyen de bloquer un crawler.
- `sitemap.xml` présent, à jour, référencé dans `robots.txt`.

### 5. Fraîcheur
- Timestamp "Dernière mise à jour" visible + `dateModified` dans le schema.

### 6. Autorité / entités et backlinks — évaluation technique, pas acquisition
Ce skill **évalue et vérifie** des backlinks (existants ou proposés), il ne
les **acquiert** pas : trouver des opportunités, choisir des cibles,
prospecter, rédiger et envoyer des pitchs/outreach est le rôle du skill
`SEO` (`/SEO`) — ne pas dupliquer ce travail ici.
- `Organization` + `sameAs` vers réseaux + Wikidata pour désambiguïsation
  (ça, c'est du code/on-site, donc dans le périmètre de ce skill).
- Cadre d'évaluation technique d'un lien ou d'une opportunité de lien
  (interne vs externe, dofollow/nofollow, variation d'ancres, risque PBN,
  critères de choix d'annuaire, ce qui est à bannir) :
  [references/backlinks.md](references/backlinks.md).
- Vérification technique d'une page source donnée (dofollow ? ancres
  répétées ?) : [scripts/check_backlinks.sh](scripts/check_backlinks.sh).

## Indexation — règles strictes
- La bonne méthode par défaut : `sitemap.xml` à jour + Google Search
  Console + inspection d'URL manuelle ponctuelle. Rien d'autre à construire.
- **Ne jamais utiliser la Google Indexing API** pour des pages classiques —
  elle est réservée à `JobPosting` et `BroadcastEvent`/`VideoObject` ; un
  usage détourné risque un flag spam et une coupure d'accès à l'API.
- **Ne jamais coder d'auto-submit d'URLs** vers un moteur en dehors du flux
  sitemap → crawl normal.
- Détail complet et nuances (Brave Search excepté) :
  [references/indexing-rules.md](references/indexing-rules.md).

## Hygiène des données
Toujours distinguer donnée **mesurée** (Search Console, analytics, preuve
concrète) de donnée **générée/hypothèse IA** dans un audit ou un rapport.
Ne jamais recycler une génération IA comme si c'était une donnée vérifiée —
détail : [references/data-hygiene.md](references/data-hygiene.md).

## Architecture : sous-répertoire vs sous-domaine
Par défaut : sous-répertoires (héritent de l'autorité du domaine racine,
rankent plus vite). C'est une décision produit (isolation, custom domains) :
toujours présenter le trade-off, ne jamais migrer sans validation explicite.

## Limitation connue : détection de schema
`web_fetch`/`curl` ne détectent pas fiablement le schema injecté côté client
(WordPress + Yoast/RankMath/AIOSEO le font souvent en JS). Pour vérifier un
schema existant, utiliser le navigateur (`document.querySelectorAll('script[type="application/ld+json"]')`)
ou le Rich Results Test — jamais conclure "pas de schema" sur la seule base
d'un `curl`.

## Livrables standard
- `AUDIT_GEO.md` — état + problèmes priorisés P0/P1/P2.
- `CHANGELOG_GEO.md` — chaque modif + son objectif SEO/GEO.
- Note de validation schema (sortie de `validate_schema.py` + Rich Results
  Test) avant de clore une tâche d'implémentation de schema.

## Références du skill
- [references/checklist.md](references/checklist.md) — pass rapide, à
  remplir dans `AUDIT_GEO.md`.
- [references/audit-framework.md](references/audit-framework.md) — détail
  technique, on-page, E-E-A-T, par type de site.
- [references/schema-templates.md](references/schema-templates.md) — blocs
  JSON-LD paste-ready.
- [references/ai-crawlers.md](references/ai-crawlers.md) — robots.txt/llms.txt,
  liste des bots IA, soumission Brave Search (GEO), sources.
- [references/indexing-rules.md](references/indexing-rules.md) — méthode
  d'indexation correcte, interdictions (Google Indexing API, auto-submit).
- [references/backlinks.md](references/backlinks.md) — cadre backlinks
  (interne/externe, PBN, annuaires, à bannir).
- [references/data-hygiene.md](references/data-hygiene.md) — mesuré vs
  généré IA, audit périodique de la base de connaissances.
- [scripts/validate_schema.py](scripts/validate_schema.py) — validateur JSON-LD
  local (champs requis par type schema.org).
- [scripts/audit_site.sh](scripts/audit_site.sh) — audit technique
  multi-URLs (curl) : HTTP, title, description, canonical, hreflang,
  JSON-LD, OG, robots.txt/sitemap.
- [scripts/generate_sitemap.py](scripts/generate_sitemap.py) — génère
  `sitemap.xml` (+ `robots.txt` optionnel) pour un site ou un déploiement
  multi-sites, sans dépendance à un schéma de DB particulier.
- [scripts/check_backlinks.sh](scripts/check_backlinks.sh) — vérifie
  dofollow/nofollow et répétition d'ancres sur une page source.
