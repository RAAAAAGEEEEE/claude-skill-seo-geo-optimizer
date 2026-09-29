# Faire découvrir les nouvelles URL, sans navigateur

Revu le 2026-09-30. Étiquettes : [data-hygiene.md](data-hygiene.md#étiquettes-de-preuve).
« maj » = date « Last updated » de la page, lue le 2026-09-30.
Accès Search Console : [gsc-access.md](gsc-access.md). Règles générales
d'indexation : [indexing-rules.md](indexing-rules.md).

## La méthode, par ordre de valeur

Rien ne force Google à explorer ni à indexer une page. Ces moyens-là sont
documentés, gratuits, automatisables et se combinent.

| # | Moyen | Pour qui | Niveau | Source |
|---|---|---|---|---|
| 1 | **Sitemap avec `lastmod` exact** : la date du dernier changement significatif (contenu principal, données structurées, liens), jamais la date de génération | Google, Bing | ESTABLISHED | [build sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) (maj 2026-07-08) ; [Google](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping) (2023-06-26) |
| 2 | **Ligne `Sitemap:` dans robots.txt** : Google la lit au prochain passage sur robots.txt | tous | ESTABLISHED | build sitemap (maj 2026-07-08) |
| 3 | **Soumission du sitemap par l'API Search Console** (`sitemaps.submit`), à chaque publication | Google | ESTABLISHED | build sitemap ; [référence](https://developers.google.com/webmaster-tools/v1/sitemaps/submit) (maj 2024-07-23) |
| 4 | **Flux Atom ou RSS avec hub WebSub**, et notification du hub à chaque publication | Google et tout abonné du hub | ESTABLISHED | build sitemap : « If you use Atom or RSS, you can use WebSub to broadcast your changes to search engines, including Google. » |
| 5 | **IndexNow** : URL nouvelles, modifiées ou supprimées | Bing, Yandex, Seznam, Naver, Yep, Internet Archive, Amazon | ESTABLISHED | [documentation](https://www.indexnow.org/documentation), [searchengines.json](https://www.indexnow.org/searchengines.json) (consultés 2026-09-30) |
| 6 | **Lien interne** depuis l'accueil ou une rubrique vers chaque nouvelle page (`<a href>`) | tous | ESTABLISHED | [links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) (maj 2025-12-10) |
| 7 | Bonus : **demande d'indexation manuelle** de quelques pages prioritaires | Google | ESTABLISHED (outil), quota non publié | [ask Google to recrawl](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl) (maj 2025-12-10) |

Pourquoi IndexNow compte pour les moteurs de réponse IA : Copilot s'appuie
sur l'index de Bing (grounding, voir [ai-crawlers.md](ai-crawlers.md)).
Pour les autres assistants, l'usage de l'index Bing n'est pas documenté
par eux : CLAIMED au mieux, ne pas le promettre.

### Ce qui ne marche plus ou est interdit
- **Ping sitemap** (`https://www.google.com/ping?sitemap=…`) : déprécié le
  2023-06-26, arrêté six mois plus tard ; il répond 404
  ([Google](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)).
  Google renvoie vers robots.txt et Search Console. Supprimer ce ping des
  scripts de déploiement.
- **Indexing API de Google** : réservée aux pages `JobPosting` et aux
  vidéos en direct (`BroadcastEvent` dans une `VideoObject`)
  ([quickstart](https://developers.google.com/search/apis/indexing-api/v3/quickstart),
  maj 2026-07-16). Ne pas l'utiliser pour un article, une fiche produit ou
  une page de service.
- **Redemander** le crawl d'une même URL : « won't get it crawled any
  faster » (ask Google to recrawl, maj 2025-12-10).
- **`lastmod` du jour sur toutes les URL** : Google finit par ignorer le
  champ ([Google](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)).

## 1-3. Sitemap : ce que vérifie et fait `url_discovery.py`
- lit robots.txt : P1 si aucune ligne `Sitemap:` ;
- lit tous les sitemaps (index suivis, gzip) ; P1 si `lastmod` est
  identique partout ou dans le futur, P2 pour les URL sans `lastmod` ;
- compare au passage précédent (`discovery_state.json`) : URL nouvelles,
  modifiées (`lastmod` changé), retirées. Le premier passage sert de
  référence et n'annonce rien ;
- lit la liste des sitemaps connus de Search Console : P1 si le sitemap de
  robots.txt n'y est pas, ou si Search Console le signale en erreur ;
- avec `--submit` et s'il y a du nouveau : re-soumet le sitemap
  (`sitemaps.submit`). Pas de nouveauté, pas de soumission : soumettre
  n'est qu'un indice pour Google, le répéter n'ajoute rien.

Les URL annoncées restent « en attente » dans l'état tant qu'un passage
avec `--submit` n'a pas réussi : un passage en lecture seule ne les perd
pas.

## 4. WebSub (flux Atom/RSS)
WebSub est une recommandation du W3C ([spec](https://www.w3.org/TR/websub/)).
Le hub public de Google, <https://pubsubhubbub.appspot.com/> (page lue le
2026-09-30), indique :
- déclarer le hub dans le flux : `<link rel="hub"
  href="https://pubsubhubbub.appspot.com/"/>` sous `atom:feed` (Atom) ou
  `<atom:link rel="hub" …/>` sous `rss/channel` (RSS), ou par en-têtes HTTP
  `Link` (`rel="hub"` et `rel="self"`) ;
- à chaque nouveau contenu, envoyer un `POST` sur le hub,
  `Content-Type: application/x-www-form-urlencoded`, avec
  `hub.mode=publish` et `hub.url=<URL du flux>`.

Exemple de flux Atom minimal (illustratif) :
```xml
<feed xmlns="http://www.w3.org/2005/Atom">
  <link rel="self" href="https://example.com/feed.xml"/>
  <link rel="hub" href="https://pubsubhubbub.appspot.com/"/>
  <!-- entrées -->
</feed>
```
Notification manuelle (illustratif ; à ne lancer que pour un vrai flux) :
```bash
curl -X POST https://pubsubhubbub.appspot.com/ -d hub.mode=publish -d hub.url=https://example.com/feed.xml
```
`url_discovery.py` détecte les flux (`--feed`, ou `<link rel="alternate">`
de l'accueil), vérifie le hub déclaré (P2 s'il manque) et, avec `--submit`
et du nouveau, notifie **seulement les hubs que le flux déclare** : un hub
ne relaie qu'aux abonnés du flux qui le déclare. Code HTTP 2xx attendu ;
tout autre code est une erreur rapportée. Le hub est un service de Google
régi par ses conditions, affichées sur sa page.

## 5. IndexNow
Règles, clé et portée : [indexing-rules.md](indexing-rules.md#bing-yandex-naver-seznam-yep-amazon-internet-archive--indexnow).
`url_discovery.py --submit` envoie les URL nouvelles, modifiées **et
retirées** (le protocole les accepte toutes), après avoir vérifié le
fichier de clé, jamais tout le sitemap.

## 6. Maillage depuis l'accueil
Une nouvelle page que rien ne lie dépend du seul sitemap. Le script lit
l'accueil (et les pages `--hub-page`, par exemple la page « actualités »)
et liste en P1 les nouvelles URL qu'aucune de ces pages ne lie. Il ne
modifie pas le site : le correctif (bloc « derniers articles », lien depuis
la rubrique) se fait dans le code, avec GO du propriétaire.

## Inspection : quelles URL ne sont pas indexées
`search_console.py inspect` (ou `url_discovery.py --inspect N`) interroge
l'URL Inspection API sur les nouvelles URL d'abord, puis sur les plus
récentes. Quota : 2 000 par jour et 600 par minute par propriété
([limits](https://developers.google.com/webmaster-tools/limits), maj
2025-08-28). Les URL trouvées indexées il y a moins de 7 jours ne sont pas
réinspectées. Chaque URL non indexée reçoit une catégorie, tirée des
champs énumérés de la réponse (indépendants de la langue) :

| Catégorie | Signification | Suite |
|---|---|---|
| `unknown_to_google` | Google ne connaît pas l'URL | sitemap, lien interne ; demande manuelle possible |
| `discovered_not_crawled` | découverte, pas encore explorée | maillage, patience ; demande manuelle possible |
| `crawled_not_indexed` | explorée, non retenue | contenu, doublon ; soumettre n'y change rien |
| `blocked_robots_txt`, `noindex`, `fetch_error`, `canonical_elsewhere` | bloquée par le site | corriger le site, **jamais** de demande |

Sortie (JSON) : `inspected`, `indexed`, `not_indexed` (URL, catégorie,
dernier crawl, lien d'inspection), `by_category`, `to_request` (10 au plus,
seulement les catégories qui peuvent en profiter, sauf URL demandée il y a
moins de 7 jours), `errors`, `quota_stopped`.

## Bonus : demande d'indexation manuelle
Optionnel, pour **quelques** pages prioritaires (la page d'accueil d'une
nouvelle rubrique, un article important), jamais pour tout le site. Pas
d'API : l'outil d'inspection de l'interface est le seul moyen, et Google
limite le nombre de demandes par jour sans publier le chiffre
([aide](https://support.google.com/webmasters/answer/9012289?hl=fr),
consultée le 2026-09-30). Environ 10 par jour et par propriété constatés à
l'usage (CLAIMED, observation). Il faut être propriétaire ou utilisateur
avec accès complet (ask Google to recrawl).

Qui clique : l'agent, dans le navigateur de l'utilisateur, **déjà
connecté** à son compte Google, via l'extension Claude in Chrome
(`mcp__claude-in-chrome__*`). L'agent ne saisit jamais d'identifiant et ne
résout jamais de CAPTCHA : si Google demande une connexion ou affiche un
CAPTCHA, il s'arrête et le signale.

Méthode qui fonctionne (testée en conditions réelles le 2026-09-29) :
1. Liste des URL : `to_request` de `search_console.py inspect`.
2. Garder la fenêtre du navigateur **visible au premier plan**, pas
   réduite : sinon l'interface ne réagit qu'une fois sur deux.
3. Pour **chaque** URL, repartir de la vue d'ensemble de la propriété :
   `https://search.google.com/search-console?resource_id=<propriété encodée>`
   (par exemple `resource_id=sc-domain%3Aexample.com` ou
   `resource_id=https%3A%2F%2Fexample.com%2F`), attendre environ 6 s.
   Un lien direct `…/inspect?…&id=…` renvoie une 404 : `id` est un jeton
   interne, pas l'URL.
4. Trouver le champ « Inspecter n'importe quelle URL » (outil `find`), le
   remplir avec `form_input`, cliquer le bouton de recherche à côté, attendre
   15 à 20 s.
5. Vérifier que l'URL affichée est bien celle demandée. La page peut
   contenir plusieurs panneaux d'inspection : prendre le bouton **Demander
   une indexation** du panneau de **cette** URL.
6. Cliquer, attendre environ 20 s, vérifier le dialogue « Indexation
   demandée », le fermer.
7. Si l'URL inspectée ne change pas après deux essais : passer à la
   suivante et le signaler. Si Google affiche un dépassement de quota :
   arrêter pour la journée.
8. Noter les URL effectivement demandées :
   `python scripts/search_console.py mark-requested --state <état> <url>…`
   (elles ne sont pas reproposées pendant 7 jours).
9. Fermer l'onglet ouvert. Ne rien toucher d'autre dans Search Console
   (aucun réglage, aucune suppression, aucun ajout d'utilisateur).

Demander l'indexation est une action visible au nom du propriétaire :
à faire seulement avec son accord, une fois pour la tâche planifiée.

## Mode planifiable (tâche quotidienne)
Un passage par jour, ou à chaque déploiement :
```bash
set -a; . ~/secrets/seo-discovery.env; set +a   # GSC_SERVICE_ACCOUNT_FILE, GSC_SITE, INDEXNOW_KEY
python scripts/url_discovery.py --site https://example.com --submit --inspect 200 --out-dir ~/seo-reports
```
Effet : re-soumission du sitemap s'il a changé, notification WebSub,
IndexNow des URL changées, rapport des URL non indexées
(`discovery_<date>.md` et `.json`). Codes : 0 OK, 1 une action a échoué ou
aucun sitemap lisible, 2 site injoignable.

`--submit` envoie des données à des tiers à chaque passage (Google,
hub WebSub, IndexNow) : **accord du propriétaire requis** avant de le mettre
dans une tâche planifiée, comme pour la création de la tâche elle-même.
Exemples cron, Planificateur Windows et tâche Claude Code :
[docs/USAGE.md](../docs/USAGE.md#découverte-des-url--url_discoverypy).

Consigne type pour une tâche planifiée Claude Code (à adapter) :
> Chaque jour à 7 h : depuis le dossier du skill seo-geo-optimizer, lance
> `python scripts/url_discovery.py --site https://example.com --submit
> --inspect 200 --out-dir ~/seo-reports`. Résume le `discovery_*.md` le plus
> récent en 4 lignes : nouvelles URL annoncées, échecs, URL non indexées
> par catégorie, pages nouvelles sans lien depuis l'accueil. Si l'extension
> Claude in Chrome est connectée **et** que le propriétaire l'a autorisé,
> demande l'indexation des URL `to_request` selon
> references/url-discovery.md (bonus), puis `mark-requested`. Sinon, liste
> ces URL sans rien faire d'autre.
