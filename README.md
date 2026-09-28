# seo-geo-optimizer

Skill Claude Code qui audite puis corrige, dans le dépôt d'un site, sa
visibilité dans Google (y compris AI Overviews, AI Mode, Discover) et dans
les moteurs de réponse IA (ChatGPT, Claude, Perplexity, Gemini, Copilot,
Mistral). L'audit complet tourne sans intervention, se planifie, et compare
chaque rapport au précédent.

**Statut : bêta.** Version 2.3.2, connaissances revues le 2026-09-28
([CHANGELOG.md](CHANGELOG.md)). Le skill est utilisé en conditions réelles
sur quelques sites. Ses scripts sont testés (66 tests hors ligne), mais le
comportement du skill lui-même n'a pas de suite d'évaluation.

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
Extrait réel de `run_audit.py` sur un site réel, le 2026-09-27 à 22:32 UTC
(aucune clé fournie) :
```
Resultat : P0=0 P1=1 P2=4 ; 25 page(s), 80 requete(s)
  P1 Page du sitemap sans aucun lien interne entrant (orpheline) (1) [ESTABLISHED, inféré]
  P2 Page indexable quasi vide (risque de soft 404) (6) [ESTABLISHED, inféré]
  P2 Page en noindex liée en interne : vérifier que c'est voulu (4) [ESTABLISHED, inféré]
  P2 Page sans lien contextuel sortant (11) [CLAIMED, inféré]
  P2 Page liée uniquement depuis la navigation (aucun lien contextuel entrant) (6) [CLAIMED, inféré]
  module ai_access: ran -- 25 crawlers, 0 bloqué(s)
  module pagespeed: skipped -- PAGESPEED_API_KEY absente
```

## Prérequis
- Python 3.10+. Tous les scripts se contentent de la bibliothèque standard,
  sauf `gsc_report.py`.
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

# Tests hors ligne
python -m unittest discover -s tests
```
Codes de sortie de `run_audit.py` : 0 = aucun P0, 1 = au moins un P0,
2 = accueil injoignable. Planification (cron, Windows, Claude Code) :
[docs/USAGE.md](docs/USAGE.md#planifier-laudit).

## Architecture
- `SKILL.md` : la procédure que suit Claude (PLAN → FIX → VERIFY).
- `references/` : le détail daté et sourcé, chargé à la demande.
- `scripts/` : `run_audit.py` orchestre des modules testables (règles,
  sitemaps, maillage, secrets).
- `tests/` : tests hors ligne.

Détail : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Configuration
Aucune configuration n'est requise pour l'audit de base. Les accès
optionnels se donnent **uniquement par variables d'environnement** :
`PAGESPEED_API_KEY`, `CRUX_API_KEY`, `GSC_SERVICE_ACCOUNT_FILE`, `GSC_SITE`,
`INDEXNOW_KEY`. Voir [.env.example](.env.example) et
[docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Sécurité et confidentialité
Par défaut, le skill n'envoie que des requêtes GET publiques vers le site
audité, en respectant robots.txt. Des données ne partent vers des tiers que
si l'accès correspondant est fourni (API Google, Search Console).
La soumission IndexNow exige une option explicite, car c'est une action
externe. Les clés ne sont jamais affichées ni écrites dans un rapport.
Voir [SECURITY.md](SECURITY.md) et
[docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md).

## Limites
- Pas de rendu JavaScript : ce qui est injecté côté client est invisible.
- Les user-agents des crawlers sont simulés : un 200 ne prouve pas que le
  vrai crawler passe.
- Le maillage « contextuel » dépend des balises `<main>`/`<nav>`, et les
  rubriques sont déduites des répertoires d'URL.
- Aucune mesure directe des citations dans ChatGPT, Claude ou Perplexity.
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
