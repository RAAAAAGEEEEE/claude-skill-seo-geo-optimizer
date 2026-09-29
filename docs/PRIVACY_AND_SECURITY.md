# Confidentialité et sécurité

Retour : [README](../README.md) · Voir aussi : [SECURITY.md](../SECURITY.md),
[CONFIGURATION](CONFIGURATION.md).

## Ce qui sort de la machine

| Quand | Vers | Quoi |
|---|---|---|
| Toujours | Le site audité | GET publics : pages, robots.txt, sitemaps, URLs inexistantes, et un GET par crawler testé (user-agent simulé). Le crawl respecte robots.txt et `--delay`. |
| `PAGESPEED_API_KEY` présente | googleapis.com (PageSpeed Insights) | URL des pages mesurées + clé en paramètre `?key=` (seule méthode documentée) |
| `CRUX_API_KEY` ou `PAGESPEED_API_KEY` présente | chromeuxreport.googleapis.com | Origine du site + clé |
| `GSC_SERVICE_ACCOUNT_FILE` + propriété | oauth2.googleapis.com, googleapis.com | Assertion signée du compte de service, puis requête Search Analytics en lecture seule |
| `INDEXNOW_KEY` présente | Le site audité | GET de `/<clé>.txt` : vérification seulement |
| `search_console.py` (`sites`, `sitemaps`, `inspect`, `stats`) ou `url_discovery.py` avec propriété | oauth2.googleapis.com, googleapis.com, searchconsole.googleapis.com | Assertion signée du compte de service (ou jeton fourni), puis lectures : liste des propriétés et sitemaps, URL à inspecter, requêtes Search Analytics. Portée `webmasters.readonly` |
| `search_console.py submit-sitemap` ou `url_discovery.py --submit` | googleapis.com (Search Console) | URL du sitemap soumis. Portée `webmasters`. **Action externe, à approuver.** |
| `url_discovery.py --submit` avec un flux qui déclare un hub | Le hub déclaré (par exemple pubsubhubbub.appspot.com, service de Google) | POST `hub.mode=publish` et l'URL du flux. **Action externe, à approuver.** |
| `url_discovery.py --submit` avec `INDEXNOW_KEY` | api.indexnow.org | Hôte, clé, URL nouvelles, modifiées ou retirées. **Action externe, à approuver.** |
| Bonus : demande d'indexation manuelle | Search Console, dans le navigateur de l'utilisateur (session déjà ouverte) | Clic « Demander une indexation » pour quelques URL. **Accord requis** ; aucun identifiant saisi, aucun CAPTCHA résolu |
| `crawler_logs.py` sans `--no-verify` | Serveurs des fournisseurs (Google, Bing, OpenAI, Perplexity, Anthropic, Apple, DuckDuckGo, Common Crawl, Mistral) | GET des listes d'IP publiques. Rien du journal n'est envoyé. |
| `glossary_check.py audit --site` ou `suggest` | Le site indiqué | GET publics : robots.txt, sitemaps, pages (au plus `--max-pages`, pause `--delay`, robots.txt respecté) |
| `--indexnow-submit` **et** clé vérifiée **et** rapport précédent | api.indexnow.org | Hôte, clé, URLs nouvelles ou modifiées. Elles sont partagées avec tous les moteurs participants. **Action externe, à approuver.** |

Rien d'autre. Pas de télémétrie, pas d'appel à une API payante. L'API X
(Twitter) n'est jamais appelée.

## Secrets
- Ils sont lus **uniquement** dans des variables d'environnement, ou via un
  chemin de fichier donné par une variable (`envkeys.py`). Jamais en
  argument : l'argument serait visible dans `ps` et dans l'historique du
  shell.
- Ils ne sont jamais affichés ni écrits. Le JSON et le Markdown passent par
  `envkeys.redact_obj` / `redact` avant écriture. Les erreurs des API sont
  réduites à leur message, puis masquées.
- Le JSON garde seulement la **présence** de chaque accès
  (`options.credentials_present`), jamais sa valeur.
- Tests :
  - `tests/test_automation.py` vérifie qu'une clé IndexNow de test
    n'apparaît ni dans la console, ni dans le Markdown, ni dans le JSON ;
  - il vérifie aussi qu'une erreur PageSpeed ne contient pas la clé.

  Vérifié aussi en réel le 2026-09-28, avec une fausse clé PageSpeed et une
  fausse clé IndexNow contre un site réel : aucune trace dans les sorties.
- Fichier de compte de service : hors du dépôt, avec les droits 600, jamais
  ouvert dans une conversation. Niveau dans Search Console : **Propriétaire**
  pour que l'agent fasse tout (sitemaps, inspection), **Accès complet** pour
  le moindre privilège, **Restreint** pour les seules statistiques. Un
  propriétaire peut gérer les utilisateurs : une clé qui fuit se révoque
  aussitôt ([gsc-access.md](../references/gsc-access.md#propriétaire-ou-accès-complet-)).
- Le jeton OAuth est masqué dans les erreurs de `search_console.py` (test
  `test_error_message_never_contains_the_token`).

## Données dans les rapports
Les rapports ne contiennent que des données publiques du site audité :
- URLs, titres, descriptions, en-têtes ;
- avec Search Console : clics, impressions et positions par page.

Ils ne contiennent aucune donnée personnelle de visiteurs. Les rapports
Search Console restent confidentiels pour le propriétaire du site : ne pas
les publier.

## Journaux serveur
Un journal d'accès contient des adresses IP, qui sont des données
personnelles. `crawler_logs.py` les lit en mémoire et ne les écrit jamais :
la sortie contient des compteurs, et les sources usurpées sont agrégées en
/24 (IPv4) ou /48 (IPv6). Un test le vérifie
(`tests/test_glossary_logs.py`). Ne pas copier un journal brut dans un
rapport, un ticket ou le dépôt.

## Charge sur le site audité
Par défaut, au plus 60 pages, 20 sondes 404 et environ 27 requêtes d'accès
crawlers, avec 0,5 s entre deux requêtes. Sur un site de 25 pages le 2026-09-27 :
80 requêtes en 40 à 50 s. Le user-agent `seo-geo-optimizer-audit/2.3` est
identifiable dans les journaux du site.
