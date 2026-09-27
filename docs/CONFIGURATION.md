# Configuration

Retour : [README](../README.md) · Voir aussi : [USAGE](USAGE.md),
[PRIVACY_AND_SECURITY](PRIVACY_AND_SECURITY.md).

L'audit de base (crawl, robots.txt, sitemaps, cohérence, maillage, accès des
crawlers) ne demande **aucune** configuration. Les modules optionnels
s'activent quand leur accès est présent dans l'environnement. Sinon, ils sont
marqués `skipped` dans le rapport, avec la raison.

Règle : **aucune clé en argument de ligne de commande**. Une clé passée en
argument est visible dans la liste des processus et dans l'historique du
shell. Les options `--key` et `--crux-key` des anciens scripts restent
acceptées pour compatibilité, mais elles sont dépréciées.

## Variables

| Variable | Utilisée par | Contenu | Données envoyées |
|---|---|---|---|
| `PAGESPEED_API_KEY` | `run_audit.py`, `pagespeed.py` | Clé API Google Cloud avec « PageSpeed Insights API » activée | URL auditée + clé → googleapis.com |
| `CRUX_API_KEY` | `run_audit.py`, `crux_report.py`, `generate_report.py` | Clé avec « Chrome UX Report API » activée. Si vide, `run_audit.py` réutilise `PAGESPEED_API_KEY` | Origine + clé → chromeuxreport.googleapis.com |
| `GSC_SERVICE_ACCOUNT_FILE` | `run_audit.py` | **Chemin** du fichier JSON d'un compte de service en lecture seule ([gsc-access.md](../references/gsc-access.md)) | Jeton OAuth → googleapis.com |
| `GSC_SITE` | `run_audit.py` | Propriété Search Console, ex. `sc-domain:example.com` (équivaut à `--gsc-site`) | — |
| `INDEXNOW_KEY` | `run_audit.py`, `indexnow_submit.py` | Clé IndexNow du site. Le fichier `/<clé>.txt` doit être publié à la racine | Vérification : GET du fichier de clé sur le site. Soumission (option explicite) : URLs → api.indexnow.org |

Plusieurs sites, plusieurs clés IndexNow : une variable par site, par exemple
`INDEXNOW_KEY_ACME`. Passer ensuite `--indexnow-key-env INDEXNOW_KEY_ACME`
à `run_audit.py`, ou `--key-env` à `indexnow_submit.py`.

Modèle sans valeur : [.env.example](../.env.example). Le copier **hors du
dépôt**, lui donner les droits 600, puis le charger avec
`set -a; . fichier; set +a`.

## Obtenir les accès
- **Clé Google (PageSpeed et CrUX)** :
  1. Dans [console.cloud.google.com](https://console.cloud.google.com/),
     ouvrir APIs & Services > Library.
  2. Activer « PageSpeed Insights API » et « Chrome UX Report API ».
  3. Dans Credentials, créer une clé API, puis la restreindre à ces deux
     API.

  Documentation : [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started),
  [CrUX API](https://developer.chrome.com/docs/crux/api). Sans clé, le quota
  partagé de PageSpeed est souvent épuisé : c'était le cas le 2026-09-27 et
  le 2026-09-28.
- **Search Console** : compte de service en lecture seule, ajouté comme
  utilisateur de la propriété. Pas à pas : [gsc-access.md](../references/gsc-access.md).
  Nécessite `pip install google-auth requests`.
- **IndexNow** : générer une clé
  (`python -c "import uuid; print(uuid.uuid4().hex)"`), puis la publier à la
  racine du site. Voir [indexing-rules.md](../references/indexing-rules.md).

## Paramètres de `run_audit.py` (pas de secret)

| Option | Défaut | Rôle |
|---|---|---|
| `--site` | requis | URL de l'accueil |
| `--out-dir` | `seo-reports` | Dossier des rapports ; un sous-dossier par hôte |
| `--max-pages` | 60 | Pages HTML récupérées au plus (budget du crawl) |
| `--delay` | 0.5 | Secondes entre deux requêtes |
| `--timeout` | 20 | Délai par requête |
| `--include-query` | non | Suivre aussi les URLs à paramètres |
| `--max-depth` | 3 | Profondeur de clic au-delà de laquelle une page est signalée (heuristique CLAIMED) |
| `--thin-words` | 60 | Mots (dans `<main>` si présent) sous lesquels une page indexable est « quasi vide » (heuristique) |
| `--probes` | 20 | URLs inexistantes sondées au plus |
| `--extra-targets` | 15 | Cibles canonical/hreflang hors crawl à vérifier |
| `--psi-pages` / `--psi-strategy` | 3 / mobile | Pages mesurées par PageSpeed |
| `--gsc-site` / `--gsc-days` | — / 28 | Propriété et période Search Console |
| `--indexnow-key-env` | `INDEXNOW_KEY` | Nom de la variable qui contient la clé de ce site |
| `--indexnow-submit` | non | Soumet les URLs nouvelles ou modifiées. **Action externe** |
| `--no-ai-access` / `--no-diff` | non | Désactive le test des crawlers IA / la comparaison |
