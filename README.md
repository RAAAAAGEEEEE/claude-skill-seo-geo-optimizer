# seo-geo-optimizer

Skill Claude Code qui audite puis corrige, dans le dépôt d'un site, sa
visibilité dans Google (y compris AI Overviews, AI Mode, Discover) et dans
les moteurs de réponse IA (ChatGPT, Claude, Perplexity, Gemini, Copilot,
Mistral). L'audit complet tourne sans intervention, se planifie, et compare
chaque rapport au précédent. Le skill opère aussi Search Console avec les
accès du propriétaire (sitemaps, inspection des URL) et fait découvrir les
nouvelles pages sans navigateur.

**Statut : bêta.** Version 2.4.0, connaissances revues le 2026-09-28,
découverte des URL et Search Console le 2026-09-30
([CHANGELOG.md](CHANGELOG.md)). Le skill est utilisé en conditions réelles
sur quelques sites. Ses scripts sont testés (91 tests hors ligne). Le
comportement du skill lui-même est décrit par 8 cas d'évaluation
([evals/evals.json](evals/evals.json)), à faire relire ou passer par le
skill-creator d'Anthropic : il n'existe pas de exécution automatique.

## Le problème
Un site peut être invisible pour les moteurs de réponse IA sans que personne
le voie. Quelques cas réels :
- un CDN qui renvoie 403 à `ClaudeBot` alors que `robots.txt` l'autorise ;
- un `nosnippet` oublié ;
- une URL inconnue qui répond 500 ;
- une page du sitemap qu'aucune autre page ne lie.

En parallèle, les conseils « GEO » circulent sans source : `llms.txt`
miracle, schema « pour l'IA », seuils de maillage présentés comme des règles.

## Pour qui
Développeurs et indépendants qui maintiennent un site vitrine, un SaaS, un
e-commerce, un commerce local ou un site de contenu. Ils veulent un audit
re-exécutable et planifiable plutôt qu'une liste de bonnes pratiques.

## Ce que le skill apporte
- **Une commande, un rapport daté** : `run_audit.py` écrit un rapport
  Markdown et JSON avec un plan P0/P1/P2. Il couvre :
  - l'accès réel des crawlers ;
  - les sitemaps ;
  - la cohérence canonical, hreflang et noindex ;
  - le JSON-LD ;
  - les 404 ;
  - le maillage interne et le cocon ;
  - en option : PageSpeed, CrUX, Search Console et IndexNow.
- **Découverte des nouvelles URL, sans navigateur** : `url_discovery.py`
  contrôle `Sitemap:` dans robots.txt, `lastmod`, le lien depuis l'accueil
  et le hub WebSub des flux ; avec `--submit` (accord du propriétaire), il
  re-soumet le sitemap par l'API Search Console, notifie le hub WebSub et
  envoie les URL changées à IndexNow. Pas d'Indexing API (réservée aux
  offres d'emploi et vidéos en direct), pas de ping sitemap (mort depuis
  2023). Planifiable chaque jour
  ([references/url-discovery.md](references/url-discovery.md)).
- **Search Console opérée par l'agent** : tutoriel numéroté pour brancher
  un compte de service ([references/gsc-access.md](references/gsc-access.md)),
  puis `search_console.py` : sitemaps, inspection des URL (quota 2 000 par
  jour) avec la cause de non-indexation, statistiques. La demande
  d'indexation manuelle reste un bonus optionnel, dans le navigateur de
  l'utilisateur.
- **Suivi dans le temps** : chaque passage est comparé au précédent
  (`diff_*.md`), avec un code de sortie 1 si un problème bloquant apparaît.
  C'est utilisable dans un cron.
- **Preuves étiquetées** : chaque règle porte une source datée et une
  étiquette. ESTABLISHED = documentation officielle, SUPPORTED = étude
  indépendante, CLAIMED = praticien ou vendeur. Les méthodes de Laurent
  Bourrelly (cocon sémantique) et de Stéphane Delgado (GEO, maillage) sont
  intégrées comme CLAIMED, confrontées à la documentation de Google
  ([references/french-practitioners.md](references/french-practitioners.md)).
- **Ce qui s'automatise, et ce qui est interdit** : analyse des journaux
  serveur avec vérification des IP des crawlers (`crawler_logs.py`),
  glossaire construit et audité depuis les données du site
  (`glossary_check.py`), et les limites posées par Google
  ([references/automation.md](references/automation.md),
  [references/glossary.md](references/glossary.md)).
- **Quels contenus publier** : table de décision par type de site (site de
  référence ou base de produits, média, SaaS, e-commerce, local, site de
  données) pour les comparatifs, guides d'achat, tests, fiches techniques,
  données originales, tutoriels, FAQ, définitions, outils et pages auteur.
  Chaque ligne dit ce que Google documente et ce que mesurent les études
  de citations IA ([references/content-formats.md](references/content-formats.md)).

## Exemple de sortie
Sortie réelle de `run_audit.py` sur le site de test du dépôt
(`tests/fixtures/site/`, servi sur 127.0.0.1), exécutée le 2026-09-29, sans
aucune clé. Les problèmes de ce site sont plantés volontairement :
```
Resultat : P0=0 P1=4 P2=6 ; 7 page(s), 42 requete(s)
  P1 URL du sitemap en noindex (1) [ESTABLISHED, mesuré]
  P1 Page auditée hors 200 (1) [ESTABLISHED, inféré]
  P1 Lien interne vers une URL en erreur (4xx/5xx) (1) [ESTABLISHED, mesuré]
  P1 Page du sitemap sans aucun lien interne entrant (orpheline) (1) [ESTABLISHED, inféré]
  P2 Page indexable quasi vide (risque de soft 404) (4) [ESTABLISHED, inféré]
  P2 Page fille sans lien vers sa page mère (cocon) (1) [CLAIMED, inféré]
  P2 Page sans lien contextuel sortant (1) [CLAIMED, inféré]
  module ai_access: ran -- 25 crawlers, 0 bloqué(s)
  module pagespeed: skipped -- PAGESPEED_API_KEY absente
```
(Extrait : 3 constats P2 et 8 modules ne sont pas repris.)

## Prérequis
- Python 3.10+. Tous les scripts se contentent de la bibliothèque standard,
  sauf pour transformer une clé de compte de service Search Console en
  jeton (`google-auth`).
- Bash et curl, seulement pour `audit_site.sh` et `check_backlinks.sh`.
- Optionnel : une clé API Google (PageSpeed / CrUX), un compte de service
  Search Console (`pip install google-auth requests`), une clé IndexNow.

## Installation
```bash
git clone https://github.com/RAAAAAGEEEEE/claude-skill-seo-geo-optimizer.git ~/.claude/skills/seo-geo-optimizer
```
Pour un seul projet : `.claude/skills/seo-geo-optimizer/` à la racine du
projet. Détail : [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Démarrage rapide
Depuis le dossier du skill :
```bash
# Audit complet (lecture seule), rapport dans ./seo-reports/<hôte>/
python scripts/run_audit.py --site https://example.com

# Relancé plus tard : un diff_*.md compare au rapport précédent
python scripts/diff_reports.py --dir seo-reports/example.com

# Découverte des nouvelles URL, lecture seule (ajouter --submit après accord)
python scripts/url_discovery.py --site https://example.com

# Tests hors ligne
python -m unittest discover -s tests
```
Codes de sortie de `run_audit.py` : 0 = aucun P0, 1 = au moins un P0,
2 = accueil injoignable. Planification (cron, Windows, Claude Code) :
[docs/USAGE.md](docs/USAGE.md#planifier-laudit).

## Compatibilité
Le skill suit le format ouvert des Agent Skills (`name`, `description`,
`license`, `compatibility`, `metadata` dans le front-matter de
[SKILL.md](SKILL.md)). Il est conçu et testé avec Claude Code. Les scripts
de `scripts/` s'exécutent aussi seuls, sans agent. Le front-matter ne
contient aucun champ propre à Claude Code.

Skill compagnon : [citation-engine-skill](https://github.com/RAAAAAGEEEEE/citation-engine-skill)
(prospection et digital PR, commande `/seo`). Ce skill-ci audite et modifie
le site courant ; l'autre ne touche pas au code du site.

## Architecture
- `SKILL.md` : la procédure que suit Claude (PLAN → FIX → VERIFY).
- `references/` : le détail daté et sourcé, chargé à la demande.
- `scripts/` : `run_audit.py` orchestre des modules testables (règles,
  sitemaps, maillage, secrets).
- `tests/` : tests hors ligne.
- `evals/` : cas d'évaluation du comportement du skill.

Détail : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Configuration
Aucune configuration n'est requise pour l'audit de base. Les accès
optionnels se donnent **uniquement par variables d'environnement** :
`PAGESPEED_API_KEY`, `CRUX_API_KEY`, `GSC_SERVICE_ACCOUNT_FILE` (ou
`GSC_ACCESS_TOKEN`), `GSC_SITE`, `INDEXNOW_KEY`. Voir [.env.example](.env.example) et
[docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Sécurité et confidentialité
Par défaut, le skill n'envoie que des requêtes GET publiques vers le site
audité, en respectant robots.txt. Des données ne partent vers des tiers que
si l'accès correspondant est fourni (API Google, Search Console).
La soumission IndexNow, la soumission de sitemap et la notification WebSub
exigent une option explicite (`--indexnow-submit`, `--submit`,
`submit-sitemap`), car ce sont des actions externes. La demande
d'indexation manuelle ne se fait qu'avec l'accord du propriétaire, sans
jamais saisir d'identifiant ni résoudre de CAPTCHA. Les clés ne sont jamais affichées ni écrites dans un rapport.
Voir [SECURITY.md](SECURITY.md) et
[docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).

## Limites
- Pas de rendu JavaScript : ce qui est injecté côté client est invisible.
- Les user-agents des crawlers sont simulés : un 200 ne prouve pas que le
  vrai crawler passe.
- Le maillage « contextuel » dépend des balises `<main>`/`<nav>`, et les
  rubriques sont déduites des répertoires d'URL.
- Aucune mesure directe des citations dans ChatGPT, Claude ou Perplexity.
- Aucune garantie d'indexation : sitemap, WebSub et IndexNow informent les
  moteurs, qui décident. La soumission de sitemap par l'API et la
  notification WebSub ne sont couvertes que par des tests hors ligne.
- Journaux serveur : vérification par listes d'IP seulement (Meta et Amazon
  restent non vérifiables).
- Les seuils de praticiens restent des heuristiques.
- Les parts de citation IA par format viennent d'études de vendeurs
  d'outils (CLAIMED) : des corrélations, pas des causes.

Liste complète : [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Feuille de route (non contractuelle)
- Lecture du rapport IA de Search Console, si Google l'expose dans l'API.
- Rendu JavaScript optionnel (navigateur sans interface) pour les sites en
  rendu client.
- Vérification des crawlers par DNS inverse et signatures Web Bot Auth,
  en complément des listes d'IP.

## Contribution
Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence
MIT — voir [LICENSE](LICENSE).

## Documentation
- [SKILL.md](SKILL.md) : la procédure.
- [docs/](docs/) : installation, usage, configuration, dépannage, limites,
  sécurité, attributions.
- [references/](references/) : les règles sourcées.
- [CHANGELOG.md](CHANGELOG.md) : les versions.
