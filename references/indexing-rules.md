# Indexation — ce qui est autorisé, ce qui est interdit

Revu le 2026-09-30. Tout est **ESTABLISHED** sauf mention.

## Google : sitemap, Search Console, WebSub
`sitemap.xml` à jour, référencé dans `robots.txt`, soumis dans Search
Console (interface ou API `sitemaps.submit`), flux Atom/RSS avec WebSub.
Inspection d'URL manuelle et ponctuelle pour une page importante. Méthode
complète et automatisée (`url_discovery.py`, `search_console.py`) :
[url-discovery.md](url-discovery.md).

Règles du sitemap ([Google](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), maj 2026-07-08) :
- `lastmod` utilisé seulement s'il est exact de façon constante et
  vérifiable ; il doit refléter un changement significatif (contenu
  principal, données structurées, liens). Dater toutes les pages du jour
  apprend à Google à ignorer le champ.
- `priority` et `changefreq` : ignorés par Google.
- 50 000 URLs ou 50 Mo non compressés par fichier ; au-delà, un index.
- Le « ping » sitemap (`google.com/ping?sitemap=`) est déprécié depuis le
  2023-06-26 et répond 404 depuis l'arrêt, six mois plus tard
  ([Google](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)).
- Soumission : rapport Sitemaps de Search Console, API Search Console, ou
  ligne `Sitemap:` de robots.txt ; flux Atom/RSS : WebSub « to broadcast
  your changes to search engines, including Google ».
- Uniquement des URLs canoniques, indexables, en 200.
Générateur conforme : [`../scripts/generate_sitemap.py`](../scripts/generate_sitemap.py).

### Interdit — Google Indexing API hors périmètre
Réservée aux pages `JobPosting` et `BroadcastEvent` dans une `VideoObject`.
Chaque soumission passe par une détection de spam, l'abus peut couper
l'accès, le quota par défaut ne sert qu'aux tests et l'usage réel demande
une approbation ([quickstart](https://developers.google.com/search/apis/indexing-api/v3/quickstart), maj 2026-07-16).
À quelqu'un qui veut « indexer plus vite via l'API Google » : expliquer,
proposer sitemap + Search Console, et IndexNow pour les autres moteurs.

### Interdit — auto-submit maison
Pas de mécanisme qui pousse des URLs en boucle hors des canaux documentés
(sitemap, API Search Console, WebSub, IndexNow) : rien de fiable, et proche
du spam d'indexation. Re-soumettre un sitemap **qui a changé**, notifier un
hub WebSub à la publication et envoyer à IndexNow les URL changées sont des
usages documentés ; les répéter sans changement n'apporte rien.

## Bing, Yandex, Naver, Seznam, Yep, Amazon, Internet Archive : IndexNow
Mécanisme prévu, gratuit, encouragé par ces moteurs
([searchengines.json](https://www.indexnow.org/searchengines.json), consulté
2026-09-27). Une soumission est partagée entre tous les participants.
Google **n'y participe pas**.

Règles du protocole ([documentation](https://www.indexnow.org/documentation)) :
- Clé : 8 à 128 caractères parmi `a-z`, `A-Z`, `0-9`, `-` (la doc dit
  aussi « hexadécimal », ce qui contredit la liste ; un UUID hex convient
  aux deux lectures).
- **Emplacement de la clé** : un fichier de clé hors racine ne couvre que
  les URLs sous son répertoire. Une clé servie en `/indexnow/<clé>.txt` ne
  peut pas soumettre `/fr/page` : la soumission est refusée. Publier la clé
  à la racine (`/<clé>.txt`).
- 10 000 URLs max par POST ; réponses 200, 202 (clé en validation), 400,
  403 (clé invalide), 422 (URL hors hôte/portée), 429 (trop de requêtes).
- Soumettre les URLs nouvelles ou réellement modifiées, pas tout le sitemap.

Script : [`../scripts/indexnow_submit.py`](../scripts/indexnow_submit.py) —
vérifie la clé publiée **et** la portée de son emplacement avant tout
envoi, refuse sinon.

Mise en place (une fois par site) :
1. `python -c "import uuid; print(uuid.uuid4().hex)"`
2. Publier `https://example.com/<clé>.txt` contenant uniquement la clé.
3. Mettre la clé dans la variable `INDEXNOW_KEY` (jamais en argument), puis
   `python scripts/indexnow_submit.py --host example.com --urls urls.txt --dry-run`,
   et enfin sans `--dry-run`.

En automatique, `run_audit.py` vérifie le fichier de clé à chaque passage. Il
écrit la liste des URLs nouvelles ou modifiées depuis le rapport précédent
(`audit_<date>_indexnow_urls.txt`). Il ne les soumet qu'avec
`--indexnow-submit`, option à n'ajouter à une tâche planifiée qu'après
accord du propriétaire (action externe).

Bing URL Submission API : le quota « 10 000 URLs/jour » date de 2019 ; un
développeur a constaté 100/jour en 2026 (CLAIMED). Préférer IndexNow.

## Brave Search
Pas de crawler propre : Brave ne crawle que ce que `Googlebot` peut crawler.
Soumission manuelle et ponctuelle sur `https://search.brave.com/submit-url`
(re-crawl, sans garantie). Voir [ai-crawlers.md](ai-crawlers.md).

## Rappel : l'indexation n'est pas le problème le plus fréquent
Avant d'accélérer, vérifier l'accès réel
([cloudflare-ai-access.md](cloudflare-ai-access.md)) et l'absence de
`noindex`, de canonical mal orienté, de redirection temporaire, de 5xx.
Un problème d'accès ne se corrige pas en soumettant plus fort.
