# Accès Google Search Console (donnée mesurée)

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
   public du repo (convention déjà en place sur hermes :
   `secrets/gsc-service-account.json`, permissions `600`).
5. Dans [Search Console](https://search.google.com/search-console) sur la
   propriété visée : **Paramètres > Utilisateurs et autorisations > Ajouter
   un utilisateur**. Coller l'email du compte de service (visible dans le
   JSON, champ `client_email`, format
   `xxx@projet.iam.gserviceaccount.com`). Rôle **Propriétaire** ou
   **Complet** — le rôle **Restreint** ne suffit pas pour interroger l'API.

## Vérifier l'accès
```bash
python scripts/gsc_report.py --service-account creds.json --site "sc-domain:example.com"
```
Le script affiche un avertissement explicite si le compte de service n'a
pas d'accès confirmé à la propriété demandée, plutôt que d'échouer
silencieusement.

## Piège : propriété domaine vs propriété URL-préfixe
Une propriété **domaine** (`sc-domain:example.com`) agrège **tous les
sous-domaines** — si le projet a des sous-domaines clients ou applicatifs
(ex. `*.example.com`), les requêtes remontent mélangées. Toujours filtrer
avec `--path-filter https://example.com/` (ou l'équivalent
`--gsc-path-filter` dans `generate_report.py`) pour isoler un domaine
racine précis. Confirmé empiriquement sur SiteServi : sans filtre, les
résultats mélangeaient le site marketing et ~2800 sous-domaines clients.

## Scripts associés
- [../scripts/gsc_report.py](../scripts/gsc_report.py) — requête Search
  Console autonome (top pages ou top requêtes), sortie JSON.
- [../scripts/generate_report.py](../scripts/generate_report.py) — rapport
  consolidé : audit technique + validation schema + Search Console en une
  seule commande, sortie Markdown + JSON.
