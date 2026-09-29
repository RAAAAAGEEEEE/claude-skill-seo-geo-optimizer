# Accès Search Console pour l'agent (compte de service)

Revu le 2026-09-30. Source unique de la mise en place : les autres documents
renvoient ici.

L'agent opère Search Console **avec les accès du propriétaire du site**,
sans navigateur ni mot de passe : le propriétaire crée un **compte de
service** Google Cloud, télécharge sa clé JSON et ajoute l'adresse e-mail de
ce compte à sa propriété Search Console. L'agent s'en sert ensuite pour :
- lire les performances (Search Analytics, donnée **mesurée**, voir
  [data-hygiene.md](data-hygiene.md)) ;
- lister et **soumettre** les sitemaps (`sitemaps.submit`) ;
- **inspecter** des URL (URL Inspection API) et sortir la liste des pages
  non indexées.

Scripts : [`../scripts/search_console.py`](../scripts/search_console.py),
[`../scripts/url_discovery.py`](../scripts/url_discovery.py),
[`../scripts/gsc_report.py`](../scripts/gsc_report.py). Méthode de
découverte des URL : [url-discovery.md](url-discovery.md).

## Tutoriel (à faire une fois, par le propriétaire du site)

Durée : 10 à 15 minutes. Gratuit : l'API Search Console n'est pas facturée
et ce tutoriel n'active pas de facturation. Il faut un compte Google
propriétaire de la propriété dans Search Console. Les libellés entre
guillemets sont ceux des pages d'aide officielles en français, lues le
2026-09-30 ; l'interface anglaise dit « Create Project », « Keys »,
« Add key », « Users and permissions ».

1. **Créer un projet Google Cloud.** Ouvrir
   <https://console.cloud.google.com/projectcreate> (connexion Google
   demandée), saisir un nom de projet (4 à 30 caractères, par exemple
   `search-console-agent`), puis cliquer **Créer**.
   Doc : [Créer et gérer des projets](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=fr)
   (maj 2026-09-26).
   Vérifier : le projet apparaît dans le sélecteur de projet de la barre
   d'outils de la console.
2. **Activer l'API.** Ouvrir
   <https://console.cloud.google.com/apis/library/searchconsole.googleapis.com>,
   vérifier que le projet de l'étape 1 est sélectionné en haut, puis cliquer
   **Activer** sur la fiche « Google Search Console API ».
   Doc : [Activer et désactiver des services](https://cloud.google.com/service-usage/docs/enable-disable?hl=fr)
   (maj 2026-09-26) ; nom exact de l'API lu dans son document de découverte
   (`https://searchconsole.googleapis.com/$discovery/rest?version=v1`,
   révision 20260923).
   Vérifier : l'étape 9 échoue avec un message « API not enabled » (ou
   « has not been used in project ») tant que l'API n'est pas activée.
3. **Créer le compte de service.** Ouvrir
   <https://console.cloud.google.com/iam-admin/serviceaccounts/create>,
   saisir un nom (par exemple `search-console-agent`), puis cliquer **OK**.
   Aucun rôle IAM n'est nécessaire : l'accès se donne dans Search Console
   (étape 7).
   Doc : [Créer des comptes de service](https://cloud.google.com/iam/docs/service-accounts-create?hl=fr)
   (maj 2026-09-25).
   Vérifier : le compte apparaît dans la liste, avec une adresse de la forme
   `nom@projet.iam.gserviceaccount.com`.
4. **Créer la clé JSON.** Sur
   <https://console.cloud.google.com/iam-admin/serviceaccounts>, cliquer
   l'adresse e-mail du compte, onglet **Clés**, menu **Ajouter une clé** >
   **Créer une clé**, type **JSON**, **Créer**. Le fichier se télécharge
   **une seule fois**.
   Doc : [Créer et supprimer des clés de compte de service](https://cloud.google.com/iam/docs/keys-create-delete?hl=fr)
   (maj 2026-09-25).
   Si la création est refusée : la contrainte d'organisation
   `iam.disableServiceAccountKeyCreation` est active (par défaut pour les
   organisations créées depuis le 2024-05-03, même page). Un compte Google
   personnel sans organisation n'est pas concerné.
5. **Ranger la clé hors de tout dépôt.** Déplacer le fichier dans un dossier
   de secrets, par exemple `~/secrets/gsc-service-account.json`, droits
   `600` (`chmod 600 ~/secrets/gsc-service-account.json` sous Linux et
   macOS). Ne jamais le commiter, ne jamais l'ouvrir dans une conversation,
   ne jamais coller son contenu : la clé privée qu'il contient donne l'accès
   à la propriété.
6. **Relever l'adresse du compte de service** sans afficher la clé :
   ```bash
   python -c "import json,os;print(json.load(open(os.path.expanduser('~/secrets/gsc-service-account.json')))['client_email'])"
   ```
   Seul le champ `client_email` est affiché ; ce n'est pas un secret.
7. **Ajouter le compte à la propriété Search Console.** Ouvrir
   <https://search.google.com/search-console>, choisir la propriété, puis
   **Paramètres** > **Utilisateurs et autorisations** > **Ajouter un
   utilisateur**. Coller l'adresse de l'étape 6, choisir l'autorisation
   **Propriétaire**, puis enregistrer. Le compte devient « propriétaire
   délégué » (propriétaire sans jeton de validation).
   Doc : [Gérer les propriétaires, les utilisateurs et les autorisations](https://support.google.com/webmasters/answer/7687615?hl=fr)
   (consultée le 2026-09-30). La page n'est visible que pour un
   propriétaire.
   Vérifier : l'adresse apparaît dans la liste avec l'autorisation
   « Propriétaire », sans la mention « Validé ».
8. **Donner le chemin à l'agent** par une variable d'environnement, jamais
   en argument : `GSC_SERVICE_ACCOUNT_FILE=~/secrets/gsc-service-account.json`,
   et la propriété dans `GSC_SITE` (par exemple `sc-domain:example.com` ou
   `https://example.com/`). Installer les bibliothèques :
   `pip install google-auth requests`.
9. **Vérifier l'accès** (lecture seule) :
   ```bash
   python scripts/search_console.py sites
   python scripts/search_console.py sitemaps --site "sc-domain:example.com"
   ```
   Attendu : la propriété figure dans `sites` avec `siteOwner` (ou
   `siteFullUser`), et `sitemaps` répond sans erreur. Code 2 = variable
   absente ou fichier introuvable ; `HTTP 403` = compte non ajouté à la
   propriété, ou ajouté à une autre propriété (domaine ou préfixe d'URL).

### Propriétaire ou accès complet ?
La table des autorisations de Google (même page d'aide) donne à
l'« utilisateur avec accès complet » les droits « Envoyer un sitemap » et
« Inspection de l'URL ». Ce tutoriel ajoute le compte comme
**Propriétaire** : c'est le niveau qui couvre toutes les actions de
l'agent sans exception, et celui avec lequel `sites`, `sitemaps`, `stats`
et `inspect` ont été exécutés sur une propriété réelle le 2026-09-30. La
**soumission** de sitemap par l'API n'a pas été exécutée en réel par ce
skill (ni en Propriétaire, ni en accès complet) : seuls les tests hors
ligne la couvrent.

Contrepartie : un propriétaire peut ajouter ou retirer des utilisateurs.
Une fuite de la clé donnerait donc la maîtrise de la propriété. Qui veut le
moindre privilège choisit **Accès complet**, puis passe à Propriétaire
seulement si `submit-sitemap` répond `HTTP 403`. Dans les deux cas :
révoquer la clé (étape 4, onglet **Clés**, supprimer) dès qu'elle a pu
fuiter.

### Sans fichier de clé
`GSC_ACCESS_TOKEN` accepte un jeton OAuth déjà obtenu (par exemple avec
Google Cloud CLI), valable une heure. Utile pour un essai ponctuel ; pour
une tâche planifiée, le fichier de clé reste plus simple.

## Portée OAuth demandée par les scripts
- `https://www.googleapis.com/auth/webmasters.readonly` : lecture
  (statistiques, liste des sitemaps, inspection). URL Inspection accepte
  l'une ou l'autre portée ([référence](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect),
  maj 2024-07-23).
- `https://www.googleapis.com/auth/webmasters` : **seulement** pour
  `sitemaps.submit`, qui l'exige ([référence](https://developers.google.com/webmaster-tools/v1/sitemaps/submit),
  maj 2024-07-23). `search_console.py` ne la demande que pour
  `submit-sitemap`, `url_discovery.py` que avec `--submit`.

## Quotas
[Usage limits](https://developers.google.com/webmaster-tools/limits)
(maj 2025-08-28), ESTABLISHED :
- URL Inspection : **2 000 requêtes/jour et 600/minute par propriété** ;
  10 000 000/jour par projet.
- Search Analytics : 1 200 requêtes/minute par propriété et par
  utilisateur ; les requêtes groupées par page **et** requête coûtent le
  plus cher.
- Autres ressources (sitemaps, sites) : 20 requêtes/seconde et 200/minute
  par utilisateur.

`search_console.py inspect` plafonne à 2 000 inspections, espace les appels
d'au moins 0,1 s et s'arrête au premier refus de quota en gardant ce qu'il a
déjà inspecté.

## Piège : propriété domaine vs propriété préfixe d'URL
Une propriété **domaine** (`sc-domain:example.com`) agrège **tous les
sous-domaines**. Si le projet a des sous-domaines clients ou applicatifs,
les statistiques remontent mélangées : filtrer avec `--path-filter
https://example.com/` (`gsc_report.py`, `search_console.py stats`).
Constaté sur un site réel dont le nom n'est pas publié : sans filtre, les
résultats mélangeaient le site marketing et environ 2 800 sous-domaines
clients. Pour l'inspection, l'URL doit appartenir à la propriété ; une
propriété préfixe d'URL s'écrit **avec** la barre finale
(`https://example.com/`).

## Ce que l'API ne donne pas (au 2026-09-30)
- La **demande d'indexation** de l'outil d'inspection : pas d'API. Bonus
  manuel décrit dans [url-discovery.md](url-discovery.md#bonus--demande-dindexation-manuelle).
- Le rapport **« Generative AI performance »** (impressions dans AI
  Overviews, AI Mode, AI Overviews de Discover ; tous les sites depuis le
  2026-08-31) : interface seulement. Les mêmes impressions restent incluses
  dans le type `web` de l'API, sans distinction.
- Le réglage **« Search generative AI »** (Inclure/Exclure) : à vérifier
  dans Paramètres, à la main ([google-ai-features.md](google-ai-features.md)).
- Le test en direct d'une URL : l'inspection ne porte que sur la version
  indexée.

Types disponibles pour Search Analytics (`--search-type`) : `web`,
`discover`, `googleNews`, `news`, `image`, `video` ; `--data-state all`
(`gsc_report.py`) pour inclure les données fraîches non consolidées.

Anomalie connue : impressions faussées du 2025-05-13 au 2026-04-27 (clics non
affectés). Le signaler avant toute comparaison sur un an.

## Sécurité
- La clé ne passe jamais en argument, n'est jamais lue dans une conversation
  et n'est jamais écrite dans un rapport ; le jeton OAuth est masqué dans les
  messages d'erreur (un test le vérifie).
- Ce skill ne modifie aucun réglage de la propriété : ni utilisateurs, ni
  paramètres, ni suppressions d'URL. Les seules écritures sont
  `sitemaps.submit` et, en option, la demande d'indexation manuelle.
