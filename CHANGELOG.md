# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Les versions 1.x sont reconstituées depuis l'historique git.

## [2.3.3] — 2026-09-29

Préparation à la publication communautaire. Aucun comportement de script
modifié. 66 tests.

### Ajouté
- `evals/evals.json` : 6 cas d'évaluation du comportement du skill, au
  format du skill-creator d'Anthropic.
- Front-matter de `SKILL.md` portable : `license`, `compatibility`,
  `metadata` (auteur, version, dépôt). Description ramenée sous 1024
  caractères.
- Section « Compatibilité » du README et lien vers le skill compagnon
  `seo` ([citation-engine-skill](https://github.com/RAAAAAGEEEEE/citation-engine-skill)).

### Modifié
- Exemples de sortie : remplacés par des exécutions réelles sur les sites de
  démonstration locaux (`tests/fixtures/site/`), datées du 2026-09-29.
- Anonymisation : noms de sites et de serveurs privés remplacés par
  `example.com` et `acme` dans la documentation, `.env.example`, les
  commentaires et les tests.
- Le skill compagnon s'appelle désormais `seo` (commande `/seo`).

## [2.3.2] — 2026-09-28

Posts X de Laurent Bourrelly. Aucun script modifié. 66 tests.

### Modifié
- `references/french-practitioners.md` : les 100 derniers posts originaux
  de `@aibloodmoon`, compte actif de Laurent Bourrelly (l'ancien est
  suspendu), lus le 2026-09-28 avec l'outil de lecture du propriétaire
  (comptes utilisateur, pas l'API X). 14 portent sur le SEO/GEO ; 9
  méthodes reprises avec lien et date (BX1 à BX9, CLAIMED). Ajouts : étape
  manuelle « lecture de la SERP » (BX2) ; confirmation Google datée de la
  neutralisation des liens achetés (BX5, 2022-12-14). Conflits signalés :
  réseau de liens privé et achat d'un lien « pour tester » (*link spam*),
  et contradiction entre BX4 (0 achat de lien) et BX6.

## [2.3.1] — 2026-09-28

Renvois vers le nouveau skill `redaction`. Aucun script modifié. 66 tests.

### Modifié
- `SKILL.md` : la rédaction des pages planifiées renvoie au skill
  `redaction` (périmètre et « Quand l'utiliser ») ; `copywriting` reste
  cité pour la structure des pages de vente.
- `references/content-formats.md` : renvoi vers `redaction` pour écrire
  les formats retenus.

## [2.3.0] — 2026-09-28

Formats de contenu et lecture des posts X des praticiens. Aucune rupture :
aucun script ne change de comportement (seuls la version et le user-agent
passent à 2.3). Aucun test ajouté : aucun script ajouté. 66 tests.

### Ajouté
- `references/content-formats.md` : quels formats publier pour être classé
  par Google et cité par les moteurs IA, au 2026-09-28.
  - Ce que Google documente : helpful content, guide IA (contenu non
    banal, test de première main), *reviews system* (tests, comparatifs,
    classements ; français inclus), bonnes pratiques des tests, *thin
    affiliation*, dates, données structurées encore utiles par format.
  - Ce que mesurent les études de citations : 4 déclarations de moteurs
    (ESTABLISHED), 7 études indépendantes (SUPPORTED), 8 études de vendeurs
    (CLAIMED), avec leurs conflits (comparatifs, listes « best », FAQ,
    réécriture pour l'IA) et les formats sans aucune donnée.
  - 13 fiches de format (fiche produit, comparatif, classement, guide
    d'achat, test, données originales, chronologie, tutoriel, FAQ,
    définitions, changelog, calculateur, page auteur) : Google, études,
    condition pour publier, risque de spam.
  - Table de décision pour 6 types de site : référence ou base de
    produits, média, SaaS, e-commerce, local, données ou observatoire.

### Modifié
- `SKILL.md` : planification de contenu dans l'étape 3, levier « Formats
  de contenu », déclencheur et exemple d'invocation.
- `references/checklist.md` : contrôles avant de planifier un format.
- `references/evidence.md` : renvoi vers les études par format.
- `references/french-practitioners.md` : posts X lus le 2026-09-28 avec
  l'outil de lecture du propriétaire (comptes utilisateur, pas l'API X).
  - `@laurentbourelly` : compte suspendu, 0 post lu.
  - `@stephdelgado` (lien du site) : compte inactif. Compte actif :
    `@Stephanedelgado`, confirmé par le lien de sa bio vers son site.
    10 posts renvoyés, 9 originaux, 3 sur le SEO/GEO, repris avec lien et
    date (X1 à X3, CLAIMED). Aucun nouveau contrôle : X1 résume D1 à D6 ;
    « ChatGPT ignore les backlinks » reste non vérifiable.
- `docs/` : USAGE (planifier du contenu), ARCHITECTURE, LIMITATIONS,
  LEGAL_AND_ATTRIBUTION, INSTALLATION, PRIVACY_AND_SECURITY ; README et
  CONTRIBUTING.

## [2.2.0] — 2026-09-28

Techniques automatisables, journaux serveur et glossaire. Aucune rupture :
les sorties de `run_audit.py`, `generate_report.py` et `check_ai_access.py`
sont inchangées (seuls la version et le user-agent passent à 2.2).

### Ajouté
- `scripts/crawler_logs.py` : analyse des journaux serveur (*combined* ou
  JSON lines, `.gz` accepté). Pour chaque crawler, il compte les requêtes,
  les statuts et les pages les plus demandées. Il vérifie les IP contre les
  17 listes JSON publiées (Google, Bing, OpenAI, Perplexity, Anthropic,
  Apple, DuckDuckGo, Common Crawl, Mistral) et signale :
  - les 5xx et 429 servis aux crawlers ;
  - un robots.txt servi hors 200 ;
  - les usurpations de user-agent ;
  - les 404 les plus demandés ;
  - les URLs du sitemap jamais récupérées.

  Aucune adresse IP n'est écrite dans la sortie.
- `scripts/glossary_check.py` : `build` (HTML `<dl>` et JSON-LD
  `DefinedTermSet` depuis un fichier de termes, sans rien inventer), `audit`
  (balisage invisible, ancres cassées, définitions courtes, occasions de
  liens sur un échantillon du sitemap, termes jamais cités), `suggest`
  (sigles, `<abbr>`, `<dfn>` présents sur plusieurs pages).
- `references/automation.md` : ce qu'un script ou un agent planifié peut
  faire seul au 2026-09-28, classé par valeur et effort. Couvre :
  - les API Search Console et Bing, et ce qu'elles n'exposent pas (rapports
    IA) ;
  - la vérification des crawlers ;
  - les flux de fraîcheur ;
  - le suivi des citations IA : ce que renvoient les API d'OpenAI, de
    Perplexity et d'Anthropic, et pourquoi le grounding Gemini et le
    scraping de Google sont exclus par leurs conditions ;
  - la veille de mentions ;
  - la liste de ce que Google interdit quand on automatise.
- `references/glossary.md` : verdict sur les glossaires. SEO : utile sous
  conditions (ESTABLISHED, règles générales). Citations IA : non démontré.
  `DefinedTerm` : aucun rich result. Recette en 9 points, risques, et
  contrôles du script.
- `tests/test_glossary_logs.py` : 14 tests hors ligne et leurs fixtures
  (`tests/fixtures/glossary/`, `tests/fixtures/logs/`). 66 tests au total.

### Modifié
- `SKILL.md` : glossaire et journaux dans l'étape 3 ; leviers « Glossaire »
  et « Automatisation » ; deux scripts ; replis et confidentialité.
- `references/checklist.md` : glossaire, journaux serveur, limites du suivi
  des citations par API.
- `references/evidence.md` : deux croyances démenties (glossaire « 3 à 5
  fois plus cité », suivi des citations par scraping de Google).
- `references/schema-templates.md` : statut de `DefinedTermSet` et gabarit.
- `references/french-practitioners.md` : comptes X confirmés depuis leurs
  sites (`@laurentbourelly`, `@stephdelgado`). La lecture des posts a
  échoué : le jeton API a été refusé (401). Aucun post n'a été lu, et rien
  de ce fichier ne vient de X.
- `docs/` : USAGE (deux sections, commandes exécutées), ARCHITECTURE,
  LIMITATIONS, PRIVACY_AND_SECURITY (listes d'IP, journaux), TROUBLESHOOTING,
  LEGAL_AND_ATTRIBUTION (définitions ISO et Wikipedia), INSTALLATION ;
  README et CONTRIBUTING.

## [2.1.0] — 2026-09-28

Audit complet sans intervention, méthodes des praticiens français, et
documentation mise au standard. Aucune rupture : les sorties de
`generate_report.py` et de `check_ai_access.py` sont inchangées.

### Ajouté
- `scripts/run_audit.py`, point d'entrée unique. En une commande, il produit
  un rapport daté (Markdown et JSON) avec un plan P0/P1/P2, et un diff avec
  le rapport précédent. Il couvre :
  - l'accueil et robots.txt ;
  - l'accès des crawlers ;
  - les sitemaps (index, gzip, lastmod) ;
  - un crawl qui respecte robots.txt ;
  - des sondes 404 sous chaque rubrique ;
  - la cohérence sitemap, canonical, hreflang, noindex et langue ;
  - le maillage interne ;
  - en option : PageSpeed, CrUX, Search Console, IndexNow.

  Codes de sortie : 0 = aucun P0, 1 = au moins un P0, 2 = non concluant.
- Correctifs sûrs, qui ne touchent pas le site :
  - un sitemap proposé (URLs vérifiées, lastmod jamais inventé) ;
  - la liste des URLs nouvelles ou modifiées pour IndexNow ;
  - la soumission IndexNow, seulement avec `--indexnow-submit`.
- `scripts/linkgraph.py` : profondeur de clic, orphelines, liens cassés ou
  vers une redirection, ancres génériques, vides ou répétées, liens
  contextuels (`<main>`/`<article>`) et liens de navigation, tableau
  cocon/silos par répertoire.
- `scripts/audit_rules.py` : catalogue unique des règles (code, priorité,
  étiquette, source, correctif). Une règle CLAIMED est toujours P2.
- `scripts/sitemaps.py`, `scripts/pagespeed.py` (PageSpeed Insights v5, labo
  et terrain), `scripts/envkeys.py` (secrets lus dans l'environnement,
  masqués dans les sorties), `scripts/diff_reports.py`,
  `scripts/report_markdown.py`.
- `htmlsignals.py` relève les liens `<a>` (URL résolue, ancre, zone de page)
  et le nombre de mots visibles.
- `references/french-practitioners.md` : méthodes publiques de Laurent
  Bourrelly et de Stéphane Delgado, étiquetées, confrontées à Google, avec
  ce qui entre dans le skill et ce qui n'y entre pas.
- `tests/test_automation.py` : 22 tests, dont un audit complet sur un site
  de test servi en 127.0.0.1 et un contrôle d'absence de secret dans les
  sorties. 52 tests au total.
- `CONTRIBUTING.md`, `SECURITY.md`, `.env.example`, et `docs/` :
  ARCHITECTURE, INSTALLATION, USAGE (dont la planification), CONFIGURATION,
  TROUBLESHOOTING, LIMITATIONS, PRIVACY_AND_SECURITY, LEGAL_AND_ATTRIBUTION.

### Modifié
- `SKILL.md` : la procédure commence par `run_audit.py`. Ajouts : entrées et
  sorties, levier « Maillage / cocon », étape de planification (sur
  confirmation), et un nouvel exemple réel.
- `generate_report.py` : les constats par page viennent de
  `audit_rules.py`, avec le même libellé qu'avant. La clé CrUX se lit dans
  `CRUX_API_KEY` ; `--crux-key` est déprécié.
- `crux_report.py` et `indexnow_submit.py` : la clé se lit dans
  l'environnement (`CRUX_API_KEY`, `INDEXNOW_KEY` ou `--key-env`) ; `--key`
  est déprécié. La clé IndexNow est masquée dans les messages.
- Références `audit-framework.md`, `checklist.md`, `indexing-rules.md`,
  `gsc-access.md` : maillage et cocon, automatisation, variables
  d'environnement.
- `README.md` raccourci ; le détail est déplacé dans `docs/`.

### Corrigé
- `audit-framework.md` présentait « pages à ≤ 3 clics » comme une règle.
  C'est une convention (CLAIMED) ; seul « au moins un lien interne » vient
  de Google.

## [2.0.0] — 2026-09-27

Revue complète sur sources primaires au 2026-09-27. Rupture : sortie JSON de
`check_ai_access.py` et de `generate_report.py` modifiée, un fichier de
référence renommé.

### Ajouté
- Étiquettes de preuve ESTABLISHED / SUPPORTED / CLAIMED sur toutes les
  références, avec source et date (`references/data-hygiene.md`).
- `references/google-ai-features.md` : AI Overviews et AI Mode en France
  (2026-07-22), réglage Search Console « Search generative AI » (mondial le
  2026-08-31), rapports « Generative AI performance », sources préférées,
  Discover, Google Actualités, mises à jour de classement 2026.
- `references/licensing-signals.md` : llms.txt, RSL 1.0 (vocabulaire exact),
  IETF aipref, Content Signals, Pay per crawl, Markdown pour agents.
- `references/evidence.md` : études sur les citations IA, déclarations des
  moteurs, croyances démenties.
- `references/eeat-news.md` : E-E-A-T selon Google, signaux d'éditeur,
  `NewsMediaOrganization`, Trust Project, JTI.
- `scripts/ai_bots.py` : catalogue unique des crawlers (rôles engine,
  search, user, training, token) avec user-agents documentés.
- `scripts/robotstxt.py` : interprétation RFC 9309 (groupes, plus long motif,
  jokers, codes HTTP ; 429 traité comme 5xx comme chez Google).
- `scripts/htmlsignals.py` : extraction HTML par parseur, chaîne de
  redirections, `X-Robots-Tag`.
- `tests/` : 30 tests unitaires hors ligne et une fixture JSON-LD.
- `gsc_report.py` : `--search-type` (web, discover, googleNews, news, image,
  video) et `--data-state`.
- `generate_sitemap.py` : `--ai-policy open|search-only`.

### Modifié
- `check_ai_access.py` réécrit : 25 crawlers (dont Google-Agent,
  MistralAI-Index, meta-webindexer, Amzn-SearchBot), user-agents complets,
  référence navigateur, verdicts `ok` / `blocked-upstream` /
  `blocked-by-robots` / `token-only` / `inconclusive`, code de sortie 2 si non
  concluant, lecture des lignes `Sitemap`, `License`, `Content-Signal`,
  `Content-Usage`.
- `generate_report.py` réécrit sur `htmlsignals.py` : détecte redirections
  temporaires, `noindex`, `nosnippet`/`max-snippet:0`, `lang` absent, 5xx ;
  résout les hreflang relatifs ; signale l'absence de `x-default`.
- `validate_schema.py` : exigences Google réelles (Article sans propriété
  requise, Product = `offers` ou `review` ou `aggregateRating`), `@graph`,
  sous-types, types retirés, avis auto-attribués, gabarits non remplis,
  valeurs `null`, lecture d'une URL.
- `references/agent-readiness.md` renommé `references/agent-discovery.md` et
  étendu (registre MCP, server cards, WebMCP, RFC 9727, annuaires OpenAI et
  Anthropic, UCP/ACP).
- `SKILL.md` resserré en procédure PLAN → FIX → VERIFY ; détail déplacé dans
  `references/`.
- `README.md` réécrit selon le standard de documentation.

### Corrigé
- Parseur robots.txt : les règles d'un groupe fuyaient vers le groupe `*`, et
  une ligne `Crawl-delay` redirigeait les règles suivantes vers `*`.
- `Google-Extended` et `Applebot-Extended` testés en HTTP alors qu'aucune
  requête ne porte ces user-agents ; `Google-Extended` présenté à tort comme
  agissant sur AI Overviews.
- `generate_sitemap.py` datait toutes les URLs du jour (`lastmod` faux),
  n'échappait pas le XML et écrivait `changefreq`/`priority` ignorés par Google.
- `indexnow_submit.py` : accepte les clés alphanumériques de la spec et refuse
  une clé hors racine qui ne couvre pas les URLs soumises.
- `check_backlinks.sh` : `sponsored` et `ugc` comptés comme non suivis.
- `audit_site.sh` : colonnes redirection temporaire et `noindex`, comptage
  des vrais blocs JSON-LD.
- `gsc-access.md` : le rôle « Restreint » n'est pas exclu de l'API (droit de
  lecture suffisant, inférence signalée).
- Statistiques non sourcées ou mal datées retirées ou corrigées : « 75 % des
  sites ont une erreur hreflang (étude 2026) » (SEMrush 2017), « ~65 % de
  zéro clic » (chiffre 2020), posts Google Business Profile « expirant après
  7 jours » (archivés après 6 mois).

### Retiré
- Gabarits JSON-LD `FAQPage` et `HowTo` (rich results supprimés) et
  `aggregateRating` du gabarit `LocalBusiness` (avis auto-attribués).

## [1.3.0] — 2026-08-03
### Ajouté
- Réciprocité hreflang dans `generate_report.py` ; références
  agent-readiness, spam-policies, Google Business Profile.

## [1.2.0] — 2026-07-31
### Modifié
- Révision majeure : consignes dépréciées corrigées, contrôle d'accès CDN
  (`check_ai_access.py`), nettoyage.

## [1.1.0] — 2026-07-23
### Ajouté
- Accès Search Console et générateur de rapport consolidé.

## [1.0.1] — 2026-07-21
### Corrigé
- Référence cassée vers un skill supprimé ; chevauchement avec le skill `SEO`.

### Ajouté
- Scripts SEO techniques, cadre backlinks, règles d'indexation, hygiène des
  données.

## [1.0.0] — 2026-07-18
- Première version du skill.
