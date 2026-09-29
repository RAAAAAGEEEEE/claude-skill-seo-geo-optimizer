---
name: seo-geo-optimizer
description: >
  Audite puis corrige, dans le code d'un site, sa visibilité dans Google
  (AI Overviews, AI Mode, Discover) et dans les moteurs de réponse IA
  (ChatGPT, Claude, Perplexity, Gemini, Copilot, Mistral) : accès réel des
  crawlers (robots.txt, blocage CDN), indexabilité, sitemap, canonical,
  hreflang, JSON-LD, maillage interne et cocon, glossaire, journaux serveur,
  Core Web Vitals, Search Console, IndexNow. Audit complet en une commande,
  rapport daté, diff dans le temps, planifiable ; chaque recommandation porte
  une source datée et une étiquette ESTABLISHED, SUPPORTED ou CLAIMED. À
  utiliser pour « auditer le SEO/GEO », « pourquoi mon site n'est pas cité
  par ChatGPT », « vérifier robots.txt, sitemap, schema, maillage »,
  « quels bots viennent vraiment », « planifier un audit SEO ». Ne fait ni
  prospection ni outreach (skill compagnon `seo`).
license: MIT
compatibility: Python 3.10+ (bibliothèque standard). bash et curl pour deux scripts. Accès réseau sortant vers le site audité. Conçu pour Claude Code ; les scripts s'exécutent aussi seuls.
metadata:
  author: Anto1nx
  version: "2.3.3"
  repository: https://github.com/RAAAAAGEEEEE/claude-skill-seo-geo-optimizer
---

# SEO / GEO Optimizer

Version 2.3.3 — connaissances revues le **2026-09-28** (historique :
[CHANGELOG.md](CHANGELOG.md)). Au-delà de 3 mois, revérifier toute
affirmation datée avant de la ressortir.

## Principe
Google dit lui-même que l'optimisation pour ses fonctions IA « reste du
SEO ». Les autres moteurs de réponse s'appuient eux aussi sur des index de
recherche. L'ordre ne se négocie pas :
**accès → indexation et extrait autorisé → contenu dans le HTML → preuves
vérifiables → balisage exact → performance**. Un site que les crawlers ne
peuvent pas lire a un plafond de zéro. Tout ce qui peut tourner sans humain
passe par `scripts/run_audit.py`. Le jugement et les décisions produit
restent humains.

## Périmètre
- **Dans** : audit et modification du site courant (code, templates,
  robots.txt, sitemap, meta, JSON-LD, en-têtes, maillage interne), mesure via
  APIs gratuites, audit planifié.
- **Hors** : prospection, netlinking, digital PR, outreach → skill `seo`
  ([citation-engine-skill](https://github.com/RAAAAAGEEEEE/citation-engine-skill),
  commande `/seo`). Rédaction des pages planifiées → skill `redaction`. Production
  massive de contenu → jamais (scaled content abuse).
- Sur un même projet : ce skill d'abord, `/seo` ensuite.

## Quand l'utiliser
- audit SEO/GEO, ou site absent des réponses IA ;
- doute sur robots.txt ou le CDN ;
- migration, ajout de schema, préparation d'un lancement ;
- revue d'un `llms.txt`/RSL ;
- maillage interne ou cocon sémantique ;
- glossaire ou lexique (créer, auditer, lier) ;
- choix des formats de contenu à publier (comparatif, guide d'achat, test,
  fiche technique, données originales, tutoriel…) ;
- journaux serveur : quels crawlers viennent vraiment ;
- suivi planifié d'un site.

Pas pour rédiger : la prose en français (articles, pages, fiches) relève
du skill `redaction`, la structure d'une page de vente de `copywriting`.

## Entrées et sorties
- **Entrée** : l'URL du site ; le dépôt du site si des corrections sont
  demandées. Les accès optionnels (PageSpeed, CrUX, Search Console, IndexNow)
  passent **uniquement** par des variables d'environnement
  ([docs/CONFIGURATION.md](docs/CONFIGURATION.md)).
- **Sortie** : `<out-dir>/<hôte>/audit_<AAAAMMJJTHHMMSSZ>.md` et `.json`,
  avec un plan P0/P1/P2 ; `diff_<date>.md` quand un rapport précédent
  existe ; un sitemap proposé et la liste des URLs pour IndexNow quand ils
  s'appliquent.

## Procédure (PLAN → FIX → VERIFY)

1. **Audit automatique** — `python scripts/run_audit.py --site <url> --out-dir <dossier>`.
   - Code de sortie : 0 = aucun P0, 1 = au moins un P0, 2 = accueil
     injoignable (ne rien conclure).
   - Lire en premier les modules `skipped` et `error` : un module absent
     n'est pas un module OK.
   - Détail des étapes : [docs/USAGE.md](docs/USAGE.md).
2. **Explorer** le dépôt : stack, rendu (SSR ou JS client), génération de
   robots.txt, du sitemap, du head/meta, du JSON-LD, des redirections, des
   pages d'erreur et des menus (origine des liens de navigation).
3. **Compléter** avec [checklist.md](references/checklist.md) : réglages de
   comptes, jugement éditorial, carte de la demande et définition canonique
   ([french-practitioners.md](references/french-practitioners.md)).
   - Vocabulaire propre au site (sigles, termes techniques) : proposer un
     glossaire. `glossary_check.py suggest` liste les candidats, `audit`
     contrôle un glossaire existant et ses occasions de liens
     ([glossary.md](references/glossary.md)).
   - Journaux serveur fournis : `crawler_logs.py` (crawlers réels,
     usurpations, 5xx, couverture du sitemap)
     ([automation.md](references/automation.md)).
   - **Planification de contenu** (nouvelles pages, refonte éditoriale) :
     partir de la carte de la demande, puis choisir un format par
     intention avec la table de décision par type de site
     ([content-formats.md](references/content-formats.md)). Un format ne
     se publie que si le site détient la preuve qu'il exige (test réel,
     donnée propre, source datée). Jamais une page par variante de requête.
4. **PLAN** : reprendre le plan P0/P1/P2 du rapport. Un constat CLAIMED
   (maillage de praticien, seuils) reste P2. **Attendre le GO** avant de
   coder.
5. **FIX** par lots, un diff à la fois. Les décisions produit restent au
   propriétaire : exposer les options, **ne pas trancher**. Exemples :
   - ouvrir ou fermer des crawlers, opt-out IA Google ;
   - migrer des URLs, désindexer ;
   - restructurer une rubrique en cocon ;
   - soumettre à IndexNow.
6. **VERIFY** : relancer `run_audit.py`. Le `diff_*.md` doit montrer les
   constats résolus. Lancer `validate_schema.py` sur tout JSON-LD touché, et
   `python -m unittest discover -s tests` si un script du skill a changé.
   Pas de « terminé » sans sortie de script.
7. **Planifier** si le propriétaire le demande : cron, Planificateur de
   tâches Windows ou tâche Claude Code
   ([docs/USAGE.md](docs/USAGE.md#planifier-laudit)). La création de la
   tâche est une configuration persistante : **confirmation requise**.

## Les leviers (détail dans les références)

| Levier | À retenir | Référence |
|---|---|---|
| Accès crawlers | Rôles : engine, search, user, training, token. `Google-Extended` et `Applebot-Extended` ne sont que des jetons. Plusieurs fetchers « utilisateur » ignorent robots.txt. Depuis le 2026-09-15, Cloudflare bloque par défaut Training et Agent sur les pages avec publicité. | [ai-crawlers.md](references/ai-crawlers.md), [cloudflare-ai-access.md](references/cloudflare-ai-access.md) |
| Google IA | AI Overviews et AI Mode sont en France depuis le 2026-07-22. Conditions : page indexée, extrait autorisé, réglage Search Console « Search generative AI » sur Inclure. Les rapports IA donnent les impressions seulement. | [google-ai-features.md](references/google-ai-features.md) |
| Technique / on-page | Une URL inconnue répond 404, jamais 5xx. Un déplacement définitif passe par 301/308. Pas de doublon de langue. Un canonical sur chaque page. Le contenu est dans le HTML initial. | [audit-framework.md](references/audit-framework.md) |
| Maillage / cocon | Google : `<a href>`, au moins un lien vers chaque page importante, ancres descriptives, aucun nombre idéal de liens. Cocon, liens contextuels et profondeur ≤ 3 : méthodes de praticiens, CLAIMED. | [french-practitioners.md](references/french-practitioners.md) |
| Schema | Rich results FAQ supprimés le 2026-05-07. Dataset ne sert qu'à Dataset Search. `WebSite` porte le nom du site. Pas d'étoiles auto-attribuées, aucun schema « spécial IA ». | [schema-templates.md](references/schema-templates.md) |
| Contenu citable | Preuves vérifiables (chiffres, sources, dates), fraîcheur réelle, structure lisible, pas de découpage artificiel. | [evidence.md](references/evidence.md) |
| Formats de contenu | Google ne favorise aucun format en soi : il récompense l'information originale, l'expérience de première main et les sources claires. Tests, comparatifs et classements relèvent du reviews system. FAQ : texte visible oui, rich result non. Les parts de citation par format viennent d'études de vendeurs (CLAIMED), varient selon l'intention et le moteur, et se contredisent. | [content-formats.md](references/content-formats.md) |
| E-E-A-T / éditeur | Pas un facteur de classement en soi. Auteur désambiguïsé (`author.url`), politiques éditoriales exactes. | [eeat-news.md](references/eeat-news.md) |
| Performance | LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1, au p75 terrain (CrUX). | [audit-framework.md](references/audit-framework.md#vitesse--core-web-vitals) |
| Indexation | Google : sitemap exact (lastmod vrai) et Search Console. Indexing API interdite hors JobPosting/BroadcastEvent. IndexNow pour Bing et les autres, **clé à la racine**. | [indexing-rules.md](references/indexing-rules.md) |
| Glossaire | Utile pour le SEO si chaque définition est originale et liée depuis les articles (ESTABLISHED, règles générales). Effet sur les citations IA : non démontré. `DefinedTerm` : aucun rich result. | [glossary.md](references/glossary.md) |
| Automatisation | Mesurer, détecter, préparer : oui. Publier du contenu, des liens ou du balisage sans relecture : non (spam policies). Pas de suivi de citations par grounding Gemini ni par scraping de Google (conditions). | [automation.md](references/automation.md) |
| Signaux « pour l'IA » | llms.txt, RSL, aipref, Content Signals : aucun fournisseur ne s'engage à les lire. P2 au mieux. | [licensing-signals.md](references/licensing-signals.md) |
| Agents | MCP, API catalog, WebMCP : impact marginal au 2026-09-27. | [agent-discovery.md](references/agent-discovery.md) |
| Liens externes | Évaluer, pas acquérir. `sponsored`, `ugc`, `nofollow` sont des indications. | [backlinks.md](references/backlinks.md), [spam-policies.md](references/spam-policies.md) |
| Local | API GBP : fiche validée depuis 60 jours ou plus, approbation manuelle. | [google-business-profile.md](references/google-business-profile.md) |

## Niveaux de preuve
- **ESTABLISHED** : documentation officielle, ou déclaration du fournisseur
  sur son propre produit.
- **SUPPORTED** : étude indépendante avec données.
- **CLAIMED** : vendeur, blog ou praticien, y compris une étude de vendeur à
  méthode publiée.

Un CLAIMED ne fonde jamais seul une priorité : les règles CLAIMED de
`scripts/audit_rules.py` sont P2, et un test le vérifie.

Chaque constat d'audit est marqué **mesuré** (requête HTTP, CrUX, Search
Console), **inféré** (HTML, code) ou **hypothèse**. Détail :
[data-hygiene.md](references/data-hygiene.md).

## Replis et erreurs
- Schema, liens ou contenu injectés en JavaScript : les scripts ne les voient
  pas. Conclure avec un navigateur ou le Rich Results Test, jamais par
  « absent ».
- Accès crawlers : les user-agents sont simulés depuis votre machine. Un 403
  prouve une règle par user-agent. Un 200 ne prouve pas que le vrai bot
  passe. Confirmer dans les journaux ou le tableau de bord CDN.
- Pas de `<main>`/`<nav>` dans le HTML : les contrôles de liens contextuels
  sont désactivés, et le rapport le dit.
- Crawl incomplet (`--max-pages` atteint) : les orphelines et la profondeur
  sont des estimations, et le rapport le dit.
- CrUX sans données = trafic insuffisant, pas un problème de performance.
- PageSpeed sans clé : le quota partagé est souvent épuisé. Fournir
  `PAGESPEED_API_KEY`, sinon le module est `skipped`.
- Pas d'accès Search Console ni Bing Webmaster Tools : le dire, ne pas
  extrapoler une mesure de citation.
- Page en 403 ou rendue en JS lors d'une vérification de source : noter
  « non vérifié ».
- Journal serveur : un crawler sans liste d'IP publiée (Meta, Amazon) reste
  « non vérifiable », jamais « vérifié ». Format non reconnu : code 2.
- Glossaire : `glossary_check.py` n'insère aucun lien et n'écrit aucune
  définition ; il liste, le propriétaire décide.

## Sécurité et confidentialité
- Par défaut, uniquement des **GET publics** vers le site audité. Le crawl
  respecte robots.txt et marque une pause entre les requêtes (`--delay`).
- Rien d'autre ne sort sans accès fourni par l'environnement :
  - `PAGESPEED_API_KEY` / `CRUX_API_KEY` : clé en paramètre d'URL vers les
    API Google ;
  - `GSC_SERVICE_ACCOUNT_FILE` : jeton OAuth vers Search Console ;
  - `--indexnow-submit` : URLs envoyées à api.indexnow.org et partagées
    avec tous les moteurs participants. C'est une **action externe :
    confirmation requise**.
- `crawler_logs.py` télécharge les listes d'IP publiques des fournisseurs
  (GET, rien n'est envoyé) ; `--no-verify` l'évite. Les IP du journal sont
  des données personnelles : jamais écrites, seulement comptées ou agrégées
  en /24 et /48.
- Les clés ne passent jamais en argument. Elles ne sont jamais affichées ni
  écrites : le rapport est masqué avant écriture, et un test le vérifie.
  Détail : [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).
- Ce skill ne modifie aucun compte (Search Console, CDN, GBP) : il liste
  les réglages, et le propriétaire les change.

## Exemples d'invocation
- « Audite le SEO/GEO de ce site et propose un plan » → procédure complète.
- « Pourquoi Perplexity ne nous cite jamais ? » → étape 1, puis
  [ai-crawlers.md](references/ai-crawlers.md).
- « Vérifie notre maillage, on veut un cocon » → étape 1, tableau
  « Cocon / silos » du rapport, puis
  [french-practitioners.md](references/french-practitioners.md).
- « Lance cet audit chaque lundi » → étape 7, après confirmation.
- « Quels contenus publier pour être classé et cité ? » → carte de la
  demande, puis [content-formats.md](references/content-formats.md) ;
  plan soumis au propriétaire.
- « Faut-il un lexique ? » → `glossary_check.py suggest`, puis
  [glossary.md](references/glossary.md) ; décision au propriétaire.
- « Ajoute le schema produit » →
  [schema-templates.md](references/schema-templates.md), puis
  `validate_schema.py`.

## Exemple de sortie
Sortie réelle de `run_audit.py` sur le site de test du dépôt
(`tests/fixtures/site/`, servi sur 127.0.0.1, exécuté le 2026-09-29, sans
aucune clé) :
```
Resultat : P0=0 P1=4 P2=6 ; 7 page(s), 42 requete(s)
  P1 URL du sitemap en noindex (1) [ESTABLISHED, mesuré]
  P1 Page auditée hors 200 (1) [ESTABLISHED, inféré]
  P1 Lien interne vers une URL en erreur (4xx/5xx) (1) [ESTABLISHED, mesuré]
  P1 Page du sitemap sans aucun lien interne entrant (orpheline) (1) [ESTABLISHED, inféré]
  P2 Page indexable quasi vide (risque de soft 404) (4) [ESTABLISHED, inféré]
  P2 Page fille sans lien vers sa page mère (cocon) (1) [CLAIMED, inféré]
  P2 Ancre générique (« cliquez ici », « en savoir plus ») (1) [ESTABLISHED, inféré]
  P2 Page sans lien contextuel sortant (1) [CLAIMED, inféré]
  P2 <a> sans href exploitable (javascript:, absent) (1) [ESTABLISHED, inféré]
  P2 meta description manquante (1) [ESTABLISHED, inféré]
  module ai_access: ran -- 25 crawlers, 0 bloqué(s)
  module crawl: ran -- 7 page(s) récupérée(s), 6/6 URL(s) du sitemap, 0 lien(s) découvert(s) non visité(s)
  module link_graph: ran -- 13 lien(s) interne(s), 1 rubrique(s)
  module pagespeed: skipped -- PAGESPEED_API_KEY absente
  module indexnow: skipped -- variable INDEXNOW_KEY absente
```
L'URL orpheline est `/lonely.html` : présente dans le sitemap, liée par
aucune page. Les problèmes de ce site sont plantés volontairement pour les
tests.

## Livrables
- Le rapport `audit_*.md` + `.json` de `run_audit.py`, et `diff_*.md` au
  passage suivant.
- `CHANGELOG_GEO.md` dans le projet audité : chaque modification et son but.
- La sortie de `validate_schema.py` avant de clore une tâche schema.

## Scripts
| Script | Rôle | Accès requis |
|---|---|---|
| [run_audit.py](scripts/run_audit.py) | **Point d'entrée** : audit complet, plan priorisé, correctifs sûrs, diff | optionnel (env) |
| [diff_reports.py](scripts/diff_reports.py) | Évolution entre deux rapports ; sortie 1 si un P0 apparaît | aucun |
| [check_ai_access.py](scripts/check_ai_access.py) | robots.txt (RFC 9309) + accès HTTP par crawler vs navigateur | aucun |
| [generate_report.py](scripts/generate_report.py) | Rapport sur une liste d'URLs choisie | optionnel |
| [validate_schema.py](scripts/validate_schema.py) | JSON-LD vs exigences Google, types retirés, avis auto-attribués | aucun |
| [generate_sitemap.py](scripts/generate_sitemap.py) | sitemap.xml conforme + robots.txt (`--ai-policy open\|search-only`) | aucun |
| [indexnow_submit.py](scripts/indexnow_submit.py) | IndexNow avec contrôle de la clé et de sa portée | `INDEXNOW_KEY` |
| [pagespeed.py](scripts/pagespeed.py) | PageSpeed Insights : labo + terrain | `PAGESPEED_API_KEY` |
| [crux_report.py](scripts/crux_report.py) | Core Web Vitals terrain | `CRUX_API_KEY` |
| [gsc_report.py](scripts/gsc_report.py) | Search Console (web, discover, googleNews, news, image, video) | compte de service |
| [crawler_logs.py](scripts/crawler_logs.py) | Journaux serveur : crawlers réels, IP vérifiées contre les listes des fournisseurs, 5xx, 404, couverture du sitemap ; aucune IP écrite | aucun (lit les listes publiques) |
| [glossary_check.py](scripts/glossary_check.py) | Glossaire : `build` (HTML + JSON-LD depuis un fichier de termes), `audit` (balisage visible, ancres, occasions de liens), `suggest` (termes candidats) | aucun |
| [audit_site.sh](scripts/audit_site.sh), [check_backlinks.sh](scripts/check_backlinks.sh) | Passe curl rapide ; liens suivis/nofollow d'une page | aucun |

Modules partagés :
- [audit_rules.py](scripts/audit_rules.py) : catalogue des règles
  (priorité, étiquette, source) ;
- [linkgraph.py](scripts/linkgraph.py) : maillage et cocon ;
- [sitemaps.py](scripts/sitemaps.py), [htmlsignals.py](scripts/htmlsignals.py),
  [robotstxt.py](scripts/robotstxt.py) ;
- [ai_bots.py](scripts/ai_bots.py) : catalogue des crawlers ;
- [envkeys.py](scripts/envkeys.py) : secrets ;
- [report_markdown.py](scripts/report_markdown.py).

Tests hors ligne, dont un audit complet sur un site de test servi en
127.0.0.1 : `python -m unittest discover -s tests`.

## Évaluations
[evals/evals.json](evals/evals.json) : 6 cas (audit complet, site non cité
par les IA, journaux serveur, schema Product, planification et IndexNow,
glossaire), au format du skill-creator d'Anthropic (`prompt`,
`expected_output`, `expectations`). Ce sont des critères à faire vérifier
par un relecteur ou par le skill-creator ; ils ne s'exécutent pas seuls.

## Installation
- Personnelle : `~/.claude/skills/seo-geo-optimizer/`.
- Par projet : `.claude/skills/seo-geo-optimizer/`.
- Python 3.10+, bibliothèque standard uniquement.
  `pip install google-auth requests` n'est nécessaire que pour Search
  Console.

Voir [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Références et attributions
Méthodes de Laurent Bourrelly et de Stéphane Delgado, citées et étiquetées
dans [french-practitioners.md](references/french-practitioners.md).
Attributions : [docs/LEGAL_AND_ATTRIBUTION.md](docs/LEGAL_AND_ATTRIBUTION.md).
