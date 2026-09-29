# Accès Google Search Console (donnée mesurée)

Revu le 2026-09-28.

Ce fichier documente comment obtenir un accès **programmatique en lecture
seule** à Search Console pour n'importe quel site, via un compte de service
GCP — pas de flow OAuth interactif, réutilisable en automatisation (cron,
CI, etc.).

## Pourquoi (cf. [data-hygiene.md](data-hygiene.md))
Tout ce que `scripts/audit_site.sh` et `scripts/generate_report.py`
détectent sans Search Console est une **inférence** depuis le HTML public
(title présent, schema valide...). Search Console donne de la **donnée
mesurée** : impressions, clics, position réelle, requêtes tapées par de
vrais utilisateurs. Les deux sont complémentaires, ne jamais présenter l'un
comme un substitut de l'autre.

## Mise en place (une fois par site/projet)

1. **Créer un projet GCP** (ou réutiliser un projet existant) sur
   [console.cloud.google.com](https://console.cloud.google.com).
2. Activer l'**API "Google Search Console API"** pour ce projet
   (APIs & Services > Library > rechercher "Search Console API" > Enable).
3. **IAM & Admin > Comptes de service > Créer un compte de service.**
   Nom libre (ex. `search-console-readonly`). Pas besoin de rôle IAM
   particulier au niveau du projet — l'accès se donne côté Search Console
   directement (étape 5).
4. Sur ce compte de service : **Clés > Ajouter une clé > JSON** → télécharge
   le fichier. C'est un secret : jamais commité, jamais dans un dossier
   public du repo (exemple : `~/secrets/gsc-service-account.json`, permissions `600`).
5. Dans [Search Console](https://search.google.com/search-console) sur la
   propriété visée : **Paramètres > Utilisateurs et autorisations > Ajouter
   un utilisateur**. Coller l'email du compte de service (visible dans le
   JSON, champ `client_email`, format
   `xxx@projet.iam.gserviceaccount.com`). L'API Search Analytics demande
   un droit de lecture : **Restreint** devrait suffire (inférence depuis la
   table des permissions, Google ne l'écrit pas), **Complet** en cas de doute.
   Ne jamais donner **Propriétaire** à un compte de service de lecture.

## Vérifier l'accès
```bash
python scripts/gsc_report.py --service-account creds.json --site "sc-domain:example.com"
```
En automatique : `GSC_SERVICE_ACCOUNT_FILE=/chemin/creds.json` et
`--gsc-site sc-domain:example.com` (ou `GSC_SITE`) pour `run_audit.py`. Le
rapport liste alors les pages du sitemap sans impression sur 28 jours.
Le script affiche un avertissement explicite si le compte de service n'a
pas d'accès confirmé à la propriété demandée, plutôt que d'échouer
silencieusement.

## Piège : propriété domaine vs propriété URL-préfixe
Une propriété **domaine** (`sc-domain:example.com`) agrège **tous les
sous-domaines** — si le projet a des sous-domaines clients ou applicatifs
(ex. `*.example.com`), les requêtes remontent mélangées. Toujours filtrer
avec `--path-filter https://example.com/` (ou l'équivalent
`--gsc-path-filter` dans `generate_report.py`) pour isoler un domaine
racine précis. Constaté sur un site réel (dont le nom n'est pas publié) : sans filtre,
les résultats mélangeaient le site marketing et ~2800 sous-domaines clients.

## Ce que l'API ne donne pas (au 2026-09-27)
- Le rapport **« Generative AI performance »** (impressions dans AI
  Overviews, AI Mode, AI Overviews de Discover ; tous les sites depuis le
  2026-08-31) : interface seulement. Les mêmes impressions restent incluses
  dans le type `web` de l'API, sans distinction.
- Le réglage **« Search generative AI »** (Inclure/Exclure) : à vérifier dans
  Paramètres, à la main. Voir [google-ai-features.md](google-ai-features.md).

Types disponibles dans l'API (`--search-type`) : `web`, `discover`,
`googleNews`, `news`, `image`, `video` ; `--data-state all` pour inclure les
données fraîches non consolidées.

Anomalie connue : impressions faussées du 2025-05-13 au 2026-04-27 (clics non
affectés). Le signaler avant toute comparaison sur un an.

## Scripts associés
- [../scripts/gsc_report.py](../scripts/gsc_report.py) — requête Search
  Console autonome (top pages ou top requêtes), sortie JSON.
- [../scripts/generate_report.py](../scripts/generate_report.py) — rapport
  consolidé : audit technique + validation schema + Search Console en une
  seule commande, sortie Markdown + JSON.
