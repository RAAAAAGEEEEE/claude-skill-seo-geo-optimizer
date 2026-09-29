# Limites

Retour : [README](../README.md) · Voir aussi : [ARCHITECTURE](ARCHITECTURE.md).

## Mesure
- **Pas de rendu JavaScript.** Le contenu, les liens, les canonical et le
  JSON-LD injectés côté client sont invisibles. Pour ces sites, utiliser un
  navigateur ou le Rich Results Test.
- **User-agents simulés.** Les requêtes partent de votre machine, pas des
  IP des fournisseurs. Un 403 prouve une règle par user-agent. Un 200 ne
  prouve pas que le vrai crawler passe.
- Les user-agents complets de ClaudeBot, Claude-User et Claude-SearchBot ne
  sont pas publiés par Anthropic. Le script utilise une chaîne construite
  autour du jeton.
- **Échantillon.** Au-delà de `--max-pages`, le crawl est partiel. Les
  orphelines et la profondeur deviennent alors des estimations, et le
  rapport le signale.
- **Aucune mesure directe des citations** dans ChatGPT, Claude ou
  Perplexity. Un panel par API (OpenAI, Perplexity, Anthropic) serait
  payant et ne reproduit pas l'application grand public ; le skill n'en
  fournit pas ([automation.md](../references/automation.md)). Les rapports IA de Search Console (« Generative AI
  performance ») et de Bing (« AI Performance ») n'existent que dans les
  interfaces, pas dans les API.
- PageSpeed : sans clé, le quota partagé est souvent épuisé. Le module n'a
  pas pu être exécuté contre l'API réelle lors de la mise au point de la
  version 2.1.0 (quota sans clé épuisé le 2026-09-28). Le parseur est testé
  sur une réponse de structure documentée ; l'appel réel avec une clé invalide
  a été exécuté pour vérifier le masquage.

## Découverte des URL et Search Console (`url_discovery.py`, `search_console.py`)
- **Aucune garantie d'indexation.** Sitemap, WebSub et IndexNow informent
  les moteurs ; ils décident seuls d'explorer et d'indexer. Aucun délai
  n'est promis.
- **Soumission de sitemap par l'API : pas exécutée en réel** par ce skill
  (2026-09-30). Elle suit la référence de Google et les tests hors ligne
  vérifient la requête (PUT, URL encodées, portée `webmasters`). Les
  lectures (`sites`, `sitemaps`, `stats`, `inspect`) ont été exécutées sur
  une propriété réelle le 2026-09-30.
- **WebSub** : notifié seulement pour les hubs que le flux déclare. Google
  documente WebSub comme moyen de diffusion, sans dire comment il pèse sur
  l'exploration. La notification réelle d'un hub n'a pas été exécutée par
  ce skill : seuls les tests hors ligne la couvrent.
- **Inspection** : version indexée seulement (pas de test en direct). Les
  catégories `unknown_to_google`, `discovered_not_crawled` et
  `crawled_not_indexed` viennent du libellé anglais de `coverageState`
  (le script demande `en-US`) ; si Google change ces libellés, elles
  tombent dans `other`.
- **Maillage** : seuls l'accueil et les pages `--hub-page` sont lus, en
  HTML statique. Un lien injecté en JavaScript n'est pas vu.
- **État local** : `discovery_state.json` et l'état d'inspection vivent sur
  la machine qui lance le script. Deux machines = deux états.
- **Demande d'indexation manuelle** : dépend de l'interface de Search
  Console, qui peut changer ; quota non publié (environ 10 par jour
  constatés, CLAIMED). Méthode testée le 2026-09-29.

## Journaux serveur (`crawler_logs.py`)
- Vérification par listes d'IP seulement. Pas de DNS inverse ni de
  signature Web Bot Auth : Meta et Amazon (listes en HTML) restent « non
  vérifiables ». La liste de Bing date du 2024-01-03 : un vrai bingbot hors
  de cette liste serait compté comme usurpé. Confirmer par DNS inverse
  (`search.msn.com`) avant d'agir.
- Formats lus : *combined* (Apache, nginx) et JSON lines. Un format CDN
  différent donne le code 2.
- La couverture du sitemap ne vaut que pour la période du journal.

## Glossaire (`glossary_check.py`)
- Les termes sont reconnus par `DefinedTerm`, `<dfn>`, `<dt>`, titres avec
  `id`, ou liens du hub (`--term-links`). Un glossaire rendu en JavaScript
  ou paginé n'est lu que sur la page donnée.
- La détection des mentions est lexicale (mot entier, accents et casse
  ignorés, pluriel en s/x). Elle ne comprend pas le sens : un terme
  homonyme donne un faux positif.
- `suggest` ne relève que des sigles et des balises `<abbr>`/`<dfn>` : un
  terme ordinaire (« préhenseur ») n'y apparaît pas.
- Aucun effet d'un glossaire sur les citations IA n'est démontré
  ([glossary.md](../references/glossary.md)).

## Formats de contenu
- La table de [content-formats.md](../references/content-formats.md) est
  un guide de planification, pas un contrôle automatique : aucun script ne
  détecte le format d'une page ni ne juge la qualité d'un test.
- Les parts de citation par format viennent d'études de vendeurs d'outils
  (CLAIMED, méthode publiée ou partielle), faites surtout en anglais et aux
  États-Unis. Ce sont des corrélations : publier un format n'entraîne pas
  une citation.
- Google ne publie aucune règle sur les calculateurs, les chronologies ou
  les changelogs : ces lignes s'appuient sur les règles générales.

## Maillage et cocon
- **Liens contextuels.** Un lien est « contextuel » s'il se trouve dans
  `<main>` ou `<article>`, hors de `<nav>` et `<aside>`. Sans ces balises,
  la distinction est impossible et les contrôles correspondants sont
  désactivés.
- **Rubriques.** Elles sont déduites du répertoire d'URL. Un cocon qui ne
  suit pas les répertoires sera mal lu.
- **Seuils.** Profondeur 3, 60 mots, 80 % d'ancres identiques : ce sont
  des heuristiques du skill ou des praticiens (CLAIMED), pas des règles
  Google.
- **Méthodes de Laurent Bourrelly.** Ses règles précises ne sont publiées
  que dans sa formation payante. Le skill n'en reprend que la partie
  publique ([french-practitioners.md](../references/french-practitioners.md)).

## Portée
- Le skill ne modifie ni le site en production, ni les réglages d'un
  compte (Search Console, CDN, Google Business Profile). Seules écritures
  dans Search Console : soumission de sitemap (`--submit`,
  `submit-sitemap`) et, en bonus, demande d'indexation manuelle. Les
  corrections de code passent par la procédure avec GO.
- Les 8 cas de [evals/evals.json](../evals/evals.json) décrivent le
  comportement attendu de Claude avec ce skill, mais ne s'exécutent pas
  automatiquement : seuls les scripts sont testés par `unittest`.
- Connaissances datées : au-delà de 3 mois, revérifier les références.
