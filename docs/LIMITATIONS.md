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
  Perplexity. Les rapports IA de Search Console (« Generative AI
  performance ») et de Bing (« AI Performance ») n'existent que dans les
  interfaces, pas dans les API.
- PageSpeed : sans clé, le quota partagé est souvent épuisé. Le module n'a
  pas pu être exécuté contre l'API réelle lors de la mise au point de la
  version 2.1.0 (quota sans clé épuisé le 2026-09-28). Le parseur est testé
  sur une réponse de structure documentée ; l'appel réel avec une clé invalide
  a été exécuté pour vérifier le masquage.

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
- Le skill ne modifie ni le site en production, ni un compte (Search
  Console, CDN, Google Business Profile). Il produit des rapports et des
  artefacts. Les corrections de code passent par la procédure avec GO.
- Pas de suite d'évaluation du comportement de Claude avec ce skill :
  seuls les scripts sont testés.
- Connaissances datées : au-delà de 3 mois, revérifier les références.
