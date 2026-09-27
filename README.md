# seo-geo-optimizer

Skill Claude Code qui audite puis corrige, dans le dépôt d'un site, sa
visibilité dans Google (y compris AI Overviews, AI Mode, Discover) et dans
les moteurs de réponse IA (ChatGPT, Claude, Perplexity, Gemini, Copilot,
Mistral).

**Statut : bêta** — version 2.0.0, connaissances revues le 2026-09-27
([CHANGELOG.md](CHANGELOG.md)). Utilisé en conditions réelles sur quelques
sites ; pas de suite d'évaluation du comportement du skill lui-même, seuls
ses scripts sont testés.

## Le problème
Un site peut être invisible pour les moteurs de réponse IA sans que personne
le voie : un CDN qui renvoie 403 à `ClaudeBot` alors que `robots.txt`
l'autorise, un `nosnippet` oublié, une URL inconnue qui répond 500, une page
de langue qui duplique le français. En parallèle, les conseils « GEO »
circulent sans source : `llms.txt` miracle, schema « pour l'IA »,
statistiques recopiées de blog en blog.

## Pour qui
Développeurs et indépendants qui maintiennent un site vitrine, un SaaS, un
e-commerce, un commerce local ou un site de contenu, et qui veulent un audit
re-exécutable plutôt qu'une liste de bonnes pratiques.

## Ce que le skill apporte
- **Accès réel des crawlers** : `robots.txt` interprété selon la RFC 9309,
  puis requête de la page avec le user-agent documenté de chaque crawler,
  comparée à un navigateur. Détecte le blocage CDN silencieux.
- **Audit consolidé** sur un vrai parseur HTML : redirections temporaires,
  `noindex`/`nosnippet` (meta et en-tête), canonical, lang, H1, JSON-LD
  validé contre les exigences Google, hreflang, et en option Core Web Vitals
  terrain et Search Console.
- **Preuves étiquetées** : chaque affirmation des références porte une source
  datée et une étiquette ESTABLISHED (doc officielle), SUPPORTED (étude
  indépendante) ou CLAIMED (vendeur, blog). Les croyances démenties sont
  listées ([references/evidence.md](references/evidence.md)).

## Exemple de sortie
Extrait réel de `generate_report.py` sur un site réel, 2026-09-27 :
```
### https://example.com/
- Redirections : 307 https://example.com/fr
- **redirection temporaire 307 vers https://example.com/fr : utiliser 301/308 si le deplacement est definitif**

### https://example.com/fr/robots/nexiste-pas
- **HTTP 500 : erreur serveur (une URL inconnue doit repondre 404/410, jamais 5xx ; des 5xx repetes ralentissent le crawl)**
```

## Prérequis
- Python 3.10+ (bibliothèque standard uniquement pour tous les scripts sauf
  `gsc_report.py`) ; Bash et curl pour `audit_site.sh` et
  `check_backlinks.sh`.
- Optionnel : `pip install google-auth requests` (Search Console), une clé
  API Chrome UX Report gratuite (Core Web Vitals terrain).

## Installation
```bash
git clone https://github.com/RAAAAAGEEEEE/claude-skill-seo-geo-optimizer.git ~/.claude/skills/seo-geo-optimizer
```
Ou, pour un seul projet, dans `.claude/skills/seo-geo-optimizer/` à la
racine du projet. Claude Code le déclenche sur une demande d'audit SEO/GEO.

## Démarrage rapide
Depuis le dossier du skill :
```bash
# 1. Les crawlers de recherche et d'IA accèdent-ils vraiment au site ?
python scripts/check_ai_access.py https://example.com

# 2. Rapport consolidé (Markdown + JSON)
printf 'https://example.com/\n' > urls.txt
python scripts/generate_report.py --urls urls.txt --out-prefix AUDIT_GEO --check-ai-access

# 3. Valider du JSON-LD (fichier HTML, .json ou URL)
python scripts/validate_schema.py tests/fixtures/schema_cases.html

# 4. Tests hors ligne des scripts
python -m unittest discover -s tests
```
Codes de sortie de `check_ai_access.py` : 0 aucun blocage, 1 blocage,
2 non concluant (la page ne répond pas 200 à un navigateur).

## Architecture
- `SKILL.md` : la procédure que suit Claude (PLAN → FIX → VERIFY), courte.
- `references/` : le détail daté et sourcé, chargé à la demande.
- `scripts/` : outils re-exécutables ; modules partagés `ai_bots.py`
  (catalogue des crawlers), `robotstxt.py` (RFC 9309), `htmlsignals.py`
  (extraction HTML).
- `tests/` : tests unitaires hors ligne et fixture JSON-LD.

## Configuration
Aucune configuration requise. Les accès optionnels passent en arguments :
`--crux-key` (clé API CrUX), `--gsc-service-account` + `--gsc-site`
(compte de service Search Console, mise en place dans
[references/gsc-access.md](references/gsc-access.md)), `--key` pour
IndexNow. Garder clés et fichiers de compte hors du dépôt.

## Sécurité et confidentialité
Par défaut, uniquement des requêtes GET publiques vers le site audité.
Envois vers des tiers seulement sur option explicite : API CrUX (clé en
paramètre d'URL), API Search Console (jeton OAuth), IndexNow (les URLs
soumises sont partagées avec tous les moteurs participants — action externe,
à confirmer). Le skill ne modifie aucun compte (Search Console, CDN, Google
Business Profile).

## Limites
- Les tests d'accès utilisent des user-agents simulés depuis votre machine :
  un 403 prouve une règle par user-agent, un 200 ne prouve pas que le vrai
  crawler (identifié par IP ou signature) passe.
- Pas de rendu JavaScript : un schema injecté côté client est invisible pour
  les scripts (utiliser le Rich Results Test).
- Les user-agents complets de ClaudeBot, Claude-User et Claude-SearchBot ne
  sont pas publiés par Anthropic : le script utilise une chaîne construite
  autour du jeton.
- Le rapport « Generative AI performance » de Search Console et le rapport
  « AI Performance » de Bing ne sont pas accessibles par API : lecture
  manuelle.
- Aucune mesure directe des citations dans ChatGPT, Claude ou Perplexity.
- Connaissances datées : au-delà de 3 mois, revérifier les références.
- Pas de dossier `docs/` ni de `CONTRIBUTING.md` à ce jour.

## Feuille de route (non contractuelle)
- Lecture du rapport IA de Search Console si Google l'expose dans l'API.
- Script Google Business Profile quand un accès API pourra être testé.
- Vérification optionnelle des IP réelles des crawlers dans des journaux
  serveur fournis par l'utilisateur.

## Contribution
Issues et pull requests bienvenues. Toute modification de script passe
`python -m unittest discover -s tests` ; toute affirmation ajoutée dans
`references/` porte une source primaire datée et son étiquette.

## Licence
MIT — voir [LICENSE](LICENSE).

## Documentation
[SKILL.md](SKILL.md) (procédure) · [references/](references/) (détail) ·
[CHANGELOG.md](CHANGELOG.md) (versions).
